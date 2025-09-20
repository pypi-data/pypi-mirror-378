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
import sys
import os
from typing import Optional, Any, Union

from matplotlib import use as mpluse
mpluse('pdf')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.colors as mplcolors

from .colortools import hsl_to_rgb, rgb_to_hsl, try_colormap
from .tools import get_fignum, get_plot_size, plotswitch
from .toolstext import set_xlabel, set_ylabel, get_partext

from ..physconst import eoverhbar
from ..phystext import orbital_labels
from ..observables import blockdiag
from ..types import Vector, PhysParams, DiagDataPoint
from ..config import get_config, get_config_bool, get_config_num
from ..iotools import get_unique_filenames, convert_pngs_to_pdf

orb_colors = ['r', 'c', 'b', 'g', 'm', 'y', '#3fdf3f', '#ff7fff']
orb_labels = ["$|" + orb_label.strip('$').lstrip('$') + "\\rangle$" for orb_label in orbital_labels(style = 'tex')]
ls_p, ls_m = '-', (0, (1.3, 1.0))
orb_ls = [ls_p, ls_m, ls_p, ls_p, ls_m, ls_m, ls_p, ls_m]

### TOOLS ###
def get_bandlabel(diagdatapoint: DiagDataPoint, bandlabels: Any, j: int) -> str:
	"""Get band label string for state j in a DiagDataPoint instance.

	Arguments:
	diagdatapoint  DiagDataPoint instance.
	bandlabels     Passed from other plot functions that determines what type
	               of label should be shown. If None, determine automatically.
	               If a string, use one label for all states. If a list or array
	               of strings, use different labels for the states. If a tuple
	               of the form (string, list of strings), apply first element as
	               a formatter for the strings in the list.
	j              Integer. The index of the state in the DiagDataPoint.

	Returns:
	bandlabel      String, possibly empty.
	"""
	if bandlabels is None:
		bandlabel = diagdatapoint.char[j] if diagdatapoint.char is not None and '?' not in diagdatapoint.char[j] else diagdatapoint.bindex[j] if diagdatapoint.bindex is not None else ("%i" % j)
	elif isinstance(bandlabels, str):
		bandlabel = bandlabels
	elif isinstance(bandlabels, (list, np.ndarray)):
		bandlabel = bandlabels[j]
	elif isinstance(bandlabels, tuple) and len(bandlabels) == 2 and isinstance(bandlabels[0], str) and isinstance(bandlabels[1], (list, np.ndarray)):
		bandlabel = bandlabels[0] % bandlabels[1][j]
	else:
		sys.stderr.write("Warning (ploto.get_bandlabel): Band label argument invalid.\n")
		bandlabel = ""
	return str(bandlabel)

def subband_overlap_colors(overlap_eivec: dict[str, Any]) -> dict[str, Any]:
	"""Get colors for subband overlaps"""
	ov_bands = []
	for ov in overlap_eivec:
		if len(ov) >= 3 and ov[0] in 'eElLhH' and ov[1] in '123456789':
			ov1 = ov[0].upper() + ov[1]
			if ov1 not in ov_bands:
				ov_bands.append(ov1)
	ov_bands = sorted(ov_bands)
	subcolors = {}
	if len(ov_bands) == 2:
		subcolors[ov_bands[0]] = 'r'
		subcolors[ov_bands[1]] = 'b'
	elif len(ov_bands) <= 6:
		for ov_band, color in zip(ov_bands, ['r', 'g', 'b', 'y', 'm', 'c']):
			subcolors[ov_bands] = color
	else:
		for j, ov_band in enumerate(ov_bands):
			subcolors[ov_band] = hsl_to_rgb([j / len(ov_bands), 1.0, 0.5])
	return subcolors

def rgb_color(color_model: str, r: np.ndarray, g: np.ndarray, b: np.ndarray, s: np.ndarray, vmax: float = 1.0) -> np.ndarray:
	"""Extract RGB colour map

	Arguments:
	color_model   'hsv', 'hsl', or 'rgb'. The colour model to use.
	r, g, b       Arrays of dim 2. The data for the red, green, blue colour
	              channels, between 0 and 1.
	s             Array of dim 2. The sum, which acts as a scaling factor or to
	              set the colour intensity.
	vmax          Float. Maximum value by which to scale.

	Returns:
	rgb           Array of dim 3. RGB colour triplets for each data point.
	"""
	zeros, ones = np.zeros_like(s), np.ones_like(s)
	if color_model == 'hsv':
		# HSV color model
		rr = np.where(s == 0, zeros, r / s)
		gg = np.where(s == 0, zeros, g / s)
		bb = np.where(s == 0, zeros, b / s)
		hh = mplcolors.rgb_to_hsv(np.dstack((rr, gg, bb)))[:, :, 0]
		hsv = np.dstack((hh, (s / vmax)**2, ones))
		rgb = mplcolors.hsv_to_rgb(hsv)
	elif color_model == 'hsl':
		# HSL color model (default)
		rr = np.where(s == 0, zeros, r / s)
		gg = np.where(s == 0, zeros, g / s)
		bb = np.where(s == 0, zeros, b / s)
		hh = rgb_to_hsl(np.dstack((rr, gg, bb)))[:, :, 0]
		hsl = np.dstack((hh, ones, 1 - 0.5 * (s / vmax)**2))
		rgb = hsl_to_rgb(hsl)
	elif color_model == 'rgb':
		# Simple RGB color model (inversion is required to map zero to white)
		rr = 1.0 - (g + b) / vmax  # 1 - anti-red
		gg = 1.0 - (r + b) / vmax  # 1 - anti-green
		bb = 1.0 - (r + g) / vmax  # 1 - anti-blue
		rgb = np.dstack((rr, gg, bb))
	else:
		raise ValueError("Invalid value for variable 'color'")
	return rgb

def display_parameter_text(paramvalue: Any, var: Optional[str] = None, ax: Optional[Axes] = None, text_y: float = 0.97) -> float:
	"""Display parameter text in the upper left corner in the form $param=value$.

	Arguments:
	paramvalue  None, dict, Vector instance, or numerical value. If a Vector or
	            numerical value, show the value. If a dict, show '$key=value$'
	            on subsequent lines. If None, do not show.
	var         None or string. If paramvalue is a Vector instance, use this
	            string as the variable name. If None, use 'k'. This argument is
	            ignored if paramvalue is a dict instance.
	ax          Matplotlib Axes object or None. If None, use the current Axes.
	text_y      Float. Vertical coordinate of the text.

	Returns:
	text_y      Float. Vertical coordinate of the next line of text. It is
	            decreased by a fixed value for every line of text.
	"""
	if ax is None:
		ax = plt.gca()
	if var is None:
		var = 'k'
	if isinstance(paramvalue, dict) and len(paramvalue) > 0:
		for var in paramvalue:
			if isinstance(paramvalue[var], Vector):
				var1 = var.lower() if isinstance(var, str) and var.lower() in ['k', 'b'] else var
				pname, pval = paramvalue[var].get_pname_pval(prefix = var1)
				parstr = get_partext(pval, pname).replace('For ', 'At ')
			elif isinstance(paramvalue[var], (int, np.integer, float, np.floating)):
				parstr = "At $%s=%g$" % (str(var), paramvalue[var])
			else:
				parstr = "At $%s=%s$" % (str(var), str(paramvalue[var]))
			ax.text(0.02, text_y, parstr, ha='left', va='top', transform=ax.transAxes)
			text_y -= 0.07
	elif isinstance(paramvalue, Vector):
		var1 = var.lower() if isinstance(var, str) and var.lower() in ['k', 'b'] else var
		pname, pval = paramvalue.get_pname_pval(prefix = var1)
		parstr = get_partext(pval, pname).replace('For ', 'At ')
		ax.text(0.02, text_y, parstr, ha='left', va='top', transform=ax.transAxes)
		text_y -= 0.07
	elif isinstance(paramvalue, (int, np.integer, float, np.floating)):
		ax.text(0.02, text_y, "At $%s=%g$" % (str(var), paramvalue), ha='left', va='top', transform=ax.transAxes)
		text_y -= 0.07
	return text_y

