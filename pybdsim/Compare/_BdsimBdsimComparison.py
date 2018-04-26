"""
Functions for comparing the optical distributions of two
BDSIM models.

Functions for plotting the individual optical functions, and an
eighth, helper function ''compare_all_optics``, to plot display all
seven in one go.
"""

import datetime as _datetime
import matplotlib.pyplot as _plt
from matplotlib.backends.backend_pdf import PdfPages as _PdfPages
import os.path as _path

import pybdsim.Data
import pybdsim.Plot

# Predefined lists of tuples for making the standard plots,
# format = (optical_var_name, optical_var_error_name, legend_name)

_BETA = [("Beta_x", "Sigma_Beta_x", r'$\beta_{x}$'),
         ("Beta_y", "Sigma_Beta_y", r'$\beta_{y}$')]

_ALPHA = [("Alpha_x", "Sigma_Alpha_x", r"$\alpha_{x}$"),
          ("Alpha_y", "Sigma_Alpha_y", r"$\alpha_{y}$")]

_DISP = [("Disp_x", "Sigma_Disp_x", r"$D_{x}$"),
         ("Disp_y", "Sigma_Disp_y", r"$D_{y}$")]

_DISP_P = [("Disp_xp", "Sigma_Disp_xp", r"$D_{p_{x}}$"),
           ("Disp_yp", "Sigma_Disp_yp", r"$D_{p_{y}}$")]

_SIGMA = [("Sigma_x", "Sigma_Sigma_x", r"$\sigma_{x}$"),
          ("Sigma_y", "Sigma_Sigma_y", r"$\sigma_{y}$")]

_SIGMA_P = [("Sigma_xp", "Sigma_Sigma_xp", r"$\sigma_{xp}$"),
            ("Sigma_yp", "Sigma_Sigma_yp", r"$\sigma_{yp}$")]

_MEAN = [("Mean_x", "Sigma_Mean_x", r"$\bar{x}$"),
         ("Mean_y", "Sigma_Mean_y", r"$\bar{y}$")]

def _parse_bdsim_input(bdsim_in, name):
   """Return bdsim_in as a BDSAsciiData instance, which should either
   be a path to a BDSIM root output file, rebdsimOptics output file,
   or a BDSAsciiData instance, and in either case, generate a
   name if None is provided, and return that as well."""
   if isinstance(bdsim_in, basestring):
       if not _path.isfile(bdsim_in):
           raise IOError("file \"{}\" not found!".format(bdsim_in))
       name = (_path.splitext(_path.basename(bdsim_in))[0]
               if name is None else name)
       return pybdsim.Data.Load(bdsim_in).optics, name
   try:
       if isinstance(bdsim_in, pybdsim.Data.RebdsimFile):
           bdsim_in = bdsim_in.optics
       name = bdsim_in.filename if name is None else name
       return bdsim_in, name
   except AttributeError:
       raise TypeError(
           "Expected Tfs input is neither a "
           "file path nor a Tfs instance: {}".format(tfs_in))

# use closure to avoid tonnes of boilerplate code as happened with
# MadxBdsimComparison.py
def _make_plotter(plot_info_tuples, x_label, y_label, title):
    def f_out(first, second, first_name=None, second_name=None,
              survey=None, **kwargs):

        # Get the initial N for the two sources
        first_nparticles = first.Npart()[0]
        second_nparticles = second.Npart()[0]

        plot = _plt.figure(title, figsize=(9,5), **kwargs)
        # Loop over the variables in plot_info_tuples and draw the plots.
        for var, error, legend_name in plot_info_tuples:
            _plt.errorbar(first.GetColumn('S'),
                          first.GetColumn(var),
                          yerr=first.GetColumn(error),
                          label="{}; {}; N = {:.1E}".format(
                              first_name, legend_name, first_nparticles),
                          capsize=3, **kwargs)
            _plt.errorbar(second.GetColumn('S'),
                          second.GetColumn(var),
                          yerr=second.GetColumn(error),
                          label="{}; {}; N = {:.1E}".format(
                              second_name, legend_name, second_nparticles),
                          capsize=3, **kwargs)

        # Set axis labels and draw legend
        axes = _plt.gcf().gca()
        axes.set_ylabel(y_label)
        axes.set_xlabel(x_label)
        axes.legend(loc='best')

        if survey is not None:
            try:
                pybdsim.Plot.AddMachineLatticeFromSurveyToFigure(_plt.gcf(), survey)
            except IOError:
                pybdsim.Plot.AddMachineLatticeToFigure(_plt.gcf(), survey)
        _plt.show(block=False)
        return plot
    return f_out

PlotBeta   = _make_plotter(_BETA,    "S / m", r"$\beta_{x,y}$ / m",      "Beta")
PlotAlpha  = _make_plotter(_ALPHA,   "S / m", r"$\alpha_{x,y}$ / m",     "Alpha")
PlotDisp   = _make_plotter(_DISP,    "S / m", r"$D_{x,y} / m$",          "Dispersion")
PlotDispP  = _make_plotter(_DISP_P,  "S / m", r"$D_{p_{x},p_{y}}$ / m",  "Momentum_Dispersion")
PlotSigma  = _make_plotter(_SIGMA,   "S / m", r"$\sigma_{x,y}$ / m",     "Sigma")
PlotSigmaP = _make_plotter(_SIGMA_P, "S / m", r"$\sigma_{xp,yp}$ / rad", "SigmaP")
PlotMean   = _make_plotter(_MEAN,    "S / m", r"$\bar{x}, \bar{y}$ / m", "Mean")


def BDSIMVsBDSIM(first, second, first_name=None,
                 second_name=None, survey=None, saveAll=True, 
                 outputFileName=None, **kwargs):
    """
    Display all the optical function plots for the two input optics files.
    """
    first, first_name = _parse_bdsim_input(first, first_name)
    second, second_name = _parse_bdsim_input(second, second_name)

    first = pybdsim.Data.Load(first).optics
    second = pybdsim.Data.Load(second).optics

    figures = [
    PlotBeta(first, second, first_name=first_name,
             second_name=second_name, survey=survey, **kwargs),
    PlotAlpha(first, second, first_name=first_name,
              second_name=second_name, survey=survey, **kwargs),
    PlotDisp(first, second, first_name=first_name,
             second_name=second_name, survey=survey, **kwargs),
    PlotDispP(first, second, first_name=first_name,
              second_name=second_name, survey=survey, **kwargs),
    PlotSigma(first, second, first_name=first_name,
              second_name=second_name, survey=survey, **kwargs),
    PlotSigmaP(first, second, first_name=first_name,
               second_name=second_name, survey=survey, **kwargs),
    PlotMean(first, second, first_name=first_name,
             second_name=second_name, survey=survey, **kwargs),
        ]

    if saveAll:
        if outputFileName is not None:
            output_filename = outputFileName
        else:
            output_filename = "optics-report.pdf"

        with _PdfPages(output_filename) as pdf:
            for figure in figures:
                pdf.savefig(figure)
            d = pdf.infodict()
            d['Title'] = "{} VS {} Optical Comparison".format(first_name, second_name)
            d['CreationDate'] = _datetime.datetime.today()
        print "Written ", output_filename

def PTCVsBDSIM(first, second, first_name="PTC",
               second_name="BDSIM", survey=None, saveAll=True, 
               outputFileName=None, **kwargs):
    BDSIMVsBDSIM(first, second, first_name, second_name, survey, **kwargs)
