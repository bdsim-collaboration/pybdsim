"""
Useful plots for bdsim output

"""
import Data as _Data
import pymadx as _pymadx

import matplotlib as _matplotlib
from matplotlib.colors import LogNorm as _LogNorm
import matplotlib.pyplot as _plt
import matplotlib.patches as _patches
import matplotlib.ticker as _ticker
import numpy as _np
import string as _string

from _General import CheckItsBDSAsciiData as _CheckItsBDSAsciiData

class _My_Axes(_matplotlib.axes.Axes):
    """
    Inherit matplotlib.axes.Axes but override pan action for mouse.
    Only allow horizontal panning - useful for lattice axes.
    """
    name = "_My_Axes"
    def drag_pan(self, button, key, x, y):
        _matplotlib.axes.Axes.drag_pan(self, button, 'x', x, y) # pretend key=='x'

#register the new class of axes
_matplotlib.projections.register_projection(_My_Axes)

def MadxTfsBetaSimple(tfsfile, title='', outputfilename=None):
    """
    A forward to the pymadx.Plot.PlotTfsBetaSimple function.
    """
    _pymadx.Plot.PlotTfsBetaSimple(tfsfile,title,outputfilename)

def MadxTfsBeta(tfsfile, title='', outputfilename=None):
    """
    A forward to the pymadx.Plot.PlotTfsBeta function.
    """
    _pymadx.Plot.PlotTfsBeta(tfsfile,title,outputfilename)

def AddMachineLatticeToFigure(figure,tfsfile, tightLayout=True):
    """
    A forward to the pymadx.Plot.AddMachineLatticeToFigure function.
    """
    _pymadx.Plot.AddMachineLatticeToFigure(figure, tfsfile, tightLayout)

def ProvideWrappedS(sArray, index):
    s = sArray #shortcut
    smax = s[-1]
    sind = s[index]
    snewa = s[index:]
    snewa = snewa - sind
    snewb = s[:index]
    snewb = snewb + (smax - sind)
    snew  = _np.concatentate((snewa,snewb))
    return snew

def _SetMachineAxesStyle(ax):
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)

def _PrepareMachineAxes(figure):
    # create new machine axis with proportions 6 : 1
    axmachine = figure.add_subplot(911, projection="_My_Axes")
    _SetMachineAxesStyle(axmachine)
    return axmachine

def _AdjustExistingAxes(figure, fraction=0.9, tightLayout=True):
    """
    Fraction is fraction of height all subplots will be after adjustment.
    Default is 0.9 for 90% of height. 
    """
    # we have to set tight layout before adjustment otherwise if called
    # later it will cause an overlap with the machine diagram
    if (tightLayout):
        _plt.tight_layout()
    
    axs = figure.get_axes()
    
    for ax in axs:
        bbox = ax.get_position()
        bbox.y0 = bbox.y0 * fraction
        bbox.y1 = bbox.y1 * fraction
        ax.set_position(bbox)

def AddMachineLatticeFromSurveyToFigureMultiple(figure, machines, tightLayout=True):
    """
    Similar to AddMachineLatticeFromSurveyToFigure() but accepts multiple machines.
    """
    d = _CheckItsBDSAsciiData(machines[0])
    if len(args) > 1:
        for machine in machines[1:]:
            d.ConcatenateMachine(machine)
    return d

def AddMachineLatticeFromSurveyToFigure(figure, surveyfile, tightLayout=True):
    """
    Add a machine diagram to the top of the plot in a current figure

    """
    import Data as _Data
    sf = _CheckItsBDSAsciiData(surveyfile)
    # we don't need to check this has the required columns because we control a
    # BDSIM survey contents.
    
    axoptics  = figure.get_axes()[0]
    _AdjustExistingAxes(figure, tightLayout=tightLayout)
    axmachine = _PrepareMachineAxes(figure)

    _DrawMachineLattice(axmachine,sf)

    #put callbacks for linked scrolling
    def MachineXlim(ax): 
        axmachine.set_autoscale_on(False)
        axoptics.set_xlim(axmachine.get_xlim())

    def Click(a) : 
        if a.button == 3:
            try:
                print 'Closest element: ',sf.NameFromNearestS(a.xdata)
            except ValueError:
                pass # don't complain if the S is out of bounds
            
    MachineXlim(axmachine)
    axmachine.callbacks.connect('xlim_changed', MachineXlim)
    figure.canvas.mpl_connect('button_press_event', Click)

