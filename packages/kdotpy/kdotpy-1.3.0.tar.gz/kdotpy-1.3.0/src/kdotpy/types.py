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

from abc import ABC, abstractmethod
from typing import Any, Optional, Union
import numpy as np

class Vector(ABC):
	"""ABC for Vector"""

	value: Union[float, tuple]
	vtype: str
	degrees: Optional[bool]
	aunit: Optional[float]

	@abstractmethod
	def len(self, square=False):
		pass

	@abstractmethod
	def __abs__(self):
		pass

	@abstractmethod
	def x(self):
		pass

	@abstractmethod
	def y(self):
		pass

	@abstractmethod
	def z(self):
		pass

	@abstractmethod
	def xy(self):
		pass

	@abstractmethod
	def xyz(self):
		pass

	@abstractmethod
	def pm(self):
		pass

	@abstractmethod
	def pmz(self):
		pass

	@abstractmethod
	def polar(self, deg=True, fold=True):
		pass

	@abstractmethod
	def cylindrical(self, deg=True, fold=True):
		pass

	@abstractmethod
	def spherical(self, deg=True, fold=True):
		pass

	@abstractmethod
	def component(self, comp, prefix=''):
		pass

	@abstractmethod
	def components(self, prefix = ''):
		pass

	@abstractmethod
	def to_dict(self, prefix = '', all_components = False):
		pass

	@abstractmethod
	def get_pname_pval(self, prefix=''):
		pass

	@abstractmethod
	def set_component(self, comp, val=None, prefix='', inplace=True):
		pass

	@abstractmethod
	def astype(self, astype, inplace=False, deg=None, fold=True, force=False):
		pass

	@abstractmethod
	def reflect(self, axis = None, inplace = False, deg = None, fold = True):
		pass

	@abstractmethod
	def __neg__(self):
		pass

	@abstractmethod
	def diff(self, other, square=False):
		pass

	@abstractmethod
	def __sub__(self, other):
		pass

	@abstractmethod
	def equal(self, other, acc=1e-9):
		pass

	@abstractmethod
	def zero(self, acc=1e-9):
		pass

	@abstractmethod
	def __eq__(self, other):
		pass

	@abstractmethod
	def __ne__(self, other):
		pass

	@abstractmethod
	def identical(self, other, acc=1e-9):
		pass

	@abstractmethod
	def parallel(self, other, acc=1e-9):
		pass

	@abstractmethod
	def perpendicular(self, other, acc = 1e-9):
		pass

	@abstractmethod
	def __str__(self, formatstr='%6.3f'):
		pass

	@abstractmethod
	def __repr__(self):
		pass

	@abstractmethod
	def xmlattr(self, prefix = ''):
		pass

	@abstractmethod
	def to_tuple(self):
		pass

class VectorTransformation:
	"""ABC for VectorTransformation"""

	name: str
	mat_cart: Optional[np.ndarray]
	mat_cyl: Optional[np.ndarray]
	mat_sph: Optional[np.ndarray]
	delta_cyl: np.ndarray
	delta_sph: np.ndarray
	mat_e: np.ndarray
	a2g: float

	@abstractmethod
	def grid_safe(self, vtype, var):
		pass

	@abstractmethod
	def __call__(self, v, fold = True):
		pass

	@abstractmethod
	def transform(self, rep, values):
		pass

	@abstractmethod
	def __mul__(self, other):
		pass

	@abstractmethod
	def inv(self):
		pass

	@abstractmethod
	def det(self):
		pass

	@abstractmethod
	def __str__(self):
		pass

