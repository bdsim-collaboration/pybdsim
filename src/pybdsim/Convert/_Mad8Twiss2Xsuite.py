import numpy as _np
import xtrack as xt


def Mad8Twiss2Xsuite(mad8twiss,
                     linename='line_from_mad8',
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
        row = mad8twiss.getRowsByIndex(i)
        # row_rmat = rmat.getRowsByIndex(i)

        linelist.append(row.NAME)

        if row.NAME not in env.elements:
            match row.TYPE:
                case '    ':
                    env.new(row.NAME, xt.Marker)
                case 'MARK' | 'MONI':
                    env.new(row.NAME, xt.Marker)
                case 'DRIF':
                    env[row.NAME + '_L'] = row.L
                    env.new(row.NAME, xt.Drift, length=row.NAME + '_L')
                case 'KICK':
                    env[row.NAME + '_L'] = row.L
                    env.new(row.NAME, xt.Drift, length=row.NAME + '_L')
                case 'HKIC':
                    env[row.NAME + '_L'] = row.L
                    env.new(row.NAME, xt.RBend, length=row.NAME + '_L', k0=0)
                case 'VKIC':
                    env[row.NAME + '_L'] = row.L
                    env.new(row.NAME, xt.RBend, length=row.NAME + '_L', k0=0)
                case 'RBEN':
                    env[row.NAME + '_L'] = row.L
                    env[row.NAME + '_ANGLE'] = row.ANGLE
                    env.new(row.NAME, xt.RBend, length=row.NAME + '_L', angle=row.NAME + '_ANGLE',
                            k0_from_h=True)
                case 'SBEN':
                    env[row.NAME + '_L'] = row.L
                    env[row.NAME + '_ANGLE'] = row.ANGLE
                    env[row.NAME + '_E1'] = row.E1
                    env[row.NAME + '_E2'] = row.E2
                    env.new(row.NAME, xt.Bend, length=row.NAME + '_L', angle=row.NAME + '_ANGLE',
                            edge_entry_angle=row.NAME + '_E1', edge_exit_angle=row.NAME + '_E2',
                            k0_from_h=True)
                case 'QUAD':
                    env[row.NAME + '_L'] = row.L
                    env[row.NAME + '_K1'] = row.K1
                    env.new(row.NAME, xt.Quadrupole, length=row.NAME + '_L', k1=row.NAME + '_K1')
                case 'SEXT':
                    env[row.NAME + '_L'] = row.L
                    env[row.NAME + '_K2'] = row.K2
                    env.new(row.NAME, xt.Sextupole, length=row.NAME + '_L', k2=row.NAME + '_K2')
                case 'OCTU':
                    env[row.NAME + '_L'] = row.L
                    env[row.NAME + '_K3'] = row.K3
                    env.new(row.NAME, xt.Octupole, length=row.NAME + '_L', k3=row.NAME + '_K3')
                case 'SOLE':
                    env[row.NAME + '_L'] = row.L
                    env[row.NAME + '_KS'] = row.KS
                    env.new(row.NAME, xt.Solenoid, length=row.NAME + '_L', ks=row.NAME + '_KS')
                case 'ECOL':
                    # env.new(row.NAME, xt.LimitEllipse, a=row.XSIZE, b=row.XSIZE)
                    env[row.NAME + '_L'] = row.L
                    env.new(row.NAME, xt.Drift, length=row.NAME + '_L')
                case 'SROT':
                    env[row.NAME + '_ANGLE'] = row.ANGLE
                    env.new(row.NAME, xt.SRotation, angle=row.NAME + '_ANGLE')
                case 'YROT':
                    env[row.NAME + '_ANGLE'] = row.ANGLE
                    env.new(row.NAME, xt.YRotation, angle=row.NAME + '_ANGLE')
                case 'LCAV':
                    name = row.NAME + '_lcav_' + str(nblcav)
                    linelist[-1] = name

                    # env.new(row.NAME, xt.Cavity, voltage=row.VOLT, frequency=row.FREQ, lag=row.LAG)  # No length in Xsuite cavity
                    prev_row = mad8twiss.getRowsByIndex(i - 1)
                    env.elements[name] = xt.LineSegmentMap(length=row.L,
                                                           qx=row.MUX, qy=row.MUY,
                                                           betx=(prev_row.BETX, row.BETX), bety=(prev_row.BETY, row.BETY),
                                                           alfx=(prev_row.ALPHX, row.ALPHX), alfy=(prev_row.ALPHY, row.ALPHY),
                                                           dx=(prev_row.DX, row.DX), dy=(prev_row.DY, row.DY),
                                                           dpx=(prev_row.DPX, row.DPX), dpy=(prev_row.DPY, row.DPY))
                    nblcav += 1
                case 'MATR':
                    name = row.NAME + '_matr_' + str(nbmatr)
                    linelist[-1] = name

                    prev_row = mad8twiss.getRowsByIndex(i - 1)
                    env.elements[name] = xt.LineSegmentMap(length=row.L,
                                                           qx=row.MUX, qy=row.MUY,
                                                           betx=(prev_row.BETX, row.BETX), bety=(prev_row.BETY, row.BETY),
                                                           alfx=(prev_row.ALPHX, row.ALPHX), alfy=(prev_row.ALPHY, row.ALPHY),
                                                           dx=(prev_row.DX, row.DX), dy=(prev_row.DY, row.DY),
                                                           dpx=(prev_row.DPX, row.DPX), dpy=(prev_row.DPY, row.DPY))
                    nbmatr += 1
                #     M = [[row_rmat.R11-1, row_rmat.R12, row_rmat.R13, row_rmat.R14, 0, 0],
                #          [row_rmat.R21, row_rmat.R22-1, row_rmat.R23, row_rmat.R24, 0, 0],
                #          [row_rmat.R31, row_rmat.R32, row_rmat.R33-1, row_rmat.R34, 0, 0],
                #          [row_rmat.R41, row_rmat.R42, row_rmat.R43, row_rmat.R44-1, 0, 0],
                #          [0, 0, 0, 0, 0, 0],
                #          [0, 0, 0, 0, 0, 0]]
                #     env.elements[row.NAME] = xt.LineSegmentMap(length=row.L, damping_matrix=M)
                case _:
                    env[row.NAME + '_L'] = row.L
                    env.new(row.NAME, xt.Drift, length=row.NAME + '_L')
                    print('Unknown type {} for element {}'.format(row.TYPE, row.NAME))
            if not _np.isnan(row.TILT) and row.TILT != 0:
                env[row.NAME].rot_s_rad = row.TILT
    env.new_line(name=linename, components=linelist, refer='end')
    env.lines[linename]._extra_config['twiss_default'] = _getTwissAtIndex(mad8twiss, 0)
    return env


def _getTwissAtIndex(mad8twiss, index):
    row = mad8twiss.getRowsByIndex(index)
    return {'betx': row.BETX, 'bety': row.BETY, 'alfx': row.ALPHX, 'alfy': row.ALPHY,
            'dx': row.DX, 'dy': row.DY, 'dpx': row.DPX, 'dpy': row.DPY}


def _getStartEnery(mad8twiss):
    row = mad8twiss.getRowsByIndex(0)
    return row.E


def _getEndEnergy(mad8twiss):
    row = mad8twiss.data.iloc[-1]
    return row.E
