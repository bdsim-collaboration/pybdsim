"""
Survey() - survey a gmad lattice, plot element coords
Loader() - load a gmad file using the comipled bdsim parser

"""

import ctypes as _ctypes
import ctypes as __ctypes
from ctypes.util import find_library as _find_library
import numpy as _np
import matplotlib.pyplot as _plt


class Survey:
    """
    Survey - load a gmad lattice and have a look

    Example:
    a = Survey()
    a.Load('mylattice.gmad')
    a.Plot()
    
    """
    def __init__(self) : 
        self._x_current = 0 
        self._y_current = 0
        self._theta     = _np.pi
        self._names     = []
        self._beamline  = []
        self._x_coords  = [] 
        self._y_coords  = []
        self._lentotal  = 0

    def Load(self, fileName) : 
        self._file = Loader() 
        self._file.Load(fileName) 
        
        nelement = self._file._parserLib.get_nelements()
        
        for i in range(0,nelement,1) : 
            name   = self._file._parserLib.get_name(i) 
            length = self._file._parserLib.get_length(i)
            angle  = self._file._parserLib.get_angle(i)
            self._names.append(name)
            self.Step(angle,length)
            i += 1    
               
    def Step(self,angle,length):
        self._theta += angle
        dx    = length * _np.cos(self._theta)
        dy    = length * _np.sin(self._theta)
        self._lentotal += length
        
        x_new = self._x_current - dx
        y_new = self._y_current - dy
        self._beamline.append([[self._x_current,x_new],[self._y_current,y_new]])
        self._x_current = x_new
        self._y_current = y_new
        self._x_coords.append(x_new)
        self._y_coords.append(y_new)        

    def FinalDiff(self):
        dx = self._beamline[-1][0][1] - self._x_current
        dy = self._beamline[-1][1][1] - self._y_current
        print 'Final dx ',dx
        print 'Final dy ',dy
        
    def Plot(self) : 
        _plt.figure()
        _plt.plot(self._x_coords,self._y_coords,'b.')
        _plt.plot(self._x_coords,self._y_coords,'b-')
        _plt.xlabel('X (m)')
        _plt.ylabel('Y (m)')
        _plt.show()

    def CompareMadX(self, fileName) : 
        import pymadx as _pymadx
        
        mxs = _pymadx.Survey()
        mxs.Load(fileName) 

        self.Plot()

        _plt.plot(mxs._x_coords,mxs._y_coords,'rx')
        _plt.plot(mxs._x_coords,mxs._y_coords,'r-')
        _plt.show()        
        
    def FindClosestElement(self, coord) : 
        arr = _np.arange(0,len(self._x_coords),1) 
        xdiff = _np.array(self._x_coords)-coord[0]
        ydiff = _np.array(self._y_coords)-coord[1]
        d     = _np.sqrt(xdiff**2+ydiff**2)
        print arr[d == min(d)]
            

class Loader:
    """
    Loader - bare bones loader for gmad files
    
    Uses compiled bdsim library

    NOTE - currently uses absolute path - need to fix

    """
    def __init__(self) :
        self._LoadLib()
    
    def _LoadLib(self):
        libname = 'gmadShared'
        libpath = '/usr/local/lib'

        test1,test2,test3 = False, False, False
        
        #test1 - try general find function
        libpatht1 = _find_library(libname)
        if libpatht1 != None:
            test1 = True
        
        #test2 - try /opt/local/lib/libgmadShared.so
        try:
            fulllibname = 'lib'+libname+'.so'
            self._parserLib = _ctypes.cdll.LoadLibrary('/usr/local/lib/'+fulllibname)
            test2 = True
        except OSError:
            pass
        
        #test3 - try /opt/local/lib/libgmadShared.dylib
        try:
            fulllibname = 'lib'+libname+'.dylib'
            self._parserLib = _ctypes.cdll.LoadLibrary('/usr/local/lib/'+fulllibname)
            test3 = True
        except OSError:
            pass

        if [test1,test2,test3].count(True) == 0:
            print 'LoadLib - cannot find libgmadShared - check paths'
            raise OSError('LoadLib - cannot find libgmadShared - check paths')
        elif test1 == True:
            self._parserLib = libpatht1
        else:
            pass

        #self._parserLibFileName = "libgmadShared.dylib"
        #self._libpath           = '/usr/local/lib/'
        #self._parserLib = _ctypes.cdll.LoadLibrary(self._libpath+self._parserLibFileName)
        
        self._parserLib.get_name.restype    = _ctypes.c_char_p
        self._parserLib.get_name.argtypes   = [_ctypes.c_int]
        self._parserLib.get_type.restype    = _ctypes.c_short
        self._parserLib.get_type.argtypes   = [_ctypes.c_int]    
        self._parserLib.get_length.restype  = _ctypes.c_double
        self._parserLib.get_length.argtypes = [_ctypes.c_int]
        self._parserLib.get_angle.restype   = _ctypes.c_double
        self._parserLib.get_angle.argtypes  = [_ctypes.c_int]
        
    def Load(self, fileName) :
        self._parserLib.gmad_parser_c(fileName)
    
    def GetElement(self, i) : 
        name   = self._parserLib.get_name(i) 
        type   = self._parserLib.get_type(i) 
        length = self._parserLib.get_length(i)
        angle  = self._parserLib.get_angle(i)
        
        d = dict() 
        d['name']   = name
        d['type']   = type
        d['length'] = length
        d['angle']  = angle
        
        return d

    def ParseLattice(self) : 
        '''Parse entire lattice to python''' 
        nelement = self._parserLib.get_nelements()
        self._lattice = [] 
        suml = 0 
        for i in range(0,nelement,1) : 
            d = self.GetElement(i) 
            d['suml'] = suml 
            self._lattice.append(d)
            suml += d['length']
        
    def GetElementByName(self, name) :
        pass

    def PrintToScreen(self) :
        '''Print entire lattice to screen''' 
        nelement = self._parserLib.get_nelements()

        for i in range(0,nelement,1) : 
            name   = self._parserLib.get_name(i) 
            type   = self._parserLib.get_type(i) 
            length = self._parserLib.get_length(i)
            angle  = self._parserLib.get_angle(i)
            print i,name,type,length,angle        
    
    def PrintZeroLength(self) : 
        '''Print elements with zero length with s location''' 
        
        nelement = self._parserLib.get_nelements()


        types = [] 
        sumlength = 0 

        for i in range(0,nelement,1) : 
            name   = self._parserLib.get_name(i) 
            type   = self._parserLib.get_type(i) 
            length = self._parserLib.get_length(i)
            angle  = self._parserLib.get_angle(i)
            sumlength += length

            if length == 0.0 and type != 41 : 
                types.append(type)
#                print name,type,length,sumlength
            
        print _np.unique(types)
