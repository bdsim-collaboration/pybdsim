"""
Read and write gmad options files

Options - bdsim options class
Beam    - bdsim beam options class

Example:

a = Options() # sets up default parameters
#now customise...
a.SetBeamPipeRadius(10)
a.SetBeamPipeRadius? #to see instructions and units
a.Write('myoptions.gmad')

a = Beam()
a.SetParticle('proton')
a.Write('beam.gmad')

"""

class Options : 
    def __init__(self) : 
        print 'Options.Options.__init__>'
        self.optionDict = dict() 
        self.optionDict['beampipeRadius']      = '10 * cm'
        self.optionDict['boxSize']             = '1.9 * m'
        self.optionDict['tunnelRadius']        = '2.0 * m'
        self.optionDict['beampipeThickness']   = '0.5 * cm'
        self.optionDict['chordStepMinimum']    = '0.0000000001 * m'
        self.optionDict['deltaIntersection']   = '0.00000001 * m'
        self.optionDict['deltaChord']          = '0.001 * m'
        self.optionDict['lengthSafety']        = '0.00001 * m'
        self.optionDict['thresholdCutCharged'] = '100 * MeV'
        self.optionDict['thresholdCutPhotons'] = '1000 * KeV'
        self.optionDict['physicsList']         = '"standard"'
        self.optionDict['ngenerate']           = '10'
        
    def Write(self, fileName='options.gmad'):
        if fileName[-4:] != '.gmad':
            fileName += '.gmad'
        f = open(fileName,'w')
        for k in self.optionDict : 
            f.write('option, '+k+' = '+self.optionDict[k]+';\n')
        f.close() 

    def SetBeamPipeRadius(self,value) : 
        ''' Set Beampipe radius in cm ''' 
        self.optionDict['beampipeRadius'] = str(value)+' * cm'
        
    def SetBoxSize(self,value) : 
        ''' Set Boxsize in m '''         
        self.optionDict['boxSize'] = str(value)+' * m'

    def SetTunnelRadius(self,value) : 
        ''' Set Tunnel radius in m '''         
        self.optionDict['tunnelRadius'] = str(value)+' * m'

    def SetBeamPipeThickness(self,value) : 
        ''' Set Beampipe thickness in cm '''                 
        self.optionDict['beampipThickness'] = str(value)+' * cm'
    
    def SetChordStepMinimum(self,value) : 
        ''' Set Chord Step Minimum in m'''                 
        self.optionDict['chordStepMinimum'] = str(value)+' * m'        

    def SetDeltaIntersection(self,value) : 
        ''' Set Delta Intersection  in m '''                 
        self.optionDict['deltaIntersection'] = str(value)+' * m'        

    def SetDeltaChord(self,value) : 
        ''' Set delta intersection in m '''                 
        self.optionDict['deltaIntersection'] = str(value)+' * m'        

    def SetLengthSafety(self,value) : 
        ''' Set Length Safety in m'''                 
        self.optionDict['lengthSafety'] = str(value)+' * m'        

    def SetThresoldCutCharged(self,value) : 
        ''' Set Threshold Cut Charged in  MeV '''                 
        self.optionDict['thresholdCutCharged'] = str(value)+' * MeV'        

    def SetThresholdCutPhotons(self,value) : 
        ''' Set Beampipe thickness in cm '''                 
        self.optionDict['thresholdCutPhotons'] = str(value)+' * MeV'        

    def SetPhysicsList(self,value) : 
        ''' Set Physics list'''                 
        self.optionDict['physicsList'] = '"'+value+'"'

    def SetNGenerate(self,value) : 
        ''' Set number of particles to generate''' 
        self.optionDict['ngenerate'] = str(value)


class Beam:
    def __init__(self):
        self.beamDict = dict()
        self.beamDict['particle']              = '"e-"'
        self.beamDict['energy']                = '1.5405110 * GeV'
        self.beamDict['distrType']             = '"gauss"'
        self.beamDict['sigmaX']                = '0.002 * mm'
        self.beamDict['sigmaY']                = '0.002 * mm'
        self.beamDict['sigmaXp']               = '0.02*0.005'
        self.beamDict['sigamYp']               = '0.02*0.004'
   
    def Write(self, fileName='beam.gmad'):
        if fileName[-4:] != '.gmad':
            fileName += '.gmad'
        f = open(fileName,'w')
        for k in self.beamDict : 
            f.write('option, '+k+' = '+self.beamDict[k]+';\n')
        f.close()
     
    def SetParticle(self, value) : 
        ''' Set Particle type ''' 
        self.beamDict['particle'] = '"'+value+'"'
    
    def SetEnergy(self, value) : 
        ''' Set energy in GeV ''' 
        self.beamDict['energy'] = str(value)+' * GeV'
        
    def SetDistributionType(self,value) :
        ''' Set distribution type ''' 
        self.beamDict['distrType'] = value 

    def SetSigmaX(self,value) : 
        ''' Set SigmaX in mm ''' 
        self.beamDict['sigmaX'] = str(value)+' * mm';

    def SetSigmaY(self,value) : 
        ''' Set SigmaX in mm ''' 
        self.beamDict['sigmaY'] = str(value)+' * mm';

    def SetSigmaXp(self,value) : 
        ''' Set SigmaX in mm ''' 
        self.beamDict['sigmaXp'] = str(value);

    def SetSigmaXp(self,value) : 
        ''' Set SigmaX in mm ''' 
        self.beamDict['sigmaYp'] = str(value);
