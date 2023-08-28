from .. import Builder as _Builder
import pybdsim._General as _General
import pybdsim.Data as _Data

_ElementModifier = _Builder.ElementModifier

def ElegantParam2GmadStrength(paramfile, outputfilename,
                              existingmachine = None,
                              verbose         = False,
                              flipmagnets     = False,
                              linear          = False,
                              ignoreZeroLengthItems = True):
    """
    Use an Elegant 'parameters' file containing details about each component to generate a 
    strength (only) BDSIM GMAD file to be used with an existing lattice.
    
    +------------------+----------------------------------------------------------------+
    | existingmachine  | either a list or dictionary with names of elements to prepare. |
    +------------------+----------------------------------------------------------------+
    | flipmagnet       | whether to flip k values for  negatively charged particles.    |
    +------------------+----------------------------------------------------------------+
    | linear           | only use linear strengths, k2 and higher set to 0.             |
    +------------------+----------------------------------------------------------------+

    """
    params = _Data.LoadSDDSColumnsToDict(paramfile)
    paramsd = _Data.SDDSBuildParameterDicts(params)

    if existingmachine == None:
        existingnames = []
    elif type(existingmachine) == list:
        existingnames = existingmachine
    elif type(existingmachine) == dict:
        existingnames = list(existingmachine.keys()) #dictionary
    else:
        raise ValueError("Unsuitable type of existing machine")

    newStrengths = []

    for name,paramDict in paramsd.items():
        if _WillIgnoreItem(paramDict, ignoreZeroLengthItems):
            continue
        
        # remove special characters like $, % etc 'reduced' name - rname:
        rname = _General.PrepareReducedName2(name)

        # generate elementmodifier with approprate name to match one
        # already used in existing machine
        nameToUse = name if name in existingnames else rname
        a = _GenerateElementModifier(paramDict, nameToUse, verbose, flipmagnets, linear)
        
        if verbose:
            print(a)
        if a != None:
            newStrengths.append(a)

    #write output
    if not outputfilename.endswith('.gmad'):
        outputfilename += '.gmad'
    f = open(outputfilename, 'w')
    for strength in newStrengths:
        f.write(str(strength))
    f.close()


def _GenerateElementModifier(item, nameToUse, verbose=False, flipmagnets=False, linear=False):
    """
    Generate an Builder.ElementModifier instance based on the particular
    element / magnet type.  

    Takes second argument of nameToUse to match whatever the name as been
    changed to.

    This function doesn't do any key checking for the dictionary as that should
    be done by MadxTfs2GmadStrength
    """
    category = item['KEYWORD']
    factor   = -1 if flipmagnets else 1  #flipping magnets
    
    a = None
    if category == 'KQUAD':
        newk1 = item['K1'] * factor
        a = _ElementModifier(nameToUse, k1=newk1)
    else:
        pass # just keep a = None and return that

    #TBC for other types

    if verbose:
        print(('New Strength: ', a))
        if a is None:
            print(('Unsupported type: ', category))
    
    return a


def _WillIgnoreItem(paramDict, ignoreZeroLengthItems=False, ignoreableThinElements=[]):
    kw = paramDict['KEYWORD']

    if kw in ['CHARGE', 'ENERGY', 'FLOOR', 'MALIGN', 'MARK', 'MONI', 'WATCH']:
        return True
    else:
        if 'L' in paramDict:
            l = paramDict['L']
            zeroLength = l < 1e-9
            if zeroLength and ignoreZeroLengthItems:
                return True
            if zeroLength and kw in ignoreableThinElements:
                return True
    return False
        
