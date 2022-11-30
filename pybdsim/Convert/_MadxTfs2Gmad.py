from copy import deepcopy as _deepcopy
import numpy as _np
import pymadx as _pymadx
import warnings as _warnings
from .. import Builder as _Builder
from ..Options import Options as _Options
from .. import Beam as _Beam
from .. import Data as _Data
import pybdsim._General

_requiredKeys = frozenset([
    'L', 'ANGLE', 'KSI',
    'K1L', 'K2L', 'K3L', 'K4L', 'K5L', 'K6L',
    'K1SL', 'K2SL', 'K3SL', 'K4SL', 'K5SL', 'K6SL',
    'TILT', 'KEYWORD', 'ALFX', 'ALFY', 'BETX', 'BETY',
    'VKICK', 'HKICK', 'E1', 'E2', 'FINT', 'FINTX', 'HGAP'])

_ignoreableThinElements = {"MONITOR", "PLACEHOLDER", "MARKER",
                           "RCOLLIMATOR", "ECOLLIMATOR",
                           "COLLIMATOR", "INSTRUMENT"}

# Constants
# anything below this length is treated as a thin element
_THIN_ELEMENT_THRESHOLD = 1e-6


def ZeroMissingRequiredColumns(tfsinstance):
    """
    Sets any missing required columns to zero.  Warns user when doing so.
    """
    missingColumns = [key for key
                      in _requiredKeys if key not in tfsinstance.columns]

    if not missingColumns:
        return

    for column in missingColumns:
        tfsinstance.columns.append(column)
        for key, data in tfsinstance.data.items():
            data.append(0.0)

    missingColsString = ", ".join(["\"{}\"".format(col)
                                   for col in missingColumns])
    msg = ("Columns missing from TFS: {}.  All have been set"
           " to zero.").format(missingColsString)
    print(msg)

def _WillIgnoreItem(item, tfsinstance, ignoreZeroLength, ignoreableThinElements):
    tresult    = item['KEYWORD'] in ignoreableThinElements    
    zerolength = item['L'] < 1e-9
    result     = not tfsinstance.ElementPerturbs(item) and zerolength and ignoreZeroLength and tresult
    return result

