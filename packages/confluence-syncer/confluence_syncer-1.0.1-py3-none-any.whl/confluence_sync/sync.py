import collections
import dataclasses as dc
import datetime as dt
import itertools as it
import logging
import queue
import threading
import typing as tp
from concurrent import futures

from atlassian import errors

from confluence_sync import context, events, fmt, observer, tree
from confluence_sync.confluence import CustomConfluence, StrDict


@dc.dataclass(slots=True)
class OutHierarchyPage:
	title: str
	# True if the page is just used to keep the tree structure;
	# otherwise, False, which means the page itself is copied.
	nominal: bool


@dc.dataclass(frozen=True)
class ConfluenceConfig:
	url: str
	username: str | None = None
	password: str | None = None
	token: str | None = None


class _ConfluenceSynchronizerSession(observer.Observable):
	_datetime_parser = dt.datetime.fromisoformat
	_logger = logging.getLogger('confluence-sync')

	def __init__(
		self,
		*,
		executor: futures.ThreadPoolExecutor,
		src_cli: CustomConfluence,
		dst_cli: CustomConfluence,
		src_space: str | None = None,
		src_title: str | None = None,
		src_id: str | None = None,
		dst_space: str | None = None,
		dst_title: str | None = None,
		dst_id: str | None = None,
		sync_out_hierarchy: bool = False,
		replace_title_substr: tuple[str, str] | None = None,
		start_title_with: str | None = None,
	):
		super().__init__()

		# THREADING
		self._executor = executor
		self._lock = threading.Lock()
		self._futures = []

		# CLIENTS
		self._src_cli = src_cli
		self._dst_cli = dst_cli

		# PAGES and SPACES
		if src_id is None:
			self._src_space = src_space
			self._src_page = self._src_cli.get_page_by_title_or_homepage(src_space, src_title, expand='body.storage,ancestors')
		else:
			self._src_page = self._src_cli.get_page_by_id(src_id, expand='body.storage,ancestors,space')
			self._src_space = self._src_page['space']['key']

		if dst_id is None:
			self._dst_page = self._dst_cli.get_page_by_title_or_homepage(dst_space, dst_title)
			self._dst_space = dst_space
		else:
			self._dst_page = self._dst_cli.get_page_by_id(dst_id, expand='space')
			self._dst_space = self._dst_page['space']['key']

		self._sync_out_hierarchy = sync_out_hierarchy

		# PAGE INDEX
		descendant_pages = self._src_cli.traverse_descendant_pages(self._src_page['id'])

		self._page_index = context.PageIndex()
		for page in it.chain((self._src_page,), descendant_pages):
			self._page_index.add_page(
				context.Page(
					src_id=page['id'],
					src_space=self._src_space,
					src_title=page['title']
				)
			)

		# FORMATTERS
		self._title_formatter = fmt.title_formatter(
			replace_title_substr,
			start_title_with,
			self._src_space if sync_out_hierarchy else None,
		)

		if sync_out_hierarchy:
			self._page_title_formatter = fmt.PageTittleFormatter(self._title_formatter, self._src_space, self._dst_space)
			self._out_hierarchy_title_keeper = fmt.OutHierarchyPageTitleKeeper(self._page_index, self._src_space)
			self._out_hierarchy_title_checker = None
		else:
			self._page_title_formatter = fmt.HierarchyPageTittleFormatter(
				self._title_formatter,
				self._page_index,
				self._src_space,
				self._dst_space,
			)

			self._out_hierarchy_title_keeper = None
			self._out_hierarchy_title_checker = fmt.OutHierarchyPageTitleChecker(self._page_index, self._src_space)

		self._inc_drawio_formatter = fmt.IncDrawIOFormatter(self._src_cli, self._dst_cli, self._page_index)

		# STATS
		self._total_page_count = 0
		self._synced_paged_count = 0

	def _run_task(self, fn, *args, **kwargs) -> None:
		ft = self._executor.submit(fn, *args, **kwargs)
		self._futures.append(ft)

	def _wait_tasks(self) -> None:
		done, _ = futures.wait(self._futures, return_when=futures.FIRST_EXCEPTION)

		# We need to get the result so that errors in the child thread are thrown in the main thread.
		for ft in done:
			ft.result()

		self._futures.clear()

	def _init_stats(self, total_page_count: int) -> None:
		"""Initialize statistics values."""
		self._inc_total_page_count(total_page_count)

	def _inc_synced_page_count(self, n: int = 1) -> None:
		"""Increase the count of synced pages."""
		with self._lock:
			self._synced_paged_count += n

		self.notify(events.SyncedPageCountChanged(self._synced_paged_count))

	def _inc_total_page_count(self, n: int) -> None:
		"""Increase the number of pages to be synced."""
		with self._lock:
			self._total_page_count += n

		self.notify(events.TotalPageCountChanged(self._total_page_count))

	def run(self) -> None:
		self._init_stats(self._page_index.count)
		self._sync_hierarchy(self._src_page, self._dst_page)

		if self._sync_out_hierarchy:
			self._sync_out_hierarchy_pages()

		self._sync_inc_drawio()

	# FIXME: it doesn't work with some macros, for example, the 'Page tree' macro
	def _sync_out_hierarchy_pages(self):
		pages = [
			self._out_hierarchy_title_keeper.pages.pop()
			for _ in range(len(self._out_hierarchy_title_keeper.pages))
		]

		space_roots: dict[str, tree.Node] = collections.defaultdict(tree.Node[OutHierarchyPage])

		# Get all pages in the tree.
		while pages:
			space, title = pages.pop()
			try:
				page = self._src_cli.get_page_by_title(space, title, expand='ancestors,body.storage')
			# Keep syncing even if ‘included page’ values are incorrect.
			except errors.ApiPermissionError:
				self._logger.error('Get out hierarchy page, space="%s", title="%s"', space, title)

				continue

			# Skip ancestor pages
			cur_node = space_roots[space]

			ancestors = page['ancestors']
			# Skip homepage
			ancestors = ancestors[1:] if len(ancestors) > 0 else ancestors

			for ancestor in ancestors:
				ancestor_node = cur_node.find_child_by(key=lambda d: d.title == ancestor['title'])

				if not ancestor_node:
					ancestor_node = tree.Node(OutHierarchyPage(title=ancestor['title'], nominal=True))
					cur_node.add_child(ancestor_node)

				cur_node = ancestor_node

			# Add page itself
			page_node = tree.Node(OutHierarchyPage(title=title, nominal=False))
			cur_node.add_child(page_node)

			page_context = context.Page(src_id=page['id'], src_space=space, src_title=title)
			self._page_index.add_page(page_context)

			# Get page dependencies
			self._out_hierarchy_title_keeper._src_space = space
			fmt.format_page(
				context.Page(src_id=page['id'], src_space=space, src_title=page['title']),
				page['body']['storage']['value'],
				(self._out_hierarchy_title_keeper,),
			)

			while self._out_hierarchy_title_keeper.pages:
				space, title = self._out_hierarchy_title_keeper.pages.pop()
				space_root = space_roots[space]
				page_node = space_root.find_descendant_by(key=lambda d: d.title == title)

				if page_node:
					if page_node.data.nominal:
						page_node.data.nominal = False
						# The page is fully copied and added to the index to prevent duplicates in _out_hierarchy_title_keeper
						ext_page = self._src_cli.get_page_by_title(space, title)
						page_context = context.Page(src_id=ext_page['id'], src_space=space, src_title=title)
						self._page_index.add_page(page_context)
					else:
						continue

				pages.append((space, title))

		total_count = 0
		for space_root in space_roots.values():
			# Go through the entire tree
			descendants_count = space_root.descendants_count

			self._inc_total_page_count(descendants_count)
			total_count += descendants_count

		self._logger.info('Syncing out hierarchy pages, page count: %d', total_count)

		page_formatters = (
			self._page_title_formatter,
			self._inc_drawio_formatter,
		)

		for space, space_root in space_roots.items():
			dst_parent_page_id = self._dst_page['id']

			pages_to_sync = queue.SimpleQueue()

			# tuple(nodes, dst_page_id)
			pages_to_sync.put((space_root.children(), dst_parent_page_id))

			while not pages_to_sync.empty():
				nodes, dst_parent_page_id = pages_to_sync.get()

				for node in nodes:
					page = self._src_cli.get_page_by_title(space, node.data.title, expand='body.storage')

					page_context = self._page_index.search_by_title(space, page['title'])
					# Pages not in the index are considered nominal.
					# Nominal pages shouldn’t be in the index, so any draw.io diagrams they contain as a source won’t be referenced.
					if page_context is None:
						page_context = context.Page(src_id=page['id'], src_space=space, src_title=page['title'])

					dst_page_id = self._sync_page(page_context, page_formatters, page, dst_parent_page_id, node.data.nominal)
					pages_to_sync.put((node.children(), dst_page_id))

	def _sync_hierarchy(self, src_page: StrDict, dst_page: StrDict) -> None:
		if self._sync_out_hierarchy:
			page_formatters = (
				self._out_hierarchy_title_keeper,
				self._page_title_formatter,
				self._inc_drawio_formatter,
			)
		else:
			page_formatters = (
				self._out_hierarchy_title_checker,
				self._page_title_formatter,
				self._inc_drawio_formatter,
			)

		pages_to_sync = queue.SimpleQueue()

		# tuple(iterable of source pages, parent_page_id)
		pages_to_sync.put(((src_page,), dst_page['id']))

		def _task(_src_page: StrDict, _dst_parent_page_id: str) -> None:
			page_context = self._page_index.search_by_id(_src_page['id'])

			dst_page_id = self._sync_page(
				page_context,
				page_formatters,
				_src_page,
				_dst_parent_page_id,
			)

			src_child_pages = self._src_cli.get_page_child_by_type(_src_page['id'], expand='body.storage')
			pages_to_sync.put((src_child_pages, dst_page_id))

		while not pages_to_sync.empty():
			src_pages, dst_parent_page_id = pages_to_sync.get()

			for src_page in src_pages:
				self._run_task(_task, src_page, dst_parent_page_id)

			self._wait_tasks()

	def _sync_page(
		self,
		page_context: context.Page,
		page_formatters: tp.Iterable[fmt.TagFormatter],
		src_page: StrDict,
		dst_parent_page_id: str,
		nominal: bool = False,
	) -> str:
		"""Copy page."""
		dst_page_id, dst_page_title = self._sync_body(
			page_context,
			page_formatters,
			src_page,
			dst_parent_page_id,
			nominal,
		)

		if not nominal:
			self._sync_attachments(page_context.src_id, dst_page_id, dst_page_title)

		self._logger.info('Page synced, "%s"', src_page['title'])
		self._inc_synced_page_count()

		return dst_page_id

	def _sync_body(
		self,
		page_context: context.Page,
		page_formatters: tp.Iterable[fmt.TagFormatter],
		src_page: StrDict,
		dst_page_parent_id: str,
		nominal: bool = False,
	) -> tuple[str, str]:
		"""Copy page text."""
		old_title = page_context.src_title
		old_body = src_page['body']['storage']['value']

		new_title = self._title_formatter(page_context.src_space, old_title)

		# If a nominal page is needed, and it already exists, skip it
		if nominal:
			dst_page = self._dst_cli.get_page_by_title(self._dst_space, new_title)

			if not dst_page:
				new_body = 'Nominal page that keeps the tree structure'
				dst_page = self._dst_cli.create_page(self._dst_space, new_title, new_body, dst_page_parent_id)
		else:
			new_body = fmt.format_page(page_context, old_body, page_formatters)
			dst_page = self._dst_cli.get_page_by_title(self._dst_space, new_title, expand='ancestors')

			if dst_page:
				# If the page exists and the content hasn’t changed, simply move it.
				if self._dst_cli.is_page_content_is_already_updated(dst_page['id'], new_body, new_title):
					cur_dst_page_parent_id = dst_page['ancestors'][-1].get('id')

					if cur_dst_page_parent_id and cur_dst_page_parent_id != dst_page_parent_id:
						self._dst_cli.move_page(self._dst_space, dst_page['id'], dst_page_parent_id)
				else:
					dst_page = self._dst_cli.update_page(
						page_id=dst_page['id'],
						title=new_title,
						body=new_body,
						parent_id=dst_page_parent_id,
					)
			else:
				dst_page = self._dst_cli.create_page(
					space=self._dst_space,
					title=new_title,
					body=new_body,
					parent_id=dst_page_parent_id,
				)

		page_context.dst_id = dst_page['id']

		self._logger.info('Page body synced, "%s"', old_title)

		return dst_page['id'], dst_page['title']

	def _sync_attachments(self, src_page_id: str, dst_page_id: str, dst_page_title: str | None = None) -> None:
		"""Copy page attachments."""
		src_attachments = self._src_cli.traverse_page_attachments(
			src_page_id,
			expand='history.lastUpdated'
		)

		self._copy_attachments(src_attachments, dst_page_id, dst_page_title)

	def _copy_attachments(
		self,
		src_attachments: tp.Iterable[StrDict],
		dst_page_id: str,
		dst_page_title: str | None = None
	) -> None:
		"""Copy page attachments to the destination page."""
		dst_attachments = self._dst_cli.traverse_page_attachments(dst_page_id, expand='history.lastUpdated')
		dst_attachments_map = {attachment['title']: attachment for attachment in dst_attachments}

		for src_attachment in src_attachments:
			dst_attachment = dst_attachments_map.get(src_attachment['title'])
			self._copy_attachment_only_updated(
				src_attachment,
				dst_attachment,
				dst_page_id,
				dst_page_title
			)

	def _copy_attachment_only_updated(
		self,
		src_attachment: StrDict,
		dst_attachment: StrDict | None,
		dst_page_id: str,
		dst_page_title: str | None = None,
	) -> None:
		"""Copy an attachment.

		Copy the attachment only if it’s new or its content has changed since the last copy.
		"""
		if dst_attachment:
			src_attachment_last_updated = self._datetime_parser(src_attachment['history']['lastUpdated']['when'])
			dst_attachment_last_updated = self._datetime_parser(dst_attachment['history']['lastUpdated']['when'])

			if dst_attachment_last_updated >= src_attachment_last_updated:
				self._logger.warning(
					'Attachment "%s" already copied, page: "%s"',
					src_attachment['title'],
					dst_page_title or dst_page_id
				)

				return

		self._run_task(self._copy_attachment, src_attachment, dst_page_id, dst_page_title)

	def _copy_attachment(
		self,
		src_attachment: StrDict,
		dst_page_id: str,
		dst_page_title: str | None = None,
	) -> None:
		title = src_attachment['title']

		download_url = src_attachment['_links']['download']
		content = self._src_cli.get(download_url, not_json_response=True)

		# For some reason, it gives a 503 HTTP status code without a lock, but the Confluence log shows 403
		with self._lock:
			self._dst_cli.attach_content(
				content,
				page_id=dst_page_id,
				title=title,
				name=title,
				comment=src_attachment['metadata'].get('comment'),
			)

		self._logger.info('Attachment "%s" copied, page: "%s"', title, dst_page_title or dst_page_id)

	def _sync_inc_drawio(self) -> None:
		self._logger.info(
			'Fixing pages with included drawio diagrams, page count: %d',
			self._inc_drawio_formatter.delayed_pages_count
		)

		self._inc_synced_page_count(-self._inc_drawio_formatter.delayed_pages_count)

		for src_page_id, body, attachments, comment in self._inc_drawio_formatter.process_delayed_pages():
			page_context = self._page_index.search_by_id(src_page_id)

			new_title = self._title_formatter(page_context.src_space, page_context.src_title)

			self._dst_cli.update_page(
				page_id=page_context.dst_id,
				title=new_title,
				body=body,
				version_comment=comment
			)

			attachments = it.chain.from_iterable(
				self._src_cli.get_attachment_by_names(
					ref_page_id,
					attachment_names,
					expand='history.lastUpdated',
				)

				for ref_page_id, attachment_names
				in attachments.items()
			)

			attachments = list(attachments)

			self._copy_attachments(attachments, page_context.dst_id, new_title)
			self._wait_tasks()

			self._logger.info('Included drawio diagram was fixed, page: "%s"', new_title)
			self._inc_synced_page_count()


