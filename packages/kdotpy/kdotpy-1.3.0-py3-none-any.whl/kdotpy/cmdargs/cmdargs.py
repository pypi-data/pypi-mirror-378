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

import numpy as np
import os
import os.path
import sys
import re
from datetime import datetime

from .tools import from_pct, format_string, find_in_tar, parse_direction
from .base import sysargv
from . import custom as customarg
from . import range as cmdargsrange


### MAIN ARGUMENT PARSERS ###
## May be called from elsewhere

def erange():
	"""Parse command-line arguments for energy range"""
	val, arg = sysargv.getval("erange", 2)
	if val is None:
		return [-100.0, 100.0]
	if isinstance(val, list) and len(val) in [1, 2]:
		try:
			e1 = float(val[0])
		except:
			sys.stderr.write("ERROR: Invalid value for argument \"%s\"\n" % arg)
			exit(1)
		try:
			e2 = float(val[1])
		except:
			e2 = -e1
		return [min(e1, e2), max(e1, e2)]
	sys.stderr.write("ERROR: Invalid value for argument \"%s\"\n" % arg)
	exit(1)

def vectorvalues(prefix = 'k', onedim = False, twodim = False, threedim = False, defaultaxis = 'x', magn_epsilon = None):
	"""Get vector values

	Arguments:
	prefix        'k', 'b', etc. Quantity. This will affect the command-line
	              arguments that match as well as the 'prefix' in the resulting
	              Vectors/VectorGrid.
	onedim, twodim, threedim    False or True. Whether a grid dimension of 1, 2,
	                            and 3 dimensions, respectively, are accepted.
	defaultaxis   'x', 'y', or 'z'. If a Vector with one component is input, how
	              to interpret it. For example, treat 'k' as 'kx' or 'b' as
	              'bz'.
	magn_epsilon  Float. If positive, add points with these values to a range of
	              magnetic field values, if the range contains zero. If
	              negative, only add these numbers if the range contains both
	              positive and negative values.

	Note:
	The dimensionality boolean values onedim and twodim should not be both
	False, and twodim must be True if threedim is True, i.e., combinations of
	dimensionalities allowed are 1, 1+2, 2, 2+3, 1+2+3.

	Exits on error.

	Returns:
	vg_args       Dict. The keyword arguments used for constructing a
	              VectorGrid instance using VectorGrid(**vg_args). If the
	              prefix does not match any command-line argument, then return
	              an empty dict {}.
	"""
	if not (onedim or twodim):
		raise ValueError("Arguments onedim and twodim should not be both False.")
	if (threedim and not twodim):
		raise ValueError("Argument twodim must be True if argument threedim is True.")
	ranges = {}
	components = ['', 'perp', 'x', 'y', 'z', 'phi', 'theta']
	for comp in components:
		try:
			vrange = cmdargsrange.grid(args = prefix + comp, from_argv = sysargv)
			if vrange is not None:
				ranges[comp] = vrange
		except:
			continue
		if prefix == 'b' and comp in ['', 'perp', 'x', 'y', 'z'] and vrange is not None and magn_epsilon is not None and magn_epsilon != 0.0:
			ranges[comp] = cmdargsrange.add_epsilon(vrange, magn_epsilon)

	if len(ranges) == 0:
		return {}

	if any(len(r) == 0 for r in ranges.values()):
		none_comp = [prefix + comp for comp, r in ranges.items() if len(r) == 0]
		comp_str = "component" + ("s" if len(none_comp) > 1 else "")
		sys.stderr.write("ERROR (cmdargs.vectorvalues): Missing value(s) for grid " + comp_str + " " + ", ".join(none_comp) + ".\n")
		exit(1)

	ranges_str = ", ".join([prefix + comp for comp in ranges])

	# Angular unit: degrees by default
	degrees = 'radians' not in sysargv

	# Directional
	dirval, dirarg = sysargv.getval(prefix + 'dir', 3)
	if dirval is not None:
		direction = parse_direction(dirval)
		if direction is None:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Invalid or missing argument following '{dirarg}'.\n")
			exit(1)
		if 'x' in ranges or 'y' in ranges or 'z' in ranges or 'perp' in ranges or 'phi' in ranges or 'theta' in ranges:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Argument {dirarg} may not be combined with other vector components other than {prefix} itself.\n")
			exit(1)
		dirx, diry, dirz = direction
		if dirx == 0 and diry == 0 and dirz == 0:
			sys.stderr.write("ERROR (cmdargs.vectorvalues): Singular direction vector.\n")
			exit(1)
		if not threedim and dirz != 0:
			sys.stderr.write("ERROR (cmdargs.vectorvalues): Direction vector must have zero z component in 2D mode.\n")
			exit(1)
		if threedim:
			return dict(r=ranges[''], direction=direction, prefix=prefix, astype='sph', deg=True)
		elif dirz != 0:
			sys.stderr.write("ERROR (cmdargs.vectorvalues): Direction vector must have zero z component in 1D or 2D mode.\n")
			exit(1)
		elif twodim:
			return dict(r=ranges[''], direction=direction, prefix=prefix, astype='pol', deg=True)
		elif diry != 0:
			sys.stderr.write("ERROR (cmdargs.vectorvalues): Direction vector must have zero y component in 1D.\n")
			exit(1)
		else:
			return dict(r=ranges[''], direction=direction, prefix=prefix, astype='x')

	# Valid combinations
	if not twodim:  # implies not threedim
		if 'perp' in ranges or 'y' in ranges or 'z' in ranges or 'phi' in ranges or 'theta' in ranges:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): The vector components {prefix}perp, {prefix}y, {prefix}z, {prefix}theta, {prefix}phi are not allowed in 1D mode.\n")
			exit(1)
		if 'x' in ranges and len(ranges) == 1:
			return dict(x=ranges['x'], prefix=prefix, astype='x')
		elif '' in ranges and len(ranges) == 1:
			return dict(x=ranges[''], prefix=prefix, astype='x')
		else:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): In 1D mode, the grid value(s) must be specified with either {prefix} or {prefix}x.\n")
			exit(1)

	if threedim and 'x' in ranges and 'y' in ranges and 'z' in ranges:
		if len(ranges) > 3:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Invalid combination of vector components {ranges_str}; perhaps you mean {prefix}x, {prefix}y, {prefix}z only.\n")
			exit(1)
		return dict(x=ranges['x'], y=ranges['y'], z=ranges['z'], prefix=prefix, astype='xyz')
	elif threedim and '' in ranges and 'phi' in ranges and 'z' in ranges:
		if len(ranges) > 3:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Invalid combination of vector components {ranges_str}; perhaps you mean {prefix}, {prefix}phi, {prefix}z only.\n")
			exit(1)
		return dict(r=ranges[''], phi=ranges['phi'], z=ranges['z'], prefix=prefix, astype='cyl', deg=degrees)
	elif threedim and 'x' in ranges and 'phi' in ranges and len(ranges['phi']) == 1 and 'z' in ranges:
		# r = x / cos phi
		if len(ranges) > 3:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Invalid combination of vector components {ranges_str}; perhaps you mean {prefix}x, {prefix}phi, {prefix}z only.\n")
			exit(1)
		phi = ranges['phi'][0]
		if degrees:
			phi *= np.pi / 180
		if abs(np.cos(phi)) < 1e-10:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Combination of components {prefix}x, {prefix}phi = {ranges['phi'][0]}, {prefix}z is singular.\n")
			exit(1)
		return dict(r=ranges['x'] / np.cos(phi), phi=ranges['phi'], z=ranges['z'], prefix=prefix, astype='cyl', deg=degrees)
	elif threedim and 'y' in ranges and 'phi' in ranges and len(ranges['phi']) == 1 and 'z' in ranges:
		# r = y / sin phi
		if len(ranges) > 3:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Invalid combination of vector components {ranges_str}; perhaps you mean {prefix}y, {prefix}phi, {prefix}z only.\n")
			exit(1)
		phi = ranges['phi'][0]
		if degrees:
			phi *= np.pi / 180
		if abs(np.sin(phi)) < 1e-10:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Combination of components {prefix}y, {prefix}phi = {ranges['phi'][0]}, {prefix}z is singular.\n")
			exit(1)
		return dict(r=ranges['y'] / np.sin(phi), phi=ranges['phi'], z=ranges['z'], prefix=prefix, astype='cyl', deg=degrees)

	elif threedim and '' in ranges and 'theta' in ranges and 'phi' in ranges:
		if len(ranges) > 3:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Invalid combination of vector components {ranges_str}; perhaps you mean {prefix}, {prefix}theta, {prefix}phi only.\n")
			exit(1)
		return dict(r=ranges[''], theta=ranges['theta'], phi=ranges['phi'], prefix=prefix, astype='sph', deg=degrees)
	elif threedim and 'x' in ranges and 'theta' in ranges and len(ranges['theta']) == 1 and 'phi' in ranges and len(ranges['phi']) == 1:
		# r = x / sin theta cos phi
		if len(ranges) > 3:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Invalid combination of vector components {ranges_str}; perhaps you mean {prefix}x, {prefix}theta, {prefix}phi only.\n")
			exit(1)
		phi = ranges['phi'][0]
		theta = ranges['theta'][0]
		if degrees:
			phi *= np.pi / 180
			theta *= np.pi / 180
		if abs(np.sin(theta)) < 1e-10 or abs(np.cos(phi)) < 1e-10:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Combination of vector components {prefix}x, {prefix}theta = {ranges['theta'][0]}, {prefix}phi = {ranges['phi'][0]} is singular.\n")
			exit(1)
		return dict(r=ranges['x'] / np.cos(phi) / np.sin(theta), theta=ranges['theta'], phi=ranges['phi'], prefix=prefix, astype='sph', deg=degrees)
	elif threedim and 'y' in ranges and 'theta' in ranges and len(ranges['theta']) == 1 and 'phi' in ranges and len(ranges['phi']) == 1:
		# r = y / sin theta sin phi
		if len(ranges) > 3:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Invalid combination of vector components {ranges_str}; perhaps you mean {prefix}y, {prefix}theta, {prefix}phi only.\n")
			exit(1)
		phi = ranges['phi'][0]
		theta = ranges['theta'][0]
		if degrees:
			phi *= np.pi / 180
			theta *= np.pi / 180
		if abs(np.sin(theta)) < 1e-10 or abs(np.sin(phi)) < 1e-10:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Combination of vector components {prefix}y, {prefix}theta = {ranges['theta'][0]}, {prefix}phi = {ranges['phi'][0]} is singular.\n")
			exit(1)
		return dict(r=ranges['y'] / np.sin(phi) / np.sin(theta), theta=ranges['theta'], phi=ranges['phi'], prefix=prefix, astype='sph', deg=degrees)
	elif threedim and 'z' in ranges and 'theta' in ranges and len(ranges['theta']) == 1 and 'phi' in ranges and len(ranges['phi']) == 1:
		# r = z / cos theta
		if len(ranges) > 3:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Invalid combination of vector components {ranges_str}; perhaps you mean {prefix}z, {prefix}theta, {prefix}phi only.\n")
			exit(1)
		theta = ranges['theta'][0]
		if degrees:
			theta *= np.pi / 180
		if abs(np.cos(theta)) < 1e-10:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Combination of vector components {prefix}z, {prefix}theta = {ranges['theta'][0]}, {prefix}phi = {ranges['phi'][0]} is singular.\n")
			exit(1)
		return dict(r=ranges['z'] / np.cos(theta), theta=ranges['theta'], phi=ranges['phi'], prefix=prefix, astype='sph', deg=degrees)
	elif threedim and 'z' in ranges and len(ranges['z']) == 1 and 'theta' in ranges and 'phi' in ranges and len(ranges['phi']) == 1:
		# r = z / cos theta
		if len(ranges) > 3:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Invalid combination of vector components {ranges_str}; perhaps you mean {prefix}z, {prefix}theta, {prefix}phi only.\n")
			exit(1)
		theta = np.array(ranges['theta'])
		if degrees:
			theta *= np.pi / 180
		if np.amin(np.abs(np.cos(theta))) < 1e-10:
			min_idx = np.argsort(np.abs(np.cos(theta)))[0]
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Combination of vector components {prefix}z, {prefix}theta = {ranges['theta'][min_idx]}, {prefix}phi = {ranges['phi'][0]} is singular.\n")
			exit(1)
		# convert to cylindrical coordinates
		sys.stderr.write(f"Warning (cmdargs.vectorvalues): This combination of vector components {prefix}z, {prefix}theta, {prefix}phi requires conversion to a nonuniform grid of cylindrical coordinates.\n")
		return dict(r=ranges['z'][0] / np.cos(theta), z=ranges['z'], phi=ranges['phi'], prefix=prefix, astype='cyl', deg=degrees)


	elif threedim and '' in ranges and 'theta' in ranges and len(ranges) == 2:
		return dict(r=ranges[''], theta=ranges['theta'], prefix=prefix, astype='sph', deg=degrees)
	elif threedim and 'x' in ranges and 'theta' in ranges and len(ranges['theta']) == 1 and len(ranges) == 2:
		# r = x / sin theta
		theta = ranges['theta'][0]
		if degrees:
			theta *= np.pi / 180
		if abs(np.sin(theta)) < 1e-10:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Combination of vector components {prefix}x, {prefix}theta = {ranges['theta'][0]} is singular.\n")
			exit(1)
		return dict(r=ranges['x'] / np.sin(theta), theta=ranges['theta'], prefix=prefix, astype='sph', deg=degrees)
	elif threedim and 'x' in ranges and len(ranges['x']) == 1 and 'theta' in ranges and len(ranges) == 2:
		# r = x / sin theta
		theta = np.array(ranges['theta'])
		if degrees:
			theta *= np.pi / 180
		if np.amin(np.abs(np.tan(theta))) < 1e-10:
			min_idx = np.argsort(np.abs(np.tan(theta)))[0]
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Combination of vector components {prefix}x, {prefix}theta = {ranges['theta'][min_idx]} is singular.\n")
			exit(1)
		# convert to cylindrical coordinates
		sys.stderr.write(f"Warning (cmdargs.vectorvalues): This combination of vector components {prefix}x, {prefix}theta requires conversion to a nonuniform grid of cylindrical coordinates.\n")
		return dict(r=ranges['x'], z=ranges['x'][0] / np.tan(theta), prefix=prefix, astype='cyl', deg=degrees)
	elif threedim and 'z' in ranges and 'theta' in ranges and len(ranges['theta']) == 1 and len(ranges) == 2:
		# r = z / cos theta
		theta = ranges['theta'][0]
		if degrees:
			theta *= np.pi / 180
		if abs(np.cos(theta)) < 1e-10:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Combination of vector components {prefix}z, {prefix}theta = {ranges['theta'][0]} is singular.\n")
			exit(1)
		return dict(r=ranges['z'] / np.cos(theta), theta=ranges['theta'], prefix=prefix, astype='sph', deg=degrees)
	elif threedim and 'z' in ranges and len(ranges['z']) == 1 and 'theta' in ranges and len(ranges) == 2:
		# r = z / cos theta
		theta = np.array(ranges['theta'])
		if degrees:
			theta *= np.pi / 180
		if np.amin(np.abs(np.cos(theta))) < 1e-10:
			min_idx = np.argsort(np.abs(np.cos(theta)))[0]
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Combination of vector components {prefix}z, {prefix}theta = {ranges['theta'][min_idx]} is singular.\n")
			exit(1)
		# convert to cylindrical coordinates
		sys.stderr.write(f"Warning (cmdargs.vectorvalues): This combination of vector components {prefix}z, {prefix}theta requires conversion to a nonuniform grid of cylindrical coordinates.\n")
		return dict(r=ranges['z'][0] / np.cos(theta), z=ranges['z'], prefix=prefix, astype='cyl', deg=degrees)

	elif threedim and 'x' in ranges and 'z' in ranges and len(ranges) == 2:
		return dict(x=ranges['x'], z=ranges['z'], prefix=prefix, astype='xyz')
	elif threedim and 'z' in ranges and len(ranges) == 1:
		return dict(z=ranges['z'], prefix=prefix, astype='z')
	## below here, we have either twodim or threedim
	elif '' in ranges and 'phi' in ranges:
		if 'perp' in ranges and len(ranges) == 3:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Combination of vector components {prefix}perp, {prefix}phi is not (yet) implemented.\n")
			exit(1)  # TODO: Implement suitable vector format; or maybe not ...
		elif len(ranges) == 2:
			return dict(r=ranges[''], phi=ranges['phi'], prefix=prefix, astype='pol', deg=degrees)
		else:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Invalid combination of vector components {ranges_str}; perhaps you mean {prefix}, {prefix}phi only.\n")
			exit(1)
	elif 'x' in ranges and 'phi' in ranges and len(ranges['phi']) == 1:
		# r = x / cos phi
		phi = ranges['phi'][0]
		if degrees:
			phi *= np.pi / 180
		if abs(np.cos(phi)) < 1e-10:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Combination of vector components {prefix}x, {prefix}phi = {ranges['phi'][0]} is singular.\n")
			exit(1)
		return dict(r=ranges['x'] / np.cos(phi), phi=ranges['phi'], prefix=prefix, astype='pol', deg=degrees)
	elif 'y' in ranges and 'phi' in ranges and len(ranges['phi']) == 1:
		# r = y / sin phi
		phi = ranges['phi'][0]
		if degrees:
			phi *= np.pi / 180
		if abs(np.sin(phi)) < 1e-10:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Combination of vector components {prefix}y, {prefix}phi = {ranges['phi'][0]} is singular.\n")
			exit(1)
		return dict(r=ranges['y'] / np.sin(phi), phi=ranges['phi'], prefix=prefix, astype='pol', deg=degrees)
	elif 'x' in ranges and 'y' in ranges:
		if len(ranges) > 2:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Invalid combination of vector components {ranges_str}; perhaps you mean {prefix}x, {prefix}y only.\n")
			exit(1)
		return dict(x=ranges['x'], y=ranges['y'], prefix=prefix, astype='xy')
	elif '' in ranges and 'perp' in ranges:
		if len(ranges) > 2:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Invalid combination of vector components {ranges_str}; perhaps you mean {prefix}, {prefix}perp only.\n")
			exit(1)
		if defaultaxis == 'x':
			return dict(x=ranges[''], y=ranges['perp'], prefix=prefix, astype='xy')
		elif defaultaxis == 'y':
			return dict(y=ranges[''], x=ranges['perp'], prefix=prefix, astype='xy')
		elif defaultaxis == 'z':
			return dict(z=ranges[''], x=ranges['perp'], prefix=prefix, astype='xyz')
	elif 'x' in ranges:
		if len(ranges) > 1:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Invalid combination of vector components {ranges_str}; perhaps you mean {prefix}x only.\n")
			exit(1)
		return dict(x=ranges['x'], prefix=prefix, astype='x')
	elif '' in ranges:
		if len(ranges) > 1:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Invalid combination of vector components {ranges_str}; perhaps you mean {prefix} only.\n")
			exit(1)
		if threedim and defaultaxis == 'z':
			return dict(z=ranges[''], prefix=prefix, astype='z')
		elif defaultaxis in ['x', 'y']:
			return dict(**{defaultaxis: ranges['']}, prefix=prefix, astype=defaultaxis)
		else:
			raise ValueError("Invalid value for argument defaultaxis.")
	elif 'y' in ranges:
		if len(ranges) > 1:
			sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Invalid combination of vector components {ranges_str} with {prefix}y.\n")
			exit(1)
		return dict(y=ranges['y'], prefix=prefix, astype='y')
	# Fallthrough: Illegal combination
	sys.stderr.write(f"ERROR (cmdargs.vectorvalues): Invalid combination of vector components {ranges_str} (in this dimension).\n")
	exit(1)

