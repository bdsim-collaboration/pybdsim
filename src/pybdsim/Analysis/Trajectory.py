import hashlib as _hashlib

def find_primary_index(t) :
    '''
    :param t: Trajectory
    :type t: BDSOutputROOTEventTrajectory
    :return: Index of primary particles
    :rtype: int

    Find the primary trajectory index
    '''

    ntraj = t.n

    for itraj in range(ntraj) :
        if t.parentID[itraj] == 0 :
            return itraj

def build_topdown_tree(t) :
    '''
    :param t: Trajectory
    :type t: BDSOutputROOTEventTrajectory
    :return: (daughter_index, daugher_step, daughter_energy)
    :rtype: tuple

    Build arrays to allow top down tree navigation (daugter_index, daugter_step, daughter_energy)
    Order navigation (daughter_index) is in order of step, energy, z position.
    '''
    ntraj = t.n

    daughter_index = [[] for _ in range(ntraj)]
    daughter_step = [[] for _ in range(ntraj)]
    daughter_energy = [[] for _ in range(ntraj)]
    daughter_z = [[] for _ in range(ntraj)]

    # loop over all trajectories
    for itraj in range(ntraj) :

        if t.parentID[itraj] == 0 :
            continue

        parent_index = t.parentIndex[itraj]
        parent_step  = t.parentStepIndex[itraj]
        daughter_index[parent_index].append(itraj)
        daughter_step[parent_index].append(parent_step)
        daughter_energy[parent_index].append(t.kineticEnergy[itraj][0])
        daughter_z[parent_index].append(t.kineticEnergy[itraj][1])

    # loop over all trajectories and sort on daughter_step
    for itraj in range(ntraj) :
        sorted_pairs = sorted(zip(daughter_step[itraj], daughter_index[itraj], daughter_energy[itraj], daughter_z[itraj]), key=lambda x: (x[0], x[2], x[3]))
        if len(sorted_pairs) == 0 :
            continue

        (daughter_step_sorted,
         daughter_index_sorted,
         daughter_energy_sorted,
         daughter_z_sorted) = zip(*sorted_pairs)

        daughter_index[itraj] = list(daughter_index_sorted)
        daughter_step[itraj] = list(daughter_step_sorted)
        daughter_energy[itraj] = list(daughter_energy_sorted)
        daughter_z[itraj] = list(daughter_z_sorted)

    return daughter_index, daughter_step, daughter_energy

