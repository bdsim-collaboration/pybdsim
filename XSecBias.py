from numpy import arange as _arange
from re import split as _split

_allowedprocesses = [
    'eBrem',
    'eIoni',
    'msc',
    'all',
    'protonInelastic'
]

_allowedparticles = [
    'e-',
    'e+',
    'proton',
    'gamma'
]

_allowedflags = [
    '1',
    '2',
    '3'
]


class XSecBias(object):
    """ 
    A class for containing all information regarding cross section definitions.
    """
    def __init__(self, name, particle, processes, xsecfactors, flags):
        self.name        = self.SetName(name)
        self.particle    = self.SetParticle(particle)
        self.processlist = self.SetProcessList(processes)
        self.flaglist    = self.SetFlagList(flags)
        self.xseclist    = self.SetXSecFactorList(xsecfactors)
        self.CheckBiasedProcesses()
    
    def SetName(self, name):
        if name.lower() == 'xsecbias':
            raise ValueError("Forbidden name: "+ str(name) +".  Bias name cannot be any variant of 'xsecbias' (case insensitive)")
        return name
    
    def SetParticle(self, particle):
        if particle  in _allowedparticles:
            return particle
        else:
            raise ValueError("Unknown Particle type: " + str(particle) + ".")
    
    def SetProcessList(self, processes):
        processlist = _split(', |,| ', processes)

        # as we don't have a complete list just now, prevent this checking.
        return processlist

        if ('all' in processlist) and (len(processlist) > 1):
            raise Warning("You cannot have both all and another process to be biased.")
        for process in processlist:
            if process not in _allowedprocesses:
                raise ValueError("Unknown process type: " + str(process))
        return processlist

    
    def SetFlagList(self, flag):
        flag = self._MapToString(flag)
        flaglist = _split(', |,| ',flag)
        for number in flaglist:
            if number not in _allowedflags:
                raise ValueError("Unknown Flag type: " + str(number))
        return flaglist
    
    def SetXSecFactorList(self, xsec):
        xsec = self._MapToString(xsec)
        xseclist = _split(', |,| ', xsec)
        for factor in xsec:
            if factor < 0:
                raise ValueError("Negative cross section factor: " +str(factor))
        return xseclist
    
    def CheckBiasedProcesses(self):
        if (len(self.xseclist) != len(self.flaglist)) or (len(self.xseclist) != len(self.processlist)):
            raise Warning("There must be a uniquely defined flag and xsecfactor to go  with every listed process.")

    def _MapToString(self, argument):
        if (type(argument) == list) or (type(argument) == tuple):
            return map(str, argument)
        else:
            return str(argument)
        
    def __repr__(self):
        particle = 'particle="' + self.particle + '"'
        proc     = 'proc="' + ' '.join(map(str, self.processlist)) + '"'
        xsec     = 'xsecfact={' + ','.join(map(str, self.xseclist)) + '}'
        flag     = 'flag={' + ','.join(map(str,self.flaglist)) + '}'

        s = self.name + ": xsecBias, " + ', '.join([particle,proc,xsec,flag]) + ';\n'
        
        return s


