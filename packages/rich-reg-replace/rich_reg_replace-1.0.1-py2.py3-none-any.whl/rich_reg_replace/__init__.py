#  rich_reg_replace/__init__.py
#
#  Copyright 2025 Leon Dionne <ldionne@dridesign.sh.cn>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
"""
Search and replace using regular expressions with a "rich" frontend.

By default, only files with the following extensions are searched:

	.php .css .js .ui .py .toml .conf
"""

__version__ = "1.0.1"

import sys, logging, argparse, re
from time import sleep
from os import walk, getcwd
from os.path import isdir, isfile, join, splitext, basename
from glob import iglob as glob
from rich.console import Console, Group, group
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich.prompt import Prompt
from rich.panel import Panel
from rich.align import Align
from rich.style import Style
from rich.styled import Styled

PROMPT = '[y]es, [n]o, [s]kip file, all in [f]ile, all in [e]very file, [q]uit (ENTER for no)'
DEFAULT_EXTENSIONS = ['.php', '.css', '.js', '.ui', '.py', '.toml', '.conf']
SKIP_DIRS = ['.git', 'venv']
SKIP_FILES = []
TAB_SIZE = 4
INFO = 0
WARNING = 1
ERROR = 2
MESSAGE_DURATION = 1.0
ERROR_MESSAGE_DURATION = 3.0


