import root_numpy as _rnp
import robdsim as _rbs
import matplotlib.pyplot as _plt



def bdsimPrimaries2Ptc(filename):
    """"
    Takes .root file generated from a BDSIM run an an input and creates
    a PTC inrays file from the primary particle tree
    """
    
    rootin      = _rbs.robdsimOutput(filename)
    primchain   = rootin.GetSamplerChain('primaries')
    arrchain    = _rnp.tree2rec(primchain)

    x           = arrchain['x']
    y           = arrchain['y']
    xp          = arrchain['xp']
    yp          = arrchain['yp']
    
    ##testing file loading with a plot

    _plt.plot(x,y)
