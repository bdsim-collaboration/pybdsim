import pybdsim as _pybdsim
import matplotlib.pyplot as _plt
from os.path import isfile as _isfile
from matplotlib.backends.backend_pdf import PdfPages as _PdfPages
import datetime as _datetime

from pybdsim.Data import LoadSDDSColumnsToDict as _LoadSDDSColumnsToDict
from pybdsim.Plot import AddMachineLatticeFromSurveyToFigure as _AddMachineLatticeFromSurveyToFigure

def ElegantVsBDSIM(elegantTwiss, elegantSigma, elegantCentroid, bdsim, functions=None,
                   postfunctions=None, figsize=(10, 5), saveAll=True, outputFileName=None,
                   particleType="e-"):
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
    eleopt  = _GetElegantOptics(eTwi,eSig,eCen,particleType)

    figures = [PlotBeta(eleopt, bdsopt, survey=survey),
               PlotAlpha(eleopt, bdsopt, survey=survey),
               PlotDisp(eleopt, bdsopt, survey=survey),
               PlotDispP(eleopt, bdsopt, survey=survey),
               PlotSigma(eleopt, bdsopt, survey=survey),
               PlotSigmaP(eleopt, bdsopt, survey=survey),
               PlotMean(eleopt, bdsopt, survey=survey),
               PlotEmitt(eleopt, bdsopt, survey=survey),
               PlotNParticles(bdsopt, survey=survey),
               PlotEnergy(eleopt, bdsopt, survey=survey)]

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

def _GetElegantOptics(twiss, sigma, centroid, particleType="e-"):
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
                    'ey':'EY',
                    'Sdelta':'SIGMAP'}
    eCentroidToMadx = {'Cx':'X',
                       'Cy':'Y',
                       'Cxp':'PX',
                       'Cyp':'PY',
                       'pCentral':'P'}
    
    optvars = {}
    for kele,kmadx in eTwissToMadx.items():
        optvars[kmadx] = twiss[kele]
    for kele,kmadx in eSigmaToMadx.items():
        optvars[kmadx] = sigma[kele]
    for kele,kmadx in eCentroidToMadx.items():
        optvars[kmadx] = centroid[kele]

    massDict = {"e-" : 0.00051099891,
                "proton" : 0.938}
    massDict["e+"] = massDict["e-"]

    optvars['P'] *= massDict[particleType] # fix energy from lorentz gamma to E (yeah... P vs E..)
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

_EMITT = [("EX", "Emitt_x", "Sigma_Emitt_x", r"$\eta_{x}$"),
          ("EY", "Emitt_y", "Sigma_Emitt_y", r"$\eta_{y}$")]

_ENERGY = [("P", "Mean_E", "Sigma_E", r"Energy")]

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
PlotEmitt  = _MakePlotter(_EMITT,   "S / m", r"$\eta_{x}, \eta_{y}$ / rad m", "Emittance")
PlotEnergy = _MakePlotter(_ENERGY,  "S / m", r"Total Energy / GeV",     "Energy")

def PlotNParticles(bdsopt, survey=None, **kwargs):
    # options
    tightLayout = kwargs['tightLayout'] if 'tightLayout' in kwargs else True
    
    npartPlot = _plt.figure('NParticles', figsize=(9,5), **kwargs)

    _plt.plot(bdsopt['S'],bdsopt['Npart'], 'k-', label='BDSIM N Particles')
    _plt.plot(bdsopt['S'],bdsopt['Npart'], 'k.')
    axes = _plt.gcf().gca()
    axes.set_ylabel(r'N Particles')
    axes.set_xlabel('S / m')
    axes.legend(loc='best')

    if survey is not None:
        _AddMachineLatticeFromSurveyToFigure(npartPlot, survey, tightLayout)
    else:
        _plt.tight_layout()

    _plt.show(block=False)
    return npartPlot

def _CheckFileExistsList(*fns):
    for fn in fns:
        _CheckFileExists(fn)

def _CheckFileExists(fn):
    if isinstance(fn, str):
        if not _isfile(fn):
            raise IOError('File "'+fn+'" not found')
