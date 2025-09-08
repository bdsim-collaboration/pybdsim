import pybdsim

def test_drift():
    drift = pybdsim.Builder.Drift('myd', 0.5)

def test_hkicker():
    hkicker = pybdsim.Builder.HKicker('myh', 0.5, l=0.5)

def test_vkicker():
    vkicker = pybdsim.Builder.VKicker('myv', 0.5, l=0.5)

def test_kicker():
    pybdsim.Builder.Kicker('myk', 0.5, 0.5, l=0.5)

def test_tkicker():
    pybdsim.Builder.TKicker('myt', 0.5, 0.5, l=0.5)

def test_multipole():
    pybdsim.Builder.Multipole("mym", 0.5, (0.5, 0.5, 0.5, 0.5, 0.5), (0.5, 0.5, 0.5, 0.5, 0.5))

def test_quadrupole():
    pybdsim.Builder.Quadrupole('myq', 0.5, 0.5)

def test_sextupole():
    pybdsim.Builder.Sextupole('mys', 0.5, 0.5)

def test_octupole():
    pybdsim.Builder.Octupole('myo', 0.5, 0.5)

def test_decapole():
    pybdsim.Builder.Decapole('myd', 0.5, 0.5)

def test_sbend():
    pybdsim.Builder.SBend('mys', 0.5, angle=0.5, e1=0.1, e2=0.2, fint=0.1, fintx=0.2, h1=0.1, h2=0.2, hgap=0.5)

def test_rbend():
    pybdsim.Builder.RBend('myr', 0.5, angle=0.5, e1=0.1, e2=0.2, fint=0.1, fintx=0.2, h1=0.1, h2=0.2, hgap=0.5)

def test_drift_repr():
    drift = pybdsim.Builder.Drift('myd', 0.5)
    assert repr(drift) == 'myd: drift, l=0.5;\n'

def test_drift_split():
    drift = pybdsim.Builder.Drift('myd', 0.5)
    split_drifts = drift.split([0.2, 0.4])
    expected = [pybdsim.Builder.Drift('myd_split_0', 0.2),
                pybdsim.Builder.Drift('myd_split_1', 0.2),
                pybdsim.Builder.Drift('myd_split_2', 0.1)]
    assert split_drifts == expected

def test_hkicker_repr():
    hkicker = pybdsim.Builder.HKicker('myh', 0.5, l=0.5)
    assert repr(hkicker) == 'myh: hkicker, hkick=0.5, l=0.5;\n'

def test_hkicker_split():
    hkicker = pybdsim.Builder.HKicker('myh', 0.5, l=0.5)
    split_kickers = hkicker.split([0.2, 0.4])
    expected = [pybdsim.Builder.HKicker('myh_split_0', 0.2, l=0.2),
                pybdsim.Builder.HKicker('myh_split_1', 0.2, l=0.2),
                pybdsim.Builder.HKicker('myh_split_2', 0.1, l=0.1)]
    assert split_kickers == expected

def test_vkicker_repr():
    vkicker = pybdsim.Builder.VKicker('myv', 0.5, l=0.5)
    assert repr(vkicker) == 'myv: vkicker, l=0.5, vkick=0.5;\n'

def test_vkicker_split():
    vkicker = pybdsim.Builder.VKicker('myv', 0.5, l=0.5)
    split_kickers = vkicker.split([0.2, 0.4])
    expected = [pybdsim.Builder.VKicker('myv_split_0', 0.2, l=0.2),
                pybdsim.Builder.VKicker('myv_split_1', 0.2, l=0.2),
                pybdsim.Builder.VKicker('myv_split_2', 0.1, l=0.1)]
    assert split_kickers == expected

def test_kicker_repr():
    kicker = pybdsim.Builder.Kicker('myk', 0.5, 0.5, l=0.5)
    assert repr(kicker) == 'myk: kicker, hkick=0.5, l=0.5, vkick=0.5;\n'

def test_kicker_split():
    kicker = pybdsim.Builder.Kicker('myk', 0.5, 0.5, l=0.5)
    split_kickers = kicker.split([0.2, 0.4])
    expected = [pybdsim.Builder.Kicker('myk_split_0', 0.2, 0.2, l=0.2),
                pybdsim.Builder.Kicker('myk_split_1', 0.2, 0.2, l=0.2),
                pybdsim.Builder.Kicker('myk_split_2', 0.1, 0.1, l=0.1)]
    assert split_kickers == expected

def test_tkicker_repr():
    tkicker = pybdsim.Builder.TKicker('myt', 0.5, 0.5, l=0.5)
    assert repr(tkicker) == 'myt: tkicker, hkick=0.5, l=0.5, vkick=0.5;\n'

