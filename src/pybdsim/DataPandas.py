import pandas as _pd
import os.path as _path
from .Data import LoadROOTLibraries as _LoadROOTLibraries
from .Data import RebdsimFile as _RebdsimFile
from .Data import TH1 as _TH1
from .Data import TH2 as _TH2
from .Data import TH3 as _TH3

try:
    import ROOT as _ROOT
    _LoadROOTLibraries()
except ImportError:
    print("ROOT load fail")
    _useRoot = False


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
        self.csampler_names = list(self.root_file.GetSamplerCNames())
        self.ssampler_names = list(self.root_file.GetSamplerSNames())

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

    def get_csampler_names(self):
        return self.csampler_names

    def get_ssampler_names(self):
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
        file_idx = []
        bdsimVersion = []
        clhepVersion = []
        rootVersion  = []
        dataVersion = []
        doublePrecisionOutput = []
        fileType = []
        nEventsInFile = []
        nEventsInFileSkipped = []
        nEventsRequested = []
        nOriginalEvents = []
        nTrajectoryFilters = []
        skimmedFile = []
        timeStamp = []
        trajectoryFilters = []

        for iheader in range(0, self.ht.GetEntries()) :
            self.ht.GetEntry(iheader)
            file_idx.append(self.get_filename_index(self.ht.GetFile().GetName()))
            bdsimVersion.append(str(self.h.header.bdsimVersion))
            clhepVersion.append(str(self.h.header.clhepVersion))
            rootVersion.append(str(self.h.header.rootVersion))
            dataVersion.append(str(self.h.header.dataVersion))
            doublePrecisionOutput.append(self.h.header.doublePrecisionOutput)
            fileType.append(str(self.h.header.fileType))
            nEventsInFile.append(self.h.header.nEventsInFile)
            nEventsInFileSkipped.append(self.h.header.nEventsInFileSkipped)
            nEventsRequested.append(self.h.header.nEventsRequested)
            nOriginalEvents.append(self.h.header.nOriginalEvents)
            nTrajectoryFilters.append(self.h.header.nTrajectoryFilters)
            skimmedFile.append(self.h.header.skimmedFile)
            timeStamp.append(str(self.h.header.timeStamp).strip())
            trajectoryFilters.append([str(tf) for tf in self.h.header.trajectoryFilters] )
        dd = {}
        dd['file_idx'] = file_idx
        dd['bdsimVersion'] = bdsimVersion
        dd['clhepVersion'] = clhepVersion
        dd['rootVersion'] = rootVersion
        dd['dataVersion'] = dataVersion
        dd['doublePrecisionOutput'] = doublePrecisionOutput
        dd['fileType'] = fileType
        dd['nEventsInFile'] = nEventsInFile
        dd['nEventsInFileSkipped'] = nEventsInFileSkipped
        dd['nEventsRequested'] = nEventsRequested
        dd['nOriginalEvents'] = nOriginalEvents
        dd['nTrajectoryFilters'] = nTrajectoryFilters
        dd['skimmedFile'] = skimmedFile
        dd['timeStamp'] = timeStamp
        dd['trajectoryFilters'] = trajectoryFilters

        df = _pd.DataFrame(dd)

        return df

    def get_model(self):
        model_number = []
        component_name = []
        component_type = []
        placement_name = []

        length = []
        angle = []
        k1 = []
        k2 = []
        k3 = []
        k4 = []
        k5 = []
        k6 = []
        k7 = []
        k8 = []
        k9 = []
        k10 = []
        k11 = []
        k12 = []
        k1s = []
        k2s = []
        k3s = []
        k4s = []
        k5s = []
        k6s = []
        k7s = []
        k8s = []
        k9s = []
        k10s = []
        k11s = []
        k12s = []
        ks   = []
        material = []

        staPos_x = []
        staPos_y = []
        staPos_z = []
        staRot_thetaX = []
        staRot_thetaY = []
        staRot_thetaZ = []
        staRefPos_x = []
        staRefPos_y = []
        staRefPos_z = []
        staRefRot_thetaX = []
        staRefRot_thetaY = []
        staRefRot_thetaZ = []
        staS = []

        midPos_x = []
        midPos_y = []
        midPos_z = []
        midRot_thetaX = []
        midRot_thetaY = []
        midRot_thetaZ = []
        midRefPos_x = []
        midRefPos_y = []
        midRefPos_z = []
        midRefRot_thetaX = []
        midRefRot_thetaY = []
        midRefRot_thetaZ = []
        midS = []
        midT = []

        endPos_x = []
        endPos_y = []
        endPos_z = []
        endRot_thetaX = []
        endRot_thetaY = []
        endRot_thetaZ = []
        endRefPos_x = []
        endRefPos_y = []
        endRefPos_z = []
        endRefRot_thetaX = []
        endRefRot_thetaY = []
        endRefRot_thetaZ = []
        endS = []

        e1 = []
        e2 = []
        beamPipeAper1 = []
        beamPipeAper2 = []
        beamPipeAper3 = []
        beamPipeAper4 = []
        beamPipeType = []
        bField = []
        eField = []
        fint = []
        fintx = []
        fintk2 = []
        fintxk2 = []
        hgap = []

        offsetX = []
        offsetY = []

        pvName = []
        staEk = []
        staP = []

        tilt = []
        hkick = []
        vkick = []

        for imodel in range(0, self.mt.GetEntries()) :
            self.mt.GetEntry(imodel)
            for ielement in range(0, self.m.model.n) :
                model_number.append(imodel)
                component_name.append(self.m.model.componentName[ielement])
                placement_name.append(self.m.model.placementName[ielement])
                component_type.append(self.m.model.componentType[ielement])
                length.append(self.m.model.length[ielement])
                angle.append(self.m.model.angle[ielement])
                k1.append(self.m.model.k1[ielement])
                k2.append(self.m.model.k2[ielement])
                k3.append(self.m.model.k3[ielement])
                k4.append(self.m.model.k4[ielement])
                k5.append(self.m.model.k5[ielement])
                k6.append(self.m.model.k6[ielement])
                k7.append(self.m.model.k7[ielement])
                k8.append(self.m.model.k8[ielement])
                k9.append(self.m.model.k9[ielement])
                k10.append(self.m.model.k10[ielement])
                k11.append(self.m.model.k11[ielement])
                k12.append(self.m.model.k12[ielement])
                k1s.append(self.m.model.k1s[ielement])
                k2s.append(self.m.model.k2s[ielement])
                k3s.append(self.m.model.k3s[ielement])
                k4s.append(self.m.model.k4s[ielement])
                k5s.append(self.m.model.k5s[ielement])
                k6s.append(self.m.model.k6s[ielement])
                k7s.append(self.m.model.k7s[ielement])
                k8s.append(self.m.model.k8s[ielement])
                k9s.append(self.m.model.k9s[ielement])
                k10s.append(self.m.model.k10s[ielement])
                k11s.append(self.m.model.k11s[ielement])
                k12s.append(self.m.model.k12s[ielement])
                ks.append(self.m.model.ks[ielement])
                material.append(self.m.model.material[ielement])

                staPos_x.append(self.m.model.staPos[ielement].x())
                staPos_y.append(self.m.model.staPos[ielement].y())
                staPos_z.append(self.m.model.staPos[ielement].z())
                staRot_thetaX.append(self.m.model.staRot[ielement].ThetaX())
                staRot_thetaY.append(self.m.model.staRot[ielement].ThetaY())
                staRot_thetaZ.append(self.m.model.staRot[ielement].ThetaZ())
                staRefPos_x.append(self.m.model.staRefPos[ielement].x())
                staRefPos_y.append(self.m.model.staRefPos[ielement].y())
                staRefPos_z.append(self.m.model.staRefPos[ielement].z())
                staRefRot_thetaX.append(self.m.model.staRefRot[ielement].ThetaX())
                staRefRot_thetaY.append(self.m.model.staRefRot[ielement].ThetaY())
                staRefRot_thetaZ.append(self.m.model.staRefRot[ielement].ThetaZ())
                staS.append(self.m.model.staS[ielement])

                midPos_x.append(self.m.model.midPos[ielement].x())
                midPos_y.append(self.m.model.midPos[ielement].y())
                midPos_z.append(self.m.model.midPos[ielement].z())
                midRot_thetaX.append(self.m.model.midRot[ielement].ThetaX())
                midRot_thetaY.append(self.m.model.midRot[ielement].ThetaY())
                midRot_thetaZ.append(self.m.model.midRot[ielement].ThetaZ())
                midRefPos_x.append(self.m.model.midRefPos[ielement].x())
                midRefPos_y.append(self.m.model.midRefPos[ielement].y())
                midRefPos_z.append(self.m.model.midRefPos[ielement].z())
                midRefRot_thetaX.append(self.m.model.midRefRot[ielement].ThetaX())
                midRefRot_thetaY.append(self.m.model.midRefRot[ielement].ThetaY())
                midRefRot_thetaZ.append(self.m.model.midRefRot[ielement].ThetaZ())
                midS.append(self.m.model.midS[ielement])
                try :
                    midT.append(self.m.model.midT[ielement])
                except :
                    midT.append(0)

                endPos_x.append(self.m.model.endPos[ielement].x())
                endPos_y.append(self.m.model.endPos[ielement].y())
                endPos_z.append(self.m.model.endPos[ielement].z())
                endRot_thetaX.append(self.m.model.endRot[ielement].ThetaX())
                endRot_thetaY.append(self.m.model.endRot[ielement].ThetaY())
                endRot_thetaZ.append(self.m.model.endRot[ielement].ThetaZ())
                endRefPos_x.append(self.m.model.endRefPos[ielement].x())
                endRefPos_y.append(self.m.model.endRefPos[ielement].y())
                endRefPos_z.append(self.m.model.endRefPos[ielement].z())
                endRefRot_thetaX.append(self.m.model.endRot[ielement].ThetaX())
                endRefRot_thetaY.append(self.m.model.endRot[ielement].ThetaY())
                endRefRot_thetaZ.append(self.m.model.endRot[ielement].ThetaZ())
                endS.append(self.m.model.endS[ielement])

                e1.append(self.m.model.e1[ielement])
                e2.append(self.m.model.e2[ielement])
                beamPipeAper1.append(self.m.model.beamPipeAper1[ielement])
                beamPipeAper2.append(self.m.model.beamPipeAper2[ielement])
                beamPipeAper3.append(self.m.model.beamPipeAper3[ielement])
                beamPipeAper4.append(self.m.model.beamPipeAper4[ielement])
                beamPipeType.append(self.m.model.beamPipeType[ielement])
                bField.append(self.m.model.bField[ielement])
                eField.append(self.m.model.eField[ielement])
                fint.append(self.m.model.fint[ielement])
                fintx.append(self.m.model.fintx[ielement])
                fintk2.append(self.m.model.fintk2[ielement])
                fintxk2.append(self.m.model.fintxk2[ielement])
                hgap.append(self.m.model.hgap[ielement])

                offsetX.append(self.m.model.offsetX[ielement])
                offsetY.append(self.m.model.offsetY[ielement])

                pvName.append(' '.join([str(s) for s in self.m.model.pvName[ielement]]))
                try :
                    staEk.append(self.m.model.staEk[ielement])
                    staP.append(self.m.model.staP[ielement])
                except :
                    staEk.append(0)
                    staP.append(0)

                tilt.append(self.m.model.tilt[ielement])
                hkick.append(self.m.model.hkick[ielement])
                vkick.append(self.m.model.vkick[ielement])


        dd = {}
        dd['model_number'] = model_number
        dd['component_name'] = component_name
        dd['placement_name'] = placement_name
        dd['component_type'] = component_type
        dd['length'] = length
        dd['angle'] = angle
        dd['k1'] = k1
        dd['k2'] = k2
        dd['k3'] = k3
        dd['k4'] = k4
        dd['k5'] = k5
        dd['k6'] = k6
        dd['k7'] = k7
        dd['k8'] = k8
        dd['k9'] = k9
        dd['k10'] = k10
        dd['k11'] = k11
        dd['k12'] = k12
        dd['k1s'] = k1s
        dd['k2s'] = k2s
        dd['k3s'] = k3s
        dd['k4s'] = k4s
        dd['k5s'] = k5s
        dd['k6s'] = k6s
        dd['k7s'] = k7s
        dd['k8s'] = k8s
        dd['k9s'] = k9s
        dd['k10s'] = k10s
        dd['k11s'] = k11s
        dd['k12s'] = k12s
        dd['ks'] = ks
        dd['material'] = material
        dd['staPos_x'] = staPos_x
        dd['staPos_y'] = staPos_y
        dd['staPos_z'] = staPos_z
        dd['staRot_thetaX'] = staRefRot_thetaX
        dd['staRot_thetaY'] = staRefRot_thetaY
        dd['staRot_thetaZ'] = staRefRot_thetaZ
        dd['staRefPos_x'] = staRefPos_x
        dd['staRefPos_y'] = staRefPos_y
        dd['staRefPos_z'] = staRefPos_z
        dd['staRefRot_thetaX'] = staRefRot_thetaX
        dd['staRefRot_thetaY'] = staRefRot_thetaY
        dd['staRefRot_thetaZ'] = staRefRot_thetaZ
        dd['staS'] = staS
        dd['midPos_x'] = midPos_x
        dd['midPos_y'] = midPos_y
        dd['midPos_z'] = midPos_z
        dd['midRot_thetaX'] = midRot_thetaX
        dd['midRot_thetaY'] = midRot_thetaY
        dd['midRot_thetaZ'] = midRot_thetaZ
        dd['midRefPos_x'] = midRefPos_x
        dd['midRefPos_y'] = midRefPos_y
        dd['midRefPos_z'] = midRefPos_z
        dd['midRefRot_thetaX'] = midRefRot_thetaX
        dd['midRefRot_thetaY'] = midRefRot_thetaY
        dd['midRefRot_thetaZ'] = midRefRot_thetaZ
        dd['midS'] = midS
        dd['midT'] = midT
        dd['endPos_x'] = endPos_x
        dd['endPos_y'] = endPos_y
        dd['endPos_z'] = endPos_z
        dd['endRot_thetaX'] = endRot_thetaX
        dd['endRot_thetaY'] = endRot_thetaY
        dd['endRot_thetaZ'] = endRot_thetaZ
        dd['endRefPos_x'] = endRefPos_x
        dd['endRefPos_y'] = endRefPos_y
        dd['endRefPos_z'] = endRefPos_z
        dd['endRefRot_thetaX'] = endRefRot_thetaX
        dd['endRefRot_thetaY'] = endRefRot_thetaY
        dd['endRefRot_thetaZ'] = endRefRot_thetaZ
        dd['endS'] = endS

        dd['e1'] = e1
        dd['e2'] = e2
        dd['beamPipeAper1'] = beamPipeAper1
        dd['beamPipeAper2'] = beamPipeAper2
        dd['beamPipeAper3'] = beamPipeAper3
        dd['beamPipeAper4'] = beamPipeAper4
        dd['beamPipeType'] = beamPipeType
        dd['bField'] = bField
        dd['eField'] = eField
        dd['fint'] = fint
        dd['fintx'] = fintx
        dd['fintk2'] = fintk2
        dd['fintxk2'] = fintxk2
        dd['hgap'] = hgap

        dd['offsetX'] = offsetX
        dd['offsetY'] = offsetY

        dd['pvName'] = pvName
        dd['staEk'] = staEk
        dd['staP'] = staP

        dd['tilt'] = tilt
        dd['hkick'] = hkick
        dd['vkick'] = vkick

        df = _pd.DataFrame(dd)

        return df

    def get_beam(self):
        pass

    def get_options(self):

        file_idx = []
        aper1 = []
        aper2 = []
        aper3 = []
        aper4 = []
        apertureImpactsMinimumKE = []
        apertureType = []
        backupStepperMomLimit = []
        batch = []
        bdsimPath = []
        beamlineAngle = []
        beamlineAxisAngle = []
        beamlineAxisX = []
        beamlineAxisY = []
        beamlineAxisZ = []
        beamlinePhi = []
        beamlinePsi = []
        beamlineS = []
        beamlineTheta = []
        beamlineX = []
        beamlineY = []
        beamlineZ = []
        beampipeIsInfiniteAbsorber = []
        beampipeMaterial = []
        beampipeThickness = []
        biasForWorldContents = []
        biasForWorldVacuum = []
        biasForWorldVolume = []
        buildPoleFaceGeometry = []
        buildTunnel = []
        buildTunnelFloor = []
        buildTunnelStraight = []
        cavityFieldType = []
        checkOverlaps = []
        chordStepMinimum = []
        chordStepMinimumYoke = []
        circular = []
        coilHeightFraction = []
        coilWidthFraction = []
        collimatorHitsMinimumKE = []
        collimatorsAreInfiniteAbsorbers = []
        defaultBiasMaterial = []
        defaultBiasVacuum = []
        defaultRangeCut = []
        deltaIntersection = []
        deltaOneStep = []
        dEThresholdForScattering = []
        dontSplitSBends = []
        elossHistoBinWidth = []
        emax = []
        emin = []
        emptyMaterial = []
        eventNumberOffset = []
        eventOffset = []
        exportFileName = []
        exportGeometry = []
        exportType = []
        ffact = []
        fieldModulator = []
        g4PhysicsUseBDSIMCutsAndLimits = []
        g4PhysicsUseBDSIMRangeCuts = []
        geant4MacroFileName = []
        geant4PhysicsMacroFileName = []
        geant4PhysicsMacroFileNameFromExecOptions = []
        generatePrimariesOnly = []
        horizontalWidth = []
        ignoreLocalAperture = []
        ignoreLocalMagnetGeometry = []
        importanceVolumeMap = []
        importanceWorldGeometryFile = []
        includeFringeFields = []
        includeFringeFieldsCavities = []
        inputFileName = []
        integrateKineticEnergyAlongBeamline = []
        integratorSet = []
        killedParticlesMassAddedToEloss = []
        killNeutrinos = []
        lengthSafety = []
        lengthSafetyLarge = []
        magnetGeometryType = []
        maximumBetaChangePerStep = []
        maximumEpsilonStep = []
        maximumEpsilonStepThin = []
        maximumPhotonsPerStep = []
        maximumStepLength = []
        maximumTrackingTime = []
        maximumTrackLength = []
        maximumTracksPerEvent = []
        minimumEpsilonStep = []
        minimumEpsilonStepThin = []
        minimumKineticEnergy = []
        minimumKineticEnergyTunnel = []
        minimumRadiusOfCurvature = []
        minimumRange = []
        modelSplitLevel = []
        muonSplittingExcludeWeight1Particles = []
        muonSplittingExclusionWeight = []
        muonSplittingFactor = []
        muonSplittingFactor2 = []
        muonSplittingThresholdParentEk = []
        muonSplittingThresholdParentEk2 = []
        nbinse = []
        nbinsx = []
        nbinsy = []
        nbinsz = []
        neutronKineticEnergyLimit = []
        neutronTimeLimit = []
        nGenerate = []
        nominalMatrixRelativeMomCut = []
        nSegmentsPerCircle = []
        nturns = []
        numberOfEventsPerNtuple = []
        outerMaterialName = []
        outputCompressionLevel = []
        outputDoublePrecision = []
        outputFileName = []
        outputFormat = []
        particlesToExcludeFromCuts = []
        physicsEnergyLimitHigh = []
        physicsEnergyLimitLow = []
        physicsList = []
        physicsVerbose = []
        physicsVerbosity = []
        preprocessGDML = []
        preprocessGDMLSchema = []
        printVar = []
        printFractionEvents = []
        printFractionTurns = []
        printPhysicsProcesses = []
        prodCutElectrons = []
        prodCutPhotons = []
        prodCutPositrons = []
        prodCutProtons = []
        ptcOneTurnMapFileName = []
        randomEngine = []
        recreate = []
        recreateFileName = []
        recreateSeedState = []
        removeTemporaryFiles = []
        restoreFTPFDiffractionForAGreater10 = []
        sampleElementsWithPoleface = []
        samplerDiameter = []
        samplersSplitLevel = []
        scalingFieldOuter = []
        scintYieldFactor = []
        seed = []
        seedStateFileName = []
        sensitiveBeamPipe = []
        sensitiveOuter = []
        setKeys = []
        soilMaterial = []
        startFromEvent = []
        stopSecondaries = []
        storeApertureImpacts = []
        storeApertureImpactsAll = []
        storeApertureImpactsHistograms = []
        storeApertureImpactsIons = []
        storeCavityInfo = []
        storeCollimatorHits = []
        storeCollimatorHitsAll = []
        storeCollimatorHitsIons = []
        storeCollimatorHitsLinks = []
        storeCollimatorInfo = []
        storeEloss = []
        storeElossGlobal = []
        storeElossHistograms = []
        storeElossLinks = []
        storeElossLocal = []
        storeElossModelID = []
        storeElossPhysicsProcesses = []
        storeElossPreStepKineticEnergy = []
        storeElossStepLength = []
        storeElossTime = []
        storeElossTunnel = []
        storeElossTunnelHistograms = []
        storeElossTurn = []
        storeElossVacuum = []
        storeElossVacuumHistograms = []
        storeElossWorld = []
        storeElossWorldContents = []
        storeElossWorldContentsIntegral = []
        storeElossWorldIntegral = []
        storeMinimalData = []
        storeModel = []
        storeParticleData = []
        storePrimaries = []
        storePrimaryHistograms = []
        storeSamplerAll = []
        storeSamplerCharge = []
        storeSamplerIon = []
        storeSamplerKineticEnergy = []
        storeSamplerMass = []
        storeSamplerPolarCoords = []
        storeSamplerRigidity = []
        storeTrajectory = []
        storeTrajectoryAllVariables = []
        storeTrajectoryDepth = []
        storeTrajectoryELossSRange = []
        storeTrajectoryEnergyThreshold = []
        storeTrajectoryIon = []
        storeTrajectoryKineticEnergy = []
        storeTrajectoryLinks = []
        storeTrajectoryLocal = []
        storeTrajectoryMaterial = []
        storeTrajectoryMomentumVector = []
        storeTrajectoryParticle = []
        storeTrajectoryParticleID = []
        storeTrajectoryProcesses = []
        storeTrajectorySamplerID = []
        storeTrajectorySecondaryParticles = []
        storeTrajectoryStepPointLast = []
        storeTrajectoryStepPoints = []
        storeTrajectoryTime = []
        storeTrajectoryTransportationSteps = []
        survey = []
        surveyFileName = []
        teleporterFullTransform = []
        temporaryDirectory = []
        thinElementLength = []
        trajConnect = []
        trajCutGTZ = []
        trajCutLTR = []
        trajectoryFilterLogicAND = []
        trajNoTransportation = []
        tunnelAper1 = []
        tunnelAper2 = []
        tunnelFloorOffset = []
        tunnelIsInfiniteAbsorber = []
        tunnelMaterial = []
        tunnelMaxSegmentLength = []
        tunnelOffsetX = []
        tunnelOffsetY = []
        tunnelSoilThickness = []
        tunnelThickness = []
        tunnelType = []
        tunnelVisible = []
        turnOnMieScattering = []
        turnOnOpticalAbsorption = []
        turnOnOpticalSurface = []
        turnOnRayleighScattering = []
        uprootCompatible = []
        useASCIISeedState = []
        useElectroNuclear = []
        useGammaToMuMu = []
        useLENDGammaNuclear = []
        useMuonNuclear = []
        useOldMultipoleOuterFields = []
        usePositronToHadrons = []
        usePositronToMuMu = []
        useScoringMap = []
        vacMaterial = []
        vacuumPressure = []
        verbose = []
        verboseEventBDSIM = []
        verboseEventContinueFor = []
        verboseEventLevel = []
        verboseEventStart = []
        verboseImportanceSampling = []
        verboseRunLevel = []
        verboseSensitivity = []
        verboseSteppingBDSIM = []
        verboseSteppingEventContinueFor = []
        verboseSteppingEventStart = []
        verboseSteppingLevel = []
        verboseSteppingPrimaryOnly = []
        verboseTrackingLevel = []
        vhRatio = []
        visDebug = []
        visMacroFileName = []
        visVerbosity = []
        worldGeometryFile = []
        worldMaterial = []
        worldVacuumVolumeNames = []
        worldVolumeMargin = []
        writeSeedState = []
        xmax = []
        xmin = []
        xrayAllSurfaceRoughness = []
        xsize = []
        ymax = []
        ymin = []
        yokeFields = []
        yokeFieldsMatchLHCGeometry = []
        ysize = []
        zmax = []
        zmin = []

        for ioptions in range(0, self.ot.GetEntries()) :
            self.ot.GetEntry(ioptions)
            file_idx.append(self.get_filename_index(self.ot.GetFile().GetName()))
            aper1.append(self.o.options.aper1)
            aper2.append(self.o.options.aper2)
            aper3.append(self.o.options.aper3)
            aper4.append(self.o.options.aper4)
            apertureImpactsMinimumKE.append(self.o.options.apertureImpactsMinimumKE)
            apertureType.append(self.o.options.apertureType)
            backupStepperMomLimit.append(self.o.options.backupStepperMomLimit)
            batch.append(self.o.options.batch)
            bdsimPath.append(self.o.options.bdsimPath)
            beamlineAngle.append(self.o.options.beamlineAngle)
            beamlineAxisAngle.append(self.o.options.beamlineAxisAngle)
            beamlineAxisX.append(self.o.options.beamlineAxisX)
            beamlineAxisY.append(self.o.options.beamlineAxisY)
            beamlineAxisZ.append(self.o.options.beamlineAxisZ)
            beamlinePhi.append(self.o.options.beamlinePhi)
            beamlinePsi.append(self.o.options.beamlinePsi)
            beamlineS.append(self.o.options.beamlineS)
            beamlineTheta.append(self.o.options.beamlineTheta)
            beamlineX.append(self.o.options.beamlineX)
            beamlineY.append(self.o.options.beamlineY)
            beamlineZ.append(self.o.options.beamlineZ)
            beampipeIsInfiniteAbsorber.append(self.o.options.beamlinePhi)
            beampipeMaterial.append(self.o.options.beamlinePsi)
            beampipeThickness.append(self.o.options.beamlineS)
            biasForWorldContents.append(self.o.options.biasForWorldContents)
            biasForWorldVacuum.append(self.o.options.biasForWorldVacuum)
            biasForWorldVolume.append(self.o.options.biasForWorldVolume)
            buildPoleFaceGeometry.append(self.o.options.buildPoleFaceGeometry)
            buildTunnel.append(self.o.options.buildTunnel)
            buildTunnelFloor.append(self.o.options.buildTunnelFloor)
            buildTunnelStraight.append(self.o.options.buildTunnelStraight)
            cavityFieldType.append(self.o.options.cavityFieldType)
            checkOverlaps.append(self.o.options.checkOverlaps)
            chordStepMinimum.append(self.o.options.chordStepMinimum)
            chordStepMinimumYoke.append(self.o.options.chordStepMinimumYoke)
            circular.append(self.o.options.circular)
            coilHeightFraction.append(self.o.options.coilHeightFraction)
            coilWidthFraction.append(self.o.options.coilWidthFraction)
            collimatorHitsMinimumKE.append(self.o.options.collimatorHitsMinimumKE)
            collimatorsAreInfiniteAbsorbers.append(self.o.options.collimatorsAreInfiniteAbsorbers)
            defaultBiasMaterial.append(self.o.options.defaultBiasMaterial)
            defaultBiasVacuum.append(self.o.options.defaultBiasVacuum)
            defaultRangeCut.append(self.o.options.defaultRangeCut)
            deltaIntersection.append(self.o.options.deltaIntersection)
            deltaOneStep.append(self.o.options.deltaOneStep)
            dEThresholdForScattering.append(self.o.options.dEThresholdForScattering)
            dontSplitSBends.append(self.o.options.dontSplitSBends)
            elossHistoBinWidth.append(self.o.options.elossHistoBinWidth)
            emax.append(self.o.options.emax)
            emin.append(self.o.options.emin)
            emptyMaterial.append(self.o.options.emptyMaterial)
            eventNumberOffset.append(self.o.options.eventNumberOffset)
            eventOffset.append(self.o.options.eventOffset)
            exportFileName.append(self.o.options.exportFileName)
            exportGeometry.append(self.o.options.exportGeometry)
            exportType.append(self.o.options.exportType)
            ffact.append(self.o.options.ffact)
            fieldModulator.append(self.o.options.fieldModulator)
            g4PhysicsUseBDSIMCutsAndLimits.append(self.o.options.g4PhysicsUseBDSIMCutsAndLimits)
            g4PhysicsUseBDSIMRangeCuts.append(self.o.options.g4PhysicsUseBDSIMRangeCuts)
            geant4MacroFileName.append(str(self.o.options.geant4MacroFileName))
            geant4PhysicsMacroFileName.append(str(self.o.options.geant4PhysicsMacroFileName))
            geant4PhysicsMacroFileNameFromExecOptions.append(str(self.o.options.geant4PhysicsMacroFileNameFromExecOptions))
            generatePrimariesOnly.append(self.o.options.generatePrimariesOnly)
            horizontalWidth.append(self.o.options.horizontalWidth)
            ignoreLocalAperture.append(self.o.options.ignoreLocalAperture)
            ignoreLocalMagnetGeometry.append(self.o.options.ignoreLocalMagnetGeometry)
            importanceVolumeMap.append(self.o.options.importanceVolumeMap)
            importanceWorldGeometryFile.append(self.o.options.importanceWorldGeometryFile)
            includeFringeFields.append(self.o.options.includeFringeFields)
            includeFringeFieldsCavities.append(self.o.options.includeFringeFieldsCavities)
            inputFileName.append(self.o.options.inputFileName)
            integrateKineticEnergyAlongBeamline.append(self.o.options.integrateKineticEnergyAlongBeamline)
            integratorSet.append(self.o.options.integratorSet)
            killedParticlesMassAddedToEloss.append(self.o.options.killedParticlesMassAddedToEloss)
            killNeutrinos.append(self.o.options.killNeutrinos)
            lengthSafety.append(self.o.options.lengthSafety)
            lengthSafetyLarge.append(self.o.options.lengthSafetyLarge)
            magnetGeometryType.append(self.o.options.magnetGeometryType)
            maximumBetaChangePerStep.append(self.o.options.maximumBetaChangePerStep)
            maximumEpsilonStep.append(self.o.options.maximumEpsilonStep)
            maximumEpsilonStepThin.append(self.o.options.maximumEpsilonStepThin)
            maximumPhotonsPerStep.append(self.o.options.maximumPhotonsPerStep)
            maximumStepLength.append(self.o.options.maximumStepLength)
            maximumTrackingTime.append(self.o.options.maximumTrackingTime)
            maximumTrackLength.append(self.o.options.maximumTrackLength)
            maximumTracksPerEvent.append(self.o.options.maximumTracksPerEvent)
            minimumEpsilonStep.append(self.o.options.minimumEpsilonStep)
            minimumEpsilonStepThin.append(self.o.options.minimumEpsilonStepThin)
            minimumKineticEnergy.append(self.o.options.minimumKineticEnergy)
            minimumKineticEnergyTunnel.append(self.o.options.minimumKineticEnergyTunnel)
            minimumRadiusOfCurvature.append(self.o.options.minimumRadiusOfCurvature)
            minimumRange.append(self.o.options.minimumRange)
            modelSplitLevel.append(self.o.options.modelSplitLevel)
            muonSplittingExcludeWeight1Particles.append(self.o.options.muonSplittingExcludeWeight1Particles)
            muonSplittingExclusionWeight.append(self.o.options.muonSplittingExclusionWeight)
            muonSplittingFactor.append(self.o.options.muonSplittingFactor)
            muonSplittingFactor2.append(self.o.options.muonSplittingFactor2)
            muonSplittingThresholdParentEk.append(self.o.options.muonSplittingThresholdParentEk)
            muonSplittingThresholdParentEk2.append(self.o.options.muonSplittingThresholdParentEk2)
            nbinse.append(self.o.options.nbinse)
            nbinsx.append(self.o.options.nbinsx)
            nbinsy.append(self.o.options.nbinsy)
            nbinsz.append(self.o.options.nbinsz)
            neutronKineticEnergyLimit.append(self.o.options.neutronKineticEnergyLimit)
            neutronTimeLimit.append(self.o.options.neutronTimeLimit)
            nGenerate.append(self.o.options.nGenerate)
            nominalMatrixRelativeMomCut.append(self.o.options.nominalMatrixRelativeMomCut)
            nSegmentsPerCircle.append(self.o.options.nSegmentsPerCircle)
            nturns.append(self.o.options.nturns)
            numberOfEventsPerNtuple.append(self.o.options.numberOfEventsPerNtuple)
            outerMaterialName.append(self.o.options.outerMaterialName)
            outputCompressionLevel.append(self.o.options.outputCompressionLevel)
            outputDoublePrecision.append(self.o.options.outputDoublePrecision)
            outputFileName.append(self.o.options.outputFileName)
            outputFormat.append(self.o.options.outputFormat)
            particlesToExcludeFromCuts.append(self.o.options.particlesToExcludeFromCuts)
            physicsEnergyLimitHigh.append(self.o.options.physicsEnergyLimitHigh)
            physicsEnergyLimitLow.append(self.o.options.physicsEnergyLimitLow)
            physicsList.append(self.o.options.physicsList)
            physicsVerbose.append(self.o.options.physicsVerbose)
            physicsVerbosity.append(self.o.options.physicsVerbosity)
            preprocessGDML.append(self.o.options.preprocessGDML)
            preprocessGDMLSchema.append(self.o.options.preprocessGDMLSchema)
            printVar.append(self.o.options.print)
            printFractionEvents.append(self.o.options.printFractionEvents)
            printFractionTurns.append(self.o.options.printFractionTurns)
            printPhysicsProcesses.append(self.o.options.printPhysicsProcesses)
            prodCutElectrons.append(self.o.options.prodCutElectrons)
            prodCutPhotons.append(self.o.options.prodCutPhotons)
            prodCutPositrons.append(self.o.options.prodCutPositrons)
            prodCutProtons.append(self.o.options.prodCutProtons)
            ptcOneTurnMapFileName.append(self.o.options.ptcOneTurnMapFileName)
            randomEngine.append(self.o.options.randomEngine)
            recreate.append(self.o.options.recreate)
            recreateFileName.append(self.o.options.recreateFileName)
            recreateSeedState.append(self.o.options.recreateSeedState)
            removeTemporaryFiles.append(self.o.options.removeTemporaryFiles)
            restoreFTPFDiffractionForAGreater10.append(self.o.options.restoreFTPFDiffractionForAGreater10)
            sampleElementsWithPoleface.append(self.o.options.sampleElementsWithPoleface)
            samplerDiameter.append(self.o.options.samplerDiameter)
            samplersSplitLevel.append(self.o.options.samplersSplitLevel)
            scalingFieldOuter.append(self.o.options.scalingFieldOuter)
            scintYieldFactor.append(self.o.options.scintYieldFactor)
            seed.append(self.o.options.seed)
            seedStateFileName.append(self.o.options.seedStateFileName)
            sensitiveBeamPipe.append(self.o.options.sensitiveBeamPipe)
            sensitiveOuter.append(self.o.options.sensitiveOuter)
            setKeys.append([str(v) for v in self.o.options.setKeys])
            soilMaterial.append(self.o.options.soilMaterial)
            startFromEvent.append(self.o.options.startFromEvent)
            stopSecondaries.append(self.o.options.stopSecondaries)
            storeApertureImpacts.append(self.o.options.storeApertureImpacts)
            storeApertureImpactsAll.append(self.o.options.storeApertureImpactsAll)
            storeApertureImpactsHistograms.append(self.o.options.storeApertureImpactsHistograms)
            storeApertureImpactsIons.append(self.o.options.storeApertureImpactsIons)
            storeCavityInfo.append(self.o.options.storeCavityInfo)
            storeCollimatorHits.append(self.o.options.storeCollimatorHits)
            storeCollimatorHitsAll.append(self.o.options.storeCollimatorHitsAll)
            storeCollimatorHitsIons.append(self.o.options.storeCollimatorHitsIons)
            storeCollimatorHitsLinks.append(self.o.options.storeCollimatorHitsLinks)
            storeCollimatorInfo.append(self.o.options.storeCollimatorInfo)
            storeEloss.append(self.o.options.storeEloss)
            storeElossGlobal.append(self.o.options.storeElossGlobal)
            storeElossHistograms.append(self.o.options.storeElossHistograms)
            storeElossLinks.append(self.o.options.storeElossLinks)
            storeElossLocal.append(self.o.options.storeElossLocal)
            storeElossModelID.append(self.o.options.storeElossModelID)
            storeElossPhysicsProcesses.append(self.o.options.storeElossPhysicsProcesses)
            storeElossPreStepKineticEnergy.append(self.o.options.storeElossPreStepKineticEnergy)
            storeElossStepLength.append(self.o.options.storeElossStepLength)
            storeElossTime.append(self.o.options.storeElossTime)
            storeElossTunnel.append(self.o.options.storeElossTunnel)
            storeElossTunnelHistograms.append(self.o.options.storeElossTunnelHistograms)
            storeElossTurn.append(self.o.options.storeElossTurn)
            storeElossVacuum.append(self.o.options.storeElossVacuum)
            storeElossVacuumHistograms.append(self.o.options.storeElossVacuumHistograms)
            storeElossWorld.append(self.o.options.storeElossWorld)
            storeElossWorldContents.append(self.o.options.storeElossWorldContents)
            storeElossWorldContentsIntegral.append(self.o.options.storeElossWorldContentsIntegral)
            storeElossWorldIntegral.append(self.o.options.storeElossWorldIntegral)
            storeMinimalData.append(self.o.options.storeMinimalData)
            storeModel.append(self.o.options.storeModel)
            storeParticleData.append(self.o.options.storeParticleData)
            storePrimaries.append(self.o.options.storePrimaries)
            storePrimaryHistograms.append(self.o.options.storePrimaryHistograms)
            storeSamplerAll.append(self.o.options.storeSamplerAll)
            storeSamplerCharge.append(self.o.options.storeSamplerCharge)
            storeSamplerIon.append(self.o.options.storeSamplerIon)
            storeSamplerKineticEnergy.append(self.o.options.storeSamplerKineticEnergy)
            storeSamplerMass.append(self.o.options.storeSamplerMass)
            storeSamplerPolarCoords.append(self.o.options.storeSamplerPolarCoords)
            storeSamplerRigidity.append(self.o.options.storeSamplerRigidity)
            storeTrajectory.append(self.o.options.storeTrajectory)
            storeTrajectoryAllVariables.append(self.o.options.storeTrajectoryAllVariables)
            storeTrajectoryDepth.append(self.o.options.storeTrajectoryDepth)
            storeTrajectoryELossSRange.append(self.o.options.storeTrajectoryELossSRange)
            storeTrajectoryEnergyThreshold.append(self.o.options.storeTrajectoryEnergyThreshold)
            storeTrajectoryIon.append(self.o.options.storeTrajectoryIon)
            storeTrajectoryKineticEnergy.append(self.o.options.storeTrajectoryKineticEnergy)
            storeTrajectoryLinks.append(self.o.options.storeTrajectoryLinks)
            storeTrajectoryLocal.append(self.o.options.storeTrajectoryLocal)
            storeTrajectoryMaterial.append(self.o.options.storeTrajectoryMaterial)
            storeTrajectoryMomentumVector.append(self.o.options.storeTrajectoryMomentumVector)
            storeTrajectoryParticle.append(self.o.options.storeTrajectoryParticle)
            storeTrajectoryParticleID.append(self.o.options.storeTrajectoryParticleID)
            storeTrajectoryProcesses.append(self.o.options.storeTrajectoryProcesses)
            storeTrajectorySamplerID.append(self.o.options.storeTrajectorySamplerID)
            storeTrajectorySecondaryParticles.append(self.o.options.storeTrajectorySecondaryParticles)
            storeTrajectoryStepPointLast.append(self.o.options.storeTrajectoryStepPointLast)
            storeTrajectoryStepPoints.append(self.o.options.storeTrajectoryStepPoints)
            storeTrajectoryTime.append(self.o.options.storeTrajectoryTime)
            storeTrajectoryTransportationSteps.append(self.o.options.storeTrajectoryTransportationSteps)
            survey.append(self.o.options.survey)
            surveyFileName.append(self.o.options.surveyFileName)
            teleporterFullTransform.append(self.o.options.teleporterFullTransform)
            temporaryDirectory.append(self.o.options.temporaryDirectory)
            thinElementLength.append(self.o.options.thinElementLength)
            trajConnect.append(self.o.options.trajConnect)
            trajCutGTZ.append(self.o.options.trajCutGTZ)
            trajCutLTR.append(self.o.options.trajCutLTR)
            trajectoryFilterLogicAND.append(self.o.options.trajectoryFilterLogicAND)
            trajNoTransportation.append(self.o.options.trajNoTransportation)
            tunnelAper1.append(self.o.options.tunnelAper1)
            tunnelAper2.append(self.o.options.tunnelAper2)
            tunnelFloorOffset.append(self.o.options.tunnelFloorOffset)
            tunnelIsInfiniteAbsorber.append(self.o.options.tunnelIsInfiniteAbsorber)
            tunnelMaterial.append(self.o.options.tunnelMaterial)
            tunnelMaxSegmentLength.append(self.o.options.tunnelMaxSegmentLength)
            tunnelOffsetX.append(self.o.options.tunnelOffsetX)
            tunnelOffsetY.append(self.o.options.tunnelOffsetY)
            tunnelSoilThickness.append(self.o.options.tunnelSoilThickness)
            tunnelThickness.append(self.o.options.tunnelThickness)
            tunnelType.append(self.o.options.tunnelType)
            tunnelVisible.append(self.o.options.tunnelVisible)
            turnOnMieScattering.append(self.o.options.turnOnMieScattering)
            turnOnOpticalAbsorption.append(self.o.options.turnOnOpticalAbsorption)
            turnOnOpticalSurface.append(self.o.options.turnOnOpticalSurface)
            turnOnRayleighScattering.append(self.o.options.turnOnRayleighScattering)
            uprootCompatible.append(self.o.options.uprootCompatible)
            useASCIISeedState.append(self.o.options.useASCIISeedState)
            useElectroNuclear.append(self.o.options.useElectroNuclear)
            useGammaToMuMu.append(self.o.options.useGammaToMuMu)
            useLENDGammaNuclear.append(self.o.options.useLENDGammaNuclear)
            useMuonNuclear.append(self.o.options.useMuonNuclear)
            useOldMultipoleOuterFields.append(self.o.options.useOldMultipoleOuterFields)
            usePositronToHadrons.append(self.o.options.usePositronToHadrons)
            usePositronToMuMu.append(self.o.options.usePositronToMuMu)
            useScoringMap.append(self.o.options.useScoringMap)
            vacMaterial.append(self.o.options.vacMaterial)
            vacuumPressure.append(self.o.options.vacuumPressure)
            verbose.append(self.o.options.verbose)
            verboseEventBDSIM.append(self.o.options.verboseEventBDSIM)
            verboseEventContinueFor.append(self.o.options.verboseEventContinueFor)
            verboseEventLevel.append(self.o.options.verboseEventLevel)
            verboseEventStart.append(self.o.options.verboseEventStart)
            verboseImportanceSampling.append(self.o.options.verboseImportanceSampling)
            verboseRunLevel.append(self.o.options.verboseRunLevel)
            verboseSensitivity.append(self.o.options.verboseSensitivity)
            verboseSteppingBDSIM.append(self.o.options.verboseSteppingBDSIM)
            verboseSteppingEventContinueFor.append(self.o.options.verboseSteppingEventContinueFor)
            verboseSteppingEventStart.append(self.o.options.verboseSteppingEventStart)
            verboseSteppingLevel.append(self.o.options.verboseSteppingLevel)
            verboseSteppingPrimaryOnly.append(self.o.options.verboseSteppingPrimaryOnly)
            verboseTrackingLevel.append(self.o.options.verboseTrackingLevel)
            vhRatio.append(self.o.options.vhRatio)
            visDebug.append(self.o.options.visDebug)
            visMacroFileName.append(self.o.options.visMacroFileName)
            visVerbosity.append(self.o.options.visVerbosity)
            worldGeometryFile.append(self.o.options.worldGeometryFile)
            worldMaterial.append(self.o.options.worldMaterial)
            worldVacuumVolumeNames.append(self.o.options.worldVacuumVolumeNames)
            worldVolumeMargin.append(self.o.options.worldVolumeMargin)
            writeSeedState.append(self.o.options.writeSeedState)
            xmax.append(self.o.options.xmax)
            xmin.append(self.o.options.xmin)
            xrayAllSurfaceRoughness.append(self.o.options.xrayAllSurfaceRoughness)
            xsize.append(self.o.options.xsize)
            ymax.append(self.o.options.ymax)
            ymin.append(self.o.options.ymin)
            yokeFields.append(self.o.options.yokeFields)
            yokeFieldsMatchLHCGeometry.append(self.o.options.yokeFieldsMatchLHCGeometry)
            ysize.append(self.o.options.ysize)
            zmax.append(self.o.options.zmax)
            zmin.append(self.o.options.zmin)

        dd = {}
        dd['file_idx'] = file_idx
        dd['aper1'] = aper1
        dd['aper2'] = aper2
        dd['aper3'] = aper3
        dd['aper4'] = aper4
        dd['apertureImpactsMinimumKE'] = apertureImpactsMinimumKE
        dd['apertureType'] = apertureType
        dd['beamlineAngle'] = beamlineAngle
        dd['beamlineAxisAngle'] = beamlineAxisAngle
        dd['beamlineAxisX'] = beamlineAxisX
        dd['beamlineAxisY'] = beamlineAxisY
        dd['beamlineAxisZ'] = beamlineAxisZ
        dd['beamlinePhi'] = beamlinePhi
        dd['beamlinePsi'] = beamlinePsi
        dd['beamlineS'] = beamlineS
        dd['beamlineTheta'] = beamlineTheta
        dd['beamlineX'] = beamlineX
        dd['beamlineY'] = beamlineY
        dd['beamlineZ'] = beamlineZ
        dd['beampipeIsInfiniteAbsorber'] = beampipeIsInfiniteAbsorber
        dd['beampipeMaterial'] = beampipeMaterial
        dd['beampipeThickness'] = beampipeThickness
        dd['biasForWorldContents'] = biasForWorldContents
        dd['biasForWorldVacuum'] = biasForWorldVacuum
        dd['biasForWorldVolume'] = biasForWorldVolume
        dd['buildPoleFaceGeometry'] = buildPoleFaceGeometry
        dd['buildTunnel'] = buildTunnel
        dd['buildTunnelFloor'] = buildTunnelFloor
        dd['buildTunnelStraight'] = buildTunnelStraight
        dd['cavityFieldType'] = cavityFieldType
        dd['checkOverlaps'] = checkOverlaps
        dd['chordStepMinimum'] = chordStepMinimum
        dd['chordStepMinimumYoke'] = chordStepMinimumYoke
        dd['circular'] = circular
        dd['coilHeightFraction'] = coilHeightFraction
        dd['coilWidthFraction'] = coilWidthFraction
        dd['collimatorHitsMinimumKE'] = collimatorHitsMinimumKE
        dd['collimatorsAreInfiniteAbsorbers'] = collimatorsAreInfiniteAbsorbers
        dd['defaultBiasMaterial'] = defaultBiasMaterial
        dd['defaultBiasVacuum'] = defaultBiasVacuum
        dd['defaultRangeCut'] = defaultRangeCut
        dd['deltaIntersection'] = deltaIntersection
        dd['deltaOneStep'] = deltaOneStep
        dd['dEThresholdForScattering'] = dEThresholdForScattering
        dd['dontSplitSBends'] = dontSplitSBends
        dd['elossHistoBinWidth'] = elossHistoBinWidth
        dd['emax'] = emax
        dd['emin'] = emin
        dd['emptyMaterial'] = emptyMaterial
        dd['eventNumberOffset'] = eventNumberOffset
        dd['eventOffset'] = eventOffset
        dd['exportFileName'] = exportFileName
        dd['exportGeometry'] = exportGeometry
        dd['exportType'] = exportType
        dd['ffact'] = ffact
        dd['fieldModulator'] = fieldModulator
        dd['g4PhysicsUseBDSIMCutsAndLimits'] = g4PhysicsUseBDSIMCutsAndLimits
        dd['g4PhysicsUseBDSIMRangeCuts'] = g4PhysicsUseBDSIMRangeCuts
        dd['geant4MacroFileName'] = geant4MacroFileName
        dd['geant4PhysicsMacroFileName'] = geant4PhysicsMacroFileName
        dd['geant4PhysicsMacroFileNameFromExecOptions'] = geant4PhysicsMacroFileNameFromExecOptions
        dd['generatePrimariesOnly'] = generatePrimariesOnly
        dd['horizontalWidth'] = horizontalWidth
        dd['ignoreLocalAperture'] = ignoreLocalAperture
        dd['ignoreLocalMagnetGeometry'] = ignoreLocalMagnetGeometry
        dd['importanceVolumeMap'] = importanceVolumeMap
        dd['importanceWorldGeometryFile'] = importanceWorldGeometryFile
        dd['includeFringeFields'] = includeFringeFields
        dd['includeFringeFieldsCavities'] = includeFringeFieldsCavities
        dd['inputFileName'] = inputFileName
        dd['integrateKineticEnergyAlongBeamline'] = integrateKineticEnergyAlongBeamline
        dd['integratorSet'] = integratorSet
        dd['killedParticlesMassAddedToEloss'] = killedParticlesMassAddedToEloss
        dd['killNeutrinos'] = killNeutrinos
        dd['lengthSafety'] = lengthSafety
        dd['lengthSafetyLarge'] = lengthSafetyLarge
        dd['magnetGeometryType'] = magnetGeometryType
        dd['maximumBetaChangePerStep'] = maximumBetaChangePerStep
        dd['maximumEpsilonStep'] = maximumEpsilonStep
        dd['maximumEpsilonStepThin'] = maximumEpsilonStepThin
        dd['maximumPhotonsPerStep'] = maximumPhotonsPerStep
        dd['maximumStepLength'] = maximumStepLength
        dd['maximumTrackingTime'] = maximumTrackingTime
        dd['maximumTrackLength'] = maximumTrackLength
        dd['maximumTracksPerEvent'] = maximumTracksPerEvent
        dd['minimumEpsilonStep'] = minimumEpsilonStep
        dd['minimumEpsilonStepThin'] = minimumEpsilonStepThin
        dd['minimumKineticEnergy'] = minimumKineticEnergy
        dd['minimumKineticEnergyTunnel'] = minimumKineticEnergyTunnel
        dd['minimumRadiusOfCurvature'] = minimumRadiusOfCurvature
        dd['minimumRange'] = minimumRange
        dd['modelSplitLevel'] = modelSplitLevel
        dd['muonSplittingExcludeWeight1Particles'] = muonSplittingExcludeWeight1Particles
        dd['muonSplittingExclusionWeight'] = muonSplittingExclusionWeight
        dd['muonSplittingFactor'] = muonSplittingFactor
        dd['muonSplittingFactor2'] = muonSplittingFactor2
        dd['muonSplittingThresholdParentEk'] = muonSplittingThresholdParentEk
        dd['muonSplittingThresholdParentEk2'] = muonSplittingThresholdParentEk2
        dd['nbinse'] = nbinse
        dd['nbinsx'] = nbinsx
        dd['nbinsy'] = nbinsy
        dd['nbinsz'] = nbinsz
        dd['neutronKineticEnergyLimit'] = neutronKineticEnergyLimit
        dd['neutronTimeLimit'] = neutronTimeLimit
        dd['nGenerate'] = nGenerate
        dd['nominalMatrixRelativeMomCut'] = nominalMatrixRelativeMomCut
        dd['nSegmentsPerCircle'] = nSegmentsPerCircle
        dd['nturns'] = nturns
        dd['numberOfEventsPerNtuple'] = numberOfEventsPerNtuple
        dd['outerMaterialName'] = outerMaterialName
        dd['outputCompressionLevel'] = outputCompressionLevel
        dd['outputDoublePrecision'] = outputDoublePrecision
        dd['outputFileName'] = outputFileName
        dd['outputFormat'] = outputFormat
        dd['physicsVerbose'] = physicsVerbose
        dd['physicsVerbosity'] = physicsVerbosity
        dd['preprocessGDML'] = preprocessGDML
        dd['preprocessGDMLSchema'] = preprocessGDMLSchema
        dd['print'] = printVar
        dd['printFractionEvents'] = printFractionEvents
        dd['printFractionTurns'] = printFractionTurns
        dd['printPhysicsProcesses'] = printPhysicsProcesses
        dd['prodCutElectrons'] = prodCutElectrons
        dd['prodCutPhotons'] = prodCutPhotons
        dd['prodCutPositrons'] = prodCutPositrons
        dd['prodCutProtons'] = prodCutProtons
        dd['ptcOneTurnMapFileName'] = ptcOneTurnMapFileName
        dd['randomEngine'] = randomEngine
        dd['recreate'] = recreate
        dd['recreateFileName'] = recreateFileName
        dd['recreateSeedState'] = recreateSeedState
        dd['removeTemporaryFiles'] = removeTemporaryFiles
        dd['restoreFTPFDiffractionForAGreater10'] = restoreFTPFDiffractionForAGreater10
        dd['sampleElementsWithPoleface'] = sampleElementsWithPoleface
        dd['samplerDiameter'] = samplerDiameter
        dd['samplersSplitLevel'] = samplersSplitLevel
        dd['scalingFieldOuter'] = scalingFieldOuter
        dd['scintYieldFactor'] = scintYieldFactor
        dd['seed'] = seed
        dd['seedStateFileName'] = seedStateFileName
        dd['sensitiveBeamPipe'] = sensitiveBeamPipe
        dd['sensitiveOuter'] = sensitiveOuter
        dd['setKeys'] = setKeys
        dd['soilMaterial'] = soilMaterial
        dd['startFromEvent'] = startFromEvent
        dd['stopSecondaries'] = stopSecondaries
        dd['storeApertureImpacts'] = storeApertureImpacts
        dd['storeApertureImpactsAll'] = storeApertureImpactsAll
        dd['storeApertureImpactsHistograms'] = storeApertureImpactsHistograms
        dd['storeApertureImpactsIons'] = storeApertureImpactsIons
        dd['storeCavityInfo'] = storeCavityInfo
        dd['storeCollimatorHits'] = storeCollimatorHits
        dd['storeCollimatorHitsAll'] = storeCollimatorHitsAll
        dd['storeCollimatorHitsIons'] = storeCollimatorHitsIons
        dd['storeCollimatorHitsLinks'] = storeCollimatorHitsLinks
        dd['storeCollimatorInfo'] = storeCollimatorInfo
        dd['storeEloss'] = storeEloss
        dd['storeElossGlobal'] = storeElossGlobal
        dd['storeElossHistograms'] = storeElossHistograms
        dd['storeElossHistograms'] = storeElossHistograms
        dd['storeElossLinks'] = storeElossLinks
        dd['storeElossLocal'] = storeElossLocal
        dd['storeElossModelID'] = storeElossModelID
        dd['storeElossPhysicsProcesses'] = storeElossPhysicsProcesses
        dd['storeElossPreStepKineticEnergy'] = storeElossPreStepKineticEnergy
        dd['storeElossStepLength'] = storeElossStepLength
        dd['storeElossTime'] = storeElossTime
        dd['storeElossTunnel'] = storeElossTunnel
        dd['storeElossTunnelHistograms'] = storeElossTunnelHistograms
        dd['storeElossTurn'] = storeElossTurn
        dd['storeElossVacuum'] = storeElossVacuum
        dd['storeElossVacuumHistograms'] = storeElossVacuumHistograms
        dd['storeElossWorld'] = storeElossWorld
        dd['storeElossWorldContents'] = storeElossWorldContents
        dd['storeElossWorldContentsIntegral'] = storeElossWorldContentsIntegral
        dd['storeElossWorldIntegral'] = storeElossWorldIntegral
        dd['storeMinimalData'] = storeMinimalData
        dd['storeModel'] = storeModel
        dd['storeParticleData'] = storeParticleData
        dd['storePrimaries'] = storePrimaries
        dd['storePrimaryHistograms'] = storePrimaryHistograms
        dd['storeSamplerAll'] = storeSamplerAll
        dd['storeSamplerCharge'] = storeSamplerCharge
        dd['storeSamplerIon'] = storeSamplerIon
        dd['storeSamplerKineticEnergy'] = storeSamplerKineticEnergy
        dd['storeSamplerMass'] = storeSamplerMass
        dd['storeSamplerPolarCoords'] = storeSamplerPolarCoords
        dd['storeSamplerRigidity'] = storeSamplerRigidity
        dd['storeTrajectory'] = storeTrajectory
        dd['storeTrajectoryAllVariables'] = storeTrajectoryAllVariables
        dd['storeTrajectoryDepth'] = storeTrajectoryDepth
        dd['storeTrajectoryELossSRange'] = storeTrajectoryELossSRange
        dd['storeTrajectoryEnergyThreshold'] = storeTrajectoryEnergyThreshold
        dd['storeTrajectoryIon'] = storeTrajectoryIon
        dd['storeTrajectoryTime'] = storeTrajectoryTime
        dd['storeTrajectoryTransportationSteps'] = storeTrajectoryTransportationSteps
        dd['survey'] = survey
        dd['surveyFileName'] = surveyFileName
        dd['uprootCompatible'] = uprootCompatible
        dd['useASCIISeedState'] = useASCIISeedState
        dd['useElectroNuclear'] = useElectroNuclear
        dd['useGammaToMuMu'] = useGammaToMuMu
        dd['useLENDGammaNuclear'] = useLENDGammaNuclear
        dd['useMuonNuclear'] = useMuonNuclear
        dd['useOldMultipoleOuterFields'] = useOldMultipoleOuterFields
        dd['usePositronToHadrons'] = usePositronToHadrons
        dd['usePositronToMuMu'] = usePositronToMuMu
        dd['useScoringMap'] = useScoringMap
        dd['vacMaterial'] = vacMaterial
        dd['vacuumPressure'] = vacuumPressure
        dd['verbose'] = verbose
        dd['verboseEventBDSIM'] = verboseEventBDSIM
        dd['verboseEventContinueFor'] = verboseEventContinueFor
        dd['verboseEventLevel'] = verboseEventLevel
        dd['verboseEventStart'] = verboseEventStart
        dd['verboseImportanceSampling'] = verboseImportanceSampling
        dd['verboseRunLevel'] = verboseRunLevel
        dd['verboseSteppingBDSIM'] = verboseSteppingBDSIM
        dd['verboseSteppingEventContinueFor'] = verboseSteppingEventContinueFor
        dd['verboseSteppingEventStart'] = verboseSteppingEventStart
        dd['verboseSteppingLevel'] = verboseSteppingLevel
        dd['verboseSteppingPrimaryOnly'] = verboseSteppingPrimaryOnly
        dd['verboseTrackingLevel'] = verboseTrackingLevel
        dd['vhRatio'] = vhRatio
        dd['visDebug'] = visDebug
        dd['visMacroFileName'] = visMacroFileName
        dd['visVerbosity'] = visVerbosity
        dd['worldGeometryFile'] = worldGeometryFile
        dd['worldMaterial'] = worldMaterial
        dd['worldVacuumVolumeNames'] = worldVacuumVolumeNames
        dd['worldVolumeMargin'] = worldVolumeMargin
        dd['writeSeedState'] = writeSeedState
        dd['xmax'] = xmax
        dd['xmin'] = xmin
        dd['xrayAllSurfaceRoughness'] = xrayAllSurfaceRoughness
        dd['xsize'] = xsize
        dd['ymax'] = ymax
        dd['ymin'] = ymin
        dd['yokeFields'] = yokeFields
        dd['yokeFieldsMatchLHCGeometry'] = yokeFieldsMatchLHCGeometry
        dd['ysize'] = ysize
        dd['zmax'] = zmax
        dd['zmin'] = zmin

        df = _pd.DataFrame(dd)
        #return dd
        return df

    def get_run(self):
        pass

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

        df = _pd.DataFrame(dd)
        return df

    def get_primary(self):

        x  = []
        xp = []
        y  = []
        yp = []
        z  = []
        zp = []
        T  = []
        theta = []
        energy = []
        partID = []
        trackID = []
        weight = []
        turnNumber = []

        # primary
        nprimary = 0
        primary = self.e.Primary

        for ievt in range(0, self.et.GetEntries()):
            self.et.GetEntry(ievt)

            x.append(primary.x[0])
            xp.append(primary.xp[0])
            y.append(primary.y[0])
            yp.append(primary.yp[0])
            z.append(primary.z)
            zp.append(primary.zp[0])
            T.append(primary.T[0])
            theta.append(primary.theta[0])
            energy.append(primary.energy[0])
            partID.append(primary.partID[0])
            trackID.append(primary.trackID[0])
            weight.append(primary.weight[0])
            turnNumber.append(primary.turnNumber[0])


        dd = {}
        dd['x']  = x
        dd['xp'] = xp
        dd['y']  = y
        dd['yp'] = yp
        dd['z']  = z
        dd['zp'] = zp
        dd['T'] = T
        dd['theta'] = theta
        dd['energy'] = energy
        dd['partID'] = partID
        dd['trackID'] = trackID
        dd['weight'] = weight
        dd['turnNumber'] = turnNumber

        df = _pd.DataFrame(dd)
        return df

    def get_primary_global(self):
        pass

    def get_eloss(self):

        eloss = self.e.Eloss

        energy = []
        S      = []
        partID = []

        for ievt in range(0, self.et.GetEntries()):
            self.et.GetEntry(ievt)
            for ieloss in range(0, eloss.n) :
                energy.append(eloss.energy[ieloss])
                S.append(eloss.S[ieloss])
                if self.o.options.storeElossLinks :
                    partID.append(eloss.partID[ieloss])

        dd = {}
        dd['energy'] = energy
        dd['S'] = S
        if self.o.options.storeElossLinks :
            dd['partID'] = partID


        df = _pd.DataFrame(dd)
        return df


    def get_primary_first_hit(self):
        pass

    def get_primary_last_hit(self):
        pass

    def get_aperture_impacts(self):
        pass

    def get_sampler(self, sampler_name):
        pass

    def get_trajectories(self, i_evnt):
        self.et.GetEntry(i_evnt)

        traj = self.e.Trajectory

        nstep = []
        partID = []
        trackID = []
        for i in range(0,len(traj.partID)) :
            nstep.append(len(traj.XYZ[i]))
            partID.append(traj.partID[i])
            trackID.append(traj.trackID[i])

        dd = {}
        dd['nstep'] = nstep
        dd['partID'] = partID
        dd['trackID'] = trackID

        df = _pd.DataFrame(dd)

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

        df = _pd.DataFrame(dd)

        return df


    def get_histograms(self):
        pass

    def get_sampler(self, sampler_name):
        if sampler_name not in self.sampler_names:
            print("Sampler name not recognized")
            return

        sampler = self.e.GetSampler(sampler_name)

        evt_number = []
        x  = []
        xp = []
        y  = []
        yp = []
        z  = []
        zp = []
        T  = []
        energy = []
        partID = []
        trackID = []

        for ievt in range(0, self.et.GetEntries()):
            self.et.GetEntry(ievt)

            for ipart in range(0, sampler.n) :
                evt_number.append(ievt)
                x.append(sampler.x[ipart])
                xp.append(sampler.xp[ipart])
                y.append(sampler.y[ipart])
                yp.append(sampler.yp[ipart])
                z.append(sampler.z)
                zp.append(sampler.zp[ipart])
                T.append(sampler.T[ipart])
                energy.append(sampler.energy[ipart])
                partID.append(sampler.partID[ipart])
                trackID.append(sampler.trackID[ipart])

        dd = {}
        dd['event_number'] = evt_number
        dd['x'] = x
        dd['xp'] = xp
        dd['y'] = y
        dd['yp'] = yp
        dd['z'] = z
        dd['zp'] = zp
        dd['T'] = T
        dd['energy'] = energy
        dd['partID'] = partID
        dd['trackID'] = trackID

        df = _pd.DataFrame(dd)
        return df

    def get_csampler(self, sampler_name):
        if sampler_name not in self.csampler_names:
            print("Sampler name not recognized")
            return

    def get_ssampler(self, sampler_name):
        if sampler_name not in self.ssampler_names:
            print("Sampler name not recognized")
            return


