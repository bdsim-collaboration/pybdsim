"""
Output loading

Read bdsim output

Classes:
Data - read various output files

"""
import Constants as _Constants
import _General

import glob as _glob
import numpy as _np
import os as _os

_useRoot      = True
_useRootNumpy = True
_libsLoaded   = False

try:
    import root_numpy as _rnp
except ImportError:
    _useRootNumpy = False
    pass

try:
    import ROOT as _ROOT
except ImportError:
    _useRoot = False
    pass

def _LoadROOTLibraries():
    """
    Load root libraries. Only works once to prevent errors.
    """
    global _libsLoaded
    if _libsLoaded:
        return #only load once
    try:
        import ROOT as _ROOT
    except ImportError:
        raise Warning("ROOT in python not available")
    bdsLoad = _ROOT.gSystem.Load("libbdsimRootEvent")
    reLoad  = _ROOT.gSystem.Load("librebdsim")
    if reLoad is not 0:
        raise Warning("librebdsim not found")
    if bdsLoad is not 0:
        raise Warning("libbdsimRootEvent not found")
    _libsLoaded = True

def Load(filepath):
    """
    Load the data with the appropriate loader.

    ASCII file   - returns BDSAsciiData instance.
    BDSIM file   - uses ROOT, returns BDSIM DataLoader instance.
    REBDISM file - uses ROOT, returns RebdsimFile instance.

    """
    extension = filepath.split('.')[-1]
    if ("elosshist" in filepath) or (".hist" in filepath):
        return _LoadAsciiHistogram(filepath)
    elif "eloss" in filepath:
        return _LoadAscii(filepath)
    elif extension == 'txt':
        return _LoadAscii(filepath)
    elif extension == 'root':
        return _LoadRoot(filepath)
        try:
            return _LoadRoot(filepath)
        except NameError:
            #raise error rather than return None, saves later scripting errors.
            raise IOError('Root loader not available.')
    elif extension == 'dat':
        print '.dat file - trying general loader'
        try:
            return _LoadAscii(filepath)
        except:
            print "Didn't work"
            raise IOError("Unknown file type - not BDSIM data")
    else:
        raise IOError("Unknown file type - not BDSIM data")

def _LoadAscii(filepath):
    data = BDSAsciiData()
    data.filename = filepath
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
            #this tries to cast to float, but if not leaves as string
            data.append(tuple(map(_General.Cast,line.split())))
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
        elif "nderflow" in line:
            data.underflow = float(line.strip().split()[1])
        elif "verflow" in line:
            data.overflow  = float(line.strip().split()[1])
        elif i >= 4:
            data.append(tuple(map(float,line.split())))
    f.close()
    return data

def _ROOTFileType(filepath):
    """
    Determine BDSIM file type by loading header and extracting fileType.
    """
    files = _glob.glob(filepath) # works even if just 1 file
    try:
        fileToCheck = files[0] # just check first file
    except IndexError:
        raise IOError("File(s) not found.")
    f = _ROOT.TFile(fileToCheck)
    htree = f.Get("Header")
    if not htree:
        raise Warning("ROOT file is not a BDSIM one")
    h = _ROOT.Header()
    h.SetBranchAddress(htree)
    htree.GetEntry(0)
    result = str(h.header.fileType)
    f.Close()
    return result

def _LoadRoot(filepath):
    """
    Inspect file and check it's a BDSIM file of some kind and load.
    """
    if not _useRoot:
        raise IOError("ROOT in python not available - can't load ROOT file")
    if not _useRootNumpy:
        raise IOError("root_numpy not available - can't load ROOT file")

    _LoadROOTLibraries()
    
    fileType = _ROOTFileType(filepath) #throws warning if not a bdsim file

    if fileType == "BDSIM":
        print 'BDSIM output file - using DataLoader'
        d = _ROOT.DataLoader(filepath)
        return d # just return the DataLoader instance
    elif fileType == "REBDSIM":
        print 'REBDSIM analysis file - using RebdsimFile'
        return RebdsimFile(filepath)
    elif fileType == "REBDSIMCOMBINE":
        print 'REBDSIMCOMBINE analysis file - using RebdsimFile'
        return RebdsimFile(filepath)
    else:
        raise IOError("This file type "+fileType+" isn't supported")

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

