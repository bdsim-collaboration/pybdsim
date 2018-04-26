from scipy import constants as _con
import warnings

try:
    import ROOT as _rt
except ImportError:
    warnings.warn("ROOT not available - some functionality missing", UserWarning)
    
import numpy as _np
import matplotlib.pyplot as _plt

import sys
import time

try:
    import root_numpy as _rnp
except ImportError:
    warnings.warn("No root_numpy found - some functionality missing", UserWarning)

def BdsimPrimaries2Ptc(inputfile,outfile,start=0, ninrays=-1):
    """"
    Takes .root file generated from a BDSIM run an an input and creates
    a PTC inrays file from the primary particle tree.
    inputfile - <str> root format output from BDSIM run
    outfile   - <str> filename for the inrays file
    start     - <int>  starting primary particle index
    ninrays   - <int> total number of inrays to generate
    """
    if not (outfile[-5:] == ".madx"):
        outfile = outfile+".madx"
    
    primary_coords = _LoadBdsimPrimaries(inputfile, start, ninrays)
    
    outfile  = open(outfile,'w' )

    nentries =  len(primary_coords[0])
    headstr  = "! PTC format inrays file of "+str(nentries)
    headstr += " initial coordinates generated from BDSIM primaries on "+time.strftime("%c")+"\n"

    outfile.writelines(headstr)
    for n in range(0,nentries):                  # n denotes a given particle
        s    =  'ptc_start'
        s   += ', x='  + repr(primary_coords[0][n][0])
        s   += ', px=' + repr(primary_coords[1][n][0])
        s   += ', y='  + repr(primary_coords[2][n][0])
        s   += ', py=' + repr(primary_coords[3][n][0])
        s   += ', t='  + repr(primary_coords[4][n][0])
        s   += ', pt=' + repr(primary_coords[5][n])   
        s   += ';\n'
        outfile.writelines(s)

    outfile.close()

def BdsimPrimaries2Madx(inputfile,outfile,start=0, ninrays=-1):
    """"
    Takes .root file generated from a BDSIM run an an input and creates
    a MADX inrays file from the primary particle tree.
    inputfile - <str> root format output from BDSIM run
    outfile   - <str> filename for the inrays file
    start     - <int>  starting primary particle index
    ninrays   - <int> total number of inrays to generate, default is all available
    """
    if not (outfile[-5:] == ".madx"):
        outfile = outfile+".madx"
    
    primary_coords = _LoadBdsimPrimaries(inputfile, start, ninrays)
    
    outfile = open(outfile,'w' )

    nentries =  len(primary_coords[0])
    headstr  = "! MadX format inrays file of "+str(nentries)
    headstr += " initial coordinates generated from BDSIM output on "+time.strftime("%c")+"\n"

    outfile.writelines(headstr)
    for n in range(0,nentries):               # n denotes a given particle
        s  =  'start'
        s += ', x='  + repr(primary_coords[0][n][0])
        s += ', px=' + repr(primary_coords[1][n][0])
        s += ', y='  + repr(primary_coords[2][n][0])
        s += ', py=' + repr(primary_coords[3][n][0])
        s += ', t='  + repr(primary_coords[4][n][0])
        s += ', pt=' + repr(primary_coords[5][n][0])   
        s += ';\n'
        outfile.writelines(s)
        
    outfile.close()

def BdsimPrimaries2Mad8(inputfile,outfile,start=0, ninrays=-1):
    """"
    Takes .root file generated from a BDSIM run an an input and creates
    a MAD8 inrays file from the primary particle tree.
    inputfile - <str> root format output from BDSIM run
    outfile   - <str> filename for the inrays file
    start     - <int>  starting primary particle index
    ninrays   - <int> total number of inrays to generate
    """
    if not (outfile[-5:] == ".mad8"):
        outfile = outfile+".mad8"
    
    primary_coords = _LoadBdsimPrimaries(inputfile, start, ninrays)
   
    outfile = open(outfile,'w' )

    nentries =  len(primary_coords[0])
    headstr  = "! Mad8 format inrays file of "+repr(nentries)
    headstr += " initial coordinates generated from BDSIM output on "+time.strftime("%c")+"\n"

    outfile.writelines(headstr)
    for n in range(0,nentries):    #n denotes a given particle
        s  =  'START'
        s += ', X='  + repr(primary_coords[0][n][0])
        s += ', PX=' + repr(primary_coords[1][n][0])
        s += ', Y='  + repr(primary_coords[2][n][0])
        s += ', &\n'                             #line continuation needed to obey FORTRAN 80 char input limit
        s += 'PY=' + repr(primary_coords[3][n][0])
        s += ', T='  + repr(primary_coords[4][n][0])
        s += ', DELTAP=' + repr(primary_coords[5][n][0])   
        s += '\n'
        outfile.writelines(s)
        
    outfile.close()


def _LoadBdsimPrimaries(inputfile, start, ninrays):
    c = 299792458.0     #speed of light in vacuum        
    
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
    tof         =  _rnp.tree2array(tree, branches="Primary.T")
    E           =  _rnp.tree2array(tree, branches="Primary.energy")

    #Get particle pdg number
    priPid      =  _rnp.tree2array(tree, branches="Primary.partID")
    pid         =  _np.int(_np.mean(priPid)[0])  #cast to int to match pdg id

    #Particle mass needed for calculating momentum, in turn needed for dE.
    mass = 0
    if pid == 2212:                                     #proton
        mass = _con.proton_mass * c**2 / _con.e / 1e9
    elif (pid == 11) or (pid == -11):                   #electron / positron
        mass = _con.electron_mass * c**2 / _con.e / 1e9
    elif (pid == 13) or (pid == -13):                   #mu- / mu+
        mass = 0.1056583745

    #TODO: Add more particle masses and particle numbers as needed.

    if mass == 0:
        raise ValueError('Unknown primary particle species.')

    npart       = len(x)
    E = _np.array([val[0] for val in E])

    beam = rootin.Get("Beam")
    Em = _rnp.tree2array(beam, branches="Beam.GMAD::BeamBase.beamEnergy")[0]

    beta = _np.sqrt(1 - (mass/Em)**2)

    p           = _np.sqrt(E**2 - _np.full_like(E, mass)**2)
    p0          = _np.sqrt(Em**2 - mass**2)
    tofm        = _np.mean(tof)

    #Use deltap and pathlength as needed for the time=false flag in PTC
    #Reference on p.201 of the MADX User's Reference Manual V5.03.07
    dE          = (p-p0)/p0
    t           = beta*(tof-_np.full(npart,tofm))*1.e-9*c    #c is sof and the 1.e-9 factor is nm to m conversion

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