class VectorGrid(ABC):
	"""ABC for VectorGrid"""

	var: list[str]
	values: list[np.ndarray]
	const: list[str]
	constvalues: list[Union[int, float, np.ndarray]]
	vtype: str
	degrees: Optional[bool]
	shape: tuple[int, ...]
	ndim: int
	prefix: str

	@classmethod
	@abstractmethod
	def legacy(cls, *args, prefix=None, **kwds):
		pass

	@classmethod
	@abstractmethod
	def from_components(cls, val, var, constval, const, **kwds):
		pass

	@abstractmethod
	def __getitem__(self, idx):
		pass

	@abstractmethod
	def get_array(self, comp=None):
		pass

	@abstractmethod
	def get_components(self, include_prefix=False):
		pass

	@abstractmethod
	def get_grid(self, comp=None):
		pass

	@abstractmethod
	def get_values(self, comp, flat=True):
		pass

	@abstractmethod
	def __iter__(self):
		pass

	@abstractmethod
	def __len__(self):
		pass

	@abstractmethod
	def subgrid_shapes(self, dim):
		pass

	@abstractmethod
	def __min__(self):
		pass

	@abstractmethod
	def __max__(self):
		pass

	@abstractmethod
	def __eq__(self, other):
		pass

	@abstractmethod
	def index(self, v, flat=True, acc=None, angle_fold=True, fast_method_only=True):
		pass

	@abstractmethod
	def get_var_const(self, return_tuples=False, use_prefix=True):
		pass

	@abstractmethod
	def select(self, *arg, flat=True, acc=1e-10, fold=None, deg=None):
		pass

	@abstractmethod
	def subdivide(self, comp, subdivisions, quadratic=None):
		pass

	@abstractmethod
	def subdivide_to(self, comp, n_target, quadratic=None):
		pass

	@abstractmethod
	def midpoints(self):
		pass

	@abstractmethod
	def symmetrize(self, axis=None, deg=None):
		pass

	@abstractmethod
	def integration_element(self, dk=None, dphi=None, full=True, flat=True):
		pass

	@abstractmethod
	def volume(self, *args, **kwds):
		pass

	@abstractmethod
	def jacobian(self, component, unit=False):
		pass

	@abstractmethod
	def gradient_length_coeff(self):
		pass

	@abstractmethod
	def get_derivative_components(self):
		pass

	@abstractmethod
	def identical(self, other, acc=1e-9):
		pass

	@abstractmethod
	def equal(self, other, acc=1e-9):
		pass

	@abstractmethod
	def get_subset(self, indices):
		pass

	@abstractmethod
	def is_subset_of(self, other, acc=1e-9):
		pass

	@abstractmethod
	def is_compatible_with(self, other, acc=1e-9):
		pass

	@abstractmethod
	def is_sorted(self, increasing=False, strict=True):
		pass

	@abstractmethod
	def zero(self):
		pass

	@abstractmethod
	def is_vertical(self):
		pass

	@abstractmethod
	def is_inplane(self):
		pass

	@abstractmethod
	def sort(self, in_place=False, flat_indices=False, expand_indices=False):
		pass

	@abstractmethod
	def extend(self, other, acc=1e-9):
		pass

	@abstractmethod
	def to_dict(self):
		pass

class ZippedKB(ABC):
	"""ABC for ZippedKB"""

	k: Union[None, list[Vector], VectorGrid]
	b: Union[None, list[Vector], VectorGrid]

	@abstractmethod
	def __len__(self):
		pass

	@abstractmethod
	def shape(self):
		pass

	@abstractmethod
	def __iter__(self):
		pass

	@abstractmethod
	def __getitem__(self, idx):
		pass

	@abstractmethod
	def dependence(self):
		pass

	@abstractmethod
	def get_grid(self):
		pass

	@abstractmethod
	def to_dict(self):
		pass

