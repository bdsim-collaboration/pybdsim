# pybdsim.Data - output data loader for pybdsim
# Version 1.0
# L. Nevay
# laurie.nevay@rhul.ac.uk

"""
Output

Read bdsim output

Classes:
Data - read various output files


"""

import numpy as _np
import Constants as _Constants

class AsciiData(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self)
        self._Update(*args, **kwargs)
        self._UpdateKeys()
        self.units = {}
        
    def _Update(self, *args, **kwargs):
        for k,v in dict(*args,**kwargs).iteritems():
            self[k] = v
    
    def SetUnits(self,unitsdict):
        self.unitsdict = unitsdict
        
    def _UpdateKeys(self):
        self.keyslist = self.keys()

    def __setitem__(self,key,value):
        dict.__setitem__(self,key,value)
        self._UpdateKeys()

def LoadOld(filepath):
    knownfiletypes = ['txt','root']
    format = filepath.split('.')[-1]
    if format not in knownfiletypes:
        print 'pybdsim.Data.Load - unknown format'
    elif filepath.count('eloss') > 0 :
        data,dataarray,keys,units = _LoadAscii3(filepath)
    elif format == 'txt':
        data,dataarray,keys,units = _LoadAscii2(filepath)
    elif format == 'root':
        data,dataarray,keys,units = _LoadRoot(filepath)
    return data,dataarray,keys

def ParseKeys(keyline):
    rawkeys    = keyline.split()[1:]
    keys  = []
    units = []
    #remove units from keys
    for i,key in enumerate(rawkeys):
        if key.count('[') > 0:
            unit   = key.split('[')[1].split(']')[0].replace('mu','$\mu$')
            newkey = key.split('[')[0] 
            keys.append(newkey)
            units.append(unit)
        else:
            keys.append(key)
            units.append('NA')
    return keys,units

def _LoadAscii(filepath):
    data = AsciiData()
    f = open(filepath,'r')
    datalist = []
    for i, line in enumerate(f):
        if i < 2:
            pass
        elif i == 2:
            keys,units = ParseKeys(line)
        else:
            datalist.append(map(float,line.split()))
    f.close()
    dataarray = _np.array(datalist)
    del datalist
    for i,key in enumerate(keys):
        data[key] = list(dataarray[:,i])
    data.SetUnits(dict(zip(keys,units)))
    return data,dataarray,keys,units
    
def _LoadRoot(filepath):
    data = RootData()
    units = []
    keys  = []
    dataarray = _np.array([])
    f = open(filepath,'r')
    #stuff here
    f.close()
    return data,dataarray,keys,units
    
def _LoadAscii2(filepath):
    data = BDSAsciiData()
    f = open(filepath,'r')
    newdata = False
    for i, line in enumerate(f):
        # first 3 lines are header
        if i > 2:
            data.append(tuple(map(float,line.split())))
            #data.append(tuple(map(float,line.split()[1:])+[line.split()[0]]))
    f.close()
    data._MakeSamplerIndex()
    return data

def _LoadAscii3(filepath):
    data = BDSAsciiData2()
    f = open(filepath, 'r')
    for i, line in enumerate(f):
        # first line is header
        if i == 1:
            names,units = ParseHeaderLine(line)
            for name,unit in zip(names,units):
                data._AddProperty(name,unit)
        if i > 1:
            data.append(tuple(map(float,line.split())))
    f.close()
    return data

def Load(filepath):
    extension = filepath.split('.')[-1]
    if filepath.count('eloss') > 0:
        return _LoadAscii3(filepath)
    elif extension == 'txt':
        return _LoadAscii3(filepath)
    elif extension == 'root':
        print 'Root loader not implemented yet...'
    else:
        raise IOError("Unknown file type - not BDSIM data")

def ParseHeaderLine(line):
    names = []
    units = []
    for word in line.split():
        if word.count('[') > 0:
            names.append(word.split('[')[0])
            units.append(word.split('[')[1].strip(']'))
        else:
            names.append(word)
            units.append('NA')
    return names, units
                

