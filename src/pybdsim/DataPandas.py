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
    print("fail")
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

        if not _path.isfile(filepath) :
            print("file not found",filepath)
            return

        self.root_file = _ROOT.DataLoader(filepath)

        self.et = self.root_file.GetEventTree()
        self.e  = self.root_file.GetEvent()
        self.et.GetEntry(0)
        self.sampler_names = list(self.root_file.GetSamplerNames())

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

    def get_sampler_names(self):
        return self.sampler_names

    def get_1dhisto_names(self):
        hist_names = []
        for h in self.r.Histos.Get1DHistograms():
            hist_names.append(h.GetName())

        return hist_names

    def get_2dhisto_names(self):
        hist_names = []
        for h in self.r.Histos.Get2DHistograms():
            hist_names.append(h.GetName())

        return hist_names

    def get_3dhisto_names(self):
        hist_names = []
        for h in self.r.Histos.Get3DHistograms():
            hist_names.append(h.GetName())

        return hist_names

    def get_4dhisto_names(self):
        hist_names = []
        for h in self.r.Histos.Get4DHistograms():
            hist_names.append(h.GetName())

        return hist_names

    def get_1dhisto(self, name, evnt = -1):

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

    def get_2dhisto(self, name, evnt = -1):

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

    def get_3dhisto(self, name, evnt = -1):

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
        pass

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
        staRefPos_x = []
        staRefPos_y = []
        staRefPos_z = []
        staS = []

        midPos_x = []
        midPos_y = []
        midPos_z = []
        midRefPos_x = []
        midRefPos_y = []
        midRefPos_z = []
        midS = []
        midT = []

        endPos_x = []
        endPos_y = []
        endPos_z = []
        endRefPos_x = []
        endRefPos_y = []
        endRefPos_z = []
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
                # TODO staRot
                staRefPos_x.append(self.m.model.staRefPos[ielement].x())
                staRefPos_y.append(self.m.model.staRefPos[ielement].y())
                staRefPos_z.append(self.m.model.staRefPos[ielement].z())
                # TODO staRefRot
                staS.append(self.m.model.staS[ielement])

                midPos_x.append(self.m.model.midPos[ielement].x())
                midPos_y.append(self.m.model.midPos[ielement].y())
                midPos_z.append(self.m.model.midPos[ielement].z())
                # TODO midRot
                midRefPos_x.append(self.m.model.midRefPos[ielement].x())
                midRefPos_y.append(self.m.model.midRefPos[ielement].y())
                midRefPos_z.append(self.m.model.midRefPos[ielement].z())
                # TODO midRefRot
                midS.append(self.m.model.midS[ielement])
                midT.append(self.m.model.midT[ielement])

                endPos_x.append(self.m.model.endPos[ielement].x())
                endPos_y.append(self.m.model.endPos[ielement].y())
                endPos_z.append(self.m.model.endPos[ielement].z())
                # TODO endRot
                endRefPos_x.append(self.m.model.endRefPos[ielement].x())
                endRefPos_y.append(self.m.model.endRefPos[ielement].y())
                endRefPos_z.append(self.m.model.endRefPos[ielement].z())
                # TODO endRefRot
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
                staEk.append(self.m.model.staEk[ielement])
                staP.append(self.m.model.staP[ielement])

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
        dd['staRefPos_x'] = staRefPos_x
        dd['staRefPos_y'] = staRefPos_y
        dd['staRefPos_z'] = staRefPos_z
        dd['staS'] = staS
        dd['midPos_x'] = midPos_x
        dd['midPos_y'] = midPos_y
        dd['midPos_z'] = midPos_z
        dd['midRefPos_x'] = midRefPos_x
        dd['midRefPos_y'] = midRefPos_y
        dd['midRefPos_z'] = midRefPos_z
        dd['midS'] = midS
        dd['midT'] = midT
        dd['endPos_x'] = endPos_x
        dd['endPos_y'] = endPos_y
        dd['endPos_z'] = endPos_z
        dd['endRefPos_x'] = endRefPos_x
        dd['endRefPos_y'] = endRefPos_y
        dd['endRefPos_z'] = endRefPos_z
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
        pass

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



