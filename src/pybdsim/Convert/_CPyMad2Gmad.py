from __future__ import annotations as _annotations
from typing import Optional as _Optional
from typing import Dict as _Dict
from typing import Tuple as _Tuple
from typing import MutableMapping as _MutableMapping
from typing import Callable as _Callable
from typing import TYPE_CHECKING as _TYPE_CHECKING
import os as _os
import re as _re
import logging as _logging
import cpymad.madx as _madx
import yaml as _yaml
import pandas as _pd
import numpy as _np
from mergedeep import merge as _merge

import pybdsim.Builder as _Builder
import pybdsim.Beam as _Beam
import pybdsim.Options as _Options

# commented out as seems to be another dependency... don't know about it... only for type checking
#if _TYPE_CHECKING:
#    from pymask.madxp import Madxp

BDSIM_MAD_CONVENTION = {
    'apertype': 'apertureType',
    'circle': 'circular',
    'octagon': 'octagonal',
    'rectangle': 'rectangular',
    'collimator': 'rcol',
    'rcollimator': 'rcol',
    'electron': 'e-',
}

BDSIM_RESERVED_NAME = {
    'ms': 'ms.'
}

BDSIM_MADX_ELEMENTS_ARGUMENTS = ['l',
                                 'k1',
                                 'k1s',
                                 'k2',
                                 'k2s',
                                 'k3',
                                 'ks',
                                 'angle',
                                 'tilt',
                                 'kick',
                                 'hkick',
                                 'vkick',
                                 'knl',
                                 'ksl',
                                 'apertype',
                                 'aperture',
                                 'aper_offset']

BDSIM_ELEMENTS_TO_GENERATE = ['drift', 'sbend', 'rbend', 'quadrupole', 'sextupole', 'octupole',
                              'decapole', 'hkicker', 'vkicker', 'tkicker', 'kicker',
                              'solenoid', 'rcol', 'ecol', 'jcol', 'multipole', 'thinmultipole', 'rfcavity']

MAD_ELEMENTS_TO_DROP_IF_ZERO_LENGTH = ['marker', 'monitor', 'instrument', 'placeholder', 'rcollimator', 'cavity']


def _log_component_info(name: str, parent_name: str, base_name: str, max_length: int = 25) -> str:
    return ' ' * 5 + name.ljust(max_length, ' ') + parent_name.ljust(max_length, ' ') + base_name.ljust(max_length, ' ')


