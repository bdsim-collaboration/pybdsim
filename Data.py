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
    data = BDSAsciiData()
    f = open(filepath, 'r')
    for i, line in enumerate(f):
        if line.startswith("#"):
            pass
        elif i == 1:
        # first line is header
            names,units = _ParseHeaderLine(line)
            for name,unit in zip(names,units):
                data._AddProperty(name,unit)
        else:
            data.append(tuple(map(float,line.split())))
    f.close()
    return data

def _LoadAsciiHistogram(filepath):
    data = BDSAsciiData()
    f = open(filepath,'r')
    for i, line in enumerate(f):
        # first line is header (0 counting)
        if i == 1:
            names,units = _ParseHeaderLine(line)
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

def _ParseHeaderLine(line):
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
                

class BDSAsciiData(list):
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
            a = BDSAsciiData()            #build bdsasciidata2
            a._DuplicateNamesUnits(self)   #copy names and units
            pindex = a.names.index(parametername)
            filtereddata = [event for event in self if abs(event[pindex]-matchvalue)<=tolerance]
            a.extend(filtereddata)
            return a
        else:
            print "The parameter: ",parametername," does not exist in this instance"

    def Filter(self,booleanarray):
        """
        Filter the data with a booleanarray.  Where true, will return
        that event in the data.

        Return type is BDSAsciiData
        """
        a = BDSAsciiData()
        a._DuplicateNamesUnits(self)
        a.extend([event for i,event in enumerate(self) if booleanarray[i]])
        return a

