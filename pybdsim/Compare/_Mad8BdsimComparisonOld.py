import pickle as _pkl
import pylab  as _pl
import pymad8 as _pymad8
import pybdsim as _pybdsim
import matplotlib.pyplot as _plt
import numpy as _np
from os.path import isfile as _isfile
from matplotlib.backends.backend_pdf import PdfPages as _PdfPages
import datetime as _datetime


# Predefined dicts for making the standard plots,
# format = (mad8_optical_var_name, bdsim_optical_var_name, bdsim_optical_var_error_name, legend_name)

_BETA =    {"bdsimdata"  : ("Beta_x", "Beta_y"),
            "bdsimerror" : ("Sigma_Beta_x","Sigma_Beta_y"),
            "mad8"       : ("betx", "bety"),
            "legend"     : (r'$\beta_{x}$', r'$\beta_{y}$'),
            "xlabel"     : "S / m",
            "ylabel"     : r"$\beta_{x,y}$ / m",
            "title"      : "Beta"
            }

_ALPHA =   {"bdsimdata"  : ("Alpha_x", "Alpha_y"),
            "bdsimerror" : ("Sigma_Alpha_x","Sigma_Alpha_y"),
            "mad8"       : ("alfx", "alfy"),
            "legend"     : (r'$\alpha_{x}$', r'$\alpha_{y}$'),
            "xlabel"     : "S / m",
            "ylabel"     : r"$\alpha_{x,y}$ / m",
            "title"      : "Alpha"
           }

_DISP  =   {"bdsimdata"  : ("Disp_x", "Disp_y"),
            "bdsimerror" : ("Sigma_Disp_x","Sigma_Disp_y"),
            "mad8"       : ("dx", "dy"),
            "legend"     : (r"$\eta_{x}$", r"$\eta_{y}$"),
            "xlabel"     : "S / m",
            "ylabel"     : r"$\eta_{x,y} / m$",
            "title"      : "Dispersion"
            }

_DISP_P=   {"bdsimdata"  : ("Disp_xp", "Disp_yp"),
            "bdsimerror" : ("Sigma_Disp_xp","Sigma_Disp_yp"),
            "mad8"       : ("dpx", "dpy"),
            "legend"     : (r"$\eta_{p_x}$", r"$\eta_{p_x}$"),
            "xlabel"     : "S / m",
            "ylabel"     : r"$\eta_{p_{x},p_{y}}$ / m",
            "title"      : "Momentum_Dispersion"
            }

_SIGMA =   {"bdsimdata"  : ("Sigma_x", "Sigma_y"),
            "bdsimerror" : ("Sigma_Sigma_x","Sigma_Sigma_y"),
            "mad8"       : ("", ""),
            "legend"     : (r"$\sigma_{x}$",r"$\sigma_{y}$"),
            "xlabel"     : "S / m",
            "ylabel"     : r"$\sigma_{x,y}$ / m",
            "title"      : "Sigma"
            }

_SIGMA_P = {"bdsimdata"  : ("Sigma_xp", "Sigma_yp"),
            "bdsimerror" : ("Sigma_Sigma_xp","Sigma_Sigma_yp"),
            "mad8"       : ("", ""),
            "legend"     : (r"$\sigma_{xp}$",r"$\sigma_{yp}$"),
            "xlabel"     : "S / m",
            "ylabel"     : r"$\sigma_{xp,yp}$ / rad",
            "title"      : "SigmaP"
            }

_MEAN    = {"bdsimdata"  : ("Mean_x", "Mean_y"),
            "bdsimerror" : ("Sigma_Mean_x","Sigma_Mean_y"),
            "mad8"       : ("x", "y"),
            "legend"     : (r"$\overline{x}$", r"$\overline{y}$"),
            "xlabel"     : "S / m",
            "ylabel"     : r"$\bar{x,y}$ / m",
            "title"      : "Mean"
            }

_EMITT   = {"bdsimdata"  : ("Emitt_x", "Emitt_y"),
            "bdsimerror" : ("Sigma_Emitt_x","Sigma_Emitt_y"),
            "mad8"       : ("", ""),
            "legend"     : (r"$\epsilon_x$", r"$\epsilon_y$"),
            "xlabel"     : "S / m",
            "ylabel"     : r"$\epsilon_{x,y}$ / m",
            "title"      : "Emittance"
            }

