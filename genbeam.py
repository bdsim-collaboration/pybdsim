import numpy.random as _rdm 

def emit(ex, ey, npart) : 
    ''' Generate npart(icles) on ellipse set by ex and ey
    ex = [alphax,betax,gammax]
    ey = [alphay,betay,gammax]
    ''' 
# ellipse 

    pass

def normal(mean, sigma, npart) :
    ''' Generate npart(icles) with sigma matrix given by sigma
    ''' 
# _rdm.multivariate_normal(mean, cov)

    pass

def halo(mean, sigma, ex,ey, npart) : 
    ''' Generate npart(icles) greater than ellipse set by ex and ey
    ex = [alphax,betax,gammax]
    ey = [alphay,betay,gammax]
    ''' 
# generate with normal and cut out below ex and ey

    pass

