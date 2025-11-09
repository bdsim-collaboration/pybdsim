"""
Utilities for running BDSIM and other tools from Python.

"""
import glob as _glob
from multiprocessing import Pool as _Pool
from multiprocessing import cpu_count as _cpu_count
import numpy as _np
import os as _os
import subprocess as _subprocess
import uuid as _uuid
import time as _time

from . import Data as _Data
from . import _General


class ExecOptions(dict):
    def __init__(self, *args, **kwargs):
        """
        Executable options class for BDSIM. In addition, 'bdsimcommand' is an extra
        allowed keyword argument that allows the user to specify the bdsim executable
        of their choice.

        bdsimcommand='bdsim-devel'
        bdsimcommand='/Users/nevay/physics/bdsim-build2/bdsim'

        Based on python dictionary but with parameter checking.
        """
        super().__init__()
        self._okFlags = ['batch',
                         'circular',
                         'generatePrimariesOnly',
                         'verbose']
        self._okArgs = ['bdsimcommand',
                        'file',
                        'output',
                        'outfile',
                        'ngenerate',
                        'seed',
                        'seedstate',
                        'survey',
                        'distrFile']
        for key,value in kwargs.items():
            if key in self._okFlags or key in self._okArgs:
                self[key] = value
            else:
                raise ValueError(key+'='+str(value)+' is not a valid BDSIM executable option')
        self.bdsimcommand = 'bdsim'
        if 'bdsimcommand' in self:
            self.bdsimcommand = self['bdsimcommand']
            self.pop("bdsimcommand", None)

    def GetExecFlags(self):
        result = dict((k,self[k]) for k in list(self.keys()) if k in self._okFlags)
        return result

    def GetExecArgs(self):
        result = dict((k,self[k]) for k in list(self.keys()) if k in self._okArgs)
        return result


class GmadModifier(object):
    def __init__(self, rootgmadfilename):
        self.rootgmadfilename = rootgmadfilename
        self.gmadfiles = [self.rootgmadfilename]
        self.DetermineIncludes(self.rootgmadfilename)
        self.CheckExtensions()

    def DetermineIncludes(self,filename) :
        f = open(filename)
        for l in f :
            if l.find("include") != -1 :
                includefile = l.split()[1].replace(";","")
                self.gmadfiles.append(includefile)
                self.DetermineIncludes(includefile)
        f.close()

    def CheckExtensions(self) :
        for filename in self.gmadfiles : 
            pass
    
    def ReplaceTokens(self,tokenDict) :
        pass


class Study(object):
    """
    A holder for multiple runs.
    """
    def __init__(self):
        self.execoptions = [] # exec options
        self.outputnames = [] # file names
        self.outputsizes = [] # in bytes

    def GetInfo(self, index=-1):
        """
        Get info about a particular run.
        """
        if index < 0:
            print("No runs yet")
            return
        
        i = index
        result = {'execoptions' : self.execoptions[i],
                  'outputname'  : self.outputnames[i],
                  'outputsize'  : self.outputsizes[i]}
        return result
                
    def Run(self, inputfile='optics.gmad',
            output='rootevent',
            outfile='output',
            ngenerate=1,
            bdsimcommand='bdsim-devel',
            **kwargs):
        eo = ExecOptions(file=inputfile, output=output, outfile=outfile, ngenerate=ngenerate, **kwargs)
        return self.RunExecOptions(eo)

    def RunExecOptions(self, execoptions, debug=False):
        if type(execoptions) != ExecOptions:
            raise ValueError("Not instance of ExecOptions")

        # shortcut
        eo = execoptions
        
        # prepare execution command
        command = eo.bdsimcommand
        for k in eo.GetExecFlags():
            command += ' --' + k
        for k,v in eo.GetExecArgs().items():
            command += ' --' + str(k) + '=' + str(v)
        if debug:
            print('Command is')
            print(command)

        # send it to a log file
        outfilename = 'output'
        if 'outfile' in eo:
            outfilename = eo['outfile']
        command += ' > ' + outfilename + '.log'
        
        # execute process
        if debug:
            print('BDSIM Run')
        try:
            _subprocess.check_call(command, shell=True)
        except _subprocess.CalledProcessError:
            print('ERROR')
            return
        
        # get output file name - the latest file in the directory hopefully
        try:
            outfilename = eo['outfile']
        except KeyError:
            outfilename = _General.GetLatestFileFromDir(extension='*root') # this directory

        # record info
        self.execoptions.append(eo)
        self.outputnames.append(outfilename)
        try:
            self.outputsizes.append(_os.path.getsize(outfilename))
        except OSError:
            self.outputsizes.append(0)


