Uproot
======

An example Python script how to use uproot to load BDSIM output file.

Load the file with the correct method
-------------------------------------

 ::

    bdsim_output = pybdsim.DataUproot.BDSimOutput("output.root")
    rebdsim_output = pybdsim.DataUproot.ReBDSimOutput("rebdsoutput.root")
    rebdsim_optics_output = pybdsim.DataUproot.ReBDSimOpticsOutput("optics.root")

Model
*****

 ::

    model = bdsim_output.model.df
    model = rebdsim_output.model.df
    model = rebdsim_optics_output.model.df

Samplers data
*************

 ::

    samplers = bdsim_output.event.samplers
    data_d1 = samplers['d1'].df

Primary beam
************

 ::

    primary = bdsim_output.event.primary
    primary.df

Optics
******

 ::

    optics = rebdsim_optics_output.optics
    optics.df

Histograms
**********

 ::

    histos = rebdsim_output.event.MergedHistograms.ElossHisto
    values = histos.values
    centers = histos.centers