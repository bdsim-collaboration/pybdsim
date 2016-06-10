# pybdsim._General - general python scripts / tools
# Version 1.0
# L. Nevay, S.T.Boogert, J.Snuverink

"""
General utilities for day to day housekeeping
"""

import glob
import os
import pybdsim.Data
import re as _re

def CheckFileExists(filename):
    i = 1
    parts = filename.split('.')
    basefilename = parts[0]
    if len(parts) > 1:
        extension = '.' + parts[1]
    else:
        extension = ''
    while os.path.exists(filename) :
        filename = basefilename+str(i)+extension
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

def CheckItsBDSAsciiData(bfile):
    if type(bfile) == str:
        data = pybdsim.Data.Load(bfile)
    elif type(bfile) == pybdsim.Data.BDSAsciiData:
        data = bfile
    else:
        raise IOError("Not pybdsim.Data.BDSAsciiData file type: "+str(bfile))
    return data

def PrepareReducedName(elementname):
    """
    Only allow alphanumeric characters and '_'
    """
    rname = _re.sub('[^a-zA-Z0-9_]+','',elementname)
    return rname

def GetLatestFileFromDir(dirpath='', extension='*'):
    return max(glob.iglob(dirpath+extension), key=os.path.getctime)
