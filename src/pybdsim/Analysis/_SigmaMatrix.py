from numpy import cov as _cov
from numpy import ndarray as _ndarray
from pandas import DataFrame as _DataFrame

def _ReformatInputData(matrixIn) :
    if isinstance(matrixIn, _ndarray):
        na = matrixIn
    elif isinstance(matrixIn, _DataFrame) :
        na = matrixIn.to_numpy().transpose()
    #elif isinstance(matrixIn, dict) :
    #    pass

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