def reorder_legend(handles: list, labels: list, order: Optional[list[Optional[int]]] = None) -> tuple[list, list]:
	"""Reorder legend handles and labels, and possibly insert empty spaces

	Arguments:
	handles   List of legend handles
	labels    List of legend labels (str instances)
	order     None or list of integers and None. If None, take from
	          configuration option.

	Returns:
	handles_ordered   Reordered list of legend handles
	labels_ordered    Reordered list of legend labels
	"""
	if order is None:
		orb_order = get_config('plot_wf_orbitals_order', ['standard', 'paired', 'table'])
		if orb_order == 'standard':  # standard order
			order = [0, 1, 2, 3, 4, 5, 6, 7]
		elif orb_order == 'paired':  # paired Gamma6,±1/2 Gamma8,±1/2
			order = [0, 3, 2, 1, 4, 5, 6, 7]
		elif orb_order == 'table':  # orbitals vertically, Jz horizontally ordered
			order = [None, 0, 1, None, 2, 3, 4, 5, None, 6, 7]
		else:
			raise ValueError("Invalid value for configuration value 'plot_wf_orbitals_order'.")
	handles_ordered = []
	labels_ordered = []
	for o in order:
		if o is None:
			emptyplot, = plt.plot(np.nan, np.nan, '-', color='none')
			handles_ordered.append(emptyplot)
			labels_ordered.append("")  # TODO: Fix alignment
		elif not isinstance(o, int):
			raise TypeError("Argument order must be a list containing integers or None.")
		elif o >= 0 and o < len(handles) and o < len(labels):
			handles_ordered.append(handles[o])
			labels_ordered.append(labels[o])
		# else: silently skip
	# TODO: Empty elements at the end need to be deleted
	return handles_ordered, labels_ordered

def add_phases_legend(phases: np.ndarray, orbsel: Optional[np.ndarray] = None, ax: Optional[Axes] = None, text_y: float = 0.76) -> float:
	"""Add list of phases (complex arguments)

	Arguments:
	phases    Array of floats. Complex phases for each orbital in radians.
	orbsel    Array of booleans or None. If an array, select only the orbitals
	          with True value.
	ax        Matplotlib Axes instance or None.
	text_y    Float. Vertical position.

	Returns:
	text_y    Float. Vertical position for the following line of text.
	"""
	if ax is None:
		ax = plt.gca()
	if orbsel is None:
		orbsel = np.ones_like(phases, dtype=bool)
	for osel, phi, col in zip(orbsel, np.rad2deg(phases), orb_colors):
		if osel:
			ax.text(0.98, text_y, "%4i\u00b0" % np.round(phi), ha='right', va='top',	color=col, transform=ax.transAxes)
			text_y -= 0.04
	return text_y

def add_material_labels(params: PhysParams, ax: Optional[Axes] = None, vertical: bool = False) -> None:
	"""Add material labels

	Arguments:
	params    PhysParams instance
	ax        Matplotlib Axes instance
	vertical  True or False. Whether z is the vertical axis. Choose True for
	          wave function plots of psi(z, y), False for psi(z).
	"""
	mat_lab_rot = get_config_num('plot_wf_mat_label_rot')
	mat_min_thick = 0.08 if vertical else get_config_num('plot_wf_mat_min_thick_label')
	z = params.zvalues_nm()
	if ax is None:
		ax = plt.gca()
	for n in range(0, params.nlayer):
		d = params.layerstack.thicknesses_z[n]
		if d > (z.max() - z.min()) * mat_min_thick:
			mat = params.layerstack.materials[n]['material'].format('tex')
			zl = 0.5 * (params.layerstack.zinterface_nm[n] + params.layerstack.zinterface_nm[n + 1]) - 0.5 * params.lz_thick
			if vertical:
				ax.text(0.97, (zl - z.min()) / (z.max() - z.min()), mat, ha='right', va='center', transform=ax.transAxes)
			else:
				ax.text((zl - z.min()) / (z.max() - z.min()), 0.05, mat, ha='center', va='bottom', rotation=mat_lab_rot, transform=ax.transAxes)

### PLOT FUNCTIONS ###

