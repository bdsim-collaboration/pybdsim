import pymadx.Ptc
import pymadx.Beam
import pymadx.Builder
import pymadx.Tfs
import pybdsim.Beam
import pybdsim.Builder
import pybdsim.Data
import pybdsim.Convert
import os as _os
import matplotlib.pyplot as _plt
import robdsim
import numpy as _np


class FodoTest:
    def __init__(self,filename,foldername=None):
            if filename[-5:] == '.madx':                
                self.filename=filename[:-5]
                self.foldername=foldername
                if self.foldername != None:
                    self.usingfolder = True
                    self.filepath = self.foldername+'/'+self.filename
                    _os.system("mkdir -p " + self.foldername)
                else:
                    self.usingfolder = False
                    self.filepath=self.filename
                    self.figureNr = 1729
            else:
                print "IOError: Not a valid file format!"   ###make this standard


    def Run(self):
        print 'Test> FODO:' 
        print 'Test> Destination filepath: ',self.filepath

        if self.usingfolder:
            _os.chdir(self.foldername)

        _os.system("madx < "+self.filename+".madx > madx.log")

        pybdsim.Convert.MadxTfs2Gmad("fodo.tfs","fodo")

        _os.system("bdsim --file=fodo.gmad --ngenerate=50000 --batch --output=root --outfile=fodo > bdsim.log")

        madx = pymadx.Tfs("fodo.tfs")
        Ms = madx.GetColumn('S') # convert from m to um
        Mbetx = madx.GetColumn('BETX') 
        Mbety = madx.GetColumn('BETY')

        bdsim = robdsim.robdsimOutput('fodo.root')
        bdsim.CalculateOpticalFunctions('fodo_optics.dat')
        bdata = pybdsim.Data.Load('fodo_optics.dat')
        Bs    = bdata.S()
        Bbetx = bdata.Beta_x()
        Bbety = bdata.Beta_y()

        _plt.clf()
        _plt.plot(Ms,Mbetx) 
        _plt.plot(Ms,Mbety)
        _plt.plot(Bs,Bbetx,"b+--")
        _plt.plot(Bs,Bbety,"g+--")
                
        if self.usingfolder:
            _os.chdir("../")

    
    def Clean(self):        
        _os.system("rm -rf fodo*")
        _os.system("rm -rf *.log")
        _os.system("rm -rf *.dat")
        _os.system("rm -rf *.tfs")
        _os.system("rm -rf *.ps")


        

            

        
            


        

    

