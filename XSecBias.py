from numpy import arange as _arange
from re import split as _split

_allowedprocesses = [
    'eBrem',
    'eIoni',
    'msc',
    'all',
    'protonInelastic'
]

_allowedlvs = [
    'acceleratorVacuum',
    'acceleratorMaterial'
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
    def __init__(self, name, particle, processes, xsecfactors,flags, logicalvolume):
        self.name        = self.SetName(name)
        self.particle    = self.SetParticle(particle)
        self.processlist = self.SetProcessList(processes)
        self.flaglist    = self.SetFlagList(flags)
        self.xseclist    = self.SetXSecFactorList(xsecfactors)
        self.lvlist      = self.SetLogicalVolume(logicalvolume)
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
    
    def SetLogicalVolume(self, lv):
        if lv not  in _allowedlvs:
            raise ValueError("Unknown logical volume: " +str(lv))
        return lv
    
    def CheckBiasedProcesses(self):
        if (len(self.xseclist) != len(self.flaglist)) or (len(self.xseclist) != len(self.processlist)):
            raise Warning("There must be a uniquely defined flag and xsecfactor to go  with every listed process.")

    def _MapToString(self, argument):
        if (type(argument) == list) or (type(argument) == tuple):
            return map(str, argument)
        else:
            return str(argument)
        
    def __repr__(self):
        
        name = self.name + ': '

        particle = 'particle="' + self.particle + '", '

        #proc
        for index in _arange(len(self.processlist)):
            if len(self.processlist) == 1:
                proc = 'proc="' + str(self.processlist[0]) + '", '
            elif index == 0:
                proc = 'proc="' + str(self.processlist[index]) + ' '
            elif index == len(self.processlist) - 1:
                proc += self.processlist[index] + '", '
            else:
                proc += self.processlist[index] + ' '

        #xsec
        for index in _arange(len(self.xseclist)):
            if len(self.xseclist) == 1:
                xsec = 'xsecfact=' + str(self.xseclist[0]) + ', '
                break
            elif index == 0:
                xsec = 'xsecfact={' + str(self.xseclist[0]) + ','
            elif index == len(self.xseclist) - 1:
                xsec += str(self.xseclist[index]) + '}, '
            else:
                xsec += str(self.xseclist[index]) + ','
                
        #flag
        for index in _arange(len(self.flaglist)):
            if len(self.flaglist) == 1:
                flag = 'flag=' + str(self.flaglist[0]) + ', '
                break
            if index == 0:
                flag = 'flag={' +str(self.flaglist[index]) +','
            elif index == len(self.flaglist) - 1:
                flag += str(self.flaglist[index]) + '}, '
            else:
                flag += str(self.flaglist[index]) + ','
        
        #logicalvolume
        logicalvolume = 'logicalVolumes="'
        for lv in self.lvlist:
            logicalvolume += str(lv)
        logicalvolume += '"'

        s = name + "xsecBias, " + particle + proc + xsec + flag + logicalvolume + ';'
        
        return s

                             
#builder.py at the bottom writes the components.


