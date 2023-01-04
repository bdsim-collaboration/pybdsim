=========================
Data loading using uproot
=========================

Utilities to load BDSIM output data using `uproot`. It is intended for small-scale
data extraction - not a general analysis of BDSIM output.


Loading ROOT Data
-----------------

pybdsim can load several different ROOT files produced by BDSIM, rebdsim,
rebdsimCombine, bdskim, rebdsimOptics, rebdsimHistoMerge.
Depending on the type of the file, you can load the file using::

    >>> bdsim_data = pybdsim.DataUproot.BDSimOutput("output.root")
    >>> rebdsim_data = pybdsim.DataUproot.ReBDSimOutput("rebdsim_output.root")
    >>> rebdsim_optics_data = pybdsim.DataUproot.ReBDSimOpticsOutput("rebdsim_optics_output.root")

Model
*****
The model can be accessed from any file using one of these commands::

    >>> model = bdsim_data.model.df
    >>> model = rebdsim_data.model.df
    >>> model = rebdsim_optics_data.model.df
    >>> model = rebdsim_combine_data.model.df

It returns a `pandas.DataFrame` with the information of the model.

.. note::

    The option :code:`dontSplitSBends=1` should be used in :code:`BDSIM` to have
    one entry for the sbend.

Samplers Data
*************

Samplers data can be trivially extracted from a raw BDSIM output file ::

    >>> import pybdsim
    >>> d = pybdsim.DataUproot.BDSimOutput("output.root")
    >>> samplers = d.event.samplers

:code:`samplers` is a dictionary where keys are the name of the samplers and values are an instance of
`pybdsim.DataUproot.BDSimOutput.Event.Sampler`. Data can be easily converted in a `pandas.DataFrame` using::

    >>> samplers['sampler_name'].df

The primary beam can be extracted using the same procedure::

    >>> primary_beam = d.event.primary

Optics Files
************

After loading the file using :code:`pybdsim.DataUproot.ReBDSimOpticsOutput`, the optics of the line can be
accessed using::

    >>> optics = rebdsim_optics_data.optics
    >>> results = optics.df

Histograms
**********

After loading the file using :code:`pybdsim.DataUproot.ReBDSimOutput`, histograms can be
accessed using::

    >>> histos = rebdsim_data.event.MergedHistograms.ElossHisto
    >>> values = histos.values
    >>> centers = histos.centers

4D histograms are stored into a `boost histogram` and can be accessed using::

    >>> histo = rebdsim_data.event.MergedHistograms.4d_hist_name
    >>> bh = histo.bh

You can compute the Ambient dose H10 with a method that takes as input the conversion
factor file for the particle::

    >>>  h10 = histo.compute_h10("neutrons.dat")

