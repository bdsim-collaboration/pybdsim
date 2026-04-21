import gzip

import pytest

from pybdsim.Beam import Beam, WriteUserFile


def test_write_user_file_plain_and_gzip(tmp_path):
    coords = [[1, 2, 3], [4, 5, 6]]
    plain = tmp_path / "beam.txt"
    gz_path = tmp_path / "beam.txt.gz"

    WriteUserFile(str(plain), coords)
    assert plain.read_text() == '1.00000\t2.00000\t3.00000\n4.00000\t5.00000\t6.00000\n'

    WriteUserFile(str(gz_path), coords)
    with gzip.open(gz_path, "rt", encoding="ascii") as fh:
        assert fh.read() == '1.00000\t2.00000\t3.00000\n4.00000\t5.00000\t6.00000\n'


def test_default_beam_repr_and_file(tmp_path):
    beam = Beam()
    expected = 'beam,\tdistrType="reference",\n\tenergy=1.0*GeV, \n\tparticle="e-";'
    assert repr(beam) == expected

    destination = tmp_path / "beam.gmad"
    beam.WriteToFile(str(destination))
    assert destination.read_text() == expected


def test_set_particle_type_validation():
    beam = Beam()
    beam.SetParticleType("proton")
    assert beam["particle"] == '"proton"'

    with pytest.raises(ValueError):
        beam.SetParticleType("unknown")


def test_set_distribution_type_validation_and_prefix_allowlist():
    beam = Beam()
    beam.SetDistributionType("gauss")
    assert beam["distrType"] == '"gauss"'

    beam.SetDistributionType("bdsimsampler:SOURCE")
    assert beam["distrType"] == '"bdsimsampler:SOURCE"'

    beam.SetDistributionType("eventgeneratorfile:FORMAT")
    assert beam["distrType"] == '"eventgeneratorfile:FORMAT"'

    with pytest.raises(ValueError):
        beam.SetDistributionType("not-a-distribution")


@pytest.mark.parametrize(
    "method,args,kwargs,expected_key,expected_value",
    [
        ("SetEnergy", (2.5,), {"unitsstring": "MeV"}, "energy", "2.5*MeV"),
        ("SetX0", (1.2,), {"unitsstring": "cm"}, "X0", "1.2*cm"),
        ("SetY0", (2.4,), {"unitsstring": "mm"}, "Y0", "2.4*mm"),
        ("SetZ0", (3.3,), {"unitsstring": "cm"}, "Z0", "3.3*cm"),
        ("SetXP0", (0.1,), {}, "Xp0", "0.1"),
        ("SetYP0", (0.2,), {}, "Yp0", "0.2"),
        ("SetZP0", (0.3,), {}, "Zp0", "0.3"),
        ("SetS0", (10,), {"unitsstring": "km"}, "S0", "10*km"),
        ("SetE0", (5,), {"unitsstring": "MeV"}, "E0", "5*MeV"),
        ("SetT0", (7,), {"unitsstring": "ms"}, "T0", "7*ms"),
    ],
)
def test_base_setters_populate_dictionary(method, args, kwargs, expected_key, expected_value):
    beam = Beam()
    getattr(beam, method)(*args, **kwargs)
    assert beam[expected_key] == expected_value


def test_gauss_distribution_adds_sigma_methods():
    beam = Beam()
    beam.SetDistributionType("gauss")

    for name in ["SetSigmaX", "SetSigmaY", "SetSigmaE", "SetSigmaXP", "SetSigmaYP", "SetSigmaT"]:
        assert hasattr(beam, name)

    beam.SetSigmaX(1.0, unitsstring="cm")
    beam.SetSigmaE(0.02)
    beam.SetSigmaXP(0.5, unitsstring="rad")
    beam.SetSigmaYP(0.6, unitsstring="rad")
    beam.SetSigmaT(7.0, unitsstring="s")
    assert beam["sigmaX"] == "1.0*cm"
    assert beam["sigmaE"] == "0.02"
    assert beam["sigmaXp"] == "0.5*rad"
    assert beam["sigmaYp"] == "0.6*rad"
    assert beam["sigmaT"] == "7.0*s"


