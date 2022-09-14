import pymadx as _pymadx
import pybdsim as _pybdsim
import matplotlib.pyplot as _plt
import numpy as _np
from os.path import isfile as _isfile
from matplotlib.backends.backend_pdf import PdfPages as _PdfPages
import datetime as _datetime

from pybdsim.Data import LoadSDDSColumnsToDict as _LoadSDDSColumnsToDict
from pybdsim.Plot import AddMachineLatticeFromSurveyToFigure as _AddMachineLatticeFromSurveyToFigure

def ElegantVsBDSIM(elegantTwiss, elegantSigma, elegantCentroid, bdsim, functions=None,
                   postfunctions=None, figsize=(10, 5), saveAll=True, outputFileName=None):
    """
    Compares MadX and BDSIM optics variables.
    User must provide a tfsoptIn file or Tfsinstance and a BDSAscii file or instance.

    +-----------------+---------------------------------------------------------+
    | **Parameters**  | **Description**                                         |
    +-----------------+---------------------------------------------------------+
    | twiss           | Elegan twiss file instance.                             |
    +-----------------+---------------------------------------------------------+
    | bdsim           | Optics root file (from rebdsimOptics or rebdsim).       |
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
    
    """

    _CheckFileExistsList(elegantTwiss, elegantSigma, elegantCentroid, bdsim)

    fname = _pybdsim._General.GetFileName(bdsim) # cache file name
    if fname == "":
        fname = "optics_report"

    bdsData = _pybdsim.Data.Load(bdsim)

    bdsinst = _pybdsim._General.CheckItsBDSAsciiData(bdsData, True)
    bdsopt  = _GetBDSIMOptics(bdsinst)
    survey  = bdsData.model if hasattr(bdsData, "model") else None

    eTwi = _LoadSDDSColumnsToDict(elegantTwiss)
    eSig = _LoadSDDSColumnsToDict(elegantSigma)
    eCen = _LoadSDDSColumnsToDict(elegantCentroid)
    eleopt  = _GetElegantOptics(eTwi,eSig,eCen)

    figures = [PlotBeta(eleopt, bdsopt, survey=survey),
               PlotAlpha(eleopt, bdsopt, survey=survey),
               PlotDisp(eleopt, bdsopt, survey=survey),
               PlotDispP(eleopt, bdsopt, survey=survey),
               PlotSigma(eleopt, bdsopt, survey=survey),
               PlotSigmaP(eleopt, bdsopt, survey=survey),
               PlotMean(eleopt, bdsopt, survey=survey)]
    #PlotEmitt(eleopt, bdsopt, tfsinst.header, survey=survey)
    #           PlotNParticles(bdsopt, survey=survey)

    if saveAll:
        tfsname = elegantTwiss.split('/')[-1].split('.')[0]
        bdsname = repr(bdsinst)
        output_filename = "optics-report.pdf"
        if outputFileName is not None:
            output_filename = outputFileName
            if not output_filename.endswith('.pdf'):
                output_filename += ".pdf"
        else:
            output_filename = fname.replace('.root','')
            output_filename += ".pdf"
        # Should have a more descriptive name really.
        with _PdfPages(output_filename) as pdf:
            for figure in figures:
                pdf.savefig(figure)
            d = pdf.infodict()
            d['Title'] = "{} (TFS) VS {} (BDSIM) Optical Comparison".format(tfsname, bdsname)
            d['CreationDate'] = _datetime.datetime.today()

        print("Written ", output_filename)


def _GetBDSIMOptics(optics):
    """
    Takes a BDSAscii instance.
    Return a dictionary of lists matching the variable with the list of values.
    """
    optvars = {}
    for variable in optics.names:
        datum = getattr(optics, variable)()
        optvars[variable] = datum
    return optvars

