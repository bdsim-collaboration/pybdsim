import numpy as _np
import outputLoader as _ol
import matplotlib.pyplot as _plt

# make sure the interactive plotting is off
_plt.ioff()

class arrayDict : 
    def __init__(self, vars) : 
        self.dict = dict()
        for v in vars : 
            self.dict[v] = []
        
    def append(self,var,val) : 
        self.dict[var].append(val)

    def data(self,var) :
        return self.dict[var]

    def array(self) : 
        for k in keys : 
            self.dict[k] = _np.array(self.dict[k])

class analysis :
    def __init__(self,fileName) : 
        print 'analysis.__init__>'
        self._asciiLoader   = _ol.ascii() 
        self._data          = self._asciiLoader.load(fileName)
        self._samplerArray  = self._data.getSamplerDataArray()
        self._analysisArray = []

        self._dataDict      = dict()
        self._dataDict['npart']  = []
        self._dataDict['z']      = []
        self._dataDict['xmean']  = []
        self._dataDict['ymean']  = []
        self._dataDict['xpmean'] = []
        self._dataDict['ypmean'] = []
        self._dataDict['xrms']   = []
        self._dataDict['yrms']   = []
        self._dataDict['xprms']  = []
        self._dataDict['yprms']  = []
        
        self.run()

    def run(self) : 
        print 'analysis.run>'
        for sa in self._samplerArray : 
            a = asciiAnalysis(sa) 
            self._analysisArray.append(a) 
            self._dataDict['z'].append(a._zmean) 
            self._dataDict['npart'].append(a._npart)
            self._dataDict['xmean'].append(a._xmean)
            self._dataDict['ymean'].append(a._ymean)
            self._dataDict['xpmean'].append(a._xpmean)
            self._dataDict['ypmean'].append(a._ypmean)
            self._dataDict['xrms'].append(a._xrms)
            self._dataDict['yrms'].append(a._yrms)
            self._dataDict['xprms'].append(a._xprms)
            self._dataDict['yprms'].append(a._yprms)

    def plot(self,figureNr=1) :
        print 'analysis.plot>'
        fig = _plt.figure(figureNr)        
        fig.subplots_adjust(left=0.2,hspace = 0.5)

        ax1 = _plt.subplot(5,1,1)
        _plt.plot(self._dataDict['z'],self._dataDict['npart'],'-')    
        _plt.ylabel('$N_{\\textrm{particle}}$')
        ax1.yaxis.set_major_locator(_plt.MaxNLocator(3))        

        ax2 = _plt.subplot(5,1,2)
        _plt.plot(self._dataDict['z'],self._dataDict['xmean'],'-')    
        _plt.plot(self._dataDict['z'],self._dataDict['ymean'],'-') 
        _plt.ylabel('$\\overline{x},\\overline{y}/\\mu\\textrm{m}$')
        ax2.yaxis.set_major_locator(_plt.MaxNLocator(3))                

        ax3 = _plt.subplot(5,1,3)
        _plt.plot(self._dataDict['z'],self._dataDict['xpmean'],'-')    
        _plt.plot(self._dataDict['z'],self._dataDict['ypmean'],'-')
        _plt.ylabel('$\\overline{x^{\prime}},\\overline{y^{\prime}}$')    
        ax3.yaxis.set_major_locator(_plt.MaxNLocator(3))                

        ax4 = _plt.subplot(5,1,4)
        _plt.plot(self._dataDict['z'],self._dataDict['xrms'],'-')
        _plt.plot(self._dataDict['z'],self._dataDict['yrms'],'-')
        _plt.ylabel('$\sigma_{x,y}/\\mu\\textrm{m}$')
        ax4.yaxis.set_major_locator(_plt.MaxNLocator(3))                        

        ax5 = _plt.subplot(5,1,5)
        _plt.plot(self._dataDict['z'],self._dataDict['xprms'],'-')
        _plt.plot(self._dataDict['z'],self._dataDict['yprms'],'-')
        _plt.ylabel('$\sigma_{xp,yp}$')
        ax5.yaxis.set_major_locator(_plt.MaxNLocator(3))                
        _plt.xlabel('$S$/m')

        _plt.show()
    
class asciiAnalysis : 
    def __init__(self, data) : 
        self._data = data

        self._npart = len(self._data[:,self._data._keys['x']])
        self._zmean = self._data[:,self._data._keys['z']].mean()
        self._xmean = self._data[:,self._data._keys['x']].mean()
        self._ymean = self._data[:,self._data._keys['y']].mean()
        self._xpmean= self._data[:,self._data._keys['xp']].mean()
        self._ypmean= self._data[:,self._data._keys['yp']].mean()    
        self._xrms  = self._data[:,self._data._keys['x']].std()
        self._yrms  = self._data[:,self._data._keys['y']].std()
        self._xprms = self._data[:,self._data._keys['xp']].std()
        self._yprms = self._data[:,self._data._keys['yp']].std()    
            
    def plotXY(self, hist=True) : 
        if hist : 
            _plt.hist2d(self._data[:,self._data._keys['x']],self._data[:,self._data._keys['y']],30)
        else :
            _plt.plot(self._data[:,self._data._keys['x']],self._data[:,self._data._keys['y']],"+")        
        _plt.xlabel("$x\;\mu m$")
        _plt.ylabel("$y\;\mu m$")
            
    def plotXXp(self) : 
        _plt.plot(self._data[:,self._data._keys['x']],self._data[:,self._data._keys['xp']],"+")
        _plt.xlabel("$x\;\mu m$")
        _plt.ylabel("$x^{\prime}$")

    def plotYYp(self) : 
        _plt.plot(self._data[:,self._data._keys['y']],self._data[:,self._data._keys['yp']],"+")        
        _plt.xlabel("$y\;\mu m$")
        _plt.ylabel("$y^{\prime}$")

    def plotTE(self) : 
        _plt.xlabel("$T$ s")
        _plt.ylabel("$E$ MeV")        

    def plotAll(self,figureNr = 2) :

        _plt.figure(figureNr)
        _plt.clf()

        _plt.subplot(2,2,1)
        self.plotXY()

        _plt.subplot(2,2,2)
        self.plotXXp()

        _plt.subplot(2,2,3)
        self.plotYYp()

        _plt.subplot(2,2,4)
        self.plotTE()
        
        _plt.show()
        
