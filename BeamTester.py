# NOTE 'Tester' was moved to pygmad/Options.py
# this will need to be finished and updated appropriately
# before being included in pybdsim

import Tester as _Tester 

class BeamTester(_Tester.Tester) : 
    def __init__(self, particle = 'e-', energy = 1.5, distribution = 'gauss') :
        print 'BeamTester.BeamTester.__init__>'
        _Tester.Tester()

        self.particle     = particle 
        self.energy       = energy 
        self.distribution = distribution
    
    def makeOptions(self) : 
        pass

    def makeBeam(self) : 
        pass 

    def makeLattice(self) : 
        pass

    def run(self) :
        pass
    
    def plotOutput(self) :
        pass

