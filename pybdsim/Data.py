"""
Output loading

Read bdsim output

Classes:
Data - read various output files

"""
from . import Constants as _Constants
from . import _General

import copy as _copy
import glob as _glob
import numpy as _np
import os as _os

_useRoot      = True
_libsLoaded   = False

try:
    import ROOT as _ROOT
except ImportError:
    _useRoot = False
    pass

_bdsimApertureTypes = {"circular",
                       "elliptical",
                       "lhc",
                       "lhcdetailed",
                       "rectangular",
                       "rectellipse",
                       "racetrack",
                       "octagonal",
                       "circularvacuum",
                       "clicpcl"}

def LoadROOTLibraries():
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
    if "*" not in filepath:
        if not _os.path.exists(filepath):
            raise IOError("File: {} does not exist.".format(filepath))
        extension = filepath.split('.')[-1]
    else:
        print("* in name so assuming set of root files")
        extension = "root"    

    if extension == 'txt':
        return _LoadAscii(filepath)
    elif extension == 'root':
        try:
            return _LoadRoot(filepath)
        except NameError:
            #raise error rather than return None, saves later scripting errors.
            raise IOError('Root loader not available.')
    elif extension == 'dat':
        print('.dat file - trying general loader')
        try:
            return _LoadAscii(filepath)
        except IOError:
            raise IOError("No such file or directory: '{}'".format(filepath))
        except:
            raise IOError("Unknown file type - not BDSIM data")
    elif ("elosshist" in filepath) or (".hist" in filepath):
        return _LoadAsciiHistogram(filepath)
    elif "eloss" in filepath:
        return _LoadAscii(filepath)
    else:
        msg = "Unknown file type for file \"{}\" - not BDSIM data".format(filepath)
        raise IOError(msg)

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
        raise IOError("File(s) \"{}\" not found.".format(filepath))
    f = _ROOT.TFile(fileToCheck)
    if f.IsZombie():
        raise IOError("ROOT file \"{}\" is a zombie file".format(fileToCheck))
    htree = f.Get("Header")
    if not htree:
        raise Warning("ROOT file \"{}\" is not a BDSIM one".format(fileToCheck))
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

    LoadROOTLibraries()

    fileType = _ROOTFileType(filepath) #throws warning if not a bdsim file

    if fileType == "BDSIM":
        print('BDSIM output file - using DataLoader')
        d = _ROOT.DataLoader(filepath)
        d.model = GetModelForPlotting(d) # attach BDSAsciiData instance for convenience
        return d
    elif fileType == "REBDSIM":
        print('REBDSIM analysis file - using RebdsimFile')
        return RebdsimFile(filepath)
    elif fileType == "REBDSIMCOMBINE":
        print('REBDSIMCOMBINE analysis file - using RebdsimFile')
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

def _LoadVectorTree(tree):
    """
    Simple utility to loop over the entries in a tree and get all the leaves
    which are assumed to be a single number. Return BDSAsciiData instance.
    """
    result = BDSAsciiData()
    lvs = tree.GetListOfLeaves()
    lvs = [str(lvs[i].GetName()) for i in range(lvs.GetEntries())]
    for l in lvs:
        result._AddProperty(l)
    
    #tempData = []
    for value in tree:
        row = [getattr(value,l) for l in lvs]
        row = [str(value) if not isinstance(value, float) else value for value in row]
        result.append(row)

    #result = map(tuple, *tempData)
    return result
    
