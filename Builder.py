# pybdsim.Builder - tools to build bdsim lattices
# Version 1.0
# L. Nevay
# laurie.nevay@rhul.ac.uk

"""
Builder

Build generic machines for bdsim. You can create a lattice
using one of the predefined simple lattices or by adding
many pieces together of your own design. Finally, output
the gmad files required.

Classes:
Element - beam line element that always has name,type and length
Machine - a list of elements

"""

import _General
from   decimal import Decimal
import math
import time

def _IsFloat(stringtotest):
    try:
        float(stringtotest)
        return True
    except ValueError:
        return False

bdsimcategories = [
    'marker',
    'drift',
    'rbend',
    'sbend',
    'quadrupole',
    'sextupole',
    'octupole',
    'multipole',
    'rfcavity',
    'rcol',
    'ecol',
    'muspoiler',
    'solenoid',
    'hkick',
    'vkick',
    'transform3d',
    'element',
    'line',
    'matdef',
    'laser',
    'gas',
    'spec'
    ]

class Element(dict):
    """
    Element - a beam element class - inherits dict

    Element(name,type,**kwargs)
    
    A beam line element must ALWAYs have a name, and type.
    The keyword arguments are specific to the type and are up to
    the user to specify.

    Numbers are converted to a python Decimal type to provide 
    higher accuracy in the representation of numbers - 15 
    decimal places are used. 
    """
    def __init__(self, name, category, **kwargs):
        if category not in bdsimcategories:
            raise ValueError("Not a valid BDSIM element type")
        dict.__init__(self)
        self.name        = str(name)
        self.category    = str(category)
        self.length      = 0.0 #for bookeeping only
        self['name']     = self.name
        self['category'] = self.category
        self._keysextra = []
        for key,value in kwargs.iteritems():
            if type(value) == tuple:
                #use a tuple for (value,units)
                self[key] = (Decimal(str(value[0])),value[1])
            elif _IsFloat(value):
                #just a number
                self[key] = Decimal(str(value))
            else:
                #must be a string
                self[key] = '"'+value+'"'
            self._keysextra.append(str(key)) #order preserving
        if 'l' in self:
            if type(self['l']) == tuple:
                ll = self['l'][0]
            else:
                ll = self['l']
            self.length += float(ll)
    
    def keysextra(self):
        #so behaviour is similar to dict.keys()
        return self._keysextra

    def __repr__(self):
        s = ''
        s += self.name + ': '
        s += self.category
        if len(self._keysextra) > 0:
            for key in self._keysextra:
                if type(self[key]) == tuple:
                    s += ', ' + key + '=' + str(self[key][0]) + '*' + str(self[key][1])
                else:
                    s += ', ' + key + '=' + str(self[key])
        s += ';\n'
        return s

class Line(list):
    def __init__(self,name,*args):
        for item in args[0]:
            if type(item) != Element:
                raise TypeError("Line is a list of Elements")
        list.__init__(self,*args)
        self.name   = name
        self.length = 0.0 
        for item in args[0]:
            self.length += item.length
        
    def __repr__(self):
        s = ''
        for item in self:
            s += str(item)+'\n' #uses elements __repr__ function
        s += self.name+ ': line=('
        s += ', '.join([item.name for item in self]) + ');\n'
        return s

    def DefineConstituentElements(self):
        s = ''
        for item in self:
            s += str(item) #uses elements __repr__ function
        return s

class Sampler:
    def __init__(self,name):
        self.name = name

    def __repr__(self):
        return 'sample, range='+self.name+';\n'

