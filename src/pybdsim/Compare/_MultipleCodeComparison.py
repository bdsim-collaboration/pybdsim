import pymadx as _pymadx
import pybdsim as _pybdsim
import matplotlib.pyplot as _plt
import numpy as _np
import os.path as _ospath
from matplotlib.backends.backend_pdf import PdfPages as _PdfPages
import datetime as _datetime
from pybdsim._General import CheckItsBDSAsciiData, CheckBdsimDataHasSurveyModel

# Predefined dicts of variables for making the standard plots,
# ptctwiss variables are the same as madx, ptc variables are the same as bdsim

_BETA =    {"bdsimdata"  : ("Beta_x", "Beta_y"),
            "bdsimerror" : ("Sigma_Beta_x","Sigma_Beta_y"),
            "madx"       : ("BETX", "BETY"),
            "legend"     : (r'$\beta_{x}$', r'$\beta_{y}$'),
            "xlabel"     : "S / m",
            "ylabel"     : (r"$\beta_{x,y}$ / m",r"$\beta_{x}$ / m",r"$\beta_{y}$ / m"),
            "title"      : "Beta"
            }

_ALPHA =   {"bdsimdata"  : ("Alpha_x", "Alpha_y"),
            "bdsimerror" : ("Sigma_Alpha_x","Sigma_Alpha_y"),
            "madx"       : ("ALFX", "ALFY"),
            "legend"     : (r'$\alpha_{x}$', r'$\alpha_{y}$'),
            "xlabel"     : "S / m",
            "ylabel"     : (r"$\alpha_{x,y}$ / m",r"$\alpha_{x}$ / m",r"$\alpha_{y}$ / m"),
            "title"      : "Alpha"
           }

_DISP  =   {"bdsimdata"  : ("Disp_x", "Disp_y"),
            "bdsimerror" : ("Sigma_Disp_x","Sigma_Disp_y"),
            "madx"       : ("DXBETA", "DYBETA"),
            "legend"     : (r"$D_{x}$", r"$D_{y}$"),
            "xlabel"     : "S / m",
            "ylabel"     : (r"$D_{x,y} / m$",r"$D_{x} / m$",r"$D_{y} / m$"),
            "title"      : "Dispersion"
            }

_DISP_P=   {"bdsimdata"  : ("Disp_xp", "Disp_yp"),
            "bdsimerror" : ("Sigma_Disp_xp","Sigma_Disp_yp"),
            "madx"       : ("DPXBETA", "DPYBETA"),
            "legend"     : (r"$D_{p_{x}}$", r"$D_{p_{y}}$"),
            "xlabel"     : "S / m",
            "ylabel"     : (r"$D_{p_{x},p_{y}}$ / m",r"$D_{p_{x}}$ / m",r"$D_{p_{y}}$ / m"),
            "title"      : "Momentum_Dispersion"
            }

_SIGMA =   {"bdsimdata"  : ("Sigma_x", "Sigma_y"),
            "bdsimerror" : ("Sigma_Sigma_x","Sigma_Sigma_y"),
            "madx"       : ("SIGMAX", "SIGMAY"),
            "legend"     : (r"$\sigma_{x}$",r"$\sigma_{y}$"),
            "xlabel"     : "S / m",
            "ylabel"     : (r"$\sigma_{x,y}$ / m",r"$\sigma_{x}$ / m",r"$\sigma_{y}$ / m"),
            "title"      : "Sigma"
            }

_SIGMA_P = {"bdsimdata"  : ("Sigma_xp", "Sigma_yp"),
            "bdsimerror" : ("Sigma_Sigma_xp","Sigma_Sigma_yp"),
            "madx"       : ("SIGMAXP", "SIGMAYP"),
            "legend"     : (r"$\sigma_{xp}$",r"$\sigma_{yp}$"),
            "xlabel"     : "S / m",
            "ylabel"     : (r"$\sigma_{xp,yp}$ / rad",r"$\sigma_{xp}$ / rad",r"$\sigma_{yp}$ / rad"),
            "title"      : "SigmaP"
            }

_MEAN    = {"bdsimdata"  : ("Mean_x", "Mean_y"),
            "bdsimerror" : ("Sigma_Mean_x","Sigma_Mean_y"),
            "madx"       : ("X", "Y"),
            "legend"     : (r"$\bar{x}$", r"$\bar{y}$"),
            "xlabel"     : "S / m",
            "ylabel"     : (r"$\bar{x}, \bar{y}$ / m",r"$\bar{x}$ / m",r"$\bar{y}$ / m"),
            "title"      : "Mean"
            }

_MEAN_P  = {"bdsimdata"  : ("Mean_xp", "Mean_yp"),
            "bdsimerror" : ("Sigma_Mean_xp","Sigma_Mean_yp"),
            "madx"       : ("PX", "PY"),
            "legend"     : (r"$\bar{xp}$", r"$\bar{yp}$"),
            "xlabel"     : "S / m",
            "ylabel"     : (r"$\bar{xp}, \bar{yp}$ / rad",r"$\bar{xp}$ / rad",r"$\bar{yp}$ / rad"),
            "title"      : "MeanP"
            }

_EMITT   = {"bdsimdata"  : ("Emitt_x", "Emitt_y"),
            "bdsimerror" : ("Sigma_Emitt_x","Sigma_Emitt_y"),
            "madx"       : ("EX", "EY"),
            "legend"     : (r"$E_{x}$", r"$E_{y}$"),
            "xlabel"     : "S / m",
            "ylabel"     : (r"$E_{x}, E_{y}$",r"$E_{x}$",r"$E_{y}$"),
            "title"      : "Emittance"
            }

