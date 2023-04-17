import gzip as _gzip
import numpy as _np
import tarfile as _tarfile


class Field(object):
    """
    Base class used for common writing procedures for BDSIM field format.

    This does not support arbitrary loop ordering - only the originally intended
    xyzt.
    """
    def __init__(self, array=_np.array([]), columns=[], flip=False, doublePrecision=False):
        self.data            = array
        self.columns         = columns
        self.header          = {}
        self.flip            = flip
        self.doublePrecision = doublePrecision
        self.nDimensions     = 0
        self.comments        = []

    def AddComment(self, commentString):
        """
        Add a string that will be put on a comment line at the beginning of the file.
        """
        self.comments.append(str(commentString))
        
    def Write(self, fileName, writeLoopOrderReversed=False, overrideLoopOrder=None):
        """
        :param writeLoopOrderReversed: Write this field map with the other loop order.
        :type writeLoopOrderReversed: bool
        :param overrideLoopOrder: string to write irrespective of internal data as the loop order.
        :type overrideLoopOrder: str

        gzip - if the file ends with ".gz" the file will be compressed automatically.

        For overrideLoopOrder it should be only 'xyzt' or 'tzyx'. This option is
        provided in case a field is prepared in the other order somehow and you
        want to control the writing of this header variable independently.
        """
        compressed = fileName.endswith(".gz")
        if compressed:
            f = _gzip.open(fileName, 'wb')
        else:
            f = open(fileName, 'w')

        def write(fn, s):
            if compressed:
                fn.write(s.encode('ascii'))
            else:
                fn.write(s)
        write(f, "# units: cm, T\n")
        for comment in self.comments:
            write(f, "# "+str(comment)+"\n")
        for key,value in self.header.items():
            write(f, str(key)+'> '+ str(value) + '\n')
        if overrideLoopOrder:
            if overrideLoopOrder not in ['xyzt', 'tzyx']:
                raise ValueError("overrideLoopOrder must be one of 'xyzt', 'tzyx'")
            write(f, "loopOrder> "+overrideLoopOrder+"\n")
        else:
            lo = 'tzyx' if writeLoopOrderReversed else 'xyzt'
            write(f, "loopOrder> "+lo+"\n")

        if self.doublePrecision:
            colStrings = ['%23s' % s for s in self.columns]
        else:
            colStrings = ['%14s' % s for s in self.columns]
        colStrings[0] = colStrings[0].strip() # don't pad the first column title
        # a '!' denotes the column header line
        write(f, '! '+ '\t'.join(colStrings)+'\n')
        
        # flatten all but last dimension - 3 field components
        nvalues = _np.shape(self.data)[-1] # number of values in last dimension

        flipLocal = self.flip
        if writeLoopOrderReversed:
            flipLocal = not flipLocal
        
        if not flipLocal:
            # [x,y,z,t,values] -> [t,z,y,x,values] for 4D
            # [x,y,z,values]   -> [z,y,x,values]   for 3D
            # [x,y,values]     -> [y,x,values]     for 2D
            # [x,values]       -> [x,values]       for 1D
            if (self.data.ndim == 2):
                pass # do nothin for 1D
            inds = list(range(self.data.ndim))       # indices for dimension [0,1,2] etc
            # keep the last value the same but reverse all indices before then
            inds[:(self.data.ndim - 1)] = reversed(inds[:(self.data.ndim - 1)])
            datal = _np.transpose(self.data, inds)
        else:
            datal = self.data

        datal = datal.reshape(-1,nvalues)
        for value in datal:
            if self.doublePrecision:
                strings   = ['%.16E' % x for x in value]
                stringsFW = ['%23s' % s for s in strings]
            else:
                strings   = ['%.8E' % x for x in value]
                stringsFW = ['%14s' % s for s in strings]
            write(f, '\t'.join(stringsFW) + '\n')

        f.close()

    def WriteFLUKA2DFormat1(self, fileName):
        """
        Write one of the FLUKA formats (x,y,Bx,by) in cm,T with no header.
    
        Very simple and only works for Field2D - can be improved.
        """
        if self.nDimensions != 2:
            raise ValueError("This field map is not 2D - it's ",self.nDimensions,"D")

        f = open(fileName, "w")
        
        # flatten all but last dimension - 3 field components
        nvalues = _np.shape(self.data)[-1] # number of values in last dimension

        flipLocal = self.flip

        dt = self.data.reshape(-1,nvalues)
        for xi in range(self.header['nx']):
            for yi in range(self.header['ny']):
                v = self.data[xi][yi]
                v = [v[index] for index in [0,1,2,3]] # [x,y,Bx,By]
                strings   = ['%.7E' % x for x in v]
                #stringsFW = ['%14s' % s for s in strings]
                f.write(','.join(strings) + '\n')
        
        f.close()


