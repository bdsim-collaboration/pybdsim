"""
Optical calculations. Work in progress.

"""

import itertools as _itertools
from logging import warning as _warning
import warnings as _warnings
import pandas as _pd
import numpy as _np
from typing import Optional as _Optional
from typing import List as _List
from typing import Dict as _Dict
from typing import Tuple as _Tuple

from pint import UnitRegistry as _UnitRegistry

_ureg = _UnitRegistry(on_redefinition="ignore")
_ureg.define('electronvolt = e * volt = eV')


def _get_matrix_elements_block(m: _pd.DataFrame, twiss: _Dict, block: int = 1) -> _Tuple:
    """Extract parameters from the DataFrame."""
    p = 1 if block == 1 else 3
    v = 1 if block == 1 else 2
    r11: _pd.Series = m[f"R{p}{p}"]
    r12: _pd.Series = m[f"R{p}{p + 1}"]
    r21: _pd.Series = m[f"R{p + 1}{p}"]
    r22: _pd.Series = m[f"R{p + 1}{p + 1}"]
    alpha: float = twiss[f"ALPHA{v}{v}"]
    beta: float = twiss[f"BETA{v}{v}"]
    gamma: float = twiss[f"GAMMA{v}{v}"]

    return r11, r12, r21, r22, alpha, beta, gamma

class TwissException(Exception):
    """Exception raised for errors in the Twiss module."""

    def __init__(self, m):
        self.message = m