# use closure to avoid tonnes of boilerplate code as happened with
# MadxBdsimComparison.py
def _make_plotter(plot_info_dict):
    def f_out(mad8opt, bdsopt, functions=None, postfunctions=None, survey=None, figsize=(9,5), xlim=(0,0), **kwargs):

        # Get the initial N for the bdsim
        N = str(int(bdsopt['Npart'][0]))  # number of primaries.

        # labels for plot legends
        mad8legendx = r'MAD8 ' + plot_info_dict['legend'][0]
        mad8legendy = r'MAD8 ' + plot_info_dict['legend'][1]
        bdslegendx  = r'BDSIM ' + plot_info_dict['legend'][0] + ' ; N = ' + N
        bdslegendy  = r'BDSIM ' + plot_info_dict['legend'][1] + ' ; N = ' + N

        # mad8 data from correct source
        if plot_info_dict["title"] == "Sigma":
            sigmaX,sigmaY,sigmaXP,sigmaYP = _CalculateSigmas(mad8opt)
            mad8Xdata = sigmaX
            mad8Ydata = sigmaY

            mad8Xdata = _np.sqrt(mad8opt['envel'].getColumn('s11'))
            mad8Ydata = _np.sqrt(mad8opt['envel'].getColumn('s33'))

            mad8s     = mad8opt['envel'].getColumn('suml')
            mad8legendx += '(calculated)'
            mad8legendy += '(calculated)'
        elif plot_info_dict["title"] == "SigmaP":
            sigmaX,sigmaY,sigmaXP,sigmaYP = _CalculateSigmas(mad8opt)
            mad8Xdata = sigmaXP
            mad8Ydata = sigmaYP

            mad8Xdata = _np.sqrt(mad8opt['envel'].getColumn('s22'))
            mad8Ydata = _np.sqrt(mad8opt['envel'].getColumn('s44'))

            mad8s     = mad8opt['envel'].getColumn('suml')
            mad8legendx += '(calculated)'
            mad8legendy += '(calculated)'

        elif plot_info_dict["title"] == "Emittance":
            emitX, emitY = _CalculateEmittance(mad8opt)
            mad8Xdata = emitX
            mad8Ydata = emitY
            mad8s     = mad8opt['twiss'].getColumn('suml')
        else:
            mad8Xdata = mad8opt['twiss'].getColumn(plot_info_dict['mad8'][0])
            mad8Ydata = mad8opt['twiss'].getColumn(plot_info_dict['mad8'][1])
            mad8s     = mad8opt['twiss'].getColumn('suml')

        # the figure
        plot = _plt.figure(plot_info_dict["title"], figsize=figsize, **kwargs)

        # mad8 plot
        _plt.plot(mad8s, mad8Xdata, 'b--', label=mad8legendx)
        _plt.plot(mad8s, mad8Ydata, 'g--', label=mad8legendy)

        # bds plot
        _plt.errorbar(bdsopt['S'],
                      bdsopt[plot_info_dict['bdsimdata'][0]],
                      yerr=bdsopt[plot_info_dict['bdsimerror'][0]],
                      label=bdslegendx,
                      capsize=3, ls='', marker='x', color='b', **kwargs)

        _plt.errorbar(bdsopt['S'],
                      bdsopt[plot_info_dict['bdsimdata'][1]],
                      yerr=bdsopt[plot_info_dict['bdsimerror'][1]],
                      label=bdslegendy,
                      capsize=3, ls='', marker='x', color='g', **kwargs)

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
        if xlim != (0, 0):
            _plt.xlim(xlim)

        plot.sca(plot.axes[0])
        _plt.show(block=False)

        #if survey is not None:
        #    _pymad8.Plot.AddMachineLatticeToFigure(plot, survey)

        _plt.show(block=False)
        return plot
    return f_out