def _NumberOfCPUs(nCPUs=None):
    maxNumberOfCores = _cpu_count() - 1
    if nCPUs is None:
        nCPUs = maxNumberOfCores
    if nCPUs > maxNumberOfCores:
        print("Limiting the number of jobs to {}".format(maxNumberOfCores))
        nCPUs = maxNumberOfCores
    return nCPUs


def Bdsim(gmadpath, outfile, ngenerate=10000, seed=None, batch=True,
          silent=False, errorSilent=False, options=None, bdsimExecutable=None):
    """
    Runs bdsim with gmadpath as inputfile and outfile as outfile.
    Runs in batch mode by default, with 10,000 particles. Any extra
    options should be provided as a string or iterable of strings of
    the form "--vis_debug" or "--vis_mac=vis.mac", etc.
    """
    if not bdsimExecutable:
        bdsimExecutable = "bdsim"
    args = [bdsimExecutable,
            "--file={}".format(gmadpath),
            "--outfile={}".format(outfile)]
    if ngenerate is not None:
        args.append("--ngenerate={}".format(ngenerate))
    if batch:
        args.append("--batch")
    if seed is not None:
        args.append("--seed={}".format(int(seed)))

    if isinstance(options, str):
        args.append(options)
    elif options is not None:
        args.extend(options)

    if not silent:
        return _subprocess.call(args)
    elif silent and errorSilent:
        return _subprocess.call(args, stdout=open(_os.devnull, 'wb'), stderr=open(_os.devnull, 'wb'))
    else:
        return _subprocess.call(args, stdout=open(_os.devnull, 'wb'))

def BdsimParallel(gmadpath, outfile, nJobs=1, ngenerate=10000, startseed=None, batch=True,
                  silent=False, errorSilent=True, options=None, bdsimExecutable=None, nCPUs=None):
    """
    Runs multiple bdsim instances with gmadpath as inputfile and outfile as outfile.
    The number of parallel jobs is defined by nJobs. It can be specified how many cores
    are used with nCPUs (default is the total number of cores available minus 1). Runs
    in batch mode by default, with 10,000 particles.
    Any extra options should be provided as a string or iterable of strings of
    the form "--vis_debug" or "--vis_mac=vis.mac", etc.
    """
    if startseed is None:
        seed = int(_time.time())
    else:
        seed = int(startseed)

    maxNumberOfCores = _cpu_count() - 1
    if nCPUs is None:
        nCPUs = maxNumberOfCores
    if nCPUs > maxNumberOfCores:
        print("Limiting the number of cores to the maximum of {}".format(maxNumberOfCores))
        nCPUs = maxNumberOfCores
    if nJobs < nCPUs:
        nCPUs = nJobs
    p = _Pool(processes=nCPUs)
    for i in range(nJobs):
        args = (gmadpath, outfile + '_' + str(i), ngenerate, seed, batch,
                     silent, errorSilent, options, bdsimExecutable)
        p.apply_async(Bdsim, args=args)
        seed += 1
    p.close()
    p.join()

def Rebdsim(analysis_config_file, bdsim_raw_output_file, output_file_name=None, silent=False, rebdsimExecutable=None):
    """
    Run rebdsim with rootpath as analysis configuration text file on a bdsim
    raw output root file.

    :param analysis_config_file: rebdsim analysis configuration text file
    :type analysis_config_file: str
    :param bdsim_raw_output_file: bdsim raw output root file to analyse
    :type bdsim_raw_output_file: str
    :param output_file_name: optional output file name, default is (raw_name)_ana.root
    :type output_file_name: None, str
    :param silent: whether to suppress the print-out
    :type silent: bool
    :param rebdsimExecutable: specific executable to use for developers
    :type rebdsimExecutable: None, str
    """
    rebdsimExecutable = "rebdsim" if not rebdsimExecutable else rebdsimExecutable
    if not _General.IsROOTFile(bdsim_raw_output_file):
        raise IOError("Not a ROOT file")
    args = [rebdsimExecutable, analysis_config_file, bdsim_raw_output_file]
    if output_file_name is not None:
        args.append(output_file_name)
    if silent:
        return _subprocess.call(args, stdout=open(_os.devnull, 'wb'))
    else:
        return _subprocess.call(args)

