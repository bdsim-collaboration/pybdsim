============
Installation
============

pybdsim is developed for Python 3. The developers use 3.8 to 3.11. It can
be install through pip (with internet access): ::

  pip install pybdsim

There are the following features that result in more dependencies being installed:

* `uproot` - includes uproot data loading
* `boost_histogram` - includes boost-histogram package for 4d histograms
* `cpymad` - allows usage of cpymad for converting models
* `pysad` - allows usage of pysad for converting models

These can be installed as: ::

  pip install pybdsim[uproot]

or: ::

  pip install pybdsim[uproot,boost_histogram,cpymad,pysad]


Requirements
------------

ROOT and its python interface are required to load BDSIM output and also histogram files
from rebdsim (the analysis tool). This cannot be found through pip but must be separately
installed.

.. note:: When installing ROOT, make sure that ROOT is installed with the same python
          interpreter you intend to use the package through. Most systems have more than
          one Python.
  
Generally, the requirements for pybdsim are

* matplotlib >= 3.0
* numpy >= 1.14
* scipy
* fortranformat
* pymadx
* pymad8
* pytransport

These are all available through pip and will be automatically installed.

Optional:
 * ROOT Python interface


Local Installation
------------------

Although on pip, for development purposes you may wish to use pybdsim from a
copy of the source code. It is possible to clone the git repository and use
pip to `point` at the local set of files, or generally install that set of
files as a once off.

We have provided a simple Makefile in the main pybdsim directory that has
a small set of 'rules' that should help with the relevant pip commands. pip
is used even though pybdsim is found from the local set of files.

To install pybdsim, simply run ``make install`` from the root pybdsim
directory.::

  cd /my/path/to/repositories/
  git clone http://bitbucket.org/jairhul/pybdsim
  cd pybdsim
  make install

Alternatively, run ``make develop`` from the same directory to ensure
that any local changes are picked up.
