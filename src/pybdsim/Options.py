"""
See Options class inside this module.

"""

def ProtonColliderOptions():
    a = Options()
    a.SetPhysicsList('FTFP_BERT')
    a.SetBeamPipeThickness(5,'mm')
    a.SetOuterDiameter(0.5, 'm')
    a.SetTunnelRadius(2, 'm')
    a.SetNGenerate(100)
    a.SetBeamPipeRadius(5,'cm')
    a.SetBuildTunnel(True)
    a.SetBuildTunnelFloor(True)
    a.SetTunnelRadius(2,'m')
    a.SetTunnelThickness(50,'cm')
    a.SetTunnelOffsetX(1,'m')
    a.SetTunnelFloorOffset(1,'m')
    return a

def ElectronColliderOptions():
    a = Options()
    a.SetPhysicsList('em')
    a.SetBeamPipeThickness(5,'mm')
    a.SetOuterDiameter(1,'m')
    a.SetTunnelRadius(2,'m')
    a.SetNGenerate(100)
    a.SetDefaultRangeCut(0.25,"m")
    a.SetBeamPipeRadius(5,'cm')
    a.SetBuildTunnel(True)
    a.SetBuildTunnelFloor(True)
    a.SetTunnelRadius(2,'m')
    a.SetTunnelThickness(50,'cm')
    a.SetTunnelOffsetX(1,'m')
    a.SetTunnelFloorOffset(1,'m')
    return a

