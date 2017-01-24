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
import string as _string

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

def AddMachineLatticeToFigure(figure,tfsfile, tightLayout=True, countAxes=True):
    _pymadx.Plot.AddMachineLatticeToFigure(figure, tfsfile, tightLayout, countAxes)

def ProvidWrappedS(sArray, index):
    s = sArray #shortcut
    smax = s[-1]
    sind = s[index]
    snewa = s[index:]
    snewa = snewa - sind
    snewb = s[:index]
    snewb = snewb + (smax - sind)
    snew  = _np.concatentate((snewa,snewb))
    return snew    

def CompareBDSIMWithMadXSigma(tfsfile, bdsfile, emittance, title='', outputfilename=None):
    """
    This currently does not take into account the dispersion contribution to the beam size.

    """
    bds  = _Data.Load(bdsfile)
    tfs  = _pymadx._General.CheckItsTfs(tfsfile)
    tfsd = _pymadx.Plot._GetOpticalDataFromTfs(tfs)
    tfsd['sigmax'] = _np.sqrt(tfsd['betx']*emittance)
    tfsd['sigmay'] = _np.sqrt(tfsd['bety']*emittance)
    smax = tfs.smax

    f = _plt.figure(figsize=(7,6))
    ax = f.add_subplot(211)
    ax.errorbar(bds.S(), bds.Sigma_x()*1000.0, yerr=bds.Sigma_sigma_x()*1000.0, fmt='b.', label='BDSIM x')
    ax.errorbar(bds.S(), bds.Sigma_y()*1000.0, yerr=bds.Sigma_sigma_y()*1000.0, fmt='g.', label='BDSIM y')
    ax.plot(tfsd['s'], tfsd['sigmax']*1000.0, 'b-', label='MADX x')
    ax.plot(tfsd['s'], tfsd['sigmay']*1000.0, 'g-', label='MADX y')
    ax.axes.get_xaxis().set_visible(False)
    ax.set_ylabel('$\sigma_{\mathrm{x,y}}$ (mm)', fontsize='large')
    _plt.legend(numpoints=1,fontsize='small')

    ax2 = f.add_subplot(212)
    #ax2.errorbar(bds.S(), bds.Mean_x(), yerr=bds.Sigma_mean_x(), fmt='b.', label='BDSIM $\mu_x$')
    ax2.plot(bds.S(), bds.Mean_x()*1000.0, 'b.', label='BDSIM x')
    #ax2.errorbar(bds.S(), bds.Mean_y(), yerr=bds.Sigma_mean_y(), fmt='g.', label='BDSIM $\mu_y$')
    ax2.plot(bds.S(), bds.Mean_y()*1000.0, 'g.', label='BDSIM y')
    ax2.plot(tfsd['s'], tfsd['x']*1000.0, 'b-', label='MADX x')
    ax2.plot(tfsd['s'], tfsd['y']*1000.0, 'g-', label='MADX y')
    ax2.set_ylim(-7,7)

    ax2.set_xlabel('S Position from IP1 (ATLAS) (m)', fontsize='large')
    ax2.set_ylabel('$\mu_{\mathrm{x,y}}$ (mm)',fontsize='large')

    #_plt.legend(numpoints=1,fontsize='small')
    _plt.subplots_adjust(left=0.12,right=0.95,top=0.98,bottom=0.12,hspace=0.06)

    AddMachineLatticeToFigure(f,tfsfile)

    _plt.xlim(12980,13700)
    
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
    # options
    tightLayout = True
    if 'tightLayout' in kwargs:
        tightLayout = kwargs['tightLayout']

    axoptics  = figure.get_axes()[0]
    _AdjustExistingAxes(figure, tightLayout=tightLayout)
    axmachine = _PrepareMachineAxes(figure)
    
    #concatenate machine lattices
    sf = CheckItsBDSAsciiData(args[0])
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
    ax.set_ylim(-0.2,0.2)
 
    # loop over elements and Draw on beamline
    types   = bds.Type()
    lengths = bds.Arc_len()
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

