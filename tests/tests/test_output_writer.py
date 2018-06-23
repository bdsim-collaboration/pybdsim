"""Functions for generating the output files for regression testing as
well as some utility functions which are used both here and elsewhere
for easily accessing the outputs.  The starting point here is the
input file name, e.g. "atf2-nominal-twiss-v5.2.tfs.tar.gz", which is
the name of the input found in pybdsim/tests/test_input/.   """

import pybdsim

from . import utils

INPUT_FILE_NAMES = ["atf2-nominal-twiss-v5.2.tfs.tar.gz"]

def generate_output_gmad():
    for input_file_name in INPUT_FILE_NAMES:
        print "Writing {}".format(input_file_name)
        input_path, output_path = utils.get_input_and_output_paths(
            input_file_name)
        pybdsim.Convert.MadxTfs2Gmad(input_path, output_path)


if __name__ == "__main__":
    generate_output_gmad()
