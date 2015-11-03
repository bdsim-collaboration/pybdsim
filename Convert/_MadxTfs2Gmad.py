import numpy as _np
import re as _re
import pymadx as _pymadx
from .. import Builder as _Builder
from .. import Beam as _Beam

def MadxTfs2Gmad(input, outputfilename, startname=None, stopname=None, stepsize=1,
                 ignorezerolengthitems=True, thinmultipoles=False, samplers='all',
                 aperturedict={}, collimatordict={}, beampiperadius=0.2,
                 verbose=False, beam=True, flipmagnets=False, usemadxaperture=False):
    """
    MadxTfs2Gmad - convert a madx twiss output file (.tfs) into a gmad input file for bdsim
    
    inputfilename   - path to the input file
    outputfilename  - requested output file
    startname       - the name (exact string match) of the lattice element to start the machine at
                      this can also be an integer index of the element sequence number in madx tfs
    stopname        - the name (exact string match) of the lattice element to stop the machine at
                      this can also be an integer index of the element sequence number in madx tfs
    stepsize        - the slice step size. Default is 1, but -1 also useful for reversed line
    ignorezerolengthitems -
                    - nothing can be zero length in bdsim as real objects of course have some finite 
                      size.  Markers, etc are acceptable but for large lattices this can slow things 
                      down. True allows to ignore these altogether, which doesn't affect the length 
                      of the machine.
    thinmultipoles  - will convert thin multipoles to ~1um thick finite length multipoles with
                      upscaled k values - experimental feature
    samplers        - can specify where to set samplers - options are None, 'all', or list of 
                      names of elements (normal python list of strings). Note default 'all' 
                      will generate separate outputfilename_samplers.gmad with all the samplers
                      which will be included in the main .gmad file - you can comment out the 
                      include to therefore exclude all samplers and retain the samplers file.
    apertureinfo    - aperture information. Can either be a dictionary of dictionaries with the 
                      the first key the exact name of the element and the daughter dictionary 
                      containing the relevant bdsim parameters as keys (must be valid bdsim syntax).
                      Alternatively, this can be a pymadx.Aperture instance that will be queried.
    collimatordict  - a dictionary of dictionaries with collimator information keys should be exact 
                      string match of element name in tfs file value should be dictionary with the 
                      following keys:
                      "bdsim_material"   - the material - exact string as in bdsim manual
                      "angle"            - rotation angle of collimator in radians
                      "xsize"            - x full width in metres
                      "ysize"            - y full width in metres
    beampiperadius  - in metres.  Default beam pipe radius and collimator setting if unspecified
    verbose         - print out lots of information when building the model
    beam            - True | False - generate an input gauss Twiss beam based on the values
                      of the twiss parameters at the beginning of the lattice (startname)
                      NOTE - we thoroughly recommend checking these parameters and this functionality
                      is only for partial convenience to have a model that works straight away.
    flipmagnets     - True | False - flip the sign of all k values for magnets - MADX currently 
                      tracks particles agnostic of the particle charge - BDISM however, follows their 
                      manual definition strictly - positive k -> horizontal focussing for positive 
                      partilces therefore, positive k -> vertical focussing for negative particles.  
                      Use this flag to flip the sign of all magnets.
    usemadxaperture - True | False - use the aperture information in the TFS file if APER_1 and APER_2
                      columns exist.  Will only set if they're non-zero.

    """
    lFake  = 1e-6 # fake length for thin magnets
    izlis  = ignorezerolengthitems
    factor = -1 if flipmagnets else 1  #flipping magnets
    if type(input) == str :
        print 'MadxTfs2Gmad> Loading file using pymadx'
        madx   = _pymadx.Tfs(input)
    else :
        print 'Already a pymadx instance - proceeding'
        madx   = input

    if verbose:
        madx.ReportPopulations()
        
    nitems = madx.nitems
    opencollimatorsetting = beampiperadius
    
    # data structures for checks
    angtot = 0.0
    lentot = 0.0
    lldiff = []
    dldiff = {}
    itemsomitted = []

    kws = {} #extra parameters
    
    #iterate through items in tfs and construct machine
    a = _Builder.Machine()

    requiredKeys = [
        'L', 'ANGLE',
        'KSI', 'K1L', 'K2L', 'K3L', 'K4L', 'K5L',
        'K1SL', 'K2SL', 'K3SL', 'K4SL', 'K5SL', 'K6SL',
        'TILT', 'KEYWORD',
        'ALFX', 'ALFY', 'BETX', 'BETY',
        'VKICK', 'HKICK'
        ]
    for key in requiredKeys:
        if key not in madx.columns:
            print 'Required columns : L, ANGLE, KSI, K1L...K6L, K1SL...K6SL, TILT, KEYWORD, ALFX, ALFY, BETX, BETY, VKICK, HKICK'
            print 'Given columns    : '
            print madx.columns
            raise KeyError("Required key '"+str(key)+"' missing from tfs file")
     
    # iterate through input file and construct machine
    for item in madx[startname:stopname:stepsize]:
        name = item['NAME']
        #remove special characters like $, % etc 'reduced' name - rname
        rname = _re.sub('[^a-zA-Z0-9_]+','',name) #only allow alphanumeric characters and '_'
        t = item['KEYWORD']
        l = item['L']
        ang = item['ANGLE']
        if l <1e-9:
            zerolength = True
        else:
            zerolength = False
        
        if verbose:
            print 'zerolength? ',str(name).ljust(20),str(l).ljust(20),' ->',zerolength

        if zerolength and ignorezerolengthitems:
            itemsomitted.append(name)
            continue #this skips the rest of the loop as we're ignoring this item
        
        lentot += l
        angtot += ang

        #element-wise keywords
        kws = {}

        # APERTURE
        # check if aperture info in tfs file
        # only use this if aperture info not specified in aperture dict
        if ( usemadxaperture and (name not in aperturedict) ):
            if 'APER_1' in madx.columns and 'APER_2' in madx.columns:
                #elliptical aperture
                aperX = madx.GetRowDict(name)['APER_1']
                aperY = madx.GetRowDict(name)['APER_2']
                if (aperX > 1e-6) and (aperY > 1e-6):
                    #both apertures must be specified for elliptical
                    kws['aper1'] = aperX #make sure it's non zero
                    kws['aper2'] = aperY 
                elif (aperX > 1e-6):
                    #resort to circular
                    kws['aper1'] = aperX #make sure it's non zero
                else:
                    pass
            elif 'APER_1' in madx.columns:
                #circular aperture
                aper = madx.GetRowDict(name)['APER_1']
                if aper > 1e-6:
                    kws['aper1'] = aper #make sure it's non zero

        # check if aperture info in aperture dict
        if name in aperturedict:
            #for now only 1 aperture - circular
            ap = (aperturedict[name],'m')
            if ap[0] < 1e-6:
                ap = (defaultbeampiperadius,'m')
            if t != 'RCOLLIMATOR':
                kws['aper'] = ap
        
        if t == 'DRIFT':
            a.AddDrift(rname,l,**kws)
        elif t == 'HKICKER':
            kickangle = item['HKICK'] * factor
            a.AddHKicker(rname,l,angle=kickangle,**kws)
        elif t == 'INSTRUMENT':
            #most 'instruments' are just markers
            if zerolength:
                a.AddMarker(rname)
                if verbose:
                    print name,' -> marker instead of instrument'
            else:
                a.AddDrift(rname,l,**kws)
        elif t == 'MARKER':
            a.AddMarker(rname)
        elif t == 'MONITOR':
            #most monitors are just markers
            if zerolength:
                a.AddMarker(rname)
                if verbose:
                    print name,' -> marker instead of monitor'
            else:
                a.AddDrift(rname,l,**kws)
        elif t == 'MULTIPOLE':
            # TBC - cludge for thin multipoles (uses lFake for a short non-zero length)
            if thinmultipoles:
                print 'WARNING - conversion of thin multipoles is not finished yet!'
                k1  = item['K1L']  / lFake * factor
                k2  = item['K2L']  / lFake * factor
                k3  = item['K3L']  / lFake * factor
                k4  = item['K4L']  / lFake * factor
                k5  = item['K5L']  / lFake * factor
                k6  = item['K6L']  / lFake * factor
                k1s = item['K1SL'] / lFake * factor
                k2s = item['K2SL'] / lFake * factor
                k3s = item['K3SL'] / lFake * factor
                k4s = item['K4SL'] / lFake * factor
                k5s = item['K5SL'] / lFake * factor
                k6s = item['K6SL'] / lFake * factor
                tilt= item['TILT']
                if k1 != 0 : 
                    a.AddQuadrupole(rname,k1=k1,length=lFake,tilt=tilt) 
                else : 
                    a.AddMarker(rname)
