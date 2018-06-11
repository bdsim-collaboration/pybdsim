import pymadx as _pymadx
import pybdsim as _pybdsim
import matplotlib.pyplot as _plt
import numpy as _np
import os.path as _ospath
from matplotlib.backends.backend_pdf import PdfPages as _PdfPages
import datetime as _datetime
from pybdsim._General import CheckItsBDSAsciiData

# Predefined dicts of variables for making the standard plots,
# ptctwiss variables are the same as madx, ptc variables are the same as bdsim

_BETA =    {"bdsimdata"  : ("Beta_x", "Beta_y"),
            "bdsimerror" : ("Sigma_Beta_x","Sigma_Beta_y"),
            "madx"       : ("BETX", "BETY"),
            "legend"     : (r'$\beta_{x}$', r'$\beta_{y}$'),
            "xlabel"     : "S / m",
            "ylabel"     : r"$\beta_{x,y}$ / m",
            "title"      : "Beta"
            }

_ALPHA =   {"bdsimdata"  : ("Alpha_x", "Alpha_y"),
            "bdsimerror" : ("Sigma_Alpha_x","Sigma_Alpha_y"),
            "madx"       : ("ALFX", "ALFY"),
            "legend"     : (r'$\alpha_{x}$', r'$\alpha_{y}$'),
            "xlabel"     : "S / m",
            "ylabel"     : r"$\alpha_{x,y}$ / m",
            "title"      : "Alpha"
           }

_DISP  =   {"bdsimdata"  : ("Disp_x", "Disp_y"),
            "bdsimerror" : ("Sigma_Disp_x","Sigma_Disp_y"),
            "madx"       : ("DXBETA", "DYBETA"),
            "legend"     : (r"$D_{x}$", r"$D_{y}$"),
            "xlabel"     : "S / m",
            "ylabel"     : r"$D_{x,y} / m$",
            "title"      : "Dispersion"
            }

_DISP_P=   {"bdsimdata"  : ("Disp_xp", "Disp_yp"),
            "bdsimerror" : ("Sigma_Disp_xp","Sigma_Disp_yp"),
            "madx"       : ("DPXBETA", "DPYBETA"),
            "legend"     : (r"$D_{p_{x}}$", r"$D_{p_{y}}$"),
            "xlabel"     : "S / m",
            "ylabel"     : r"$D_{p_{x},p_{y}}$ / m",
            "title"      : "Momentum_Dispersion"
            }

_SIGMA =   {"bdsimdata"  : ("Sigma_x", "Sigma_y"),
            "bdsimerror" : ("Sigma_Sigma_x","Sigma_Sigma_y"),
            "madx"       : ("SIGMAX", "SIGMAY"),
            "legend"     : (r"$\sigma_{x}$",r"$\sigma_{y}$"),
            "xlabel"     : "S / m",
            "ylabel"     : r"$\sigma_{x,y}$ / m",
            "title"      : "Sigma"
            }

_SIGMA_P = {"bdsimdata"  : ("Sigma_xp", "Sigma_yp"),
            "bdsimerror" : ("Sigma_Sigma_xp","Sigma_Sigma_yp"),
            "madx"       : ("SIGMAXP", "SIGMAYP"),
            "legend"     : (r"$\sigma_{xp}$",r"$\sigma_{yp}$"),
            "xlabel"     : "S / m",
            "ylabel"     : r"$\sigma_{xp,yp}$ / rad",
            "title"      : "SigmaP"
            }

_MEAN    = {"bdsimdata"  : ("Mean_x", "Mean_y"),
            "bdsimerror" : ("Sigma_Mean_x","Sigma_Mean_y"),
            "madx"       : ("X", "Y"),
            "legend"     : (r"$\bar{x}$", r"$\bar{y}$"),
            "xlabel"     : "S / m",
            "ylabel"     : r"$\bar{x}, \bar{y}$ / m",
            "title"      : "Mean"
            }

