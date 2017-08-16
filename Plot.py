#pybdsim plotting tools
# Version 1.0
# L. Nevay, S.T.Boogert
# laurie.nevay@rhul.ac.uk

"""
Useful plots for bdsim output

"""
import Data as _Data
import pymadx as _pymadx

import matplotlib as _matplotlib
import matplotlib.pyplot as _plt
import matplotlib.patches as _patches
import numpy as _np
import string as _string

from _General import CheckItsBDSAsciiData as _CheckItsBDSAsciiData

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
    """
    A forward to the pymadx.Plot.PlotTfsBetaSimple function.
    """
    _pymadx.Plot.PlotTfsBetaSimple(tfsfile,title,outputfilename)

def MadxTfsBeta(tfsfile, title='', outputfilename=None):
    """
    A forward to the pymadx.Plot.PlotTfsBeta function.
    """
    _pymadx.Plot.PlotTfsBeta(tfsfile,title,outputfilename)

def AddMachineLatticeToFigure(figure,tfsfile, tightLayout=True):
    """
    A forward to the pymadx.Plot.AddMachineLatticeToFigure function.
    """
    _pymadx.Plot.AddMachineLatticeToFigure(figure, tfsfile, tightLayout)

def ProvideWrappedS(sArray, index):
    s = sArray #shortcut
    smax = s[-1]
    sind = s[index]
    snewa = s[index:]
    snewa = snewa - sind
    snewb = s[:index]
    snewb = snewb + (smax - sind)
    snew  = _np.concatentate((snewa,snewb))
    return snew

def _SetMachineAxesStyle(ax):
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)

def _PrepareMachineAxes(figure):
    # create new machine axis with proportions 6 : 1
    axmachine = figure.add_subplot(911, projection="_My_Axes")
    _SetMachineAxesStyle(axmachine)
    return axmachine

def _AdjustExistingAxes(figure, fraction=0.9, tightLayout=True):
    """
    Fraction is fraction of height all subplots will be after adjustment.
    Default is 0.9 for 90% of height. 
    """
    # we have to set tight layout before adjustment otherwise if called
    # later it will cause an overlap with the machine diagram
    if (tightLayout):
        _plt.tight_layout()
    
    axs = figure.get_axes()
    
    for ax in axs:
        bbox = ax.get_position()
        bbox.y0 = bbox.y0 * fraction
        bbox.y1 = bbox.y1 * fraction
        ax.set_position(bbox)    

def AddMachineLatticeFromSurveyToFigure(figure, *args, **kwargs):
    """
    kwargs - 'tightLayout' is set to True by default - can be supplied
              in kwargs to force it to false.

    """
    # options
    tightLayout = True
    if 'tightLayout' in kwargs:
        tightLayout = kwargs['tightLayout']

    axoptics  = figure.get_axes()[0]
    _AdjustExistingAxes(figure, tightLayout=tightLayout)
    axmachine = _PrepareMachineAxes(figure)
    
    #concatenate machine lattices
    sf = _CheckItsBDSAsciiData(args[0])
    if len(args) > 1:
        for machine in args[1:]:
            sf.ConcatenateMachine(machine)

    _DrawMachineLattice(axmachine,sf)

    #put callbacks for linked scrolling
    def MachineXlim(ax): 
        axmachine.set_autoscale_on(False)
        axoptics.set_xlim(axmachine.get_xlim())

    def Click(a) : 
        if a.button == 3 : 
            print 'Closest element: ',sf.NameFromNearestS(a.xdata)
            
    MachineXlim(axmachine)
    axmachine.callbacks.connect('xlim_changed', MachineXlim)
    figure.canvas.mpl_connect('button_press_event', Click)

def _DrawMachineLattice(axesinstance,bdsasciidataobject):
    ax  = axesinstance #handy shortcut
    bds = bdsasciidataobject

    if not hasattr(bds,"SStart"):
        raise ValueError("This file doesn't have the required column SStart")
    if not hasattr(bds,"ArcLength"):
        raise ValueError("This file doesn't have the required column ArcLength")
    
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
    ax.set_ylim(-0.2,0.2)
 
    # loop over elements and Draw on beamline
    types   = bds.Type()
    lengths = bds.ArcLength()
    starts  = bds.SStart()
    if hasattr(bds,'k1'):
        k1  = bds.k1()
    elif hasattr(bds,'K1'):
        k1  = bds.K1()
    for i in range(len(bds)):
        kw = types[i]
        if kw == 'quadrupole': 
            DrawQuad(starts[i],lengths[i],k1[i], u'#d10000') #red
        elif kw == 'rbend': 
            DrawBend(starts[i],lengths[i], u'#0066cc') #blue
        elif kw == 'sbend': 
            DrawBend(starts[i],lengths[i], u'#0066cc') #blue
        elif kw == 'rcol': 
            DrawRect(starts[i],lengths[i],'k')
        elif kw == 'ecol': 
            DrawRect(starts[i],lengths[i],'k')
        elif kw == 'degrader': 
            DrawRect(starts[i],lengths[i],'k')
        elif kw == 'sextupole':
            DrawHex(starts[i],lengths[i], u'#ffcc00') #yellow
        elif kw == 'octupole':
            DrawHex(starts[i],lengths[i], u'#00994c') #green
        elif kw == 'decapole':
            DrawHex(starts[i],lengths[i], u'#4c33b2') #purple
        elif kw == 'hkick':
            DrawHKicker(starts[i],lengths[i], u'#4c33b2') #purple
        elif kw == 'vkick':
            DrawVKicker(starts[i],lengths[i], u'#ba55d3') #medium orchid
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