class Replacer:

	def __init__(self, options):
		self.options = options
		self.bright_style = Style(bgcolor = 'dark_sea_green1', color = 'black')
		self.message_style = {
			INFO: Style(bgcolor = 'dark_sea_green4', color = 'bright_white'),
			WARNING: Style(bgcolor = 'orange3', color = 'bright_white'),
			ERROR: Style(bgcolor = 'red', color = 'bright_white')
		}
		self.match_style = Style(color = 'red', bold = True)
		self.repl_style = Style(bold = True)
		self.current_line = Style(bgcolor = 'khaki1')
		self.console = Console(highlight = False, tab_size = TAB_SIZE)
		self.preview_height = self.console.height - 6
		self.centerline = self.preview_height // 2
		self.live = Live(console = self.console, auto_refresh = False)
		self.layout = Layout()
		self.layout.split(
			Layout(name = 'preview', size = self.preview_height),
			Layout(name = 'repl', size = 4),
			Layout(name = 'prompt', size = 1)
		)
		self.layout['preview'].update(Panel(''))
		self.empty_repl = Panel('', title = 'Replacement')
		self.layout['repl'].update(self.empty_repl)
		self.live.update(self.layout)
		self.live.refresh()
		self.pattern = re.compile(self.options.SearchPattern)
		self.replacement = self.options.Replacement
		self.prompt_all = True
		self.prompt = Align(self.prompt_text(), align = 'center')
		self.change_count = 0

	def run(self):
		with self.console.screen(hide_cursor = True):
			self.live.start()
			self.process_paths()
			self.live.stop()
		if self.change_count == 0:
			print(' No files changed')
		elif self.change_count == 1:
			print(' 1 file changed')
		else:
			print(f' {self.change_count} files changed')

	def process_paths(self):
		paths = self.options.Filename or [ getcwd() ]
		for path in paths:
			if isfile(path) and not basename(path) in SKIP_FILES:
				if self.process_file(path): return
			elif isdir(path) and not basename(path) in SKIP_DIRS:
				if self.process_dir(path): return
			else:
				self.show_message(f'"{path}" is not a file. ', WARNING)

	def process_dir(self, dirname):
		for path in glob(join(dirname, '*')):
			if isfile(path) and not basename(path) in SKIP_FILES:
				_, ext = splitext(path)
				if ext in DEFAULT_EXTENSIONS:
					if self.process_file(path):	# Returns True to signal exit
						return True				# Signal exit
			elif isdir(path) and self.options.recurse and not basename(path) in SKIP_DIRS:
				if self.process_dir(path):		# Returns True to signal exit
					return True					# Signal exit

	def process_file(self, filename):
		try:
			with open(filename, 'r') as fob:
				self.lines = {lineno:line for lineno, line in enumerate(fob)}
		except UnicodeDecodeError:
			self.show_message(f'Could not decode "{filename}"', ERROR)
			return False	# Signals not to exit

		self.matched_lines = [ lineno for lineno, line in self.lines.items() \
			if self.pattern.search(line) ]
		if len(self.matched_lines) == 0:
			return False	# Signals not to exit

		preview_title = Text(filename, style = self.bright_style)
		if self.prompt_all:
			prompt_in_file = self.prompt_all
			changed = False
			for lineno in self.matched_lines:
				change = self.pattern.sub(self.replacement, self.lines[lineno])
				if prompt_in_file:
					self.layout['preview'].update(Panel(
						self.preview(lineno), title = preview_title))
					self.layout['repl'].update(Panel(Group(
						self.highlight_line(lineno),
						Text(change.rstrip(), style = self.repl_style)
					), title = 'Replacement'))
					while True:
						self.layout['prompt'].update(self.prompt)
						self.live.refresh()
						try:
							ans = Prompt.ask(password = True)
						except KeyboardInterrupt:
							return True	# Signals to exit
						if ans in ('y', 'r'):	# [y]es, [r]eplace
							self.lines[lineno] = change
							changed = True
							break
						elif ans in ('n', ''):	# [n]o, default
							break
						elif ans == 's':		# [s]kip file
							return False		# Signals not to exit
						elif ans == 'f':		# all in [f]ile
							self.lines[lineno] = change
							changed = True
							prompt_in_file = False
							break
						elif ans == 'e':		# all in [e]very file
							self.lines[lineno] = change
							changed = True
							prompt_in_file = False
							self.prompt_all = False
							break
						elif ans == 'q':		# [q]uit
							return True			# Signals to exit
						else:
							self.show_message(
								'Please enter one of "y", "n", "s", "f", "q", or "e"',
								WARNING
							)
				else:
					self.lines[lineno] = change
					changed = True
			self.layout['preview'].update(Panel(
				self.preview(lineno), title = preview_title))
			self.layout['repl'].update(self.empty_repl)
		else:
			self.layout['preview'].update(Panel('', title = preview_title))
			self.layout['repl'].update(self.empty_repl)
			self.layout['prompt'].update('')
			self.live.refresh()
			for lineno in self.matched_lines:
				self.lines[lineno] = self.pattern.sub(self.replacement, self.lines[lineno])
			changed = True
		if changed:
			try:
				with open(filename, 'w') as fob:
					for line in self.lines.values():
						fob.write(line)
			except OSError as e:
				self.show_message(str(e), ERROR)
			else:
				self.change_count += 1
				if self.prompt_all:
					self.show_message('CHANGED')
		else:
			self.show_message('unchanged')
		return False	# Signals not to exit

	@group()
	def preview(self, selected_line):
		first_line = max(0, selected_line - self.centerline)
		last_line = min(first_line + self.preview_height, len(self.lines))
		for lineno in range(first_line, last_line):
			if lineno in self.matched_lines:
				yield Styled(self.highlight_line(lineno),
					style = self.current_line) \
					if lineno == selected_line \
					else self.highlight_line(lineno)
			else:
				yield self.lines[lineno].rstrip()

	@group()
	def highlight_line(self, lineno):
		rline = self.lines[lineno].rstrip()
		last_end = 0
		for m in self.pattern.finditer(rline):
			start, end = m.span()
			yield Text(rline[last_end:start], end = '')
			yield Text(rline[start:end], style = self.match_style, end = '')
			last_end = end
		yield Text(rline[last_end:])

	@group()
	def prompt_text(self):
		for part in PROMPT.split('['):
			if part:
				key, text = part.split(']')
				yield Text('[', end = '')
				yield Text(key, style = self.bright_style, end = ']')
				yield Text(text, end = '')

	def show_message(self, message, level = INFO):
		self.layout['prompt'].update(Align(
			message, style = self.message_style[level], align = 'center'))
		self.live.refresh()
		sleep(MESSAGE_DURATION if level < ERROR else ERROR_MESSAGE_DURATION)


def main():
	p = argparse.ArgumentParser()
	p.add_argument('SearchPattern', type = str,
		help = 'Regular expression to search for')
	p.add_argument('Replacement', type = str,
		help = 'Replacement string. May contain references to captured subpatterns')
	p.add_argument('Filename', type = str, nargs = '*')
	p.add_argument('-r', '--recurse', action = "store_true")
	p.epilog = __doc__
	logging.basicConfig(
		level = logging.DEBUG,
		format = '[%(filename)24s:%(lineno)3d] %(message)s'
	)
	Replacer(p.parse_args()).run()


if __name__ == '__main__':
	main()


#  rich_reg_replace/__init__.py