_EMITT   = {"bdsimdata"  : ("Emitt_x", "Emitt_y"),
            "bdsimerror" : ("Sigma_Emitt_x","Sigma_Emitt_y"),
            "madx"       : ("EX", "EY"),
            "legend"     : (r"$E_{x}$", r"$E_{y}$"),
            "xlabel"     : "S / m",
            "ylabel"     : r"$E_{x}, E_{y}$",
            "title"      : "Emittance"
            }

def _LoadData(bdsim, bdsimname, madx, madxname, ptctwiss, ptctwissname, ptc, ptcname):
    """
    Load the supplied data. Can handle lists of supplied data files and names.
    Returns: listOfData, listOfNames
    """
    def Load(data, name, datatype, parsingfunction):
        """ data     : list of tfs output filenames
            name     : list of names to be used in plot legend
            datatype : string of data type, e.g. "madx". used for error output only
            parsingfunction : callable function to parse the supplied input

            Returns :  list, list
            """
        datas = []
        names = []
        if len(name) != len(data):
            print("Incorrect Number of "+datatype+" names supplied, ignoring supplied names...")
            for entryNumber, entry in enumerate(data):
                thisData, thisName = parsingfunction(entry, None)
                datas.append(thisData)
                names.append(thisName)
        else:
            for entryNumber, entry in enumerate(data):
                thisData, thisName = parsingfunction(entry, name[entryNumber])
                datas.append(thisData)
                names.append(thisName)
        return datas, names

    # convert single filenames to lists
    if isinstance(bdsim, basestring) or (bdsim is None):
        bdsim = [bdsim]
        bdsimname = [bdsimname]
    if isinstance(madx, basestring) or (madx is None):
        madx = [madx]
        madxname = [madxname]
    if isinstance(ptctwiss, basestring) or (ptctwiss is None):
        ptctwiss = [ptctwiss]
        ptctwissname = [ptctwissname]
    if isinstance(ptc, basestring) or (ptc is None):
        ptc = [ptc]
        ptcname = [ptcname]

    # load all data
    bdsim, bdsim_name = Load(bdsim, bdsimname, "bdsim", _parse_bdsim_input)
    madx, madx_name = Load(madx, madxname, "madx", _parse_tfs_input)
    ptctwiss, ptctwiss_name = Load(ptctwiss, ptctwissname, "ptctwiss", _parse_tfs_input)
    ptc, ptc_name = Load(ptc, ptcname, "ptc", _parse_bdsim_input)

    #add data and names to dicts
    data = {"bdsim": bdsim,
            "madx": madx,
            "ptctwiss": ptctwiss,
            "ptc": ptc
            }

    names = {"bdsim": bdsim_name,
             "madx": madx_name,
             "ptctwiss": ptctwiss_name,
             "ptc": ptc_name
             }
    return data, names

def _parse_bdsim_input(bdsim_in, name):
    """Return bdsim_in as a BDSAsciiData instance, which should either
    be a path to a BDSIM root output file, rebdsimOptics output file,
    or a BDSAsciiData instance, and in either case, generate a
    name if None is provided, and return that as well."""
    if bdsim_in is None:
        return None, None
    if isinstance(bdsim_in, basestring):
        if not _ospath.isfile(bdsim_in):
            raise IOError("file \"{}\" not found!".format(bdsim_in))
        name = (_ospath.splitext(_ospath.basename(bdsim_in))[0]
                if name is None else name)
        return _pybdsim.Data.Load(bdsim_in).Optics, name
    try:
        if isinstance(bdsim_in, _pybdsim.Data.RebdsimFile):
            bdsim_in = bdsim_in.Optics
        name = bdsim_in.filename if name is None else name
        return bdsim_in, name
    except AttributeError:
        raise TypeError(
            "Expected Tfs input is neither a "
            "file path nor a Tfs instance: {}".format(bdsim_in))