def _DrawMachineLattice(axesinstance,bdsasciidataobject):
    ax  = axesinstance #handy shortcut
    bds = bdsasciidataobject
    
    def DrawBend(start,length,color='b',alpha=1.0):
        br = _patches.Rectangle((start,-0.1),length,0.2,color=color,alpha=alpha)
        ax.add_patch(br)
    def DrawQuad(start,length,k1,color='r',alpha=1.0):
        if k1 > 0 :
            qr = _patches.Rectangle((start,0),length,0.2,color=color,alpha=alpha)
        elif k1 < 0: 
            qr = _patches.Rectangle((start,-0.2),length,0.2,color=color,alpha=alpha)
        else:
            #quadrupole off
            qr = _patches.Rectangle((start,-0.1),length,0.2,color='#B2B2B2',alpha=0.5) #a nice grey in hex
        ax.add_patch(qr)
    def DrawHex(start,length,color,alpha=1.0):
        s = start
        l = length
        edges = _np.array([[s,-0.1],[s,0.1],[s+l/2.,0.13],[s+l,0.1],[s+l,-0.1],[s+l/2.,-0.13]])
        sr = _patches.Polygon(edges,color=color,fill=True,alpha=alpha)
        ax.add_patch(sr)
    def DrawRect(start,length,color,alpha=1.0):
        rect = _patches.Rectangle((start,-0.1),length,0.2,color=color,alpha=alpha)
        ax.add_patch(rect)
    def DrawLine(start,color,alpha=1.0):
        ax.plot([start,start],[-0.2,0.2],'-',color=color,alpha=alpha)
            
    # plot beam line
    smax = bds.SEnd()[-1]
    ax.plot([0,smax],[0,0],'k-',lw=1)
    ax.set_ylim(-0.2,0.2)
 
    # loop over elements and Draw on beamline
    types   = bds.Type()
    lengths = bds.ArcLength()
    starts  = bds.SStart()
    k1      = bds.k1()

    for i in range(len(bds)):
        kw = types[i]
        if kw == 'quadrupole': 
            DrawQuad(starts[i],lengths[i],k1[i], u'#d10000') #red
        elif kw == 'rbend': 
            DrawBend(starts[i],lengths[i], u'#0066cc') #blue
        elif kw == 'sbend': 
            DrawBend(starts[i],lengths[i], u'#0066cc') #blue
        elif kw == 'hkicker':
            DrawRect(starts[i],lengths[i], u'#4c33b2') #purple
        elif kw == 'vkicker':
            DrawRect(starts[i],lengths[i], u'#ba55d3') #medium orchid
        elif kw == 'rcol': 
            DrawRect(starts[i],lengths[i],'k')
        elif kw == 'ecol': 
            DrawRect(starts[i],lengths[i],'k')
        elif kw == 'degrader': 
            DrawRect(starts[i],lengths[i],'k')
        elif kw == 'sextupole':
            DrawHex(starts[i],lengths[i], u'#ffcc00') #yellow
        elif kw == 'octupole':
            DrawHex(starts[i],lengths[i], u'#00994c') #green
        elif kw == 'decapole':
            DrawHex(starts[i],lengths[i], u'#4c33b2') #purple
        elif kw == 'drift':
            pass
        elif kw == 'multipole':
            DrawHex(starts[i],lengths[i],'grey',alpha=0.5)
        else:
            #unknown so make light in alpha
            if lengths[i] > 1e-1:
                DrawRect(starts[i],lengths[i],'#cccccc',alpha=0.1) #light grey
            else:
                #relatively short element - just draw a line
                DrawLine(starts[i],'#cccccc',alpha=0.1)


# Predefined lists of tuples for making the standard plots,
# format = (optical_var_name, optical_var_error_name, legend_name)

_BETA = [("Beta_x", "Sigma_Beta_x", r'$\beta_{x}$'),
         ("Beta_y", "Sigma_Beta_y", r'$\beta_{y}$')]

_ALPHA = [("Alpha_x", "Sigma_Alpha_x", r"$\alpha_{x}$"),
          ("Alpha_y", "Sigma_Alpha_y", r"$\alpha_{y}$")]

