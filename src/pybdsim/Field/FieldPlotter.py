import matplotlib.pyplot as _plt
import matplotlib as _mpl
import numpy as _np
import os as _os
import pybdsim as _pybdsim

from scipy.interpolate import RegularGridInterpolator as _RegularGridInterpolator

def _GetField(fm, nDim=None):
    """
    Check if the input is a str or a field object of the correct dimensionality. Return the field.
    """
    if type(fm) is str:
        fm = _pybdsim.Field.Load(fm)
    elif not isinstance(fm, _pybdsim.Field._Field.Field):
        raise TypeError("'filename' must be either str or Field")
    if nDim is not None and fm.nDimensions != nDim:
        raise ValueError("Field must be of dimension "+str(nDim))
    return fm


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

class FourDData:
    """
    Class purely to simplify plotting of fields. Not for general use.
    """
    def __init__(self, filename, xind=0, yind=1, zind=2, tind=3, symmetry="none", transpose=False):
        # check for the dimensionality of the field
        self.nDim = 1 if yind == -1 else 2 if zind == -1 else 3 if tind == -1 else 4
        fm = _GetField(filename, self.nDim)
        #if symmetry is not None or transpose:
        #    if symmetry is None:
        #        symmetry = "none"
        #    # currently only works for 2D fields
        #    if self.nDim == 2:
        #        fm._UseSymmetry(symmetry, transpose)
        self.data = fm.data
            
        # '...' fills in unknown number of dimensions with ':' meaning
        # all of that dimension
        if (xind >= 0):
            self.x  = self[..., xind].flatten()
            self.nx = len(_np.unique(self.x))
        if (yind >= 0):
            self.y  = self[..., yind].flatten()
            self.ny = len(_np.unique(self.y))
        if (zind >= 0):
            self.z  = self[..., zind].flatten()
            self.nz = len(_np.unique(self.z))
        if (tind >= 0):
            self.t  = self[..., tind].flatten()
            self.nt = len(_np.unique(self.t))

        # index from end as we don't know the dimensionality
        self.fx = self[..., -3].flatten()
        self.fy = self[..., -2].flatten()
        self.fz = self[..., -1].flatten()
        self.mag = _np.sqrt(self.fx**2 + self.fy**2 + self.fz**2)

    def __getitem__(self, key):
        return self.data[key]


class ThreeDData(FourDData):
    """
    Class purely to simplify plotting of fields. Not for general use.
    """
    def __init__(self, filename, symmetry="none", transpose=False):
        FourDData.__init__(self, filename, tind=-1, symmetry=symmetry, transpose=transpose)

class TwoDData(FourDData):
    """
    Class purely to simplify plotting of fields. Not for general use.
    """
    def __init__(self, filename, symmetry="none", transpose=False):
        FourDData.__init__(self, filename, tind=-1, zind=-1, symmetry=symmetry, transpose=transpose)

class OneDData(FourDData):
    """
    Class purely to simplify plotting of fields. Not for general use.
    """
    def __init__(self, filename, symmetry="none", transpose=False):
        FourDData.__init__(self, filename, tind=-1, zind=-1, yind=-1, symmetry=symmetry, transpose=transpose)

class NDData(FourDData):
    """
    Class purely to simplify plotting of fields. Not for general use.
    """
    def __init__(self, filename, symmetry="none", transpose=False):
        fm = _GetField(filename)
        if fm.nDimensions == 1:
            OneDData.__init__(self, filename, symmetry, transpose)
        elif fm.nDimensions == 2:
            TwoDData.__init__(self, filename, symmetry, transpose)
        elif fm.nDimensions == 3:
            ThreeDData.__init__(self, filename, symmetry, transpose)
        elif fm.nDimensions == 4:
            FourDData.__init__(self, filename, symmetry, transpose)
        else:
            raise ValueError("Field must be of dimension 1, 2, 3 or 4")

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


