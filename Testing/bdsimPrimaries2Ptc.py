import root_numpy as _rnp
import robdsim as _rbs
import matplotlib.pyplot as _plt
import csv



def bdsimPrimaries2Ptc(input,output):
    """"
    Takes .root file generated from a BDSIM run an an input and creates
    a PTC inrays file from the primary particle tree
    """
    
    rootin      = _rbs.robdsimOutput(input)
    primchain   = rootin.GetSamplerChain('primaries')
    arrchain    = _rnp.tree2rec(primchain)   #array form of the primary tree chain

    nparticles  = len(arrchain)
    x           = arrchain['x']
    y           = arrchain['y']
    xp          = arrchain['xp']
    yp          = arrchain['yp']
    t           = arrchain['t']
    

    outfile = open(''+output+'.madx','w' )
    
    for n in range(0,nparticles):                     # n denotes a given particle
        s  =  'ptc_start'
        s += ', x='  + str(x[n])
        s += ', px=' + str(xp[n])
        s += ', y='  + str(y[n])
        s += ', py=' + str(yp[n])
        s += ', t='  + str(t[n])
        s += ', pt=' + str(0)               ##JUST FOR TESTING, FIND OUT WHAT PT IS! 
        s += ';\n'
        outfile.writelines(s)

    outfile.close()
        

        
