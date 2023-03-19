import matplotlib.pyplot as _plt
import numpy as _np

import pybdsim as _pybdsim
import pybdsim.Field._Field

def _ArrowSize(d):
    """
    :param d: pybdsim.Field.Field instance
    :type  d: pybdsim.Field.Field
    """
    nDim = d.nDimensions
    h = d.header
    result = _np.inf
    for i in range(nDim):
        key = d.columns[i].lower()
        step = (h[key+'max'] - h[key+'min']) / h['n'+key]
        result = _np.min([result, step])
    return result

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

def _Niceties(xlabel, ylabel, zlabel="", flipX=False, aspect='equal'):
    if flipX:
        cx = _plt.xlim()
        _plt.xlim(cx[1],cx[0]) # plot backwards in effect
    _plt.xlabel(xlabel)
    _plt.ylabel(ylabel)
    _plt.colorbar(label=zlabel)
    ax = _plt.gca()
    ax.set_aspect(aspect)
    _plt.tight_layout()


def Plot1DFxFyFz(filename):
    """
    Plot a bdsim 1D field map file.

    :param filename: name of the field map file or object
    :type filename: str, pybdsim.Field._Field.Field1D instance
    """
    if type(filename) is str:
        d = _pybdsim.Field.Load(filename)
    elif isinstance(filename, _pybdsim.Field._Field.Field1D):
        d = filename
    else:
        raise TypeError("'filename' must be either str or Field1D")

    f = _plt.figure(figsize=(7.5,4))
    axFz = f.add_subplot(313)
    axFx = f.add_subplot(311, sharex=axFz)
    axFy = f.add_subplot(312, sharex=axFz)

    axFx.plot(d.data[:,0], d.data[:,1],'b')
    axFx.plot(d.data[:,0], d.data[:,1],'b.')
    axFy.plot(d.data[:,0], d.data[:,2],'g')
    axFy.plot(d.data[:,0], d.data[:,2],'g.')
    axFz.plot(d.data[:,0], d.data[:,3],'r')
    axFz.plot(d.data[:,0], d.data[:,3],'r.')

    axFx.set_ylabel('B$_x$ (T)')
    axFy.set_ylabel('B$_y$ (T)')
    axFz.set_ylabel('B$_z$ (T)')
    axFz.set_xlabel(d.columns[0]+' (cm)')

    _plt.setp(axFx.get_xticklabels(), visible=False)
    _plt.setp(axFy.get_xticklabels(), visible=False)
    _plt.tight_layout()

def Plot2DXY(filename, scale=None, title=None, flipX=False, firstDimension="X", secondDimension="Y", aspect='equal', figsize=(6,5)):
    """
    Plot a bdsim field map file using the X,Y plane.
    
    :param filename: name of field map file or object
    :type filename: str, pybdsim.Field._Field.Field2D instance
    :param scale: numerical scaling for quiver plot arrow lengths.
    :type scale: float
    :param title: title for plot
    :type title: str
    :param flipX: whether to plot x backwards to match the right hand coordinate system of Geant4.
    :type flipX: bool
    :param firstDimension: Label of first dimension, e.g. "X"
    :type firstDimension: str
    :param secondDimension: Label of second dimension, e.g. "Z"
    :type secondDimension: str
    :param aspect: Matplotlib axes aspect (e.g. 'auto' or 'equal')
    :type aspect: str
    """
    d = TwoDData(filename)
    _plt.figure(figsize=figsize)
    _plt.quiver(d.x,d.y,d.fx,d.fy,d.mag,cmap=_plt.cm.magma,pivot='mid',scale=scale)
    if title:
        _plt.title(title)
    _Niceties(firstDimension+' (cm)', secondDimension+' (cm)', zlabel="|$B_{x,y}$| (T)", flipX=flipX, aspect=aspect)