_DISP = [("Disp_x", "Sigma_Disp_x", r"$D_{x}$"),
         ("Disp_y", "Sigma_Disp_y", r"$D_{y}$")]

_DISP_P = [("Disp_xp", "Sigma_Disp_xp", r"$D_{p_{x}}$"),
           ("Disp_yp", "Sigma_Disp_yp", r"$D_{p_{y}}$")]

_SIGMA = [("Sigma_x", "Sigma_Sigma_x", r"$\sigma_{x}$"),
          ("Sigma_y", "Sigma_Sigma_y", r"$\sigma_{y}$")]

_SIGMA_P = [("Sigma_xp", "Sigma_Sigma_xp", r"$\sigma_{xp}$"),
            ("Sigma_yp", "Sigma_Sigma_yp", r"$\sigma_{yp}$")]

_MEAN = [("Mean_x", "Sigma_Mean_x", r"$\bar{x}$"),
         ("Mean_y", "Sigma_Mean_y", r"$\bar{y}$")]

def _make_plotter(plot_info_tuples, x_label, y_label, title):
    def f_out(bds, outputfilename= None, survey=None, **kwargs):
        sf = _CheckItsBDSAsciiData(bds)

        # options
        tightLayout = True
        if 'tightLayout' in kwargs:
            tightLayout = kwargs['tightLayout']

        # Get the initial N for the two sources
        first_nparticles = sf.Npart()[0]

        plot = _plt.figure(title, figsize=(9,5), **kwargs)
        # Loop over the variables in plot_info_tuples and draw the plots.
        for var, error, legend_name in plot_info_tuples:
            _plt.errorbar(sf.GetColumn('S'),
                          sf.GetColumn(var),
                          yerr=sf.GetColumn(error),
                          label="{} {}; N = {:.1E}".format(
                              "", legend_name, first_nparticles),
                          capsize=3, **kwargs)

        # Set axis labels and draw legend
        axes = _plt.gcf().gca()
        axes.set_ylabel(y_label)
        axes.set_xlabel(x_label)
        axes.legend(loc='best')

        if survey is not None:
            AddMachineLatticeFromSurveyToFigure(plot, survey)
        if (tightLayout):
            _plt.tight_layout()

        _plt.show(block=False)

        if outputfilename != None:
            if '.' in outputfilename:
                outputfilename = outputfilename.split('.')[0]
            _plt.savefig(outputfilename + '.pdf')
            _plt.savefig(outputfilename + '.png')

        return plot
    return f_out

PlotBeta   = _make_plotter(_BETA,    "S / m", r"$\beta_{x,y}$ / m",      "Beta")
PlotAlpha  = _make_plotter(_ALPHA,   "S / m", r"$\alpha_{x,y}$ / m",     "Alpha")
PlotDisp   = _make_plotter(_DISP,    "S / m", r"$D_{x,y} / m$",          "Dispersion")
PlotDispP  = _make_plotter(_DISP_P,  "S / m", r"$D_{p_{x},p_{y}}$ / m",  "Momentum_Dispersion")
PlotSigma  = _make_plotter(_SIGMA,   "S / m", r"$\sigma_{x,y}$ / m",     "Sigma")
PlotSigmaP = _make_plotter(_SIGMA_P, "S / m", r"$\sigma_{xp,yp}$ / rad", "SigmaP")
PlotMean   = _make_plotter(_MEAN,    "S / m", r"$\bar{x}, \bar{y}$ / m", "Mean")


def PlotBdsimOptics(rebdsimOpticsOutput, outputfilename=None, survey=None, **kwargs):
    """
    Display all the optical function plots for a rebdsim optics root file.
    """
    bdsdata = rebdsimOpticsOutput # shortcut
    PlotBeta(bdsdata,   survey=survey, outputfilename=outputfilename, **kwargs)
    PlotAlpha(bdsdata,  survey=survey, outputfilename=outputfilename, **kwargs)
    PlotDisp(bdsdata,   survey=survey, outputfilename=outputfilename, **kwargs)
    PlotDispP(bdsdata,  survey=survey, outputfilename=outputfilename, **kwargs)
    PlotSigma(bdsdata,  survey=survey, outputfilename=outputfilename, **kwargs)
    PlotSigmaP(bdsdata, survey=survey, outputfilename=outputfilename, **kwargs)
    PlotMean(bdsdata,   survey=survey, outputfilename=outputfilename, **kwargs)
    
