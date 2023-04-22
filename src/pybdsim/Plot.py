"""
Useful plots for bdsim output

"""
from .import Data as _Data
from .import Constants as _Constants
import pymadx as _pymadx

import copy as _copy
import matplotlib as _matplotlib
from matplotlib.colors import LogNorm as _LogNorm
import matplotlib.pyplot as _plt
import matplotlib.patches as _patches
import matplotlib.ticker as _ticker
import numpy as _np
import string as _string
import datetime as _datetime
from matplotlib.backends.backend_pdf import PdfPages as _PdfPages
from scipy import constants as _con
import os.path as _ospath

from ._General import CheckItsBDSAsciiData as _CheckItsBDSAsciiData
from ._General import CheckBdsimDataHasSurveyModel as _CheckBdsimDataHasSurveyModel

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

_defaultFigureSize=(12,6)

def MadxTfsBeta(tfsfile, title='', outputfilename=None):
    """
    A forward to the pymadx.Plot.PlotTfsBeta function.
    """
    _pymadx.Plot.Beta(tfsfile,title,outputfilename)

def AddMachineLatticeToFigure(figure, tfsfile, tightLayout=True):
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
    snew  = _np.concatenate((snewa,snewb))
    return snew

def _SetMachineAxesStyle(ax):
    ax.set_facecolor('none') # make background transparent to allow scientific notation
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
    if len(machines) > 1:
        for machine in machines[1:]:
            d.ConcatenateMachine(machine)
    return d

def AddMachineLatticeFromSurveyToFigure(figure, surveyfile,
                                        tightLayout=True, sOffset=0., fraction=0.9):
    """
    Add a machine diagram to the top of the plot in a current figure
    sOffset offsets survey along s
    fraction controls fraction of the figure for the plot, the remainder being used for the survey
    """
    from . import Data as _Data
    if isinstance(surveyfile, str) and not _ospath.isfile(surveyfile):
        raise IOError("Survey not found: ", surveyfile)
    if _CheckBdsimDataHasSurveyModel(surveyfile):
        sf = _Data.Load(surveyfile).model
    else:
        sf = _CheckItsBDSAsciiData(surveyfile)

    # we don't need to check this has the required columns because we control a
    # BDSIM survey contents.

    axoptics  = figure.get_axes()
    _AdjustExistingAxes(figure, fraction=fraction, tightLayout=tightLayout)
    axmachine = _PrepareMachineAxes(figure)
    axmachine.margins(x=0.02)

    DrawMachineLattice(axmachine, sf, sOffset=sOffset)

    #put callbacks for linked scrolling
    def MachineXlim(ax):
        axmachine.set_autoscale_on(False)
        for ax in axoptics : 
            ax.set_xlim(axmachine.get_xlim())

    def Click(a) :
        if a.button == 3:
            try:
                print('Closest element: ',sf.NameFromNearestS(a.xdata - sOffset))
            except ValueError:
                pass # don't complain if the S is out of bounds

    MachineXlim(axmachine)
    axmachine.callbacks.connect('xlim_changed', MachineXlim)
    figure.canvas.mpl_connect('button_press_event', Click)


def DrawMachineLattice(axesinstance, bdsasciidataobject, sOffset=0.0):
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

    # loop over elements and Draw on beamline
    types   = bds.Type()
    lengths = bds.ArcLength()
    starts  = bds.SStart()
    starts += sOffset
    k1      = bds.k1()

    for i in range(len(bds)):
        kw = types[i]
        if kw == 'quadrupole':
            DrawQuad(starts[i],lengths[i],k1[i], u'#d10000') #red
        elif kw == 'rbend':
            DrawBend(starts[i],lengths[i], u'#0066cc') #blue
        elif kw == 'sbend':
            DrawBend(starts[i],lengths[i], u'#0066cc') #blue
        elif kw == 'dipolefringe':
            DrawBend(starts[i],lengths[i], u'#0066cc') #blue
        elif kw == 'hkicker':
            DrawRect(starts[i],lengths[i], u'#4c33b2') #purple
        elif kw == 'vkicker':
            DrawRect(starts[i],lengths[i], u'#ba55d3') #medium orchid
        elif kw == 'rcol' or kw == 'ecol' or kw == 'jcol':
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
        elif kw == 'gap':
            pass
        elif kw == 'multipole':
            DrawHex(starts[i],lengths[i],'grey',alpha=0.5)
        elif kw == 'solenoid':
            DrawRect(starts[i],lengths[i], u'#ff8800') #orange
        elif kw == 'shield':
            DrawRect(starts[i],lengths[i], u'#808080') #dark grey
        elif kw == 'rf' or kw == 'rfcavity' or kw == 'cavity_pillbox':
            DrawRect(starts[i],lengths[i], u'#768799') #srf grey
        else:
            #unknown so make light in alpha
            if lengths[i] > 1e-1:
                DrawRect(starts[i],lengths[i],'#cccccc',alpha=0.1) #light grey
            else:
                #relatively short element - just draw a line
                DrawLine(starts[i],'#cccccc',alpha=0.1)

    # plot beam line
    smax = bds.SEnd()[-1] + sOffset
    ax.plot([sOffset, smax],[0,0],'k-',lw=1)
    ax.set_ylim(-0.2,0.2)
    ax.set_xlim(sOffset, smax)

def SubplotsWithDrawnMachineLattice(survey, nrows=2,
                                    machine_plot_gap=0.01,
                                    gridspec_kw=None,
                                    subplots_kw=None, **fig_kw):
    """
    Create a figure with a single column of axes, sharing the
    x-axis by default, with the machine drawn from the provided survey
    on the top row axes.  nrows gives the number of axes, the first is
    always the machine lattice.  by default 2 are drawn, the first for
    the machine, and the second for any data to be plotted to
    afterwards.

    Parameters:
    survey : BSDIM survey which is used to draw the machine lattice on the top axes.
    machine_plot_gap : vertical space between the top of the first axes and the 
    bottom of the machine axes. By default this is small.

    Returns (figure, machine_axes, (axes1, axes2, ...))

    figure : Figure instance.
    machine_axes : Axes instance with the machine drawn on it.  Can be used to further edit
    axes : iterable of axes, in order from the first below the machine, downwards.
    
    """

    if isinstance(survey, str):
        survey = _Data.Load(survey)

    # Make all main plots 3 times bigger than the machine plot along
    # the top, and set the height (vertical) space between them to be
    # small by default.  this is a bit arbitrary, can overide in gridspec_kw.
    height_ratios = [1]
    height_ratios.extend((nrows - 1) * [4])

    # Set all the kwargs to be supplied to plt.subplots
    the_gridspec_kw = {"height_ratios": height_ratios,
                       "hspace": 0.05}
    if gridspec_kw is not None:
        the_gridspec_kw.update(gridspec_kw)
    the_subplots_kw = {"sharex": True,
                       "gridspec_kw": the_gridspec_kw}
    if subplots_kw is not None:
        the_subplots_kw.update(subplots_kw)
    the_subplots_kw.update(fig_kw)

    fig, axes = _plt.subplots(nrows, **the_subplots_kw)

    try:
        machine_axes = axes[0]
    except TypeError:
        raise ValueError("nrows = {}.  Must be >= 2.".format(nrows))

    _SetMachineAxesStyle(machine_axes)
    DrawMachineLattice(machine_axes, survey)

    # #put callbacks for linked scrolling
    def MachineXlim(ax):
        machine_axes.set_autoscale_on(False)
        for axis in axes[1:]:
            axis.set_xlim(machine_axes.get_xlim())

    def Click(a) :
        if a.button == 3:
            try:
                msg = "Closest element: {}".format(
                    survey.NameFromNearestS(a.xdata))
                print(msg)
            except ValueError:
                pass # don't complain if the S is out of bounds

    MachineXlim(machine_axes)
    machine_axes.callbacks.connect('xlim_changed', MachineXlim)
    fig.canvas.mpl_connect('button_press_event', Click)

    # Decrease the hgap bewteen the machine axes and the first plot axes.
    machine_bbox = machine_axes.get_position()
    first_plot_bbox_y1 = axes[1].get_position().y1
    machine_bbox.y0 = first_plot_bbox_y1 + machine_plot_gap
    machine_axes.set_position(machine_bbox)
    return fig, machine_axes, axes[1:]



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