def test_gausstwiss_distribution_adds_twiss_methods():
    beam = Beam()
    beam.SetDistributionType("gausstwiss")

    expected_methods = [
        "SetBetaX",
        "SetBetaY",
        "SetAlphaX",
        "SetAlphaY",
        "SetEmittanceX",
        "SetEmittanceY",
        "SetEmittanceNX",
        "SetEmittanceNY",
        "SetSigmaE",
        "SetSigmaT",
        "SetDispX",
        "SetDispY",
        "SetDispXP",
        "SetDispYP",
    ]
    for name in expected_methods:
        assert hasattr(beam, name)

    beam.SetBetaX(3.0, unitsstring="m")
    beam.SetBetaY(4.0, unitsstring="m")
    beam.SetAlphaX(0.9)
    beam.SetAlphaY(1.1)
    beam.SetDispXP(0.05)
    beam.SetDispY(0.06, unitsstring="m")
    beam.SetSigmaT(8.0, unitsstring="s")
    beam.SetEmittanceNX(9.1e-9, unitsstring="mm*mrad")
    beam.SetEmittanceNY(9.2e-9, unitsstring="mm*mrad")
    assert beam["betx"] == "3.0*m"
    assert beam["bety"] == "4.0*m"
    assert beam["alfx"] == "0.9"
    assert beam["alfy"] == "1.1"
    assert beam["dispxp"] == "0.05"
    assert beam["dispy"] == "0.06*m"
    assert beam["sigmaT"] == "8.0*s"
    assert beam["emitnx"] == "9.1e-09*mm*mrad"
    assert beam["emitny"] == "9.2e-09*mm*mrad"


def test_gaussmatrix_distribution_adds_sigma_nm():
    beam = Beam()
    beam.SetDistributionType("gaussmatrix")
    assert hasattr(beam, "SetSigmaNM")

    beam.SetSigmaNM(2, 3, "value")
    assert beam["sigma23"] == "value"


def test_circle_distribution_adds_envelope_methods():
    beam = Beam()
    beam.SetDistributionType("circle")

    for name in ["SetEnvelopeR", "SetEnvelopeRp", "SetEnvelopeT", "SetEnvelopeE"]:
        assert hasattr(beam, name)

    beam.SetEnvelopeR(1.5, unitsstring="m")
    beam.SetEnvelopeE(5.0, unitsstring="GeV")
    beam.SetEnvelopeRp(2.5, unitsstring="mrad")
    beam.SetEnvelopeT(3.5, unitsstring="s")
    assert beam["envelopeR"] == "1.5*m"
    assert beam["envelopeE"] == "5.0*GeV"
    assert beam["envelopeRp"] == "2.5*mrad"
    assert beam["envelopeT"] == "3.5*s"


def test_square_distribution_adds_envelope_methods():
    beam = Beam()
    beam.SetDistributionType("square")

    for name in ["SetEnvelopeX", "SetEnvelopeXp", "SetEnvelopeY", "SetEnvelopeYp", "SetEnvelopeT", "SetEnvelopeE"]:
        assert hasattr(beam, name)

    beam.SetEnvelopeX(0.5, unitsstring="m")
    beam.SetEnvelopeYp(0.25, unitsstring="mrad")
    beam.SetEnvelopeXp(0.75, unitsstring="mrad")
    beam.SetEnvelopeY(0.6, unitsstring="m")
    beam.SetEnvelopeT(1.1, unitsstring="s")
    beam.SetEnvelopeE(2.2, unitsstring="GeV")
    assert beam["envelopeX"] == "0.5*m"
    assert beam["envelopeYp"] == "0.25*mrad"
    assert beam["envelopeXp"] == "0.75*mrad"
    assert beam["envelopeY"] == "0.6*m"
    assert beam["envelopeT"] == "1.1*s"
    assert beam["envelopeE"] == "2.2*GeV"


