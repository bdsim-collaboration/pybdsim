import numpy as _np


class Field(object):
    """
    Base class used for common writing procedures for BDSIM field format.
    """
    def __init__(self, array=_np.array([]), columns=[]):
        self.data    = array
        self.columns = columns
        self.header  = {}

    def Write(self, fileName):
        f = open(fileName, 'w')
        for key,value in self.header.iteritems():
            f.write(str(key)+'> '+ str(value) + '\n')

        colStrings = map(lambda s: '%14s' % s, self.columns)
        colStrings[0] = colStrings[0].strip() # don't pad the first column title
        # a '!' denotes the column header line
        f.write('! '+ '\t'.join(colStrings)+'\n')
        
        # flatten all but last dimension - 3 field components
        nvalues = _np.shape(self.data)[-1]
        datal = self.data.reshape(-1,nvalues)
        for value in datal:
            strings = map(lambda x: '%.7E' % x, value)
            stringsFW = map(lambda s: '%14s' % s, strings)
            f.write('\t'.join(stringsFW) + '\n')

        f.close()


class Field1D(Field):
    """
    Utility class to write a numpy 1D array to BDSIM field format.

    Input 4x 1D numpy arrays for x, and the field components fx,fy,fz.
    This can be used for both electric and magnetic fields.

    Example::
    
    >>> a = Field1D(x,fx,fy,fz)
    >>> a.Write('outputFileName.dat')

    """
    def __init__(self,x,fx,fy,fz):
        data = _np.column_stack([x,fx,fy,fz])
        columns = ['X','Fx','Fy','Fz']
        super(Field1D, self).__init__(data,columns)
        self.header['xmin'] = _np.min(self.data[:,0])
        self.header['xmax'] = _np.max(self.data[:,0])
        self.header['nx']   = _np.shape(self.data)[0]

class Field2D(Field):
    """
    Utility class to write a 2D field map array to BDSIM field format.

    The array supplied should be 3 dimensional. Dimensions are:
    (x,y,value) where value has 5 elements [x,y,fx,fy,fz].  So a 100x50 (x,y)
    grid would have np.shape of (100,50,5).

    Example::
    
    >>> a = Field2D(data) # data is a prepared array
    >>> a.Write('outputFileName.dat')

    """
    def __init__(self,data):
        columns = ['X','Y','Fx','Fy','Fz']
        super(Field2D, self).__init__(data,columns)
        self.header['xmin'] = _np.min(self.data[:,0])
        self.header['xmax'] = _np.max(self.data[:,0])
        self.header['nx']   = _np.shape(self.data)[0]
        self.header['ymin'] = _np.min(self.data[:,:,1])
        self.header['ymax'] = _np.max(self.data[:,:,1])
        self.header['ny']   = _np.shape(self.data)[1]

class Field3D(Field):
    """
    Utility class to write a 3D field map array to BDSIM field format.

    The array supplied should be 4 dimensional. Dimensions are:
    (x,y,z,value) where value has 6 elements [x,y,z,fx,fy,fz].  So a 100x50x30 
    (x,y,z) grid would have np.shape of (100,50,30,6).
    
    Example::
    
    >>> a = Field3D(data) # data is a prepared array
    >>> a.Write('outputFileName.dat')

    """
    def __init__(self,data):
        columns = ['X','Y','Z','Fx','Fy','Fz']
        super(Field3D, self).__init__(data,columns)
        self.header['xmin'] = _np.min(self.data[:,0])
        self.header['xmax'] = _np.max(self.data[:,0])
        self.header['nx']   = _np.shape(self.data)[0]
        self.header['ymin'] = _np.min(self.data[:,:,1])
        self.header['ymax'] = _np.max(self.data[:,:,1])
        self.header['ny']   = _np.shape(self.data)[1]
        self.header['zmin'] = _np.min(self.data[:,:,2])
        self.header['zmax'] = _np.max(self.data[:,:,2])
        self.header['nz']   = _np.shape(self.data)[2]

class Field4D(Field):
    """
    Utility class to write a 4D field map array to BDSIM field format.

    The array supplied should be 5 dimensional. Dimensions are:
    (x,y,z,t,value) where value has 7 elements [x,y,z,t,fx,fy,fz]. So a 100x50x30x10
    (x,y,z,t) grid would have np.shape of (100,50,30,10,7).
    
    Example::
    
    >>> a = Field4D(data) # data is a prepared array
    >>> a.Write('outputFileName.dat')

    """
    def __init__(self,data):
        columns = ['X','Y','Z','T','Fx','Fy','Fz']
        super(Field4D, self).__init__(data,columns)
        self.header['xmin'] = _np.min(self.data[:,0])
        self.header['xmax'] = _np.max(self.data[:,0])
        self.header['nx']   = _np.shape(self.data)[0]
        self.header['ymin'] = _np.min(self.data[:,:,1])
        self.header['ymax'] = _np.max(self.data[:,:,1])
        self.header['ny']   = _np.shape(self.data)[1]
        self.header['zmin'] = _np.min(self.data[:,:,2])
        self.header['zmax'] = _np.max(self.data[:,:,2])
        self.header['nz']   = _np.shape(self.data)[2]
        self.header['tmin'] = _np.min(self.data[:,:,3])
        self.header['tmax'] = _np.max(self.data[:,:,3])
        self.header['nt']   = _np.shape(self.data)[3]
