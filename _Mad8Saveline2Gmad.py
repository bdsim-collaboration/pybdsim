import Builder as _Builder
import Saveline as _Saveline

def mad8_saveline_to_gmad(input, output_file_name, start_name=None, end_name=None, ignore_zero_length_items=True,
    samplers='all', aperture_dict={}, collimator_dict={}, beam_pipe_radius=0.2, verbose=False, beam=False):

    zero_length = False  # Is the element so small it's length should be zero.
    items_omitted = []  # Store any items that have been skipped over.

    if type(input) == str:
        mad8 = _Saveline.Loader(input)
    else:
        mad8 = input

    kws = {}
    ilc = _Builder.Machine()

    for element in mad8.elementList:
        element_type = mad8.elementDict[element].keys()[0]
        element_properties = mad8.elementDict[element].values()[0]
        length = element_properties['L'] if 'L' in element_properties else 0 # Everything has a length.
        zero_length = True if length < 1e-9 else False

        if element_type == 'LINE':
            pass # Is this needed?

        elif element_type == 'DRIFT':
            ilc.AddDrift(element, length, **kws)

        elif element_type == 'VKICKER':
            kick = element_properties['KICK'] if 'KICK' in element_properties else 0

            ilc.AddVKicker(element, length) # Doesn't actually seem to add the kick??

        elif element_type == 'HKICKER':
            kick = element_properties['KICK'] if element_properties.has_key('KICK') else 0

            ilc.AddHKicker(element, length, **kws) # Doesn't actually seem to add the kick??

        elif element_type == 'MARKER':
            if ignore_zero_length_items:
                items_omitted.append(element)
            else:
                ilc.AddMarker(element)

        elif element_type == 'SBEND':
            hgap = element_properties['HGAP'] if element_properties.has_key('HGAP') else 0
            angle = element_properties['ANGLE'] if element_properties.has_key('ANGLE') else 0
            fintx = element_properties['FINTX'] if element_properties.has_key('FINTX') else 0
            tilt = element_properties['TILT'] if element_properties.has_key('TILT') else 0
            fint = element_properties['FINT'] if element_properties.has_key('FINT') else 0
            e1 = element_properties['E1'] if element_properties.has_key('E1') else 0
            e2 = element_properties['E2'] if element_properties.has_key('E2') else 0

            # No SBEND option ?

        elif element_type == 'RBEND':
            angle = element_properties['ANGLE'] if 'ANGLE' in element_properties else 0

            ilc.AddDipole(element, 'rbend', angle, **kws)

        elif element_type == 'QUADRUPOLE':
            aperture = element_properties['APERTURE'] if element_properties.has_key('APERTURE') else 0
            k1 = element_properties['K1'] if element_properties.has_key('K1') else 0

            ilc.AddQuadrupole(element, length, k1)

        elif element_type == 'SEXTUPOLE':
            aperture = element_properties['APERTURE'] if element_properties.has_key('APERTURE') else 0
            k2 = element_properties['K2'] if element_properties.has_key('K2') else 0
            tilt = element_properties['TILT'] if element_properties.has_key('TILT') else 0

            ilc.AddSextupole(element, length, k2)

        elif element_type == 'OCTUPOLE':
            aperture = element_properties['APERTURE'] if element_properties.has_key('APERTURE') else 0
            k3 = element_properties['K3'] if element_properties.has_key('K3') else 0

            if ignore_zero_length_items and zero_length:
                items_omitted.append(element)
            elif (not ignore_zero_length_items) and zero_length:
                ilc.AddMarker(element)
                if verbose:
                    print element, ' -> marker instead of octupole'
                else:
                    ilc.AddDrift(element, length, **kws)

            # ilc.AddOctupole(element, length, k3) Not sure if this is implemented or not, Check with Boog or Laurie

        elif element_type == 'MULTIPOLE':  # Not fully implemented, but ready to go when AddMultipole works
            lrad = element_properties['LRAD'] if 'LRAD' in element_properties else 0
            aperture = element_properties['APERTURE'] if 'APERTURE' in element_properties else 0
            tilt = element_properties['TILT'] if 'TILT' in element_properties else 0
            knl = ()
            kns = ()

            for i in range(1, 7): # Range is fixed to between 1 - 6 as far as I can tell, might be more though
                key_l = 'K%sL' % i
                key_s = 'K%sS' % i
                temp = element_properties[key_l] if key_l in element_properties else 0
                temp2 = element_properties[key_s] if key_s in element_properties else 0
                knl = knl + (temp,)
                kns = kns + (temp2,)

            if knl[0] != 0:
                ilc.AddQuadrupole(element, length, knl[0])
            else:
                ilc.AddMarker(element)

            if ignore_zero_length_items and zero_length:
                items_omitted.append(element)
            elif (not ignore_zero_length_items) and zero_length:
                ilc.AddMarker(element)
                if verbose:
                    print element, ' -> marker instead of multipole.'
            else:
                ilc.AddDrift(element, length, **kws)

            # ilc.AddMultipole(element, length, knl, ksl=kns, tilt)  # ksl should be kns to keep format

        elif element_type == 'ECOLLIMATOR':
            if element in collimator_dict:
                kws['material'] = collimator_dict[element]['bdsim_material'] if 'bdsim_material' in collimator_dict else 'Copper'
                ysize = collimator_dict[element]['YSIZE'] if 'YSIZE' in collimator_dict[element] else beam_pipe_radius
                xsize = collimator_dict[element]['XSIZE'] if 'XSIZE' in collimator_dict[element] else beam_pipe_radius
                angle = collimator_dict[element]['ANGLE'] if 'ANGLE' in collimator_dict[element] else 0.0
            else:
                kws['material'] = 'Copper'
                xsize = beam_pipe_radius
                ysize = beam_pipe_radius
                angle = 0.0
            ilc.AddEColAngled(element, length, xsize, ysize, angle)

        elif element_type == 'RCOLLIMATOR':
            if element in collimator_dict:
                kws['material'] = collimator_dict[element]['bdsim_material'] if 'bdsim_material' in collimator_dict else 'Copper'
                ysize = collimator_dict[element]['YSIZE'] if 'YSIZE' in collimator_dict[element] else beam_pipe_radius
                xsize = collimator_dict[element]['XSIZE'] if 'XSIZE' in collimator_dict[element] else beam_pipe_radius
                angle = collimator_dict[element]['ANGLE'] if 'ANGLE' in collimator_dict[element] else 0.0
            else:
                kws['material'] = 'Copper'
                xsize = beam_pipe_radius
                ysize = beam_pipe_radius
                angle = 0.0

            ilc.AddRColAngled(element, length, xsize, ysize, angle, **kws)

        elif element_type == 'WIRE':
            pass  # No implementation found

        elif element_type == 'INSTRUMENT':
            if ignore_zero_length_items and zero_length:
                items_omitted.append(element)
            elif (not ignore_zero_length_items) and zero_length:
                ilc.AddMarker(element)
                if verbose:
                    print element, ' -> marker instead of instrument.'
            else:
                ilc.AddDrift(element, length, **kws)

        elif element_type == 'MONITOR':
            if ignore_zero_length_items and zero_length:
                items_omitted.append(element)
            elif (not ignore_zero_length_items) and zero_length:
                ilc.AddMarker(element)
                if verbose:
                    print element, ' -> marker instead of monitor.'
            else:
                ilc.AddDrift(element, length, **kws)

        elif element_type == 'LCAVITY' :
            aperture = element_properties['APERTURE'] if 'APERTURE' in element_properties else 0
            freq = element_properties['FREQ'] if 'FREQ' in element_properties else 0
            phi0 = element_properties['PHI0'] if 'PHI0' in element_properties else 0
            deltae = element_properties['L'] if 'L' in element_properties else 0
            eloss = element_properties['ELOSS'] if 'ELOSS' in element_properties else 0

            # No implementation found

    ilc.AddSampler('all')
    ilc.WriteLattice('outputfilename')

mad8_saveline_to_gmad('ebds.saveline', 'test.gmad')