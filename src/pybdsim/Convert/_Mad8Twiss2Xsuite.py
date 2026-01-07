import numpy as _np
import xtrack as xt
from docutils.nodes import row


def Mad8Twiss2Xsuite(mad8twiss,
                     mad8survey,
                     mad8rmat=None,
                     line_name='line_from_mad8',
                     particle='e-',
                     startindex=None,
                     endindex=None,
                     startname=None,
                     endname=None,
                     ):

    match particle:
        case 'e-' | 'electron':
            q0 = -1
            mass0 = xt.ELECTRON_MASS_EV
        case 'e+' | 'positron':
            q0 = 1
            mass0 = xt.ELECTRON_MASS_EV
        case 'p' | 'proton':
            q0 = 1
            mass0 = xt.PROTON_MASS_EV
        case _:
            Warning('Unrecognized particle type. Defaulting to electron.')
            q0 = -1
            mass0 = xt.ELECTRON_MASS_EV

    if startindex is None:
        startindex = 0
    if endindex is None:
        endindex = mad8twiss.nrec
    if startname is not None:
        startindex = mad8twiss.getIndexByNames(startname)
    if endname is not None:
        endindex = mad8twiss.getIndexByNames(endname)

    env = xt.Environment()
    env.particle_ref = xt.Particles(p0c=_getEndEnergy(mad8twiss)*1e9, q0=q0, mass0=mass0)

    linelist = []

    nblcav = 0
    nbmatr = 0

    for i in range(startindex, endindex):
        row_twiss = mad8twiss.getRowsByIndex(i)
        row_survey = mad8survey.getRowsByIndex(i)
        linelist.append(row_twiss.NAME)

        if row_twiss.NAME not in env.elements:
            match row_twiss.TYPE:
                case '    ':
                    env.new(row_twiss.NAME, xt.Marker)
                case 'MARK' | 'MONI':
                    env.new(row_twiss.NAME, xt.Marker)
                case 'DRIF':
                    env[row_twiss.NAME + '_L'] = row_twiss.L
                    env.new(row_twiss.NAME, xt.Drift, length=row_twiss.NAME + '_L')
                case 'RBEN':
                    env[row_twiss.NAME + '_L'] = row_twiss.L
                    # env[row_survey.NAME + '_ANGLE'] = _np.nan_to_num(row_survey.ANGLE)
                    env[row_twiss.NAME + '_ANGLE'] = _np.nan_to_num(row_twiss.ANGLE)
                    env.new(row_twiss.NAME, xt.RBend, length=row_twiss.NAME + '_L', angle=row_twiss.NAME + '_ANGLE', k0_from_h=True)
                case 'KICK' | 'HKIC' | 'VKIC':
                    env[row_twiss.NAME + '_L'] = row_twiss.L
                    env[row_twiss.NAME + '_ANGLE'] = _np.nan_to_num(row_twiss.ANGLE)
                    env.new(row_twiss.NAME, xt.RBend, length=row_twiss.NAME + '_L', angle=row_twiss.NAME + '_ANGLE', k0_from_h=True)
                case 'SBEN':
                    env[row_twiss.NAME + '_L'] = row_twiss.L
                    env[row_twiss.NAME + '_ANGLE'] = row_twiss.ANGLE
                    env[row_twiss.NAME + '_E1'] = row_twiss.E1
                    env[row_twiss.NAME + '_E2'] = row_twiss.E2
                    env.new(row_twiss.NAME, xt.Bend, length=row_twiss.NAME + '_L', angle=row_twiss.NAME + '_ANGLE',
                            edge_entry_angle=row_twiss.NAME + '_E1', edge_exit_angle=row_twiss.NAME + '_E2',
                            k0_from_h=True)
                case 'QUAD':
                    env[row_twiss.NAME + '_L'] = row_twiss.L
                    env[row_twiss.NAME + '_K1'] = row_twiss.K1
                    env.new(row_twiss.NAME, xt.Quadrupole, length=row_twiss.NAME + '_L', k1=row_twiss.NAME + '_K1')
                case 'SEXT':
                    env[row_twiss.NAME + '_L'] = row_twiss.L
                    env[row_twiss.NAME + '_K2'] = row_twiss.K2
                    env.new(row_twiss.NAME, xt.Sextupole, length=row_twiss.NAME + '_L', k2=row_twiss.NAME + '_K2')
                case 'OCTU':
                    env[row_twiss.NAME + '_L'] = row_twiss.L
                    env[row_twiss.NAME + '_K3'] = row_twiss.K3
                    env.new(row_twiss.NAME, xt.Octupole, length=row_twiss.NAME + '_L', k3=row_twiss.NAME + '_K3')
                case 'SOLE':
                    env[row_twiss.NAME + '_L'] = row_twiss.L
                    env[row_twiss.NAME + '_KS'] = row_twiss.KS
                    env.new(row_twiss.NAME, xt.Solenoid, length=row_twiss.NAME + '_L', ks=row_twiss.NAME + '_KS')
                case 'ECOL':
                    # env.new(row_twiss.NAME, xt.LimitEllipse, a=row_twiss.XSIZE, b=row_twiss.XSIZE)
                    env[row_twiss.NAME + '_L'] = row_twiss.L
                    env.new(row_twiss.NAME, xt.Drift, length=row_twiss.NAME + '_L')
                case 'SROT':
                    env[row_twiss.NAME + '_ANGLE'] = row_twiss.ANGLE * 180 / _np.pi
                    env.new(row_twiss.NAME, xt.SRotation, angle=row_twiss.NAME + '_ANGLE')
                case 'YROT':
                    env[row_twiss.NAME + '_ANGLE'] = row_twiss.ANGLE * 180 / _np.pi
                    env.new(row_twiss.NAME, xt.YRotation, angle=row_twiss.NAME + '_ANGLE')
                case 'LCAV':
                    # TODO : Not working properly, seems to act like drift
                    env[row_twiss.NAME + '_L'] = row_twiss.L
                    env[row_twiss.NAME + '_VOLT'] = row_twiss.VOLT * 1e6
                    env[row_twiss.NAME + '_FREQ'] = row_twiss.FREQ * 1e6
                    env[row_twiss.NAME + '_LAG'] = row_twiss.LAG * 360
                    # env[row_twiss.NAME + '_ref_e_increase_DE'] = (row_twiss.E - mad8twiss.getRowsByIndex(i-1).E) * 1e9
                    env.new(row_twiss.NAME, xt.Cavity, length=row_twiss.NAME + '_L',
                            voltage=row_twiss.NAME + '_VOLT', frequency=row_twiss.NAME + '_FREQ', lag=row_twiss.NAME + '_LAG')
                    # env.elements[row_twiss.NAME + '_ref_e_increase'] = xt.ReferenceEnergyIncrease(
                    #     Delta_p0c=-env[row_twiss.NAME + '_ref_e_increase_DE'])
                case 'MATR':
                    # TODO : Was not working with EUXFEL mad8. Have to check with another model
                    if mad8rmat is not None:
                        row_rmat = mad8rmat.getRowsByIndex(i)
                        M = _np.array([[row_rmat.R11, row_rmat.R12, row_rmat.R13, row_rmat.R14, row_rmat.R15, row_rmat.R16],
                                       [row_rmat.R21, row_rmat.R22, row_rmat.R23, row_rmat.R24, row_rmat.R25, row_rmat.R26],
                                       [row_rmat.R31, row_rmat.R32, row_rmat.R33, row_rmat.R34, row_rmat.R35, row_rmat.R36],
                                       [row_rmat.R41, row_rmat.R42, row_rmat.R43, row_rmat.R44, row_rmat.R45, row_rmat.R46],
                                       [row_rmat.R51, row_rmat.R52, row_rmat.R53, row_rmat.R54, row_rmat.R55, row_rmat.R56],
                                       [row_rmat.R61, row_rmat.R62, row_rmat.R63, row_rmat.R64, row_rmat.R65, row_rmat.R66]])
                        env.elements[row_rmat.NAME] = xt.LineSegmentMap(length=row_rmat.L, damping_matrix=M)
                    else:
                        print('Rmat file not provided. Defaulting to drift')
                        env[row_twiss.NAME + '_L'] = row_twiss.L
                        env.new(row_twiss.NAME, xt.Drift, length=row_twiss.NAME + '_L')
                case _:
                    print('Unknown type {} for element {}'.format(row_twiss.TYPE, row_twiss.NAME))
                    if not _np.isnan(row_twiss.L) and row_twiss.L > 0:
                        env[row_twiss.NAME + '_L'] = row_twiss.L
                        env.new(row_twiss.NAME, xt.Drift, length=row_twiss.NAME + '_L')
                    else:
                        env.new(row_twiss.NAME, xt.Marker)
            if _np.nan_to_num(row_survey.TILT) != 0:
                env[row_survey.NAME].rot_s_rad = row_survey.TILT
    env.new_line(name=line_name, components=linelist, refer='end')

    # Register input position and twiss
    surv0 = _getInputPosAnglAtIndex(mad8survey, startindex-1)
    tws0 = _getInputTwissAtIndex(mad8twiss, startindex-1)

    return env, tws0, surv0


