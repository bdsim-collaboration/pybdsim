import pandas as _pd
import os.path as _path
import types as _types

from .Data import LoadROOTLibraries as _LoadROOTLibraries
from .Data import RebdsimFile as _RebdsimFile
from .Data import TH1 as _TH1
from .Data import TH2 as _TH2
from .Data import TH3 as _TH3

# BDSOutputROOTEventSampler<float> (sampler, Primary)
# BDSOutputROOTEventLoss (Eloss, ElossTunnel, ElossVacuum, ElossWorld, ElossWorldContents,
#                         ElossWorldExit, PrimaryFirstHit, PrimaryLastHit, TunnelHit)
# BDSOutputROOTEventCoords (PrimaryGlobal)
# BDSOutputROOTEventSamplerC (SamplersC)
# BDSOutputROOTEventSamplerS (SamplersS)
# BDSOutputROOTEventAperture (ApertureImpacts)
# BDSOutputROOTEventCollimator (collimators)

try:
    import ROOT as _ROOT
    _LoadROOTLibraries()
    import cppyy as _cppyy

except ImportError:
    _useRoot = False

def _enforce_same_length_dict(d) :
    # find first non-zero length
    max_l = 0
    for k in d :
        max_l = max(len(d[k]),max_l)

    key_to_del = []
    for k in d :
        if len(d[k]) != max_l :
            key_to_del.append(k)

    for k in key_to_del :
        del d[k]

    return d

def _fill_event_sampler(root_obj, root_tree, pandas_obj) :
    sampler_attribs = ['S', 'T', 'charge', 'energy', 'ionA', 'ionZ', 'isIon', 'kineticEnergy',
                       'mass', 'modelID', 'n', 'nElectrons', 'p', 'parentID', 'partID', 'phi',
                       'phip', 'r', 'rigidity', 'rp', 'samplerName', 'theta', 'trackID',
                       'turnNumber', 'weight', 'x', 'xp', 'y', 'yp', 'z', 'zp']

    # sampler
    sampler = root_obj

    dd = {}
    dd['file_idx'] = []
    dd['file_name'] = []
    dd['event_idx'] = []
    dd['sampler_idx'] = []

    for attrib in sampler_attribs:
        dd[attrib] = []

    for ievt in range(0, root_tree.GetEntries()):
        root_tree.GetEntry(ievt)

        for iprim in range(0, sampler.n):
            dd['file_name'].append(pandas_obj.ht.GetFile().GetName())
            dd['file_idx'].append(pandas_obj.get_filename_index(pandas_obj.et.GetFile().GetName()))
            dd['event_idx'].append(ievt)
            dd['sampler_idx'].append(iprim)
            for attrib in sampler_attribs:
                if attrib == "z" or \
                   attrib == "S" or \
                   attrib == "modelID" or \
                   attrib == "n":
                    dd[attrib].append(getattr(sampler, attrib))
                else:
                    try :
                        dd[attrib].append(getattr(sampler, attrib)[iprim])
                    except IndexError :
                        pass

    df = _pd.DataFrame(_enforce_same_length_dict(dd))
    return df

def _fill_event_eloss(root_obj, root_tree, pandas_obj) :

    energy = []
    S = []
    partID = []

    for ievt in range(0, root_tree.GetEntries()):
        root_tree.GetEntry(ievt)
        for ieloss in range(0, root_obj.n):
            energy.append(root_obj.energy[ieloss])
            S.append(root_obj.S[ieloss])
            # partID.append(root_obj.partID[ieloss])

    dd = {}
    dd['energy'] = energy
    dd['S'] = S
    dd['partID'] = partID

    df = _pd.DataFrame(_enforce_same_length_dict(dd))
    return df

def _fill_event_coords(root_obj, root_tree, pandas_obj) :
    coord_attribs = ['T', 'X', 'Xp', 'Y', 'Yp', 'Z', 'Zp', 'n']

    dd = {}

    for attrib in coord_attribs:
        dd[attrib] = []

    for ievt in range(0, root_tree.GetEntries()):
        root_tree.GetEntry(ievt)

        for icoord in range(0, root_obj.n):
            for attrib in coord_attribs:
                if attrib == "n":
                    dd[attrib].append(getattr(root_obj, attrib))
                else:
                    try :
                        dd[attrib].append(getattr(root_obj, attrib)[icoord])
                    except IndexError :
                        pass

    df = _pd.DataFrame(_enforce_same_length_dict(dd))
    return df

def _fill_event_aperture(root_obj, root_tree, pandas_obj) :
    aperture_attribs = ['S', 'T', 'energy', 'firstPrimaryImpact', 'ionA', 'ionZ', 'isIon',
                        'isPrimary',  'kineticEnergy', 'modelID', 'n', 'nElectrons', 'parentID',
                        'partID', 'trackID', 'turn', 'weight', 'x', 'xp', 'y', 'yp']

    dd = {}
    dd['aperture_idx'] = []

    for attrib in aperture_attribs:
        dd[attrib] = []

    for ievt in range(0, root_tree.GetEntries()):
        root_tree.GetEntry(ievt)

        for iprim in range(0, root_obj.n):
            dd['aperture_idx'].append(iprim)
            for attrib in aperture_attribs:
                if attrib == "n":
                    dd[attrib].append(getattr(root_obj, attrib))
                else:
                    try :
                        dd[attrib].append(getattr(root_obj, attrib)[iprim])
                    except IndexError :
                        pass

    df = _pd.DataFrame(_enforce_same_length_dict(dd))
    return df

