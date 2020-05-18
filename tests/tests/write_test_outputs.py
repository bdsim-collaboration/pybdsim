"""Functions for generating the output files for regression testing as
well as some utility functions which are used both here and elsewhere
for easily accessing the outputs.  The starting point here is the
input file name, e.g. "atf2-nominal-twiss-v5.2.tfs.tar.gz", which is
the name of the input found in pybdsim/tests/test_input/.   """

import pybdsim
import pymadx

from . import pybdsim_test_utils as utils

def generate_atf2_gmad():
    input_file_name = "atf2-nominal-twiss-v5.2.tfs.tar.gz"
    input_path, output_path = utils.get_input_and_output_paths(
        input_file_name)
    pybdsim.Convert.MadxTfs2Gmad(input_path, output_path)

def generate_model_model_gmad():
    input_file_name = "model-model.tfs.gz"
    input_path, output_path = utils.get_input_and_output_paths(
        input_file_name)
    # Load the collimator settings
    collsettings_path = utils.get_input_path("model-model-collsettings.dat")
    coll_settings =  pybdsim.Data.Load(collsettings_path)
    # Load the aperture information
    aper_path = utils.get_input_path("model-model-aper.tfs.gz")
    aper = pymadx.Data.Aperture(aper_path)
    aper = aper.RemoveBelowValue(0.005)

    pybdsim.Convert.MadxTfs2Gmad(input_path, output_path,
                                 aperturedict=aper,
                                 collimatordict=coll_settings)

if __name__ == "__main__":
    generate_atf2_gmad()
    generate_model_model_gmad()
