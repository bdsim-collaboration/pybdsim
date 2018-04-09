import pickle as _pkl
import pylab  as _pl
import pymad8 as _pymad8
import pybdsim as _pybdsim
import matplotlib.pyplot as _plt
import numpy as _np
from os.path import isfile as _isfile
from matplotlib.backends.backend_pdf import PdfPages as _PdfPages
import datetime as _datetime

def Mad8VsBDSIM(twiss, envel, bdsim, survey=None, functions=None,
                postfunctions=None, figsize=(10, 5), saveAll=True, outputFileName=None):
    """
    Compares Mad8 and BDSIM optics variables.

    +-----------------+---------------------------------------------------------+
    | **Parameters**  | **Description**                                         |
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
    """

    _CheckFilesExist(twiss, envel, bdsim)

    fname = _pybdsim._General.GetFileName(bdsim) # cache file name
    if fname == "":
        fname = "optics_report"
    
    # load mad8 optics
    mad8reader   = _pymad8.Output.OutputReader() 
    [com, twissL] = mad8reader.readFile(twiss,'twiss')
    [com, envelL] = mad8reader.readFile(envel,'envel')
    
    # load bdsim optics
    bdsinst = _pybdsim._General.CheckItsBDSAsciiData(bdsim)
    bdsopt  = _GetBDSIMOptics(bdsinst)
    
    # make plots 
    mad8opt = {'comm':com, 'twiss':twissL, 'envel':envelL}
    
    figures = [PlotBetas(mad8opt,bdsopt,functions=functions,
                         postfunctions=postfunctions,
                         figsize=figsize),
               PlotAlphas(mad8opt,bdsopt,functions=functions,
                          postfunctions=postfunctions,
                          figsize=figsize),
               PlotDs(mad8opt,bdsopt,functions=functions,
                      postfunctions=postfunctions,
                      figsize=figsize),
               PlotDps(mad8opt,bdsopt,functions=functions,
                       postfunctions=postfunctions,
                       figsize=figsize),
               PlotSigmas(mad8opt,bdsopt,functions=functions,
                          postfunctions=postfunctions,
                          figsize=figsize),
               PlotSigmasP(mad8opt,bdsopt,functions=functions,
                           postfunctions=postfunctions,
                           figsize=figsize),
               PlotEnergy(mad8opt,bdsopt,functions=functions,
                          postfunctions=postfunctions,
                          figsize=figsize),
               PlotMeans(mad8opt,bdsopt,functions=functions,
                         postfunctions=postfunctions,
                         figsize=figsize),
               PlotEmittance(mad8opt,bdsopt,functions=functions,
                             postfunctions=postfunctions,
                             figsize=figsize),
               PlotNParticles(mad8opt,bdsopt,functions=functions,
                              postfunctions=postfunctions,
                              figsize=figsize)]    
    if saveAll:
        tfsname = repr(twiss)
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
            d['Title'] = "{} (MAD8) VS {} (BDSIM) Optical Comparison".format(tfsname, bdsname)
            d['CreationDate'] = _datetime.datetime.today()

        print "Written ", output_filename
    
    return mad8opt

def _CheckFilesExist(twiss, envel, bdsim):
    '''
    Otherwise such errors are too cryptic.
    '''
    if not _isfile(twiss):
        raise IOError("File not found: ", twiss)
    if not _isfile(envel):
        raise IOError("File not found: ", envel);
    if isinstance(bdsim, basestring) and not _isfile(bdsim):
        raise IOError("File not found: ", bdsim)

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

def PlotBetas(mad8opt, bdsopt, survey=None, functions=None, postfunctions=None, figsize=(12,5)) :
    N = str(int(bdsopt['Npart'][0]))  #number of primaries.
    betaPlot = _plt.figure('Beta',figsize)
    
    _plt.plot(mad8opt['twiss'].getColumn('suml'), 
              mad8opt['twiss'].getColumn('betx'),
              'b', label=r'MAD8 $\beta_{x}$')
    _plt.plot(mad8opt['twiss'].getColumn('suml'), 
              mad8opt['twiss'].getColumn('bety'),
              'g', label=r'MAD8 $\beta_{y}$')
    
    # bds plot
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
    axes.set_xlabel('S / m')
    axes.legend(loc='best')

    _CallUserFigureFunctions(functions)
    _AddSurvey(betaPlot, mad8opt)
    _CallUserFigureFunctions(postfunctions)
    
    _plt.show(block=False)
    return betaPlot

