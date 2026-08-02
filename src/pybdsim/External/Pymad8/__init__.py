"""
pymad8 - python tools for working with MAD8 output and input.

Authors:

 * Stewart Boogert
 * Laurie Nevay
 * Andrey Abramov
 * William Shields
 * Jochem Snuverink
 * Stuart Walker
 * Marin Deniaud

Dependencies: (*package* - *minimum version required*)

 * numpy         - 1.7.1
 * matplotlib    - 1.3.0
 * pylab         - 1.3.0 (dependancy of matplotlib)
 * pandas        - 1.4.3
 * fortranformat - 1.2.0

Modules: (*script name* - *usage*)

 * Input         - Tidy Mad8 input
 * Output        - Load Mad8 files into dataframes
 * Plot          - Draw machine lattice and quick optics plots
 * Sim           - Perform simulations on a machine, like particle tracking
 * Track         - Old particle tracking code
 * Visualisation - Old survey plotting code

Copyright Royal Holloway, University of London 2019.
"""
try:
    from ._version import version as __version__
    from ._version import version_tuple
except ImportError:
    __version__ = "unknown version"
    version_tuple = (0, 0, "unknown version")

from . import Input
from .Output import *
from . import Plot
from . import Sim
# import Track  #not imported by default - can be explicitly imported
from . import Visualisation

__all__ = ['Input',
           'Output',
           'Plot',
           'Sim',
           'Visualisation'
]
