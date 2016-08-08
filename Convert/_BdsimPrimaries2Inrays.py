import ROOT as _rt
import numpy as _np
import matplotlib.pyplot as _plt
from scipy.constants import c
import sys
import time
try:
    import root_numpy as _rnp
except ImportError:
    print "No root_numpy found.  mad8 conversion tools may not work as intended."


def bdsimPrimaries2Ptc(inputfile,outfile,start=0, ninrays=-1):
    """"
    Takes .root file generated from a BDSIM run an an input and creates
    a PTC inrays file from the primary particle tree.
    inputfile - <str> root format output from BDSIM run
    outfile   - <str> filename for the inrays file
    start     - <int>  starting primary particle index
    ninrays   - <int> total number of inrays to generate
    """
    if not (outfile[:-5] == ".madx"):
        outfile = outfile+".madx"
    
    primary_coords = _LoadBdsimPrimaries(inputfile, start, ninrays)
    
    outfile  = open(outfile,'w' )

    nentries =  len(primary_coords[0])
    headstr  = "! PTC format inrays file of "+str(nentries)
    headstr += " initial coordinates generated from BDSIM primaries on "+time.strftime("%c")+"\n"

    outfile.writelines(headstr)
    for n in range(0,nentries):                  # n denotes a given particle
        s    =  'ptc_start'
        s   += ', x='  + str(primary_coords[0][n][0])
        s   += ', px=' + str(primary_coords[1][n][0])
        s   += ', y='  + str(primary_coords[2][n][0])
        s   += ', py=' + str(primary_coords[3][n][0])
        s   += ', t='  + str(primary_coords[4][n][0])
        s   += ', pt=' + str(primary_coords[5][n][0])   
        s   += ';\n'
        outfile.writelines(s)

    outfile.close()

def bdsimPrimaries2Madx(inputfile,outfile,start=0, ninrays=-1):
    """"
    Takes .root file generated from a BDSIM run an an input and creates
    a MADX inrays file from the primary particle tree.
    inputfile - <str> root format output from BDSIM run
    outfile   - <str> filename for the inrays file
    start     - <int>  starting primary particle index
    ninrays   - <int> total number of inrays to generate, default is all available
    """
    if not (outfile[:-5] == ".madx"):
        outfile = outfile+".madx"
    
    primary_coords = _LoadBdsimPrimaries(inputfile, start, ninrays)
    
    outfile = open(outfile,'w' )

    nentries =  len(primary_coords[0])
    headstr  = "! MadX format inrays file of "+str(nentries)
    headstr += " initial coordinates generated from BDSIM output on "+time.strftime("%c")+"\n"

    outfile.writelines(headstr)
    for n in range(0,nentries):               # n denotes a given particle
        s  =  'start'
        s += ', x='  + str(primary_coords[0][n][0])
        s += ', px=' + str(primary_coords[1][n][0])
        s += ', y='  + str(primary_coords[2][n][0])
        s += ', py=' + str(primary_coords[3][n][0])
        s += ', t='  + str(primary_coords[4][n][0])
        s += ', pt=' + str(primary_coords[5][n][0])   
        s += ';\n'
        outfile.writelines(s)
        
    outfile.close()

def bdsimPrimaries2Mad8(inputfile,outfile,start=0, ninrays=-1):
    """"
    Takes .root file generated from a BDSIM run an an input and creates
    a MAD8 inrays file from the primary particle tree.
    inputfile - <str> root format output from BDSIM run
    outfile   - <str> filename for the inrays file
    start     - <int>  starting primary particle index
    ninrays   - <int> total number of inrays to generate
    """
    if not (outfile[:-5] == ".mad8"):
        outfile = outfile+".mad8"
    
    primary_coords = _LoadBdsimPrimaries(inputfile, start, ninrays)
   
    outfile = open(outfile,'w' )

    nentries =  len(primary_coords[0])
    headstr  = "! Mad8 format inrays file of "+str(nentries)
    headstr += " initial coordinates generated from BDSIM output on "+time.strftime("%c")+"\n"

    outfile.writelines(headstr)
    for n in range(0,nentries):    #n denotes a given particle
        s  =  'START'
        s += ', X='  + str(primary_coords[0][n][0])
        s += ', PX=' + str(primary_coords[1][n][0])
        s += ', Y='  + str(primary_coords[2][n][0])
        s += ', &\n'                             #line continuation needed to obey FORTRAN 80 char input limit
        s += 'PY=' + str(primary_coords[3][n][0])
        s += ', T='  + str(primary_coords[4][n][0])
        s += ', DELTAP=' + str(primary_coords[5][n][0])   
        s += ';\n'
        outfile.writelines(s)
        
    outfile.close()


def _LoadBdsimPrimaries(inputfile, start, ninrays):

    print "Loading input file: ", inputfile
    rootin      = _rt.TFile(inputfile)
    if (rootin.IsZombie()):
        print "No such file. Terminating..."
        sys.exit(1)
        
    tree        = rootin.Get("Event")

    #Load the primary particle coordinates
    x           =  _rnp.tree2array(tree, branches="Primary.x")
    xp          =  _rnp.tree2array(tree, branches="Primary.xp")
    y           =  _rnp.tree2array(tree, branches="Primary.y")
    yp          =  _rnp.tree2array(tree, branches="Primary.yp")
    tof         =  _rnp.tree2array(tree, branches="Primary.t")
    E           =  _rnp.tree2array(tree, branches="Primary.energy")

    npart       = len(x)
    Em          = _np.mean(E)
    tofm        = _np.mean(tof)
    
    dE          = (E -_np.full(npart,Em))/E
    t           = (tof-_np.full(npart,tofm))*1.e-9*c    #c is sof and the 1.e-9 factor is nm to m conversion

    #Truncate the arrays to the desired lenght
    if (ninrays<0):            
        x  = x[start:]
        y  = y[start:]
        xp = xp[start:]
        yp = yp[start:]
        t  = t[start:]
        dE = dE[start:]
        
    else:
        x  = x[start:ninrays]
        y  = y[start:ninrays]
        xp = xp[start:ninrays]
        yp = yp[start:ninrays]
        t  = t[start:ninrays]
        dE = dE[start:ninrays]
        

    #Agglomerate the coordinate arrays and return reuslting superarray
    primary_coords = _np.stack((x,xp,y,yp,t,dE))

    return primary_coords
