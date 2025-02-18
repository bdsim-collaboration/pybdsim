from numpy import cov as _cov
from numpy import ndarray as _ndarray
from pandas import DataFrame as _DataFrame

def CalculateSigmaMatrix(matrixIn) :

    if isinstance(matrixIn, _ndarray):
        na = matrixIn
    elif isinstance(matrixIn, _DataFrame) :
        na = matrixIn.to_numpy().transpose()
    #elif isinstance(matrixIn, dict) :
    #    pass

    # mean subtract data
    # na = na - na.mean(0)

    # compute covariance matrix
    na_cov = _cov(na)

    return na_cov

