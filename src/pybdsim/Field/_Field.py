import gzip as _gzip
import importlib_resources as _importlib_resources
import numpy as _np
import tarfile as _tarfile
import os as _os    
import pybdsim

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

    def __add__(self, field):
        if self.nDimensions == field.nDimensions:
            self.data[..., self.nDimensions:] = self.data[..., self.nDimensions:] + field.data[..., field.nDimensions:]
            return self
        else:
            raise ValueError("The two field maps do not have the same dimension!")

    def __iadd__(self, field):
        self = self + field
        return self

    def __mul__(self, scalingFactor):
        self.data[..., self.nDimensions:] *= scalingFactor
        return self

    def __imul__(self, scalingFactor):
        self = self * scalingFactor
        return self

    def ScaleField(self, scalingFactor):
        self *= scalingFactor

    def AddField(self, field):
        self += field

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
            write(f, "# "+str(comment).strip()+"\n")
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

    def WriteMGNDataCard2D(self, fileName, name = 'magnet', symmetry = '0.0'):
        """
        :param fileName: Name of file to write the fieldmap to.
        :type fileName: str
        :param name: Name of the magnetic field in the MGNCREAT card.
        :type name: str
        :param symmetry: Symmetry that gets applied to the fieldmap inside FLUKA.
        :type symmetry: str

        Write 2D field maps stored in Field2D to FLUKA format which can be loaded with MGN data cards.
        Therefore, we create a magnet which is purely based on a fieldmap (200.0) without offsetting it, as
        (0,0) in the fieldmap is, where the beam is (and it's only used for analytical fields).
        The symmetry needs to be specified in accordance to Sx + Sy*10 + Sz*100, for example for a quadrupole
        it's 12.0 and for a C-shaped bend it's 10.0. 0.0 means no symmetry.
        In the final file, one can see three field points per MGNDATA card without specifying the location,
        as this is given by the grid definition. In the file, the points need to go from low x and y
        to high x and y, with looping first over y and then x.
        """
        if self.nDimensions != 2:
            raise ValueError("This field map is not 2D - it's ",self.nDimensions,"D")
        f = open(fileName, 'w')

        numberOfDigits = 9

        f.write('FREE\n')
        f.write('MGNCREAT  , 200.0, , 0.0, 0.0, ' + symmetry + ', , ' + name + '\n')
        f.write('MGNCREAT  , , , , ' + str(self.header['nx']) + ', ' + str(self.header['ny'])
                + ', ,  &\n')
        f.write('MGNCREAT  , ' +  str(self.header['xmin']) + ', ' + str(self.header['ymin'])
                + ', , ' + str(self.header['xmax']) + ', ' + str(self.header['ymax']) + ',  , &&\n')
        fieldPointCounter = 0 #Maximal 3 points per card
        lineCounter = 0 #First card ends with name of mgncreat card, second one with & and then &&
        line = 'MGNDATA   , '
        for yi in range(self.header['ny']):
            for xi in range(self.header['nx']):
                line += str(round(self.data[xi][yi][2], numberOfDigits)) + ', ' + str(round(self.data[xi][yi][3], numberOfDigits)) + ', '
                if fieldPointCounter == 2 and lineCounter == 0:
                    line += ' ' + name + '\n'
                    f.write(line)
                    line = 'MGNDATA   , '
                    lineCounter += 1
                    fieldPointCounter = 0
                elif fieldPointCounter == 2 and lineCounter == 1:
                    line += '  &\n'
                    f.write(line)
                    line = 'MGNDATA   , '
                    lineCounter += 1
                    fieldPointCounter = 0
                elif fieldPointCounter == 2 and lineCounter > 1:
                    line += '  &&\n'
                    f.write(line)
                    line = 'MGNDATA   , '
                    fieldPointCounter = 0
                elif fieldPointCounter < 2:
                    fieldPointCounter += 1

        if fieldPointCounter != 0:
            line += ', , ' * (3 - fieldPointCounter) + '  &&\nFIXED'
            f.write(line)
        else:
            f.write('FIXED')

    def WriteMGNDataCard3D(self, fileName, name = 'magnet'):
        """
        :param fileName: Name of file to write the fieldmap to.
        :type fileName: str
        :param name: Name of the magnetic field in the MGNCREAT card.
        :type name: str
        :param symmetry: Symmetry that gets applied to the fieldmap inside FLUKA.
        :type symmetry: str

        Write 2D field maps stored in Field2D to FLUKA format which can be loaded with MGN data cards.
        Therefore, we create a magnet which is purely based on a fieldmap (200.0) without offsetting it, as
        (0,0) in the fieldmap is, where the beam is (and it's only used for analytical fields).
        The symmetry needs to be specified in accordance to Sx + Sy*10 + Sz*100, for example for a quadrupole
        it's 12.0 and for a C-shaped bend it's 10.0. 0.0 means no symmetry.
        In the final file, one can see three field points per MGNDATA card without specifying the location,
        as this is given by the grid definition. In the file, the points need to go from low x and y
        to high x and y, with looping first over y and then x.
        """
        if self.nDimensions != 3:
            raise ValueError("This field map is not 3D - it's ",self.nDimensions,"D")
        f = open(fileName, 'w')

        numberOfDigits = 9

        f.write('FREE\n')
        f.write('MGNCREAT, 300.0, , 0.0, 0.0, 0.0, , ' + name + '\n')
        f.write('MGNCREAT, , , , ' + str(self.header['nx']) + ', ' + str(self.header['ny'])
                + ', ' + str(self.header['nz']) + ', &\n')
        f.write('MGNCREAT, ' +  str(self.header['xmin']) + ', ' + str(self.header['ymin'])
                + ', ' + str(self.header['zmin']) + ', ' + str(self.header['xmax']) + ', ' + str(self.header['ymax'])
                + ', ' + str(self.header['zmax']) + ', &&\n')
        fieldPointCounter = 0 #Maximal 2 points per card
        lineCounter = 0 #First card ends with name of mgncreat card, second one with & and then &&
        line = 'MGNDATA, '
        for zi in range(self.header['nz']):
            for yi in range(self.header['ny']):
                for xi in range(self.header['nx']):
                    line += ("{0:.4e}".format(self.data[xi][yi][zi][3]) + ', '
                             + "{0:.4e}".format(self.data[xi][yi][zi][4]) + ', '
                             + "{0:.4e}".format(self.data[xi][yi][zi][5]) + ', ')
                    if fieldPointCounter == 1 and lineCounter == 0:
                        line += ' ' + name + '\n'
                        f.write(line)
                        line = 'MGNDATA, '
                        lineCounter += 1
                        fieldPointCounter = 0
                    elif fieldPointCounter == 1 and lineCounter == 1:
                        line += '&\n'
                        f.write(line)
                        line = 'MGNDATA, '
                        lineCounter += 1
                        fieldPointCounter = 0
                    elif fieldPointCounter == 1 and lineCounter > 1:
                        line += '&&\n'
                        f.write(line)
                        line = 'MGNDATA, '
                        fieldPointCounter = 0
                    elif fieldPointCounter < 1:
                        fieldPointCounter += 1

        if fieldPointCounter != 0:
            line += ', , , ' * (2 - fieldPointCounter) + '&&'#\nFIXED'
            f.write(line)
        #else:
        #    f.write('FIXED')

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
    
    def _SortField(self):
        """
        Sort the field map in a linearly progressing loop of (x,y,z,t).
        """
        field = SortUnorderedFieldMap2D(self)
        self.data = field.data
        self.header = field.header

    def _UseSymmetry(self, symmetry='none', transpose=False):
        """
        Expand the field map to include the symmetries of the field.

        :param symmetry: Symmetry to apply to the field
        :type symmetry: str
        """
        field = SortUnorderedFieldMap2D(self, symmetry, transpose)
        self.data = field.data
        self.header = field.header


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
    2. data mirrored in x, (x,Bx) \\*= -1
    3. data mirrored in x,y, (x,y,By) \\*= -1
    4. data mirrored in y, (y,Bx) \\*= -1

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


