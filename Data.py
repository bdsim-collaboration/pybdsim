# pybdsim.Data - output data loader for pybdsim
# Version 1.0
# L. Nevay, S.Boogert
# laurie.nevay@rhul.ac.uk

"""
Output

Read bdsim output

Classes:
Data - read various output files


"""
import numpy as _np
import Constants as _Constants

def Load(filepath):
    extension = filepath.split('.')[-1]
    if "elosshist" in filepath:
        return _LoadAsciiHistogram(filepath)
    elif "eloss" in filepath:
        return _LoadAscii(filepath)
    elif extension == 'txt':
        return _LoadAscii(filepath)
    elif extension == 'root':
        print 'Root loader not implemented yet...'
    else:
        raise IOError("Unknown file type - not BDSIM data")

def _LoadRoot(filepath):
    data = RootData()
    units = []
    keys  = []
    dataarray = _np.array([])
    f = open(filepath,'r')
    #stuff here
    f.close()
    return data,dataarray,keys,units

def _LoadAscii(filepath):
    data = BDSAsciiData2()
    f = open(filepath, 'r')
    for i, line in enumerate(f):
        if line.startswith("#"):
            pass
        elif i == 1:
        # first line is header
            names,units = ParseHeaderLine(line)
            for name,unit in zip(names,units):
                data._AddProperty(name,unit)
        else:
            data.append(tuple(map(float,line.split())))
    f.close()
    return data

def _LoadAsciiHistogram(filepath):
    data = BDSAsciiData2()
    f = open(filepath,'r')
    for i, line in enumerate(f):
        # first line is header (0 counting)
        if i == 1:
            names,units = ParseHeaderLine(line)
            for name,unit in zip(names,units):
                data._AddProperty(name,unit)
        elif "underflow" in line:
            print line
            print line.strip().split()[1]
            data.underflow = float(line.strip().split()[1])
        elif "overflow" in line:
            print line
            print line.strip().split()[1]
            data.overflow  = float(line.strip().split()[1])
        elif i >= 4:
            print line
            data.append(tuple(map(float,line.split())))
    f.close()
    return data

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
            return _np.array([event[ind] for event in self])
        setattr(self,variablename,GetAttribute)

    def _AddProperty(self,variablename,variableunit='NA'):
        """
        This is used to add a new variable and hence new getter function
        """
        self.names.append(variablename)
        self.units.append(variableunit)
        self._AddMethod(variablename)

    def _DuplicateNamesUnits(self,bdsasciidata2instance):
        d = bdsasciidata2instance
        for name,unit in zip(d.names,d.units):
            self._AddProperty(name,unit)

    def MatchValue(self,parametername,matchvalue,tolerance):
        """
        This is used to filter the instance of the class based on matching
        a parameter withing a certain tolerance.

        a = pybdsim.Data.Load("myfile.txt")
        MatchValue("S",0.3,0.0004)
        
        this will match the "S" variable in instance "a" to the value of 0.3
        within +- 0.0004.

        You can therefore used to match any parameter.

        Return type is BDSAsciiData
        """
        if hasattr(self,parametername):
            a = BDSAsciiData2()            #build bdsasciidata2
            a._DuplicateNamesUnits(self)   #copy names and units
            pindex = a.names.index(parametername)
            filtereddata = [event for event in self if abs(event[pindex]-matchvalue)<=tolerance]
            a.extend(filtereddata)
            return a
        else:
            print "The parameter: ",parametername," does not exist in this instance"

    def Filter(self,booleanarray):
        a = BDSAsciiData2()
        """
        Filter the data with a booleanarray.  Where true, will return
        that event in the data.

        Return type is BDSAsciiData
        """
        a._DuplicateNamesUnits(self)
        a.extend([event for i,event in enumerate(self) if booleanarray[i]])
        return a

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