class RebdsimFile(object):
    """
    Class to represent data in rebdsim output file.

    Contains histograms as root objects. Conversion function converts
    to pybdsim.Rebdsim.THX classes holding numpy data.

    If optics data is present, this is loaded into self.Optics which is
    BDSAsciiData instance.

    If convert=True (default), root histograms are automatically converted
    to classes provided here with numpy data.
    """
    def __init__(self, filename, convert=True):
        _LoadROOTLibraries()
        self.filename = filename
        self._f = _ROOT.TFile(filename)
        self.histograms   = {}
        self.histograms1d = {}
        self.histograms2d = {}
        self.histograms3d = {}
        dirs = self.ListOfDirectories()
        self._Map("", self._f)
        if convert:
            self.ConvertToPybdsimHistograms()

        def _prepare_data(branches, treedata):
            data = BDSAsciiData()
            data.filename = self.filename
            for element in range(len(treedata[branches[0]])):
                elementlist=[]
                for branch in branches:
                    if element == 0:
                        data._AddProperty(branch)
                    elementlist.append(treedata[branch][element])
                data.append(elementlist)
            return data

        trees = _rnp.list_trees(self.filename)            
        if 'Optics' in trees:
            branches = _rnp.list_branches(self.filename,'Optics')
            treedata = _rnp.root2array(self.filename,'Optics')
            self.Optics = _prepare_data(branches, treedata)
        if 'Orbit' in trees:
            branches = _rnp.list_branches(self.filename, 'Orbit')
            treedata = _rnp.root2array(self.filename, 'Orbit')
            self.orbit = _prepare_data(branches, treedata)

    def _Map(self, currentDirName, currentDir):
        h1d = self._ListType(currentDir, "TH1D")
        h2d = self._ListType(currentDir, "TH2D")
        h3d = self._ListType(currentDir, "TH3D")
        for h in h1d:
            name = currentDirName + '/' + h
            name = name.strip('/') # protect against starting /
            hob = currentDir.Get(h)
            self.histograms[name] = hob
            self.histograms1d[name] = hob
        for h in h2d:
            name = currentDirName + '/' + h
            name = name.strip('/') # protect against starting /
            hob = currentDir.Get(h)
            self.histograms[name] = hob
            self.histograms2d[name] = hob
        for h in h3d:
            name = currentDirName + '/' + h
            name = name.strip('/') # protect against starting /
            hob = currentDir.Get(h)
            self.histograms[name] = hob
            self.histograms3d[name] = hob
        subDirs = self._ListType(currentDir, "Directory")
        for d in subDirs:
            dName = currentDirName + '/' + d
            dName = dName.strip('/') # protect against starting /
            dob = currentDir.Get(d)
            self._Map(dName, dob)      

    def _ListType(self, ob, typeName):
        keys = ob.GetListOfKeys()
        result = []
        for i in range(keys.GetEntries()):
            if typeName in keys.At(i).GetClassName():
                result.append(keys.At(i).GetName())
        return result
    
    def ListOfDirectories(self):
        """
        List all directories inside the root file.
        """
        return self._ListType(self._f, 'Directory')

    def ListOfTrees(self):
        """
        List all trees inside the root file.
        """
        return self._ListType(self._f, 'Tree')

    def ConvertToPybdsimHistograms(self):
        """
        Convert all root histograms into numpy arrays.
        """
        self.histogramspy = {}
        self.histograms1dpy = {}
        self.histograms2dpy = {}
        self.histograms3dpy = {}
        for path,hist in self.histograms1d.iteritems():
            hpy = TH1(hist)
            self.histograms1dpy[path] = hpy
            self.histogramspy[path] = hpy
        for path,hist in self.histograms2d.iteritems():
            hpy = TH2(hist)
            self.histograms2dpy[path] = hpy
            self.histogramspy[path] = hpy
        for path,hist in self.histograms3d.iteritems():
            hpy = TH3(hist)
            self.histograms3dpy[path] = hpy
            self.histogramspy[path] = hpy