def _fill_event_collimator(root_obj, root_tree, pandas_obj) :
    collimator_attribs = ['T', 'charge', 'energy', 'energyDeposited', 'firstPrimaryHitThisTurn', 'impactParameterX',
                          'impactParameterY', 'ionA', 'ionZ', 'isIon', 'kineticEnergy', 'mass', 'n', 'parentID',
                          'partID', 'primaryInteracted', 'primaryStopped', 'rigidity', 'totalEnergyDeposited', 'turn',
                          'weight', 'xIn', 'xpIn', 'yIn', 'ypIn', 'zIn', 'zpIn']

    dd = {}
    dd['collimator_idx'] = []

    for attrib in collimator_attribs:
        dd[attrib] = []

    for ievt in range(0, root_tree.GetEntries()):
        root_tree.GetEntry(ievt)

        for icollimator in range(0, root_obj.n):
            dd['collimator_idx'].append(icollimator)
            for attrib in collimator_attribs:
                if attrib == "n" or \
                   attrib == "primaryInteracted" or \
                   attrib == "primaryStopped" or \
                   attrib == "totalEnergyDeposited" :
                    dd[attrib].append(getattr(root_obj, attrib))
                else:
                    try :
                        dd[attrib].append(getattr(root_obj, attrib)[icollimator])
                    except IndexError :
                        pass
                    except TypeError :
                        print(attrib)

    df = _pd.DataFrame(_enforce_same_length_dict(dd))
    return df

def _fill_event_samplerC(root_obj, root_tree, pandas_obj) :
    pass

def __fill_event_samplerS(root_obj, root_tree, pandas_obj) :
    pass

class PandasConverter :

    attr_to_skip = ['__python_owns__', 'kBitMask', 'kInconsistent', 'kIsOnHeap',
                    'kNotDeleted', 'kOverwrite','kSingleKey', 'kWriteDelete',
                    'kZombie','']

    def __init__(self,root_structure, root_tree):
        self.root_structure = root_structure
        self.root_tree = root_tree

        self.attr_dict = self.variables()

    def variables(self):
        root_obj_attributes = dir(self.root_structure)

        root_obj_attributes_set = set()
        root_obj_attributes_tocheck = []
        root_attribute_map = {}

        for att_key in root_obj_attributes:
            if att_key in PandasConverter.attr_to_skip :
                continue

            att = getattr(self.root_structure, att_key)

            att_type = type(att)

            root_obj_attributes_set.add(str(att_type))

            if att_type == _types.MethodWrapperType:
                pass
            elif att_type == _types.MethodType:
                pass
            elif att_type == _types.BuiltinFunctionType:
                pass
            elif att_type == dict:
                pass
            elif att_type == _types.NoneType:
                pass
            elif att_type == bool:
                root_obj_attributes_tocheck.append(att_key)
                root_attribute_map[att_key] = att
            elif att_type == int:
                root_obj_attributes_tocheck.append(att_key)
                root_attribute_map[att_key] = att
            elif att_type == float:
                root_obj_attributes_tocheck.append(att_key)
                root_attribute_map[att_key] = att
            elif att_type == _cppyy.gbl.std.string:
                root_obj_attributes_tocheck.append(att_key)
                root_attribute_map[att_key] = att
            else:
                try:
                    if type(att_type.__cpp_name__) == str:
                        if att_type.__cpp_name__.startswith("std::vector"):
                            root_obj_attributes_tocheck.append(att_key)
                            root_attribute_map[att_key] = att
                except AttributeError:
                    pass

        return root_attribute_map

    def convert_entry_as_row(self):
        pass

    def convert_vector_as_row(self):
        pass

class REBDSIM:
    def __init__(self, filepath):
        if not _path.isfile(filepath) :
            print("file not found",filepath)
            return

        self.root_file = _RebdsimFile(filepath)

class REBDSIMOptics:
    def __init__(self, filepath):
        if not _path.isfile(filepath) :
            print("file not found",filepath)
            return

        self.root_file = _RebdsimFile(filepath)

    def get_optics(self):
        columns = self.root_file.optics.columns

        dd = {}
        for c in columns:
            d = self.root_file.optics.GetColumn(c)
            dd[c] = d

        df = _pd.DataFrame(dd)
        return df

