import sys

# requires the pyhepmc package
try:
    import pyhepmc as _hep
except ImportError:
    # pip install .[pyhepmc] --user
    print("pyhepmc module not found.")
    sys.exit(1)

import os.path as _path
import pybdsim.Data as _Data

def BdsimSamplerData2Hepmc2(bdsimFile,outputFileName,samplerName,ZForHits=0,pidList=[]):
    """
    !!! hepmc2 format does not allow per event weight assignment,
    !!! for this please use BdsimSamplerData2Hepmc3()

    bdsimFile - (str) - path to bdsim raw file (can be combined)
    outputFileName - (str) - for HEPMC3 output file
    samplerName - (str) - name of branch in bdsim file
    ZForHits - (float) - Z coordinate for z and ct info of all vertices
    pidList - (list[int]) - list of PDG IDs to include in output file (leave empty for all)
    """

    if not _path.isfile(bdsimFile):
        raise IOError("File {} not found!".format(bdsimFile))
    else:
        print("Loading input file: {}.".format(bdsimFile))
        fBDS = _Data.Load(bdsimFile)

    fHEP = _hep.io.WriterAsciiHepMC2(outputFileName)

    mToMM = 1e3
    eventID = 0
    for event in fBDS.GetEventTree():
        # sample plane data branch
        s = getattr(event, samplerName)

        # check event for particle selection
        if len(pidList) > 0:
            samplerPIDs = list(s.partID)
            containsRelevant = any([PID in samplerPIDs for PID in pidList])
            if not containsRelevant:
                continue

        for ti in range(s.n):
            # apply selection
            if len(pidList) != 0 and s.partID[ti] not in pidList:
                continue

            # set event info
            evt = _hep.GenEvent(_hep.Units.GEV,_hep.Units.MM)
            evt.event_number = eventID
            evt.attributes['signal_process_id'] = -1 # point to 1st vtx for optimization

            # xp, yp, zp are components of the unit momentum vector
            # p is the momentum magnitude, 'energy' the total energy
            # next we define the PID and 'status' (1 for undecayed particle, 4 for beam particle)
            prt1 = _hep.GenParticle((s.xp[ti]*s.p[ti], s.yp[ti]*s.p[ti], s.zp[ti]*s.p[ti], s.energy[ti]), s.partID[ti], 1)
            prt2 = _hep.GenParticle((s.xp[ti]*s.p[ti], s.yp[ti]*s.p[ti], s.zp[ti]*s.p[ti], s.energy[ti]), s.partID[ti], 1)
            # generate vertex with x,y,z,ct
            vtx = _hep.GenVertex((s.x[ti]*mToMM, s.y[ti]*mToMM, ZForHits*mToMM, ZForHits*mToMM))
            vtx.add_particle_in(prt1)
            vtx.add_particle_out(prt2)
            evt.add_vertex(vtx)

            fHEP.write(evt)
            eventID += 1

    fHEP.close()
    print("{} events written to HEPMC2 file {}.".format(eventID,outputFileName))

def BdsimSamplerData2Hepmc3(bdsimFile,outputFileName,samplerName,ZForHits=0,pidList=[],weightsName=""):
    """
    bdsimFile - (str) - path to bdsim raw file (can be combined or skimmed)
    outputFileName - (str) - for HEPMC3 output file
    samplerName - (str) - name of branch in bdsim file
    ZForHits - (float) - Z coordinate for z and ct info of all vertices
    pidList - (list[int]) - list of PDG IDs to include in output file (leave empty for all)
    weightsName - (str) - user assigned name for statistical weights (leave "" to exclude weights)
    """
    if not _path.isfile(bdsimFile):
        raise IOError("File {} not found!".format(bdsimFile))
    else:
        print("Loading input file: {}.".format(bdsimFile))
        fBDS = _Data.Load(bdsimFile)

    fHEP = _hep.io.WriterAscii(outputFileName)

    run_info = _hep.GenRunInfo()
    # calculate rolling weight factor for skimmed events
    skimWeight = 1
    weightNameStr = ""
    if fBDS.header.skimmedFile:
        nEventsOriginal = fBDS.header.nOriginalEvents
        nEvents = int(fBDS.GetEventTree().GetEntries())
        skimWeight = nEvents/nEventsOriginal # python3 upgrades this to a float
        weightNameStr += "skimmed_"
    if len(weightsName) > 0:
        # add weight name to run_info to store weights in HEPMC3 file
        weightNameStr += weightsName
    if weightNameStr != "":
        run_info.weight_names = [weightNameStr]

    mToMM = 1e3
    eventID = 0
    for event in fBDS.GetEventTree():
        # sample plane data branch
        s = getattr(event, samplerName)

        # check event for particle selection
        if len(pidList) > 0:
            samplerPIDs = list(s.partID)
            containsRelevant = any([PID in samplerPIDs for PID in pidList])
            if not containsRelevant:
                continue

        for ti in range(s.n):
            # apply selection
            if len(pidList) != 0 and s.partID[ti] not in pidList:
                continue

            # set event info
            evt = _hep.GenEvent(_hep.Units.GEV,_hep.Units.MM)
            evt.event_number = eventID
            evt.attributes['signal_process_id'] = -1 # point to 1st vtx for optimization
            evt.run_info = run_info

            # compound weight
            if len(weightsName) > 0:
                try:
                    compoundWeight = skimWeight*s.weight[ti]
                except:
                    compoundWeight = skimWeight
            evt.set_weight(weightNameStr,compoundWeight)

            # xp, yp, zp are components of the unit momentum vector
            # p is the momentum magnitude, 'energy' the total energy
            # next we define the PID and 'status' (1 for undecayed particle, 4 for beam particle)
            prt1 = _hep.GenParticle((s.xp[ti]*s.p[ti], s.yp[ti]*s.p[ti], s.zp[ti]*s.p[ti], s.energy[ti]), s.partID[ti], 1)
            prt2 = _hep.GenParticle((s.xp[ti]*s.p[ti], s.yp[ti]*s.p[ti], s.zp[ti]*s.p[ti], s.energy[ti]), s.partID[ti], 1)
            # generate vertex with x,y,z,ct
            vtx = _hep.GenVertex((s.x[ti]*mToMM, s.y[ti]*mToMM, ZForHits*mToMM, ZForHits*mToMM))
            vtx.add_particle_in(prt1)
            vtx.add_particle_out(prt2)
            evt.add_vertex(vtx)

            fHEP.write(evt)
            eventID += 1

    fHEP.close()
    print("{} events written to HEPMC3 file {}.".format(eventID,outputFileName))