class Machine1:
    def __init__(self,verbose=False):
        self.verbose   = verbose
        self.sequence  = []
        self.elements  = []
        self.elementsd = {}
        self.samplers  = []
        self.length    = 0.0
        self.angint    = 0.0

    def __repr__(self):
        s = ''
        s += 'pybdism.Builder.Machine instance\n'
        s += str(len(self.sequence)) + ' items in sequence\n'
        s += str(len(self.elements)) + ' unique elements defined\n'
        return s

    def __iter__(self):
        self._iterindex = -1
        return self

    def next(self):
        if self._iterindex == len(self.sequence)-1:
            raise StopIteration
        self._iterindex += 1
        return self.elementsd[self.sequence[self._iterindex]]
        
    def __getitem__(self,name):
        if _IsFloat(name):
            return self.elementsd[self.sequence[name]]
        else:
            return self.elementsd[name]

    def __len__(self):
        return len(self.elementsd.keys())

    def Append(self,object):
        if type(object) not in (Element,Line):
            raise TypeError("Only Elements or Lines can be added to the machine")
        elif object.name not in self.sequence:
            #hasn't been used before - define it
            if type(object) is Line:
                for element in object:
                    self.elements.append(element)
                    self.elementsd[element.name] = element
                self.elements.append(object)
                self.elementsd[object.name] = object
            else:
                self.elements.append(object)
                self.elementsd[object.name] = object
        #finally add it to the sequence
        self.sequence.append(object.name)
        self.length += object.length

    def WriteLattice(self,filename,verbose=False):
        if self.verbose or verbose:
            WriteLattice1(self,filename,True)
        else:
            WriteLattice1(self,filename,False)

    def AddMarker(self, name='mk'):
        if self.verbose:
            print 'AddMarker> ',name
        self.Append(Element(name,'marker'))
    
    def AddDrift(self, name='dr', length=0.1, **kwargs):
        if self.verbose:
            print 'AddDrift>  ',name,' ',length,' ',kwargs
        if length < 1e-12:
            self.AddMarker(name)
        else:
            self.Append(Element(name,'drift',l=length,**kwargs))
          
    def AddDipole(self, name='dp', category='sbend', length=0.1, angle=None, b=None, **kwargs):
        """
        AddDipole(category='sbend')

        category - 'sbend' or 'rbend' - sector or rectangular bend

        """
        if (angle==None) and (b==None):
            raise TypeError('angle or b must be specified for an sbend')
        elif angle != None:
            self.Append(Element(name,category,l=length,angle=angle,**kwargs))
        else:
            self.Append(Element(name,category,l=length,B=b,**kwargs))

    def AddQuadrupole(self, name='qd', length=0.1, k1=0.0, **kwargs):
        self.Append(Element(name,'quadrupole',l=length,k1=k1,**kwargs))
        
    def AddSextupole(self, name='sx', length=0.1, k2=0.0, **kwargs):
        self.Append(Element(name,'sextupole',l=length,k2=k2,**kwargs))

    def AddOctupole(self, name='oc', length=0.1, k3=0.0, **kwargs):
        self.Append(Element(name,'octupole',l=length,k3=k3,**kwargs))

    def AddMultipole(self, name='mp', length=0.1, knl=(0), ksl=(0), **kwargs):
        if length > 1e-12:
            self.AddDrift(name,length)
        else:
            self.AddMarker(name)

    def AddRF(self, name='arreff', length=0.1, gradient=10, **kwargs):
        """
        AddRF(name,length,graident,**kwargs)
        
        length in metres
        gradient in MV / m
        """
        self.AddDrift(name,length)
        self.Append(Element(name,'rfcavity',l=length,gradient=gradient,**kwargs))
        
    def AddRCol(self, name='rc', length=0.1, xsize=0.1, ysize=0.1, **kwargs):
        self.Append(Element(name,'rcol',l=length,xsize=xsize,ysize=ysize,material=kwargs['material']))
    
    def AddTransform3D(self, name='t3d', **kwargs):
        if len(kwargs.keys()) == 0:
            pass
        else:
            self.Append(Element(name,'transform3d',**kwargs))
        
    def AddRColAngled(self, name='rc', length=0.1, xsize=0.1, ysize=0.1, angle=0.1745329, **kwargs):
        """
        default angle is 10 degrees in radians (0.1745329)

        """
        self.AddTransform3D(name+'_angle_pos', psi=angle)
        #self.AddDrift(name,length)
        self.Append(Element(name,'rcol',l=length,xsize=xsize,ysize=ysize,**kwargs))
        self.AddTransform3D(name+'_angle_neg', psi=-1*angle)

    def AddRColAngledTilted(self, name='rc', length=0.1, xsize=0.1, ysize=0.1, angle=0.1745329, tilt=0.01, **kwargs):
        self.AddDrift(name,length)

    def AddECol(self, name='ec', length=0.1, xsize=0.1, ysize=0.1, **kwargs):
        self.Append(Element(name,'ecol',l=length,xsize=xsize,ysize=ysize,**kwargs))
        
    def AddHKicker(self, name='hk', length=0.1, **kwargs):
        self.AddDrift(name,length)
        #self.Append(Element(name,'hkick',l=length,**kwargs))

    def AddVKicker(self, name='vk', length=0.1, **kwargs):
        self.AddDrift(name,length)
        #self.Append(Element(name,'vkick',l=length,**kwargs))

    def AddFodoCell(self, basename='fodo', magnetlength=1.0, driftlength=4.0,kabs=1.0,**kwargs):
        """
        AddFodoCell(basename,magnetlength,driftlength,kabs,**kwargs)
        basename     - the basename for the fodo cell beam line elements
        magnetlength - length of magnets in metres
        driftlength  - length of drift segment in metres
        kabs         - the absolute value of the quadrupole strength - alternates between magnets

        **kwargs are other parameters for bdsim - ie material='Fe'
        """
        names = [basename+extrabit for extrabit in ['_qfa','_dra','_qda','_drb','_qfb']]
        items = (
            Element(names[0],'quadrupole',l=magnetlength/2.0,k1=kabs,**kwargs),
            Element(names[1],'drift',l=driftlength),
            Element(names[2],'quadrupole',l=magnetlength,k1=-1.0*kabs,**kwargs),
            Element(names[3],'drift',l=driftlength),
            Element(names[4],'quadrupole',l=magnetlength/2.0,k1=kabs,**kwargs)
            )
        self.Append(Line(basename,items))

    def AddFodoCellSplitDrift(self, basename='fodo', magnetlength=1.0, driftlength=4.0, kabs=1.0,nsplits=10, **kwargs):
        """
        AddFodoCellSplitDrift(basename,magnetlength,driftlength,kabs,nsplits,**kwargs)
        basename - the basename for the fodo cell beam line elements
        magnetlength - length of magnets in metres
        driftlength  - length of drift segment in metres
        kabs         - the absolute value of the quadrupole strength - alternates between magnets
        nsplits      - number of segments drift length is split into 

        Will add qf quadrupole of strength +kabs, then drift of l=driftlength split into 
        nsplit segments followed by a qd quadrupole of strength -kabs and the same pattern
        of drift segments.
        
        nsplits will be cast to an even integer for symmetry purposes.

        **kwargs are other parameters for bdsim - ie aper=0.2
        """
        nsplits = _General.NearestEvenInteger(nsplits)
        splitdriftlength = driftlength / float(nsplits)
        maxn    = int(len(str(nsplits)))
        self.Append(Element(basename+'_qfa','quadrupole',l=magnetlength/2.0,k1=kabs,**kwargs))
        for i in range(nsplits):
            self.Append(Element(basename+'_d'+str(i).zfill(maxn),'drift',l=splitdriftlength))
        self.Append(Element(basename+'_qd','quadrupole',l=magnetlength,k1=-1.0*kabs,**kwargs))
        for i in range(nsplits):
            self.Append(Element(basename+'_d'+str(i).zfill(maxn),'drift',l=splitdriftlength))
        self.Append(Element(basename+'_qfb','quadrupole',l=magnetlength/2.0,k1=kabs,**kwargs))

    def AddFodoCellMultiple(self, basename='fodo', magnetlength=1.0, driftlength=4.0, kabs=1.0, ncells=2, **kwargs):
        ncells = int(ncells)
        maxn   = int(len(str(ncells)))
        for i in range(ncells):
            cellname = basename+'_'+str(i).zfill(maxn)
            self.AddFodoCell(cellname,magnetlength,driftlength,kabs,**kwargs)

    def AddFodoCellSplitDriftMultiple(self, basename='fodo', magnetlength=1.0, driftlength=4.0, kabs=1.0, nsplits=10, ncells=2, **kwargs):
        ncells = int(ncells)
        maxn   = int(len(str(ncells)))
        for i in range(ncells):
            cellname = basename+'_'+str(i).zfill(maxn)
            self.AddFodoCellSplitDrift(cellname,magnetlength,driftlength,kabs,nsplits=10,**kwargs)
            
    def AddSampler(self,*elementnames):
        if elementnames[0] == 'all':
            for element in self.elements:
                #remember we can only have samplers on uniquely
                #named elements (for now)
                self.samplers.append(Sampler(element.name))
        else:
            for element in elementnames[0]:
                if element not in self.elements:
                    raise ValueError(elementname+" is not a valid element in this machine")
                else:
                    self.samplers.append(Sampler(element))


