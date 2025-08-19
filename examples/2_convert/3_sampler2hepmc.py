#! /usr/bin/env python2.7

import pybdsim

def Main():
    pybdsim.Convert.BdsimSamplerData2Hepmc2('bdsim_raw.root','hepmc2_example.dat','sampler',-5,[13,-13])
    pybdsim.Convert.BdsimSamplerData2Hepmc3('bdsim_raw.root','hepmc3_example.dat','sampler',-5,[13,-13],weightsName='splitting_bias')

if __name__ == "__main__":
    Main()