def _LoadData(bdsim, bdsimname, madx, madxname, ptctwiss, ptctwissname, ptc, ptcname, relativeTo=None):
    """
    Load the supplied data. Can handle lists of supplied data files and names.
    Returns: dictOfData, dictOfNames
    """
    def Load(data, name, datatype, parsingfunction):
        """ data     : list of output files or instances
            name     : list of names to be used in plot legend
            datatype : string of data type, e.g. "madx". used for error output only
            parsingfunction : callable function to parse the supplied input

            Returns :  list, list
            """
        datas = []
        names = []
        if isinstance(data, _pybdsim.Data.BDSAsciiData):
            thisData, thisName = parsingfunction(data, name)
            datas.append(thisData)
            names.append(thisName)
        elif isinstance(data, _pymadx.Data.Tfs):
            thisData, thisName = parsingfunction(data, name)
            datas.append(thisData)
            names.append(thisName)
        elif isinstance(data, _pybdsim.Data.RebdsimFile):
            try:
                thisData, thisName = parsingfunction(data.optics, name)
                datas.append(thisData)
                names.append(thisName)
            except AttributeError:
                raise AttributeError("No optics data found in pybdsim.Data.RebdsimFile object")
        elif len(name) != len(data):
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

    # convert single filenames to lists. Nothing for residual file - handle separately.
    if isinstance(bdsim, str) or (bdsim is None):
        bdsim = [bdsim]
        bdsimname = [bdsimname]
    if isinstance(madx, str) or (madx is None):
        madx = [madx]
        madxname = [madxname]
    if isinstance(ptctwiss, str) or (ptctwiss is None):
        ptctwiss = [ptctwiss]
        ptctwissname = [ptctwissname]
    if isinstance(ptc, str) or (ptc is None):
        ptc = [ptc]
        ptcname = [ptcname]

    # load all data
    bdsim, bdsim_name = Load(bdsim, bdsimname, "bdsim", _parse_bdsim_input)
    madx, madx_name = Load(madx, madxname, "madx", _parse_tfs_input)
    ptctwiss, ptctwiss_name = Load(ptctwiss, ptctwissname, "ptctwiss", _parse_tfs_input)
    ptc, ptc_name = Load(ptc, ptcname, "ptc", _parse_bdsim_input)
    relativeTo, rel_name = Load([relativeTo], [""], "RelativeTo", _parse_relative_input)

    # add data and names to dicts
    data = {"bdsim": bdsim,
            "madx": madx,
            "ptctwiss": ptctwiss,
            "ptc": ptc,
            "rel": relativeTo
            }

    names = {"bdsim": bdsim_name,
             "madx": madx_name,
             "ptctwiss": ptctwiss_name,
             "ptc": ptc_name,
             "rel": rel_name
             }
    return data, names

def _parse_bdsim_input(bdsim_in, name):
    """Return bdsim_in as a BDSAsciiData instance, which should either
    be a path to a BDSIM root output file, rebdsimOptics output file,
    or a BDSAsciiData instance, and in either case, generate a
    name if None is provided, and return that as well."""
    if bdsim_in is None:
        return None, None
    if isinstance(bdsim_in, str):
        if not _ospath.isfile(bdsim_in):
            raise IOError("file \"{}\" not found!".format(bdsim_in))
        name = (_ospath.splitext(_ospath.basename(bdsim_in))[0]
                if name is None else name)
        data = _pybdsim.Data.Load(bdsim_in)
        if hasattr(data,'Optics'):
            return _pybdsim.Data.Load(bdsim_in).Optics, name
        elif hasattr(data, 'optics'):
            return _pybdsim.Data.Load(bdsim_in).optics, name
        else:
            raise AttributeError("Optics not found in supplied file : {}".format(bdsim_in))
    if isinstance(bdsim_in, _pybdsim.Data.RebdsimFile):
        if hasattr(bdsim_in,'Optics'):
            bdsim_in = bdsim_in.Optics
        elif hasattr(bdsim_in, 'optics'):
            bdsim_in = bdsim_in.optics
        else:
            raise AttributeError("Optics not found in supplied file : {}".format(bdsim_in))
        name = bdsim_in.filename if name is None else name
        return bdsim_in, name
    elif isinstance(bdsim_in, _pybdsim.Data.BDSAsciiData):
        if hasattr(bdsim_in, 'Optics'):
            bdsim_in = bdsim_in.Optics
            name = bdsim_in.filename if name is None else name
            return bdsim_in, name
        elif hasattr(bdsim_in, 'optics'):
            bdsim_in = bdsim_in.optics
            name = bdsim_in.filename if name is None else name
            return bdsim_in, name
        elif hasattr(bdsim_in, 'S'):
            name = bdsim_in.filename if name is None else name
            return bdsim_in, name

def _parse_tfs_input(tfs_in, name):
    """Return tfs_in as a Tfs instance, which should either be a path
    to a TFS file or a Tfs instance, and in either case, generate a
    name if None is provided, and return that as well."""
    if tfs_in is None:
        return None, None
    if isinstance(tfs_in, str):
        if not _ospath.isfile(tfs_in):
            raise IOError("file \"{}\" not found!".format(tfs_in))
        name = (_ospath.splitext(_ospath.basename(tfs_in))[0]
                if name is None else name)
        return _pymadx.Data.Tfs(tfs_in), name
    try:
        if isinstance(tfs_in, _pymadx.Data.Tfs):
            name = tfs_in.header["NAME"] if name is None else name
            return tfs_in, name
        else:
            name = tfs_in.filename if name is None else name
            return tfs_in, name
    except AttributeError:
        raise TypeError(
            "Expected Tfs input is neither a "
            "file path nor a Tfs instance: {}".format(tfs_in))

