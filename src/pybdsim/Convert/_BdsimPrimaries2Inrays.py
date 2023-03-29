from scipy import constants as _con
import numpy as _np
import os.path as _path
import time as _time

import pybdsim.Data as _Data

def BdsimPrimaries2Ptc(inputfile, outfile=None, start=0, ninrays=-1):
    """
    Takes .root file generated from a BDSIM run an an input and creates
    a PTC inrays file from the primary particle tree. If no output file
    name is given, it will be <inputfile>.madx (stripping off the .root).
    
    :param inputfile: root format output from BDSIM run
    :type  inputfile: str
    :param outfile: filename for the inrays file
    :type  outfile: str
    :param start: starting primary particle index
    :type  start: int
    :param ninrays: total number of inrays to generate (-1 means all)
    :type  ninrays: int
    """
    if outfile is None:
        outfile = inputfile.rstrip(".root")
        outfile += ".madx"

    BdsimSampler2Ptc(inputfile, outfile, "Primary", start, ninrays)

def BdsimSampler2Ptc(inputfile, outfile, samplername, start=0, ninrays=-1):
    """
    Takes .root file generated from a BDSIM run an an input and creates
    a PTC inrays file from the sampler particle tree. Converts primary particles only.
    
    :param inputfile: root format output from BDSIM run
    :type  inputfile: str
    :param outfile: filename for the inrays file
    :type  outfile: str
    :param samplername: sampler name in BDSIM root file
    :type  samplername: str
    :param start: starting primary particle index
    :type  start: int
    :param ninrays: total number of inrays to generate
    :type  ninrays: int
    """
    if not (outfile[-5:] == ".madx"):
        outfile = outfile + ".madx"

    # specify if primaries as there's a minor difference in conversion. The primary sampler can use the nominal
    # energy from the beam tree, however a specified sampler may be after an energy changing element (e.g
    # degrader or RF cavity), so the energy is taken to be the mean particle energy in that sampler. Note that
    # this is susceptible to incorrect conversion at low statistics.
    if samplername == "Primary":
        sampler_coords = _LoadBdsimCoordsAndConvert(inputfile, samplername, start, ninrays, isPrimaries=True)
    else:
        sampler_coords = _LoadBdsimCoordsAndConvert(inputfile, samplername, start, ninrays, isPrimaries=False)

    outfile = open(outfile, 'w')

    nentries = len(sampler_coords[0])
    headstr = "! PTC format inrays file of " + str(nentries)
    headstr += " initial coordinates generated from primaries in BDSIM sampler " + samplername + " on " + _time.strftime("%c") + "\n"

    outfile.writelines(headstr)
    for n in range(0, nentries):  # n denotes a given particle
        s = 'ptc_start'
        s += ', x=' + repr(sampler_coords[0][n])
        s += ', px=' + repr(sampler_coords[1][n])
        s += ', y=' + repr(sampler_coords[2][n])
        s += ', py=' + repr(sampler_coords[3][n])
        s += ', t=' + repr(sampler_coords[4][n])
        s += ', pt=' + repr(sampler_coords[5][n])
        s += ';\n'
        outfile.writelines(s)

    outfile.close()

def BdsimPrimaries2BdsimUserFile(inputfile, outfile, start=0, ninrays=-1):
    """
    Takes .root file generated from a BDSIM run and creates
    a BDSIM userFile file from the primary particle tree.
    
    :param inputfile: root format output from BDSIM run
    :type  inputfile: str
    :param outfile: filename for the inrays file
    :type  outfile: str
    :param start: starting primary particle index
    :type  start: int
    :param ninrays: total number of inrays to generate
    :type  ninrays: int
    
    Writes the following columns to file:
      x[m] xp[rad] y[m] yp[rad] t[ns] E[GeV]
    E is the total particle energy.
    """
    BdsimSampler2BdsimUserFile(inputfile, outfile, "Primary", start, ninrays)