def _MakePlotter(plot_info_tuples, x_label, y_label, title):
    def f_out(bds, outputfilename=None, survey=None, **kwargs):
        # options
        tightLayout = True
        if 'tightLayout' in kwargs:
            tightLayout = kwargs['tightLayout']

        # Get the initial N for the two sources
        first_nparticles = bds.Npart()[0]

        plot = _plt.figure(title, figsize=(9,5), **kwargs)
        colours = ('b', 'g')
        # Loop over the variables in plot_info_tuples and draw the plots.
        for a, colour in zip(plot_info_tuples, colours):
            var, error, legend_name = a # unpack one tuple
            s = bds.GetColumn('S') # cache data
            d = bds.GetColumn(var)
            _plt.errorbar(s, d, fmt=colour+".",
                          yerr=bds.GetColumn(error),
                          label="{} {}; N = {:.1E}".format(
                              "", legend_name, first_nparticles),
                          capsize=3, **kwargs)
            _plt.plot(s, d, colour) # line plot without label

        # Set axis labels and draw legend
        axes = _plt.gcf().gca()
        axes.set_ylabel(y_label)
        axes.set_xlabel(x_label)
        axes.legend(loc='best')

        if survey is not None:
            AddMachineLatticeFromSurveyToFigure(plot, survey, tightLayout)
        else:
            _plt.tight_layout()

        _plt.show(block=False)

        if outputfilename != None:
            if '.' in outputfilename:
                outputfilename = outputfilename.split('.')[0]
            _plt.savefig(outputfilename + '_' + title + '.pdf')
            _plt.savefig(outputfilename + '_' + title + '.png')

        return plot
    return f_out

PlotBeta   = _MakePlotter(_BETA,    "S / m", r"$\beta_{x,y}$ / m",      "Beta")
PlotAlpha  = _MakePlotter(_ALPHA,   "S / m", r"$\alpha_{x,y}$ / m",     "Alpha")
PlotDisp   = _MakePlotter(_DISP,    "S / m", r"$D_{x,y} / m$",          "Dispersion")
PlotDispP  = _MakePlotter(_DISP_P,  "S / m", r"$D_{p_{x},p_{y}}$ / m",  "Momentum_Dispersion")
PlotSigma  = _MakePlotter(_SIGMA,   "S / m", r"$\sigma_{x,y}$ / m",     "Sigma")
PlotSigmaP = _MakePlotter(_SIGMA_P, "S / m", r"$\sigma_{xp,yp}$ / rad", "SigmaP")
PlotMean   = _MakePlotter(_MEAN,    "S / m", r"$\bar{x}, \bar{y}$ / m", "Mean")

def PlotNPart(bds, outputfilename=None, survey=None, **kwargs):
    # options
    tightLayout = True
    if 'tightLayout' in kwargs:
        tightLayout = kwargs['tightLayout']

    plot = _plt.figure("Npart", figsize=(9,5), **kwargs)
    # Loop over the variables in plot_info_tuples and draw the plots.
    _plt.plot(bds.GetColumn('S'),bds.GetColumn('Npart'), 'k-', label='N Particles', **kwargs)
    _plt.plot(bds.GetColumn('S'),bds.GetColumn('Npart'), 'k.')

    # Set axis labels and draw legend
    axes = _plt.gcf().gca()
    axes.set_ylabel(r'N Particles')
    axes.set_xlabel('S / m')
    axes.legend(loc='best')

    if survey is not None:
        AddMachineLatticeFromSurveyToFigure(plot, survey, tightLayout)
    else:
        _plt.tight_layout()

    _plt.show(block=False)

    if outputfilename != None:
        if '.' in outputfilename:
            outputfilename = outputfilename.split('.')[0]
        _plt.savefig(outputfilename + '_Npart.pdf')
        #_plt.savefig(outputfilename + '_Npart.png')
    return plot

def BDSIMOptics(rebdsimOpticsOutput, outputfilename=None, saveall=True, survey=None, **kwargs):
    """
    Display all the optical function plots for a rebdsim optics root file. By default, this saves all optical
    functions into a single (outputfilename) pdf, to save the optical functions separately, supply an
    outputfilename with saveall=false.
    """
    bdsdata = rebdsimOpticsOutput
    if type(bdsdata) is str:
        bdsdata = _Data.Load(bdsdata)
    optics  = bdsdata.optics
    if survey is None and hasattr(bdsdata, "model"):
        if len(bdsdata.model) > 0:
            survey = bdsdata.model

    # overwrite with none to prevent plotting individual optical functions as well as combined pdf
    plotfilename=outputfilename
    if saveall:
        outputfilename=None

    figures = [
    PlotBeta(optics,   survey=survey, outputfilename=outputfilename, **kwargs),
    PlotAlpha(optics,  survey=survey, outputfilename=outputfilename, **kwargs),
    PlotDisp(optics,   survey=survey, outputfilename=outputfilename, **kwargs),
    PlotDispP(optics,  survey=survey, outputfilename=outputfilename, **kwargs),
    PlotSigma(optics,  survey=survey, outputfilename=outputfilename, **kwargs),
    PlotSigmaP(optics, survey=survey, outputfilename=outputfilename, **kwargs),
    PlotMean(optics,   survey=survey, outputfilename=outputfilename, **kwargs),
    PlotNPart(optics,  survey=survey, outputfilename=outputfilename, **kwargs)
    ]

    if saveall:
        if plotfilename is not None:
            output_filename = plotfilename
        else:
            output_filename = "optics-report.pdf"

        with _PdfPages(output_filename) as pdf:
            for figure in figures:
                pdf.savefig(figure)
            d = pdf.infodict()
            d['Title'] = "Optical Comparison"
            d['CreationDate'] = _datetime.datetime.today()
        print("Written ", output_filename)


def Histogram1D(histogram, xlabel=None, ylabel=None, title=None, scalingFactor=1.0, xScalingFactor=1.0, figsize=(6.4, 4.8), log=False, **errorbarKwargs):
    """
    Plot a pybdsim.Data.TH1 instance.

    :param xlabel: x axis label
    :param ylabel: y axis label
    :param title:  plot title
    :param scalingFactor: multiplier for values
    :param xScalingFactor: multiplier for x axis coordinates
    :param log: whether to automatically plot on a vertical log scale

    return figure instance
    """
    if 'drawstyle' not in errorbarKwargs:
        errorbarKwargs['drawstyle'] = 'steps-mid'
    h = histogram
    f = _plt.figure(figsize=figsize)
    ax = f.add_subplot(111)
    sf  = scalingFactor #shortcut
    xsf = xScalingFactor
    histEmpty = len(h.contents[h.contents!=0]) == 0
    if not histEmpty:
        ht = _Data.PadHistogram1D(h)
    else:
        ht = h
    ax.errorbar(xsf*ht.xcentres, sf*ht.contents, yerr=sf*ht.errors,xerr=xsf*ht.xwidths*0.5, **errorbarKwargs)
    if xlabel is None:
        ax.set_xlabel(h.xlabel)
    else:
        ax.set_xlabel(xlabel)
    if ylabel is None:
        ax.set_ylabel(h.ylabel)
    else:
        ax.set_ylabel(ylabel)
    if title == "":
        ax.set_title(h.title) # default to one in histogram
    elif title is None:
        pass
    else:
        ax.set_title(title)

    yvl = h.contents-h.errors
    yvh = h.contents+h.errors
    ymin = _np.min(yvl)
    ymax = _np.max(yvl)
    try:
        ymin = sf*_np.min(yvl[yvl>0])
        ymax = sf*_np.max(yvh[yvh>0])
    except:
        pass
    if log and not histEmpty:
        _plt.ylim(abs(ymin)*0.9,abs(ymax)*1.3)
        if _matplotlib.__version__ >= '3.3':
            _plt.yscale('log', nonpositive='clip')
        else:
            _plt.yscale('log', nonposy='clip')
    else:
        _plt.ylim(ymin*0.8, ymax*1.05)

    _plt.tight_layout()
    return f

