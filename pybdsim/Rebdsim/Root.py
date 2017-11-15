"""
Converts ROOT histogram to matplotlib figure
"""

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

        #Extract statistics box data
        self.mean  = hist.GetMean()
        self.stdev = hist.GetStdDev()

        for i in range(nbinsx):
            self.widths[i]   = hist.GetXaxis().GetBinWidth(i)
            self.lowedge[i]  = hist.GetBinLowEdge(i+1)
            self.highedge[i] = hist.GetBinLowEdge(i+1)
            self.centres[i]  = hist.GetBinCenter(i+1)
            self.contents[i] = hist.GetBinContent(i+1)
            self.errors[i]   = hist.GetBinError(i+1)

    def Plot(self,opt ='hist', logx=False, logy=False, outputfilename=None):
        '''
        ROOT like plotting options for convenience
        :param opt: hist|e1
        :return:
        '''
        _plt.figure(num=1, figsize=(11,7), facecolor="w", edgecolor="w")

        if opt.find('hist') != -1 :
            self.PlotHist()
        elif opt.find('line') != -1 :
            self.PlotPlot()
        elif opt.find('e1') != -1:
            self.PlotErrorbar()

        self._SetLabels()
        self._StatBox()

        if logx or logy:
            self._LogAxes(logx, logy)

        if outputfilename != None:
            self._SaveFigure(outputfilename)

    def PlotPlot(self):
        _plt.plot(self.centres,self.contents)

    def PlotErrorbar(self, edgecolor='none', color='b', label=''):
        _plt.errorbar(self.centres,self.contents, self.errors, color=color, label=label)

    def PlotBar(self, edgecolor='none', color='b', label=''):
        _plt.bar(self.lowedge, self.contents, self.widths, edgecolor=edgecolor, color=color, label=label)

    def PlotHist(self, edgecolor='none', color='b', label=''):
        _plt.hist(self.centres, self.lowedge, weights=self.contents, edgecolor=edgecolor, color=color, label=label)

    def _SetLabels(self):
        _plt.xlabel(self.labelX)
        _plt.ylabel(self.labelY)

    def _StatBox(self):
        _plt.plot([],[], linestyle="None", label=self.title)
        _plt.plot([],[], linestyle="None", label=r"Entries".ljust(15)+self._LegNum(self.entries))
        _plt.plot([],[], linestyle="None", label=r"Mean".ljust(15)+self._LegNum(self.mean))
        _plt.plot([],[], linestyle="None", label=r"Std Dev".ljust(14)+self._LegNum(self.stdev))
        leg = _plt.legend(loc=1, frameon=True, edgecolor="k",
                    handlelength=0.05, fontsize="x-small")
        if leg:
            leg.draggable(True,update='bbox')

    def _LogAxes(self, x=False, y=False):
        ax = _plt.gca()
        if x:
            ax.set_xscale("log")
        if y:
            ax.set_yscale("log")

    def _LegNum(self, number):
        n = number #shortcut
        l = str(n)

        if "e" in l:              #Numbers that are already in scientific notation
            ln  = l.split("e")[0]
            le  = l.split("e")[1]
            try:
                lnr = ln[:7]
            except:
                lnr = ln

            nas = lnr+r"x10$^{"+le+r"}$"

        elif n > 1.e6:             #Large numbers (eg. 2375)
            if l[:-1][-1]==("."):  #Take into account trailing .0s (eg. 2375.0)
                ll = len(l)-2
            else:
                ll = len(l)        #ll is the power of 10 (e.g 3)
            lf = l[0]              #The first number will be the integer base (eg. 2)
            try:
                ls = l[1:6]        #Get the fractional base (e.g 375)
            except:
                ls = l[1:]
            if not ls:             #Or add a zero if no fractional base
                ls = "0"
            nas = lf+r"."+ls+r"x10$^{"+str(ll-1)+r"}$" #Put a decimal point and a power of 10

        elif n < 1.e-6:               #Small numbers (eg. 0.0000456)
            lsp  = l.split(".")[1]    #Get digits after the decimal point
            lr   = lsp.split("0")[-1]         #Get the part with no leading zeros (e.g 456)
            nz   = len(lsp.split("0")[-1])-1  #Count the leading zeros
            lf   = lr[0]                      #Get the desired integer base

            try:
                ls   = lr[1:6]     #Geth the fractional base
            except:
                ls   = lr[1:]
            if not ls:
                ls = "0"           #If no fractional base add a zero
            nas  = lf+r"."+ls+r"x10$^{-"+str(nz+2)+r"}$" #Put decimal point and neg power of 10
        else:
            try:
                nas = l[:7]        #If number is small/big enough print without alteration
            except:
                nas = l

        return nas.ljust(11)

    def _SaveFigure(self, outputfilename):
        if '.' in outputfilename:
            outputfilename = outputfilename.split('.')[0]
        _plt.savefig(outputfilename+'.pdf')
        #_plt.savefig(outputfilename+'.png')


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