def _parse_relative_input(rel_in, name):
    """Return relative data as the appropriate instance, which should either be a path
    to a TFS or BDSAsciiData file or instance, and in either case, generate a
    name if None is provided, and return that as well."""
    if rel_in is None:
        return None, None
    if isinstance(rel_in, str):
        if not _ospath.isfile(rel_in):
            raise IOError("file \"{}\" not found!".format(rel_in))
        name = (_ospath.splitext(_ospath.basename(rel_in))[0]
                if name is None else name)
        try:
            return _pymadx.Data.Tfs(rel_in), name
        except ValueError:  # malformed TFS
            pass
        try:
            return _pybdsim.Data.Load(rel_in).Optics, name
        except AttributeError:  # won't have Optics attribute
            pass
    try:
        if isinstance(rel_in, _pymadx.Data.Tfs):
            name = rel_in.header["NAME"] if name is None else name
            return rel_in, name
        else:
            name = rel_in.filename if name is None else name
            return rel_in, name
    except AttributeError:
        pass
    try:
        if isinstance(rel_in, _pybdsim.Data.RebdsimFile):
            rel_in = rel_in.Optics
            name = rel_in.filename if name is None else name
            return rel_in, name
        elif isinstance(rel_in, _pybdsim.Data.BDSAsciiData):
            if hasattr(rel_in, 'Optics'):
                rel_in = rel_in.Optics
                name = rel_in.filename if name is None else name
                return rel_in, name
            elif hasattr(rel_in, 'S'):
                name = rel_in.filename if name is None else name
                return rel_in, name
    except AttributeError:
        pass
    raise ValueError("Unknown data type for relative data.")

# template plotter for BDSIM type data (BDSIM and PTC)
def _plotBdsimType(data, name, plot_info, axis='both', **kwargs):
    """ data : pybdsim.Data.RebdsimFile instance
        name : supplied tfsname
        plot_info : one of the predefined dicts from top of this file
        axis : which axis to plot (x, y, or both)"""
    def _plot(data, variableName, errorVariableName , legLabel='', **kwargs):
        """ Plots the BDSIM type data with errors."""
        _plt.errorbar(data.GetColumn('S'),
                      data.GetColumn(variableName),
                      yerr=data.GetColumn(errorVariableName),
                      label=legLabel,
                      capsize=3, **kwargs)

    # plot specific axes according to tuple index in predefined dict. x = 0, y = 1
    if axis == 'x':
        legendLabel = "{}; N = {:.1E}".format(name, data.Npart()[0])
        _plot(data, plot_info["bdsimdata"][0], plot_info["bdsimerror"][0], legendLabel, **kwargs)
    elif axis == 'y':
        legendLabel = "{}; N = {:.1E}".format(name, data.Npart()[0])
        _plot(data, plot_info["bdsimdata"][1], plot_info["bdsimerror"][1], legendLabel, **kwargs)
    elif axis == 'both':
        xlegendLabel = "{}; {}; N = {:.1E}".format(name, plot_info["legend"][0], data.Npart()[0])
        ylegendLabel = "{}; {}; N = {:.1E}".format(name, plot_info["legend"][1], data.Npart()[0])
        _plot(data, plot_info["bdsimdata"][0], plot_info["bdsimerror"][0], xlegendLabel, **kwargs)
        _plot(data, plot_info["bdsimdata"][1], plot_info["bdsimerror"][1], ylegendLabel, **kwargs)

# template plotter for madx type data (madx and ptctwiss)
def _plotMadxType(data, name, plot_info, axis='both', **kwargs):
    """ data : pymadx.Data.Tfs instance
        name : supplied tfsname
        plot_info : one of the predefined dicts from top of this file
        axis : which axis to plot (x, y, or both) """
    def _plot(data, plot_info, n, legLabel='', **kwargs):
        """ Plots the MADX type data."""
        variable = plot_info["madx"][n]  # variable name from predefined dict
        title = plot_info['title'] + axis  # add axis to distinguish plot titles
        s = data.GetColumn('S')
        # emittance is a number in the header so convert to an array for plotting
        if title[:5] == "Emitt":
            var = data.header[plot_info["madx"][n]] * _np.ones(len(data.GetColumn('S')))
        else:
            var = data.GetColumn(variable)
        _plt.plot(s, var, label=legLabel, **kwargs)

    if axis == 'x':
        _plot(data, plot_info, 0, name, **kwargs)
    elif axis == 'y':
        _plot(data, plot_info, 1, name, **kwargs)
    elif axis == 'both':
        xlegendLabel = "{}: {}".format(name, plot_info["legend"][0])
        ylegendLabel = "{}: {}".format(name, plot_info["legend"][1])
        _plot(data, plot_info, 0, xlegendLabel, **kwargs)
        _plot(data, plot_info, 1, ylegendLabel, **kwargs)

