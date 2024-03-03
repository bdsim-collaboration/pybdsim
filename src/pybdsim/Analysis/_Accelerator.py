import numpy as _np
import scipy.special as _special
import scipy.constants as _constants
import vtk as _vtk


def DriftTransverseMatrix(l) :
    '''
    Calculates drift transverse matrix.

    Example:

    >>> d = DriftTransverseMatrix(2)
        array([[1, 2],
               [0, 1]])

    +-----------------+---------------------------------------------------------+
    | **Parameters**  | **Description**                                         |
    +-----------------+---------------------------------------------------------+
    | l               | Longitudinal length of drift                            |
    +-----------------+---------------------------------------------------------+
    '''

    return _np.array([[1,l],[0,1]])

def QuadrupoleThickTransverseMatrix(l,k1 = None, k1l = None) :
    '''
    Calculates thick quadrupole transverse matrix.

    Example:

    >>> d = QuadrupoleThickTransverseMatrix(0.25, k1 = 2)

    +-----------------+---------------------------------------------------------+
    | **Parameters**  | **Description**                                         |
    +-----------------+---------------------------------------------------------+
    | l               | Longitudinal length of drift                            |
    +-----------------+---------------------------------------------------------+
    | k1              | Quadrupole kick strengt                                 |
    +-----------------+---------------------------------------------------------+
    '''

    if l == 0 :
        return QuadrupoleThinTransverseMatrix(k1l)

    if k1 >= 0:
        return _np.array([[_np.cos(_np.sqrt(k1)*l),               _np.sin(_np.sqrt(k1)*l)/_np.sqrt(k1)],
                          [-_np.sqrt(k1)*_np.sin(_np.sqrt(k1)*l), _np.cos(_np.sqrt(k1)*l)             ]])
    else:
        k1 = fabs(k1)
        return _np.array([[_np.cosh(_np.sqrt(k1)*l),               _np.sinh(_np.sqrt(k1)*l)/_np.sqrt(k1)],
                          [-_np.sqrt(k1)*_np.sinh(_np.sqrt(k1)*l), _np.cosh(_np.sqrt(k1)*l)             ]])
def QuadrupoleThinTransverseMatrix(k1l) :
    return _np.array([[1    ,0],
                      [1./k1l,1]])


def plot() :

    nR = 10
    nZ = 10
    nPhi = 10

    sg = _vtk.vtkStructuredGrid()
    points = _vtk.vtkPoints()
    points.Allocate(nR*nZ*nPhi)

    scalars = _vtk.vtkDoubleArray()
    scalars.SetNumberOfComponents(1)
    scalars.SetName("scalar data")

    vectors = _vtk.vtkDoubleArray()
    vectors.SetNumberOfComponents(3)
    vectors.SetName("vector data")


    R = 1
    Z = 5
    phi = 2*_np.pi

    for r in _np.linspace(0, R, nR) :
        for phi in _np.linspace(0, phi, nPhi):
            for z in _np.linspace(0, Z, nZ) :
                x = r*_np.cos(phi)
                y = r*_np.sin(phi)
                points.InsertNextPoint([x,y,z])
                vectors.InsertNextTuple([x/(r+0.01)**2, y/(r+0.01)**2, z/(r+0.01)**2])
                scalars.InsertNextTuple([1/(r+0.01)**2])
    sg.SetPoints(points)
    sg.GetPointData().SetScalars(scalars)
    sg.GetPointData().SetVectors(vectors)

    mapper = _vtk.vtkDataSetMapper()
    mapper.SetInputData(sg)
    actor = _vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetPointSize(1)

    renderer = _vtk.vtkRenderer()
    renderer.SetBackground([1,1,1])
    renderWindow = _vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindow.SetWindowName("VisualizeStructuredGrid")

    renderWindowInteractor = _vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    renderer.AddActor(actor)

    renderWindow.Render()
    renderWindowInteractor.Start()

    return sg

def CylindricalPipeTransverseMagneticField(r,z,phi, t, omega, radius) :
    c = 2.99e8
    Z0 = 377
    lambda_c = 2.61*radius
    wavenumber_c = 2*_np.pi/lambda_c
    wavenumber = omega/c
    wavenumber_z = _np.sqrt(wavenumber**2 - wavenumber_c**2)

    print(lambda_c)
    print(wavenumber_c)
    print(wavenumber)
    print(wavenumber_z)
    oscillator = _np.exp(complex(0,1)*wavenumber_z*z)*_np.exp(complex(0,1)*omega*t)
    Er = complex(0,1)*wavenumber_z/wavenumber_c*_special.j1(wavenumber_c*r)*oscillator
    Ez = _special.j0(wavenumber_c*r)*oscillator
    Bphi = complex(0,1)*wavenumber/Z0/wavenumber_c*_special.j1(wavenumber_c*r)*oscillator

    return [[Er,Ez,0], [0,0,Bphi]]

def TransitTimeFactorFrequency(length, frequency, beta = 1) :
    wavelength = 3e8/frequency
    return TransitTimeFactorWavelength(length, wavelength, beta)

