import pytest

import pybdsim


def test_Drift_repr():
    drift = pybdsim.Builder.Drift('mydrift', 0.5)
    expected = 'mydrift: drift, l=0.5;\n'
    assert repr(drift) == expected

def test_HKicker_repr():
    hkicker = pybdsim.Builder.HKicker('myhkick', 0.5, l=0.5)
    expected = 'myhkick: hkicker, hkick=0.5, l=0.5;\n'
    assert repr(hkicker) == expected

def test_VKicker_repr():
    vkicker = pybdsim.Builder.VKicker('myvkick', 0.5, l=0.5)
    expected = 'myvkick: vkicker, l=0.5, vkick=0.5;\n'
    assert repr(vkicker) == expected

def test_Kicker_repr():
    kicker = pybdsim.Builder.Kicker('mykicker', 0.5, 0.5, l=0.5)
    expected ='mykicker: kicker, hkick=0.5, l=0.5, vkick=0.5;\n'
    assert repr(kicker) == expected

def test_TKicker_repr():
    tkicker = pybdsim.Builder.TKicker('mytkicker', 0.5, 0.5, l=0.5)
    expected = 'mytkicker: tkicker, hkick=0.5, l=0.5, vkick=0.5;\n'
    assert repr(tkicker) == expected

def test_Gap_repr():
    assert (repr(pybdsim.Builder.Gap('mygap', 0.6)) == "mygap: gap, l=0.6;\n")

def test_Marker_repr():
    assert (repr(pybdsim.Builder.Marker("mymarker")) == 'mymarker: marker;\n')

def test_Multipole_repr():
    mp = pybdsim.Builder.Multipole("mymultipole", 0.5,
                                   (0.1, 0.2, 0.3, 0.4, 0.5),
                                   (0.15, 0.25, 0.35, 0.45, 0.55))
    expected = ("mymultipole: multipole, knl={0.1,0.2,0.3,0.4,0.5},"
                " ksl={0.15,0.25,0.35,0.45,0.55}, l=0.5;\n")
    assert repr(mp) == expected


def test_Multipole_repr():
    m = pybdsim.Builder.ThinMultipole("mythinmultipole",
                                      (0.1, 0.2, 0.3, 0.4, 0.5),
                                      (0.15, 0.25, 0.35, 0.45, 0.55))
    assert (repr(m) == ('mythinmultipole: thinmultipole, '
                        'knl={0.1,0.2,0.3,0.4,0.5}, '
                        'ksl={0.15,0.25,0.35,0.45,0.55};\n'))

def test_Quadrupole_repr():
    q = pybdsim.Builder.Quadrupole('myquad', 0.5, 1.0)
    assert repr(q) == 'myquad: quadrupole, k1=1.0, l=0.5;\n'

def test_Sextupole_repr():
    s = pybdsim.Builder.Sextupole('myquad', 0.5, 1.0)
    assert repr(s) == 'myquad: sextupole, k2=1.0, l=0.5;\n'

def test_Octupole_repr():
    o = pybdsim.Builder.Octupole('myquad', 0.5, 1.0)
    assert repr(o) == 'myquad: octupole, k3=1.0, l=0.5;\n'

def test_Decapole_repr():
    d = pybdsim.Builder.Decapole('myquad', 0.5, 1.0)
    assert repr(d) == 'myquad: decapole, k4=1.0, l=0.5;\n'

def test_SBend_repr():
    sbend = pybdsim.Builder.SBend('mysbend', 0.5, angle=0.5)
    assert repr(sbend) == 'mysbend: sbend, angle=0.5, l=0.5;\n'

def test_RBend_repr():
    rbend = pybdsim.Builder.RBend('myrbend', 0.5, angle=0.5)
    assert repr(rbend) ==  'myrbend: rbend, angle=0.5, l=0.5;\n'

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
    shield = pybdsim.Builder.Shield('myshield', 0.5)
    expected = 'myshield: shield, l=0.5;\n'
    assert repr(shield) == expected

def test_Laser_repr():
    laser = pybdsim.Builder.Laser('mylaser', 0.1, 0.2, 0.3, 0.4, 5370)
    expected = 'mylaser: laser, l=0.1, waveLength=5370, x=0.2, y=0.3, z=0.4;\n'
    assert repr(laser) == expected
