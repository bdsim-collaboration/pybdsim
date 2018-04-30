#explicit imports to keep namespace clean
from _MadxBdsimComparison import MadxVsBDSIM
from _MadxBdsimComparison import MadxVsBDSIMOrbit
from _MadxBdsimComparison import MadxVsBDSIMFromGMAD

try:
    from _TransportBdsimComparison import TransportVsBDSIM
except ImportError:
    import warnings
    msg = ("Missing pytransport dependency. "
           " Transport comparison facilities excluded.")
    warnings.warn(msg)
    del warnings
try:
    import pymad8 as _pymad8
    from _Mad8BdsimComparison import Mad8VsBDSIM
except ImportError:
    import warnings
    msg = "Missing pymad8 dependency.  MAD8 comparison facilities excluded."
    warnings.warn(msg)
    del warnings

from _BdsimBdsimComparison import BDSIMVsBDSIM
from _BdsimBdsimComparison import PTCVsBDSIM

try:
    import pysad as _pysad
    from _SadComparison import SadComparison
except ImportError:
    pass


from _MadxMadxComparison import MadxVsMadx
