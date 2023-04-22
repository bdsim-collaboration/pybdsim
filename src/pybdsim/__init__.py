"""
pybdsim - python tool for BDSIM.

Copyright Royal Holloway, University of London 2023.

+-----------------+----------------------------------------------------------+
| **Module**      | **Description**                                          |
+-----------------+----------------------------------------------------------+
| Builder         | Create generic accelerators for BDSIM.                   |
+-----------------+----------------------------------------------------------+
| Compare         | Comparison of optics between different codes.            |
+-----------------+----------------------------------------------------------+
| Constants       | Constants.                                               |
+-----------------+----------------------------------------------------------+
| Convert         | Convert other formats into gmad.                         |
+-----------------+----------------------------------------------------------+
| Data            | Read the bdsim output formats.                           |
+-----------------+----------------------------------------------------------+
| DataUproot      | Data loading with uproot instead of pyroot. (optional)   |
+-----------------+----------------------------------------------------------+
| Field           | Read and write BDSIM field format files.                 |
+-----------------+----------------------------------------------------------+
| Geant4          | Dictionary that contains process and subprocess IDs      |
+-----------------+----------------------------------------------------------+
| Gmad            | Create bdsim input files - lattices & options.           |
+-----------------+----------------------------------------------------------+
| ModelProcessing | Tools to process existing BDSIM models and generate      |
|                 | other versions of them.                                  |
+-----------------+----------------------------------------------------------+
| Optics          | Optical calculation in development. (optional)           |
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
| Writer          | Write various objects from Builder.                      |
+-----------------+----------------------------------------------------------+

+-------------+--------------------------------------------------------------+
| **Class**   | **Description**                                              |
+-------------+--------------------------------------------------------------+
| Beam        | A beam options dictionary with methods.                      |
+-------------+--------------------------------------------------------------+
| XSecBias    | A cross-section biasing object.                              |
+-------------+--------------------------------------------------------------+

"""

try:
    from ._version import __version__
    from ._version import __version_tuple__
except ImportError:
    __version__ = "unknown version"
    __version_tuple__ = (0, 0, "unknown version")

from . import Beam
from . import Builder
from . import Constants
from . import Convert
from . import Compare
from . import Data
from . import Field
from . import Geant4
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
           'DataUproot',
           'Field',
           'Geant4',
           'Gmad',
           'Options',
           'Plot',
           'Run',
           'ModelProcessing',
           'Visualisation',
           'XSecBias',
           '_General']

try:
    from . import Optics
    __all__.append("Optics")
except:
    pass

try:
    from . import DataUproot
    __all__.append("DataUproot")
except:
    pass