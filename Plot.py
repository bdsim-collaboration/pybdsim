#pybdsim plotting tools
# Version 1.0
# L. Nevay, S.T.Boogert
# laurie.nevay@rhul.ac.uk

"""
Useful plots for bdsim output


"""
import Data
import pymadx

import matplotlib as _matplotlib
import matplotlib.pyplot as _plt
import matplotlib.patches as _patches
import numpy as _np

class My_Axes(_matplotlib.axes.Axes):
    """
    Inherit matplotlib.axes.Axes but override pan action for mouse.
    Only allow horizontal panning - useful for lattice axes.
    """
    name = "My_Axes"
    def drag_pan(self, button, key, x, y):
        _matplotlib.axes.Axes.drag_pan(self, button, 'x', x, y) # pretend key=='x'

#register the new class of axes
_matplotlib.projections.register_projection(My_Axes)

def _CheckItsTfs(tfsfile):
    if type(tfsfile) == str:
        madx = pymadx.Tfs(tfsfile)
    elif type(tfsfile) == pymadx.Tfs:
        madx = tfsfile
    else:
        raise IOError("Unknown type: "+str(tfsfile))
    return madx

def _GetOpticalDataFromTfs(tfsobject):
    d = {}
    d['s']     = tfsobject.GetColumn('S')
    d['betx']  = tfsobject.GetColumn('BETX')
    d['bety']  = tfsobject.GetColumn('BETY')
    d['dispx'] = tfsobject.GetColumn('DX')
    d['dispy'] = tfsobject.GetColumn('DY')
    return d

def PlotMadXTfsBetaSimple(tfsfile):
    """

    """
    madx = _CheckItsTfs(tfsfile)
    d    = _GetOpticalDataFromTfs(madx)

    _plt.figure()
    _plt.plot(d['s'],_np.sqrt(d['betx']),'b-', label=r'$\sqrt{\beta_{x}}$')
    _plt.plot(d['s'],_np.sqrt(d['bety']),'g-', label=r'$\sqrt{\beta_{y}}$')
    _plt.xlabel(r'$\mathrm{S (m)}$')
    _plt.ylabel(r'$\sqrt{\beta_{x,y}}$ $\sqrt{\mathrm{m}}$')
    _plt.legend(loc=0) #best position


def PlotMadXTfsBeta(tfsfile,title='',outputfilename=None):
    """

    """
    madx = _CheckItsTfs(tfsfile)
    d    = _GetOpticalDataFromTfs(madx)
    smax = madx.smax

    f    = _plt.figure(figsize=(11,5))
    f.set_facecolor('white')
    gs   = _plt.GridSpec(2,1,height_ratios=(1,5))
    axmachine = _plt.subplot(gs[0], projection="My_Axes")
    axoptics  = _plt.subplot(gs[1])

    def MachineXlim(ax): 
        axmachine.set_autoscale_on(False)
        axoptics.set_xlim(axmachine.get_xlim())

    def Click(a) : 
        if a.button == 3 : 
            print 'Closest element: ',madx.NameFromNearestS(a.xdata)

    axmachine.callbacks.connect('xlim_changed', MachineXlim)
    f.canvas.mpl_connect('button_press_event', Click) 
    
    _plt.subplots_adjust(hspace=0,top=0.95,left=0.1,right=0.92) #no gap between plots

    #optics plots
    axoptics.plot(d['s'],_np.sqrt(d['betx']),'b-', label=r'$\sqrt{\beta_{x}}$')
    axoptics.plot(d['s'],_np.sqrt(d['bety']),'g-', label=r'$\sqrt{\beta_{y}}$')
    axoptics.plot(-100,-100,'r--', label=r'$\mathrm{D}(x)$') #fake plot for legend
    axoptics.set_xlabel('S (m)')
    axoptics.set_ylabel(r'$\sqrt{\beta_{x,y}}$ (m$^{1/2}$)')
    axoptics.legend(loc=0,fontsize='small') #best position

    #plot dispersion - only in horizontal
    ax2 = axoptics.twinx()
    ax2.plot(d['s'],d['dispx'],'r--')
    ax2.set_ylabel('Dispersion (m)')

    #lattice plot
    #hide all borders
    axmachine.get_xaxis().set_visible(False)
    axmachine.get_yaxis().set_visible(False)
    axmachine.spines['top'].set_visible(False)
    axmachine.spines['bottom'].set_visible(False)
    axmachine.spines['left'].set_visible(False)
    axmachine.spines['right'].set_visible(False)
    _DrawMachineLattice(axmachine,madx)

    _plt.suptitle(title,size='x-large')

    #set ranges
    pcy = 0.05
    pcx = 0.02
    xr = smax
    opyr = _np.sqrt(max([max(d['betx']),max(d['bety'])]))
    dsyr = max(d['dispx']) - min(d['dispx'])
    dsmax = max(d['dispx'])
    dsmin = min(d['dispx'])
    axoptics.set_xlim(0-pcx*xr,smax+pcx*xr)
    axoptics.set_ylim(0-pcy*opyr,opyr+pcy*opyr)
    ax2.set_ylim(dsmin-pcy*dsyr,dsmax+pcy*dsyr)
    axmachine.set_xlim(0-pcx*xr,smax+pcx*xr)
    
    if outputfilename != None:
        if '.' in outputfilename:
            outputfilename = outputfilename.split('.')[0]
        _plt.savefig(outputfilename+'.pdf')
        _plt.savefig(outputfilename+'.png')

