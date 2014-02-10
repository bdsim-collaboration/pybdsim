# pybdsim.Beam - generate BDSIM beam
# Version 1.0
# L. Nevay
# laurie.nevay@rhul.ac.uk

class Beam(dict):
    def __init__(self,particletype='e-',energy=1.0,distrtype='reference',*args,**kwargs):
        dict.__init__(self,*args,**kwargs)
        self.SetParticleType(particletype)
        self.SetEnergy(energy)
        self.SetDistributionType(distrtype)
        
    def SetParticleType(self,particletype='e-'):
        particlelist = [
            'e-',
            'e+',
            'proton',
            'gamma',
        ]
        if particletype not in particlelist:
            raise ValueError("Unknown particle type: '"+str(particletype)+"'")
        self['particle'] = '"' + str(particletype) + '"'

    def SetEnergy(self,energy=1.0,unitsstring='GeV'):
        self['energy'] = str(energy) + '*' + unitsstring

    def SetDistributionType(self,distrtype='reference'):
        self['distrType'] = '"' + distrtype + '"'
        if distrtype == 'reference':
            pass
        elif distrtype == 'gauss':
            setattr(Beam, 'SetSigmaX',     _SetSigmaX)
            setattr(Beam, 'SetSigmaY',     _SetSigmaY)
            setattr(Beam, 'SetSigmaE',     _SetSigmaE)
            setattr(Beam, 'SetSigmaXP',    _SetSigmaXP)
            setattr(Beam, 'SetSigmaYP',    _SetSigmaYP)
            setattr(Beam, 'SetSigmaT',     _SetSigmaT)
        elif distrtype == 'gausstwiss':
            setattr(Beam, 'SetBetaX',      _SetBetaX)
            setattr(Beam, 'SetBetaY',      _SetBetaY)
            setattr(Beam, 'SetAlphaX',     _SetAlphaX)
            setattr(Beam, 'SetAlphaY',     _SetAlphaY)
            setattr(Beam, 'SetEmittanceX', _SetEmittanceX)
            setattr(Beam, 'SetBmittanceY', _SetEmittanceY)
            setattr(Beam, 'SetSigmaE',     _SetSigmaE)
            setattr(Beam, 'SetSigmaT',     _SetSigmaT)
        elif distrtype == 'eshell':
            setattr(Beam, 'SetShellX',     _SetShellX)
            setattr(Beam, 'SetShellY',     _SetShelly)
            setattr(Beam, 'SetShellXP',    _SetShellXP)
            setattr(Beam, 'SetShellYP',    _SetShellYP)
        elif distrtype == 'ring':
            setattr(Beam, 'SetRMin',       _SetRMin)
            setattr(Beam, 'SetRMax',       _SetRMax)
        else:
            raise ValueError('unkonwn distribution type')

    
    def ReturnBeamString(self):
        s = ''
        for k,v in self.iteritems():
            s += ', \n\t'+str(k)+'='+str(v)
        s += ';'
        s2 = s.split('\n')
        s3 = 'beam,\t'+s2[1].replace('\t','').replace('\n','').replace(',','').strip()+',\n'
        s4 = '\n'.join(s2[2:])
        st = s3+s4
        return st

    def SetX0(self,x0=0.0,unitsstring='m'):
        self['X0'] = x0 + '*' + unitsstring

    def SetY0(self,y0=0.0,unitsstring='m'):
        self['Y0'] = y0 + '*' + unitsstring

    def SetZ0(self,z0=0.0,unitsstring='m'):
        self['Z0'] = z0 + '*' + unitsstring

    def SetXP0(self,xp0=0.0):
        self['Xp0'] = xp0

    def SetYP0(self,yp0=0.0):
        self['Yp0'] = yp0

    def SetZP0(self,zp0=0.0):
        self['Zp0'] = zp0

    def SetT0(self,t0=0.0,unitsstring='s'):
        self['T0'] = t0 + '*' + unitsstring


def _SetSigmaX(self,sigmax=1.0,unitsstring='um'):
    self['sigmaX'] = str(sigmax) + '*' + unitsstring

def _SetSigmaY(self,sigmay=1.0,unitsstring='um'):
    self['sigmaY'] = str(sigmay) + '*' + unitsstring

def _SetSigmaE(self,sigmae=0.001):
    """
    fractional energy spread
    """
    self['sigmaE'] = sigmae

def _SetSigmaXP(self,sigmaxp=1.0):
    self['sigmaXp'] = sigmaxp

def _SetSigmaYP(self,sigmayp=1.0):
        self['sigmaYp'] = sigmayp

def _SetSigmaT(self,sigmat=1.0,unitsstring='um'):
        self['sigmaT'] = sigmat

def _SetBetaX(self,betx=1.0,unitsstring='m'):
    self['betx'] = str(betx) + '*' + unitsstring

def _SetBetaY(self,bety=1.0,unitsstring='m'):
    self['bety'] = str(bety) + '*' + unitsstring

def _SetAlphaX(self,alphax=1.0,unitsstring='m'):
    self['alfx'] = str(alphax) + '*' + unitsstring

def _SetAlpgaY(self,alphay=1.0,unitsstring='m'):
    self['alfy'] = str(alphay) + '*' + unitsstring

def _SetEmittanceX(self,emitx=1.0,unitsstring='um'):
    self['emitx'] = str(emitx) + '*' + unitsstring
   
def _SetEmittanceY(self,emity=1.0,unitsstring='um'):
    self['emity'] = str(emity) + '*' + unitsstring

def _SetShellX(self,shellx=1.0,unitsstring='m'):
    self['shellX'] = str(shellx) + '*' + unitsstring

def _SetShellY(self,shelly=1.0,unitsstring='m'):
    self['shellY'] = str(shelly) + '*' + unitsstring

def _SetShellXP(self,shellxp=1.0):
    self['shellXp'] = shellxp

def _SetShellYP(self,shellyp=1.0):
    self['shellYp'] = shellyp

def _SetRMin(self,rmin=0.9,unitsstring='mm'):
    if self.has_key('Rmax') == True:
        if self['Rmax'] < rmin:
            raise ValueError('Rmax must be > RMin')
    self['Rmin'] = str(rmin) + '*' + unitsstring
    
def _SetRMax(self,rmax=1.0,unitsstring='mm'):
    if self.has_key('Rmin') == True:
        if self['Rmin'] > rmax:
            raise ValueError('Rmin must be < RMax')
    self['Rmax'] = str(rmax) + '*' + unitsstring

    

    

