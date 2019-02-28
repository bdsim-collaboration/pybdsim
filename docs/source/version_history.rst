===============
Version History
===============

v2.0 - 2019 / 02 / 27
=====================

New Features
------------

* Machine diagram plotting automatically from BDSIM output. Compatible with newer
  BDSIM output format.
* Support for thin R matrix, parallel transporter and thick R matrix in builder.
* Generate transfer matrix from tracking data from BDSIM for a single element.
* Control over legend location in stanard energy deposition and loss plots.
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
* Compatability with PIP install system.
* Manual.
* Testing suite.