#                    a.AddMultipole(name,length=lFake,knl=(k1,k2,k3),ksl=(k1s,k2s,k3s),tilt=tilt)
            if zerolength:
                a.AddMarker(rname)
                if verbose:
                    print name,' -> marker instead of multipole'
            else:
                a.AddDrift(rname,l,**kws)
        elif t == 'OCTUPOLE':
            k3 = item['K3L'] / l * factor
            a.AddOctupole(rname,l,k3=k3,**kws)
        elif t == 'PLACEHOLDER':
            if zerolength:
                a.AddMarker(rname)
                if verbose:
                    print name,' -> marker instead of placeholder'
            else:
                a.AddDrift(rname,l,**kws)
        elif t == 'QUADRUPOLE':
            k1 = item['K1L'] / l * factor
            a.AddQuadrupole(rname,l,k1=k1,**kws)
        elif t == 'RBEND':
            angle = item['ANGLE']
            a.AddDipole(rname,'rbend',l,angle=angle,**kws)
        elif t == 'RCOLLIMATOR':
            #only use xsize as only have half gap
            if name in collimatordict:
                #gets a dictionary then extends kws dict with that dictionary
                kws['material'] = collimatordict[name]['material']
                kws['tilt']     = collimatordict[name]['tilt']
                xsize           = collimatordict['xsize']
                ysize           = collimatordict['ysize']
                a.AddRCol(rname,l,xsize,ysize,**kws)
            else:
                a.AddDrift(rname,l)
        elif t == 'ECOLLIMATOR':
            if name in collimatordict:
                #gets a dictionary then extends kws dict with that dictionary
                kws['material'] = collimatordict[name]['material']
                kws['tilt']     = collimatordict[name]['tilt']
                xsize           = collimatordict['xsize']
                ysize           = collimatordict['ysize']
                a.AddECol(rname,l,xsize,ysize,**kws)
            else:
                a.AddDrift(rname,l)
        elif t == 'RFCAVITY':
            a.AddDrift(rname,l,**kws)
        elif t == 'SBEND':
            angle = item['ANGLE']
            k1 = item['K1L'] / l * factor
            a.AddDipole(rname,'sbend',l,angle=angle, k1=k1, **kws)
        elif t == 'SEXTUPOLE':
            k2 = item['K2L'] / l * factor
            a.AddSextupole(rname,l,k2=k2,**kws)
        elif t == 'SOLENOID':
            #ks = item['KSI'] / l
            #a.AddSolenoid(rname,l,ks=ks
            a.AddDrift(rname,l,**kws)
        elif t == 'TKICKER':
            a.AddDrift(rname,l,**kws)
        elif t == 'VKICKER':
            kickangle = item['VKICK'] * factor
            a.AddVKicker(rname,l,angle=kickangle,**kws)
        else:
            print 'unknown element type:', t, 'for element named: ', name
            if zerolength:
                print 'putting marker in instead as its zero length'
                a.AddMarker(rname)
            else:
                print 'putting drift in instead as it has a finite length'
                a.AddDrift(rname,l)

    #add a single marker at the end of the line
    a.AddMarker('theendoftheline')
    
    a.AddSampler(samplers)

    # Make beam file 
    if beam: 
        b = MadxTfs2GmadBeam(madx, startname, verbose)
        a.AddBeam(b)

    a.Write(outputfilename)

    if verbose:
        print 'lentot ',lentot
        print 'angtot ',angtot
        print 'items omitted: '
        print itemsomitted
        #return lldiff,dldiff,a
    return a

