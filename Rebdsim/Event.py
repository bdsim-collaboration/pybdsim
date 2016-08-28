import ROOT as _ROOT
import ROOT.gDirectory as _gDirectory
import Root as _Root
import numpy as _np
import platform as _platform

class Event :
    '''
    Converter and convenience methods for Bdsim root output files in python
    '''


    def __init__(self, filename):
        self._filename = filename
        self._rootFile = _ROOT.TFile(filename)
        self._tree     = self._rootFile.Get("Event")

    def getNumpyBranch(self,branchname,selector):
        '''
        Extract array of event tree
        :param branchname: name of event branch/leaf
        :param selector: root section string
        :return: numpy array of data
        '''
        nSelected = self._tree.Draw(branchname,selector,"goff")
        dat       = self._tree.GetV1();
        dat.SetSize(nSelected)
        datArray= _np.array(dat)
        return datArray

    def make1DHistogram(self, command, selector, name="hist", title="hist", nbins = 100, xlow=-1., xhigh=1.):
        '''
        Use TTree.Draw to create a histogram, useful when the size of the data cannot be extracted using getNumpyBranch
        :param command:
        :param selector:
        :param name: histogram name
        :param title: histogram title
        :param nbins: number of bins
        :param xlow: histogram lowest edge
        :param xhigh: histogram highest edge
        :return: Root.TH1 object
        '''
        h = _ROOT.TH1D(name,title,nbins,xlow,xhigh)
        nSelected = self._tree.Draw(command+" >> "+name,selector,"goff")
        rootH = _gDirectory.Get(name)    # root histogram object
        maplH = _Root.TH1(rootH)         # matplotlib histogram object

        return maplH


    def make2DHistogram(self, command, selector, name="hist", title="hist",
                        xnbins=100, xlow=-1., xhigh=1.,
                        ynbins=100, ylow=-1., yhigh=1.):
        '''
        Use TTree.Draw to create a histogram, useful when the size of the data cannot be extracted using getNumpyBranch
        :param command:
        :param selector:
        :param name: histogram name
        :param title: histogram title
        :param xnbins: x number of bins
        :param xlow: x histogram lowest edge
        :param xhigh: x histogram highest edge
        :param ynbins: y number of bins
        :param ylow: y histogram lowest edge
        :param yhigh: y histogram highest edge
        :return: Root.TH1 object
        '''
        h = _ROOT.TH2D(name, title, xnbins, xlow, xhigh, ynbins, ylow, yhigh)
        nSelected = self._tree.Draw(command + " >> " + name, selector, "goff")
        rootH = _gDirectory.Get(name)  # root histogram object
        maplH = _Root.TH2(rootH)  # matplotlib histogram object

        return maplH