####################################################################################################


class Machine(list):
    """
    Machine()

    Generic machine class. Allows you to create your own 
    lattice easily either by adding several components or
    choosing to use a premade builder.

    instance.line is a list of beam line elements

    each element is a list of [name,type,length...other parameters]

    """
    def __init__(self, verbose=False):
        list.__init__(self)
        self.nelements     = int(0)
        self.samplers      = []
        self.totallength   = Decimal(str(0.0))
        self._elementindex = int(0)
        self._maxindexpow  = 5
        self.verbose       = verbose

    def append(self, object):
        if type(object) == Element:
            object.name = object.name + '_' + str(self._elementindex).zfill(self._maxindexpow)
            object['name'] = object['name'] + '_' + str(self._elementindex).zfill(self._maxindexpow)
        list.append(self,object)
        self.nelements     += 1
        self.totallength   += object.length
        self._elementindex += 1
       
    def WriteLattice(self, filename, verbose=False):
        if self.verbose==True or verbose == True:
            v = True
        else:
            v = False
        WriteLattice(self,filename,v)
    
    def AddMarker(self, name='mk'):
        if self.verbose:
            print 'AddMarker> ',name
        self.append(Element(name,'marker',0.0))
    
    def AddDrift(self, name='dr', length=0.1, **kwargs):
        if self.verbose:
            print 'AddDrift>  ',name,' ',length,' ',kwargs
        if length < 1e-12:
            self.AddMarker(name)
        else:
            self.append(Element(name,'drift',length,**kwargs))
          
    def AddDipole(self, name='dp', category='sbend', length=0.1, angle=None, b=None, **kwargs):
        """
        AddDipole(category='sbend')

        category - 'sbend' or 'rbend' - sector or rectangular bend

        """
        if (angle==None) and (b==None):
            raise TypeError('angle or b must be specified for an sbend')
        elif angle != None:
            self.append(Element(name,category,length,angle=angle,**kwargs))
        else:
            self.append(Element(name,category,length,B=b,**kwargs))

    def AddQuadrupole(self, name='qd', length=0.1, k1=0.0, **kwargs):
        self.append(Element(name,'quadrupole',length,k1=k1,**kwargs))
        
    def AddSextupole(self, name='sx', length=0.1, k2=0.0, **kwargs):
        self.append(Element(name,'sextupole',length,k2=k2,**kwargs))

    def AddOctupole(self, name='oc', length=0.1, k3=0.0, **kwargs):
        self.append(Element(name,'octupole',length,k3=k3,**kwargs))

    def AddMultipole(self, name='mp', length=0.1, knl=(0), ksl=(0), **kwargs):
        if length > 1e-12:
            self.AddDrift(name,length)
        else:
            self.AddMarker(name)

    def AddRF(self, name='arreff', length=0.1, gradient=10, **kwargs):
        """
        AddRF(name,length,graident,**kwargs)
        
        length in metres
        gradient in MV / m
        """
        self.append(Element(name,'rfcavity',length,gradient=gradient,**kwargs))
        
    def AddRCol(self, name='rc', length=0.1, xsize=0.1, ysize=0.1, **kwargs):
        self.append(Element(name,'rcol',length,xsize=xsize,ysize=ysize,**kwargs))
    
    def AddTransform3D(self, name='t3d', **kwargs):
        if len(kwargs.keys()) == 0:
            pass
        else:
            length=0.0
            self.append(Element(name,'transform3d',length, **kwargs))
        
    def AddRColAngled(self, name='rc', length=0.1, xsize=0.1, ysize=0.1, angle=0.1745329, **kwargs):
        """
        default angle is 10 degrees in radians (0.1745329)

        """
        self.AddTransform3D(name+'_angle_pos', psi=angle)
        self.append(Element(name,'rcol',length,xsize=xsize,ysize=ysize,**kwargs))
        self.AddTransform3D(name+'_angle_neg', psi=-1*angle)

    def AddRColAngledTilted(self, name='rc', length=0.1, xsize=0.1, ysize=0.1, angle=0.1745329, tilt=0.01, **kwargs):
        self.AddDrift(name,length)

    def AddECol(self, name='ec', length=0.1, xsize=0.1, ysize=0.1, **kwargs):
        self.append(Element(name,'ecol',length,xsize=xsize,ysize=ysize,**kwargs))
        
    def AddHKicker(self, name='hk', length=0.1, **kwargs):
        self.append(Element(name,'hkick',length,**kwargs))

    def AddVKicker(self, name='vk', length=0.1, **kwargs):
        self.append(Element(name,'vkick',length,**kwargs))

    def AddFodoCell(self, basename='fodo', magnetlength=1.0, driftlength=4.0,kabs=1.0,**kwargs):
        """
        AddFodoCell(basename,magnetlength,driftlength,kabs,**kwargs)
        basename     - the basename for the fodo cell beam line elements
        magnetlength - length of magnets in metres
        driftlength  - length of drift segment in metres
        kabs         - the absolute value of the quadrupole strength - alternates between magnets

        **kwargs are other parameters for bdsim - ie material='W'
        """
        self.append(Element(basename+'_qfa','quadrupole',magnetlength/2.0,k1=kabs,**kwargs))
        self.append(Element(basename,'drift',driftlength))
        self.append(Element(basename+'_qd','quadrupole',magnetlength,k1=-1.0*kabs,**kwargs))
        self.append(Element(basename,'drift',driftlength))
        self.append(Element(basename+'_qfb','quadrupole',magnetlength/2.0,k1=kabs,**kwargs))

    def AddFodoCellSplitDrift(self, basename='fodo', magnetlength=1.0, driftlength=4.0, kabs=1.0,nsplits=10, **kwargs):
        """
        AddFodoCellSplitDrift(basename,magnetlength,driftlength,kabs,nsplits,**kwargs)
        basename - the basename for the fodo cell beam line elements
        magnetlength - length of magnets in metres
        driftlength  - length of drift segment in metres
        kabs         - the absolute value of the quadrupole strength - alternates between magnets
        nsplits      - number of segments drift length is split into 

        Will add qf quadrupole of strength +kabs, then drift of l=driftlength split into 
        nsplit segments followed by a qd quadrupole of strength -kabs and the same pattern
        of drift segments.
        
        nsplits will be cast to an even integer for symmetry purposes.

        **kwargs are other parameters for bdsim - ie aper=0.2
        """
        nsplits = _General.NearestEvenInteger(nsplits)
        splitdriftlength = driftlength / float(nsplits)
        maxn    = int(len(str(nsplits)))
        self.append(Element(basename+'_qfa','quadrupole',magnetlength/2.0,k1=kabs,**kwargs))
        for i in range(nsplits):
            self.append(Element(basename+'_d'+str(i).zfill(maxn),'drift',length=splitdriftlength))
        self.append(Element(basename+'_qd','quadrupole',magnetlength,k1=-1.0*kabs,**kwargs))
        for i in range(nsplits):
            self.append(Element(basename+'_d'+str(i).zfill(maxn),'drift',length=splitdriftlength))
        self.append(Element(basename+'_qfb','quadrupole',magnetlength/2.0,k1=kabs,**kwargs))

    def AddFodoCellMultiple(self, basename='fodo', magnetlength=1.0, driftlength=4.0, kabs=1.0, ncells=2, **kwargs):
        ncells = int(ncells)
        maxn   = int(len(str(ncells)))
        for i in range(ncells):
            cellname = basename+'_'+str(i).zfill(maxn)
            self.AddFodoCell(cellname,magnetlength,driftlength,kabs,**kwargs)

    def AddFodoCellSplitDriftMultiple(self, basename='fodo', magnetlength=1.0, driftlength=4.0, kabs=1.0, nsplits=10, ncells=2, **kwargs):
        ncells = int(ncells)
        maxn   = int(len(str(ncells)))
        for i in range(ncells):
            cellname = basename+'_'+str(i).zfill(maxn)
            self.AddFodoCellSplitDrift(cellname,magnetlength,driftlength,kabs,nsplits=10,**kwargs)
            
    def SetSamplers(self, command='first'):
        """
        SetSamplers(command)
        command is a string and one of:
        first - only the first element in the lattice
        last  - only the last element in the lattice
        all   - all elements
        category - only elements of that category
        """
        if command == 'first':
            self.samplers.append(self[0].name)
        elif command == 'last':
            self.samplers.append(self[-1].name)
        elif command == 'all':
            for e in self:
                self.samplers.append(e.name)
        else:
            #assume it's a category
            #if it's not, it won't match so tolerant of faulty commands
            for e in self:
                if e.category == command:
                    self.samplers.append(e.name)