def AddMachineLatticeToFigure(figure,tfsfile):
    tfs = _CheckItsTfs(tfsfile) #load the machine description

    axs = figure.get_axes() #get the existing graph
    axoptics = axs[0]  #get the only presumed axes from the figure

    #adjust existing plot to make way for machine lattice
    gs = _plt.GridSpec(2,1,height_ratios=(1,5))
    axoptics.set_position(gs[1].get_position(figure))
    axoptics.set_subplotspec(gs[1])
    #axoptics.spines['top'].set_visible(False)

    #add new axes for machine lattice
    axmachine = figure.add_subplot(gs[0], projection="My_Axes")
    axmachine.get_xaxis().set_visible(False)
    axmachine.get_yaxis().set_visible(False)
    axmachine.spines['top'].set_visible(False)
    axmachine.spines['bottom'].set_visible(False)
    axmachine.spines['left'].set_visible(False)
    axmachine.spines['right'].set_visible(False)
    figure.set_facecolor('white')
    _plt.subplots_adjust(hspace=0.01,top=0.95,left=0.1,right=0.92)

    #generate the machine lattice plot
    _DrawMachineLattice(axmachine,tfs)

    #put callbacks for linked scrolling
    def MachineXlim(ax): 
        axmachine.set_autoscale_on(False)
        axoptics.set_xlim(axmachine.get_xlim())

    def Click(a) : 
        if a.button == 3 : 
            print 'Closest element: ',tfs.NameFromNearestS(a.xdata)

    axmachine.callbacks.connect('xlim_changed', MachineXlim)
    figure.canvas.mpl_connect('button_press_event', Click) 

def _DrawMachineLattice(axesinstance,pymadxtfsobject):
    ax  = axesinstance #handy shortcut
    tfs = pymadxtfsobject

    #define temporary functions to draw individual objects
    def DrawBend(e):
        br = _patches.Rectangle((e['S'],-0.1),e['L'],0.2,color='b')
        ax.add_patch(br)
    def DrawQuad(e):
        if e['K1L'] > 0 :
            qr = _patches.Rectangle((e['S'],0),e['L'],0.2,color='r')
        elif e['K1L'] < 0: 
            qr = _patches.Rectangle((e['S'],-0.2),e['L'],0.2,color='r')
        else: 
            qr = _patches.Rectangle((e['S'],-0.1),e['L'],0.2,color='#B2B2B2') #a nice grey in hex
        ax.add_patch(qr)
    def DrawHex(e,color):
        s = e['S']
        l = e['L']
        coloryellow = '#ffcf17'
        edges = _np.array([[s,-0.1],[s,0.1],[s+l/2.,0.13],[s+l,0.1],[s+l,-0.1],[s+l/2.,-0.13]])
        sr = _patches.Polygon(edges,color=color,fill=True)
        ax.add_patch(sr)

    def DrawRect(e,color):
        rect = _patches.Rectangle((e['S'],-0.1),e['L'],0.2,color=color)
        ax.add_patch(rect)

    def DrawLine(e,color):
        ax.plot([e['S'],e['S']],[-0.2,0.2],'-',color=color)
            
    # plot beam line 
    ax.plot([0,tfs.smax],[0,0],'k-',lw=1)
    ax.set_ylim(-0.5,0.5)
 
    # loop over elements and Draw on beamline
    for element in tfs:
        kw = element['KEYWORD']
        if kw == 'QUADRUPOLE': 
            DrawQuad(element)
        elif kw == 'RBEND': 
            DrawBend(element)
        elif kw == 'SBEND': 
            DrawBend(element)
        elif kw == 'RCOLLIMATOR': 
            DrawRect(element,'k')
        elif kw == 'ECOLLIMATOR': 
            DrawRect(element,'k')
        elif kw == 'SEXTUPOLE':
            DrawHex(element,'#ffcf17') #yellow
        elif kw == 'OCTUPOLE':
            DrawHex(element,'g')
        elif kw == 'DRIFT':
            pass
        else:
            if element['L'] > 1e-1:
                DrawRect(element,'#cccccc',alpha=0.1) #light grey, probably multipole
            else:
                #relatively short element - just draw a line
                DrawLine(element,'#cccccc',alpha=0.1)
        


