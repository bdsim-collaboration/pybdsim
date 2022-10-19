import pickle as _pkl
import pylab as _pl
import pymad8 as _m8
import pybdsim as _bd
import matplotlib.pyplot as _plt
import numpy as _np
from os.path import isfile as _isfile
from matplotlib.backends.backend_pdf import PdfPages as _PdfPages
import datetime as _datetime

# Predefined dicts for making the standard plots,
# format = (mad8_optical_var_name, bdsim_optical_var_name, bdsim_optical_var_error_name, legend_name)

_BETA = {"bdsimdata": ("Beta_x", "Beta_y"),
         "bdsimerror": ("Sigma_Beta_x", "Sigma_Beta_y"),
         "mad8": ("BETX", "BETY"),
         "legend": (r'$\beta_{x}$', r'$\beta_{y}$'),
         "xlabel": "S / m",
         "ylabel": r"$\beta_{x,y}$ / m",
         "title": "Beta"}

_ALPHA = {"bdsimdata": ("Alpha_x", "Alpha_y"),
          "bdsimerror": ("Sigma_Alpha_x", "Sigma_Alpha_y"),
          "mad8": ("ALPHX", "ALPHY"),
          "legend": (r'$\alpha_{x}$', r'$\alpha_{y}$'),
          "xlabel": "S / m",
          "ylabel": r"$\alpha_{x,y}$ / m",
          "title": "Alpha"}

_DISP = {"bdsimdata": ("Disp_x", "Disp_y"),
         "bdsimerror": ("Sigma_Disp_x", "Sigma_Disp_y"),
         "mad8": ("DX", "DY"),
         "legend": (r"$\eta_{x}$", r"$\eta_{y}$"),
         "xlabel": "S / m",
         "ylabel": r"$\eta_{x,y} / m$",
         "title": "Dispersion"}

_DISP_P = {"bdsimdata": ("Disp_xp", "Disp_yp"),
           "bdsimerror": ("Sigma_Disp_xp", "Sigma_Disp_yp"),
           "mad8": ("DPX", "DPY"),
           "legend": (r"$\eta_{p_x}$", r"$\eta_{p_x}$"),
           "xlabel": "S / m",
           "ylabel": r"$\eta_{p_{x},p_{y}}$ / m",
           "title": "Momentum_Dispersion"}

_SIGMA = {"bdsimdata": ("Sigma_x", "Sigma_y"),
          "bdsimerror": ("Sigma_Sigma_x", "Sigma_Sigma_y"),
          "mad8": ("", ""),
          "legend": (r"$\sigma_{x}$", r"$\sigma_{y}$"),
          "xlabel": "S / m",
          "ylabel": r"$\sigma_{x,y}$ / m",
          "title": "Sigma"}

_SIGMA_P = {"bdsimdata": ("Sigma_xp", "Sigma_yp"),
            "bdsimerror": ("Sigma_Sigma_xp", "Sigma_Sigma_yp"),
            "mad8": ("", ""),
            "legend": (r"$\sigma_{xp}$", r"$\sigma_{yp}$"),
            "xlabel": "S / m",
            "ylabel": r"$\sigma_{xp,yp}$ / rad",
            "title": "SigmaP"}

_MEAN = {"bdsimdata": ("Mean_x", "Mean_y"),
         "bdsimerror": ("Sigma_Mean_x", "Sigma_Mean_y"),
         "mad8": ("X", "Y"),
         "legend": (r"$\overline{x}$", r"$\overline{y}$"),
         "xlabel": "S / m",
         "ylabel": r"$\bar{x,y}$ / m",
         "title": "Mean"}

_EMITT = {"bdsimdata": ("Emitt_x", "Emitt_y"),
          "bdsimerror": ("Sigma_Emitt_x", "Sigma_Emitt_y"),
          "mad8": ("", ""),
          "legend": (r"$\epsilon_x$", r"$\epsilon_y$"),
          "xlabel": "S / m",
          "ylabel": r"$\epsilon_{x,y}$ / m",
          "title": "Emittance"}


