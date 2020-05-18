import os
import sys

PATH_TO_TEST_INPUT = "{}/../test_input/".format(os.path.dirname(os.path.abspath(__file__)))
# we have different numerical precision for python3 vs 2, so 2 sets of test files
if sys.version_info[0] == 3:
    PATH_TO_TEST_OUTPUT = "{}/../test_output/".format(os.path.dirname(os.path.abspath(__file__)))
else:
    PATH_TO_TEST_OUTPUT = "{}/../test_output2/".format(os.path.dirname(os.path.abspath(__file__)))

def make_model_name(model_file_name):
    return model_file_name.split('.tfs')[0]

def get_input_and_output_paths(input_file_name):
    """input file name = e.g. 'atf2-nominal-twiss-v5.2.tfs.tar.gz', which
    must be placed in the test_input directory."""
    return get_input_path(input_file_name), get_output_path(input_file_name)

def get_input_path(input_file_name):
    input_path = "{}/{}".format(PATH_TO_TEST_INPUT, input_file_name)
    return input_path

def get_output_path(input_file_name):
    # Use the name of the input file without its tfs... extensions to
    # make the output directory.
    model_name = make_model_name(input_file_name)
    output_path = "{0}/{1}/model".format(PATH_TO_TEST_OUTPUT, model_name)
    return output_path

def _make_output_dir(output_path):
    try:
        os.mkdir("{}/{}".format(os.path.dirname(output_path)))
    except OSError: # then the directory already exists.
        pass
