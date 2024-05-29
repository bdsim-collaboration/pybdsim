from scipy.special import jn_zeros as _jn_zeros
from scipy.special import jnp_zeros as _jnp_zeros
from scipy.special import jn as _jn
from scipy.special import jvp as _jvp
from scipy.constants import speed_of_light as _c
from numpy import pi as _pi
from numpy import sqrt as _sqrt
from numpy import linspace as _linspace
from numpy import meshgrid as _meshgrid
from numpy import cos as _cos
from numpy import sin as _sin
from numpy import arctan2 as _arctan2
from numpy import array as _array
from numpy import reshape as _reshape
from numpy import tensordot as _tensordot
from numpy import logical_and as _logical_and
from numpy import trapz as _trapz

def TM_cylindrical(r, t, z, radius, length, m, n, p, E0=1, opt=""):

    if opt == "cart":
        x = r
        y = t

        r = _sqrt(x**2+y**2)
        t = _arctan2(y,x)


    if type(r) is not _array :
        r = _array(r)
    if type(t) is not _array:
        t = _array(t)
    if type(z) is not _array:
        z = _array(z)

    kmn = _jn_zeros(m,n)[n-1]/radius
    kz  = p *_pi / length

    omega = _sqrt(_c**2 * (kmn**2 + kz**2))
    freq = omega/2/_pi
    wavelength = _c/freq

    cavityshape = 1.0*(_logical_and(r < radius,z<length))

    # divergence if r=0
    r[r == 0.0] = 1e-9

    Ez = cavityshape * E0 * _jn(m, kmn * r) * _cos(m * t) * _cos(p * _pi * z / length)
    Er = - cavityshape * p * _pi / length * radius / _jn_zeros(m, n)[n - 1] * E0 * _jvp(m, kmn * r) * _cos(m * t) * _sin(p * _pi * z / length)
    Et = - cavityshape * p * _pi / length * m * radius ** 2 / _jn_zeros(m, n)[n-1] ** 2 / r * E0 * _jn(m,kmn * r) * _sin(m * t) * _sin(p * _pi * z / length)
    Ex = Er * _cos(t) - Et * _sin(t)
    Ey = Er * _sin(t) + Et * _cos(t)

    Bz = cavityshape * 0 * r
    Br = cavityshape * omega * m * radius ** 2 / _jn_zeros(m, n)[n-1] ** 2 / r / _c ** 2 * E0 * _jn(m,kmn * r) * _sin(m * t) * _cos(p * _pi * z / length)
    Bt = cavityshape * omega * radius / _jn_zeros(m, n)[n-1] / _c ** 2 * E0 * _jvp(m, kmn * r) * _cos(m * t) * _cos(p * _pi * z / length)

    Bx = Br * _cos(t) - Bt * _sin(t)
    By = Br * _sin(t) + Bt * _cos(t)

    E = _sqrt(Ex**2+Ey**2+Ez**2)
    B = _sqrt(Bx**2+By**2+Bz**2)

    return {"kmn":kmn, "kz":kz,"omega":omega, "freq":freq, "wavelength":wavelength,
            "Ex":Ex, "Ey":Ey, "Ez":Ez, "Er":Er, "Et":Et,"E":E,
            "Bx":Bx, "By":By, "Bz":Bz, "Br":Er, "Bt":Bt,"B":B}