def test_tkicker_split():
    tkicker = pybdsim.Builder.TKicker('myt', 0.5, 0.5, l=0.5)
    split_tkickers = tkicker.split([0.2, 0.4])
    expected = [pybdsim.Builder.TKicker('myt_split_0', 0.2, 0.2, l=0.2),
                pybdsim.Builder.TKicker('myt_split_1', 0.2, 0.2, l=0.2),
                pybdsim.Builder.TKicker('myt_split_2', 0.1, 0.1, l=0.1)]
    assert split_tkickers == expected

def test_gap_repr():
    assert (repr(pybdsim.Builder.Gap('myg', 0.6)) == "myg: gap, l=0.6;\n")

def test_marker_repr():
    assert (repr(pybdsim.Builder.Marker("mym")) == 'mym: marker;\n')

def test_multipole_repr():
    multipole = pybdsim.Builder.Multipole("mym", 0.5, (0.5, 0.5, 0.5, 0.5, 0.5), (0.5, 0.5, 0.5, 0.5, 0.5))
    expected = ("mym: multipole, knl={0.5,0.5,0.5,0.5,0.5},"
                " ksl={0.5,0.5,0.5,0.5,0.5}, l=0.5;\n")
    assert repr(multipole) == expected

def test_multipole_split():
    multipole = pybdsim.Builder.Multipole("mym", 0.5, (0.5, 0.5, 0.5, 0.5, 0.5), (0.5, 0.5, 0.5, 0.5, 0.5))
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


def test_thinmultipole_repr():
    m = pybdsim.Builder.ThinMultipole("myt",
                                      (0.5, 0.5, 0.5, 0.5, 0.5),
                                      (0.5, 0.5, 0.5, 0.5, 0.5))
    assert (repr(m) == ('myt: thinmultipole, '
                        'knl={0.5,0.5,0.5,0.5,0.5}, '
                        'ksl={0.5,0.5,0.5,0.5,0.5};\n'))

def test_quadrupole_repr():
    quadrupole = pybdsim.Builder.Quadrupole('myq', 0.5, 0.5)
    assert repr(quadrupole) == 'myq: quadrupole, k1=0.5, l=0.5;\n'

def test_quadrupole_split():
    quadrupole = pybdsim.Builder.Quadrupole('myq', 0.5, 0.5)
    split_quadrupoles = quadrupole.split([0.2, 0.4])
    expected = [pybdsim.Builder.Quadrupole('myq_split_0', l=0.2, k1=0.5),
                pybdsim.Builder.Quadrupole('myq_split_1', l=0.2, k1=0.5),
                pybdsim.Builder.Quadrupole('myq_split_2', l=0.1, k1=0.5)]
    assert expected == split_quadrupoles

def test_sextupole_repr():
    sextupole = pybdsim.Builder.Sextupole('mys', 0.5, 0.5)
    assert repr(sextupole) == 'mys: sextupole, k2=0.5, l=0.5;\n'

def test_sextupole_split():
    sextupole = pybdsim.Builder.Sextupole('mys', 0.5, 0.5)
    split_sextupoles = sextupole.split([0.2, 0.4])
    expected = [pybdsim.Builder.Sextupole('mys_split_0', l=0.2, k2=0.5),
                pybdsim.Builder.Sextupole('mys_split_1', l=0.2, k2=0.5),
                pybdsim.Builder.Sextupole('mys_split_2', l=0.1, k2=0.5)]
    assert expected == split_sextupoles

def test_octupole_repr():
    octupole = pybdsim.Builder.Octupole('myo', 0.5, 0.5)
    assert repr(octupole) == 'myo: octupole, k3=0.5, l=0.5;\n'

def test_octupole_split():
    octupole = pybdsim.Builder.Octupole('myo', 0.5, 0.5)
    split_octupoles = octupole.split([0.2, 0.4])
    expected = [pybdsim.Builder.Octupole('myo_split_0', l=0.2, k3=0.5),
                pybdsim.Builder.Octupole('myo_split_1', l=0.2, k3=0.5),
                pybdsim.Builder.Octupole('myo_split_2', l=0.1, k3=0.5)]
    assert expected == split_octupoles

def test_decapole_repr():
    decapole = pybdsim.Builder.Decapole('myd', 0.5, 0.5)
    assert repr(decapole) == 'myd: decapole, k4=0.5, l=0.5;\n'

def test_decapole_split():
    decapole = pybdsim.Builder.Decapole('myd', 0.5, 0.5)
    split_decapoles = decapole.split([0.2, 0.4])
    expected = [pybdsim.Builder.Decapole('myd_split_0', l=0.2, k4=0.5),
                pybdsim.Builder.Decapole('myd_split_1', l=0.2, k4=0.5),
                pybdsim.Builder.Decapole('myd_split_2', l=0.1, k4=0.5)]
    assert expected == split_decapoles