def Spectra(spectra,
            log=False, xlog=False,
            xlabel=None, ylabel=None, title=None,
            scalingFactors=None, xScalingFactors=None,
            figsize=(10,5), legendKwargs={}, **errorbarKwargs):
    """
    Plot a Spectra object loaded from data that represents a set of histograms.

    returns a list of figure objects.
    """
    histograms = [spectra.histogramspy[(pdgid,flag)] for (pdgid,flag) in spectra.pdgidsSorted]
    
    labels = []
    for (pdgid, flag) in spectra.pdgidsSorted:
        rn = _Constants.GetPDGName(pdgid)[1]
        if flag != 'n':
            rn += r" ("+flag+r")"
        labels.append(rn)        
            
    if xlabel is None:
        print("Using default xlabel of kinetic energy")
        xlabel="Kinetic Energy (GeV)"
    if ylabel is None:
        h1 = histograms[0]
        if _np.any(_np.diff(h1.xwidths)):
            # uneven binning suspected
            ylabel = "Per-Event Rate"
        else:
            ylabel = "Per-Event Rate / " + str(round(h1.xwidths[0],2)) + " GeV"
    if title is None:
        title = spectra.name

    # avoid overly busy plots... if more than 8 lines, split into 2. Copy the total to both.
    if len(histograms) > 8:
        histogramsA = histograms[:9]
        histogramsB = histograms[9:]
        labelsA = labels[:9]
        labelsB = labels[9:]
        if (0,'n') in spectra.pdgidsSorted:
            # if pdgid of 0, which is the 'total' histogram is present,
            # then it's integral must be the greatest and it should be first
            # in the A list, so also put it first in the B list
            histogramsB.insert(0, histogramsA[0])
            
        f1 = Histogram1DMultiple(histogramsA, labelsA, log, xlog, xlabel, ylabel, title,
                                 scalingFactors, xScalingFactors, figsize, legendKwargs, **errorbarKwargs)
        f2 = Histogram1DMultiple(histogramsB, labelsB, log, xlog, xlabel, ylabel, title,
                                 scalingFactors, xScalingFactors, figsize, legendKwargs, **errorbarKwargs)
        return [f1,f2]
    else:
        f1 = Histogram1DMultiple(histograms, labels, log, xlog, xlabel, ylabel, title,
                                 scalingFactors, xScalingFactors, figsize, legendKwargs, **errorbarKwargs)
        return [f1]


def Histogram1DMultiple(histograms, labels, log=False, xlog=False, xlabel=None, ylabel=None, title=None, scalingFactors=None, xScalingFactors=None, figsize=(10,5), legendKwargs={}, **errorbarKwargs):
    """
    Plot multiple 1D histograms on the same plot. Histograms and labels should 
    be lists of the same length with pybdsim.Data.TH1 objects and strings.

    return figure instance

    xScalingFactors may be a float, int or list

    Example: ::

      Histogram1DMultiple([h1,h2,h3], 
                          ['Photons', 'Electrons', 'Positrons'], 
                          xlabel=r'$\mu$m', 
                          ylabel='Fraction',
                          scalingFactors=[1,100,100],
                          xScalingFactors=1e6,
                          log=True)
    """
    if "xScalingFactor" in errorbarKwargs:
        raise ValueError("'xScalingFactor' - did you mean 'xScalingFactors'?")

    f = _plt.figure(figsize=figsize)
    ax = f.add_subplot(111)
    
    if scalingFactors is None:
        scalingFactors = _np.ones_like(histograms)
    if xScalingFactors is None:
        xScalingFactors = _np.ones_like(histograms)
    elif type(xScalingFactors) == float or type(xScalingFactors) == int:
        xScalingFactors = xScalingFactors * _np.ones_like(histograms)
    ymax = -_np.inf
    ymin =  _np.inf
    yminpos = _np.inf
    xmin = _np.inf
    xmax = -_np.inf
    allHistsEmpty = True  # true until one hist isn't empty
    for xsf,h,l,sf in zip(xScalingFactors, histograms, labels, scalingFactors):
        histEmpty = len(h.contents[h.contents != 0]) == 0
        # x range heuristic - do before padding
        xmin = min(xmin, _np.min(xsf*h.xlowedge))
        xmax = max(xmax, _np.max(xsf*h.xhighedge))
        if not histEmpty:
            allHistsEmpty = False
            ht = _Data.PadHistogram1D(h)
        else:
            ht = h
        ax.errorbar(xsf*ht.xcentres, sf*ht.contents, yerr=sf*ht.errors,
                    xerr=ht.xwidths*0.5, label=l, drawstyle='steps-mid', **errorbarKwargs)

        # for heuristic determination of ylim we use original unpadded histogram data
        ymin = min(ymin, sf*_np.min(h.contents-h.errors))
        ypos = h.contents[h.contents>0]
        if len(ypos) > 0:
            yminpos = min(yminpos, _np.min(ypos))
        ymax = max(ymax, sf*_np.max(h.contents+h.errors))
        
    if xlabel is None:
        ax.set_xlabel(histograms[0].xlabel)
    else:
        ax.set_xlabel(xlabel)
    if ylabel is None:
        ax.set_ylabel(histograms[0].ylabel)
    else:
        ax.set_ylabel(ylabel)
    if title == "":
        ax.set_title(histograms[0].title) # default to one in histogram
    elif title is None:
        pass
    else:
        ax.set_title(title)
    if log and not allHistsEmpty:
        _plt.ylim(abs(yminpos)*0.9,abs(ymax)*1.1)
        if _matplotlib.__version__ >= '3.3':
            _plt.yscale('log', nonpositive='clip')
        else:
            _plt.yscale('log', nonposy='clip')
    else:
        _plt.ylim(ymin*0.8, ymax*1.05)

    if xlog:
        _plt.xscale('log')
        suggestedXMin = 0.95*xmin
        if suggestedXMin <= 0:
            suggestedXMin = 1
        _plt.xlim(suggestedXMin, 1.05*xmax)

    _plt.legend(**legendKwargs)
    _plt.tight_layout()
    
    return f

def Histogram2D(histogram, logNorm=False, xLogScale=False, yLogScale=False, xlabel="", ylabel="", zlabel="", title="", aspect="auto", scalingFactor=1.0, xScalingFactor=1.0, yScalingFactor=1.0, figsize=(6,5), vmin=None, autovmin=False, vmax=None, colourbar=True, **imshowKwargs):
    """
    Plot a pybdsim.Data.TH2 instance.
    logNorm        - logarithmic colour scale
    xlogscale      - x axis logarithmic scale
    ylogscale      - y axis logarithmic scale
    zlabel         - label for color bar scale
    aspect         - "auto", "equal", "none" - see imshow?
    scalingFactor  - multiplier for values
    xScalingFactor - multiplier for x coordinates
    yScalingFactor - multiplier for y coordinates
    autovmin       - automatically determin the lower limit of the colourbar from the data
    vmin           - explicitly control the vmin for the colour normalisation
    vmax           - explicitly control the vmax for the colour normalisation

    return figure instance
    """
    h = histogram
    f = _plt.figure(figsize=figsize)
    x, y = _np.meshgrid(h.xcentres,h.ycentres)
    sf  = scalingFactor #shortcut
    xsf = xScalingFactor
    ysf = yScalingFactor
    ext = [_np.min(xsf*h.xlowedge),_np.max(xsf*h.xhighedge),_np.min(ysf*h.ylowedge),_np.max(ysf*h.yhighedge)]
    histEmpty = len(h.contents[h.contents!=0]) == 0
    if vmin is None:
        if autovmin and vmin is None and not histEmpty:
            vmin = _np.min(h.contents[h.contents!=0])
        else:
            vmin = None
    if logNorm:
        d = _copy.deepcopy(sf*h.contents.T)
        norm = _LogNorm(vmin=vmin,vmax=vmax) if vmax is not None else _LogNorm(vmin=vmin)
        ax = f.add_subplot(111)
        im = ax.pcolormesh(h.xedges*xsf, h.yedges*ysf, d, norm=norm, rasterized=True, **imshowKwargs)
        #_plt.imshow(d, extent=ext, origin='lower', aspect=aspect, norm=norm, interpolation='none', **imshowKwargs)
        if colourbar:
            _plt.colorbar(im, label=zlabel)
    else:
        _plt.imshow(sf*h.contents.T, extent=ext, origin='lower', aspect=aspect, interpolation='none', vmin=vmin, vmax=vmax,**imshowKwargs)
        if colourbar:
            _plt.colorbar(format='%.0e', label=zlabel)

    if xLogScale:
        _plt.xscale('log')
    if yLogScale:
        _plt.yscale('log')

    if xlabel == "":
        _plt.xlabel(h.xlabel)
    elif xlabel is None:
        pass
    else:
        _plt.xlabel(xlabel)
    if ylabel == "":
        _plt.ylabel(h.ylabel)
    elif ylabel is None:
        pass
    else:
        _plt.ylabel(ylabel)
    if title == "":
        _plt.title(h.title) # default to one in histogram
    elif title is None:
        pass
    else:
        _plt.title(title)
    return f

def Histogram2DErrors(histogram, logNorm=False, xLogScale=False, yLogScale=False, xlabel="", ylabel="", zlabel="", title="", aspect="auto", scalingFactor=1.0, xScalingFactor=1.0, yScalingFactor=1.0, figsize=(6,5), vmin=None, autovmin=False, vmax=None, **imshowKwargs):
    """
    Similar to Histogram2D() but plot the errors from the histogram instead of the contents.
    See pybdsim.Plot.Histogram2D for documentation of arguments.
    """
    h2 = _copy.deepcopy(histogram)
    h2.contents = h2.errors # set contents as errors and just use regular plot
    return Histogram2D(h2, logNorm, xLogScale, yLogScale, xlabel, ylabel, zlabel, title, aspect, scalingFactor,
                       xScalingFactor, yScalingFactor, figsize, vmin, autovmin, vmax, **imshowKwargs)