def _parse_tfs_input(tfs_in, name):
    """Return tfs_in as a Tfs instance, which should either be a path
    to a TFS file or a Tfs instance, and in either case, generate a
    name if None is provided, and return that as well."""
    if tfs_in is None:
        return None, None
    if isinstance(tfs_in, basestring):
        if not _ospath.isfile(tfs_in):
            raise IOError("file \"{}\" not found!".format(tfs_in))
        name = (_ospath.splitext(_ospath.basename(tfs_in))[0]
                if name is None else name)
        return _pymadx.Data.Tfs(tfs_in), name
    try:
        name = tfs_in.filename if name is None else name
        return tfs_in, name
    except AttributeError:
        raise TypeError(
            "Expected Tfs input is neither a "
            "file path nor a Tfs instance: {}".format(tfs_in))

# template plotter for BDSIM type data (BDSIM and PTC)
def _plotBdsimType(data, name, plot_info, axis='both', **kwargs):
    """ data : pybdsim.Data.RebdsimFile instance
        name : supplied tfsname
        plot_info : one of the predefined dicts from top of this file
        axis : which axis to plot (x, y, or both)"""
    def _plot(data, name, plot_info, n, **kwargs):
        """ data : pymadx.Data.Tfs instance
            name : supplied tfsname
            plot_info : one of the predefined dicts from top of this file
            axis : index of tuple in predefined dict. """
        variable      = plot_info["bdsimdata"][n]  #variable name from predefined dict
        variableError = plot_info["bdsimerror"][n] #variable error name from predefined dict
        legendname    = plot_info["legend"][n]     #legend name from predefined dict
        _plt.errorbar(data.GetColumn('S'),
                      data.GetColumn(variable),
                      yerr=data.GetColumn(variableError),
                      label="{}; {}; N = {:.1E}".format(name, legendname, data.Npart()[0]),
                      capsize=3, **kwargs)
    # plot specific axes according to tuple index in predefined dict
    # x = 0, y = 1
    if axis == 'x':
        _plot(data, name, plot_info, 0, **kwargs)
    elif axis == 'y':
        _plot(data, name, plot_info, 1, **kwargs)
    elif axis == 'both':
        _plot(data, name, plot_info, 0, **kwargs)
        _plot(data, name, plot_info, 1, **kwargs)

# template plotter for madx type data (madx and ptctwiss)
def _plotMadxType(data, name, plot_info, axis='both', **kwargs):
    """ data : pymadx.Data.Tfs instance
        name : supplied tfsname
        plot_info : one of the predefined dicts from top of this file
        axis : which axis to plot (x, y, or both) """
    def _plot(data, name, plot_info, n, **kwargs):
        """ data : pymadx.Data.Tfs instance
            name : supplied tfsname
            plot_info : one of the predefined dicts from top of this file
            axis : index of tuple in predefined dict. """
        variable   = plot_info["madx"][n]      #variable name from predefined dict
        legendname = plot_info["legend"][n]    #legend name from predefined dict
        title      = plot_info['title'] + axis #add axis to distinguish plot titles
        s = data.GetColumn('S')
        #emittance is a number in the header so convert to an array for plotting
        if title[:5] == "Emitt":
            var = data.header[plot_info["madx"][n]] * _np.ones(len(data.GetColumn('S')))
        else:
            var = data.GetColumn(variable)
        _plt.plot(s, var, label="{}: {}".format(name, legendname), **kwargs)
    if axis == 'x':
        _plot(data, name, plot_info, 0, **kwargs)
    elif axis == 'y':
        _plot(data, name, plot_info, 1, **kwargs)
    elif axis == 'both':
        _plot(data, name, plot_info, 0, **kwargs)
        _plot(data, name, plot_info, 1, **kwargs)