def PlotAlphas(mad8opt, bdsopt, survey=None, functions=None, postfunctions=None, figsize=(12,5)) :
    N = str(int(bdsopt['Npart'][0]))  #number of primaries.
    alphaPlot = _plt.figure('Alpha',figsize)
    
    _plt.plot(mad8opt['twiss'].getColumn('suml'), 
              mad8opt['twiss'].getColumn('alfx'),
              'b', label=r'MAD8 $\beta_{x}$')
    _plt.plot(mad8opt['twiss'].getColumn('suml'), 
              mad8opt['twiss'].getColumn('alfy'),
              'g', label=r'MAD8 $\beta_{y}$')
    
    # bds plot
    _plt.errorbar(bdsopt['S'], bdsopt['Alpha_x'],
                  yerr=bdsopt['Sigma_Alpha_x'],
                  label=r'BDSIM $\alpha_{x}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '',
                  color='b')
    
    _plt.errorbar(bdsopt['S'], bdsopt['Alpha_y'],
                  yerr=bdsopt['Sigma_Alpha_y'],
                  label=r'BDSIM $\alpha_{y}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '',
                  color='g')

    axes = _plt.gcf().gca()
    axes.set_ylabel(r'$\alpha_{x,y}$')
    axes.set_xlabel('S / m')
    axes.legend(loc='best')

    _CallUserFigureFunctions(functions)
    _AddSurvey(alphaPlot, mad8opt)
    _CallUserFigureFunctions(postfunctions)

    _plt.show(block=False)
    return alphaPlot

def PlotDs(mad8opt, bdsopt, survey=None, functions=None, postfunctions=None, figsize=(12,5)) :
    N = str(int(bdsopt['Npart'][0]))  #number of primaries.
    dispPlot = _plt.figure('Dispersion',figsize)

    _plt.plot(mad8opt['twiss'].getColumn('suml'), 
              mad8opt['twiss'].getColumn('dx'),
              'b', label=r'MAD8 $\beta_{x}$')
    _plt.plot(mad8opt['twiss'].getColumn('suml'), 
              mad8opt['twiss'].getColumn('dy'),
              'g', label=r'MAD8 $D_{y}$')
     
    # bds plot
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
    axes.set_xlabel('S / m')
    axes.legend(loc='best')

    _CallUserFigureFunctions(functions)
    _AddSurvey(dispPlot, mad8opt)
    _CallUserFigureFunctions(postfunctions)

    _plt.show(block=False)
    return dispPlot

def PlotDps(mad8opt, bdsopt, survey=None, functions=None, postfunctions=None, figsize=(12,5)) :
    N = str(int(bdsopt['Npart'][0]))  #number of primaries.
    dispPPlot = _plt.figure('Momentum_Dispersion',figsize)
    
    _plt.plot(mad8opt['twiss'].getColumn('suml'), 
              mad8opt['twiss'].getColumn('dpx'),
              'b', label=r'MAD8 $\beta_{x}$')
    _plt.plot(mad8opt['twiss'].getColumn('suml'), 
              mad8opt['twiss'].getColumn('dpy'),
              'g', label=r'MAD8 $D_{y}$')
    
    # bds plot
    _plt.errorbar(bdsopt['S'], bdsopt['Disp_xp'],
                  yerr=bdsopt['Sigma_Disp_xp'],
                  label=r'BDSIM $D_{p_x}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '',
                  color='b')
        
    _plt.errorbar(bdsopt['S'], bdsopt['Disp_yp'],
                  yerr=bdsopt['Sigma_Disp_yp'],
                  label=r'BDSIM $D_{p_y}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '',
                  color='g')

    axes = _plt.gcf().gca()
    axes.set_ylabel(r'$D_{p_{x},p_{y}}$ / rad')
    axes.set_xlabel('S / m')
    axes.legend(loc='best')

    _CallUserFigureFunctions(functions)
    _AddSurvey(dispPPlot, mad8opt)
    _CallUserFigureFunctions(postfunctions)

    _plt.show(block=False)
    return dispPPlot