def Bdskim(skim_config_file, bdsim_raw_output_file, output_file_name=None, silent=False, bdskimExecutable=None):
    """
    Run bdskim with skim_config_file as skim configuration text file on a bdsim
    raw output root file.

    :param skim_config_file: skim configuration text file
    :type skim_config_file: str
    :param bdsim_raw_output_file: bdsim raw output root file to analyse
    :type bdsim_raw_output_file: str
    :param output_file_name: optional output file name, default is (raw_name)_skim.root
    :type output_file_name: None, str
    :param silent: whether to suppress the print-out
    :type silent: bool
    :param rebdsimExecutable: specific executable to use for developers
    :type rebdsimExecutable: None, str
    """
    bdskimExecutable = "bdskim" if not bdskimExecutable else bdskimExecutable
    if not _General.IsROOTFile(bdsim_raw_output_file):
        raise IOError("Not a ROOT file")
    args = [bdskimExecutable, skim_config_file, bdsim_raw_output_file]
    if output_file_name is not None:
        args.append(output_file_name)
    if silent:
        return _subprocess.call(args, stdout=open(_os.devnull, 'wb'))
    else:
        return _subprocess.call(args)

def BdskimParallel(skim_config_file, bdsim_raw_output_file_list, outfilelist=None, silent=False,
                   bdskimExecutable=None, nCPUs=None):
    """
    Run multiple bdskim instances with a single skim config file. The number
    of parallel jobs is defined by nCPUs, but limited to the total number
    of cores available minus 1.

    :param skim_config_file: skim configuration text file
    :type skim_config_file: str
    :param bdsim_raw_output_file_list: list of bdsim raw output root files to analyse
    :type bdsim_raw_output_file_list: list(str)
    """
    nCPUs = _NumberOfCPUs(nCPUs)

    if outfilelist is not None and len(bdsim_raw_output_file_list) != len(outfilelist):
        raise ValueError("Number of input files and output files do not match")
    elif outfilelist is None:
        outfilelist = [f[:-5] if f.endswith('.root') else f for f in bdsim_raw_output_file_list]
        outfilelist = [f + '_skim.root' for f in outfilelist]
    p = _Pool(processes=nCPUs)

    for infile, outfile in zip(bdsim_raw_output_file_list, outfilelist):
        args = (skim_config_file, infile, outfile, silent, bdskimExecutable)
        p.apply_async(Bdskim, args=args)
    p.close()
    p.join()

def RebdsimParallel(analysis_config_file, bdsim_raw_output_file_list, outfilelist=None, silent=False,
                    rebdsimExecutable=None, nCPUs=None):
    """
    Run multiple rebdsim instances with a single analysis config file. The number
    of parallel jobs is defined by nCPUs, but limited to the total number
    of cores available minus 1.

    :param analysis_config_file: rebdsim analysis configuration text file
    :type analysis_config_file: str
    :param bdsim_raw_output_file_list: list of bdsim raw output root files to analyse
    :type bdsim_raw_output_file_list: list(str)
    """
    nCPUs = _NumberOfCPUs(nCPUs)

    if outfilelist is not None and len(bdsim_raw_output_file_list) != len(outfilelist):
        raise ValueError("Number of input files and output files do not match")
    elif outfilelist is None:
        outfilelist = [f[:-5] if f.endswith('.root') else f for f in bdsim_raw_output_file_list]
        outfilelist = [f + '_ana.root' for f in outfilelist]
    p = _Pool(processes=nCPUs)

    for infile, outfile in zip(bdsim_raw_output_file_list, outfilelist):
        args = (analysis_config_file, infile, outfile, silent, rebdsimExecutable)
        p.apply_async(Rebdsim, args=args)
    p.close()
    p.join()

def RebdsimOptics(rootpath, outpath, silent=False):
    """
    Run rebdsimOptics
    """
    if not _General.IsROOTFile(rootpath):
        raise IOError("Not a ROOT file")
    if silent:
        return _subprocess.call(["rebdsimOptics", rootpath, outpath],
                               stdout=open(_os.devnull, 'wb'))
    else:
        return _subprocess.call(["rebdsimOptics", rootpath, outpath])

