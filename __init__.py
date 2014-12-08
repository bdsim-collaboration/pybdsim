# pybdsim - python tools for bdsim
# Version 1.0
# L. Nevay, S.T.Boogert
# laurie.nevay@rhul.ac.uk


"""
pybdsim - python tools for bdsim

dependencies:
package     - minimum version required
numpy       - 1.7.1
matplotlib  - 1.3.0

Modules:
Builder - create generic accelerators for bdsim
Convert - convert other formats into gmad
Data    - read the bdsim output formats
Gmad    - create bdsim input files - lattices & options
Options - methods to generate bdsim options
Plot    - some nice plots for data

Classes:
Analysis - encapsulates functions & plots for a single file
Beam     - a beam options dictionary with methods

"""

from Beam import Beam
import Builder
import Constants
import Convert
import Data
import Gmad
import Options
import Plot

#import Root

import _General

#from Analysis import Analysis
#from AnalysisRoot import AnalysisRoot
#from AnalysisRootOptics import AnalysisRootOptics

#__all__ = ['Builder','Data','Gmad','Plot']
__all__ = ['Beam','Builder','Constants','Data','Gmad','Options','Plot']