# template residual plotter for all data types
def _plotResiduals(alldata, allnames,
                   plot_info,
                   plotterData=None,
                   axis='both',
                   plotErrors=True,
                   **kwargs):
    """ alldata  : dict of supplied data
        allnames : dict of supplied data names for plot legend
        plot_info : one of the predefined dicts from top of this file
        plotterData: dict with plotting info
        axis : which axis to plot (x, y, or both)
        plotErrors: bool for plotting errors."""
    def _getColumn(data, plot_info, n):
        variable = None
        variableError = None
        if isinstance(data, _pymadx.Data.Tfs):
            variable = plot_info["madx"][n]             # variable name from predefined dict
        if isinstance(data, _pybdsim.Data.BDSAsciiData):
            variable = plot_info["bdsimdata"][n]        # variable name from predefined dict
            variableError = plot_info["bdsimerror"][n]  # variable name from predefined dict
        return variable, variableError

    def _plot(firstData, secondData, plot_info, n, legLabel='', plotErrors=True, relativeData=None, **kwargs):
        firstColumn, firstColumnError = _getColumn(firstdata, plot_info, n)
        secondColumn, secondColumnError = _getColumn(seconddata, plot_info, n)
        relColumn, relColumnError = _getColumn(relativeData, plot_info, n)

        # no errors in tfs or ptctwiss output
        if (firstColumnError is None) or (secondColumnError is None):
            plotErrors = False
        # relative data supplied but it has no errors, i.e. is TFS data.
        if (relativeData is not None) and relColumnError is None:
            plotErrors = False

        firstvarError = None
        secondvarError = None

        # emittance is a number in the header for tfs or ptctwiss so convert to an array for plotting
        if (firstColumn == "EX") or (firstColumn == "EY"):
            firstvar = firstdata.header[firstColumn] * _np.ones(len(firstdata.GetColumn('S')))
        else:
            firstvar = firstdata.GetColumn(firstColumn)
            if plotErrors:
                firstvarError = firstdata.GetColumn(firstColumnError)
        if (secondColumn == "EX") or (secondColumn == "EY"):
            secondvar = seconddata.header[secondColumn] * _np.ones(len(seconddata.GetColumn('S')))
        else:
            secondvar = secondData.GetColumn(secondColumn)
            if plotErrors:
                secondvarError = secondData.GetColumn(secondColumnError)

        # residual data
        residData = firstvar - secondvar

        residDataError = None
        # now calculate relative data and statistical errors
        if relativeData is not None:
            if (relColumn == "EX") or (relColumn == "EY"):
                relvar = relativeData.header[relColumn] * _np.ones(len(relativeData.GetColumn('S')))
            else:
                relvar = relativeData.GetColumn(relColumn)

            # relative residuals
            residData /= relvar

            # from error propagation formulae: f = (a-b)/c
            # df**2 = (da**2 /c**2) + (db**2 /c**2) + (dc**2 /c**2)*((a**2 + b**2)/c**2)
            if plotErrors:
                relvarError = relativeData.GetColumn(relColumnError)
                residDataError2 = (firstvarError**2 + secondvarError**2 +
                                               (relvarError**2 * (firstvar**2 + secondvar**2)/relvar**2)) / relvar**2
                residDataError = _np.sqrt(residDataError2)
        else:
            if plotErrors:
                # from error propagation formulae: f = a-b
                # df**2 = da**2 + db**2
                residDataError = _np.sqrt(firstvarError**2 + secondvarError**2)

        if plotErrors:
            _plt.errorbar(firstData.GetColumn('S'),
                          residData,
                          yerr=residDataError,
                          label=legLabel)
        else:
            _plt.plot(firstData.GetColumn('S'), residData, label=legLabel)

    # get correct data and names
    firsttype = plotterData["firsttype"]
    secondtype = plotterData["secondtype"]

    firstdata = alldata[firsttype][0]
    firstname = allnames[firsttype][0]
    if firsttype == secondtype:
        seconddata = alldata[secondtype][1]
        secondname = allnames[secondtype][1]
    else:
        seconddata = alldata[secondtype][0]
        secondname = allnames[secondtype][0]
    name = firstname + " - " + secondname

    # get number particles. Check needed as number only available in bdsim type data
    if hasattr(firstdata,"Npart") and hasattr(seconddata,"Npart"):
        if firstdata.Npart()[0] != seconddata.Npart()[0]:
            numParticles = None
        else:
            numParticles= firstdata.Npart()[0]
    elif hasattr(firstdata,"Npart"):
        numParticles = firstdata.Npart()[0]
    elif hasattr(seconddata, "Npart"):
        numParticles = seconddata.Npart()[0]
    else:
        numParticles = None

    if numParticles is not None:
        legendLabel = "{}; N = {:.1E}".format(name, numParticles)
        xlegendLabel = "{}; {}; N = {:.1E}".format(name, plot_info["legend"][0], numParticles)
        ylegendLabel = "{}; {}; N = {:.1E}".format(name, plot_info["legend"][1], numParticles)
    else:
        legendLabel = name
        xlegendLabel = "{}; {}; ".format(name, plot_info["legend"][0])
        ylegendLabel = "{}; {}; ".format(name, plot_info["legend"][1])

    relativeData = None
    if len(alldata["rel"]) > 0:
        relativeData = alldata["rel"][0]

    if isinstance(firstdata, _pymadx.Data.Tfs) or isinstance(seconddata, _pymadx.Data.Tfs):
        plotErrors = False

    # plot specific axes according to tuple index in predefined dict. x = 0, y = 1
    if axis == 'x':
        _plot(firstdata, seconddata, plot_info, 0, legendLabel, plotErrors, relativeData, **kwargs)
    elif axis == 'y':
        _plot(firstdata, seconddata, plot_info, 1, legendLabel, plotErrors, relativeData, **kwargs)
    elif axis == 'both':
        _plot(firstdata, seconddata, plot_info, 0, xlegendLabel, plotErrors, relativeData, **kwargs)
        _plot(firstdata, seconddata, plot_info, 1, ylegendLabel, plotErrors, relativeData, **kwargs)

