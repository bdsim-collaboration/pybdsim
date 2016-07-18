import pickle as _pkl
import pylab  as _pl
import pymad8 as _pymad8
from .. import Data as _Data
import matplotlib.pyplot as _plt

class Mad8Bdsim :
    def __init__(self, 
                 bdsimFileName = "output.pickle",
                 mad8TwissFileName   = "ebds1.twiss",
                 mad8EnvelopeFileName = "ebds1.envelope") : 
        # load bdsim data
        f = open(bdsimFileName) 
        self.bdsimData = _pkl.load(f)
        self.bdsimOptics = self.bdsimData['optics']
        f.close()

        # load mad8 data
        r = _pymad8.Mad8.OutputReader()    
        [self.c,self.mad8Envel] = r.readFile(mad8EnvelopeFileName,"envel")
        [self.c,self.mad8Twiss] = r.readFile(mad8TwissFileName,"twiss")

    def plotSigma(self) : 
        figure = _plt.figure()
        gs  = _plt.GridSpec(3,1,height_ratios=[1,3,3])
        ax0 = figure.add_subplot(gs[0],projection="_My_Axes")
        _pymad8.Plot.drawMachineLattice(self.c,self.mad8Twiss)   

        ax1 = _plt.subplot(gs[1])
        _pl.plot(self.mad8Envel.getColumn('suml'),_pl.sqrt(self.mad8Envel.getColumn('s11'))*1e6,"+-",label="MAD8")
        _pl.plot(self.bdsimOptics['S'],self.bdsimOptics['Sigma_x']/1e-6,"x--",label="BDSIM")
        _pl.xlim(0,2275)
        _pl.ylim(0,3000)
        _pl.legend(loc=0)
        _pl.ylabel("$\\sigma_x$ [$\mu$m]")

        ax2 = _plt.subplot(gs[2])
        _pl.plot(self.mad8Envel.getColumn('suml'),_pl.sqrt(self.mad8Envel.getColumn('s33'))*1e6,"+-")
        _pl.plot(self.bdsimOptics['S'],self.bdsimOptics['Sigma_y']/1e-6,"x--")
        _pl.xlim(0,2275)
        _pl.ylim(0,100)
        _pl.ylabel("$\\sigma_y$ [$\mu$m]")
        _pl.xlabel("$S$ [m]")

        _pymad8.Plot.setCallbacks(figure,ax0,ax1)
        _pymad8.Plot.setCallbacks(figure,ax0,ax2)

        _pl.savefig("mad8bdsim_sigma.pdf")


    
    def plotBeta(self) : 
        figure = _plt.figure()
        gs  = _plt.GridSpec(3,1,height_ratios=[1,3,3])
        ax0 = figure.add_subplot(gs[0],projection="_My_Axes")
        _pymad8.Plot.drawMachineLattice(self.c,self.mad8Twiss)  

        _pl.clf()
        ax1 = _pl.subplot(gs[1])
        _pl.plot(self.mad8Envel.getColumn('suml'),_pl.sqrt(self.mad8Twiss.getColumn('betx')),"+-")
        _pl.plot(self.bdsimOptics['S'],_pl.sqrt(self.bdsimOptics['Beta_x']),"+--")
        _pl.ylabel("$\\beta_x$")

        ax2 = _pl.subplot(gs[2])
        _pl.plot(self.mad8Envel.getColumn('suml'),_pl.sqrt(self.mad8Twiss.getColumn('bety')),"+-")
        _pl.plot(self.bdsimOptics['S'],_pl.sqrt(self.bdsimOptics['Beta_y']),"+--")
        _pl.ylabel("$\\beta_y$")
        _pl.xlabel("$S$ [m]")

        _pymad8.Plot.setCallbacks(figure,ax0,ax1)
        _pymad8.Plot.setCallbacks(figure,ax0,ax2)
    
        _pl.savefig("mad8bdsim_beta.pdf")


    def plotDispersion(self) :
        figure = _plt.figure()
        gs  = _plt.GridSpec(3,1,height_ratios=[1,3,3])
        ax0 = figure.add_subplot(gs[0],projection="_My_Axes")
        _pymad8.Plot.drawMachineLattice(self.c,self.mad8Twiss)  

        ax1 = _pl.subplot(gs[1])
        ax1.set_autoscale_on(True)
        _pl.plot(self.mad8Envel.getColumn('suml'),self.mad8Twiss.getColumn('dx'),"+-",label="MAD8")
        _pl.plot(self.bdsimOptics['S'],self.bdsimOptics['Disp_x'],"+--",label="BDSIM") # 4000 1/250*1e6
        _pl.ylabel("$\\eta_x$ [m]")

        ax2 = _pl.subplot(gs[2])
        ax2.set_autoscale_on(True)
        _pl.plot(self.mad8Envel.getColumn('suml'),self.mad8Twiss.getColumn('dy'),"+-",label="MAD8")
        _pl.plot(self.bdsimOptics['S'],self.bdsimOptics['Disp_y'],"+--",label="BDSIM") # 4000 1/250*1e6
        _pl.ylabel("$\\eta_y$ [m]")
        _pl.xlabel("$S$ [m]")
        
        _pl.legend(loc=0)

        _pymad8.Plot.setCallbacks(figure,ax0,ax1)
        _pymad8.Plot.setCallbacks(figure,ax0,ax2)

        _pl.savefig("mad8bdsim_eta.pdf")