def Plot2DXYMagnitude(filename, title=None, flipX=False, firstDimension="X", secondDimension="Y", aspect="equal", zlabel="|$B_{x,y}$| (T)", figsize=(6,5)):
    """
    Plot a the magnitude of a 2D bdsim field map file using any two planes.

    :param filename: name of field map file or object
    :type filename: str, pybdsim.Field._Field.Field2D instance
    :param title: title for plot
    :type title: str, None
    :param flipX: whether to plot x backwards to match the right hand coordinate system of Geant4.
    :type flipX: bool
    :param firstDimension: Name of first dimension, e.g. "X"
    :type firstDimension: str
    :param secondDimension: Name of second dimension, e.g. "Z"
    :type secondDimension: str
    :param aspect: Matplotlib axes aspect (e.g. 'auto' or 'equal')
    :type aspect: str
    :param zlabel: Label for colour bar
    :type zlabel: str
    """
    flip = False
    if type(filename) is str:
        doriginal = _pybdsim.Field.Load(filename)
        d = doriginal.data
        flip = doriginal.flip
    elif isinstance(filename, _pybdsim.Field._Field.Field):
        doriginal = filename
        d = filename.data
        flip = doriginal.flip
    else:
        raise ValueError("Invalid type of data")
    
    _plt.figure(figsize=figsize)

    # assumes the columns are X Y Fx Fy Fz
    bmag = _np.sqrt(d[:,:,2]**2 + d[:,:,3]**2)

    ext = [_np.min(d[:,:,0]), _np.max(d[:,:,0]), _np.min(d[:,:,1]), _np.max(d[:,:,1])]

    # the data will write out flipped but we need to draw it the right way
    theData = bmag.T if flip else bmag
    _plt.imshow(theData, extent=ext, origin='lower', aspect=aspect, interpolation='none')

    if title:
        _plt.title(title)

    fd = firstDimension
    sd = secondDimension
    _Niceties(fd+' (cm)', sd+' (cm)', zlabel=zlabel, flipX=flipX, aspect=aspect)


def Plot2D(filename, scale=None, title=None, flipX=False, flipY=False, firstDimension="X", secondDimension="Y", aspect="equal"):
    """
    Plot a bdsim field map file using any two planes. The corresponding
    field components are plotted (e.g. X:Z -> Fx:Fz).

    :param filename: name of field map file or object
    :type filename: str, pybdsim.Field._Field.Field2D instance
    :param scale: numerical scaling for quiver plot arrow lengths.
    :type scale: float
    :param title: title for plot
    :type title: str
    :param flipX: whether to plot x backwards to match the right hand coordinate system of Geant4.
    :type flipX: bool
    :param firstDimension: Name of first dimension, e.g. "X"
    :type firstDimension: str
    :param secondDimension: Name of second dimension, e.g. "Z"
    :type secondDimension: str
    :param aspect: Matplotlib axes aspect (e.g. 'auto' or 'equal')
    :type aspect: str
    """
    if type(filename) is str:
        doriginal = _pybdsim.Field.Load(filename)
        d = doriginal.data
    elif isinstance(filename, _pybdsim.Field._Field.Field):
        doriginal = filename
        d = filename.data
    else:
        raise ValueError("Invalid type of data")
    _plt.figure()
    assert(firstDimension != secondDimension)
    iInd = ['x', 'y', 'z', 't'].index(firstDimension.lower())
    jInd = ['x', 'y', 'z', 't'].index(secondDimension.lower())
    ci = d[:, :, 0].flatten()
    cj = d[:, :, 1].flatten()
    fi = d[:, :, iInd+2].flatten()
    fj = d[:, :, jInd+2].flatten()
    if scale is None:
        scale = _ArrowSize(doriginal)
    fmag = _np.hypot(fi,fj)
    fi /= fmag
    fj /= fmag
    _plt.quiver(ci, cj, fi, fj, fmag, cmap=_plt.cm.magma, pivot='mid', scale=1.0/scale, units='xy', scale_units='xy')
    if title:
        _plt.title(title)
    fd = firstDimension
    sd = secondDimension
    _Niceties(fd + ' (cm)', sd + ' (cm)', zlabel="|$B_{"+fd+","+sd+"}$| (T)", flipX=flipX, aspect=aspect)

def Plot2DXYStream(filename, density=1, zIndexIf3D=0, useColour=True, aspect='equal'):
    """
    Plot a bdsim field map file using the X,Y plane as a stream plot and plotting Fx, Fy.
    
    :param filename: name of field map file or object
    :type filename: str, pybdsim.Field._Field.Field2D or Field3D instance
    :param density: arrow density (default=1) for matplotlib streamplot
    :type density: float
    :param zIndexIf3D: index in Z if using 3D field map (default=0)
    :type zIndexIf3D: int
    :param useColour: use magnitude of field as colour.
    :type useColour: bool\
    :param aspect: Matplotlib axes aspect (e.g. 'auto' or 'equal')
    :type aspect: str

    Note, matplotlibs streamplot may raise an exception if the field is entriely 0 valued.
    """
    if type(filename) is str:
        d = _pybdsim.Field.Load(filename)
    elif isinstance(filename, _pybdsim.Field._Field.Field):
        d = filename.data
    else:
        raise ValueError("Invalid type of data")

    shape = _np.shape(d.data)
    zInd = zIndexIf3D
    if len(shape) == 3:
        cx = d[0,:,0]
        cy = d[:,0,1]
        fx = d[:,:,2]
        fy = d[:,:,3]
    elif len(shape) == 4:
        cx = d[zInd,0,:,0]
        cy = d[zInd,:,0,1]
        fx = d[zInd,:,:,3]
        fy = d[zInd,:,:,4]
    else:
        raise ValueError("Currently only 2D and 3D field maps supported.")

    # modern matplotlib's streamplot has a very strict check on the spacing
    # of points being equal, which they're meant. However, it is too strict
    # given the precision of incoming data, So, knowing here they're linearly
    # spaced, we regenerate again for the purpose of this plot.
    cx = _np.linspace(_np.min(cx), _np.max(cx), len(cx))
    cy = _np.linspace(_np.min(cy), _np.max(cy), len(cy))
    
    _plt.figure()
    if useColour:
        mag = _np.sqrt(fx**2 + fy**2)
        _plt.streamplot(cx,cy,fx,fy,color=mag,cmap=_plt.cm.magma,density=density)
    else:
        _plt.streamplot(cx,cy,fx,fy,density=density)
    _Niceties('X (cm)', 'Y (cm)', zlabel="|$B_{x,y}$| (T)", aspect=aspect)