class ConfluenceSynchronizer:
	def __init__(self, src_conf: ConfluenceConfig, dst_conf: ConfluenceConfig) -> None:
		super().__init__()

		self._src_conf = src_conf
		self._dst_conf = dst_conf

		self._src_cli: CustomConfluence | None = None
		self._dst_cli: CustomConfluence | None = None

		self._executor = futures.ThreadPoolExecutor()

		self._opened = False

	def __enter__(self) -> 'ConfluenceSynchronizer':
		self._ensure_closed()

		self._src_cli = CustomConfluence(**dc.asdict(self._src_conf))
		self._dst_cli = CustomConfluence(**dc.asdict(self._dst_conf))
		self._executor = self._executor.__enter__()

		self._opened = True

		return self

	def __exit__(self, *args) -> None:
		self._ensure_opened()

		self._executor.__exit__(*args)
		self._src_cli.close()
		self._dst_cli.close()

	def _ensure_opened(self) -> None:
		if not self._opened:
			raise ValueError('ConfluenceSynchronizer must be entered')

	def _ensure_closed(self) -> None:
		if self._opened:
			raise ValueError('ConfluenceSynchronizer must be closed')

	def sync_page_hierarchy(
		self,
		src_space: str | None,
		src_title: str | None,
		src_id: str | None,
		dst_space: str | None,
		dst_title: str | None,
		dst_id: str | None,
		*,
		sync_out_hierarchy: bool = False,
		replace_title_substr: tuple[str, str] | None = None,
		start_title_with: str | None = None,
	) -> _ConfluenceSynchronizerSession:
		"""Copy all pages in the tree hierarchy.

		:param src_space: source page space
		:param src_title: source page title
		:param src_id: source page id
		:param dst_space: destination page space
		:param dst_title: destination page title
		:param dst_id: destination page id
		:param sync_out_hierarchy: copy the page outside the target hierarchy
		:param replace_title_substr: change part of page titles to a new value
		:param start_title_with: add prefix to page title
		:return: page copying session
		"""
		self._ensure_opened()

		return _ConfluenceSynchronizerSession(
			executor=self._executor,
			src_cli=self._src_cli,
			dst_cli=self._dst_cli,
			src_space=src_space,
			src_title=src_title,
			src_id=src_id,
			dst_space=dst_space,
			dst_title=dst_title,
			dst_id=dst_id,
			sync_out_hierarchy=sync_out_hierarchy,
			replace_title_substr=replace_title_substr,
			start_title_with=start_title_with,
		)


def get_page(
	cli: CustomConfluence,
	page_space: str,
	page_id: str | None = None,
	page_title: str | None = None,
	expand: tp.Any = None
) -> StrDict:
	if page_id:
		return cli.get_page_by_id(page_id, expand=expand)
	if page_title:
		return cli.get_page_by_title(page_space, page_title, expand=expand)
	else:
		dst_space_data = cli.get_space(page_space)
		return cli.get_page_by_id(dst_space_data['homepage']['id'], expand)
