# pybdsim.ModelProcessing - tools to process existing BDSIM models
# Version 1.0
# L. Nevay
# laurie.nevay@rhul.ac.uk

"""
ModelProcessing

Tools to process existing BDSIM models and generate other
versions of them.

"""

import Gmad as _Gmad
import Builder as _Builder

def GenerateFullListOfSamplers(inputfile, outputfile):
    """
    inputfile - path to main gmad input file

    This will parse the input using the compiled BDSIM
    parser (GMAD), iterate over all the beamline elements
    and generate a sampler for every elements.  Ignores
    samplers, but may include already defined ones in your
    own input.

    """
    lattice  = _Gmad.Lattice(inputfile)
    samplers = []
    typestoignore = [
        'None',
        'Sampler',
        'CSampler',
        'Line',
        'Reversed Line',
        'Material',
        'Atom',
        'Sequence',
        'Tunnel',
        'Teleporter',
        'Terminator',
        'Transform3D'
        ]
    for e in lattice:
        if e['Type'] not in typestoignore:
           samplers.append(_Builder.Sampler(e['Name']))

    _WriteSamplerToGmadFile(samplers,outputfile)

def _WriteSamplerToGmadFile(samplerlist, outputfile):
    f = open(outputfile, "w")
    for s in samplerlist:
        f.write(s.__repr__())
    f.close()
                           

                           