# use closure to avoid tonnes of boilerplate code as happened with MadxBdsimComparison.py
def _make_plotter(plot_info_dict):
    def f_out(mad8opt, bdsopt, beamParams, functions=None, postfunctions=None, survey=None, figsize=(9, 5), xlim=(0, 0), **kwargs):

        # Get the initial N for the bdsim
        N = str(int(bdsopt['Npart'][0]))  # number of primaries.

        # labels for plot legends
        mad8legendx = r'MAD8 ' + plot_info_dict['legend'][0]
        mad8legendy = r'MAD8 ' + plot_info_dict['legend'][1]
        bdslegendx = r'BDSIM ' + plot_info_dict['legend'][0] + ' ; N = ' + N
        bdslegendy = r'BDSIM ' + plot_info_dict['legend'][1] + ' ; N = ' + N

        # mad8 data from correct source
        if plot_info_dict["title"] == "Sigma":
            mad8opt.calcBeamSize(beamParams['ex'], beamParams['ey'], beamParams['esprd'])
            mad8Xdata = mad8opt.getColumnsByKeys('SIGX')
            mad8Ydata = mad8opt.getColumnsByKeys('SIGY')

            mad8s = mad8opt.getColumnsByKeys('S')
            mad8legendx += '(calculated)'
            mad8legendy += '(calculated)'
        elif plot_info_dict["title"] == "SigmaP":
            mad8opt.calcBeamSize(beamParams['ex'], beamParams['ey'], beamParams['esprd'])
            mad8Xdata = mad8opt.getColumnsByKeys('SIGXP')
            mad8Ydata = mad8opt.getColumnsByKeys('SIGYP')

            mad8s = mad8opt.getColumnsByKeys('S')
            mad8legendx += '(calculated)'
            mad8legendy += '(calculated)'
        elif plot_info_dict["title"] == "Emittance":
            emitX, emitY = _CalculateEmittance(mad8opt, beamParams)
            mad8Xdata = emitX
            mad8Ydata = emitY
            mad8s = mad8opt.getColumnsByKeys('S')
        else:
            mad8Xdata = mad8opt.getColumnsByKeys(plot_info_dict['mad8'][0])
            mad8Ydata = mad8opt.getColumnsByKeys(plot_info_dict['mad8'][1])
            mad8s = mad8opt.getColumnsByKeys('S')

        # the figure
        plot = _plt.figure(plot_info_dict["title"], figsize=figsize, **kwargs)

        # mad8 plot
        _plt.plot(mad8s, mad8Xdata, 'b--', label=mad8legendx)
        _plt.plot(mad8s, mad8Ydata, 'g--', label=mad8legendy)

        # bds plot
        _plt.errorbar(bdsopt['S'], bdsopt[plot_info_dict['bdsimdata'][0]], bdsopt[plot_info_dict['bdsimerror'][0]],
                      label=bdslegendx, capsize=3, ls='', marker='x', color='b', **kwargs)
        _plt.errorbar(bdsopt['S'], bdsopt[plot_info_dict['bdsimdata'][1]], bdsopt[plot_info_dict['bdsimerror'][1]],
                      label=bdslegendy, capsize=3, ls='', marker='x', color='g', **kwargs)

        # Set axis labels and draw legend
        axes = _plt.gcf().gca()
        axes.set_ylabel(plot_info_dict['ylabel'])
        axes.set_xlabel(plot_info_dict['xlabel'])
        axes.legend(loc='best')
        axes.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))

        if survey is None:
            survey = mad8opt
        _CallUserFigureFunctions(functions)
        _AddSurvey(plot, survey)
        _CallUserFigureFunctions(postfunctions)

        plot.sca(plot.axes[0])
        _plt.show(block=False)

        if xlim != (0, 0):
            _plt.xlim(xlim)
        _plt.show(block=False)
        return plot

    return f_out


PlotBeta = _make_plotter(_BETA)
PlotAlpha = _make_plotter(_ALPHA)
PlotDisp = _make_plotter(_DISP)
PlotDispP = _make_plotter(_DISP_P)
PlotSigma = _make_plotter(_SIGMA)
PlotSigmaP = _make_plotter(_SIGMA_P)
PlotMean = _make_plotter(_MEAN)
PlotEmitt = _make_plotter(_EMITT)


