import pylab as _pl
import pymad8 
from .. import Data

class Mad8Bdsim :
    def __init__(self, bdsimFileName = "output_0.dat",
                 mad8TwissFileName   = "ebds1.twiss",
                 mad8EnvelopeFileName = "ebds1.envelope") : 
        # load bdsim data
        self.bdsimData = Data.Load(bdsimFileName)

        # load mad8 data
        r = pymad8.Mad8.OutputReader()    
        [self.c,self.mad8Envel] = r.readFile(mad8EnvelopeFileName,"envel")
        [self.c,self.mad8Twiss] = r.readFile(mad8TwissFileName,"twiss")

    def plotSigma(self) : 
        _pl.subplot(2,1,1)
        _pl.plot(self.mad8Envel.getColumn('suml'),_pl.sqrt(self.mad8Envel.getColumn('s11'))*1e6,"+-",label="MAD8")
        _pl.plot(self.bdsimData.S(),self.bdsimData.Sigma_x(),"x--",label="BDSIM")
        _pl.xlim(0,2275)
        _pl.ylim(0,3000)
        _pl.legend(loc=0)
        _pl.ylabel("$\\sigma_x$ [$\mu$m]")

        _pl.subplot(2,1,2)
        _pl.plot(self.mad8Envel.getColumn('suml'),_pl.sqrt(self.mad8Envel.getColumn('s33'))*1e6,"+-")
        _pl.plot(self.bdsimData.S(),self.bdsimData.Sigma_y(),"x--")
        _pl.xlim(0,2275)
        _pl.ylim(0,100)
        _pl.ylabel("$\\sigma_y$ [$\mu$m]")
        _pl.xlabel("$S$ [m]")

        _pl.savefig("mad8bdsim_sigma.pdf")
    
    def plotBeta(self) : 
        _pl.subplot(2,1,1)
        _pl.plot(self.mad8Envel.getColumn('suml'),_pl.sqrt(self.mad8Twiss.getColumn('betx')),"+-")
        _pl.plot(self.bdsimData.S(),_pl.sqrt(self.bdsimData.Beta_x()),"+--")
        _pl.ylabel("$\\beta_x$")

        _pl.subplot(2,1,2)
        _pl.plot(self.mad8Envel.getColumn('suml'),_pl.sqrt(self.mad8Twiss.getColumn('bety')),"+-")
        _pl.plot(self.bdsimData.S(),_pl.sqrt(self.bdsimData.Beta_y()),"+--")
        _pl.ylabel("$\\beta_y$")
        _pl.xlabel("$S$ [m]")
    
        _pl.savefig("mad8bdsim_beta.pdf")


    def plotDispersion(self) :
        _pl.subplot(2,1,1)
        _pl.plot(self.mad8Envel.getColumn('suml'),self.mad8Twiss.getColumn('dx'),"+-",label="MAD8")
        _pl.plot(self.bdsimData.S(),self.bdsimData.Disp_x()/4000.0,"+--",label="BDSIM") # 4000 1/250*1e6
        _pl.ylabel("$\\eta_x$ [m]")

        _pl.subplot(2,1,2)
        _pl.plot(self.mad8Envel.getColumn('suml'),self.mad8Twiss.getColumn('dy'),"+-",label="MAD8")
        _pl.plot(self.bdsimData.S(),self.bdsimData.Disp_y()/4000.0,"+--",label="BDSIM") # 4000 1/250*1e6
        _pl.ylabel("$\\eta_y$ [m]")
        _pl.xlabel("$S$ [m]")
        
        _pl.legend(loc=0)

        _pl.savefig("mad8bdsim_eta.pdf")
