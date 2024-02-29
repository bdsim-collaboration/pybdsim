"""
Utilities to convert and prepare field maps.

Most of the plots assume magnetic fields for the labels, but they
work equally well for electric fields.

"""

from ._Field import Field1D
from ._Field import Field2D
from ._Field import Field3D
from ._Field import Field4D
from ._Field import Load
from ._Field import MirrorDipoleQuadrant1
from ._Field import SortUnorderedFieldMap2D

from .FieldPlotter import Plot1DFxFyFz
from .FieldPlotter import Plot2D
from .FieldPlotter import Plot2DXY
from .FieldPlotter import Plot2DXYMagnitude
from .FieldPlotter import Plot2DXYStream
from .FieldPlotter import Plot2DXZStream
from .FieldPlotter import Plot2DXYConnectionOrder
from .FieldPlotter import Plot2DXYBx
from .FieldPlotter import Plot2DXYBy
from .FieldPlotter import Plot2DXYBz
from .FieldPlotter import Plot2DXYFxFyFz
from .FieldPlotter import Plot3DXY
from .FieldPlotter import Plot3DXZ

try:
    from .FieldPlotterVtk import Plot3DXYZVtk
except ImportError:
    hasVtk = False