class BDSAsciiData2(list):
    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)
        self.units = []
        self.names = []

    def _AddMethod(self, variablename):
        """
        This is used to dynamically add a getter function for a variable name.
        """
        def GetAttribute():
            if self.names.count(variablename) == 0:
                raise KeyError(variablename+" is not a variable in this data")
            ind = self.names.index(variablename)
            return [event[ind] for event in self]
        setattr(self,variablename,GetAttribute)

    def _AddProperty(self,variablename,variableunit='NA'):
        """
        This is used to add a new variable and hence new getter function
        """
        self.names.append(variablename)
        self.units.append(variableunit)
        self._AddMethod(variablename)

class BDSAsciiData(list):
    """
    BDSAsciiData class (OBSELETE - only kept for sampler Z grouping)

    Inherits python list class

    callable with arguments (particletype='all', samplerindex='all')

    eg.
    a = pyBdsim.Data.Load('path/to/file.txt') #returns BDSAsciiData instance

    a('electron',0) # returns electrons at sampler number 0
    a('all',12)     # returns all partcles at sampler number 12
    a(11,0)         # returns electrons (PDGid=11) at sampler number 0

    see pyBdsim.Constants.PDGid for names
     
    """
    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)
        self.names = ['PT', 'E',   'X',      'Y',      'Z', 'Xp',  'Yp',  'NEvent', 'Weight', 'ParentID', 'TrackID']
        self.units = ['NA', 'GeV', '$\mu$m', '$\mu$m', 'm', 'rad', 'rad', 'NA',     'NA',     'NA',       'NA']
        self._zr   = 3 #z grouping tolerance in decimal places
        self._MakeSamplerIndex()
        
    def _MakeSamplerIndex(self):
        self.samplerzs = sorted(list(set([round(x[self.names.index('Z')],self._zr) for x in self])))
        
    def SamplerIndex(self,zlocation):
        if zlocation not in self.samplerzs:
            raise ValueError("zlocation does not match any sampler")
        else:
            return self.samplerzs.index(zlocation)

    def __call__(self,particletype='all', samplerindex='all'):
        if particletype != 'all':
            if type(particletype) == str:
                pt = _Constants.GetPDGInd(particletype)
            else:
                pt = particletype
        if samplerindex != 'all':
            samplerz = self.samplerzs[samplerindex]
        
        ptind   = self.names.index('PT')
        zind    = self.names.index('Z')
        
        if (particletype != 'all'):
            df = filter(lambda event: event[ptind] == pt, self)
        else:
            df = self
        if samplerindex != 'all':
            df      = filter(lambda event: round(event[zind],self._zr) == samplerz, df)
        return BDSAsciiData(df)
        
    def __repr__(self):
        return '('+', '.join(self.names)+')'

    def ParticleType(self):
        ind = self.names.index('PT')
        return [e[ind] for e in self]
    
    def E(self):
        ind = self.names.index('E')
        return [e[ind] for e in self]
        
    def X(self):
        ind = self.names.index('X')
        return [e[ind] for e in self]
        
    def Y(self):
        ind = self.names.index('Y')
        return [e[ind] for e in self]
        
    def Z(self):
        ind = self.names.index('Z')
        return [e[ind] for e in self]
        
    def Xp(self):
        ind = self.names.index('Xp')
        return [e[ind] for e in self]
        
    def Yp(self):
        ind = self.names.index('Yp')
        return [e[ind] for e in self]
        
    def NEvent(self):
        ind = self.names.index('NEvent')
        return [e[ind] for e in self]
        
    def Weight(self):
        ind = self.names.index('Weight')
        return [e[ind] for e in self]
        
    def ParentID(self):
        ind = self.names.index('ParentID')
        return [e[ind] for e in self]
        
    def TrackID(self):
        ind = self.names.index('TrackID')
        return [e[ind] for e in self]