# General scripts below this point

def CreateDipoleRing(filename, ncells=60, circumference=100.0, dfraction=0.1, samplers='first'):
    """
    Create a ring composed solely of dipoles
    filename
    ncells        - number of cells, each containing 1 dipole and a drift
    circumference - in metres
    dfraction     - the fraction of dipoles in each cell (0.0<dfraction<1.0)
    samplers      - 'first', 'last' or 'all'
    
    """
    ncells = int(ncells)
    if dfraction > 1.0:
        raise Warning("Fraction of dipoles must be less than 1.0 -> setting to 0.9")
        dfraction = 0.9
    if dfraction < 0.0:
        raise Warning("Fraction of dipoles must be greater than 1.0 -> setting to 0.1")
        dfraction = 0.1
    a           = Machine()
    dangle      = Decimal(str(2.0*math.pi / ncells))
    clength     = Decimal(str(float(circumference) / ncells))
    dlength     = clength * Decimal(str(dfraction))
    driftlength = clength - dlength
    a.AddDipole(length=dlength/Decimal(2), angle=dangle/Decimal(2))
    a.AddDrift(length=driftlength)
    for i in range(1,ncells,1):
        a.AddDipole(length=dlength, angle=dangle)
        a.AddDrift(length=driftlength)
    a.AddDipole(length=dlength/Decimal(2), angle=dangle/Decimal(2))
    a.SetSamplers(samplers)
    a.WriteLattice(filename)