def _CalculateEmittance(mad8opt, beamParams):
    emitX0 = beamParams['ex']
    emitY0 = beamParams['ey']
    particle = beamParams['particle']
    if particle == 'electron' or particle == 'positron':
        mass = 0.5109989461
    elif particle == 'proton':
        mass = 938.2720813
    else:  # default is mad8 default particle mass.
        mass = 0.5109989461

    e = mad8opt.getColumnsByKeys('E')
    rgamma = e / (mass / 1e3)
    rbeta = _np.sqrt(1 - 1.0 / rgamma ** 2)

    emitXN0 = emitX0 * rgamma[0] * rbeta[0]
    emitYN0 = emitY0 * rgamma[0] * rbeta[0]

    emitX = emitXN0 / (rbeta * rgamma)
    emitY = emitYN0 / (rbeta * rgamma)
    return emitX, emitY


def _CallUserFigureFunctions(functions):
    if isinstance(functions, list):
        for function in functions:
            if callable(function):
                function()
    elif callable(functions):
        functions()


def _AddSurvey(figure, survey):
    if survey is None:
        return
    else:
        _m8.Plot.AddMachineLatticeToFigure(figure, survey)


def Mad8VsBDSIM(twiss, bdsim, survey=None, functions=None, postfunctions=None, figsize=(10, 5), xlim=(0, 0),
                saveAll=True, outputFileName=None, particle="electron", energySpread=1e-4, ex=1e-8, ey=1e-8):
    """ Compares Mad8 and BDSIM optics variables.

    +-----------------+---------------------------------------------------------+
    | **Parameters**  | **Description**
    +-----------------+---------------------------------------------------------+
    | twiss           | Mad8 twiss file                                         |
    +-----------------+---------------------------------------------------------+
    | bdsim           | Optics root file (from rebdsimOptics or rebdsim).       |
    +-----------------+---------------------------------------------------------+
    | functions       | Hook for users to add their functions that are called   |
    |                 | immediately prior to the addition of the plot. Use a    |
    |                 | lambda function to add functions with arguments. Can    |
    |                 | be a function or a list of functions.                   |
    +-----------------+---------------------------------------------------------+
    | figsize         | Figure size for all figures - default is (12,5)         |
    +-----------------+---------------------------------------------------------+
    | xlim            | Set xlimit for all figures                              |
    +-----------------+---------------------------------------------------------+
    | particle        | Beam particle type to determine particle mass, required |
    |                 | for beam size calculation - default is electron.        |
    +-----------------+---------------------------------------------------------+
    | energySpread    | Energy spread used in beam size calculation - default   |
    |                 | is 1e-4.                                                |
    +-----------------+---------------------------------------------------------+
    | ex / ey         | Horizontal / vertical emittance used in beam size       |
    |                 | calculation - default is 1e-8.                          |
    +-----------------+---------------------------------------------------------+
    """

    if not _isfile(twiss):
        raise IOError("File not found: ", twiss)
    if isinstance(bdsim, str) and not _isfile(bdsim):
        raise IOError("File not found: ", bdsim)

    fname = _bd._General.GetFileName(bdsim)  # cache file name
    if fname == "":
        fname = "optics_report"

    # load mad8 optics and bdsim optics
    mad8opt = _m8.Output(twiss)
    bdsinst = _bd._General.CheckItsBDSAsciiData(bdsim)
    bdsopt = _GetBDSIMOptics(bdsinst)

    # parameters required for calculating beam sizes, not written in mad8 output so have to supply manually.
    beamParams = {'esprd': energySpread, 'particle': particle, 'ex': ex, 'ey': ey}

    # make plots
    # energy and npart plotted with individual methods
    figures = [PlotBeta(mad8opt, bdsopt, beamParams, functions=functions, postfunctions=postfunctions, figsize=figsize, xlim=xlim, survey=survey),
               PlotAlpha(mad8opt, bdsopt, beamParams, functions=functions, postfunctions=postfunctions, figsize=figsize, xlim=xlim, survey=survey),
               PlotDisp(mad8opt, bdsopt, beamParams, functions=functions, postfunctions=postfunctions, figsize=figsize, xlim=xlim, survey=survey),
               PlotDispP(mad8opt, bdsopt, beamParams, functions=functions, postfunctions=postfunctions, figsize=figsize, xlim=xlim, survey=survey),
               PlotSigma(mad8opt, bdsopt, beamParams, functions=functions, postfunctions=postfunctions, figsize=figsize, xlim=xlim, survey=survey),
               PlotSigmaP(mad8opt, bdsopt, beamParams, functions=functions, postfunctions=postfunctions, figsize=figsize, xlim=xlim, survey=survey),
               PlotEnergy(mad8opt, bdsopt, beamParams, functions=functions, postfunctions=postfunctions, figsize=figsize, xlim=xlim, survey=survey),
               PlotMean(mad8opt, bdsopt, beamParams, functions=functions, postfunctions=postfunctions, figsize=figsize, xlim=xlim, survey=survey),
               PlotEmitt(mad8opt, bdsopt, beamParams, functions=functions, postfunctions=postfunctions, figsize=figsize, xlim=xlim, survey=survey),
               PlotNParticles(mad8opt, bdsopt, beamParams, functions=functions, postfunctions=postfunctions, figsize=figsize, xlim=xlim, survey=survey)]

    if saveAll:
        tfsname = repr(twiss)
        bdsname = repr(bdsinst)
        output_filename = "optics-report.pdf"
        if outputFileName is not None:
            output_filename = outputFileName
            if not output_filename.endswith('.pdf'):
                output_filename += ".pdf"
        else:
            output_filename = fname.replace('.root', '')
            output_filename += ".pdf"
        # Should have a more descriptive name really.
        with _PdfPages(output_filename) as pdf:
            for figure in figures:
                pdf.savefig(figure)
            d = pdf.infodict()
            d['Title'] = "{} (MAD8) VS {} (BDSIM) Optical Comparison".format(tfsname, bdsname)
            d['CreationDate'] = _datetime.datetime.today()
        print("Written ", output_filename)
    return mad8opt


