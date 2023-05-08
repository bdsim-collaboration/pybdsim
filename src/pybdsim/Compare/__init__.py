#explicit imports to keep namespace clean

from ._MadxBdsimComparison import MadxVsBDSIM
from ._MadxBdsimComparison import MadxVsBDSIMOrbit
from ._MadxBdsimComparison import MadxVsBDSIMOrbitResiduals
from ._MadxBdsimComparison import MadxVsBDSIMFromGMAD
from ._BdsimBdsimComparison import BDSIMVsBDSIM
from ._BdsimBdsimComparison import PTCVsBDSIM
from ._TransportBdsimComparison import TransportVsBDSIM
from ._MadxMadxComparison import MadxVsMadx
from ._MultipleCodeComparison import Optics
from ._MultipleCodeComparison import OpticsResiduals
from ._ElegantBdsimComparison import ElegantVsBDSIM

# optional pymad8
try:
    from ._Mad8BdsimComparison import Mad8VsBDSIM
except ImportError:
    pass

# optional pysad
try:
    import pysad as _pysad
    from ._SadComparison import SadComparison
except ImportError:
    pass


