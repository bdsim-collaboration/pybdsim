from ._GmadTemplate import ScanParameter1D as _ScanParameter1D
from ._GmadTemplate import ScanParameter2D as _ScanParameter2D
from ._Calculate import CalculateRMatrix as _CalculateRMatrix
from ._Calculate import CalculateTaylorMapOrder2 as _CalculateTaylorMapOrder2
from ._Calculate import CalculateEnergyGain as _CalculateEnergyGain
import numpy as _np

'''
    Code temporarily here (for testing) until move to testing repo 
'''

def linear(filename) :
    return _CalculateRMatrix(filename, "d1", "t1",size=4)

def taylor(filename):
    return _CalculateTaylorMapOrder2(filename, "d1", "t1")

def gain(filename):
    return _CalculateEnergyGain(filename, "d1", "t1")

def cavity(filename) :
    return [_CalculateRMatrix(filename, "d1", "t1",size=4),_CalculateEnergyGain(filename, "d1", "t1")]

def T01_drift() :
    return _ScanParameter1D("./01_drift.tem",
                          "DRIFT_LENGTH",
                          _np.linspace(1, 2, 2),
                          {"BEAM_ENERGY": "5"},
                          taylor)

def T02_rbend() :
    return _ScanParameter1D("./02_rbend.tem",
                            "RBEND_LENGTH",
                            _np.linspace(1, 2, 2),
                            {"BEAM_ENERGY": "5",
                             "RBEND_ANGLE": "0.05"},
                            taylor)

def T02_rbend_2D() :
    return _ScanParameter2D("./02_rbend.tem",
                            "RBEND_LENGTH",
                            "RBEND_ANGLE",
                            _np.linspace(1, 2, 2),
                            _np.linspace(0.1, 0.2, 2),
                            {"BEAM_ENERGY": "5"},
                            linear)

def T03_sbend() :
    return _ScanParameter1D("./03_sbend.tem",
                            "SBEND_LENGTH",
                            _np.linspace(1, 2, 2),
                            {"BEAM_ENERGY": "5",
                             "SBEND_ANGLE": "0.05"},
                            taylor)

def T06_sextupole() :
    return _ScanParameter1D("./05_sextupole.tem",
                            "SEXTUPOLE_STRENGTH",
                            _np.linspace(1, 2, 2),
                            {"BEAM_ENERGY": "5",
                             "SEXTUPOLE_LENGTH":"1.0"}, taylor)


def T13_rf() :
    return _ScanParameter1D("./13_rf.tem",
                            "RF_GRADIENT",
                            _np.linspace(100,101,1),
#                            "BEAM_X0",
#                            _np.linspace(-1e-3, 1e-3, 11),
                            {"BEAM_ENERGY": "10",
                             "BEAM_DISTRTYPE":'\"gausstwiss\"',
#                             "BEAM_DISTRTYPE":'\"reference\"',
                             "BEAM_X0":"0",
                             "BEAM_Y0":"0",
                             "BEAM_XP0":"0",
                             "BEAM_YP0":"0",
                             "RF_GRADIENT":"100",
                             "RF_LENGTH":"0.2",
                             "RF_FREQUENCY":"747.5",
#                             "RF_FIELD_TYPE":'\"rfconstantinz\"',
                             "RF_FIELD_TYPE":'\"rfpillbox\"'},
                             analysis_function=cavity,
                             keep_files=True,
                             ngenerate=10000)

def T13_rf_rfconstantinz() :
    return _ScanParameter1D("./13_rf.tem",
                            "RF_GRADIENT",
                            _np.linspace(10,101,3),
                            {"BEAM_ENERGY": "10",
                             "BEAM_DISTRTYPE":'\"gausstwiss\"',
                             "BEAM_X0":"0",
                             "BEAM_Y0":"0",
                             "BEAM_XP0":"0",
                             "BEAM_YP0":"0",
                             "RF_GRADIENT":"100",
                             "RF_LENGTH":"0.2",
                             "RF_FREQUENCY":"747.5",
                             "RF_FIELD_TYPE":'\"rfconstantinz\"'},
                             analysis_function=cavity,
                             keep_files=False,
                             ngenerate=10000)

def T13_rf_perle() :
    return _ScanParameter1D("./13_rf.tem",
                            "RF_GRADIENT",
                            _np.linspace(100, 101, 1),
                            {"BEAM_ENERGY": "7",
                             "RF_LENGTH":"0.93",
#                             "RF_GRADIENT":"45",
                             "RF_FREQUENCY":"801.58",
#                             "RF_FIELD_TYPE":'\"rfconstantinz\"'},
                             "RF_FIELD_TYPE":'\"rfpillbox\"'},
                             cavity,
                            keep_files=True)