def MadxTfs2Gmad(tfs, outputfilename,
                 startname             = None,
                 stopname              = None,
                 stepsize              = 1,
                 ignorezerolengthitems = True,
                 samplers              = 'all',
                 aperturedict          = {},
                 aperlocalpositions    = {},
                 collimatordict        = {},
                 userdict              = {},
                 partnamedict          = {},
                 verbose               = False,
                 beam                  = True,
                 flipmagnets           = None,
                 usemadxaperture       = False,
                 defaultAperture       = 'circular',
                 biases                = None,
                 allelementdict        = {},
                 optionsdict           = {},
                 beamparamsdict        = {},
                 linear                = False,
                 overwrite             = True,
                 write                 = True,
                 allNamesUnique        = False,
                 namePrepend           = ""):
    """
    **MadxTfs2Gmad** convert a madx twiss output file (.tfs) into a gmad tfs file for bdsim

    Example:

    >>> a,b = pybdsim.Convert.MadxTfs2Gmad('twiss.tfs', 'mymachine')

    returns Machine, [omittedItems]

    Returns two pybdsim.Builder.Machine instances. The first desired full conversion.  The second is
    the raw conversion that's not split by aperture. Thirdly, a list of the names of the omitted items
    is returned.

    +-------------------------------+-------------------------------------------------------------------+
    | **tfs**                       | path to the input tfs file or pymadx.Data.Tfs instance            |
    +-------------------------------+-------------------------------------------------------------------+
    | **outputfilename**            | requested output file                                             |
    +-------------------------------+-------------------------------------------------------------------+
    | **startname**                 | the name (exact string match) of the lattice element to start the |
    |                               | machine at this can also be an integer index of the element       |
    |                               | sequence number in madx tfs. This item is included in the lattice |
    +-------------------------------+-------------------------------------------------------------------+
    | **stopname**                  | the name (exact string match) of the lattice element to stop the  |
    |                               | machine at this can also be an integer index of the element       |
    |                               | sequence number in madx tfs. This item is not included            |
    +-------------------------------+-------------------------------------------------------------------+
    | **stepsize**                  | the slice step size. Default is 1, but -1 also useful for         |
    |                               | reversed line.                                                    |
    +-------------------------------+-------------------------------------------------------------------+
    | **ignorezerolengthitems**     | nothing can be zero length in bdsim as real objects of course     |
    |                               | have some finite size.  Markers, etc are acceptable but for large |
    |                               | lattices this can slow things down. True allows to ignore these   |
    |                               | altogether, which doesn't affect the length of the machine.       |
    +-------------------------------+-------------------------------------------------------------------+
    | **samplers**                  | can specify where to set samplers - options are None, 'all', or a |
    |                               | list of names of elements (normal python list of strings). Note   |
    |                               | default 'all' will generate separate outputfilename_samplers.gmad |
    |                               | with all the samplers which will be included in the main .gmad    |
    |                               | file - you can comment out the include to therefore exclude all   |
    |                               | samplers and retain the samplers file.                            |
    +-------------------------------+-------------------------------------------------------------------+
    | **aperturedict**              | Aperture information. Can either be a dictionary of dictionaries  |
    |                               | with the the first key the exact name of the element and the      |
    |                               | daughter dictionary containing the relevant bdsim parameters as   |
    |                               | keys (must be valid bdsim syntax). Alternatively, this can be a   |
    |                               | pymadx.Aperture instance that will be queried.                    |
    +-------------------------------+-------------------------------------------------------------------+
    | **aperlocalpositions**        | Dictionary of element indices to local aperture definitions       |
    |                               | of the form                                                       |
    |                               | {1: [(0.0, {"APERTYPE": "CIRCULAR", "APER1": 0.4}),               |
    |                               |      (0.5, {"APERTYPE": "ELLIPSE",  "APER1": 0.3, "APER2": 0.4}), |
    |                               |      ...],                                                        |
    |                               |  2: [...],                                                        |
    |                               | }                                                                 |
    |                               | This defines apertures in the element at index 1                  |
    |                               | starting with a CIRCULAR aper from 0.0m (i.e. the start) before   |
    |                               | changing to ELLIPSE 0.5m into the element, with possible further  |
    |                               | changes not displayed above.  As the aperture definition in GMAD  |
    |                               | is tied inseparable from its aperture definition, and vice versa, |
    |                               | this conversion function will automatically split the element     |
    |                               | at the provided local aperture points whilst retaining optical    |
    |                               | correctness.                                                      |
    |                               | This kwarg is mutually exclusive with 'aperturedict'.             |
    +-------------------------------+-------------------------------------------------------------------+
    | **collimatordict**            | A dictionary of dictionaries with collimator information keys     |
    |                               | should be exact string match of element name in tfs file value    |
    |                               | should be dictionary with the following keys:                     |
    |                               | 'bdsim_material'   - the material                                 |
    |                               | 'angle'            - rotation angle of collimator in radians      |
    |                               | 'xsize'            - x full width in metres                       |
    |                               | 'ysize'            - y full width in metres                       |
    +-------------------------------+-------------------------------------------------------------------+
    | **userdict**                  | A python dictionary the user can supply with any additional       |
    |                               | information for that particular element. The dictionary should    |
    |                               | have keys matching the exact element name in the Tfs file and     |
    |                               | contain a dictionary itself with key, value pairs of parameters   |
    |                               | and values to be added to that particular element.                |
    +-------------------------------+-------------------------------------------------------------------+
    | **partnamedict**              | A python dictionary of dictionaries. The key is a substring of    |
    |                               | that should be matched. ie add the parameter 'vhRatio' : 1 to all |
    |                               | elements with 'MBVA' in their name.                               |
    +-------------------------------+-------------------------------------------------------------------+
    | **verbose**                   | Print out lots of information when building the model.            |
    +-------------------------------+-------------------------------------------------------------------+
    | **beam**                      | True \| False - generate an input gauss Twiss beam based on the   |
    |                               | values of the twiss parameters at the beginning of the lattice    |
    |                               | (startname) NOTE - we thoroughly recommend checking these         |
    |                               | parameters and this functionality is only for partial convenience |
    |                               | to have a model that works straight away.                         |
    +-------------------------------+-------------------------------------------------------------------+
    | **flipmagnets**               | True \| False - flip the sign of all k values for magnets - MADX  |
    |                               | currently tracks particles agnostic of the particle charge -      |
    |                               | BDSIM however, follows the definition strictly -                  |
    |                               | positive k -> horizontal focussing for positive particles         |
    |                               | therefore, positive k -> vertical focussing for negative          |
    |                               | particles. Use this flag to flip the sign of all magnets.         |
    +-------------------------------+-------------------------------------------------------------------+
    | **usemadxaperture**           | True \| False - use the aperture information in the TFS file if   |
    |                               | APER_1 and APER_2 columns exist.  Will only set if they're        |
    |                               | non-zero.  Supercedes kwargs `aperturedict` and                   |
    |                               | `aperlocalpositions`.                                             |
    +-------------------------------+-------------------------------------------------------------------+
    | **defaultAperture**           | The default aperture model to assume if none is specified.        |
    +-------------------------------+-------------------------------------------------------------------+
    | **biases**                    | Optional list of bias objects to be defined in own _bias.gmad     |
    |                               | file.  These can then be attached either with allelementdict for  |
    |                               | all components or userdict for individual ones.                   |
    +-------------------------------+-------------------------------------------------------------------+
    | **allelementdict**            | Dictionary of parameter/value pairs to be written to all          |
    |                               | components.                                                       |
    +-------------------------------+-------------------------------------------------------------------+
    | **optionsdict**               | Optional dictionary of general options to be written to the       |
    |                               | bdsim model options.                                              |
    +-------------------------------+-------------------------------------------------------------------+
    | **beamparamsdict**            | Optional dictionary of parameters to be passed to the beam.       |
    +-------------------------------+-------------------------------------------------------------------+
    | **linear**                    | Only linear optical components                                    |
    +-------------------------------+-------------------------------------------------------------------+
    | **overwrite**                 | Do not append an integer to the base file name if it already      |
    |                               | exists.  Instead overwrite the files.                             |
    +-------------------------------+-------------------------------------------------------------------+
    | **allNamesUnique**            | Treat every row in the TFS file/instance as a unique element.     |
    |                               | This makes it easier to edit individual components as they are    |
    |                               | guaranteed to appear only once in the entire resulting GMAD       |
    |                               | lattice.                                                          |
    +-------------------------------+-------------------------------------------------------------------+
    | **write**                     | Whether to write the converted machine to file or not.            |
    +-------------------------------+-------------------------------------------------------------------+
    | **namePrepend**               | Optional string prepended to the name of every component.         |
    +-------------------------------+-------------------------------------------------------------------+

    """

    # machine instance that will be added to
    machine = _Builder.Machine()

    # test whether filepath or tfs instance supplied
    madx = _pymadx.Data.CheckItsTfs(tfs)

    # not very elegant but needs to be done
    varnames = ['collimatordict','userdict','partnamedict','allelementdict','optionsdict','beamparamsdict']
    vars     = [collimatordict,   userdict,  partnamedict,  allelementdict,  optionsdict,  beamparamsdict]
    for var,varname in zip(vars,varnames):
        typevar = type(var)
        if typevar not in (dict, _Data.BDSAsciiData):
            raise TypeError("Argument '" + varname + "' is not a dictionary")

    if usemadxaperture:
        aperturedict = madx
    elif aperturedict and aperlocalpositions:
        msg = "'aperturedict' and 'aperlocalpositions' are mutually exclusive."
        raise TypeError(msg)

    if "PARTICLE" in madx.header and flipmagnets is None:
        # try to check automatically
        particleName = madx.header['PARTICLE']
        if particleName == "ELECTRON":
            flipmagnets = True
            print('Detected electron in TFS file - changing flipmagnets to True')

    # If we have collimators but no collimator dict then inform that
    # they will be converted to drifts.  should really check
    # tfs[startname..]
    if "APERTYPE" in madx.columns:
        if (("RCOLLIMATOR" in madx.GetColumn("APERTYPE")
             or "ECOLLIMATOR" in madx.GetColumn("APERTYPE"))
                and not collimatordict):
            _warnings.warn("No collimatordict provided.  ALL collimators will be converted to DRIFTs.")

    if biases is not None:
        machine.AddBias(biases)

    # check whether it has all the required columns.
    ZeroMissingRequiredColumns(madx)

    if verbose:
        madx.ReportPopulations()

    # keep list of omitted zero length items
    itemsomitted = []

    # iterate through input file and construct machine
    for item in madx[startname:stopname:stepsize]:
        name = item['NAME']
        t = item['KEYWORD']
        l = item['L']
        i = item['INDEX']

        zerolength = True if item['L'] < 1e-9 else False
        if (_WillIgnoreItem(item, madx, ignorezerolengthitems, _ignoreableThinElements)):
            if verbose:
                print('skipping zero-length item: {}'.format(name))
            itemsomitted.append(name)
            continue  # skip this item.

        gmadElement = _Tfs2GmadElementFactory(item, allelementdict, verbose,
                                              userdict, collimatordict, partnamedict,
                                              flipmagnets, linear,
                                              zerolength, ignorezerolengthitems,
                                              allNamesUnique,
                                              namePrepend)
        if gmadElement is None: # factory returned nothing, go to next item.
            continue
        # We generally convert unsupported elements in the factory to
        # drifts, but if that then results in a drift with zero
        # length, then skip it.
        elif gmadElement.length == 0.0 and isinstance(gmadElement,
                                                      _Builder.Drift):
            continue
        elif l == 0.0: # Don't try to attach apertures to thin elements.
            machine.Append(gmadElement)
        elif name in collimatordict: # Don't add apertures to collimators
            machine.Append(gmadElement)
        elif aperlocalpositions: # split aperture if provided.
            elements_split_with_aper = _GetElementSplitByAperture(gmadElement,
                                                                  aperlocalpositions[i])
            for ele in elements_split_with_aper:
                machine.Append(ele)
        else: # Get element with single aperture
            element_with_aper = _GetSingleElementWithAper(item,
                                                          gmadElement,
                                                          aperturedict,
                                                          defaultAperture)
            machine.Append(element_with_aper)

    if (samplers is not None):
        machine.AddSampler(samplers)

    # Make beam file
    if beam:
        bm = MadxTfs2GmadBeam(madx, startname, verbose, extraParamsDict=beamparamsdict)
        machine.AddBeam(bm)

    options = _Options()
    if optionsdict:
        options.update(optionsdict)  # expand with user supplied bdsim options
    machine.AddOptions(options)

    if verbose:
        print('Total length: ', machine.GetIntegratedLength())
        print('Total angle:  ', machine.GetIntegratedAngle())
        print('items omitted: ')
        print(itemsomitted)
        print('number of omitted items: ', len(itemsomitted))

    if write:
        machine.Write(outputfilename, overwrite=overwrite)
    # We return machine twice to not break old interface of returning
    # two machines.
    return machine, itemsomitted