def PlotSigmas(mad8opt, bdsopt, survey=None, functions=None, postfunctions=None, figsize=(12,5)) :
    N = str(int(bdsopt['Npart'][0]))  #number of primaries.
    sigmaPlot = _plt.figure('Sigma',figsize)

    _plt.plot(mad8opt['envel'].getColumn('suml'),
              _np.sqrt(mad8opt['envel'].getColumn('s11')),
              'b', label=r'MAD8 $\sigma_{x}$')
    _plt.plot(mad8opt['envel'].getColumn('suml'),
              _np.sqrt(mad8opt['envel'].getColumn('s33')),
              'g', label=r'MAD8 $\sigma_{y}$')
    
    # Own calculation of beam sizes
    emitX0 = 1e-8
    emitY0 = 1e-8

    e      = mad8opt['comm'].getColumn('E')
    rgamma = e/(0.5109989461/1e3)
    rbeta  = _np.sqrt(1-1.0/rgamma**2)

    emitXN0 = emitX0*rgamma[0]*rbeta[0]
    emitYN0 = emitY0*rgamma[0]*rbeta[0]

    sigmaX = _np.sqrt(emitXN0*mad8opt['twiss'].getColumn('betx')/(rbeta*rgamma))
    sigmaY = _np.sqrt(emitYN0*mad8opt['twiss'].getColumn('bety')/(rbeta*rgamma))

    _plt.plot(mad8opt['envel'].getColumn('suml'),sigmaX,'b--')
    _plt.plot(mad8opt['envel'].getColumn('suml'),sigmaY,'g--')

    # bds plot
    _plt.errorbar(bdsopt['S'], bdsopt['Sigma_x'],
                  yerr=bdsopt['Sigma_Sigma_x'],
                  label=r'BDSIM $\sigma_{x}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '',
                  color='b')
    
    _plt.errorbar(bdsopt['S'], bdsopt['Sigma_y'],
                  yerr=bdsopt['Sigma_Sigma_y'],
                  label=r'BDSIM $\sigma_{y}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '',
                  color='g')

    axes = _plt.gcf().gca()
    axes.set_ylabel(r'$\sigma_{x,y}$ / m')
    axes.set_xlabel('S / m')
    axes.legend(loc='best')

    _CallUserFigureFunctions(functions)
    _AddSurvey(sigmaPlot, mad8opt)
    _CallUserFigureFunctions(postfunctions)

    _plt.show(block=False)
    return sigmaPlot

def PlotSigmasP(mad8opt, bdsopt, survey=None, functions=None, postfunctions=None, figsize=(12,5)) :
    N = str(int(bdsopt['Npart'][0]))  #number of primaries.
    sigmaPPlot = _plt.figure('SigmaP',figsize)

    _plt.plot(mad8opt['envel'].getColumn('suml'), 
              _np.sqrt(mad8opt['envel'].getColumn('s22')),
              'b', label=r'MAD8 $\sigma_{xp}$')
    _plt.plot(mad8opt['envel'].getColumn('suml'), 
              _np.sqrt(mad8opt['envel'].getColumn('s44')),
              'g', label=r'MAD8 $\sigma_{yp}$')
    
    # bds plot
    _plt.errorbar(bdsopt['S'], bdsopt['Sigma_xp'],
                  yerr=bdsopt['Sigma_Disp_xp'],
                  label=r'BDSIM $\sigma_{p_x}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '',
                  color='b')
        
    _plt.errorbar(bdsopt['S'], bdsopt['Sigma_yp'],
                  yerr=bdsopt['Sigma_Sigma_yp'],
                  label=r'BDSIM $\sigma_{p_y}$' + ' ; N = ' + N,
                  marker='x',
                  ls = '',
                  color='g')

    axes = _plt.gcf().gca()
    axes.set_ylabel(r'$\sigma_{xp,yp}$ / rad')
    axes.set_xlabel('S / m')
    axes.legend(loc='best')

    _CallUserFigureFunctions(functions)
    _AddSurvey(sigmaPPlot, mad8opt)
    _CallUserFigureFunctions(postfunctions)

    _plt.show(block=False)
    return sigmaPPlot

