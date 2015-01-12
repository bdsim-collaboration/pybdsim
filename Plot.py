#pybdsim plotting tools
# Version 1.0
# L. Nevay, S.T.Boogert
# laurie.nevay@rhul.ac.uk

"""
Useful plots for bdsim output

"""
import Data as _Data
import pymadx as _pymadx
import pymadx._General

import matplotlib as _matplotlib
import matplotlib.pyplot as _plt
import matplotlib.patches as _patches
import numpy as _np


def MadxTfsBetaSimple(tfsfile, title='', outputfilename=None):
    _pymadx.Plot.PlotTfsBetaSimple(tfsfile,title,outputfilename)

def MadxTfsBeta(tfsfile, title='', outputfilename=None):
    _pymadx.Plot.PlotTfsBeta(tfsfile,title,outputfilename)

def MadxGmadComparison(tfsfile, gmadfile, title='', outputfilename=None):
    pass

def AddMachineLatticeToFigure(figure,tfsfile):
    _pymadx.Plot.AddMachineLatticeToFigure(figure,tfsfile)

def CompareBDSIMSurveyWithMadXTfs(tfsfile, bdsfile, title='', outputfilename=None):
    bds  = _Data.Load(bdsfile)
    tfs  = _pymadx._General.CheckItsTfs(tfsfile)
    tfsd = _pymadx.Plot._GetOpticalDataFromTfs(tfs)
    smax = tfs.smax

    #X
    f1   = _plt.figure(figsize=(11,5))
    axx  = f1.add_subplot(111)
    axx.plot(tfsd['s'],_np.sqrt(tfsd['betx']),'b-', label='MADX')
    axx.plot(bds.S(),_np.sqrt(bds.Beta_x()),'g-', label='BDSIM')
    axx.set_xlabel('S (m)')
    axx.set_ylabel(r'$\sqrt{\beta_{x}}$ ($\sqrt{\mathrm{m}}$)')
    axx.legend(loc=2,fontsize='small') #best position
    AddMachineLatticeToFigure(f1,tfs)
    _plt.suptitle("X")

    if outputfilename != None:
        if '.' in outputfilename:
            outputfilename = outputfilename.split('.')[0]
        _plt.savefig(outputfilename+'.pdf')
        _plt.savefig(outputfilename+'.png')

    #Y
    f2   = _plt.figure(figsize=(11,5))
    axy  = f2.add_subplot(111)
    axy.plot(tfsd['s'],_np.sqrt(tfsd['bety']),'b-', label='MADX')
    axy.plot(bds.S(),_np.sqrt(bds.Beta_y()),'g-', label='BDSIM')
    axy.set_xlabel('S (m)')
    axy.set_ylabel(r'$\sqrt{\beta_{y}}$ ($\sqrt{\mathrm{m}}$)')
    axy.legend(loc=2,fontsize='small') #best position
    AddMachineLatticeToFigure(f2,tfs)
    _plt.suptitle("Y")

    if outputfilename != None:
        if '.' in outputfilename:
            outputfilename = outputfilename.split('.')[0]
        _plt.savefig(outputfilename+'.pdf')
        _plt.savefig(outputfilename+'.png')
    

#archived - needs updating to new data structures
def _ControlPlot(datadict,title):
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