# use closure to avoid tonnes of boilerplate code
def _make_plotter(plot_info):
    """ plot_info : one of the predefined dicts from top of this file """

    def f_out(alldata, allnames, axis='both', plotterData=None, **kwargs):
        """ alldata  : dict of all data returned by _LoadData method
            allnames : dict of all names returned by _LoadData method
            axis     : which axis to plot (x, y, or both)
            plotterData : plotting config data
            """
        # extract plot labelling from predefined dict
        x_label = plot_info['xlabel']
        if axis == 'x':
            y_label = plot_info['ylabel'][1]
        elif axis == 'y':
            y_label = plot_info['ylabel'][2]
        else:
            y_label = plot_info['ylabel'][0]  # both

        title = plot_info['title'] + axis  # add axis to distinguish plot titles
        isResidualPlot = plotterData["isresidualplot"]
        figsize = plotterData["figsize"]
        survey = plotterData["survey"]
        saveFig = plotterData["savefig"]
        errors = plotterData["errors"]  # plot errorbars or not

        plot = _plt.figure(title, figsize, **kwargs)

        if isResidualPlot:
            _plotResiduals(alldata, allnames, plot_info, plotterData, axis, errors, **kwargs)
        else:
            # loop over data lists and plot using appropriate function
            for bdsimIndex, bdsimData in enumerate(alldata["bdsim"]):
                if bdsimData is not None:
                    _plotBdsimType(bdsimData, allnames["bdsim"][bdsimIndex], plot_info, axis, **kwargs)

            for madxIndex, madxData in enumerate(alldata["madx"]):
                if madxData is not None:
                    _plotMadxType(madxData, allnames["madx"][madxIndex], plot_info, axis, **kwargs)

            for ptctwissIndex, ptctwissData in enumerate(alldata["ptctwiss"]):
                if ptctwissData is not None:
                    _plotMadxType(ptctwissData, allnames["ptctwiss"][ptctwissIndex], plot_info, axis, **kwargs)

            for ptcIndex, ptcData in enumerate(alldata["ptc"]):
                if ptcData is not None:
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

        if saveFig:
            _plt.savefig(title+".pdf")

        return plot
    return f_out

PlotBeta   = _make_plotter(_BETA)
PlotAlpha  = _make_plotter(_ALPHA)
PlotDisp   = _make_plotter(_DISP)
PlotDispP  = _make_plotter(_DISP_P)
PlotSigma  = _make_plotter(_SIGMA)
PlotSigmaP = _make_plotter(_SIGMA_P)
PlotMean   = _make_plotter(_MEAN)
PlotMeanP  = _make_plotter(_MEAN_P)
PlotEmitt  = _make_plotter(_EMITT)


def _CompareOptics(bdsim=None, bdsimname=None,
                   tfs=None, tfsname=None,
                   ptctwiss=None, ptctwissname=None,
                   ptc=None, ptcname=None,
                   plotterData=None,
                   relativeTo=None):
    if (bdsim is None) and (tfs is None) and (ptctwiss is None) and (ptc is None):
        print("Nothing to compare.")
        return

    plotAxesSeparately = plotterData["plotaxesseparately"]
    kwargs = plotterData["kwargs"]

    # load data and get names
    data, names = _LoadData(bdsim, bdsimname, tfs, tfsname, ptctwiss, ptctwissname, ptc, ptcname, relativeTo=relativeTo)

    # check number of entries being compared.
    numBdsim    = len([x for x in data["bdsim"] if x is not None])
    numMadx     = len([x for x in data["madx"] if x is not None])
    numPtcTwiss = len([x for x in data["ptctwiss"] if x is not None])
    numPtc      = len([x for x in data["ptc"] if x is not None])
    total = numBdsim + numMadx + numPtc + numPtcTwiss

    # limit the amount of data shown.
    if total > 2:
        plotAxesSeparately = True  # if > 2, plot x and y separately.
        if plotterData["isresidualplot"]:
            print("Cannot show residuals for more than 2 files.")
            return
    if not plotterData["isresidualplot"] and total > 6:
        print("Too many files to compare")
        return

    # cannot calculate residuals if machines are different lengths
    if plotterData["isresidualplot"]:
        firsttype = plotterData["firsttype"]
        secondtype = plotterData["secondtype"]
        firstdata = data[firsttype][0]
        if firsttype == secondtype:
            seconddata = data[secondtype][1]
        else:
            seconddata = data[secondtype][0]
        if len(firstdata) != len(seconddata):
            print("First and second files have different lengths. Residuals cannot be calculated.")
            return

        # remove relative data if is not the same length as the residual data.
        if data['rel'][0] is not None:
            reldata = data['rel'][0]
            if len(reldata) != len(firstdata):
                print("Length of relative data is not equal to the residual data. Not plotting relative data.")
                data['rel'] = []

        # warn if number of initial primaries is different.
        if hasattr(firstdata, "Npart") and hasattr(seconddata, "Npart"):
            if firstdata.Npart()[0] != seconddata.Npart()[0]:
                print("Data has different number of particles in inital distribution.")

    # now plot the graphs
    if plotAxesSeparately:
        figures = [
        PlotBeta(data,   names, axis='x', plotterData=plotterData, **kwargs),
        PlotBeta(data,   names, axis='y', plotterData=plotterData, **kwargs),
        PlotAlpha(data,  names, axis='x', plotterData=plotterData, **kwargs),
        PlotAlpha(data,  names, axis='y', plotterData=plotterData, **kwargs),
        PlotDisp(data,   names, axis='x', plotterData=plotterData, **kwargs),
        PlotDisp(data,   names, axis='y', plotterData=plotterData, **kwargs),
        PlotDispP(data,  names, axis='x', plotterData=plotterData, **kwargs),
        PlotDispP(data,  names, axis='y', plotterData=plotterData, **kwargs),
        PlotSigma(data,  names, axis='x', plotterData=plotterData, **kwargs),
        PlotSigma(data,  names, axis='y', plotterData=plotterData, **kwargs),
        PlotSigmaP(data, names, axis='x', plotterData=plotterData, **kwargs),
        PlotSigmaP(data, names, axis='y', plotterData=plotterData, **kwargs),
        PlotMean(data,   names, axis='x', plotterData=plotterData, **kwargs),
        PlotMean(data,   names, axis='y', plotterData=plotterData, **kwargs),
        PlotMeanP(data,  names, axis='x', plotterData=plotterData, **kwargs),
        PlotMeanP(data,  names, axis='y', plotterData=plotterData, **kwargs),
        PlotEmitt(data,  names, axis='x', plotterData=plotterData, **kwargs),
        PlotEmitt(data,  names, axis='y', plotterData=plotterData, **kwargs),
        PlotNPart(data,  names, plotterData=plotterData, **kwargs)
            ]
    else:
        figures = [
        PlotBeta(data,   names, plotterData=plotterData, **kwargs),
        PlotAlpha(data,  names, plotterData=plotterData, **kwargs),
        PlotDisp(data,   names, plotterData=plotterData, **kwargs),
        PlotDispP(data,  names, plotterData=plotterData, **kwargs),
        PlotSigma(data,  names, plotterData=plotterData, **kwargs),
        PlotSigmaP(data, names, plotterData=plotterData, **kwargs),
        PlotMean(data,   names, plotterData=plotterData, **kwargs),
        PlotMeanP(data,  names, plotterData=plotterData, **kwargs),
        PlotEmitt(data,  names, plotterData=plotterData, **kwargs),
        PlotNPart(data,  names, plotterData=plotterData, **kwargs)
            ]

    # save the plots
    if plotterData["saveall"]:
        if plotterData["outputname"] is not None:
            output_filename = plotterData["outputname"]
        else:
            output_filename = "optics-report.pdf"

        with _PdfPages(output_filename) as pdf:
            for figure in figures:
                pdf.savefig(figure)
            d = pdf.infodict()
            d['Title'] = "Multi Code Optical Comparison"
            d['CreationDate'] = _datetime.datetime.today()
        print("Written ", output_filename)