def Histogram1D(histogram, xlabel=None, ylabel=None, title=None, **errorbarKwargs):
    """
    Plot a pybdsim.Data.TH1 instance.
    """
    h = histogram
    f = _plt.figure(figsize=(10,5))
    ax = f.add_subplot(111)
    ax.errorbar(h.xcentres, h.contents, yerr=h.errors,xerr=h.xwidths*0.5, fmt='.', **errorbarKwargs)
    if xlabel is None:
        ax.set_xlabel(h.xlabel)
    else:
        ax.set_xlabel(xlabel)
    if ylabel is None:
        ax.set_ylabel(h.ylabel)
    else:
        ax.set_ylabel(ylabel)
    if title is None:
        f.suptitle(h.title)
    elif title is "":
        pass
    else:
        f.suptitle(title)
    return f

def Histogram2D(histogram, logNorm=False, xlogscale=False, ylocscale=False, zlabel=""):
    """
    Plot a pybdsim.Data.TH2 instance.
    logNorm   - logarithmic colour scale
    xlogscale - x axis logarithmic scale
    ylogscale - y axis logarithmic scale
    zlabel    - label for color bar scale
    """
    h = histogram
    f = _plt.figure()
    x, y = _np.meshgrid(h.xcentres,h.ycentres)
    ext = [_np.min(h.xcentres),_np.max(h.xcentres),_np.min(h.ycentres),_np.max(h.ycentres)]
    if logNorm:
        _plt.imshow(h.contents[::-1,:], extent=ext, aspect='equal', norm=_LogNorm())
        _plt.colorbar()
    else:
        _plt.imshow(h.contents[::-1,:], extent=ext, aspect='equal')
        _plt.colorbar(format='%.0e', label=zlabel)

    if xlogscale:
        _plt.xscale('log')
    if ylocscale:
        _plt.yscale('log')

    _plt.xlabel(h.xlabel)
    _plt.ylabel(h.ylabel)
    _plt.title(h.title)
    return f

def Histogram3D(th3):
    """
    Plot a pybdsim.Data.TH1 instance - TBC
    """
    print 'Not written yet - TBC'

def PrimaryPhaseSpace(filename, outputfilename=None):
    """
    Load a BDSIM output file and plot primary phase space. Only accepts raw BDSIM output.
    """
    PhaseSpaceFromFile(filename, 0, outputfilename=outputfilename)

def PhaseSpaceFromFile(filename, samplerIndexOrName=0, outputfilename=None):
    """
    Load a BDSIM output file and plot the phase space of a sampler (default the primaries).
    Only accepts raw BDSIM output.
    """
    import Data as _Data
    d = _Data.Load(filename)
    psd = _Data.PhaseSpaceData(d,samplerIndexOrName=samplerIndexOrName)
    PhaseSpace(psd, outputfilename)

def EnergyDeposition(filename, outputfilename=None, tfssurvey=None, bdsimsurvey=None):
    """
    Plot the energy deposition from a REBDSIM output file - uses premade merged histograms.

    Optional either Twiss table for MADX or BDSIM Survey to add machine diagram to plot. If both are provided,
    the machine diagram is plotted from the MADX survey.
    """
    import Data as _Data
    d = _Data.Load(filename)
    if type(d) is not _Data.RebdsimFile:
        raise IOError("Not a rebdsim file")
    eloss = d.histogramspy['Event/MergedHistograms/ElossHisto']

    xwidth    = eloss.xwidths[0]
    xlabel = r"S (m)"
    ylabel = r"Energy Deposition / Event (Gev / {}) m".format(xwidth)
    f = Histogram1D(eloss, xlabel='S (m)', ylabel=ylabel, title="")

    ax = f.get_axes()[0]
    ax.set_yscale('log')

    if tfssurvey:
        AddMachineLatticeToFigure(f, tfssurvey)
    elif bdsimsurvey:
        AddMachineLatticeFromSurveyToFigure(f, bdsimsurvey)

    if outputfilename is not None:
        _plt.savefig(outputfilename)