def hash_trajectory(t,
                    itraj,
                    debugFile = None) :

    '''
    :param t: Trajectory
    :type t: BDSOutputROOTEventTrajectory
    :param itraj: Trajectory index
    :type itraj: int
    :param debugFile: debug file name
    :type debugFile: str
    :return: hash
    :rtype: bytes (256)

    Example hash function
    '''

    nstep = t.xyz[itraj].size()

    depth = t.depth[itraj]
    parentID = t.parentID[itraj]
    parentIndex = t.parentIndex[itraj]
    parentStepIndex = t.parentStepIndex[itraj]
    partID = t.partID[itraj]

    charge = t.charge[itraj]
    energyDeposit = t.energyDeposit[itraj]
    ionA = t.ionA[itraj]
    ionZ = t.ionZ[itraj]
    kineticEnergy = t.kineticEnergy[itraj]
    mass = t.mass[itraj]
    modelIndicies = t.modelIndicies[itraj]
    nElectrons = t.nElectrons[itraj]

    pxpypz = t.pxpypz[itraj]
    PXPYPZ = t.PXPYPZ[itraj]
    xyz = t.xyz[itraj]
    XYZ = t.XYZ[itraj]
    T = t.T[itraj]
    S = t.S[itraj]

    hash = _hashlib.sha256(str(nstep).encode('utf-8')).digest()
    hash += _hashlib.sha256(str(depth).encode('utf-8')).digest()
    hash += _hashlib.sha256(str(parentID).encode('utf-8')).digest()
    hash += _hashlib.sha256(str(parentStepIndex).encode('utf-8')).digest()
    hash += _hashlib.sha256(str(partID).encode('utf-8')).digest()

    for istep in range(nstep) :
        hash += _hashlib.sha256(str(charge[istep]).encode('utf-8')).digest()
        hash += _hashlib.sha256(str(energyDeposit[istep]).encode('utf-8')).digest()
        hash += _hashlib.sha256(str(ionA[istep]).encode('utf-8')).digest()
        hash += _hashlib.sha256(str(ionZ[istep]).encode('utf-8')).digest()
        hash += _hashlib.sha256(str(kineticEnergy[istep]).encode('utf-8')).digest()
        hash += _hashlib.sha256(str(mass[istep]).encode('utf-8')).digest()
        hash += _hashlib.sha256(str(modelIndicies[istep]).encode('utf-8')).digest()
        hash += _hashlib.sha256(str(nElectrons[istep]).encode('utf-8')).digest()
        hash += _hashlib.sha256(str(xyz[istep][0]).encode('utf-8')).digest()
        hash += _hashlib.sha256(str(xyz[istep][1]).encode('utf-8')).digest()
        hash += _hashlib.sha256(str(xyz[istep][2]).encode('utf-8')).digest()
        hash += _hashlib.sha256(str(XYZ[istep][0]).encode('utf-8')).digest()
        hash += _hashlib.sha256(str(XYZ[istep][1]).encode('utf-8')).digest()
        hash += _hashlib.sha256(str(XYZ[istep][2]).encode('utf-8')).digest()
        hash += _hashlib.sha256(str(pxpypz[istep][0]).encode('utf-8')).digest()
        hash += _hashlib.sha256(str(pxpypz[istep][1]).encode('utf-8')).digest()
        hash += _hashlib.sha256(str(pxpypz[istep][2]).encode('utf-8')).digest()
        hash += _hashlib.sha256(str(PXPYPZ[istep][0]).encode('utf-8')).digest()
        hash += _hashlib.sha256(str(PXPYPZ[istep][1]).encode('utf-8')).digest()
        hash += _hashlib.sha256(str(PXPYPZ[istep][2]).encode('utf-8')).digest()
        hash += _hashlib.sha256(str(T[istep]).encode('utf-8')).digest()
        hash += _hashlib.sha256(str(S[istep]).encode('utf-8')).digest()

    ret = _hashlib.sha256(hash).digest()

    if debugFile is not None  :
        debugFile.write(str(t.trackID[itraj])+" "+str(nstep)+" "+str(ret.hex())+"\n")
        
    return ret

def visit_trajectories(t,
                       itraj,
                       daugher_index,
                       daughter_step,
                       debugFile = None,
                       traj_hash_func = None,
                       ) :
    '''
    :param t: Trajectory
    :type t:  BDSOutputROOTEventTrajectory
    :param daugher_index: daugher indices
    :type daugher_index:  list
    :param daugher_step: daugher step indices
    :type daugher_step:  list
    :param debugFile: debug file name
    :type debugFile:  str
    :param traj_hash_func: trajectory hash function
    :type traj_hash_func:  function
    :return: tuple of visited trackIndex, hash
    :rtype: tuple

    Visitor function for each trajectory recursively. Each trajectory is hashed and combined.
    '''

    visited = [itraj]

    if traj_hash_func is None :
        hash = hash_trajectory(t,itraj, debugFile)
    else :
        hash = traj_hash_func(t,itraj, debugFile)

    for dtraj in daugher_index[itraj]:
        dvisited, dhash = visit_trajectories(t, dtraj, daugher_index, daughter_step, debugFile, traj_hash_func)
        visited.extend(dvisited)
        hash = _hashlib.sha256(hash + dhash).digest()
        if debugFile is not None :
            debugFile.write(str(hash.hex())+"\n")

    return visited, hash

def traverse_trajectories(t,
                          debugFile = None,
                          traj_hash_func = None) :

    '''
    :param t: Trajectory
    :type t:  BDSOutputROOTEventTrajectory
    :param debugFile: debug file
    :type debugFile:  str
    :param traj_hash_func: trajectory hash function
    :type traj_hash_func:  function

    Function to visit all (connected) trajectories in a event trajectory data structure.
    '''

    f = None
    if debugFile is not None:
        f = open(debugFile, 'w')

    # build top down trajectory
    daughter_index, daughter_step, daughter_energy = build_topdown_tree(t)

    # find primary
    iprimary = find_primary_index(t)

    # recurse down tree
    visted, hash = visit_trajectories(t, iprimary, daughter_index, daughter_step, f, traj_hash_func)

    assert len(visted) == len(set(visted))

    if debugFile :
        f.close()

    return visted, hash