import numpy as _np
import xtrack as _xt
import ocelot as _ocl


convert_name_dict = {'beta_x': 'betx', 'beta_y': 'bety',
                     'alpha_x': 'alfx', 'alpha_y': 'alfy',
                     'Dx': 'dx', 'Dy': 'dy',
                     'Dxp': 'dpx', 'Dyp': 'dpy',
                     'mux': 'mux', 'muy': 'muy'}


def _getCellAndTws0FromList(ocelotlist):
    """ Combine the cells from a list of ocelot environements """
    tws0 = ocelotlist[0].tws0
    cell = ()
    for ocelot in ocelotlist:
        cell += ocelot.cell
    return cell, tws0


def _getOutuptSurveyPoint(ocelotlist, s0=0, x0=0, y0=0, z0=0, ang_x=0, ang_y=0):
    """ Compute the position and angle at the end of a line. """
    if isinstance(ocelotlist, list):
        cell, tws0 = _getCellAndTws0FromList(ocelotlist)
    else:
        cell = ocelotlist.cell
        tws0 = ocelotlist.tws0
    lat = _ocl.MagneticLattice(cell)
    tws = _ocl.twiss(lat, tws0)
    surv = lat.survey(x0=x0, y0=y0, z0=z0, ang_x=ang_x, ang_y=ang_y)
    surv0_xsuite = {'X0': surv[0][-1], 'Y0': surv[1][-1], 'Z0': surv[2][-1],
                    'theta0': surv[3][-1], 'phi0': surv[4][-1], 'psi0': 0}
    return surv0_xsuite, tws[-1].s + s0


