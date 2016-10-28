"""
Module for various conversions.

"""

import numpy as _np
import pymadx as _pymadx
from .. import Builder as _Builder

from _MadxTfs2Gmad import MadxTfs2Gmad
from _MadxTfs2GmadStrength import MadxTfs2GmadStrength
#from _Mad8Twiss2Gmad import *
#from _Mad8Saveline2Gmad import *

from _Mad8Saveline2Gmad import Mad8Saveline2Gmad

from _Mad8Twiss2Gmad import Mad8Twiss2Gmad
from _Mad8Twiss2Gmad import Mad8MakeOptions
from _Mad8Twiss2Gmad import Mad8MakeApertureTemplate
from _Mad8Twiss2Gmad import Mad8MakeCollimatorTemplate

from _BdsimPrimaries2Inrays import BdsimPrimaries2Ptc
from _BdsimPrimaries2Inrays import BdsimPrimaries2Madx
from _BdsimPrimaries2Inrays import BdsimPrimaries2Mad8