def CompareBDSIMWithTfs(parameter, bdsfile, tfsfile, scaling=1, lattice=None, ylabel=None, outputfilename=None):
    #bdsim parameter names and equivalent tfs names
    okParams = {'Sigma_x'   : 'SIGMAX',
                'Sigma_y'   : 'SIGMAY',
                'Sigma_xp'  : 'SIGMAXP',
                'Sigma_yp'  : 'SIGMAYP',
                'Beta_x'    : 'BETX',
                'Beta_y'    : 'BETY',
                'Disp_x'    : 'DX',
                'Disp_y'    : 'DY',
                'Alph_x'    : 'ALFX',
                'Alph_y'    : 'ALFY'}

    #check inputs and load data
    if  isinstance(bdsfile,_Data.BDSAsciiData):
        bds = bdsfile
    else:
        bds = _Data.Load(bdsfile)
    if isinstance(tfsfile,_pymadx.Tfs):
        tfs  = tfsfile
    else:
        tfs  = _pymadx._General.CheckItsTfs(tfsfile)

    if parameter not in okParams.keys():
        raise ValueError(parameter +' is not a plottable parameter.')
    tfsparam = okParams[parameter]

    #name of parameter error
    errorparam = 'Sigma_' + _string.lower(parameter)

    maxes = []
    mins  = []
    #set plot minimum to 0 for any parameter which can't be negative.
    if parameter[:4] != ('Disp' or 'Alph'):
            mins.append(0)

    _plt.figure()
    if bds.names.__contains__(parameter):
        data   = bds.GetColumn(parameter) * scaling
        bdsimlabel = 'BDSIM, NPrimaries = %1.0e' %bds.GetColumn('Npart')[0]
        #Check if errors exist
        if bds.names.__contains__(errorparam):
            errors = bds.GetColumn(errorparam)*scaling
            _plt.errorbar(bds.GetColumn('S'), data, yerr=errors, label=bdsimlabel)
        else:
            _plt.plot(bds.GetColumn('S'), data,label=bdsimlabel)
        maxes.append(_np.max(data + errors))
        mins.append(_np.max(data - errors))
    if tfs.names.__contains__(tfsparam):
        data = tfs.GetColumn(tfsparam)*scaling
        _plt.plot(tfs.GetColumn('S'), data, label='MADX')
        maxes.append(_np.max(data))
        mins.append(_np.min(data))

    _plt.xlabel('S (m)')
    if ylabel != None:
        _plt.ylabel(ylabel)
    _plt.legend(loc=0)
    _plt.ylim(1.1*_np.min(mins), 1.1*_np.max(maxes))
    if lattice != None:
        AddMachineLatticeFromSurveyToFigure(_plt.gcf(),lattice)
    if outputfilename != None:
        if '.' in outputfilename:
            outputfilename = outputfilename.split('.')[0]
        _plt.savefig(outputfilename+'.pdf')
        _plt.savefig(outputfilename+'.png')


def CompareBDSIMWithTRANSPORT(parameter, bdsfile, transfile, transscaling=1, lattice=None, ylabel=None, outputfilename=None):
    #bdsim parameter names and equivalent tfs names
    okParams = ['Sigma_x',
                'Sigma_y',
                'Sigma_xp',
                'Sigma_yp',
                'Beta_x',
                'Beta_y',
                'Disp_x',
                'Disp_y',
                'Alph_x',
                'Alph_y']

    #check inputs and load data
    if  isinstance(bdsfile,_Data.BDSAsciiData):
        bds = bdsfile
    else:
        bds = _Data.Load(bdsfile)
    if isinstance(transfile,_Data.BDSAsciiData):
        trans  = transfile
    else:
        trans  = _pymadx._General.CheckItsTfs(tfsfile)

    if not okParams.__contains__(parameter):
        raise ValueError(parameter +' is not a plottable parameter.')

    #name of parameter error
    errorparam = 'Sigma_' + _string.lower(parameter)

    maxes = []
    mins  = []
    #set plot minimum to 0 for any parameter which can't be negative.
    if parameter[:4] != ('Disp' or 'Alph'):
            mins.append(0)

    _plt.figure()
    if bds.names.__contains__(parameter):
        data   = bds.GetColumn(parameter)
        bdsimlabel = 'BDSIM, NPrimaries = %1.0e' %bds.GetColumn('Npart')[0]
        #Check if errors exist
        if bds.names.__contains__(errorparam):
            errors = bds.GetColumn(errorparam)
            _plt.errorbar(bds.GetColumn('S'), data, yerr=errors, label=bdsimlabel)
        else:
            _plt.plot(bds.GetColumn('S'), data,label=bdsimlabel)
        maxes.append(_np.max(data + errors))
        mins.append(_np.max(data - errors))
    if trans.names.__contains__(parameter):
        data = trans.GetColumn(parameter)*transscaling
        _plt.plot(trans.GetColumn('S'), data, label='TRANSPORT')
        maxes.append(_np.max(data))
        mins.append(_np.min(data))

    _plt.xlabel('S (m)')
    if ylabel != None:
        _plt.ylabel(ylabel)
    _plt.legend(loc=0)
    _plt.ylim(1.1*_np.min(mins), 1.1*_np.max(maxes))
    if lattice != None:
        AddMachineLatticeFromSurveyToFigure(_plt.gcf(),lattice)
    if outputfilename != None:
        if '.' in outputfilename:
            outputfilename = outputfilename.split('.')[0]
        _plt.savefig(outputfilename+'.pdf')
        _plt.savefig(outputfilename+'.png')

