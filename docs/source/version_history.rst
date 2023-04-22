===============
Version History
===============

V3.1.1 - 2023 / 04 / 23
=======================

* Fixed spectra loading and plotting for when the 'p' and 's' prefixes are used
  in the rebdsim Spectra command to denote primary and secondary particles.
* Fixed error with default log scale in `Plot.Histogram2D` when no `vmin` was specified.
* Fix :code:`pybdsim._version_tuple` which should be :code:`pybdsim.__version_tuple__`.
* Fix import without awkward array which is only required for the [uproot] feature of pybdsim.
* :code:`pybdsim.Plot.Spectra()` now makes more than one plot if more than 8 particles are specified.
* Recognised PDG ID 0 as "total" from BDSIM.


V3.1.0 - 2023 / 04 / 02
=======================

* Add the writing and reading of comment lines in field maps.
* Reduce print out when loading a field map.
* Clean imports in cpymad interface as well as in Convert functions.


V3.0.1 - 2023 / 03 / 22
=======================

* Fix import for pybdsim when ROOT is present but librebdsim etc. are not available
  through environmental variables, or findable. Would cause induce a classic ROOT
  segfault when importing pybdsim.
* Fix wrong exception being raised.
* Always write a comment string at the start of a BDSIM field map file to specify
  the units of the file.

V3.0.0 - 2023 / 03 / 19
=======================

* Restructure package into a declarative Python package where all source files are now in
  `src/pybdsim/`.
* The package now has a feature called `uproot` for the optional dependencies of uproot, pandas,
  and pint packages.
* Field classes no longer have :code:`flip=True` as the default - it is now :code:`False`.
  Please check any field maps created by scripts using these classes.

New Features
------------

* Add a module to load BDSIM output file, included rebdsim files with uproot.
* Create a nice Python copy of the header information from any (re)bdsim file when
  loading with pybdsim using only Python types.
* New integration for 2D histograms along each axis to 1D histograms.
* New slices for 3D histograms as well as integrating along a dimension ('projection').
  See :ref:`data-3d-histograms`.
* New ratio plot for 2x 1D histograms. See `pybdsim.Plot.Histogram1DRatio`.
* New loading and handling of 4D histograms (from BDSIM with Boost). They can now be
  loaded and handled similarly to 1,2,3D histograms. They are loaded automatically when
  loading a rebdsim file.
* pybdsim.Data.TH1,2,3 now have :code:`xrange`, :code:`yrange`, and :code:`zrange` members
  where appropriate with a convenient tuple of the range in each dimension. They also
  have the member :code:`integral` and :code:`integralError` taken from their ROOT objects.
* Field plotting functions now tolerate Field class objects as well as filenames to make
  it easier to check field objects as you're making them.
* New field plotting for 2D field maps showing each component.
* New field reflection utility function `pybdsim.Field.MirrorDipoleQuadrant1` for 2D fields.
* New field plotting function `pybdsim.Field.Plot2DXYConnectionOrder` to see the order
  an array is written in. This can be used to validate any field manipulations.
* New field plotting function `pybdsim.Field.Plot1DFxFyFz` to see field components in 1D.
* Field loading automatically works for dimensions such as X, Z for 2D instead of X, Y now.
* Ability to load a rebdsim output file and only load the ROOT histograms without loading
  the BDSIM and rebdsim shared libraries, so it can be used on a separate computer with just
  ROOT.
* Added classes to Builder for all GMAD objects. New ones include `aperture`, `atom`, `blm`,
  `cavitymodel`, `crystal`, `field`, `material`, `newcolour`, `query`, `region`, `samplerplacement`,
  `scorer`, `tunnel`, `xsecbias`.

Bug Fixes
---------

* pybdsim would throw an exception that librebdsim and libbdsimRootEvent could not be
  loaded and stop if the libraries had been already loaded separately outside pybdsim.
  This has been fixed by fixing the interpretation of the error codes from ROOT.
* Fix warning about "nonposy" in matplotlib version for log scales.
* Fix check in Run of if it's a ROOT file or not. Simplify it to use file extension.
* Tolerate no pytransport installation.
* Fix loading of aperture data from a BDSIM output file.
* Fix loading of model data.
* Fix aperture plots from a BDSIM output file.

General
-------

* The Beam class now takes `distrType` and not `distrtype` so as to match BDSIM syntax
  and be less confusing.
* Updated out of date documentation.
* Better automatic ranges for Histogram1DMultiple plots by default.
* Better field loading in `pybdsim.Field.Load`. Returns the same Field object
  from pybdsim as you would write.

v2.4.0 - 2021 / 06 / 16
=======================

New Features
------------

* Transform3D function in a Machine.
* Crystal, ScorerMesh and Placement also can be added to a Machine.
* Ability to insert and replace an element in a machine.

Bug Fixes
---------

* Python 3.8+ warnings fixed.
* Add ROOT_INCLUDE_PATH to ROOT as newer versions don't do this automatically.
* Fixed vmin for 2D histogram plot.

v2.3.0 - 2020 / 12 / 15
=======================

New Features
------------

* Convenience functions for pickling and un-pickling data in the Data module with optional compression.
* Generic loss map plot.


v2.2.0 - 2020 / 06 / 08
=======================

New Features
------------

* Support for Python3.

v2.1 - 2019 / 04 / 20
=====================

New Featuers
------------