def _GetElegantOptics(twiss, sigma, centroid):
    """
    Requires 3 dicts for twiss, sigma and centroid files from Elegant.
    """
    eTwissToMadx = {'ElementName':'NAME',
                    's': 'S',
                    'betax':'BETX',
                    'betay':'BETY',
                    'alphax':'ALFX',
                    'alphay':'ALFY',
                    'etax':'DX',
                    'etaxp':'DPX',
                    'etay':'DY',
                    'etayp':'DPY'}
    eSigmaToMadx = {'Sx':'SIGMAX',
                    'Sy':'SIGMAY',
                    'Sxp':'SIGMAXP',
                    'Syp':'SIGMAYP',
                    'ex':'EX',
                    'ey':'EY'}
    eCentroidToMadx = {'Cx':'X',
                       'Cy':'Y',
                       'Cxp':'PX',
                       'Cyp':'PY'}
    
    optvars = {}
    for kele,kmadx in eTwissToMadx.items():
        optvars[kmadx] = twiss[kele]
    for kele,kmadx in eSigmaToMadx.items():
        optvars[kmadx] = sigma[kele]
    for kele,kmadx in eCentroidToMadx.items():
        optvars[kmadx] = centroid[kele]
    return optvars

def _GetTfsOrbit(optics):
    '''
    Takes either Tfs instance.  Returns dictionary of lists.
    '''

    MADXOpticsVariables = frozenset(['S',
                                     'X',
                                     'Y',
                                     'PX',
                                     'PY'])

    optvars = {}
    for variable in MADXOpticsVariables:
        optvars[variable] = optics.GetColumn(variable)
    return optvars

# Predefined lists of tuples for making the standard plots,
# format = (optical_var_name, optical_var_error_name, legend_name)

_BETA = [("BETX", "Beta_x", "Sigma_Beta_x", r'$\beta_{x}$'),
         ("BETY", "Beta_y", "Sigma_Beta_y", r'$\beta_{y}$')]

_ALPHA = [("ALFX", "Alpha_x", "Sigma_Alpha_x", r"$\alpha_{x}$"),
          ("ALFY", "Alpha_y", "Sigma_Alpha_y", r"$\alpha_{y}$")]

_DISP = [("DX", "Disp_x", "Sigma_Disp_x", r"$D_{x}$"),
         ("DY", "Disp_y", "Sigma_Disp_y", r"$D_{y}$")]

_DISP_P = [("DPX", "Disp_xp", "Sigma_Disp_xp", r"$D_{p_{x}}$"),
           ("DPY", "Disp_yp", "Sigma_Disp_yp", r"$D_{p_{y}}$")]

_SIGMA = [("SIGMAX", "Sigma_x", "Sigma_Sigma_x", r"$\sigma_{x}$"),
          ("SIGMAY", "Sigma_y", "Sigma_Sigma_y", r"$\sigma_{y}$")]

_SIGMA_P = [("SIGMAXP", "Sigma_xp", "Sigma_Sigma_xp", r"$\sigma_{xp}$"),
            ("SIGMAYP", "Sigma_yp", "Sigma_Sigma_yp", r"$\sigma_{yp}$")]

_MEAN = [("X", "Mean_x", "Sigma_Mean_x", r"$\bar{x}$"),
         ("Y", "Mean_y", "Sigma_Mean_y", r"$\bar{y}$")]

def _MakePlotter(plot_info_tuples, x_label, y_label, title):
    def f_out(ele, bds, survey=None, **kwargs):
        # options
        tightLayout = True
        if 'tightLayout' in kwargs:
            tightLayout = kwargs['tightLayout']

        # Get the initial N for the two sources
        first_nparticles = bds['Npart'][0]

        plot = _plt.figure(title, figsize=(9,5), **kwargs)
        colours = ('b', 'g')
        # Loop over the variables in plot_info_tuples and draw the plots.
        for a, colour in zip(plot_info_tuples, colours):
            eVar, bVar, bError, legend_name = a # unpack one tuple
            bdsS = bds['S'] # cache data
            bdsD = bds[bVar]
            bdsE = bds[bError]
            l = "{} {}; N = {:.1E}".format("", legend_name, first_nparticles),
            _plt.errorbar(bdsS, bdsD, fmt=colour+".", yerr=bdsE, label='BDSIM', capsize=3, **kwargs)
            #_plt.plot(bdsS, bdsD, colour) # line plot without label
            eS = ele['S']
            eVar = ele[eVar]
            _plt.plot(eS, eVar, colour+"--", label='Elegant')
            #_plt.plot(eS, eVar, colour+".")

        # Set axis labels and draw legend
        axes = _plt.gcf().gca()
        axes.set_ylabel(y_label)
        axes.set_xlabel(x_label)
        axes.legend(loc='best')

        if survey is not None:
            _AddMachineLatticeFromSurveyToFigure(plot, survey, tightLayout)
        else:
            _plt.tight_layout()

        _plt.show(block=False)

        return plot
    return f_out

