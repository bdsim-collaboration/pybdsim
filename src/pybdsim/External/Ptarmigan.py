import numpy as _np
import pybdsim as _bd
import h5py as _h5


particle_dict = {11: {"Name": "electron", "mass": 0.511e-3},
                 -11: {"Name": "positron", "mass": 0.511e-3},
                 22: {"Name": "photon", "mass": 0}}


def getBdsimLastSamplerInDF(bdsimfile, mu_z=0, sigma_z=25e-12):
    bdsim = _bd.DataPandas.BDSIMOutput(bdsimfile)
    last_sampler = bdsim.get_sampler_names()[-1]
    df = bdsim.get_sampler(last_sampler)
    for partID in particle_dict.keys():
        df.loc[df['partID'] == partID, 'mass'] = particle_dict[partID]['mass']

    df['Px'] = df['xp'] * _np.sqrt(pow(df['energy'], 2) - pow(df['mass'], 2))
    df['Py'] = df['yp'] * _np.sqrt(pow(df['energy'], 2) - pow(df['mass'], 2))
    df['Pz'] = _np.sqrt(pow(df['energy'], 2) - pow(df['Px'], 2) - pow(df['Py'], 2) - pow(df['mass'], 2))

    df['z'] = _np.array([_np.random.normal(mu_z, sigma_z) for i in range(len(df['x']))])

    # We assume that the spacetime interval s^2 is 0
    df['T'] = _np.sqrt(pow(df['x'], 2) + pow(df['y'], 2) + pow(df['z'], 2))

    return df


def writeBdsimDataInH5(bdsimfile, hdf5file, mu_z=0, sigma_z=25e-12):
    df = getBdsimLastSamplerInDF(bdsimfile, mu_z, sigma_z)

    h5 = _h5.File(hdf5file, 'w')
    h5["beam_axis"] = "+z"
    h5['config/unit/momentum'] = "GeV/c"
    h5['config/unit/position'] = "m"

    for partID in df['partID'].unique():
        npart = len(df[df['partID'] == partID])
        partname = particle_dict[partID]['Name']

        Momentum = _np.array([])
        Position = _np.array([])
        Weight = _np.array([])
        for i in df.index:
            mom4vect = _np.array([df.iloc[i]['energy'], df.iloc[i]['Px'], df.iloc[i]['Py'], df.iloc[i]['Pz']])
            pos4vect = _np.array([df.iloc[i]['T'], df.iloc[i]['x'], df.iloc[i]['y'], df.iloc[i]['z']])

            Momentum = _np.append(Momentum, mom4vect)
            Position = _np.append(Position, pos4vect)
            Weight = _np.append(Weight, df.iloc[i]['weight'])

        h5.create_dataset('final-state/{}/momentum'.format(partname), data=_np.reshape(Momentum, (npart, 4)))
        h5.create_dataset('final-state/{}/position'.format(partname), data=_np.reshape(Position, (npart, 4)))
        h5.create_dataset('final-state/{}/weight'.format(partname), data=Weight)

    h5.close()

def getH5DataInDict(hdf5file):
    h5 = _h5.File(hdf5file)
    data_dict = {}
    for particle in h5['final-state'].keys():
        if particle != 'laser':
            data_dict[particle] = {}
            data_dict[particle]['partID'] = [key for key, value in particle_dict.items() if value['Name'] == particle][0]
            data_dict[particle]['momentum'] = h5['final-state/{}/momentum'.format(particle)][()]
            data_dict[particle]['position'] = h5['final-state/{}/position'.format(particle)][()]
            data_dict[particle]['weight'] = h5['final-state/{}/weight'.format(particle)][()]
    return data_dict
    h5.close()


def writeDataInBdsim(hdf5file, outputfilename):
    data_dict = getH5DataInDict(hdf5file)
    file = open(outputfilename, 'w')
    for particle in data_dict.keys():
        partID = data_dict[particle]['partID']
        weight = data_dict[particle]['weight'][:]

        energy = data_dict[particle]['momentum'][:][:, 0]
        momX = data_dict[particle]['momentum'][:][:, 1]
        momY = data_dict[particle]['momentum'][:][:, 2]

        posX = data_dict[particle]['position'][:][:, 1]
        posY = data_dict[particle]['position'][:][:, 2]
        posZ = data_dict[particle]['position'][:][:, 3]

        angX = momX / _np.sqrt(pow(energy, 2) - pow(particle_dict[partID]['mass'], 2))
        angY = momY / _np.sqrt(pow(energy, 2) - pow(particle_dict[partID]['mass'], 2))

        for i in range(len(energy)):
            file.write("{} {} {} {} {} {} {} {} \n".format(posX[i], angX[i], posY[i], angY[i], posZ[i], energy[i], weight[i], partID))
    file.close()