PlotBeta   = _make_plotter(_BETA)
PlotAlpha  = _make_plotter(_ALPHA)
PlotDisp   = _make_plotter(_DISP)
PlotDispP  = _make_plotter(_DISP_P)
PlotSigma  = _make_plotter(_SIGMA)
PlotSigmaP = _make_plotter(_SIGMA_P)
PlotMean   = _make_plotter(_MEAN)
PlotEmitt  = _make_plotter(_EMITT)


def _CalculateSigmas(mad8opt):
    rgamma, rbeta, emitXN0, emitYN0 = _CalculateNEmittance(mad8opt)

    E = mad8opt['comm'].getColumn('E')
    E0 = E[0]
    sigE = mad8opt['beam']['esprd']

    sige = sigE*E0/E # absolute energy spread is constant, fractional decreases (TODO need the energy spread from MAD8)

    sigmaX = _np.sqrt(emitXN0*mad8opt['twiss'].getColumn('betx')/(rbeta*rgamma)+mad8opt['twiss'].getColumn('dx')**2*sige**2)
    sigmaY = _np.sqrt(emitYN0*mad8opt['twiss'].getColumn('bety')/(rbeta*rgamma)+mad8opt['twiss'].getColumn('dy')**2*sige**2)

    sigmaXP = _np.sqrt(emitXN0 / (rbeta * rgamma) * (mad8opt['twiss'].getColumn('alfx') ** (2) + 1) / mad8opt['twiss'].getColumn(
            'betx') + (mad8opt['twiss'].getColumn('dpx') ** (2)) * (sige ** (2)))
    sigmaYP = _np.sqrt(emitYN0 / (rbeta * rgamma) * (mad8opt['twiss'].getColumn('alfy') ** (2) + 1) / mad8opt['twiss'].getColumn(
            'bety') + (mad8opt['twiss'].getColumn('dpy') ** (2)) * (sige ** (2)))
    return sigmaX, sigmaY, sigmaXP, sigmaYP

def _CalculateNEmittance(mad8opt):
    # Own calculation of beam sizes
    emitX0 = mad8opt['beam']['ex']
    emitY0 = mad8opt['beam']['ey']
    particle =  mad8opt['beam']['particle']
    if particle == 'electron' or particle == 'positron':
        mass = 0.5109989461
    elif particle == 'proton':
        mass = 938.2720813
    else:  # default is mad8 default particle mass.
        mass = 0.5109989461

    e = mad8opt['comm'].getColumn('E')
    rgamma = e / (mass / 1e3) 
    rbeta = _np.sqrt(1 - 1.0 / rgamma ** 2)

    emitXN0 = emitX0 * rgamma[0] * rbeta[0]
    emitYN0 = emitY0 * rgamma[0] * rbeta[0]
    return rgamma, rbeta, emitXN0, emitYN0

def _CalculateEmittance(mad8opt):
    rgamma, rbeta, emitXN0, emitYN0 = _CalculateNEmittance(mad8opt)
    emitX = emitXN0 / (rbeta * rgamma)
    emitY = emitYN0 / (rbeta * rgamma)
    return emitX, emitY

def _CheckFilesExist(twiss, envel, bdsim):
    '''
    Otherwise such errors are too cryptic.
    '''
    if not _isfile(twiss):
        raise IOError("File not found: ", twiss)
    if not _isfile(envel):
        raise IOError("File not found: ", envel);
    if isinstance(bdsim, str) and not _isfile(bdsim):
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


