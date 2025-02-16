import pytest as _pytest
import numpy as _np

def round_matrix(m, decimals=1) :
    return m.round(decimals)

def max_matrix_diff(m1,m2) :
    m1 = _np.array(m1)
    m2 = _np.array(m2)

    diff = m1-m2

    return diff.max()

def compare_matrix(m1, m2, abs=1e-3) :
    m1 = _np.array(m1)
    m2 = _np.array(m2)

    diff = m1-m2

    retVal = True
    for e in diff.ravel() :
        retVal = retVal and (e == _pytest.approx(0,abs=1e-3))

    return retVal
