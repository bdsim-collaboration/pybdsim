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
    functions  :    Hook for users to add their functions which are called
                    immediately prior to the addition of the plot.  Use lambda
                    to add functions with arguments.
    '''

    _CheckFilesExist(tfs, bdsim, survey)

    tfsinst   = _pymadx._General.CheckItsTfs(tfs)
    bdsinst   = _pybdsim._General.CheckItsBDSAsciiData(bdsim)

    tfsopt    = _GetTfsOptics(tfsinst)
    bdsopt    = _GetBDSIMOptics(bdsinst)

    if survey == None:
        survey = tfsinst

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

def _GetBDSIMOptics(optics):
    '''
    Takes a BDSAscii instance.
    Return a dictionary of lists matching the variable with the list of values.
    '''
    optvars = {}
    for variable in optics.names:
        datum = getattr(optics, variable)()
        optvars[variable] = datum
    return optvars

def _GetTfsOptics(optics):
    '''
    Takes either Tfs instance.  Returns dictionary of lists.
    '''

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
        optvars[variable] = optics.GetColumn(variable)
    return optvars

def PlotBetas(tfsopt, bdsopt, survey=None, functions=None):

    N = str(int(bdsopt['Npart'][0]))  #number of primaries.
    betaPlot = _plt.figure('Beta')
    _plt.plot(tfsopt['S'], tfsopt['BETX'], 'b', label=r'MADX $\beta_{x}$')
    _plt.plot(tfsopt['S'], tfsopt['BETY'], 'g', label=r'MADX $\beta_{y}$')

    #bds
    _plt.errorbar(bdsopt['S'], bdsopt['Beta_x'],
                  yerr=bdsopt['Sigma_Beta_x'],
                  label=r'BDSIM $\beta_{x}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '',
                  color='b')

    _plt.errorbar(bdsopt['S'], bdsopt['Beta_y'],
                  yerr=bdsopt['Sigma_Beta_y'],
                  label=r'BDSIM $\beta_{y}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '',
                  color='g')

    axes = _plt.gcf().gca()
    axes.set_ylabel(r'$\beta_{x,y}$ / m')
    axes.set_xlabel('S from IR1 / m')

    print "survey =", survey

    _CallUserFigureFunctions(functions)
    _AddSurvey(betaPlot, survey)

    _plt.show(block=False)
    return betaPlot

def PlotAlphas(tfsopt, bdsopt, survey=None, functions=None):
    N = str(int(bdsopt['Npart'][0]))  #number of primaries.
    alphaPlot = _plt.figure('Alpha')
    #tfs
    _plt.plot(tfsopt['S'], tfsopt['ALFX'], 'b', label=r'MADX $\alpha_{x}$')
    _plt.plot(tfsopt['S'], tfsopt['ALFY'], 'g', label=r'MADX $\alpha_{y}$')
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
    _plt.plot(tfsopt['S'], tfsopt['DX'], 'b', label=r'MADX $D_{x}$')
    _plt.plot(tfsopt['S'], tfsopt['DY'], 'g', label=r'MADX $D_{y}$')
    #bds
    _plt.errorbar(bdsopt['S'], bdsopt['Disp_x'],
                  yerr=bdsopt['Sigma_Disp_x'],
                  label=r'BDSIM $D_{x}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '',
                  color='b')

    _plt.errorbar(bdsopt['S'], bdsopt['Disp_y'],
                  yerr=bdsopt['Sigma_Disp_y'],
                  label=r'BDSIM $D_{y}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '',
                  color='g')

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
    _plt.plot(tfsopt['S'], tfsopt['DPX'], 'b', label=r'MADX $D_{p_{x}}$')
    _plt.plot(tfsopt['S'], tfsopt['DPY'], 'g', label=r'MADX $D_{p_{y}}$')
    #bds
    _plt.errorbar(bdsopt['S'], bdsopt['Disp_xp'],
                  yerr=bdsopt['Sigma_Disp_xp'],
                  label=r'BDSIM $D_{p_{x}}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '',
                  color='b')

    _plt.errorbar(bdsopt['S'], bdsopt['Disp_yp'],
                  yerr=bdsopt['Sigma_Disp_yp'],
                  label=r'BDSIM $D_{p_{y}}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '',
                  color='g')

    axes = _plt.gcf().gca()
    axes.set_ylabel(r'$D_{p_{x},p_{y}}$ / m')
    axes.set_xlabel('S from IR1 / m')
    axes.legend(loc='best')

    _CallUserFigureFunctions(functions)
    _AddSurvey(dispPPlot, survey)

    _plt.show(block=False)
    return dispPPlot

def PlotSigmas(tfsopt, bdsopt, survey=None, functions=None):
    N = str(int(bdsopt['Npart'][0]))  #number of primaries.
    sigmaPlot = _plt.figure('Sigma')
    #tfs
    _plt.plot(tfsopt['S'], tfsopt['SIGMAX'], 'b', label=r'MADX $\sigma_{x}$')
    _plt.plot(tfsopt['S'], tfsopt['SIGMAY'], 'g', label=r'MADX $\sigma_{y}$')
    #bds
    _plt.errorbar(bdsopt['S'],
                  bdsopt['Sigma_x'],
                  yerr=bdsopt['Sigma_Sigma_x'],
                  label=r'BDSIM $\sigma_{x}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '',
                  color='b')

    _plt.errorbar(bdsopt['S'],
                  bdsopt['Sigma_y'],
                  yerr=bdsopt['Sigma_Sigma_y'],
                  label=r'BDSIM $\sigma_{y}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '',
                  color='g')

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


    _plt.plot(tfsopt['S'], tfsopt['X'], 'b', label=r'MADX $\bar{x}$')
    _plt.plot(tfsopt['S'], tfsopt['Y'], 'g', label=r'MADX $\bar{y}$')

    #bdsim
    _plt.errorbar(bdsopt['S'], bdsopt['Mean_x'],
                  yerr=bdsopt['Sigma_Mean_x'],
                  label=r'BDSIM $\bar{x}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '',
                  color='b')

    _plt.errorbar(bdsopt['S'], bdsopt['Mean_y'],
                  yerr=bdsopt['Sigma_Mean_y'],
                  label=r'BDSIM $\bar{y}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '',
                  color='g')

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
    if type(survey) == str:
        if survey.split(".")[-1] == 'dat':
            _pybdsim.Plot.AddMachineLatticeFromSurveyToFigure(figure,survey)
    elif type(survey) == _pybdsim.Data.BDSAsciiData:
        _pybdsim.Plot.AddMachineLatticeToFigure(figure,survey)
    elif type(survey) == _pymadx.Tfs:
        _pymadx.Plot.AddMachineLatticeToFigure(figure,survey)

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
    if isinstance(tfs, str):
        if not isfile(tfs):
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