def PlotEnergy(mad8opt, bdsopt, survey=None, functions=None, postfunctions=None, figsize=(12,5)) :
    N = str(int(bdsopt['Npart'][0]))  #number of primaries.
    energyPlot = _plt.figure('Energy',figsize)

    _plt.plot(mad8opt['twiss'].getColumn('suml'), # one missing energy due to initial 
              mad8opt['comm'].getColumn('E'),
              'b', label=r'MAD8 $E$')

    _plt.errorbar(bdsopt['S'], bdsopt['Mean_E'],
                  yerr=bdsopt['Sigma_Mean_E'],
                  label=r'BDSIM $E$' + ' ; N = ' + N,
                  marker='x',
                  ls = '',
                  color='b')
    
    axes = _plt.gcf().gca()
    axes.set_ylabel('Energy / GeV')
    axes.set_xlabel('S / m')
    axes.legend(loc='best')

    _CallUserFigureFunctions(functions)
    _AddSurvey(energyPlot, mad8opt)
    _CallUserFigureFunctions(postfunctions)
    
    _plt.show(block=False)
    return energyPlot

def PlotMeans(mad8opt, bdsopt, survey=None, functions=None, postfunctions=None, figsize=(12, 5)):
    N = str(int(bdsopt['Npart'][0]))  # number of primaries.
    meanPlot = _plt.figure('Mean', figsize)

    _plt.plot(mad8opt['twiss'].getColumn('suml'),  # one missing energy due to initial
              mad8opt['twiss'].getColumn('x'),
              'b', label=r'MAD8 $\overline{x}$')

    _plt.plot(mad8opt['twiss'].getColumn('suml'),  # one missing energy due to initial
              mad8opt['twiss'].getColumn('y'),
              'g', label=r'MAD8 $\overline{y}$')
    
    _plt.errorbar(bdsopt['S'], bdsopt['Mean_x'],
                  yerr=bdsopt['Sigma_Mean_x'],
                  label=r'BDSIM $\overline{x}$' + ' ; N = ' + N,
                  marker='x',
                  ls='',
                  color='b')
    _plt.errorbar(bdsopt['S'], bdsopt['Mean_y'],
                  yerr=bdsopt['Sigma_Mean_y'],
                  label=r'BDSIM $\overline{y}$' + ' ; N = ' + N,
                  marker='x',
                  ls='',
                  color='g')

    axes = _plt.gcf().gca()
    axes.set_ylabel(r'$\bar{x}, \bar{y}$ / m')
    axes.set_xlabel('S / m')
    axes.legend(loc='best')

    _CallUserFigureFunctions(functions)
    _AddSurvey(meanPlot, mad8opt)
    _CallUserFigureFunctions(postfunctions)

    _plt.show(block=False)
    return meanPlot