@plotswitch
def _wavefunction_z_single(
		eivec: np.ndarray, params: Optional[PhysParams] = None, filename: str = "",
		energy: Optional[float] = None, display_k: Optional[dict] = None,
		ll_full: bool = False, bandlabel: str = "",
		basis_mat: Optional[np.ndarray] = None, basislabels: Optional[list] = None,
		phase_rotate: Union[bool, str] = False, phase_kval: Optional[Vector] = None,
		coeff_at_max: Optional[np.ndarray] = None) -> Figure:
	"""Plot a single wave function as function of z (private)

	Arguments:
	eivec         Array of dim 1. The eigenvector.
	params        PhysParams instance
	filename      String. The filename where to save the plot. If not set,
	              produce the figure but do not write it to a file.
	energy        Float or None. If set, write the energy as parameter text into
	              the plot.
	display_k     None, dict or a Vector instance. If a Vector, show the value.
	              If a dict, show '$key=value$' joined with commas. If None, do
	              not show.
	ll_full       True or False. Set to True for full LL mode, else False. The
	              effect is that the 'y' value at which the section is taken
	              (in full LL mode, this is the LL index) is where the integral
	              $\\int |\\psi(z, y)|^2 dz$ is maximal. In other cases, the
	              section is taken at y = 0 (at the center).
	bandlabel     String. Band label to write as parameter text into the plot.
	basis_mat     Array of dim 2. Transformation matrix for the eigenvectors.
	              Expand the wave functions in this basis  rather than the
	              standard basis of orbitals. The matrix should contain the
	              basis vectors as row vectors.
	basislabels   List of strings. The expressions for the basis states. This
	              may also be used for the standard basis, i.e., if argument
	              basis is None.
	phase_rotate  True, False, or 'k'. If True (default), multiply the
	              eigenvector by a phase factor such that the value psi_i of
	              largest magnitude is purely real with Re psi_i > 0. In case
	              the phases are already set with DiagDataPoint.set_eivec_phase(),
	              it is recommended to use False, so that the phase choice is
	              not overwritten. If the value is 'k', then rotate according to
	              the in-plane angle of the momentum.
    phase_kval    Vector or None. If phase_rotate is set to 'k', use the polar
                  angle of this vector in order to set the phase of the
                  eigenvector.
    coeff_at_max  Complex. The eigenvector element of each orbital component
                  where the magnitude is maximal.

	Returns:
	fig           Matplotlib Figure instance.
	"""
	fig = plt.figure(get_fignum(), figsize=get_plot_size('s'))
	plt.subplots_adjust(**get_plot_size('subplot'))
	ax = fig.add_subplot(1, 1, 1)

	nz, ny, norb = params.nz, params.ny, params.norbitals
	dz = params.zres

	if params.kdim == 1:  # 1D (proper)
		eivec0 = np.reshape(eivec, (ny, norb * nz))
		ny_sect = ny // 2  # take a section in the middle
		eivec = eivec0[ny_sect, :]
		nrm = np.vdot(eivec, eivec)
		eivec /= np.sqrt(nrm)  # normalize only for proper 1D, but not LL
	elif params.kdim == 2 and ll_full:  # 2D full LL
		eivec0 = np.reshape(eivec, (ny, norb * nz))
		abseivec2 = np.abs(eivec0) ** 2
		ny_sect = np.argmax(np.sum(abseivec2, axis=1))
		eivec = eivec0[ny_sect, :]  # normalize only for proper 1D, but not LL
		nrm = np.vdot(eivec, eivec)
	else:
		ny_sect, nrm = None, 1.0

	# Apply basis transformation
	if basis_mat is not None:
		eivec = basis_mat @ eivec

	z = params.zvalues_nm()
	zint = params.interface_z_nm()
	plt.plot([z.min(), z.max()], [0, 0], 'k-')

	# Apply phase factor
	phase = 1
	if phase_rotate is True:
		# Try to make largest component purely real
		psimax = eivec[np.argmax(np.abs(eivec))]
		phase = psimax / abs(psimax)
	elif phase_rotate == 'k' and isinstance(phase_kval, Vector):
		# Rotate by momentum vector phase (slightly experimental/heuristic)
		orbmax = np.argmax(np.abs(eivec)) % norb
		k, kphi = phase_kval.polar(deg=False, fold=True)
		if abs(k) < 1e-7:
			kphi = 0
		elif k < 0:  # not sure why this is necessary, in view of 'fold = true'
			kphi = np.mod(kphi, 2 * np.pi) - np.pi
		jz = np.array([0.5, -0.5, 1.5, 0.5, -0.5, -1.5, 0.5, -0.5][orbmax])
		phase = np.exp(1.j * jz * kphi)

	phases = np.angle(coeff_at_max / phase, deg=False)
	orbsel = []
	allplots = []
	legendlabels = []

	for b in range(0, norb):
		psi = eivec[b::norb]
		psi2 = np.vdot(psi, psi)
		orb_label = basislabels[b] if basislabels else orb_labels[b]
		if psi2 > 5e-3:
			re_max = np.amax(np.abs(np.real(psi / phase)))
			im_max = np.amax(np.abs(np.imag(psi / phase)))
			if get_config_bool('plot_wf_orbitals_realshift'):  # Plot all orbital components shifted to real functions
				thisplot, = plt.plot(
					z, np.real(psi * np.exp(-1j * phases[b]) / phase) / np.sqrt(dz),
					linestyle=orb_ls[b], color=orb_colors[b])  # Note normalization
			elif im_max < 1e-5:  # purely real
				thisplot, = plt.plot(z, np.real(psi / phase) / np.sqrt(dz), '-', color=orb_colors[b])  # Note normalization
			elif re_max < 1e-5:  # purely imaginary
				thisplot, = plt.plot(z, np.imag(psi / phase) / np.sqrt(dz), '--', color=orb_colors[b])  # Note normalization
			else:  # general complex
				if np.amax(np.abs(np.real(psi / phase) - np.imag(psi / phase)) / np.sqrt(dz)) < 1e-5:  # overlapping re and im curves: dashdot
					thisplot, = plt.plot(z, np.real(psi / phase) / np.sqrt(dz), '-.', color=orb_colors[b])
				else:  # non-overlapping re and im curves: solid and dashed
					thisplot, = plt.plot(z, np.real(psi / phase) / np.sqrt(dz), '-', color=orb_colors[b])  # Note normalization
					plt.plot(z, np.imag(psi / phase) / np.sqrt(dz), '--', color=orb_colors[b])  # Note normalization
			allplots.append(thisplot)
			legendlabels.append(orb_label + (" %i%%" % np.floor(np.real(psi2) * 100 + 0.5)))
			orbsel.append(True)
		else:
			thisplot, = plt.plot(np.nan, np.nan, '-', color='none')
			allplots.append(thisplot)
			legendlabels.append(orb_label + (" %i%%" % 0))
			orbsel.append(False)

	# Estimate well width and subsequently an estimate for the maximum of psi(z)
	l_well = z.max() - z.min() if params.nlayer <= 1 else zint[2] - zint[1] if params.nlayer <= 3 else zint[-2] - zint[1]
	ymax = np.sqrt(2.0 / l_well)
	for zi in zint[1:-1]:
		plt.plot([zi, zi], [-ymax, ymax], 'k:')
	plt.axis((z.min(), z.max(), -1.2 * ymax, 1.8 * ymax))
	plt.xlabel("$z$")
	plt.ylabel("$\\psi_i(z)$")

	# Orbital or subband legend
	allplots_sorted, legendlabels_sorted = reorder_legend(allplots, legendlabels, order=None)
	if norb == 8:
		ax.legend(handles=allplots_sorted, labels=legendlabels_sorted, loc='upper right', ncol=3, fontsize='small', columnspacing=1.0, handlelength=1.6, handletextpad=0.5)
	else:
		ax.legend(handles=allplots_sorted, labels=legendlabels_sorted, loc='upper right', ncol=2)

	# Phases legend
	add_phases_legend(phases, orbsel=np.array(orbsel))

	# Title / parameter text (energy, LL index, k)
	title = "$E=%.3f\\;\\mathrm{meV}$" % energy
	text_y = 0.97
	ax.text(0.02, text_y, title, ha='left', va='top', transform=ax.transAxes)
	text_y -= 0.07
	if params.kdim == 1:
		text_y = display_parameter_text(0, var='y', ax=ax, text_y=text_y)
	elif params.kdim == 2 and ll_full:
		text_y = display_parameter_text(ny_sect - 2, var=r'\mathrm{LL}', ax=ax, text_y=text_y)
		ax.text(0.02, text_y, r'$|\psi_\mathrm{LL}|^2 = %.4f$' % np.real(nrm), ha='left', va='top', transform=ax.transAxes)
		text_y -= 0.07
	else:
		text_y = display_parameter_text(display_k, ax=ax, text_y=text_y)
	ax.text(0.02, text_y, bandlabel, ha='left', va='top', transform=ax.transAxes)

	# Material labels
	add_material_labels(params)

	if filename:
		plt.savefig(filename)
	return fig