def Plot1DFxFyFz(filename, symmetry="none", transpose=False):
    """
    Plot a bdsim 1D field map file.

    :param filename: name of the field map file or object
    :type filename: str, pybdsim.Field._Field.Field1D instance
    """
    fm = _GetField(filename, 1)
    d = OneDData(filename, symmetry, transpose)

    f = _plt.figure(figsize=(7.5,4))
    axFz = f.add_subplot(313)
    axFx = f.add_subplot(311, sharex=axFz)
    axFy = f.add_subplot(312, sharex=axFz)

    axFx.plot(d.x, d.fx,'b')
    axFx.plot(d.x, d.fx,'b.')
    axFy.plot(d.x, d.fy,'g')
    axFy.plot(d.x, d.fy,'g.')
    axFz.plot(d.x, d.fz,'r')
    axFz.plot(d.x, d.fz,'r.')

    axFx.set_ylabel('B$_x$ (T)')
    axFy.set_ylabel('B$_y$ (T)')
    axFz.set_ylabel('B$_z$ (T)')
    axFz.set_xlabel(fm.columns[0]+' (cm)')

    _plt.setp(axFx.get_xticklabels(), visible=False)
    _plt.setp(axFy.get_xticklabels(), visible=False)
    _plt.tight_layout()

def Plot2DXY(filename, scale=None, title=None, flipX=False, firstDimension="X", secondDimension="Y", aspect='equal', figsize=(6,5), cmap='magma', symmetry="none", transpose=False, vmin=None, vmax=None):
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
    d = TwoDData(filename, symmetry, transpose)
    _plt.figure(figsize=figsize)
    norm = _mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    cmap = _mpl.colors.ListedColormap(_plt.cm.get_cmap(cmap)(_np.linspace(0, 1, 256)))
    _plt.quiver(d.x,d.y,d.fx,d.fy,d.mag,cmap=cmap,pivot='mid',scale=scale, norm=norm)
    if title:
        _plt.title(title)
    _Niceties(firstDimension+' (cm)', secondDimension+' (cm)', zlabel="|$B_{x,y}$| (T)", flipX=flipX, aspect=aspect)


def Plot2DXYMagnitude(filename, title=None, flipX=False, firstDimension="X", secondDimension="Y", aspect="equal", zlabel="|$B_{x,y}$| (T)", figsize=(6,5), cmap='magma', symmetry="none", transpose=False, vmin=None, vmax=None):
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
    d = TwoDData(filename, symmetry, transpose)
    _plt.figure(figsize=figsize)
    ext = [_np.min(d.x),_np.max(d.x),_np.min(d.y),_np.max(d.y)]

    # the data will write out flipped but we need to draw it the right way
    theData = d.mag.reshape(d.ny, d.nx)
    _plt.imshow(theData, extent=ext, origin='lower', aspect=aspect, interpolation='none', cmap=_mpl.colormaps.get_cmap(cmap), vmin=vmin, vmax=vmax)

    if title:
        _plt.title(title)

    fd = firstDimension
    sd = secondDimension
    _Niceties(fd+' (cm)', sd+' (cm)', zlabel=zlabel, flipX=flipX, aspect=aspect)


def Plot2D(filename, scale=None, title=None, flipX=False, flipY=False, firstDimension="X", secondDimension="Y", aspect="equal", cmap='magma', symmetry="none", transpose=False, vmin=None, vmax=None):
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
    fm = _GetField(filename, 2)
    d = TwoDData(filename, symmetry, transpose)
    
    _plt.figure()
    assert(firstDimension != secondDimension)
    iInd = ['x', 'y', 'z', 't'].index(firstDimension.lower())
    jInd = ['x', 'y', 'z', 't'].index(secondDimension.lower())
    ci = d[:, :, 0].flatten()
    cj = d[:, :, 1].flatten()
    fi = d[:, :, iInd+2].flatten()
    fj = d[:, :, jInd+2].flatten()
    if scale is None:
        scale = _ArrowSize(fm) 
    fmag = _np.hypot(fi,fj)
    fi /= fmag
    fj /= fmag
    norm = _mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    cmap = _mpl.colors.ListedColormap(_plt.cm.get_cmap(cmap)(_np.linspace(0, 1, 256)))
    _plt.quiver(ci, cj, fi, fj, fmag, cmap=cmap, norm=norm, pivot='mid', scale=1.0/scale, units='xy', scale_units='xy')
    if title:
        _plt.title(title)
    fd = firstDimension
    sd = secondDimension
    _Niceties(fd + ' (cm)', sd + ' (cm)', zlabel="|$B_{"+fd+","+sd+"}$| (T)", flipX=flipX, aspect=aspect)

