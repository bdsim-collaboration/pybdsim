import numpy as _np
import pymadx
import Builder

def IndexOfElement(tfsinstance,markername):
    t = tfsinstance
    names = list(t.data['NAME'])
    try:
        i = names.index(markername)
    except ValueError:
        i = 0
        print 'Unknown element name'
    return i

def MadxTfs2Gmad(inputfile,outputfile,startname=None,endname=None,ignorezerolengthitems=True,samplers='all'):
    """
    MadxTfs2Gmad - convert a madx twiss output file (.tfs) into a gmad input file for bdsim

    MadxTfs2Gamd(inputfile,outputfile,startname=None,endname=None,ignorezerolengthitems=True,samplers=None)

    inputfile  - path to the input file
    outputfile - requested output file
    startname  - the name (exact string match) of the lattice element to start the machine at
    stopname   - the name (exact string match) of the lattice element to stop the machine at

    ignorezerolengthitems=True    - nothing can be zero length in bdsim as real objects 
                                    of course have some finite size.  Markers, etc are 
                                    acceptable but for large lattices this can slow things down.
                                    True allows to ignore these altogether, which doesn't
                                    affect the length of the machine.

    samplers   - can specify where to set samplers - options are None or 'all'.

    """
    izlis = ignorezerolengthitems
    madx                    = pymadx.MadX.Tfs(inputfile)
    nitems = madx.nitems

    kws = {} #extra parameters TO BE FINISHED
    
    #iterate through items in tfs and construct machine
    a = Builder.Machine()
    elementtype = madx.data['KEYWORD']
    
    #prepare index for iteration:
    if startname == None:
        startindex = 0
    else:
        startindex = IndexOfElement(madx,startname)
    if endname   == None:
        stopindex = nitems #this is 1 larger, but ok as range will stop at n-step -> step=1, range function issue
    else:
        stopindex  = IndexOfElement(madx,endname)
    if stopindex <= startindex:
        print 'stopindex <= startindex'
        stopindex = startindex + 1
        
    for i in range(startindex,stopindex):
        t    = madx.data['KEYWORD'][i]
        name = ''.join(e for e in madx.data['NAME'][i] if e.isalnum())
        l    = madx.data['L'][i]
        if l == 0 and izlis == True:
            pass
        elif t == 'DRIFT':
            a.AddDrift(name,l,**kws)
        elif t == 'HKICKER':
            a.AddHKicker(name,l,**kws)
        elif t == 'INSTRUMENT':
            #most 'instruments' are just markers
            if l == 0:
                a.AddMarker(name)
            else:
                a.AddDrift(name,l,**kws)
        elif t == 'MARKER':
                a.AddMarker(name)
        elif t == 'MONITOR':
            #most monitors are just markers
            if l == 0:
                a.AddMarker(name)
            else:
                a.AddMarker(name)
                #a.AddDrift(name,l,**kws)
        elif t == 'MULTIPOLE':
            #figure out which components are non zero
            #a.AddMultipole(name,l,)
            #TO BE FINISHED
            a.AddDrift(name,l,**kws)
        elif t == 'OCTUPOLE':
            #TO BE FINISHED
            a.AddDrift(name,l,**kws)
        elif t == 'PLACEHOLDER':
            if l == 0:
                a.AddMarker(name)
            else:
                a.AddDrift(name,l,**kws)
        elif t == 'QUADRUPOLE':
            k1 = madx.data['K1L'][i] / l
            a.AddQuadrupole(name,l,k1=k1,**kws)
        elif t == 'RBEND':
            #IS RBEND IMPLEMENTED IN BDSIM???
            a.AddDipole(name,'sbend',l,angle=madx.data['ANGLE'][i],**kws)
        elif t == 'RCOLLIMATOR':
            #only use xsize as only have half gap
            try : 
                if coll.has_key(name):
                    kws['material'] = coll[name]['bdsim_material']
                if gaps.has_key(name):
                    xsize = gaps[name]['halfgap'] * 2.0
                    angle = gaps[name]['angle']
                else:
                    xsize = opencollimatorsetting
                    angle = 0.0
                    ysize = opencollimatorsetting
            except NameError :  # if there is no coll or gaps structures 
                opencollimatorsetting = 10.0
                xsize = opencollimatorsetting
                ysize = opencollimatorsetting
                angle = 0.0
                
            a.AddRColAngled(name,l,xsize,ysize,angle,**kws)
            #a.AddRCol(name,l,xsize,ysize,**kws)
        elif t == 'RFCAVITY':
            a.AddDrift(name,l,**kws)
        elif t == 'SBEND':
            a.AddDipole(name,'sbend',l,angle=madx.data['ANGLE'][i],**kws)
        elif t == 'SEXTUPOLE':
            k2 = madx.data['K2L'][i] / l
            a.AddSextupole(name,l,k2=k2,**kws)
        elif t == 'SOLENOID':
            a.AddDrift(name,l,**kws)
        elif t == 'TKICKER':
            a.AddDrift(name,l,**kws)
        elif t == 'VKICKER':
            a.AddDrift(name,l,**kws)
        else:
            if l == 0:
                a.AddMarker(name)
            else:
                a.AddDrift(name,l)

    a.SetSamplers(samplers)
    a.WriteLattice(outputfile)
    
def InterrogateLattice(tfsfilename):
    """
    InterrogateLattice(tfsfilename)

    return populations,populationsbynumber

    two dictionaries with the keyword arguement and the number
    of items in the MADX tfs file supplied that match that
    keyword.

    """
    
    a = pymadx.MadX.Tfs(tfsfilename)
    keys = set(a.data['KEYWORD'])
    nitems = len(a.data['NAME'])
    print 'Filename           > ',tfsfilename
    print 'Number of Elements > ',nitems
    print 'Lattice Length     > ',a.data['S'][-1]+a.data['L'][-1]+'m'
    populations = {key:0 for key in keys}
    for i in range(nitems):
        populations[a.data['KEYWORD'][i]] += 1
    #flip dictionary around
    popsr = zip([populations[key] for key in populations.keys()],populations.keys())
    #sort it so we can see what's the most common element
    popsr = sorted(popsr)[::-1]
    #print feedback
    print 'Type'.ljust(15)+'#'.rjust(len(str(max(popsr)[0])))
    for item in popsr:
        print item[1].ljust(15,'.')+str(item[0]).rjust(len(str(max(popsr)[0])),'.')
    return populations,popsr