class BDSIMOutput:
    def __init__(self, filepath):

        #if not _path.isfile(filepath) :
        #    print("file not found",filepath)
        #    return

        self.root_file = _ROOT.DataLoader(filepath)

        self.ht = self.root_file.GetHeaderTree()
        self.h = self.root_file.GetHeader()
        self.ht.GetEntry(0)

        self.et = self.root_file.GetEventTree()
        self.e  = self.root_file.GetEvent()
        self.et.GetEntry(0)
        self.sampler_names  = list(self.root_file.GetSamplerNames())
        try : # TODO needs to be removed when or guarded against with BDSIM version mismatch
            self.csampler_names = list(self.root_file.GetSamplerCNames())
            self.ssampler_names = list(self.root_file.GetSamplerSNames())
        except :
            pass

        self.mt = self.root_file.GetModelTree()
        self.m  = self.root_file.GetModel()
        self.mt.GetEntry(0)

        self.bt = self.root_file.GetBeamTree()
        self.b = self.root_file.GetBeam()
        self.bt.GetEntry(0)

        self.ot = self.root_file.GetOptionsTree()
        self.o = self.root_file.GetOptions()
        self.ot.GetEntry(0)

        self.rt = self.root_file.GetRunTree()
        self.r = self.root_file.GetRun()
        self.rt.GetEntry(0)

        self.root_file_names = []

    def get_filename_index(self, file_name):
        if file_name not in self.root_file_names:
            self.root_file_names.append(file_name)

        return self.root_file_names.index(file_name)

    def get_sampler_names(self):
        return self.sampler_names

    def get_samplerc_names(self):
        return self.csampler_names

    def get_samplers_names(self):
        return self.ssampler_names

    def get_histo1d_names(self):
        hist_names = []
        for h in self.r.Histos.Get1DHistograms():
            hist_names.append(h.GetName())

        return hist_names

    def get_histo2d_names(self):
        hist_names = []
        for h in self.r.Histos.Get2DHistograms():
            hist_names.append(h.GetName())

        return hist_names

    def get_histo3d_names(self):
        hist_names = []
        for h in self.r.Histos.Get3DHistograms():
            hist_names.append(h.GetName())

        return hist_names

    def get_histo4d_names(self):
        hist_names = []
        for h in self.r.Histos.Get4DHistograms():
            hist_names.append(h.GetName())

        return hist_names

    def get_histo1d(self, name, evnt = -1):

        # Check event number
        if evnt > self.et.GetEntries()-1 :
            print("event number beyond end of file")
            return

        # Find histogram index
        ind = -1
        hist_list = self.r.Histos.Get1DHistograms()
        for h, i in zip(hist_list,range(0,len(hist_list))) :
            if name == h.GetName() :
                ind = i
        if ind == -1 :
            print("histogram not found")
            return

        if evnt < 0 :
            h = self.r.Histos.Get1DHistogram(ind)
        else :
            self.et.GetEntry(evnt)
            h = self.e.Histos.Get1DHistogram(ind)

        return _TH1(h)

    def get_histo2d(self, name, evnt = -1):

        # Check event number
        if evnt > self.et.GetEntries()-1 :
            print("event number beyond end of file")
            return

        # Find histogram index
        ind = -1
        hist_list = self.r.Histos.Get2DHistograms()
        for h, i in zip(hist_list,range(0,len(hist_list))) :
            if name == h.GetName() :
                ind = i
        if ind == -1 :
            print("histogram not found")
            return

        if evnt < 0 :
            h = self.r.Histos.Get2DHistogram(ind)
        else :
            self.et.GetEntry(evnt)
            h = self.e.Histos.Get2DHistogram(ind)

        return _TH2(h)

    def get_histo3d(self, name, evnt = -1):

        # Check event number
        if evnt > self.et.GetEntries()-1 :
            print("event number beyond end of file")
            return

        # Find histogram index
        ind = -1
        hist_list = self.r.Histos.Get3DHistograms()
        for h, i in zip(hist_list,range(0,len(hist_list))) :
            if name == h.GetName() :
                ind = i
        if ind == -1 :
            print("histogram not found")
            return

        if evnt < 0 :
            h = self.r.Histos.Get3DHistogram(ind)
        else :
            self.et.GetEntry(evnt)
            h = self.e.Histos.Get3DHistogram(ind)

        return _TH3(h)

    def get_header(self):

        header_attribs = ["bdsimVersion","clhepVersion","rootVersion","dataVersion",
                          "doublePrecisionOutput","fileType","nEventsInFile","nEventsInFileSkipped",
                          "nEventsRequested","nOriginalEvents","nTrajectoryFilters","skimmedFile",
                          "timeStamp","trajectoryFilters"]

        dd = {}
        dd['file_name'] = []
        dd['file_idx'] = []
        for attrib in header_attribs:
            dd[attrib] = []

        for iheader in range(0, self.ht.GetEntries()) :
            self.ht.GetEntry(iheader)
            dd['file_name'].append(self.ht.GetFile().GetName())
            dd['file_idx'].append(self.get_filename_index(self.ht.GetFile().GetName()))
            dd['header_idx'].append(iheader)

            for attrib in header_attribs:
                if attrib == "trajectoryFilters" :
                    dd[attrib].append([str(tf) for tf in getattr(self.h.header, attrib)])
                elif attrib == "bdsimVersion" or \
                     attrib == "clhepVersion" or \
                     attrib == "rootVersion" or \
                     attrib == "timeStamp" or \
                     attrib == "fileType":
                    dd[attrib].append(str(getattr(self.h.header, attrib)).strip())
                else :
                    dd[attrib].append(getattr(self.h.header, attrib))

        df = _pd.DataFrame(_enforce_same_length_dict(dd))

        return df

    def get_model(self, debug = False):

        model_attribs = ['angle', 'bField', 'beamPipeAper1', 'beamPipeAper2', 'beamPipeAper3', 'beamPipeAper4',
                         'beamPipeType', 'cavityBranchNamesUnique', 'cavityIndices', 'cavityInfo', 'collimatorBranchNamesUnique',
                         'collimatorIndices', 'collimatorInfo', 'componentName', 'componentType', 'e1',
                         'e2', 'eField', 'endPos', 'endRefPos', 'endRefRot', 'endRot', 'endS', 'fint', 'fintk2', 'fintx',
                         'fintxk2', 'hgap', 'hkick', 'k1', 'k10', 'k10s', 'k11', 'k11s', 'k12', 'k12s', 'k1s', 'k2', 'k2s', 'k3', 'k3s', 'k4', 'k4s',
                         'k5', 'k5s', 'k6', 'k6s', 'k7', 'k7s', 'k8', 'k8s', 'k9', 'k9s', 'ks', 'length', 'material', 'midPos', 'midRefPos',
                         'midRefRot', 'midRot', 'midS', 'midT', 'n', 'nCavities', 'nCollimators', 'offsetX', 'offsetY', 'placementName', 'pvName',
                         'pvNameWPointer', 'samplerCNamesUnique', 'samplerNamesUnique', 'samplerSNamesUnique', 'samplerSPosition', 'scoringMeshName',
                         'staEk', 'staP', 'staPos', 'staRefPos', 'staRefRot', 'staRot', 'staS', 'storeCavityInfo', 'storeCollimatorInfo', 'tilt', 'vkick']

        dd = {}
        dd['file_name'] = []
        dd['file_idx'] = []
        dd['model_idx'] = []
        for attrib in model_attribs:
            dd[attrib] = []

        for imodel in range(0, self.mt.GetEntries()) :
            self.mt.GetEntry(imodel)

            for imodel in range(0, self.m.model.n) :
                dd['file_name'].append(self.ht.GetFile().GetName())
                dd['file_idx'].append(self.get_filename_index(self.ht.GetFile().GetName()))
                dd['model_idx'].append(imodel)

                for attrib in model_attribs:
                    if attrib == "n" or \
                       attrib == "nCavities" or \
                       attrib == "nCollimators" or \
                       attrib == "storeCollimatorInfo" or \
                       attrib == "storeCavityInfo" :
                        dd[attrib].append(getattr(self.m.model, attrib))
                    # TODO add these variables
                    elif attrib == 'scoringMeshName' or \
                         attrib == 'scoringMeshRotation' or \
                         attrib == 'scoringMeshTranslation' :
                        pass
                    else :
                        try :
                            dd[attrib].append(getattr(self.m.model, attrib)[imodel])
                        except :
                            if debug and imodel == 0:
                                print(attrib)

        df = _pd.DataFrame(_enforce_same_length_dict(dd))

        return df

    def get_beam(self):
        run_attribs = ["alfx","alfy","beamEnergy","beamKineticEnergy","beamMomentum",
                       "beamParticleName","betx","bety","bunchFrequency","bunchPeriod",
                       "dispx","dispxp","dispy","dispyp","distrFile","distrFileFormat",
                       "distrFileFromExecOptions","distrFileLoop","distrFileLoopNTimes",
                       "distrFileMatchLength","distrType","emitNX","emitNY","emitx",
                       "emity","energyDistrType","envelopeE","envelopeR","envelopeRp",
                       "envelopeT","envelopeX","envelopeXp","envelopeY","envelopeYp",
                       "envelopeZ","envelopeZp","eventGeneratorMaxEK","eventGeneratorMaxRp",
                       "eventGeneratorMaxT","eventGeneratorMaxX","eventGeneratorMaxXp",
                       "eventGeneratorMaxY","eventGeneratorMaxYp","eventGeneratorMaxZ",
                       "eventGeneratorMaxZp","eventGeneratorMinEK","eventGeneratorMinRp",
                       "eventGeneratorMinT","eventGeneratorMinX","eventGeneratorMinXp",
                       "eventGeneratorMinY","eventGeneratorMinYp","eventGeneratorMinZ",
                       "eventGeneratorMinZp","eventGeneratorNEventsSkip","eventGeneratorParticles",
                       "eventGeneratorWarnSkippedParticles","eventsPerBunch","haloNSigmaXInner",
                       "haloNSigmaXOuter","haloNSigmaYInner","haloNSigmaYOuter","haloPSWeightFunction",
                       "haloPSWeightParameter","haloXCutInner","haloXCutOuter","haloXpCutInner",
                       "haloXpCutOuter","haloYCutInner","haloYCutOuter","haloYpCutInner",
                       "haloYpCutOuter","nlinesIgnore","nlinesSkip","offsetSampleMean",
                       "particle","removeUnstableWithoutDecay","setKeys",
                       "shellX","shellXp","shellXpWidth","shellXWidth","shellY","shellYp",
                       "shellYpWidth","shellYWidth",
                       "sigma11","sigma12","sigma13","sigma14","sigma15","sigma16",
                        "sigma22","sigma23","sigma24","sigma25","sigma26",
                        "sigma33","sigma34","sigma35","sigma36",
                        "sigma44","sigma45","sigma46",
                        "sigma55","sigma56",
                        "sigma66",
                        "sigmaE","sigmaEk","sigmaP","sigmaT","sigmaX","sigmaXp","sigmaY","sigmaYp",
                        "spaceDistrType","tilt","xDistrType","X0","Xp0","yDistrType","Y0","Yp0","Z0","Zp0"]

        dd = {}
        dd['file_name'] = []
        dd['file_idx'] = []
        dd['beam_idx'] = []

        for attrib in run_attribs:
            dd[attrib] = []

        for ibeam in range(0, self.bt.GetEntries()) :
            self.bt.GetEntry(ibeam)
            dd['file_name'].append(self.bt.GetFile().GetName())
            dd['file_idx'].append(self.get_filename_index(self.bt.GetFile().GetName()))
            dd['beam_idx'].append(ibeam)
            for attrib in run_attribs:
                if attrib == "setKeys" :
                    dd[attrib].append([str(v) for v in getattr(self.b.beam, attrib)])
                elif attrib == "spaceDistrType" or \
                     attrib == "distrType" or \
                     attrib == "xDistrType" or\
                     attrib == "yDistrType" or\
                     attrib == "energyDistrType" or \
                     attrib == "distrFile" or \
                     attrib == "distrFileFormat" :

                    dd[attrib].append(str(getattr(self.b.beam, attrib)))
                else :
                    dd[attrib].append(getattr(self.b.beam, attrib))

        df = _pd.DataFrame(_enforce_same_length_dict(dd))

        return df

    def get_options(self):
        option_attribs = ["aper1","aper2","aper3","aper4", "apertureImpactsMinimumKE","apertureType",
                          "backupStepperMomLimit","batch","bdsimPath", "beamlineAngle","beamlineAxisAngle",
                          "beamlineAxisX", "beamlineAxisY","beamlineAxisZ","beamlinePhi",
                          "beamlinePsi","beamlineS","beamlineTheta", "beamlineX","beamlineY","beamlineZ",
                          "beampipeMaterial", "beampipeThickness","biasForWorldContents","biasForWorldVacuum",
                          "biasForWorldVolume","buildPoleFaceGeometry","buildTunnel",
                          "buildTunnelFloor","buildTunnelStraight","cavityFieldType",
                          "checkOverlaps","chordStepMinimum","chordStepMinimumYoke",
                          "circular","coilHeightFraction","coilWidthFraction","collimatorHitsMinimumKE",
                          "collimatorsAreInfiniteAbsorbers","defaultBiasMaterial","defaultBiasVacuum",
                          "defaultRangeCut", "deltaIntersection", "deltaOneStep", "dEThresholdForScattering",
                          "dontSplitSBends", "elossHistoBinWidth","emax","emin","emptyMaterial",
                          "eventNumberOffset", "eventOffset", "exportFileName", "exportGeometry",
                          "exportType", "ffact", "fieldModulator","g4PhysicsUseBDSIMCutsAndLimits","g4PhysicsUseBDSIMRangeCuts",
                          "geant4MacroFileName","geant4PhysicsMacroFileName","geant4PhysicsMacroFileNameFromExecOptions",
                          "generatePrimariesOnly", "ignoreLocalAperture","ignoreLocalMagnetGeometry","importanceVolumeMap",
                          "importanceWorldGeometryFile","includeFringeFields","includeFringeFieldsCavities","inputFileName",
                          "integrateKineticEnergyAlongBeamline","integratorSet","killedParticlesMassAddedToEloss",
                          "killNeutrinos","lengthSafety","lengthSafetyLarge","magnetGeometryType","maximumBetaChangePerStep",
                          "maximumEpsilonStep","maximumEpsilonStepThin","maximumPhotonsPerStep","maximumStepLength",
                          "maximumTrackingTime","maximumTrackLength","maximumTracksPerEvent","minimumEpsilonStep",
                          "minimumEpsilonStepThin","minimumKineticEnergy","minimumKineticEnergyTunnel","minimumRadiusOfCurvature",
                          "minimumRange","modelSplitLevel","muonSplittingExcludeWeight1Particles","muonSplittingExclusionWeight",
                          "muonSplittingFactor","muonSplittingFactor2","muonSplittingThresholdParentEk","muonSplittingThresholdParentEk2",
                          "nbinse","nbinsx","nbinsy","nbinsz","neutronKineticEnergyLimit","neutronTimeLimit",
                          "nGenerate","nominalMatrixRelativeMomCut","nSegmentsPerCircle","nturns","numberOfEventsPerNtuple",
                          "outerMaterialName","outputCompressionLevel","outputDoublePrecision","outputFileName",
                          "outputFormat","particlesToExcludeFromCuts","physicsEnergyLimitHigh","physicsEnergyLimitLow",
                          "physicsList","physicsVerbose","physicsVerbosity","preprocessGDML","preprocessGDMLSchema",
                          "printFractionEvents","printFractionTurns","printPhysicsProcesses","prodCutElectrons",
                          "prodCutPhotons","prodCutPositrons","prodCutProtons","ptcOneTurnMapFileName","randomEngine",
                          "recreate","recreateFileName","recreateSeedState","removeTemporaryFiles","restoreFTPFDiffractionForAGreater10",
                          "sampleElementsWithPoleface","samplerDiameter","samplersSplitLevel","scalingFieldOuter",
                          "scintYieldFactor","seed","seedStateFileName","sensitiveBeamPipe","sensitiveOuter",
                          "setKeys","soilMaterial","startFromEvent","stopSecondaries","storeApertureImpacts",
                          "storeApertureImpactsAll","storeApertureImpactsHistograms","storeApertureImpactsIons",
                          "storeCavityInfo","storeCollimatorHits","storeCollimatorHitsAll","storeCollimatorHitsIons",
                          "storeCollimatorHitsLinks","storeCollimatorInfo","storeEloss","storeElossGlobal",
                          "storeElossHistograms","storeElossLinks","storeElossLocal","storeElossModelID",
                          "storeElossPhysicsProcesses","storeElossPreStepKineticEnergy","storeElossStepLength",
                          "storeElossTime","storeElossTunnel","storeElossTunnelHistograms","storeElossTurn","storeElossVacuum",
                          "storeElossVacuumHistograms","storeElossWorld","storeElossWorldContents",
                          "storeElossWorldContentsIntegral","storeElossWorldIntegral","storeMinimalData","storeModel",
                          "storeParticleData","storePrimaries","storePrimaryHistograms","storeSamplerAll",
                          "storeSamplerCharge","storeSamplerIon","storeSamplerKineticEnergy","storeSamplerMass","storeSamplerPolarCoords",
                          "storeSamplerRigidity","storeTrajectory","storeTrajectoryAllVariables","storeTrajectoryDepth",
                          "storeTrajectoryELossSRange","storeTrajectoryEnergyThreshold","storeTrajectoryIon","storeTrajectoryKineticEnergy",
                          "storeTrajectoryLinks","storeTrajectoryLocal","storeTrajectoryMaterial","storeTrajectoryMomentumVector",
                          "storeTrajectoryParticle","storeTrajectoryParticleID","storeTrajectoryProcesses","storeTrajectorySamplerID",
                          "storeTrajectorySecondaryParticles","storeTrajectoryStepPointLast","storeTrajectoryStepPoints","storeTrajectoryTime",
                          "storeTrajectoryTransportationSteps","survey","surveyFileName","teleporterFullTransform","temporaryDirectory",
                          "thinElementLength","trajConnect","trajCutGTZ","trajCutLTR","trajectoryFilterLogicAND","trajNoTransportation",
                          "tunnelAper1","tunnelAper2","tunnelFloorOffset","tunnelIsInfiniteAbsorber","tunnelMaterial",
                          "tunnelMaxSegmentLength","tunnelOffsetX","tunnelOffsetY","tunnelSoilThickness",
                          "tunnelThickness","tunnelType","tunnelVisible","turnOnMieScattering","turnOnOpticalAbsorption",
                          "turnOnOpticalSurface","turnOnRayleighScattering","uprootCompatible","useASCIISeedState",
                          "useElectroNuclear","useGammaToMuMu","useLENDGammaNuclear","useMuonNuclear","useOldMultipoleOuterFields",
                          "usePositronToHadrons","usePositronToMuMu","useScoringMap","vacMaterial",
                          "vacuumPressure","verbose","verboseEventBDSIM","verboseEventContinueFor","verboseEventLevel",
                          "verboseEventStart","verboseImportanceSampling","verboseRunLevel","verboseSensitivity",
                          "verboseSteppingBDSIM","verboseSteppingEventContinueFor","verboseSteppingEventStart","verboseSteppingLevel",
                          "verboseSteppingPrimaryOnly","verboseTrackingLevel","vhRatio","visDebug","visMacroFileName","visVerbosity",
                          "worldGeometryFile","worldMaterial","worldVacuumVolumeNames","worldVolumeMargin",
                          "writeSeedState","xmax","xmin","xrayAllSurfaceRoughness","xsize","ymax","ymin",
                          "yokeFields","yokeFieldsMatchLHCGeometry","ysize","zmax","zmin"]

        dd = {}
        dd['file_name'] = []
        dd['file_idx'] = []
        dd['option_idx'] = []

        for attrib in option_attribs:
            dd[attrib] = []

        for iopt in range(0, self.ot.GetEntries()):
            self.ot.GetEntry(iopt)
            dd['file_name'].append(self.ot.GetFile().GetName())
            dd['file_idx'].append(self.get_filename_index(self.ot.GetFile().GetName()))
            dd['option_idx'].append(iopt)

            for attrib in option_attribs:
                if attrib == "apertureType" or \
                   attrib == "beampipeMaterial" or \
                   attrib == "bdsimPath" or \
                   attrib == "cavityFieldType" or \
                   attrib == "emptyMaterial" or \
                   attrib == "exportFileName" or \
                   attrib == "exportType" or \
                   attrib == "inputFileName" or \
                   attrib == "integratorSet" or \
                   attrib == "magnetGeometryType" or \
                   attrib == "outerMaterialName" or \
                   attrib == "outputFileName" or \
                   attrib == "outputFormat" or \
                   attrib == "randomEngine" or \
                   attrib == "surveyFileName" or \
                   attrib == "tunnelType" or \
                   attrib == "vacMaterial" or \
                   attrib == "worldMaterial":
                    dd[attrib].append(str(getattr(self.o.options, attrib)))
                elif attrib == "setKeys":
                    dd[attrib].append([str(v) for v in getattr(self.o.options, attrib)])
                else :
                    dd[attrib].append(getattr(self.o.options, attrib))

        df = _pd.DataFrame(_enforce_same_length_dict(dd))

        return df

    def get_run(self):
        run_attribs = ['durationCPU', 'durationWall', 'seedStateAtStart', 'startTime', 'stopTime']

        dd = {}
        dd['file_name'] = []
        dd['file_idx'] = []
        dd['run_idx'] = []

        for attrib in run_attribs:
            dd[attrib] = []

        for irun in range(0, self.rt.GetEntries()) :
            self.ht.GetEntry(irun)
            dd['file_name'].append(self.ht.GetFile().GetName())
            dd['file_idx'].append(self.get_filename_index(self.ht.GetFile().GetName()))
            dd['run_idx'].append(irun)

            for attrib in run_attribs:
                if attrib == 'seedStateAtStart' :
                    dd[attrib].append(str(getattr(self.r.Summary, attrib)))
                else :
                    dd[attrib].append(getattr(self.r.Summary, attrib))

        df = _pd.DataFrame(_enforce_same_length_dict(dd))

        return df

    def get_events(self):

        # primary
        primary = self.e.Primary
        nprimary = []

        # primary first hit
        primary_first_hit = self.e.PrimaryFirstHit
        nprimary_first_hit = []

        # primary last hit
        primary_last_hit = self.e.PrimaryLastHit
        nprimary_last_hit = []

        # aperure
        aperture_hit = self.e.ApertureImpacts
        naperture_hit = []

        # eloss
        eloss = self.e.GetLoss()
        neloss = []

        # eloss tunnel
        eloss_tunnel = self.e.ElossTunnel
        neloss_tunnel = []

        # eloss vacuum
        eloss_vacuum = self.e.ElossVacuum
        neloss_vacuum = []

        # eloss world
        eloss_world = self.e.ElossWorld
        neloss_world = []

        # eloss world contents
        eloss_world_contents = self.e.ElossWorldContents
        neloss_world_contents = []

        # eloss world exit
        eloss_world_exit = self.e.ElossWorldExit
        neloss_world_exit = []

        # trajectory
        traj = self.e.GetTrajectory()
        ntraj = []

        # plane samplers
        samplers = [self.e.GetSampler(sn) for sn in self.sampler_names]

        for ievt in range(0, self.et.GetEntries()) :
            self.et.GetEntry(ievt)

            nprimary.append(primary.n)
            nprimary_first_hit.append(primary_first_hit.n)
            nprimary_last_hit.append(primary_last_hit.n)
            naperture_hit.append(aperture_hit.n)
            neloss.append(eloss.n)
            neloss_tunnel.append(eloss_tunnel.n)
            neloss_vacuum.append(eloss_vacuum.n)
            neloss_world.append(eloss_world.n)
            neloss_world_contents.append(eloss_world_contents.n)
            neloss_world_exit.append(eloss_world_exit.n)
            ntraj.append(traj.n)

            # loop over plane samplers
            nsampler = [s.n for s in samplers]

            # print(ievt,nprimary, nprimary_first_hit, nprimary_last_hit, naperture_hit, neloss, ntraj, nsampler)

        dd = {}
        dd['nprimary'] = nprimary
        dd['nprimary_first_hit'] = nprimary_first_hit
        dd['nprimary_last_hit'] = nprimary_last_hit
        dd['naperture_hit'] = naperture_hit
        dd['neloss'] = neloss
        dd['neloss_tunnel'] = neloss_tunnel
        dd['neloss_vacuum'] = neloss_vacuum
        dd['neloss_world'] = neloss_world
        dd['neloss_world_contents'] = neloss_world_contents
        dd['neloss_world_exit'] = neloss_world_exit
        dd['ntraj'] = ntraj

        df = _pd.DataFrame(_enforce_same_length_dict(dd))
        return df

    def get_primary(self):
        return _fill_event_sampler(self.e.Primary,self.et, self)

    def get_primary_global(self):
        return _fill_event_coords(self.e.PrimaryGlobal, self.et, self)

    def get_eloss(self):
        eloss = self.e.Eloss
        return _fill_event_eloss(eloss, self.et, self)

    def get_eloss_tunnel(self):
        eloss = self.e.ElossTunnel
        return _fill_event_eloss(eloss, self.et, self)

    def get_eloss_vacuum(self):
        eloss = self.e.ElossVacuum
        return _fill_event_eloss(eloss, self.et, self)

    def get_eloss_world(self):
        eloss = self.e.ElossWorld
        return _fill_event_eloss(eloss, self.et, self)

    def get_eloss_world_contents(self):
        eloss = self.e.ElossWorldContents
        return _fill_event_eloss(eloss, self.et, self)

    def get_eloss_world_exit(self):
        eloss = self.e.ElossWorldExit
        return _fill_event_eloss(eloss, self.et, self)

    def get_primary_first_hit(self):
        eloss = self.e.PrimaryFirstHit
        return _fill_event_eloss(eloss, self.et, self)

    def get_primary_last_hit(self):
        pass
        eloss = self.e.PrimaryLastHit
        return _fill_event_eloss(eloss, self.et, self)

    def get_tunnel_hit(self):
        eloss = self.e.TunnelHit
        return _fill_event_eloss(eloss, self.et, self)

    def get_aperture_impacts(self):
        return _fill_event_aperture(self.e.ApertureImpacts, self.et, self)

    def get_collimator(self, collimator_name):
        collimator = self.e.collimators[collimator_name]
        return _fill_event_collimator(collimator, self.et, self)

    def get_trajectories(self, i_evnt):
        self.et.GetEntry(i_evnt)

        traj = self.e.Trajectory

        nstep = []
        partID = []
        trackID = []
        for i in range(0,len(traj.partID)) :
            nstep.append(len(traj.XYZ[i]))
            trackID.append(traj.trackID[i])
            partID.append(traj.partID[i])

        dd = {}
        dd['nstep'] = nstep
        dd['partID'] = partID
        dd['trackID'] = trackID

        df = _pd.DataFrame(_enforce_same_length_dict(dd))

        return df

    def get_trajectory(self, i_evnt = 0 , i_traj = 0):
        self.et.GetEntry(i_evnt)

        traj = self.e.Trajectory
        XYZ = traj.XYZ[i_traj]
        kineticEnergy = traj.kineticEnergy[i_traj]

        # T  = traj.T[i_traj]

        X = []
        Y = []
        Z = []
        KE = []

        # loop over points
        for i in range(0,XYZ.size()) :
            X.append(XYZ[i].x())
            Y.append(XYZ[i].y())
            Z.append(XYZ[i].z())
            KE.append(kineticEnergy[i])

        dd = {}
        dd['X'] = X
        dd['Y'] = Y
        dd['Z'] = Z
        dd['kineticEnergy'] = KE

        df = _pd.DataFrame(_enforce_same_length_dict(dd))

        return df

    def get_histograms(self):
        pass

    def get_sampler(self, sampler_name):
        if sampler_name not in self.sampler_names:
            print("Sampler name not recognized")
            return

        sampler = self.e.GetSampler(sampler_name)

        return _fill_event_sampler(sampler, self.et, self)

    def get_samplerc(self, sampler_name):
        if sampler_name not in self.csampler_names:
            print("Sampler name not recognized")
            return

        sampler = self.e.GetSamplerC(sampler_name)

        dd = {}
        dd['file_idx'] = []
        dd['event_idx'] = []
        dd['sampler_idx'] = []
        dd['rp'] = []
        dd['phi'] = []
        dd['phip'] = []
        dd['z'] = []
        dd['zp'] = []
        dd['T'] = []
        dd['totalEnergy'] = []
        dd['partID'] = []
        dd['trackID'] = []
        dd['weight'] = []


        for ievt in range(0, self.et.GetEntries()):
            self.et.GetEntry(ievt)

            for ipart in range(0, sampler.n) :
                dd['file_idx'].append(self.get_filename_index(self.ot.GetFile().GetName()))
                dd['event_idx'].append(ievt)
                dd['sampler_idx'].append(ipart)
                dd['rp'].append(sampler.rp[ipart])
                dd['phi'].append(sampler.phi[ipart])
                dd['phip'].append(sampler.phip[ipart])
                dd['z'].append(sampler.z[ipart])
                dd['zp'].append(sampler.zp[ipart])
                dd['T'].append(sampler.T[ipart])
                dd['totalEnergy'].append(sampler.totalEnergy[ipart])
                dd['partID'].append(sampler.partID[ipart])
                dd['trackID'].append(sampler.trackID[ipart])
                dd['weight'].append(sampler.weight[ipart])

        df = _pd.DataFrame(dd)
        return df

    def get_samplers(self, sampler_name):
        if sampler_name not in self.ssampler_names:
            print("Sampler name not recognized")
            return

        sampler = self.e.GetSamplerS(sampler_name)

        dd = {}
        dd['file_idx'] = []
        dd['event_idx'] = []
        dd['sampler_idx'] = []
        dd['phi'] = []
        dd['phip'] = []
        dd['theta'] = []
        dd['thetap'] = []
        dd['T'] = []
        dd['totalEnergy'] = []
        dd['partID'] = []
        dd['trackID'] = []
        dd['weight'] = []

        for ievt in range(0, self.et.GetEntries()):
            self.et.GetEntry(ievt)

            for ipart in range(0, sampler.n) :
                dd['file_idx'].append(self.get_filename_index(self.ot.GetFile().GetName()))
                dd['event_idx'].append(ievt)
                dd['sampler_idx'].append(ipart)
                dd['phi'].append(sampler.phi[ipart])
                dd['phip'].append(sampler.phip[ipart])
                dd['theta'].append(sampler.theta[ipart])
                dd['thetap'].append(sampler.thetap[ipart])
                dd['T'].append(sampler.T[ipart])
                dd['totalEnergy'].append(sampler.totalEnergy[ipart])
                dd['partID'].append(sampler.partID[ipart])
                dd['trackID'].append(sampler.trackID[ipart])
                dd['weight'].append(sampler.weight[ipart])

        df = _pd.DataFrame(dd)
        return df

