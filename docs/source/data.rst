============
Data Loading
============

Utilies to load BDSIM output data. This is intended for optical function plotting
and small scale data extraction - not general analysis of BDSIM output.


Loading ROOT Data
-----------------

The output optics in the ROOT file from `rebdsim` or `rebdsimOptics` may be loaded
with pybdsim providing the `root_numpy` package is available.::

  >>> d = pybdsim.Data.Load("optics.root")

In the case of a `rebdsim` file, an instance of the pybdsim.Data.RebdsimFile class
is returned (See `RebdsimFile`_). In the case of a raw BDSIM output file, an instance
of the BDSIM DataLoader analysis class is returned (even in Python).

Sampler Data
------------

Sampler data can be trivially extracted from a raw BDSIM output file ::

  >>> import pybdsim
  >>> d = pybdsim.Data.Load("output.root")
  >>> primaries = pybdsim.Data.SamplerData(d)

The optional second argument to `SamplerData` can be either the index of the sampler
as counting from 0 including the primaries, or the name of the sampler. ::

  >>> fq15x = pybdsim.Data.SamplerData(d, fq15x)
  >>> thirdAfterPrimares = pybdsim.Data.SamplerData(d, 3)

A near-duplicate class exists called `PhaseSpaceData` that can extract only the
variables most interesting for tracking ('x','xp','y','yp','z','zp','energy','t'). ::

  >>> psd1 = pybdsim.Data.PhaseSpaceData(d)
  >>> psd2 = pybdsim.Data.PhaseSpaceData(d, fq15x)
  >>> psd3 = pybdsim.Data.PhaseSpaceData(d, 3)


RebdsimFile
-----------

When a `rebdsim` output file is loaded, all histograms will be loaded into a dictionary
with their path inside the root file (ie in various folders) as a key. All histograms
are held in a member dictionary called `histograms`. Copies are also provided in
`histograms1d`, `histograms2d` and `histograms3d`.

.. figure:: figures/rebdsimFileMembers.png
	    :width: 100%
	    :align: center

For convenience we provide wrappers for the raw ROOT histogram classes that provide
easy access to the data in numpy format with simple matplotlib plotting called
`pybdsim.Data.TH1`, `TH2` and `TH3`. Shown below is loading of the example output
file `combined-ana.root` in `bdsim/examples/features/data`.

.. figure:: figures/rebdsimFileHistograms.png
	    :width: 100%
	    :align: center


.. figure:: figures/rebdsimFileHistogramsWrapped.png
	    :width: 100%
	    :align: center

Histogram Plotting
------------------

Loaded histograms that are wrapped in our pybdsim.Data.THX classes can be plotted::

   >>> pybdsim.Plot.Histogram1D(d.histogramspy['Event/PerEntryHistograms/EnergyLossManual'])

Note, the use of `d.histogramspy` for the wrapped set of histograms and not the raw ROOT
histograms.


.. figure:: figures/simpleHistogramPlot.png
	    :width: 100%
	    :align: center
