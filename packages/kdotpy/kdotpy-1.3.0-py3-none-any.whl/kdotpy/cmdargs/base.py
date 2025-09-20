# kdotpy - k·p theory on a lattice for simulating semiconductor band structures
# Copyright (C) 2024, 2025 The kdotpy collaboration <kdotpy@uni-wuerzburg.de>
#
# SPDX-License-Identifier: GPL-3.0-only
#
# This file is part of kdotpy.
#
# kdotpy is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, version 3.
#
# kdotpy is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# kdotpy. If not, see <https://www.gnu.org/licenses/>.
#
# Under Section 7 of GPL version 3 we require you to fulfill the following
# additional terms:
#
#     - We require the preservation of the full copyright notice and the license
#       in all original files.
#
#     - We prohibit misrepresentation of the origin of the original files. To
#       obtain the original files, please visit the Git repository at
#       <https://git.physik.uni-wuerzburg.de/kdotpy/kdotpy>
#
#     - As part of a scientific environment, we believe it is reasonable to
#       expect that you follow the rules of good scientific practice when using
#       kdotpy. In particular, we expect that you credit the original authors if
#       you benefit from this program, by citing our work, following the
#       citation instructions in the file CITATION.md bundled with kdotpy.
#
#     - If you make substantial changes to kdotpy, we strongly encourage that
#       you contribute to the original project by joining our team. If you use
#       or publish a modified version of this program, you are required to mark
#       your material in a reasonable way as different from the original
#       version.

import sys
import shlex

from .tools import remove_underscores, is_kdotpy_cmd, isint, isfloat

# Mark some command-line arguments as parsed at initialization of sysargv (the
# global CmdArgs instance), regardless of whether they are actively used. This
# is done for the 'verbose' argument (parsed at initialization) as well as for
# 'showetf' and 'monitoretf', for which it is irrelevant whether they are parsed
# or not. Previously, more arguments were on this list, when they were parsed
# from sys.argv instead of sysargv, because importing from cmdargs module was
# too cumbersome. The latter case should no longer occur in version v1.3.x and
# newer.
set_parsed_cmds = ['verbose', 'showetf', 'monitoretf']

