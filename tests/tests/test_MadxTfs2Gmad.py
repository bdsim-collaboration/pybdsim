import os.path

import pytest

import pybdsim
import pymadx

# TODO:
# TEST with aperturedict of pymadx.Data.Aperture.
# TEST with collimator dict (atf2 has no collimators).
# TEST with usemadxaperture (atf2 has no aperinfo with it).
# TEST coupled combinations of arguments, whatever they may be.

PATH_TO_TEST_INPUT = "{}/../test_input/".format(os.path.dirname(__file__))

@pytest.fixture
def atf2():
    return "{}/atf2-nominal-twiss-v5.2.tfs.tar.gz".format(
        PATH_TO_TEST_INPUT)

@pytest.fixture
def outpath(tmpdir):
    """A temporary file path"""
    return str(tmpdir.mkdir("testdir").join("testoutput"))

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

def test_atf2_conversion_default(atf2, outpath):
    """Default parameters should not fail."""
    pybdsim.Convert.MadxTfs2Gmad(atf2, outpath)

@pytest.mark.parametrize(('start', 'stop', 'step'),
                         [(10, 20, 2),
                          ("KEX1A", "L229", 1),
                          ("KEX1A", 40, 1),
                          (10, "L229", 1)])
def test_atf2_conversion_with_start_stop_and_stepsize(atf2, outpath,
                                                      start, stop, step):
    """Given the ATF2 model and a start, stop and step:  do not crash."""
    pybdsim.Convert.MadxTfs2Gmad(atf2, outpath,
                                 startname=start,
                                 stopname=stop,
                                 stepsize=step)

@pytest.mark.parametrize('ignorezerolengthitems', [True, False])
def test_atf2_conversion_with_ignorezerolengthitems(atf2, outpath,
                                                    ignorezerolengthitems):
    """Given the ATF2 model and valid args for
    ignorezerolengthitems:  do not crash."""
    pybdsim.Convert.MadxTfs2Gmad(atf2, outpath,
                                 ignorezerolengthitems=ignorezerolengthitems)


@pytest.mark.parametrize('flipmagnets', [True, False, None])
def test_atf2_conversion_with_flipmagnets(atf2, outpath, flipmagnets):
    """Given the ATF2 model and the set of allowed `flipmagnets` arguments:
    do not crash."""
    pybdsim.Convert.MadxTfs2Gmad(atf2, outpath, flipmagnets=flipmagnets)

@pytest.mark.parametrize('linear', [True, False])
def test_atf2_conversion_with_linear(atf2, outpath, linear):
    """Given the ATF2 model and the set of allowed `linear` arguments:
    do not crash."""
    pybdsim.Convert.MadxTfs2Gmad(atf2, outpath, linear=linear)

@pytest.mark.parametrize('samplers', ['all', None, ["KEX1A", "KEX1B"]])
def test_atf2_conversion_with_samplers(atf2, outpath, samplers):
    """Given the ATF2 model and the set of allowed `samplers` arguments:
    do not crash."""
    pybdsim.Convert.MadxTfs2Gmad(atf2, outpath, samplers=samplers)

# should also test with a pymadx.Data.Aperture instance.
def test_atf2_conversion_with_aperturedict(atf2, outpath):
    pybdsim.Convert.MadxTfs2Gmad(atf2, outpath,
                                 aperturedict={
                                     "KEX1A":
                                     {"APERTYPE": "circular",
                                      "APER_1": 1,
                                      "APER_2": 0,
                                      "APER_3": 0,
                                      "APER_4": 0}})

def test_atf2_conversion_with_optionsDict(atf2, outpath):
    pybdsim.Convert.MadxTfs2Gmad(atf2, outpath,
                                 optionsDict={"stopSecondaries": "1"})

def test_atf2_conversion_with_userdict(atf2, outpath):
    pybdsim.Convert.MadxTfs2Gmad(atf2, outpath,
                                 userdict={"KEX1A": {"biasVacuum": "mybias"}})

def test_atf2_conversion_with_allelementdict(atf2, outpath):
    """Don't crash for valid arguments of allelementdict"""
    pybdsim.Convert.MadxTfs2Gmad(atf2, outpath,
                                 allelementdict={"biasVacuum": "mybias"})

def test_atf2_conversion_with_defaultAperture(atf2, outpath):
    """Don't crash for valid arguments of defaultAperture"""
    pybdsim.Convert.MadxTfs2Gmad(atf2, outpath,
                                 defaultAperture="rectellipse")

def test_atf2_conversion_with_biases(atf2, outpath, biases):
    pybdsim.Convert.MadxTfs2Gmad(atf2, outpath, biases=biases)

@pytest.mark.parametrize('beam', [True, False])
def test_atf2_conversion_with_beam(atf2, outpath, beam):
    pybdsim.Convert.MadxTfs2Gmad(atf2, outpath, beam=beam)

@pytest.mark.parametrize('overwrite', [True, False])
def test_atf2_conversion_with_overwrite(atf2, outpath, overwrite):
    pybdsim.Convert.MadxTfs2Gmad(atf2, outpath, overwrite=overwrite)

@pytest.mark.parametrize('allNamesUnique', [True, False])
def test_atf2_conversion_with_allNamesUnique(atf2, outpath, allNamesUnique):
    pybdsim.Convert.MadxTfs2Gmad(atf2, outpath, allNamesUnique=allNamesUnique)

@pytest.mark.parametrize('verbose', [True, False])
def test_atf2_conversion_with_verbose(atf2, outpath, verbose):
    pybdsim.Convert.MadxTfs2Gmad(atf2, outpath, verbose=verbose)

def test_atf2_conversion_with_beamParmsDict(atf2, outpath):
    beam = pybdsim.Convert.MadxTfs2GmadBeam(pymadx.Data.Tfs(atf2),
                                            startname="KEX1A")
    pybdsim.Convert.MadxTfs2Gmad(atf2, outpath, beam=beam)