def params(kdim = None):
	"""Parse command-line arguments for physical parameters.

	Argument:
	kdim     1, 2, or 3. Dimensionality of the geometry, i.e., the number of
	         momentum components.

	Returns:
	PhysParams instance
	"""
	physparams = {}
	physparams['kdim'] = kdim

	# get temperature first, as it is required for the evaluation of some material parameters
	try:
		val, arg = sysargv.getval(["temp"])
		temperature = float(val) if val is not None else None
		physparams['temperature'] = temperature
	except ValueError:
		sys.stderr.write("ERROR: Absent or invalid value for argument \"temp\"\n")
		exit(1)

	## Material parameters
	customarg.materialparam()

	## Layer materials
	m_layers = customarg.get_material(['mlayer', 'mater', 'material'], temperature)
	substrate_material = customarg.get_material(['msubstrate', 'msubst', 'msub', 'substrate'], temperature)
	m_well = customarg.get_material(['mwell', 'mqw'], temperature)
	m_barr = customarg.get_material(['mbarrier', 'mbarr', 'mbar'], temperature)

	## checks
	if len(m_well) == 0 and len(m_barr) == 0 and len(m_layers) == 0:
		example_arg_str = "'mlayer', 'mater'" if kdim == 3 else "'mlayer', 'mater', 'mwell', 'mbarr'"
		sys.stderr.write(f"ERROR: No material specifications given. At least one material parameter ({example_arg_str}, etc.), followed by at least one material id, is required.\n")
		exit(1)
	elif len(m_layers) > 0:
		if len(m_well) != 0 or len(m_barr) != 0:
			sys.stderr.write("ERROR: Material specifications must either be generic ('mlayer', 'mater', 'material') or specific ('mwell', 'mqw', 'mbarrier', 'mbarr', 'mbar') but cannot be mixed.\n")
			exit(1)
		if kdim == 3 and len(m_layers) > 1:
			sys.stderr.write("ERROR: In bulk mode, you can specify only one material (with 'mater', 'material', or 'mlayer').\n")
			exit(1)
	elif kdim == 3:  # len(m_layers) == 0
		if len(m_barr) > 0:
			sys.stderr.write("ERROR: In bulk mode, the barrier material cannot be specified. Specify a single material with 'mater' or 'mlayer'.\n")
			exit(1)
		if len(m_well) > 1:
			sys.stderr.write("ERROR: In bulk mode, you can specify only one material, preferably with 'mater' or 'mlayer', but 'mwell' is permitted.\n")
			exit(1)
		else:  # len(m_well) == 1
			sys.stderr.write("Warning: In bulk mode, prefer to use 'mater' or 'mlayer' instead of 'mwell'.\n")
			m_layers = [m_well[0]]
	else:  # kdim == 3 and len(m_layers) == 0
		if len(m_well) == 0:
			sys.stderr.write("ERROR: In combination with a barrier material, a well material must be specified using 'mwell'.\n")
			exit(1)
		if len(m_well) > 1:
			sys.stderr.write("ERROR: More than one well material (with 'mwell') is not permitted.\n")
			exit(1)
		if len(m_barr) == 0:
			m_layers = [m_well[0]]
		elif len(m_barr) == 1:
			m_layers = [m_barr[0], m_well[0], m_barr[0]]
		elif len(m_barr) == 2:
			m_layers = [m_barr[0], m_well[0], m_barr[1]]
		if len(m_barr) > 2:
			sys.stderr.write("ERROR: Maximally two barrier materials can be specified with 'mbarr'. For more layers, use 'mater' or 'mlayer'.\n")
			exit(1)
	if len(substrate_material) == 0:
		substrate_material = None
	elif len(substrate_material) == 1:
		substrate_material = substrate_material[0]
	else:
		sys.stderr.write("ERROR: Only one substrate material can be specified.\n")
		exit(1)
	physparams.update(m_layers=m_layers, substrate_material=substrate_material)

	## Layer thicknesses
	if kdim != 3:
		l_layers = customarg.layersizes(['llayer', 'llayers', 'layer', 'layers', 'thickness', 'thicknesses', 'thick'])
		l_well = customarg.layersizes(['qw', 'lhgte', 'lqw', 'lwell'])
		l_barr = customarg.layersizes(['bar', 'barr', 'barrier', 'lhgcdte', 'lbar', 'lbarr', 'lbarrier'])
	else:
		l_layers, l_well, l_barr = [1.0], [], []  # default for 3 dimensions

	## Material and layer checks
	if kdim == 3:
		pass  # thickness arguments are ignored
	elif len(l_layers) > 0:  # kdim != 3
		if len(l_well) != 0 or len(l_barr) != 0:
			sys.stderr.write("ERROR: Layer thickness specifications must either be generic ('llayer', etc.) or specific ('lwell', 'lbarr', etc.) but cannot be mixed.\n")
			exit(1)
	else:  # kdim != 3 and len(l_layer) == 0
		if len(l_well) == 0 and len(l_barr) == 0:
			sys.stderr.write("ERROR: No layer thickness given. For each material (except the substrate) the thickness must be provided using 'llayer', 'lwell', 'lbarr', etc.).\n")
			exit(1)
		if len(l_well) == 0:  # len(l_barr) > 0
			sys.stderr.write("ERROR: In combination with a barrier thickness, the well thickness must be specified using 'lwell'.\n")
			exit(1)
		if len(l_well) > 1:
			sys.stderr.write("ERROR: More than one well thickness (with 'lwell') is not permitted.\n")
			exit(1)
		if len(l_barr) == 0:
			l_layers = [l_well[0]]
		elif len(l_barr) == 1:
			l_layers = [l_barr[0], l_well[0], l_barr[0]]
		elif len(l_barr) == 2:
			l_layers = [l_barr[0], l_well[0], l_barr[1]]
		if len(l_barr) > 2:
			sys.stderr.write("ERROR: Maximally two barrier thicknesses can be specified with 'lbarr'. For more layers, use 'llayer'.\n")
			exit(1)

	if len(m_layers) != len(l_layers):
		sys.stderr.write(f"ERROR: Unequal number of specified materials and thicknesses ({len(m_layers)} vs {len(l_layers)}). Use the appropriate material and thickness commands (e.g., 'mlayer' and 'llayer') and make sure that the number of their arguments match.\n")
		exit(1)
	physparams['l_layers'] = l_layers

	## Layer types
	layer_types, _ = sysargv.getval(['ltype', 'ltypes', 'lstack'])
	physparams['layer_types'] = layer_types

	## Layer densities
	physparams['layer_density'] = sysargv.getfloats(['ldens', 'layerdens', 'layerdensity'])

	if sysargv.verbose:
		print("Layer structure:")
		for m, l in zip(reversed(m_layers), reversed(l_layers)):
			print("%7.2f nm  %s" % (l, m.format("plain")))
		print("Substrate:", " ---" if substrate_material is None else substrate_material.format("plain"))

	## Lattice orientation
	physparams['lattice_orientation'] = customarg.orientation()

	# Strain
	physparams['rel_strain'] = customarg.strain()
	if ("ignorestrain" in sysargv) or ("nostrain" in sysargv):
		physparams['rel_strain'] = 'none'

	# Other parameters
	for i, arg, arglower in sysargv.iter_enumerate():
		if arglower in ['linterface', 'interface'] and kdim <= 2:
			physparams['linterface'] = sysargv.getfloat_after(i)
		elif arglower in ['zres', 'lres'] and kdim <= 2:
			physparams['zres'] = sysargv.getfloat_after(i)
		elif arglower in ['width', 'w'] and kdim <= 1:
			sysargv.setparsed(i)
			w_num, w_res1, w_total1, narg = customarg.width_wres(sysargv[i:])
			if w_res1 is not None:
				if physparams.get('yres'):
					sys.stderr.write(f"Warning: Duplicate value for wres (width resolution), argument \"{arg}\"\n")
				physparams['yres'] = w_res1
			if w_total1 is not None:
				if physparams.get('width'):
					sys.stderr.write(f"Warning: Duplicate value for w (width), argument \"{arg}\"\n")
				physparams['width'] = w_total1
			if w_num is not None:
				physparams['ny'] = w_num
			sysargv.setparsednext(narg)
		elif arglower in ['wres', 'yres'] and kdim <= 1:
			w_res1 = sysargv.getfloat_after(i)
			if physparams.get('yres'):
				sys.stderr.write(f"Warning: Duplicate value for wres (width resolution), argument \"{arg}\"\n")
			physparams['yres'] = w_res1
		elif arglower in ['alattice', 'alatt', 'latticeconst']:
			physparams['a_lattice'] = sysargv.getfloat_after(i)
		elif arglower in ['stripdir', 'ribbondir']:
			sdir = sysargv.getval_after(i).lower()
			if physparams.get('lattice_orientation'):
				sys.stderr.write(f"Warning: Duplicate definition for strip direction or orientation (argument \"{arg}\")\n")
			m = re.match("(-?[0-9])(-?[0-9])(-?[0-9])", sdir)
			if m is not None:
				lattice_orientation = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
			elif sdir == "x":
				lattice_orientation = 0
			elif sdir == "y":
				lattice_orientation = 90
			elif sdir == "xy":
				lattice_orientation = 45
			elif sdir == "-xy":
				lattice_orientation = -45
			else:
				sys.stderr.write(f"ERROR: Absent or invalid value for argument \"{arg}\". Valid arguments are x, y, xy, -xy, or ab0 where a and b are integers from -9 to 9. For angular values, use argument 'stripangle'.\n")
				exit(1)
			physparams['lattice_orientation'] = lattice_orientation
		elif arglower in ['stripangle', 'ribbonangle']:
			sangle = sysargv.getfloat_after(i)
			if physparams.get('lattice_orientation'):
				sys.stderr.write(f"Warning: Duplicate definition for strip direction (argument \"{arg}\")\n")
			physparams['lattice_orientation'] = sangle
		elif arglower in ['yconf', 'confinement', 'yconfinement']:
			physparams['yconfinement'] = sysargv.getfloat_after(i)
		elif arglower in ['mn', 'ymn']:
			sys.stderr.write(f"ERROR: Deprecated argument \"{arg}\". Enter the material as 'HgMnTe 0.02' or 'HgMnTe 2%%' (substitute the desired Mn concentration).\n")
			exit(1)
		elif arglower in ['cd', 'ycd']:
			sys.stderr.write(f"ERROR: Deprecated argument \"{arg}\". Enter the material as 'HgCdTe 0.68' or 'HgCdTe 68%%' (substitute the desired Cd concentration).\n")
			exit(1)
		elif arglower in ['eightband', '8band', '8o', '8orb', '8orbital']:
			sysargv.setparsed(i)
			if physparams.get('norbitals'):
				sys.stderr.write(f"ERROR: Conflicting or double argument \"{arg}\" for number of orbitals\n")
				exit(1)
			else:
				physparams['norbitals'] = 8
		elif arglower in ['sixband', '6band', '6o', '6orb', '6orbital']:
			sysargv.setparsed(i)
			if physparams.get('norbitals'):
				sys.stderr.write(f"ERROR: Conflicting or double argument \"{arg}\" for number of orbitals\n")
				exit(1)
			else:
				physparams['norbitals'] = 6
		elif arglower in ['orbitals', 'orb', 'norb']:
			sysargv.setparsed(i)
			if physparams.get('norbitals'):
				sys.stderr.write(f"ERROR: Conflicting or double argument \"{arg}\" for number of orbitals\n")
				exit(1)
			try:
				norbitals = int(sysargv[i+1])
			except ValueError:
				sys.stderr.write(f"ERROR: Absent or invalid value for argument \"{arg}\"\n")
				exit(1)
			if norbitals not in [6, 8]:
				sys.stderr.write(f"ERROR: Number of orbitals must be 6 or 8 (argument \"{arg}\")\n")
				exit(1)
			else:
				physparams['norbitals'] = norbitals
				sysargv.setparsednext(1)

	## Check that norbitals has been set correctly
	if not physparams.get('norbitals'):
		sys.stderr.write("ERROR: Number of orbitals must be specified. Use 'norb 6', '6o', 'norb 8', or '8o', for example.\n")
		exit(1)

	# Enable or disable renormalization between different number of orbitals
	physparams['matdef_renorm'] = not (("noren" in sysargv) or ("norenorm" in sysargv) or ("norenormalization" in sysargv) or ("norenormalisation" in sysargv))

	return physparams