class Field1D(Field):
    """
    Utility class to write a 1D field map array to BDSIM field format.

    The array supplied should be 2 dimensional. Dimensions are:
    (x,value) where value has 4 elements [x,fx,fy,fz]. So a 120 long
    array would have np.shape of (120,4).
    
    This can be used for both electric and magnetic fields.

    Example::
    
    >>> a = Field1D(data)
    >>> a.Write('outputFileName.dat')

    """
    def __init__(self, data, doublePrecision=False, column='X'):
        columns = [column,'Fx','Fy','Fz']
        super(Field1D, self).__init__(data,columns,doublePrecision=doublePrecision)
        self.header[column.lower() + 'min'] = _np.min(self.data[:,0])
        self.header[column.lower() + 'max'] = _np.max(self.data[:,0])
        self.header['n' + column.lower()]   = _np.shape(self.data)[0]
        self.nDimensions = 1


class Field2D(Field):
    """
    Utility class to write a 2D field map array to BDSIM field format.

    The array supplied should be 3 dimensional. Dimensions are:
    (x,y,value) where value has 5 elements [x,y,fx,fy,fz].  So a 100x50 (x,y)
    grid would have np.shape of (100,50,5).

    Example::
    
    >>> a = Field2D(data) # data is a prepared array
    >>> a.Write('outputFileName.dat')

    The 'flip' boolean allows an array with (y,x,value) dimension order
    to be written as (x,y,value). Values must still be (x,y,fx,fy,fz).

    The 'doublePrecision' boolean controls whether the field and spatial
    values are written to 16 s.f. (True) or 8 s.f. (False - default).

    """
    def __init__(self, data, flip=False, doublePrecision=False, firstColumn='X', secondColumn='Y'):
        columns = [firstColumn, secondColumn, 'Fx', 'Fy', 'Fz']
        super(Field2D, self).__init__(data,columns,flip,doublePrecision)
        inds = [1,0] if flip else [0,1]
        fcl = firstColumn.lower()
        scl = secondColumn.lower()
        self.header[fcl+'min'] = _np.min(self.data[:,:,0])
        self.header[fcl+'max'] = _np.max(self.data[:,:,0])
        self.header['n'+fcl]   = _np.shape(self.data)[inds[0]]
        self.header[scl+'min'] = _np.min(self.data[:,:,1])
        self.header[scl+'max'] = _np.max(self.data[:,:,1])
        self.header['n'+scl]   = _np.shape(self.data)[inds[1]]
        self.nDimensions = 2


class Field3D(Field):
    """
    Utility class to write a 3D field map array to BDSIM field format.

    The array supplied should be 4 dimensional. Dimensions are:
    (x,y,z,value) where value has 6 elements [x,y,z,fx,fy,fz].  So a 100x50x30 
    (x,y,z) grid would have np.shape of (100,50,30,6).
    
    Example::
    
    >>> a = Field3D(data) # data is a prepared array
    >>> a.Write('outputFileName.dat')

    The 'flip' boolean allows an array with (z,y,x,value) dimension order to
    be written as (x,y,z,value). Values must still be (x,y,fx,fy,fz).

    The 'doublePrecision' boolean controls whether the field and spatial
    values are written to 16 s.f. (True) or 8 s.f. (False - default).

    """
    def __init__(self, data, flip=False, doublePrecision=False, firstColumn='X', secondColumn='Y', thirdColumn='Z'):
        columns = [firstColumn,secondColumn,thirdColumn,'Fx','Fy','Fz']
        super(Field3D, self).__init__(data,columns,flip,doublePrecision)
        inds = [2,1,0] if flip else [0,1,2]
        fcl = firstColumn.lower()
        scl = secondColumn.lower()
        tcl = thirdColumn.lower()
        self.header[fcl+'min'] = _np.min(self.data[:,:,:,0])
        self.header[fcl+'max'] = _np.max(self.data[:,:,:,0])
        self.header['n'+fcl]   = _np.shape(self.data)[inds[0]]
        self.header[scl+'min'] = _np.min(self.data[:,:,:,1])
        self.header[scl+'max'] = _np.max(self.data[:,:,:,1])
        self.header['n'+scl]   = _np.shape(self.data)[inds[1]]
        self.header[tcl+'min'] = _np.min(self.data[:,:,:,2])
        self.header[tcl+'max'] = _np.max(self.data[:,:,:,2])
        self.header['n'+tcl]   = _np.shape(self.data)[inds[2]]
        self.nDimensions = 3


