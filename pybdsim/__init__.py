"""
pybdsim - python tool for BDSIM.

Copyright Royal Holloway, University of London 2018.

+-----------------+--------------------------------+
| **Dependency**  | **Minimum Version Required**   |
+-----------------+--------------------------------+
| numpy           | 1.7.1                          |
+-----------------+--------------------------------+
| matplotlib      | 1.3.0                          |
+-----------------+--------------------------------+
| pymadx          | latest                         |
+-----------------+--------------------------------+

+-----------------+----------------------------------------------------------+
| **Module**      | **Description**                                          |
+-----------------+----------------------------------------------------------+
| Builder         | Create generic accelerators for bdsim.                   |
+-----------------+----------------------------------------------------------+
| Convert         | Convert other formats into gmad.                         |
+-----------------+----------------------------------------------------------+
| Data            | Read the bdsim output formats.                           |
+-----------------+----------------------------------------------------------+
| Fields          | Write BDSIM field format.                                |
+-----------------+----------------------------------------------------------+
| Gmad            | Create bdsim input files - lattices & options.           |
+-----------------+----------------------------------------------------------+
| ModelProcessing | Tools to process existing BDSIM models and generate      |
|                 | other versions of them.                                  |
+-----------------+----------------------------------------------------------+
| Options         | Methods to generate bdsim options.                       |
+-----------------+----------------------------------------------------------+
| Plot            | Some nice plots for data.                                |
+-----------------+----------------------------------------------------------+
| Run             | Run BDSIM programatically.                               |
+-----------------+----------------------------------------------------------+
| Visualisation   | Help locate objects in the BDSIM visualisation, requires |
|                 | a BDSIM survey file.                                     |
+-----------------+----------------------------------------------------------+

+-------------+--------------------------------------------------------------+
| **Class**   | **Description**                                              |
+-------------+--------------------------------------------------------------+
| Beam        | A beam options dictionary with methods.                      |
+-------------+--------------------------------------------------------------+
| ExecOptions | All the executable options for BDSIM for a particular run,   |
|             | included in the Run module.                                  |
+-------------+--------------------------------------------------------------+
| Study       | A holder for the output of runs. Included in the Run Module. |
+-------------+--------------------------------------------------------------+
| XSecBias    | A cross-section biasing object.                              |
+-------------+--------------------------------------------------------------+

"""

__version__ = "1.6"

import Beam
import Builder
import Constants
import Convert
import Compare
import Field
import Data
import Gmad
import Options
import Plot
import Run
import ModelProcessing
import Visualisation
import XSecBias
#import Rebdsim
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
           'Field',
           'Gmad',
           'Options',
           'Plot',
           'ModelProcessing',
           'Visualisation',
           'XSecBias']