* Optional flag of whether to write out the converted model with `pybdsim.Convert.MadxTfs2Gmad`.
* Machine builder now supports new bdsim jcol element.
* Machine diagram drawing can now start from any arbitrary S location.
* For loaded histograms (using `pybdsim.Data.TH1`, `TH2`, `TH3` classes, there are now
  functions `ErrorsToSTD()` and `ErrorsToErrorOnMean()` to easily convert between the
  different types of error - the default is error on the mean.
* New plotting function `pybdsim.Plot.Histogram2DErrors` to visualise 2D histogram errors.

General
-------

* Return arguments of `pybdsim.Convert.MadxTfs2Gmad` is now just 2 items - machine and omitted items. Previously 3.

Bug Fixes
---------

* Fix loading of Model tree from ROOT output given some recent collimation variables may have
  a different structure or type from the existing ones.
* In `pybdsim.Plot.Histogram2D`, the y log scale argument was "ylocscale" and is fixed to "yLogScale".

v2.0 - 2019 / 02 / 27
=====================

New Features
------------

* Machine diagram plotting automatically from BDSIM output. Compatible with newer
  BDSIM output format.
* Support for thin R matrix, parallel transporter and thick R matrix in builder.
* Generate transfer matrix from tracking data from BDSIM for a single element.
* Control over legend location in standard energy deposition and loss plots.
* Utility function to write sampler data from BDSIM output to a user input file.
* Support for energy variation in the beam line in MAD8 conversion.

General
-------

* Remove dependency of root_numpy. pybdsim now uses only standard ROOT interfaces.
* Update physics lists.

Bug Fixes
---------

* Fix bug where calling pybdsim.Plot.PrimaryPhaseSpace with an output file name
  would result in an error as this argument was wrongly supplied to the number
  of bins argument.
* Fix for hidden scientific notation when using machine diagram.
* Fix TH1 TH2 TH3 histogram x,y,z highedge variables in histogram loading. These
  were the lowedge duplicated, which was wrong.
* Add missing variables from sampler data given changes in BDSIM.


v1.9 - 2018 / 08 / 24
=====================

General
-------

* Significant new tests.
* Trajectory loading from BDSIM ROOT output.
* Plot trajectories.
* New padding function for 1D histogram to ensure lines in plots.
* New value replacement function for histograms to ensure continuous line in log plots.
* Control over aspect ration in default 2D histogram plots.
* New classes for each element in the Builder.
* Refactor of MadxTfs2Gmad to use new classes in Builder.

Bug Fixes
---------

* Fix orientation of 2D histograms in plotting.
* Fix header information labels when writing field maps with reversed order.

v1.8 - 2018 / 06 / 23
=====================

General
-------

* Setup requires pytest-runner.
* Introduction of testing.
* Removed line wrapping written to GMAD files in Builder.
* "PlotBdsimOptics" is now "BDSIMOptics" in the Plot module.
* New comparison plots for arbitrary inputs from different tracking codes.
* Prepare PTC coordinates from any BDSIM sampler.

Bug Fixes
---------

* Fixes for "Optics" vs "optics" naming change in ROOT files.


v1.7 - 2018 / 06 / 30
=====================

General
-------

* Can specify which dimension in Field class construction (i.e. 'x':'z' instead of default 'x':'y').

Bug Fixes
---------

* 'nx' and 'ny' were written the wrong way around from a 2D field map in pybdsim.


v1.6 - 2018 / 05 / 23
=====================

Bug Fixes
---------

* Fix machine diagram plotting from BDSIM survey.
* Fix machine diagram searching with right-click in plots.

v1.5 - 2018 / 05 / 17
=====================

New Features
------------

* Function now public to create beam from Madx TFS file.
* Improved searching for BDSAsciiData class.
* Ability to easily write out beam class.
* Plot phase space from any sampler in a BDSIM output file.
* __version__ information in package.
* Get a column from data irrespective of case.
* Coded energy deposition plot. Use for example for labelling cyrogenic, warm and collimator losses.
* Improved Transport BDSIM comparison.
* Function to convert a line from a TFS file into a beam definition file.

Bug Fixes
---------

* Fix library loading given changes to capitalisation in BDSIM.
* Beam class now supports all BDSIM beam definitions.
* Support all aperture shapes in Builder.
* Fixes for loading optics given changes to capitalisation and BDSAsciiData class usage.
* Fixes for collimator conversion from MADX.


v1.4 - 2018 / 10 / 04
=====================

New Features
------------

* Full support for loading BDSIM output formats through ROOT.
* Extraction of data from ROOT histograms to numpy arrays.
* Simple histogram plotting from ROOT files.
* Loading of sampler data and simple extraction of phase space data.
* Line wrapping for elements with very long definitions.
* Comparison plots standardised.
* New BDSIM BDSIM comparison.
* New BDSIM Mad8 comparison.
* Support for changes to BDSIM data format variable renaming in V1.0

Bug Fixes
---------

* Correct conversion of all dispersion component for Beam.
* Don't write all multipole components if not needed.
* Fixed histogram plotting.
* Fixed conversion of coordinates in BDSIM2PtcInrays for subrelativistic particles.
* Fixed behaviour of fringe field `fint` and `fintx` behaviour from MADX.
* Fixed pole face angles given MADX writes out wrong angles.
* Fixed conversion of multipoles and other components for 'linear' flag in MadxTfs2Gmad.
* Fixed axis labels in field map plotting utilities.
* MADX BDSIM testing suite now works with subrelativistic particles.
* Many small fixes to conversion.

v1.3 - 2017 / 12 / 05
=====================

New Features
------------

* GPL3 licence introduced.
* Compatibility with PIP install system.
* Manual.
* Testing suite.
