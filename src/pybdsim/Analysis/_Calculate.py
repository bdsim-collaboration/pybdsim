import pybdsim.Data as _Data
import numpy as _np

def CalculateRMatrix(root_file_name, sampler1_name, sampler2_name, size=4) :
    """
    **CalculateRMatrix** calculate rmatrix from a BDSIM output root file and two sampler names

    Example:

    >>> rmatrix = pybdsim.Analysis.CalculateRMatrix('output.root', 'd1','e1')

    returns numpy.array 4x4 (or 6x6)

    +-----------------+---------------------------------------------------------+
    | **Parameters**  | **Description**                                         |
    +-----------------+---------------------------------------------------------+
    | root_file_name  | Input root file name (raw output)                       |
    +-----------------+---------------------------------------------------------+
    | sampler1_name   | First sampler name to take coordinates for calculation  |
    +-----------------+---------------------------------------------------------+
    | sampler2_name   | Second sampler name to take coordinates for calculation |
    +-----------------+---------------------------------------------------------+
    | size (int)      | 4 (x, x', y, y') or 6 (x,x',y,y',T,E)                   |
    +-----------------+---------------------------------------------------------+
    """

    root_file = _Data.Load(root_file_name)
    sampler1_data = _Data.SamplerData(root_file, sampler1_name)
    sampler2_data = _Data.SamplerData(root_file, sampler2_name)

    if size == 4 :
        sampler1_matrix = _np.array([sampler1_data.data['x'],
                                        sampler1_data.data['xp'],
                                        sampler1_data.data['y'],
                                        sampler1_data.data['yp']])

        sampler2_matrix = _np.array([sampler2_data.data['x'],
                                        sampler2_data.data['xp'],
                                        sampler2_data.data['y'],
                                        sampler2_data.data['yp']])
    elif size == 6:
        sampler1_time = sampler1_data.data['T']
        sampler2_time = sampler2_data.data['T']
        sampler1_energy = sampler1_data.data['energy']
        sampler2_energy = sampler2_data.data['energy']

        sampler1_matrix = _np.array([sampler1_data.data['x'],
                                     sampler1_data.data['xp'],
                                     sampler1_data.data['y'],
                                     sampler1_data.data['yp'],
                                     sampler1_time - sampler1_time.mean(),
                                     sampler1_energy - sampler1_energy.mean()])

        sampler2_matrix = _np.array([sampler2_data.data['x'],
                                     sampler2_data.data['xp'],
                                     sampler2_data.data['y'],
                                     sampler2_data.data['yp'],
                                     sampler2_time - sampler2_time.mean(),
                                     sampler2_energy-sampler2_energy.mean()])

    sampler1_matrix_inv = _np.linalg.pinv(sampler1_matrix)

    return _np.dot(sampler2_matrix, sampler1_matrix_inv)

def CalculateTaylorMapOrder2(root_file_name, sampler1_name, sampler2_name) :
    """
    **CalculateTaylorMapOrder2** calculate 2nd order Taylor map from a BDSIM output root file and two sampler names

    Example:

    >>> tmatrix = pybdsim.Analysis.CalculateTaylorMapOrder2('output.root', 'd1','e1')

    returns numpy.array 4x12

    +-----------------+---------------------------------------------------------+
    | **Parameters**  | **Description**                                         |
    +-----------------+---------------------------------------------------------+
    | root_file_name  | Input root file name (raw output)                       |
    +-----------------+---------------------------------------------------------+
    | sampler1_name   | First sampler name to take coordinates for calculation  |
    +-----------------+---------------------------------------------------------+
    | sampler2_name   | Second sampler name to take coordinates for calculation |
    +-----------------+---------------------------------------------------------+
    """

    root_file = _Data.Load(root_file_name)
    sampler1_data = _Data.SamplerData(root_file, sampler1_name)
    sampler2_data = _Data.SamplerData(root_file, sampler2_name)

    sampler1_matrix = _np.array([sampler1_data.data['x'],
                                 sampler1_data.data['xp'],
                                 sampler1_data.data['x'] * sampler1_data.data['x'],
                                 sampler1_data.data['x'] * sampler1_data.data['xp'],
                                 sampler1_data.data['x'] * sampler1_data.data['y'],
                                 sampler1_data.data['x'] * sampler1_data.data['yp'],
                                 sampler1_data.data['y'],
                                 sampler1_data.data['yp'],
                                 sampler1_data.data['y'] * sampler1_data.data['xp'],
                                 sampler1_data.data['y'] * sampler1_data.data['y'],
                                 sampler1_data.data['y'] * sampler1_data.data['yp'],
                                 sampler1_data.data['xp'] * sampler1_data.data['xp'],
                                 sampler1_data.data['yp'] * sampler1_data.data['yp']])

    sampler2_matrix = _np.array([sampler2_data.data['x'],
                                 sampler2_data.data['xp'],
                                 sampler2_data.data['y'],
                                 sampler2_data.data['yp']])

    sampler1_matrix_inv = _np.linalg.pinv(sampler1_matrix)

    return _np.dot(sampler2_matrix, sampler1_matrix_inv)

def CalculateEnergyGain(root_file_name, sampler1_name, sampler2_name) :
    """
    **CalculateEnergyGain** calculate energy gain from a BDSIM output root file and two sampler names

    Example:

    >>> rmatrix = pybdsim.Analysis.CalculateEneryGain('output.root', 'd1','e1')

    returns float

    +-----------------+---------------------------------------------------------+
    | **Parameters**  | **Description**                                         |
    +-----------------+---------------------------------------------------------+
    | root_file_name  | Input root file name (raw output)                       |
    +-----------------+---------------------------------------------------------+
    | sampler1_name   | First sampler name to take coordinates for calculation  |
    +-----------------+---------------------------------------------------------+
    | sampler2_name   | Second sampler name to take coordinates for calculation |
    +-----------------+---------------------------------------------------------+
    """

    root_file = _Data.Load(root_file_name)
    sampler1_data = _Data.SamplerData(root_file, sampler1_name)
    sampler2_data = _Data.SamplerData(root_file, sampler2_name)

    if sampler1_data.data['n'][0] == sampler2_data.data['n'][0] :
        deltaE = sampler2_data.data['energy'] - sampler1_data.data['energy']
    else :
        deltaE = _np.array([0.0])

    return deltaE.mean()

def CompareRMatrix(rmatrix1, rmatrix2) :
    # difference matrix
    dmatrix = rmatrix2 - rmatrix1



def PlotRMatrix(rmatrix1) :
    pass

