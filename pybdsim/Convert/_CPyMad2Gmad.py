import yaml
import re
import os

import pybdsim
import pandas as _pd
import numpy as _np
from pymask.madxp import Madxp


BDSIM_MAD_CONVENTION = {'apertype': 'apertureType',
                        'circle': 'circular',
                        'octagon': 'octagonal',
                        'rectangle': 'rectangular',
                        'rcollimator': 'rcol',
                        'electron': 'e-'}

BDSIM_RESERVED_NAME = {'ms': 'ms.'}

BDSIM_ELEMENTS_ARGUMENTS = ['l',
                            'k1',
                            'k2',
                            'angle',
                            'knl',
                            'apertype',
                            'aperture']

ELEMENTS_TO_KEEP = ['drift', 'sbend', 'quadrupole', 'rbend', 'sextupole', 'octupole', 'hkicker', 'vkicker', 'solenoid',
                    'rcol']


class CPyMad2Gmad:

    def __init__(self,
                 madx_instance: Madxp = None,
                 sequence_name: str = 'lhcb1',
                 from_element: str = None,
                 to_element: str = None,
                 aperture_path: str = '.',
                 aperture_file: str = ''):

        self.madx_elements = madx_instance.elements
        self.madx_sequence = self.get_madx_sequence(madx_instance.sequence[sequence_name], from_element, to_element)
        self.madx_beam = madx_instance.sequence[sequence_name].beam
        self.df_sequence = self.get_sequence()
        self.base_components = _pd.DataFrame(columns=['NAME', 'PARENT', 'LEVEL'])
        self.get_base_components()

        with open(os.path.join(aperture_path, aperture_file)) as file:
            self.aperture_file = yaml.full_load(file)

        self.magnets_properties = {}
        self.blms_properties = {}
        self.placement_properties = {}
        self.extract_yaml_data()

        self.bdsim_elements = {}
        self.bdsim_sequence = {}
        self.define_bdsim_elements()
        self.define_bdsim_sequence()

    def __call__(self, with_beam=True, with_blms=False, with_placement=False, with_individual_placement=False):
        bdsim_input = pybdsim.Builder.Machine()
        # Add elements
        for k, i in self.bdsim_elements.items():
            bdsim_input.Append(i, is_component=True)

        # Add sequence
        for k, i in self.bdsim_sequence.items():
            if 'l' in i:
                if i['l'] > 0:
                    bdsim_input.Append(i, is_component=False)
            else:
                bdsim_input.Append(i, is_component=False)

        if with_blms:
            pass
            # Add BLM
            for ref_name, blms in self.blms_properties.items():
                for blm in blms:
                    for blm_name, blm_prop in blm.items():
                        blm_prop['referenceElement'] = ref_name
                        bdsim_input.AddBLMs(blm_name + '_' + ref_name, **blm_prop)

        if with_placement:
            for ref_name, placements in self.placement_properties.items():
                for plcm in placements:
                    for plm_name, placement_prop in plcm.items():
                        placement_prop['referenceElement'] = ref_name
                        bdsim_input.AddPlacement(plm_name + '_' + ref_name, **placement_prop)

        if with_individual_placement:
            for ref_name, placements in self.aperture_file['placements'].items():
                bdsim_input.AddPlacement(ref_name, **placements)

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
        return bdsim_input

    @staticmethod
    def get_madx_sequence(madx_sequence, from_element, to_element):
        idx1 = madx_sequence.expanded_elements.index(from_element or madx_sequence.expanded_elements[0].name)
        idx2 = madx_sequence.expanded_elements.index(to_element or madx_sequence.expanded_elements[-1].name)
        return [madx_sequence.expanded_elements[i] for i in range(idx1, idx2 + 1)]

    @staticmethod
    def reset_level(e):
        e['LEVEL'] = 1 + _np.abs(e['LEVEL'] - e['LEVEL'].max())
        return e

    def get_base_components(self):
        id_component = 0  # To reset correctly the level
        for ele_seq in self.madx_sequence:
            self.get_level(ele_seq, id_component)
            id_component += 1

        self.base_components = self.base_components.groupby("ID").apply(lambda x: self.reset_level(x))
        self.base_components.drop(labels='ID', inplace=True, axis=1)
        self.base_components.drop_duplicates(inplace=True)
        self.base_components.query("PARENT != 'drift'", inplace=True)  # To check
        self.base_components.set_index("NAME", inplace=True)
        self.base_components.sort_values(by='LEVEL', inplace=True)

    def get_level(self, e, id_component, level=0):
        if e.parent.name == e.name or e.base_type.name == 'marker':
            return level

        else:
            self.fill_df(e, level, id_component)
            level += 1
            return self.get_level(e.parent, id_component, level)

    def fill_df(self, e, level, id_component):
        # if e.name not in self.base_components['NAME'].values:  # Avoid duplicate elements in dataframe
        idx = len(self.base_components)
        self.base_components.at[idx + 1, 'NAME'] = e.name
        self.base_components.at[idx + 1, 'PARENT'] = BDSIM_MAD_CONVENTION.get(e.parent.name, e.parent.name)
        self.base_components.at[idx + 1, 'BASE_PARENT'] = BDSIM_MAD_CONVENTION.get(e.base_type.name, e.base_type.name)
        self.base_components.at[idx + 1, 'LEVEL'] = level
        self.base_components.at[idx + 1, 'AT_ENTRY'] = e.at
        self.base_components.at[idx + 1, 'L'] = e.l
        self.base_components.at[idx + 1, 'ID'] = id_component

    def check_keys(self, element_name):
        # Function that check which key has been modified and return only a dictionnary with the correct keys for BDSIM.
        # If the element is a drift built on the fly, do no check because there is not in the MAD-X element.

        bdsim_non_default_args = {}
        if self.madx_elements.get(element_name):
            parent_keys = self.madx_elements[self.madx_elements.index(element_name)].parent.defs
            daughter_keys = self.madx_elements[self.madx_elements.index(element_name)].defs

            non_default_args = {k: daughter_keys[k] for k in parent_keys if
                                k in daughter_keys and parent_keys[k] != daughter_keys[k]}
            bdsim_non_default_args = {}  # Per default

            for k, i in non_default_args.items():
                if k in BDSIM_ELEMENTS_ARGUMENTS:
                    if k == 'knl' or k == 'ksl':
                        # The value in madx.defs is an expression
                        bdsim_non_default_args[k] = tuple(self.madx_elements.get(element_name)[k])  # For bdsim

                    else:
                        value = self.madx_elements[element_name].get(k)
                        value = BDSIM_MAD_CONVENTION.get(value, value)
                        bdsim_non_default_args[BDSIM_MAD_CONVENTION.get(k, k)] = value  # bdsim_mad_convention.get(i, i)

                    if k == 'aperture':
                        bdsim_non_default_args['aper1'] = self.madx_elements.get(element_name)[k][0]
                        bdsim_non_default_args['aper2'] = self.madx_elements.get(element_name)[k][1]
                        bdsim_non_default_args['aper3'] = self.madx_elements.get(element_name)[k][2]
                        bdsim_non_default_args['aper4'] = self.madx_elements.get(element_name)[k][3]
                        bdsim_non_default_args.pop('aperture')

        return bdsim_non_default_args

    def get_sequence(self) -> _pd.DataFrame:

        idx = 0
        df_sequence = _pd.DataFrame(columns=['NAME', 'PARENT', 'AT', 'L', 'AT_EXIT'])
        for e in self.madx_sequence:
            if e.parent.name != 'marker':
                df_sequence.at[idx, 'NAME'] = e.name
                df_sequence.at[idx, 'PARENT'] = BDSIM_MAD_CONVENTION.get(e.parent.name, e.parent.name)
                df_sequence.at[idx, 'BASE_PARENT'] = BDSIM_MAD_CONVENTION.get(e.base_type.name, e.base_type.name)
                df_sequence.at[idx, 'AT'] = e.at
                df_sequence.at[idx, 'L'] = e.l
                df_sequence.at[idx, 'AT_EXIT'] = e.at + e.l
                idx += 1
        df_sequence.set_index("NAME", inplace=True)
        df_sequence.query("L > 0", inplace=True)
        return df_sequence

    def define_bdsim_elements(self):

        for name, i in self.base_components.iterrows():
            bdsim_dict_arg = self.check_keys(name)
            if name in self.magnets_properties.keys():
                bdsim_dict_arg = {**bdsim_dict_arg, **self.magnets_properties[name]}  # z = x | y  # NOTE: 3.9+ ONLY

            ismultipole = False

            element_name = BDSIM_RESERVED_NAME.get(name, name)
            parent_name = BDSIM_RESERVED_NAME.get(i['PARENT'], i['PARENT'])

            if 'octagonal' in bdsim_dict_arg.values():  # Change fo bdsim
                # https://indico.cern.ch/event/379692/contributions/1804923/subcontributions/156446/attachments/757501/1039118/2105-03-18_HSS_meeting_rev.pdf
                aper3_mad = bdsim_dict_arg['aper3']
                aper4_mad = bdsim_dict_arg['aper4']
                bdsim_dict_arg['aper3'] = bdsim_dict_arg['aper2'] / _np.tan(aper4_mad)
                bdsim_dict_arg['aper4'] = bdsim_dict_arg['aper1'] * _np.tan(aper3_mad)

            if 'knl' in bdsim_dict_arg.keys():  # It is a multipole
                ismultipole = True

            if i['BASE_PARENT'] not in ELEMENTS_TO_KEEP:

                args_drift = {'l': i['L']}
                ele = pybdsim.Builder.Element(name=element_name,
                                              category='drift',
                                              isMultipole=False, **args_drift)  # Give a dict with non default args.
            else:
                if i['LEVEL'] == 1:
                    # Give a dict with non default args.
                    if not bool(bdsim_dict_arg):
                        bdsim_dict_arg = {'l': 0.0}
                    ele = pybdsim.Builder.Element(name=element_name,
                                                  category=parent_name,
                                                  isMultipole=ismultipole,
                                                  **bdsim_dict_arg)  # Give a dict with non default args.

                else:
                    ele = pybdsim.Builder.Element.from_element(name=element_name,
                                                               element=self.bdsim_elements[parent_name],
                                                               isMultipole=ismultipole, **bdsim_dict_arg)

            if element_name not in self.bdsim_elements.keys():
                self.bdsim_elements[element_name] = ele

    def extract_yaml_data(self):
        for name, i in self.base_components.iterrows():
            for item, val in self.aperture_file['sequence'].items():
                pattern = re.compile(item)
                if pattern.match(name):
                    self.magnets_properties[name] = val['properties']
                    if "blms" in val.keys():
                        self.blms_properties[name] = val['blms']
                    if "placement" in val.keys():
                        self.placement_properties[name] = val['placement']

    def define_bdsim_sequence(self):
        for name, i in self.df_sequence.iterrows():
            bdsim_dict_arg = self.check_keys(name)
            if name in self.magnets_properties.keys():
                bdsim_dict_arg = {**bdsim_dict_arg, **self.magnets_properties[name]}

            parent_name = BDSIM_RESERVED_NAME.get(i['PARENT'], i['PARENT'])
            element_name = BDSIM_RESERVED_NAME.get(name, name)

            if 'octagonal' in bdsim_dict_arg.values():  # Change fo bdsim
                # https://indico.cern.ch/event/379692/contributions/1804923/subcontributions/156446/attachments/757501/1039118/2105-03-18_HSS_meeting_rev.pdf
                aper3_mad = bdsim_dict_arg['aper3']
                aper4_mad = bdsim_dict_arg['aper4']
                bdsim_dict_arg['aper3'] = bdsim_dict_arg['aper2'] / _np.tan(aper4_mad)
                bdsim_dict_arg['aper4'] = bdsim_dict_arg['aper1'] * _np.tan(aper3_mad)

            if i['BASE_PARENT'] not in ELEMENTS_TO_KEEP:
                args_drift = {'l': i['L']}
                ele = pybdsim.Builder.Element(name=element_name,
                                              category="drift",
                                              **args_drift)

            else:
                if parent_name in self.bdsim_elements.keys():
                    ele = pybdsim.Builder.Element.from_element(name=element_name,
                                                               element=self.bdsim_elements[parent_name],
                                                               **bdsim_dict_arg)
                else:
                    if parent_name == 'drift':
                        bdsim_dict_arg = {'l': i['L']}
                    ele = pybdsim.Builder.Element(name=element_name,
                                                  category=parent_name,
                                                  **bdsim_dict_arg)
            self.bdsim_sequence[element_name] = ele