class BDSAsciiData(list):
    """
    General class representing simple 2 column data.

    Inherits python list.  It's a list of tuples with extra columns of 'name' and 'units'.
    """
    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)
        self.units   = []
        self.names   = []
        self.columns = self.names
        self._columnsLower = map(str.lower, self.columns)
        self.filename = "" # file data was loaded from

    def __getitem__(self,index):
        if type(index) is str:
            nameCol = map(str.lower, self.GetColumn('name', ignoreCase=True))
            index = nameCol.index(index.lower())
        return dict(zip(self.names,list.__getitem__(self,index)))

    def GetItemTuple(self,index):
        """
        Get a specific entry in the data as a tuple of values rather than a dictionary.
        """
        return list.__getitem__(self,index)
        
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

    def ConcatenateMachine(self, *args):
        """
        Add 1 or more data instances to this one - suitable only for things that
        could be loaded by this class. Argument can be one or iterable. Either
        of str type or this class.
        """
        #Get final position of the machine (different param for survey)
        if _General.IsSurvey(self):
            lastSpos = self.GetColumn('SEnd')[-1]
        else:
            lastSpos = self.GetColumn('S')[-1]
        
        for machine in args:
            if isinstance(machine,_np.str):
                machine = Load(machine)
        
            #check names sets are equal
            if len(set(self.names).difference(set(machine.names))) != 0:
                raise AttributeError("Cannot concatenate machine, variable names do not match")
        
            #surveys have multiple s positions per element
            if _General.IsSurvey(machine):
                sstartind = self.names.index('SStart')
                smidind = self.names.index('SMid')
                sendind = self.names.index('SEnd')
            elif self.names.count('S') != 0:
                sind = self.names.index('S')
            else:
                raise KeyError("S is not a variable in this data")
        
            #Have to convert each element to a list as tuples can't be modified
            for index in range(len(machine)):
                element = machine.GetItemTuple(index)
                elementlist = list(element)
                
                #update the elements S position
                if _General.IsSurvey(machine):
                    elementlist[sstartind] += lastSpos
                    elementlist[smidind] += lastSpos
                    elementlist[sendind] += lastSpos
                else:
                    elementlist[sind] += lastSpos
                
                self.append(tuple(elementlist))
                
            #update the total S position.
            if _General.IsSurvey(machine):
                lastSpos += machine.GetColumn('SEnd')[-1]
            else:
                lastSpos += machine.GetColumn('S')[-1]


    def _AddProperty(self,variablename,variableunit='NA'):
        """
        This is used to add a new variable and hence new getter function
        """
        self.names.append(variablename)
        self._columnsLower.append(variablename.lower())
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

        >>> a = pybdsim.Data.Load("myfile.txt")
        >>> a.MatchValue("S",0.3,0.0004)
        
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

    def NameFromNearestS(self,S):
        i = self.IndexFromNearestS(S)
        return self.Name()[i]
    
    def IndexFromNearestS(self,S) : 
        """
        IndexFromNearestS(S) 

        return the index of the beamline element clostest to S 

        Only works if "SStart" column exists in data
        """
        #check this particular instance has the required columns for this function
        if not hasattr(self,"SStart"):
            raise ValueError("This file doesn't have the required column SStart")
        if not hasattr(self,"ArcLength"):
            raise ValueError("This file doesn't have the required column Arc_len")
        s = self.SStart()
        l = self.ArcLength()

        #iterate over beamline and record element if S is between the
        #sposition of that element and then next one
        #note madx S position is the end of the element by default
        ci = [i for i in range(len(self)-1) if (S > s[i] and S < s[i]+l[i])]
        try:
            ci = ci[0] #return just the first match - should only be one
        except IndexError:
            #protect against S positions outside range of machine
            if S > s[-1]:
                ci =-1
            else:
                ci = 0
        #check the absolute distance to each and return the closest one
        #make robust against s positions outside machine range
        return ci

    def GetColumn(self,columnstring, ignoreCase=False):
        """
        Return a numpy array of the values in columnstring in order
        as they appear in the beamline
        """
        ind = 0
        if ignoreCase:
            try:
                ind = self._columnsLower.index(columnstring.lower())
            except:
                raise ValueError("Invalid column name")
        else:
            if columnstring not in self.columns:
                raise ValueError("Invalid column name")
            else:
                ind = self.names.index(columnstring)
        return _np.array([element[ind] for element in self])

    def __repr__(self):
        s = ''
        s += 'pybdsim.Data.BDSAsciiData instance\n'
        s += str(len(self)) + ' entries'
        return s

    def __contains__(self, obj):
        nameAvailable = 'name' in self._columnsLower
        if type(obj) is str and nameAvailable:
            return obj in self.GetColumn('name',ignoreCase=True)
        else:
            return False        