def _getInputPosAnglAtIndex(mad8survey, index=0):
    if index == -1:
        index = 0
    row = mad8survey.getRowsByIndex(index)
    return {'X0': row.X, 'Y0': row.Y, 'Z0': row.Z,
            'theta0': row.THETA + _np.nan_to_num(row.ANGLE), 'phi0': row.PHI, 'psi0': row.PSI}


def _getInputTwissAtIndex(mad8twiss, index=0):
    if index == -1:
        index = 0
    row = mad8twiss.getRowsByIndex(index)
    # return xt.TwissInit(betx=row.BETX, bety=row.BETY, alfx=row.ALPHX, alfy=row.ALPHY,
    #                     dx=row.DX,     dy=row.DY,     dpx=row.DPX,    dpy=row.DPY,
    #                     mux=row.MUX,   muy=row.MUY)
    return {'betx': row.BETX, 'bety': row.BETY, 'alfx': row.ALPHX, 'alfy': row.ALPHY,
            'dx': row.DX, 'dy': row.DY, 'dpx': row.DPX, 'dpy': row.DPY,
            'mux': row.MUX, 'muy': row.MUY}


def _getStartEnery(mad8twiss):
    row = mad8twiss.getRowsByIndex(0)
    return row.E


def _getEndEnergy(mad8twiss):
    row = mad8twiss.data.iloc[-1]
    return row.E