# use closure to avoid tonnes of boilerplate code
def _make_plotter(plot_info):
    """ plot_info : one of the predefined dicts from top of this file """

    def f_out(alldata, allnames, axis='both', survey=None, figsize=(10,5), **kwargs):
        """ alldata  : dict of all data returned by _LoadData method
            allnames : dict of all names returned by _LoadData method
            axis     : axis/axes to plot. Can be 'x', 'y' or 'both'
            survey   : bdsim survey
            """
        # extract plot labelling from predefined dict
        x_label = plot_info['xlabel']
        y_label = plot_info['ylabel']
        title   = plot_info['title'] + axis  #add axis to distinguish plot titles

        plot = _plt.figure(title, figsize, **kwargs)

        # loop over data lists and plot using appropriate function
        if alldata["bdsim"] is not None:
            for bdsimIndex,bdsimData in enumerate(alldata["bdsim"]):
                _plotBdsimType(bdsimData, allnames["bdsim"][bdsimIndex], plot_info, axis, **kwargs)

        if alldata["madx"] is not None:
            for madxIndex,madxData in enumerate(alldata["madx"]):
                _plotMadxType(madxData, allnames["madx"][madxIndex], plot_info, axis, **kwargs)

        if alldata["ptctwiss"] is not None:
            for ptctwissIndex,ptcData in enumerate(alldata["ptctwiss"]):
                _plotMadxType(ptcData, allnames["ptctwiss"][ptctwissIndex], plot_info, axis, **kwargs)

        if alldata["ptc"] is not None:
            for ptcIndex,ptcData in enumerate(alldata["ptc"]):
                _plotBdsimType(ptcData, allnames["ptc"][ptcIndex], plot_info, axis, **kwargs)

        # Set axis labels and draw legend
        axes = _plt.gcf().gca()
        axes.set_ylabel(y_label)
        axes.set_xlabel(x_label)
        axes.legend(loc='best')

        if survey is not None:
            try:
                _pybdsim.Plot.AddMachineLatticeFromSurveyToFigure(_plt.gcf(), survey)
            except IOError:
                _pybdsim.Plot.AddMachineLatticeToFigure(_plt.gcf(), survey)
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


