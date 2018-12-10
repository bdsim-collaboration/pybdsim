import pytest

import pybdsim

@pytest.fixture
def drift():
    return pybdsim.Builder.Drift('myd', 0.5)

@pytest.fixture
def hkicker():
    return pybdsim.Builder.HKicker('myh', 0.5, l=0.5)

@pytest.fixture
def vkicker():
    return pybdsim.Builder.VKicker('myv', 0.5, l=0.5)

@pytest.fixture
def kicker():
    return pybdsim.Builder.Kicker('myk', 0.5, 0.5, l=0.5)

@pytest.fixture
def tkicker():
    return pybdsim.Builder.TKicker('myt', 0.5, 0.5, l=0.5)

@pytest.fixture
def multipole():
    return pybdsim.Builder.Multipole("mym", 0.5,
                                     (0.5, 0.5, 0.5, 0.5, 0.5),
                                     (0.5, 0.5, 0.5, 0.5, 0.5))

@pytest.fixture
def quadrupole():
    return pybdsim.Builder.Quadrupole('myq', 0.5, 0.5)

@pytest.fixture
def sextupole():
    return pybdsim.Builder.Sextupole('mys', 0.5, 0.5)

@pytest.fixture
def octupole():
    return pybdsim.Builder.Octupole('myo', 0.5, 0.5)

@pytest.fixture
def decapole():
    return pybdsim.Builder.Decapole('myd', 0.5, 0.5)

@pytest.fixture
def sbend():
    return pybdsim.Builder.SBend('mys', 0.5, angle=0.5,
                                 e1=0.1, e2=0.2,
                                 fint=0.1, fintx=0.2,
                                 h1=0.1, h2=0.2, hgap=0.5)

@pytest.fixture
def rbend():
    return pybdsim.Builder.RBend('myr', 0.5, angle=0.5,
                                 e1=0.1, e2=0.2,
                                 fint=0.1, fintx=0.2,
                                 h1=0.1, h2=0.2, hgap=0.5)

def test_Drift_repr(drift):
    expected = 'myd: drift, l=0.5;\n'
    assert repr(drift) == expected

def test_Drift_split(drift):
    split_drifts = drift.split([0.2, 0.4])
    expected = [pybdsim.Builder.Drift('myd_split_0', 0.2),
                pybdsim.Builder.Drift('myd_split_1', 0.2),
                pybdsim.Builder.Drift('myd_split_2', 0.1)]
    assert split_drifts == expected

def test_HKicker_repr(hkicker):
    expected = 'myh: hkicker, hkick=0.5, l=0.5;\n'
    assert repr(hkicker) == expected

def test_HKicker_split(hkicker):
    split_kickers = hkicker.split([0.2, 0.4])
    expected = [pybdsim.Builder.HKicker('myh_split_0', 0.2, l=0.2),
                pybdsim.Builder.HKicker('myh_split_1', 0.2, l=0.2),
                pybdsim.Builder.HKicker('myh_split_2', 0.1, l=0.1)]
    assert split_kickers == expected

def test_VKicker_repr(vkicker):
    expected = 'myv: vkicker, l=0.5, vkick=0.5;\n'
    assert repr(vkicker) == expected

def test_VKicker_split(vkicker):
    split_kickers = vkicker.split([0.2, 0.4])
    expected = [pybdsim.Builder.VKicker('myv_split_0', 0.2, l=0.2),
                pybdsim.Builder.VKicker('myv_split_1', 0.2, l=0.2),
                pybdsim.Builder.VKicker('myv_split_2', 0.1, l=0.1)]
    assert split_kickers == expected

def test_Kicker_repr(kicker):
    expected ='myk: kicker, hkick=0.5, l=0.5, vkick=0.5;\n'
    assert repr(kicker) == expected

def test_Kicker_split(kicker):
    split_kickers = kicker.split([0.2, 0.4])
    expected = [pybdsim.Builder.Kicker('myk_split_0', 0.2, 0.2, l=0.2),
                pybdsim.Builder.Kicker('myk_split_1', 0.2, 0.2, l=0.2),
                pybdsim.Builder.Kicker('myk_split_2', 0.1, 0.1, l=0.1)]
    assert split_kickers == expected