def CreateDipoleFodoRing(filename, ncells=60, circumference=200.0, samplers='first'):
    """
    Create a ring composed of fodo cells with 2 dipoles per fodo cell.

    filename
    ncells         - number of fodo+dipole cells to create
    circumference  - circumference of machine in metres
    samplers       - 'first','last' or 'all'
    
    Hard coded to produce the following cell fractions:
    50% dipoles
    20% quadrupoles
    30% beam pipe / drift
    """
    a       = Machine()
    cangle  = Decimal(str(2.0*math.pi / ncells))
    clength = Decimal(str(float(circumference) / ncells))
    #dipole = 0.5 of cell, quads=0.2, drift=0.3, two dipoles
    #dipole:
    dl  = clength * Decimal(str(0.5)) * Decimal(str(0.5))
    da  = cangle/Decimal(2.0)
    #quadrupole:
    ql  = clength * Decimal('0.2') * Decimal('0.5')
    k1  = Decimal(str(SuggestFodoK(ql,dl)))
    #drift:
    drl = clength * Decimal('0.3') * Decimal('0.25')
    #naming
    nplaces  = len(str(ncells))
    basename = 'dfodo_'
    for i in range(ncells):
        cellname = basename + str(i).zfill(nplaces)
        a.AddQuadrupole(cellname+'_qd_a',ql/Decimal('2.0'),k1)
        a.AddDrift(cellname+'_dr_a',drl)
        a.AddDipole(cellname+'_dp_a','sbend',dl,da)
        a.AddDrift(cellname+'_dr_b',drl)
        a.AddQuadrupole(cellname+'_qf_b',ql,k1*Decimal('-1.0'))
        a.AddDrift(cellname+'_dr_c',drl)
        a.AddDipole(cellname+'_dp_b','sbend',dl,da)
        a.AddDrift(cellname+'_dr_d',drl)
        a.AddQuadrupole(cellname+'_qd_c',ql/Decimal('2.0'),k1)
    a.SetSamplers(samplers)
    a.WriteLattice(filename)
    
