import numpy as _np
import matplotlib as _matplotlib
import matplotlib.pyplot as _plt
import matplotlib.patches as _patches
import warnings as _warnings
import pymad8 as _m8


class _My_Axes(_matplotlib.axes.Axes):
    """
    | Inherit matplotlib.axes.Axes but override pan action for mouse.
    | Only allow horizontal panning - useful for lattice axes.
    """
    name = "_My_Axes"

    def drag_pan(self, button, key, x, y):
        _matplotlib.axes.Axes.drag_pan(self, button, 'x', x, y)  # pretend key=='x'


_matplotlib.projections.register_projection(_My_Axes)


def AddMachineLatticeToFigure(figure, mad8opt, fraction=0.9, tightLayout=True, sConvention='end'):
    """
    | Add a diagram above the current graph in the figure that represents the accelerator based on a mad8 twiss file.
    |
    | Note you can use matplotlib's gcf() 'get current figure' as an argument.
    |
    | >>> pymad8.Plot.AddMachineLatticeToFigure(gcf(), '/mad8_twiss_tape')
    """    

    axs = figure.get_axes()  # get existing graph

    axoptics = figure.get_axes()[0]
    _AdjustExistingAxes(figure, tightLayout=tightLayout, fraction=fraction)
    axmachine = _PrepareMachineAxes(figure)

    _DrawMachineLattice(axmachine, mad8opt, sConvention=sConvention)

    # put callbacks for linked scrolling 
    def MachineXlim(ax):
        axmachine.set_autoscale_on(True)
        axoptics.set_xlim(axmachine.get_xlim())

    def Click(a):
        if a.button == 3:
            try:
                print(a.xdata, mad8opt.getNameByNearestS(a.xdata))
            except ValueError:
                pass  # don't complain if the S is out of bounds

    MachineXlim(axmachine)
    axmachine.callbacks.connect('xlim_changed', MachineXlim)
    figure.canvas.mpl_connect('button_press_event', Click)


def _PrepareMachineAxes(figure):
    # create new machine axis with proportions 6 : 1
    axmachine = figure.add_subplot(911, projection="_My_Axes")
    axmachine.set_facecolor('none')  # make background transparent to allow scientific notation
    _SetMachineAxesStyle(axmachine)
    return axmachine


def _AdjustExistingAxes(figure, fraction=0.9, tightLayout=True):
    """
    | Fraction is fraction of height all subplots will be after adjustment.
    | Default is 0.9 for 90% of height.
    """
    # we have to set tight layout before adjustment otherwise if called
    # later it will cause an overlap with the machine diagram
    if tightLayout:
        _plt.tight_layout()

    axs = figure.get_axes()

    for ax in axs:
        bbox = ax.get_position()
        bbox.y0 = bbox.y0 * fraction
        bbox.y1 = bbox.y1 * fraction
        ax.set_position(bbox)


def _SetMachineAxesStyle(ax):
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)


def _DrawMachineLattice(axesinstance, mad8opt, sConvention='end'):
    ax = axesinstance

    match sConvention:
        case 'end':
            s_conv_factor = 1
        case 'middle':
            s_conv_factor = 0.5
        case 'start':
            s_conv_factor = 0
        case _:
            s_conv_factor = 1

    def DrawBend(e, color='b', alpha=1.0):
        br = _patches.Rectangle((e['S']-s_conv_factor*e['L'], -0.1), e['L'], 0.2, color=color, alpha=alpha)
        ax.add_patch(br)

    def DrawQuad(e, color='r', alpha=1.0):
        if e['K1'] > 0:
            qr = _patches.Rectangle((e['S']-s_conv_factor*e['L'], 0), e['L'], 0.2, color=color, alpha=alpha)
        elif e['K1'] < 0:
            qr = _patches.Rectangle((e['S']-s_conv_factor*e['L'], -0.2), e['L'], 0.2, color=color, alpha=alpha)
        else:
            # quadrupole off
            qr = _patches.Rectangle((e['S']-s_conv_factor*e['L'], -0.1), e['L'], 0.2, color='#B2B2B2', alpha=0.5)  # a nice grey in hex
        ax.add_patch(qr)

    def DrawHex(e, color, alpha=1.0):
        s = e['S']-s_conv_factor*e['L']
        l = e['L']
        edges = _np.array([[s, -0.1], [s, 0.1], [s+l/2., 0.13], [s+l, 0.1], [s+l, -0.1], [s+l/2., -0.13]])
        sr = _patches.Polygon(edges, color=color, fill=True, alpha=alpha)
        ax.add_patch(sr)

    def DrawRect(e, color, alpha=1.0):
        rect = _patches.Rectangle((e['S']-s_conv_factor*e['L'], -0.1), e['L'], 0.2, color=color, alpha=alpha)
        ax.add_patch(rect)

    def DrawLine(e, color, alpha=1.0):
        ax.plot([e['S']-s_conv_factor*e['L'], e['L']-e['L']], [-0.2, 0.2], '-', color=color, alpha=alpha)

    ax.plot([mad8opt.sMin(), mad8opt.sMax()], [0, 0], 'k-', lw=1)
    ax.set_ylim(-0.2, 0.2)

    # loop over elements 
    for i in range(0, mad8opt.nrec):
        e = mad8opt.getRowsByIndex(i)

        if e['TYPE'] == 'QUAD': DrawQuad(e, u'#d10000')  # red
        elif e['TYPE'] == 'RBEN': DrawBend(e, u'#0066cc')  # blue
        elif e['TYPE'] == 'SBEN': DrawBend(e, u'#0066cc')  # blue
        elif e['TYPE'] == 'KICK': DrawRect(e, u'#4c33b2')
        elif e['TYPE'] == 'HKIC': DrawRect(e, u'#4c33b2')  # purple
        elif e['TYPE'] == 'VKIC': DrawRect(e, u'#ba55d3')
        elif e['TYPE'] == 'RCOL': DrawRect(e, 'k')
        elif e['TYPE'] == 'ECOL': DrawRect(e, 'k')
        elif e['TYPE'] == 'SEXT': DrawHex(e, u'#ffcc00')
        elif e['TYPE'] == 'OCTU': DrawHex(e, u'#00994c')  # green
        elif e['TYPE'] == 'LCAV': DrawRect(e, u'#000000', 0.1)
        elif e['TYPE'] == 'SOLE': DrawRect(e, u'#000000', 0.1)
        elif e['TYPE'] == 'MATR':
            if e['L'] != 0:
                DrawRect(e, u'#000000', 0.1)
        elif e['TYPE'] == 'DRIF': pass
        elif e['TYPE'] == 'MONI': pass
        elif e['TYPE'] == 'MARK': pass
        else:
            pass
            # print 'not drawn',e['type']


