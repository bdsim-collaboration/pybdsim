import numpy as _np
import pybdsim.Data as _Data

def BdsimElement2TransferMatrix(bdsfile,element,outputType="list"):
    """
    Calculates the Transfer Matrix of an element in a BDSIM beamline from an output (non-optical) 
    rootfile of the beamline by using a Singular Value Decomposition pseudo-inverse of a matrix of
    particle trajectories.
    
    Inputs:
    bdsfile - File to use to find the element.
    element - Number of element (must be >0, as requires an element before the element of interest).
    outputtype - "list", "dict" (default "list"). Controls output type, list returns a 16-element list of 
    floats of the matrix elements, dict returns a dict of labelled elements r11 through r44.
    """
    if element == 0:
        raise ValueError('Element to convert must have a preceding Element.')
    
    #take sampler data before and after element
    rootfile    = _Data.Load(bdsfile)
    priorund    = _Data.SamplerData(rootfile,element-1)
    postund     = _Data.SamplerData(rootfile,element)
    
    #put into matrix, transpose so each row is a single particle's co-ordinates.
    priormatrix = _np.asmatrix([priorund.data['x'], priorund.data['xp'], priorund.data['y'], priorund.data['yp']]).T
    lefthandx  = _np.asmatrix(postund.data['x']).T
    lefthandxp = _np.asmatrix(postund.data['xp']).T
    lefthandy  = _np.asmatrix(postund.data['y']).T
    lefthandyp = _np.asmatrix(postund.data['yp']).T
    
    #Pseudoinverse using SVD method
    righthandinverse = _np.linalg.pinv(priormatrix)
    
    #solve for matrix single row at a time for clarity
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
    elif outputType == "list":
        output = [xrow.item(0),xrow.item(1),xrow.item(2),xrow.item(3),
                  xprow.item(0),xprow.item(1),xprow.item(2),xprow.item(3),
                  yrow.item(0),yrow.item(1),yrow.item(2),yrow.item(3),
                  yprow.item(0),yprow.item(1),yprow.item(2),yprow.item(3)]
    else:
        raise TypeError('outputType: "'+outputType+'" invalid.')
        
    return output