def Optics(bdsim=None, bdsimname=None,
           tfs=None, tfsname=None,
           ptctwiss=None, ptctwissname=None,
           ptc=None, ptcname=None,
           survey=None, figsize=(9, 5),
           saveAll=True,
                  outputFilename=None,
           plotAxesSeparately=False,
           saveIndivFigs=False,
           **kwargs):
    """
    Compares optics of multiple files supplied. 

    pybdsim.Compare.Optics(bdsim="t1_optics.root",bdsimname="BDSIM", 
                           tfs="t1.tfs", tfsname="Madx Twiss",
                           ptctwiss="ptc_twiss.outx", ptctwissname="PTC Twiss",
                           ptc="ptc_optics.root", ptcname="PTC Track",
                           survey="bdsim_surv.dat', 
                           outputFilename="BDSIMVsTFSVsPTCTWISSVsPTCTRACK.pdf")

    pybdsim.Compare.Optics(bdsim=["t1_optics.root","t2_optics.root"],
                           bdsimname=["BDSIM 10 GeV","BDSIM 20 GeV"],
                                  tfs=["t1.tfs","t2.tfs"], tfsname=["TFS 10 GeV","TFS 20 GeV"],
                                  outputFilename="BDSIMVsTFS_10GeV20GeV.pdf")



    Can be any combination of single or multiple. BDSIM, Tfs, ptc_twiss output, 
    or PTC output (PTC output converted to BDSIM compatible format). Pymadx.Data.TFS 
    or pybdsim.Data.BDSAsciiData instances can also be supplied instead of filenames.

    Names can be supplied along with the filenames that will appear in the legend. 
    Multiple filenames can be supplied in a list. If the number of names is not equal 
    to the number of filenames, the supplied names will be ignored.

    Up to 6 files can be compared to one another.

    If up to 2 files are supplied, the optical functions for the x and y axes are plotted on the
    same figure.

    If more than 2 files are supplied, the optical functions for the x and y axes are plotted on
    seperate figures.

    +--------------------+---------------------------------------------------------+
    | **Parameters**     | **Description**                                         |
    +--------------------+---------------------------------------------------------+
    | bdsim              | Optics root file (from rebdsimOptics or rebdsim),       |
    |                    | or BDSAsciiData instance, or list of multiple root      |
    |                    | files or instances.                                     |
    |                    | default = None                                          |
    +--------------------+---------------------------------------------------------+
    | bdsimname          | bdsim name that will appear in the plot legend          |
    |                    | or list of multiple bdsim names.                        |
    |                    | default = None                                          |
    +--------------------+---------------------------------------------------------+
    | tfs                | Tfs file (or pymadx.Data.Tfs instance),                 |
    |                    | or list of multiple Tfs files or instances.             |
    |                    | default = None                                          |
    +--------------------+---------------------------------------------------------+
    | tfsname            | tfs name that will appear in the plot legend            |
    |                    | or list of multiple tfs names.                          |
    |                    | default = None                                          |
    +--------------------+---------------------------------------------------------+
    | ptctwiss           | ptctwiss output file (or pymadx.Data.Tfs instance),     |
    |                    | of list of multiple ptctwiss files or instances.        |
    |                    | default = None                                          |
    +--------------------+---------------------------------------------------------+
    | ptctwissname       | ptctwiss name that will appear in the plot legend       |
    |                    | or list of multiple ptctwiss names.                     |
    |                    | default = None                                          |
    +--------------------+---------------------------------------------------------+
    | ptc                | Optics root file (from rebdsimOptics or rebdsim) or     |
    |                    | BDSAsciiData instance that was generated with PTC data  |
    |                    | and has been converted to bdsim format via ptc2bdsim,   |
    |                    | or list of multiple files or instances.                 |
    |                    | default = None                                          |
    +--------------------+---------------------------------------------------------+
    | ptcname            | ptc name that will appear in the plot legend            |
    |                    | or list of multiple ptc names.                          |
    |                    | default = None                                          |
    +--------------------+---------------------------------------------------------+
    | survey             | BDSIM model survey.                                     |
    +--------------------+---------------------------------------------------------+
    | figsize            | Figure size for all figures - default is (9,5)          |
    +--------------------+---------------------------------------------------------+
    | saveAll            | Save all plots generated in a single pdf file           |
    |                    | default = True.                                         |
    +--------------------+---------------------------------------------------------+
    | outputFilename     | filename of generated plots.                            |
    |                    | default = optics-report.pdf                             |
    +--------------------+---------------------------------------------------------+
    | plotAxesSeparately | Plot x and y axes on separate plots                     |
    |                    | default = false                                         |
    +--------------------+---------------------------------------------------------+
    | saveIndivFigs      | Save each plot individually as PDF.                     |
    |                    | default = false                                         |
    +--------------------+---------------------------------------------------------+

    """

    # load once here to save loading for every plot
    if survey is not None:
        if isinstance(survey, str) and not _ospath.isfile(survey):
            raise IOError("Survey not found: ", survey)
        if CheckBdsimDataHasSurveyModel(survey):
            survey = _pybdsim.Data.Load(survey).model
        else:
            survey = CheckItsBDSAsciiData(survey)

    # pass in plotting config data in a dict to minimise number of args (which will only increase)
    plotterData = {"survey": survey,
                   "figsize": figsize,
                   "savefig": saveIndivFigs,
                   "errors": False,
                   "isresidualplot": False,
                   "saveall": saveAll,
                   "outputname": outputFilename,
                   "plotaxesseparately": plotAxesSeparately,
                   "kwargs": kwargs,
                   "firstdata": None,
                   "seconddata": None
                   }

    _CompareOptics(bdsim, bdsimname, tfs, tfsname, ptctwiss, ptctwissname, ptc, ptcname, plotterData=plotterData)


