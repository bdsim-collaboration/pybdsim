=========================
Data Loading Using Uproot
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

.. note::

    To use methods in this module, the user must run :code:`BDSIM` with the option :code:`uprootCompatible=1`.

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

    >>> histo = rebdsim_data.event.MergedHistograms.ElossHisto
    >>> values = histo.values
    >>> centers = histo.centers
    >>> errors = histos.errors()

4D histograms are stored in a `boost histogram` and can be accessed using :code:`histo.bh`. The methods to use to access
the data (values, errors, centers) are the same as above.
You can compute the Ambient dose H10 with a method that takes as input the conversion
factor file for the particle::

    >>>  h10 = histo.compute_h10("conversion_factor.dat")

The `conversion_factor` file is a table that contains the energy and the conversion factor for a given particle. This
method returns a 3D histograms over the form `X, Y, Z, H10`.

..  note::

    There is no filter in this method therefore, the user must specify a filter for a given particle (see BDSIM
    documentation).