def test_sbend_repr():
    sbend = pybdsim.Builder.SBend('mys', 0.5, angle=0.5, e1=0.1, e2=0.2, fint=0.1, fintx=0.2, h1=0.1, h2=0.2, hgap=0.5)
    assert repr(sbend) == 'mys: sbend, angle=0.5, e1=0.1, e2=0.2, fint=0.1, fintx=0.2, h1=0.1, h2=0.2, hgap=0.5, l=0.5;\n'

def test_sbend_split():
    sbend = pybdsim.Builder.SBend('mys', 0.5, angle=0.5, e1=0.1, e2=0.2, fint=0.1, fintx=0.2, h1=0.1, h2=0.2, hgap=0.5)
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

def test_rbend_repr():
    rbend = pybdsim.Builder.RBend('myr', 0.5, angle=0.5, e1=0.1, e2=0.2, fint=0.1, fintx=0.2, h1=0.1, h2=0.2, hgap=0.5)
    assert repr(rbend) == 'myr: rbend, angle=0.5, e1=0.1, e2=0.2, fint=0.1, fintx=0.2, h1=0.1, h2=0.2, hgap=0.5, l=0.5;\n'

def test_rbend_split():
    rbend = pybdsim.Builder.RBend('myr', 0.5, angle=0.5, e1=0.1, e2=0.2, fint=0.1, fintx=0.2, h1=0.1, h2=0.2, hgap=0.5)
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

def test_rfcavity_repr():
    rf = pybdsim.Builder.RFCavity('rf', 0.5, 0.5)
    assert repr(rf) == 'rf: rfcavity, gradient=0.5, l=0.5;\n'

def test_rcol_repr():
    rcol = pybdsim.Builder.RCol("rc", 0.5, 0.5, 0.5)
    assert repr(rcol) == 'rc: rcol, l=0.5, xsize=0.5, ysize=0.5;\n'

def test_ecol_repr():
    ecol = pybdsim.Builder.ECol("ec", 0.5, 0.5, 0.5)
    assert repr(ecol) == 'ec: ecol, l=0.5, xsize=0.5, ysize=0.5;\n'

def test_degrader_repr():
    degrader = pybdsim.Builder.Degrader("deg", 0.5, 1, 2, 3, 4, 5)
    expected = ('deg: degrader, degraderHeight=3, l=0.5,'
                ' materialThickness=4, numberWedges=1, wedgeLength=2;\n')
    assert repr(degrader) == expected

def test_muspoiler_repr():
    spoiler = pybdsim.Builder.MuSpoiler("mu", 0.5, 1.0)
    assert repr(spoiler) == 'mu: muspoiler, B=1.0, l=0.5;\n'

def test_Solenoid_repr():
    sol = pybdsim.Builder.Solenoid("sol", 0.5, 0.1)
    assert repr(sol) == 'sol: solenoid, ks=0.1, l=0.5;\n'

def test_Shield_repr():
    shield = pybdsim.Builder.Shield('mys', 0.5)
    assert repr(shield) == 'mys: shield, l=0.5;\n'

def test_Laser_repr():
    laser = pybdsim.Builder.Laser('myl', 0.1, 0.2, 0.3, 0.4, 5370)
    assert repr(laser) == 'myl: laser, l=0.1, waveLength=5370, x=0.2, y=0.3, z=0.4;\n'

def test_insert():
    machine = pybdsim.Builder.Machine()
    machine.AddDrift(name="dr", length=0.1)
    machine.Insert(pybdsim.Builder.RBend("myr", 0.1, angle=0), index = "dr")
    machine.Insert(pybdsim.Builder.RBend("myr1", 0.1, angle=0), index = "dr", after=True)
    machine.Insert("dr", index = "myr1", after=True, substitute=True)
    expected = ['myr', 'dr', 'myr1', 'dr']
    assert machine.sequence == expected

def test_bdsimsampler_repr():
    beam = pybdsim.Beam.Beam()
    beam.SetDistributionType("bdsimsampler:SAMPLER")
    beam.SetEnergy(100)
    beam.SetParticleType("proton")
    expected = 'beam,\tdistrType="bdsimsampler:SAMPLER",\n\tenergy=100*GeV, \n\tparticle="proton";'
    assert repr(beam) == expected

def test_eventgeneratorfile_repr():
    beam = pybdsim.Beam.Beam()
    beam.SetDistributionType("eventgeneratorfile:FORMAT")
    beam.SetEnergy(100)
    beam.SetParticleType("proton")
    expected = 'beam,\tdistrType="eventgeneratorfile:FORMAT",\n\tenergy=100*GeV, \n\tparticle="proton";'
    assert repr(beam) == expected


#test_element_split_sbend()
#test_drift_split()
#test_multipole_split()