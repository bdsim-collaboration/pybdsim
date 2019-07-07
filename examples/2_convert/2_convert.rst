Convert
=======

1_madxtfs2gmad.py
-----------------

A sample `.tfs` file is provided that represents the first ~300 m of the
LHC beam 1, 3.5 TeV lattice, containing around 160 mixed elements. This
example loads the compressed (`.tar.gz`) tfs file and converts it to
BDSIM gmad syntax.

How to run::

  ./1_madxtfs2gmad.py
  bdsim --file=lhcb1.gmad

The optics and lattice from madx:

.. figure:: twiss35tevb1_short.pdf
	    :width: 70%

The converted lattice as visualised in BDSIM.
  
.. figure:: 1_madxtfs2gmad.png
	    :width: 70%
  

2_transport2gmad.py
-----------------

A sample transport file is provided that contains the output from the lattice
provided with the TRANSPORT distribution.This example loads the output file
and converts it to BDSIM gmad syntax.

How to run::

  ./2_transport2gmad.py
  cd transport_example/
  bdsim --file=transport_example.gmad

The optics and lattice from Transport:

.. figure:: 2_transport2gmad.pdf
        :width: 70%

The converted lattice as visualised in BDSIM.

.. figure:: 2_transport2gmad.png
        :width: 70%

