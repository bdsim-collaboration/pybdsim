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
Data    - read the bdsim output formats
Gmad    - create bdsim input files - lattices & options
Plot    - some nice plots for data

Classes:
Analysis - encapsulates functions & plots for a single file 

"""

import Builder
import Constants
import Data
#import Gmad
import Plot

import _General

from Analysis import Analysis

#__all__ = ['Builder','Data','Gmad','Plot']
__all__ = ['Builder','Data','Plot']
