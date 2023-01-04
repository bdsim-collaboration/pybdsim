===============
Utility Classes
===============

Various classes are provided for the construction of BDSIM input definitions. There are
classes defined in :code:`pybdsim.Builder` that allow writing of an object without any
checks. Also, there are some specialised classes listed here that exist in :code:`pybdsim`
that include some checking and utility functions.

Once a class is constructed, converting to a string in Python will produce a string
in BDSIM input syntax that can be written to a file.

General Classes
---------------

* :code:`pybdsim.Builder.Aperture`
* :code:`pybdsim.Builder.Atom`
* :code:`pybdsim.Builder.BLM`
* :code:`pybdsim.Builder.CavityModel`
* :code:`pybdsim.Builder.Crystal`
* :code:`pybdsim.Builder.Field`
* :code:`pybdsim.Builder.Material`
* :code:`pybdsim.Builder.Query`
* :code:`pybdsim.Builder.Region`
* :code:`pybdsim.Builder.SamplerPlacement`
* :code:`pybdsim.Builder.Scorer`
* :code:`pybdsim.Builder.ScorerMesh`
* :code:`pybdsim.Builder.Tunnel`
* :code:`pybdsim.Builder.XSecBias`

These all work in the same way. The are constructed with the first argument being
a name, then paramter value pairs as keyword arguments ("kwargs"). e.g. ::

  >>> a = pybdsim.Builder.Aperture('aperDef1', aper1=3, aper2=(2.5,'cm'))
  >>> str(a)
      'aperDef1: aperture, aper1=3, aper2=2.5*cm;\n'


Acceptable types are int, float, str, list, tuple(number, str). In the case
of a tuple (e.g. :code:`()`), it should contain 2 items and the second is the
units string.

An example with a list: ::

  >>> sp = pybdsim.Builder.SamplerPlacement('z350mL',
                                            z=(350,'m'),
                                            shape="rectangular",
                                            aper1=(5,'m'),
                                            aper2=(5,'m'),
                                            partID=[13,-13])
  >>> str(sp)
      'z350mL: samplerplacement, shape="rectangular", partID={13,-13}, aper1=5.0*m, z=350.0*m, aper2=5.0*m;\n'


.. note:: The keyword arguments are not checked. One could write "bananas=5" and it
	  would be used, but ultimately would have no meaning to BDSIM.


Specialised Classes
-------------------


Beam.Beam
*********

This beam class represents a beam definition in gmad syntax. The class has 'setter'
functions that are added dynamically based on the distribution type selected.::

  >>> b = pybdsim.Beam.Beam()
  >>> b.SetParicleType("proton")
  >>> b.SetDistributionType("reference")


Options.Options
***************

This class provides the set of options for BDSIM. Please see
:ref:`pybdsim-options-module` for more details.

XSecBias.XSecBias
*****************

This class provides the definition process biasing in BDSIM. Please see
:ref:`pybdsim-xsecbias-module` for more details.