def CompareMultipleOptics(bdsim=None, bdsimname=None,
                          tfs=None, tfsname=None,
                          ptctwiss=None, ptctwissname=None,
                          ptc=None, ptcname=None,
                          survey=None, figsize=(9, 5), saveAll=True, outputFilename=None, **kwargs):
    """
    Compares optics of multiple files supplied. Can be any combination of single or multiple
    BDSIM, Tfs, ptc_twiss output, or PTC output (PTC output converted to BDSIM compatible format).

    Names can be supplied along with the filenames that will appear in the legend. Multiple filenames
    can be supplied in a list. If the number of names is not equal to the number of filenames, the supplied
    names will be ignored.

    Up to 6 files can be compared to one another.

    If up to 2 files are supplied, the optical functions for the x and y axes are plotted on the
    same figure

    If more than 2 files are supplied, the optical functions for the x and y axes are plotted on
    seperate figures.

    +-----------------+---------------------------------------------------------+
    | **Parameters**  | **Description**                                         |
    +-----------------+---------------------------------------------------------+
    | bdsim           | Optics root file (from rebdsimOptics or rebdsim),       |
    |                 | or list of multiple optics root files.                  |
    |                 | default = None                                          |
    +-----------------+---------------------------------------------------------+
    | bdsimname       | bdsim name that will appear in the plot legend          |
    |                 | or list of multiple bdsim names.                        |
    |                 | default = None                                          |
    +-----------------+---------------------------------------------------------+
    | tfs             | Tfs file (or pymadx.Data.Tfs instance),                 |
    |                 | or list of multiple Tfs files.                          |
    |                 | default = None                                          |
    +-----------------+---------------------------------------------------------+
    | tfsname         | tfs name that will appear in the plot legend            |
    |                 | or list of multiple tfs names.                          |
    |                 | default = None                                          |
    +-----------------+---------------------------------------------------------+
    | ptctwiss        | ptctwiss output file (or pymadx.Data.Tfs instance),     |
    |                 | of list of multiple ptctwiss files.                     |
    |                 | default = None                                          |
    +-----------------+---------------------------------------------------------+
    | ptctwissname    | ptctwiss name that will appear in the plot legend       |
    |                 | or list of multiple ptctwiss names.                     |
    |                 | default = None                                          |
    +-----------------+---------------------------------------------------------+
    | ptc             | Optics root file (from rebdsimOptics or rebdsim) that   |
    |                 | was generated with PTC data that has been               |
    |                 | converted to bdsim format via ptc2bdsim,                |
    |                 | or list of multiple files.                              |
    |                 | default = None                                          |
    +-----------------+---------------------------------------------------------+
    | ptcname         | ptc name that will appear in the plot legend            |
    |                 | or list of multiple ptc names.                          |
    |                 | default = None                                          |
    +-----------------+---------------------------------------------------------+
    | survey          | BDSIM model survey.                                     |
    +-----------------+---------------------------------------------------------+
    | figsize         | Figure size for all figures - default is (9,5)          |
    +-----------------+---------------------------------------------------------+
    | saveAll         | Save all plots generated in a single pdf file           |
    |                 | default = True.                                         |
    +-----------------+---------------------------------------------------------+
    | outputFilename  | filename of generated plots.                            |
    |                 | default = optics-report.pdf                             |
    +-----------------+---------------------------------------------------------+

    examples:

    pybdsim.Compare.CompareOptics(bdsim=["t1_optics.root","t2_optics.root"], bdsimname=["BDSIM 10 GeV","BDSIM 20 GeV"],
                                  tfs=["t1.tfs","t2.tfs"], tfsname=["TFS 10 GeV","TFS 20 GeV"],
                                  outputFilename="BDSIMVsTFS_10GeV20GeV.pdf")

    pybdsim.Compare.CompareOptics(bdsim="t1_optics.root",bdsimname="BDSIM", tfs="t1.tfs", tfsname="Madx Twiss",
                                  ptctwiss="ptc_twiss.outx", ptctwissname="PTC Twiss",
                                  ptc="ptc_optics.root", ptcname="PTC Track",
                                  survey="bdsim_surv.dat', outputFilename="BDSIMVsTFSVsPTCTWISSVsPTCTRACK.pdf")

    """

    if (bdsim is None) and (tfs is None) and (ptctwiss is None) and (ptc is None):
        print("Nothing to compare.")
        return

    # load data and get names
    data, names = _LoadData(bdsim, bdsimname, tfs, tfsname, ptctwiss, ptctwissname, ptc, ptcname)

    # check number of entries being compared. If > 2, plot x and y seperately
    numBdsim    = len([x for x in data["bdsim"] if x is not None])
    numMadx     = len([x for x in data["madx"] if x is not None])
    numPtcTwiss = len([x for x in data["ptctwiss"] if x is not None])
    numPtc      = len([x for x in data["ptc"] if x is not None])
    total = numBdsim + numMadx + numPtc + numPtcTwiss
    if total > 6:
        print("Too many files to compare")
        return

    # if > 2, plot x and y seperately.
    plotAxesSeperately = False
    if total > 2:
        plotAxesSeperately=True

    if isinstance(survey, basestring):
        if not _ospath.isfile(survey):
            raise IOError("Survey not found: ", survey)

    # load once here to save loading for every plot
    survey = CheckItsBDSAsciiData(survey)

    if plotAxesSeperately:
        figures = [
        PlotBeta(data,   names, axis='x', survey=survey, figsize=figsize, **kwargs),
        PlotBeta(data,   names, axis='y', survey=survey, figsize=figsize, **kwargs),
        PlotAlpha(data,  names, axis='x', survey=survey, figsize=figsize, **kwargs),
        PlotAlpha(data,  names, axis='y', survey=survey, figsize=figsize, **kwargs),
        PlotDisp(data,   names, axis='x', survey=survey, figsize=figsize, **kwargs),
        PlotDisp(data,   names, axis='y', survey=survey, figsize=figsize, **kwargs),
        PlotDispP(data,  names, axis='x', survey=survey, figsize=figsize, **kwargs),
        PlotDispP(data,  names, axis='y', survey=survey, figsize=figsize, **kwargs),
        PlotSigma(data,  names, axis='x', survey=survey, figsize=figsize, **kwargs),
        PlotSigma(data,  names, axis='y', survey=survey, figsize=figsize, **kwargs),
        PlotSigmaP(data, names, axis='x', survey=survey, figsize=figsize, **kwargs),
        PlotSigmaP(data, names, axis='y', survey=survey, figsize=figsize, **kwargs),
        PlotMean(data,   names, axis='x', survey=survey, figsize=figsize, **kwargs),
        PlotMean(data,   names, axis='y', survey=survey, figsize=figsize, **kwargs),
        PlotEmitt(data,  names, axis='x', survey=survey, figsize=figsize, **kwargs),
        PlotEmitt(data,  names, axis='y', survey=survey, figsize=figsize, **kwargs),
        PlotNPart(data,  names, survey=survey, figsize=figsize, **kwargs)
            ]
    else:
        figures = [
        PlotBeta(data,   names, survey=survey, figsize=figsize, **kwargs),
        PlotAlpha(data,  names, survey=survey, figsize=figsize, **kwargs),
        PlotDisp(data,   names, survey=survey, figsize=figsize, **kwargs),
        PlotDispP(data,  names, survey=survey, figsize=figsize, **kwargs),
        PlotSigma(data,  names, survey=survey, figsize=figsize, **kwargs),
        PlotSigmaP(data, names, survey=survey, figsize=figsize, **kwargs),
        PlotMean(data,   names, survey=survey, figsize=figsize, **kwargs),
        PlotEmitt(data,  names, survey=survey, figsize=figsize, **kwargs),
        PlotNPart(data,  names, survey=survey, figsize=figsize, **kwargs)
            ]

    if saveAll:
        if outputFilename is not None:
            output_filename = outputFilename
        else:
            output_filename = "optics-report.pdf"

        with _PdfPages(output_filename) as pdf:
            for figure in figures:
                pdf.savefig(figure)
            d = pdf.infodict()
            d['Title'] = "Multi Code Optical Comparison"
            d['CreationDate'] = _datetime.datetime.today()
        print "Written ", output_filename