def Histogram3D(th3):
    """
    Plot a pybdsim.Data.TH3 instance - TBC
    """
    print('Not written yet - best take a slice or projection and plot a 2D histogram')
    from mpl_toolkits.mplot3d import axes3d, Axes3D

    histEmpty = len(th3.contents[th3.contents!=0]) == 0
    if histEmpty:
        raise ValueError("th3 contents empty for histogram "+th3.name)

    f = _plt.figure()
    ax = f.gca(projection='3d')

    fill = th3.contents > 0
    l = _LogNorm()
    d = l(th3.contents)
    d.data[d.mask] = 0
    colours = _plt.cm.viridis(l(th3.contents))
    colours[:,:,:,3] = d.data
    ax.voxels(fill, facecolors=colours)
    #return colours
    return f
    

def Histogram1DRatio(histogram1, histogram2, label1="", label2="", xLogScale=False, yLogScale=False, xlabel=None, ylabel=None, title=None, scalingFactor=1.0, xScalingFactor=1.0, figsize=(6.4, 4.8), ratio=3, histogram1Colour=None, histogram2Colour=None, ratioColour=None, ratioYAxisLimit=None, **errorbarKwargs):
    """
    Plot two histograms with their ratio (#1 / #2) in a subplot below.

    :param histogram1: a `pybdsim.Data.TH1` instance
    :param histogram2: a `pybdsim.Data.TH1` instance
    :param label1: legend label for histogram1 (str or "" or None)
    :param label2: legend label for histogram2
    :param ratio:  integer ratio of main plot height to ratio plot height (recommend 1 - 5)
    :param ratioYAxisLimit: ylim upper for ratio subplot y axis
    :type  ratioYAxisLimit: tuple(float, float)

    If the labels are "" then the histogram.title string will be used. If None, then
    no label will be added.
    """

    if 'drawstyle' not in errorbarKwargs:
        errorbarKwargs['drawstyle'] = 'steps-mid'   

    h1 = histogram1
    h2 = histogram2
    fig     = _plt.figure(figsize=figsize)
    nrows   = ratio + 1
    gs      = fig.add_gridspec(ncols=1, nrows=nrows, hspace=0.06)
    axHist  = fig.add_subplot(gs[:-1,0])
    axRatio = fig.add_subplot(gs[-1,0], sharex=axHist)

    # calculate ratio array
    if len(h1.xcentres) != len(h2.xcentres):
        raise ValueError("Histograms with different binning - ratio cannot be taken")

    mask = _np.logical_and(h1.contents != 0, h2.contents != 0)
    ratio = _np.divide(h1.contents, h2.contents, where=mask)
    ratio = _np.ma.masked_where(_np.logical_not(mask), ratio)
    con1  = _np.ma.masked_where(_np.logical_not(mask), h1.contents)
    con2  = _np.ma.masked_where(_np.logical_not(mask), h2.contents)
    err1  = _np.ma.masked_where(_np.logical_not(mask), h1.errors)
    err2  = _np.ma.masked_where(_np.logical_not(mask), h2.errors)
    ratioErr = ratio * _np.sqrt( (err1/con1)**2 + (err2/con2)**2 )
    
    sf  = scalingFactor
    xsf = xScalingFactor
    if label1 == "":
        label1 = h1.title
    if label2 == "":
        label2 = h2.title
    if histogram1Colour is not None:
        errorbarKwargs['c'] = histogram1Colour
    axHist.errorbar(xsf*h1.xcentres, sf*h1.contents, yerr=sf*h1.errors, label=label1, **errorbarKwargs)
    if histogram1Colour is not None:
        errorbarKwargs.pop('c')
    if histogram2Colour is not None:
        errorbarKwargs['c'] = histogram2Colour
    axHist.errorbar(xsf*h2.xcentres, sf*h2.contents, yerr=sf*h2.errors, label=label2, **errorbarKwargs)
    if label1 is not None and label2 is not None:
        axHist.legend()
    if yLogScale:
        if _matplotlib.__version__ >= '3.3':
            axHist.set_yscale('log', nonpositive='clip')
        else:
            axHist.set_yscale('log', nonposy='clip')
    if xLogScale:
        _plt.xscale('log')
    _plt.setp(axHist.get_xticklabels(), visible=False)

    colour = _plt.rcParams['axes.prop_cycle'].by_key()['color'][2] # 3rd colour
    if ratioColour is not None:
        colour = ratioColour
    axRatio.axhline(1.0, c='grey', alpha=0.2)
    axRatio.errorbar(xsf*h1.xcentres, sf*ratio, yerr=sf*ratioErr, color=colour, drawstyle='steps-mid')
    if ratioYAxisLimit:
        axRatio.set_ylim(*ratioYAxisLimit)

    if xlabel is None:
        axRatio.set_xlabel(h1.xlabel)
    else:
        axRatio.set_xlabel(xlabel)
    if ylabel is None:
        axHist.set_ylabel(h1.ylabel)
    else:
        axHist.set_ylabel(ylabel)
    if title == "":
        axHist.set_title(h1.title) # default to one in histogram
    elif title is None:
        pass
    else:
        axHist.set_title(title)

    axRatio.set_ylabel('Ratio')

    # when using gridspec, we use its tight layout
    gs.tight_layout(fig)

    return fig

def PrimaryPhaseSpace(filename, outputfilename=None, extension='.pdf'):
    """
    Load a BDSIM output file and plot primary phase space. Only accepts raw BDSIM output.

    'outputfilename' should be without an extension - any extension will be stripped off.
    Plots are saves automatically as pdf, the file extension can be changed with
    the 'extension' kwarg, e.g. extension='.png'.
    """
    PhaseSpaceFromFile(filename, 0, outputfilename=outputfilename, extension=extension)

def PhaseSpaceFromFile(filename, samplerIndexOrName=0, nbins=None, outputfilename=None, extension='.pdf'):
    """
    Load a BDSIM output file and plot the phase space of a sampler (default the primaries).
    Only accepts raw BDSIM output.
    
    Number of bins chosen depending on number of samples.

    'outputfilename' should be without an extension - any extension will be stripped off.
    Plots are saves automatically as pdf, the file extension can be changed with
    the 'extension' kwarg, e.g. extension='.png'.

    """
    from . import Data as _Data
    d = _Data.Load(filename)
    psd = _Data.PhaseSpaceData(d,samplerIndexOrName=samplerIndexOrName)
    PhaseSpace(psd, nbins=nbins, outputfilename=outputfilename, extension=extension)

