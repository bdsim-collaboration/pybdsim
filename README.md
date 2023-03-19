# pybdsim #

A python package containing both utilities for preparing and analysing BDSIM input and output as well as controlling BDSIM.

## Authors ##

L. Nevay
A. Abramov
S. Alden
S. Boogert
C. Hernalsteens
W. Parker
E. Ramoisiaux
W. Shields
J. Snuverink
R. Tesse
S. Walker


## Setup ##

pip install pybdsim

Or from source, from the main directory:

$ make install

or for development where the local copy of the repository is used and can
be reloaded with local changes:

$ make develop

Look in the Makefile for the various pip commands (e.g. for with a venv)


```
python
>>> import pybdsim
>>> d = pybdsim.Data.Load("output.root")
>>> eventTree = a.GetEventTree()
>>> for event in eventTree:
        print(event.Summary.nTracks)
>>> dh = pybdsim.Data.Load("analysis_histograms.root")
>>> pybdsim.Plot.Histogram1D(dh.histogramspy["Event/MergedHistograms/PlossHisto"])
```
