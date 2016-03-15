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

from _General import CheckItsBDSAsciiData

class _My_Axes(_matplotlib.axes.Axes):
    """
    Inherit matplotlib.axes.Axes but override pan action for mouse.
    Only allow horizontal panning - useful for lattice axes.
    """
    name = "_My_Axes"
    def drag_pan(self, button, key, x, y):
        _matplotlib.axes.Axes.drag_pan(self, button, 'x', x, y) # pretend key=='x'

#register the new class of axes
_matplotlib.projections.register_projection(_My_Axes)

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
    

def AddMachineLatticeFromSurveyToFigure(figure,surveyfile):
    sf  = CheckItsBDSAsciiData(surveyfile) #load the machine description

    axs = figure.get_axes() #get the existing graph
    axoptics = axs[0]  #get the only presumed axes from the figure

    #adjust existing plot to make way for machine lattice
    #iterate over axes incase there's dual plots
    gs = _plt.GridSpec(2,1,height_ratios=(1,5))
    for ax in axs:
        ax.set_position(gs[1].get_position(figure))
        ax.set_subplotspec(gs[1])

    #add new axes for machine lattice
    axmachine = figure.add_subplot(gs[0], projection="_My_Axes")
    axmachine.get_xaxis().set_visible(False)
    axmachine.get_yaxis().set_visible(False)
    axmachine.spines['top'].set_visible(False)
    axmachine.spines['bottom'].set_visible(False)
    axmachine.spines['left'].set_visible(False)
    axmachine.spines['right'].set_visible(False)
    figure.set_facecolor('white')
    _plt.subplots_adjust(hspace=0.01,top=0.94,left=0.1,right=0.92)

    #generate the machine lattice plot
    _DrawMachineLattice(axmachine,sf)
    xl = axmachine.get_xlim()
    xr = xl[1] - xl[0]
    axoptics.set_xlim(xl[0]-0.02*xr,xl[1]+0.02*xr)
    axmachine.set_xlim(xl[0]-0.02*xr,xl[1]+0.02*xr)

    #put callbacks for linked scrolling
    def MachineXlim(ax): 
        axmachine.set_autoscale_on(False)
        axoptics.set_xlim(axmachine.get_xlim())

    def Click(a) : 
        if a.button == 3 : 
            print 'Closest element: ',sf.NameFromNearestS(a.xdata)

    axmachine.callbacks.connect('xlim_changed', MachineXlim)
    figure.canvas.mpl_connect('button_press_event', Click)

def _DrawMachineLattice(axesinstance,bdsasciidataobject):
    ax  = axesinstance #handy shortcut
    bds = bdsasciidataobject

    if not hasattr(bds,"SStart"):
        raise ValueError("This file doesn't have the required column SStart")
    if not hasattr(bds,"Arc_len"):
        raise ValueError("This file doesn't have the required column Arc_len")
    
    def DrawBend(start,length,color='b',alpha=1.0):
        br = _patches.Rectangle((start,-0.1),length,0.2,color=color,alpha=alpha)
        ax.add_patch(br)
    def DrawHKicker(start, length, color='purple', alpha=1.0):
        br = _patches.Rectangle((start,-0.1),length,0.2,color=color,alpha=alpha)
        ax.add_patch(br)
    def DrawVKicker(start, length, color='magenta', alpha=1.0):
        br = _patches.Rectangle((start,-0.1),length,0.2,color=color,alpha=alpha)
        ax.add_patch(br)
    def DrawQuad(start,length,k1l,color='r',alpha=1.0):
        #survey file doesn't have k values
        if k1l > 0 :
            qr = _patches.Rectangle((start,0),length,0.2,color=color,alpha=alpha)
        elif k1l < 0: 
            qr = _patches.Rectangle((start,-0.2),length,0.2,color=color,alpha=alpha)
        else:
            #quadrupole off
            qr = _patches.Rectangle((start,-0.1),length,0.2,color='#B2B2B2',alpha=0.5) #a nice grey in hex
        ax.add_patch(qr)
    def DrawHex(start,length,color,alpha=1.0):
        s = start
        l = length
        edges = _np.array([[s,-0.1],[s,0.1],[s+l/2.,0.13],[s+l,0.1],[s+l,-0.1],[s+l/2.,-0.13]])
        sr = _patches.Polygon(edges,color=color,fill=True,alpha=alpha)
        ax.add_patch(sr)
    def DrawRect(start,length,color,alpha=1.0):
        rect = _patches.Rectangle((start,-0.1),length,0.2,color=color,alpha=alpha)
        ax.add_patch(rect)
    def DrawLine(start,color,alpha=1.0):
        ax.plot([start,start],[-0.2,0.2],'-',color=color,alpha=alpha)
            
    # plot beam line
    smax = bds.SEnd()[-1]
    ax.plot([0,smax],[0,0],'k-',lw=1)
    ax.set_ylim(-0.5,0.5)
 
    # loop over elements and Draw on beamline
    types   = bds.Type()
    lengths = bds.Arc_len()
    starts  = bds.SStart()
    k1      = bds.K1()
    for i in range(len(bds)):
        kw = types[i]
        if kw == 'quadrupole': 
            DrawQuad(starts[i],lengths[i],k1[i])
        elif kw == 'rbend': 
            DrawBend(starts[i],lengths[i])
        elif kw == 'sbend': 
            DrawBend(starts[i],lengths[i])
        elif kw == 'rcol': 
            DrawRect(starts[i],lengths[i],'k')
        elif kw == 'ecol': 
            DrawRect(starts[i],lengths[i],'k')
        elif kw == 'degrader': 
            DrawRect(starts[i],lengths[i],'k')
        elif kw == 'sextupole':
            DrawHex(starts[i],lengths[i],'#ffcf17') #yellow
        elif kw == 'octupole':
            DrawHex(starts[i],lengths[i],'g')
        elif kw == 'hkick':
            DrawHKicker(starts[i],lengths[i])
        elif kw == 'vkick':
            DrawVKicker(starts[i],lengths[i])
        elif kw == 'drift':
            pass
        elif kw == 'multipole':
            DrawHex(starts[i],lengths[i],'grey',alpha=0.5)
        else:
            #unknown so make light in alpha
            if lengths[i] > 1e-1:
                DrawRect(starts[i],lengths[i],'#cccccc',alpha=0.1) #light grey
            else:
                #relatively short element - just draw a line
                DrawLine(starts[i],'#cccccc',alpha=0.1)