class DiagDataPoint(ABC):
	"""ABC for diagdata.DiagDataPoint"""

	k: Any  # float, Vector
	paramval: Any
	eival: Optional[np.ndarray]
	eivec: Optional[np.ndarray]
	neig: int
	dim: Optional[int]
	obsvals: Optional[np.ndarray]
	_obsids: Optional[list[str]]
	bindex: Optional[np.ndarray]
	llindex: Optional[np.ndarray]
	aligned_with_e0: bool
	char: Union[np.ndarray, list, None]
	transitions: Any  # TransitionsData, None
	wffigure: Any  # int, str, matplotlib figure object
	current_step: Optional[int]
	ham: Any  # np.ndarray, scipy sparse matrix object
	grid_index: int
	tuple_index: Optional[dict]
	opts: dict
	binary_file: Optional[str]

	@property
	@abstractmethod
	def obsids(self):
		pass

	@abstractmethod
	def __str__(self):
		pass

	@abstractmethod
	def hash_id(self, length=6, precision='%.12e'):
		pass

	@abstractmethod
	def file_id(self):
		pass

	@abstractmethod
	def stitch_with(self, k, eival, eivec, targetenergy_old, targetenergy_new, inplace=False, accuracy=0.01):
		pass

	@abstractmethod
	def update(self, new_ddp):
		pass

	@abstractmethod
	def extend_by(self, k, eival, eivec, paramval = None, obsvals = None, obsids = None, char = None, llindex = None, bindex = None, accuracy = 1e-6):
		pass

	@abstractmethod
	def extend(self, *args, **kwds):
		pass

	@abstractmethod
	def set_observables(self, obsvals, obsids = None):
		pass

	@abstractmethod
	def calculate_observables(self, params, obs, obs_prop = None, overlap_eivec = None, magn = None, ll_full = False):
		pass

	@abstractmethod
	def add_observable(self, obsvals = None, obsid = None):
		pass

	@abstractmethod
	def reset_observable(self, obsid=None, value=np.nan):
		pass

	@abstractmethod
	def delete_eivec(self):
		pass

	@abstractmethod
	def build_tuple_index_cache(self):
		pass

	# Some 'get' functions
	@abstractmethod
	def get_index(self, val):
		pass

	@abstractmethod
	def get_index_with_llindex(self, val, llindex):
		pass

	@abstractmethod
	def get_ubindex(self):
		pass

	@abstractmethod
	def get_eival(self, val):
		pass

	@abstractmethod
	def get_eival0(self):
		pass

	@abstractmethod
	def get_char(self, val):
		pass

	@abstractmethod
	def get_all_char(self):
		pass

	@abstractmethod
	def get_observable(self, obs, val = None):
		pass

	@abstractmethod
	def set_observable_value(self, obs, bandval, obsval):
		pass

	@abstractmethod
	def subset(self, sel):
		pass

	@abstractmethod
	def subset_inplace(self, sel):
		pass

	@abstractmethod
	def select_llindex(self, ll):
		pass

	@abstractmethod
	def select_bindex(self, b):
		pass

	@abstractmethod
	def select_obs(self, obs, val, accuracy = None):
		pass

	@abstractmethod
	def select_eival(self, val):
		pass

	@abstractmethod
	def select_char(self, which, inplace = False):
		pass

	@abstractmethod
	def sort_by_eival(self, inplace = False, reverse = False):
		pass

	@abstractmethod
	def sort_by_obs(self, obs, inplace = False):
		pass

	@abstractmethod
	def set_eivec_phase(self, accuracy = 1e-6, inplace = False):
		pass

	@abstractmethod
	def get_eivec_coeff(self, norbitals, accuracy = 1e-6, ll_full = False, ny = None):
		pass

	@abstractmethod
	def set_char(self, chardata, eival = None, llindex = None, eival_accuracy = 1e-6):
		pass

	@abstractmethod
	def set_bindex(self, bindexdata, eival = None, llindex = None, aligned_with_e0 = False):
		pass

	@abstractmethod
	def set_llindex(self, llindex):
		pass

	@abstractmethod
	def set_eivec(self, eivec, val = None):
		pass

	@abstractmethod
	def to_binary_file(self, filename):
		pass