def TE_cylindrical(r, t, z, radius, length, m, n, p, B0=1, opt=""):

    if opt == "cart":
        x = r
        y = t

        r = _sqrt(x**2+y**2)
        t = _arctan2(y,x)

    if type(r) is not _array :
        r = _array(r)
    if type(t) is not _array:
        t = _array(t)
    if type(z) is not _array:
        z = _array(z)

    kmn = _jnp_zeros(m, n)[n - 1] / radius
    kz = p * _pi / length

    omega = _sqrt(_c ** 2 * (kmn ** 2 + kz ** 2))
    freq = omega / 2 / _pi
    wavelength = _c/freq

    cavityshape = 1.0*(_logical_and(r < radius,z<length))

    # divergence if r=0
    r[r == 0.0] = 1e-9

    Ez = cavityshape * 0
    Er = cavityshape * omega * m * radius ** 2 / _jnp_zeros(m, n)[n - 1] / r * B0 * _jn(m, kmn * r) * _sin(m * t) * _sin(p * _pi * z / length)
    Et = cavityshape * omega * radius / _jnp_zeros(m, n)[n - 1] * B0 * _jvp(m, kmn * r) * _cos(m * t) * _sin(p * _pi * z / length)

    Ex = Er * _cos(t) - Et * _sin(t)
    Ey = Er * _sin(t) + Et * _cos(t)

    Bz = cavityshape * B0 * _jn(m, kmn * r) * _cos(m * t) * _sin(p * _pi * z / length)
    Br = cavityshape * p * _pi / length * radius / _jnp_zeros(m, n)[n - 1] * B0 * _jvp(m, kmn * r) * _cos(m * t) * _cos(p * _pi * z / length)
    Bt = - cavityshape * p * _pi / length * m * radius ** 2 / _jnp_zeros(m, n)[n - 1] ** 2 / radius * B0 * _jn(m,kmn * r) * _sin(m * t) * _cos(p * _pi * z / length)

    Bx = Br * _cos(t) - Bt * _sin(t)
    By = Br * _sin(t) + Bt * _cos(t)

    E = _sqrt(Ex**2+Ey**2+Ez**2)
    B = _sqrt(Bx**2+By**2+Bz**2)

    return {"kmn": kmn, "kz": kz, "omega": omega, "freq": freq, "wavelength":wavelength,
            "Ex": Ex, "Ey": Ey, "Ez": Ez, "Er": Er, "Et": Et, "E":E,
            "Bx": Bx, "By": By, "Bz": Bz, "Br": Er, "Bt": Bt, "B":B}

def Cylindrical_cartesianmesh(radius, length, modeType, m,n,p, nx=20, ny=20, nz=20, safety=0.01, field0=1) :

    lowx = -radius - safety
    lowy = -radius - safety
    lowz =  0
    highx = radius + safety
    highy = radius + safety
    highz = length

    dx = (highx - lowx)/nx
    dy = (highy - lowy)/ny
    dz = (highz - lowz)/nz

    ox = lowx
    oy = lowy
    oz = lowz

    xspace = _linspace(lowx,highx,nx)
    yspace = _linspace(lowy,highy,ny)
    zspace = _linspace(lowz,highz,nz)

    xmesh, ymesh = _meshgrid(xspace, yspace)
    rmesh = _sqrt(xmesh**2 + ymesh**2)
    tmesh = _arctan2(ymesh, xmesh)

    cavityshape = 1.0*(_sqrt(xmesh**2 + ymesh**2) < radius)

    EzArray = []
    ErArray = []
    EtArray = []
    ExArray = []
    EyArray = []

    BzArray = []
    BrArray = []
    BtArray = []
    BxArray = []
    ByArray = []

    for z in zspace  :
        if modeType == "TM" :
            r = TM_cylindrical(rmesh,tmesh,z,radius,length,m,n,p,field0)
        else :
            r = TE_cylindrical(rmesh,tmesh,z,radius,length,m,n,p,field0)

        EzArray.append(r['Ez'])
        ErArray.append(r['Er'])
        EtArray.append(r['Et'])
        ExArray.append(r['Ex'])
        EyArray.append(r['Ey'])

        BzArray.append(r['Bz'])
        BrArray.append(r['Br'])
        BtArray.append(r['Bt'])
        BxArray.append(r['Bx'])
        ByArray.append(r['By'])

    print(r['kmn'],r['kz'],r['omega'], r['freq'])

    ExArray = _array(ExArray)
    EyArray = _array(EyArray)
    EzArray = _array(EzArray)
    ErArray = _array(ErArray)
    EtArray = _array(EtArray)

    BxArray = _array(BxArray)
    ByArray = _array(ByArray)
    BzArray = _array(BzArray)
    BrArray = _array(BrArray)
    BtArray = _array(BtArray)

    B = _array([BxArray,ByArray,BzArray])
    E = _array([ExArray,EyArray,EzArray])

    return {"type":"3dcart","kmn":r['kmn'], "kz":r['kz'], "omega":r['omega'], "freq":r['freq'],
            "nx":nx, "ny":ny, "nz":nz,
            "dx":dx, "dy":dy, "dz":dz,
            "ox":ox, "oy":oy, "oz":oz,
            "spacing":(dx,dy,dz),
            "dimensions":(nx,ny,nz),
            "origin":(ox,oy,oz),
            "Ez":EzArray.T, "Er":ErArray.T, "Et":EtArray.T,
            "Bz":BzArray.T, "Br":BrArray.T, "Bt":BtArray.T,
            "Ex":ExArray.T, "Ey":EyArray.T,
            "Bx":BxArray.T, "By":ByArray.T,
            "B":B.T, "E":E.T}

