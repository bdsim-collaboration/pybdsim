import numpy as _np
import pybdsim.Data

def BdsimElement2TransferMatrix(bdsfile,element,outputType="list"):
    
    """
    Calculates the Transfer Matrix of an element in a BDSIM beamline from an output (non-optical) 
    rootfile of the beamline by using a Singular Value Decomposition pseudoinverse of a matrix of 
    particle trajectories.
    
    Inputs:
    bdsfile - File to use to find the element.
    element - Number of element (must be >0, as requires an element before the element of interest).
    outputtype - "list", "dict" (default "list"). Controls output type, list returns a 16-element list of 
    floats of the matrix elements, dict returns a dict of labelled elements r11 through r44.
    """

    rootfile    = pybdsim.Data.Load(bdsfile)
    priorund    = pybdsim.Data.SamplerData(rootfile,element-1)
    postund     = pybdsim.Data.SamplerData(rootfile,element)
    priormatrix = _np.asmatrix([priorund.data['x'], priorund.data['xp'], priorund.data['y'], priorund.data['yp']]).T
    postmatrix  = _np.asmatrix([postund.data['x'], postund.data['xp'], postund.data['y'], postund.data['yp']]).T
    
    lefthandx  = _np.asmatrix(postund.data['x']).T
    lefthandxp = _np.asmatrix(postund.data['xp']).T
    lefthandy  = _np.asmatrix(postund.data['y']).T
    lefthandyp = _np.asmatrix(postund.data['yp']).T
    
    righthandinverse = _np.linalg.pinv(priormatrix)
    xrow  = righthandinverse * lefthandx
    xprow = righthandinverse * lefthandxp
    yrow  = righthandinverse * lefthandy
    yprow = righthandinverse * lefthandyp
   
    if outputType == "dict" :
        output = {
            "r11" : xrow.item(0),
            "r12" : xrow.item(1),
            "r13" : xrow.item(2),
            "r14" : xrow.item(3),
            "r21" : xprow.item(0),
            "r22" : xprow.item(1),
            "r23" : xprow.item(2),
            "r24" : xprow.item(3),
            "r31" : yrow.item(0),
            "r32" : yrow.item(1),
            "r33" : yrow.item(2),
            "r34" : yrow.item(3),
            "r41" : yprow.item(0),
            "r42" : yprow.item(1),
            "r43" : yprow.item(2),
            "r44" : yprow.item(3),
                 }
    
    elif outputType == "list" :
        output = [xrow.item(0),xrow.item(1),xrow.item(2),xrow.item(3),
                  xprow.item(0),xprow.item(1),xprow.item(2),xprow.item(3),
                  yrow.item(0),yrow.item(1),yrow.item(2),yrow.item(3),
                  yprow.item(0),yprow.item(1),yprow.item(2),yprow.item(3)]
           
    else:
        raise TypeError('outputType: "'+outputType+'" invalid.')
        
    return output