def Plot2DXZStream(filename, density=1, yIndexIf3D=0, useColour=True, aspect='equal'):
    """
    Plot a bdsim field map file using the X,Z plane as a stream plot and plotting Fx, Fz.
    
    :param filename: name of field map file or object
    :type filename: str, pybdsim.Field._Field.Field2D or Field3D instance
    :param density: arrow density (default=1) for matplotlib streamplot
    :type density: float
    :param yIndexIf3D: index in Z if using 3D field map (default=0)
    :type yIndexIf3D: int
    :param useColour: use magnitude of field as colour.
    :type useColour: bool
    :param aspect: Matplotlib axes aspect (e.g. 'auto' or 'equal')
    :type aspect: str

    Note, matplotlibs streamplot may raise an exception if the field is entriely 0 valued.
    """
    if type(filename) is str:
        d = _pybdsim.Field.Load(filename)
    elif isinstance(filename, _pybdsim.Field._Field.Field):
        d = filename.data
    else:
        raise ValueError("Invalid type of data")

    shape = _np.shape(d.data)
    yInd = yIndexIf3D
    if len(shape) == 3:
        cx = d[0,:,0]
        cz = d[:,0,1] # still 2d data
        fx = d[:,:,2]
        fz = d[:,:,4]
    elif len(shape) == 4:
        cx = d[yInd,0,:,0]
        cz = d[yInd,:,0,2]
        fx = d[yInd,:,:,3]
        fz = d[yInd,:,:,5]
    else:
        raise ValueError("Currently only 2D and 3D field maps supported.")

    # modern matplotlib's streamplot has a very strict check on the spacing
    # of points being equal, which they're meant. However, it is too strict
    # given the precision of incoming data, So, knowing here they're linearly
    # spaced, we regenerate again for the purpose of this plot.
    cx = _np.linspace(_np.min(cx), _np.max(cx), len(cx))
    cz = _np.linspace(_np.min(cz), _np.max(cz), len(cz))
    
    _plt.figure()
    if useColour:
        mag = _np.sqrt(fx**2 + fz**2)
        _plt.streamplot(cx,cz,fx,fz,color=mag,cmap=_plt.cm.magma,density=density)
    else:
        _plt.streamplot(cx,cz,fx,fz,density=density)
    _Niceties('X (cm)', 'Z (cm)', zlabel="|$B_{x,z}$| (T)", aspect=aspect)

def Plot2DXYConnectionOrder(filename):
    """
    Plot a point in orange and a line in blue (default matplotlib colours)
    for each locationin the field map. If the field map is constructed
    correctly, this should show a set of lines with diagonals between them.
    The other plots with the arrows are independent of order unlike when
    BDSIM loads the fields. So you might see an OK field map, but it could
    be wrong if hand written.
    """
    d = TwoDData(filename)
    _plt.figure()
    _plt.plot(d.x,d.y)
    _plt.plot(d.x,d.y,'.')
    _plt.xlabel('X (cm)')
    _plt.ylabel('Y (cm)')
    _plt.tight_layout()

def Plot2DXYComponent(filename, componentIndex=2, scale=None, title=None, flipX=False, aspect='equal'):
    """
    Plot a bdsim field map file use the X,Y plane, but plotting By component.
    
    :param filename: name of field map file or object
    :type filename: str, pybdsim.Field._Field.Field2D instance
    :param componentIndex: index of field component (0,1,2) for Fx, Fy, Fz
    :type componentIndex: int
    :param scale: numerical scaling for quiver plot arrow lengths.
    :type scale: float
    :param title: title for plot
    :type title: str
    :param aspect: Matplotlib axes aspect (e.g. 'auto' or 'equal')
    :type aspect: str
    """
    if type(filename) is str:
        d = _pybdsim.Field.Load(filename)
    elif isinstance(filename, _pybdsim.Field._Field.Field2D):
        d = filename
    else:
        raise TypeError("'filename' must be either str or Field2D")

    acceptableIndices = {0,1,2}
    assert(componentIndex in acceptableIndices)

    label = ["x", "y", "z"][componentIndex]

    ci = -3 + componentIndex
    
    _plt.figure()
    ext = [_np.min(d.data[:,:,0]),_np.max(d.data[:,:,0]),_np.min(d.data[:,:,1]),_np.max(d.data[:,:,1])]
    _plt.imshow(d.data[:,:,ci], extent=ext, origin='lower', aspect='equal', interpolation='none', cmap=_plt.cm.magma)
    if title:
        _plt.title(title)
    _Niceties(d.columns[0]+' (cm)', d.columns[1]+' (cm)', zlabel="$B_"+label+"$ (T)", flipX=flipX, aspect=aspect)