def PlotNPart(data, names, survey=None, figsize=(10, 5), **kwargs):
    """ Method for plotting the number of particles.
        Seperate as only applicable to BDSIM/PTC type files.
        """
    npartPlot = _plt.figure('NParticles', figsize, **kwargs)
    for i in range(len(data["bdsim"])):
        bdsimdata = data["bdsim"][i]
        bdsimname = names["bdsim"][i]
        _plt.plot(bdsimdata.GetColumn('S'), bdsimdata.GetColumn('Npart'), 'k-', label="{};".format(bdsimname))

    for i in range(len(data["ptc"])):
        ptcdata   = data["ptc"][i]
        ptcname   = names["ptc"][i]
        if ptcdata is not None:
            _plt.plot(ptcdata.GetColumn('S'), ptcdata.GetColumn('Npart'), 'k-', label="{};".format(ptcname))

    axes = _plt.gcf().gca()
    axes.set_ylabel(r'N Particles')
    axes.set_xlabel('S / m')
    axes.legend(loc='best')

    if survey is not None:
        try:
            _pybdsim.Plot.AddMachineLatticeFromSurveyToFigure(_plt.gcf(), survey)
        except IOError:
            _pybdsim.Plot.AddMachineLatticeToFigure(_plt.gcf(), survey)
    _plt.show(block=False)
    return npartPlot