def plot_options(plotopts = None, format_args = None):
	"""Parse command-line arguments for plot options

	Arguments:
	plotopts     A dict instance or None. If this is a non-empty dict, use this
	             as the initial values which are then updated by this function.
	format_args  A dict of objects that are either dict or define .to_dict().
	             Arguments for variable substitution in format_string().
	             Typically this will be (physparams, opts).

	Returns:
	A dict instance.
	"""
	## Default values (plotopts and format_args)
	if plotopts is None:
		plotopts = {}
	elif not isinstance(plotopts, dict):
		raise TypeError("Argument plotopts must be a dict instance or None")
	if format_args is None:
		format_args = ()
	elif not isinstance(format_args, tuple):
		raise TypeError("Argument format_args must be a dict instance or None")

	plotopts['legend'] = 'legend' in sysargv
	plotopts['labels'] = 'char' in sysargv or 'labels' in sysargv or 'plotlabels' in sysargv

	plotopts['mode'] = None
	val, arg = sysargv.getval(['plotmode', 'plotstyle'])
	if val is not None:
		if val in ['auto', 'automatic', 'normal', 'join', 'curves', 'horizontal', 'spin'] or re.fullmatch(r'(spin|berry)(xy|xz|yz)1?', val) is not None:
			plotopts['mode'] = val
		else:
			sys.stderr.write("Warning: '%s' is not a valid plot style (argument '%s'); plot style is set to automatic.\n" % (val, arg))

	plotopts['xrange'] = None
	val, arg = sysargv.getval(['xrange', 'krange', 'brange'], 2)
	if isinstance(val, list) and len(val) in [1, 2, 3]:
		try:
			x1 = float(val[0])
		except:
			sys.stderr.write("ERROR: Invalid value for argument \"%s\"\n" % arg)
			exit(1)
		try:
			x2 = float(val[1])
		except:
			x2 = 0.0
		plotopts['xrange'] = [min(x1, x2), max(x1, x2)]

	elif val is not None:
		sys.stderr.write("ERROR: Invalid value for argument \"%s\"\n" % arg)
		exit(1)

	plotopts['obs'] = None
	val, arg = sysargv.getval(['obs'])
	if val is not None:
		plotopts['obs'] = val

	plotopts['plotvar'] = None
	val, arg = sysargv.getval(['plotvar'])
	if val is not None:
		if val.startswith("k") or val.startswith("b"):
			plotopts['plotvar'] = val
		else:
			sys.stderr.write("Warning: '%s' is not a valid plot variable (argument '%s')\n" % (val, arg))

	plotopts['title_pos'] = None
	val, arg = sysargv.getval(['titlepos', 'titleposition', 'plottitleposition', 'plottitlepos'])
	if val is not None:
		plotopts['title_pos'] = val.replace('-', '').replace('_', '').replace(' ', '')

	plotopts['title'] = None
	val, arg = sysargv.getval(['title', 'plottitle'])
	if val is not None:
		if params is not None:
			plotopts['title'] = format_string(val, plotopts, *format_args, material_format = 'tex')
		else:
			sys.stderr.write("Warning: Could not format plot title; system parameters are missing\n")

	# Obsolete: plotopts['density_unit'] = None
	for a in ['densitycm', 'densityecm', 'densitypcm', 'densitynm', 'densityenm', 'densitypnm', 'densityunit', 'densunit', 'dunit']:
		if a in sysargv:
			sys.stderr.write("Warning: Density unit argument '%s' is deprecated. Use the configuration values 'dos_quantity' and 'dos_unit' instead.\n" % a)

	val, arg = sysargv.getval(['rcfile', 'plotrc'])
	if val is not None:
		sys.stderr.write(f"Warning: Deprecated argument {arg}. Plot customization is now done by setting the configuration value 'fig_matplotlib_style'.\n")

	plotopts['density_range'] = None
	val, arg = sysargv.getval(['dosrange', 'densityrange', 'dosmax', 'densitymax'], 2)
	if isinstance(val, list) and len(val) in [1, 2]:
		try:
			x1 = float(val[0])
		except:
			sys.stderr.write("ERROR: Invalid value for argument \"%s\"\n" % arg)
			exit(1)
		try:
			x2 = float(val[1])
		except:
			x2 = None
		plotopts['density_range'] = [None, x1] if x2 is None else [min(x1, x2), max(x1, x2)]
	elif val is not None:
		sys.stderr.write("ERROR: Invalid value for argument \"%s\"\n" % arg)
		exit(1)

	plotopts['obsrange'] = None
	val, arg = sysargv.getval(['orange', 'obsrange', 'colorrange', 'colourrange'], 2)
	if isinstance(val, list) and len(val) in [1, 2]:
		try:
			x1 = float(val[0])
		except:
			sys.stderr.write("ERROR: Invalid value for argument \"%s\"\n" % arg)
			exit(1)
		try:
			x2 = float(val[1])
		except:
			x2 = None
		plotopts['obsrange'] = [None, x1] if x2 is None else [min(x1, x2), max(x1, x2)]
	elif val is not None:
		sys.stderr.write("ERROR: Invalid value for argument \"%s\"\n" % arg)
		exit(1)

	return plotopts

