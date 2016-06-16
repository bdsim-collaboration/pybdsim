import os
import subprocess

import _General

class ExecOptions(dict):
    def __init__(self,*args,**kwargs):
        """
        Executable options class for BDSIM. In addition, 'bdsimcommand' is an extra
        allowed keyword argument that allows the user to specify the bdsim executable
        of their choice.

        bdsimcommand='bdsim-devel'
        bdsimcommand='/Users/nevay/physics/bdsim-build2/bdsim'

        Based on python dictionary but with parameter checking.
        """
        self.__dict__.__init__()
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
        for key,value in kwargs.iteritems():
            if key in self._okFlags or key in self._okArgs:
                self[key] = value
            else:
                raise ValueError(key+'='+str(value)+' is not a valid BDISM executable option')
        self.bdsimcommand = 'bdsim'
        if 'bdsimcommand' in self:
            self.bdsimcommand = self['bdsimcommand']
            self.pop("bdsimcommand", None)

    def GetExecFlags(self):
        result = dict((k,self[k]) for k in self.keys() if k in self._okFlags)
        return result

    def GetExecArgs(self):
        result = dict((k,self[k]) for k in self.keys() if k in self._okArgs)
        return result

class Study:
    """
    A holder for multiple runs.
    """
    def __init__(self):
        self.execoptions = [] # exec options
        self.outputnames = [] # file names
        self.outputsizes = [] # in bytes

    def GetInfo(index=-1):
        """
        Get info about a particular run.
        """
        i = index
        result = {'execoptions' : self.execoptions[i],
                  'outputname'  : self.outputnames[i],
                  'outputsize'  : self.outputsizes[i]}
        return result
                
    def Run(self, inputfile='optics.gmad',
            output='rootevent',
            outfile='output',
            ngenerate=1,
            bdsimcommand='bdsim-devel'):
        eo = ExecOptions(file=inputfile, output=output, outfile=outfile, ngenerate=ngenerate)
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
        for k,v in eo.GetExecArgs().iteritems():
            command += ' --' + str(k) + '=' + str(v)
        if debug:
            print 'Command is'
            print command

        # send it to a log file
        outfilename = 'output'
        if 'outfile' in eo:
            outfilename = eo['outfile']
        command += ' > ' + outfilename + '.log'
        
        # execute process
        if debug:
            print 'BDSIM Run'
        try:
            subprocess.check_call(command, shell=True)
        except subprocess.CalledProcessError:
            print 'ERROR'
            return
        
        # get output file name - the latest file in the directory hopefully
        outfilename = _General.GetLatestFileFromDir(extension='*root') # this directory

        # record info
        self.execoptions.append(eo)
        self.outputnames.append(outfilename)
        self.outputsizes.append(os.path.getsize(outfilename))