class Twiss:
    def __init__(self,
                 samplers_data: _Dict[str, _pd.DataFrame] = None,
                 first_sampler: str = None,
                 last_sampler: str = None
                 ):
        """
        Args:
            samplers_data: Dictionary of Dataframe that contains all the samplers. {sampler's name: dataFrame}.
                           The following coordinates must be in the DataFrame and in this order
                           ['x', 'xp', 'y', 'yp', 'S', 'p']
            first_sampler: First element where to compute the optics
            last_sampler: Last element where to compute the optics

        Returns:

        """
        samplers_name = list(samplers_data)
        if first_sampler is None:
            first_sampler = samplers_name[0]
        if last_sampler is None:
            last_sampler = samplers_name[-1]
        if first_sampler not in samplers_name:
            raise TwissException(f"{first_sampler} not in samplers_data")
        if last_sampler not in samplers_name:
            raise TwissException(f"{last_sampler} not in samplers_data")
        self.samplers_data = dict(_itertools.islice(samplers_data.items(),
                                                    samplers_name.index(first_sampler),
                                                    samplers_name.index(last_sampler)+1))

    def __call__(self,
                 twiss_init: _Optional[_Dict] = None,
                 with_phase_unrolling: bool = True,
                 offsets: _List = None, # -> Must be computed on the fly
                 ) -> _pd.DataFrame:
        """
        Uses a step-by-step transfer matrix to compute the Twiss parameters (uncoupled). The phase advance and the
        determinants of the jacobians are computed as well.

        Args:
            matrix: the input step-by-step transfer matrix

        Returns:
            the same DataFrame as the input, but with added columns for the computed quantities.
        """
        matrix = self.compute_matrix_for_twiss(offsets)

        if twiss_init is None:
            twiss_init = self.compute_periodic_twiss(matrix)

        matrix['BETA11'] = self.compute_beta_from_matrix(matrix, twiss_init)
        matrix['BETA22'] = self.compute_beta_from_matrix(matrix, twiss_init, plane=2)
        matrix['ALPHA11'] = self.compute_alpha_from_matrix(matrix, twiss_init)
        matrix['ALPHA22'] = self.compute_alpha_from_matrix(matrix, twiss_init, plane=2)
        matrix['GAMMA11'] = self.compute_gamma_from_matrix(matrix, twiss_init)
        matrix['GAMMA22'] = self.compute_gamma_from_matrix(matrix, twiss_init, plane=2)
        matrix['MU1'] = self.compute_mu_from_matrix(matrix, twiss_init)
        matrix['MU2'] = self.compute_mu_from_matrix(matrix, twiss_init, plane=2)
        matrix['DET1'] = self.compute_jacobian_from_matrix(matrix, twiss_init)
        matrix['DET2'] = self.compute_jacobian_from_matrix(matrix, twiss_init, plane=2)
        matrix['DISP1'] = self.compute_dispersion_from_matrix(matrix, twiss_init)
        matrix['DISP2'] = self.compute_dispersion_prime_from_matrix(matrix, twiss_init)
        matrix['DISP3'] = self.compute_dispersion_from_matrix(matrix, twiss_init, plane=2)
        matrix['DISP4'] = self.compute_dispersion_prime_from_matrix(matrix, twiss_init, plane=2)

        def phase_unrolling(phi):
            """TODO"""
            if phi[0] < 0:
                phi[0] += 2 * _np.pi
            for i in range(1, phi.shape[0]):
                if phi[i] < 0:
                    phi[i] += 2 * _np.pi
                if phi[i - 1] - phi[i] > 0.5:
                    phi[i:] += 2 * _np.pi
            return phi

        try:
            from numba import njit
            phase_unrolling = njit(phase_unrolling)
        except ModuleNotFoundError:
            pass

        if with_phase_unrolling:
            matrix['MU1U'] = phase_unrolling(matrix['MU1'].values)
            matrix['MU2U'] = phase_unrolling(matrix['MU2'].values)

        return matrix


    def compute_matrix_for_twiss(self, offsets) -> _pd.DataFrame:

        normalization = 2 * offsets
        step_by_step_matrix = _pd.DataFrame()
        for sampler_name, data_sampler in self.samplers_data.items():
            if data_sampler.empty or len(data_sampler) != 11:
                raise TwissException(f"Sampler {sampler_name} is empty or particles are missing. "
                                     f"Size of sampler {sampler_name} = {len(data_sampler)}")

            p0 = data_sampler['p'][0]
            data_sampler['dpp'] = (data_sampler['p'] - p0) / p0

            output_coordinates = data_sampler.drop(columns=['p', 'S'])
            m = output_coordinates.values
            matrix = {
                f'R{j + 1}{i + 1}': ((m[i + 1, j] - m[i + 1 + 5, j]) / normalization[i]) + m[0, j]
                for j in range(0, 5)
                for i in range(0, 5)
            }

            matrix['S'] = data_sampler.iloc[0]['S']
            matrix['X0'] = data_sampler.iloc[0]['x']
            matrix['XP0'] = data_sampler.iloc[0]['xp']
            matrix['Y0'] = data_sampler.iloc[0]['y']
            matrix['YP0'] = data_sampler.iloc[0]['yp']
            step_by_step_matrix = step_by_step_matrix.append(_pd.DataFrame.from_dict(matrix,
                                                                                     orient='index',
                                                                                     columns=[sampler_name]).T)
        return step_by_step_matrix

    @staticmethod
    def compute_alpha_from_matrix(m: _pd.DataFrame, twiss: _Dict, plane: int = 1) -> _pd.Series:
        """
        Computes the Twiss alpha values at every step of the input step-by-step transfer matrix.

        Args:
            m: the step-by-step transfer matrix for which the alpha values should be computed
            twiss: the initial Twiss values
            plane: an integer representing the block (1 or 2)

        Returns:
            a Pandas Series with the alpha values computed at all steps of the input step-by-step transfer matrix
        """
        r11, r12, r21, r22, alpha, beta, gamma = _get_matrix_elements_block(m, twiss, plane)
        return -r11 * r21 * beta + (r11 * r22 + r12 * r21) * alpha - r12 * r22 * gamma

    @staticmethod
    def compute_beta_from_matrix(m: _pd.DataFrame, twiss: _Dict, plane: int = 1,
                                 strict: bool = False) -> _pd.Series:
        """
        Computes the Twiss beta values at every step of the input step-by-step transfer matrix.

        Args:
            m: the step-by-step transfer matrix for which the beta values should be computed
            twiss: the initial Twiss values
            plane: an integer representing the block (1 or 2)
            strict: flag to activate the strict mode: checks and ensures that all computed beta are positive

        Returns:
            a Pandas Series with the beta values computed at all steps of the input step-by-step transfer matrix
        """
        r11, r12, r21, r22, alpha, beta, gamma = _get_matrix_elements_block(m, twiss, plane)
        _ = r11 ** 2 * beta - 2.0 * r11 * r12 * alpha + r12 ** 2 * gamma
        if strict:
            assert (_ > 0).all(), "Not all computed beta are positive."
        return _

    @staticmethod
    def compute_gamma_from_matrix(m: _pd.DataFrame, twiss: _Dict, plane: int = 1) -> _pd.Series:
        """
        Computes the Twiss gamma values at every step of the input step-by-step transfer matrix.

        Args:
            m: the step-by-step transfer matrix for which the beta values should be computed
            twiss: the initial Twiss values
            plane: an integer representing the block (1 or 2)

        Returns:
            a Pandas Series with the gamma values computed at all steps of the input step-by-step transfer matrix
        """
        r11, r12, r21, r22, alpha, beta, gamma = _get_matrix_elements_block(m, twiss, plane)
        return r21 ** 2 * beta - 2.0 * r21 * r22 * alpha + r22 ** 2 * gamma

    @staticmethod
    def compute_mu_from_matrix(m: _pd.DataFrame, twiss: _Dict, plane: int = 1) -> _pd.Series:
        """
        Computes the phase advance values at every step of the input step-by-step transfer matrix.

        Args:
            m: the step-by-step transfer matrix for which the beta values should be computed
            twiss: the initial Twiss values
            plane: an integer representing the block (1 or 2)

        Returns:
            a Pandas Series with the phase advance computed at all steps of the input step-by-step transfer matrix
        """
        r11, r12, r21, r22, alpha, beta, gamma = _get_matrix_elements_block(m, twiss, plane)
        return _np.arctan2(r12.astype(_np.float64), (r11 * beta - r12 * alpha).astype(_np.float64))

    @staticmethod
    def compute_jacobian_from_matrix(m: _pd.DataFrame, twiss: _Dict, plane: int = 1) -> _pd.Series:
        """
        Computes the jacobian of the 2x2 transfer matrix (useful to verify the simplecticity).

        Args:
            m: the step-by-step transfer matrix for which the jacobians should be computed
            twiss: initial values for the Twiss parameters
            plane: an integer representing the block (1 or 2)

        Returns:
            a Pandas Series with the jacobian computed at all steps of the input step-by-step transfer matrix
        """
        r11, r12, r21, r22, alpha, beta, gamma = _get_matrix_elements_block(m, twiss, plane)
        return r11 * r22 - r12 * r21

    @staticmethod
    def compute_dispersion_from_matrix(m: _pd.DataFrame, twiss: _Dict, plane: int = 1) -> _pd.Series:
        """
        Computes the dispersion function at every step of the input step-by-step transfer matrix.

        Args:
            m: the step-by-step transfer matrix for which the dispersion function should be computed
            twiss: initial values for the Twiss parameters
            plane: an integer representing the block (1 or 2)

        Returns:
            a Pandas Series with the dispersion function computed at all steps of the input step-by-step transfer matrix

        """
        p = 1 if plane == 1 else 3
        if p == 1:
            d0 = twiss['DISP1']
            dp0 = twiss['DISP2']
        else:
            d0 = twiss['DISP3']
            dp0 = twiss['DISP4']
        r11: _pd.Series = m[f"R{p}{p}"]
        r12: _pd.Series = m[f"R{p}{p + 1}"]
        r15: _pd.Series = m[f"R{p}5"]
        return d0 * r11 + dp0 * r12 + r15

    @staticmethod
    def compute_dispersion_prime_from_matrix(m: _pd.DataFrame, twiss: _Dict, plane: int = 1) -> _pd.Series:
        """
        Computes the dispersion prime function at every step of the input step-by-step transfer matrix.

        Args:
            m: the step-by-step transfer matrix for which the dispersion prime function should be computed
            twiss: initial values for the Twiss parameters
            plane: an integer representing the block (1 or 2)

        Returns:
            a Pandas Series with the dispersion prime function computed at all steps of the input step-by-step transfer
            matrix

        Example:

        """
        p = 1 if plane == 1 else 3
        if p == 1:
            d0 = twiss['DISP1']
            dp0 = twiss['DISP2']
        else:
            d0 = twiss['DISP3']
            dp0 = twiss['DISP4']
        r21: _pd.Series = m[f"R{p + 1}{p}"]
        r22: _pd.Series = m[f"R{p + 1}{p + 1}"]
        r25: _pd.Series = m[f"R{p + 1}5"]
        return d0 * r21 + dp0 * r22 + r25

    @staticmethod
    def compute_periodic_twiss(matrix: _pd.DataFrame) -> _Dict:
        """
        Compute twiss parameters from a transfer matrix which is assumed to be a periodic transfer matrix.

        Args:
            matrix: the (periodic) transfer matrix

        Returns:
            a Series object with the values of the periodic Twiss parameters.
        """
        twiss = dict({
            'CMU1': (matrix['R11'] + matrix['R22']) / 2.0,
            'CMU2': (matrix['R33'] + matrix['R44']) / 2.0,
        })
        if twiss['CMU1'] < -1.0 or twiss['CMU1'] > 1.0:
            _warning(f"Horizontal motion is unstable; proceed with caution (cos(mu) = {twiss['CMU1']}).")
        with _warnings.catch_warnings():
            _warnings.simplefilter("ignore")
            twiss['MU1'] = _np.arccos(twiss['CMU1'])
        if twiss['CMU2'] < -1.0 or twiss['CMU2'] > 1.0:
            _warning(f"Vertical motion is unstable; proceed with caution (cos(mu) = {twiss['CMU2']}).")
        with _warnings.catch_warnings():
            _warnings.simplefilter("ignore")
            twiss['MU2'] = _np.arccos(twiss['CMU2'])
        twiss['BETA11'] = matrix['R12'] / _np.sin(twiss['MU1']) * _ureg.m
        if twiss['BETA11'] < 0.0:
            twiss['BETA11'] *= -1
            twiss['MU1'] *= -1
        twiss['BETA22'] = matrix['R34'] / _np.sin(twiss['MU2']) * _ureg.m
        if twiss['BETA22'] < 0.0:
            twiss['BETA22'] *= -1
            twiss['MU2'] *= -1
        twiss['ALPHA11'] = (matrix['R11'] - matrix['R22']) / (2.0 * _np.sin(twiss['MU1']))
        twiss['ALPHA22'] = (matrix['R33'] - matrix['R44']) / (2.0 * _np.sin(twiss['MU2']))
        twiss['GAMMA11'] = -matrix['R21'] / _np.sin(twiss['MU1']) * _ureg.m ** -1
        twiss['GAMMA22'] = -matrix['R43'] / _np.sin(twiss['MU2']) * _ureg.m ** -1
        m44 = matrix[['R11', 'R12', 'R13', 'R14',
                 'R21', 'R22', 'R23', 'R24',
                 'R31', 'R32', 'R33', 'R34',
                 'R41', 'R42', 'R43', 'R44']].apply(float).values.reshape(4, 4)
        r6 = matrix[['R15', 'R25', 'R35', 'R45']].apply(float).values.reshape(4, 1)
        disp = _np.dot(_np.linalg.inv(_np.identity(4) - m44), r6).reshape(4)
        twiss['DY'] = disp[0] * _ureg.m
        twiss['DYP'] = disp[1] * _ureg.radians
        twiss['DZ'] = disp[2] * _ureg.m
        twiss['DZP'] = disp[3] * _ureg.radians
        twiss['DISP1'] = twiss['DY']
        twiss['DISP2'] = twiss['DYP']
        twiss['DISP3'] = twiss['DZ']
        twiss['DISP4'] = twiss['DZP']

        return twiss