def _Tfs2GmadElementFactory(item, allelementdict, verbose,
                            userdict, collimatordict, partnamedict, flipmagnets,
                            linear, zerolength,
                            ignorezerolengthitems,
                            allNamesUnique,
                            namePrepend=""):
    """
    Function which makes the correct GMAD element given a TFS
    element to gmad.
    """
    factor = 1
    if flipmagnets is not None:
        factor = -1 if flipmagnets else 1  # flipping magnets

    # if it's already a prepared element, just return it
    if isinstance(item, _Builder.Element):
        return item

    kws = {}  # ensure empty
    # deep copy as otherwise allelementdict gets irreparably changed!
    kws = _deepcopy(allelementdict)
    if verbose:
        print('Starting key word arguments from all element dict')
        print(kws)

    name = item['NAME']
    # remove special characters like $, % etc 'reduced' name - rname:
    rname = pybdsim._General.PrepareReducedName(name
                                                if not allNamesUnique
                                                else item["UNIQUENAME"])
    t = item['KEYWORD']
    l = item['L']
    tilt = item['TILT']

    if tilt != 0:
        kws['tilt'] = tilt

    # append any user defined parameters for this element into the
    # kws dictionary

    rname = namePrepend + rname
    # name appears in the madx.  try this first.
    if name in userdict:
        kws.update(userdict[name])
    elif rname in userdict:  # rname appears in the gmad
        kws.update(userdict[rname])

    for partname in partnamedict:
        if partname in name:
            kws.update(partnamedict[partname])

    if verbose:
        print('Full set of key word arguments:')
        print(kws)

    if t == 'DRIFT':
        return _Builder.Drift(rname, l, **kws)
    elif t == 'HKICKER':
        if verbose:
            print('HICKER', rname)
        hkick = item['HKICK'] * factor
        if not zerolength:
            if l > _THIN_ELEMENT_THRESHOLD:
                kws['l'] = l
        return _Builder.HKicker(rname, hkick=hkick, **kws)
    elif t == 'VKICKER':
        if verbose:
            print('VKICKER', rname)
        vkick = item['VKICK'] * factor
        if not zerolength:
            if l > _THIN_ELEMENT_THRESHOLD:
                kws['l'] = l
        return _Builder.VKicker(rname, vkick=vkick, **kws)
    elif t == 'KICKER':
        if verbose:
            print('KICKER', rname)
        hkick = item['HKICK'] * factor
        vkick = item['VKICK'] * factor
        if not zerolength:
            if l > _THIN_ELEMENT_THRESHOLD:
                kws['l'] = l
        return _Builder.Kicker(rname, hkick=hkick, vkick=vkick, **kws)
    elif t == 'TKICKER':
        if verbose:
            print('TKICKER', rname)
        hkick = item['HKICK'] * factor
        vkick = item['VKICK'] * factor
        if not zerolength:
            if l > _THIN_ELEMENT_THRESHOLD:
                kws['l'] = l
        return _Builder.TKicker(rname, hkick=hkick, vkick=vkick, **kws)
    elif t == 'INSTRUMENT':
        # most 'instruments' are just markers
        if zerolength and not ignorezerolengthitems:
            return _Builder.Marker(rname)
        return _Builder.Drift(rname, l, **kws)
    elif t == 'MARKER':
        if not ignorezerolengthitems:
            return _Builder.Marker(rname)
    elif t == 'MONITOR':
        # most monitors are just markers
        if zerolength and not ignorezerolengthitems:
            return _Builder.Marker(rname)
        return _Builder.Drift(rname, l, **kws)
    elif t == 'MULTIPOLE':
        k1 = item['K1L'] * factor
        k2 = item['K2L'] * factor if not linear else 0
        k3 = item['K3L'] * factor if not linear else 0
        k4 = item['K4L'] * factor if not linear else 0
        k5 = item['K5L'] * factor if not linear else 0
        k6 = item['K6L'] * factor if not linear else 0
        k1s = item['K1SL'] * factor
        k2s = item['K2SL'] * factor if not linear else 0
        k3s = item['K3SL'] * factor if not linear else 0
        k4s = item['K4SL'] * factor if not linear else 0
        k5s = item['K5SL'] * factor if not linear else 0
        k6s = item['K6SL'] * factor if not linear else 0

        knl = (k1,  k2,  k3,  k4,  k5,  k6)
        ksl = (k1s, k2s, k3s, k4s, k5s, k6s)

        finiteStrength = _np.any(
            [k1, k2, k3, k4, k5, k6, k1s, k2s, k3s, k4s, k5s, k6s])

        if zerolength or l < _THIN_ELEMENT_THRESHOLD:
            return _Builder.ThinMultipole(rname, knl=knl, ksl=ksl, **kws)
        else:
            return _Builder.Multipole(rname, l, knl=knl, ksl=ksl, **kws)
    elif t == 'OCTUPOLE':
        if zerolength or l < _THIN_ELEMENT_THRESHOLD:
            k3 = item['K3L'] * factor if not linear else 0
            return _Builder.ThinMultipole(rname, knl=(0, 0, k3), **kws)
        k3 = item['K3L'] / l * factor if not linear else 0
        return _Builder.Octupole(rname, l, k3=k3, **kws)
    elif t == 'PLACEHOLDER':
        if zerolength:
            if not ignorezerolengthitems:
                return _Builder.Marker(rname)
        else:
            return _Builder.Drift(rname, l, **kws)
    elif t == 'QUADRUPOLE':
        if zerolength or l < _THIN_ELEMENT_THRESHOLD:
            k1 = item['K1L'] * factor
            return _Builder.ThinMultipole(rname, knl=(k1,), **kws)
        k1 = item['K1L'] / l * factor
        return _Builder.Quadrupole(rname, l, k1, **kws)
    elif t == 'RBEND':
        angle = item['ANGLE']
        e1 = item['E1'] if 'E1' in item else 0
        e2 = item['E2'] if 'E2' in item else 0
        fint = item['FINT'] if 'FINT' in item else 0
        fintx = item['FINTX'] if 'FINTX' in item else -1 # madx convention -> -1 => same as FINT
        h1 = item['H1'] if 'H1' in item else 0
        h2 = item['H2'] if 'H2' in item else 0
        hgap = item['HGAP'] if 'HGAP' in item else 0
        k1l = item['K1L']
        # set element length to be the chord length - tfs output rbend
        # length is arc length
        chordLength = l
        if angle != 0:
            chordLength = 2 * (l / angle) * _np.sin(angle / 2.) #protect against 0 angle rbends
        # subtract dipole angle/2 added on to poleface angles internally by
        # madx
        poleInAngle = e1 - 0.5 * angle
        poleOutAngle = e2 - 0.5 * angle
        if poleInAngle != 0:
            kws['e1'] = poleInAngle
        if poleOutAngle != 0:
            kws['e2'] = poleOutAngle
        if fint != 0:
            kws['fint'] = fint
        # in madx, -1 means fintx was allowed to default to fint and we should do the same
        # so if set to 0, this means we want it to be 0
        if fintx != -1:
            kws['fintx'] = fintx
        if h1 != 0:
            kws['h1'] = h1
        if h2 != 0:
            kws['h2'] = h2
        if hgap != 0:
            kws['hgap'] = hgap
        if k1l != 0:
            # NOTE we don't use factor here for magnet flipping
            k1 = k1l / l
            kws['k1'] = k1
        return _Builder.RBend(rname, chordLength, angle=angle, **kws)
    elif t == 'SBEND':
        angle = item['ANGLE']
        e1 = item['E1'] if 'E1' in item else 0
        e2 = item['E2'] if 'E2' in item else 0
        fint = item['FINT'] if 'FINT' in item else 0
        fintx = item['FINTX'] if 'FINTX' in item else -1
        h1 = item['H1'] if 'H1' in item else 0
        h2 = item['H2'] if 'H2' in item else 0
        hgap = item['HGAP'] if 'HGAP' in item else 0
        k1l = item['K1L']
        if e1 != 0:
            kws['e1'] = e1
        if e2 != 0:
            kws['e2'] = e2
        if k1l != 0:
            # NOTE we're not using factor for magnet flipping here
            k1 = k1l / l
            kws['k1'] = k1

        # if fint != 0:
        kws['fint'] = fint

        # in madx, -1 means fintx was allowed to default to fint and we should do the same
        # so if set to 0, this means we want it to be 0
        if fintx == -1:
            if fint:
                kws['fintx'] = fint
            else:
                kws['fintx'] = 0
        else:
            kws['fintx'] = fintx
        if h1 != 0:
            kws['h1'] = h1
        if h2 != 0:
            kws['h2'] = h2
        # if hgap != 0:
        kws['hgap'] = hgap
        return _Builder.SBend(rname, l, angle=angle, **kws)
    elif t in {'RCOLLIMATOR', 'ECOLLIMATOR', 'COLLIMATOR'}:
        # only use xsize as only have half gap
        if name in collimatordict:
            # gets a dictionary then extends kws dict with that dictionary
            colld = collimatordict[name]

            # collimator defined by external geometry file
            if 'geometryFile' in colld:
                kws['geometryFile'] = colld['geometryFile']
                k = 'outerDiameter'  # key
                if k not in kws:
                    # not already specified via other dictionaries
                    if k in colld:
                        kws[k] = colld[k]
                    else:
                        kws[k] = 1  # ensure there's a default as not in madx
                # add a general element
                return _Builder.ExternalGeometry(rname, l, **kws)
            else:
                kws['material'] = colld.get('material', 'copper')
                tilt = colld.get('tilt', 0)
                if tilt != 0:
                    kws['tilt'] = tilt
                try:
                    xsize = colld['xsize']
                    ysize = colld['ysize']
                except KeyError:
                    xsize = colld['XSIZE']
                    ysize = colld['YSIZE']
                if verbose:
                    print('collimator x,y size ', xsize, ysize)
                if 'outerDiameter' in colld:
                    kws['outerDiameter'] = colld['outerDiameter']
                else:
                    kws['outerDiameter'] = max([0.5,
                                                xsize * 2.5,
                                                ysize * 2.5])
                if t == 'RCOLLIMATOR' or t == "COLLIMATOR":
                    return _Builder.RCol(rname, l, xsize, ysize, **kws)
                else:
                    return _Builder.ECol(rname, l, xsize, ysize, **kws)
        # dict is incomplete or the component is erroneously
        # reffered to as a collimator even when it can be thought
        # of as a drift (e.g. LHC TAS).
        elif collimatordict != {}:
            msg = ("{} {} not found in collimatordict."
                   " Will instead convert to a DRIFT!  This is not"
                   " necessarily wrong!".format(t, name))
            _warnings.warn(msg)
            return _Builder.Drift(rname, l, **kws)
        # if user didn't provide a collimatordict at all.
        else:
            return _Builder.Drift(rname, l, **kws)
    elif t == 'RFCAVITY':
        return _Builder.Drift(rname, l, **kws)
    elif t == 'SEXTUPOLE':
        if zerolength or l < _THIN_ELEMENT_THRESHOLD:
            k2 = item['K2L'] * factor if not linear else 0
            return _Builder.ThinMultipole(rname, knl=(0, k2), **kws)
        k2 = item['K2L'] / l * factor if not linear else 0
        return _Builder.Sextupole(rname, l, k2, **kws)
    elif t == 'SOLENOID':
        if l == 0.0:
            msg = "{} is a thin solenoid and is omitted.".format(name)
            _warnings.warn(msg)
            return None
        ks = item['KSI'] / l
        return _Builder.Solenoid(rname, l, ks=ks, **kws)
    else:
        print('unknown element type:', t, 'for element named: ', name)
        if zerolength and not ignorezerolengthitems:
            print('putting marker in instead as its zero length')
            return _Builder.Marker(rname)
        print('putting drift in instead as it has a finite length')
        return _Builder.Drift(rname, l)

    raise ValueError("Unable to construct Element: {}, {}".format(t, name))

