def tidy(input):
    """
    | Tidy input, remove EOL, remove empty lines
    | input : list of file lines
    """
    output = []

    for l in input:
        l  = l.strip(' \n')  # tidy end of lines
        if len(l) == 0:      # strip empty lines
            continue 
        if l.find("RETURN") != -1:
            continue
        output.append(l)
    return output


def removeContinuationSymbols(input):
    """
    | Remove continuation symbols from input
    | input : list of file lines
    """
    output = []
    ml     = ''  # merged line

    # fine line continuations
    for l in input:
        ai = l.find('&') 
        
        if ai != -1:
            l = l.replace('&', '')
            ml = ml+l
        else:
            if len(ml) == 0:
                ml = l
            else:
                ml = ml+l
            output.append(ml)
            ml = ''

    return output


def removeComments(input):
    """
    | Remove comment lines
    | input : list of file lines
    """
    output = []

    for l in input:
        if l[0] == '!':
            continue 
        else:
            output.append(l)

    return output


def decodeFileLine(input):
    """
    | Decode line for each element type
    | input : string of a mad8 line
    """
    splitInput = input.split()
    
    for i in range(0, len(splitInput)):
        splitInput[i] = splitInput[i].strip(',')

    d = dict() 

    if len(splitInput) == 1:
        pass
    elif len(splitInput) > 1:
        type = splitInput[1].strip(',')
        if type == 'LINE':
            if len(splitInput) == 4:
                input = input.replace(',', ' ')
                splitInput = input.split()

            d = _decodeLine(splitInput)
        elif type == 'INSTRUMENT':
            d = _decodeNamed(splitInput)
        elif type == 'MONITOR':
            d = _decodeNamed(splitInput)
        elif type == 'WIRE':
            d = _decodeNamed(splitInput)
        elif type == 'MARKER':
            d = _decodeNamed(splitInput)
        elif type == 'PROFILE':
            d = _decodeNamed(splitInput)
        elif type == 'LCAVITY':
            d = _decodeLcavity(splitInput)
        elif type == 'DRIFT':
            d = _decodeDrift(splitInput)
        elif type == 'SBEND':
            d = _decodeSbend(splitInput)
        elif type == 'QUADRUPOLE':
            d = _decodeQuadrupole(splitInput)
        elif type == 'SEXTUPOLE':
            d = _decodeSextupole(splitInput)
        elif type == 'OCTUPOLE':
            d = _decodeOctupole(splitInput)
        elif type == 'DECAPOLE':
            d = _decodeDecapole(splitInput)
        elif type == 'MULTIPOLE':
            d = _decodeMultipole(splitInput)
        elif type == 'VKICKER':
            d = _decodeKicker(splitInput)
        elif type == 'HKICKER':
            d = _decodeKicker(splitInput)
        elif type == 'RCOLLIMATOR':
            d = _decodeCollimator(splitInput)
        elif type == 'ECOLLIMATOR':
            d = _decodeCollimator(splitInput)
        else:
            if len(splitInput) == 2:
                d = _decodeNamed(splitInput)
            else:
                d = _decodeLcavity(splitInput)

    return d


def _decodeLine(input):
    d = _decodeNameAndType(input)

    input[3] = input[3].replace('(', '')
    input[-1] = input[-1].replace(')', '')
    d['LINE'] = input[3:]    

    return d


def _decodeNamed(input):
    d = _decodeNameAndType(input)
    return d


def _decodeLcavity(input):
    d = _decodeNameAndType(input)
    for t in input[2:]:
        [key, val] = _splitKeyValue(t)
        d[key] = val
    return d


def _decodeDrift(input):
    d = _decodeNameAndType(input)
    for t in input[2:]:
        [key, val] = _splitKeyValue(t)
        d[key] = val
    return d


def _decodeSbend(input):
    d = _decodeNameAndType(input)
    for t in input[2:]:
        [key, val] = _splitKeyValue(t)
        d[key] = val
    return d    


def _decodeQuadrupole(input):
    d = _decodeNameAndType(input)
    for t in input[2:]:
        [key, val] = _splitKeyValue(t)
        d[key] = val
    return d


def _decodeSextupole(input):
    d = _decodeNameAndType(input)
    for t in input[2:]:
        [key, val] = _splitKeyValue(t)
        d[key] = val
    return d


def _decodeOctupole(input):
    d = _decodeNameAndType(input)
    for t in input[2:]:
        [key, val] = _splitKeyValue(t)
        d[key] = val
    return d


def _decodeDecapole(input):
    d = _decodeNameAndType(input)
    for t in input[2:]:
        [key, val] = _splitKeyValue(t)
        d[key] = val
    return d


def _decodeMultipole(input):
    d = _decodeNameAndType(input)
    for t in input[2:]:
        [key, val] = _splitKeyValue(t)
        d[key] = val
    return d


def _decodeKicker(input):
    d = _decodeNameAndType(input)
    for t in input[2:]:
        [key, val] = _splitKeyValue(t)
        d[key] = val
    return d


def _decodeCollimator(input):
    d = _decodeNameAndType(input)
    for t in input[2:]:
        [key, val] = _splitKeyValue(t)
        d[key] = val
    return d


def _decodeNameAndType(input):
    name = input[0].strip(':')
    type = input[1]
    d = dict()
    d['name'] = name
    d['type'] = type
    return d 


def _splitKeyValue(t):
    st = t.split('=')
    key   = st[0]
    value = float(st[1])

    return [key, value]
