import os.path
from itertools import islice

import pytest
import pybdsim
import pymadx

from . import pybdsim_test_utils as utils

# TODO:
# TEST with aperturedict of pymadx.Data.Aperture.
# TEST with collimator dict (atf2 has no collimators).
# TEST with usemadxaperture (atf2 has no aperinfo with it).
# TEST coupled combinations of arguments, whatever they may be.

PATH_TO_TEST_INPUT = "{}/../test_input/".format(os.path.dirname(__file__))
PATH_TO_TEST_OUTPUT = "{}/../test_output/".format(os.path.dirname(__file__))

GMAD_SUFFIXES = ["",
                 "_beam",
                 "_components",
                 "_options",
                 "_sequence",
#                 "_bias",
#                 "_samplers"
]


@pytest.fixture
def atf2_input():
    return "{}/atf2-nominal-twiss-v5.2.tfs.tar.gz".format(
        PATH_TO_TEST_INPUT)

@pytest.fixture
def model_model_input(tmppath):
    tfs = "{}/model-model.tfs.gz".format(PATH_TO_TEST_INPUT)
    aper = pymadx.Data.Aperture("{}/model-model-aper.tfs.gz".format(PATH_TO_TEST_INPUT))
    aper = aper.RemoveBelowValue(0.005)
    coll = pybdsim.Data.Load("{}/model-model-collsettings.dat".format(PATH_TO_TEST_INPUT))
    return {"tfs": tfs, "outputfilename": tmppath, "aperturedict": aper, "collimatordict": coll}

@pytest.fixture
def tmppath(tmpdir):
    """A temporary file path"""
    return str(tmpdir.mkdir("testdir").join("model"))

@pytest.fixture(params=["one", "list"]) # bias or list of biases..
def biases(request):
    """Biases can be either a single XSecBias instance or a list
    thereof.  This fixture provides both."""
    bias1 = pybdsim.XSecBias.XSecBias("mydecay1", "gamma", "decay", "1e5", "2")
    bias2 = pybdsim.XSecBias.XSecBias("mydecay2", "proton", "decay", "1e5", "2")
    if request.param == "bias":
        return bias1
    if request.param == "list":
        return [bias1, bias2]

@pytest.fixture
def gmad_comparator():
    def f(first, second):
        """Paths to two sets of gmad files"""
        for suffix in GMAD_SUFFIXES:
            print("comparing '"+suffix+"'")
            new_gmad = "{}{}.gmad".format(first, suffix)
            old_gmad = "{}{}.gmad".format(second, suffix)
            # Skip the first 3 lines which are just the header
            with open(new_gmad, "r") as new, open(old_gmad, "r") as old:
                for new_line, old_line in zip(islice(new, 3, None),
                                              islice(old, 3, None)):
                    assert new_line == old_line
    return f

@pytest.mark.sanity
def test_atf2_conversion_default(atf2_input, tmppath):
    """Default parameters should not fail."""
    pybdsim.Convert.MadxTfs2Gmad(atf2_input, tmppath)

@pytest.mark.sanity
@pytest.mark.parametrize(('start', 'stop', 'step'),
                         [(10, 20, 2),
                          ("KEX1A", "L229", 1),
                          ("KEX1A", 40, 1),
                          (10, "L229", 1)])
def test_atf2_conversion_with_start_stop_and_stepsize(atf2_input, tmppath,
                                                      start, stop, step):
    """Given the ATF2 model and a start, stop and step:  do not crash."""
    pybdsim.Convert.MadxTfs2Gmad(atf2_input, tmppath,
                                 startname=start,
                                 stopname=stop,
                                 stepsize=step)
@pytest.mark.sanity
@pytest.mark.parametrize('ignorezerolengthitems', [True, False])
def test_atf2_conversion_with_ignorezerolengthitems(atf2_input, tmppath,
                                                    ignorezerolengthitems):
    """Given the ATF2 model and valid args for
    ignorezerolengthitems:  do not crash."""
    pybdsim.Convert.MadxTfs2Gmad(atf2_input, tmppath,
                                 ignorezerolengthitems=ignorezerolengthitems)

@pytest.mark.sanity
@pytest.mark.parametrize('flipmagnets', [True, False, None])
def test_atf2_conversion_with_flipmagnets(atf2_input, tmppath, flipmagnets):
    """Given the ATF2 model and the set of allowed `flipmagnets` arguments:
    do not crash."""
    pybdsim.Convert.MadxTfs2Gmad(atf2_input, tmppath, flipmagnets=flipmagnets)