def CreateFodoLine(filename, ncells=10, driftlength=4.0, magnetlength=1.0, samplers='all',**kwargs):
    """
    Create a FODO lattice with ncells.

    ncells       - number of fodo cells
    driftlength  - length of drift segment in between magnets
    magnetlength - length of quadrupoles
    samplers     - 'all','first' or 'last'
    **kwargs     - kwargs to supply to quadrupole constructor

    """
    ncells = int(ncells)
    a      = Machine()
    k1     = SuggestFodoK(magnetlength,driftlength)
    a.AddFodoCellSplitDriftMultiple(magnetlength=magnetlength,driftlength=driftlength,kabs=k1,nsplits=10,ncells=ncells,**kwargs)
    a.SetSamplers(samplers)
    a.WriteLattice(filename)

def SuggestFodoK(magnetlength,driftlength):
    """
    SuggestFodoK(magnetlength,driftlength)

    returns k1 (float) value for matching into next quad in a FODO cell.
    f = 1/(k1 * magnetlength) = driftlength -> solve for k1

    """
    return 1.0 / (float(magnetlength)*(float(magnetlength) + float(driftlength)))

def WriteLattice(machine, filename, verbose=False):
    """
    WriteLattice(machineclassinstance,filenamestring)

    Write a lattice to disk.  This writes several files to make the
    machine, namely:
    
    filename_components_XX.gmad - component files (max 10k per file)
    filename_lattice.gmad       - lattice definition
    filename_samplers_XX.gmad   - sampler definitions (max 10k per file)
    filename_options.gmad       - options (TO BE IMPLEMENTED)
    filename.gmad          - suitable main file with all sub files in correct order

    these are prefixed with the basefile name / path

    """
    if type(machine) != Machine:
        raise TypeError("Not machine instance")

    #check machine length
    #to avoid parser problems with too long text files
    maxlinesperfile = 20000 #number of machine elements defined in 1 gmad file
    elementsperline = 100 #number of machine elements per bdsim line (not text line)
    
    #split machine into chunks - can be just one if only one...
    machinechunks   = _General.Chunks(machine,maxlinesperfile)

    #do the same with the samplers - remember nsamplers may not = nelements
    if len(machine.samplers) == 0:
        samplersexist = False
    else:
        samplersexist = True
    if samplersexist:
        samplerchunks = _General.Chunks(machine.samplers,maxlinesperfile)
    
    #check filename
    if filename[-5:] != '.gmad':
        filename += '.gmad'
    #check if file already exists
    filename = _General.CheckFileExists(filename)
    basefilename = filename[:-5]#.split('/')[-1]

    #prepare names
    maxn    = len(str(len(machinechunks)))
    files   = []
    fn_comp = [basefilename+'_components_'+str(n).zfill(maxn)+'.gmad' for n in range(len(machinechunks))]
    if samplersexist:
        fn_samp = [basefilename+'_samplers___'+str(n).zfill(maxn)+'.gmad' for n in range(len(samplerchunks))]
    timestring = '! ' + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()) + '\n'
    
    #write component files
    elementnames = []
    for filenumber,cfn in enumerate(fn_comp):
        f = open(cfn,'w')
        files.append(cfn)
        f.write(timestring)
        f.write('! pybdsim.Builder Lattice \n')
        f.write('! COMPONENT DEFINITION - File number '+str(filenumber+1)+'/'+str(len(fn_comp))+'\n\n')
        for e in machinechunks[filenumber]:
            if verbose:
                print e['name']
            if e.category == 'marker':
                linetowrite = e.name+' : ' + e.category
            #elif e.length < 1e-12:
            #    linetowrite = e.name+' : ' + 'marker'
            else:
                linetowrite = e.name+' : '+e.category+', l=%(LENGTH).15f *m' %{'LENGTH':e.length}
                for parameter in  e.keysextra():
                    #linetowrite += ', '+str(parameter)+'=%(NUMBER).15f' %{'NUMBER':e[parameter]}
                    linetowrite += ', '+str(parameter)+'='+str(e[parameter])
            linetowrite = linetowrite + ';\n'
            f.write(linetowrite)
            elementnames.append(e.name)
        f.close()

    #write lattice lines
    latfn = basefilename + '_lines______' + '_'*maxn + '.gmad'
    f = open(latfn,'w')
    files.append(latfn)
    f.write(timestring)
    f.write('! pybdsim.Builder Lattice \n')
    f.write('! LATTICE DEFINITION\n\n')
    linelist = []
    ti = 0
    for line in _General.Chunks(elementnames,elementsperline):
        stw2 = 'l'+str(ti)+': line = ('+', '.join(line)+');\n'
        f.write(stw2)
        linelist.append('l'+str(ti))
        ti += 1
    # need to define the period before making sampler planes
    f.write('lattice: line = ('+', '.join(linelist)+');\n')
    f.write('use, period=lattice;\n')
    f.close()

    #write samplers
    if samplersexist:
        for filenumber,sfn in enumerate(fn_samp):
            f = open(sfn,'w')
            files.append(sfn)
            f.write(timestring)
            f.write('! pybdsim.Builder Lattice \n')
            f.write('! SAMPLER DEFINITION - File number '+str(filenumber+1)+'/'+str(filenumber+1)+'\n\n')
            for s in samplerchunks[filenumber]:
                f.write('sample, range=' + str(s) + ';\n')
            f.close()

    # WRITE MACHINE OPTIONS
    # YET TO BE IMPLMENTED

    # write main file
    mainfn = basefilename + '.gmad'
    f = open(mainfn,'w')
    f.write(timestring)
    f.write('! pybdsim.Builder Lattice \n')
    f.write('! number of elements = ' + str(machine.nelements) + '\n')
    f.write('! total length       = ' + str(machine.totallength) + ' m\n\n')
    
    for fn in files:
        fn = fn.split('/')[-1]
        f.write('include '+fn+';\n')
    f.close()

    #user feedback
    print 'Lattice written to:'
    for fn in files:
        print(fn)
    print 'All included in main file: \n',mainfn