def test_ring_distribution_adds_radius_methods():
    beam = Beam()
    beam.SetDistributionType("ring")
    assert hasattr(beam, "SetRMin")
    assert hasattr(beam, "SetRMax")

    beam.SetRMin(0.9, unitsstring="mm")
    beam.SetRMax(1.1, unitsstring="mm")
    assert beam["Rmin"] == "0.9*mm"
    assert beam["Rmax"] == "1.1*mm"


def test_eshell_distribution_adds_shell_methods():
    beam = Beam()
    beam.SetDistributionType("eshell")

    for name in ["SetShellX", "SetShellY", "SetShellXP", "SetShellYP"]:
        assert hasattr(beam, name)

    beam.SetShellX(2.0, unitsstring="cm")
    beam.SetShellYP(0.7)
    beam.SetShellY(3.0, unitsstring="cm")
    beam.SetShellXP(0.8)
    assert beam["shellX"] == "2.0*cm"
    assert beam["shellYp"] == "0.7"
    assert beam["shellY"] == "3.0*cm"
    assert beam["shellXp"] == "0.8"


def test_halo_distribution_adds_halo_and_twiss_methods():
    beam = Beam()
    beam.SetDistributionType("halo")

    for name in ["SetHaloNSigmaXInner", "SetHaloNSigmaXOuter", "SetHaloNSigmaYInner", "SetHaloNSigmaYOuter",
                 "SetHaloPSWeightParameter", "SetHaloPSWeightFunction", "SetHaloXCutInner", "SetHaloYCutInner",
                 "SetBetaX", "SetBetaY"]:
        assert hasattr(beam, name)

    beam.SetHaloPSWeightFunction("weight")
    beam.SetHaloNSigmaXOuter(3)
    beam.SetBetaY(4.0, unitsstring="m")
    beam.SetHaloNSigmaXInner(1)
    beam.SetHaloNSigmaYInner(2)
    beam.SetHaloNSigmaYOuter(5)
    beam.SetHaloXCutInner(0.11)
    beam.SetHaloYCutInner(0.22)
    beam.SetHaloPSWeightParameter({"p": 1})
    beam.SetBetaX(6.0, unitsstring="m")
    assert beam["haloPSWeightFunction"] == '"weight"'
    assert beam["haloNSigmaXOuter"] == "3"
    assert beam["bety"] == "4.0*m"
    assert beam["haloNSigmaXInner"] == "1"
    assert beam["haloNSigmaYInner"] == "2"
    assert beam["haloNSigmaYOuter"] == "5"
    assert beam["haloXCutInner"] == "0.11"
    assert beam["haloYCutInner"] == "0.22"
    assert beam["haloPSWeightParameter"] == {"p": 1}
    assert beam["betx"] == "6.0*m"


def test_composite_distribution_injects_axis_methods():
    beam = Beam()
    beam.SetDistributionType("composite")

    beam.SetXDistrType("gauss")
    assert hasattr(beam, "SetSigmaX")
    beam.SetSigmaX(0.25, unitsstring="mm")
    assert beam["xDistrType"] == '"gauss"'
    assert beam["sigmaX"] == "0.25*mm"

    beam.SetYDistrType("ring")
    assert hasattr(beam, "SetRMin")
    beam.SetRMin(0.5, unitsstring="mm")
    assert beam["yDistrType"] == '"ring"'
    assert beam["Rmin"] == "0.5*mm"

    beam.SetZDistrType("square")
    assert hasattr(beam, "SetEnvelopeX")
    beam.SetEnvelopeX(1.5, unitsstring="m")
    assert beam["zDistrType"] == '"square"'
    assert beam["envelopeX"] == "1.5*m"


