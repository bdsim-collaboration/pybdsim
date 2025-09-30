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
    # rmat = _m8.Output(rmatfile, 'rmat')

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
        # row_rmat = mad8rmat.getRowsByIndex(i)

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
                    name = row_twiss.NAME + '_lcav_' + str(nblcav)
                    linelist[-1] = name

                    # env.new(row_twiss.NAME, xt.Cavity, voltage=row_twiss.VOLT, frequency=row_twiss.FREQ, lag=row_twiss.LAG)
                    # No length in Xsuite cavity

                    prev_row_twiss = mad8twiss.getRowsByIndex(i - 1)
                    env.elements[name] = xt.LineSegmentMap(length=row_twiss.L,
                                                           qx=row_twiss.MUX, qy=row_twiss.MUY,
                                                           betx=(prev_row_twiss.BETX, row_twiss.BETX), bety=(prev_row_twiss.BETY, row_twiss.BETY),
                                                           alfx=(prev_row_twiss.ALPHX, row_twiss.ALPHX), alfy=(prev_row_twiss.ALPHY, row_twiss.ALPHY),
                                                           dx=(prev_row_twiss.DX, row_twiss.DX), dy=(prev_row_twiss.DY, row_twiss.DY),
                                                           dpx=(prev_row_twiss.DPX, row_twiss.DPX), dpy=(prev_row_twiss.DPY, row_twiss.DPY))
                    nblcav += 1
                case 'MATR':
                    name = row_twiss.NAME + '_matr_' + str(nbmatr)
                    linelist[-1] = name

                    prev_row_twiss = mad8twiss.getRowsByIndex(i - 1)
                    env.elements[name] = xt.LineSegmentMap(length=row_twiss.L,
                                                           qx=row_twiss.MUX, qy=row_twiss.MUY,
                                                           betx=(prev_row_twiss.BETX, row_twiss.BETX), bety=(prev_row_twiss.BETY, row_twiss.BETY),
                                                           alfx=(prev_row_twiss.ALPHX, row_twiss.ALPHX), alfy=(prev_row_twiss.ALPHY, row_twiss.ALPHY),
                                                           dx=(prev_row_twiss.DX, row_twiss.DX), dy=(prev_row_twiss.DY, row_twiss.DY),
                                                           dpx=(prev_row_twiss.DPX, row_twiss.DPX), dpy=(prev_row_twiss.DPY, row_twiss.DPY))
                    nbmatr += 1
                #     M = [[row_rmat.R11-1, row_rmat.R12, row_rmat.R13, row_rmat.R14, 0, 0],
                #          [row_rmat.R21, row_rmat.R22-1, row_rmat.R23, row_rmat.R24, 0, 0],
                #          [row_rmat.R31, row_rmat.R32, row_rmat.R33-1, row_rmat.R34, 0, 0],
                #          [row_rmat.R41, row_rmat.R42, row_rmat.R43, row_rmat.R44-1, 0, 0],
                #          [0, 0, 0, 0, 0, 0],
                #          [0, 0, 0, 0, 0, 0]]
                #     env.elements[row.NAME] = xt.LineSegmentMap(length=row.L, damping_matrix=M)
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

    _setInputPosAnglAtIndex(env, line_name, mad8survey, startindex)
    inputTwiss = _getInputTwissAtIndex(mad8twiss, startindex)
    env.lines[line_name]._extra_config['twiss_default'] = inputTwiss

    return env


def _setInputPosAnglAtIndex(env, line_name, mad8survey=None, index=0):
    try:
        row = mad8survey.getRowsByIndex(index)
        env[f"X0_{line_name}"] = row.X
        env[f"Y0_{line_name}"] = row.Y
        env[f"Z0_{line_name}"] = row.Z
        env[f"theta0_{line_name}"] = row.THETA + _np.nan_to_num(row.ANGLE)
        env[f"phi0_{line_name}"] = row.PHI
        env[f"psi0_{line_name}"] = row.PSI
    except:
        pass


def _getInputTwissAtIndex(mad8twiss=None, index=0):
    try:
        row = mad8twiss.getRowsByIndex(index)
        return {
                'betx': row.BETX, 'bety': row.BETY, 'alfx': row.ALPHX, 'alfy': row.ALPHY,
                'dx': row.DX, 'dy': row.DY, 'dpx': row.DPX, 'dpy': row.DPY
               }
    except:
        return {}


def _getStartEnery(mad8twiss):
    row = mad8twiss.getRowsByIndex(0)
    return row.E


def _getEndEnergy(mad8twiss):
    row = mad8twiss.data.iloc[-1]
    return row.E
