import pymadx as _pymadx
import pybdsim as _pybdsim
import matplotlib.pyplot as _plt
from matplotlib import use as _use
import os as _os

def MadxVsBDSIM(tfsoptIn, bdsoptIn, survey=None,saveFigs=False,outdir='bdsmad-comp-result', start=None, stop=None, full=False):
    '''
    Compares MadX and BDSIM optics variables.
    User must provide a tfsoptIn file or Tfsinstance and a BDSAscii file or instance.

    Parameters:
    tfsoptin   :    tfs file or Tfs instance
    bdsoptin   :    bdsAscii file or instance.
    survey     :    BDSIM model survey
    saveFigs   :    save the figures automatically.  Default False.
    outdir     :    output directory for figures to be saved in if saveFigs==True
    start      :    A name or index where to begin the tfs lattice.  Preferably an index as names can repeat
    stop       :    A name or index where to end the tfs lattice.  Preferably an index as names can repeat
    full       :    Whether or not to plot dispersion plots.
    '''

    bdsopt = _GetBDSIMOptics(bdsoptIn)
    tfsopt = _GetTfsOptics(tfsoptIn, start, stop)
    _PlotOptics(tfsopt, bdsopt, outdir, saveFigs,survey, full)

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

    def GetROOTOptics():
        raise IOError("Module does not currently support ROOT files")

    if isinstance(opticsfile, _pybdsim.Data.BDSAsciiData):
        bdsoptics = opticsfile
        return GetDatOptics()
    elif isinstance(opticsfile, str):
        try:
            bdsoptics = _pybdsim.Data.Load(opticsfile)
            return GetDatOptics()
        except IOError:
            return GetROOTOptics()

def _GetTfsOptics(opticsIn,start, stop):
    '''
    Takes either Tfs file or instance.  Returns dictionary of lists.
    '''
    if isinstance(opticsIn, str):
        tfsopt = _pymadx.Tfs(opticsIn)
    elif isinstance(opticsIn, _pymadx.Tfs):
        tfsopt = opticsIn

    if stop != None:
        stopInd = _ReturnBoundaryIndex(tfsopt,stop)
        tfsopt = tfsopt[:stopInd]
    if start != None:
        # - 1 to allign with because MADX because
        # defines point as at the end of a component.
        startInd = _ReturnBoundaryIndex(tfsopt,start) - 1
        tfsopt = tfsopt[startInd:]

    _MADXOpticsVariables = ['NAME',
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
                            'PY']

    optvars = {}
    for variable in _MADXOpticsVariables:
        optvars[variable] = tfsopt.GetColumn(variable)
    return optvars