PlotBeta   = _MakePlotter(_BETA,    "S / m", r"$\beta_{x,y}$ / m",      "Beta")
PlotAlpha  = _MakePlotter(_ALPHA,   "S / m", r"$\alpha_{x,y}$ / m",     "Alpha")
PlotDisp   = _MakePlotter(_DISP,    "S / m", r"$D_{x,y} / m$",          "Dispersion")
PlotDispP  = _MakePlotter(_DISP_P,  "S / m", r"$D_{p_{x},p_{y}}$ / m",  "Momentum_Dispersion")
PlotSigma  = _MakePlotter(_SIGMA,   "S / m", r"$\sigma_{x,y}$ / m",     "Sigma")
PlotSigmaP = _MakePlotter(_SIGMA_P, "S / m", r"$\sigma_{xp,yp}$ / rad", "SigmaP")
PlotMean   = _MakePlotter(_MEAN,    "S / m", r"$\bar{x}, \bar{y}$ / m", "Mean")


def PlotEmitt(eleopt, bdsopt, header, survey=None, functions=None, postfunctions=None, figsize=(12, 5)):
    N = str(int(bdsopt['Npart'][0]))  # number of primaries.
    emittPlot = _plt.figure('Emittance', figsize=figsize)
    ex = header['EX'] * _np.ones(len(eleopt['S']))
    ey = header['EY'] * _np.ones(len(eleopt['S']))

    # tfs
    _plt.plot(eleopt['S'], ex, 'b', label=r'MADX $E_{x}$')
    _plt.plot(eleopt['S'], ey, 'g', label=r'MADX $E_{x}$')
    # bds
    _plt.errorbar(bdsopt['S'], bdsopt['Emitt_x'],
                  yerr=bdsopt['Sigma_Emitt_x'],
                  label=r'BDSIM $E_{x}$' + ' ; N = ' + N,
                  fmt='b.', capsize=3)

    _plt.errorbar(bdsopt['S'], bdsopt['Emitt_y'],
                  yerr=bdsopt['Sigma_Emitt_y'],
                  label=r'BDSIM $E_{y}$' + ' ; N = ' + N,
                  fmt='g.', capsize=3)

    axes = _plt.gcf().gca()
    axes.set_ylabel(r'$E_{x,y} / m$')
    axes.set_xlabel('S / m')
    axes.legend(loc='best')

    _CallUserFigureFunctions(functions)
    _AddSurvey(emittPlot, survey)
    _CallUserFigureFunctions(postfunctions)

    _plt.show(block=False)
    return emittPlot

def PlotNParticles(bdsopt, survey=None, functions=None, postfunctions=None, figsize=(12, 5)):
    npartPlot = _plt.figure('NParticles', figsize)

    _plt.plot(bdsopt['S'],bdsopt['Npart'], 'k-', label='BDSIM N Particles')
    _plt.plot(bdsopt['S'],bdsopt['Npart'], 'k.')
    axes = _plt.gcf().gca()
    axes.set_ylabel(r'N Particles')
    axes.set_xlabel('S / m')
    axes.legend(loc='best')

    _CallUserFigureFunctions(functions)
    _AddSurvey(npartPlot, survey)
    _CallUserFigureFunctions(postfunctions)

    _plt.show(block=False)
    return npartPlot

def _CheckFileExistsList(*fns):
    for fn in fns:
        _CheckFileExists(fn)

def _CheckFileExists(fn):
    if isinstance(fn, str):
        if not _isfile(fn):
            raise IOError('File "'+fn+'" not found')