def RebdsimHistoMerge(rootpath, outpath, silent=False, rebdsimHistoExecutable=None):
    """
    Run rebdsimHistoMerge
    """
    if not rebdsimHistoExecutable:
        rebdsimHistoExecutable = "rebdsimHistoMerge"
    if not _General.IsROOTFile(rootpath):
        raise IOError("Not a ROOT file")
    if silent:
        return _subprocess.call([rebdsimHistoExecutable, rootpath, outpath],
                               stdout=open(_os.devnull, 'wb'))
    else:
        return _subprocess.call([rebdsimHistoExecutable, rootpath, outpath])

def RebdsimHistoMergeParallel(bdsim_raw_output_file_list, outfilelist=None, silent=False,
                              rebdsimHistoExecutable=None, nCPUs=None):
    """
    Run multiple rebdsimHistoMerge instances. The number of parallel jobs is defined by nCPUs,
    but limited to the total number of cores available minus 1.

    :param bdsim_raw_output_file_list: list of bdsim raw output root files to analyse
    :type bdsim_raw_output_file_list: list(str)
    """
    nCPUs = _NumberOfCPUs(nCPUs)

    if outfilelist is not None and len(bdsim_raw_output_file_list) != len(outfilelist):
        raise ValueError("Number of input files and output files do not match")
    elif outfilelist is None:
        outfilelist = [f[:-5] if f.endswith('.root') else f for f in bdsim_raw_output_file_list]
        outfilelist = [f + '_histo.root' for f in outfilelist]
    p = _Pool(processes=nCPUs)

    for infile, outfile in zip(bdsim_raw_output_file_list, outfilelist):
        args = (infile, outfile, silent, rebdsimHistoExecutable)
        p.apply_async(RebdsimHistoMerge, args=args)
    p.close()
    p.join()

def BdsimCombine(infileList, outpath, silent=False, bdsimCombineExecutable=None):
    """
    Run bdsimCombine
    """
    if not bdsimCombineExecutable:
        bdsimCombineExecutable = "bdsimCombine"
    for file in infileList:
        if not _General.IsROOTFile(file):
            raise IOError("Not a ROOT file")
    job = [bdsimCombineExecutable, outpath]
    job.extend(infileList)
    if silent:
        return _subprocess.call(job, stdout=open(_os.devnull, 'wb'))
    else:
        return _subprocess.call(job)

def RebdsimCombine(infileList, outpath, silent=False, rebdsimCombineExecutable=None):
    """
    Run rebdsimCombine
    """
    if not rebdsimCombineExecutable:
        rebdsimCombineExecutable = "rebdsimCombine"
    for file in infileList:
        if not _General.IsROOTFile(file):
            raise IOError("Not a ROOT file")
    job = [rebdsimCombineExecutable, outpath]
    job.extend(infileList)
    if silent:
        return _subprocess.call(job, stdout=open(_os.devnull, 'wb'))
    else:
        return _subprocess.call(job)

def RebdsimOrbit(rootpath, outpath, index='1', silent=False, rebdsimHistoExecutable=None):
    """
    Run rebdsimOrbit
    """
    if not rebdsimHistoExecutable:
        rebdsimHistoExecutable = "rebdsimOrbit"
    if not _General.IsROOTFile(rootpath):
        raise IOError("Not a ROOT file")
    if silent:
        return _subprocess.call([rebdsimHistoExecutable, rootpath, outpath, index],
                               stdout=open(_os.devnull, 'wb'))
    else:
        return _subprocess.call([rebdsimHistoExecutable, rootpath, outpath, index])

def GetOpticsFromGMAD(gmad, keep_optics=False):
    """
    Get the optical functions as a BDSAsciiData instance from this
    GMAD file. If keep_optics is false then all intermediate files are
    discarded, otherwise the final optics ROOT file is written to ./
    """
    tmpdir = "/tmp/pybdsim-get-optics-{}/".format(_uuid.uuid4())
    gmadname = _os.path.splitext(_os.path.basename(gmad))[0]
    _os.mkdir(tmpdir)

    Bdsim(gmad, "{}/{}".format(tmpdir, gmadname), silent=False, ngenerate=10000)
    bdsim_output_path = "{}/{}.root".format(tmpdir, gmadname)
    if keep_optics: # write output root file locally.
        RebdsimOptics(bdsim_output_path, "./{}-optics.root".format(gmadname))
        return _Data.Load("./{}-optics.root".format(gmadname))
    else: # do it in /tmp/
        RebdsimOptics(bdsim_output_path, "{}/{}-optics.root".format(tmpdir, gmadname))
        return _Data.Load("{}/{}-optics.root".format(tmpdir, gmadname))