class Field4D(Field):
    """
    Utility class to write a 4D field map array to BDSIM field format.

    The array supplied should be 5 dimensional. Dimensions are:
    (t,y,z,x,value) where value has 7 elements [x,y,z,t,fx,fy,fz]. So a 100x50x30x10
    (x,y,z,t) grid would have np.shape of (10,30,50,100,7).
    
    Example::
    
    >>> a = Field4D(data) # data is a prepared array
    >>> a.Write('outputFileName.dat')

    The 'flip' boolean allows an array with (t,z,y,x,value) dimension order to
    be written as (x,y,z,t,value). Values must still be (x,y,fx,fy,fz).

    The 'doublePrecision' boolean controls whether the field and spatial
    values are written to 16 s.f. (True) or 8 s.f. (False - default).

    """
    def __init__(self, data, flip=False, doublePrecision=False):
        columns = ['X','Y','Z','T','Fx','Fy','Fz']
        super(Field4D, self).__init__(data,columns,flip,doublePrecision)
        inds = [3,2,1,0] if flip else [0,1,2,3]
        self.header['xmin'] = _np.min(self.data[:,:,:,:,0])
        self.header['xmax'] = _np.max(self.data[:,:,:,:,0])
        self.header['nx']   = _np.shape(self.data)[inds[0]]
        self.header['ymin'] = _np.min(self.data[:,:,:,:,1])
        self.header['ymax'] = _np.max(self.data[:,:,:,:,1])
        self.header['ny']   = _np.shape(self.data)[inds[1]]
        self.header['zmin'] = _np.min(self.data[:,:,:,:,2])
        self.header['zmax'] = _np.max(self.data[:,:,:,:,2])
        self.header['nz']   = _np.shape(self.data)[inds[2]]
        self.header['tmin'] = _np.min(self.data[:,:,:,:,3])
        self.header['tmax'] = _np.max(self.data[:,:,:,:,3])
        self.header['nt']   = _np.shape(self.data)[inds[3]]
        self.nDimensions = 4


def Load(filename, debug=False):
    """
    :param filename: name of file to load
    :type filename: str
    
    Load a BDSIM field format file into a numpy array. Can either
    be a regular ascii text file or can be a compressed file ending
    in ".tar.gz".

    returns a numpy array with the corresponding number of dimensions
    and the dimension has the coordinates and fx,fy,fz.
    """
    gzippedFile = False
    if (filename.endswith('.tar.gz')):
        if debug:
            print('Field Loader> loading compressed file ' + filename)
        tar = _tarfile.open(filename,'r')
        f = tar.extractfile(tar.firstmember)
    elif '.gz' in filename:
        f = _gzip.open(filename)
        gzippedFile = True
    else:
        if debug:
            print('Field Loader> loading file ' + filename)
        f = open(filename)

    intoData = False
    header   = {}
    columns  = []
    data     = []
    comments = []
    
    for line in f:
        if gzippedFile:
            line = line.decode('utf-8')
        if intoData:
            ls = line.strip()
            # avoid empty lines
            if ls.isspace() or len(ls) == 0:
                continue
            data.append(line.strip().split())
        elif '>' in line:
            d = line.strip().split('>')
            k = d[0].strip()
            try:
                v = float(d[1].strip())
            except ValueError:
                v = d[1].strip()
            header[k] = v
        elif '!' in line:
            columns = line.strip('!').strip().split()
            intoData = True
        elif line.lstrip().startswith('#'):
            comments.append(line.lstrip()[1:])

    f.close()
    
    data = _np.array(data, dtype=float)

    normalLoopOrder = ['x','y','z','t']
    # this is convention - in the case of xyzt, bdsim loops
    # over x first, then y, then z, so it appears the first
    # column is changing.
    flip = False

    if 'loopOrder' in header:
        order = header['loopOrder']
        flip = order == 'tzyx'
        if debug:
            print("flip :",flip)

    nDim = len(columns) - 3
    # TBC for no case when we don't store spatial coords also
    if (nDim < 1 or nDim > 4):
        if debug:
            print('Invalid number of columns')
            print(columns)
        return

    requiredSet = {'nx','ny','nz','nt'}
    headerKeySet = set(header.keys())
    keysPresent = headerKeySet.intersection(requiredSet)
    if len(keysPresent) < nDim:
        print('missing keys from header!')
        if debug:
            print(header)
        return
    else:
        dimToNVariable = {'x' : 'nx',
                          'y' : 'ny',
                          'z' : 'nz',
                          't' : 'nt'}
        if debug:
            print("Columns: ", columns)
            print("Header: ", header)
        dims = [int(header[dimToNVariable[k.lower()]]) for k in columns[:-3]]
        dims.append(len(columns))
        if debug:
            print("Shape of numpy array to be: ", dims)
            print("nDimensions: ", nDim)
            print("Existing numpy array shape: ", _np.shape(data))
        data = data.reshape(*dims)

    # build field object
    #columns = [s.strip('n') for s in keysPresentList]
    if nDim == 1:
        fd = Field1D(data, column=columns[0])
    elif nDim == 2:
        fd = Field2D(data, flip=flip, firstColumn=columns[0], secondColumn=columns[1])
    elif nDim == 3:
        fd = Field3D(data, flip=flip, firstColumn=columns[0], secondColumn=columns[1], thirdColumn=columns[2])
    elif nDim == 4:
        fd = Field4D(data, flip=flip)
    else:
        raise ValueError("Invalid number of dimensions")

    fd.comments = comments
    return fd