class Optics:
    """
    | Class to load pymad8 DataFrames and make optics plots
    | >>> plot_data = pymad8.Plot.Optics('/mad8_twiss_tape')
    | >>> plot_data.Betas()
    |
    | Plot avaliable are plotBetas, plotAlphas, plotMus, plotDisp and plotSigmas
    """

    def __init__(self, mad8file, beamParams=None):
        """
        Load from form the two filenames both the twiss files and
        the twiss DataFrame and save them as internal variables.

        Also match the positions from the two lines with respect to the LUXE IP
        """
        self.mad8_data = _m8.Output(mad8file)
        self.beamParams = beamParams

    def Beta(self):
        """Plot the Beta functions for both planes and both Mad"""
        _plt.figure(figsize=(10, 6))

        self.mad8_data.plotXY('S', 'BETX')
        self.mad8_data.plotXY('S', 'BETY')
        _plt.xlabel('S [m]')
        _plt.ylabel('Beta [m]')
        _plt.legend()

        _m8.Plot.AddMachineLatticeToFigure(_plt.gcf(), self.mad8_data)
        _plt.show()

    def Alpha(self):
        """Plot the Alpha functions for both planes and both Mad"""
        _plt.figure(figsize=(10, 6))

        self.mad8_data.plotXY('S', 'ALPHX')
        self.mad8_data.plotXY('S', 'ALPHY')
        _plt.xlabel('S [m]')
        _plt.ylabel('Alpha [rad]')
        _plt.legend()

        _m8.Plot.AddMachineLatticeToFigure(_plt.gcf(), self.mad8_data)
        _plt.show()

    def Mu(self):
        """Plot the Mu functions for both planes and both Mad"""
        _plt.figure(figsize=(10, 6))

        self.mad8_data.plotXY('S', 'MUX')
        self.mad8_data.plotXY('S', 'MUY')
        _plt.xlabel('S [m]')
        _plt.ylabel('Mu [?]')
        _plt.legend()

        _m8.Plot.AddMachineLatticeToFigure(_plt.gcf(), self.mad8_data)
        _plt.show()

    def Disp(self):
        """Plot the Dispertion functions for both planes and both Mad"""
        _plt.figure(1, figsize=(10, 6))

        self.mad8_data.plotXY('S', 'DX')
        self.mad8_data.plotXY('S', 'DY')
        _plt.xlabel('S [m]')
        _plt.ylabel('Disp [m]')
        _plt.legend()

        _m8.Plot.AddMachineLatticeToFigure(_plt.gcf(), self.mad8_data)

        _plt.figure(2, figsize=(10, 6))

        self.mad8_data.plotXY('S', 'DPX')
        self.mad8_data.plotXY('S', 'DPY')
        _plt.xlabel('S [m]')
        _plt.ylabel('Disp_p [rad]')
        _plt.legend()

        _m8.Plot.AddMachineLatticeToFigure(_plt.gcf(), self.mad8_data)
        _plt.show()

    def Sigma(self):
        """Plot the beam size and beam divergence functions for both planes and both Mad"""
        if self.beamParams is None:
            _warnings.warn("No beam parameters provided.  Using default values.")
            self.mad8_data.calcBeamSize(3.58 * 10 ** -11, 3.58 * 10 ** -11, 1 * 10 ** -6)
        else:
            self.mad8_data.calcBeamSize(self.beamParams['ex'], self.beamParams['ey'], self.beamParams['esprd'])

        _plt.figure(1, figsize=(10, 6))

        self.mad8_data.plotXY('S', 'SIGX')
        self.mad8_data.plotXY('S', 'SIGY')
        _plt.xlabel('S [m]')
        _plt.ylabel('Sigma [m]')
        _plt.legend()

        _m8.Plot.AddMachineLatticeToFigure(_plt.gcf(), self.mad8_data)

        _plt.figure(2, figsize=(10, 6))

        self.mad8_data.plotXY('S', 'SIGXP')
        self.mad8_data.plotXY('S', 'SIGYP')
        _plt.xlabel('S [m]')
        _plt.ylabel('Sigma_p [rad]')
        _plt.legend()

        _m8.Plot.AddMachineLatticeToFigure(_plt.gcf(), self.mad8_data)
        _plt.show()