def Ocelot2Xsuite(ocelot, line_name='line_from_ocelot', s0=0, x0=0, y0=0, z0=0, ang_x=0, ang_y=0, previousLineList=None):
    """ Convert Ocelot lattice to Xsuite environment.

        +------------------+---------------------------------------------------------+
        | **Parameters**   | **Description**                                         |
        +------------------+---------------------------------------------------------+
        | ocelot           | Ocelot environement imported from a script.             |
        +------------------+---------------------------------------------------------+
        | line_name        | Name that will be used for the created Xsuite line.     |
        |                  | By default it is 'line_from_ocelot'.                    |
        +------------------+---------------------------------------------------------+
        | s0               | Initial curvilinear position. Default is 0.             |
        +------------------+---------------------------------------------------------+
        | x0, y0, z0       | Initial position for the lattice. Defaults are 0.       |
        +------------------+---------------------------------------------------------+
        | ang_x, ang_y     | Initial angle for the lattice. Defaults are 0.          |
        +------------------+---------------------------------------------------------+
        | previousLineList | List of ocelot environements forming a lattice          |
        |                  | upstream of the converted one. It is used to calculate  |
        |                  | the initial position and angle. If provided, s0, x0,    |
        |                  | y0, z0, ang_x, ang_y, define the initial position and   |
        |                  | angle of this previous lattice.                         |
        +------------------+---------------------------------------------------------+
    """

    lattice = _ocl.MagneticLattice(ocelot.cell)
    tws0_ocelot = ocelot.tws0

    env = _xt.Environment()
    env.particle_ref = _xt.Particles(p0c=tws0_ocelot.E, q0=-1, mass0=_xt.ELECTRON_MASS_EV)

    linelist = []
    for elem in lattice.sequence:
        linelist.append(elem.id)

        if elem.id not in env.elements:
            match type(elem):
                case _ocl.Marker:
                    env.new(elem.id, _xt.Marker)
                case _ocl.Monitor:
                    env.elements[elem.id] = _xt.BeamPositionMonitor()
                case _ocl.Drift:
                    env[elem.id + '_L'] = elem.l
                    env.new(elem.id, _xt.Drift, length=elem.id + '_L')
                case _ocl.RBend:
                    env[elem.id + '_L'] = elem.l
                    env[elem.id + '_ANGLE'] = elem.angle
                    env[elem.id + '_K1'] = elem.k1
                    env.new(elem.id, _xt.RBend, length_straight=elem.id + '_L', angle=elem.id + '_ANGLE',
                            k1=elem.id + '_K1', k0_from_h=True)
                case _ocl.Hcor | _ocl.Vcor:
                    env[elem.id + '_L'] = elem.l
                    env[elem.id + '_ANGLE'] = elem.angle
                    env.new(elem.id, _xt.RBend, length=elem.id + '_L', angle=elem.id + '_ANGLE', k0_from_h=True)
                case _ocl.SBend | _ocl.Bend:
                    env[elem.id + '_L'] = elem.l
                    env[elem.id + '_ANGLE'] = elem.angle
                    env[elem.id + '_E1'] = elem.e1
                    env[elem.id + '_E2'] = elem.e2
                    env[elem.id + '_K1'] = elem.k1
                    env.new(elem.id, _xt.Bend, length=elem.id + '_L', angle=elem.id + '_ANGLE',
                            edge_entry_angle=elem.id + '_E1', edge_exit_angle=elem.id + '_E2',
                            k1=elem.id + '_K1', k0_from_h=True)
                case _ocl.Quadrupole:
                    env[elem.id + '_L'] = elem.l
                    env[elem.id + '_K1'] = elem.k1
                    env.new(elem.id, _xt.Quadrupole, length=elem.id + '_L', k1=elem.id + '_K1')
                case _ocl.Sextupole:
                    env[elem.id + '_L'] = elem.l
                    env[elem.id + '_K2'] = elem.k2
                    env.new(elem.id, _xt.Sextupole, length=elem.id + '_L', k2=elem.id + '_K2')
                case _ocl.Octupole:
                    env[elem.id + '_L'] = elem.l
                    env[elem.id + '_K3'] = elem.k3
                    env.new(elem.id, _xt.Octupole, length=elem.id + '_L', k3=elem.id + '_K3')
                case _ocl.Solenoid:
                    env[elem.id + '_L'] = elem.l
                    env[elem.id + '_KS'] = elem.k
                    env.new(elem.id, _xt.Solenoid, length=elem.id + '_L', ks=elem.id + '_KS')
                case _ocl.EllipticalAperture | _ocl.RectAperture:
                    # env.new(row_twiss.NAME, xt.LimitEllipse, a=row_twiss.XSIZE, b=row_twiss.XSIZE)
                    env[elem.id + '_L'] = elem.l
                    env.new(elem.id, _xt.Drift, length=elem.id + '_L')
                case _ocl.Undulator:
                    env[elem.id + '_L'] = elem.l
                    env.new(elem.id, _xt.Drift, length=elem.id + '_L')
                case _ocl.Cavity | _ocl.TDCavity:
                    # TODO : Fix cavities, not working
                    env[elem.id + '_L'] = elem.l
                    env[elem.id + '_VOLT'] = elem.v * 1e9
                    env[elem.id + '_FREQ'] = elem.freq
                    env[elem.id + '_LAG'] = elem.phi
                    env.new(elem.id, _xt.Cavity, length=elem.id + '_L',
                            voltage=elem.id + '_VOLT', frequency=elem.id + '_FREQ', lag=elem.id + '_LAG')
                # case _ocl.Matrix:
                #     pass
                # case _ocl.Multipole:
                #     pass
                # case _ocl.Undulator:
                #     pass
                case _:
                    print('Unknown type {} for element {}'.format(type(elem), elem.id))
                    if elem.l > 0:
                        env[elem.id + '_L'] = elem.l
                        env.new(elem.id, _xt.Drift, length=elem.id + '_L')
                    else:
                        env.new(elem.id, _xt.Marker)
            if hasattr(elem, 'tilt') and type(elem) not in [_ocl.Drift, _ocl.Marker, _ocl.Monitor, _ocl.Undulator]:
                env[elem.id].rot_s_rad = elem.tilt
    env.new_line(name=line_name, components=linelist, refer='end')

    tws0_xsuite = {'betx': tws0_ocelot.beta_x, 'bety': tws0_ocelot.beta_y,
                   'alfx': tws0_ocelot.alpha_x, 'alfy': tws0_ocelot.alpha_y,
                   'dx': tws0_ocelot.Dx, 'dy': tws0_ocelot.Dy,
                   'dpx': tws0_ocelot.Dxp, 'dpy': tws0_ocelot.Dyp,
                   'mux': tws0_ocelot.mux, 'muy': tws0_ocelot.muy}

    if previousLineList is not None:
        surv0_xsuite, s0 = _getOutuptSurveyPoint(previousLineList, s0, x0, y0, z0, ang_x, ang_y)
    else:
        surv0_xsuite = {'X0': x0, 'Y0': y0, 'Z0': z0, 'theta0': ang_x, 'phi0': ang_y, 'psi0': 0}

    class xsuite:
        def __init__(self, env, tws0, surv0, s0):
            self.env = env
            self.tws0 = tws0
            self.surv0 = surv0
            self.s0 = s0

    return xsuite(env, tws0_xsuite, surv0_xsuite, s0)