def PlotEmittance(mad8opt, bdsopt, survey=None, functions=None, postfunctions=None, figsize=(12, 5)) :
    N = str(int(bdsopt['Npart'][0]))  # number of primaries.
    emittancePlot = _plt.figure('Emittance', figsize)

    # Own calculation of beam sizes
    emitX0 = 1e-8
    emitY0 = 1e-8

    e      = mad8opt['comm'].getColumn('E')
    rgamma = e/(0.5109989461/1e3)
    rbeta  = _np.sqrt(1-1.0/rgamma**2)

    emitXN0 = emitX0*rgamma[0]*rbeta[0]
    emitYN0 = emitY0*rgamma[0]*rbeta[0]

    emitX = emitXN0/(rbeta*rgamma)
    emitY = emitYN0/(rbeta*rgamma)

    _plt.plot(mad8opt['twiss'].getColumn('suml'),  # one missing energy due to initial
              emitX,
              'b', label=r'MAD8 $\epsilon_x$')

    _plt.plot(mad8opt['twiss'].getColumn('suml'),  # one missing energy due to initial
              emitY,
              'g', label=r'MAD8 $\epsilon_y$')

    _plt.plot(bdsopt['S'], bdsopt['Emitt_x'],
              label=r'BDSIM $N$' + ' ; N = '+N,
              marker='x',
              ls='',
              color='b')

    _plt.plot(bdsopt['S'], bdsopt['Emitt_y'],
              label=r'BDSIM $N$' + ' ; N = '+N,
              marker='x',
              ls='',
              color='g')

    axes = _plt.gcf().gca()
    axes.set_ylabel(r'$\epsilon_{x,y}$ / m')

    _CallUserFigureFunctions(functions)
    _AddSurvey(emittancePlot, mad8opt)
    _CallUserFigureFunctions(postfunctions)

    _plt.show(block=False)
    return emittancePlot

def PlotNParticles(mad8opt, bdsopt, survey=None, functions=None, postfunctions=None, figsize=(12, 5)):
    npartPlot = _plt.figure('NParticles', figsize)

    _plt.plot(bdsopt['S'],bdsopt['Npart'], 'k-', label='BDSIM N Particles')
    _plt.plot(bdsopt['S'],bdsopt['Npart'], 'k.')
    axes = _plt.gcf().gca()
    axes.set_ylabel(r'N Particles')
    axes.set_xlabel('S / m')
    axes.legend(loc='best')

    _CallUserFigureFunctions(functions)
    _AddSurvey(npartPlot, mad8opt)
    _CallUserFigureFunctions(postfunctions)

    _plt.show(block=False)
    return npartPlot
    
def _AddSurvey(figure, survey):
    if survey is None:
        return 
    else:
        _pymad8.Plot.AddMachineLatticeToFigure(figure,survey)

def _CallUserFigureFunctions(functions):
    if isinstance(functions, list):
        for function in functions:
            if callable(function):
                function()
    elif callable(functions):
        functions()


