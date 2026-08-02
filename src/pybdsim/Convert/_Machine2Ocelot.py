import numpy as _np
import pybdsim as _bd
import ocelot as _ocl


def Machine2Ocelot(bdsmachine, s0=0):
    """ Convert BDSIM machine to an Ocelot lattice.

       +-----------------+---------------------------------------------------------+
       | **Parameters**  | **Description**                                         |
       +-----------------+---------------------------------------------------------+
       | bdsmachine      | BDSIM machine element                                   |
       +-----------------+---------------------------------------------------------+
       | s0              | Initial s position of the line. Optional.               |
       +-----------------+---------------------------------------------------------+
    """

    # Initial Twiss parameters
    tws0 = _ocl.Twiss()
    tws0.beta_x = float(bdsmachine.beam['betx'].split('*')[0])
    tws0.beta_y = float(bdsmachine.beam['bety'].split('*')[0])
    tws0.alpha_x = float(bdsmachine.beam['alfx'].split('*')[0])
    tws0.alpha_y = float(bdsmachine.beam['alfy'].split('*')[0])
    tws0.Dx = float(bdsmachine.beam['dispx'].split('*')[0])
    tws0.Dy = float(bdsmachine.beam['dispy'].split('*')[0])
    tws0.Dxp = float(bdsmachine.beam['dispxp'].split('*')[0])
    tws0.Dyp = float(bdsmachine.beam['dispyp'].split('*')[0])
    # tws0.mux = float(bdsmachine.beam['mux'].split('*')[0])
    # tws0.muy = float(bdsmachine.beam['muy'].split('*')[0])
    tws0.E = float(bdsmachine.beam['energy'].split('*')[0])*1e-9
    tws0.s = s0

    cell = []
    # unique_name_list = []

    for elem_name in bdsmachine.sequence:
        # if elem_name not in unique_name_list:
        #     unique_name_list.append(elem_name)

        element = bdsmachine.elements[elem_name]

        factor = 1
        if bdsmachine.charge == -1:
            factor = -1

        match element.category:
            case 'marker':
                cell.append(_ocl.Marker(eid=elem_name))
            case 'drift':
                cell.append(_ocl.Drift(eid=elem_name, l=element.length))
            case 'rbend':
                e1 = element.get('e1') if element.get('e1') is not None else 0
                e2 = element.get('e2') if element.get('e2') is not None else 0
                k1 = element.get('k1') if element.get('k1') is not None else 0
                cell.append(_ocl.RBend(eid=elem_name, l=element.length, angle=element.get('angle'),
                                       e1=e1, e2=e2, k1=k1))
            case 'sbend':
                e1 = element.get('e1') if element.get('e1') is not None else 0
                e2 = element.get('e2') if element.get('e2') is not None else 0
                k1 = element.get('k1') if element.get('k1') is not None else 0
                cell.append(_ocl.SBend(eid=elem_name, l=element.length, angle=element.get('angle'),
                                       e1=e1, e2=e2, k1=k1))
            case 'quadrupole':
                cell.append(_ocl.Quadrupole(eid=elem_name, l=element.length, k1=factor*element.get('k1')))
            case 'sextupole':
                cell.append(_ocl.Sextupole(eid=elem_name, l=element.length, k2=factor*element.get('k2')))
            case 'octupole':
                cell.append(_ocl.Octupole(eid=elem_name, l=element.length, k3=factor*element.get('k3')))
            case 'solenoid':
                cell.append(_ocl.Solenoid(eid=elem_name, l=element.length, k=element.get('ks')))
            case 'rfcavity':
                volt = element.length * element.get('gradient')
                cell.append(_ocl.Cavity(eid=elem_name, l=element.length, freq=element.get('freq'),
                                        v=volt, phi=element.get('phase')))
            case _:
                print('Unknown element type:', element.category)
                if element.length > 0:
                    cell.append(_ocl.Drift(eid=elem_name, l=element.length))
                else:
                    cell.append(_ocl.Marker(eid=elem_name))
        if element.get('tilt') is not None and element.get('tilt') > 0:
            cell[-1].tilt = element.get('tilt')

    return _ocl.MagneticLattice(cell, method={'global': _ocl.SecondTM}), tws0