@pytest.mark.sanity
@pytest.mark.parametrize('linear', [True, False])
def test_atf2_conversion_with_linear(atf2_input, tmppath, linear):
    """Given the ATF2 model and the set of allowed `linear` arguments:
    do not crash."""
    pybdsim.Convert.MadxTfs2Gmad(atf2_input, tmppath, linear=linear)

@pytest.mark.sanity
@pytest.mark.parametrize('samplers', ['all', None, ["KEX1A", "KEX1B"]])
def test_atf2_conversion_with_samplers(atf2_input, tmppath, samplers):
    """Given the ATF2 model and the set of allowed `samplers` arguments:
    do not crash."""
    pybdsim.Convert.MadxTfs2Gmad(atf2_input, tmppath, samplers=samplers)


@pytest.mark.sanity
def test_atf2_conversion_with_aperturedict(atf2_input, tmppath):
    # should also test with a pymadx.Data.Aperture instance.
    pybdsim.Convert.MadxTfs2Gmad(atf2_input, tmppath,
                                 aperturedict={
                                     "KEX1A":
                                     {"APERTYPE": "circular",
                                      "APER_1": 1,
                                      "APER_2": 0,
                                      "APER_3": 0,
                                      "APER_4": 0}})

@pytest.mark.sanity
def test_atf2_conversion_with_optionsDict(atf2_input, tmppath):
    pybdsim.Convert.MadxTfs2Gmad(atf2_input, tmppath, optionsdict={"stopSecondaries": "1"})

@pytest.mark.sanity
def test_atf2_conversion_with_userdict(atf2_input, tmppath):
    pybdsim.Convert.MadxTfs2Gmad(atf2_input, tmppath, userdict={"KEX1A": {"biasVacuum": "mybias"}})

@pytest.mark.sanity
def test_atf2_conversion_with_allelementdict(atf2_input, tmppath):
    """Don't crash for valid arguments of allelementdict"""
    pybdsim.Convert.MadxTfs2Gmad(atf2_input, tmppath, allelementdict={"biasVacuum": "mybias"})

@pytest.mark.sanity
def test_atf2_conversion_with_defaultAperture(atf2_input, tmppath):
    """Don't crash for valid arguments of defaultAperture"""
    pybdsim.Convert.MadxTfs2Gmad(atf2_input, tmppath, defaultAperture="rectellipse")

@pytest.mark.sanity
def test_atf2_conversion_with_biases(atf2_input, tmppath, biases):
    pybdsim.Convert.MadxTfs2Gmad(atf2_input, tmppath, biases=biases)

@pytest.mark.parametrize('beam', [True, False])
def test_atf2_conversion_with_beam(atf2_input, tmppath, beam):
    pybdsim.Convert.MadxTfs2Gmad(atf2_input, tmppath, beam=beam)

@pytest.mark.parametrize('overwrite', [True, False])
@pytest.mark.sanity
def test_atf2_conversion_with_overwrite(atf2_input, tmppath, overwrite):
    pybdsim.Convert.MadxTfs2Gmad(atf2_input, tmppath, overwrite=overwrite)

@pytest.mark.parametrize('allNamesUnique', [True, False])
@pytest.mark.sanity
def test_atf2_conversion_with_allNamesUnique(atf2_input, tmppath, allNamesUnique):
    pybdsim.Convert.MadxTfs2Gmad(atf2_input, tmppath, allNamesUnique=allNamesUnique)

@pytest.mark.parametrize('verbose', [True, False])
@pytest.mark.sanity
def test_atf2_conversion_with_verbose(atf2_input, tmppath, verbose):
    pybdsim.Convert.MadxTfs2Gmad(atf2_input, tmppath, verbose=verbose)

@pytest.mark.sanity
def test_atf2_conversion_with_beamParmsDict(atf2_input, tmppath):
    beam = pybdsim.Convert.MadxTfs2GmadBeam(pymadx.Data.Tfs(atf2_input),
                                            startname="KEX1A")
    pybdsim.Convert.MadxTfs2Gmad(atf2_input, tmppath, beam=beam)

@pytest.mark.regression
def test_atf2_default_conversion_with_gmad_regression(atf2_input,
                                                      gmad_comparator,
                                                      tmppath):
    pybdsim.Convert.MadxTfs2Gmad(atf2_input, tmppath)
    output_path = utils.get_output_path("atf2-nominal-twiss-v5.2.tfs.tar.gz")
    gmad_comparator(output_path, tmppath)

@pytest.mark.regression
def test_model_model_conversion_with_gmad_regression(model_model_input,
                                                     gmad_comparator):
    pybdsim.Convert.MadxTfs2Gmad(**model_model_input)
    output_path = utils.get_output_path("model-model.tfs.gz")
    gmad_comparator(output_path, model_model_input['outputfilename'])
