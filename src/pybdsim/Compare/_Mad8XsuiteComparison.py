import pymad8 as _m8
import matplotlib.pyplot as _plt
import numpy as _np
from os.path import isfile as _isfile
from matplotlib.backends.backend_pdf import PdfPages as _PdfPages
import datetime as _datetime

# Predefined dicts for making the standard plots,
# format = (mad8_optical_var_name, xsuite_env_var_name, xsuite_env_var_error_name, legend_name)

_BETA = {"xsuitedata": ("betx", "bety"),
         "xsuiteerror": ("", ""),
         "mad8": ("BETX", "BETY"),
         "legend": (r'$\beta_{x}$', r'$\beta_{y}$'),
         "xlabel": "S / m",
         "ylabel": r"$\beta_{x,y}$ / m",
         "title": "Beta"}

_ALPHA = {"xsuitedata": ("alfx", "alfy"),
          "xsuiteerror": ("", ""),
          "mad8": ("ALPHX", "ALPHY"),
          "legend": (r'$\alpha_{x}$', r'$\alpha_{y}$'),
          "xlabel": "S / m",
          "ylabel": r"$\alpha_{x,y}$ / m",
          "title": "Alpha"}

_DISP = {"xsuitedata": ("dx", "dy"),
         "xsuiteerror": ("", ""),
         "mad8": ("DX", "DY"),
         "legend": (r"$\eta_{x}$", r"$\eta_{y}$"),
         "xlabel": "S / m",
         "ylabel": r"$\eta_{x,y} / m$",
         "title": "Dispersion"}

_DISP_P = {"xsuitedata": ("dpx", "dpy"),
           "xsuiteerror": ("", ""),
           "mad8": ("DPX", "DPY"),
           "legend": (r"$\eta_{p_x}$", r"$\eta_{p_x}$"),
           "xlabel": "S / m",
           "ylabel": r"$\eta_{p_{x},p_{y}}$ / m",
           "title": "Momentum_Dispersion"}

_SIGMA = {"xsuitedata": ("sigma_x", "sigma_y"),
          "xsuiteerror": ("", ""),
          "mad8": ("SIGX", "SIGY"),
          "legend": (r"$\sigma_{x}$", r"$\sigma_{y}$"),
          "xlabel": "S / m",
          "ylabel": r"$\sigma_{x,y}$ / m",
          "title": "Sigma"}

_SIGMA_P = {"xsuitedata": ("sigma_px", "sigma_py"),
            "xsuiteerror": ("", ""),
            "mad8": ("SIGXP", "SIGYP"),
            "legend": (r"$\sigma_{xp}$", r"$\sigma_{yp}$"),
            "xlabel": "S / m",
            "ylabel": r"$\sigma_{xp,yp}$ / rad",
            "title": "SigmaP"}

_MEAN = {"xsuitedata": ("x", "y"),
         "xsuiteerror": ("", ""),
         "mad8": ("X", "Y"),
         "legend": (r"$\overline{x}$", r"$\overline{y}$"),
         "xlabel": "S / m",
         "ylabel": r"$\bar{x,y}$ / m",
         "title": "Mean"}

_EMITT = {"xsuitedata": ("Emitt_x", "Emitt_y"),
          "xsuiteerror": ("", ""),
          "mad8": ("", ""),
          "legend": (r"$\epsilon_x$", r"$\epsilon_y$"),
          "xlabel": "S / m",
          "ylabel": r"$\epsilon_{x,y}$ / m",
          "title": "Emittance"}


# use closure to avoid tonnes of boilerplate code as happened with MadxBdsimComparison.py
def _make_plotter(plot_info_dict):
    def f_out(mad8opt, xstopt, beamParams, functions=None, postfunctions=None, survey=None, figsize=(9, 5), xlim=(0, 0), **kwargs):

        # labels for plot legends
        mad8legendx = r'MAD8 ' + plot_info_dict['legend'][0]
        mad8legendy = r'MAD8 ' + plot_info_dict['legend'][1]
        xstlegendx = r'Xsuite ' + plot_info_dict['legend'][0]
        xstlegendy = r'Xsuite ' + plot_info_dict['legend'][1]

        # mad8 data from correct source
        if plot_info_dict["title"] == "Sigma" or plot_info_dict["title"] == "SigmaP":
            mad8opt.calcBeamSize(beamParams['ex'], beamParams['ey'], beamParams['esprd'])
            mad8Xdata = mad8opt.getColumnsByKeys(plot_info_dict['mad8'][0])
            mad8Ydata = mad8opt.getColumnsByKeys(plot_info_dict['mad8'][1])

            mad8s = mad8opt.getColumnsByKeys('S')
            mad8legendx += '(calculated)'
            mad8legendy += '(calculated)'

            gemitt_zeta = beamParams['esprd'] ** 2 * xstopt.bets0
            xsuiteXdata = xstopt.get_beam_covariance(nemitt_x=beamParams['ex'],
                                                     nemitt_y=beamParams['ey'],
                                                     gemitt_zeta=gemitt_zeta)[plot_info_dict['xsuitedata'][0]]
            xsuiteYdata = xstopt.get_beam_covariance(nemitt_x=beamParams['ex'],
                                                     nemitt_y=beamParams['ey'],
                                                     gemitt_zeta=gemitt_zeta)[plot_info_dict['xsuitedata'][1]]
        elif plot_info_dict["title"] == "Emittance":
            emitX, emitY = _CalculateEmittance(mad8opt, beamParams)
            mad8Xdata = emitX
            mad8Ydata = emitY
            mad8s = mad8opt.getColumnsByKeys('S')
            xsuiteXdata = xstopt[plot_info_dict['xsuitedata'][0]]
            xsuiteYdata = xstopt[plot_info_dict['xsuitedata'][1]]
        else:
            mad8Xdata = mad8opt.getColumnsByKeys(plot_info_dict['mad8'][0])
            mad8Ydata = mad8opt.getColumnsByKeys(plot_info_dict['mad8'][1])
            xsuiteXdata = xstopt[plot_info_dict['xsuitedata'][0]]
            xsuiteYdata = xstopt[plot_info_dict['xsuitedata'][1]]
            mad8s = mad8opt.getColumnsByKeys('S')

        # the figure
        plot = _plt.figure(plot_info_dict["title"], figsize=figsize, **kwargs)

        # mad8 plot
        _plt.plot(mad8s, mad8Xdata, 'b--', label=mad8legendx)
        _plt.plot(mad8s, mad8Ydata, 'g--', label=mad8legendy)

        # xsuite plot
        _plt.plot(xstopt.s, xsuiteXdata, label=xstlegendx, ls='', marker='x', color='b', **kwargs)
        _plt.plot(xstopt.s, xsuiteYdata, label=xstlegendy, ls='', marker='x', color='g', **kwargs)

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


