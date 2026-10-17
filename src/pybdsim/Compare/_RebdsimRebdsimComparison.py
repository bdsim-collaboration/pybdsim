import os as _os
import matplotlib.pyplot as _plt
import matplotlib.cbook as _cbook
import numpy as _np
from .. import Data as _Data
from .. import Plot as _Plot

def _chi2dof(h1d1,h1d2) :
    dy = h1d1.contents - h1d2.contents
    sigma = h1d1.errors**2 + h1d2.errors**2
    sigma_nonzero = sigma != 0
    return (dy[sigma_nonzero]/sigma[sigma_nonzero]).sum()/len(dy[sigma_nonzero])

def RebdsimVsRebdsim(rebdsimFiles = [],
                     rebdsimLabels = [],
                     histosToCompare = [],
                     histosLabels = [],
                     histosLogx = [],
                     histosLogy = [],
                     defaultHistos = False):

    # check if there are enough lables
    if len(histosToCompare) != len(histosLabels) :
        raise ValueError("Need same number of histosLabels [['x1','y1'], ['x2','y2], ... ] as histosToCompare")

    # if no histos are given
    if histosToCompare == [] :
        defaultHistos = True

    if defaultHistos :
        histosToCompare.extend(['Event/MergedHistograms/PhitsHisto',
                                'Event/MergedHistograms/PlossHisto',
                                'Event/MergedHistograms/ElossHisto',
                                'Event/MergedHistograms/PhitsPEHisto',
                                'Event/MergedHistograms/PlossPEHisto',
                                'Event/MergedHistograms/ElossPEHisto',
                                'Event/MergedHistograms/PFirstAIHisto'])

    # list of loaded rebdsimFiles
    files = []

    # set of histogram names
    histoNamesSet = set()

    # dict key is histoname, value is list of histos
    histos = {}

    firstFile = True
    for fn in rebdsimFiles :

        # check if files exsits
        if not _os.path.isfile(fn) :
            raise ValueError("File %s does not exist" % fn)

        # load file
        f = _Data.Load(fn)

        # check if file is a valid rebdsim file
        if type(f) is not _Data.RebdsimFile :
            raise ValueError("File %s is not a valid rebdsim file" % fn)

        files.append(f)

        # verify the same histograms are in all files
        f_histoNames = f.histogramspy.keys()
        if firstFile :
            histoNamesSet = set(f_histoNames)
            firstFile = False
        else :
            if histoNamesSet != set(f_histoNames) :
                raise ValueError("File %s does not have all histos" % fn)

    # gather histograms for statistical test in histos
    for i, h in enumerate(histosToCompare):
        for j, (f, fn, label) in enumerate(zip(files, rebdsimFiles, rebdsimLabels)) :
            if j == 0:
                histos[h] = []
            histo = f.histogramspy[h]
            histos[h].append(histo)

    # plot histograms
    fig,ax = _plt.subplots(3,3, figsize=(10, 8))
    ax_list = list(_cbook.flatten(ax))

    # chi2
    chi2 = {}
    for i, (k, (xl,yl), lx, ly, pl)  in enumerate(zip(histos.keys(),histosLabels, histosLogx, histosLogy, rebdsimLabels)) :
        h1d1 = None
        for h in histos[k]:

            # first histogram
            if h1d1 is None :
                h1d1 = h

            chi2dof = _chi2dof(h1d1, h)

            _Plot.Histogram1D(h, ax=ax_list[i], log=ly, xlabel=xl, ylabel=yl, label=pl+" $\\chi^2$/ndf=" +str(round(chi2dof,2)))

        ax_list[i].set_title(k, fontsize=9)
        ax_list[i].legend(loc=1, fontsize=9)
        if lx :
            ax_list[i].set_xscale('log')

    # clear empty axes
    for ax in fig.axes:
        if not ax.has_data():
            ax.remove()

    # tight layout
    _plt.tight_layout()

    return histos