def PhaseSpaceSeparateAxes(filename, samplerIndexOrName=0, outputfilename=None, extension='.pdf',
                           nbins=None, energy='total', offsetTime=True, includeSecondaries=False,
                           coordsTitle=None, correlationTitle=None, scalefactors={}, labels={},
                           log1daxes=False, log2daxes=False, includeColorbar=True):
    """
    Plot the coordinates and correlations of both the transverse and longitudinal phase space in separate plots
    (four total) recorded in a sampler. Default sampler is the primary distribution.

    'outputfilename' is name without extension, extension can be supplied as a string separately. Default = pdf.

    The number of bins chosen depending on number of samples. Can be overridden with nbins.

    Energy can be binned as either kinetic or total (default), supply either energy='total' or energy='kinetic'.

    offSetTime centers the time distribution about the nominal time for the specified sampler rather than
    the absolute time. Default = True.

    Secondaries can be included in the distributions with includeSecondaries. Default = False.

    Plot titles can be supplied as strings with coordsTitle and correlationTitle.

    Parameter scale factors should be supplied in a dictionary in the format {parameter: scalefactor},
    e.g scalefactors={'x': 1000, 'y':1000}. Acceptable parameters are 'x','y','xp','yp', 'T','kinetic',
    and 'energy' for total energy.

    Axis labels for parameters should be supplied as a dictionary in the format {parameter: label},
    e.g labels={'x': "X (mm)", 'energy': "Energy (MeV)"}. Acceptable parameters are 'x','y','xp','yp',
    'T','kinetic', and 'energy' for total energy.

    log1daxes & log2daxes plots the 1D and 2D phase space on logarithmic scales respectively. Defaults = False.

    includeColorbar adds a colorbar to the correlation plots. The colorbar is normalised for all plot subfigures.
    Default = True.
    """

    defaultLabels = {'x': 'X (mm)',
                     'y': 'Y (mm)',
                     'xp': r'X$^{\prime}$  $(\times 10^{-3})$',
                     'yp': r'Y$^{\prime}$  $(\times 10^{-3})$',
                     'T': 'T (ns)',
                     'energy': 'Energy (GeV)',
                     'kinetic': 'Kinetic Energy (GeV)'
                     }

    defaultScales = {'x': 1000,  # m to mm
                     'y': 1000,  # m to mm
                     'xp': 1000,  # rad to mrad
                     'yp': 1000,  # rad to mrad
                     'T': 1,  # s
                     'energy': 1,  # GeV
                     'kinetic': 1  # GeV
                     }

    if (str.lower(energy) != 'kinetic') and (str.lower(energy) != 'total'):
        raise ValueError("energy parameter can only be 'kinetic' or 'total'")

    # load the data
    filedata = _Data.Load(filename)
    sd = _Data.SamplerData(filedata, samplerIndexOrName=samplerIndexOrName)
    beam = _Data.BeamData(filedata)  # needed for offsetting T distributions in phasespace plots
    data = sd.data  # shortcut

    # primary and sampler masses
    mass = 0.938272  # (default) for KE calculation
    primarymass = mass  # (default) for nominal sampler T
    if offsetTime or energy == 'kinetic':  # only get if necessary, otherwise cut out primary sampler data load time
        if samplerIndexOrName == 0:
            mass = data['mass'][0]  # primary mass stored in sampler
            primarymass = mass
        else:
            psd = _Data.SamplerData(filedata, samplerIndexOrName=0)
            primarymass = psd.data['mass'][0]

            if not includeSecondaries:  # use mass from primary sampler
                mass = primarymass
            else:  # calculate different particle masses
                mass = []
                # TODO: Add masses as appropriate
                for pidindex, pid in enumerate(data['partID']):
                    if pid == 2212:
                        mass.append(_con.proton_mass * _con.c*_con.c/ _con.electron_volt / 1e9)
                    elif pid == 2112:
                        mass.append(_con.neutron_mass * _con.c*_con.c/ _con.electron_volt / 1e9)
                    elif (pid == 11) or (pid == -11):
                        mass.append(_con.electron_mass * _con.c * _con.c / _con.electron_volt / 1e9)
                    else:
                        mass.append(0)  # photons etc

    if nbins is None:
        entries = sd._entries
        nbins = int(_np.ceil(25*(entries/100.)**0.2))
        print('Automatic number of bins> ', nbins)

    # switch total energy to bdsim sampler parameter name
    if energy == 'total':
        energy = 'energy'

    # empty containers for storing labels and data
    l = {}
    da = {}

    for parameter in ('x', 'y', 'xp', 'yp', 'T', energy):
        # get the parameter label
        if parameter in list(labels.keys()):
            l[parameter] = labels[parameter]
        else:
            l[parameter] = defaultLabels[parameter]

        if parameter == 'kinetic':
            if data['kineticEnergy'].size != 0:  # check if KE stored in output to begin with
                da[parameter] = data['kineticEnergy']
            elif not includeSecondaries:
                primKEs = _np.array([data['energy'][i] for i, j in enumerate(data['parentID']) if j == 0])
                da[parameter] = primKEs - primarymass
            else:
                da[parameter] = data['energy'] - mass
        else:
            if not includeSecondaries:
                da[parameter] = _np.array([data[parameter][i] for i, j in enumerate(data['parentID']) if j == 0])
            else:
                da[parameter] = data[parameter]

        # multiply data by scale factor
        if parameter in list(scalefactors.keys()):
            da[parameter] *= scalefactors[parameter]
        else:
            da[parameter] *= defaultScales[parameter]

    # offset time profile to be centered around 0
    # Use nominal T with beam E0 as low no. of particles can cause statistical fluctuation
    if offsetTime:
        S = max(data['S'])  # should all be the same for a sampler, take max to be safe
        t = S / (_np.sqrt(1.0 - 1.0/((beam.beamEnergy/primarymass)**2)) * _con.c)
        da['T'] -= (t * 1e9)

    # create correlation and coords figures and empty subplots
    # transverse
    fcorrTrans, axscorrTrans = _plt.subplots(2, 2, figsize=(9, 6))
    axXXP = axscorrTrans[0][0]
    axYYP = axscorrTrans[0][1]
    axXY = axscorrTrans[1][0]
    axXPYP = axscorrTrans[1][1]

    fcoordTrans, axscoordsTrans = _plt.subplots(2, 2, figsize=(8, 6))
    axX = axscoordsTrans[0][0]
    axY = axscoordsTrans[0][1]
    axXp = axscoordsTrans[1][0]
    axYp = axscoordsTrans[1][1]

    # longitudinal
    fcorrLong = _plt.figure(figsize=(9, 6))
    axTE = fcorrLong.add_subplot(111)

    fcoordLong = _plt.figure(figsize=(10, 6))
    axE = fcoordLong.add_subplot(121)
    axT = fcoordLong.add_subplot(122)

    # optionally set 1D and 2D to log scales
    if log2daxes:
        norm2D = _LogNorm()
    else:
        norm2D = None
    if log1daxes:
        axes = [axX, axY, axXp, axYp, axE, axT]
        if _matplotlib.__version__ >= '3.3':
            [a.set_yscale('log', nonpositive='clip') for a in axes]
        else:
            [a.set_yscale('log', nonposy='clip') for a in axes]

    # plot the transverse coords histograms
    axX.hist(da['x'], nbins)
    axX.set_xlabel(l['x'])
    axX.ticklabel_format(axis='x', style='sci', useMathText=True)

    axY.hist(da['y'], nbins)
    axY.set_xlabel(l['y'])
    axY.ticklabel_format(axis='x', style='sci', useMathText=True)

    axXp.hist(da['xp'], nbins)
    axXp.set_xlabel(l['xp'])
    axXp.ticklabel_format(axis='x', style='sci', useMathText=True, useOffset=False)

    axYp.hist(da['yp'], nbins)
    axYp.set_xlabel(l['yp'])
    axYp.ticklabel_format(axis='x', style='sci', useMathText=True, useOffset=False)

    # plot the transverse correlation histograms
    images = []
    limitScaling = 1.1

    a = axXXP.hist2d(da['x'], da['xp'], bins=nbins, cmin=1, norm=norm2D)
    axXXP.set_xlim(limitScaling*min(da['x']), limitScaling*max(da['x']))
    axXXP.set_ylim(limitScaling*min(da['xp']), limitScaling*max(da['xp']))
    axXXP.set_xlabel(l['x'])
    axXXP.set_ylabel(l['xp'])
    images.append(a[3])

    b = axYYP.hist2d(da['y'], da['yp'], bins=nbins, cmin=1, norm=norm2D)
    axYYP.set_xlim(limitScaling*min(da['y']), limitScaling*max(da['y']))
    axYYP.set_ylim(limitScaling*min(da['yp']), limitScaling*max(da['yp']))
    axYYP.set_xlabel(l['y'])
    axYYP.set_ylabel(l['yp'])
    images.append(b[3])

    c = axXY.hist2d(da['x'], da['y'], bins=nbins, cmin=1, norm=norm2D)
    axXY.set_xlim(limitScaling*min(da['x']), limitScaling*max(da['x']))
    axXY.set_ylim(limitScaling*min(da['y']), limitScaling*max(da['y']))
    axXY.set_xlabel(l['x'])
    axXY.set_ylabel(l['y'])
    images.append(c[3])

    d = axXPYP.hist2d(da['xp'], da['yp'], bins=nbins, cmin=1, norm=norm2D)
    axXPYP.set_xlim(limitScaling*min(da['xp']), limitScaling*max(da['xp']))
    axXPYP.set_ylim(limitScaling*min(da['yp']), limitScaling*max(da['yp']))
    axXPYP.set_xlabel(l['xp'])
    axXPYP.set_ylabel(l['yp'])
    images.append(d[3])

    # plot the longitudinal coordinate histograms
    axE.hist(da[energy], nbins)
    axE.set_xlabel(l[energy])
    axE.ticklabel_format(axis='x', style='sci', useMathText=True, useOffset=False)

    axT.hist(da['T'], nbins)
    axT.set_xlabel(l['T'])
    axT.ticklabel_format(axis='x', style='sci', useMathText=True)

    # plot the longitudinal correlation histograms
    e = axTE.hist2d(da['T'], da[energy], bins=nbins, cmin=1, norm=norm2D)
    axTE.set_xlim(min(da['T']), max(da['T']))
    axTE.set_ylim(min(da[energy]), max(da[energy]))
    axTE.set_xlabel(l['T'])
    axTE.set_ylabel(l[energy])

    # normalise data so same colorbar can be used for all 2d plots
    if log2daxes:
        vmintrans = min(image.get_array().min() for image in images)
        vmaxtrans = max(image.get_array().max() for image in images)
        normtrans = _LogNorm(vmin=vmintrans, vmax=vmaxtrans)
        for im in images:
            im.set_norm(normtrans)

        # apply same to longitudinal - bit redundant as only one 2D histogram is generated,
        # but it allows for expansion if energy vs. Z is desired.
        vminlong = e[3].get_array().min()
        vmaxlong = e[3].get_array().max()
        normlong = _LogNorm(vmin=vminlong, vmax=vmaxlong)
        e[3].set_norm(normlong)

    # set titles, and adjust layout
    if correlationTitle is None:
        correlationTitle = 'Correlations at ' + sd.samplerName
    if coordsTitle is None:
        coordsTitle = 'Coordinates at '+ sd.samplerName

    fcoordTrans.suptitle(coordsTitle, fontsize='xx-large')
    fcoordTrans.tight_layout()
    fcoordTrans.subplots_adjust(top=0.92)

    fcorrTrans.suptitle(correlationTitle, fontsize='xx-large')
    fcorrTrans.tight_layout()
    fcorrTrans.subplots_adjust(top=0.92)

    fcoordLong.suptitle(coordsTitle, fontsize='xx-large')
    fcoordLong.tight_layout()
    fcoordLong.subplots_adjust(top=0.92)

    fcorrLong.suptitle(correlationTitle, fontsize='xx-large')
    fcorrLong.tight_layout()
    fcorrLong.subplots_adjust(top=0.92)

    # add colorbar
    if includeColorbar:
        fcorrTrans.subplots_adjust(right=0.885)
        cbar_ax = fcorrTrans.add_axes([0.92, 0.15, 0.03, 0.7])
        fcorrTrans.colorbar(images[0], ax=axscorrTrans, cax=cbar_ax, fraction=.1)
        cbarLong = fcorrLong.colorbar(e[3])

    if outputfilename is not None:
        if '.' in outputfilename:
            outputfilename = outputfilename.split('.')[0]
        fcoordTrans.savefig(outputfilename + '_coords' + extension)
        fcorrTrans.savefig(outputfilename + '_correlations' + extension)
        fcoordLong.savefig(outputfilename + '_long_coords' + extension)
        fcorrLong.savefig(outputfilename + '_long_correlations' + extension)

