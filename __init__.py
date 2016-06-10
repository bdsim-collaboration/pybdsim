# pybdsim - python tools for bdsim
# Version 1.0
# L. Nevay, S.T.Boogert


"""
pybdsim - python tools for bdsim

| Dependencies:
| package     - minimum version required
| numpy       - 1.7.1
| matplotlib  - 1.3.0

| Modules:
| Builder - create generic accelerators for bdsim
| Convert - convert other formats into gmad
| Data    - read the bdsim output formats
| Gmad    - create bdsim input files - lattices & options
| ModelProcessing - tools to process existing BDSIM models and generate other versions of them.
| Options - methods to generate bdsim options
| Plot    - some nice plots for data
| Root    - functions to convert ROOT histograms into matplotlib (not explicitly imported)
| Run     - run BDSIM programatically
| Visualisation - help locate objects in the BDSIM visualisation, requires a BDSIM survey file

| Classes:
| Analysis - encapsulates functions & plots for a single file
| Beam     - a beam options dictionary with methods
| ExecOptions - all the executable options for BDSIM for a particular run
| Study       - a holder for the output of runs
| XSecBias - a cross-section biasing object

"""

import Beam
import Builder
import Constants
import Convert
import Compare
import Data
import Gmad
import Options
import Plot
import Run
import ModelProcessing
import Visualisation
import XSecBias
#import Testing

#import Root - not imported since dependency on pyROOT

import _General

#from Analysis import Analysis
#from AnalysisRoot import AnalysisRoot
#from AnalysisRootOptics import AnalysisRootOptics

__all__ = ['Beam',
           'Builder',
           'Constants',
           'Convert',
           'Compare',
           'Data',
           'Gmad',
           'Options',
           'Plot',
           'ModelProcessing',
           'Visualisation',
           'XSecBias']