class LinkBunch :
    def __init__(self, link_Bunch):
        self._link_Bunch = link_Bunch

    def get_dataframe(self):

        dd = {}

        dd['Beta'] = []
        dd['BRho'] = []
        dd['Charge'] = []
        dd['FFact'] = []
        dd['Forwards'] = []
        dd['Gamma'] = []

        # ion definition

        dd['IsAnIon'] = []
        dd['KineticEnergy'] = []
        dd['Mass'] = []
        dd['Momentum'] = []
        dd['Name'] = []
        dd['NElectrons'] = []
        dd['PDGID'] = []
        dd['TotalEnergy'] = []
        dd['Velocity'] = []

        dd['s'] = []
        dd['T'] = []
        dd['coords.totalEnergy'] = []
        dd['x'] = []
        dd['y'] = []
        dd['z'] = []
        dd['xp'] = []
        dd['yp'] = []
        dd['zp'] = []

        for i in range(0,self._link_Bunch.Size()) :
            pd = self._link_Bunch.ParticleDefinition()
            lc = self._link_Bunch.GetNextParticleLocal()
            dd['Beta'].append(pd.Beta())
            dd['BRho'].append(pd.BRho())
            dd['Charge'].append(pd.Charge())
            dd['FFact'].append(pd.FFact())
            dd['Forwards'].append(pd.Forwards())
            dd['Gamma'].append(pd.Gamma())

            dd['IsAnIon'].append(pd.IsAnIon())
            dd['KineticEnergy'].append(pd.KineticEnergy())
            dd['Mass'].append(pd.Mass())
            dd['Momentum'].append(pd.Momentum())
            dd['Name'].append(pd.Name())
            dd['NElectrons'].append(pd.NElectrons())
            dd['PDGID'].append(pd.PDGID())
            dd['TotalEnergy'].append(pd.TotalEnergy())
            dd['Velocity'].append(pd.Velocity())

            dd['s'].append(lc.s)
            dd['T'].append(lc.T)
            dd['coords.totalEnergy'].append(lc.totalEnergy)
            dd['x'].append(lc.x)
            dd['y'].append(lc.y)
            dd['z'].append(lc.z)
            dd['xp'].append(lc.xp)
            dd['yp'].append(lc.yp)
            dd['zp'].append(lc.zp)

        return _pd.DataFrame(dd)