class Options(dict):
    """
    Inherits a dict. Converting to a string or using
    ReturnOptionsString() will give a suitable GMAD
    string to write out to a file.

    o = pybdsim.Options.Options()
    o["trajectoryConnect"] = 1
    o["aper1"] = (5, 'm')
    str(o)
    'option,\ttrajectoryConnect=1,\n\taper1=5*m;'

    There is no checking on the option if using []. A tuple
    of (value, unitsString) can be used too resulting in
    value*unitsString.
    """
    def __init__(self,*args,**kwargs):
        dict.__init__(self,*args,**kwargs)

    def __repr__(self):
        return self.ReturnOptionsString()

    def SetGeneralOption(self, option, value):
        self[option] = value

    def ReturnOptionsString(self):
        s = ''
        if len(list(self.keys())) == 0:
            #print 'No options set - empty string'
            return s
        
        numOptions=0
        for k,v in self.items():
            if type(v) is tuple:
                vs = str(v[0]) + "*" + v[1]
            else:
                vs = str(v)
            s += ', \n\t'+str(k)+'='+vs
            numOptions += 1
        s += ';'
        s2 = s.split('\n')
        s3 = 'option,\t'+s2[1].replace('\t','').replace('\n','').replace(',','').strip()
        if numOptions == 1:
            s3 += '\n'
        else:
            s3 += ',\n'
        s4 = '\n'.join(s2[2:])
        st = s3+s4
        return st

    def SetNGenerate(self, nparticles=1):
        self['ngenerate'] = nparticles

    def SetPhysicsList(self, physicslist=''):
        physicslistlist = [
            'all_particles',
            'annihi_to_mumu',
            'charge_exchange',
            'cherenkov',
            'cuts_and_limits',
            'decay',
            'decay_radioactive',
            'em',
            'em_extra',
            'em_livermore',
            'em_livermore_polarised',
            'em_low_ep',
            'em_penelope',
            'em_low', # alias to em_penelope
            'em_ss',
            'em_wvi',
            'em_1',
            'em_2',
            'em_3',
            'em_4',
            'ftfp_bert',
            'ftfp_bert_hp',
            'hadronic', # alias to ftfp_bert
            'hadronichp', # alias to ftfp_bert_hp
            'hadronic_elastic',
            'hadronic_elastic_d',
            'hadronic_elastic_h',
            'hadronic_elastic_hp',
            'hadronic_elastic_lend',
            'hadronic_elastic_xs',
            'ion',
            'ion_binary',
            'ion_elastic',
            'ion_elastic_qmd',
            'ion_em_dissociation',
            'ion_inclxx',
            'lw',
            'muon',
            'neutron_tracking_cut',
            'optical',
            'qgsp_bert',
            'qgsp_bert_hp',
            'qgsp_bic',
            'qgsp_bic_hp',
            'shielding',
            'stopping',
            'synch_rad',
            'synchrad', # alias to synch_rad
            'em_gs',
            'decay_spin',
            'ion_php',
            'decay_muonic_atom',
            'channelling',
            'dna',
            'dna_1',
            'dna_2',
            'dna_2',
            'dna_3',
            'dna_4',
            'dna_5',
            'dna_6',
            'dna_7',
            'radioactivation',
            'shielding_lend'
            ]
        if len(physicslist.split()) == 1:
            if physicslist not in physicslistlist and not physicslist.startswith("g4"):
                print('Warning: unknown physicslist: '+physicslist)
            self['physicsList'] = '"' + str(physicslist) + '"'
        else:
            splitphysicslist = physicslist.split()
            for token in splitphysicslist :
                if token not in physicslistlist :
                    print('Warning: unknown physicslist: '+physicslist)

            self['physicsList'] = '"' + str(physicslist) + '"'

    def SetBeamPipeRadius(self, beampiperadius=5.0, unitsstring='cm'):
        self['beampipeRadius'] = str(beampiperadius) + '*' +unitsstring
        
    def SetOuterDiameter(self, outerdiameter=2.0, unitsstring='m'):
        self['outerDiameter'] = str(outerdiameter) + '*' + unitsstring

    def SetTunnelRadius(self, tunnelradius=2.0, unitsstring='m'):
        self['tunnelRadius'] = str(tunnelradius) + '*' + unitsstring

    def SetBeamPipeThickness(self, bpt, unitsstring='mm'):
        self['beampipeThickness'] = str(bpt) + '*' + unitsstring

    def SetPipeMaterial(self, bpm):
        self['pipeMaterial'] = '"' + str(bpm) + '"'

    def SetVacuumMaterial(self, vm):
        self['vacMaterial'] = '"' + str(vm) + '"'

    def SetVacuumPressure(self, vp):
        """
        Vacuum pressure in bar
        """
        self['vacuumPressure'] = str(vp)

    def SetBuildTunnel(self, tunnel=False):
        self['buildTunnel'] = int(tunnel)

    def SetBuildTunnelFloor(self, tunnelfloor=False):
        self['buildTunnelFloor'] = int(tunnelfloor)

    def SetTunnelThickness(self, tt=1.0, unitsstring='m'):
        self['tunnelThickness'] = str(tt) + '*' + unitsstring

    def SetSoilThickness(self, st=4.0, unitsstring='m'):
        self['tunnelSoilThickness'] = str(st) + '*' + unitsstring

    def SetTunnelMaterial(self, tm):
        self['tunnelMaterial'] = '"' + str(tm) + '"'

    def SetSoilMaterial(self, sm):
        self['soilMaterial'] = '"' + str(sm) + '"'

    def SetTunnelOffsetX(self, offset=0.0, unitsstring='m'):
        self['tunnelOffsetX'] = str(offset) + '*' + unitsstring

    def SetTunnelOffsetY(self, offset=0.0, unitsstring='m'):
        self['tunnelOffsetY'] = str(offset) + '*' + unitsstring

    def SetTunnelFloorOffset(self, offset=1.0, unitsstring='m'):
        self['tunnelFloorOffset'] = str(offset) + '*' + unitsstring

    def SetSamplerDiameter(self, radius=10.0, unitsstring='m'):
        self['samplerDiameter'] = str(radius) + '*' + unitsstring

    def SetBLMRadius(self, radius=5.0, unitsstring='cm'):
        self['blmRad'] = str(radius) + '*' + unitsstring

    def SetBLMLength(self, length=50.0, unitsstring='cm'):
        self['blmLength'] = str(length) + '*' + unitsstring

    def SetIncludeIronMagField(self, iron=True):
        self['includeIronMagFields'] = int(iron)

    def SetDontSplitSBends(self, dontsplitsbends=False):
        self['dontSplitSBends'] = int(dontsplitsbends)

    def SetDeltaChord(self, dc=0.001, unitsstring='m'):
        self['deltaChord'] = str(dc) + '*' + unitsstring

    def SetDeltaIntersection(self, di=10.0, unitsstring='nm'):
        self['deltaIntersection'] = str(di) + '*' + unitsstring

    def SetChordStepMinimum(self, csm=1.0, unitsstring='nm'):
        self['chordStepMinimum'] = str(csm) + '*' + unitsstring

    def SetLengthSafety(self, ls=10.0, unitsstring='um'):
        self['lengthSafety'] = str(ls) + '*' + unitsstring

    def SetMinimumEpsilonStep(self, mes=10.0, unitsstring='nm'):
        self['minimumEpsilonStep'] = str(mes) + '*' + unitsstring

    def SetMaximumEpsilonStep(self, mes=1.0, unitsstring='m'):
        self['maximumEpsilonStep'] = str(mes) + '*' + unitsstring

    def SetDeltaOneStep(self, dos=10.0, unitsstring='nm'):
        self['deltaOneStep'] = str(dos) + '*' + unitsstring

    def SetMaximumStepLength(self, msl=20.0, unitsstring='m'):
        self['maximumStepLength'] = str(msl) + '*' + unitsstring

    def SetMaximumTrackingTime(self, mtt=-1.0, unitsstring='s'):
        self['maximumTrackingTime'] = str(mtt) + '*' + unitsstring

    def SetIntegratorSet(self, integratorSet='"bdsim"'):
        self['integratorSet'] = integratorSet

    def SetThresholdCutCharged(self, tcc=100.0, unitsstring='MeV'):
        self['thresholdCutCharged'] = str(tcc) + '*' + unitsstring

    def SetThresholdCutPhotons(self, tcp=1.0, unitsstring='MeV'):
        self['thresholdCutPhotons'] = str(tcp) + '*' + unitsstring

    def SetStopSecondaries(self, stop=True):
        self['stopSecondaries'] = int(stop)

    def SetSynchRadiationOn(self, on=True):
        self['synchRadOn'] = int(on)

    def SetTrackSRPhotons(self, track=True):
        self['srTrackPhotons'] = int(track)

    def SetSRLowX(self, lowx=True):
        self['srLowX'] = int(lowx)

    def SetSRMultiplicity(self, srm=2.0):
        self['srMultiplicity'] = srm

    def SetProductionCutPhotons(self, pc=100.0, unitsstring='keV'):
        self['prodCutPhotons'] = str(pc) + '*' + unitsstring

    def SetProductionCutElectrons(self, pc=100.0, unitsstring='keV'):
        self['prodCutElectrons'] = str(pc) + '*' + unitsstring

    def SetProductionCutPositrons(self, pc=100.0, unitsstring='keV'):
        self['prodCutPositrons'] = str(pc) + '*' + unitsstring

    def SetCherenkovOn(self, on=True):
        self['turnOnCerenkov'] = int(on)

    def SetDefaultRangeCut(self, drc=0.7, unitsstring='mm'):
        self['defaultRangeCut'] = str(drc) + '*' + unitsstring

    def SetGamma2MuonEnahncementFactor(self, ef=1.0):
        self['gammToMuFe'] = ef

    def SetEPAnnihilation2MuonEnhancementFactor(self, ef=1.0):
        self['annihiToMuFe'] = ef

    def SetEPAnnihilation2HadronEnhancementFactor(self, ef=1.0):
        self['eetoHadronsFe'] = ef

    def SetEMLeadParticleBiasing(self, on=True):
        self['useEMLPB'] = int(on)

    def SetLPBFraction(self, fraction=0.5):
        self['LPBFraction'] = fraction

    def SetRandomSeed(self, rs=0):
        self['randomSeed'] = rs

    def SetNGenerate(self, nparticles=10):
        self['ngenerate'] = nparticles

    def SetWritePrimaries(self, on=True):
        self['writePrimaries'] = int(on)

    def SetELossHistBinWidth(self,width):
        self['elossHistoBinWidth'] = width

    def SetSensitiveBeamlineComponents(self, on=True):
        self['sensitiveBeamLineComponents'] = int(on)

    def SetSensitiveBeamPipe(self, on=True):
        self['sensitiveBeamPipe'] = int(on)

    def SetSenssitiveBLMs(self, on=True):
        self['sensitiveBLMs'] = int(on)

    def SetStoreTrajectory(self, on=True):
        self['storeTrajectory'] = int(on)

    def SetStoreTrajectoryParticle(self, particle="muon"):
        self['storeTrajectoryParticle'] = particle

    def SetMagnetGeometryType(self, magnetGeometryType='"none"'):
        self['magnetGeometryType'] = magnetGeometryType

    def SetTrajectoryCutGTZ(self, gtz=0.0, unitsstring='m'):
        self['trajCutGTZ'] = str(gtz) + '*' + unitsstring

    def SetTrajectoryCutLTR(self, ltr=10.0, unitsstring='m'):
        self['trajCutLTR'] = str(ltr) + '*' + unitsstring

    def SetPrintModuloFraction(self, pmf=1e-2):
        self['printModuloFraction'] = pmf

    def SetNPerFile(self, nperfile=100):
        self['nperfile'] = nperfile

    def SetNLinesIgnore(self, nlines=0):
        self['nlinesIgnore'] = nlines

    def SetIncludeFringeFields(self, on=True):
        self['includeFringeFields'] = int(on)

    def SetDefaultBiasVaccum(self, biases=""):
        self["defaultBiasVacuum"] = biases

    def SetDefaultBiasMaterial(self, biases=""):
        self["defaultBiasMaterial"] = biases
        
    def SetBeamlineS(self,beamlineS=0, unitsstring='m'):
        self["beamlineS"] = str(beamlineS) + '*' +unitsstring