def MadxTfs2GmadBeam(tfs, startname=None, verbose=False):
    print 'Warning - using automatic generation of input beam distribution from madx tfs file - PLEASE CHECK!'
    if startname == None:
        startindex = 0
    elif type(startname) == int:
        startindex = startname
    else:
        startindex = tfs.IndexFromName(startname)

    #MADX defines parameters at the end of elements so need to go 1 element
    #back if we can.

    if startindex > 0:
        startindex -= 1
    
    energy   = float(tfs.header['ENERGY'])
    gamma    = float(tfs.header['GAMMA'])
    particle = tfs.header['PARTICLE']
    ex       = tfs.header['EX']
    ey       = tfs.header['EY']
    sigmae   = float(tfs.header['SIGE'])
    sigmat   = float(tfs.header['SIGT'])

    data     = tfs.GetRowDict(tfs.sequence[startindex])

    if particle == 'ELECTRON' :
        particle = 'e-'
    elif particle == 'POSITRON' : 
        particle = 'e+' 
    elif particle == 'PROTON' : 
        particle = 'proton' 

    #print particle,energy,gamma,ex,ey
    if verbose:
        print data['BETX'],data['ALFX'],data['MUX']
        print data['BETY'],data['ALFY'],data['MUY']
    
    gammax = (1.0+data['ALFX'])/data['BETX']
    gammay = (1.0+data['ALFY'])/data['BETY']

    #note, in the main pybdsim.__init__.py Beam class is imported from Beam.py
    #so in this submodule when we do from .. import Beam it's actually the
    #already imported class that's being imported
    beam   = _Beam.Beam(particle,energy,'gausstwiss')
    beam.SetBetaX(data['BETX'])
    beam.SetBetaY(data['BETY'])
    beam.SetAlphaX(data['ALFX'])
    beam.SetAlphaY(data['ALFY'])
    beam.SetEmittanceX(ex,'m') 
    beam.SetEmittanceY(ey,'m')
    beam.SetSigmaE(sigmae)
    
    return beam