# ============================================================================
# Below is old
# ============================================================================
class Mad8Bdsim :
    def __init__(self, 
                 bdsimFileName = "output.pickle",
                 mad8TwissFileName   = "ebds1.twiss",
                 mad8EnvelopeFileName = "ebds1.envelope") : 
        # load bdsim data
        if bdsimFileName.find("pickle") != -1 :
            f = open(bdsimFileName) 
            self.bdsimData = _pkl.load(f)
            self.bdsimOptics = self.bdsimData['optics']
            f.close()
        elif bdsimFileName.find(".root") != -1 :
            import ROOT as _ROOT 
            import root_numpy as _root_numpy
            f = _ROOT.TFile(bdsimFileName)
            t = f.Get("optics")
            self.bdsimOptics = _root_numpy.tree2rec(t)
            


        # load mad8 data
        r = _pymad8.Mad8.OutputReader()    
        [self.mad8Comm,self.mad8Envel] = r.readFile(mad8EnvelopeFileName,"envel")
        [self.mad8Comm,self.mad8Twiss] = r.readFile(mad8TwissFileName,"twiss")

    def plotSigma(self) : 
        figure = _plt.figure(figsize=(11.6, 7.2))
        gs  = _plt.GridSpec(3,1,height_ratios=[1,3,3])
        ax0 = figure.add_subplot(gs[0],projection="_My_Axes")
        _pymad8.Plot.drawMachineLattice(self.mad8Comm,self.mad8Twiss)

        ax1 = _plt.subplot(gs[1])
        _pl.plot(self.mad8Envel.getColumn('suml'),_pl.sqrt(self.mad8Envel.getColumn('s11'))*1e6,"+-",label="MAD8")
        _pl.plot(self.bdsimOptics['S'],self.bdsimOptics['Sigma_x']/1e-6,"x--",label="BDSIM")
        #_pl.xlim(0,2275)
        #_pl.ylim(0,3000)
        _pl.legend(loc=0)
        _pl.ylabel("$\\sigma_x$ [$\mu$m]")

        ax2 = _plt.subplot(gs[2])
        _pl.plot(self.mad8Envel.getColumn('suml'),_pl.sqrt(self.mad8Envel.getColumn('s33'))*1e6,"+-")
        _pl.plot(self.bdsimOptics['S'],self.bdsimOptics['Sigma_y']/1e-6,"x--")
        #_pl.xlim(0,2275)
        #_pl.ylim(0,100)
        _pl.ylabel("$\\sigma_y$ [$\mu$m]")
        _pl.xlabel("$S$ [m]")

        _pymad8.Plot.setCallbacks(figure,ax0,[ax1,ax2],self.mad8Twiss)

        _pl.savefig("mad8bdsim_sigma.pdf")

        
    def plotSigmaPrim(self) : 
        figure = _plt.figure(figsize=(11.6, 7.2))
        gs  = _plt.GridSpec(3,1,height_ratios=[1,3,3])
        ax0 = figure.add_subplot(gs[0],projection="_My_Axes")
        _pymad8.Plot.drawMachineLattice(self.mad8Comm,self.mad8Twiss)

        ax1 = _plt.subplot(gs[1])
        _pl.plot(self.mad8Envel.getColumn('suml'),_pl.sqrt(self.mad8Envel.getColumn('s22'))*1e6,"+-",label="MAD8")
        _pl.plot(self.bdsimOptics['S'],self.bdsimOptics['Sigma_xp']/1e-6,"x--",label="BDSIM")
        #_pl.xlim(0,2275)
        #_pl.ylim(0,3000)
        _pl.legend(loc=0)
        _pl.ylabel("$\\sigma^{'}_{x}$ [$\mu$m]")

        ax2 = _plt.subplot(gs[2])
        _pl.plot(self.mad8Envel.getColumn('suml'),_pl.sqrt(self.mad8Envel.getColumn('s44'))*1e6,"+-")
        _pl.plot(self.bdsimOptics['S'],self.bdsimOptics['Sigma_yp']/1e-6,"x--")
        #_pl.xlim(0,2275)
        #_pl.ylim(0,100)
        _pl.ylabel("$\\sigma^{'}_{y}$ [$\mu$m]")
        _pl.xlabel("$S$ [m]")

        _pymad8.Plot.setCallbacks(figure,ax0,[ax1,ax2],self.mad8Twiss)

        _pl.savefig("mad8bdsim_sigma_prim.pdf")

    def plotOrbit(self) :
        figure = _plt.figure(figsize=(11.6, 7.2))
        gs  = _plt.GridSpec(3,1,height_ratios=[1,3,3])
        ax0 = figure.add_subplot(gs[0],projection="_My_Axes")
        _pymad8.Plot.drawMachineLattice(self.mad8Comm,self.mad8Twiss)

        ax1 = _plt.subplot(gs[1])
        _pl.plot(self.mad8Envel.getColumn('suml'), _np.zeros(len(self.mad8Envel.getColumn('suml'))),"+-",label="MAD8") #mad8 orbit perfectly on reference
        _pl.plot(self.bdsimOptics['S'],self.bdsimOptics['Mean_x']/1e-6,"x--",label="BDSIM")
        #_pl.xlim(0,2275)
        #_pl.ylim(0,3000)
        _pl.legend(loc=0)
        _pl.ylabel("$\\overline{x}$ [$\mu$m]")

        ax2 = _plt.subplot(gs[2])
        _pl.plot(self.mad8Envel.getColumn('suml'), _np.zeros(len(self.mad8Envel.getColumn('suml'))) ,"+-")
        _pl.plot(self.bdsimOptics['S'],self.bdsimOptics['Mean_y']/1e-6,"x--")
        _pl.xlim(0,2275)
        #_pl.ylim(0,100)
        _pl.ylabel("$\\overline{y}$ [$\mu$m]")
        _pl.xlabel("$S$ [m]")

        _pymad8.Plot.setCallbacks(figure,ax0,[ax1,ax2],self.mad8Twiss)
        
        _pl.savefig("mad8bdsim_mean.pdf")

    
    def plotBeta(self) : 
        figure = _plt.figure(figsize=(11.6, 7.2))
        gs  = _plt.GridSpec(3,1,height_ratios=[1,3,3])
        ax0 = figure.add_subplot(gs[0],projection="_My_Axes")
        _pymad8.Plot.drawMachineLattice(self.mad8Comm,self.mad8Twiss)
        
        ax1 = _pl.subplot(gs[1])
        ax1.set_autoscale_on(True)
        _pl.plot(self.mad8Envel.getColumn('suml'),_pl.sqrt(self.mad8Twiss.getColumn('betx')),"+-")
        _pl.plot(self.bdsimOptics['S'],_pl.sqrt(self.bdsimOptics['Beta_x']),"+--")
        _pl.ylabel("$\sqrt\\beta_x$ [m]")

        ax2 = _pl.subplot(gs[2])
        ax2.set_autoscale_on(True)
        _pl.plot(self.mad8Envel.getColumn('suml'),_pl.sqrt(self.mad8Twiss.getColumn('bety')),"+-")
        _pl.plot(self.bdsimOptics['S'],_pl.sqrt(self.bdsimOptics['Beta_y']),"+--")
        _pl.ylabel("$\sqrt\\beta_y$ [m]")
        _pl.xlabel("$S$ [m]")

        _pymad8.Plot.setCallbacks(figure,ax0,[ax1,ax2],self.mad8Twiss)
        
        _pl.savefig("mad8bdsim_beta.pdf")
    

    def plotSurvey(self, mad8SurveyFileName, bdsimSurveyFileName) :
        # load bdsim survey
        fs = _pybdsim.Data.Load(bdsimSurveyFileName)

        # load mad8 survey
        rs = _pymad8.Mad8.OutputReader()    
        [common, mad8Survey] = rs.readFile(mad8SurveyFileName,"survey")
        
        figure = _plt.figure(figsize=(11.6, 7.2))
        gs  = _plt.GridSpec(3,1,height_ratios=[1,3,3])
        ax0 = figure.add_subplot(gs[0],projection="_My_Axes")
        _pymad8.Plot.drawMachineLattice(self.mad8Comm,self.mad8Twiss)

        ax1 = _pl.subplot(gs[1])
        _pl.plot(mad8Survey.getColumn('suml'), mad8Survey.getColumn('x'),"+-", label = "MAD8")
        _pl.plot(fs.SStart(),fs.X(),"+--", label = "BDSIM")
        #_pl.xlim(0,max(mad8Survey.getColumn('suml')))
        _pl.ylabel("$X$ [m]")

        ax2 = _pl.subplot(gs[2])
        _pl.plot(mad8Survey.getColumn('suml'),mad8Survey.getColumn('y'),"+-", label = "MAD8")
        _pl.plot(fs.SStart(),fs.Y(),"+--", label = "BDSIM")
        #_pl.xlim(0,max(mad8Survey.getColumn('suml')))
        _pl.ylabel("$Y$ [m]")
        _pl.xlabel("$S$ [m]")

        _pl.legend(loc=0)
        _pl.subplots_adjust(hspace=0.25,top=0.94,left=0.1,right=0.92)

        _pymad8.Plot.setCallbacks(figure,ax0,[ax1,ax2],self.mad8Twiss)
        
        _pl.savefig("mad8bdsim_survey.pdf")


    def plotDispersion(self) :
        figure = _plt.figure(figsize=(11.6, 7.2))
        gs  = _plt.GridSpec(3,1,height_ratios=[1,3,3])
        ax0 = figure.add_subplot(gs[0],projection="_My_Axes")
        _pymad8.Plot.drawMachineLattice(self.mad8Comm,self.mad8Twiss)

        ax1 = _pl.subplot(gs[1])
        ax1.set_autoscale_on(True)
        _pl.plot(self.mad8Envel.getColumn('suml'),self.mad8Twiss.getColumn('dx'),"+-",label="MAD8")
        _pl.plot(self.bdsimOptics['S'],self.bdsimOptics['Disp_x'],"+--",label="BDSIM") # 4000 1/250*1e6
        _pl.ylabel("$\\eta_x$ [m]")

        ax2 = _pl.subplot(gs[2])
        ax2.set_autoscale_on(True)
        _pl.plot(self.mad8Envel.getColumn('suml'),self.mad8Twiss.getColumn('dy'),"+-",label="MAD8")
        _pl.plot(self.bdsimOptics['S'],self.bdsimOptics['Disp_y'],"+--",label="BDSIM") # 4000 1/250*1e6
        _pl.ylabel("$\\eta_y$ [m]")
        _pl.xlabel("$S$ [m]")
        
        _pl.legend(loc=0)
        
        _pymad8.Plot.setCallbacks(figure,ax0,[ax1,ax2],self.mad8Twiss)

        _pl.savefig("mad8bdsim_eta.pdf")
        

    def plotDispersionPrim(self) :
        figure = _plt.figure(figsize=(11.6, 7.2))
        gs  = _plt.GridSpec(3,1,height_ratios=[1,3,3])
        ax0 = figure.add_subplot(gs[0],projection="_My_Axes")
        _pymad8.Plot.drawMachineLattice(self.mad8Comm,self.mad8Twiss)

        ax1 = _pl.subplot(gs[1])
        ax1.set_autoscale_on(True)
        _pl.plot(self.mad8Envel.getColumn('suml'),self.mad8Twiss.getColumn('dpx'),"+-",label="MAD8")
        _pl.plot(self.bdsimOptics['S'],self.bdsimOptics['Disp_xp'],"+--",label="BDSIM") # 4000 1/250*1e6
        _pl.ylabel("$\\eta^{'}_{x}$ [rad]")

        ax2 = _pl.subplot(gs[2])
        ax2.set_autoscale_on(True)
        _pl.plot(self.mad8Envel.getColumn('suml'),self.mad8Twiss.getColumn('dpy'),"+-",label="MAD8")
        _pl.plot(self.bdsimOptics['S'],self.bdsimOptics['Disp_yp'],"+--",label="BDSIM") # 4000 1/250*1e6
        _pl.ylabel("$\\eta^{'}_{y}$ [rad]")
        _pl.xlabel("$S$ [m]")
        
        _pl.legend(loc=0)
        
        _pymad8.Plot.setCallbacks(figure,ax0,[ax1,ax2],self.mad8Twiss)

        _pl.savefig("mad8bdsim_etaprim.pdf")

        
    def plotEmittance(self) :
        figure = _plt.figure(figsize=(11.6, 7.2))
        gs  = _plt.GridSpec(3,1,height_ratios=[1,3,3])
        ax0 = figure.add_subplot(gs[0],projection="_My_Axes")
        _pymad8.Plot.drawMachineLattice(self.mad8Comm,self.mad8Twiss)

        ax1 = _pl.subplot(gs[1])
        ax1.set_autoscale_on(True)
        #_pl.plot(self.mad8Envel.getColumn('suml'), _np.zeros(len(self.mad8Envel.getColumn('suml'))),"+-",label="MAD8")
        _pl.plot(self.bdsimOptics['S'],self.bdsimOptics['Emitt_x'],"+--",label="BDSIM") # 4000 1/250*1e6
        _pl.ylabel("$\\epsilon_{x}$ [m]")

        ax2 = _pl.subplot(gs[2])
        ax2.set_autoscale_on(True)
        #_pl.plot(self.mad8Envel.getColumn('suml'), _np.zeros(len(self.mad8Envel.getColumn('suml'))),"+-",label="MAD8")
        _pl.plot(self.bdsimOptics['S'],self.bdsimOptics['Emitt_y'],"+--",label="BDSIM") # 4000 1/250*1e6
        _pl.ylabel("$\\epsilon_{y}$ [m]")
        _pl.xlabel("$S$ [m]")
        
        _pl.legend(loc=0)
        
        _pymad8.Plot.setCallbacks(figure,ax0,[ax1,ax2],self.mad8Twiss)

        _pl.savefig("mad8bdsim_emitt.pdf")
