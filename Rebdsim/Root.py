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

    def plot(self, keyX, keyY, opt = ''):
        _plt.plot(self.data[keyX], self.data[keyY])

class TH1 :
    def __init__(self, hist):
        self.hist   = hist

        # extract meta data
        self.name   = hist.GetName()
        self.title  = hist.GetTitle()
        self.labelX = hist.GetXaxis().GetTitle()
        self.labelY = hist.GetYaxis().GetTitle()

        # extract data
        nbinsx   = hist.GetNbinsX()
        self.widths   = _np.zeros(nbinsx)
        self.centres  = _np.zeros(nbinsx)
        self.lowedge  = _np.zeros(nbinsx)
        self.highedge = _np.zeros(nbinsx)
        self.contents = _np.zeros(nbinsx)
        self.errors   = _np.zeros(nbinsx)

        for i in range(nbinsx):
            self.widths[i]   = hist.GetXaxis().GetBinWidth(i)
            self.lowedge[i]  = hist.GetBinLowEdge(i)
            self.highedge[i] = hist.GetBinLowEdge(i+1)
            self.contents[i] = hist.GetBinContent(i)
            self.centres[i]  = hist.GetBinCenter(i)
            self.errors[i]   = hist.GetBinError(i)

    def plot(self,opt ='hist'):
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

    def plotPlot(self):
        _plt.plot(self.centres,self.contents)

    def plotErrorbar(self, edgecolor='none', color='b', label=''):
        _plt.errorbar(self.centres,self.contents, self.errors, color=color, label=label)

    def plotBar(self, edgecolor='none', color='b', label=''):
        _plt.bar(self.lowedge, self.contents, self.widths, edgecolor=edgecolor, color=color, label=label)

    def plotHist(self, edgecolor='none', color='b', label=''):
        _plt.hist(self.centres, self.lowedge, weights=self.contents, edgecolor=edgecolor, color=color, label=label)

    def setLabels(self):
        _plt.xlabel(self.labelX)
        _plt.ylabel(self.labelY)