class ROOTHist(object):
    """
    Base class for histogram wrappers.
    """
    def __init__(self, hist):
        self.hist = hist
        self.name   = hist.GetName()
        self.title  = hist.GetTitle()
        self.xlabel = hist.GetXaxis().GetTitle()
        self.ylabel = hist.GetYaxis().GetTitle()

class TH1(ROOTHist):
    """
    Wrapper for a ROOT TH1 instance. Converts to numpy data.

    >>> h = file.Get("histogramName")
    >>> hpy = TH1(h)
    """
    def __init__(self, hist, extractData=True):
        super(TH1, self).__init__(hist)
        self.nbinsx     = hist.GetNbinsX()
        self.entries    = hist.GetEntries()
        self.xwidths    = _np.zeros(self.nbinsx)
        self.xcentres   = _np.zeros(self.nbinsx)
        self.xlowedge   = _np.zeros(self.nbinsx)
        self.xhighedge  = _np.zeros(self.nbinsx)

        # data holders
        self.contents  = _np.zeros(self.nbinsx)
        self.errors    = _np.zeros(self.nbinsx)
        self.xunderflow = hist.GetBinContent(0)
        self.xoverflow  = hist.GetBinContent(self.nbinsx+1)      

        for i in range(self.nbinsx):
            xaxis = hist.GetXaxis()
            self.xwidths[i]   = xaxis.GetBinWidth(i)
            self.xlowedge[i]  = xaxis.GetBinLowEdge(i+1)
            self.xhighedge[i] = xaxis.GetBinLowEdge(i+1)
            self.xcentres[i]  = xaxis.GetBinCenter(i+1)

        if extractData:
            self._GetContents()

    def _GetContents(self):
        for i in range(self.nbinsx):
            self.contents[i] = self.hist.GetBinContent(i+1)
            self.errors[i]   = self.hist.GetBinError(i+1)

class TH2(TH1):
    """
    Wrapper for a ROOT TH2 instance. Converts to numpy data.

    >>> h = file.Get("histogramName")
    >>> hpy = TH2(h)
    """
    def __init__(self, hist, extractData=True):
        super(TH2, self).__init__(hist, False)
        self.nbinsy    = hist.GetNbinsY()
        self.ywidths   = _np.zeros(self.nbinsy)
        self.ycentres  = _np.zeros(self.nbinsy)
        self.ylowedge  = _np.zeros(self.nbinsy)
        self.yhighedge = _np.zeros(self.nbinsy)

        self.contents = _np.zeros((self.nbinsx,self.nbinsy))
        self.errors   = _np.zeros((self.nbinsx,self.nbinsy))

        for i in range(self.nbinsy):
            yaxis = hist.GetYaxis()
            self.ywidths[i]   = yaxis.GetBinWidth(i+1)
            self.ylowedge[i]  = yaxis.GetBinLowEdge(i+1)
            self.yhighedge[i] = yaxis.GetBinLowEdge(i+2)
            self.ycentres[i]  = yaxis.GetBinCenter(i+1)

        if extractData:
            self._GetContents()   
        
    def _GetContents(self):
        for i in range(self.nbinsx) :
            for j in range(self.nbinsy) :
                self.contents[i,j] = self.hist.GetBinContent(i+1,j+1)
                self.errors[i,j]   = self.hist.GetBinError(i+1,j+1)

class TH3(TH2):
    """
    Wrapper for a ROOT TH3 instance. Converts to numpy data.

    >>> h = file.Get("histogramName")
    >>> hpy = TH3(h)
    """
    def __init__(self, hist, extractData=True):
        super(TH3, self).__init__(hist, False)
        self.zlabel    = hist.GetZaxis().GetTitle()
        self.nbinsz    = hist.GetNbinsZ()
        self.zwidths   = _np.zeros(self.nbinsz)
        self.zcentres  = _np.zeros(self.nbinsz)
        self.zlowedge  = _np.zeros(self.nbinsz)
        self.zhighedge = _np.zeros(self.nbinsz)

        self.contents = _np.zeros((self.nbinsx,self.nbinsy,self.nbinsz))
        self.errors   = _np.zeros((self.nbinsx,self.nbinsy,self.nbinsz))

        for i in range(self.nbinsz):
            zaxis = hist.GetZaxis()
            self.zwidths[i]   = zaxis.GetBinWidth(i+1)
            self.zlowedge[i]  = zaxis.GetBinLowEdge(i+1)
            self.zhighedge[i] = zaxis.GetBinLowEdge(i+2)
            self.zcentres[i]  = zaxis.GetBinCenter(i+1)

        if extractData:
            self._GetContents()   
        
    def _GetContents(self):
        for i in range(self.nbinsx):
            for j in range(self.nbinsy):
                for k in range(self.nbinsz):
                    self.contents[i,j,k] = self.hist.GetBinContent(i+1,j+1,k+1)
                    self.errors[i,j,k]   = self.hist.GetBinError(i+1,j+1,k+1)
                    