def Mad8VsXsuite(twiss, xstline, tws0=None, survey=None, functions=None, postfunctions=None, figsize=(10, 5), xlim=(0, 0),
                 saveAll=True, outputFileName=None, particle="electron", energySpread=1e-4, ex=1e-8, ey=1e-8):
    """ Compares Mad8 and Xsuite optics variables.

    +-----------------+---------------------------------------------------------+
    | **Parameters**  | **Description**                                         |
    +-----------------+---------------------------------------------------------+
    | twiss           | Mad8 twiss file                                         |
    +-----------------+---------------------------------------------------------+
    | xstline         | Xsuite line instance                                    |
    +-----------------+---------------------------------------------------------+
    | tws0            | Initial twiss for the xsuite line                       |
    +-----------------+---------------------------------------------------------+
    | survey          | BDSIM model survey.                                     |
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

    fname = "optics_report"

    # load mad8 optics and compute xsuite optics
    mad8opt = _m8.Output(twiss)
    xstline.build_tracker()
    xstopt = xstline.twiss(**tws0)

    # parameters required for calculating beam sizes, not written in mad8 output so have to supply manually.
    beamParams = {'esprd': energySpread, 'particle': particle, 'ex': ex, 'ey': ey}

    # make plots
    # energy and npart plotted with individual methods
    figures = [PlotBeta(mad8opt, xstopt, beamParams, functions=functions, postfunctions=postfunctions, figsize=figsize, xlim=xlim, survey=survey),
               PlotAlpha(mad8opt, xstopt, beamParams, functions=functions, postfunctions=postfunctions, figsize=figsize, xlim=xlim, survey=survey),
               PlotDisp(mad8opt, xstopt, beamParams, functions=functions, postfunctions=postfunctions, figsize=figsize, xlim=xlim, survey=survey),
               PlotDispP(mad8opt, xstopt, beamParams, functions=functions, postfunctions=postfunctions, figsize=figsize, xlim=xlim, survey=survey),
               # PlotSigma(mad8opt, xstopt, beamParams, functions=functions, postfunctions=postfunctions, figsize=figsize, xlim=xlim, survey=survey),
               # PlotSigmaP(mad8opt, xstopt, beamParams, functions=functions, postfunctions=postfunctions, figsize=figsize, xlim=xlim, survey=survey),
               # PlotEnergy(mad8opt, xstopt, beamParams, functions=functions, postfunctions=postfunctions, figsize=figsize, xlim=xlim, survey=survey),
               PlotMean(mad8opt, xstopt, beamParams, functions=functions, postfunctions=postfunctions, figsize=figsize, xlim=xlim, survey=survey),
               # PlotEmitt(mad8opt, xstopt, beamParams, functions=functions, postfunctions=postfunctions, figsize=figsize, xlim=xlim, survey=survey),
               # PlotNParticles(mad8opt, xstopt, beamParams, functions=functions, postfunctions=postfunctions, figsize=figsize, xlim=xlim, survey=survey)
              ]

    if saveAll:
        tfsname = repr(twiss)
        xstname = xstline.name
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
            d['Title'] = "{} (MAD8) VS {} (Xsuite) Optical Comparison".format(tfsname, xstname)
            d['CreationDate'] = _datetime.datetime.today()
        print("Written ", output_filename)
    return mad8opt


def PlotEnergy(mad8opt, xstopt, beamParams, survey=None, functions=None, postfunctions=None, figsize=(12, 5), xlim=(0, 0)):
    energyPlot = _plt.figure('Energy', figsize)

    # one missing energy due to initial
    _plt.plot(mad8opt.getColumnsByKeys('S'), mad8opt.getColumnsByKeys('E'), 'b--', label=r'MAD8 $E$')

    _plt.errorbar(xstopt.s, xstopt['E'], yerr=xstopt['Sigma_Mean_E'], label=r'Xsuite $E$', marker='x', ls='', color='b')

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