def PhaseSpace(data, nbins=None, outputfilename=None, extension='.pdf'):
    """
    Make two figures for coordinates and correlations.

    Number of bins chosen depending on number of samples.

    'outputfilename' should be without an extension - any extension will be stripped off.
     Plots are saves automatically as pdf, the file extension can be changed with
     the 'extension' kwarg, e.g. extension='.png'.
    """
    if nbins is None:
        entries = data._entries
        nbins = int(_np.ceil(25*(entries/100.)**0.2))
        print('Automatic number of bins> ',nbins)

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

    if outputfilename is not None:
        if '.' in outputfilename:
            outputfilename = outputfilename.split('.')[0]
        f.savefig(outputfilename + '_coords'+extension)
        f2.savefig(outputfilename + '_correlations'+extension)

def EnergyDeposition(filename, outputfilename=None, tfssurvey=None, bdsimsurvey=None):
    """
    Plot the energy deposition from a REBDSIM output file - uses premade merged histograms.

    Optional either Twiss table for MADX or BDSIM Survey to add machine diagram to plot. If both are provided,
    the machine diagram is plotted from the MADX survey.
    """
    from . import Data as _Data
    d = _Data.Load(filename)
    if type(d) is not _Data.RebdsimFile:
        raise IOError("Not a rebdsim file")
    eloss = d.histogramspy['Event/MergedHistograms/ElossHisto']

    xwidth = eloss.xwidths[0]
    xlabel = r"S (m)"
    ylabel = r"Energy Deposition / Event (GeV / {} m)".format(round(xwidth,2))
    f = Histogram1D(eloss, xlabel='S (m)', ylabel=ylabel)

    ax = f.get_axes()[0]
    ax.set_yscale('log')

    if tfssurvey:
        AddMachineLatticeToFigure(f, tfssurvey)
    elif bdsimsurvey:
        AddMachineLatticeFromSurveyToFigure(f, bdsimsurvey)
    elif hasattr(d, "model"):
        AddMachineLatticeFromSurveyToFigure(f, d.model)

    if outputfilename is not None:
        _plt.savefig(outputfilename)
    else:
        _plt.show()

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
        return

    d = _Data.Load(filename)
    if type(d) is not _Data.RebdsimFile:
        raise IOError("Not a rebdsim file")
    eloss = d.histogramspy['Event/MergedHistograms/ElossHisto']

    xwidth    = eloss.xwidths[0]
    xlabel = r"S (m)"
    ylabel = r"Energy Deposition / Event (GeV / {}) m".format(round(xwidth,2))

    skipMachineLattice = False
    if "skipMachineLattice" in kwargs:
        skipMachineLattice = kwargs["skipMachineLattice"]

    print("Note that collimator/warm/cold loss classification is approximate for "
          "binned data and missclasification probability increases with bin sze.")

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
            raise ValueError(
                "Unrecognised warmaperinfo option: {}".format(warmaperinfo))

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

    if _matplotlib.__version__ >= '3.3':
        ax.set_yscale("log", nonpositive='clip')
    else:
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
        print("not working like this")
    elif hasattr(d, "model"):
        AddMachineLatticeFromSurveyToFigure(f, d.model)

    if outputfilename is not None:
        _plt.savefig(outputfilename)

def PrimarySurvival(filename, outputfilename=None, tfssurvey=None, bdsimsurvey=None):

    from . import Data as _Data
    d = _Data.Load(filename)
    if type(d) is not _Data.RebdsimFile:
        raise IOError("Not a rebdsim file")

    ploss = d.histogramspy['Event/MergedHistograms/PlossHisto']

    fig = _plt.figure(figsize=(10,5))
    ax1 = fig.add_subplot(111)
    ax1.set_yscale('log')
    ax1.set_ylabel('Fraction of Beam Surviving')

    survival = 1.0 - _np.cumsum(ploss.contents)
    ax1.plot(ploss.xcentres, survival)
    ax1.set_xlabel('S (m)')

    if tfssurvey:
        AddMachineLatticeToFigure(fig, tfssurvey)
    elif bdsimsurvey:
        AddMachineLatticeFromSurveyToFigure(fig, bdsimsurvey)
    elif hasattr(d, "model"):
        AddMachineLatticeFromSurveyToFigure(fig, d.model)

    if outputfilename is not None:
        _plt.savefig(outputfilename)

def LossAndEnergyDeposition(filename, outputfilename=None, tfssurvey=None, bdsimsurvey=None, hitslegendloc='upper left', elosslegendloc='upper right', perelement=False, elossylim=None, phitsylim=None):
    """
    Load a REBDSIM output file and plot the merged histograms automatically generated by BDSIM.

    Optional either Twiss table for MADX or BDSIM Survey to add machine diagram to plot.
    """
    from . import Data as _Data
    d = _Data.Load(filename)
    if type(d) is not _Data.RebdsimFile:
        raise IOError("Not a rebdsim file")

    phitsHisto = 'PhitsHisto'
    plossHisto = 'PlossHisto'
    elossHisto = 'ElossHisto'
    if perelement:
        phitsHisto = 'PhitsPEHisto'
        plossHisto = 'PlossPEHisto'
        elossHisto = 'ElossPEHisto'

    phits = d.histogramspy['Event/MergedHistograms/' + phitsHisto]
    ploss = d.histogramspy['Event/MergedHistograms/' + plossHisto]
    eloss = d.histogramspy['Event/MergedHistograms/' + elossHisto]

    fig = _plt.figure(figsize=(14,5))
    ax1 = fig.add_subplot(111)
    ax1.set_yscale('log')
    ax1.set_ylabel('Fractional Beam Loss')

    ax1.errorbar(phits.xcentres, phits.contents, xerr=phits.xwidths*0.5,yerr=phits.errors,
                 fmt='bs',elinewidth=0.8, label='Primary Hit', markersize=3)
    ax1.errorbar(ploss.xcentres, ploss.contents, xerr=ploss.xwidths*0.5,yerr=ploss.errors,
                 fmt='r.',elinewidth=0.8, label='Primary Loss', markersize=6)

    ax2 = ax1.twinx()
    ax2.errorbar(eloss.xcentres, eloss.contents, xerr=eloss.xwidths*0.5,yerr=eloss.errors,c='k',
                 elinewidth=0.8, label='Energy Deposition', drawstyle='steps-mid', alpha=0.5)
    if _matplotlib.__version__ >= '3.3':
        ax2.set_yscale('log',nonpositive='clip')
    else:
        ax2.set_yscale('log',nonposy='clip')

    if phitsylim is not None:
        ax1.set_ylim(*phitsylim)
    if elossylim is not None:
        ax2.set_ylim(*elossylim)

    xwidth = eloss.xwidths[0]
    ylabel = 'Energy Deposition / Event (GeV / '+str(round(xwidth, 2))+" m)"
    if perelement:
        ylabel = 'Energy Deposition / Event (GeV / Element)'
    ax2.set_ylabel(ylabel)

    ax1.legend(loc=hitslegendloc)
    ax2.legend(loc=elosslegendloc)

    ax1.set_xlabel('S (m)')

    if tfssurvey:
        AddMachineLatticeToFigure(fig, tfssurvey)
    elif bdsimsurvey:
        AddMachineLatticeFromSurveyToFigure(fig, bdsimsurvey)
    elif hasattr(d, "model"):
        AddMachineLatticeFromSurveyToFigure(fig, d.model)

    if outputfilename is not None:
        _plt.savefig(outputfilename)

