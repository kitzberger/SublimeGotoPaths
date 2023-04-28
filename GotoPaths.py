import sublime
import sublime_plugin
import threading
import re

class GotoPaths(sublime_plugin.EventListener):

	PATH_REGEXS = [
		# Laravel blade templates
		"\'([a-z]+)::([a-zA-Z\.\-_]+)\'",
		"@(view|include)\(\'([a-zA-Z\.\-_]+)\'",
		# TYPO3 extension strings
		"\\bEXT:([A-Za-z0-9_\.\-\/]+)(\.[A-Za-z0-9]{2,4})?",
	]
	DEFAULT_MAX_URLS = 200
	SETTINGS_FILENAME = 'GotoPaths.sublime-settings'

	paths_for_view = {}
	scopes_for_view = {}
	ignored_views = []
	highlight_semaphore = threading.Semaphore()

	def on_activated(self, view):
		self.update_url_highlights(view)

	# Async listeners
	def on_load_async(self, view):
		self.update_url_highlights_async(view)

	def on_modified_async(self, view):
		self.update_url_highlights_async(view)

	def on_close(self, view):
		for map in [self.paths_for_view, self.scopes_for_view, self.ignored_views]:
			if view.id() in map:
				del map[view.id()]

	"""Same as update_url_highlights, but avoids race conditions with a semaphore."""
	def update_url_highlights_async(self, view):
		GotoPaths.highlight_semaphore.acquire()
		try:
			self.update_url_highlights(view)
		finally:
			GotoPaths.highlight_semaphore.release()

	"""The logic entry point. Find all URLs in view, store and highlight them"""
	def update_url_highlights(self, view):
		settings = sublime.load_settings(GotoPaths.SETTINGS_FILENAME)
		should_highlight_paths = settings.get('highlight_paths', True)
		max_url_limit = settings.get('max_url_limit', GotoPaths.DEFAULT_MAX_URLS)

		if view.id() in GotoPaths.ignored_views:
			return

		paths = []
		for pathRegex in GotoPaths.PATH_REGEXS:
			paths += view.find_all(pathRegex)
		print(paths)

		# Avoid slowdowns for views with too much paths
		if len(paths) > max_url_limit:
			print("GotoPaths: ignoring view with %u paths" % len(paths))
			GotoPaths.ignored_views.append(view.id())
			return

		GotoPaths.paths_for_view[view.id()] = paths

		should_highlight_paths = sublime.load_settings(GotoPaths.SETTINGS_FILENAME).get('highlight_paths', True)
		if (should_highlight_paths):
			self.highlight_paths(view, paths)

	"""Creates a set of regions from the intersection of paths and scopes, underlines all of them."""
	def highlight_paths(self, view, paths):
		print('Highlighting paths:')
		# We need separate regions for each lexical scope for ST to use a proper color for the underline
		scope_map = {}
		for path in paths:
			#print(path)
			href = view.substr(path)

			# Cleanups
			matches = re.match(r"(@(view|include)\()", href)
			if matches:
				#print(matches.group(1))
				beginOffset = len(matches.group(1))
				path.a += beginOffset
				href = view.substr(path)
			matches = re.match(r"'(.+)'", href)
			if matches:
				print(matches.group(1))
				path.a += 1
				path.b -= 1
				href = view.substr(path)

			print('Path: ' + str(path).rjust(16) + ' => ' + href)

			scope_name = view.scope_name(path.a)
			scope_map.setdefault(scope_name, []).append(path)

		for scope_name in scope_map:
			self.underline_regions(view, scope_name, scope_map[scope_name])

		self.update_view_scopes(view, scope_map.keys())

	"""Apply underlining with provided scope name to provided regions."""
	def underline_regions(self, view, scope_name, regions):
		# print('Underline regions: ' + scope_name)
		# print(regions)

		# https://www.sublimetext.com/docs/api_reference.html#sublime.View.add_regions
		view.add_regions(
			u'clickable-paths ' + scope_name,
			regions,
			"markup.underline.link", # markup.underline.link or region.redish
			flags=sublime.DRAW_NO_FILL|sublime.DRAW_NO_OUTLINE|sublime.DRAW_STIPPLED_UNDERLINE)

	"""Store new set of underlined scopes for view. Erase underlining from
	scopes that were used but are not anymore."""
	def update_view_scopes(self, view, new_scopes):
		old_scopes = GotoPaths.scopes_for_view.get(view.id(), None)
		if old_scopes:
			unused_scopes = set(old_scopes) - set(new_scopes)
			for unused_scope_name in unused_scopes:
				view.erase_regions(u'clickable-paths ' + unused_scope_name)

		GotoPaths.scopes_for_view[view.id()] = new_scopes

def open_path(path):
	print('You\'ve clicked on path: ' + path)
	path = path.replace('EXT:', '')
	path = re.sub(r"[:.]", '', path)
	pattern = '*' + path
	print('Try finding file(s) with pattern: ' + pattern)
	files = sublime.find_resources(pattern)
	if (len(files) == 1):
		sublime.active_window().open_file(files[0])
	else:
		sublime.active_window().run_command("show_overlay", {"overlay": "goto", "text": path})

class OpenPathUnderCursorCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if self.view.id() in GotoPaths.paths_for_view:
			selection = self.view.sel()[0]
			print(selection)
			if selection.empty():
				selection = next((path for path in GotoPaths.paths_for_view[self.view.id()] if path.contains(selection)), None)
				if not selection:
					return
			path = self.view.substr(selection)
			open_path(path)
