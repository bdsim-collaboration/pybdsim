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
import numpy as _np
import subprocess
import uuid

def GenUniqueFilename(filename):
    i = 1
    parts = filename.split('.')
    basefilename = parts[0]
    if len(parts) > 1:
        extension = '.' + parts[1]
    else:
        extension = ''
    while os.path.exists(filename) :
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

def IsSurvey(file):
    """
    Checks if input is a BDSIM generated survey
    """
    if isinstance(file,_np.str):
        machine = pybdsim.Data.Load(file)
    elif isinstance(file,pybdsim.Data.BDSAsciiData):
        machine = file
    else:
        raise IOError("Unknown input type - not BDSIM data")

    return machine.names.count('SStart') != 0

def IsRootFile(path):
    """Check if input is a ROOT file."""
    # First four bytes of a ROOT file is the word "root"
    with open(path, "rb") as f:
        return f.read()[:4] == "root"

def RunBdsim(gmadpath, outfile, ngenerate=10000, batch=True,
             silent=False, options=None):
    """Runs bdsim with gmadpath as inputfile and outfile as outfile.
    Runs in batch mode by default, with 10,000 particles.  Any extra
    options should be provided as a string or iterable of strings of
    the form "--vis_debug" or "--vis_mac=vis.mac", etc.

    """
    args = ["bdsim",
            "--file={}".format(gmadpath),
            "--outfile={}".format(outfile),
            "--ngenerate={}".format(ngenerate)]
    if batch:
        args.append("--batch")

    if isinstance(options, basestring):
        args.append(options)
    elif options is not None:
        args.extend(options)

    if not silent:
        return subprocess.call(args)
    else:
        return subprocess.call(args, stdout=open(os.devnull, 'wb'))

def RunRebdsimOptics(rootpath, outpath, silent=False):
    """Run rebdsimOptics"""
    if not IsRootFile(rootpath):
        raise IOError("Not a ROOT file")
    if not silent:
        return subprocess.call(["rebdsimOptics", rootpath, outpath])
    else:
        return subprocess.call(["rebdsimOptics", rootpath, outpath],
                               stdout=open(os.devnull, 'wb'))

def GetOptics(gmad, write_optics=False):
    """Run the input gmadfile, and get the optics from the output as a
    BDSAsciiData instance.  If write_optics is true then the rebdsim
    optics file will be kept."""
    tmpdir = "/tmp/pybdsim-get-optics-{}/".format(uuid.uuid4())
    gmadname = os.path.splitext(os.path.basename(gmad))[0]
    os.mkdir(tmpdir)

    RunBdsim(gmad,
             "{}/{}".format(tmpdir, gmadname), silent=False,
             ngenerate=10000)
    bdsim_output_path = "{}/{}.root".format(tmpdir, gmadname)
    if write_optics: # write output root file locally.
        RunRebdsimOptics(bdsim_output_path,
                         "./{}-optics.root".format(gmadname))
        return pybdsim.Data.Load("./{}-optics.root".format(gmadname))
    else: # do it in /tmp/
        RunRebdsimOptics(bdsim_output_path,
                         "{}/{}-optics.root".format(tmpdir, gmadname))
        return pybdsim.Data.Load("{}/{}-optics.root".format(tmpdir, gmadname))
