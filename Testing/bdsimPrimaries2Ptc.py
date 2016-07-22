import root_numpy as _rnp
import numpy as _np
import robdsim as _rbs
import matplotlib.pyplot as _plt



def BdsimPrimaries2Ptc(inputfile,outfile):
    """"
    Takes .root file generated from a BDSIM run an an input and creates
    a PTC inrays file from the primary particle tree. Outfile should be .madx
    """    

    print "BdsimPrimaries2Ptc processing... ", inputfile
    rootin      = _rbs.RobdsimOutput(inputfile,'none')
    primchain   = rootin.GetSamplerChain('Primaries')
    arrchain    = _rnp.tree2rec(primchain)   #array form of the primary tree chain

    nparticles  = len(arrchain)
    x           = arrchain['x']
    y           = arrchain['y']
    xp          = arrchain['xp']
    yp          = arrchain['yp']
    t           = arrchain['z']
    E           = arrchain['E']
    meanE       = _np.mean(E)
    

    outfile = open(outfile,'w' )
    
    for n in range(0,nparticles):               # n denotes a given particle
        s  =  'ptc_start'
        s += ', x='  + str(x[n])
        s += ', px=' + str(xp[n])
        s += ', y='  + str(y[n])
        s += ', py=' + str(yp[n])
        s += ', t='  + str(t[n])
        s += ', pt=' + str((E[n]-meanE)/meanE)   
        s += ';\n'
        
        outfile.writelines(s)

    outfile.close()
        

        