def options(opts = None, axial_automatic = None):
	"""Parse command-line arguments for generic options (model options)

	Argument:
	opts    A dict instance or None. If this is a non-empty	dict, use this as
	        the initial values which are then updated by this function.
	axial_automatic  None, 'ignore', True or False. If True or False, use this
	                 value if neither 'axial' nor 'nonaxial' are given on the
	                 command line. If None, raise an error in that case. If
	                 'ignore', pass on silently.

	Returns:
	A dict instance.
	"""
	## Default value (opts)
	if opts is None:
		opts = {}
	elif not isinstance(opts, dict):
		raise TypeError("Argument opts must be a dict instance or None")

	## Set number of processes for multiprocessing / parallel computation
	num_cpus, max_cpus = customarg.cpus()
	if num_cpus > 1:
		opts['cpu'] = num_cpus
	num_thr = customarg.threads()
	if num_thr is not None and num_thr >= 1:
		opts['threads'] = num_thr
	num_gpu = customarg.gpu_workers()
	if num_gpu is not None and num_gpu >= 1:
		opts['gpu'] = num_gpu

	## Ignore strain terms
	if ("ignorestrain" in sysargv) or ("nostrain" in sysargv):
		opts["ignorestrain"] = True

	## Ignore exchange (obsolete argument)
	if "ignoreexchange" in sysargv:
		sys.stderr.write("ERROR: Argument 'ignoreexchange' is no longer supported. In order to disable exchange coupling, adjust the relevant material parameters.\n")
		exit(1)

	# Forced disable/enable lattice regularization (obsolete)
	if "nolatticereg" in sysargv or "latticereg" in sysargv:
		sys.stderr.write("ERROR: Lattice regularization is now controlled by configuration value 'lattice_regularization'.\n")
		exit(1)

	## Exclude non-axial terms
	if ("noax" in sysargv) or ("noaxial" in sysargv) or ("nonaxial" in sysargv):
		opts['axial'] = False
	elif ("ax" in sysargv) or ("axial" in sysargv):
		opts['axial'] = True
	elif isinstance(axial_automatic, str) and axial_automatic.lower() == 'ignore':
		pass
	elif axial_automatic is None:
		sys.stderr.write("ERROR: Either 'ax' ('axial') or 'noax' ('nonaxial') is required as an argument.\n")
		exit(1)
	else:
		sys.stderr.write("Warning: Axial approximation has been set to %s automatically.\n" % axial_automatic)
		opts['axial'] = axial_automatic

	## Do not renormalize material parameters
	# (just set the option; param will actually take care of it)
	if ("noren" in sysargv) or ("norenorm" in sysargv) or ("norenormalization" in sysargv) or ("norenormalisation" in sysargv):
		opts['renorm'] = False
	else:
		opts['renorm'] = True

	## Include BIA terms
	if "bia" in sysargv:
		opts["bia"] = True

	## Ignore in-plane orbital field
	if ("ignoremagnxy" in sysargv) or ("ignorebxy" in sysargv) or ("ignoreorbxy" in sysargv):
		opts["ignore_magnxy"] = True

	## Dimensionful(l) observables
	if 'dimful' in sysargv or 'dimfull' in sysargv:
		opts['dimful_obs'] = True

	## Orbital overlap observables
	if 'orboverlaps' in sysargv or 'orbobs' in sysargv or 'orbitaloverlaps' in sysargv or 'orbitalobs' in sysargv:
		opts['orbitalobs'] = True

	## Number of eigenvalues and states
	neig = sysargv.getint(["neig", "neigs"], 50, limit = [1, None])
	opts['neig'] = neig

	## Number of Landau levels
	ll_max = sysargv.getint(["llmax", "nll"], 30, limit = [0, None])
	opts['ll_max'] = ll_max

	## Landau level (density / Berry curvature) broadening
	broadening_val, broadening_val2 = customarg.broadening()
	berrybroadening_val, _ = customarg.broadening(['berrybroadening', 'hallbroadening', 'chernbroadening'], allow_extra_val = False)
	if len(broadening_val) >= 1:
		customarg.broadening_setopts(opts, 'broadening', broadening_val)
		if opts['broadening_type'].count('thermal') + opts['broadening_type'].count('fermi') > 1:
			sys.stderr.write("Warning (Main): More than one thermal/fermi broadening given.\n")
	elif 'hall' in sysargv:
		customarg.broadening_setopts(opts, 'broadening', (0.5, 'gauss', 'auto'))
		sys.stderr.write("Warning (Main): Argument 'hall' implies broadening_scale = %g meV. Use explicit 'broadening' argument to override this value.\n" % opts['broadening_scale'])

	if broadening_val2 is not None:
		if len(berrybroadening_val) > 0:
			sys.stderr.write("ERROR (Main): Numerical extra argument to 'broadening' cannot be combined with argument 'berrybroadening'.\n")
			exit(1)
		customarg.broadening_setopts(opts, 'berrybroadening', broadening_val2)
	elif len(berrybroadening_val) >= 1:
		customarg.broadening_setopts(opts, 'berrybroadening', berrybroadening_val)
	elif 'hall' in sysargv:
		if opts['broadening_type'] == 'gauss':
			opts['berrybroadening_scale'] = 0.1 * opts['broadening_scale']
		elif isinstance(opts['broadening_type'], list):
			n_gauss = opts['broadening_type'].count('gauss')
			if 'gauss' in opts['broadening_type']:
				i_gauss = opts['broadening_type'].index('gauss')
				opts['berrybroadening_scale'] = 0.1 * opts['broadening_scale'][i_gauss]
				if opts['broadening_type'].count('gauss') > 1:
					sys.stderr.write("Warning (Main): For argument 'hall', extract Berry broadening width from first Gaussian broadening parameter only.\n")
			else:
				opts['berrybroadening_scale'] = 0.05  # default value
		opts['berrybroadening_type'] = 'gauss'
		opts['berrybroadening_dep'] = 'auto'
		sys.stderr.write("Warning (Main): Argument 'hall' implies berrybroadening_scale = %g meV. Use explicit 'broadening' argument (with two values) to override this value.\n" % opts['berrybroadening_scale'])

	## Temperature broadening (dostemp)
	temp_broadening = sysargv.getfloat(["dostemp", "tbroadening", "tempbroadening"])
	if temp_broadening is not None and temp_broadening < 0.0:
		sys.stderr.write("ERROR: Broadening temperature may not be negative.\n")
		exit(1)
	if temp_broadening is not None and temp_broadening >= 0.0:
		if 'broadening_type' not in opts:
			opts['broadening_type'] = 'thermal'
			opts['broadening_scale'] = temp_broadening
			opts['broadening_dep'] = 'const'
		elif isinstance(opts['broadening_type'], (str, list)):
			if isinstance(opts['broadening_type'], str):
				opts['broadening_type'] = [opts['broadening_type']]
				opts['broadening_scale'] = [opts['broadening_scale']]
				opts['broadening_dep'] = [opts['broadening_dep']]
			if any([x in ['thermal', 'fermi'] for x in opts['broadening_type']]):
				sys.stderr.write("ERROR: Arguments 'dostemp' and 'broadening thermal/fermi' cannot be combined.\n")
				exit(1)
			opts['broadening_type'].append('thermal')
			opts['broadening_scale'].append(temp_broadening)
			opts['broadening_dep'].append('const')
		else:
			raise TypeError("Type of opts['broadening_type'] should be str or list")
		opts['tempbroadening'] = temp_broadening

	## Target energy
	targetenergy = sysargv.getfloats(["targetenergy", "e0"])
	if len(targetenergy) == 0:
		opts['targetenergy'] = 0.0  # default value
	elif len(targetenergy) == 1:
		opts['targetenergy'] = targetenergy[0]
	else:
		opts['targetenergy'] = targetenergy
	# TODO: Some solvers might accept only a single value, not a list

	## Artificial split
	splitwarningvalue = 0.1
	split = sysargv.getfloat(["split"], 0.0)
	if split != 0.0:
		opts['split'] = split
	if abs(split) > splitwarningvalue:
		sys.stderr.write("Warning (Main): Artificial energy splitting is large. It is advisable to keep it under %f (in meV).\n" % splitwarningvalue)
	val, arg = sysargv.getval(['splittype'])
	if val is not None:
		opts['splittype'] = val

	## Artificial shift of E1 bands (no longer supported)
	if 'e1shift' in sysargv:
		sys.stderr.write("Warning (Main): The argument 'e1shift' is no longer supported.\n")

	## Energy shift and automatic shift to zero energy
	eshift = sysargv.getfloat(["eshift", "energyshift"])
	if eshift is not None:
		opts['eshift'] = eshift
	else:
		opts['eshift'] = 0.0
	opts['zeroenergy'] = ('zeroenergy' in sysargv)

	## Get transitions
	transitions_arg = customarg.transitions()
	if isinstance(transitions_arg, list) and len(transitions_arg) == 2:
		opts['transitions'] = transitions_arg[1]
		opts['transitionsrange'] = transitions_arg[0]
	else:
		opts['transitions'] = bool(transitions_arg)
		opts['transitionsrange'] = None

	## BHZ anchor point
	k0_bhz = sysargv.getfloat(["kbhz", "bhzk", "bhzat"], 0.0)
	if k0_bhz != 0.0:
		opts['k0_bhz'] = k0_bhz

	## Zero of gauge potential
	gauge_zero = sysargv.getfloat(["gaugezero", "gauge0"], 0.0)
	if gauge_zero != 0.0:
		opts['gauge_zero'] = gauge_zero
	if abs(gauge_zero) > 1.0:
		sys.stderr.write("Warning (Main): Zero of gauge potential lies outside the sample.\n")

	## Periodic in y?
	if "periodicy" in sysargv:
		opts['periodicy'] = True

	## Gate potential (+Vg/2 at top, -Vg/2 at bottom edge)
	v_inner = sysargv.getfloat(["vinner", "vwell"], None)
	v_outer = sysargv.getfloat(["vouter", "vtotal"], None)
	vgate = sysargv.getfloat(["vgate", "vtb", "vg"], None)
	if v_inner is not None:
		if vgate is not None:
			sys.stderr.write("ERROR (Main): Potential options (vgate, v_inner, v_outer) cannot be combined.\n")
			exit(1)
		opts['v_inner'] = v_inner
	if v_outer is not None:
		if vgate is not None or v_inner is not None:
			sys.stderr.write("ERROR (Main): Potential options (vgate, v_inner, v_outer) cannot be combined.\n")
			exit(1)
		opts['v_outer'] = v_outer
	if vgate is not None:
		sys.stderr.write("Warning (Main): Potential option vgate (vtb, vg) has been replaced by options vtotal (alias v_outer) and vwell (alias v_inner). Use vtotal (v_outer) to get the same functionality as vgate formerly.\n")
		opts['v_outer'] = vgate

	## Surface potential at the interface
	vsurf_v, vsurf_l, vsurf_quadratic = customarg.vsurf()
	if vsurf_v != 0.0:
		opts['vsurf'] = vsurf_v
		opts['vsurf_l'] = vsurf_l
		opts['vsurf_quadratic'] = vsurf_quadratic

	## Potential files
	val = customarg.potential(["pot", "potential"])
	if val is not None and len(val) > 0:
		opts['potentialfile'] = val
	val = customarg.potential(["poty", "potentialy"])
	if val is not None and len(val) > 0:
		if 'potentialfile' in opts:
			sys.stderr.write("ERROR (Main): Invalid combination of potential arguments: 'potentialy' (alias 'poty') and 'potential' (alias 'pot').\n")
			exit(1)
		else:
			sys.stderr.write("Warning (Main): The command-line argument 'potentialy' (alias 'poty') is deprecated. It will work for now, but prefer to use 'potential' instead.\n")
			opts['potentialfile'] = val

	## Selfconsistent calculation options
	selfcon_max_it, selfcon_acc = customarg.selfcon()
	if selfcon_max_it is not None:
		opts['selfcon_max_iterations'] = selfcon_max_it
	if selfcon_acc is not None:
		opts['selfcon_accuracy'] = selfcon_acc
	val, arg = sysargv.getval(['selfconweight', 'scweight', 'scw'])
	if val is not None:
		val = from_pct(val)
		if val is not None:
			opts['selfcon_weight'] = val

	## Boundary conditions for solving Poisson equation
	bc = customarg.potential_bc()
	if bc is not None:
		opts['custom_bc'] = bc

	## Depletion layer charge and width
	ndepletion, ldepletion = customarg.depletion()
	if ndepletion is not None:
		opts['n_depletion'] = ndepletion
	if ldepletion is not None:
		opts['l_depletion'] = ldepletion
	carrierdensity = cmdargsrange.grid(args = ["carrdens", "cardens", "carrierdensity", "ncarr", "ncar", "ncarrier"], from_argv = sysargv)
	if isinstance(carrierdensity, (np.ndarray, list)) and len(carrierdensity) >= 1:
		opts['cardensrange'] = carrierdensity
		# TODO: Single number is required for many functions. Distinction between
		# cardensrange and cardens may disappear when all functions are reimplemented
		# for density ranges, or raise an appropriate warning.
		opts['cardens'] = carrierdensity[0]
		if len(carrierdensity) > 1:
			sys.stderr.write("Warning (cmdargs.options): Density ranges are supported only for a few functions. Most functions will take just the first density value.\n")
	efield_arg = customarg.efield()
	if efield_arg is not None:
		opts['efield'] = efield_arg
	e_cnp = sysargv.getfloat(["ecnp", "cnp", "efermi", "ef0"])
	if e_cnp is not None:
		opts['e_cnp'] = e_cnp
	n_cnp = sysargv.getfloat(["noffset", "densoffset", "ncnp"])
	if n_cnp is not None:
		opts['n_offset'] = n_cnp
	else:
		n_cnp = sysargv.getfloat(["idosoffset", "dosoffset"])
		if n_cnp is not None:
			opts['n_offset'] = n_cnp / (2 * np.pi)**2
	n_bg = sysargv.getfloat(["cardensbg"])
	if n_bg is not None:
		opts['n_bg'] = n_bg
	opts['tempout'] = 'tempout' in sysargv
	opts['return_eivec'] = 'keepeivecs' in sysargv
	opts['currents'] = 'currents' in sysargv
	opts['custom_interface_length'] = sysargv.getint(["custominterfacelengthnm"], limit = (0, np.inf))
	opts['verbose'] = sysargv.verbose
	return opts

