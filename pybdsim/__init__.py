"""
pybdsim - python tool for BDSIM.

Copyright Royal Holloway, University of London 2020.

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

__version__ = "2.2.0"

from . import Beam
from . import Builder
from . import Constants
from . import Convert
from . import Compare
from . import Data
from . import Field
from . import Gmad
from . import Options
from . import Plot
from . import Run
from . import ModelProcessing
from . import Visualisation
from . import XSecBias
from . import _General

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
           'Run',
           'ModelProcessing',
           'Visualisation',
           'XSecBias',
           '_General']