def WriteLattice1(machine, filename, verbose=False):
    """
    WriteLattice(machine(machine),filename(string),verbose(bool))

    Write a lattice to disk. This writes several files to make the
    machine, namely:
    
    filename_components.gmad - component files (max 10k per file)
    filename_sequence.gmad   - lattice definition
    filename_samplers.gmad   - sampler definitions (max 10k per file)
    filename_options.gmad    - options (TO BE IMPLEMENTED)
    filename.gmad            - suitable main file with all sub 
                               files in correct order

    these are prefixed with the specified filename / path

    """
    
    if not isinstance(machine,Machine1):
        raise TypeError("Not machine instance")
    
    elementsperline = 100 #number of machine elements per bdsim line (not text line)
    
    #check filename
    if filename[-5:] != '.gmad':
        filename += '.gmad'
    #check if file already exists
    filename = _General.CheckFileExists(filename)
    basefilename = filename[:-5]#.split('/')[-1]

    #prepare names
    files         = []
    fn_main       = basefilename + '.gmad'
    fn_components = basefilename + '_components.gmad'
    fn_sequence   = basefilename + '_sequence.gmad'
    fn_samplers   = basefilename + '_samplers.gmad'
    fn_options    = basefilename + '_options.gmad'
    timestring = '! ' + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()) + '\n'
    
    #write component files
    f = open(fn_components,'w')
    files.append(fn_components)
    f.write(timestring)
    f.write('! pybdsim.Builder Lattice \n')
    f.write('! COMPONENT DEFINITION\n\n')
    for element in machine.elements:
        f.write(str(element))
    f.close()

    #write lattice sequence
    f = open(fn_sequence,'w')
    files.append(fn_sequence)
    f.write(timestring)
    f.write('! pybdsim.Builder Lattice \n')
    f.write('! LATTICE SEQUENCE DEFINITION\n\n')
    sequencechunks = _General.Chunks(machine.sequence,elementsperline)
    linelist = []
    ti = 0
    for line in _General.Chunks(machine.sequence,elementsperline):
        f.write('l'+str(ti)+': line = ('+', '.join(line)+');\n')
        linelist.append('l'+str(ti))
        ti += 1
    # need to define the period before making sampler planes
    f.write('lattice: line = ('+', '.join(linelist)+');\n')
    f.write('use, period=lattice;\n')
    f.close()

    #write samplers
    if len(machine.samplers) > 0:
        f = open(fn_samplers,'w')
        files.append(fn_samplers)
        f.write(timestring)
        f.write('! pybdsim.Builder Lattice \n')
        f.write('! SAMPLER DEFINITION\n\n')
        for sampler in machine.samplers:
            f.write(str(sampler))
        f.close()

    # WRITE MACHINE OPTIONS
    # YET TO BE IMPLMENTED

    # write main file
    f = open(fn_main,'w')
    f.write(timestring)
    f.write('! pybdsim.Builder Lattice \n')
    f.write('! number of elements = ' + str(len(machine.elements)) + '\n')
    f.write('! total length       = ' + str(machine.length) + ' m\n\n')
    
    for fn in files:
        fn = fn.split('/')[-1]
        f.write('include '+fn+';\n')
    f.close()

    #user feedback
    print 'Lattice written to:'
    for fn in files:
        print(fn)
    print 'All included in main file: \n',fn_main
