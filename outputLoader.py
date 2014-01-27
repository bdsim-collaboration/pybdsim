import numpy as _np

_debug = False

class asciiData(_np.ndarray) : 
    def __new__(cls, input_array):
        if _debug : 
            print 'outputLoader.asciiData.__new__>'

        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        obj = _np.asarray(input_array).view(cls)
        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        if _debug : 
            print 'outputLoader.asciiData.__array_finalize__>'
        # see InfoArray.__array_finalize__ for comments
        if obj is None: return

    def __init__(self, data) : 
        if _debug : 
            print 'outputLoader.asciiData.__init__>'

        # keys for different columns 
        self._keys = dict() 
        self._keys['part']   = 0
        self._keys['energy'] = 1
        self._keys['x']      = 2
        self._keys['y']      = 3
        self._keys['z']      = 4 
        self._keys['xp']     = 5
        self._keys['yp']     = 6

        # assign data
        self.data = data
        
        # rounded z sampler locations
        z = self[:,self._keys['z']]
        round = 11
        self.sampzround = _np.round(z,round)                 
        self.sampz      = _np.unique(self.sampzround)
        self.nsamp      = len(self.sampz)

    def findSamplers(self, isamp = 0) : 
        '''Return array of true/false for a given sampler'''
        return self.sampzround == self.sampz[isamp]
    
    def getSamplerData(self, isamp = 0) : 
        '''Return slice of data for a given sampler'''
        if isamp < self.nsamp and isamp > -1 : 
            c = self.findSamplers(isamp) 
            return asciiData(self[c,:])
        else :
            raise IndexError('Index {0} is out of bounds for size {1}'.format(isamp,self.nsamp))

    def getSamplerDataArray(self) : 
        '''Return array of data divided'''     
        samplerDataList = list()
        for i in range(0,self.nsamp,1) : 
            samplerDataList.append(self.getSamplerData(i))                   
        return samplerDataList               

    def array(self) : 
        return _np.array(self)

class ascii : 
    def __init__(self) : 
        pass

    def load(self,filename):
        """
        Parses raw ASCII output from BDSIM into a numpy array.
        
        Example:
        Load('../path/to/my/file.txt')
        returns numpy array
        """

        print 'ascii.load>'

        dataSet = []
        
        f = open(filename,'r')
        lines = f.readlines()
        f.close()
        
        for line in lines[3:]:
            dataSet.append(map(_np.double,line.strip("\n").split()))
            
        dataSet=_np.array(dataSet)

        print 'ascii.load> end'

        return asciiData(dataSet)