def _GetElementSplitByAperture(gmadElement, localApertures):
    # tolerate any bad apertures - like only a few - and just don't append them
    apertures = []
    for point, aper in localApertures:
        try:
            arp = _Builder.PrepareApertureModel(aper, warningName=gmadElement.name)
            apertures.append(arp)
        except ValueError:
            pass
        
    if localApertures[0][0] != 0.0 :
        raise ValueError("No aperture defined at start of element.")
    if len(localApertures) > 1:
        split_points = [point for point, _  in localApertures[1:]]
        split_elements = gmadElement.split(split_points)
        for aper, split_element in zip(apertures, split_elements):
            split_element.update(aper)
        return split_elements
    elif len(localApertures) == 1:
        gmadElement = _deepcopy(gmadElement)
        gmadElement.update(apertures[0])
        return [gmadElement]
    raise ValueError("Unable to split element by apertures.")

def _GetSingleElementWithAper(item, gmadElement,
                              aperturedict, defaultAperture):
    """Returns the raw aperture model (i.e. unsplit), and a list of
    split apertures."""
    gmadElement = _deepcopy(gmadElement)
    name = item["NAME"]
    # note SORIGINAL not S.  This is so it works still after slicing.
    sMid = item["SORIGINAL"] - item["L"] / 2.0
    aper = {}
    try:
        aper = _Builder.PrepareApertureModel(
            aperturedict.GetApertureAtS(sMid), defaultAperture)
    except AttributeError:
        pass
    try:
        this_aperdict = aperturedict[name]
    except KeyError:
        pass
    else:
        aper = _Builder.PrepareApertureModel(this_aperdict, defaultAperture)

    gmadElement.update(aper)
    return gmadElement