@plotswitch
def wavefunction_z(
		params, diagdatapoint, filename = "", eivalrange = None, num = None,
		bandlabels = None, display_k = None, basis = None, basislabels = None,
		phase_rotate = True, ll_full = False, remember = False):
	"""Plot wave functions as function of z.
	Separate by orbital and real/imarginary value.

	Arguments:
	params        PhysParams instance
	diagdatapoint DiagDataPoint instance. For eigenvalues, eigenvectors, and
	              labels.
	filename      String. Where to save the plots. If the file extension is
	              .pdf, a multi-page PDF file is produced. Otherwise, individual
	              files for each eigenstate are saved; in this case, a band
	              label (and if necessary an integer index) will be inserted
	              into filename.
	eivalrange    None or a 2-tuple. If set, do not plot wave functions for the
	              states whose eigenvalues lie outside this range.
	num           IGNORED
	bandlabels    Labels that will be drawn on the plots. If None, determine
	              automatically. If a string, use one label for all states. If a
	              list or array of strings, use different labels for the states.
	              If a tuple of the form (string, list of strings), apply first
	              element as a formatter for the strings in the list.
	display_k     None, dict or a Vector instance. If a Vector, show the value.
	              If a dict, show '$key=value$' joined with commas. If None, do
	              not show.
	basis         Numpy array or matrix, shape (norb, norb), where norb is the
	              number of orbitals. Expand the wave functions in this basis
	              rather than the standard basis of orbitals. The matrix should
	              contain the basis vectors as row vectors.
	basislabels   List of strings. The expressions for the basis states. This
	              may also be used for the standard basis, i.e., if argument
	              basis is None.
	phase_rotate  True, False, or 'k'. If True (default), multiply each
	              eigenvector by a phase factor such that the value psi_i of
	              largest magnitude is purely real with Re psi_i > 0. In case
	              the phases are already set with DiagDataPoint.set_eivec_phase(),
	              it is recommended to use False, so that the phase choice is
	              not overwritten. If the value is 'k', then rotate according to
	              the in-plane angle of the momentum.
	ll_full       True or False. Set to True for full LL mode, else False. The
	              effect is that the 'y' value at which the section is taken
	              (in full LL mode, this is the LL index) is where the integral
	              $\\int |\\psi(z, y)|^2 dz$ is maximal. In other cases, the
	              section is taken at y = 0 (at the center).
	remember      True or False. If False (default), close each figure with
	              plt.close(). If True, do not close the figures, so that they
	              can be modified in the future. The figures are saved
	              regardless.

	Note:
	The arguments labelled as ignored, are included only to make the argument
	lists between wavefunction_z() and abs_wavefunctions_z() identical.

	Returns:
	fig   List of figure numbers when successful. None if an error occurs, if
	      there is no data, or Figure objects have been closed (if argument
	      remember is False).
	"""
	eival = diagdatapoint.eival
	eivecs = diagdatapoint.eivec.T
	if eivecs is None:
		sys.stderr.write("ERROR (ploto.wavefunction_z): Eigenvector data is missing.\n")
		return None
	nz = params.nz
	ny = params.ny
	dz = params.zres
	norb = params.norbitals
	suppress_character_warning = (diagdatapoint.k != 0)

	if params.kdim == 1 or (ll_full and params.kdim == 2):
		dim = params.ny * params.nz * params.norbitals
	elif params.kdim == 2:
		dim = params.nz * params.norbitals
	else:
		raise ValueError("Invalid dimension")
	if eivecs.shape[1] != dim:
		raise ValueError("Eigenvectors have incorrect number of components")

	if isinstance(basislabels, list):
		if len(basislabels) < norb:
			raise ValueError("Argument basislabels must have at least norb (%i) entries." % norb)
	elif basislabels is not None:
		raise TypeError("Argument basislabels must be None or a list of strings.")

	if isinstance(basis, np.ndarray):
		basis_mat = basis.conjugate()
		if min(basis_mat.shape) < norb:
			raise ValueError("Argument basis is a matrix of insufficient size")
		elif max(basis_mat.shape) > norb:
			sys.stderr.write("Warning (ploto.wavefunction_z): Matrix for argument basis is too large. Superfluous entries are discarded.\n")
			basis_mat = basis_mat[:norb, :norb]
		basis_mat = blockdiag(basis_mat, nz).tocsc()  # expand over the z coordinate
	elif basis is None:
		basis_mat = None
	else:
		raise TypeError("Argument basis must be a numpy array or matrix, or None.")

	bandchar_failed = 0
	sorted_idx = np.argsort(eival)
	coeff_at_max = diagdatapoint.get_eivec_coeff(norb, ll_full = ll_full, ny = ny)
	kval = diagdatapoint.k
	if phase_rotate == 'k' and not isinstance(kval, Vector):
		sys.stderr.write("Warning (ploto.wavefunction_z): Rotation by momentum phase was requested, but momentum not given as Vector instance.\n")

	figures = []
	filenames = []
	fname, fext = os.path.splitext(filename)
	multipage = (fext == '.pdf')
	for j in sorted_idx:
		eivec = eivecs[j]
		energy = eival[j]
		if eivalrange is not None and isinstance(eivalrange, list) and len(eivalrange) == 2 and (energy < min(eivalrange) or energy > max(eivalrange)):
			continue

		bandlabel = get_bandlabel(diagdatapoint, bandlabels, j)
		if bandlabels is None and bandlabel == '??' or bandlabel == '':
			bandchar_failed += 1
		filenames.append(f"{fname}.{bandlabel}{fext}")

		fig = _wavefunction_z_single(
			eivec, params=params, filename="", energy=energy, display_k=display_k,
			phase_kval=diagdatapoint.k, ll_full=ll_full, basis_mat=basis_mat,
			bandlabel=bandlabel.replace('-', '\u2212'), phase_rotate=phase_rotate,
			coeff_at_max=coeff_at_max[j]
		)
		figures.append(fig)

	if multipage:
		with PdfPages(filename) as pdf:
			for fig in figures:
				pdf.savefig(fig)
	else:
		filenames = get_unique_filenames(filenames, splitext=True)
		for fig, fname in zip(figures, filenames):
			fig.savefig(fname)

	if not remember:
		for fig in figures:
			plt.close(fig)

	if bandchar_failed > 0 and not suppress_character_warning:
		sys.stderr.write("Warning (ploto.wavefunction_z): Cannot determine band character for %i wave functions.\n" % bandchar_failed)

	return figures if remember else None