def OpticsResiduals(first=None, firstname=None,
                    second=None, secondname=None,
                    firsttype="",
                    secondtype="",
                    survey=None, figsize=(9, 5),
                    relativeTo=None,
                    saveAll=True,
                    includeErrors=False,
                    outputFilename=None,
                    plotAxesSeparately=False,
                    saveIndivFigs=False,
                    **kwargs):
    """
    pybdsim.Compare.OpticsResiduals(bdsim="t1_optics.root",bdsimname="BDSIM", 
                           tfs="t1.tfs", tfsname="Madx Twiss",
                           ptctwiss="ptc_twiss.outx", ptctwissname="PTC Twiss",
                           ptc="ptc_optics.root", ptcname="PTC Track",
                           survey="bdsim_surv.dat', 
                           outputFilename="BDSIMVsTFSVsPTCTWISSVsPTCTRACK.pdf")
    
    pybdsim.Compare.OpticsResiduals(bdsim=["t1_optics.root","t2_optics.root"],
                                    bdsimname=["BDSIM 10 GeV","BDSIM 20 GeV"],
                                    tfs=["t1.tfs","t2.tfs"], 
                                    tfsname=["TFS 10 GeV","TFS 20 GeV"],
                                    outputFilename="BDSIMVsTFS_10GeV20GeV.pdf")

    Compares absolute residual optics of multiple files supplied. Can be any 
    combination of single or multiple BDSIM, Tfs, ptc_twiss output, or PTC 
    output (PTC output converted to BDSIM compatible format). pymadx.Data.TFS 
    or pybdsim.Data.BDSAsciiData instances can also be supplied instead of filenames.

    Names can be supplied along with the filenames that will appear in the legend. 
    Multiple filenames can be supplied in a list. If the number of names is not 
    equal to the number of filenames, the supplied names will be ignored.

    The "type" of data must also be supplied to help distinguish the data type 
    and subsequent loading and processing. Must be one of "bdsim", "tfs", "ptctwiss", 
    or "ptc".

    The residuals will be the first data minus the second data. The residuals can 
    also be relative to a third data set supplied by the relativeTo argument. 
    This can be a filename or instance of a BDSIM, Tfs, ptc_twiss, or PTC output. 
    Errors are not plotted by default. If errors are desired, the errors plotted 
    are calculated from the supplied data (and relative data) using standard error 
    propagation to ensure they are statistically correct. If nothing is supplied 
    to the relativeTo arguments, the residuals are plotted as absolute.

    +--------------------+---------------------------------------------------------+
    | **Parameters**     | **Description**                                         |
    +--------------------+---------------------------------------------------------+
    | first              | Optics root file (from rebdsimOptics or rebdsim),       |
    |                    | BDSAsciiData instance, Tfs file, or pymadx.Data.Tfs     |
    |                    | instance.                                               |
    |                    | default = None                                          |
    +--------------------+---------------------------------------------------------+
    | firstname          | Name that will appear in the plot legend.               |
    |                    | default = None                                          |
    +--------------------+---------------------------------------------------------+
    | second             | Optics root file (from rebdsimOptics or rebdsim),       |
    |                    | BDSAsciiData instance, Tfs file, or pymadx.Data.Tfs     |
    |                    | instance.                                               |
    |                    | default = None                                          |
    +--------------------+---------------------------------------------------------+
    | secondname         | Name that will appear in the plot legend.               |
    |                    | default = None                                          |
    +--------------------+---------------------------------------------------------+
    | firstype           | Data type of first optics data, must be one of "bdsim", |
    |                    | "tfs", "ptctwiss", or "ptc".                            |
    |                    | default = ""                                            |
    +--------------------+---------------------------------------------------------+
    | secondtype         | Data type of second optics data, must be one of "bdsim",|
    |                    | "tfs", "ptctwiss", or "ptc".                            |
    |                    | default = ""                                            |
    +--------------------+---------------------------------------------------------+
    | survey             | BDSIM model survey.                                     |
    +--------------------+---------------------------------------------------------+
    | figsize            | Figure size for all figures - default is (9,5)          |
    +--------------------+---------------------------------------------------------+
    | relativeTo         | Optics data that the residuals will be plotted relative |
    |                    | to. Must be a root file (from rebdsimOptics or rebdsim),|
    |                    | BDSAsciiData instance, Tfs file, or pymadx.Data.Tfs     |
    |                    | instance.                                               |
    |                    | default = None                                          |
    +--------------------+---------------------------------------------------------+
    | saveAll            | Save all plots generated in a single pdf file           |
    |                    | default = True.                                         |
    +--------------------+---------------------------------------------------------+
    | includeErrors      | Include errors in the residual plots.                   |
    |                    | default = False                                         |
    +--------------------+---------------------------------------------------------+
    | outputFilename     | filename of generated plots.                            |
    |                    | default = optics-report.pdf                             |
    +--------------------+---------------------------------------------------------+
    | plotAxesSeparately | Plot x and y axes on separate plots                     |
    |                    | default = false                                         |
    +--------------------+---------------------------------------------------------+
    | saveIndivFigs      | Save each plot individually as PDF.                     |
    |                    | default = false                                         |
    +--------------------+---------------------------------------------------------+

    """

    # load once here to save loading for every plot
    if survey is not None:
        if isinstance(survey, str) and not _ospath.isfile(survey):
            raise IOError("Survey not found: ", survey)
        if CheckBdsimDataHasSurveyModel(survey):
            survey = _pybdsim.Data.Load(survey).model
        else:
            survey = CheckItsBDSAsciiData(survey)

    validtypes = ["bdsim", "tfs", "ptctwiss", "ptc"]

    if firsttype not in validtypes:
        print('Unrecognised data type for first data, must be one of: "bdsim" "tfs" "ptctwiss" or "ptc"')
        return
    if secondtype not in validtypes:
        print('Unrecognised data type for second data, must be one of: "bdsim" "tfs" "ptctwiss" or "ptc"')
        return

    bdsim=[]; bdsimname=[]; tfs=[]; tfsname=[]; ptctwiss=[]; ptctwissname=[]; ptc=[]; ptcname=[]
    if firsttype == "bdsim":
        bdsim.append(first)
        bdsimname.append(firstname)
    if firsttype == "tfs":
        tfs.append(first)
        tfsname.append(firstname)
    if firsttype == "ptctwiss":
        ptctwiss.append(first)
        ptctwissname.append(firstname)
    if firsttype == "ptc":
        ptc.append(first)
        ptcname.append(firstname)
    if secondtype == "bdsim":
        bdsim.append(second)
        bdsimname.append(secondname)
    if secondtype == "tfs":
        tfs.append(second)
        tfsname.append(secondname)
    if secondtype == "ptctwiss":
        ptctwiss.append(second)
        ptctwissname.append(secondname)
    if secondtype == "ptc":
        ptc.append(second)
        ptcname.append(secondname)

    # switch data type to madx as it is used later instead of tfs in the loading methods
    if firsttype == 'tfs':
        firsttype = 'madx'
    if secondtype == 'tfs':
        secondtype = 'madx'

    # pass in plotting config data in a dict to minimise number of args (which will only increase)
    plotterData = {"survey": survey,
                   "figsize": figsize,
                   "savefig": saveIndivFigs,
                   "errors": includeErrors,
                   "isresidualplot": True,
                   "saveall": saveAll,
                   "outputname": outputFilename,
                   "plotaxesseparately": plotAxesSeparately,
                   "kwargs": kwargs,
                   "firsttype": firsttype,
                   "secondtype": secondtype}

    _CompareOptics(bdsim, bdsimname, tfs, tfsname, ptctwiss, ptctwissname, ptc, ptcname,
                   plotterData=plotterData, relativeTo=relativeTo)

