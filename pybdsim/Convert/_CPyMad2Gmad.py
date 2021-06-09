from __future__ import annotations
from typing import Optional, Dict
import os
import re

import yaml
import pandas as _pd
import numpy as _np
from mergedeep import merge
import pybdsim
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pymask.madxp import Madxp

BDSIM_MAD_CONVENTION = {
    'apertype': 'apertureType',
    'circle': 'circular',
    'octagon': 'octagonal',
    'rectangle': 'rectangular',
    'rcollimator': 'rcol',
    'electron': 'e-'}

BDSIM_RESERVED_NAME = {
    'ms': 'ms.'
}

BDSIM_ELEMENTS_ARGUMENTS = ['l',
                            'k1',
                            'k2',
                            'angle',
                            'knl',
                            'ksl',
                            'apertype',
                            'aperture']

# Keep these elements (in BDSIM convention)
ELEMENTS_TO_KEEP = ['drift', 'sbend', 'rbend', 'quadrupole', 'sextupole', 'octupole', 'hkicker', 'vkicker', 'solenoid',
                    'rcol', 'multipole', 'thinmultipole']

ELEMENTS_TO_DROP = ['monitor', 'marker', 'instrument']


class CPyMad2Gmad:
    def __init__(self,
                 madx_instance: Madxp,
                 model: Optional[Dict] = None,
                 model_path: str = '.',
                 model_file: str = 'model.yml',
                 ):
        # Read main configuration file
        with open(os.path.join(model_path, model_file)) as file:
            _ = yaml.full_load(file)

        # Build the complete model dictionnary
        self.model = {}
        for module in _['builder']['modules']:
            with open(os.path.join(
                    model_path,
                    _['builder']['config']['geometries_path'],
                    'modules',
                    module,
                    'data.yml')
            ) as file:
                self.model = merge(self.model, yaml.full_load(file))
        self.model = merge(self.model, _)
        self.model = merge(self.model, model or {})

        # Add quotes for BDSim options
        for k, v in self.model['options'].items():
            if isinstance(v, str):
                self.model['options'][k] = '"' + v + '"'

        # Compile the regular expressions in the model
        for r in list(self.model['sequence'].keys()):
            self.model['sequence'][re.compile(r)] = self.model['sequence'].pop(r)

        # MAD-X
        self.madx = madx_instance
        self.madx_beam = self.madx.sequence[self.model['builder']['sequence']].beam

        def build_component(element, i, level):
            parent = element.parent.name
            base_parent = element.base_type.name
            length = element.l
            if parent == 'multipole' and base_parent == 'multipole' and length == 0:
                parent = 'thinmultipole'
                base_parent = 'thinmultipole'
                length = None
            elif base_parent != 'multipole' and length == 0:
                parent = 'marker'
                base_parent = 'marker'

            return {
                'NAME': element.name,
                'PARENT': BDSIM_MAD_CONVENTION.get(parent, parent),
                'BASE_PARENT': BDSIM_MAD_CONVENTION.get(base_parent, base_parent),
                'IS_ELEMENT': element is e,
                'IS_DRIFT': element.parent.name == 'drift',
                'LEVEL': level - bottom,
                'AT': element.at,
                'L': length,
                'ID': i,
            }

        def build_component_recursive(element, i, level=0):
            nonlocal bottom
            if element.parent.name != element.name and element.base_type.name != 'marker':
                build_component_recursive(element.parent, i, level - 1)
                component = build_component(element, i, level)
                if component['BASE_PARENT'] in ELEMENTS_TO_KEEP:
                    components.append(component)
            else:
                bottom = level

        components = []
        for i, e in enumerate(self._madx_subsequence()):
            bottom = 0
            build_component_recursive(e, i)
        self.components = _pd.DataFrame(components)
        # Fast method to drop duplicated indices - https://stackoverflow.com/a/34297689/420892
        self.components = self.components[~self.components['NAME'].duplicated(keep='first')]
        self.components.sort_values(by=['IS_DRIFT', 'IS_ELEMENT', 'BASE_PARENT', 'LEVEL'], inplace=True)
        self.components['BDSIM'] = self.components.apply(lambda r: self._build_bdsim_component(r['NAME'], r), axis=1)
        self.components.set_index("NAME", inplace=True)

    @property
    def _madx_subsequence(self):
        def _iterator():
            expanded_elements = self.madx.sequence[self.model['builder']['sequence']].expanded_elements
            idx1 = expanded_elements.index(self.model['builder']['from'] or expanded_elements[0].name)
            idx2 = expanded_elements.index(self.model['builder']['to'] or expanded_elements[-1].name)
            for i in range(idx1, idx2+1):
                if expanded_elements[i].base_type.name not in ELEMENTS_TO_DROP:
                    yield expanded_elements[i]
        return _iterator

    def _get_model_properties_for_element(self, element_name):
        properties = {}
        for regex, data in self.model['sequence'].items():
            if regex.match(element_name):
                properties = merge(properties, data['properties'])
        return properties

    def _build_bdsim_component_properties(self, element):
        parent_keys = element.parent.defs
        daughter_keys = element.defs
        non_default_args = {
            k: daughter_keys[k] for k in parent_keys if
                            k in daughter_keys and parent_keys[k] != daughter_keys[k]
        }

        bdsim_properties = {}
        for k, i in non_default_args.items():
            if k in BDSIM_ELEMENTS_ARGUMENTS:
                if k == 'knl' or k == 'ksl':
                    # The value in madx.defs is an expression
                    bdsim_properties[k] = tuple(element[k])
                elif k == 'aperture':
                    if len(element[k]) >= 1:
                        bdsim_properties['aper1'] = element[k][0]
                    if len(element[k]) >= 2:
                        bdsim_properties['aper2'] = element[k][1]
                    if len(element[k]) >= 3:
                        bdsim_properties['aper3'] = element[k][2]
                    if len(element[k]) >= 4:
                        bdsim_properties['aper4'] = element[k][3]
                else:
                    bdsim_properties[BDSIM_MAD_CONVENTION.get(k, k)] = element[k]

        return self.__class__._adjust_bdsim_component_properties(bdsim_properties)

    @staticmethod
    def _adjust_bdsim_component_properties(bdsim_properties):
        if 'apertureType' in bdsim_properties:
            bdsim_properties['apertureType'] = BDSIM_MAD_CONVENTION.get(bdsim_properties['apertureType'], bdsim_properties['apertureType'])
        if bdsim_properties.get('apertureType') == 'octagonal':
            # https://indico.cern.ch/event/379692/contributions/1804923/subcontributions/156446/attachments/757501/1039118/2105-03-18_HSS_meeting_rev.pdf
            aper3_mad = bdsim_properties['aper3']
            aper4_mad = bdsim_properties['aper4']
            bdsim_properties['aper3'] = bdsim_properties['aper2'] / _np.tan(aper4_mad)
            bdsim_properties['aper4'] = bdsim_properties['aper1'] * _np.tan(aper3_mad)

        return bdsim_properties

    def _build_bdsim_component(self, name, element):
        if element['PARENT'] == 'drift':
            bdsim_dict_arg = {'l': element['L']}
        else:
            bdsim_dict_arg = self._build_bdsim_component_properties(self.madx.elements.get(name))
        bdsim_dict_arg = merge(bdsim_dict_arg, self._get_model_properties_for_element(name))
        element_name = BDSIM_RESERVED_NAME.get(name, name)
        parent_name = BDSIM_RESERVED_NAME.get(element['PARENT'], element['PARENT'])

        if element['BASE_PARENT'] not in ELEMENTS_TO_KEEP:
            bdsim_element = pybdsim.Builder.Element(name=element_name,
                                                     category='drift',
                                                     isMultipole=False,
                                                     l=element['L'])
        else:
            if not bool(bdsim_dict_arg):
                bdsim_dict_arg = {'l': 0.0}  # Bare aliases not allowed in BDSim
            if element['LEVEL'] == 1:
                bdsim_element = pybdsim.Builder.Element(name=element_name,
                                                        category=parent_name,
                                                        isMultipole='knl' in bdsim_dict_arg.keys() or 'ksl' in bdsim_dict_arg.keys(),
                                                        **bdsim_dict_arg)
            else:
                bdsim_element = pybdsim.Builder.Element.from_element(name=element_name,
                                                           parent_element_name=parent_name,
                                                           isMultipole='knl' in bdsim_dict_arg.keys() or 'ksl' in bdsim_dict_arg.keys(),
                                                           **bdsim_dict_arg)

        return bdsim_element

    def __call__(self,
                 with_beam: bool = True,
                 with_options: bool = True,
                 with_placements: bool = True,
                 drop_inactive_thinmultipoles: bool = False,
                 ):
        bdsim_input = pybdsim.Builder.Machine()

        # Add all components
        for name, component in self.components.iterrows():
            bdsim_input.Append(component['BDSIM'], is_component=True)

        # Add elements (won't be redefined, simply added to the sequence)
        for name, component in self.components.query("IS_ELEMENT == True").sort_values(by=['ID']).iterrows():
            if drop_inactive_thinmultipoles and \
                component['BASE_PARENT'] == 'thinmultipole' and \
                component['BDSIM'].get('knl') is None and \
                component['BDSIM'].get('ksl') is None:
                continue
            bdsim_input.Append(component['BDSIM'], is_component=False)

        if with_beam:
            bdsim_beam = pybdsim.Beam.Beam(particletype=self.madx_beam['particle'],
                                           energy=self.madx_beam['energy'] + self.madx_beam['mass'],
                                           distrtype='gausstwiss')
            bdsim_beam.SetBetaX(self.madx_beam['beta'])
            bdsim_beam.SetBetaY(self.madx_beam['beta'])
            bdsim_beam.SetAlphaX(self.madx_beam['alfa'])
            bdsim_beam.SetAlphaY(self.madx_beam['alfa'])

            bdsim_beam.SetEmittanceX(self.madx_beam['ex'])
            bdsim_beam.SetEmittanceY(self.madx_beam['ey'])
            bdsim_beam.SetSigmaE(self.madx_beam['sige'])
            bdsim_beam.SetSigmaT(self.madx_beam['sigt'])
            bdsim_input.AddBeam(bdsim_beam)

        if with_options:
            bdsim_input.AddOptions(pybdsim.Options.Options(**self.model['options']))

        # if with_placements:
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
