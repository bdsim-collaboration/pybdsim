============
Installation
============


Requirements
------------

 * pybdsim is developed for Python 3. The developers use 3.8, 3.9 and 3.10.

 * matplotlib
 * numpy
 * scipy
 * fortranformat
 * pymadx, pymad8
 * pip to install the package

Optional:
 * ROOT Python interface
 * pytransport

pybdsim should be compatible with Python 2 but this is untested.


Installation
------------

To install pybdsim, simply run ``make install`` from the root pybdsim
directory.::

  cd /my/path/to/repositories/
  git clone http://bitbucket.org/jairhul/pybdsim
  cd pybdsim
  make install

Alternatively, run ``make develop`` from the same directory to ensure
that any local changes are picked up.
