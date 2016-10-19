import numpy as _np
import re as _re
import pymadx as _pymadx
from .. import Builder as _Builder
from .. import Options as _Options
from .. import Beam as _Beam
from .. import _General
from .. import XSecBias

_requiredKeys = [
    'L', 'ANGLE', 'KSI', 'K1L', 'K2L', 'K3L', 'K4L', 'K5L',
    'K1SL', 'K2SL', 'K3SL', 'K4SL', 'K5SL', 'K6SL',
    'TILT', 'KEYWORD', 'ALFX', 'ALFY', 'BETX', 'BETY',
    'VKICK', 'HKICK', 'E1', 'E2'
]

_lFake = 1e-6 # fake length for thin magnets

def TfsHasRequiredColumns(tfsinstance):
    """
    Test the tfs file to check it has everything we need.
    """
    test = _np.array([not (key in tfsinstance.columns) for key in _requiredKeys])
    if test.any():
        print 'Required columns : L, ANGLE, KSI, K1L...K6L, K1SL...K6SL, TILT,' 
        print '                   KEYWORD, ALFX, ALFY, BETX, BETY, VKICK, HKICK'
        print 'Missing column(s): ',_requiredKeys[test==True]
        raise KeyError("Required column missing from tfs file")

def MadxTfs2Gmad(input, outputfilename, startname=None, stopname=None, stepsize=1,
                 ignorezerolengthitems=True, thinmultipoles=False, samplers='all',
                 aperturedict={},
                 collimatordict={},
                 userdict={},
                 beampiperadius=5.0,
                 verbose=False, beam=True, flipmagnets=False, usemadxaperture=False,
                 defaultAperture='circular',
                 biasVacuum=None,
                 biasMaterial=None):
    """
    **MadxTfs2Gmad** convert a madx twiss output file (.tfs) into a gmad input file for bdsim
    
    +---------------------------+-------------------------------------------------------------------+
    | **inputfilename**         | path to the input file                                            |
    +---------------------------+-------------------------------------------------------------------+
    | **outputfilename**        | requested output file                                             |
    +---------------------------+-------------------------------------------------------------------+
    | **startname**             | the name (exact string match) of the lattice element to start the |
    |                           | machine at this can also be an integer index of the element       |
    |                           | sequence number in madx tfs.                                      |
    +---------------------------+-------------------------------------------------------------------+
    | **stopname**              | the name (exact string match) of the lattice element to stop the  |
    |                           | machine at this can also be an integer index of the element       |
    |                           | sequence number in madx tfs.                                      |
    +---------------------------+-------------------------------------------------------------------+
    | **stepsize**              | the slice step size. Default is 1, but -1 also useful for         |
    |                           | reversed line.                                                    |
    +---------------------------+-------------------------------------------------------------------+
    | **ignorezerolengthitems** | nothing can be zero length in bdsim as real objects of course     |
    |                           | have some finite size.  Markers, etc are acceptable but for large |
    |                           | lattices this can slow things down. True allows to ignore these   |
    |                           | altogether, which doesn't affect the length of the machine.       |
    +---------------------------+-------------------------------------------------------------------+
    | **thinmultipoles**        | will convert thin multipoles to ~1um thick finite length          |
    |                           | multipoles with upscaled k values - experimental feature          |
    +---------------------------+-------------------------------------------------------------------+
    | **samplers**              | can specify where to set samplers - options are None, 'all', or a |
    |                           | list of names of elements (normal python list of strings). Note   |
    |                           | default 'all' will generate separate outputfilename_samplers.gmad |
    |                           | with all the samplers which will be included in the main .gmad    |
    |                           | file - you can comment out the include to therefore exclude all   |
    |                           | samplers and retain the samplers file.                            |
    +---------------------------+-------------------------------------------------------------------+
    | **apertureinfo**          | aperture information. Can either be a dictionary of dictionaries  |
    |                           | with the the first key the exact name of the element and the      |
    |                           | daughter dictionary containing the relevant bdsim parameters as   |
    |                           | keys (must be valid bdsim syntax). Alternatively, this can be a   |
    |                           | pymadx.Aperture instance that will be queried.                    |
    +---------------------------+-------------------------------------------------------------------+
    | **collimatordict**        | a dictionary of dictionaries with collimator information keys     |
    |                           | should be exact string match of element name in tfs file value    |
    |                           | should be dictionary with the following keys:                     |
    |                           | "bdsim_material"   - the material                                 |
    |                           | "angle"            - rotation angle of collimator in radians      |
    |                           | "xsize"            - x full width in metres                       |
    |                           | "ysize"            - y full width in metres                       |
    +---------------------------+-------------------------------------------------------------------+
    | **userdict**              | A python dictionary the user can supply with any additional       |
    |                           | information for that particular element. The dictionary should    |
    |                           | have keys matching the exact element name in the Tfs file and     |
    |                           | contain a dictionary itself with key, value pairs of parameters   |
    |                           | and values to be added to that particular element.                |
    +---------------------------+-------------------------------------------------------------------+
    | **beampiperadius**        | In metres.  Default beam pipe radius and collimator setting if    |
    |                           | unspecified.                                                      |
    +---------------------------+-------------------------------------------------------------------+
    | **verbose**               | Print out lots of information when building the model.            |
    +---------------------------+-------------------------------------------------------------------+    
    | **beam**                  | True \| False - generate an input gauss Twiss beam based on the   |
    |                           | values of the twiss parameters at the beginning of the lattice    |
    |                           | (startname) NOTE - we thoroughly recommend checking these         |
    |                           | parameters and this functionality is only for partial convenience |
    |                           | to have a model that works straight away.                         |
    +---------------------------+-------------------------------------------------------------------+
    | **flipmagnets**           | True \| False - flip the sign of all k values for magnets - MADX  |
    |                           | currently tracks particles agnostic of the particle charge -      |
    |                           | BDISM however, follows their manual definition strictly -         |
    |                           | positive k -> horizontal focussing for positive partilces         |
    |                           | therefore, positive k -> vertical focussing for negative          |
    |                           | particles. Use this flag to flip the sign of all magnets.         |
    +---------------------------+-------------------------------------------------------------------+
    | **usemadxaperture**       | True \| False - use the aperture information in the TFS file if   |
    |                           | APER_1 and APER_2 columns exist.  Will only set if they're        |
    |                           | non-zero.                                                         |
    +---------------------------+-------------------------------------------------------------------+
    | **defaultAperture**       | The default aperture model to assume if none is specified.        |
    +---------------------------+-------------------------------------------------------------------+
    | **biasVacuum**            | Optional list of bias objects to written into each component      |
    |                           | definition that are attached to the vacuum volume.                |
    +---------------------------+-------------------------------------------------------------------+
    | **biasMaterial**          | Optional list of bias objects to written into each component      |
    |                           | definition that are attached to volumes outside the vacuum.       |
    +---------------------------+-------------------------------------------------------------------+

    Example:
    
    >>> a,o = pybdsim.Convert.MadxTfs2Gmad('twiss.tfs', 'mymachine')

    In normal mode:
    Returns Machine, [omittedItems]

    In verbose mode:
    Returns Machine, Machine, [omittedItems]
    
    Returns two pybdsim.Builder.Machine instances. The first desired full conversion.  The second is 
    the raw conversion that's not split by aperture. Thirdly, a list of the names of the omitted items
    is returned.
    """

    # machine instance that will be added to
    a = _Builder.Machine() # raw converted machine
    b = _Builder.Machine() # final machine, split with aperture
   
    izlis  = ignorezerolengthitems
    factor = -1 if flipmagnets else 1  #flipping magnets
    
    biasVacuumNames = []
    if type(biasVacuum) == XSecBias.XSecBias:
        biasVacuumNames.append(biasVacuum.name)
        a.AddBias(biasVacuum)
        b.AddBias(biasVacuum)
    elif type(biasVacuum) == list:
        biasVacuumNames = [bias.name for bias in biasVacuum]
        [a.AddBias(bias) for bias in biasVacuum]
        [b.AddBias(bias) for bias in biasVacuum]
    
    biasMaterialNames = []
    if type(biasMaterial) == XSecBias.XSecBias:
        biasMaterialNames.append(biasMaterial.name)
        a.AddBias(biasMaterial)
        b.AddBias(biasMaterial)
    elif type(biasMaterial) == list:
        biasMaterialNames = [bias.name for bias in biasMaterial]
        [a.AddBias(bias) for bias in biasMaterial]
        [b.AddBias(bias) for bias in biasMaterial]
    
    # define utility function that does conversion
    def AddSingleElement(item, a, aperModel=None):
        # a is a pybdsim.Builder.Machine instance
        # if it's already a prepared element, just append it
        if type(item) == _Builder.Element:
            a.Append(item)
            return

        kws = {} # element-wise keywords
        if len(biasVacuumNames) > 0:
            kws['biasVacuum'] = ' '.join(biasVacuumNames)
        if len(biasMaterialNames) > 0:
            kws['biasMaterial'] = ' '.join(biasMaterialNames)
        
        if aperModel != None:
            kws.update(aperModel)

        name  = item['NAME']
        rname = _General.PrepareReducedName(name) #remove special characters like $, % etc 'reduced' name - rname
        t     = item['KEYWORD']
        l     = item['L']
        ang   = item['ANGLE']

        # append any user defined parameters for this element into the kws dictionary
        if name in userdict:
            kws.update(userdict[name])

        if verbose:
            print kws
        
        if t == 'DRIFT':
            #print 'AddDrift'
            a.AddDrift(rname,l,**kws)
        elif t == 'HKICKER':
            kickangle = item['HKICK'] * factor
            if zerolength and not izlis:
                a.AddMarker(rname)
            else:
                a.AddHKicker(rname,l,angle=kickangle,**kws)
        elif t == 'INSTRUMENT':
            #most 'instruments' are just markers
            if zerolength and not izlis:
                a.AddMarker(rname)
                if verbose:
                    print name,' -> marker instead of instrument'
            else:
                a.AddDrift(rname,l,**kws)
        elif t == 'MARKER':
            if not izlis:
                a.AddMarker(rname)
        elif t == 'MONITOR':
            #most monitors are just markers
            if zerolength and not izlis:
                a.AddMarker(rname)
                if verbose:
                    print name,' -> marker instead of monitor'
            else:
                a.AddDrift(rname,l,**kws)
        elif t == 'MULTIPOLE':
            # TBC - cludge for thin multipoles (uses _lFake for a short non-zero length)
            if thinmultipoles:
                print 'WARNING - conversion of thin multipoles is not finished yet!'
                k1  = item['K1L']  / _lFake * factor
                k2  = item['K2L']  / _lFake * factor
                k3  = item['K3L']  / _lFake * factor
                k4  = item['K4L']  / _lFake * factor
                k5  = item['K5L']  / _lFake * factor
                k6  = item['K6L']  / _lFake * factor
                k1s = item['K1SL'] / _lFake * factor
                k2s = item['K2SL'] / _lFake * factor
                k3s = item['K3SL'] / _lFake * factor
                k4s = item['K4SL'] / _lFake * factor
                k5s = item['K5SL'] / _lFake * factor
                k6s = item['K6SL'] / _lFake * factor
                tilt= item['TILT']
                print 'WARNING - only using quadrupole component just now!'
                if k1 != 0 : 
                    a.AddQuadrupole(rname,k1=k1,length=_lFake,**kws) 
                else:
                    a.AddMarker(rname)
                    #a.AddMultipole(name,length=_lFake,knl=(k1,k2,k3),ksl=(k1s,k2s,k3s),**kws)
            elif zerolength and not izlis:
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
            e1 = item['E1']
            e2 = item['E2']
            if (e1 != 0):
                kws['e1'] = e1
            if (e1 != 0):
                kws['e2'] = e2
            a.AddDipole(rname,'rbend',l,angle=angle,**kws)
        elif t == 'RCOLLIMATOR' or t == 'ECOLLIMATOR':
            #only use xsize as only have half gap
            if name in collimatordict:
                #gets a dictionary then extends kws dict with that dictionary
                colld = collimatordict[name]
                kws['material'] = colld['material']
                kws['tilt']     = colld['tilt']
                xsize           = colld['xsize']
                ysize           = colld['ysize']
                print xsize
                #if xsize > 0.1 or ysize > 0.1:
                kws['outerDiameter'] = max(xsize,ysize)*2.5
                print kws
                if t == 'RCOLLIMATOR':
                    a.AddRCol(rname,l,xsize,ysize,**kws)
                else:
                    a.AddECol(rname,l,xsize,ysize,**kws)
            else:
                a.AddDrift(rname,l)
        elif t == 'RFCAVITY':
            a.AddDrift(rname,l,**kws)
        elif t == 'SBEND':
            angle = item['ANGLE']
            e1 = item['E1']
            e2 = item['E2']
            if (e1 != 0):
                kws['e1'] = e1
            if (e1 != 0):
                kws['e2'] = e2
            k1l = item['K1L']
            if k1l != 0:
                k1 = k1l / l * factor
                kws['k1'] = k1
            a.AddDipole(rname,'sbend',l,angle=angle,**kws)
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
            if zerolength and not izlis:
                print 'putting marker in instead as its zero length'
                a.AddMarker(rname)
            else:
                print 'putting drift in instead as it has a finite length'
                a.AddDrift(rname,l)
    # end of utility conversion function

    # test whether filpath or tfs instance supplied
    madx = _pymadx._General.CheckItsTfs(input)

    # check it has all the required columns
    TfsHasRequiredColumns(madx)

    if verbose:
        madx.ReportPopulations()

    # check aperture information if supplied
    useTfsAperture = False
    print 'TYPE of aperdict: ',type(aperturedict)
    if type(aperturedict) == _pymadx.Aperture:
        useTfsAperture = True
        if verbose:
            aperturedict.ReportPopulations()
    if verbose:
        print 'Using pymadx.Apeture instance? --> ',useTfsAperture
    
    # keep list of omitted zero length items
    itemsomitted = []
    
    # iterate through input file and construct machine
    for item in madx[startname:stopname:stepsize]:
        name = item['NAME']
        t    = item['KEYWORD']
        l    = item['L']
        zerolength = True if item['L'] < 1e-9 else False
        if verbose:
            print 'zerolength? ',str(name).ljust(20),str(l).ljust(20),' ->',zerolength
        if zerolength and ignorezerolengthitems:
            itemsomitted.append(name)
            if verbose:
                print 'skipping this item'
            continue # skip this item in the for loop

        # now deal with aperture
        if useTfsAperture:
            sMid = (item['S']*2 - item['L'] ) * 0.5
            apermodel = _Builder.PrepareApertureModel(aperturedict.GetApertureAtS(sMid), defaultAperture)
            #apermodel = aperturedict.GetApertureForElementNamed(name)
            #print 'Using aperture instance'
            should,lengths,apers = aperturedict.ShouldSplit(item)
            should = False
            if should:
                if verbose:
                    print 'Splitting item based on aperture'
                ls = _np.array(lengths)
                if abs(_np.array(lengths).sum() - l) > 1e-6 or (ls < 0).any():
                    print 'OH NO!!!'
                    print l
                    print lengths
                    print apers
                    return
                # we should split this item up
                # add it first to the raw machine
                AddSingleElement(item, a)
                # now get the last element - the one that's just been added
                lastelement = a[-1]
                for splitLength,aper in zip(lengths,apers):
                    # append the right fraction with the appropriate aperture
                    # to the 'b' machine
                    apermodel = _Builder.PrepareApertureModel(aper, defaultAperture)
                    print apermodel
                    AddSingleElement(lastelement*(splitLength/l), b, apermodel)
            #else:
                #apermodel = _Builder.PrepareApertureModel(apers[0],defaultAperture)
                #print apermodel
                #print len(b)
            AddSingleElement(item, a, apermodel)
            AddSingleElement(item, b, apermodel)
            #    print len(b)
        elif usemadxaperture and name not in aperturedict:
            print 'Using aperture in madx tfs file'
            apermodel = _Builder.PrepareApertureModel(item, defaultAperture)
            AddSingleElement(item, a, apermodel)
            AddSingleElement(item, b, apermodel)
        elif item['NAME'] in aperturedict:
            apermodel = _Build.PrepareApertureModel(aperturedict[name], defaultAperture)
            AddSingleElement(item, a, apermodel)
            AddSingleElement(item, b, apermodel)
        else:
            AddSingleElement(item, a)
            AddSingleElement(item, b)
    # end of for loop
                
    #add a single marker at the end of the line
    a.AddMarker('theendoftheline')
    b.AddMarker('theendoftheline')
    
    a.AddSampler(samplers)
    b.AddSampler(samplers)

    # Make beam file 
    if beam: 
        bm = MadxTfs2GmadBeam(madx, startname, verbose)
        a.AddBeam(bm)
        b.AddBeam(bm)

    options = _Options.Options()
    options.SetBeamPipeRadius(beampiperadius,unitsstring='cm')
    a.AddOptions(options)
    b.AddOptions(options)

    b.Write(outputfilename)
    if verbose:
        a.Write(outputfilename+"_raw")
        print 'Total length: ',a.GetIntegratedLength()
        print 'Total angle:  ',a.GetIntegratedAngle()
        print 'items omitted: '
        print itemsomitted
        print 'number of omitted items: ',len(itemsomitted)

    return b,a,itemsomitted

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
        print 'beta_x: ',data['BETX'],'alpha_x: ',data['ALFX'],'mu_x: ',data['MUX']
        print 'beta_y: ',data['BETY'],'alpha_y: ',data['ALFY'],'mu_y: ',data['MUY']
    
    #gammax = (1.0+data['ALFX'])/data['BETX']
    #gammay = (1.0+data['ALFY'])/data['BETY']

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
    beam.SetXP0(tfs[startindex]['PX'])
    beam.SetYP0(tfs[startindex]['PY'])
    return beam
