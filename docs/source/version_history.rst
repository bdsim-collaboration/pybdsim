===============
Version History
===============

v 1.5 - 2018 / ?? / ??
======================

New Features
------------

* Function now public to create beam from Madx TFS file.
* Improved searching for BDSAsciiData class.
* Ability to easily write out beam class.
* Plot phase space from any sampler in a BDSIM output file.

Bug Fixes
---------

* Beam class now supports all BDSIM beam definitions.
* Support all aperture shapes in Builder.


v 1.4 - 2018 / 10 / 04
======================

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

v 1.3 - 2017 / 12 / 05
======================

New Features
------------

* GPL3 licence introduced.
* Compatability with PIP install system.
* Manual.
* Testing suite.
