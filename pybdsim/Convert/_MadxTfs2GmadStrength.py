from .. import Builder as _Builder
import pybdsim._General as _General
import _MadxTfs2Gmad
import pymadx as _pymadx
from pybdsim.Convert import _ZeroMissingRequiredColumns

_ElementModifier = _Builder.ElementModifier

def MadxTfs2GmadStrength(input, outputfilename,
                         existingmachine = None,
                         verbose         = False,
                         flipmagnets     = False,
                         linear          = False):
    """
    Use a MADX Tfs file containing full twiss information to generate a 
    strength (only) BDSIM GMAD file to be used with an existing lattice.
    
    +------------------+----------------------------------------------------------------+
    | existingmachine  | either a list or dictionary with names of elements to prepare. |
    +------------------+----------------------------------------------------------------+
    | flipmagnet       | similar behaviour to MAdxTfs2Gmad whether to flip k values for |
    |                  | negatively charged particles.                                  |
    +------------------+----------------------------------------------------------------+
    | linear           | only use linear strengths, k2 and higher set to 0.             |
    +------------------+----------------------------------------------------------------+

    """
    # ensure it's tfs instance and if not open the filepath provided
    madx = _pymadx.Data.CheckItsTfs(input)

    # Zero any missing required columns
    _ZeroMissingRequiredColumns(madx)

    if existingmachine == None:
        existingnames = madx.GetColumn('NAME')
    elif type(existingmachine) == list:
        existingnames = existingmachine
    elif type(existingmachine) == dict:
        existingnames = existingmachine.keys() #dictionary
    else:
        raise ValueError("Unsuitable type of existing machine")

    if verbose:
        madx.ReportPopulations()

    #existing machine can be a pybdsim.Builder.Machine instance or a list or a dictionary instance
    #but should contain the desired keys that strengths should be generated for from the Tfs file.

    newStrengths = []
    
    for item in madx:
        name  = item['NAME']
        rname = _General.PrepareReducedName(name) # the same as any normal conversion
        
        # generate elementmodifier with approprate name to match one
        # already used in existing machine
        if name in existingnames:
            a = _GenerateElementModifier(item, name, verbose, flipmagnets, linear)
        elif rname in existingnames:
            a = _GenerateElementModifier(item, rname, verbose, flipmagnets, linear)
        else:
            a = None
        if verbose:
            print a
        if a != None:
            newStrengths.append(a)

    #write output
    if not outputfilename.endswith('.gmad'):
        outputfilename += '.gmad'
    f = open(outputfilename, 'w')
    for strength in newStrengths:
        f.write(str(strength))
    f.close()


def _GenerateElementModifier(madxitem, nameToUse,
                             verbose     = False,
                             flipmagnets = False,
                             linear      = False):
    """
    Generate an Builder.ElementModifier instance based on the particular
    element / magnet type.  

    Takes second argument of nameToUse to match whatever the name as been
    changed to.

    This function doesn't do any key checking for the dictionary as that should
    be done by MadxTfs2GmadStrength
    """
    item = madxitem
    category = item['KEYWORD']

    l      = item['L']
    factor = -1 if flipmagnets else 1  #flipping magnets
    
    a = None
    if category == 'SOLENOID':
        newk0 = item['K0L'] / l  * factor 
        a = _ElementModifier(nameToUse, ks=newk0)
    elif category == 'QUADRUPOLE':
        newk1 = item['K1L'] / l * factor
        a = _ElementModifier(nameToUse, k1=newk1)
    elif category == 'SEXTUPOLE':
        newk2 = item['K2L'] / l * factor if not linear else 0
        a = _ElementModifier(nameToUse, k2=newk2)
    elif category == 'OCTUPOLE':
        newk3 = item['K3L'] / l * factor if not linear else 0
        a = _ElementModifier(nameToUse, k3=newk3)
    elif category == 'DECAPOLE':
        newk4 = item['K4L'] / l * factor if not linear else 0
        a = _ElementModifier(nameToUse, k4=newk4)
    elif category == 'HKICKER':
        a = _ElementModifier(nameToUse, angle=item['HKICK']*factor)
    elif category == 'VKICKER':
        a = _ElementModifier(nameToUse, angle=item['VKICK']*factor)
    elif category == 'TKICKER':
        if verbose:
            print 'WARNING - TKICKER not implemented yet'
    elif category == 'RFCAVITY':
        if verbose:
            print 'WARNING - RFCAVITY not implemented yet'
    elif category == 'MULTIPOLE':
        k1  = item['K1L']  * factor
        k2  = item['K2L']  * factor if not linear else 0
        k3  = item['K3L']  * factor if not linear else 0
        k4  = item['K4L']  * factor if not linear else 0
        k5  = item['K5L']  * factor if not linear else 0
        k6  = item['K6L']  * factor if not linear else 0
        k1s = item['K1SL'] * factor
        k2s = item['K2SL'] * factor if not linear else 0
        k3s = item['K3SL'] * factor if not linear else 0
        k4s = item['K4SL'] * factor if not linear else 0
        k5s = item['K5SL'] * factor if not linear else 0
        k6s = item['K6SL'] * factor if not linear else 0
        a = _ElementModifier(nameToUse, True, knl=(k1,k2,k3,k4,k5,k6), ksl=(k1s,k2s,k3s,k4s,k5s,k6s))
    else:
        pass # just keep a = None and return that

    if verbose:
        print 'New Strength: ',a
        if a == None:
            print 'Unsupported type: ',item['KEYWORD']
    
    return a