class _SamplerData(object):
    """
    Base class for loading a chosen set of sampler data from a file.
    data - is the DataLoader instance.
    params - is a list of parameter names as strings.
    samplerIndexOrName - is the index of the sampler (0=primaries) or name.

    """
    def __init__(self, data, params, samplerIndexOrName=0):        
        self._et           = data.GetEventTree()
        self._ev           = data.GetEvent()
        self._samplerNames = list(data.GetSamplerNames())
        self._samplerNames.insert(0,'Primary')
        self._samplers     = list(self._ev.Samplers)
        self._samplers.insert(0,self._ev.GetPrimaries())
        self._entries      = int(self._et.GetEntries())

        if type(samplerIndexOrName) == str:
            try:
                self.samplerIndex = self._samplerNames.index(samplerIndexOrName)
            except ValueError:
                self.samplerIndex = self._samplerNames.index(samplerIndexOrName+".")
        else:
            self.samplerIndex = samplerIndexOrName   
        
        self.samplerName = self._samplerNames[self.samplerIndex]
        self.data        = self._GetVariables(self.samplerIndex, params)

    def _SamplerIndex(self, samplerName):
        try:
            return self._samplerNames.index(samplerName)
        except ValueError:
            raise ValueError("Invalid sampler name")
        
    def _GetVariable(self, samplerIndex, var):
        result = []
        s = self._samplers[samplerIndex]
        for i in range(self._entries):
            self._et.GetEntry(i)
            v = getattr(s, var)
            try:
                res = list(v)
            except TypeError:
                res = list([v])
            result.extend(res)

        return _np.array(result)

    def _GetVariables(self, samplerIndex, vs):
        result = {v:[] for v in vs}
        s = self._samplers[samplerIndex]
        for i in range(self._entries):
            self._et.GetEntry(i) # loading is the heavy bit
            for v in vs:
                r = getattr(s, v)
                try:
                    res = list(r)
                except TypeError:
                    res = list([r])
                result[v].extend(res)

        for v in vs:
            result[v] = _np.array(result[v])
        return result


class PhaseSpaceData(_SamplerData):
    """
    Pull phase space data from a loaded DataLoader instance of raw data.

    Extracts only: 'x','xp','y','yp','z','zp','energy','T'

    Can either supply the sampler name or index as the optional second
    argument. The index is 0 counting including the primaries (ie +1 
    on the index in data.GetSamplerNames()). Examples::

    >>> f = pybdsim.Data.Load("file.root")
    >>> primaries = pybdsim.Data.PhaseSpaceData(f)
    >>> samplerfd45 = pybdsim.Data.PhaseSpaceData(f, "samplerfd45")
    >>> thirdAfterPrimaries = pybdsim.Data.PhaseSpaceData(f, 3)
    """
    def __init__(self, data, samplerIndexOrName=0):
        params = ['x','xp','y','yp','z','zp','energy','T']
        super(PhaseSpaceData, self).__init__(data, params, samplerIndexOrName)


class SamplerData(_SamplerData):
    """
    Pull sampler data from a loaded DataLoader instance of raw data.

    Loads all data in a given sampler.

    Can either supply the sampler name or index as the optional second
    argument. The index is 0 counting including the primaries (ie +1 
    on the index in data.GetSamplerNames()). Examples::

    >>> f = pybdsim.Data.Load("file.root")
    >>> primaries = pybdsim.Data.SampoerData(f)
    >>> samplerfd45 = pybdsim.Data.SamplerData(f, "samplerfd45")
    >>> thirdAfterPrimaries = pybdsim.Data.SamplerData(f, 3)
    """
    def __init__(self, data, samplerIndexOrName=0):
        params = ['n', 'energy', 'x', 'y', 'z', 'xp', 'yp','zp','T',
                  'weight','partID','parentID','trackID','modelID','turnNumber','S']
        super(SamplerData, self).__init__(data, params, samplerIndexOrName)
