#!/usr/bin/env python2.7

import pickle
import ROOT as _ROOT 
from ROOT import TFile as _TFile 
import root_numpy as _root_numpy 
import sys as _sys

def Rebdsim2Numpy(rootfilename,picklefilename) :
    # open file 
    f = _TFile(rootfilename)

    # loop over keys
    kl = f.GetListOfKeys() 

    # data dict
    dd = {}

    for ki in range(0,kl.GetSize()) :
        cname = kl[ki].GetClassName()
        name  = kl[ki].GetName()

        if cname == "TDirectoryFile" : 
            d = f.Get(name)
            d.cd()
            # loop over histos in dir
            dkl = d.GetListOfKeys()
            for dki in range(0,dkl.GetSize()) :
                h  = d.Get(dkl[dki].GetName())
                ah = _root_numpy.hist2array(h)
                print "Histogram : ",name+"_"+dkl[dki].GetName()
                dd[name+"_"+dkl[dki].GetName()] = ah

        if cname == "TTree" : 
            t = f.Get(name)
            print "Tree      : ",name
            at = _root_numpy.tree2array(t)
            dd[name] = at

     
    f.Close()
   
    of = open(picklefilename,"wb")
    pickle.dump(dd,of)
    of.close()

if __name__ == "__main__" :
    Rebdsim2Numpy(_sys.argv[1],_sys.argv[2])
