#! /usr/bin/env python2.7

import pybdsim

def Main():
    pybdsim.Convert.Transport2Gmad('transport_example.dat',outputDir='transport_example')

if __name__ == "__main__":
    Main()