def EnergyDepositionCoded(filename, outputfilename=None, tfssurvey=None, bdsimsurvey=None, warmaperinfo=None, **kwargs):
    """
    Plot the energy deposition from a REBDSIM output file - uses premade merged histograms.

    Optional either Twiss table for MADX or BDSIM Survey to add machine diagram to plot. 
    If both are provided, the machine diagram is plotted from the MADX survey.

    If a BDSIM survey is provided, collimator positions and dimensions can be taken and 
    used to split losses into categories: collimator, warm and cold based on warm aperture
    infomation provided. To enable this, the "warmaperinfo" option must be set according 
    to the prescription below.

    The user can supply a list of upper and lower edges of warm regions or give the path
    to a coulmn-formated data file with this information via the "warmaperinfo" option.
    Set warmaperinfo=1 to treat all non-collimator losses as warm or set warmaperinfo=-1 
    to treat them as cold. Default is not perform the loss classification.

    If no warm aperture information is provided, the plotting falls back to the standard 
    simple plotting provided by a pybdsimm.Plot.Hisgogram1D interface.

    Args:
        filename       (str):  Path to the REBDSIM data file
        outputfilename (str, optional):  Path where to save a pdf file with the plot. Default is None.
    
        tfssurvey      (str, optional):  Path to MADX survey used to plot machine diagram on top of figure. Default is None.
    
        tfssurvey      (str, optional):  Path to BDSIM survey used to classify losses into collimator/warm/cold and/or plot machine diagram on top of figure. Default is None.
    
        warmaperinfo  (int|list|str, optional): Information about warm aperture in the machine. Default is None.
        \*\*kwargs: Arbitrary keyword arguments.

    Kwargs:
        skipMachineLattice   (bool): If enabled, use the BDSIM survey to classify losses, but do not plot the lattice on top.

    Returns:
        matplotlib.pyplot.Figure object

    """
    if not warmaperinfo:
        EnergyDeposition(filename, outputfilename, tfssurvey, bdsimsurvey)

    else:
        import Data as _Data
        d = _Data.Load(filename)
        if type(d) is not _Data.RebdsimFile:
            raise IOError("Not a rebdsim file")
        eloss = d.histogramspy['Event/MergedHistograms/ElossHisto']

        xwidth    = eloss.xwidths[0]
        xlabel = r"S (m)"
        ylabel = r"Energy Deposition / Event (Gev / {}) m".format(xwidth)

        skipMachineLattice = False
        if "skipMachineLattice" in kwargs:
            skipMachineLattice = kwargs["skipMachineLattice"]

        print "Note that collimator/warm/cold loss classification is approximate for binned data and missclasification probability increases with bin sze."

        collimators=[]
        if bdsimsurvey:
            bsu   = _Data.Load(bdsimsurvey)
            relfields = [bsu.Name(), bsu.Type(), bsu.SStart(), bsu.SEnd()]
            collimators = [element for element in zip(*relfields) if element[1]=="rcol"]

        warmapers=[]
        if warmaperinfo:
            if warmaperinfo == -1:
                warmapers = []
            elif warmaperinfo == 1:
                warmapers = [[0, 1.e9]] #Crude, but no need to be exact
            elif isinstance(warmaperinfo, list):
                warmapers = warmaperinfo
            elif isinstance(warmaperinfo, str):
                warmapers=_np.genfromtxt(warmaperinfo)
            else:
                raise SystemExit("Unrecognised warmaperinfo option: {}".format(aperinfo))

        coll_binmask = []
        warm_binmask = []
        cold_binmask = []

        ledges   = eloss.xlowedge
        contents = eloss.contents
        errors   = eloss.errors

        for i in range(len(contents)):
            """
            The check here is done on the presence of a lower bin edge in a region of
            interest (collimator or warm segment). For bin of similar or larger size
            than the size of the region of interest, a misidenfication is possible.
            Can reduce probabliluty of misclassification by also checking for the presencce
            of an upper bin edge, but it increasses processing time and ultimately, for
            bins that are too large it is impossible to overcome resolution constraints.
            """
            in_coll=False
            in_warm=False
            for coll in collimators:
                smin, smax = coll[2], coll[3]
                if ledges[i]>smin and ledges[i]<smax:
                    in_coll=True

            for waper in warmapers:
                smin, smax = waper[0], waper[1]
                if ledges[i]>smin and ledges[i]<smax:
                    in_warm=True

            coll_binmask.append(int(in_coll)) #collimators have priority over warm aper
            warm_binmask.append(int(in_warm and not in_coll))
            cold_binmask.append(int(not in_coll and not in_warm))

        coll_binmask = _np.array(coll_binmask)
        warm_binmask = _np.array(warm_binmask)
        cold_binmask = _np.array(cold_binmask)

        coll_bins = _np.multiply(contents, coll_binmask)
        coll_errs = _np.multiply(errors, coll_binmask)
        warm_bins = _np.multiply(contents, warm_binmask)
        warm_errs = _np.multiply(errors, warm_binmask)
        cold_bins = _np.multiply(contents, cold_binmask)
        cold_errs = _np.multiply(errors, cold_binmask)

        scale=1

        coll_col = "k"
        warm_col = "r"
        cold_col = "b"

        f = _plt.figure(figsize=(10,5))
        ax  = _plt.gca()

        if any(coll_binmask):
            ax.plot(ledges, scale*coll_bins, ls="steps", color=coll_col, label="Collimator", zorder=10)
            ax.errorbar(ledges-xwidth/2, scale*coll_bins, scale*coll_errs, linestyle="*", fmt="none", color=coll_col, zorder=10)

        if any(warm_binmask):
            ax.plot(ledges, scale*warm_bins, ls="steps", color=warm_col, label="Warm")
            ax.errorbar(ledges-xwidth/2, scale*warm_bins, scale*warm_errs, linestyle="", fmt="none", color=warm_col)

        if any(cold_binmask):
            ax.plot(ledges, scale*cold_bins, ls="steps", color=cold_col, label="Cold", zorder=5)
            ax.errorbar(ledges-xwidth/2, scale*cold_bins, scale*cold_errs, linestyle="", fmt="none", color=cold_col, zorder=5)

        ax.set_yscale("log", nonposy='clip')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.yaxis.set_major_locator(_plt.LogLocator(subs=(1.0,))) #TODO: Find a way to disable auto ticks and always display all int powers
        ax.yaxis.grid(which="major", linestyle='--')
        _plt.legend(fontsize="small", framealpha=1)# bbox_to_anchor=(0.85, 1), loc=2, borderaxespad=0., framealpha=1)

    if tfssurvey:
        AddMachineLatticeToFigure(f, tfssurvey)
    elif bdsimsurvey and not skipMachineLattice:
        #AddMachineLatticeFromSurveyToFigure(f, bdsimsurvey) #TODO: Fix this, currenly gives an error
        print "Lattice diagram not added, module under maintenance"

    if outputfilename is not None:
        _plt.savefig(outputfilename)

