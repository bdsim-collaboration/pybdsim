import os.path
from itertools import islice, izip

import pytest

import pybdsim
import pymadx

from . import utils

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
def atf2():
    return "{}/atf2-nominal-twiss-v5.2.tfs.tar.gz".format(
        PATH_TO_TEST_INPUT)

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

@pytest.mark.sanity
def test_atf2_conversion_default(atf2, tmppath):
    """Default parameters should not fail."""
    pybdsim.Convert.MadxTfs2Gmad(atf2, tmppath)

@pytest.mark.sanity
@pytest.mark.parametrize(('start', 'stop', 'step'),
                         [(10, 20, 2),
                          ("KEX1A", "L229", 1),
                          ("KEX1A", 40, 1),
                          (10, "L229", 1)])
def test_atf2_conversion_with_start_stop_and_stepsize(atf2, tmppath,
                                                      start, stop, step):
    """Given the ATF2 model and a start, stop and step:  do not crash."""
    pybdsim.Convert.MadxTfs2Gmad(atf2, tmppath,
                                 startname=start,
                                 stopname=stop,
                                 stepsize=step)
@pytest.mark.sanity
@pytest.mark.parametrize('ignorezerolengthitems', [True, False])
def test_atf2_conversion_with_ignorezerolengthitems(atf2, tmppath,
                                                    ignorezerolengthitems):
    """Given the ATF2 model and valid args for
    ignorezerolengthitems:  do not crash."""
    pybdsim.Convert.MadxTfs2Gmad(atf2, tmppath,
                                 ignorezerolengthitems=ignorezerolengthitems)

@pytest.mark.sanity
@pytest.mark.parametrize('flipmagnets', [True, False, None])
def test_atf2_conversion_with_flipmagnets(atf2, tmppath, flipmagnets):
    """Given the ATF2 model and the set of allowed `flipmagnets` arguments:
    do not crash."""
    pybdsim.Convert.MadxTfs2Gmad(atf2, tmppath, flipmagnets=flipmagnets)

@pytest.mark.sanity
@pytest.mark.parametrize('linear', [True, False])
def test_atf2_conversion_with_linear(atf2, tmppath, linear):
    """Given the ATF2 model and the set of allowed `linear` arguments:
    do not crash."""
    pybdsim.Convert.MadxTfs2Gmad(atf2, tmppath, linear=linear)

@pytest.mark.sanity
@pytest.mark.parametrize('samplers', ['all', None, ["KEX1A", "KEX1B"]])
def test_atf2_conversion_with_samplers(atf2, tmppath, samplers):
    """Given the ATF2 model and the set of allowed `samplers` arguments:
    do not crash."""
    pybdsim.Convert.MadxTfs2Gmad(atf2, tmppath, samplers=samplers)


@pytest.mark.sanity
def test_atf2_conversion_with_aperturedict(atf2, tmppath):
    # should also test with a pymadx.Data.Aperture instance.
    pybdsim.Convert.MadxTfs2Gmad(atf2, tmppath,
                                 aperturedict={
                                     "KEX1A":
                                     {"APERTYPE": "circular",
                                      "APER_1": 1,
                                      "APER_2": 0,
                                      "APER_3": 0,
                                      "APER_4": 0}})
@pytest.mark.sanity
def test_atf2_conversion_with_optionsDict(atf2, tmppath):
    pybdsim.Convert.MadxTfs2Gmad(atf2, tmppath,
                                 optionsDict={"stopSecondaries": "1"})

@pytest.mark.sanity
def test_atf2_conversion_with_userdict(atf2, tmppath):
    pybdsim.Convert.MadxTfs2Gmad(atf2, tmppath,
                                 userdict={"KEX1A": {"biasVacuum": "mybias"}})

@pytest.mark.sanity
def test_atf2_conversion_with_allelementdict(atf2, tmppath):
    """Don't crash for valid arguments of allelementdict"""
    pybdsim.Convert.MadxTfs2Gmad(atf2, tmppath,
                                 allelementdict={"biasVacuum": "mybias"})

@pytest.mark.sanity
def test_atf2_conversion_with_defaultAperture(atf2, tmppath):
    """Don't crash for valid arguments of defaultAperture"""
    pybdsim.Convert.MadxTfs2Gmad(atf2, tmppath,
                                 defaultAperture="rectellipse")

@pytest.mark.sanity
def test_atf2_conversion_with_biases(atf2, tmppath, biases):
    pybdsim.Convert.MadxTfs2Gmad(atf2, tmppath, biases=biases)

@pytest.mark.parametrize('beam', [True, False])
def test_atf2_conversion_with_beam(atf2, tmppath, beam):
    pybdsim.Convert.MadxTfs2Gmad(atf2, tmppath, beam=beam)

@pytest.mark.parametrize('overwrite', [True, False])
@pytest.mark.sanity
def test_atf2_conversion_with_overwrite(atf2, tmppath, overwrite):
    pybdsim.Convert.MadxTfs2Gmad(atf2, tmppath, overwrite=overwrite)

@pytest.mark.parametrize('allNamesUnique', [True, False])
@pytest.mark.sanity
def test_atf2_conversion_with_allNamesUnique(atf2, tmppath, allNamesUnique):
    pybdsim.Convert.MadxTfs2Gmad(atf2, tmppath, allNamesUnique=allNamesUnique)

@pytest.mark.parametrize('verbose', [True, False])
@pytest.mark.sanity
def test_atf2_conversion_with_verbose(atf2, tmppath, verbose):
    pybdsim.Convert.MadxTfs2Gmad(atf2, tmppath, verbose=verbose)

@pytest.mark.sanity
def test_atf2_conversion_with_beamParmsDict(atf2, tmppath):
    beam = pybdsim.Convert.MadxTfs2GmadBeam(pymadx.Data.Tfs(atf2),
                                            startname="KEX1A")
    pybdsim.Convert.MadxTfs2Gmad(atf2, tmppath, beam=beam)

@pytest.mark.regression
def test_atf2_default_conversion_with_gmad_regression(atf2, tmppath):
    pybdsim.Convert.MadxTfs2Gmad(atf2, tmppath)

    output_path = utils.get_output_path("atf2-nominal-twiss-v5.2.tfs.tar.gz")
    for suffix in GMAD_SUFFIXES:
        new_gmad = "{}{}.gmad".format(tmppath, suffix)
        old_gmad = "{}{}.gmad".format(output_path, suffix)
        # Skip the first 3 lines which are just the header
        with open(new_gmad, "r") as new, open(old_gmad, "r") as old:
            for new_line, old_line in izip(islice(new, 3, None),
                                           islice(old, 3, None)):
                assert new_line == old_line