def PlotNPart(data, names, plotterData=None, **kwargs):
    """ Method for plotting the number of particles.
        Separate as only applicable to BDSIM/PTC type files.
        """
    figsize = plotterData["figsize"]
    survey = plotterData["survey"]
    saveFig = plotterData["savefig"]

    if (len(data["bdsim"]) == 0) and (len(data["ptc"]) == 0):
        print("Data provided does not contain a particle count. Not plotting Npart comparison.")
        return

    npartPlot = _plt.figure('NParticles', figsize, **kwargs)
    try:
        if data["bdsim"][0] is not None:
            for i in range(len(data["bdsim"])):
                bdsimdata = data["bdsim"][i]
                bdsimname = names["bdsim"][i]
                _plt.plot(bdsimdata.GetColumn('S'), bdsimdata.GetColumn('Npart'), 'k-', label="{};".format(bdsimname))
        if data["ptc"][0] is not None:
            for i in range(len(data["ptc"])):
                ptcdata = data["ptc"][i]
                ptcname = names["ptc"][i]
                if ptcdata is not None:
                    _plt.plot(ptcdata.GetColumn('S'), ptcdata.GetColumn('Npart'), 'kx', label="{};".format(ptcname))
    except AttributeError:
        pass

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

    if saveFig:
        _plt.savefig("NPart" + ".pdf")

    return npartPlot