def Cylindrical_line(radius, length, modeType, m,n,p, nx=20, ny=20, nz=20, safety=0.01, field0=1,
                     p0=[0,0,0], dl=[0,0,1], nlambda=50, linelength=0.1):
    p0 = _array(p0)
    dl = _array(dl)

    hl = linelength

    hmesh = _linspace(0, hl, nlambda)

    v = p0 + _tensordot(hmesh,dl,0)

    z = v[:,2]
    t = _arctan2(v[:,1],v[:,0])
    r = _sqrt(v[:,0]**2+v[:,1]**2)

    if modeType == "TM" :
        fd = TM_cylindrical(r,t,z,radius,length,m,n,p,field0)
    elif modeType == "TE" :
        fd = TE_cylindrical(r,t,z,radius,length,m,n,p,field0)

    fd['type'] = '1d'
    fd['x'] = v[:,0]
    fd['y'] = v[:,1]
    fd['z'] = v[:,2]-length/2.0 # probably better to centre around z=0

    fd['r'] = r
    fd['t'] = t

    return fd

def MatplotlibPlotField(fieldDataDict):

    import matplotlib.pyplot as plt

    Bmax = max(Bz.max(), Br.max(), Bt.max())
    _plt.subplot(6, 6, iplt)
    if plotField == "Ez":
        plt.imshow(Ez)
        plt.clim(-E0, E0)
    elif plotField == "Er":
        plt.imshow(Er)
        plt.clim(-E0, E0)
    elif plotField == "Et":
        plt.imshow(Et)
        plt.clim(-E0, E0)
    elif plotField == "Ex":
        plt.imshow(Ex)
        plt.clim(-E0, E0)
    elif plotField == "Ey":
        plt.imshow(Ey)
        plt.clim(-E0, E0)
    elif plotField == "Bz":
        plt.imshow(Bz)
        plt.clim(-Bmax, Bmax)
    elif plotField == "Br":
        plt.imshow(Br)
        plt.clim(-Bmax, Bmax)
    elif plotField == "Bt":
        plt.imshow(Bt)
        plt.clim(-Bmax, Bmax)
    elif plotField == "Bx":
        plt.imshow(Bx)
        plt.clim(-Bmax, Bmax)
    elif plotField == "Bx":
        plt.imshow(By)
        plt.clim(-Bmax, Bmax)
    _plt.colorbar()

def PyVistaPlotField(fieldDataDict) :
    import pyvista as pv

    grid = pv.ImageData(
        dimensions=fieldDataDict['dimensions'],
        spacing=fieldDataDict['spacing'],
        origin=fieldDataDict['origin'],
    )

    grid['E'] = _reshape(fieldDataDict['E'], (len(grid.points),3),"F")
    grid['B'] = _reshape(fieldDataDict['B'], (len(grid.points),3),"F")

    # Compute the field lines
    #seed = pv.Disc(inner=0.0, outer=0.05, r_res=10, c_res=10)
    #strl = grid.streamlines_from_source(seed,
    #                                    vectors="E",
    #                                    max_step_length=0.001,
    #                                    max_time=200,
    #                                    integration_direction="both")

    EFieldLines, src = grid.streamlines(
        'E',
        return_source=True,
        max_time=100.0,
        initial_step_length=0.02,
        terminal_speed=0,
        n_points=1000,
        source_radius=0.1,
        source_center=(0, 0, 0))

    BFieldLines, src = grid.streamlines(
        'B',
        return_source=True,
        max_time=100.0,
        initial_step_length=0.02,
        terminal_speed=0,
        n_points=1000,
        source_radius=0.1,
        source_center=(0, 0, 0))

    pl = pv.Plotter()

    Eglyphs = grid.glyph(orient="E", factor=grid.x.max()/grid.get_array("E").max()/10)
    pl.add_mesh(Eglyphs, show_scalar_bar=True, lighting=False, color="red")
    Bglyphs = grid.glyph(orient="B", factor=grid.x.max()/grid.get_array("B").max()/10)
    pl.add_mesh(Bglyphs, show_scalar_bar=True, lighting=False, color="blue")
    #pl.add_mesh(EFieldLines, color="red")
    #pl.add_mesh(BFieldLines, color="blue")
    pl.camera.position = (0.3, 0.3, 0.3)
    pl.show()

    return grid

def MatplotlibPlotField_1d(fd) :
    pass
def V0(fd) :
    if fd['type'] == "1d" :
        z = fd['z']
        E = fd['Ez']
        return _trapz(E,z)

