import pybdsim


def test_run_bdskim_custom():
    def filter(event):
        return event.d1.n > 2

    pybdsim.Data.SkimBDSIMFile("samplerdata", filter)