def outputid(format_args = None):
	"""Parse command-line arguments for outputid (string inserted into file names)"""
	outputid = ""
	outputid, arg = sysargv.getval(["out", "outputid", "outputname", "outid", "outfile"])
	if outputid is None or outputid == "":
		outputid = ""
	if isinstance(format_args, tuple) and (outputid == '?' or '{' in outputid):
		outputid = format_string(outputid, *format_args)
		if outputid is None:
			exit(1)
	return outputid

def outdir(allow_mkdir = True, do_chdir = True, replacements = None):
	"""Parse command-line arguments for output directory (and go there)

	Arguments:
	allow_mkdir   True or False. If True, create the directory if it does not
	              exist yet. If False, do not create the directory
	do_chdir      True or False. If True, change to new output directory. If
	              False, do not do so.
	replacements  A dict instance. The key value pairs indicate string
	              substitution key -> value. This only applies to a directory
	              that contains '@'.

	Returns:
	curdir   Previous working directory
	outdir   New output directory
	"""
	curdir = os.getcwd()

	d, arg = sysargv.getval(["dir", "outputdir", "outdir"])
	outdir = None
	if d is not None:
		if isinstance(replacements, dict) and '@' in d:  # Handle directory name containing @var substitutions
			for from_, to in replacements.items():
				d = d.replace(from_, to)
		if os.path.exists(d):
			outdir = d
		else:
			if allow_mkdir:
				try:
					os.makedirs(d)
				except OSError as e:
					sys.stderr.write("Warning (cmdargs.outdir): Directory \'%s\' could not be created / %s\n" % (d, e))
				except:
					sys.stderr.write("Warning (cmdargs.outdir): Directory \'%s\' could not be created\n" % d)
				else:
					print("Output directory (created):", d)
					outdir = d
			else:
				sys.stderr.write("Warning (cmdargs.outdir): Directory \'%s\' does not exist\n" % d)
	if outdir is None:
		if os.path.exists("data"):
			outdir = "data"
		else:
			outdir = "."
		print("Output directory:", outdir)

	if do_chdir:
		try:
			os.chdir(outdir)
		except:
			sys.stderr.write("ERROR (cmdargs.outdir): Output directory not accessible.\n")
			exit(1)
	return curdir, os.path.normpath(os.path.join(curdir, outdir))