def Mad8VsBDSIM(twiss, envel, bdsim, survey=None, functions=None,
                postfunctions=None, figsize=(10, 5), xlim=(0,0),
                saveAll=True, outputFileName=None,
                particle="electron", energySpread=1e-4, ex=1e-8, ey=1e-8):
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

    # parameters required for calculating beam sizes, not written in mad8 output so have to supply manually.
    beamParams = {'esprd': energySpread, 'particle': particle, 'ex': ex, 'ey':ey}

    # make plots 
    mad8opt = {'comm':com, 'twiss':twissL, 'envel':envelL, 'beam': beamParams}

    # energy and npart plotted with individual methods
    figures = [PlotBeta(mad8opt,bdsopt,functions=functions,
                         postfunctions=postfunctions,
                         figsize=figsize, xlim=xlim, survey=survey),
               PlotAlpha(mad8opt,bdsopt,functions=functions,
                          postfunctions=postfunctions,
                          figsize=figsize, xlim=xlim, survey=survey),
               PlotDisp(mad8opt,bdsopt,functions=functions,
                      postfunctions=postfunctions,
                      figsize=figsize, xlim=xlim, survey=survey),
               PlotDispP(mad8opt,bdsopt,functions=functions,
                       postfunctions=postfunctions,
                       figsize=figsize, xlim=xlim, survey=survey),
               PlotSigma(mad8opt,bdsopt,functions=functions,
                          postfunctions=postfunctions,
                          figsize=figsize, xlim=xlim, survey=survey),
               PlotSigmaP(mad8opt,bdsopt,functions=functions,
                           postfunctions=postfunctions,
                           figsize=figsize, xlim=xlim, survey=survey),
               PlotEnergy(mad8opt,bdsopt,functions=functions,
                          postfunctions=postfunctions,
                          figsize=figsize, xlim=xlim, survey=survey),
               PlotMean(mad8opt,bdsopt,functions=functions,
                         postfunctions=postfunctions,
                         figsize=figsize, xlim=xlim, survey=survey),
               PlotEmitt(mad8opt,bdsopt,functions=functions,
                             postfunctions=postfunctions,
                             figsize=figsize, xlim=xlim, survey=survey),
               PlotNParticles(mad8opt,bdsopt,functions=functions,
                              postfunctions=postfunctions,
                              figsize=figsize, xlim=xlim, survey=survey)]
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

        print("Written ", output_filename)
    
    return mad8opt

def PlotEnergy(mad8opt, bdsopt, survey=None, functions=None, postfunctions=None, figsize=(12,5), xlim=(0,0)) :
    N = str(int(bdsopt['Npart'][0]))  #number of primaries.
    energyPlot = _plt.figure('Energy',figsize)

    _plt.plot(mad8opt['twiss'].getColumn('suml'), # one missing energy due to initial 
              mad8opt['comm'].getColumn('E'),
              'b--', label=r'MAD8 $E$')

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

    if survey is None:
        survey = mad8opt
    _CallUserFigureFunctions(functions)
    _AddSurvey(energyPlot, survey)
    _CallUserFigureFunctions(postfunctions)
    if xlim != (0,0):
        _plt.xlim(xlim)

    energyPlot.sca(energyPlot.axes[0])
    
    _plt.show(block=False)
    return energyPlot

def PlotNParticles(mad8opt, bdsopt, survey=None, functions=None, postfunctions=None, figsize=(12, 5), xlim=(0,0)):
    npartPlot = _plt.figure('NParticles', figsize)

    _plt.plot(bdsopt['S'],bdsopt['Npart'], 'k-', label='BDSIM N Particles')
    _plt.plot(bdsopt['S'],bdsopt['Npart'], 'k.')
    axes = _plt.gcf().gca()
    axes.set_ylabel(r'N Particles')
    axes.set_xlabel('S / m')
    axes.legend(loc='best')

    if survey is None:
        survey = mad8opt
    _CallUserFigureFunctions(functions)
    _AddSurvey(npartPlot, survey)
    _CallUserFigureFunctions(postfunctions)
    if xlim != (0,0):
        _plt.xlim(xlim)

    npartPlot.sca(npartPlot.axes[0])

    _plt.show(block=False)
    return npartPlot
    
def _AddSurvey(figure, survey):
    if survey is None:
        return 
    elif survey[-5:] == ".root":
        _pybdsim.Plot.AddMachineLatticeFromSurveyToFigure(figure,survey)
    else:
        _pymad8.Plot.AddMachineLatticeToFigure(figure,survey)

def _CallUserFigureFunctions(functions):
    if isinstance(functions, list):
        for function in functions:
            if callable(function):
                function()
    elif callable(functions):
        functions()

def ChangeYlim(plotname,limits):
    """
    Change ylimit on data subfigure after survey has been added to the plot.
    Limits must be supplied as a tuple (ymin,ymax).
    """
    f = _plt.figure(plotname)
    ax = f.axes[0]
    ax.set_ylim(limits)

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
