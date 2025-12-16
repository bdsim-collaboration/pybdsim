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
        dd['file_idx'] = []
        dd['file_name'] = []

        for attrib in run_attribs:
            dd[attrib] = []

        for ibeam in range(0, self.bt.GetEntries()) :
            self.bt.GetEntry(ibeam)
            dd['file_name'].append(self.bt.GetFile().GetName())
            dd['file_idx'].append(self.get_filename_index(self.bt.GetFile().GetName()))
            for attrib in run_attribs:
                if attrib == "setKeys" :
                    dd[attrib].append([str(v) for v in getattr(self.b.beam, attrib)])
                elif attrib == "spaceDistrType" :
                    dd[attrib].append(str(getattr(self.b.beam, attrib)))
                else :
                    dd[attrib].append(getattr(self.b.beam, attrib))

        df = _pd.DataFrame(dd)

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
        for attrib in option_attribs:
            dd[attrib] = []

        for iopt in range(0, self.ot.GetEntries()):
            self.ot.GetEntry(iopt)
            dd['file_name'].append(self.ot.GetFile().GetName())
            dd['file_idx'].append(self.get_filename_index(self.ot.GetFile().GetName()))

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

        df = _pd.DataFrame(dd)

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

        primary_attribs = ["x","xp","y","yp","z","zp","T","theta",
                           "energy","partID","trackID","weight",
                           "turnNumber"]

        # primary
        nprimary = 0
        primary = self.e.Primary

        dd = {}
        dd['file_idx'] = []
        dd['primary_idx'] = []
        for attrib in primary_attribs:
            dd[attrib] = []

        for ievt in range(0, self.et.GetEntries()):
            self.et.GetEntry(ievt)

            for iprim in range(0, primary.n) :
                dd['file_idx'].append(self.get_filename_index(self.et.GetFile().GetName()))
                dd['primary_idx'].append(iprim)
                for attrib in primary_attribs:
                    # print(attrib,getattr(primary, attrib))
                    if attrib == "z" :
                        dd[attrib].append(getattr(primary, attrib))
                    else:
                        dd[attrib].append(getattr(primary, attrib)[iprim])

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

        dd = {}
        dd['file_idx'] = []
        dd['event_idx'] = []
        dd['sampler_idx'] = []
        dd['x'] = []
        dd['xp'] = []
        dd['y'] = []
        dd['yp'] = []
        dd['z'] = []
        dd['zp'] = []
        dd['T'] = []
        dd['energy'] = []
        dd['partID'] = []
        dd['trackID'] = []
        dd['weight'] = []

        for ievt in range(0, self.et.GetEntries()):
            self.et.GetEntry(ievt)

            for ipart in range(0, sampler.n) :
                dd['file_idx'].append(self.get_filename_index(self.ot.GetFile().GetName()))
                dd['event_idx'].append(ievt)
                dd['sampler_idx'].append(ipart)
                dd['x'].append(sampler.x[ipart])
                dd['xp'].append(sampler.xp[ipart])
                dd['y'].append(sampler.y[ipart])
                dd['yp'].append(sampler.yp[ipart])
                dd['z'].append(sampler.z)
                dd['zp'].append(sampler.zp[ipart])
                dd['T'].append(sampler.T[ipart])
                dd['energy'].append(sampler.energy[ipart])
                dd['partID'].append(sampler.partID[ipart])
                dd['trackID'].append(sampler.trackID[ipart])
                dd['weight'].append(sampler.weight[ipart])

        df = _pd.DataFrame(dd)
        return df

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
            lc = self._link_Bunch.GetNextParticleLocal()
            pd = self._link_Bunch.ParticleDefinition()
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