def resume_from():
	"""Parse command-line arguments for loading pickled DiagDataPoints
	generated by tempout argument and resume process from there on.

	Returns:
	load_dir        Directory to load DiagDataPoint temporary files from.
	resume_step     Step from which to resume progress from (manual overwrite).
	"""

	values, arg = sysargv.getval('resume', n = 2, mark = None)
	sysargv.setparsed('resume')
	if values is None:
		return None, None
	resume_step = None
	load_dir = None
	# load_dir and resume_step may be specified in arbitrary order:
	for v in values:
		try:
			# For both sysargs following the 'resume' argument
			# test if it is an integer specifying the step index.
			resume_step = int(v)
		except ValueError:
			# If it's not an integer, it is either the directory value or the next argument
			if load_dir is None:
				# If we have not parsed a directory yet, do it now.
				load_dir = v
			else:
				# otherwise no step was given (single value for the resume argument).
				# Stop parsing more values (limited to 2 anyway).
				break
		sysargv.setparsednext(1)
	if load_dir is None:
		return None, None
	elif load_dir == 'last':
		tmpdirname = 'temp%s_' % outputid()
		alltempout = [tempdir for tempdir in os.listdir() if tempdir.find(tmpdirname) != -1]
		if len(alltempout) == 0:
			sys.stderr.write("WARNING (cmdargs.resume_from): Resume from 'last' run was requested, but no tempout "
			                 "folder was matched (should start with %s).\n" % os.path.join(os.getcwd(), tmpdirname))
			return None, None
		else:
			load_dir = sorted(alltempout, key = lambda t: datetime.strptime(t.split('_')[-1], '%Y-%m-%dT%H-%M-%S'))[-1]
			return load_dir, resume_step
	elif os.path.exists(load_dir):
		return load_dir, resume_step
	else:
		raise ValueError("Invalid path to temporary files for resume option: %s" % load_dir)

