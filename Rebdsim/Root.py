# converts ROOT histogram to matplotlib figure

import matplotlib.pyplot as _plt
import numpy as _np

'''
Wrapper classes for ROOT data to be plotted properly in matplotlib
'''

class TTree :
    def __init__(self, r2n_tree):
        '''
        :param r2n_tree: root_numpy converted tree
        '''
        self.data = r2n_tree

    def Plot(self, keyX, keyY, keyYErr = '', opt = '', label = ''):
        if keyYErr == '' :
            _plt.plot(self.data[keyX], self.data[keyY], opt, label = label)
        else :
            _plt.errorbar(self.data[keyX], self.data[keyY], self.data[keyYErr], opt, label = label)

    def Keys(self):
        return self.data.dtype.names

class TH1 :
    # TODO : TH1 Deal with under/overflows properly
    # TODO : TH1 Equivalent of statistics box
    def __init__(self, hist):
        self.hist   = hist

        # extract meta data
        self.name   = hist.GetName()
        self.title  = hist.GetTitle()
        self.labelX = hist.GetXaxis().GetTitle()
        self.labelY = hist.GetYaxis().GetTitle()

        # extract data
        nbinsx   = hist.GetNbinsX()
        self.entries   = hist.GetEntries()
        self.widths   = _np.zeros(nbinsx)
        self.centres  = _np.zeros(nbinsx)
        self.lowedge  = _np.zeros(nbinsx)
        self.highedge = _np.zeros(nbinsx)
        self.contents = _np.zeros(nbinsx)
        self.errors   = _np.zeros(nbinsx)

        for i in range(nbinsx):
            self.widths[i]   = hist.GetXaxis().GetBinWidth(i)
            self.lowedge[i]  = hist.GetBinLowEdge(i+1)
            self.highedge[i] = hist.GetBinLowEdge(i+1)
            self.centres[i]  = hist.GetBinCenter(i+1)
            self.contents[i] = hist.GetBinContent(i+1)
            self.errors[i]   = hist.GetBinError(i+1)

    def Plot(self,opt ='hist'):
        '''
        ROOT like plotting options for convenience
        :param opt: hist|e1
        :return:
        '''
        if opt.find('hist') != -1 :
            self.plotHist()
        elif opt.find('line') != -1 :
            self.plotPlot()
        elif opt.find('e1') != -1:
            self.plotErrorbar()

        self.setLabels()

    def PlotPlot(self):
        _plt.plot(self.centres,self.contents)

    def PlotErrorbar(self, edgecolor='none', color='b', label=''):
        _plt.errorbar(self.centres,self.contents, self.errors, color=color, label=label)

    def PlotBar(self, edgecolor='none', color='b', label=''):
        _plt.bar(self.lowedge, self.contents, self.widths, edgecolor=edgecolor, color=color, label=label)

    def PlotHist(self, edgecolor='none', color='b', label=''):
        _plt.hist(self.centres, self.lowedge, weights=self.contents, edgecolor=edgecolor, color=color, label=label)

    def SetLabels(self):
        _plt.xlabel(self.labelX)
        _plt.ylabel(self.labelY)


class TH2 :
    # TODO : TH2 Deal with under/overflows properly
    # TODO : TH2 Equivalent of statistics box
    def __init__(self,hist):
        self.hist   = hist

        # extract meta data
        self.name   = hist.GetName()
        self.title  = hist.GetTitle()
        self.labelX = hist.GetXaxis().GetTitle()
        self.labelY = hist.GetYaxis().GetTitle()

        # extract data

        nbinsx   = hist.GetNbinsX()
        nbinsy   = hist.GetNbinsY()
        self.entries   = hist.GetEntries()
        self.xwidths   = _np.zeros(nbinsx)
        self.xcentres  = _np.zeros(nbinsx)
        self.xlowedge  = _np.zeros(nbinsx)
        self.xhighedge = _np.zeros(nbinsx)
        self.ywidths   = _np.zeros(nbinsy)
        self.ycentres  = _np.zeros(nbinsy)
        self.ylowedge  = _np.zeros(nbinsy)
        self.yhighedge = _np.zeros(nbinsy)
        self.contents = _np.zeros((nbinsx,nbinsy))
        self.errors   = _np.zeros((nbinsx,nbinsy))

        for i in range(nbinsx):
            self.xwidths[i]   = hist.GetXaxis().GetBinWidth(i+1)
            self.xlowedge[i]  = hist.GetXaxis().GetBinLowEdge(i+1)
            self.xhighedge[i] = hist.GetXaxis().GetBinLowEdge(i+2)
            self.xcentres[i]  = hist.GetXaxis().GetBinCenter(i+1)

        for i in range(nbinsy):
            self.ywidths[i]   = hist.GetYaxis().GetBinWidth(i+1)
            self.ylowedge[i]  = hist.GetYaxis().GetBinLowEdge(i+1)
            self.yhighedge[i] = hist.GetYaxis().GetBinLowEdge(i+2)
            self.ycentres[i]  = hist.GetYaxis().GetBinCenter(i+1)

        for i in range(nbinsx) :
            for j in range(nbinsy) :
                self.contents[i,j] = hist.GetBinContent(i+1,j+1)
                self.errors[i,j]   = hist.GetBinError(i+1,j+1)

    def Plot(self):
        pass

    def PlotColz(self):
        xx, yy = _np.meshgrid(self.xcentres,self.ycentres)
        _plt.rcParams['image.cmap'] = 'coolwarm'
        _plt.pcolormesh(xx,yy,self.contents)
        # _plt.colorbar()