class CPyMad2Gmad:
    def __init__(self,
                 madx_instance,
                 model: _Optional[_Dict] = None,
                 aperture_model: _Callable[[str], str] = None,
                 model_path: str = '.',
                 model_file: str = 'model.yml',
                 log_file: str = 'model.log',
                 ):
        # Read main configuration file
        self.logging = _logging.getLogger()
        handler = _logging.FileHandler(log_file, mode='w')
        handler.setLevel(_logging.INFO)
        self.logging.addHandler(handler)
        self.logging.info("Reading the model configuration file.")
        with open(_os.path.join(model_path, model_file)) as file:
            _ = _yaml.full_load(file)

        # Build the complete model dictionary
        self.model = {}

        # need to check if there are some modules in the yml file
        if _['builder']['modules']:
            for module in _['builder']['modules']:
                with open(_os.path.join(
                        model_path,
                        _['builder']['config']['geometries_path'],
                        'modules',
                        module,
                        'data.yml')
                ) as file:
                    self.model = _merge(self.model, _yaml.full_load(file))
                    self.logging.info(f"Merged data from module '{module}'.")

        self.model = _merge(self.model, _)
        self.model = _merge(self.model, model or {})

        # Add quotes for BDSim options
        for k, v in self.model['options'].items():
            if isinstance(v, str) and '*' not in v:  # Physical quantity with units should not be quoted
                self.model['options'][k] = '"' + v + '"'

        if 'sequence' in self.model.keys():
            # Compile the regular expressions in the model
            self.logging.info("Compiling regular expressions...")
            for r in list(self.model['sequence'].keys()):
                self.model['sequence'][_re.compile(r)] = self.model['sequence'].pop(r)
            self.logging.info("... done.")

        # Aperture model
        self.aperture = aperture_model

        # MAD-X
        self.madx = madx_instance
        self.madx_beam = self.madx.sequence[self.model['builder']['sequence']].beam
        self.madx_sequence = self.madx.sequence[self.model['builder']['sequence']]
        self.madx_expanded_element_positions = self.madx_sequence.expanded_element_positions()
        self.madx_expanded_element_names = self.madx_sequence.expanded_element_names()

        def build_component(element, i, position, level):
            return {
                'NAME': BDSIM_RESERVED_NAME.get(element.name, element.name),
                'PARENT': BDSIM_MAD_CONVENTION.get(element.parent.name, element.parent.name),
                'BASE_PARENT': BDSIM_MAD_CONVENTION.get(element.base_type.name, element.base_type.name),
                'MAD_ELEMENT': element,
                'IS_ELEMENT': element is e,
                'IS_IMPLICIT_DRIFT': level - bottom == 0 and element.parent.name == 'drift',
                'LEVEL': level - bottom,
                'L': element.l,
                'AT': position,
                'ID': i,
                'USED': 1,
            }

        def build_component_recursive(i, element, position, level=0):
            nonlocal bottom
            if element.parent.name != element.name:
                if element.name not in components:
                    components[element.name] = build_component(element, i, position, level)
                    build_component_recursive(i, element.parent, position, level - 1)
                else:
                    components[element.name]['USED'] += 1
            else:
                bottom = level

        components = {}
        self.logging.info("Extracting all elements of the sequence to the dataframe...")
        for i, e, p in self._madx_subsequence():
            bottom = 0
            build_component_recursive(i, e, p)
        self.components = _pd.DataFrame(components.values())
        self.components.sort_values(by=['IS_IMPLICIT_DRIFT', 'IS_ELEMENT', 'BASE_PARENT', 'LEVEL'], inplace=True)
        self.logging.info("... done.")

        self.logging.info("Starting the conversion to BDSIM elements...")
        self.components['BDSIM'] = self.components.apply(self._build_bdsim_component, axis=1)
        self.components['BDSIM_TYPE'] = self.components.apply(lambda _: getattr(_['BDSIM'], 'category', None), axis=1)
        self.components.set_index("NAME", inplace=True)

        used = self.components['USED'].copy()
        for i, _ in self.components.iterrows():
            if _['BDSIM'] is None and _['PARENT'] in used:
                used.loc[_['PARENT']] -= 1
        self.components['USED'] = used
        keep = self.components['USED'] > 0

        self.logging.info("Dropping the following unused components:")
        for _ in keep[~keep].index:
            self.logging.info(' ' * 5 + _)
        self.components = self.components[keep]
        self.logging.info("... done.")

    @property
    def _madx_subsequence(self):
        def _iterator():
            mad_sequence = self.madx.sequence[self.model['builder']['sequence']]
            expanded_elements = mad_sequence.expanded_elements
            expanded_element_positions = mad_sequence.expanded_element_positions()
            idx1 = expanded_elements.index(self.model['builder']['from'] or expanded_elements[0].name)
            idx2 = expanded_elements.index(self.model['builder']['to'] or expanded_elements[-1].name)
            for i in range(idx1, idx2 + 1):
                element = expanded_elements[i]
                if element.base_type.name not in MAD_ELEMENTS_TO_DROP_IF_ZERO_LENGTH or element.get('l', 0.0) > 0.0:
                    yield i, element, expanded_element_positions[i]
                else:
                    self.logging.info(_log_component_info(element.name, element.parent.name, element.base_type.name)
                                      + f" - Skipping element because it should be dropped and its length is zero.")

        return _iterator

    def _get_model_properties_for_element(self, element_name: str) -> _Tuple[_Optional[str], dict]:
        properties = {}
        element_type = None
        for regex, data in self.model['sequence'].items():
            if regex.match(element_name):
                properties = _merge(properties, data['properties'])
                element_type: _Optional[str] = data.get('type', None)
        return element_type, properties

    def _build_bdsim_component_properties(self, element: _pd.Series) -> dict:
        mad_element = element['MAD_ELEMENT']
        mad_parent = mad_element.parent
        bdsim_properties = {}
        for k, v in mad_element.items():
            if k in BDSIM_MADX_ELEMENTS_ARGUMENTS:
                if isinstance(v, _madx.madx.ArrayAttribute):
                    if list(mad_parent.get(k)) != list(v):
                        bdsim_properties[BDSIM_MAD_CONVENTION.get(k, k)] = v
                else:
                    if mad_parent.get(k) != v:
                        bdsim_properties[BDSIM_MAD_CONVENTION.get(k, k)] = v
        if not bool(bdsim_properties):
            bdsim_properties = {'l': mad_element.l}
            self.logging.info(_log_component_info(element['NAME'], element['PARENT'], element['BASE_PARENT'])
                              + f" - Adding the length in the definition because bare aliases are not allowed.")

        return self._generate_apertures(element, self._adjust_bdsim_component_properties(element, bdsim_properties))

    def _generate_apertures(self, element: _pd.Series, bdsim_properties: dict) -> dict:
        """Generate missing apertures"""
        if element['IS_ELEMENT'] \
                and 'apertureType' not in bdsim_properties \
                and 'xsize' not in bdsim_properties \
                and 'ysize' not in bdsim_properties:
            self.logging.info(_log_component_info(element['NAME'], element['PARENT'], element['BASE_PARENT'])
                              + f" - Setting the aperture from the aperture model for this element.")
            if self.aperture:
                if element['NAME'] in self.aperture.keys():
                    apertype, aper1, aper2, aper3, aper4 = self.aperture[element['NAME']]
                else:
                    print(f"Attention, element {element['NAME']} not in aperture model")
                    apertype = "elliptical"
                    aper1 = 0.073
                    aper2 = 0.035
                    aper3 = 0.1
                    aper4 = 0.1
            else:
                apertype = "elliptical"
                aper1 = 0.073
                aper2 = 0.035
                aper3 = 0.1
                aper4 = 0.1
            if element['BASE_PARENT'] == 'rcol':
                bdsim_properties['xsize'] = aper1
                bdsim_properties['ysize'] = aper2
            else:
                bdsim_properties['apertureType'] = apertype
                bdsim_properties['aper1'] = aper1
                bdsim_properties['aper2'] = aper2
                bdsim_properties['aper3'] = aper3
                bdsim_properties['aper4'] = aper4

        return bdsim_properties

    def _adjust_bdsim_component_properties(self, element: _pd.Series, bdsim_properties: dict) -> dict:
        """For this method, explicit is better than implicit!"""

        def convert_aperture_value_definitions():
            k = 'aperture'
            if k in bdsim_properties:
                if len(bdsim_properties[k]) >= 1:
                    bdsim_properties['aper1'] = bdsim_properties[k][0]
                if len(bdsim_properties[k]) >= 2:
                    bdsim_properties['aper2'] = bdsim_properties[k][1]
                if len(bdsim_properties[k]) >= 3:
                    bdsim_properties['aper3'] = bdsim_properties[k][2]
                if len(bdsim_properties[k]) >= 4:
                    bdsim_properties['aper4'] = bdsim_properties[k][3]

        def set_collimator_gap_definitions():
            if element['BASE_PARENT'] == 'rcol':
                if 'aperture' in bdsim_properties:
                    bdsim_properties['xsize'] = bdsim_properties['aper1']
                    bdsim_properties['ysize'] = bdsim_properties['aper2']
                    if 'aper_offset' in bdsim_properties:
                        bdsim_properties['offsetX'] = bdsim_properties['aper_offset'][0]
                        bdsim_properties['offsetY'] = bdsim_properties['aper_offset'][1]
                        del bdsim_properties['aper_offset']
                    del bdsim_properties['aper1']
                    del bdsim_properties['aper2']
                    del bdsim_properties['aper3']
                    del bdsim_properties['aper4']
                    del bdsim_properties['apertureType']
                    self.logging.info(_log_component_info(element['NAME'], element['PARENT'], element['BASE_PARENT'])
                                      + f" - Setting the collimator opening: "
                                        f"xsize={bdsim_properties['xsize']}, ysize={bdsim_properties['ysize']}, "
                                        f"offsetX={bdsim_properties.get('offsetX', 0.0)}, "
                                        f"offsetY={bdsim_properties.get('offsetY', 0.0)}.")
                elif element['IS_ELEMENT']:
                    bdsim_properties['xsize'] = 0.05
                    bdsim_properties['ysize'] = 0.05
                    self.logging.warning(_log_component_info(element['NAME'], element['PARENT'], element['BASE_PARENT'])
                                         + f" - Setting the collimator opening with default values: "
                                           f"xsize={bdsim_properties['xsize']}, ysize={bdsim_properties['ysize']}.")

        def convert_aperture_types():
            k = 'apertureType'
            if k in bdsim_properties:
                bdsim_properties[k] = BDSIM_MAD_CONVENTION.get(bdsim_properties[k], bdsim_properties[k])

            k = 'apertureType'
            v = 'octagonal'
            if bdsim_properties.get(k) == v:
                # https://indico.cern.ch/event/379692/contributions/1804923/subcontributions/156446/attachments/757501/1039118/2105-03-18_HSS_meeting_rev.pdf
                aper3_mad = bdsim_properties['aper3']
                aper4_mad = bdsim_properties['aper4']
                bdsim_properties['aper3'] = bdsim_properties['aper2'] / _np.tan(aper4_mad)
                bdsim_properties['aper4'] = bdsim_properties['aper1'] * _np.tan(aper3_mad)

        def clean_apertures():
            k = 'aperture'
            if k in bdsim_properties:
                del bdsim_properties[k]

            k = ('aper1', 'aper2', 'aper3', 'aper4')
            for _ in k:
                threshold = self.model['builder']['config']['apertures']['remove_above_value']
                if bdsim_properties.get(_, 0.0) > threshold:
                    self.logging.info(_log_component_info(element['NAME'], element['PARENT'], element['BASE_PARENT'])
                                      + f" - Dropping the key {_} because it exceeds the treshold value {threshold}.")
                    del bdsim_properties[_]

            if 'aper1' not in bdsim_properties and 'aper2' not in bdsim_properties and 'aper3' not in bdsim_properties \
                    and 'aper4' not in bdsim_properties and 'apertureType' in bdsim_properties:
                del bdsim_properties['apertureType']
                self.logging.info(_log_component_info(element['NAME'], element['PARENT'], element['BASE_PARENT'])
                                  + f" - Dropping `apertureType` because it has no definition of aperture values.")

        def process_kicker_strengths():
            if element['BASE_PARENT'] == 'hkicker':
                if 'kick' in bdsim_properties:
                    if 'hkick' in bdsim_properties:
                        bdsim_properties['hkick'] += bdsim_properties['kick']
                    else:
                        bdsim_properties['hkick'] = bdsim_properties['kick']
                    del bdsim_properties['kick']
            if element['BASE_PARENT'] == 'vkicker':
                if 'kick' in bdsim_properties:
                    if 'vkick' in bdsim_properties:
                        bdsim_properties['vkick'] += bdsim_properties['kick']
                    else:
                        bdsim_properties['vkick'] = bdsim_properties['kick']
                    del bdsim_properties['kick']

        def process_multipolar_components():
            for _ in ('knl', 'ksl'):
                if _ in bdsim_properties:
                    bdsim_properties[_] = tuple(bdsim_properties[_])

        convert_aperture_value_definitions()
        set_collimator_gap_definitions()
        convert_aperture_types()
        clean_apertures()
        process_kicker_strengths()
        process_multipolar_components()

        return bdsim_properties

    def _generate_bdsim_component(self, element: _pd.Series, bdsim_properties: _MutableMapping):
        """
        Generate the Pybdsim component from its adjusted properties.

        Args:
            element:
            bdsim_properties:

        Returns:

        """
        parent_name = element['PARENT']
        if element['L'] == 0:
            if element['BASE_PARENT'] == 'multipole':
                element['LEVEL'] += 1

            if element['BASE_PARENT'] == 'multipole' \
                    and all(m == 0 for m in bdsim_properties.get('knl', ()) + bdsim_properties.get('ksl', ())) \
                    and element['LEVEL'] == 0:
                self.logging.info(_log_component_info(element['NAME'], element['PARENT'], element['BASE_PARENT'])
                                  + f" - Dropping multipole because its length is zero and it has no field.")
                return None
            if element['BASE_PARENT'] in ('kicker', 'hkicker', 'vkicker', 'tkicker') \
                    and bdsim_properties.get('hkick', 0.0) == 0 \
                    and bdsim_properties.get('vkick', 0.0) == 0 \
                    and element['LEVEL'] == 0:
                self.logging.info(_log_component_info(element['NAME'], element['PARENT'], element['BASE_PARENT'])
                                  + f" - Dropping kicker because its length is zero and it has no field.")
                return None
            # if :  # Means it is a base type
            #     parent_name = 'thinmultipole'
            #     logging.info(_log_component_info(element['NAME'], element['PARENT'], element['BASE_PARENT'])
            #                  + f" - Converting to thinmultipole because it is a zero-length multipole.")

        if element['PARENT'] not in self.components['NAME'].values:
            if element['PARENT'] not in BDSIM_ELEMENTS_TO_GENERATE:
                parent_name = 'drift'
                self.logging.info(_log_component_info(element['NAME'], element['PARENT'], element['BASE_PARENT'])
                                  + f" - Converting to a drift because {element['PARENT']} is not supported.")
            bdsim_component = _Builder.Element(
                name=element['NAME'],
                category=parent_name,
                isMultipole='knl' in bdsim_properties or 'ksl' in bdsim_properties,
                **bdsim_properties)
        else:
            bdsim_component = _Builder.Element.from_element(
                name=element['NAME'],
                parent_element_name=parent_name,
                isMultipole='knl' in bdsim_properties.keys() or 'ksl' in bdsim_properties.keys(),
                **bdsim_properties)

        return bdsim_component

    def _build_bdsim_component(self, element: _pd.Series):
        bdsim_properties = self._build_bdsim_component_properties(element)

        if 'sequence' in self.model.keys():
            bdsim_element_type, properties = self._get_model_properties_for_element(element['NAME'])
            bdsim_properties = _merge(bdsim_properties, properties)
            element['PARENT'] = bdsim_element_type or BDSIM_RESERVED_NAME.get(element['PARENT'], element['PARENT'])
        else:
            element['PARENT'] = BDSIM_RESERVED_NAME.get(element['PARENT'], element['PARENT'])

        return self._generate_bdsim_component(element, bdsim_properties)

    def __call__(self,
                 with_bdsim_beam: bool = True,
                 with_bdsim_options: bool = True,
                 with_bdsim_placements: bool = True,
                 ):
        bdsim_input = _Builder.Machine()
        components = self.components[~self.components['BDSIM'].isnull()]
        # Add all components
        for name, component in components.iterrows():
            bdsim_input.Append(component['BDSIM'], is_component=True)

        # Add elements (won't be redefined, simply added to the sequence)
        for name, component in components.query("IS_ELEMENT == True").sort_values(by=['ID']).iterrows():
            bdsim_input.Append(component['BDSIM'], is_component=False)
            if 'apertureType' not in component['BDSIM'].keys() and 'xsize' not in component['BDSIM'].keys() \
                    and 'ysize' not in component['BDSIM'].keys():
                self.logging.warning(_log_component_info(name, component['PARENT'], component['BASE_PARENT'])
                                     + f" - Placing an element with no aperture definition !")

        if with_bdsim_beam:
            if 'twiss' not in self.madx.table:
                self.madx.input('twiss;')
            tw = self.madx.table['twiss'].dframe().iloc[0]
            bdsim_beam = _Beam.Beam(particletype=self.madx_beam['particle'],
                                           energy=self.madx_beam['energy'],
                                           distrtype='gausstwiss')
            bdsim_beam.SetX0(tw['x'])
            bdsim_beam.SetXP0(tw['px'])
            bdsim_beam.SetY0(tw['y'])
            bdsim_beam.SetYP0(tw['py'])
            bdsim_beam.SetBetaX(tw['betx'])
            bdsim_beam.SetBetaY(tw['bety'])
            bdsim_beam.SetAlphaX(tw['alfx'])
            bdsim_beam.SetAlphaY(tw['alfy'])
            bdsim_beam.SetDispX(tw['dx'])
            bdsim_beam.SetDispY(tw['dy'])

            bdsim_beam.SetEmittanceX(self.madx_beam['ex'])
            bdsim_beam.SetEmittanceY(self.madx_beam['ey'])
            bdsim_beam.SetSigmaE(self.madx_beam['sige'])
            #bdsim_beam.SetSigmaT(self.madx_beam['sigt'])
            bdsim_input.AddBeam(bdsim_beam)

        if with_bdsim_options:
            bdsim_input.AddOptions(_Options.Options(**self.model['options']))

        # if with_bdsim_placements:
        #     for ref_name, placements in self.placement_properties.items():
        #         for plcm in placements:
        #             for plm_name, placement_prop in plcm.items():
        #                 placement_prop['referenceElement'] = ref_name
        #                 bdsim_input.AddPlacement(plm_name + '_' + ref_name, **placement_prop)

        # if with_blms:
        #     pass
        #     # Add BLM
        #     for ref_name, blms in self.blms_properties.items():
        #         for blm in blms:
        #             for blm_name, blm_prop in blm.items():
        #                 blm_prop['referenceElement'] = ref_name
        #                 bdsim_input.AddBLM(blm_name + '_' + ref_name, **blm_prop)
        #

        #
        # if with_individual_placement:
        #     for ref_name, placements in self.aperture_file['placements'].items():
        #         bdsim_input.AddPlacement(ref_name, **placements)
        #

        return bdsim_input
