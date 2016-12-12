import pymadx as _pymadx
import pybdsim as _pybdsim
import matplotlib.pyplot as _plt
from os.path import isfile

def MadxVsBDSIM(tfs, bdsim, survey=None, functions=None):
    '''
    Compares MadX and BDSIM optics variables.
    User must provide a tfsoptIn file or Tfsinstance and a BDSAscii file or instance.

    Parameters:
    tfs        :    tfs file or Tfs instance
    bdsim      :    optics root file (from rebdsimOptics or rebdsim) or
    survey     :    BDSIM model survey
    functions  :    A function or list of functions which
                    are called immediately prior to adding survey to figure.
                    For some reason there is no pythonic way to add to figure
                    after having added survey.  So this is next best thing.
    '''

    _CheckFilesExist(tfs, bdsim, survey)

    tfsopt = _GetTfsOptics(tfs)
    bdsopt = _GetBDSIMOptics(bdsim)

    PlotBetas(tfsopt, bdsopt, survey=survey,
              functions=functions)
    PlotAlphas(tfsopt, bdsopt, survey=survey,
               functions=functions)
    PlotDs(tfsopt, bdsopt, survey=survey,
           functions=functions)
    PlotDps(tfsopt, bdsopt, survey=survey,
            functions=functions)
    PlotSigmas(tfsopt, bdsopt, survey=survey,
               functions=functions)
    PlotMeans(tfsopt, bdsopt, survey=survey,
              functions=functions)



def _GetBDSIMOptics(opticsfile):
    '''
    Takes either a BDSAscii instance or file.
    Return a dictionary of lists matching the variable with the list of values.
    '''
    def GetDatOptics():
        optvars = {}
        for variable in bdsoptics.names:
            datum = getattr(bdsoptics, variable)()
            optvars[variable] = datum
        return optvars

    if isinstance(opticsfile, _pybdsim.Data.BDSAsciiData):
        bdsoptics = opticsfile
        return GetDatOptics()
    elif isinstance(opticsfile, str):
        bdsoptics = _pybdsim.Data.Load(opticsfile)
        return GetDatOptics()

def _GetTfsOptics(opticsIn):
    '''
    Takes either Tfs file or instance.  Returns dictionary of lists.
    '''
    if isinstance(opticsIn, str):
        tfsopt = _pymadx.Tfs(opticsIn)
    elif isinstance(opticsIn, _pymadx.Tfs):
        tfsopt = opticsIn

    MADXOpticsVariables = frozenset(['NAME',
                                     'S',
                                     'BETX',
                                     'BETY',
                                     'ALFX',
                                     'ALFY',
                                     'DX',
                                     'DPX',
                                     'DY',
                                     'DPY',
                                     'SIGMAX',
                                     'SIGMAY',
                                     'SIGMAXP',
                                     'SIGMAYP',
                                     'X',
                                     'Y',
                                     'PX',
                                     'PY'])

    optvars = {}
    for variable in MADXOpticsVariables:
        optvars[variable] = tfsopt.GetColumn(variable)
    return optvars

