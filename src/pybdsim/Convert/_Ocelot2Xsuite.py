import numpy as _np
import xtrack as _xt
import ocelot as _ocl


def getOutuptSurveyPoint(ocelotlist):
    """ Compute the position and angle at the end of a line. """
    if isinstance(ocelotlist, list):
        tws0 = ocelotlist[0].tws0
        cell = ()
        for ocelot in ocelotlist:
            cell += ocelot.cell
    else:
        cell = ocelotlist.cell
        tws0 = ocelotlist.tws0
    lat = _ocl.MagneticLattice(cell)
    tws = _ocl.twiss(lat, tws0)
    survey = lat.survey(z0=tws0.s)
    return {'x0': survey[0][-1], 'y0': survey[1][-1], 'z0': survey[2][-1],
            'ang_x': survey[3][-1], 'ang_y': survey[4][-1]}


def Ocelot2Xsuite(lattice, twiss_init, survey_init=None, line_name='line_from_ocelot'):
    """ Convert Ocelot lattice to Xsuite environment.

        +-----------------+---------------------------------------------------------+
        | **Parameters**  | **Description**                                         |
        +-----------------+---------------------------------------------------------+
        | lattice         | Ocelot lattice                                          |
        +-----------------+---------------------------------------------------------+
        | twiss_init      | Initial twiss element from Ocelot                       |
        +-----------------+---------------------------------------------------------+
        | line_name       | Name that will be used for the created Xsuite line.     |
        |                 | By default it is 'line_from_ocelot'.                    |
        +-----------------+---------------------------------------------------------+
    """

    env = _xt.Environment()
    env.particle_ref = _xt.Particles(p0c=twiss_init.E, q0=-1, mass0=_xt.ELECTRON_MASS_EV)

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
                    env.new(elem.id, _xt.RBend, length=elem.id + '_L', angle=elem.id + '_ANGLE',
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

    tws0 = {'betx': twiss_init.beta_x, 'bety': twiss_init.beta_y,
            'alfx': twiss_init.alpha_x, 'alfy': twiss_init.alpha_y,
            'dx': twiss_init.Dx, 'dy': twiss_init.Dy,
            'dpx': twiss_init.Dxp, 'dpy': twiss_init.Dyp,
            'mux': twiss_init.mux, 'muy': twiss_init.muy}

    if survey_init is not None:
        surv0 = {'X0': survey_init['x0'], 'Y0': survey_init['y0'], 'Z0': survey_init['z0'],
                 'theta0': survey_init['ang_x'], 'phi0': survey_init['ang_y'], 'psi0': 0}
    else:
        surv0 = None

    return env, tws0, surv0