def TransitTime(fd):
    if fd['type'] == "1d" :
        z = fd['z']
        E = fd['Ez']

        t = z/_c
        return _trapz(E*_cos(fd['omega']*t),z)/V0(fd)

def TransitTime_TM010(gap, beta, frequency) :
    wavelength = _c/frequency
    return _sin(_pi*gap/(beta*wavelength))/(_pi*gap)*beta*wavelength

def TM_cylindical_old(radius, length, m,n,p, nx=20, ny=20, nz=20, safety=0.01, E0=1) :
    kmn = _jn_zeros(m,n)[n-1]/radius
    kz  = p *_pi / length

    omega = _sqrt(_c**2 * (kmn**2 + kz**2))
    freq = omega/2/_pi

    lowx = -radius - safety
    lowy = -radius - safety
    lowz =  0
    highx = radius + safety
    highy = radius + safety
    highz = length

    dx = (highx - lowx)/nx
    dy = (highy - lowy)/ny
    dz = (highz - lowz)/nz

    ox = lowx
    oy = lowy
    oz = lowz

    xspace = _linspace(lowx,highx,nx)
    yspace = _linspace(lowy,highy,ny)
    zspace = _linspace(lowz,highz,nz)

    xmesh, ymesh = _meshgrid(xspace, yspace)
    rmesh = _sqrt(xmesh**2 + ymesh**2)
    tmesh = _arctan2(ymesh, xmesh)

    cavityshape = 1.0*(_sqrt(xmesh**2 + ymesh**2) < radius)

    EzArray = []
    ErArray = []
    EtArray = []
    ExArray = []
    EyArray = []

    BzArray = []
    BrArray = []
    BtArray = []
    BxArray = []
    ByArray = []

    for z in zspace  :
        Ez = cavityshape * E0*_jn(m,kmn*rmesh) * _cos(m*tmesh) *_cos(p * _pi * z/length)
        Er = - cavityshape * p * _pi/length * radius/_jn_zeros(m,n)[n-1] * E0 *_jvp(m,kmn*rmesh) * _cos(m*tmesh) * _sin(p * _pi * z/length)
        Et = - cavityshape * p * _pi/length * m * radius**2/_jn_zeros(m,n)**2/rmesh * E0 * _jn(m,kmn*rmesh)*_sin(m*tmesh) * _sin(p * _pi * z/length)

        Ex = Er*_cos(tmesh) - Et*_sin(tmesh)
        Ey = Er*_sin(tmesh) + Et*_cos(tmesh)

        Bz = cavityshape * 0*rmesh
        Br = cavityshape * omega* m*radius**2/_jn_zeros(m,n)**2/rmesh/_c**2 * E0 *_jn(m,kmn*rmesh) * _sin(m * tmesh) * _cos(p * _pi * z/length)
        Bt = cavityshape * omega* radius/_jn_zeros(m,n)/_c**2 * E0 * _jvp(m, kmn*rmesh) * _cos(m * tmesh) * _cos(p * _pi * z/length)

        Bx = Br*_cos(tmesh) - Bt*_sin(tmesh)
        By = Br*_sin(tmesh) + Bt*_cos(tmesh)

        EzArray.append(Ez)
        ErArray.append(Er)
        EtArray.append(Et)
        ExArray.append(Ex)
        EyArray.append(Ey)

        BzArray.append(Bz)
        BrArray.append(Br)
        BtArray.append(Bt)
        BxArray.append(Bx)
        ByArray.append(By)

    print(kmn, kz, omega, freq)

    ExArray = _array(ExArray)
    EyArray = _array(EyArray)
    EzArray = _array(EzArray)
    ErArray = _array(ErArray)
    EtArray = _array(EtArray)

    BxArray = _array(BxArray)
    ByArray = _array(ByArray)
    BzArray = _array(BzArray)
    BrArray = _array(BrArray)
    BtArray = _array(BtArray)

    B = _array([BxArray,ByArray,BzArray])
    E = _array([ExArray,EyArray,EzArray])

    print(E.max(), B.max())

    return {"kmn":kmn, "kz":kz, "omega":omega, "freq":freq,
            "nx":nx, "ny":ny, "nz":nz,
            "dx":dx, "dy":dy, "dz":dz,
            "ox":ox, "oy":oy, "oz":oz,
            "spacing":(dx,dy,dz),
            "dimensions":(nx,ny,nz),
            "origin":(ox,oy,oz),
            "Ez":EzArray.T, "Er":ErArray.T, "Et":EtArray.T,
            "Bz":BzArray.T, "Br":BrArray.T, "Bt":BtArray.T,
            "Ex":ExArray.T, "Ey":EyArray.T,
            "Bx":BxArray.T, "By":ByArray.T,
            "B":B.T, "E":E.T}
