import matplotlib.pyplot as _plt
import numpy as _np

import pybdsim as _pybdsim

class FourDData(object):
    """
    Class purely to simplify plotting of fields. Not for general use.
    """
    def __init__(self, filename, xind=0, yind=1, zind=2, tind=3):
        if type(filename) is str:
            d = _pybdsim.Field.Load(filename)
        elif isinstance(filename, _pybdsim.Field._Field.Field):
            d = filename.data
        else:
            d = filename
            
        # '...' fills in unknown number of dimensions with ':' meaning
        # all of that dimension
        if (xind >= 0):
            self.x  = d[..., xind].flatten()
        if (yind >= 0):
            self.y  = d[..., yind].flatten()
        if (zind >= 0):
            self.z  = d[..., zind].flatten()
        if (tind >= 0):
            self.t  = d[..., tind].flatten()

        # index from end as we don't know the dimensionality
        self.fx = d[...,-3].flatten()
        self.fy = d[...,-2].flatten()
        self.fz = d[...,-1].flatten()

        self.mag = _np.sqrt(self.fx**2 + self.fy**2 + self.fz**2)

class ThreeDData(FourDData):
    """
    Class purely to simplify plotting of fields. Not for general use.
    """
    def __init__(self, filename):
        FourDData.__init__(self, filename, tind=-1)

class TwoDData(FourDData):
    """
    Class purely to simplify plotting of fields. Not for general use.
    """
    def __init__(self, filename):
        FourDData.__init__(self, filename, tind=-1, zind=-1)

class OneDData(FourDData):
    """
    Class purely to simplify plotting of fields. Not for general use.
    """
    def __init__(self, filename):
        FourDData.__init__(self, filename, tind=-1, zind=-1, yind=-1)

def _Niceties(xlabel, ylabel, zlabel=""):
    _plt.xlabel(xlabel)
    _plt.ylabel(ylabel)
    _plt.colorbar(label=zlabel)
    _plt.tight_layout()
    ax = _plt.gca()
    ax.set_aspect('equal')

def Plot2DXY(filename, scale=None):
    """
    Plot a bdsim field map file use the X,Y plane.
    
    :param filename: name of field map file or object
    :type filename: str, pybdsim.Field._Field.Field1D instance
    :param scale: numerical scaling for quiver plot arrow lengths.
    :type scale: float
    """
    d = TwoDData(filename)
    _plt.figure()
    _plt.quiver(d.x,d.y,d.fx,d.fy,d.mag,cmap=_plt.cm.magma,pivot='mid',scale=scale)
    _Niceties('X (cm)', 'Y (cm)', zlabel="|$B_{x,y}$| (T)")

def Plot2DXYBz(filename, scale=None):
    """
    Plot a bdsim field map file use the X,Y plane, but plotting By component.
    
    :param filename: name of field map file or object
    :type filename: str, pybdsim.Field._Field.Field2D instance
    :param scale: numerical scaling for quiver plot arrow lengths.
    :type scale: float
    """
    if type(filename) is str:
        d = _pybdsim.Field.Load(filename)
    elif isinstance(filename, _pybdsim.Field._Field.Field2D):
        d = filename
    else:
        raise TypeError("'filename' must be either str or Field2D")
    
    _plt.figure()
    ext = [_np.min(d.data[:,:,0]),_np.max(d.data[:,:,0]),_np.min(d.data[:,:,1]),_np.max(d.data[:,:,1])]
    _plt.imshow(d.data[:,:,-1], extent=ext, origin='lower', aspect='equal', interpolation='none', cmap=_plt.cm.magma)
    _Niceties('X (cm)', 'Y (cm)', zlabel="$B_z$ (T)")


def Plot2DXYFxFyFz(filename, title=None, aspect="auto", **imshowKwargs):
    """
    Plot Fx,Fy,Fz components of a field separately as a function of X,Y.

    :param filename: name of field map file or object
    :type filename: str, pybdsim.Field._Field.Field1D instance
    :param title: optional title for plot
    :type title: None, str
    :param aspect: aspect ratio for matplotlib imshow
    :type aspect: str
    """
    imshowKwargs['aspect'] = aspect
    if type(filename) is str:
        fd = _pybdsim.Field.Load(filename)
    elif isinstance(filename, _pybdsim.Field._Field.Field2D):
        fd = filename
    else:
        raise TypeError("'filename' must be either str or Field2D")
    a = fd.data
    
    f   = _plt.figure(figsize=(7.5,4))
    ax  = f.add_subplot(131)
    ax2 = f.add_subplot(132)
    ax3 = f.add_subplot(133)

    xmin = _np.min(a[:,:,0])
    xmax = _np.max(a[:,:,0])
    ymin = _np.min(a[:,:,1])
    ymax = _np.max(a[:,:,1])
    ext = [_np.min(a[:,:,0]), _np.max(a[:,:,0]), _np.min(a[:,:,1]), _np.max(a[:,:,1])]

    # determine a consistent colour min and max value for all three subplots
    if 'vmin' not in imshowKwargs:
        imshowKwargs['vmin'] = _np.min(a[:,:,3:])
    if 'vmax' not in imshowKwargs:
        imshowKwargs['vmax'] = _np.max(a[:,:,3:])
    
    ax.imshow(a[:,:,2], interpolation='None', extent=ext, origin='lower', **imshowKwargs)
    ax.set_xlabel('X (cm)')
    ax.set_ylabel('Y (cm)')
    ax.set_title('X-Component',size='medium')
    
    im = ax2.imshow(a[:,:,3], interpolation='None', extent=ext, origin='lower', **imshowKwargs)
    ax2.set_xlabel('X (cm)')
    ax2.set_title('Y-Component',size='medium')
    ax2.get_yaxis().set_ticks([])

    im = ax3.imshow(a[:,:,4], interpolation='None', extent=ext, origin='lower', **imshowKwargs)
    ax3.set_xlabel('X (cm)')
    ax3.set_title('Z-Component',size='medium')
    ax3.get_yaxis().set_ticks([])

    f.subplots_adjust(left=0.09, right=0.85, top=0.86, bottom=0.12, wspace=0.02)
    cbar_ax = f.add_axes([0.88, 0.15, 0.05, 0.7])
    f.colorbar(im, cax=cbar_ax)

    if title:
        _plt.suptitle(title, size='x-large')
    _plt.savefig(filename+'.png', dpi=400)
    _plt.draw()

def Plot3DXY(filename, scale=None):
    """
    Plots (B_x,B_y) as a function of x and y.
    """
    d = ThreeDData(filename)
    _plt.figure()
    _plt.quiver(d.x,d.y,d.fx,d.fy,d.mag,cmap=_plt.cm.magma,pivot='mid',scale=scale)
    _Niceties('X (cm)', 'Y (cm)')

def Plot3DXZ(filename, scale=None):
    """
    Plots (B_x,B_z) as a function of x and z.
    """
    d = ThreeDData(filename)
    _plt.figure()
    _plt.quiver(d.x,d.z,d.fx,d.fz,d.mag,cmap=_plt.cm.magma,pivot='mid',scale=scale)
    _Niceties('X (cm)', 'Z (cm)')