def MirrorDipoleQuadrant1(field2D):
    """
    +-------+-------+
    |       |       |
    |   2   |   1   |
    |       |       |
    +-------+-------+
    |       |       |
    |   3   |   4   |
    |       |       |
    +-------+-------+

    :param field2D: field object
    :type field2D: pybdsim.Field._Field.Field2D instance

    returns an instance of the same type.
    
    For a 2D field (i.e. function of x,y but can include Bx,By,Bz),
    for the quadrant number 1, mirror it and generate a bigger field for
    all four quadrants.
    
    1. original data
    2. data mirrored in x, (x,Bx) \*= -1
    3. data mirrored in x,y, (x,y,By) \*= -1
    4. data mirrored in y, (y,Bx) \*= -1

    This is based on a dipole field.
    """
    d = field2D.data
    ds = _np.shape(d)
    sx = ds[0]
    sy = ds[1]
    result = _np.empty((2*sx, 2*sy, ds[2]))
    # top right quadrant
    result[sx:,sy:,:] = d
    # top left quadrant
    result[:sx,sy:,:] = d[::-1,:,:]
    # bottom left quadrant
    result[:sx,:sy] = d[::-1,::-1,:]
    # bottom right quadrant
    result[sx:,:sy,:] = d[:,::-1,:]

    # each value is x,y,Bx,By,Bz
    
    # flip x,Bx for top left
    result[:sx,sy:,_np.array([0,2])] *= -1
    # flip x,y for bottom left
    result[:sx,:sy,:2] *= -1
    # flip y,Bx for bottom right
    result[sx:,:sy,_np.array([1,2])] *= -1
    
    resultField = Field2D(result)
    return resultField


def SortUnorderedFieldMap2D(field):
    """
    Rearrange the data in a 2D field map to be in a linearly
    progressing loop of (x,y). In future this could be generalised
    to more dimensions and also any two dimensions, not just x,y.

    :param field: Incoming jumbled field map
    :type  field: pybdsim.Field.Field2D

    Returns a new Field2D object
    """
    d  = field.data
    sh = _np.shape(d)
    d2 = fd.data.reshape((sh[0]*sh[1],sh[2]))

    # build a dict with key (x,y)
    dmap = {}
    for v in d2:
        dmap[(v[0],v[1])] = v[2:]

    # build up new array now in order
    dnew = []
    h = fd.header
    for y in np.linspace(h['ymin'], h['ymax'], h['ny']):
        r = []
        for x in np.linspace(h['xmin'], h['xmax'], h['nx']):
            fv = dmap[(x,y)]
            r.append([x,y,*fv])
        dnew.append(r)

    dnew = _np.array(dnew)
    fdnew = Field2D(dnew)
    return fdnew