def MadxTfs2GmadBeam(tfs, startname=None, verbose=False, extraParamsDict={}):
    """
    Takes a pymadx.Data.Tfs instance and extracts information from first line to
    create a BDSIM beam definition in a pybdsim.Beam object.  Note
    that if kwarg startname is used, the optics are retrieved at the
    start of the element, i.e. you do not need to get the optics of
    the previous element, this function does that automatically.

    Works for e+, e- and proton.
    Default emittance is 1e-9mrad if 1 in tfs file.


    """
    print('Warning - using automatic generation of input beam distribution from madx tfs file - PLEASE CHECK!')

    if startname is None:
        startindex = 0
    else:
        try:
            startindex = tfs.IndexFromName(startname)
        except ValueError:  # Then assume it's already an index.
            startindex = startname

    # MADX defines parameters at the end of elements so need to go 1 element
    # back if we can.

    if startindex > 0:
        startindex -= 1

    energy = float(tfs.header['ENERGY'])
    particle = tfs.header['PARTICLE']
    ex = tfs.header['EX']
    ey = tfs.header['EY']
    if 'EX' in extraParamsDict:
        ex = extraParamsDict['EX']
    if 'EY' in extraParamsDict:
        ey = extraParamsDict['EY']
    sigmae = float(tfs.header['SIGE'])

    if ex == 1:
        print('Horizontal emittance of 1 is too large - setting to 1e-9')
        ex = 1e-9
    if ey == 1:
        print('Horizontal emittance of 1 is too large - setting to 1e-9')
        ey = 1e-9

    data = tfs[startindex]

    if particle == 'ELECTRON':
        particle = 'e-'
    elif particle == 'POSITRON':
        particle = 'e+'
    elif particle == 'PROTON':
        particle = 'proton'
    else:
        raise ValueError("Unsupported particle " + particle)

    if verbose:
        print('beta_x: ', data['BETX'], 'alpha_x: ', data['ALFX'], 'mu_x: ', data['MUX'])
        print('beta_y: ', data['BETY'], 'alpha_y: ', data['ALFY'], 'mu_y: ', data['MUY'])

    # note, in the main pybdsim.__init__.py Beam class is imported from Beam.py
    # so in this submodule when we do from .. import Beam it's actually the
    # already imported class that's being imported
    beam = _Beam.Beam(particle, energy, 'gausstwiss')
    if ex != 0:
        beam.SetEmittanceX(ex, 'm')
    if ey != 0:
        beam.SetEmittanceY(ey, 'm')
    beam.SetSigmaE(sigmae)

    beamparams = {"SetBetaX":'BETX',
                  "SetBetaY":'BETY',
                  "SetAlphaX":'ALFX',
                  "SetAlphaY":'ALFY',
                  "SetDispX":'DXBETA',
                  "SetDispY":'DYBETA',
                  "SetDispXP":'DPXBETA',
                  "SetDispYP":'DPYBETA',
                  "SetXP0": 'PX',
                  "SetYP0": 'PY',
                  "SetX0": 'X',
                  "SetY0": 'Y'
                  }
    for func,parameter in beamparams.items():
        if parameter in list(data.keys()):
            getattr(beam, func)(data[parameter])

    for k, v in extraParamsDict.items():
        beam[k] = v

    return beam
