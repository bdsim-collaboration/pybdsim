import numpy as _np
import pymadx as _pymadx
from .. import Builder as _Builder
from .. import Beam as _Beam

def MadxTfs2Gmad(input,outputfilename,startname=None,stopname=None,ignorezerolengthitems=True,thinmultipoles=False,samplers='all',aperturedict={},collimatordict={},beampiperadius=0.2,verbose=False, beam=True, flipmagnets=False):
    """
    MadxTfs2Gmad - convert a madx twiss output file (.tfs) into a gmad input file for bdsim
    
    inputfilename  - path to the input file
    outputfilename - requested output file
    startname      - the name (exact string match) of the lattice element to start the machine at
                     this can also be an integer index of the element sequence number in madx tfs
    stopname       - the name (exact string match) of the lattice element to stop the machine at
                     this can also be an integer index of the element sequence number in madx tfs
    ignorezerolengthitems -
                   - nothing can be zero length in bdsim as real objects of course have some finite 
                     size.  Markers, etc are acceptable but for large lattices this can slow things 
                     down. True allows to ignore these altogether, which doesn't affect the length 
                     of the machine.
    thinmultipoles - will convert thin multipoles to ~1um thick finite length multipoles with
                     upscaled k values - experimental feature
    samplers       - can specify where to set samplers - options are None, 'all', or list of 
                     names of elements (normal python list of strings). Note default 'all' 
                     will generate separate outputfilename_samplers.gmad with all the samplers
                     which will be included in the main .gmad file - you can comment out the 
                     include to therefore exclude all samplers and retain the samplers file.
    aperturedict   - a dictionary of aperture information.  
                     keys should be exact string match of element name in tfs file
                     value should be a single number of the circular aperture (only circular just now)
                     e.g.  aperturdict = {'TCT1Bxy2':0.15,'TCT2Bxy2:0.20}  note values in metres
    collimatordict - a dictionary of dictionaries with collimator information keys should be exact 
                     string match of element name in tfs file value should be dictionary with the 
                     following keys:
                     "bdsim_material"   - the material - exact string as in bdsim manual
                     "angle"            - rotation angle of collimator in radians
                     "xsize"            - x full width in metres
                     "ysize"            - y full width in metres
    beampiperadius - in metres.  Default beam pipe radius and collimator setting if unspecified
    verbose        - print out lots of information when building the model
    beam           - True | False - generate an input gauss Twiss beam based on the values
                     of the twiss parameters at the beginning of the lattice (startname)
                     NOTE - we thoroughly recommend checking these parameters and this functionality
                     is only for partial convenience to have a model that works straight away.
    flipmagnets    - Trye | False - flip the sign of all k values for magnets - MADX currently 
                     tracks particles agnostic of the particle charge - BDISM however, follows their 
                     manual definition strictly - positive k -> horizontal focussing for positive 
                     partilces therefore, positive k -> vertical focussing for negative particles.  
                     Use this flag to flip the sign of all magnets.                    

    """
    lFake  = 1e-6 # fake length for thin magnets
    izlis  = ignorezerolengthitems
    if type(input) == str :
        print 'MadxTfs2Gmad> Loading file using pymadx'
        madx   = _pymadx.Tfs(input)
    else :
        print 'Already a pymadx instance - proceeding'
        madx   = input
    
    nitems = madx.nitems
    opencollimatorsetting = beampiperadius

    if verbose:
        madx.ReportPopulations()
        aper.ReportPopulations()

    # data structures for checks
    angtot = 0.0
    lentot = 0.0
    lldiff = []
    dldiff = {}
    itemsomitted = []

    kws = {} #extra parameters TO BE FINISHED
    
    #iterate through items in tfs and construct machine
    a = _Builder.Machine()
    
    #prepare index for iteration:
    if startname == None:
        startindex = 0
    elif type(startname) == int:
        startindex = startname
    else:
        startindex = madx.IndexFromName(startname)
    if stopname   == None:
        stopindex = nitems #this is 1 larger, but ok as range will stop at n-step -> step=1, range function issue
    elif type(stopname) == int:
        stopindex = stopname
    else:
        stopindex  = madx.IndexFromName(stopname)
    if stopindex <= startindex:
        print 'stopindex <= startindex'
        stopindex = startindex + 1

    lindex     = madx.ColumnIndex('L')
    angleindex = madx.ColumnIndex('ANGLE')
    vkickangleindex = madx.ColumnIndex('VKICK')
    hkickangleindex = madx.ColumnIndex('HKICK')
    ksIindex   = madx.ColumnIndex('KSI')
    k1lindex   = madx.ColumnIndex('K1L')
    k2lindex   = madx.ColumnIndex('K2L')
    k3lindex   = madx.ColumnIndex('K3L')
    k4lindex   = madx.ColumnIndex('K4L')
    k5lindex   = madx.ColumnIndex('K5L')
    k6lindex   = madx.ColumnIndex('K6L')
    k1slindex   = madx.ColumnIndex('K1SL')
    k2slindex   = madx.ColumnIndex('K2SL')
    k3slindex   = madx.ColumnIndex('K3SL')
    k4slindex   = madx.ColumnIndex('K4SL')
    k5slindex   = madx.ColumnIndex('K5SL')
    k6slindex   = madx.ColumnIndex('K6SL')
    tiltindex   = madx.ColumnIndex('TILT')
    tindex     = madx.ColumnIndex('KEYWORD')
    if verbose:
        print 'L       Column Index: ',lindex
        print 'ANGLE   Column Index: ',angleindex
        print 'K1L     Column Index: ',k1lindex
        print 'K2L     Column Index: ',k2lindex
        print 'K3L     Column Index: ',k3lindex
        print 'KEYWORD Column Index: ',tindex
     
    # iterate through input file and construct machine
    for i in range(startindex,stopindex):
        name = madx.sequence[i]
        #remove special characters like $, % etc 'reduced' name - rname
        rname = ''.join(e for e in name if e.isalnum()) 
        t     = madx.data[name][tindex]
        l     = madx.data[name][lindex]
        ang   = madx.data[name][angleindex]
        if l <1e-9:
            zerolength = True
        else:
            zerolength = False
        if verbose:
            print 'zerolength? ',str(name).ljust(20),str(l).ljust(20),' ->',zerolength
        lentot += l
        angtot += ang

        #element-wise keywords
        kws = {}
        if name in aperturedict:
            #for now only 1 aperture - circular
            ap = (aperturedict[name],'m')
            if ap[0] < 1e-4:
                ap = (defaultbeampiperadius,'m')
            if t != 'RCOLLIMATOR':
                kws['aper'] = ap

        #if l == 0 and izlis == True:
        #    pass
        if t == 'DRIFT':
            a.AddDrift(rname,l,**kws)
        elif t == 'HKICKER':
            kickangle = madx.data[name][hkickangleindex]
            a.AddHKicker(rname,l,angle=kickangle,**kws)
        elif t == 'INSTRUMENT':
            #most 'instruments' are just markers
            if izlis and zerolength:
                itemsomitted.append(name)
            elif (not izlis) and zerolength:
                a.AddMarker(rname)
                if verbose:
                    print name,' -> marker instead of instrument'
            else:
                a.AddDrift(rname,l,**kws)
        elif t == 'MARKER':
            if izlis:
                itemsomitted.append(name)
            else:
                a.AddMarker(rname)
        elif t == 'MONITOR':
            #most monitors are just markers
            if izlis and zerolength:
                itemsomitted.append(name)
            elif (not izlis) and zerolength:
                a.AddMarker(rname)
                if verbose:
                    print name,' -> marker instead of monitor'
            else:
                a.AddDrift(rname,l,**kws)
        elif t == 'MULTIPOLE':
            # TBC - cludge for thin multipoles (uses lFake for a short non-zero length)
            factor = -1 if flipmagnets else 1  #flipping magnets
            if thinmultipoles : 
                k1  = madx.data[name][k1lindex] / lFake * factor
                k2  = madx.data[name][k2lindex] / lFake * factor
                k3  = madx.data[name][k3lindex] / lFake * factor
                k4  = madx.data[name][k4lindex] / lFake * factor
                k5  = madx.data[name][k5lindex] / lFake * factor
                k6  = madx.data[name][k6lindex] / lFake * factor
                k1s = madx.data[name][k1slindex] / lFake * factor
                k2s = madx.data[name][k2slindex] / lFake * factor
                k3s = madx.data[name][k3slindex] / lFake * factor
                k4s = madx.data[name][k4slindex] / lFake * factor
                k5s = madx.data[name][k5slindex] / lFake * factor
                k6s = madx.data[name][k6slindex] / lFake * factor
                tilt= madx.data[name][tiltindex]
                if k1 != 0 : 
                    a.AddQuadrupole(rname,k1=k1,length=lFake,tilt=tilt) 
                else : 
                    a.AddMarker(rname)