def _fmtCbar(x, pos): #Format in scientific notation and make vals < 1 = 0
    if float(x) == 1.0:
        fst = r"$1$" #For a histogram valuesa smalled that 1 are set to 0
    else:            #Such values are set as dummies to allow log plots
        a, b = '{:.0e}'.format(x).split('e')
        b = int(b)
        fst = r'$10^{{{}}}$'.format(b)
    return fst

def Trajectory3D(rootFileName, eventNumber=0, bottomLeft=None, topRight=None):
    """
    Plot e-, e+ and photons only as r,g,b respectively for a given event from
    a BDSIM output file.

    bottomLeft and topRight are optional [xlow,xhigh] limits for plots.
    """
    rootFile = _Data.Load(rootFileName)
    trajData = _Data.TrajectoryData(rootFile, eventNumber)

    f = _plt.figure()
    ax0 = f.add_subplot(121)
    ax1 = f.add_subplot(122)
    labelledEM = False
    labelledEP = False
    labelledG  = False
    for i,t in enumerate(trajData):
        if t['partID'] == 11 :
            if not labelledEM:
                ax0.plot(t['x'],t['z'],'r-.', lw=0.35, label=r'e$^{-}$')
                labelledEM = True
            else:
                ax0.plot(t['x'],t['z'],'r-.', lw=0.35)
            ax1.plot(t['y'],t['z'],'r-.', lw=0.35)
        elif t['partID'] == -11 :
            if not labelledEP:
                ax0.plot(t['x'],t['z'],'b-.', lw=0.35, label=r'e$^{+}$')
                labelledEP = True
            else:
                ax0.plot(t['x'],t['z'],'b-.', lw=0.35)
            ax1.plot(t['y'],t['z'],'b-.', lw=0.35)
        elif t['partID'] == 22 :
            if not labelledG:
                ax0.plot(t['x'],t['z'],'g--',lw=0.35, label='photon')
                labelledG = True
            else:
                ax0.plot(t['x'],t['z'],'g--',lw=0.35)
            ax1.plot(t['y'],t['z'],'g--',lw=0.35)

    if bottomLeft is not None and topRight is not None :
        # This will crash but I'm not sure what it's supposed to do!
        _plt.xlim(bottomLeft[0],topRight[0])
        _plt.xlim(bottomLeft[1],topRight[1])

    ax0.legend(fontsize='small')

def Aperture(rootFileName, filterThin = False, surveyFileName = None):

    d =  _Data.Load(rootFileName)
    md = _Data.ModelData(d)

    length = md.length

    # Filter out thin elements:
    s = md.staS[length>0]

    aper1 = md.beamPipeAper1[length>0]
    aper2 = md.beamPipeAper2[length>0]
    aper3 = md.beamPipeAper3[length>0]
    aper4 = md.beamPipeAper4[length>0]

    plot = _plt.figure("Aperture", figsize=(9,5))
    
    _plt.plot(s, aper1, label="aper1")
    _plt.plot(s, aper2, "x", label="aper2")
    _plt.plot(s, aper3, "o", label="aper3")
    _plt.plot(s, aper4, "+", label="aper4")
    _plt.legend()

    if surveyFileName != None :
        surveyFile = _CheckItsBDSAsciiData(surveyFileName)
        AddMachineLatticeFromSurveyToFigure(plot, surveyFile, tightLayout=True)

    _plt.show()

def PrimaryTrajectoryAndProcess(rootData, eventNumber) : 

    trajData = _Data.TrajectoryData(rootData, eventNumber)    
    event    = rootData.GetEvent()
    eventTree= rootData.GetEventTree()
    eventTree.GetEntry(eventNumber)
    firstHitS = event.GetPrimaryFirstHit().S[0]
    lastHitS  = event.GetPrimaryLastHit().S[0]

    _plt.clf()
    
    fig = _plt.figure("Npart", figsize=(9,9))
    fig.subplots_adjust(hspace=0.0)

    ax1 = _plt.subplot(9,1,2)
    
    S = trajData[0]['S']
    _plt.plot(S[0:-2],trajData[0]['x'][0:-2],label="x") 
    _plt.plot(S[0:-2],trajData[0]['y'][0:-2],label="y")

    _plt.axvline(firstHitS,ls="--",c='b')
    _plt.axvline(lastHitS,ls="--",c='r')
    ax1.set_xticklabels([])
    _plt.ylabel("$x,y$ / m")

    ax2 = _plt.subplot(9,1,3)
    _plt.plot(S[0:-2],_np.log10(trajData[0]['E'][0:-2]),".",label="energy loss")
    _plt.axhline(-9,ls="--",c="b")
    _plt.axvline(firstHitS,ls="--",c='b')
    _plt.axvline(lastHitS,ls="--",c='r')
    ax2.yaxis.tick_right()
    _plt.ylabel("$\log \Delta E$")
    ax2.yaxis.set_label_position("right")
    ax2.set_xticklabels([])

    ax3 = _plt.subplot(9,1,4)
    _plt.plot(S[0:-2],trajData[0]['px'][0:-2],"-",label="px")
    _plt.plot(S[0:-2],trajData[0]['py'][0:-2],"-",label="py")
    _plt.axvline(firstHitS,ls="--",c='b')
    _plt.axvline(lastHitS,ls="--",c='r')
    ax3.set_xticklabels([])
    _plt.ylabel("$p_x,p_y$")

    ax4 = _plt.subplot(9,1,5)
    _plt.plot(S[0:-2],trajData[0]['prePT'][0:-2],".",label="pre process type")
    _plt.axvline(firstHitS,ls="--",c='b')
    _plt.axvline(lastHitS,ls="--",c='r')
    ax4.yaxis.tick_right()
    _plt.ylabel("prePT")
    ax4.yaxis.set_label_position("right")

    ax5 = _plt.subplot(9,1,6)
    _plt.plot(S[0:-2],trajData[0]['prePST'][0:-2],".",label="pre process sub type")
    _plt.axvline(firstHitS,ls="--",c='b')
    _plt.axvline(lastHitS,ls="--",c='r')
    _plt.ylabel("prePST")

    ax6 = _plt.subplot(9,1,7)
    _plt.plot(S[0:-2],trajData[0]['postPT'][0:-2],".",label="post process type")
    _plt.axvline(firstHitS,ls="--",c='b')
    _plt.axvline(lastHitS,ls="--",c='r')
    ax6.yaxis.tick_right()
    _plt.ylabel("postPT")
    ax6.yaxis.set_label_position("right")

    ax7 = _plt.subplot(9,1,8)
    _plt.plot(S[0:-2],trajData[0]['postPST'][0:-2],".",label="post process sub type")
    _plt.axvline(firstHitS,ls="--",c='b')
    _plt.axvline(lastHitS,ls="--",c='r')
    _plt.ylabel("postPST")
    _plt.xlabel("$S$/m")

    if hasattr(rootData, "model"):
        AddMachineLatticeFromSurveyToFigure(fig, rootData.model,tightLayout=True)
    
        fig.subplots_adjust(hspace=0.05)

def BDSIMApertureFromFile(filename, machineDiagram=True, plot="xy", plotApertureType=True, removeZeroLength=False, removeZeroApertures=True):
    """
    Plot the aperture from a BDSIM output file. By default it's colour coded and excludes any 0s.
    """
    d = _Data.Load(filename)
    BDSIMAperture(d, machineDiagram, plot, plotApertureType, removeZeroLength, removeZeroApertures)