def test_TKicker_repr(tkicker):
    expected = 'myt: tkicker, hkick=0.5, l=0.5, vkick=0.5;\n'
    assert repr(tkicker) == expected

def test_TKicker_split(tkicker):
    split_tkickers = tkicker.split([0.2, 0.4])
    expected = [pybdsim.Builder.TKicker('myt_split_0', 0.2, 0.2, l=0.2),
                pybdsim.Builder.TKicker('myt_split_1', 0.2, 0.2, l=0.2),
                pybdsim.Builder.TKicker('myt_split_2', 0.1, 0.1, l=0.1)]
    assert split_tkickers == expected

def test_Gap_repr():
    assert (repr(pybdsim.Builder.Gap('myg', 0.6)) == "myg: gap, l=0.6;\n")

def test_Marker_repr():
    assert (repr(pybdsim.Builder.Marker("mym")) == 'mym: marker;\n')

def test_Multipole_repr(multipole):
    expected = ("mym: multipole, knl={0.5,0.5,0.5,0.5,0.5},"
                " ksl={0.5,0.5,0.5,0.5,0.5}, l=0.5;\n")
    assert repr(multipole) == expected

def test_Multipole_split(multipole):
    split_multipoles = multipole.split([0.2, 0.4])
    expected = [pybdsim.Builder.Multipole('mym_split_0', 0.2,
                                          (0.2, 0.2, 0.2, 0.2, 0.2),
                                          (0.2, 0.2, 0.2, 0.2, 0.2)),
                pybdsim.Builder.Multipole('mym_split_1', 0.2,
                                          (0.2, 0.2, 0.2, 0.2, 0.2),
                                          (0.2, 0.2, 0.2, 0.2, 0.2)),
                pybdsim.Builder.Multipole('mym_split_2', 0.1,
                                          (0.1, 0.1, 0.1, 0.1, 0.1),
                                          (0.1, 0.1, 0.1, 0.1, 0.1))]
    assert split_multipoles == expected


def test_ThinMultipole_repr():
    m = pybdsim.Builder.ThinMultipole("myt",
                                      (0.5, 0.5, 0.5, 0.5, 0.5),
                                      (0.5, 0.5, 0.5, 0.5, 0.5))
    assert (repr(m) == ('myt: thinmultipole, '
                        'knl={0.5,0.5,0.5,0.5,0.5}, '
                        'ksl={0.5,0.5,0.5,0.5,0.5};\n'))

def test_quadrupole_repr(quadrupole):
    assert repr(quadrupole) == 'myq: quadrupole, k1=0.5, l=0.5;\n'

def test_Quadrupole_splitting(quadrupole):
    split_quadrupoles = quadrupole.split([0.2, 0.4])
    expected = [pybdsim.Builder.Quadrupole('myq_split_0', l=0.2, k1=0.5),
                pybdsim.Builder.Quadrupole('myq_split_1', l=0.2, k1=0.5),
                pybdsim.Builder.Quadrupole('myq_split_2', l=0.1, k1=0.5)]
    assert expected == split_quadrupoles

def test_Sextupole_repr(sextupole):
    assert repr(sextupole) == 'mys: sextupole, k2=0.5, l=0.5;\n'

def test_Sextupole_splitting(sextupole):
    split_sextupoles = sextupole.split([0.2, 0.4])
    expected = [pybdsim.Builder.Sextupole('mys_split_0', l=0.2, k2=0.5),
                pybdsim.Builder.Sextupole('mys_split_1', l=0.2, k2=0.5),
                pybdsim.Builder.Sextupole('mys_split_2', l=0.1, k2=0.5)]
    assert expected == split_sextupoles

def test_Octupole_repr(octupole):
    assert repr(octupole) == 'myo: octupole, k3=0.5, l=0.5;\n'

def test_Octupole_splitting(octupole):
    split_octupoles = octupole.split([0.2, 0.4])
    expected = [pybdsim.Builder.Octupole('myo_split_0', l=0.2, k3=0.5),
                pybdsim.Builder.Octupole('myo_split_1', l=0.2, k3=0.5),
                pybdsim.Builder.Octupole('myo_split_2', l=0.1, k3=0.5)]
    assert expected == split_octupoles

def test_Decapole_repr(decapole):
    assert repr(decapole) == 'myd: decapole, k4=0.5, l=0.5;\n'

