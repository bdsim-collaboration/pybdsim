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
        _pl.plot(self.mad8Envel.getColumn('suml'),_pl.sqrt(self.mad8Envel.getColumn('s11'))*1e6,"+-")
        _pl.plot(self.bdsimData.S(),self.bdsimData.Sigma_x(),"+--")
        _pl.ylabel("$\\sigma_x$")

        _pl.subplot(2,1,2)
        _pl.plot(self.mad8Envel.getColumn('suml'),_pl.sqrt(self.mad8Envel.getColumn('s33'))*1e6,"+-")
        _pl.plot(self.bdsimData.S(),self.bdsimData.Sigma_y(),"+--")
        _pl.ylabel("$\\sigma_y$")
        _pl.xlabel("$S$ [m]")
    
    def plotBeta(self) : 
        _pl.subplot(2,1,1)
        _pl.plot(self.mad8Envel.getColumn('suml'),_pl.sqrt(self.mad8Twiss.getColumn('betx'))*1e6,"+-")
        _pl.plot(self.bdsimData.S(),_pl.sqrt(self.bdsimData.Beta_x()),"+--")
        _pl.ylabel("$\\beta_x$")

        _pl.subplot(2,1,2)
        _pl.plot(self.mad8Envel.getColumn('suml'),_pl.sqrt(self.mad8Twiss.getColumn('bety'))*1e6,"+-")
        _pl.plot(self.bdsimData.S(),_pl.sqrt(self.bdsimData.Beta_y()),"+--")
        _pl.ylabel("$\\beta_y$")
        _pl.xlabel("$S$ [m]")
        pass
