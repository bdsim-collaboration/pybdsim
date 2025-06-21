from numpy import cov as _cov
from numpy import ndarray as _ndarray
from numpy import array as _array
try:
    from pandas import DataFrame as _DataFrame
except:
    _DataFrame = None

def _ReformatInputData(matrixIn) :
    if isinstance(matrixIn, _ndarray):
        na = matrixIn
    elif isinstance(matrixIn, _DataFrame) :
        na = matrixIn.to_numpy().transpose()
    elif isinstance(matrixIn, dict) :
        na = _array([matrixIn[k] for k in ['x','xp','y','yp']])
    return na

def CalculateBeamCentroid(matrixIn) :

    # reformat data
    matrixIn = _ReformatInputData(matrixIn)

    # calculate mean
    return matrixIn.mean(1)

def CalculateSigmaMatrix(matrixIn) :

    # reformat data
    na = _ReformatInputData(matrixIn)

    # compute covariance matrix
    na_cov = _cov(na)

    return na_cov

