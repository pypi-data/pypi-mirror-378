**kdotpy** is a Python application for simulating electronic band structures of
semiconductor devices with k·p theory on a lattice.


Installation
============

You can install **kdotpy** using PIP, from the Python Package Index (PyPI):
```sh
python3 -m pip install kdotpy
```

Alternatively, you can download the source and install it from your local copy:
```sh
git clone https://git.physik.uni-wuerzburg.de/kdotpy/kdotpy.git
python3 -m pip install ./kdotpy
```

For an editable install for active coding and debugging, add the `-e` option to
`pip install`, like so: `python3 -m pip install -e ./kdotpy`.


Usage
=====

kdotpy is designed as a standalone application with a command line interface.
If you have followed the installation instructions above, you can simply run
`kdotpy` from the command line, followed by the 'sub-programme' label and
further arguments. You can do this from any folder.

The first argument is always the sub-programme. The calculation scripts are
`kdotpy 1d`, `kdotpy 2d`, `kdotpy bulk`, `kdotpy ll`, and `kdotpy bulk-ll`.
There are two re-plot scripts, `kdotpy merge` and `kdotpy compare`. Batch
calculations can be done with `kdotpy batch`. The scripts `kdotpy config`,
`kdotpy help`, and `kdotpy doc` give access to configuration and information.
Finally, `kdotpy test` runs pre-defined tests for checking that kdotpy works
correctly.

You can also use `python3 -m kdotpy` followed by the sub-programme and further
arguments.


Example
-------
```sh
kdotpy 2d 8o noax msubst CdZnTe 4% mlayer HgCdTe 68% HgTe HgCdTe 68% llayer 10 7 10 zres 0.25 k -0.6 0.6 / 60 kphi 45 erange -80 0 split 0.01 obs orbitalrgb legend char out -7nm outdir data-qw localminmax
```

This and more examples can be found in the Tutorials section of the Wiki:
https://git.physik.uni-wuerzburg.de/kdotpy/kdotpy/-/wikis/tutorials/overview



More information
================

**Repository**:
https://git.physik.uni-wuerzburg.de/kdotpy/kdotpy

**Wiki**:
https://git.physik.uni-wuerzburg.de/kdotpy/kdotpy/-/wikis/home

**Website**:
https://kdotpy.physik.uni-wuerzburg.de

**Article**:
https://doi.org/10.21468/SciPostPhysCodeb.47


Authors
=======

The following people are members of the kdotpy collaboration.

Maintainers and developers:
- **Wouter Beugeling**
- **Florian Bayer**
- **Christian Berger**
- **Maximilian Hofer**
- **Julian Kuther**

Other contributors:
- Jan Böttcher
- Leonid Bovkun
- Christopher Fuchs
- Saquib Shamim
- Moritz Siebert
- Li-Xian Wang
- Ewelina M. Hankiewicz
- Tobias Kießling
- Hartmut Buhmann
- Laurens W. Molenkamp

We thank Domenico Di Sante, Giorgio Sangiovanni, Björn Trauzettel, Florian Goth,
and Fakher Assaad for feedback and support at various stages of the project.

We acknowledge financial support from the Deutsche Forschungsgemeinschaft (DFG,
German Research Foundation) in the project SFB 1170 *ToCoTronics* and in the
Würzburg-Dresden Cluster of Excellence on Complexity and Topology in Quantum
Matter *ct.qmat* (EXC 2147), and from the Free State of Bavaria for the
Institute for Topological Insulators.


Crediting us
------------

If you use kdotpy, we encourage you to credit our work as you would do with any
scientific work. Please cite us as follows:

> W. Beugeling, F. Bayer, C. Berger, J. Böttcher, L. Bovkun, C. Fuchs, 
> M. Hofer, S. Shamim, M. Siebert, L.-X. Wang, E. M. Hankiewicz, T. Kießling,
> H. Buhmann, and L. W. Molenkamp,
> "kdotpy: k·p theory on a lattice for simulating semiconductor band structures",
> SciPost Phys. Codebases 47 (2025).

The DOI for this work is `10.21468/SciPostPhysCodeb.47`.

We also encourage you to show the kdotpy logo with graphics you present, for
example in oral presentations and on posters.

For detailed instructions, please refer to the document `CITATION.md` in the
repository.


Contributing
============

We encourage interaction (bug reports, suggestions, etc.) via the issue tracker
of the repository:
https://git.physik.uni-wuerzburg.de/kdotpy/kdotpy/-/issues

We can also be reached by e-mail at `kdotpy@uni-wuerzburg.de`.


Becoming a contributor
----------------------

For bug reports, suggestions, and criticisms just let us know via the issue
tracker or by e-mail.

We're also looking for enthusiastic people who want to join our Developer Team.
If you're interested in joining, please don't hesitate to let us know.

For information on what we expect from contributors, please note the terms
stated in `CONTRIBUTING.md` in the repository.


License
=======

kdotpy is licensed under the GNU General Public License, version 3.

> Copyright (C) 2024, 2025 The kdotpy collaboration
>
> kdotpy is free software: you can redistribute it and/or modify it under the
> terms of the GNU General Public License as published by the Free Software
> Foundation, version 3.
>
> kdotpy is distributed in the hope that it will be useful, but WITHOUT ANY
> WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
> A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
>
> You should have received a copy of the GNU General Public License along with
> kdotpy.  If not, see <https://www.gnu.org/licenses/>.

A copy of the GNU General Public License is included as the file `LICENSE` in
the kdotpy repository. Additional terms under Section 7 of the GNU General
Public License, version 3, are stated in the file `LICENSE.additional`.


Contact
=======

e-mail: kdotpy@uni-wuerzburg.de

website: https://kdotpy.physik.uni-wuerzburg.de

Git repository: https://git.physik.uni-wuerzburg.de/kdotpy/kdotpy