class CmdArgs(object):
	"""Container class that tracks parsing of command-line arguments ('rich sys.argv').

	Attributes:
	argv       List of strings. Arguments 'as is'
	argvlower  List of strings. Lower case arguments with underscores removes
	           (for case insensitive comparisons).
	isparsed   List of boolean values with the same length as argv. For each
	           argument, whether it has been parsed.
	verbose    True or False. Whether 'verbose' is in the argument list.
	idx        Index of the most recently parsed argument.
	idx_start  Index of the first argument that is not a command or script name.
	"""
	def __init__(self, args=None):
		self.argv = []
		self.argvlower = []
		self.isparsed = []
		self.verbose = False
		self.idx = 0
		self.idx_start  = 0
		self.initialize(args=args)

	def initialize(self, args=None):
		if args is None:
			self.argv = sys.argv
		elif isinstance(args, (list, tuple)):
			self.argv = list(args)
		else:
			raise TypeError("Argument 'args' must be a list, tuple, or None")
		self.argvlower = [remove_underscores(arg.lower()) for arg in self.argv]
		self.isparsed = [(a in set_parsed_cmds) for a in self.argv]
		self.verbose = 'verbose' in self.argvlower
		self.idx = 0  # Index reset
		self.idx_start = 0
		if len(self.argv) >= 2:
			is_kdotpy = is_kdotpy_cmd(self.argv)
			self.isparsed[0] = is_kdotpy
			self.isparsed[1] = is_kdotpy
			self.idx_start = 2 if is_kdotpy else 0
		for argi, arg in enumerate(self.argvlower[:-1]):
			if arg == 'config':
				self.isparsed[argi] = True
				self.isparsed[argi + 1] = True

	def __iter__(self):
		"""Raw iterator"""
		return iter(self.argv)

	def iter_enumerate(self):
		"""Iterate over index, original arguments, lower case arguments"""
		return iter(zip(range(self.idx_start, len(self.argv)), self.argv[self.idx_start:], self.argvlower[self.idx_start:]))

	def __getitem__(self, i):
		return self.argv[i]

	def __len__(self):
		return len(self.argv)

	def setparsed(self, what, value = True):
		"""Mark arguments (un)parsed

		Arguments:
		what     Integer, slice, or string. Which argument to mark. If a string,
		         mark all instances of the string (case insensitive match).
		value    True, False, or None. Target value, True means parsed, False
		         means not parsed, None means do not mark.
		"""
		if value is None:
			return
		if isinstance(what, int):
			self.isparsed[what] = value
			self.idx = what
		elif isinstance(what, slice):
			for i in range(0, len(self.argv))[what]:
				self.isparsed[i] = value
				self.idx = i
		elif isinstance(what, str):
			for i, a in enumerate(self.argvlower):
				if a == what.lower():
					self.isparsed[i] = value
					self.idx = i
		else:
			raise TypeError("Argument 'what' must be an integer, slice, or string.")

	def setparsednext(self, n, value = True):
		"""Mark next arguments (un)parsed.

		Arguments:
		n      Number of arguments to mark, starting at the argument following
		       the previously marked argument.
		value  True, False, or None. Target value, True means parsed, False
		       means not parsed, None means do not mark.
		"""
		if value is None:
			return
		if not isinstance(n, int):
			raise TypeError("Argument 'n' must be an integer.")
		end = min(self.idx + 1 + n, len(self.argv))
		for i in range(self.idx + 1, end):
			self.isparsed[i] = value
		self.idx = end - 1

	def unparsed_warning(self, color = True):
		"""Get a pretty string for non-parsed arguments.
		Call this at the end of the program."""
		if len(self.argv) <= 2:
			return None
		if all(self.isparsed):
			return None
		s = f"[{self.argv[0]}]" if self.idx_start > 0 else f"{self.argv[0]}"
		s += f" {self.argv[1]}"
		if color:
			for isp, arg in zip(self.isparsed[2:], self.argv[2:]):
				if not isp:
					s += " \x1b[1;31m" + shlex.quote(arg) + "\x1b[0m"
				else:
					s += " " + shlex.quote(arg)
		else:
			for j in range(2, len(self.argv)):
				if not self.isparsed[j]:
					if self.isparsed[j-1]:
						s += ' ... ' + shlex.quote(self.argv[j])
					else:
						s += ' ' + shlex.quote(self.argv[j])
			if self.isparsed[-1]:
				s += ' ...'
		return s

	def has(self, arg, setparsed = True):
		"""Return whether arg is in the list of arguments.
		Comparison is case insensitive.

		Arguments:
		arg         Value to test
		setparsed   True or False. Whether to mark the argument as parsed.

		Returns:
		True or False
		"""
		if setparsed and arg.lower() in self.argvlower:
			self.setparsed(arg)
		return arg.lower() in self.argvlower

	def __contains__(self, arg):
		return self.has(arg)

	def index(self, arg):
		return self.argvlower.index(arg.lower())

	def getval(self, arg, n=1, mark = True):
		"""Get value for 'arg value' in argument sequence self.argv

		Arguments:
		arg    String or list of strings. The command-line argument(s) that
			   match(es).
		n      Integer. Number of values after the command-line argument 'arg
		       that will be returned. If self.argv is not long enough, then
		       return all values till the end of self.argv.
		mark   True, False, or None. If True or False, mark this argument parsed
		       or not parsed, respectively. If None, do not mark.

		Returns:
		values       String (n=1), list of strings (n>1) or None (if the
		             matching argument is the last in self.argv).
		matched_arg  The command-line argument that matches.
		"""
		if isinstance(arg, str):
			for i in range(2, len(self.argv)):
				if self.argvlower[i] == arg:
					self.setparsed(i, value = mark)
					if i == len(self.argv) - 1:
						return None, self.argv[i]
					elif n <= 1:
						self.setparsednext(1, value = mark)
						return self.argv[i+1], self.argv[i]
					elif i + 1 + n < len(self.argv):
						self.setparsednext(n, value = mark)
						return self.argv[i+1:i+1+n], self.argv[i]
					else:
						self.setparsednext(n, value = mark)
						return self.argv[i+1:], self.argv[i]
		elif isinstance(arg, list):
			for i in range(2, len(self.argv)):
				if self.argvlower[i].lower() in arg:
					self.setparsed(i, value = mark)
					if i == len(self.argv) - 1:
						return None, self.argv[i]
					elif n <= 1:
						self.setparsednext(1, value = mark)
						return self.argv[i+1], self.argv[i]
					elif i + 1 + n < len(self.argv):
						self.setparsednext(n, value = mark)
						return self.argv[i+1:i+1+n], self.argv[i]
					else:
						self.setparsednext(n, value = mark)
						return self.argv[i+1:], self.argv[i]
		return None, ""

	def getint(self, arg, default = None, limit = None):
		"""Get integer value in argument sequence self.argv

		Arguments:
		arg        String or list of strings
		default    Return value if arg is not found
		limit      None or 2-tuple. If set, a value less than the lower bound or
			       greater than the upper bound will raise an error.

		Returns:
		An integer
		"""
		retval = default
		val, arg = self.getval(arg)
		if val is None:
			pass
		elif isint(val):
			retval = int(val)
		else:
			sys.stderr.write("ERROR (cmdargs.getint): Invalid value for argument \"%s\"\n" % arg)
			exit(1)
		if retval is not None and isinstance(limit, list) and len(limit) == 2:
			if limit[0] is not None and retval < limit[0]:
				sys.stderr.write("ERROR (cmdargs.getint): Value for argument \"%s\" out of bounds\n" % arg)
				exit(1)
			if limit[1] is not None and retval > limit[1]:
				sys.stderr.write("ERROR (cmdargs.getint): Value for argument \"%s\" out of bounds\n" % arg)
				exit(1)
		return retval

	def getfloat(self, arg, default = None, limit = None):
		"""Get numeric (float) value in argument sequence self.argv

		Arguments:
		arg        String or list of strings
		default    Return value if arg is not found
		limit      None or 2-tuple. If set, a value less than the lower bound or
			       greater than the upper bound will raise an error.

		Returns:
		A float
		"""
		retval = default
		val, arg = self.getval(arg)
		if val is None:
			pass
		elif isfloat(val):
			retval = float(val)
		else:
			sys.stderr.write("ERROR (cmdargs.getfloat): Invalid value for argument \"%s\"\n" % arg)
			exit(1)
		if retval is not None and isinstance(limit, list) and len(limit) == 2:
			if limit[0] is not None and retval < limit[0] - 1e-9:
				sys.stderr.write("ERROR (cmdargs.getfloat): Value for argument \"%s\" out of bounds\n" % arg)
				exit(1)
			if limit[1] is not None and retval > limit[1] + 1e-9:
				sys.stderr.write("ERROR (cmdargs.getfloat): Value for argument \"%s\" out of bounds\n" % arg)
				exit(1)
		return retval

	def getfloats(self, arg, positive = False):
		"""Get a sequence of numeric (float) values in argument sequence self.argv
		Get all numeric values after the matching argument. If one argument
		appears repeatedly, concatenate all the values.

		Examples:
		'arg 1 2.0 -1.0 foo ...' yields [1.0, 2.0, -1.0]
		'arg 1 2.0 -1.0 foo ... arg 3 bar ...' yields [1.0, 2.0, -1.0, 3.0]

		Arguments:
		arg        String or list of strings
		positive   False or True. If True, negative values raise an error.

		Returns:
		A list of floats.
		"""
		if isinstance(arg, str):
			arg = [arg]
		elif not isinstance(arg, list):
			raise TypeError("arg must be a str or list instance")

		retval = []
		argn = 2
		while argn < len(self.argv):
			if self.argvlower[argn] in arg:
				arg_kw = self.argvlower[argn]
				self.setparsed(argn)
				while argn < len(self.argv):
					if argn + 1 >= len(self.argv):
						break
					try:
						arg1 = float(self.argv[argn+1])
					except:
						arg1 = None
					if arg1 is None:
						break
					self.setparsed(argn + 1)
					if positive and arg1 is not None and arg1 < 0.0:
						sys.stderr.write("ERROR (cmdargs.getfloats): Values for argument '%s' must not be negative.\n" % arg_kw)
						exit(1)
					retval.append(arg1)
					argn += 1
			argn += 1
		return retval

	def getval_after(self, idx):
		"""Get generic value coming after position idx and mark idx and idx + 1 parsed."""
		self.setparsed(idx)
		try:
			retval = self.argv[idx + 1]
		except:
			sys.stderr.write("ERROR (cmdargs.getval_after): Absent value for argument \"%s\"\n" % self.argv[idx])
			exit(1)
		else:
			self.setparsednext(1)
		return retval

	def getfloat_after(self, idx):
		"""Get numerical value coming after position idx and mark idx and idx + 1 parsed."""
		self.setparsed(idx)
		try:
			retval = float(self.argv[idx + 1])
		except:
			sys.stderr.write("ERROR (cmdargs.getfloat_after): Absent or invalid value for argument \"%s\"\n" % self.argv[idx])
			exit(1)
		else:
			self.setparsednext(1)
		return retval

	def to_str(self, shorten_kdotpy=False):
		"""Convert the present command line sequence into a command-line compatible string"""
		if shorten_kdotpy and is_kdotpy_cmd(self.argv):
			argv = ['kdotpy'] + self.argv[1:]
		else:
			argv = self.argv
		cmd_str = " ".join([shlex.quote(arg) for arg in argv])
		return cmd_str

### INITIALIZATION ###

# Initialize main list of arguments. The CmdArgs instance keeps track of which
# arguments have been parsed. The CmdArgs.__init__() function sets a few very
# common arguments as parsed already.
sysargv = CmdArgs(sys.argv)

def initialize(args=None):
	"""Reinitialize sysargv with a new set of variables or with sys.argv.

	Note: The existing instance, which is a global variable imported by other
	modules, is updated rather than being replaced. A new instance would not be
	visible to these other modules as the imported sysargv would still refer to
	the old instance.
	"""
	sysargv.initialize(args=args)

