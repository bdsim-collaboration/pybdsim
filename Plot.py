#pybdsim plotting tools
# Version 1.0
# L. Nevay, S.T.Boogert
# laurie.nevay@rhul.ac.uk

"""
Useful plots for bdsim output


"""


import matplotlib.pyplot as _plt
import numpy as _np

def PlotY(y,xlabel,ylabel,title):
    _plt.figure()
    if len(x) > 1000:
        _plt.plot(x,y,',')
    else:
        _plt.plot(x,y,'.')
    _plt.xlabel(xlabel)
    _plt.ylabel(ylabel)
    _plt.title(title)
    return f

def PlotXY(x,y,xlabel,ylabel,title):
    f = _plt.figure()
    if len(x) > 1000:
        _plt.plot(x,y,',')
    else:
        _plt.plot(x,y,'.')
    _plt.xlabel(xlabel)
    _plt.ylabel(ylabel)
    _plt.title(title)
    _plt.grid()
    return f

def PlotXYFixedAspectRation(x,y,xlabel,ylabel,title):
    f  = _plt.figure()
    ax = f.add_subplot(111)
    if len(x) > 1000:
        _plt.plot(x,y,',')
    else:
        _plt.plot(x,y,'.')
    ax.plot(x,y,'.')
    ax.set_aspect('equal')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    _plt.grid()
    return f

def ControlPlot(datadict,title):
    f = _plt.figure()
    d = datadict
    xmax = len(d['X'])

    ax1 = f.add_subplot(321)
    ax1.plot(d['X'],',',ms=0.5)
    ax1.set_ylabel('X (m)')
    ax1.set_xlim(0,xmax)
    _plt.setp(ax1.get_xticklabels(), visible=False)

    ax2 = f.add_subplot(322)
    ax2.plot(d['Xp'],',')
    ax2.set_ylabel('Xp (rad)')
    ax2.set_xlim(0,xmax)
    _plt.setp(ax2.get_xticklabels(), visible=False)

    ax3 = f.add_subplot(323)
    ax3.plot(d['Y'],',')
    ax3.set_ylabel('Y (m)')
    ax3.set_xlim(0,xmax)
    _plt.setp(ax3.get_xticklabels(), visible=False)

    ax4 = f.add_subplot(324)
    ax4.plot(d['Yp'],',')
    ax4.set_ylabel('Yp (rad)')
    ax4.set_xlim(0,xmax)
    _plt.setp(ax4.get_xticklabels(), visible=False)

    ax5 = f.add_subplot(325)
    ax5.plot(d['E'],',')
    ax5.set_ylabel('E (GeV)')
    ax5.set_xlim(0,xmax)
    _plt.setp(ax5.get_xticklabels(), visible=False)

    ax6 = f.add_subplot(326)
    ax6.plot(d['Z'],',')
    ax6.set_ylabel('Z (m)')
    ax6.set_xlim(0,xmax)
    _plt.setp(ax6.get_xticklabels(), visible=False)

    _plt.subplots_adjust(wspace=0.35,right=0.95,left=0.09)
    f.suptitle(title)
    return f

def Histogram(x,xlabel,title,nbins,**kwargs):
    f = _plt.figure()
    _plt.hist(x,nbins,histtype='step',**kwargs)
    _plt.xlabel(xlabel)
    _plt.title(title)
    return f
