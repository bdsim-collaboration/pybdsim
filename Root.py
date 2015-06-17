# converts ROOT histogram to matplotlib figure

import matplotlib.pyplot as _plt
import numpy as _np
from ROOT import TH1F

#h1 is histogram, later make method

'''
converts 1d ROOT histogram TH1 (https://root.cern.ch/root/html/TH1.html) to
matplotlib.pyplot.bar or matplotlib.pyplot.hist
'''

def GetMetaDataFromROOTHist(hist):
    # naming
    name = hist.GetName()
    title = hist.GetTitle()
    labelX = hist.GetXaxis().GetTitle()
    labelY = hist.GetYaxis().GetTitle()
    return name, title, labelX, labelY

def GetDataFromROOTHist(hist):
    # data
    nbinsX   = hist.GetNbinsX()
    binWidth = []
    content  = []
    centres  = []
    for i in range(nbinsX):
        binWidth.append(hist.GetXaxis().GetBinWidth(i))
        content.append(hist.GetBinContent(i))
        centres.append(hist.GetBinCenter(i))

    return binWidth, content, centres

def PlotTH1Bar(hist, edgecolor='none', color='b'):

    (name, title, labelX, labelY) = GetMetaDataFromROOTHist(hist)
    (binWidth, content, centres) = GetDataFromROOTHist(hist)
    # bar data
    left   = centres - 0.5*_np.array(binWidth)
    height = content
    width  = binWidth

    _plt.figure()
    _plt.bar(left, height, width, edgecolor=edgecolor, color=color)
    _plt.xlabel(labelX)
    _plt.ylabel(labelY)
    _plt.title(title)

def PlotTH1Hist(hist, edgecolor='none', color='b'):
    (name, title, labelX, labelY) = GetMetaDataFromROOTHist(hist)
    (binWidth, content, centres) = GetDataFromROOTHist(hist)
    # hist data
    x       = centres
    bins    = centres - 0.5*_np.array(binWidth)
    weights = content

    _plt.figure()
    _plt.hist(x, bins, weights = weights, edgecolor='none', color='b')
    _plt.xlabel(labelX)
    _plt.ylabel(labelY)
    _plt.title(title)