def test_Decapole_splitting(decapole):
    split_decapoles = decapole.split([0.2, 0.4])
    expected = [pybdsim.Builder.Decapole('myd_split_0', l=0.2, k4=0.5),
                pybdsim.Builder.Decapole('myd_split_1', l=0.2, k4=0.5),
                pybdsim.Builder.Decapole('myd_split_2', l=0.1, k4=0.5)]
    assert expected == split_decapoles

def test_SBend_repr(sbend):
    expected = ('mys: sbend, angle=0.5, e1=0.1, e2=0.2, fint=0.1, fintx=0.2,'
                ' h1=0.1, h2=0.2, hgap=0.5, l=0.5;\n')
    assert repr(sbend) == expected

def test_SBend_split(sbend):
    split_sbends = sbend.split([0.2, 0.4])
    expected = [pybdsim.Builder.SBend('mys_split_0', 0.2,
                                      angle=0.2, e1=0.1, fint=0.1,
                                      h1=0.1, hgap=0.5),
                pybdsim.Builder.SBend('mys_split_1', 0.2,
                                      angle=0.2, hgap=0.5),
                pybdsim.Builder.SBend('mys_split_2', 0.1,
                                      angle=0.1, e2=0.2, fintx=0.2,
                                      h2=0.2, hgap=0.5)]
    assert split_sbends == expected

def test_RBend_repr(rbend):
    expected = ('myr: rbend, angle=0.5, e1=0.1, e2=0.2, fint=0.1, fintx=0.2,'
                ' h1=0.1, h2=0.2, hgap=0.5, l=0.5;\n')
    assert repr(rbend) == expected

def test_RBend_split(rbend):
    split_rbends = rbend.split([0.2, 0.4])
    expected = [pybdsim.Builder.RBend('myr_split_0', 0.2,
                                      angle=0.2, e1=0.1, fint=0.1,
                                      h1=0.1, hgap=0.5),
                pybdsim.Builder.RBend('myr_split_1', 0.2,
                                      angle=0.2, hgap=0.5),
                pybdsim.Builder.RBend('myr_split_2', 0.1,
                                      angle=0.1, e2=0.2, fintx=0.2,
                                      h2=0.2, hgap=0.5)]
    assert split_rbends == expected

def test_RFCavity_repr():
    rf = pybdsim.Builder.RFCavity('rf', 0.5, 0.5)
    assert repr(rf) == 'rf: rfcavity, gradient=0.5, l=0.5;\n'

def test_RCol_repr():
    rcol = pybdsim.Builder.RCol("rc", 0.5, 0.5, 0.5)
    assert repr(rcol) == 'rc: rcol, l=0.5, xsize=0.5, ysize=0.5;\n'

def test_ECol_repr():
    ecol = pybdsim.Builder.ECol("ec", 0.5, 0.5, 0.5)
    assert repr(ecol) == 'ec: ecol, l=0.5, xsize=0.5, ysize=0.5;\n'

def test_Degrader_repr():
    degrader = pybdsim.Builder.Degrader("deg", 0.5, 1, 2, 3, 4, 5)
    expected = ('deg: degrader, degraderHeight=3, l=0.5,'
                ' materialThickness=4, numberWedges=1, wedgeLength=2;\n')
    assert repr(degrader) == expected

def test_MuSpoiler_repr():
    spoiler = pybdsim.Builder.MuSpoiler("mu", 0.5, 1.0)
    expected = 'mu: muspoiler, B=1.0, l=0.5;\n'
    assert repr(spoiler) == expected

def test_Solenoid_repr():
    sol = pybdsim.Builder.Solenoid("sol", 0.5, 0.1)
    expected = 'sol: solenoid, ks=0.1, l=0.5;\n'
    assert repr(sol) == expected

def test_Shield_repr():
    shield = pybdsim.Builder.Shield('mys', 0.5)
    expected = 'mys: shield, l=0.5;\n'
    assert repr(shield) == expected

def test_Laser_repr():
    laser = pybdsim.Builder.Laser('myl', 0.1, 0.2, 0.3, 0.4, 5370)
    expected = 'myl: laser, l=0.1, waveLength=5370, x=0.2, y=0.3, z=0.4;\n'
    assert repr(laser) == expected