### DIAGDATA ###
class DiagData(ABC):
	"""ABC for diagdata.DiagData"""

	data: list[DiagDataPoint]
	shape: tuple
	strides: tuple
	grid: Any  # TODO: VectorGrid
	gridvar: Optional[str]
	bindex_cache: Optional[list]
	binary_file: Optional[str]

	@abstractmethod
	def align_with_grid(self):
		pass

	@abstractmethod
	def sort_by_grid(self):
		pass

	@abstractmethod
	def get_momenta(self):
		pass

	@abstractmethod
	def get_momentum_grid(self):
		pass

	@abstractmethod
	def get_paramval(self, component = None):
		pass

	@abstractmethod
	def get_xval(self, index = None):
		pass

	@abstractmethod
	def get_degrees(self, default = None):
		pass

	@abstractmethod
	def get_zero_point(self, return_index = False, ignore_paramval = False):
		pass

	@abstractmethod
	def get_base_point(self, return_index = False):
		pass

	@abstractmethod
	def get_total_neig(self):
		pass

	@abstractmethod
	def select_llindex(self, llval):
		pass

	@abstractmethod
	def select_eival(self, val):
		pass

	@abstractmethod
	def set_char(self, chardata, eival = None, llindex = None, eival_accuracy = 1e-6):
		pass

	@abstractmethod
	def get_all_char(self):
		pass

	@abstractmethod
	def get_all_llindex(self):
		pass

	@property
	@abstractmethod
	def aligned_with_e0(self):
		pass

	@abstractmethod
	def reset_bindex(self):
		pass

	@abstractmethod
	def get_all_bindex(self):
		pass

	@abstractmethod
	def check_bindex(self):
		pass

	@abstractmethod
	def get_eival_by_bindex(self, b = None):
		pass

	@abstractmethod
	def get_observable_by_bindex(self, obs = None, b = None):
		pass

	@abstractmethod
	def find(self, kval, paramval = None, return_index = False, strictmatch = False):
		pass

	@abstractmethod
	def get_data_labels(self, by_index = None):
		pass

	@abstractmethod
	def get_plot_coord(self, label, mode):
		pass

	@abstractmethod
	def get_observable(self, obs, label, mode):
		pass

	@abstractmethod
	def set_observable_values(self, obsid, obsval, label):
		pass

	@abstractmethod
	def shift_energy(self, delta):
		pass

	@abstractmethod
	def set_zero_energy(self, delta = 0.0):
		pass

	@abstractmethod
	def set_shape(self, shape = None):
		pass

	@abstractmethod
	def symmetry_test(self, tfm, observables = None, ignore_lower_dim = False, verbose = False):
		pass

	@abstractmethod
	def symmetrize(self, axis = None, copy_eivec = True):
		pass

	@abstractmethod
	def get_cnp(self):
		pass

	## Forward of 'list-like' functions
	@abstractmethod
	def __len__(self):
		pass

	@abstractmethod
	def index(self, x):
		pass

	@abstractmethod
	def __iter__(self):
		pass

	@abstractmethod
	def __getitem__(self, i):
		pass

	@abstractmethod
	def append(self, data, strictmatch = False):
		pass

	@abstractmethod
	def extend(self, data):
		pass

	@abstractmethod
	def __add__(self, other):
		pass

	@abstractmethod
	def __radd__(self, other):
		pass

	@abstractmethod
	def __iadd__(self, other):
		pass

	@abstractmethod
	def interpolate(self, subdiv = 1, obs = False):
		pass

	@abstractmethod
	def to_binary_file(self, filename):
		pass

	@abstractmethod
	def diagonalize(self, model, solver, opts_list = None):
		pass

class PhysParams(ABC):
	kdim: int
	norbitals: int
	zres: float
	yres: float
	linterface: float
	ly_width: float
	ny_midpoints: bool
	ny: int
	yconfinement: Union[int, float]
	lattice_orientation: Optional[list]
	lattice_trans: Optional[Union[list, float, np.ndarray]]
	magn: Any
	temperature: float
	substrate_material: Any
	a_lattice: Optional[float]
	layer_material: Any
	layerstack: Any

	lz_thick: float
	nz: int
	zinterface: list[int]
	nlayer: int

	c_dz: Union[float, complex]
	c_dz2: Union[float, complex]
	c_dy: Union[float, complex]
	c_dy2: Union[float, complex]

	ymid: float
	ninterface: int
	dzinterface: float
	has_exchange: bool

	@abstractmethod
	def to_dict(self, material_format = 'sub'):
		pass

	@abstractmethod
	def diff(self, other):
		pass

	@abstractmethod
	def print_diff(self, arg, style = None):
		pass

	@abstractmethod
	def check_equal(self, arg, ignore = None):
		pass

	@abstractmethod
	def lattice_transformed(self):
		pass

	@abstractmethod
	def lattice_transformed_by_matrix(self):
		pass

	@abstractmethod
	def lattice_transformed_by_angle(self):
		pass

	@abstractmethod
	def make_param_cache(self):
		pass

	@abstractmethod
	def clear_param_cache(self):
		pass

	@abstractmethod
	def z(self, z):
		pass

	@abstractmethod
	def zvalues_nm(self, extend = 0):
		pass

	@abstractmethod
	def interface_z_nm(self):
		pass

	@abstractmethod
	def yvalues_nm(self, extend = 0):
		pass

	@abstractmethod
	def well_z(self, extend_nm = 0.0, strict = False):
		pass

	@abstractmethod
	def well_z_nm(self, extend_nm = 0.0, strict = False):
		pass

	@abstractmethod
	def symmetric_z(self, strict = False):
		pass