def Plot2DXYMagnitudeAndArrows(filename, xlabel="X (cm)", ylabel="Y (cm)", zlabel="|$B_{x,y}$| (T)", figsize=None, title=None, aspect="equal", cmap='magma', symmetry="none", transpose=False, vmin=None, vmax=None, scaleArrow=None, sparsity=5, bScaling=1):
    """
    Plot a bdsim field map file using any two planes. The corresponding
    field components are plotted (e.g. X:Z -> Fx:Fz).

    :param filename: name of field map file or object
    :type filename: str, pybdsim.Field._Field.Field2D instance
    :param scaleArrow: numerical scaling for quiver plot arrow lengths.
    :type scaleArrow: float
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
    fm = _GetField(filename, 2)
    d = TwoDData(filename, symmetry, transpose)
    
    fig, ax = _plt.subplots(figsize=figsize)
    if scaleArrow is None:
        scaleArrow = _ArrowSize(fm)
    ci, cj = _np.meshgrid(_np.unique(d.x), _np.unique(d.y))
    fi, fj = d.fx.reshape(d.ny, d.nx), d.fy.reshape(d.ny, d.nx)
    skip = (slice(None, None, sparsity), slice(None, None, sparsity))
    ax.quiver(ci[skip], cj[skip], fi[skip]*bScaling, fj[skip]*bScaling, pivot='mid', units='xy', scale_units='xy', scale=1.0/scaleArrow, color='white', width=0.6)
    if title:
        ax.set_title(title)
    
    ext = [_np.min(d.x),_np.max(d.x),_np.min(d.y),_np.max(d.y)]
    # the data will write out flipped but we need to draw it the right way
    theData = d.mag.reshape(d.ny, d.nx)*bScaling
    maxMag = _np.max(theData)
    extend = 'max' if vmax is not None and vmax < maxMag else 'neither'
    cmap = _mpl.colormaps.get_cmap(cmap)
    cmap.set_under('white')
    im = ax.imshow(theData, extent=ext, origin='lower', aspect=aspect, interpolation='none', cmap=cmap, vmin=vmin, vmax=vmax)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_aspect(aspect)
    cax = fig.colorbar(im, ax=ax, extend=extend)
    cax.set_label(zlabel)
    _plt.tight_layout()



def Plot2DXYStream(filename, density=1, zInd=0, useColour=True, aspect='equal', cmap='magma', symmetry="none", transpose=False, vmin=None, vmax=None):
    """
    Plot a bdsim field map file using the X,Y plane as a stream plot and plotting Fx, Fy.
    
    :param filename: name of field map file or object
    :type filename: str, pybdsim.Field._Field.Field2D or Field3D instance
    :param density: arrow density (default=1) for matplotlib streamplot
    :type density: float
    :param useColour: use magnitude of field as colour.
    :type useColour: bool
    :param aspect: Matplotlib axes aspect (e.g. 'auto' or 'equal')
    :type aspect: str

    Note, matplotlibs streamplot may raise an exception if the field is entriely 0 valued.
    """
    d = NDData(filename, symmetry, transpose)
    if d.nDim == 2:
        cx = _np.unique(d.x)
        cy = _np.unique(d.y)
        fx = d.fx.reshape(len(cy), len(cx))
        fy = d.fy.reshape(len(cy), len(cx))
    elif d.nDim == 3:
        # with the 3D data, we need to select a slice in Z (does not seem to work yet)
        cx = d[0,:,zInd,0]
        cy = d[:,0,zInd,1]
        fx = d[:,:,zInd,3]
        fy = d[:,:,zInd,4]
    else:
        raise ValueError("Currently only 2D and 3D field maps supported.")

    # modern matplotlib's streamplot has a very strict check on the spacing
    # of points being equal, which they're meant. However, it is too strict
    # given the precision of incoming data, So, knowing here they're linearly
    # spaced, we regenerate again for the purpose of this plot.
    cx = _np.linspace(_np.min(cx), _np.max(cx), len(cx))
    cy = _np.linspace(_np.min(cy), _np.max(cy), len(cy))
    
    _plt.figure()
    mag = _np.sqrt(fx**2 + fy**2)
    if useColour:
        norm = _mpl.colors.Normalize(vmin=vmin, vmax=vmax)
        cmap = _mpl.colors.ListedColormap(_plt.cm.get_cmap(cmap)(_np.linspace(0, 1, 256)))
        _plt.streamplot(cx, cy, fx, fy, color=mag, cmap=cmap, norm=norm, density=density)
    else:
        lw = 5*mag / mag.max()
        _plt.streamplot(cx, cy, fx, fy, density=density, color='k', linewidth=lw)
    _Niceties('X (cm)', 'Y (cm)', zlabel="|$B_{x,y}$| (T)", aspect=aspect)

def Plot2DXZStream(filename, density=1, yIndexIf3D=0, useColour=True, aspect='equal', cmap='magma', symmetry="none", transpose=False, vmin=None, vmax=None):
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
    d = TwoDData(filename, symmetry, transpose)

    yInd = yIndexIf3D
    if d.nDim == 2:
        cx = d[0,:,0]
        cz = d[:,0,1] # still 2d data
        fx = d[:,:,2]
        fz = d[:,:,4]
    elif d.nDim == 3:
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
        norm = _mpl.colors.Normalize(vmin=vmin, vmax=vmax)
        cmap = _mpl.colors.ListedColormap(_plt.cm.get_cmap(cmap)(_np.linspace(0, 1, 256)))
        _plt.streamplot(cx, cz, fx, fz, color=mag, cmap=cmap, norm=norm, density=density)
    else:
        _plt.streamplot(cx, cz, fx, fz, density=density)
    _Niceties('X (cm)', 'Z (cm)', zlabel="|$B_{x,z}$| (T)", aspect=aspect)

def Plot2DXYConnectionOrder(filename, symmetry=None, transpose=False):
    """
    Plot a point in orange and a line in blue (default matplotlib colours)
    for each location in the field map. If the field map is constructed
    correctly, this should show a set of lines with diagonals between them.
    The other plots with the arrows are independent of order unlike when
    BDSIM loads the fields. So you might see an OK field map, but it could
    be wrong if handwritten.
    """
    d = TwoDData(filename, symmetry, transpose)
    _plt.figure()
    _plt.plot(d.x,d.y)
    _plt.plot(d.x,d.y,'.')
    _plt.xlabel('X (cm)')
    _plt.ylabel('Y (cm)')
    _plt.tight_layout()

def Plot2DXYComponent(filename, componentIndex=2, scale=None, title=None, flipX=False, aspect='equal', cmap='magma', symmetry="none", transpose=False, vmin=None, vmax=None):
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
    d = TwoDData(filename, symmetry, transpose)
    dataDict = {0: d.fx, 1: d.fy, 2: d.fz}
    scale = scale if scale is not None else 1.0
    data = dataDict[componentIndex]*scale
    data = data.reshape(d.ny, d.nx)
    label = ['x', 'y', 'z']

    _plt.figure()
    ext = [_np.min(d[:,:,0]),_np.max(d[:,:,0]),_np.min(d[:,:,1]),_np.max(d[:,:,1])]
    _plt.imshow(data, extent=ext, origin='lower', aspect='equal', interpolation='none', cmap=_mpl.colormaps.get_cmap(cmap), vmin=vmin, vmax=vmax)
    if title:
        _plt.title(title)
    _Niceties('X (cm)', 'Y (cm)', zlabel="$B_{}$ (T)".format(label[componentIndex]), flipX=flipX, aspect=aspect)

def Plot2DXYBx(filename, scale=None, title=None, flipX=False, aspect='equal', cmap='magma', symmetry="none", transpose=False, vmin=None, vmax=None):
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
    Plot2DXYComponent(filename, 0, scale, title, flipX, aspect, cmap, symmetry, transpose, vmin, vmax)

def Plot2DXYBy(filename, scale=None, title=None, flipX=False, aspect='equal', cmap='magma', symmetry="none", transpose=False, vmin=None, vmax=None):
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
    Plot2DXYComponent(filename, 1, scale, title, flipX, aspect, cmap, symmetry, transpose, vmin, vmax)

def Plot2DXYBz(filename, scale=None, title=None, flipX=False, aspect='equal', cmap='magma', symmetry="none", transpose=False, vmin=None, vmax=None):
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
    Plot2DXYComponent(filename, 2, scale, title, flipX, aspect, cmap, symmetry, transpose, vmin, vmax)


def Plot2DXYFxFyFz(filename, title=None, aspect="auto", extent=None, symmetry='none', transpose=False, **imshowKwargs):
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
    d = TwoDData(filename, symmetry, transpose)
    
    f   = _plt.figure(figsize=(7.5,4))
    ax  = f.add_subplot(131)
    ax2 = f.add_subplot(132)
    ax3 = f.add_subplot(133)

    if extent is None:
        extent = [_np.min(d[:,:,0]), _np.max(d[:,:,0]), _np.min(d[:,:,1]), _np.max(d[:,:,1])]
    imshowKwargs['extent'] = extent

    # determine a consistent colour min and max value for all three subplots
    if 'vmin' not in imshowKwargs:
        imshowKwargs['vmin'] = _np.min(d[:,:,3:])
    if 'vmax' not in imshowKwargs:
        imshowKwargs['vmax'] = _np.max(d[:,:,3:])
    if 'cmap' not in imshowKwargs:
        cmap = 'magma'
        imshowKwargs['cmap'] = _mpl.colormaps.get_cmap(cmap)
    im = ax.imshow(d.fx.reshape(d.ny, d.nx), interpolation='None', origin='lower', **imshowKwargs)
    ax.set_xlabel('X (cm)')
    ax.set_ylabel('Y (cm)')
    ax.set_title('X-Component',size='medium')
    
    ax2.imshow(d.fy.reshape(d.ny, d.nx), interpolation='None', origin='lower', **imshowKwargs)
    ax2.set_xlabel('X (cm)')
    ax2.set_title('Y-Component',size='medium')
    ax2.get_yaxis().set_ticks([])

    ax3.imshow(d.fz.reshape(d.ny, d.nx), interpolation='None', origin='lower', **imshowKwargs)
    ax3.set_xlabel('X (cm)')
    ax3.set_title('Z-Component',size='medium')
    ax3.get_yaxis().set_ticks([])

    f.subplots_adjust(left=0.09, right=0.85, top=0.86, bottom=0.12, wspace=0.02)
    cbar_ax = f.add_axes([0.88, 0.15, 0.05, 0.7])
    f.colorbar(im, cax=cbar_ax)

    if title:
        _plt.suptitle(title, size='x-large')

def Plot3DXY(filename, scale=None, title=None, flipX=False, flipY=False, aspect='equal', cmap='magma', symmetry="none", transpose=False, vmin=None, vmax=None):
    """
    Plots (B_x,B_y) as a function of x and y.
    """
    d = ThreeDData(filename, symmetry, transpose)
    _plt.figure()
    _plt.quiver(d.x,d.y,d.fx,d.fy,d.mag,cmap=_mpl.colormaps.get_cmap(cmap),pivot='mid',scale=scale, vmin=vmin, vmax=vmax)
    if title:
        _plt.title(title)
    _Niceties('X (cm)', 'Y (cm)', zlabel="|$B_{x,y}$| (T)", flipX=flipX, aspect=aspect)

def Plot3DXZ(filename, scale=None, title=None, flipX=False, flipZ=False, aspect='equal', cmap='magma', symmetry="none", transpose=False, vmin=None, vmax=None):
    """
    Plots (B_x,B_z) as a function of x and z.
    """
    d = ThreeDData(filename, symmetry, transpose)
    _plt.figure()
    _plt.quiver(d.x,d.z,d.fx,d.fz,d.mag,cmap=_mpl.colormaps.get_cmap(cmap),pivot='mid',scale=scale, vmin=vmin, vmax=vmax)
    if title:
        _plt.title(title)
    _Niceties('X (cm)', 'Z (cm)', zlabel="|$B_{x,z}$| (T)", flipX=flipX, aspect=aspect)

def Plot3DPyVista(filenameE, filenameB=None, tindex = 0, scale=None) :
    """
    Plots E and B as a function of x, y and z using pyvista
    """

    try :
        import pyvista as pv
        pv.global_theme.allow_empty_mesh = True
    except :
        print("Need pyvista for 3d field plotting")
        return

    dE = _pybdsim.Field.Load(filenameE)

    if len(dE.data.shape) == 5 : # deal with 4D field
        timedependent = True
    else :
        timedependent = False

    if timedependent : # deal with 4D field
        dE.data = dE.data[tindex,:,:,:,:]

    if filenameB :
        dB = _pybdsim.Field.Load(filenameB)
        if timedependent : # deal with 4D field
            dB.data = dB.data[tindex,:,:,:,:]

    x = dE.data[0,0,:,0]
    y = dE.data[0,:,0,1]
    z = dE.data[:,0,0,2]

    dimensions = [dE.data.shape[0], dE.data.shape[1], dE.data.shape[2]]
    spacing = [x[1]-x[0], y[1]-y[0], z[1]-z[0]]
    origin = [x.min(), y.min(), z.min()]

    grid = pv.ImageData(
        dimensions=dimensions,
        spacing=spacing,
        origin=origin,
    )

    if not timedependent:
        grid['E'] = _np.reshape(dE.data[:,:,:,3:], (dE.data.shape[0]*dE.data.shape[1]*dE.data.shape[2],3))
    else :
        grid['E'] = _np.reshape(dE.data[:,:,:,4:], (dE.data.shape[0]*dE.data.shape[1]*dE.data.shape[2],3))

    if filenameB :
        if not timedependent:
            grid['B'] = _np.reshape(dB.data[:,:,:,3:], (dB.data.shape[0]*dB.data.shape[1]*dB.data.shape[2],3))
        else :
            grid['B'] = _np.reshape(dB.data[:,:,:,4:], (dB.data.shape[0]*dB.data.shape[1]*dB.data.shape[2],3))

    pl = pv.Plotter()

    # intensity


    # arrows
    glyphsE = grid.glyph(orient="E", factor=grid.x.max()/grid.get_array("E").max()/10)
    glyphsB = grid.glyph(orient="B", factor=grid.x.max()/grid.get_array("B").max()/10)
    # pl.add_mesh(glyphsE, show_scalar_bar=True, lighting=False, color="red")
    # pl.add_mesh(glyphsB, show_scalar_bar=True, lighting=False, color="blue")

    # streamlines

    # compute derivatives (dEz/dz)
    E = _np.reshape(grid['E'],(grid.dimensions[0],grid.dimensions[1],grid.dimensions[2],3))
    x = _np.linspace(grid.bounds[0], grid.bounds[1],grid.dimensions[0])
    y = _np.linspace(grid.bounds[2], grid.bounds[3],grid.dimensions[1])
    z = _np.linspace(grid.bounds[4], grid.bounds[5],grid.dimensions[2])
    Einter = _RegularGridInterpolator((x,y,z),_np.swapaxes(E,0,2))

    Ez = Einter((0,0,z))[:,2]
    LocZ  = z[_np.where(_np.diff(_np.sign(_np.diff(Ez))))] # find locations of derivative sign change

    for LocZi in LocZ :
        fieldLineSeedE = pv.Disc(center = [0,0,LocZi], inner=0.0, outer=grid.x.max(), r_res=5, c_res=10)
        fieldLineE = grid.streamlines_from_source(fieldLineSeedE,
                                                  vectors="E",
                                                  max_step_length=0.2,
                                                  max_time=50.0,
                                                  integration_direction="both")
        pl.add_mesh(fieldLineE.tube(radius=0.2),cmap="Reds")


    if filenameB :
        # compute derivatives (dBp/dp)

        fieldLineSeedB = pv.Plane(center = [0,0,0], direction=[0,1,0], i_size=2*grid.x.max(), j_size=2*grid.y.max(), i_resolution=10, j_resolution=10)
        fieldLineB = grid.streamlines_from_source(fieldLineSeedB,
                                                  vectors="B",
                                                  max_step_length=0.2,
                                                  max_time=50.0,
                                                  integration_direction="both")
        pl.add_mesh(fieldLineB.tube(radius=0.2), cmap="Blues")

    pl.camera.position = (100, 100, 100)
    pl.show()

    return dE, dB, grid
