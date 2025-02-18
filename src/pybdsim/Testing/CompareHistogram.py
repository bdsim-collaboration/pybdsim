from numpy import sqrt as _sqrt
from numpy import isnan as _isnan
from numpy import bitwise_not as _bitwise_not

def compare_hist1d_hist1d(h1, h2) :
    d = h1.contents-h2.contents
    d_in_sigma = d/_sqrt(h1.errors**2 + h2.errors**2)

    chi2 = d_in_sigma[_bitwise_not(_isnan(d_in_sigma))].sum()
    return chi2

def compare_hist1d_array(h1, data) :
    # normalise h1 into pdf like distribution
    h1.contents = h1.contents/h1.contents.sum()

def compare_hist2d_hist2d(h1, h2) :
    d = h1.contents-h2.contents
    d_in_sigma = d/_sqrt(h1.errors**2 + h2.errors**2)

    chi2 = d_in_sigma[_bitwise_not(_isnan(d_in_sigma))].sum()
    return chi2