def TE_cylindical_old(radius, length, m,n,p, nx=20, ny=20, nz=20, safety=0.01, B0=1.0) :
    kmn = _jnp_zeros(m,n)[n-1]/radius
    kz  = p *_pi / length

    omega = _sqrt(_c**2 * (kmn**2 + kz**2))
    freq = omega/2/_pi

    lowx = -radius - safety
    lowy = -radius - safety
    lowz =  0
    highx = radius + safety
    highy = radius + safety
    highz = length

    dx = (highx - lowx)/nx
    dy = (highy - lowy)/ny
    dz = (highz - lowz)/nz

    ox = lowx
    oy = lowy
    oz = lowz

    xspace = _linspace(lowx,highx,nx)
    yspace = _linspace(lowy,highy,ny)
    zspace = _linspace(lowz,highz,nz)

    xmesh, ymesh = _meshgrid(xspace, yspace)
    rmesh = _sqrt(xmesh**2 + ymesh**2)
    tmesh = _arctan2(ymesh, xmesh)

    cavityshape = 1.0*(_sqrt(xmesh**2 + ymesh**2) < radius)

    EzArray = []
    ErArray = []
    EtArray = []
    ExArray = []
    EyArray = []

    BzArray = []
    BrArray = []
    BtArray = []
    BxArray = []
    ByArray = []

    for z in zspace  :
        Ez = cavityshape * 0
        Er = cavityshape * omega * m*radius**2/_jnp_zeros(m,n)[n-1]/rmesh * B0 * _jn(m,kmn*rmesh) * _sin(m*tmesh) * _sin(p*_pi*z/length)
        Et = cavityshape * omega * radius/_jnp_zeros(m,n)[n-1] * B0 * _jvp(m, kmn*rmesh) * _cos(m*tmesh) * _sin(p*_pi*z/length)

        Ex = Er*_cos(tmesh) - Et*_sin(tmesh)
        Ey = Er*_sin(tmesh) + Et*_cos(tmesh)

        Bz = cavityshape *B0*_jn(m, kmn*rmesh) * _cos(m*tmesh) * _sin(p*_pi*z/length)
        Br = cavityshape *p*_pi/length * radius/_jnp_zeros(m,n)[n-1] * B0 * _jvp(m,kmn*rmesh) * _cos(m*tmesh) * _cos(p*_pi*z/length)
        Bt = - cavityshape * p*_pi/length * m*radius**2/_jnp_zeros(m,n)[n-1]**2/radius * B0 * _jn(m, kmn*rmesh) * _sin(m*tmesh) * _cos(p*_pi*z/length)

        Bx = Br*_cos(tmesh) - Bt*_sin(tmesh)
        By = Br*_sin(tmesh) + Bt*_cos(tmesh)

        EzArray.append(Ez)
        ErArray.append(Er)
        EtArray.append(Et)
        ExArray.append(Ex)
        EyArray.append(Ey)

        BzArray.append(Bz)
        BrArray.append(Br)
        BtArray.append(Bt)
        BxArray.append(Bx)
        ByArray.append(By)

    print(kmn, kz, omega, freq)

    ExArray = _array(ExArray)
    EyArray = _array(EyArray)
    EzArray = _array(EzArray)
    ErArray = _array(ErArray)
    EtArray = _array(EtArray)

    BxArray = _array(BxArray)
    ByArray = _array(ByArray)
    BzArray = _array(BzArray)
    BrArray = _array(BrArray)
    BtArray = _array(BtArray)

    B = _array([BxArray,ByArray,BzArray])
    E = _array([ExArray,EyArray,EzArray])

    print(E.max(), B.max())

    return {"kmn":kmn, "kz":kz, "omega":omega, "freq":freq,
            "nx":nx, "ny":ny, "nz":nz,
            "dx":dx, "dy":dy, "dz":dz,
            "ox":ox, "oy":oy, "oz":oz,
            "spacing":(dx,dy,dz),
            "dimensions":(nx,ny,nz),
            "origin":(ox,oy,oz),
            "Ez":EzArray.T, "Er":ErArray.T, "Et":EtArray.T,
            "Bz":BzArray.T, "Br":BrArray.T, "Bt":BtArray.T,
            "Ex":ExArray.T, "Ey":EyArray.T,
            "Bx":BxArray.T, "By":ByArray.T,
            "B":B.T, "E":E.T}