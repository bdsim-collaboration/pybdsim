import os as _os
import matplotlib.pyplot as _plt
import matplotlib.cbook as _cbook
from .. import Data as _Data
from .. import Plot as _Plot

def RebdsimVsRebdsim(rebdsimFiles = [], rebdsimLabels = [], statisticalComparision = False) :

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
    for i, h in enumerate(sorted(histoNamesSet)):
        for j, (f, fn, label) in enumerate(zip(files, rebdsimFiles, rebdsimLabels)) :
            if j == 0:
                histos[h] = []
            histo = f.histogramspy[h]
            histos[h].append(histo)

    # plot histograms
    fig,ax = _plt.subplots(4,3, figsize=(10, 8))
    ax_list = list(_cbook.flatten(ax))
    for i, k  in enumerate(histos.keys()):
        for h in histos[k]:
            _Plot.Histogram1D(h, ax=ax_list[i])
        ax_list[i].set_title(k)
        ax_list[i].legend()
    _plt.tight_layout()

    # compare histos
    if statisticalComparision :
       pass

    return histos