_Symmetries = {
    "none": [[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]],
    "flipx": [[-1.0, 1.0, 1.0, 1.0, -1.0, 1.0, 1.0]],
    "flipy": [[1.0, -1.0, 1.0, 1.0, 1.0, -1.0, 1.0]],
    "flipz": [[1.0, 1.0, -1.0, 1.0, 1.0, 1.0, -1.0]],
    "flipt": [[1.0, 1.0, 1.0, -1.0, 1.0, 1.0, 1.0]],
    "reflectx": [
        [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        [-1.0, 1.0, 1.0, 1.0, -1.0, 1.0, 1.0]
        ],
    "reflecty": [
        [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        [1.0, -1.0, 1.0, 1.0, 1.0, -1.0, 1.0]
        ],
    "reflectz": [
        [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        [1.0, 1.0, -1.0, 1.0, 1.0, 1.0, -1.0]
        ],
    "reflectt": [
        [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0, -1.0, 1.0, 1.0, 1.0]
        ],
    "reflectxydipole": [
        [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        [-1.0, 1.0, 1.0, 1.0, -1.0, 1.0, 1.0],
        [1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0],
        [-1.0, -1.0, 1.0, 1.0, 1.0, 1.0, -1.0]
        ],
    "reflectxzdipole": [
        [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        [1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0]
        ],
    "reflectxzsolendoid": [
        [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        [1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0]
        ],
    "reflectxyquadrupole": [
        [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        [-1.0, 1.0, 1.0, 1.0, 1.0, -1.0, 1.0],
        [1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0],
        [-1.0, -1.0, 1.0, 1.0, -1.0, -1.0, 1.0]
        ]
}

# create _Symmetres2D from _Symmetries where index 2 and 3 are removed
_Symmetries2D = {}
for key in _Symmetries.keys():
    _Symmetries2D[key] = []
    for sym in _Symmetries[key]:
        _Symmetries2D[key].append(sym[:2]+sym[4:])


def SortUnorderedFieldMap2D(field, symmetry="none", transpose=False):
    """
    Rearrange the data in a 2D field map to be in a linearly
    progressing loop of (x,y). In future this could be generalised
    to more dimensions and also any two dimensions, not just x,y.
    The symmetry option allows the field to be expanded to include
    the symmetries of the field.

    :param field: Incoming jumbled field map
    :type  field: pybdsim.Field.Field2D
    :param symmetry: Symmetry to apply to the field
    :type  symmetry: str
    """
    for sym in symmetry.split():
        if sym in _Symmetries2D.keys():
            if sym in ['reflectx', 'reflectxydipole', 'reflectxyquadrupole']:
                if (field.header['xmin'] < 0 and field.header['xmax'] > 0):
                    print("Warning: Field map has positive and negative x values. The symmetry may not be applied correctly and might lead to unexpected results. Please ensure the field map is symmetric around x=0.")
            if sym in ['reflecty', 'reflectxydipole', 'reflectxyquadrupole', 'reflectxzdipole', 'reflectxzsolendoid']:
                if (field.header['ymin'] < 0 and field.header['ymax'] > 0):
                    print("Warning: Field map has positive and negative y values. The symmetry may not be applied correctly and might lead to unexpected results. Please ensure the field map is symmetric around y=0.")
        else:
            raise ValueError("Symmetry "+sym+" not recognised. Options are: "+str(_Symmetries2D.keys()))
    
    data2D = field.data.reshape(-1, field.data.shape[-1])
    for sym in symmetry.split():
        # convert the data to a 2D array
        data2D_original = _np.copy(data2D)
        # create an empty array to store the new data
        data2D = _np.empty((0, field.data.shape[-1]))
        # apply the symmetry
        for trans in _Symmetries2D[sym]:
            symData = _np.copy(data2D_original)
            for i in range(len(trans)):
                if trans[i] == -1:
                    symData[:,i] *= -1
            data2D = _np.concatenate((data2D, symData))
    # remove duplicates
    data2D = _np.unique(data2D, axis=0)
    # transpose the data if required
    if transpose:
        # switch the x and y columns with indices 0 and 1
        data2D[:,[0,1]] = data2D[:,[1,0]]
        # switch the fx and fy columns with indices -3 and -2
        data2D[:,[-3,-2]] = data2D[:,[-2,-3]]
    # prepare the data for the field object
    fieldmap = []
    for xi in _np.unique(data2D[:,0]):
        v = []
        for yi in _np.unique(data2D[:,1]):
            # find the row in data2D that corresponds to xi,yi
            row = data2D[(data2D[:,0] == xi) & (data2D[:,1] == yi)]
            v.append([row[0,0], row[0,1], row[0,2], row[0,3], row[0,4]])
        fieldmap.append(v)
    # convert to numpy array
    fieldmap = _np.array(fieldmap)
    # construct a BDSIM format field object and write it out
    field_new = pybdsim.Field.Field2D(fieldmap)
    with _importlib_resources.as_file(_importlib_resources.files("pybdsim") / "testfield2D.dat") as testfile:
        field_new.Write(testfile)
        field_new = pybdsim.Field.Load(testfile)
        _os.remove(testfile)
    return field_new
    
def TransposeFieldMap2D(field):
    """
    Transpose the field map in x and y.
    """
    data = field.data
    data = data.transpose(1,0,2)
    field.data = data
    return field