"""
General utilities for day to day housekeeping
"""

import glob as _glob
import os as _os
import pybdsim.Data as _Data
import re as _re
import numpy as _np

def GetFileName(ob):
    """

    """
    if type(ob) == str:
        return ob
    elif type(ob) == _Data.RebdsimFile:
        return ob.filename
    elif type(ob) == _Data.BDSAsciiData:
        return ob.filename
    else:
        return ""

def GenUniqueFilename(filename):
    i = 1
    parts = filename.split('.')
    basefilename = parts[0]
    if len(parts) > 1:
        extension = '.' + parts[1]
    else:
        extension = ''
    while _os.path.exists(filename) :
        filename = basefilename+'_'+str(i)+extension
        i = i + 1
    return filename

def Chunks(l, n):
    """
    Yield successive n-sized chunks from l.
    """
    return [l[i:i+n] for i in range(0,len(l),n)]

def NearestEvenInteger(number):
    number = int(number)
    return number + number%2

def Cast(string):
    """
    Cast(string)
    
    tries to cast to a (python)float and if it doesn't work, 
    returns a string

    """
    try:
        return float(string)
    except ValueError:
        return string

def IsFloat(stringtotest):
    try:
        float(stringtotest)
        return True
    except ValueError:
        return False

def CheckItsBDSAsciiData(bfile, requireOptics=False):
    def CheckOptics(obj, requireOpticsL=False):
        if hasattr(obj,'Optics'):
            return obj.Optics
        elif hasattr(obj, 'optics'):
            return obj.optics
        else:
            if requireOpticsL:
                raise IOError("No optics found in pybdsim.Data.BDSAsciiData instance")
            else:
                return None
    
    if type(bfile) == str:
        data = _Data.Load(bfile)
        data2 = CheckOptics(data, requireOptics)
        if data2 is not None:
            data = data2
    elif type(bfile) == _Data.BDSAsciiData:
        data = bfile
    elif type(bfile) == _Data.RebdsimFile:
        data = CheckOptics(bfile, requireOptics)
    else:
        raise IOError("Not pybdsim.Data.BDSAsciiData file type: "+str(bfile))
    return data

def CheckBdsimDataHasSurveyModel(bfile):
    if isinstance(bfile, str):
        data = _Data.Load(bfile)
    elif type(bfile) == _Data.BDSAsciiData:
        data = bfile
    elif type(bfile) == _Data.RebdsimFile:
        data = bfile
    else:
        return False

    if hasattr(data,"model"):
        return True
    else:
        return False

def PrepareReducedName(elementname):
    """
    Only allow alphanumeric characters and '_'
    """
    rname = _re.sub('[^a-zA-Z0-9_]+','',elementname)
    return rname

def PrepareReducedName2(elementname):
    """
    Only allow alphanumeric characters and '_'
    """
    rname = _re.sub('[^a-zA-Z0-9_\.]+','',elementname)
    return rname

def GetLatestFileFromDir(dirpath='', extension='*'):
    return max(_glob.iglob(dirpath+extension), key=_os.path.getctime)

def IsSurvey(file):
    """
    Checks if input is a BDSIM generated survey
    """
    if isinstance(file,_np.str):
        machine = _Data.Load(file)
    elif isinstance(file, _Data.BDSAsciiData):
        machine = file
    else:
        raise IOError("Unknown input type - not BDSIM data")

    return machine.names.count('SStart') != 0

def IsROOTFile(path):
    """Check if input is a ROOT file."""
    return path[-4:] == "root"