def BdsimSampler2BdsimUserFile(inputfile, outfile, samplername, start=0, ninrays=-1):
    """
    Takes .root file generated from a BDSIM run and creates
    a BDSIM userFile file from the sampler particle tree.
    
    :param inputfile: root format output from BDSIM run
    :type  inputfile: str
    :param outfile: filename for the inrays file
    :type  outfile: str
    :param samplername: sampler name in BDSIM root file
    :type  samplername: str
    :param start: starting primary particle index
    :type  start: int
    :param ninrays: total number of inrays to generate
    :type  ninrays: int
    
    Writes the following columns to file:
      x[m] xp[rad] y[m] yp[rad] t[ns] E[GeV]
    
    E is the total particle energy. The t column is the time in the given 
    sampler minus the mean time for that sampler. If not mean subtracted, 
    the particles may be significantly offset from the primary position.
    """
    if not (outfile[-4:] == ".dat"):
        outfile = outfile + ".dat"

    if not _path.isfile(inputfile):
        raise IOError("file \"{}\" not found!".format(inputfile))
    else:
        print("Loading input file: ", inputfile)
        data = _Data.Load(inputfile)

    x,xp,y,yp,tof,E,pid = _ExtractSamplerCoords(data, samplername)

    # subtract mean time as non-primary sampler will be at a finite T in the lattice - should be centred around 0.
    if samplername != "Primary":
        meanT = _np.mean(tof)
        tof = tof - meanT
    nentries = len(x)

    x,xp,y,yp,t,E = _TruncateCoordinates(x,xp,y,yp,tof,E,ninrays,start)

    outfile = open(outfile, 'w')
    for n in range(0, nentries):  # n denotes a given particle
        s =  ' ' + repr(x[n])
        s += ' ' + repr(xp[n])
        s += ' ' + repr(y[n])
        s += ' ' + repr(yp[n])
        s += ' ' + repr(tof[n])
        s += ' ' + repr(E[n])
        s += '\n'
        outfile.writelines(s)

    outfile.close()

def BdsimPrimaries2Madx(inputfile,outfile,start=0, ninrays=-1):
    """
    Takes .root file generated from a BDSIM run an an input and creates
    a MADX inrays file from the primary particle tree.

    :param inputfile: root format output from BDSIM run
    :type  inputfile: str
    :param outfile: filename for the inrays file
    :type  outfile: str
    :param start: starting primary particle index
    :type  start: int
    :param ninrays: total number of inrays to generate, default is all available
    :type  ninrays: int
    """
    if not (outfile[-5:] == ".madx"):
        outfile = outfile+".madx"

    primary_coords = _LoadBdsimCoordsAndConvert(inputfile, "Primary", start, ninrays, isPrimaries=True)

    outfile = open(outfile,'w' )

    nentries =  len(primary_coords[0])
    headstr  = "! MadX format inrays file of "+str(nentries)
    headstr += " initial coordinates generated from BDSIM output on "+_time.strftime("%c")+"\n"

    outfile.writelines(headstr)
    for n in range(0,nentries):               # n denotes a given particle
        s  =  'start'
        s += ', x='  + repr(primary_coords[0][n])
        s += ', px=' + repr(primary_coords[1][n])
        s += ', y='  + repr(primary_coords[2][n])
        s += ', py=' + repr(primary_coords[3][n])
        s += ', t='  + repr(primary_coords[4][n])
        s += ', pt=' + repr(primary_coords[5][n])
        s += ';\n'
        outfile.writelines(s)

    outfile.close()

def BdsimPrimaries2Mad8(inputfile,outfile,start=0, ninrays=-1):
    """
    Takes .root file generated from a BDSIM run an an input and creates
    a MAD8 inrays file from the primary particle tree.

    :param inputfile: root format output from BDSIM run
    :type  inputfile: str
    :param outfile: filename for the inrays file
    :type  outfile: str
    :param start: starting primary particle index
    :type  start: int
    :param ninrays: total number of inrays to generate
    :type  ninrays: int
    """
    if not (outfile[-5:] == ".mad8"):
        outfile = outfile+".mad8"

    primary_coords = _LoadBdsimCoordsAndConvert(inputfile, "Primary", start, ninrays, isPrimaries=True)

    outfile = open(outfile,'w' )

    nentries =  len(primary_coords[0])
    headstr  = "! Mad8 format inrays file of "+repr(nentries)
    headstr += " initial coordinates generated from BDSIM output on "+_time.strftime("%c")+"\n"

    outfile.writelines(headstr)
    for n in range(0,nentries):    #n denotes a given particle
        s  =  'START'
        s += ', X='  + repr(primary_coords[0][n])
        s += ', PX=' + repr(primary_coords[1][n])
        s += ', Y='  + repr(primary_coords[2][n])
        s += ', &\n'                             #line continuation needed to obey FORTRAN 80 char input limit
        s += 'PY=' + repr(primary_coords[3][n])
        s += ', T='  + repr(primary_coords[4][n])
        s += ', DELTAP=' + repr(primary_coords[5][n])
        s += '\n'
        outfile.writelines(s)

    outfile.close()