def PlotBetas(tfsopt, bdsopt, survey=None, functions=None):

    N = str(int(bdsopt['Npart'][0]))  #number of primaries.
    betaPlot = _plt.figure('Beta')
    _plt.errorbar(tfsopt['S'], tfsopt['BETX'], label=r'MADX $\beta_{x}$')
    _plt.errorbar(tfsopt['S'], tfsopt['BETY'], label=r'MADX $\beta_{y}$')

    #bds
    _plt.errorbar(bdsopt['S'], bdsopt['Beta_x'],
                  yerr=bdsopt['Sigma_Beta_x'],
                  label=r'BDSIM $\beta_{x}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '')

    _plt.errorbar(bdsopt['S'], bdsopt['Beta_y'],
                  yerr=bdsopt['Sigma_Beta_y'],
                  label=r'BDSIM $\beta_{y}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '')

    axes = _plt.gcf().gca()
    axes.set_ylabel(r'$\beta_{x,y}$ / m')
    axes.set_xlabel('S from IR1 / m')

    print "survey = ", survey

    _CallUserFigureFunctions(functions)
    _AddSurvey(betaPlot, survey)

    _plt.show(block=False)
    return betaPlot

def PlotAlphas(tfsopt, bdsopt, survey=None, functions=None):
    N = str(int(bdsopt['Npart'][0]))  #number of primaries.
    alphaPlot = _plt.figure('Alpha')
    #tfs
    _plt.errorbar(tfsopt['S'], tfsopt['ALFX'], label=r'MADX $\alpha_{x}$')
    _plt.errorbar(tfsopt['S'], tfsopt['ALFY'], label=r'MADX $\alpha_{y}$')

    #bds
    _plt.errorbar(bdsopt['S'], bdsopt['Alpha_x'],
                  yerr=bdsopt['Sigma_Alpha_x'],
                  label=r'BDSIM $\alpha_{x}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '')

    _plt.errorbar(bdsopt['S'], bdsopt['Alpha_y'],
                  yerr=bdsopt['Sigma_Alpha_y'],
                  label=r'BDSIM $\alpha_{y}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '')

    axes = _plt.gcf().gca()
    axes.set_ylabel(r'$\alpha_{x,y}$ / m')
    axes.set_xlabel('S from IR1 / m')
    axes.legend(loc='best')


    _CallUserFigureFunctions(functions)
    _AddSurvey(alphaPlot, survey)

    _plt.show(block=False)
    return alphaPlot

def PlotDs(tfsopt, bdsopt, survey=None, functions=None):
    N = str(int(bdsopt['Npart'][0]))  #number of primaries.
    dispPlot = _plt.figure('Dispersion')
    #tfs
    _plt.errorbar(tfsopt['S'], tfsopt['DX'], label=r'MADX $D_{x}$')
    _plt.errorbar(tfsopt['S'], tfsopt['DY'], label=r'MADX $D_{y}$')
    #bds
    _plt.errorbar(bdsopt['S'], bdsopt['Disp_x'],
                  yerr=bdsopt['Sigma_Disp_x'],
                  label=r'BDSIM $D_{x}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '')

    _plt.errorbar(bdsopt['S'], bdsopt['Disp_y'],
                  yerr=bdsopt['Sigma_Disp_y'],
                  label=r'BDSIM $D_{y}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '')

    axes = _plt.gcf().gca()
    axes.set_ylabel(r'$D_{x,y} / m$')
    axes.set_xlabel('S from IR1 / m')
    axes.legend(loc='best')


    _CallUserFigureFunctions(functions)
    _AddSurvey(dispPlot, survey)

    _plt.show(block=False)
    return dispPlot

def PlotDps(tfsopt, bdsopt, survey=None, functions=None):
    N = str(int(bdsopt['Npart'][0]))  #number of primaries.
    dispPPlot = _plt.figure('Momentum_Dispersion')
    #tfs
    _plt.errorbar(tfsopt['S'], tfsopt['DPX'], label=r'MADX $D_{p_{x}}$')
    _plt.errorbar(tfsopt['S'], tfsopt['DPY'], label=r'MADX $D_{p_{y}}$')
    #bds
    _plt.errorbar(bdsopt['S'], bdsopt['Disp_xp'],
                  yerr=bdsopt['Sigma_Disp_xp'],
                  label=r'BDSIM $D_{p_{x}}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '')

    _plt.errorbar(bdsopt['S'], bdsopt['Disp_yp'],
                  yerr=bdsopt['Sigma_Disp_yp'],
                  label=r'BDSIM $D_{p_{y}}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '')

    axes = _plt.gcf().gca()
    axes.set_ylabel(r'$D_{p_{x},p_{y}}$ / m')
    axes.set_xlabel('S from IR1 / m')
    axes.legend(loc='best')


    _CallUserFigureFunctions(functions)
    _AddSurvey(dispPPlot, survey)

    return dispPPlot

def PlotSigmas(tfsopt, bdsopt, survey=None, functions=None):
    N = str(int(bdsopt['Npart'][0]))  #number of primaries.
    sigmaPlot = _plt.figure('Sigma')
    #tfs
    _plt.plot(tfsopt['S'],
              tfsopt['SIGMAX'],
              label=r'MADX $\sigma_{x}$')
    _plt.plot(tfsopt['S'],
              tfsopt['SIGMAY'],
              label=r'MADX $\sigma_{y}$')
    #bds
    _plt.errorbar(bdsopt['S'],
                  bdsopt['Sigma_x'],
                  yerr=bdsopt['Sigma_Sigma_x'],
                  label=r'BDSIM $\sigma_{x}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '')

    _plt.errorbar(bdsopt['S'], bdsopt['Sigma_y'],
                  yerr=bdsopt['Sigma_Sigma_y'],
                  label=r'BDSIM $\sigma_{y}$' + ' ; N = ' + N,
                  marker='x', ls = '')

    axes = _plt.gcf().gca()
    axes.set_ylabel(r'$\sigma_{x,y}$ / m')
    axes.set_xlabel('S from IR1 / m')
    axes.legend(loc='best')

    _CallUserFigureFunctions(functions)
    _AddSurvey(sigmaPlot, survey)

    _plt.show(block=False)
    return sigmaPlot

def PlotMeans(tfsopt, bdsopt, survey=None, functions=None):
    N = str(int(bdsopt['Npart'][0]))  #number of primaries.
    meanPlot = _plt.figure('Mean')


    _plt.plot(tfsopt['S'], tfsopt['X'], label=r'MADX $\bar{x}$')
    _plt.plot(tfsopt['S'], tfsopt['Y'], label=r'MADX $\bar{y}$')

    #bdsim
    _plt.errorbar(bdsopt['S'], bdsopt['Mean_x'],
                  yerr=bdsopt['Sigma_Mean_x'],
                  label=r'BDSIM $\bar{x}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '')

    _plt.errorbar(bdsopt['S'], bdsopt['Mean_y'],
                  yerr=bdsopt['Sigma_Mean_y'],
                  label=r'BDSIM $\bar{y}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '')

    axes = _plt.gcf().gca()
    axes.set_ylabel(r'$\bar{x}, \bar{y}$ / m')
    axes.set_xlabel('S from IR1 / m')
    axes.legend(loc='best')


    _CallUserFigureFunctions(functions)
    _AddSurvey(meanPlot, survey)

    _plt.show(block=False)
    return meanPlot

def _AddSurvey(figure, survey):
    if survey == None:
        return
    if survey.split(".")[-1] == 'dat':
        _pybdsim.Plot.AddMachineLatticeFromSurveyToFigure(figure,survey)
    else:
        _pybdsim.Plot.AddMachineLatticeToFigure(figure,survey)

def _ProcessInput(tfsOptics, bdsimOptics):

    if not isinstance(tfsOptics, (_pymadx.Tfs, str)):
        raise TypeError("tfsOptics should be either a path to a tfs file or "
                        "a pymadx.Tfs instance!")
    if not isinstance(bdsimOptics, _pybdsim.Data.BDSAsciiData):
        raise TypeError("bdsimOptics should be either be a path to a "
                        "BDSAsciiData file or a pybdsim.Data.BDSAsciiData "
                        "instance")

    if isinstance(tfsOptics, str):
        tfsOptics = _pymadx.Tfs(tfsOptics)
    if isinstance(tfsOptics, str):
        bdsimOptics = _pybdsim.Data.Load(bdsimOptics)

    return tfsOptics, bdsimOptics

def _CheckFilesExist(tfs, bdsim, survey):
    '''
    Otherwise such errors are too cryptic.
    '''
    if isinstance(tfs, str) and not isfile(tfs):
        raise IOError("File not found: ", tfs)
    if isinstance(bdsim, str) and not isfile(bdsim):
        raise IOError("File not found: ", bdsim)
    if isinstance(survey, str) and not isfile(survey):
        raise IOError("File not found: ", survey)


def _CallUserFigureFunctions(functions):
    if isinstance(functions, list):
        for function in functions:
            if callable(function):
                function()
    elif callable(functions):
        functions()