def LossAndEnergyDeposition(filename, outputfilename=None, tfssurvey=None, bdsimsurvey=None):
    """
    Load a REBDSIM output file and plot the merged histograms automatically generated by BDSIM.
    
    Optional either Twiss table for MADX or BDSIM Survey to add machine diagram to plot.
    """
    import Data as _Data
    d = _Data.Load(filename)
    if type(d) is not _Data.RebdsimFile:
        raise IOError("Not a rebdsim file")
    phits = d.histogramspy['Event/MergedHistograms/PhitsHisto']
    ploss = d.histogramspy['Event/MergedHistograms/PlossHisto']
    eloss = d.histogramspy['Event/MergedHistograms/ElossHisto']

    fig = _plt.figure(figsize=(10,5))
    ax1 = fig.add_subplot(111)
    ax1.set_yscale('log')
    ax1.set_ylabel('Fractional Beam Loss')

    ax1.errorbar(phits.xcentres, phits.contents, xerr=phits.xwidths*0.5,yerr=phits.errors,
                 fmt='bs',elinewidth=0.8, label='Primary Hit', markersize=3)
    ax1.errorbar(ploss.xcentres, ploss.contents, xerr=ploss.xwidths*0.5,yerr=ploss.errors,
                 fmt='r.',elinewidth=0.8, label='Primary Loss', markersize=6)

    ax2 = ax1.twinx()
    ax2.errorbar(eloss.xcentres, eloss.contents, xerr=eloss.xwidths*0.5,yerr=eloss.errors,
                 fmt='k,',elinewidth=0.8, label='Energy Deposition')
    ax2.set_yscale('log')

    xwidth = eloss.xwidths[0]
    ylabel = 'Energy Deposition / Event (GeV / '+str(xwidth)+" m)"
    ax2.set_ylabel(ylabel)

    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    
    ax1.set_xlabel('S (m)')

    if tfssurvey:
        AddMachineLatticeToFigure(fig, tfssurvey)
    elif bdsimsurvey:
        AddMachineLatticeFromSurveyToFigure(fig, bdsimsurvey)

    if outputfilename is not None:
        _plt.savefig(outputfilename)
    