def _LoadBdsimCoordsAndConvert(inputfile, samplername, start, ninrays, isPrimaries):
    """
    Load BDSIM coordinates and convert to PTC format.
    """
    if not _path.isfile(inputfile):
        raise IOError("file \"{}\" not found!".format(inputfile))
    else:
        print("Loading input file: ", inputfile)
        data = _Data.Load(inputfile)

    #Get sampler/primaries data
    x,xp,y,yp,tof,E,pid = _ExtractSamplerCoords(data, samplername)

    #Get particle pdg number
    pid  =  int(_np.mean(pid))  #cast to int to match pdg id

    #Particle mass needed for calculating momentum, in turn needed for dE.
    mass = 0
    if pid == 2212:                                     #proton
        mass = _con.proton_mass * _con.c**2 / _con.e / 1e9
    elif (pid == 11) or (pid == -11):                   #electron / positron
        mass = _con.electron_mass * _con.c**2 / _con.e / 1e9
    elif (pid == 13) or (pid == -13):                   #mu- / mu+
        mass = 0.1056583745
    elif (pid == 1000020040):                           # helium4 nuclei
        mass = 3.756671525    # value calculated by Keenan Ngo 02/2020
    elif (pid == 1000060120):                           # carbon12 nuclei
        mass = 11.27001475    # value calculated by Keenan Ngo 02/2020

    #TODO: Add more particle masses and particle numbers as needed.
    # Note PDGID scheme for ions is 10LZZZAAAI - L is no. strange quarks (0 realistically), Z is no. protons,
    # A is no. neutrons+protons, and I is excited state, 0 being ground.

    if mass == 0:
        raise ValueError('Unknown particle species.')

    if isPrimaries:
        # use design energy for primaries as a significant mean offset can exist with small number of particles
        beam = _Data.BeamData(data)
        Em = beam.beamEnergy
    else:
        # Use the mean energy as there may have been a designed energy change (from RF, degrader, etc)
        Em = _np.mean(E)

    beta = _np.sqrt(1 - (mass/Em)**2)

    p           = _np.sqrt(E**2 - _np.full_like(E, mass)**2)
    p0          = _np.sqrt(Em**2 - mass**2)
    tofm        = _np.mean(tof)

    # BDSIM output momenta are normalised w.r.t the individual particle
    # momentum.  But PTC expects normalised w.r.t the reference momentum.
    xp *= (p / p0)
    yp *= (p / p0)

    #Use deltap and pathlength as needed for the time=false flag in PTC
    #Reference on p.201 of the MADX User's Reference Manual V5.03.07
    dE          = (p-p0)/p0
    t           = beta*(tof-_np.full(len(tof),tofm))*1.e-9*_con.c    #c is sof and the 1.e-9 factor is nm to m conversion

    x,xp,y,yp,t,dE = _TruncateCoordinates(x,xp,y,yp,t,dE,ninrays,start)

    #Agglomerate the coordinate arrays and return resulting superarray
    coords = _np.stack([x,xp,y,yp,t,dE])
    return coords

def _ExtractSamplerCoords(data, samplername):
    """
    Extract sampler coordinates.
    """
    if samplername != "Primary":
        # add . to the sampler name to match branch names from file
        if samplername[-1] != ".":
            samplername += "."
        # check branch exists
        allSamplers = data.GetSamplerNames()
        if not samplername in allSamplers:
            msg = "Sampler " + samplername + " not found in inputfile."
            raise ValueError(msg)

    sampler = _Data.SamplerData(data, samplername)

    # get particle coords and filter out secondaries
    primary = sampler.data['parentID'] == 0
    x   = sampler.data['x'][primary]
    xp  = sampler.data['xp'][primary]
    y   = sampler.data['y'][primary]
    yp  = sampler.data['yp'][primary]
    tof = sampler.data['T'][primary]
    E   = sampler.data['energy'][primary]
    pid = sampler.data['partID'][primary]

    return x,xp,y,yp,tof,E,pid

def _TruncateCoordinates(x,xp,y,yp,t,dE,ninrays,start):
    # Truncate the arrays to the desired length
    if ninrays < 0:
        x = x[start:]
        y = y[start:]
        xp = xp[start:]
        yp = yp[start:]
        t = t[start:]
        dE = dE[start:]

    else:
        if start > 0:
            ninrays += start
        x = x[start:ninrays]
        y = y[start:ninrays]
        xp = xp[start:ninrays]
        yp = yp[start:ninrays]
        t = t[start:ninrays]
        dE = dE[start:ninrays]

    return x,xp,y,yp,t,dE