def plotwf(onedim = False, twodim = True):
	"""Parse command-line arguments for wave function plots (style and locations)

	Arguments:
	onedim, twodim   True or False. Whether wave-function options specific to 1
	                 and/or 2 dimensions are accepted. May not both be False.
	                 Default: False, True. (For LL mode, use default.)

	Returns:
	style       String. The plot style.
	locations   List. Indicates where to evaluate the wave functions.

	Note:
	If the command-line argument is absent, return False, None.
	"""
	if "plotwf" not in sysargv:
		return False, None
	if (not onedim) and (not twodim):
		sys.stderr.write("ERROR (cmdargs.plotwf): Arguments onedim and twodim cannot be False at the same time.\n")
	argn = sysargv.index("plotwf")
	sysargv.setparsed(argn)
	if argn + 1 >= len(sysargv):
		return "default", [0]
	style = None
	locations = []
	for arg in sysargv[argn + 1:]:
		if (arg in ['separate', 'together'] and twodim) or (arg in ['z', '1d', 'y', 'byband', 'by_band', 'color', 'colour', 'zy', 'yz'] and onedim) or arg == 'default':
			if style is not None:
				sys.stderr.write("Warning (cmdargs.plotwf): Got multiple styles for plotting wave functions.\n")
			elif arg == "by_band":
				style = "byband"
			elif arg == "colour":
				style = "color"
			elif arg == "yz":
				style = "zy"
			else:
				style = arg
		elif arg in ['zero', '0']:
			locations.append('zero')
		elif arg in ['min', 'max', 'mid', 'all']:
			locations.append(arg)
		elif arg == 'minmax':
			locations.extend(['min', 'max'])
		elif arg in ['3', 'three', 'halves']:
			locations.extend(['min', 'mid', 'max'])
		elif arg in ['5', 'five', 'quarters']:
			locations.extend(['min', '1/4', 'mid', '3/4', 'max'])
		else:
			try:
				argval = float(arg)  # If it is a number, treat it as such
			except:
				break  # No match: Stop looking further
			else:
				locations.append(argval)
		sysargv.setparsednext(1)
	if style is None:
		style = "default"
	if locations == []:
		locations = ['zero']
	return style, list(set(locations))

