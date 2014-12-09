import numpy as _np
import pymadx as _pymadx
import Builder as _Builder
import _MadxTfs2Gmad

"""
Module for various conversions.

"""

def _IndexOfElement(tfsinstance,markername):
    t = tfsinstance
    names = list(t.data['NAME'])
    try:
        i = names.index(markername)
    except ValueError:
        i = 0
        print 'Unknown element name'
    return i

def MadxTfs2Gmad(inputfilename,outputfilename,startname=None,endname=None,ignorezerolengthitems=True,samplers='all',aperturedict={},collimatordict={},beampipeRadius=0.2,verbose=False, beam=False):
    __doc__ = _MadxTfs2Gmad.MadxTfs2Gmad.__doc__
    _MadxTfs2Gmad.MadxTfs2Gmad(inputfilename,outputfilename,startname,endname,ignorezerolengthitems,samplers,aperturedict,collimatordict,beampipeRadius,verbose, beam)
    
    
def InterrogateMadXLattice(tfsfilename):
    """
    InterrogateMadXLattice(tfsfilename)

    return populations,populationsbynumber

    two dictionaries with the keyword arguement and the number
    of items in the MADX tfs file supplied that match that
    keyword.

    """
    
    a = pymadx.MadX.Tfs(tfsfilename)
    keys = set(a.data['KEYWORD'])
    nitems = len(a.data['NAME'])
    print 'Filename           > ',tfsfilename
    print 'Number of Elements > ',nitems
    print 'Lattice Length     > ',a.data['S'][-1]+a.data['L'][-1]+'m'
    populations = {key:0 for key in keys}
    for i in range(nitems):
        populations[a.data['KEYWORD'][i]] += 1
    #flip dictionary around
    popsr = zip([populations[key] for key in populations.keys()],populations.keys())
    #sort it so we can see what's the most common element
    popsr = sorted(popsr)[::-1]
    #print feedback
    print 'Type'.ljust(15)+'#'.rjust(len(str(max(popsr)[0])))
    for item in popsr:
        print item[1].ljust(15,'.')+str(item[0]).rjust(len(str(max(popsr)[0])),'.')
    return populations,popsr