def _PlotOptics(tfsopt, bdsopt,outdir,saveFigs,survey, full):

    N = bdsopt['Npart'][0]  #number of primaries.

    def PlotBetas():
        betaPlot = _plt.figure('Beta')
        _plt.errorbar(tfsopt['S'], tfsopt['BETX'], label=r'MADX $\beta_{x}$')
        _plt.errorbar(tfsopt['S'], tfsopt['BETY'], label=r'MADX $\beta_{y}$')
        #bds
        _plt.errorbar(bdsopt['S'], bdsopt['Beta_x'], yerr=bdsopt['Sigma_Beta_x'] ,label=r'BDSIM $\beta_{x}$' + ' ; N=' + str(int(N)),marker='x', ls = '')
        _plt.errorbar(bdsopt['S'], bdsopt['Beta_y'], yerr=bdsopt['Sigma_Beta_y'],label=r'BDSIM $\beta_{y}$' + ' ; N=' + str(int(N)),marker='x', ls = '')
        axes = _plt.gcf().gca()
        axes.set_ylabel(r'$\beta_{x,y}$ / m')
        return betaPlot
    def PlotAlphas():
        alphaPlot = _plt.figure('Alpha')
        #tfs
        _plt.errorbar(tfsopt['S'], tfsopt['ALFX'], label=r'MADX $\alpha_{x}$')
        _plt.errorbar(tfsopt['S'], tfsopt['ALFY'], label=r'MADX $\alpha_{y}$')
        #bds
        _plt.errorbar(bdsopt['S'], bdsopt['Alpha_x'], yerr=bdsopt['Sigma_Alpha_x'] ,label=r'BDSIM $\alpha_{x}$' + ' ; N=' + str(int(N)),marker='x', ls = '')
        _plt.errorbar(bdsopt['S'], bdsopt['Alpha_y'], yerr=bdsopt['Sigma_Alpha_y'] ,label=r'BDSIM $\alpha_{y}$' + ' ; N=' + str(int(N)),marker='x', ls = '')
        axes = _plt.gcf().gca()
        axes.set_ylabel(r'$\alpha_{x,y}$ / m')
        return alphaPlot
    def PlotDs():
        dispPlot = _plt.figure('Dispersion')
        #tfs
        _plt.errorbar(tfsopt['S'], tfsopt['DX'], label=r'MADX $D_{x}$')
        _plt.errorbar(tfsopt['S'], tfsopt['DY'], label=r'MADX $D_{y}$')
        #bds
        _plt.errorbar(bdsopt['S'], bdsopt['Disp_x'], yerr=bdsopt['Sigma_Disp_x'] ,label=r'BDSIM $D_{x}$' + ' ; N=' + str(int(N)),marker='x', ls = '')
        _plt.errorbar(bdsopt['S'], bdsopt['Disp_y'], yerr=bdsopt['Sigma_Disp_y'] ,label=r'BDSIM $D_{y}$' + ' ; N=' + str(int(N)),marker='x', ls = '')
        axes = _plt.gcf().gca()
        axes.set_ylabel(r'$D_{x,y} / m$')
        return dispPlot
    def PlotDps():
        dispPPlot = _plt.figure('Momentum_Dispersion')
        #tfs
        _plt.errorbar(tfsopt['S'], tfsopt['DPX'], label=r'MADX $D_{p_{x}}$')
        _plt.errorbar(tfsopt['S'], tfsopt['DPY'], label=r'MADX $D_{p_{y}}$')
        #bds
        _plt.errorbar(bdsopt['S'], bdsopt['Disp_xp'], yerr=bdsopt['Sigma_Disp_xp'] ,label=r'BDSIM $D_{p_{x}}$' + ' ; N=' + str(int(N)),marker='x', ls = '')
        _plt.errorbar(bdsopt['S'], bdsopt['Disp_yp'], yerr=bdsopt['Sigma_Disp_yp'] ,label=r'BDSIM $D_{p_{y}}$' + ' ; N=' + str(int(N)),marker='x', ls = '')
        axes = _plt.gcf().gca()
        axes.set_ylabel(r'$D_{p_{x},p_{y}}$ / m')
        return dispPPlot
    def PlotSigmas():
        sigmaPlot = _plt.figure('Sigma')
        #tfs
        _plt.errorbar(tfsopt['S'], tfsopt['SIGMAX'], label=r'MADX $\sigma_{x}$')
        _plt.errorbar(tfsopt['S'], tfsopt['SIGMAY'], label=r'MADX $\sigma_{y}$')
        #bds
        _plt.errorbar(bdsopt['S'], bdsopt['Sigma_x'], yerr=bdsopt['Sigma_Sigma_x'] ,label=r'BDSIM $\sigma_{x}$' + ' ; N=' + str(int(N)),marker='x', ls = '')
        _plt.errorbar(bdsopt['S'], bdsopt['Sigma_y'], yerr=bdsopt['Sigma_Sigma_y'] ,label=r'BDSIM $\sigma_{y}$' + ' ; N=' + str(int(N)),marker='x', ls = '')
        axes = _plt.gcf().gca()
        axes.set_ylabel(r'$\sigma_{x,y}$ / m')
        return sigmaPlot
    def PlotMeans():
        meanPlot = _plt.figure('Mean')
        _plt.errorbar(tfsopt['S'], tfsopt['X'], label=r'MADX $\bar{x}$')
        _plt.errorbar(tfsopt['S'], tfsopt['Y'], label=r'MADX $\bar{y}$')
        #bds
        _plt.errorbar(bdsopt['S'], bdsopt['Mean_x'], yerr=bdsopt['Sigma_Mean_x'] ,label=r'BDSIM $\bar{x}$' + ' ; N=' + str(int(N)),marker='x', ls = '')
        _plt.errorbar(bdsopt['S'], bdsopt['Mean_y'], yerr=bdsopt['Sigma_Mean_y'] ,label=r'BDSIM $\bar{y}$' + ' ; N=' + str(int(N)),marker='x', ls = '')
        axes = _plt.gcf().gca()
        axes.set_ylabel(r'$\bar{x}, \bar{y}$ / m')
        return meanPlot


    figs = []

    figs.append(PlotBetas())
    figs.append(PlotAlphas())
    figs.append(PlotSigmas())
    figs.append(PlotMeans())

    if full:
        figs.append(PlotDs())
        figs.append(PlotDps())


    for index, figure in enumerate(figs):
        axes = figure.gca()
        axes.legend(loc='best')
        axes.set_xlabel('S / m')
        if survey != None:
            if survey.split(".")[-1] == 'dat':
                _pybdsim.Plot.AddMachineLatticeFromSurveyToFigure(figure,survey)
            else:
                _pybdsim.Plot.AddMachineLatticeToFigure(figure,survey)
            if saveFigs == True:
                if index == 0:  #only make directory once.
                    dirname = _pybdsim._General.GenUniqueFilename(outdir)
                    _os.mkdir(dirname)
                filename = figure.canvas.get_window_title()
                figure.savefig(dirname+'/' + filename +'.pdf')

    _plt.show()


def _ReturnBoundaryIndex(tfs, bound):
    if isinstance(bound, str):
        try:
            boundInd = tfs.IndexFromGmadName(bound)
        except ValueError:
            boundInd = tfs.IndexFromName(bound)
    elif isinstance(bound, int):
        boundInd = bound

    return boundInd