def TransitTimeFactorWavelength(length, wavelength, beta = 1) :
    argument = _np.pi*length/(beta*wavelength)
    return _np.sinc(argument)

def CavityBodyConstantEMatrix(gammaI, gammaF, L) :
    gammaPrime = (gammaF-gammaI)/L

    return _np.array([[1, gammaI/gammaPrime*_np.log(gammaF/gammaI)],[0, gammaI/gammaF]])

def CavityBodyTransverseMatrix(gammaI, gammaF, L, alpha, eta, deltaPhi) :
    '''
    Calculates RF cavity body transverse matrix.

    Example:

    >>> deltaPhi = 0
    >>> gammaI = 1
    >>> gammaF = 3
    >>> eta = CavityBodyEta([1],[0],deltaPhi)
    >>> alpha = CavityBodyAlpha(gammaI,gammaF,eta,deltaPhi)
    >>> m = CavityFringeTransverseMatrix(gammaI, gammaF, alpha, eta, deltaPhi)
        array([[ 0.92550932,  0.53559779],
               [-0.0892663 ,  0.30850311]])

    +-----------------+---------------------------------------------------------+
    | **Parameters**  | **Description**                                         |
    +-----------------+---------------------------------------------------------+
    | gammaI          | Incoming energy (gamma units do not matter)             |
    +-----------------+---------------------------------------------------------+
    | gammaF          | Outgoing energy (or gamma, units do not matter)         |
    +-----------------+---------------------------------------------------------+
    | alpha           | Entrance (True) or exit (False)                         |
    +-----------------+---------------------------------------------------------+
    | eta             | Energy gain (or gamma, units do not matter). If None    |
    +-----------------+---------------------------------------------------------+
    | deltaPhi        | Energy gain (or gamma, units do not matter). If None    |
    +-----------------+---------------------------------------------------------+
    '''

    gammaPrime = (gammaF - gammaI)/L
    return _np.array([[_np.cos(alpha), _np.sqrt(8/eta)*gammaI/gammaPrime*_np.cos(deltaPhi)*_np.sin(alpha)],
                      [-_np.sqrt(eta/8)*gammaPrime/(gammaF*_np.cos(deltaPhi))*_np.sin(alpha), gammaI/gammaF*_np.cos(alpha)]])

def CavityFringeTransverseMatrix(gammaI, gammaF, L = 1, inward = True, gammaPrime = None) :
    '''
    Calculates RF cavity fringe transverse matrix.

    Example:

    >>> cf = CavityFringeTransverseMatrix(1,2 inward = True)
        array([[1.   , 0.   ],
               [0.375, 1.   ]])

    +-----------------+---------------------------------------------------------+
    | **Parameters**  | **Description**                                         |
    +-----------------+---------------------------------------------------------+
    | gammaI          | Incoming energy (gamma units do not matter)             |
    +-----------------+---------------------------------------------------------+
    | gammaF          | Outgoing energy (or gamma, units do not matter)         |
    +-----------------+---------------------------------------------------------+
    | inward          | Entrance (True) or exit (False)                         |
    +-----------------+---------------------------------------------------------+
    | gammaPrime      | Energy gain (or gamma, units do not matter). If None    |
    |                 | it is calculated from gammaF - gammaI                   |
    +-----------------+---------------------------------------------------------+
    '''

    if not gammaPrime and L != 0:
        gammaPrime = (gammaF - gammaI)/L

    if inward:
        gammaPrime = -gammaPrime
        gamma = gammaI
    else:
        gamma = gammaF

    return _np.array([[1,                   0],
                      [gammaPrime/(2*gamma),1]])

def CavityGammaPrime(E0, deltaPhi, q = 1, m0 = 0.511) :
    '''
    Calculates RF cavity energy gain (inits are energy MeV, momentum MeV/c, mass MeV/c**2)

    gammaPrime = q*E0*cos(deltaPhi)/m

    +-----------------+---------------------------------------------------------+
    | **Parameters**  | **Description**                                         |
    +-----------------+---------------------------------------------------------+
    | E0              | Peak field (MV)                                         |
    +-----------------+---------------------------------------------------------+
    | deltaPhi        | Phase difference compared to crest phase                |
    +-----------------+---------------------------------------------------------+
    | charge          | Particle charge in units of e                           |
    +-----------------+---------------------------------------------------------+
    | m0              | Rest mass (MeV/c^2)                                     |
    +-----------------+---------------------------------------------------------+
    '''

    return q*E0*_np.cos(deltaPhi)/m0

def CavityBodyEta(bn, bmn, deltaPhi) :
    bn = _np.array(bn)
    bmn = _np.array(bmn)
    return (bn**2 + bmn**2 + 2*bn*bmn*_np.cos(2*deltaPhi)).sum()

def CavityBodyAlpha(gammaI, gammaF, eta, deltaPhi) :
    return _np.sqrt(eta/8.0)/_np.cos(deltaPhi)*_np.log(gammaF/gammaI)