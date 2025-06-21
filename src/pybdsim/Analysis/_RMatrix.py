import pybdsim.Data as _Data
import numpy as _np
import matplotlib.pyplot as _plt

def CalculateRMatrix(root_file_name, sampler1_name, sampler2_name, size=4, average = False):
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
    | average (bool)  | True : Compute average T and E for subtraction          |
    |                 | False : Use first particle for  T and E for subtraction |
    +-----------------+---------------------------------------------------------+
    """

    root_file = _Data.Load(root_file_name)
    sampler1_data = _Data.SamplerData(root_file, sampler1_name)
    sampler2_data = _Data.SamplerData(root_file, sampler2_name)

    sampler1_x  = sampler1_data.data['x']
    sampler1_xp = sampler1_data.data['xp']
    sampler1_y  = sampler1_data.data['y']
    sampler1_yp = sampler1_data.data['yp']

    sampler2_x  = sampler2_data.data['x']
    sampler2_xp = sampler2_data.data['xp']
    sampler2_y  = sampler2_data.data['y']
    sampler2_yp = sampler2_data.data['yp']

    sampler1_time = sampler1_data.data['T']
    sampler2_time = sampler2_data.data['T']
    sampler1_energy = sampler1_data.data['energy']
    sampler2_energy = sampler2_data.data['energy']

    if average :
        sampler1_x  = sampler1_x - sampler1_x.mean()
        sampler1_xp = sampler1_xp - sampler1_xp.mean()
        sampler1_y  = sampler1_y - sampler1_y.mean()
        sampler1_yp = sampler1_yp - sampler1_yp.mean()

        sampler2_x  = sampler2_x - sampler2_x.mean()
        sampler2_xp = sampler2_xp - sampler2_xp.mean()
        sampler2_y  = sampler2_y - sampler2_y.mean()
        sampler2_yp = sampler2_yp - sampler2_yp.mean()

        sampler1_time = sampler1_time - sampler1_time.mean()
        sampler2_time = sampler2_time - sampler2_time.mean()
        sampler1_energy = sampler1_energy - sampler1_energy.mean()
        sampler2_energy = sampler2_energy - sampler2_energy.mean()

    if size == 6:
        sampler1_matrix = _np.array([sampler1_x,
                                     sampler1_xp,
                                     sampler1_y,
                                     sampler1_yp,
                                     sampler1_time,
                                     sampler1_energy])

        sampler2_matrix = _np.array([sampler2_x,
                                     sampler2_xp,
                                     sampler2_y,
                                     sampler2_yp,
                                     sampler2_time,
                                     sampler2_energy])

    else:
        sampler1_matrix = _np.array([sampler1_x,sampler1_xp,sampler1_y,sampler1_yp])
        sampler2_matrix = _np.array([sampler2_x,sampler2_xp,sampler2_y,sampler2_yp])

    sampler1_matrix_inv = _np.linalg.pinv(sampler1_matrix)

    return _np.dot(sampler2_matrix, sampler1_matrix_inv)

def CalculateTaylorMapOrder2(root_file_name, sampler1_name, sampler2_name, average=True) :
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

    sampler1_x  = sampler1_data.data['x']
    sampler1_xp = sampler1_data.data['xp']
    sampler1_y  = sampler1_data.data['y']
    sampler1_yp = sampler1_data.data['yp']

    sampler2_x  = sampler2_data.data['x']
    sampler2_xp = sampler2_data.data['xp']
    sampler2_y  = sampler2_data.data['y']
    sampler2_yp = sampler2_data.data['yp']

    sampler1_time = sampler1_data.data['T']
    sampler2_time = sampler2_data.data['T']
    sampler1_energy = sampler1_data.data['energy']
    sampler2_energy = sampler2_data.data['energy']

    if average :
        sampler1_x  = sampler1_x - sampler1_x.mean()
        sampler1_xp = sampler1_xp - sampler1_xp.mean()
        sampler1_y  = sampler1_y - sampler1_y.mean()
        sampler1_yp = sampler1_yp - sampler1_yp.mean()

        sampler2_x  = sampler2_x - sampler2_x.mean()
        sampler2_xp = sampler2_xp - sampler2_xp.mean()
        sampler2_y  = sampler2_y - sampler2_y.mean()
        sampler2_yp = sampler2_yp - sampler2_yp.mean()

        sampler1_time = sampler1_time - sampler1_time.mean()
        sampler2_time = sampler2_time - sampler2_time.mean()
        sampler1_energy = sampler1_energy - sampler1_energy.mean()
        sampler2_energy = sampler2_energy - sampler2_energy.mean()

    sampler1_matrix = _np.array([sampler1_x,
                                 sampler1_xp,
                                 sampler1_y,
                                 sampler1_yp,
                                 sampler1_x * sampler1_x,
                                 sampler1_x * sampler1_xp,
                                 sampler1_x * sampler1_y,
                                 sampler1_x * sampler1_yp,
                                 sampler1_y * sampler1_xp,
                                 sampler1_y * sampler1_y,
                                 sampler1_y * sampler1_yp,
                                 sampler1_xp * sampler1_xp,
                                 sampler1_yp * sampler1_yp])

    sampler2_matrix = _np.array([sampler2_x,
                                 sampler2_xp,
                                 sampler2_y,
                                 sampler2_yp])

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

def CompareRMatrix(rmatrix1, rmatrix2, toll = 1e-4, user_print = True):
    """
    **CompareRMatrix** compare two rmatrices. If all elements differences are less than toll

    Example:

    >>> m1 = numpy.array([[1,2],[3,4]])
    >>> m2 = numpy.array([[1,2],[3,4]])
    >>> rmatrix = pybdsim.Analysis.CompareRMatrix(m1,m2)

    returns boolean

    +-----------------+---------------------------------------------------------+
    | **Parameters**  | **Description**                                         |
    +-----------------+---------------------------------------------------------+
    | rmatrix1        | First numpy matrix                                      |
    +-----------------+---------------------------------------------------------+
    | rmatrix2        | Second numpy matrix                                     |
    +-----------------+---------------------------------------------------------+
    | toll            | Tollerence                                              |
    +-----------------+---------------------------------------------------------+
    | user_print      | Some print out for user                                 |
    +-----------------+---------------------------------------------------------+
    """

    # difference matrix
    dmatrix = rmatrix2 - rmatrix1

    bmatrix = abs(dmatrix) > toll

    if bmatrix.any() :
        print(dmatrix/toll)
        print(bmatrix*1)

    return not bmatrix.any()

def PlotRMatrix(rmatrix):
    _plt.imshow(rmatrix)
    _plt.colorbar()