def test_ptc_distribution_methods():
    beam = Beam()
    beam.SetDistributionType("ptc")
    for name in ["SetSigmaE", "SetDistribFileName"]:
        assert hasattr(beam, name)

    beam.SetSigmaE(0.01)
    beam.SetDistribFileName("ptc.dat")
    assert beam["sigmaE"] == "0.01"
    assert beam["distrFile"] == '"ptc.dat"'


def test_userfile_distribution_methods():
    beam = Beam()
    beam.SetDistributionType("userfile")
    for name in ["SetDistrFile", "SetDistrFileFormat"]:
        assert hasattr(beam, name)

    beam.SetDistrFile("beam.dat")
    beam.SetDistrFileFormat("ascii")
    assert beam["distrFile"] == '"beam.dat"'
    assert beam["distrFileFormat"] == '"ascii"'


def test_slowext_distribution_methods():
    beam = Beam()
    beam.SetDistributionType("slowext")
    for name in ["SetDTStart", "SetDTStop", "SetDPStart", "SetDPStop"]:
        assert hasattr(beam, name)

    beam.SetDTStart(0.5, unitsstring="s")
    beam.SetDTStop(0.6, unitsstring="s")
    beam.SetDPStart(0.7, unitsstring="GeV")
    beam.SetDPStop(1.2, unitsstring="GeV")
    assert beam["dTStart"] == "0.5*s"
    assert beam["dTStop"] == "0.6*s"
    assert beam["dPStart"] == "0.7*GeV"
    assert beam["dPStop"] == "1.2*GeV"


def test_gaussslowext_combines_gauss_and_timing_methods():
    beam = Beam()
    beam.SetDistributionType("gaussslowext")

    for name in ["SetSigmaX", "SetSigmaY", "SetDTStart", "SetDPStop", "SetDPStart"]:
        assert hasattr(beam, name)

    beam.SetSigmaY(0.3, unitsstring="mm")
    beam.SetDTStart(2.0, unitsstring="s")
    beam.SetDPStart(1.5, unitsstring="GeV")
    beam.SetDPStop(1.6, unitsstring="GeV")
    assert beam["sigmaY"] == "0.3*mm"
    assert beam["dTStart"] == "2.0*s"
    assert beam["dPStart"] == "1.5*GeV"
    assert beam["dPStop"] == "1.6*GeV"


def test_gaussmatrixslowext_combines_sigma_nm_and_timing_methods():
    beam = Beam()
    beam.SetDistributionType("gaussmatrixslowext")

    for name in ["SetSigmaNM", "SetDTStop", "SetDPStart", "SetDTStart"]:
        assert hasattr(beam, name)

    beam.SetSigmaNM(4, 5, "v")
    beam.SetDTStop(1.1, unitsstring="s")
    beam.SetDTStart(0.9, unitsstring="s")
    beam.SetDPStart(2.2, unitsstring="GeV")
    assert beam["sigma45"] == "v"
    assert beam["dTStop"] == "1.1*s"
    assert beam["dTStart"] == "0.9*s"
    assert beam["dPStart"] == "2.2*GeV"


def test_gausstwissslowext_combines_twiss_and_timing_methods():
    beam = Beam()
    beam.SetDistributionType("gausstwissslowext")

    for name in ["SetBetaX", "SetAlphaY", "SetDPStop", "SetDTStop"]:
        assert hasattr(beam, name)

    beam.SetAlphaY(0.9)
    beam.SetDPStop(3.3, unitsstring="GeV")
    beam.SetDTStop(4.4, unitsstring="s")
    beam.SetBetaX(5.5, unitsstring="m")
    assert beam["alfy"] == "0.9"
    assert beam["dPStop"] == "3.3*GeV"
    assert beam["dTStop"] == "4.4*s"
    assert beam["betx"] == "5.5*m"


def test_direct_private_setters_for_unattached_methods():
    beam = Beam()
    beam._SetOffsetSampleMean(True)
    beam._SetOffsetSampleMean(False)
    beam._SetDistrFileLoop(3)
    assert beam["offsetSampleMean"] == 0
    assert beam["distrFileLoop"] == 3