#                    a.AddMultipole(name,length=lFake,knl=(k1,k2,k3),ksl=(k1s,k2s,k3s),tilt=tilt)

            if izlis and zerolength:
                itemsomitted.append(name)
            elif (not izlis) and zerolength:
                a.AddMarker(rname)
                if verbose:
                    print name,' -> marker instead of multipole'
            else:
                a.AddDrift(rname,l,**kws)
        elif t == 'OCTUPOLE':
            #TO BE FINISHED
            if izlis and zerolength:
                itemsomitted.append(name)
            elif (not izlis) and zerolength:
                a.AddMarker(rname)
                if verbose:
                    print name,' -> marker instead of octupole'
            else:
                #NO implmentation of octupoles yet..
                a.AddDrift(rname,l,**kws)
        elif t == 'PLACEHOLDER':
            if izlis and zerolength:
                itemsomitted.append(name)
            elif (not izlis) and zerolength:
                a.AddMarker(rname)
            else:
                a.AddDrift(rname,l,**kws)
                if verbose:
                    print name,' -> marker instead of placeholder'
        elif t == 'QUADRUPOLE':
            factor = -1 if flipmagnets else 1  #flipping magnets
            k1 = madx.data[name][k1lindex] / l * factor
            a.AddQuadrupole(rname,l,k1=k1,**kws)
        elif t == 'RBEND':
            angle = madx.data[name][angleindex]
            a.AddDipole(rname,'rbend',l,angle=angle,**kws)
        elif t == 'RCOLLIMATOR':
            #only use xsize as only have half gap
            if name in collimatordict:
                if 'bdsim_material' in collimatordict[name]:
                    kws['material'] = collimatordict[name]['bdsim_material']
                else:
                    kws['material'] = 'Copper'
                if 'xsize' in collimatordict[name]:
                    xsize = collimatordict[name]['xsize']
                else:
                    xsize = opencollimatorsetting
                if 'ysize' in collimatordict[name]:
                    ysize = collimatordict[name]['ysize']
                else:
                    tsize = opencollimatorsetting
                if 'angle' in collimatordict[name]:
                    angle = collimatordict[name]['angle']
                else:
                    angle = 0.0
            else:
                xsize = beampiperadius
                ysize = beampiperadius
                angle = 0.0
                kws['material'] = "Copper"
            a.AddRColAngled(rname,l,xsize,ysize,angle,**kws)
        elif t == 'ECOLLIMATOR':
            if name in collimatordict:
                if 'bdsim_material' in collimatordict[name]:
                    kws['material'] = collimatordict[name]['bdsim_material']
                else:
                    kws['material'] = 'Copper'
                if 'xsize' in collimatordict[name]:
                    xsize = collimatordict[name]['xsize']
                else:
                    xsize = opencollimatorsetting
                if 'ysize' in collimatordict[name]:
                    ysize = collimatordict[name]['ysize']
                else:
                    tsize = opencollimatorsetting
                if 'angle' in collimatordict[name]:
                    angle = collimatordict[name]['angle']
                else:
                    angle = 0.0
            else:
                xsize = beampiperadius
                ysize = beampiperadius
                angle = 0.0
                kws['material'] = "Copper"
            a.AddEColAngled(rname,l,xsize,ysize,angle,**kws)
        elif t == 'RFCAVITY':
            a.AddDrift(rname,l,**kws)
        elif t == 'SBEND':
            angle = madx.data[name][angleindex]
            k1 = madx.data[name][k1lindex] / l
            a.AddDipole(rname,'sbend',l,angle=angle, k1=k1,**kws)
        elif t == 'SEXTUPOLE':
            factor = -1 if flipmagnets else 1  #flipping magnets
            k2 = madx.data[name][k2lindex] / l * factor
            a.AddSextupole(rname,l,k2=k2,**kws)
        elif t == 'SOLENOID':
            #factor = -1 if flipmagnets else 1  #flipping magnets
            #ksi = madx.data[name][ksiindex]
            #a.AddSolenoid(rname,l,ks=ksi
            a.AddDrift(rname,l,**kws)
        elif t == 'TKICKER':
            a.AddDrift(rname,l,**kws)
        elif t == 'VKICKER':
            kickangle = madx.data[name][vkickangleindex]
            a.AddDrift(rname,l,angle=kickangle,**kws)
        else:
            print 'unknown element type: ',t,' for element named: ',name
            if zerolength:
                if izlis :
                    itemsomitted.append(name)
                else:
                    print 'putting marker in instead as its zero length'
                    a.AddMarker(rname)
            else:
                print 'putting drift in instead as it has finite length'
                a.AddDrift(rname,l)

    #add a single marker at the end of the line
    a.AddMarker('theendoftheline')
    
    a.AddSampler(samplers)

    # Make beam file 
    if beam : 
        b = MadxTfs2GmadBeam(madx, startname)
        a.AddBeam(b)

    a.WriteLattice(outputfilename)

    if verbose:
        print 'lentot ',lentot
        print 'angtot ',angtot
        print 'items omitted: '
        print itemsomitted
        #return lldiff,dldiff,a
    return a

def MadxTfs2GmadBeam(tfs,startname=None):
    if startname == None:
        startindex = 0
    elif type(startname) == int:
        startindex = startname
    else:
        startindex = madx.IndexFromName(startname)
    
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
    #print data['BETX'],data['ALFX'],data['MUX']
    #print data['BETY'],data['ALFY'],data['MUY']
    
    gammax = (1.0+data['ALFX'])/data['BETX']
    gammay = (1.0+data['ALFY'])/data['BETY']

    #note, in the main pybdsim.__init__.py Beam class is imported from Beam.py
    #so in this submodule when we do from .. import Beam it's actually the
    #already imported class that's being imported
    beam   = _Beam(particle,energy,'gausstwiss')
    beam.SetBetaX(data['BETX'])
    beam.SetBetaY(data['BETY'])
    beam.SetAlphaX(data['ALFX'])
    beam.SetAlphaY(data['ALFY'])
    beam.SetEmittanceX(ex,'m') 
    beam.SetEmittanceY(ey,'m')
    
    return beam

    

    