def BDSIMAperture(data, machineDiagram=True, plot="xy", plotApertureType=True, removeZeroLength=False, removeZeroApertures=True):
    """
    Plot the aperture from a BDSIM DataLoader instance. By default it's colour coded and excludes
    any 0 aperture elements. Zero length elements are included.
    """
    # compare by string to avoid importing ROOT here
    # print "'",type(data).__name__,"'"
    if type(data).__name__ != "DataLoader":
        raise IOError("Invalid data type - should be BDSIM's DataLoader type.")

    md = _Data.ModelData(data)
    l,s,x,y,apers = md.GetApertureData(removeZeroLength, removeZeroApertures)
    
    if plotApertureType:
        apertureTypes = [ap.apertureType for ap in apers]
        colours = list(map(_ApertureTypeToColour, apertureTypes))
        
    fig = _plt.figure(figsize=_defaultFigureSize)
        
    if "x" in plot.lower():
        line1, = _plt.plot(s, x, 'b-', label='X', alpha=0.6)
        if plotApertureType:
            _plt.scatter(s, x, c=colours, s=6)

    if "y" in plot.lower():
        line2, = _plt.plot(s, y, 'g-', label='Y', alpha=0.6)
        if plotApertureType:
            _plt.scatter(s, y, c=colours, s=6)

    _plt.xlabel('S (m)')
    _plt.ylabel('Aperture (m)')

    if plotApertureType:
        _AddColourLegend(apertureTypes)

    _plt.legend(loc='best', numpoints=1, scatterpoints=1, fontsize='small')

    maxxy = max(_np.max(x), _np.max(y))
    _plt.ylim(0,1.1*maxxy)

    if machineDiagram:
        if hasattr(data, "model"):
            AddMachineLatticeFromSurveyToFigure(fig, data.model)
        else:
            print('Machine diagram requested but no model available in data')

    _plt.show()

def _ApertureTypeColourMap():
    # these are taken from pymadx.Plot and are reordered to be the same as the madx
    # colour coding for the appropriate bdsim ones. The order is from pybdsim.Data._bdsimApertureTypes
    _colourCodes = ['#C03028', # circular    = CRICLE
                    '#6890F0', # elliptical  = ELLIPSE
                    '#6890F0', # lhc         = LHCSCREEN
                    '#6890F0', # lhcdetailed = LHCSCREEN
                    '#F8D030', # rectangular = RECTANGLE
                    '#7038F8', # rectellipse = RECTELLIPSE
                    '#78C850', # racetrack   = RACETRACK
                    '#A8A878', # octagonal   = OCTAGON
                    '#C03028', # circularvacuum = CIRCULAR
                    '#F08030'] # clicpcl     = MARGUERITE - not true but need different colour
    
    typeToCol = dict(zip(_Data._bdsimApertureTypes, _colourCodes))
    return typeToCol

def _AddColourLegend(apertureTypes, cmap=_ApertureTypeColourMap()):
    """
    Make a legend with the set of colours used.
    """
    apertureTypes = set(apertureTypes)
    for apertureType in apertureTypes:
        colour = cmap[apertureType]
        _plt.scatter(None,None,color=colour, label=apertureType.lower())

def _ApertureTypeToColour(apertureType, cmap=_ApertureTypeColourMap()):
    """
    Try to map an aperture type name to a colour. Return grey if unknown.
    """
    colour = (0,0,0)
    try:
        colour = cmap[apertureType.lower()]
    except:
        colour =(0.8,0.8,0.8) # greyish
        
    return colour

def LossMap(ax, xcentres, y, ylow=None, **kwargs):
    """
    Plot a loss map in such a way that works well for very large loss maps.
    xcentres, xwidth and y are all provided by TH1 python histograms (see
    pybdsim.Data.TH1).

    :param  ax:      Matplotlib axes instance to draw to
    :param xcentres: centres of bins
    :param y:        loss map signal data, same length as xcentres.
    :param ylow:     small non-zero value to fill between to ensure works with log scales.

    kwargs:
    * passed to calls to plot and fill_between.

    """

    if ylow is None:
        ylow = min(y[~_np.isclose(0, y)])
    elif ylow <=0:
        raise ValueError("ylow must be positive.")

    # here we remove runs of consecutive zeros but leave a 0 on either side of any
    # finite value so the line drops back to 0. done by looking at difference from
    # one value to another both for the regular data and the data shifted by 1.
    # treats these differences as a Boolean in an or. one shorter than data length
    # so just always take the last bin too irrespective if 0 or not
    filt = _np.append(_np.logical_or(_np.diff(y), _np.diff(_np.roll(y,1))),
                      [True])
    xcentres = xcentres[filt]
    y = y[filt]
    # prepare 'low' values to fill between as no 0 on log scale
    low = _np.full_like(y, ylow)
    # the plot line with stepping is always visible as at least one pixel even
    # at the widest scale. however, if you zoom in, they're not filled, so plot
    # a fill between plot to fill in these bits. the fill between isn't really
    # visible at the largest scale so can't use just that alone
    line, = ax.plot(xcentres, y, drawstyle='steps-mid', **kwargs)
    kwargs.pop("label", None) # Only attach label to the line plot.
    kwargs.pop("color", None) # Duplicate kwargs is an error, it is set below.
    ax.fill_between(xcentres, low, y, step='mid',
                    color=line.get_color(),
                    **kwargs)

"""
The ModelBDSIMXZ and ModelBDSIMYZ functions add the possibility to plot a survey
done in BDSIM. The results can be found in the BDSIM output file in the Model tree.
The functions can plot the start and end positions of each element in the sequence.
"""

def ModelBDSIMXZ(model, ax=None):

    staPos = model.staRefPos
    endPos = model.endRefPos

    typ = model.componentType

    #xr = (_np.min([_np.min(staPos[:,0]), _np.min(endPos[:,0])]), _np.max([_np.max(staPos[:,0]), _np.max(endPos[:,0])]))
    #zr = (_np.min([_np.min(staPos[:,2]), _np.min(endPos[:,2])]), _np.max([_np.max(staPos[:,2]), _np.max(endPos[:,2])]))

    if not ax:
        f =  _plt.figure()
        ax = f.add_subplot(111)

    for t,s,e in zip(typ,staPos,endPos):
        ax.plot(s[2],s[0], 'r.', alpha=0.2)
        ax.plot(e[2],e[0], 'bo', alpha=0.2)
        ax.plot([s[2],e[2]],[s[0],e[0]],'k-')

    _plt.xlabel('Z (m)')
    _plt.ylabel('X (m)')
    _plt.tight_layout()

def ModelBDSIMYZ(model, ax=None):

    staPos = model.staRefPos
    endPos = model.endRefPos

    typ = model.componentType

    #xr = (_np.min([_np.min(staPos[:,0]), _np.min(endPos[:,0])]), _np.max([_np.max(staPos[:,0]), _np.max(endPos[:,0])]))
    #zr = (_np.min([_np.min(staPos[:,2]), _np.min(endPos[:,2])]), _np.max([_np.max(staPos[:,2]), _np.max(endPos[:,2])]))

    if not ax:
        f =  _plt.figure()
        ax = f.add_subplot(111)

    for t,s,e in zip(typ,staPos,endPos):
        ax.plot(s[2],s[1], 'r.', alpha=0.2)
        ax.plot(e[2],e[1], 'bo', alpha=0.2)
        ax.plot([s[2],e[2]],[s[1],e[1]],'k-')

    _plt.xlabel('Z (m)')
    _plt.ylabel('Y (m)')
    _plt.tight_layout()

def ModelElegantXZ(model, ax=None, transpose=False):

    X = model['X']
    Z = model['Z']
    if transpose:
        xi = X
        X = Z
        Z = xi
    XZ = _np.stack([X,Z],axis=1)

    staPos = XZ[:-1]
    endPos = XZ[1:]

    if not ax:
        f =  _plt.figure()
        ax = f.add_subplot(111)

    for s,e in zip(staPos,endPos):
        ax.plot(s[1],s[0], 'g.', alpha=0.2)
        ax.plot(e[1],e[0], 'mo', alpha=0.2)
        ax.plot([s[1],e[1]],[s[0],e[0]],'c-')

    if transpose:
        _plt.xlabel('X (m)')
        _plt.ylabel('Z (m)')
    else:
        _plt.xlabel('Z (m)')
        _plt.ylabel('X (m)')
    _plt.tight_layout()

def ModelElegantYZ(model, ax=None, transpose=False):

    Y = model['Y']
    Z = model['Z']
    if transpose:
        yi = Y
        Y = Z
        Z = yi
    YZ = _np.stack([Y,Z],axis=1)

    staPos = YZ[:-1]
    endPos = YZ[1:]

    if not ax:
        f =  _plt.figure()
        ax = f.add_subplot(111)

    for s,e in zip(staPos,endPos):
        ax.plot(s[1],s[0], 'g.', alpha=0.2)
        ax.plot(e[1],e[0], 'mo', alpha=0.2)
        ax.plot([s[1],e[1]],[s[0],e[0]],'c-')

    if transpose:
        _plt.xlabel('Y (m)')
        _plt.ylabel('Z (m)')
    else:
        _plt.xlabel('Z (m)')
        _plt.ylabel('Y (m)')
    _plt.tight_layout()
