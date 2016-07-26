import ROOT as _rt
import root_numpy as _rnp
import numpy as _np
import matplotlib.pyplot as _plt



def BdsimPrimaries2Ptc(inputfile,outfile):
    """"
    Takes .root file generated from a BDSIM run an an input and creates
    a PTC inrays file from the primary particle tree. Outfile should be .madx
    """    

    print "BdsimPrimaries2Ptc processing... ", inputfile
    rootin      = _rt.TFile(inputfile)
    t           = rootin.Get("Event")
    
    x           =  _rnp.tree2rec(t, branches="Primary.x")
    y           =  _rnp.tree2rec(t, branches="Primary.y")
    xp          =  _rnp.tree2rec(t, branches="Primary.xp")
    yp          =  _rnp.tree2rec(t, branches="Primary.yp")
    t           =  _rnp.tree2rec(t, branches="Primary.z")
   # E           =  _rnp.tree2rec(t, branches="Primary.energy")
    E           = _np.full((len(x)), 250.0)

    nparticles  = len(x)
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
        

        
