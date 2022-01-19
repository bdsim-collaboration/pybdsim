import pybdsim

d = pybdsim.Data.Load("r2-ana.root")

h1 = d.histograms1dpy['Event/PerEntryHistograms/Q2Neutrons']
h2 = d.histograms1dpy['Event/PerEntryHistograms/Q2Gammas']

binWidth = str(round(h1.xwidths[0],1))

h1c, h2c, r = pybdsim.Plot.Histogram1DRatio(h1,h2, yLogScale=True,
                              xlabel="Total Energy (GeV)",
                              ylabel="Fraction / Event / "+binWidth+" GeV",
                              title="Comparison of Fluxes",
                              histogram1Colour='r',
                              histogram2Colour='b',
                              ratioColour='k')