def Plot2DXYBx(filename, scale=None, title=None, flipX=False, aspect='equal'):
    """
    Plot a bdsim field map file use the X,Y plane, but plotting By component.
    
    :param filename: name of field map file or object
    :type filename: str, pybdsim.Field._Field.Field2D instance
    :param scale: numerical scaling for quiver plot arrow lengths.
    :type scale: float
    :param title: title for plot
    :type title: str
    :param aspect: Matplotlib axes aspect (e.g. 'auto' or 'equal')
    :type aspect: str
    """
    Plot2DXYComponent(filename, 0, scale, title, flipX, aspect)

def Plot2DXYBy(filename, scale=None, title=None, flipX=False, aspect='equal'):
    """
    Plot a bdsim field map file use the X,Y plane, but plotting By component.
    
    :param filename: name of field map file or object
    :type filename: str, pybdsim.Field._Field.Field2D instance
    :param scale: numerical scaling for quiver plot arrow lengths.
    :type scale: float
    :param title: title for plot
    :type title: str
    :param aspect: Matplotlib axes aspect (e.g. 'auto' or 'equal')
    :type aspect: str
    """
    Plot2DXYComponent(filename, 1, scale, title, flipX, aspect)

def Plot2DXYBz(filename, scale=None, title=None, flipX=False, aspect='equal'):
    """
    Plot a bdsim field map file use the X,Y plane, but plotting By component.
    
    :param filename: name of field map file or object
    :type filename: str, pybdsim.Field._Field.Field2D instance
    :param scale: numerical scaling for quiver plot arrow lengths.
    :type scale: float
    :param title: title for plot
    :type title: str
    :param aspect: Matplotlib axes aspect (e.g. 'auto' or 'equal')
    :type aspect: str
    """
    Plot2DXYComponent(filename, 2, scale, title, flipX, aspect)


def Plot2DXYFxFyFz(filename, title=None, aspect="auto", extent=None, **imshowKwargs):
    """
    Plot Fx,Fy,Fz components of a field separately as a function of X,Y.

    :param filename: name of field map file or object
    :type filename: str, pybdsim.Field._Field.Field1D instance
    :param title: optional title for plot
    :type title: None, str
    :param aspect: aspect ratio for matplotlib imshow
    :type aspect: str
    :param extent: list or tuple of (xmin,xmax,ymin,ymax) for each plot (optional)
    :type extent: list,tuple
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
    if extent is None:
        extent = [_np.min(a[:,:,0]), _np.max(a[:,:,0]), _np.min(a[:,:,1]), _np.max(a[:,:,1])]
    imshowKwargs['extent'] = extent

    # determine a consistent colour min and max value for all three subplots
    if 'vmin' not in imshowKwargs:
        imshowKwargs['vmin'] = _np.min(a[:,:,3:])
    if 'vmax' not in imshowKwargs:
        imshowKwargs['vmax'] = _np.max(a[:,:,3:])
    
    ax.imshow(a[:,:,2], interpolation='None', origin='lower', **imshowKwargs)
    ax.set_xlabel('X (cm)')
    ax.set_ylabel('Y (cm)')
    ax.set_title('X-Component',size='medium')
    
    im = ax2.imshow(a[:,:,3], interpolation='None', origin='lower', **imshowKwargs)
    ax2.set_xlabel('X (cm)')
    ax2.set_title('Y-Component',size='medium')
    ax2.get_yaxis().set_ticks([])

    im = ax3.imshow(a[:,:,4], interpolation='None', origin='lower', **imshowKwargs)
    ax3.set_xlabel('X (cm)')
    ax3.set_title('Z-Component',size='medium')
    ax3.get_yaxis().set_ticks([])

    f.subplots_adjust(left=0.09, right=0.85, top=0.86, bottom=0.12, wspace=0.02)
    cbar_ax = f.add_axes([0.88, 0.15, 0.05, 0.7])
    f.colorbar(im, cax=cbar_ax)

    if title:
        _plt.suptitle(title, size='x-large')

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