def PhaseSpace(data, nbins=None, outputfilename=None):
    """
    Make two figures for coordinates and correlations.

    Number of bins chosen depending on number of samples.

    'outputfilename' is name without extension.
    """
    if nbins == None:
        entries = data._entries
        nbins = int(_np.ceil(25*(entries/100.)**0.2))
        print 'Automatic number of bins> ',nbins
    
    d = data.data #shortcut
    f = _plt.figure(figsize=(12,6))

    axX = f.add_subplot(241)
    axX.hist(d['x'],nbins)
    axX.set_xlabel('X (m)')

    axY = f.add_subplot(242)
    axY.hist(d['y'],nbins)
    axY.set_xlabel('Y (m)')

    axZ = f.add_subplot(243)
    axZ.hist(d['z'],nbins)
    axZ.set_xlabel('Z (m)')

    axE = f.add_subplot(244)
    axE.hist(d['energy'],nbins)
    axE.set_xlabel('E (GeV)')

    axXp = f.add_subplot(245)
    axXp.hist(d['xp'],nbins)
    axXp.set_xlabel('X$^{\prime}$')

    axYp = f.add_subplot(246)
    axYp.hist(d['yp'],nbins)
    axYp.set_xlabel('Y$^{\prime}$')

    axZp = f.add_subplot(247)
    axZp.hist(d['zp'],nbins)
    axZp.set_xlabel('Z$^{\prime}$')

    axT = f.add_subplot(248)
    axT.hist(d['T'],nbins)
    axT.set_xlabel('T (ns)')

    _plt.suptitle('Coordinates at '+data.samplerName,fontsize='xx-large')
    _plt.tight_layout()
    _plt.subplots_adjust(top=0.92)

    f2 = _plt.figure(figsize=(10,6))

    axXXP = f2.add_subplot(231)
    axXXP.hist2d(d['x'],d['xp'],bins=nbins,cmin=1)
    axXXP.set_xlabel('X (m)')
    axXXP.set_ylabel('X$^{\prime}$')

    axYYP = f2.add_subplot(232)
    axYYP.hist2d(d['y'],d['yp'],bins=nbins,cmin=1)
    axYYP.set_xlabel('Y (m)')
    axYYP.set_ylabel('Y$^{\prime}$')

    axYPYP = f2.add_subplot(233)
    axYPYP.hist2d(d['xp'],d['yp'],bins=nbins,cmin=1)
    axYPYP.set_xlabel('X$^{\prime}$')
    axYPYP.set_ylabel('Y$^{\prime}$')
    
    axXY = f2.add_subplot(234)
    axXY.hist2d(d['x'],d['y'],bins=nbins,cmin=1)
    axXY.set_xlabel('X (m)')
    axXY.set_ylabel('Y (m)')

    axXE = f2.add_subplot(235)
    axXE.hist2d(d['energy'],d['x'],bins=nbins,cmin=1)
    axXE.set_xlabel('Energy (GeV)')
    axXE.set_ylabel('X (m)')

    axYE = f2.add_subplot(236)
    axYE.hist2d(d['energy'],d['y'],bins=nbins,cmin=1)
    axYE.set_xlabel('Energy (GeV)')
    axYE.set_ylabel('Y (m)')
    
    _plt.suptitle('Correlations at '+data.samplerName,fontsize='xx-large')
    _plt.tight_layout()
    _plt.subplots_adjust(top=0.92)

    if outputfilename != None:
        if '.' in outputfilename:
            outputfilename = outputfilename.split('.')[0]
        _plt.savefig(outputfilename + '.pdf')
        _plt.savefig(outputfilename + '.png')

def _fmtCbar(x, pos): #Format in scientific notation and make vals < 1 = 0
    if float(x) == 1.0:
        fst = r"$1$" #For a histogram valuesa smalled that 1 are set to 0
    else:            #Such values are set as dummies to allow log plots
        a, b = '{:.0e}'.format(x).split('e')
        b = int(b)
        fst = r'$10^{{{}}}$'.format(b)
    return fst