def GetModelForPlotting(rootFile, beamlineIndex=0):
    """
    Returns BDSAsciiData object with just the columns from the model for plotting.
    """
    mt = None
    if hasattr(rootFile, "Get"):
        # try first for ModelTree which we call it in histomerge output
        mt = rootFile.Get("ModelTree")
        if not mt:
            mt = rootFile.Get("Model") # then try regular Model
    elif hasattr(rootFile, "GetModelTree"):
        mt = rootFile.GetModelTree() # must be data loader instance
    if not mt:
        print("No 'Model.' tree in file")
        return

    leaves = ['componentName', 'componentType', 'length',    'staS',   'endS', 'k1']
    names  = ['Name',          'Type',          'ArcLength', 'SStart', 'SEnd', 'k1']
    types  = [str,              str,             float,       float,    float,  float]

    if mt.GetEntries() == 0:
        return None
    
    beamlines = [] # for future multiple beam line support
    # use easy iteration on root file - iterate on tree
    for beamline in mt:
        beamlines.append(beamline.Model)

    if beamlineIndex >= len(beamlines):
        raise IOError('Invalid beam line index')

    bl = beamlines[beamlineIndex]
    result = BDSAsciiData()
    tempdata = []
    for leave,name,t in zip(leaves,names,types):
        result._AddProperty(name)
        tempdata.append(list(map(t, getattr(bl, leave))))

    data = list(map(tuple, list(zip(*tempdata))))
    [result.append(d) for d in data]
    return result

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
        LoadROOTLibraries()
        self.filename = filename
        self._f = _ROOT.TFile(filename)
        self.histograms   = {}
        self.histograms1d = {}
        self.histograms2d = {}
        self.histograms3d = {}
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

        trees = self.ListOfTrees()
        # keep as optics (not Optics) to preserve data loading in Bdsim comparison plotting methods.
        if 'Optics' in trees:
            self.optics = _LoadVectorTree(self._f.Get("Optics"))
        if 'Orbit' in trees:
            self.orbit  = _LoadVectorTree(self._f.Get("Orbit"))
        if 'Model' in trees or 'ModelTree' in trees:
            self.model = GetModelForPlotting(self._f)

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

    def ListOfLeavesInTree(self, tree):
        """
        List all leaves in a tree.
        """
        leaves = tree.GetListOfLeaves()
        result = []
        for i in range(leaves.GetEntries()):
            result.append(str(leaves.At(i)))
        return result

    def ConvertToPybdsimHistograms(self):
        """
        Convert all root histograms into numpy arrays.
        """
        self.histogramspy = {}
        self.histograms1dpy = {}
        self.histograms2dpy = {}
        self.histograms3dpy = {}
        for path,hist in self.histograms1d.items():
            hpy = TH1(hist)
            self.histograms1dpy[path] = hpy
            self.histogramspy[path] = hpy
        for path,hist in self.histograms2d.items():
            hpy = TH2(hist)
            self.histograms2dpy[path] = hpy
            self.histogramspy[path] = hpy
        for path,hist in self.histograms3d.items():
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
        self._columnsLower = list(map(str.lower, self.columns))
        self.filename = "" # file data was loaded from

    def __getitem__(self,index):
        if type(index) is str:
            nameCol = list(map(str.lower, self.GetColumn('name', ignoreCase=True)))
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
            try:
                return _np.array([event[ind] for event in self])
            except TypeError:
                return _np.array([str(event[ind]) for event in self])
                
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
            print("The parameter: ",parametername," does not exist in this instance")

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
                raise ValueError("Invalid column name \"" + columnstring + "\"")
        else:
            if columnstring not in self.columns:
                raise ValueError("Invalid column name \"" + columnstring + "\"")
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

def PadHistogram1D(hist, padValue=1e-20):
    """
    Pad a 1D histogram with padValue.

    This adds an extra 'bin' to xwidths, xcentres, xlowedge, xhighedge,
    contents and errors with either pad value or a linearly interpolated
    step in the range (i.e. for xcentres).

    returns a new pybdsim.Data.TH1 instance.
    """
    r = _copy.deepcopy(hist)
    r.nbinsx  = hist.nbinsx+2
    r.xwidths   = _np.pad(hist.xwidths,  1, 'edge')
    r.xcentres  = _np.pad(hist.xcentres, 1, 'reflect',  reflect_type='odd')
    r.xlowedge  = _np.pad(hist.xlowedge, 1, 'reflect',  reflect_type='odd')
    r.xhighedge = _np.pad(hist.xlowedge, 1, 'reflect',  reflect_type='odd')
    r.contents  = _np.pad(hist.contents, 1, 'constant', constant_values=padValue)
    r.errors    = _np.pad(hist.errors,   1, 'constant', constant_values=padValue)
    return r

