"""
General utilities for day to day housekeeping
"""

import glob as _glob
import os as _os
import re as _re
import numpy as _np

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

def IsROOTFile(path):
    """Check if input is a ROOT file."""
    return path[-4:] == "root"