class LinkSamplerHits :
    def __init__(self, link_SamplerHits):
        self._samplerHits = link_SamplerHits

    def get_dataframe(self):

        dd = {}

        dd['A'] = []
        dd['beamlineIndex'] = []
        dd['charge'] = []

        dd['s'] = []
        dd['T'] = []
        dd['totalEnergy'] = []
        dd['weight'] = []
        dd['x'] = []
        dd['y'] = []
        dd['z'] = []
        dd['xp'] = []
        dd['yp'] = []
        dd['zp'] = []

        dd['eventID'] = []
        dd['externalEventID'] = []
        dd['externalParticleID'] = []
        dd['mass'] = []
        dd['momentum'] = []
        dd['nElectrons'] = []
        dd['parentID'] = []
        dd['pdgID'] = []
        dd['rigidity'] = []
        dd['samplerID'] = []
        dd['trackID'] = []
        dd['turnsTaken'] = []
        dd['Z'] = []

        for i in range(0,self._samplerHits.entries()) :
            sh = self._samplerHits[i]
            dd['A'].append(sh.A)
            dd['beamlineIndex'].append(sh.beamlineIndex)
            dd['charge'].append(sh.charge)
            dd['s'].append(sh.coords.s)
            dd['T'].append(sh.coords.T)
            dd['totalEnergy'].append(sh.coords.totalEnergy)
            dd['weight'].append(sh.coords.weight)
            dd['x'].append(sh.coords.x)
            dd['y'].append(sh.coords.y)
            dd['z'].append(sh.coords.z)
            dd['xp'].append(sh.coords.xp)
            dd['yp'].append(sh.coords.yp)
            dd['zp'].append(sh.coords.zp)
            dd['eventID'].append(sh.eventID)
            dd['externalEventID'].append(sh.externalParentID)
            dd['externalParticleID'].append(sh.externalParticleID)
            dd['mass'].append(sh.mass)
            dd['momentum'].append(sh.momentum)
            dd['nElectrons'].append(sh.nElectrons)
            dd['parentID'].append(sh.parentID)
            dd['pdgID'].append(sh.pdgID)
            dd['rigidity'].append(sh.rigidity)
            dd['samplerID'].append(sh.samplerID)
            dd['trackID'].append(sh.trackID)
            dd['turnsTaken'].append(sh.turnsTaken)
            dd['Z'].append(sh.Z)

        df = _pd.DataFrame(dd)
        return df