def bhz():
	"""Parse command-line arguments for BHZ approximation

	Returns:
	[nl, bands_a, nu]   Here, nl and nu are (even) integers that indicate the
	                    number of bands in the lower and upper B sector. They
	                    can also be None, indicating that the maximum number of
	                    bands should be taken. The middle element bands_a can
	                    be any of:
	                    (nal, nau)     Tuple of two integers indicating number
	                                   of bands in A sector above and below the
	                                   gap. Input is a pair of integers without
	                                   signs.
	                    [s1, s2, ...]  List of strings with the band labels of
	                                   bands bands in A sector. Input, e.g.,
	                                   'E1 H1'.
	                    [i1, i2, ...]  List of integers indicating band indices
	                                   of bands in A sector. Input is sequence
	                                   of integers with explicit signs, e.g.,
	                                   '-2 -1 +1 +2'.
	"""
	bhzarg = [None, None, None]
	bhzintarg = []
	bhzbandarg = []
	if "bhz" in sysargv:
		argn = sysargv.index("bhz")
		sysargv.setparsed(argn)
		if argn + 1 >= len(sysargv):
			sys.stderr.write("Warning (cmdargs.bhz): Argument \'bhz\' should be followed by at least one argument\n")
		for arg in sysargv[argn + 1:]:
			m = re.match(r'[\+\-][0-9]+', arg)
			if m is not None:
				bhzbandarg.append(int(arg))
				sysargv.setparsednext(1)
				continue
			m = re.match(r'[0-9]+', arg)
			if m is not None:
				bhzintarg.append(int(arg))
				sysargv.setparsednext(1)
				continue
			m = re.match(r'[eElLhH][0-9]+[\+\-]?', arg)
			if m is not None:
				bhzbandarg.append(arg.upper())
				sysargv.setparsednext(1)
				continue
			break
		if len(bhzintarg) == 1 and len(bhzbandarg) == 0:
			if bhzintarg[0] < 2 or (bhzintarg[0] % 2) == 1:
				sys.stderr.write("Warning (cmdargs.bhz): Numbers following argument \'bhz\' should be nonzero, even integers\n")
			na = 2 * max(bhzintarg[0] // 2, 2)
			nau = 2 * (na // 4)  # floor division
			nal = na - nau
			bhzarg = [None, (nal, nau), None]
		elif len(bhzintarg) == 2 and len(bhzbandarg) == 0:
			if bhzintarg[0] + bhzintarg[1] < 2 or (bhzintarg[0] % 2) == 1 or (bhzintarg[0] % 2) == 1:
				sys.stderr.write("Warning (cmdargs.bhz): Numbers following argument \'bhz\' should be nonzero, even integers\n")
			nau = 2 * (bhzintarg[1] // 2)  # floor division
			nal = 2 * (bhzintarg[0] // 2)  # floor division
			if nal + nau == 0:
				nal = 2
			bhzarg = [None, (nal, nau), None]
		elif len(bhzintarg) == 3 and len(bhzbandarg) == 0:
			if bhzintarg[1] < 2 or bhzintarg[0] < 2 or bhzintarg[2] < 2 or (bhzintarg[1] % 2) == 1 or (bhzintarg[0] % 2) == 1 or (bhzintarg[2] % 2) == 1:
				sys.stderr.write("Warning (cmdargs.bhz): Numbers following argument \'bhz\' should be nonzero, even integers\n")
			na = 2 * max(bhzintarg[1] // 2, 2)
			nau = 2 * (na // 4)  # floor division
			nal = na - nau
			nl = 2 * (bhzintarg[0] // 2)  # floor division
			nu = 2 * (bhzintarg[2] // 2)  # floor division
			bhzarg = [nl, [nal, nau], nu]
		elif len(bhzintarg) == 4 and len(bhzbandarg) == 0:
			if bhzintarg[0] < 2 or bhzintarg[1] < 2 or bhzintarg[2] < 2 or bhzintarg[3] < 2 or (bhzintarg[0] % 2) == 1 or (bhzintarg[1] % 2) == 1 or (bhzintarg[2] % 2) == 1 or (bhzintarg[3] % 2) == 1:
				sys.stderr.write("Warning (cmdargs.bhz): Numbers following argument \'bhz\' should be nonzero, even integers\n")
			nau = 2 * (bhzintarg[2] // 2)  # floor division
			nal = 2 * (bhzintarg[1] // 2)  # floor division
			nl = 2 * (bhzintarg[0] // 2)  # floor division
			nu = 2 * (bhzintarg[3] // 2)  # floor division
			bhzarg = [nl, (nal, nau), nu]
		elif len(bhzintarg) == 0 and len(bhzbandarg) > 0:
			bhzarg = [None, bhzbandarg, None]
		elif len(bhzintarg) == 2 and len(bhzbandarg) > 0:
			if bhzintarg[1] < 2 or bhzintarg[0] < 2 or (bhzintarg[1] % 2) == 1 or (bhzintarg[0] % 2) == 1:
				sys.stderr.write("Warning (cmdargs.bhz): Numbers following argument \'bhz\' should be nonzero, even integers\n")
			nl = 2 * (bhzintarg[0] // 2)  # floor division
			nu = 2 * (bhzintarg[1] // 2)  # floor division
			bhzarg = [nl, bhzbandarg, nu]
		else:
			sys.stderr.write("Warning (cmdargs.bhz): Illegal combination of band ids and amounts. Default to four-band model.\n")
			bhzarg = [None, (2, 2), None]
	else:
		sys.stderr.write("Warning (cmdargs.bhz): Argument \'bhz\' is absent. Default to four-band model.\n")
		bhzarg = [None, (2, 2), None]
	return bhzarg

def bandalign(directory = None):
	"""Parse command-line arguments for band alignment (aka 'reconnection') parameters

	Argument:
	directory   String or None. Directory to seek for the input file. If None,
	            use the current directory.

	Returns:
	A dict instance with the following elements, if the command-line argument is
	present. This dict should be passed as keyword argument to bandindices() of
	bandalign.py.
	e0         Float or None. Energy.
	g0         Integer or None. Gap index.
	from_file  String or None. Filename of a '...byband.csv' file.
	If the command-line argument is absent, return the empty dict {}, not None.
	For testing whether the argument has been given, use 'if returnvalue:', not
	'if returnvalue is None:'.
	"""
	val, arg = sysargv.getval(['bandalign', 'reconnect'], 2)
	if val is None:
		return {}  # see comment in docstring under 'Returns:'
	e0 = None
	g0 = None
	from_file = None
	try:
		e0 = float(val[0])
	except:
		from_file = val[0]
	if from_file is not None:
		if directory is not None:
			from_file = os.path.join(directory, from_file)
		if not os.path.isfile(from_file):
			from_file = None
	if e0 is not None:
		try:
			g0 = int(val[1])
		except:
			pass
	# TODO: second argument should not be marked as parsed if g0 is None
	return {'e0': e0, 'g0': g0, 'from_file': from_file}

def select():
	"""Parse command-line argument for selection of k points (kdotpy compare, kdotpy merge)"""
	val, arg = sysargv.getval(['select'], 2)
	if val is None:
		return None, None
	try:
		sel_component = arg[0]
		sel_value = float(arg[1])
	except:
		sys.stderr.write("ERROR: Argument \"select\" must be followed by k, kx, ky, or kphi and a number.\n")
		exit(1)
	return sel_component, sel_value

def input_file_lists():
	"""Parse lists of input files that appear after '--' and are grouped by 'vs'"""
	filelist = []
	filelists = []

	# If the argument '--' appears in the command line, consider only the arguments
	# after the last '--' as input files
	argstart = 1
	for j in range(1, len(sysargv)):
		if sysargv.argv[j] == '--':
			argstart = j
	for a in sysargv.argv[argstart:]:
		if os.path.isfile(a):
			if a.endswith(".tar.gz") or a.endswith(".tar"):
				tar_contents = find_in_tar(a, "output*.xml")
				if tar_contents is not None and tar_contents != []:
					filelist.extend(tar_contents)
			else:
				filelist.append(a)
		elif os.path.isdir(a):
			ls = os.listdir(a)
			filenames_thisdir = []
			for fname in ls:
				m = re.match(r"output.*\.xml(\.gz)?", fname)
				if m is not None:
					filenames_thisdir.append(os.path.join(a, fname))
				m = re.match(r"data.*\.tar\.gz", fname)
				if m is not None:
					tar_contents = find_in_tar(os.path.join(a, fname), "output*.xml")
					if tar_contents is not None and tar_contents != []:
						filenames_thisdir.extend(tar_contents)
			if len(filenames_thisdir) > 0:
				filelist.extend(filenames_thisdir)
			else:
				sys.stderr.write("Warning (cmdargs.filenames): No data files \"output*.xml\" found in directory %s\n" % a)
		elif a == 'vs' and len(filelist) > 0:
			filelists.append(filelist)
			filelist = []
	if len(filelist) > 0:
		filelists.append(filelist)
	return filelists

def input_files():
	return [f for l in input_file_lists() for f in l]