@plotswitch
def abs_wavefunctions_z(
		params, diagdatapoint, filename = "",
		eivalrange = None, num = 12, bandlabels = None, display_k = None,
		basis = None, basislabels = None, phase_rotate = True, ll_full = False,
		remember = False):
	"""Plot wave functions (absolute value squared) as function of z.
	Plot multiple states together.

	Arguments:
	params         PhysParams instance
	diagdatapoint  DiagDataPoint instance. For eigenvalues, eigenvectors, and
	               labels.
	filename       Output filename. If None or the empty string, save to a
	               default filename.
	eivalrange     None or a 2-tuple. If set, do not plot wave functions for the
	               states whose eigenvalues lie outside this range.
	num            The number of states to be plotted. These will be the states
	               closest to the centre of eivalrange (or to 0 if eivalrange is
	               None).
	bandlabels     Labels that will be drawn on the plots. If None, determine
	               automatically. If a string, use one label for all states. If
	               a list or array of strings, use different labels for the
	               states. If a tuple of the form (string, list of strings),
	               apply first element as a formatter for the strings in the
	               list.
	basis          IGNORED
	basislabels    IGNORED
	phase_rotate   IGNORED
	display_k      None, dict or a Vector instance. If a Vector, show the value.
	               If a dict, show '$key=value$' joined with commas. If None, do
	               not show.
	ll_full        True or False. Set to True for full LL mode, else False. The
	               effect is that the 'y' value at which the section is taken
	               (in full LL mode, this is the LL index) is where the integral
	               $\\int |\\psi(z, y)|^2 dz$ is maximal. In other cases, the
	               section is taken at y = 0 (at the center).
	remember       True or False. If False (default), close the figure with
	               plt.close(). If True, do not close the figure, so that it can
	               be modified in the future. The figure is saved regardless.

	Note:
	The arguments labelled as ignored, are included only to make the argument
	lists between wavefunction_z() and abs_wavefunctions_z() identical.

	Returns:
	fig   Figure number when successful. None if an error occurs, if there is no
	      data, or Figure object has been closed (if argument remember is
	      False).
	"""
	eival = diagdatapoint.eival
	eivecs = diagdatapoint.eivec.T
	if eivecs is None:
		sys.stderr.write("ERROR (ploto.abs_wavefunctions_z): Eigenvector data is missing.\n")
		return None
	nz = params.nz
	ny = params.ny
	dz = params.zres
	norb = params.norbitals
	suppress_character_warning = (diagdatapoint.k != 0)

	if params.kdim == 1 or (ll_full and params.kdim == 2):
		dim = params.ny * params.nz * params.norbitals
	elif params.kdim == 2:
		dim = params.nz * params.norbitals
	else:
		raise ValueError("Invalid dimension")
	if eivecs.shape[1] != dim:
		raise ValueError("Eigenvectors have incorrect number of components")

	if eivalrange is None:
		e0 = 0.0
		sel = np.argsort(np.abs(eival - e0))  # [:min(neig, num)]
		if num < len(sel):
			sel = sel[:num]   # restrict to maximum number
		order = np.argsort(eival[sel])
		sel = sel[order]
	else:
		e0 = (min(eivalrange) + max(eivalrange)) // 2
		sel = np.argsort(np.abs(eival - e0))  # sort by distance to e0
		sel = sel[(eival[sel] >= min(eivalrange)) & (eival[sel] <= max(eivalrange))]  # restrict to eigenvalue range
		if num < len(sel):
			sel = sel[:num]   # restrict to maximum number
		order = np.argsort(eival[sel])
		sel = sel[order]

	if len(sel) == 0:
		sys.stderr.write("Warning (ploto.abs_wavefunctions_z): No eigenstates to be plotted\n")
		return None

	colors = ['r', 'c', 'b', 'g', 'm', 'y']
	styles = ['-', '--', ':', '-.']
	allplots = []
	legendlabels = []
	jj = 0
	z = params.zvalues_nm()
	zint = params.interface_z_nm()
	ymax = 0.0

	fig = plt.figure(get_fignum(), figsize = get_plot_size('s'))
	plt.subplots_adjust(**get_plot_size('subplot'))
	ax = fig.add_subplot(1, 1, 1)

	psi2_prev = None
	energy_prev = None
	bandlabel_prev = None
	bandchar_failed = 0
	for j in sel:
		eivec = eivecs[j]
		energy = eival[j]
		bandlabel = get_bandlabel(diagdatapoint, bandlabels, j)
		elabel = ('+%03i' % (np.floor(energy + 0.5))) if energy > 0 else ('-%03i' % (-np.floor(energy + 0.5)))

		if params.kdim == 1:  # 1D (proper)
			eivec0 = np.reshape(eivec, (ny, norb * nz))
			ny_sect = ny // 2  # take a section in the middle
			eivec = eivec0[ny_sect, :]
			nrm = np.vdot(eivec, eivec)
			eivec /= np.sqrt(nrm)  # normalize only for proper 1D, but not LL
		elif params.kdim == 2 and ll_full:  # 2D full LL
			eivec0 = np.reshape(eivec, (ny, norb * nz))
			abseivec2 = np.abs(eivec0)**2
			ny_sect = np.argmax(np.sum(abseivec2, axis = 1))
			eivec = eivec0[ny_sect, :]  # normalize only for proper 1D, but not LL
			nrm = np.vdot(eivec, eivec)
		else:
			ny_sect, nrm = None, 1.0

		eivec2 = np.real(eivec.conjugate() * eivec)  # Not a matrix multiplication!
		eivec2a = eivec2.reshape(nz, norb, order = 'C')
		psi2 = np.sum(eivec2a, axis = 1) / dz

		# check if eigenstate is "twin" of previous one
		if psi2_prev is not None and bandlabels is None:
			equal_energy = abs(energy_prev - energy) <= 0.1
			equal_bandlabel = (bandlabel[0] != '?' and bandlabel_prev[0] != '?') and (bandlabel[:-1] == bandlabel_prev[:-1]) and (bandlabel[-1] + bandlabel_prev[-1] in ['+-', '-+'])
			if equal_energy and equal_bandlabel:
				psi2diff = np.abs(psi2_prev - psi2)
				if np.amax(psi2diff) < 1e-4:
					legendlabels[-1] = legendlabels[-1][:-1] + '\u00B1'  # "+-" plus-minus
					continue  # do not add plot

		psi2_prev = psi2
		energy_prev = energy
		bandlabel_prev = bandlabel

		p, = plt.plot(z, psi2, colors[jj % 6] + styles[(jj % 24) // 6])
		allplots.append(p)

		legendlabels.append(elabel + " " + bandlabel)

		ymax = max(ymax, np.amax(psi2))
		jj += 1

	if bandchar_failed > 0 and not suppress_character_warning:
		sys.stderr.write("Warning (ploto.abs_wavefunctions_z): Cannot determine band character for %i wave functions.\n" % bandchar_failed)

	plt.plot([z.min(), z.max()], [0, 0], 'k-')
	for zi in zint[1:-1]:
		plt.plot([zi, zi], [-0.1 * ymax, 1.1 * ymax], 'k:')
	plt.axis((z.min(), z.max(), -0.2 * ymax, 1.3 * ymax))
	set_xlabel('$z$', '$\\mathrm{nm}$')
	plt.ylabel('$|\\psi(z)|^2$')

	# Eigenstate legend
	ax.legend(handles = allplots, labels = legendlabels, loc='upper right', ncol=2)

	# Title / parameter text (energy, LL index, k)
	title = "$%.3f\\;\\mathrm{meV}\\leq E \\leq %.3f\\;\\mathrm{meV}$" % (min(eival[sel]), max(eival[sel]))
	text_y = 0.97
	ax.text(0.02, text_y, title, ha='left', va='top', transform=ax.transAxes)
	text_y -= 0.07
	if params.kdim == 1:
		text_y = display_parameter_text(0, var='y', ax=ax, text_y=text_y)
	elif params.kdim == 2 and ll_full:
		ax.text(0.02, text_y, r"$\mathrm{LL}$ with $\max|\psi_\mathrm{LL}|^2$", ha='left', va='top', transform=ax.transAxes)
	else:
		text_y = display_parameter_text(display_k, ax = ax, text_y = text_y)

	# Material labels
	add_material_labels(params)

	if filename:
		plt.savefig(filename)
	if not remember:
		plt.close()

	return fig if remember else None

@plotswitch
def _abs_wavefunctions_y_single(
		eivec: np.ndarray, params: Optional[PhysParams] = None, filename: str = "",
		energy: Optional[float] = None, display_k: Optional[dict] = None,
		overlap_eivec: Optional[np.ndarray] = None,
		subcolors: Optional[dict] = None, vmax: float = 1.0) -> Figure:
	"""Plot a single wave function as function of y (private)

	Arguments:
	eivec         Array of dim 1. The eigenvector.
	params        PhysParams instance
	filename      String. The filename where to save the plot. If not set,
	              produce the figure but do not write it to a file.
	energy        Float or None. If set, write the energy as parameter text into
	              the plot.
	display_k     None, dict or a Vector instance. If a Vector, show the value.
	              If a dict, show '$key=value$' joined with commas. If None, do
	              not show.
	overlap_eivec  A dict instance. The keys are the subband labels, the values
	               are arrays representing the eigenvector. If given, decompose
	               the state into subbands. If set to None, decompose into the
	               orbitals.
	subcolors     A dict instance. The keys are the subband labels, the values
	              represent colours.
	vmax          Float or None. Maximum value of the wave functions, used to
	              scale the vertical axis.

	Returns:
	fig           Matplotlib Figure instance.
	"""
	fig = plt.figure(get_fignum(), figsize=get_plot_size('s'))
	plt.subplots_adjust(**get_plot_size('subplot'))
	ax = fig.add_subplot(1, 1, 1)

	ny, nz, norb = params.ny, params.nz, params.norbitals
	dy, dz = params.yres, params.zres
	y = params.yvalues_nm()
	vscale = get_config('plot_wf_y_scale', choices=['size', 'width', 'magn', 'separate', 'together'])

	plt.plot([y.min(), y.max()], [0, 0], 'k-')

	allplots = []
	legendlabels = []
	if overlap_eivec is None:  # Orbital overlap
		eivec_arr = np.reshape(eivec, (ny, nz, norb))
		# print()
		for b in range(0, norb):
			psi = eivec_arr[:, :, b]
			# print ('%i:' %(b+1), psi.shape, '->',)
			psi2 = np.sum(np.abs(psi) ** 2, axis=1)
			# print (psi2.shape, 'sum=', psi2.sum())
			if psi2.sum() > 5e-3:
				thisplot, = plt.plot(y, psi2 / dy, '-', color=orb_colors[b])
				allplots.append(thisplot)
				legendlabels.append(orb_labels[b] + (" %i%%" % np.floor(psi2.sum() * 100 + 0.5)))
			else:
				thisplot, = plt.plot(np.nan, np.nan, '-', color='none')
				allplots.append(thisplot)
				legendlabels.append(orb_labels[b] + (" %i%%" % 0))
		# total
		psi2 = np.sum(np.abs(eivec_arr) ** 2, axis=(1, 2))
		thisplot, = plt.plot(y, psi2 / dy, 'k-')
		allplots.append(thisplot)
		legendlabels.append("sum")
		if vscale == 'separate':
			vmax = 1.1 * np.amax(psi2) / dy
	else:  # Subband overlap
		eivec_arr = np.reshape(eivec, (ny, nz * norb))
		absv2 = np.sum(np.abs(eivec_arr) ** 2)
		total_ei = np.sum(np.abs(eivec_arr) ** 2, axis=1) / absv2
		total_ov = np.zeros_like(total_ei)
		for ov in overlap_eivec:  # overlap_eivec should be a dict
			ovec = overlap_eivec[ov]  # this is the data; argument ov is the label
			sublabel = ov[0:2] if len(ov) >= 2 else ''
			col = subcolors.get(sublabel, 'k')
			fmt = '-' if '+' in ov else '--' if '-' in ov else ':'
			absw2 = np.sum(np.abs(ovec) ** 2)
			psi = np.inner(eivec_arr.conjugate(), ovec)
			# print ('%i (%s):' % (jj+1, ov), eivec.shape, ovec.shape, '->', psi.shape, '->')
			psi2 = np.abs(psi) ** 2 / absv2 / absw2
			total_ov += psi2
			# print (psi2.shape)
			if psi2.sum() > 5e-3:
				thisplot, = plt.plot(y, psi2 / dy, fmt, color=col)
				allplots.append(thisplot)
				legendlabels.append(ov + (" %i%%" % np.floor(psi2.sum() * 100 + 0.5)))
			else:
				thisplot, = plt.plot(np.nan, np.nan, fmt, color='none')
				allplots.append(thisplot)
				legendlabels.append(ov + (" %i%%" % 0))
		other_ov = total_ei - total_ov
		if other_ov.sum() > 5e-3:
			thisplot, = plt.plot(y, other_ov / dy, 'k:')
			allplots.append(thisplot)
			legendlabels.append("other" + (" %i%%" % np.floor(other_ov.sum() * 100 + 0.5)))
		else:
			thisplot, = plt.plot(np.nan, np.nan, ':', color='none')
			allplots.append(thisplot)
			legendlabels.append("other" + (" %i%%" % 0))
		thisplot, = plt.plot(y, total_ei / dy, 'k-')
		allplots.append(thisplot)
		legendlabels.append("sum")
		if vscale == 'separate':
			vmax = 1.1 * np.amax(total_ei) / dy

	# Set axis
	plt.axis((y.min(), y.max(), -0.2 * vmax, 1.3 * vmax))

	# Legend
	if overlap_eivec is not None:
		sortedlabelsp = sorted([ll for ll in legendlabels if '+' in ll])
		sortedlabelsm = sorted([ll for ll in legendlabels if '-' in ll])
		otherlabel = [ll for ll in legendlabels if 'other' in ll]
		sumlabel = [ll for ll in legendlabels if 'sum' in ll]
		sortedlabels = sortedlabelsp + otherlabel + sortedlabelsm + sumlabel
		sortedhandles = [allplots[legendlabels.index(ll)] for ll in sortedlabels]
		sortedlabels = [ll.replace('-', '\u2212') for ll in sortedlabels]
		ax.legend(handles=sortedhandles, labels=sortedlabels, loc='upper right', ncol=2, fontsize='small', columnspacing=1.0, handlelength=1.6, labelspacing=None if len(sortedlabels) <= 8 else 0.15, handletextpad=0.5)
	elif norb == 8:
		ax.legend(handles=allplots, labels=legendlabels, loc='upper right', ncol=3, fontsize='small', columnspacing=1.0, handlelength=1.6, handletextpad=0.5)
	else:
		ax.legend(handles=allplots, labels=legendlabels, loc='upper right', ncol=2)

	# Title / parameter text
	title = "$E=%.3f\\;\\mathrm{meV}$" % energy
	ax.text(0.02, 0.97, title, ha='left', va='top', transform=ax.transAxes)
	display_parameter_text(display_k, ax=ax, text_y=0.90)

	# Expectation values
	psi2 = np.sum(np.abs(eivec.reshape(ny, nz * norb)) ** 2, axis=1)
	expval_y = np.sum(y * psi2)
	expval_y2 = np.sum(y**2 * psi2)
	sigma_y = np.sqrt(expval_y2 - expval_y**2)
	yavglabel = "$\\langle y\\rangle = %.1f\\,\\mathrm{nm}$" % expval_y
	yavglabel += ", $\\sigma_y = %.1f\\,\\mathrm{nm}$" % sigma_y
	ax.text(0.02, 0.83, yavglabel, ha='left', va='top', transform=ax.transAxes)


	set_xlabel("$y$", "$\\mathrm{nm}$")
	plt.ylabel("$|\\psi_i|^2(y)$")

	if filename:
		plt.savefig(filename)
	return fig


@plotswitch
def abs_wavefunctions_y(params, diagdatapoint, filename = "", eivalrange = None, bandlabels = None, overlap_eivec = None, obsy = None, display_k = None, magn = None, remember = False):
	"""Plot wave functions (absolute value squared) as function of y.
	Generate a multipage PDF where each figure represents a state. Decompose the
	states into orbitals or subbands.

	Arguments:
	params       PhysParams instance
	diagdatapoint  DiagDataPoint instance. For eigenvalues, eigenvectors, and
	               labels.
	filename     String. Where to save the plots. If the file extension is .pdf,
	             a multi-page PDF file is produced. Otherwise, individual files
	             for each eigenstate are saved; in this case, an energy value
	             (and if necessary an integer index) will be inserted into
	             filename.
	eivalrange   None or a 2-tuple. If set, do not plot wave functions for the
	             states whose eigenvalues lie outside this range.
	bandlabels   Labels that will be drawn on the plots. If None, do not show.
	             If a string, use one label for all states. If a list or array
	             of strings, use different labels for the states. If a tuple of
	             the form (string, list of strings), apply first element as
	             a formatter for the strings in the list.
	overlap_eivec  A dict instance. The keys are the subband labels, the values
	               are arrays representing the eigenvector. If given, decompose
	               the state into subbands. If set to None, decompose into the
	               orbitals.
	obsy         An array of dimension 1 or 2 that contains the observable
	             values <y> (and <y^2>) for the states. If one-dimensional or
	             two-dimensional with one row, the values are interpreted as
	             <y>. If two-dimensional with a second row, the second row are
	             the values of <y^2>. For each state, show the values <y> and
	             sigma_y also if <y^2> is given.
	display_k    None, dict or a Vector instance. If a Vector, show the value.
	             If a dict, show '$key=value$' joined with commas. If None, do
	             not show.
	magn         Numeric value (float or int). If set, use this magnetic field
	             value for scaling the vertical axis, if the scaling type
	             (configuration value 'plot_wf_y_scale') is 'magn'.
	remember     True or False. If False (default), close each figure with
	             plt.close(). If True, do not close the figures, so that they
	             can be modified in the future. The figures are saved
	             regardless.

	Returns:
	fig   List of figure numbers when successful. None if an error occurs, if
	      there is no data, or Figure objects have been closed (if argument
	      remember is False).
	"""
	remember = False  # TODO
	eival = diagdatapoint.eival
	eivecs = diagdatapoint.eivec.T
	if eivecs is None:
		sys.stderr.write("ERROR (ploto.abs_wavefunctions_y): Eigenvector data is missing.\n")
		return None
	nz = params.nz
	ny = params.ny
	dy = params.yres
	norb = params.norbitals

	if params.kdim != 1:
		raise ValueError("Invalid dimension")
	dim = params.ny * params.nz * params.norbitals
	if eivecs.shape[1] != dim:
		raise ValueError("Eigenvectors have incorrect number of components")
	if params.ny <= 1:
		return None

	# Determine colors for subband overlap
	subcolors = subband_overlap_colors(overlap_eivec) if overlap_eivec is not None else {}

	# Vertical scale: vertical range is [-0.2 * vmax, 1.3 * vmax]
	vscale = get_config('plot_wf_y_scale', choices = ['size', 'width', 'magn', 'separate', 'together'])
	if vscale in ['size', 'width']:
		vmax = 2.5 / params.ly_width
	elif vscale == 'magn':
		if not isinstance(magn, (float, np.floating, int, np.integer)):
			sys.stderr.write("Warning (ploto.abs_wavefunctions_y): Scaling by magnetic length requires magnetic field value to be numeric.\n")
			vmax = 2.5 / params.ly_width
		else:
			print('size:', 2.5 / params.ly_width, '| magn:', 1.25 * np.sqrt(eoverhbar * abs(magn) / np.pi))
			vmax = max(2.5 / params.ly_width, 1.25 * np.sqrt(eoverhbar * abs(magn) / np.pi))
	elif vscale == 'separate':
		vmax = 0.0  # To be determined later
	elif vscale == 'together':
		vmax = 0.0
		for eivec in eivecs:
			psi = np.reshape(eivec, (ny, nz * norb))
			psi2max = np.amax(np.sum(np.abs(psi)**2, axis = 1))
			vmax = max(vmax, 1.1 * psi2max / dy)
	else:
		sys.stderr.write("Warning (ploto.abs_wavefunctions_y): Invalid value for configuration option 'plot_wf_y_scale'. Use default 'size'.\n")
		vmax = 2.5 / params.ly_width

	sorted_idx = np.argsort(eival)
	figures = []
	filenames = []
	fname, fext = os.path.splitext(filename)
	multipage = (fext == '.pdf')
	for j in sorted_idx:
		eivec = eivecs[j]
		energy = eival[j]
		if eivalrange is not None and isinstance(eivalrange, list) and len(eivalrange) == 2 and (energy < min(eivalrange) or energy > max(eivalrange)):
			continue

		energy_int = int(round(energy))
		filenames.append(f"{fname}.{energy_int:+d}meV{fext}")

		fig = _abs_wavefunctions_y_single(
			eivec, params=params, filename="", energy=energy, display_k=display_k,
			overlap_eivec=overlap_eivec, subcolors=subcolors, vmax=vmax
		)
		figures.append(fig)

	if multipage:
		with PdfPages(filename) as pdf:
			for fig in figures:
				pdf.savefig(fig)
	else:
		filenames = get_unique_filenames(filenames, splitext=True)
		for fig, fname in zip(figures, filenames):
			fig.savefig(fname)

	if not remember:
		for fig in figures:
			plt.close(fig)

	return figures if remember else None


@plotswitch
def _wavefunction_zy_single(
		eivec: np.ndarray, params: Optional[PhysParams] = None, filename: str = "",
		energy: Optional[float] = None, display_k: Optional[dict] = None,
		separate_bands: bool = False, vmax: Optional[float] = None) -> Figure:
	"""Plot a single wave function as function of (z, y) (private)

	Arguments:
	eivec         Array of dim 1. The eigenvector.
	params        PhysParams instance
	filename      String. The filename where to save the plot. If not set,
	              produce the figure but do not write it to a file.
	energy        Float or None. If set, write the energy as parameter text into
	              the plot.
	display_k     None, dict or a Vector instance. If a Vector, show the value.
	              If a dict, show '$key=value$' joined with commas. If None, do
	              not show.
	separate_bands  If False, use the absolute value square for the colouring.
	                If True, mix colours depending on orbital composition.
	vmax          Float or None. Maximum value that corresponds to the upper
	              limit of the color map.

	Returns:
	fig           Matplotlib Figure instance.
	"""
	ny, nz, norb = params.ny, params.nz, params.norbitals
	z, y = params.zvalues_nm(extend = 1), params.yvalues_nm(extend = 1)
	zint = params.interface_z_nm()
	extent = (y.min(), y.max(), z.min(), z.max())

	if separate_bands:
		color = get_config('plot_wf_zy_bandcolors', choices = ['hsl', 'hsv', 'rgb'])
	else:
		color = get_config('color_wf_zy')

	fig = plt.figure(get_fignum(), figsize=get_plot_size('s'))
	plt.subplots_adjust(**get_plot_size('subplot'))
	ax = fig.add_subplot(1, 1, 1)

	eivec2 = eivec.conjugate() * eivec
	if separate_bands:
		psi2_zy_all = np.transpose(np.real(eivec2.reshape(ny, nz, norb)), (1, 0, 2))
		psi2_zy_g6 = psi2_zy_all[:, :, 0] + psi2_zy_all[:, :, 1]
		psi2_zy_g8h = psi2_zy_all[:, :, 2] + psi2_zy_all[:, :, 5]
		psi2_zy_g8l = psi2_zy_all[:, :, 3] + psi2_zy_all[:, :, 4]
		psi2_zy = np.sum(psi2_zy_all, axis=2)
		psi2_max = psi2_zy.max()
		if vmax is None:
			vmax = psi2_max

		# Extract rgb color from Gamma6, Gamma8L, Gamma8H
		rgb = rgb_color(color, psi2_zy_g6, psi2_zy_g8l, psi2_zy_g8h, psi2_zy, vmax=vmax)
		ax.imshow(np.clip(rgb, 0, 1), interpolation='none', extent=extent, aspect='auto', origin='lower')
	else:
		colormap = try_colormap(color)
		psi2_zy = np.sum(np.real(eivec2.reshape(ny, nz, norb)), axis=2).transpose()
		if vmax is None:
			vmax = psi2_zy.max()
		ax.imshow(np.clip(psi2_zy, 0.0, vmax), cmap=colormap, interpolation='none', extent=extent, aspect='auto', vmin=0.0, vmax=vmax, origin='lower')

	# Plot expectation value of y
	expval_y = np.sum(np.sum(np.real(eivec2.reshape(ny, nz * norb)), axis=1) * params.yvalues_nm())
	plt.plot([expval_y, expval_y], [z.min(), z.max()], 'r:')

	# Material interfaces
	ymax = y.max()
	for zi in zint[1:-1]:
		plt.plot([-ymax, ymax], [zi, zi], 'k:')
	plt.axis((-ymax * 1.05, ymax * 1.05, z.min() * 1.05, z.max() * 1.05))

	# Axes
	set_ylabel('$z$', '$\\mathrm{nm}$')
	set_xlabel('$y$', '$\\mathrm{nm}$')

	# Title / parameter text
	title = "$E=%.3f\\;\\mathrm{meV}$" % energy
	ax.text(0.02, 0.97, title, ha='left', va='top', transform=ax.transAxes)
	display_parameter_text(display_k, ax=ax, text_y=0.90)

	# Material labels
	add_material_labels(params, vertical=True)

	if filename:
		plt.savefig(filename)
	return fig


@plotswitch
def wavefunction_zy(params, diagdatapoint, filename = "", separate_bands = False, eivalrange = None, display_k = None, remember = False):
	"""Plot wave functions as function of (z, y).
	The colouring bmay be a color map for the absolute value squared, or a
	colour mixing determined for displaying the orbital content. (Detailed
	settings via configuration values.)

	Arguments:
	params       PhysParams instance
	diagdatapoint  DiagDataPoint instance. For eigenvalues, eigenvectors, and
	               labels.
	filename     String. Where to save the plots. If the file extension is .pdf,
	             a multipage PDF file is produced. Otherwise, individual files
	             for each eigenstate are saved; in this case, an energy value
	             (and if necessary an integer index) will be inserted into
	             filename.
	separate_bands  If False, use the absolute value square for the colouring.
	                If True, mix colours depending on orbital composition.
	eivalrange   None or a 2-tuple. If set, do not plot wave functions for the
	             states whose eigenvalues lie outside this range.
	display_k    None, dict or a Vector instance. If a Vector, show the value.
	             If a dict, show '$key=value$' joined with commas. If None, do
	             not show.
	remember     True or False. If False (default), close each figure with
	             plt.close(). If True, do not close the figures, so that they
	             can be modified in the future. The figures are saved
	             regardless.

	Returns:
	fig   List of figure numbers when successful. None if an error occurs, if
	      there is no data, or Figure objects have been closed (if argument
	      remember is False).
	"""
	eival = diagdatapoint.eival
	eivecs = diagdatapoint.eivec.T
	if eivecs is None:
		sys.stderr.write("ERROR (ploto.wavefunction_zy): Eigenvector data is missing.\n")
		return None
	nz = params.nz
	ny = params.ny
	norb = params.norbitals

	if params.kdim != 1:
		raise ValueError("Invalid dimension")
	dim = params.ny * params.nz * params.norbitals
	if eivecs.shape[1] != dim:
		raise ValueError("Eigenvectors have incorrect number of components")

	# Get plot mode (file format) from config and check file extension
	mode = get_config('plot_wf_zy_format', choices = ['pdf', 'png', 'pngtopdf', 'png_to_pdf'])
	fname, fext = os.path.splitext(filename)
	if mode in ['png', 'pdf'] and fext != f".{mode}":
		sys.stderr.write(f"Warning (ploto.wavefunction_zy): File extension of the requested filename does not correspond to requested file format. The extension is changed to {mode}.\n")
		fext = f".{mode}"
	elif mode in ['pngtopdf', 'png_to_pdf']:
		fext = ".png"  # Use png for intermediate files
	multipage = (mode == 'pdf')

	# Count labels for determination of file name patterns
	n_elabels = {}
	j_elabels = {}
	for energy in eival:
		elabel = ('+%03i' % (np.floor(energy + 0.5))) if energy > 0 else ('-%03i' % (-np.floor(energy + 0.5)))
		if elabel in n_elabels:
			n_elabels[elabel] += 1
		else:
			n_elabels[elabel] = 1
			j_elabels[elabel] = 0

	# Determine maximum of all eigenvectors
	psi2_max_all = 0
	for eivec in eivecs:
		eivec2 = eivec.conjugate() * eivec
		eivec2o = np.real(eivec2.reshape(ny * nz, norb))
		if separate_bands:
			psi2_max = np.amax(eivec2o)
		else:
			psi2_max = np.amax(np.sum(eivec2o, axis=1))
		psi2_max_all = max(psi2_max_all, psi2_max)
	scaletype = get_config('plot_wf_zy_scale', choices=['separate', 'together'])
	vmax = psi2_max_all if scaletype == 'together' else None

	sorted_idx = np.argsort(eival)
	figures = []
	filenames = []
	for j in sorted_idx:
		eivec = eivecs[j]
		energy = eival[j]
		if eivalrange is not None and isinstance(eivalrange, list) and len(eivalrange) == 2 and (energy < min(eivalrange) or energy > max(eivalrange)):
			continue

		energy_int = int(round(energy))
		filenames.append(f"{fname}.{energy_int:+d}meV{fext}")

		fig = _wavefunction_zy_single(
			eivec, params=params, filename = "", energy=energy,
			display_k=display_k, separate_bands=separate_bands, vmax=vmax
		)
		figures.append(fig)

	if multipage:
		with PdfPages(filename) as pdf:
			for fig in figures:
				pdf.savefig(fig)
	else:
		filenames = get_unique_filenames(filenames, splitext=True)
		for fig, fname in zip(figures, filenames):
			fig.savefig(fname)

	if mode in ['pngtopdf', 'png_to_pdf']:
		delete_pngs = get_config_bool('plot_wf_delete_png')
		convert_pngs_to_pdf(filename, filenames, delete_pngs=delete_pngs)

	if not remember:
		for fig in figures:
			plt.close(fig)

	return figures if remember else None