def Chunks(l, n):
    """ Yield successive n-sized chunks from list l."""
    return [l[i:i+n] for i in range(0,len(l),n)]


def Reduce(globcommand, nPerChunk, outputprefix):
    """
    Apply bdsimCombine to the globcommand set of files combining
    nPerchunks into an output file.

    ReduceRun("datadir/*.root", 10, "outputdir/")
    """

    files = _glob.glob(globcommand)
    print(len(files), "files to be combined in chunks of ", nPerChunk)

    # find number of integers required for output file name
    nchars = int(_np.ceil(_np.log10(len(files))))

    # append underscore if not a dir
    prefix = outputprefix if outputprefix.endswith('/') else outputprefix+"_"
    
    chunks = Chunks(files, nPerChunk)
    for i,chunk in enumerate(chunks):
        print('Chunk ',i)
        chunkName = prefix + str(i).zfill(nchars)+".root"
        command = "bdsimCombine "+chunkName + " " + " ".join(chunk)
        print(command)
        _os.system(command)


def _Combine(output, files):
    """Private function for parallelising reducing run."""
    command = "bdsimCombine " + output + " " + " ".join(files)
    print("Combinding ",files[0],"to",files[-1])
    _os.system(command)

    
def ReduceParallel(globcommand, nPerChunk, outputprefix, nCPUs=4):
    """
    In parallel, apply bdsimCombine to the globcommand set of files combining
    nPerChunk into an output file.

    chunkermp.ReduceRun("testfiles/*.root", 14, "testfiles-merge/", nCPUs=7)
    """
    files = _glob.glob(globcommand)
    print(len(files), "files to be combined in chunks of ", nPerChunk)

    # find number of integers required for output file name
    nchars = int(_np.ceil(_np.log10(len(files))))

    # append underscore if not a dir
    prefix = outputprefix if outputprefix.endswith('/') else outputprefix+"_"
    
    chunks = Chunks(files, nPerChunk)
    if len(chunks[-1]) == 1:
        chunks[-2].extend(chunks[-1])
        chunks.pop()
    chunkname = [prefix + str(i).zfill(nchars)+".root" for i in range(len(chunks))]

    p = _Pool(processes=nCPUs)
    p.starmap(_Combine, zip(chunkname, chunks))

def RenderGmadJinjaTemplate(template_file, output_file, data, path=".") :
    from jinja2 import Environment, FileSystemLoader
    import os

    # Set up Jinja2 environment and load the template file
    file_loader = FileSystemLoader(path)
    env = Environment(loader=file_loader)

    # Load the template from the file
    template = env.get_template(template_file)

    # Render the template with the data
    output = template.render(data)

    # Write output
    f = open(output_file,"w")
    f.write(output)
    f.close()

class Versions :
    """
    Retrieves and stores the versions of ROOT, Geant4, and CLHEP installed on the system.
    This class provides attributes for the detected versions of these dependencies by
    invoking their respective configuration commands. If a version cannot be found,
    the attribute will be set to "Not found".
    """

    def __init__(self):
        self.root_version = self._find_root_version()
        self.geant4_version = self._find_geant4_version()
        self.clhep_version = self._find_clhep_version()

    def _find_root_version(self) :
        try :
            result = _subprocess.run(["root-config","--version"], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except (FileNotFoundError, _subprocess.CalledProcessError):
            return "Not found"

    def _find_geant4_version(self) :
        try :
            result = _subprocess.run(["geant4-config","--version"], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except (FileNotFoundError, _subprocess.CalledProcessError):
            return "Not found"

    def _find_clhep_version(self) :
        try :
            result = _subprocess.run(["clhep-config","--version"], capture_output=True, text=True, check=True)
            parts = result.stdout.split()
            if len(parts) == 2 :
                return parts[1].strip()
            else :
                return "Not found"
        except (FileNotFoundError, _subprocess.CalledProcessError):
            return "Not found"