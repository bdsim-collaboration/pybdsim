from ._GmadTemplate import ScanParameter1D as _ScanParameter1D
from ._GmadTemplate import ScanParameter2D as _ScanParameter2D
from ._Calculate import CalculateRMatrix as _CalculateRMatrix
from ._Calculate import CalculateTaylorMapOrder2 as _CalculateTaylorMapOrder2
import numpy as _np

'''
    Code temporarily here (for testing) until move to testing repo 
'''

def linear(filename) :
    return _CalculateRMatrix(filename, "d1", "t1")

def taylor(filename):
    return _CalculateTaylorMapOrder2(filename, "d1", "t1")

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