def PlotEnergy(mad8opt, bdsopt, beamParams, survey=None, functions=None, postfunctions=None, figsize=(12, 5), xlim=(0, 0)):
    N = str(int(bdsopt['Npart'][0]))  # number of primaries.
    energyPlot = _plt.figure('Energy', figsize)

    # one missing energy due to initial
    _plt.plot(mad8opt.getColumnsByKeys('S'), mad8opt.getColumnsByKeys('E'), 'b--', label=r'MAD8 $E$')

    _plt.errorbar(bdsopt['S'], bdsopt['Mean_E'], yerr=bdsopt['Sigma_Mean_E'], label=r'BDSIM $E$' + ' ; N = ' + N, marker='x', ls='', color='b')

    axes = _plt.gcf().gca()
    axes.set_ylabel('Energy / GeV')
    axes.set_xlabel('S / m')
    axes.legend(loc='best')

    if survey is None:
        survey = mad8opt
    _CallUserFigureFunctions(functions)
    _AddSurvey(energyPlot, survey)
    _CallUserFigureFunctions(postfunctions)
    if xlim != (0, 0):
        _plt.xlim(xlim)

    energyPlot.sca(energyPlot.axes[0])

    _plt.show(block=False)
    return energyPlot


def PlotNParticles(mad8opt, bdsopt, beamParams, survey=None, functions=None, postfunctions=None, figsize=(12, 5), xlim=(0, 0)):
    npartPlot = _plt.figure('NParticles', figsize)

    _plt.plot(bdsopt['S'], bdsopt['Npart'], 'k-', label='BDSIM N Particles')
    _plt.plot(bdsopt['S'], bdsopt['Npart'], 'k.')
    axes = _plt.gcf().gca()
    axes.set_ylabel(r'N Particles')
    axes.set_xlabel('S / m')
    axes.legend(loc='best')

    if survey is None:
        survey = mad8opt
    _CallUserFigureFunctions(functions)
    _AddSurvey(npartPlot, survey)
    _CallUserFigureFunctions(postfunctions)
    if xlim != (0, 0):
        _plt.xlim(xlim)

    npartPlot.sca(npartPlot.axes[0])

    _plt.show(block=False)
    return npartPlot


def _GetBDSIMOptics(optics):
    """Takes a BDSAscii instance. Return a dictionary of lists matching the variable with the list of values."""

    optvars = {}
    for variable in optics.names:
        datum = getattr(optics, variable)()
        optvars[variable] = datum
    return optvars
