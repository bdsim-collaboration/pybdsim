import pymadx as _pymadx
import pybdsim as _pybdsim
import matplotlib.pyplot as _plt
import numpy as _np
from os.path import isfile as _isfile
from matplotlib.backends.backend_pdf import PdfPages as _PdfPages
import datetime as _datetime

def MadxVsBDSIM(tfs, bdsim, survey=None, functions=None,
                postfunctions=None, figsize=(10, 5), saveAll=True, outputFileName=None):
    """
    Compares MadX and BDSIM optics variables.
    User must provide a tfsoptIn file or Tfsinstance and a BDSAscii file or instance.

    +-----------------+---------------------------------------------------------+
    | **Parameters**  | **Description**                                         |
    +-----------------+---------------------------------------------------------+
    | tfs             | Tfs file or pymadx.Data.Tfs instance.                   |
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

    _CheckFilesExist(tfs, bdsim, survey)

    fname = _pybdsim._General.GetFileName(bdsim) # cache file name
    if fname == "":
        fname = "optics_report"

    tfsinst = _pymadx.Data.CheckItsTfs(tfs)
    bdsinst = _pybdsim._General.CheckItsBDSAsciiData(bdsim, True)

    tfsheader = tfsinst.header
    tfsopt  = _GetTfsOptics(tfsinst)
    bdsopt  = _GetBDSIMOptics(bdsinst)

    if survey is None:
        survey = tfsinst

    figures = [PlotBetas(tfsopt, bdsopt, survey=survey,
                         functions=functions,
                         postfunctions=postfunctions,
                         figsize=figsize),
               PlotAlphas(tfsopt, bdsopt, survey=survey,
                          functions=functions,
                          postfunctions=postfunctions,
                          figsize=figsize),
               PlotDs(tfsopt, bdsopt, survey=survey,
                      functions=functions,
                      postfunctions=postfunctions,
                      figsize=figsize),
               PlotDps(tfsopt, bdsopt, survey=survey,
                       functions=functions,
                       postfunctions=postfunctions,
                       figsize=figsize),
               PlotSigmas(tfsopt, bdsopt, survey=survey,
                          functions=functions,
                          postfunctions=postfunctions,
                          figsize=figsize),
               PlotSigmasP(tfsopt, bdsopt, survey=survey,
                           functions=functions,
                           postfunctions=postfunctions,
                           figsize=figsize),
               PlotMeans(tfsopt, bdsopt, survey=survey,
                         functions=functions,
                         postfunctions=postfunctions,
                         figsize=figsize),
               PlotEmitt(tfsopt, bdsopt, tfsinst.header, survey=survey,
                         functions=functions,
                         postfunctions=postfunctions,
                         figsize=figsize),
               PlotNParticles(bdsopt, survey=survey,
                              functions=functions,
                              postfunctions=postfunctions,
                              figsize=figsize)]

    if saveAll:
        tfsname = repr(tfsinst)
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

def PrepareResiduals(tfs, bds, survey=None, verbose=False):
    """
    Filter the tfs and bds to provide data that will match the 
    BDSIM data in element name. 
    """
    _CheckFilesExist(tfs, bds, survey)
    tfsinst   = _pymadx.Data.CheckItsTfs(tfs)
    bdsinst   = _pybdsim._General.CheckItsBDSAsciiData(bds) # works for root files too

    bdel    = bdsinst.orbit.elementName()
    bdslist = _np.array(bdel)
    tfsa  = tfsinst.GetColumn("NAME")

    keys = ['S', 'X', 'PX', 'Y', 'PY']

    tfsdata = {
        'S':tfsinst.GetColumn("S"),
        'X':tfsinst.GetColumn("X"),
        'PX':tfsinst.GetColumn("PX"),
        'Y':tfsinst.GetColumn("Y"),
        'PY':tfsinst.GetColumn("PY")
        }

    bdsdata = {
        'S':_np.array(bdsinst.orbit.s()),
        'X':_np.array(bdsinst.orbit.x()),
        'PX':_np.array(bdsinst.orbit.xp()),
        'Y':_np.array(bdsinst.orbit.y()),
        'PY':_np.array(bdsinst.orbit.yp())
        }

    reducedName = [_pybdsim._General.PrepareReducedName(name) for name in tfsa]
    rn = _np.array(reducedName)

    for n in keys:
        tfsdata[n] = tfsdata[n][_np.isin(rn,bdslist)]
        bdsdata[n] = bdsdata[n][_np.isin(bdslist,rn)]
        tfsdata[n] = _np.array(tfsdata[n])
        bdsdata[n] = _np.array(bdsdata[n])   

    return tfsdata,bdsdata 
 

def MadxVsBDSIMFromGMAD(tfs, gmad, outputfilename):
    """
    Runs the BDSIM model provided by the gmad file given, gets the
    optics, and then compares them with TFS.

    tfs - path to TFS file or a pymadx.Data.Tfs instance
    gmad - path to gmad file to be run.
    outputfilename - path of the output optics report file.

    """

    bdsimOptics = _pybdsim.Run.GetOpticsFromGMAD(gmad)
    # Use TFS for survey but perhaps one day can directly get the
    # model from the ROOT output (having modified the above
    # function..  Currently there's no interface for this.
    MadxVsBDSIM(tfs, bdsimOptics, survey=tfs, outputFileName=outputfilename)


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
                                     'DXBETA',
                                     'DPXBETA',
                                     'DYBETA',
                                     'DPYBETA',
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

def PlotBetas(tfsopt, bdsopt, survey=None, functions=None, postfunctions=None, figsize=(12,5)):
    N = str(int(bdsopt['Npart'][0]))  #number of primaries.
    betaPlot = _plt.figure('Beta', figsize=figsize)
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
    axes.set_xlabel('S / m')
    axes.legend(loc='best')

    print("survey =", survey)

    _CallUserFigureFunctions(functions)
    _AddSurvey(betaPlot, survey)
    _CallUserFigureFunctions(postfunctions)
    
    _plt.show(block=False)
    return betaPlot

def PlotAlphas(tfsopt, bdsopt, survey=None, functions=None, postfunctions=None, figsize=(12,5)):
    N = str(int(bdsopt['Npart'][0]))  #number of primaries.
    alphaPlot = _plt.figure('Alpha', figsize=figsize)
    #tfs
    _plt.plot(tfsopt['S'], tfsopt['ALFX'], 'b', label=r'MADX $\alpha_{x}$')
    _plt.plot(tfsopt['S'], tfsopt['ALFY'], 'g', label=r'MADX $\alpha_{y}$')
    #bds
    _plt.errorbar(bdsopt['S'], bdsopt['Alpha_x'],
                  yerr=bdsopt['Sigma_Alpha_x'],
                  label=r'BDSIM $\alpha_{x}$' + ' ; N = ' + N,
                  fmt='b.', capsize=3)

    _plt.errorbar(bdsopt['S'], bdsopt['Alpha_y'],
                  yerr=bdsopt['Sigma_Alpha_y'],
                  label=r'BDSIM $\alpha_{y}$' + ' ; N = ' + N,
                  fmt='g.', capsize=3)

    axes = _plt.gcf().gca()
    axes.set_ylabel(r'$\alpha_{x,y}$')
    axes.set_xlabel('S / m')
    axes.legend(loc='best')

    _CallUserFigureFunctions(functions)
    _AddSurvey(alphaPlot, survey)
    _CallUserFigureFunctions(postfunctions)
    
    _plt.show(block=False)
    return alphaPlot

def PlotDs(tfsopt, bdsopt, survey=None, functions=None, postfunctions=None, figsize=(12,5)):
    N = str(int(bdsopt['Npart'][0]))  #number of primaries.
    dispPlot = _plt.figure('Dispersion', figsize=figsize)
    #tfs
    _plt.plot(tfsopt['S'], tfsopt['DXBETA'], 'b', label=r'MADX $D_{x}$')
    _plt.plot(tfsopt['S'], tfsopt['DYBETA'], 'g', label=r'MADX $D_{y}$')
    #bds
    _plt.errorbar(bdsopt['S'], bdsopt['Disp_x'],
                  yerr=bdsopt['Sigma_Disp_x'],
                  label=r'BDSIM $D_{x}$' + ' ; N = ' + N,
                  fmt='b.', capsize=3)

    _plt.errorbar(bdsopt['S'], bdsopt['Disp_y'],
                  yerr=bdsopt['Sigma_Disp_y'],
                  label=r'BDSIM $D_{y}$' + ' ; N = ' + N,
                  fmt='g.', capsize=3)

    axes = _plt.gcf().gca()
    axes.set_ylabel(r'$D_{x,y} / m$')
    axes.set_xlabel('S / m')
    axes.legend(loc='best')

    _CallUserFigureFunctions(functions)
    _AddSurvey(dispPlot, survey)
    _CallUserFigureFunctions(postfunctions)
    
    _plt.show(block=False)
    return dispPlot

def PlotDps(tfsopt, bdsopt, survey=None, functions=None, postfunctions=None, figsize=(12,5)):
    N = str(int(bdsopt['Npart'][0]))  #number of primaries.
    dispPPlot = _plt.figure('Momentum_Dispersion', figsize=figsize)
    #tfs
    _plt.plot(tfsopt['S'], tfsopt['DPXBETA'], 'b', label=r'MADX $D_{p_{x}}$')
    _plt.plot(tfsopt['S'], tfsopt['DPYBETA'], 'g', label=r'MADX $D_{p_{y}}$')
    #bds
    _plt.errorbar(bdsopt['S'], bdsopt['Disp_xp'],
                  yerr=bdsopt['Sigma_Disp_xp'],
                  label=r'BDSIM $D_{p_{x}}$' + ' ; N = ' + N,
                  fmt='b.', capsize=3)

    _plt.errorbar(bdsopt['S'], bdsopt['Disp_yp'],
                  yerr=bdsopt['Sigma_Disp_yp'],
                  label=r'BDSIM $D_{p_{y}}$' + ' ; N = ' + N,
                  fmt='g.', capsize=3)

    axes = _plt.gcf().gca()
    axes.set_ylabel(r'$D_{p_{x},p_{y}}$ / rad')
    axes.set_xlabel('S / m')
    axes.legend(loc='best')

    _CallUserFigureFunctions(functions)
    _AddSurvey(dispPPlot, survey)
    _CallUserFigureFunctions(postfunctions)
    
    _plt.show(block=False)
    return dispPPlot

def PlotEmitt(tfsopt, bdsopt, header, survey=None, functions=None, postfunctions=None, figsize=(12, 5)):
    N = str(int(bdsopt['Npart'][0]))  # number of primaries.
    emittPlot = _plt.figure('Emittance', figsize=figsize)
    ex = header['EX'] * _np.ones(len(tfsopt['S']))
    ey = header['EY'] * _np.ones(len(tfsopt['S']))

    # tfs
    _plt.plot(tfsopt['S'], ex, 'b', label=r'MADX $E_{x}$')
    _plt.plot(tfsopt['S'], ey, 'g', label=r'MADX $E_{x}$')
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

def PlotSigmas(tfsopt, bdsopt, survey=None, functions=None, postfunctions=None, figsize=(12,5)):
    N = str(int(bdsopt['Npart'][0]))  #number of primaries.
    sigmaPlot = _plt.figure('Sigma', figsize=figsize)
    #tfs
    _plt.plot(tfsopt['S'], tfsopt['SIGMAX'], 'b', label=r'MADX $\sigma_{x}$')
    _plt.plot(tfsopt['S'], tfsopt['SIGMAY'], 'g', label=r'MADX $\sigma_{y}$')
    #bds
    _plt.errorbar(bdsopt['S'],
                  bdsopt['Sigma_x'],
                  yerr=bdsopt['Sigma_Sigma_x'],
                  label=r'BDSIM $\sigma_{x}$' + ' ; N = ' + N,
                  fmt='b.', capsize=3)

    _plt.errorbar(bdsopt['S'],
                  bdsopt['Sigma_y'],
                  yerr=bdsopt['Sigma_Sigma_y'],
                  label=r'BDSIM $\sigma_{y}$' + ' ; N = ' + N,
                  fmt='g.', capsize=3)
    
    axes = _plt.gcf().gca()
    axes.set_ylabel(r'$\sigma_{x,y}$ / m')
    axes.set_xlabel('S / m')
    axes.legend(loc='best')

    _CallUserFigureFunctions(functions)
    _AddSurvey(sigmaPlot, survey)
    _CallUserFigureFunctions(postfunctions)
    
    _plt.show(block=False)
    return sigmaPlot

def PlotSigmasP(tfsopt, bdsopt, survey=None, functions=None, postfunctions=None, figsize=(12,5)):
    N = str(int(bdsopt['Npart'][0]))  #number of primaries.
    sigmaPPlot = _plt.figure('SigmaP', figsize=figsize)
    #tfs
    _plt.plot(tfsopt['S'], tfsopt['SIGMAXP'], 'b', label=r'MADX $\sigma_{xp}$')
    _plt.plot(tfsopt['S'], tfsopt['SIGMAYP'], 'g', label=r'MADX $\sigma_{yp}$')
    #bds
    _plt.errorbar(bdsopt['S'],
                  bdsopt['Sigma_xp'],
                  yerr=bdsopt['Sigma_Sigma_xp'],
                  label=r'BDSIM $\sigma_{xp}$' + ' ; N = ' + N,
                  fmt='b.', capsize=3)

    _plt.errorbar(bdsopt['S'],
                  bdsopt['Sigma_yp'],
                  yerr=bdsopt['Sigma_Sigma_yp'],
                  label=r'BDSIM $\sigma_{yp}$' + ' ; N = ' + N,
                  fmt='g.', capsize=3)
    
    axes = _plt.gcf().gca()
    axes.set_ylabel(r'$\sigma_{xp,yp}$ / rad')
    axes.set_xlabel('S / m')
    axes.legend(loc='best')

    _CallUserFigureFunctions(functions)
    _AddSurvey(sigmaPPlot, survey)
    _CallUserFigureFunctions(postfunctions)

    _plt.show(block=False)
    return sigmaPPlot

def PlotMeans(tfsopt, bdsopt, survey=None, functions=None, postfunctions=None, figsize=(12,5)):
    N = str(int(bdsopt['Npart'][0]))  #number of primaries.
    meanPlot = _plt.figure('Mean', figsize=figsize)
    #tfs
    _plt.plot(tfsopt['S'], tfsopt['X'], 'b', label=r'MADX $\bar{x}$')
    _plt.plot(tfsopt['S'], tfsopt['Y'], 'g', label=r'MADX $\bar{y}$')

    #bdsim
    _plt.errorbar(bdsopt['S'], bdsopt['Mean_x'],
                  yerr=bdsopt['Sigma_Mean_x'],
                  label=r'BDSIM $\bar{x}$' + ' ; N = ' + N,
                  fmt='b.', capsize=3)

    _plt.errorbar(bdsopt['S'], bdsopt['Mean_y'],
                  yerr=bdsopt['Sigma_Mean_y'],
                  label=r'BDSIM $\bar{y}$' + ' ; N = ' + N,
                  fmt='g.', capsize=3)

    axes = _plt.gcf().gca()
    axes.set_ylabel(r'$\bar{x}, \bar{y}$ / m')
    axes.set_xlabel('S / m')
    axes.legend(loc='best')

    _CallUserFigureFunctions(functions)
    _AddSurvey(meanPlot, survey)
    _CallUserFigureFunctions(postfunctions)
    
    _plt.show(block=False)
    return meanPlot

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

def MadxVsBDSIMOrbit(tfs, bds, survey=None, functions=None, postfunctions=None, figsize=(12,5)):
    """
    Plot both the BDSIM orbit and MADX orbit (mean x,y).

    tfs - either file name or pymadx.Data.Tfs instance
    bds - filename or BDSAsciiData instance - rebdsimOrbit, rebdsimOptics output files
    """
    _CheckFilesExist(tfs, bds, survey)
    tfsopt = _pymadx.Data.CheckItsTfs(tfs)
    bdsopt = _pybdsim._General.CheckItsBDSAsciiData(bds)

    if survey is None:
        survey = tfsopt

    orbitPlot = _plt.figure('Orbit', figsize=figsize)
    
    #tfs
    tfs_s = tfsopt.GetColumn('S')
    tfs_x = tfsopt.GetColumn('X')
    tfs_y = tfsopt.GetColumn('Y')
    _plt.plot(tfs_s, tfs_x, 'b', label=r'MADX $\bar{x}$')
    _plt.plot(tfs_s, tfs_y, 'g', label=r'MADX $\bar{y}$')

    #bdsim
    if type(bdsopt) == _pybdsim.Data.RebdsimFile:
        if (hasattr(bdsopt, "orbit")):
            bds_s = bdsopt.orbit.s()
            bds_x = bdsopt.orbit.x()
            bds_y = bdsopt.orbit.y()
        else:
            raise ValueError("No orbit in file")
    elif type(bdsopt) == _pybdsim.Data.BDSAsciiData:
        # ironically this will come if it's a rebdsim optics output
        bds_s = bdsopt.GetColumn('S')
        bds_x = bdsopt.GetColumn('Mean_x')
        bds_y = bdsopt.GetColumn('Mean_y')
    _plt.plot(bds_s, bds_x, 'b.', label='BDSIM x')
    #_plt.plot(bds_s, bds_x, 'b-', alpha=0.4)
    _plt.plot(bds_s, bds_y, 'g.', label='BDSIM y')
    #_plt.plot(bds_s, bds_y, 'g-', alpha=0.4)
    
    axes = _plt.gcf().gca()
    axes.set_ylabel(r'$\bar{x}, \bar{y}$ / m')
    axes.set_xlabel('S / m')
    axes.legend(loc='best')

    _CallUserFigureFunctions(functions)
    _AddSurvey(orbitPlot, survey)
    _CallUserFigureFunctions(postfunctions)

    _plt.show(block=False)
    return orbitPlot

def MadxVsBDSIMOrbitResiduals(tfs, bds, survey=None, functions=None, postfunctions=None, verbose=False, figsize=(12,5)):
    _CheckFilesExist(tfs, bds, survey)
    tfsinst   = _pymadx.Data.CheckItsTfs(tfs)
    bdsinst   = _pybdsim._General.CheckItsBDSAsciiData(bds)
    tfsd = PrepareResiduals(tfs, bds)
    tdata = tfsd[0]
    bdata = tfsd[1]

    if survey is None:
        survey = tfs

    dx  = tdata['X']  - bdata['X']
    dxp = tdata['PX'] - bdata['PX']
    dy  = tdata['Y']  - bdata['Y']
    dyp = tdata['PY'] - bdata['PY']

    s   = tdata['S']

    orbRes = _plt.figure('OrbitResiduals', figsize=figsize)
    _plt.plot(s, abs(dx),  '.', label='x')
    _plt.plot(s, abs(dxp), '.', label='xp')
    _plt.plot(s, abs(dy),  '.', label='y')
    _plt.plot(s, abs(dyp), '.', label='yp')
    _plt.legend()
    _plt.xlabel('S (m)')
    _plt.ylabel('|residual| (m, rad)')
    _plt.yscale('log')

    _CallUserFigureFunctions(functions)
    _AddSurvey(orbRes, survey)

    _plt.show(block=False)
    return orbRes

def _AddSurvey(figure, survey):
    if survey is None:
        return
    if isinstance(survey, str): # If BDSIM ASCII survey file
        if survey.split(".")[-1] == 'dat':
            _pybdsim.Plot.AddMachineLatticeFromSurveyToFigure(figure,survey)
    # If BDSIM ASCII survey instance
    elif isinstance(survey, _pybdsim.Data.BDSAsciiData):
        _pybdsim.Plot.AddMachineLatticeToFigure(figure,survey)
    elif isinstance(survey, _pymadx.Data.Tfs): # If TFS
        _pymadx.Plot.AddMachineLatticeToFigure(figure,survey)
    # if a (BDSIM) ROOT file
    elif _pybdsim._General.IsROOTFile(survey):
        pass

def _ProcessInput(tfsOptics, bdsimOptics):

    if not isinstance(tfsOptics, (_pymadx.Data.Tfs, str)):
        raise TypeError("tfsOptics should be either a path to a tfs file or "
                        "a pymadx.Data.Tfs instance!")
    if not isinstance(bdsimOptics, _pybdsim.Data.BDSAsciiData):
        raise TypeError("bdsimOptics should be either be a path to a "
                        "BDSAsciiData file or a pybdsim.Data.BDSAsciiData "
                        "instance")

    if isinstance(tfsOptics, str):
        tfsOptics = _pymadx.Data.Tfs(tfsOptics)
    if isinstance(tfsOptics, str):
        bdsimOptics = _pybdsim.Data.Load(bdsimOptics)

    return tfsOptics, bdsimOptics

def _CheckFilesExist(tfs, bdsim, survey):
    '''
    Otherwise such errors are too cryptic.
    '''
    if isinstance(tfs, str):
        if not _isfile(tfs):
            raise IOError("File not found: ", tfs)
    if isinstance(bdsim, str) and not _isfile(bdsim):
        raise IOError("File not found: ", bdsim)
    if isinstance(survey, str) and not _isfile(survey):
        raise IOError("File not found: ", survey)


def _CallUserFigureFunctions(functions):
    if isinstance(functions, list):
        for function in functions:
            if callable(function):
                function()
    elif callable(functions):
        functions()
