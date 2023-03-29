"""
Module for various conversions.

"""

from ._MadxTfs2Gmad import MadxTfs2Gmad
from ._MadxTfs2Gmad import ZeroMissingRequiredColumns as _ZeroMissingRequiredColumns
from ._MadxTfs2GmadStrength import MadxTfs2GmadStrength
from ._MadxTfs2Gmad import MadxTfs2GmadBeam
from ._Mad8Twiss2Gmad import Mad8Twiss2Gmad
from ._Transport2Gmad import Transport2Gmad

# all optional imports are quiet without warning, so we don't see print out all the time for each one

try:
    import pysad
    from ._SadFlat2Gmad import SadFlat2GMad
except ImportError:
    pass

try:
    from ._CPyMad2Gmad import CPyMad2Gmad
except ImportError:
    pass

from ._BdsimPrimaries2Inrays import BdsimPrimaries2Ptc
from ._BdsimPrimaries2Inrays import BdsimPrimaries2Madx
from ._BdsimPrimaries2Inrays import BdsimPrimaries2Mad8
from ._BdsimPrimaries2Inrays import BdsimSampler2Ptc
from ._BdsimPrimaries2Inrays import BdsimPrimaries2BdsimUserFile
from ._BdsimPrimaries2Inrays import BdsimSampler2BdsimUserFile

from ._BdsimElement2TransferMatrix import BdsimElement2TransferMatrix

from ._ElegantParamToStrength import ElegantParam2GmadStrength