def ReplaceZeroWithMinimum(hist, value=1e-20):
    """
    Replace zero values with given value. Useful for log plots.

    For log plots we want a small but +ve number instead of 0 so the line
    is continuous on the plot. This is also required for padding to work
    for the edge of the lines.

    Works for TH1, TH2, TH3.

    returns a new instance of the pybdsim.Data.TH1, TH2 or TH3.
    """
    r = _copy.deepcopy(hist)
    r.contents[hist.contents==0] = value
    return r

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
        self.errorsAreErrorOnMean = True

    def ErrorsToSTD(self):
        """
        Errors are by default the error on the mean. Call this function
        to multiply by sqrt(N) to convert to the standard deviation.
        Will automatically only apply itself once even if repeatedly called.
        """
        if self.errorsAreErrorOnMean:
            self.errors *= _np.sqrt(self.entries)
            self.errorsAreErrorOnMean = False
        else:
            pass # don't double apply calculation

    def ErrorsToErrorOnMean(self):
        """
        Errors are by default the error on the mean. However, if you used
        ErrorsToSTD, you can convert back to error on the mean with this
        function, which divides by sqrt(N).
        """
        if self.errorsAreErrorOnMean:
            pass # don't double apply calculation
        else:
            self.errors /= _np.sqrt(self.entries)
            self.errorsAreErrorOnMean = True

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
            self.xhighedge[i] = self.xlowedge[i] + self.xwidths[i]
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
            self.yhighedge[i] = self.ylowedge[i] + self.ywidths[i]
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
            self.zhighedge[i] = self.zlowedge[i] + self.zwidths[i]
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
        if not isinstance(data,_ROOT.DataLoader):
            raise IOError("Data is not a ROOT.DataLoader object. Supply data "
                          "loaded with pybdsim.Data.Load")
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
    >>> primaries = pybdsim.Data.SamplerData(f)
    >>> samplerfd45 = pybdsim.Data.SamplerData(f, "samplerfd45")
    >>> thirdAfterPrimaries = pybdsim.Data.SamplerData(f, 3)
    """
    def __init__(self, data, samplerIndexOrName=0):
        params = ['n', 'energy', 'x', 'y', 'z', 'xp', 'yp','zp','T',
                  'weight','partID','parentID','trackID','modelID','turnNumber','S',
                  'r', 'rp', 'phi', 'phip', 'charge', 'kineticEnergy',
                  'mass', 'rigidity','isIon','ionA','ionZ']
        super(SamplerData, self).__init__(data, params, samplerIndexOrName)

class TrajectoryData(object):
    """
    Pull trajectory data from a loaded Dataloader instance of raw data

    Loads all trajectory data in a event event

    >>> f = pybdsim.Data.Load("file.root")
    >>> trajectories = pybdsim.Data.TrajectoryData(f,0)
    """


    def __init__(self, dataLoader, eventNumber=0):
        params = ['n','trajID','partID','x','y','z']
        self._dataLoader  = dataLoader
        self._eventTree   = dataLoader.GetEventTree()
        self._event       = dataLoader.GetEvent()
        self._trajectory  = self._event.GetTrajectory()
        self.trajectories = []
        _header = dataLoader.GetHeader()
        _headerTree =  dataLoader.GetHeaderTree()
        _headerTree.GetEntry(0)
        self._dataVersion = _header.header.dataVersion
        self._GetTrajectory(eventNumber)

    def __len__(self):
        return len(self.trajectories)

    def __repr__(self):
        s = ''
        s += str(len(self)) + ' trajectories'
        return s

    def __getitem__(self, index):
        return self.trajectories[index]
        
    def __iter__(self):
        self._iterindex = -1
        return self

    def __next__(self):
        if self._iterindex == len(self.trajectories)-1:
            raise StopIteration
        self._iterindex += 1
        return self.trajectories[self._iterindex]

    next = __next__

    def _GetTrajectory(self, eventNumber):
        if eventNumber >= self._eventTree.GetEntries():
            raise IndexError


        # loop over all trajectories
        self._eventTree.GetEntry(eventNumber)
        for i in range(0, self._trajectory.n):
            pyTrajectory = {}
            pyTrajectory['trackID']  = int(self._trajectory.trackID[i])
            pyTrajectory['partID']   = int(self._trajectory.partID[i])
            pyTrajectory['parentID'] = int(self._trajectory.parentID[i])

            prePT = self._trajectory.preProcessTypes[i]
            prePST = self._trajectory.preProcessSubTypes[i]
            postPT = self._trajectory.postProcessTypes[i]
            postPST = self._trajectory.postProcessSubTypes[i]

            # Adding new parameters and updating trajectory names
            if self._dataVersion >= 5:
                t = self._trajectory.XYZ[i]
                ts = self._trajectory.S[i]
                p = self._trajectory.PXPYPZ[i]
                e = self._trajectory.energyDeposit[i]
                time = self._trajectory.T[i]

                try:
                    xyz = self._trajectory.xyz[i]
                    pxpypz = self._trajectory.pxpypz[i]
                except IndexError:
                    xyz = _np.zeros(len(t))
                    pxpypz = _np.zeros(len(t))

                try:
                    q = self._trajectory.charge[i]
                    ke = self._trajectory.kineticEnergy[i]
                    tT = self._trajectory.turnsTaken[i]
                    m = self._trajectory.mass[i]
                    rho = self._trajectory.rigidity[i]
                except IndexError:
                    q = _np.zeros(len(t))
                    ke = _np.zeros(len(t))
                    tT = _np.zeros(len(t))
                    m = _np.zeros(len(t))
                    rho = _np.zeros(len(t))

                try:
                    ion = self._trajectory.isIon[i]
                    a = self._trajectory.ionA[i]
                    z = self._trajectory.ionZ[i]
                    el = self._trajectory.nElectrons[i]
                except IndexError:
                    ion = _np.full((len(t), 0), False)
                    a = _np.zeros(len(t))
                    z = _np.zeros(len(t))
                    el = _np.zeros(len(t))

            else:
                #from IPython import embed; embed()
                t  = self._trajectory.trajectories[i]
                #tS = self._trajectory.trajectoriesS[i]


                p = self._trajectory.momenta[i]
                e = self._trajectory.energies[i]

            X = _np.zeros(len(t))
            Y = _np.zeros(len(t))
            Z = _np.zeros(len(t))
            S = _np.zeros(len(t))

            T = _np.zeros(len(t))
            EDeposit = _np.zeros(len(t))

            PX = _np.zeros(len(t))
            PY = _np.zeros(len(t))
            PZ = _np.zeros(len(t))

            x = _np.zeros(len(t))
            y = _np.zeros(len(t))
            z = _np.zeros(len(t))

            px = _np.zeros(len(t))
            py = _np.zeros(len(t))
            pz = _np.zeros(len(t))

            charge = _np.zeros(len(t))
            kineticEnergy = _np.zeros(len(t))
            turnsTaken = _np.zeros(len(t))
            mass = _np.zeros(len(t))
            rigidity = _np.zeros(len(t))

            isIon = _np.full((len(t), 0), False)
            ionA = _np.zeros(len(t))
            ionZ = _np.zeros(len(t))
            nElectrons = _np.zeros(len(t))

            preProcessTypes     = _np.zeros(len(t))
            preProcessSubTypes  = _np.zeros(len(t))
            postProcessTypes    = _np.zeros(len(t))
            postProcessSubTypes = _np.zeros(len(t))

            for j in range(0, len(t)):
                # position
                X[j] = t[j].X()
                Y[j] = t[j].Y()
                Z[j] = t[j].Z()
                S[j] = S[j]

                # momenta
                PX[j] = p[j].X()
                PY[j] = p[j].Y()
                PZ[j] = p[j].Z()

                EDeposit[j] = e[j]

                if self._dataVersion >= 5:
                    T[j] = time[j]
                    try:
                        x[j] = xyz[j].X()
                        y[j] = xyz[j].Y()
                        z[j] = xyz[j].Z()
                        px[j] = pxpypz[j].X()
                        py[j] = pxpypz[j].Y()
                        pz[j] = pxpypz[j].Z()
                    except AttributeError:
                        x[j] = 0
                        y[j] = 0
                        z[j] = 0
                        px[j] = 0
                        py[j] = 0
                        pz[j] = 0

                    charge[j] = q[j]
                    kineticEnergy[j] = ke[j]
                    turnsTaken[j] = tT[j]
                    mass[j] = m[j]
                    rigidity[j] = rho[j]
                    isIon[j] = ion[j]
                    ionA[j] = a[j]
                    ionZ[j] = z[j]
                    nElectrons[j] = el[j]

                preProcessTypes[j]    = prePT[j]
                preProcessSubTypes[j] = prePST[j]

                postProcessTypes[j]    = postPT[j]
                postProcessSubTypes[j] = postPST[j]
                            
            pyTrajectory['X'] = X
            pyTrajectory['Y'] = Y
            pyTrajectory['Z'] = Z
            pyTrajectory['S'] = S

            pyTrajectory['PX'] = PX
            pyTrajectory['PY'] = PY
            pyTrajectory['PZ'] = PZ

            pyTrajectory['EnergyDeposit'] = EDeposit

            if self._dataVersion >= 5:
                pyTrajectory['T'] = T
                pyTrajectory['x'] = x
                pyTrajectory['y'] = y
                pyTrajectory['z'] = z
                pyTrajectory['px'] = px
                pyTrajectory['py'] = py
                pyTrajectory['pz'] = pz
                pyTrajectory['charge'] = charge
                pyTrajectory['kineticEnergy'] = kineticEnergy
                pyTrajectory['turnsTaken'] = turnsTaken
                pyTrajectory['mass'] = mass
                pyTrajectory['rigidity'] = rigidity
                pyTrajectory['isIon'] = isIon
                pyTrajectory['ionA'] = ionA
                pyTrajectory['ionZ'] = ionZ
                pyTrajectory['nElectrons'] = nElectrons

            pyTrajectory['prePT'] = preProcessTypes
            pyTrajectory['prePST'] = preProcessSubTypes

            pyTrajectory['postPT'] = postProcessTypes
            pyTrajectory['postPST'] = postProcessSubTypes

            self.trajectories.append(pyTrajectory)


class EventInfoData(object):
    """
    Extract data from the Info branch of the Event tree.
    """
    def __init__(self, data):
        event = data.GetEvent()
        eventTree = data.GetEventTree()
        info = event.Info
        interface = _filterROOTObject(info)
        self._getData(interface, info, eventTree)

    def _getData(self, interface, rootobj, tree):
        # Set lists to append to
        for name in interface:
            setattr(self, name, [])
        for i in range(tree.GetEntries()):
            tree.GetEntry(i)
            for name in interface:
                data = getattr(rootobj, name)
                iterable = getattr(self, name)
                iterable.append(data)

        for name in interface: # Convert lists to numpy arrays.
            setattr(self, name, _np.array(getattr(self, name)))

    @classmethod
    def FromROOTFile(cls, path):
        data = Load(path)
        return cls(data)


class EventSummaryData(EventInfoData):
    """
    Extract data from the Summary branch of the Event tree.
    """
    # this simply inherits EventInfoData as the branch is the same,
    # just renamed to Summary from Info.
    def __init__(self, data):
        event     = data.GetEvent()
        eventTree = data.GetEventTree()
        info      = event.Summary
        interface = _filterROOTObject(info)
        self._getData(interface, info, eventTree)

def GetApertureExtent(apertureType, aper1=0, aper2=0, aper3=0, aper4=0):
    apertureType = apertureType.lower()

    if apertureType == "":
        return 0,0

    if apertureType not in _bdsimApertureTypes:
        raise ValueError("Unknown aperture type: " + apertureType)

    # default behaviour
    x = aper1
    y = aper2

    if apertureType in {"circular", "circularvacuum"}:
        y = aper1
    elif apertureType in {"lhc", "lhcdetailed"}:
        x = min(aper1, aper3)
        y = min(aper2, aper3)
    elif apertureType in {"rectellipse"}:
        x = min(aper1, aper3)
        y = min(aper2, aper4)
    elif apertureType in {"racetrack"}:
        x = aper1 + aper3
        y = aper2 + aper3
    elif apertureType in {"clicpcl"}:
        y = aper2 + aper3 + aper4
        
    return x,y
        
class ApertureInfo(object):
    """
    Simple class to hold aperture parameters and extents.
    """
    def __init__(self, apertureType, aper1, aper2=0, aper3=0, aper4=0, offsetX=0, offsetY=0):
        self.apertureType = apertureType
        self.aper1    = aper1
        self.aper2    = aper2
        self.aper3    = aper3
        self.aper4    = aper4
        self.offsetX  = offsetX
        self.offsetY  = offsetY
        self.x,self.y = GetApertureExtent(apertureType, aper1, aper2, aper3, aper4)

class ModelData(object):
    def __init__(self, data):
        model = data.GetModel()
        modelTree = data.GetModelTree()
        model = model.model
        modelTree.GetEntry(0)
        interface = _filterROOTObject(model)
        self._getData(interface, model)

    @classmethod
    def FromROOTFile(cls, path):
        data = Load(path)
        return cls(data)

    def _getData(self, interface, rootobj):
        for name in interface:
            try:
                setattr(self, name, _np.array(getattr(rootobj, name)))
            except TypeError:
                # could be a map or a vector of our classes which wouldn't work
                try:
                    # try converting map to a dictionary - TBC
                    setattr(self, name, dict(getattr(rootobj, name)))
                except:
                    pass # just ignore it
            except ValueError:
                pass # just ignore it

    def GetApertureData(self, removeZeroLength=False, removeZeroApertures=True, lengthTolerance=1e-6):
        """
        return a list of aperture instances along with coordinates:
        l,s,x,y,apertures
        l - length of element
        s - curvilinear S coordinate at the *end* of the element
        x - horizontal extent
        y - vertical extent
        apertures = [ApertureInfo]
        """
        result = []
        l,s,x,y = [],[],[],[]

        for ll,ss,at,a1,a2,a3,a4 in zip(self.length,
                                        self.endS,
                                        self.beamPipeType,
                                        self.beamPipeAper1,
                                        self.beamPipeAper2,
                                        self.beamPipeAper3,
                                        self.beamPipeAper4):
            if removeZeroLength and l < lengthTolerance:
                continue # skip this entry
            elif removeZeroApertures and (a1 == 0 and a2 == 0 and a3 == 0 and a4 == 0):
                continue
            else:
                l.append(ll)
                s.append(ss)
                result.append(ApertureInfo(at,a1,a2,a3,a4))
                x.append(result[-1].x)
                y.append(result[-1].y)
        return _np.array(l),_np.array(s),_np.array(x),_np.array(y),result


class OptionsData(object):
    def __init__(self, data):
        options = data.GetOptions()
        optionsTree = data.GetOptionsTree()
        options = options.options
        optionsTree.GetEntry(0)
        interface = _filterROOTObject(options)
        self._getData(interface, options)

    @classmethod
    def FromROOTFile(cls, path):
        data = Load(path)
        return cls(data)

    def _getData(self, interface, rootobj):
        for name in interface:
            setattr(self, name, getattr(rootobj, name))


class BeamData(object):
    def __init__(self, data):
        beam = data.GetBeam()
        beamTree = data.GetBeamTree()
        beam = beam.beam
        beamTree.GetEntry(0)
        interface = _filterROOTObject(beam)
        self._getData(interface, beam)

    @classmethod
    def FromROOTFile(cls, path):
        data = Load(path)
        return cls(data)

    def _getData(self, interface, rootobj):
        for name in interface:
            setattr(self, name, getattr(rootobj, name))


def _filterROOTObject(rootobj):
    """Gets the names of the attributes which are just data and
    specific to the class.  That is to say it removes all the
    clutter inherited from TObject, any methods, and some other
    stuff.  Should retain strictly only the data."""
    # Define an instance of TObject which we can use to extract
    # the interface of our rootobj, leaving out all the rubbish.
    tobject_interface = set(dir(_ROOT.TObject()))
    rootobj_interface = set(dir(rootobj))
    interface = rootobj_interface.difference(tobject_interface)

    # remove other stuff
    interface.remove("__lifeline") # don't know what this is :)
    interface = [attr for attr in interface # remove functions
                 if not callable(getattr(rootobj, attr))]

    return interface