def CompareBDSIMSurveyWithMadXTfs(tfsfile,bdsfile,title='',outputfilename=None):
    bds  = Data.Load(bdsfile)
    madx = _CheckItsTfs(tfsfile)
    d    = _GetOpticalDataFromTfs(madx)
    smax = madx.smax

    f    = _plt.figure(figsize=(11,5))
    f.set_facecolor('white')
    gs   = _plt.GridSpec(3,1,height_ratios=(1,5,5))
    axmachine = _plt.subplot(gs[0])
    axtfs  = _plt.subplot(gs[1])
    axbds  = _plt.subplot(gs[2])

    def MachineXlim(ax): 
        axmachine.set_autoscale_on(False)
        axtfs.set_xlim(axmachine.get_xlim())
        axbds.set_xlim(axmachine.get_xlim())

    def Click(a) : 
        if a.button == 3 : 
            print 'Closest element: ',madx.NameFromNearestS(a.xdata)

    axmachine.callbacks.connect('xlim_changed', MachineXlim)
    f.canvas.mpl_connect('button_press_event', Click) 
    
    _plt.subplots_adjust(hspace=0,top=0.95,left=0.1,right=0.92) #no gap between plots

    #tfs plots
    axtfs.plot(d['s'],_np.sqrt(d['betx']),'b-', label=r'$\sqrt{\beta_{x}}$')
    axtfs.plot(d['s'],_np.sqrt(d['bety']),'g-', label=r'$\sqrt{\beta_{y}}$')
    axtfs.plot(-100,-100,'r--', label=r'$\mathrm{D}(x)$') #fake plot for legend
    axtfs.set_xlabel('S (m)')
    axtfs.set_ylabel(r'$\sqrt{\beta_{x,y}}$ (m$^{1/2}$)')
    axtfs.legend(loc=0,fontsize='small') #best position
    #plot dispersion - only in horizontal
    axtfs2 = axtfs.twinx()
    axtfs2.plot(d['s'],d['dispx'],'r--')
    axtfs2.set_ylabel('Dispersion (m)')

    #bds plots
    axbds.plot(bds.S(),_np.sqrt(bds.Beta_x()),'b-', label=r'$\sqrt{\beta_{x}}$')
    axbds.plot(bds.S(),_np.sqrt(bds.Beta_y()),'g-', label=r'$\sqrt{\beta_{y}}$')
    axbds.plot(-100,-100,'r--', label=r'$\mathrm{D}(x)$') #fake plot for legend
    axbds.set_xlabel('S (m)')
    axbds.set_ylabel(r'$\sqrt{\beta_{x,y}}$ (m$^{1/2}$)')
    axbds.text(0.02,0.85,'BDSIM',transform=axbds.transAxes,bbox=dict(facecolor='white'),backgroundcolor='white')
    #plot dispersion - only in horizontal
    axbds2 = axbds.twinx()
    axbds2.plot(bds.S(),bds.Disp_x(),'r--')
    axbds2.set_ylabel('Dispersion (m)')
    
    #lattice plot
    #hide all borders
    axmachine.get_xaxis().set_visible(False)
    axmachine.get_yaxis().set_visible(False)
    axmachine.spines['top'].set_visible(False)
    axmachine.spines['bottom'].set_visible(False)
    axmachine.spines['left'].set_visible(False)
    axmachine.spines['right'].set_visible(False)
    _DrawMachineLattice(axmachine,madx)

    _plt.suptitle(title,size='x-large')

    #set ranges
    pcy = 0.05
    pcx = 0.02
    xr = smax
    tfsyr = _np.sqrt(max([max(d['betx']),max(d['bety'])]))
    bdsyr = _np.sqrt(max([max(bds.Beta_x()),max(bds.Beta_y())]))
    tfsdsmax = max(d['dispx'])
    tfsdsmin = min(d['dispx'])
    tfsdsyr  = tfsdsmax - tfsdsmin
    bdsdsmax = max(bds.Disp_x())
    bdsdsmin = min(bds.Disp_x())
    bdsdsyr  = bdsdsmax - bdsdsmin
    axtfs.set_xlim(0-pcx*xr,smax+pcx*xr)
    axtfs.set_ylim(0-pcy*tfsyr,tfsyr+pcy*tfsyr)
    axtfs2.set_ylim(tfsdsmin-pcy*tfsdsyr,tfsdsmax+pcy*tfsdsyr)
    axbds.set_xlim(0-pcx*xr,smax+pcx*xr)
    axbds.set_ylim(0-pcy*tfsyr,tfsyr+pcy*tfsyr)

    #set_ylim(0-pcy*bdsyr,bdsyr+pcy*bdsyr)
    axbds2.set_ylim(tfsdsmin-pcy*tfsdsyr,tfsdsmax+pcy*tfsdsyr)

    #set_ylim(bdsdsmin-pcy*bdsdsyr,bdsdsmax+pcy*bdsdsyr)
    axmachine.set_xlim(0-pcx*xr,smax+pcx*xr)
    
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

def Histogram(x,xlabel,title,nbins,**kwargs):
    f = _plt.figure()
    _plt.hist(x,nbins,histtype='step',**kwargs)
    _plt.xlabel(xlabel)
    _plt.title(title)
    return f
