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
import pybdsim.XSecBias
from . import Beam as _Beam
from . import Data as _Data
from . import Options as _Options
from . import Writer as _Writer
from . import _General
from ._General import IsFloat as _IsFloat

import bisect as _bisect
try: # Deprecated, removed in Python 3.10
    from collections import MutableMapping as _MutableMapping
except ImportError: # Python 3.10 onwards.
    from collections.abc import MutableMapping as _MutableMapping
from collections import OrderedDict as _OrderedDict
import math as _math
import numpy as _np
import copy as _copy
import textwrap as _textwrap
import numbers as _numbers

# these are written to match the order in the manual - http://www.pp.rhul.ac.uk/bdsim/manual-develop/model_construction.html#beamline-elements
bdsimcategories = [
    'drift',
    'rbend',
    'sbend',
    'quadrupole',
    'sextupole',
    'octupole',
    'decapole',
    'multipole',
    'thinmultipole',
    'vkicker',
    'hkicker',
    'kicker',
    'tkicker',
    'rfcavity',
    'rf',
    'rfx',
    'rfy'
    'target',
    'rcol',
    'jcol',
    "ecol",
    'degrader',
    'muspoiler',
    'shield',
    'dump',
    'solenoid',
    'laser',
    'gap',
    'crystalcol',
    'undulator',
    'transform3d',
    'rmatrix',
    'thinrmatrix',
    'element',
    'marker',
    'wirescanner',
    'ct',
    'line',
    'matdef',
    'gas',
    'spec',
    'paralleltransporter',
    ]


class ElementBase(_MutableMapping):
    """
    A class that represents an element / item in an accelerator beamline.
    Printing or string conversion produces the BDSIM syntax.

    This class provides the basic dict(ionary) inheritance and functionality
    and the representation that allows modification of existing parameters
    of an already declared item.

    """
    def __init__(self, name, isMultipole=False, **kwargs):
        self._store = dict()
        self.name         = name
        self['name']      = name
        self._isMultipole = isMultipole
        self._keysextra   = set()
        for k, v in kwargs.items():
            self[k] = v

    def __getitem__(self, key):
        return self._store[key]

    def __setitem__(self, key, value):
        if (key == "name" or key == "category") and value:
            self._store[key] = value
        elif value == "":
            return
        elif type(value) == tuple and self._isMultipole:
            self._store[key] = value
        elif isinstance(value, tuple):
            self._store[key] = (float(value[0]), value[1])
        elif isinstance(value, _numbers.Number):
            if "aper" in key.lower() and value < 1e-6:
                return
            else:
                self._store[key] = value
        else:
            if value.startswith('"') and value.endswith('"'):
                # Prevent the buildup of quotes for multiple setitem calls
                value = value.strip('"')
            self._store[key] = '"{}"'.format(value)

        if key not in {"name", "category"}: # keys which are not # 'extra'.
            self._keysextra.add(key)

    def __len__(self):
        return len(self._store)

    def __iter__(self):
        return iter(self._store)

    def keysextra(self):
        #so behaviour is similar to dict.keys()
        return self._keysextra

    def __delitem__(self, key):
        del self._store[key]
        try: # it may be in _store, but not necessarily in _keyextra
            self._keysextra.remove(key)
        except:
            pass

    def __repr__(self):
        s = "{s.name}: ".format(s=self)
        for i,key in enumerate(self._keysextra):
            if i > 0: # Separate with commas
                s += ", "
            # Write multipole syntax
            if type(self[key]) == tuple and self._isMultipole:
                s += key + '=' + '{'+(','.join([str(s) for s in self[key]]))+'}'
            # Write tuple (i.e. number + units) syntax
            elif type(self[key]) == tuple:
                s += key + '=' + str(self[key][0]) + '*' + str(self[key][1])
            # everything else (most things!)
            else:
                s += key + '=' + str(self[key])
        s += ';\n'
        return s

def _scale_element_parameters_by_length(parameters, elements, total_length):
    """
    Scale a list of elements' parameters by their length.  So if
    you have a list of hkickers you want to rescale based on their
    length: _scale_element_parameters_by_length([('hkick', 0.5)], [hk1, hk2, hk3])
    """
    total_length = sum([element['l'] for element in elements])
    for parameter, total_parameter in parameters:
        for element in elements:
            element[parameter] = total_parameter * element['l'] / total_length


class Element(ElementBase):
    """
    Element - an element / item in an accelerator beamline. Very similar to a
    python dict(ionary) and has the advantage that built in printing or string
    conversion provides BDSIM syntax.

    Element(name,type,**kwargs)

    >>> a = Element("d1", "drift", l=1.3)
    >>> b = Element("qx1f", "quadrupole", l=(0.4,'m'), k1=0.2, aper1=(0.223,'m'))
    >>> print(b)
    qx1f: quadrupole, k1=0.2, l=0.4*m, aper1=0.223*m;
    >>> str(c)
    qx1f: quadrupole, k1=0.2, l=0.4*m, aper1=0.223*m\\n;

    A beam line element must ALWAYs have a name, and type.
    The keyword arguments are specific to the type and are up to
    the user to specify - these should match BDSIM GMAD syntax.

    The value can be either a single string or number or a python tuple
    where the second entry must be a string (shown in second example).
    Without specified units, the parser assumes S.I. units.

    An element may also be multiplied or divided.  This will scale the
    length and angle appropriately.

    >>> c = Element('sb1', 'sbend', l=(0.4,'m'), angle=0.2)
    >>> d = c/2
    >>> print(d)
    sb1: sbend, l=0.2*m, angle=0.1;

    This inherits and extends ElementBase that provides the basic dictionary
    capabilities.  It adds the requirement of type / category (because 'type' is
    a protected keyword in python) as well as checking for valid BDSIM types.
    """
    def __init__(self, name, category, isMultipole=False, **kwargs):
        """
        is Multipole is a flag to take into account the inheritance of multipole in a sequence
        This is important to correctly write the knl in the gmad file
        m1: multipole, l=0.0;
        m2: m1, knl ={};
        """

        if category not in bdsimcategories:
            raise ValueError("Not a valid BDSIM element type: {}".format(category))

        if (category == 'thinmultipole') or (category == 'multipole') or isMultipole:
            ElementBase.__init__(self, name, isMultipole=True, **kwargs)
        else:
            ElementBase.__init__(self,name,**kwargs)
        self['category'] = category
        self.category    = category
        self._isMultipole = isMultipole
        self.length      = 0.0 #for book keeping only
        self._UpdateLength()

    def _UpdateLength(self):
        if 'l' in self:
            if type(self['l']) == tuple:
                ll = self['l'][0]
            else:
                ll = self['l']
            self.length += float(ll)

    def __repr__(self):
        s = "{}: {}".format(self.name, self.category)
        if self._keysextra:
            for key in sorted(self._keysextra):
                if (type(self[key]) == tuple
                    and (self.category != 'thinmultipole')
                    and (self.category != 'multipole') and self._isMultipole==False):
                    s += (', ' + key + '=' + str(self[key][0])
                          + '*' + str(self[key][1]))
                elif (type(self[key]) == tuple
                      and ((self.category == 'thinmultipole')
                           or (self.category == 'multipole') or self._isMultipole)):
                    s += (', ' + key + '=' + '{'
                          + (','.join([str(s) for s in self[key]]))+'}')
                else:
                    s += ", {}={}".format(key, self[key])
        s += ';\n'
        return s

    def _split_length(self, points):
        """
        points = points along the start of the element.  So n
        points will return n+1 elements.
        """
        try:
            total_length = self['l']
        except:
            raise TypeError("Element has no length, cannot be split.")
        accumulated_length = 0.0
        split_elements = []
        This = type(self) # This class, we use to construct the output.
        # Not length or name.  We change these here.  We leave
        # updating other parameters (based on length or otherwise) to
        # other methods or functions.
        other_kwargs = _copy.deepcopy(dict(self))
        del other_kwargs['l']
        del other_kwargs['name']
        del other_kwargs['category'] # boilerplate argument we have to remove

        for i, point in enumerate(sorted(points)):
            name = "{}_split_{}".format(self['name'], i)
            length = round(point - accumulated_length, 15)
            accumulated_length += length
            split_elements.append(This(name, l=length, **other_kwargs))
        # Add the final element (for n points we have n+1 elements, so
        # we add the last one here "by hand").
        split_elements.append(This("{}_split_{}".format(self['name'], i + 1),
                                   l=round(total_length - accumulated_length, 15),
                                   **other_kwargs))

        return split_elements

    def _split_length_with_length_scaled_parameters(self, points, parameters):
        split_elements = self._split_length(points)
        parameters_and_original_values = [(parameter, self[parameter])
                                          for parameter in parameters]
        _scale_element_parameters_by_length(parameters_and_original_values,
                                            split_elements, self['l'])
        return split_elements

    def split(self, points):
        """
        Split this element into len(points)+1 elements, with the
        correct lengths.  This does not affect magnetic strengths,
        etc, which is left to derived classes where appropriate.
        """
        return self._split_length(points)

    @classmethod
    def from_element(cls, parent_element_name: str, isMultipole=False, **kwargs):
        # parameters = _copy.copy(dict(element))
        parameters = {}
        for key, value in kwargs.items():
            parameters[key] = value
        parameters["category"] = parent_element_name
        if parent_element_name not in bdsimcategories:
            bdsimcategories.append(parent_element_name)
        return cls(isMultipole=isMultipole, **parameters)


class ElementModifier(ElementBase):
    """
    A class to MODIFY an already defined element in a gmad file by appending an
    updated definition. Using this alone in BDSIM will result in an
    undefined type error. This class is particularly useful for creating
    a strength file.

    # define an element
    >>> a = Element('qf1', 'quadrupole', l=0.3, k1=0.00345)
    >>> b = ElementModifier('qf1',k1=0.0245)
    >>> f = open('mylattice.gmad', 'w')
    >>> f.write(str(a))
    >>> f.write(str(b))
    >>> f.close()

    cat mylattice.gmad
    qf1, quadrupole, l=0.3, k1=0.00345;
    qf1, k1=0.0245

    This results in the quadrupole strength k1 in this example being
    changed to 0.0245.
    """
    def __init__(self, name, isMultipole=False, **kwargs):
        if len(kwargs) == 0:
            raise ValueError("Error: must specify at least 1 keyword argument")
        ElementBase.__init__(self, name, isMultipole, **kwargs)


class Line(list):
    """
    A class that represents a :class:`list` of :class:`Elements`

    Provides ability to print out the sequence or define all
    the components.

    Example:

    >>> d1 = Element("drift1", "drift", l=1.3)
    >>> q1 = Element("q1", "quadrupole", l=0.4, k1=4.5)
    >>> a = Line([d1,q1])

    """
    def __init__(self,name,*args):
        self.category = "line" # for compatibility with Element(s)
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

        s += ', '.join([item.name for item in self]) + ');'
        s = '\n\t'.join(_textwrap.wrap(s))
        s += "\n"
        return s

    def DefineConstituentElements(self):
        """
        Return a string that contains the lines required
        to define each element in the :class:`Line`.

        Example using predefined Elements name 'd1' and 'q1':

        >>> l = Line([d1,q1])
        >>> f = open("file.txt", "w")
        >>> f.write(l.DefineConsituentElements())
        >>> f.close()
        """
        s = ''
        for item in self:
            s += str(item) #uses elements __repr__ function
        return s


class ApertureModel(dict):
    """
    A class that produces the aperture representation of an element. Only non-zero
    values are written for the aperture parameters. Includes parameter checking.
    """
    def __init__(self, apertureType='circular', aper1=0.1, aper2=0, aper3=0, aper4=0, warningName=""):
        dict.__init__(self)
        allowedTypes = [
            'circular',
            'elliptical',
            'rectangular',
            'lhc',
            'lhcdetailed',
            'rectellipse',
            'racetrack',
            'octagonal'
        ] # maintain order for tests further down!
        madxTypes = {
            'circle'      : 'circular',
            'ellipse'     : 'elliptical',
            'rectangle'   : 'rectangular',
            'lhcscreen'   : 'lhcdetailed',
            'marguerite'  : None,
            'rectellipse' : 'rectellipse',
            'racetrack'   : 'racetrack',
            'octagon'     : 'octagonal',
            'rectcircle'  : 'lhc',
            'filename'    : None
            }
        atL = str.lower(apertureType)
        if atL not in allowedTypes and atL not in madxTypes.keys():
            print('Allowed BDSIM aperture types are: ', allowedTypes)
            print('Allowed MADX aperture types are: ',madxTypes.keys())
            raise ValueError(str(warningName)+" Invalid aperture type: "+str(apertureType))

        if atL in list(madxTypes.keys()):
            self['apertureType'] = madxTypes[atL]
            if self['apertureType'] == None:
                print('Unsupported type: :',self['apertureType'],'" - replacing with elliptical')
                self['apertureType'] = 'elliptical'
        else:
            self['apertureType'] = apertureType

        if self['apertureType'] in allowedTypes[1:] and aper2 == 0:
            print('For aperture type "',self['apertureType'],'" at least aper1 and aper2 must be specified')
            print("apertures: ",aper1,aper2,aper3,aper4)
            raise ValueError(str(warningName) + " Too few aperture parameters supplied")
        
        self['aper1'] = aper1
        self['aper2'] = aper2
        self['aper3'] = aper3
        self['aper4'] = aper4

    def __repr__(self):
        # aper1 is always present at least.
        out = ('apertureType="{}", aper1={}*m').format(self["apertureType"],
                                                       self["aper1"])
        # Append any non-zero apertures.
        for i in [2,3,4]:
            aperKey = "aper{}".format(i)
            aperValue = self[aperKey]
            if aperValue > 0:
                out += ", {}={}*m".format(aperKey, aperValue)
        return out


class Drift(Element):
    def __init__(self, name, l, **kwargs):
        Element.__init__(self, name, "drift", l=l, **kwargs)


class HKicker(Element):
    def __init__(self, name, hkick, **kwargs):
        Element.__init__(self, name, 'hkicker', hkick=hkick, **kwargs)

    def split(self, points):
        return self._split_length_with_length_scaled_parameters(points,
                                                                ['hkick'])


class VKicker(Element):
    def __init__(self, name, vkick, **kwargs):
        Element.__init__(self, name, 'vkicker', vkick=vkick, **kwargs)


    def split(self, points):
        return self._split_length_with_length_scaled_parameters(points,
                                                                ['vkick'])


class Kicker(Element):
    def __init__(self, name, hkick, vkick, **kwargs):
        Element.__init__(self, name, 'kicker', hkick=hkick,
                         vkick=vkick, **kwargs)

    def split(self, points):
        return self._split_length_with_length_scaled_parameters(points,
                                                                ['vkick',
                                                                 'hkick'])


class TKicker(Element):
    def __init__(self, name, hkick, vkick, **kwargs):
        Element.__init__(self, name, 'tkicker', hkick=hkick,
                         vkick=vkick, **kwargs)

    def split(self, points):
        return self._split_length_with_length_scaled_parameters(points,
                                                                ['vkick',
                                                                 'hkick'])


class Gap(Element):
    def __init__(self, name, l, **kwargs):
        Element.__init__(self, name, 'gap', l=l, **kwargs)


class Marker(Element):
    def __init__(self, name):
        Element.__init__(self, name, 'marker')


class Multipole(Element):
    def __init__(self, name, l, knl, ksl, **kwargs):
        Element.__init__(self, name, 'multipole', l=l,
                         knl=knl, ksl=ksl, **kwargs)

    def split(self, points):
        split_mps = self._split_length(points)
        for mp in split_mps:
            new_knl = tuple([integrated_strength * mp['l'] / self['l']
                             for integrated_strength in mp['knl']])
            new_ksl = tuple([integrated_strength * mp['l'] / self['l']
                             for integrated_strength in mp['ksl']])
            mp['knl'] = new_knl
            mp['ksl'] = new_ksl
        return split_mps


class ThinMultipole(Element):
    def __init__(self, name, knl=(0,0), ksl=(0,0), **kwargs):
        Element.__init__(self, name, 'thinmultipole', knl=knl, ksl=ksl, **kwargs)


class Quadrupole(Element):
    def __init__(self, name, l, k1, **kwargs):
        Element.__init__(self, name, 'quadrupole', l=l,k1=k1, **kwargs)


class Sextupole(Element):
    def __init__(self, name, l, k2, **kwargs):
        Element.__init__(self, name, 'sextupole', l=l, k2=k2, **kwargs)


class Octupole(Element):
    def __init__(self, name, l, k3, **kwargs):
        Element.__init__(self, name, 'octupole', l=l, k3=k3, **kwargs)


class Decapole(Element):
    def __init__(self, name, l, k4, **kwargs):
        Element.__init__(self, name,'decapole', l=l, k4=k4, **kwargs)


class _Dipole(Element):
    def __init__(self, name, category, l, angle=None, B=None, **kwargs):
        if angle is None and B is None:
            raise TypeError('angle XOR B must be specified for an SBend')
        elif angle is not None:
            Element.__init__(self, name, category, l=l, angle=angle, **kwargs)
        else:
            Element.__init__(self, name, category, l=l, B=B, **kwargs)

    def split(self, points):
        split_bends = self._split_length_with_length_scaled_parameters(points, ['angle'])
        # Delete all the in/out parameters.  pop syntax just a quicker
        # way of doing try: del...  etc.
        for bend in split_bends:
            bend.pop('fint', None)
            bend.pop('fintx', None)
            bend.pop('fintK2', None)
            bend.pop('fintxK2', None)
            bend.pop('e1', None)
            bend.pop('e2', None)
            bend.pop('h1', None)
            bend.pop('h2', None)

        # Assign following to their respective elements, but only if
        # self (i.e., the unsplit element) had them.
        if 'e1' in self: # assign e1 to first ele only
            split_bends[0]['e1'] = self['e1']
        if 'e2' in self: # assign e2 to last ele only
            split_bends[-1]['e2'] = self['e2']
        if 'fint' in self: # assign fint to first ele only
            split_bends[0]['fint'] = self['fint']
        if 'fintx' in self: # assign fintx to last ele only
            split_bends[-1]['fintx'] = self['fintx']
        if 'fintK2' in self: # assign fintK2 to first ele only
            split_bends[0]['fintK2'] = self['fint']
        if 'fintxK2' in self: # assign fintxK2 to last ele only
            split_bends[-1]['fintxK2'] = self['fintx']
        if 'h1' in self: # assign h1 to first ele only
            split_bends[0]['h1'] = self['h1']
        if 'h2' in self: # assign h2 to last ele only
            split_bends[-1]['h2'] = self['h2']

        return split_bends


class SBend(_Dipole):
    def __init__(self, name, l, angle=None, B=None, **kwargs):
        _Dipole.__init__(self, name, 'sbend', l, angle=angle, B=B, **kwargs)


class RBend(_Dipole):
    def __init__(self, name, l, angle=None, B=None, **kwargs):
        _Dipole.__init__(self, name, 'rbend', l, angle=angle, B=B, **kwargs)


class RFCavity(Element):
    def __init__(self, name, l, gradient, **kwargs):
        Element.__init__(self, name, 'rfcavity', l=l,
                         gradient=gradient, **kwargs)


class _Col(Element):
    def __init__(self, name, category, l, xsize, ysize, **kwargs):
        d = {}
        # Strip aperture information:
        kwargs = {key: value for key, value in kwargs.items() if
                  "aper" not in key.lower()}
        Element.__init__(self, name, category, l=l, xsize=xsize,
                         ysize=ysize, **kwargs)


class RCol(_Col):
    def __init__(self, name, l, xsize, ysize, **kwargs):
        _Col.__init__(self, name, "rcol", l,
                      xsize, ysize, **kwargs)


class ECol(_Col):
    def __init__(self, name, l, xsize, ysize, **kwargs):
        _Col.__init__(self, name, "ecol", l,
                      xsize, ysize, **kwargs)


class JCol(_Col):
    def __init__(self, name, l, xsize, ysize, **kwargs):
        _Col.__init__(self, name, "jcol", l,
                      xsize, ysize, **kwargs)


class Degrader(Element):
    def __init__(self, name, l, nWedges,
                 wedgeLength, degHeight, materialThickness=None,
                 degraderOffset=None, **kwargs):
        if (materialThickness is None and degraderOffset is None):
            msg = "materialThickness or degraderOffset must be specified."
            raise TypeError(msg)
        elif materialThickness is not None:
            Element.__init__(self, name, "degrader", l=l,
                             numberWedges=nWedges,
                             wedgeLength=wedgeLength,
                             degraderHeight=degHeight,
                             materialThickness=materialThickness, **kwargs)
        else:
            Element.__init__(self, name, "degrader", l=l,
                             numberWedges=nWedges,
                             wedgeLength=wedgeLength,
                             degraderHeight=degHeight,
                             degraderOffset=degraderOffset, **kwargs)


class MuSpoiler(Element):
    def __init__(self, name, l, B, **kwargs):
        Element.__init__(self, name,'muspoiler',l=l,B=B,**kwargs)


class Solenoid(Element):
    def __init__(self, name, l, ks, **kwargs):
        Element.__init__(self, name,'solenoid',l=l,ks=ks,**kwargs)


class Shield(Element):
    def __init__(self, name, l, **kwargs):
        Element.__init__(self, name,'shield',l=l,**kwargs)


class Laser(Element):
    def __init__(self, name, l, x, y, z,
                 waveLength, **kwargs):
        Element.__init__(self, name,'laser',
                         l=l,x=x,y=y,z=z,
                         waveLength=waveLength,
                         **kwargs)


class WireScanner(Element):
    def __init__(self, name, l, wireDiameter, wireLength, material, **kwargs):
        Element.__init__(self, name,'wirescanner',l=l,
                         wireDiameter=wireDiameter,
                         wireLength=wireLength,
                         material=material,
                         **kwargs)


class CrystalCol(Element):
    def __init__(self, name, l, xsize, material, **kwargs):
        Element.__init__(self, name,'crystalcol',l=l,
                         xsize=xsize,
                         material=material,
                         **kwargs)


class Undulator(Element):
    def __init__(self, name, l, b, undulatorPeriod, **kwargs):
        Element.__init__(self, name,'undulator',l=l,B=b,
                         undulatorPeriod=undulatorPeriod,
                         **kwargs)


class Dump(Element):
    def __init__(self, name, l, **kwargs):
        Element.__init__(self, name,'dump',l=l,**kwargs)


class ExternalGeometry(Element):
    def __init__(self, name, l, outerDiameter, geometryFile, **kwargs):
        Element.__init__(self, name, 'element', l=l,
                         outerDiameter=outerDiameter,
                         geometryFile=geometryFile, **kwargs)


class Transform3D(Element):
    def __init__(self, name, **kwargs):
        Element.__init__(self, name, 'transform3d', **kwargs)


class Rmat(Element):
    def __init__(self, name, l, r11, r12, r13, r14,
                 r21, r22, r23, r24,
                 r31, r32, r33, r34,
                 r41, r42, r43, r44,  **kwargs):
        Element.__init__(self, name, 'rmatrix', l=l, r11=r11, r12=r12, r13=r13, r14=r14,
                         r21=r21, r22=r22, r23=r23, r24=r24,
                         r31=r31, r32=r32, r33=r33, r34=r34,
                         r41=r41, r42=r42, r43=r43, r44=r44, **kwargs)


class Sampler(object):
    """
    A sampler is unique in that it does not have a length unlike every
    :class:`Element` hence it needs its own class to produce its
    representation.
    """
    def __init__(self,name):
        self.name = name

    def __repr__(self):
        if self.name == 'all':
            return 'sample, all;\n'
        else:
            return 'sample, range='+self.name+';\n'


class GmadObject(_MutableMapping):
    """
    A gmad object does not have a length unlike every :class:`Element` hence it
    needs its own class to produce its representation.
    """
    def __init__(self,objecttype,name,**kwargs):
        self._store = dict()
        self.objecttype   = objecttype
        self.name         = name
        self._keysextra   = set()
        for k, v in kwargs.items():
            self[k] = v

    def __getitem__(self, key):
        return self._store[key]

    def __setitem__(self, key, value):

        if (key == "name" or key == "category") and value:
            self._store[key] = value
        elif value == "":
            return
        elif isinstance(value, tuple):
            self._store[key] = (float(value[0]), value[1])
        elif isinstance(value, str):
            if value.startswith('"') and value.endswith('"'):
                # Prevent the buildup of quotes for multiple setitem calls
                value = value.strip('"')
            self._store[key] = '"{}"'.format(value)
        else:
            self._store[key] = value

        if key not in {"name", "category"}: # keys which are not # 'extra'.
            self._keysextra.add(key)

    def __len__(self):
        return len(self._store)

    def __iter__(self):
        return iter(self._store)

    def keysextra(self):
        #so behaviour is similar to dict.keys()
        return self._keysextra

    def __delitem__(self, key):
        del self._store[key]
        try: # it may be in _store, but not necessarily in _keyextra
            self._keysextra.remove(key)
        except:
            pass

    def __repr__(self):
        s = "{s.name}: ".format(s=self) + self.objecttype + ", "
        for i,key in enumerate(self._keysextra):
            if i > 0: # Separate with commas
                s += ", "
            # Write tuple (i.e. number + units) syntax
            if type(self[key]) == tuple:
                s += key + '=' + str(self[key][0]) + '*' + str(self[key][1])
            elif type(self[key]) == list:
                s += key + '={' + ','.join(map(str,self[key])) + '}'
            # everything else (most things!)
            else:
                s += key + '=' + str(self[key])
        s += ';\n'
        return s


class Aperture(GmadObject):
    """
    A crystal definition. Any kwargs will be written as parameter=value.
    parameter=(value,unit) -> parameter=value*unit
    """
    def __init__(self,name,**kwargs):
        GmadObject.__init__(self, "aperture",name,**kwargs)


class Atom(GmadObject):
    """
    A atom definition. Any kwargs will be written as parameter=value.
    parameter=(value,unit) -> parameter=value*unit
    """
    def __init__(self,name,**kwargs):
        GmadObject.__init__(self, "atom",name,**kwargs)


class BLM(GmadObject):
    """
    A blmplacement definition. Any kwargs will be written as parameter=value.
    parameter=(value,unit) -> parameter=value*unit
    """
    def __init__(self,name,**kwargs):
        GmadObject.__init__(self, "blm",name,**kwargs)


class CavityModel(GmadObject):
    """
    A cavitymodel definition. Any kwargs will be written as parameter=value.
    parameter=(value,unit) -> parameter=value*unit
    """
    def __init__(self,name,**kwargs):
        GmadObject.__init__(self, "cavitymodel",name,**kwargs)


class Crystal(GmadObject):
    """
    A crystal definition. Any kwargs will be written as parameter=value.
    parameter=(value,unit) -> parameter=value*unit
    """
    def __init__(self,name,**kwargs):
        GmadObject.__init__(self, "crystal",name,**kwargs)


class Field(GmadObject):
    """
    A field definition. Any kwargs will be written as parameter=value.
    parameteter=(value,unit) -> parameter=value*unit
    """
    def __init__(self,name,**kwargs):
        GmadObject.__init__(self, "field",name,**kwargs)


class Material(GmadObject):
    """
    A material definition. Any kwargs will be written as parameter=value.
    parameter=(value,unit) -> parameter=value*unit
    """
    def __init__(self,name,**kwargs):
        GmadObject.__init__(self, "matdef",name,**kwargs)


class NewColour(GmadObject):
    """
    A newcolour definition. Any kwargs will be written as parameter=value.
    parameter=(value,unit) -> parameter=value*unit
    """
    def __init__(self,name,**kwargs):
        GmadObject.__init__(self, "newcolour",name,**kwargs)


class Placement(GmadObject):
    """
    A placement definition. Any kwargs will be written as parameter=value.
    parameter=(value,unit) -> parameter=value*unit
    """
    def __init__(self,name,**kwargs):
        GmadObject.__init__(self, "placement",name,**kwargs)


class Query(GmadObject):
    """
    A query definition. Any kwargs will be written as parameter=value.
    parameter=(value,unit) -> parameter=value*unit
    """
    def __init__(self,name,**kwargs):
        GmadObject.__init__(self, "query",name,**kwargs)


class Region(GmadObject):
    """
    A region definition. Any kwargs will be written as parameter=value.
    parameter=(value,unit) -> parameter=value*unit
    """
    def __init__(self,name,**kwargs):
        GmadObject.__init__(self, "region",name,**kwargs)


class SamplerPlacement(GmadObject):
    """
    A samplerplacement definition. Any kwargs will be written as parameter=value.
    parameter=(value,unit) -> parameter=value*unit
    """
    def __init__(self,name,**kwargs):
        GmadObject.__init__(self, "samplerplacement",name,**kwargs)


class Scorer(GmadObject):
    """
    A scorer definition. Any kwargs will be written as parameter=value.
    parameter=(value,unit) -> parameter=value*unit
    """
    def __init__(self,name,**kwargs):
        GmadObject.__init__(self, "scorer",name,**kwargs)


class ScorerMesh(GmadObject):
    """
    A scorermesh definition. Any kwargs will be written as parameter=value.
    parameter=(value,unit) -> parameter=value*unit
    """
    def __init__(self,name,**kwargs):
        GmadObject.__init__(self, "scorermesh",name,**kwargs)


class Tunnel(GmadObject):
    """
    A tunnel definition. Any kwargs will be written as parameter=value.
    parameter=(value,unit) -> parameter=value*unit
    """
    def __init__(self,name,**kwargs):
        GmadObject.__init__(self, "tunnel",name,**kwargs)


class XSecBias(GmadObject):
    """
    A xsecbias definition. Any kwargs will be written as parameter=value.
    parameter=(value,unit) -> parameter=value*unit
    """
    def __init__(self,name,**kwargs):
        GmadObject.__init__(self, "xsecBias",name,**kwargs)


class Machine(object):
    """
    A class represents an accelerator lattice as a sequence of
    components. Member functions allow various lattice components
    to be append to the sequence of the machine. This class allows
    the user to programatically create a lattice and write the
    BDSIM gmad representation of it.

    Example:

    >>> a = Machine()
    >>> a.AddDrift('mydrift', l=1.3)
    >>> a.Write("lattice.gmad")

    Example with Sychrotron rescaling:

    >>> a = Machine(sr=True, energy0=250,charge=-1)
    >>> a.AddDipole('sb1','sbend',length=1.0,angle=1e-5)
    >>> a.AddDrift('dr1',length=1)
    >>> a.AddDipole('sb2','sbend',length=1.0,angle=1e-5)
    >>> a.AddDrift("dr2",length=1)

    Caution: adding an element of the same name twice will result the
    element being added only to the sequence again and not being
    redefined - irrespective of if the parameters are different. If
    verbose is used (True), then a warning will be issued.
    """
    def __init__(self,verbose=False, sr=False, energy0=0.0, charge=-1.0):
        self.verbose   = verbose
        self.sequence  = []
        self.elements  = _OrderedDict()
        self.samplers  = []
        self.length    = 0.0
        self.angint    = 0.0
        self.bias      = []
        self.material  = []
        self.beam      = _Beam.Beam()
        self.options   = None
        self.energy0   = energy0
        self.energy    = []
        self.lenint    = []
        self.sr        = sr
        self.energy.append(energy0)
        self.charge    = charge
        self.objects   = []  # list of non-sequence objects e.g crystals, lasers, placements etc.
        self.includesPre  = []
        self.includesPost = []

    def __repr__(self):
        s = ''
        s += 'pybdsim.Builder.Machine instance\n'
        s += str(len(self.sequence)) + ' items in sequence\n'
        s += str(len(self.elements)) + ' unique elements defined\n'
        return s

    def __iter__(self):
        self._iterindex = -1
        return self

    def __next__(self):
        if self._iterindex == len(self.sequence)-1:
            raise StopIteration
        self._iterindex += 1
        return self.elements[self.sequence[self._iterindex]]

    next = __next__

    def __getitem__(self,name):
        if _IsFloat(name):
            return self.elements[self.sequence[name]]
        else:
            return self.elements[name]

    def __len__(self):
        print('Number of unique elements:      ',len(self.elements.keys()))
        print('Number of elements in sequence: ',len(self.sequence),' <- returning this')
        return len(self.sequence)

    def GetIntegratedAngle(self):
        """
        Get the cumulative angle of all the bends in the machine. This is therefore the difference
        in angle between the entrance and exit vectors. All angles are assumed to be in the horizontal
        plane so this will not be correct for rotated dipoles.
        """
        return self.angint

    def GetIntegratedLength(self):
        """
        Get the integrated length of all the components.
        """
        return self.length

    def Append(self, item, is_component=False):
        if not isinstance(item, (Element, Line)):
            msg = "Only Elements or Lines can be added to the machine"
            raise TypeError(msg)
        elif item.name not in list(self.elements.keys()):
            #hasn't been used before - define it
            if type(item) is Line:
                for element in item:
                    self.Append(item)
            else:
                self.elements[item.name] = item
        else:
            if self.verbose:
                print("Element of name: ",item.name," already defined, simply adding to sequence")
        # finally add it to the sequence if this is not a base component of the sequence.
        if not is_component:
            self.sequence.append(item.name)

            self.length += item.length
            self.lenint.append(self.length)

        # list of elements that produce SR
        elementsSR = ["sbend", "rbend"]

        # update energy if correct element category and has finite length.
        if item.category in elementsSR and item.length > 0:
            if "angle" in item:
                ang = item['angle']
                if type(ang) == tuple:
                    ang = ang[0]
                else:
                    ang = ang
            elif "B" in item:
                # Assume a beam instance has been added to machine...
                if (self.beam['particle'] == "e-") or (self.beam['particle'] == "e+"):
                    pMass = 0.000511
                elif (self.beam['particle'] == "proton"):
                    pMass = 0.938
                else:
                    pMass = 0
                if (self.energy[-1] > 0):
                    brho = 3.3356 * _np.sqrt(self.energy[-1]**2 - pMass**2)
                    ang  = item['B'] * item.length / brho
                else:
                    ang  = 0
            else:
                ang = 0

            self.angint += ang

            # bend so SR generated. Recompute beam energy
            energy = self.energy[-1]
            self.energy.append(energy-14.1e-6*ang**2/item.length*energy**4)
        else :
            self.energy.append(self.energy[-1])

    def GetNamesOfType(self, category):
        """
        Returns a list of names of elements that are of the specified category.
        """
        return [k for k,e in self.elements.items() if e.category == category]

    def ReplaceWithElement(self, name, newelement, warnAboutLengthDifference=True):
        """
        Replace an element in the machine with a new element object (one of the individual
        element pybdsim.Builder classes that inherit the Element class).
        """
        if name not in self.sequence:
            msg = "{} not found in machine sequence.".format(name)
            raise ValueError(msg)
        if not isinstance(newelement, Element):
            msg = "new element is not a pybdsim.Builder.Element instance."
            raise TypeError(msg)
        if self.elements[name].length != newelement.length and warnAboutLengthDifference:
            msg = "Warning: Length of new element is not the same length as existing element {}".format(name)
            print(msg)
            currlength = self.elements[name].length
            self.length -= currlength
            self.length += newelement.length
            for i,ename in enumerate(self.sequence):
                if ename == name:
                    self.lenint[i] = newelement.length
        self.elements[name] = newelement

    def ReplaceElementCategory(self, category, newcategory):
        """
        Change category of all elements of a given category. All parameters of the element
        being changed will be preserved, please update with the UpdateCategoryParameter function.
        """
        names = self.GetNamesOfType(category)
        for name in names:
            self.elements[name].category = newcategory

    def UpdateElement(self, name, parameter, value):
        """
        Update a parameter for a specified element name. Modifying element length will produce a warning.
        If a value for that parameter already exists, the value will be overwritten.
        """
        if parameter == 'length':
            msg = 'Caution: modifying an element length will change the machine length.'
            print(msg)
            # update total machine length
            currlength = self.elements[name][parameter]
            self.length -= currlength
            self.elements[name][parameter] = value
            self.length += value
            for i,ename in enumerate(self.sequence):
                if ename == name:
                    self.lenint[i] = value
        elif name in list(self.elements.keys()):
            self.elements[name][parameter] = value
        else:
            msg = 'Unknown element {}'.format(name)
            raise ValueError(msg)

    def UpdateElements(self, names, parameter, value, namelocation='all'):
        """
        Update multiple elements. Supplied names can be a sequence type object containing a list of element
        names or a string where all elements with names containing that string will be updated. namelocation
        specifies if names string can be at the 'beginning', 'end', or anywhere ('all') in an elements name.
        """
        # TODO: better method for name matching. Keep basic for now.
        if isinstance(names, str):
            if namelocation.lower() == 'all':
                elements = [name for name in list(self.elements.keys()) if names in name]
            elif namelocation.lower() == 'start':
                elements = [name for name in list(self.elements.keys()) if names in name[:len(names)]]
            elif namelocation.lower() == 'end':
                elements = [name for name in list(self.elements.keys()) if names in name[-len(names):]]
            else:
                msg = 'Unknown string location {}'.format(namelocation)
                raise ValueError(msg)
            for name in elements:
                self.UpdateElement(name, parameter, value)
        else:
            for name in names:
                self.UpdateElement(name, parameter, value)

    def UpdateCategoryParameter(self, category, parameter, value):
        """
        Update parameter for all elements of a given category.
        """
        names = self.GetNamesOfType(category)
        self.UpdateElements(names, parameter, value)

    def UpdateGlobalParameter(self, parameter, value):
        """
        Update parameter for all elements of a given category.
        """
        names = list(self.elements.keys())
        self.UpdateElements(names, parameter, value)

    def InsertAndReplace(self, newElement, sLocation):
        """
        New element will be placed at the central s location.
        """
        ne = newElement
        s = sLocation

        def CheckName(name):
            if name in self.sequence:
                raise ValueError("This new element by name is already in this machine - name uniquely")
        if type(ne) is list:
            l = _np.array([e.length for e in ne]).sum()
            for e in ne:
                CheckName(e.name)
        else:
            l = ne.length
            CheckName(ne.name)


        if l == 0:
            raise ValueError("Cannot be used to insert thin elements")
        
        sStart = s - 0.5*l
        sEnd   = s + 0.5*l

        if sStart < 0:
            raise ValueError("Given position and length of item it would precede start of beam line.")
        if sEnd > self.length:
            print("Beam line will be extended by : ",sEnd-self.length," m")

        # work out index points and new sequence to insert and do modification in only one step
        # at the end
        indFirstReplace = 0
        indLastReplace  = 0
        newSequence = []
        newElements = {}

        # first boundary
        indSStart = _bisect.bisect_left(self.lenint, sStart)
        if self.lenint[indSStart] == sStart:
            indFirstReplace = indSStart + 1 # exactly matches on a boundary
        else:
            if sStart == 0:
                indFirstReplace = 0
            else:
                indFirstReplace = indSStart
                elToSplit = self.elements[self.sequence[indSStart]]
                sElStart  = self.lenint[indSStart] - elToSplit.length # easier than boundary indexing issues
                newElsStart = elToSplit.split([sStart - sElStart])
                firstPart = newElsStart[0]
                newSequence.append(firstPart.name)
                newElements[firstPart.name] = firstPart

        # insert new sequence
        if type(ne) is list:
            newSequence.extend([e.name for e in ne])
            newElements.update({e.name:e for e in ne})
        else:
            newSequence.append(ne.name)
            newElements[ne.name] = ne

        # second boundary
        indSEnd = _bisect.bisect(self.lenint, sEnd)
        if self.lenint[indSEnd] == sEnd:
            indLastReplace = indSEnd - 1 # exactly matches on a boundary
        else:
            indLastReplace = indSEnd
            elToSplit = self.elements[self.sequence[indSEnd]]
            sElStart  = self.lenint[indSEnd] - elToSplit.length
            newElsEnd = elToSplit.split([sEnd - sElStart])
            secondPart = newElsEnd[1]
            newSequence.append(secondPart.name)
            newElements[secondPart.name] = secondPart 

        # do operation
        self.sequence[indFirstReplace:indLastReplace+1] = newSequence
        self.elements.update(newElements)
        self.RegenerateLenInt()

    def RegenerateLenInt(self):
        ltot = [0.0]
        for name in self.sequence:
            ltot.append(ltot[-1] + self.elements[name].length)
        self.lenint = ltot[1:]

    def SynchrotronRadiationRescale(self):
        """
        Rescale all component strengths for SR
        """
        ielement = 1
        for element in self.elements:
            # energyave = (self.energy[ielement]+self.energy[ielement-1])/2.0
            energyave = self.energy[ielement]
            # print energyave
            if element.category == 'rbend' or element.category == 'sbend' :
                angle  = element['angle']
                length = element['l']

                # insert magnetic field value after angle
                element._keysextra.insert(element._keysextra.index('angle')+1,'B')
                # consistent calculation with BDSIM
                element['B'] = self.charge*energyave/0.299792458*angle/length
            elif element.category == 'quadrupole' :
                element['k1'] = energyave / self.energy0 * element['k1']
            elif element.category == 'sextupole' :
                element['k2'] = energyave / self.energy0 * element['k2']
            elif element.category == 'octupole':
                element['k3'] = energyave / self.energy0 * element['k3']
            elif element.category == 'decupole':
                element['k4'] = energyave / self.energy0 * element['k4']
            elif element.category == 'multipole' :
                pass
            ielement += 1

    def Write(self, filename, verbose=False, overwrite=True):
        """
        Write the machine to a series of gmad files.

        kwargs:
        overwrite : Do not append an integer to the basefilename if
        already exists, instead overwrite existing files.
        """
        if self.sr :
            self.SynchrotronRadiationRescale()

        verboseresult = verbose or self.verbose
        writer = _Writer.Writer()
        writer.WriteMachine(self,filename,verboseresult)

    def AddObject(self, obj):
        """
        Add an object or definition to be written to the model. An 'object'
        is a definition that isn't part of a sequence such as a Field, Crystal,
        or Placement. Anything that has a string representation can be added to
        the list.

        For an iterable object, tuple, list, and dict are accepted. For a dict,
        the value (not the key) is added to the internal list without the key.

        Objects:
        Aperture, Atom, BLM, CavityModel, Crystal, Field, Laser, Material, NewColour
        Placement, Query, Region, SamplerPlacement, Scorer, ScorerMesh, XSecBias.
        """
        if type(obj) in [list, tuple]:
            for ob in obj:
                self.AddObject(ob)
        elif type(obj) is dict:
            for k,v in obj.items():
                self.AddObject(v)
        else:
            self.objects.append(obj)

    def AddBias(self, biases):
        """
        Add a Builder.XSecBias instance or iterable of instances to this machine.
        """
        self.AddObject(biases)

    def AddMaterial(self, materials):
        """
        Add a Builder.Material instance or iterable of instances
        to this machine.
        """
        # If a single material object
        if isinstance(materials, pybdsim.Builder.Material):
            self.material.append(materials)
        else: # An iterable of materials.
            try:
                for material in materials:
                    self.AddMaterial(material)
            except TypeError:
                msg = ("Unknown material! Materials must be a Builder.Material"
                       "instance or an iterable of Builder.Material instances.")
                raise TypeError(msg)

    def AddBeam(self, beam=None):
        """
        Assign a beam instance to this machine. If no Beam instance is provided,
        a reference distribution is used.
        """
        if beam == None:
            self.beam = _Beam.Beam()
        elif type(beam) != _Beam.Beam:
            raise TypeError("Incorrect type - please provide pybdsim.Beam.Beam instance")
        self.beam = beam

    def AddOptions(self, options=None):
        """
        Assign an options instance to this machine.
        """
        if type(options) != _Options.Options:
            raise TypeError("Incorrect type - please provide pybdsim.Options.Options instance")
        self.options = options

    def AddIncludePre(self, include):
        """
        Add the name of a file (str) that should be included in the main file before others.
        """
        self.includesPre.append(include)

    def AddIncludePost(self, include):
        """
        Add the name of a file (str) that should be included in the main file after others.
        """
        self.includesPost.append(include)

    def AddDrift(self, name='dr', length=0.1, **kwargs):
        """
        Add a drift to the beam line
        """
        if self.verbose:
            print('AddDrift>  ',name,' ',length,' ',kwargs)
        if length < 1e-12:
            self.AddMarker(name)
        else:
            self.Append(Element(name, 'drift', l=length ,**kwargs))

    def AddDipole(self, name='dp', category='sbend', length=0.1,
                  angle=None, b=None, **kwargs):
        """
        AddDipole(category='sbend')

        category - 'sbend' or 'rbend' - sector or rectangular bend
        """
        if category not in ['sbend','rbend']:
            s = 'Invalid category ' + category
            raise ValueError(s)
        if angle is None and b is None:
            raise TypeError('angle or b must be specified for a dipole')
        elif angle != None:
            self.Append(Element(name, category, l=length, angle=angle, **kwargs))
        else:
            self.Append(Element(name, category, l=length, B=b, **kwargs))

    def AddRBend(self, name="rb", length=0.1, angle=None, b=None, **kwargs):
        self.AddDipole(name, 'rbend', length, angle, b, **kwargs)

    def AddSBend(self, name="sb", length=0.1, angle=None, b=None, **kwargs):
            self.AddDipole(name, 'sbend', length, angle, b, **kwargs)

    def AddQuadrupole(self, name='qd', length=0.1, k1=0.0, **kwargs):
        self.Append(Element(name, 'quadrupole', l=length, k1=k1, **kwargs))

    def AddSextupole(self, name='sx', length=0.1, k2=0.0, **kwargs):
        self.Append(Element(name, 'sextupole', l=length, k2=k2, **kwargs))

    def AddOctupole(self, name='oc', length=0.1, k3=0.0, **kwargs):
        self.Append(Element(name, 'octupole', l=length, k3=k3 ,**kwargs))

    def AddDecapole(self, name='dc', length=0.1, k4=0.0, **kwargs):
        self.Append(Element(name, 'decapole', l=length,k4=k4,**kwargs))

    def AddMultipole(self, name='mp', length=0.1, knl=(0,0), ksl=(0,0), **kwargs):
        if length > 1e-12:
            self.Append(Element(name,'multipole', l=length, knl=knl, ksl=ksl, **kwargs))
        else:
            self.AddThinMultipole(name, knl, ksl, **kwargs)

    def AddThinMultipole(self, name='mp', knl=(0,0), ksl=(0,0), **kwargs):
        self.Append(Element(name,'thinmultipole', knl=knl, ksl=ksl, **kwargs))

    def AddVKicker(self, name='vk', vkick=0.0, **kwargs):
        self.Append(Element(name, 'vkicker', vkick=vkick, **kwargs))

    def AddHKicker(self, name='hk', hkick=0.0, **kwargs):
        self.Append(Element(name, 'hkicker', hkick=hkick, **kwargs))

    def AddKicker(self, name='kk', hkick=0.0, vkick=0.0, **kwargs):
        self.Append(Element(name, 'kicker', hkick=hkick, vkick=hkick, **kwargs))

    def AddTKicker(self, name='tk', hkick=0.0, vkick=0.0, **kwargs):
        self.Append(Element(name, 'tkicker', hkick=hkick, vkick=vkick, **kwargs))

    def AddRFCavity(self, name='arreff', length=0.1, gradient=10, **kwargs):
        self.Append(Element(name, 'rfcavity', l=length, gradient=gradient, **kwargs))

    def AddTarget(self, name='trg', length=0.1, material="Cu", **kwargs):
        self.Append(Element(name, 'target', l=length, material=material, **kwargs))

    def AddRCol(self, name='rc', length=0.1, xsize=0.1, ysize=0.1, **kwargs):
        d = {}
        for k,v in kwargs.items():
            if 'aper' not in str(k).lower():
                d[k] = v
        self.Append(Element(name, 'rcol', l=length, xsize=xsize, ysize=ysize, **d))

    def AddJCol(self, name='jc', length=0.1, xsize=0.1, ysize=0.1, **kwargs):
        d = {}
        for k,v in kwargs.items():
            if 'aper' not in str(k).lower():
                d[k] = v
        self.Append(Element(name, 'jcol', l=length, xsize=xsize, ysize=ysize, **d))

    def AddECol(self, name='ec', length=0.1, xsize=0.1, ysize=0.1, **kwargs):
        d = {}
        for k,v in kwargs.items():
            if 'aper' not in str(k).lower():
                d[k] = v
        self.Append(Element(name,'ecol',l=length,xsize=xsize,ysize=ysize,**d))

    def AddDegrader(self, length=0.1, name='deg', nWedges=1, wedgeLength=0.1, degHeight=0.1, materialThickness=None, degraderOffset=None, **kwargs):
        if (materialThickness==None) and (degraderOffset==None):
            raise TypeError('materialThickness or degraderOffset must be specified for a degrader')
        elif materialThickness != None:
            self.Append(Element(name,'degrader',l=length,numberWedges=nWedges,wedgeLength=wedgeLength,
                                degraderHeight=degHeight, materialThickness=materialThickness,**kwargs))
        else:
            self.Append(Element(name,'degrader',l=length,numberWedges=nWedges,wedgeLength=wedgeLength,
                                degraderHeight=degHeight, degraderOffset=degraderOffset,**kwargs))

    def AddMuSpoiler(self, name='mu', length=0.1, b=0.0, **kwargs):
        self.Append(Element(name, 'muspoiler', l=length, B=b, **kwargs))

    def AddShield(self, name='sh', length=0.1, **kwargs):
        self.Append(Element(name, 'shield', l=length, **kwargs))

    def AddDump(self, name='du', length=0.1, **kwargs):
        self.Append(Element(name, 'dump', l=length, **kwargs))

    def AddSolenoid(self, name='sl', length=0.1, ks=0.0, **kwargs):
        self.Append(Element(name, 'solenoid', l=length, ks=ks, **kwargs))

    def AddLaser(self, length=0.1, name='lsr', x=1, y=0, z=0, waveLength=532e-9, **kwargs):
        self.Append(Element(name, 'laser', l=length, x=x, y=y, z=z, waveLength=waveLength, **kwargs))

    def AddGap(self, name='gp', length=1.0, **kwargs):
        self.Append(Element(name, 'gap', l=length, **kwargs))

    def AddCrystalCol(self, name='cc', length=0.01, xsize=1e-3, **kwargs):
        objNames = [obj.name for obj in self.objects]
        for k,v in kwargs.items():
            if (k == "crystalBoth") and (v not in objNames):
                print("Warning: crystalBoth object " + v + " not known.")
            if (k == "crystalLeft") and (v not in objNames):
                print("Warning: crystalLeft object " + v + " not known.")
            if (k == "crystalRight") and (v not in objNames):
                print("Warning: crystalRight object " + v + " not known.")
        self.Append(Element(name,'crystalcol',l=length,xsize=xsize,**kwargs))

    def AddUndulator(self, name='un', length=1.0, b=0, undulatorPeriod=0.1, **kwargs):
        self.Append(Element(name,'undulator',l=length,B=b,undulatorPeriod=undulatorPeriod,**kwargs))

    def AddTransform3D(self, name='t3d',**kwargs):
        if len(list(kwargs.keys())) == 0:
            pass
        else:
            self.Append(Element(name,'transform3d',**kwargs))

    def AddRmat(self, name='rmat', length=0.1,
                r11=1.0, r12=0, r13=0, r14=0,
                r21=0, r22=1.0, r23=0, r24=0,
                r31=0, r32=0, r33=1.0, r34=0,
                r41=0, r42=0, r43=0, r44=1.0,
                **kwargs):
        self.Append(Element(name, 'rmatrix', l=length,
                            rmat11=r11, rmat12=r12, rmat13=r13, rmat14=r14,
                            rmat21=r21, rmat22=r22, rmat23=r23, rmat24=r24,
                            rmat31=r31, rmat32=r32, rmat33=r33, rmat34=r34,
                            rmat41=r41, rmat42=r42, rmat43=r43, rmat44=r44,
                            **kwargs))

    def AddThinRmat(self, name='rmatthin',
                    r11=1.0, r12=0, r13=0, r14=0,
                    r21=0, r22=1.0, r23=0, r24=0,
                    r31=0, r32=0, r33=1.0, r34=0,
                    r41=0, r42=0, r43=0, r44=1.0,
                    **kwargs):
        self.Append(Element(name, 'thinrmatrix',
                            rmat11=r11, rmat12=r12, rmat13=r13, rmat14=r14,
                            rmat21=r21, rmat22=r22, rmat23=r23, rmat24=r24,
                            rmat31=r31, rmat32=r32, rmat33=r33, rmat34=r34,
                            rmat41=r41, rmat42=r42, rmat43=r43, rmat44=r44,
                            **kwargs))

    def AddElement(self, name='el', length=0.1, outerDiameter=1, geometryFile="geometry.gdml", **kwargs):
        self.Append(Element(name, 'element',l=length,outerDiameter=outerDiameter,geometryFile=geometryFile, **kwargs))

    def AddMarker(self, name='mk'):
        self.Append(Element(name, 'marker'))

    def AddWireScanner(self, name='ws', length=0.1, wireDiameter=1e-3, wireLength=0.1, **kwargs):
        self.Append(Element(name, 'dump', l=length, wireLength=wireLength, wireDiameter=wireDiameter, **kwargs))

    def AddCT(self, name="ctscan", length=1.0, dicomDataFile="", dicomDataPath="", **kwargs):
        self.Append(Element(name, 'ct', l=length, dicomDataFile=dicomDataFile, dicomDataPath=dicomDataPath, **kwargs))


    def AddFodoCell(self, basename='fodo', magnetlength=1.0, driftlength=4.0,kabs=0.2,**kwargs):
        """
        AddFodoCell(basename,magnetlength,driftlength,kabs,**kwargs)
        basename     - the basename for the fodo cell beam line elements
        magnetlength - length of magnets in metres
        driftlength  - length of drift segment in metres
        kabs         - the absolute value of the quadrupole strength - alternates between magnets

        kwargs are other parameters for bdsim - ie material='Fe'
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

    def AddFodoCellSplitDrift(self, basename='fodo', magnetlength=1.0, driftlength=4.0, kabs=0.2,nsplits=10, **kwargs):
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

        kwargs are other parameters for bdsim - ie aper=0.2
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

    def AddFodoCellMultiple(self, basename='fodo', magnetlength=1.0, driftlength=4.0, kabs=0.2, ncells=2, **kwargs):
        ncells = int(ncells)
        maxn   = int(len(str(ncells)))
        for i in range(ncells):
            cellname = basename+'_'+str(i).zfill(maxn)
            self.AddFodoCell(cellname,magnetlength,driftlength,kabs,**kwargs)

    def AddFodoCellSplitDriftMultiple(self, basename='fodo', magnetlength=1.0, driftlength=4.0, kabs=0.2, nsplits=10, ncells=2, **kwargs):
        ncells = int(ncells)
        maxn   = int(len(str(ncells)))
        for i in range(ncells):
            cellname = basename+'_'+str(i).zfill(maxn)
            self.AddFodoCellSplitDrift(cellname,magnetlength,driftlength,kabs,nsplits=10,**kwargs)

    def AddSampler(self, names):
        if isinstance(names, str):
            if names == "all":
                self.samplers.append(Sampler("all"))
            elif names == "first":
                self.samplers.append(Sampler(self.sequence[0]))
            elif names == "last":
                self.samplers.append(Sampler(self.sequence[-1]))
            else:
                if names not in self.sequence:
                    msg = "{} not found to attach sampler to.".format(names)
                    raise ValueError(msg)
                self.samplers.append(Sampler(names))
        else: # assume some flat iterable of sampler names.
            for name in names:
                self.AddSampler(name)

    def AddCrystal(self, name, **kwargs):
        self.objects.append(Crystal(name, **kwargs))

    def AddScorerMesh(self, name, **kwargs):
        self.objects.append(ScorerMesh(name, **kwargs))

    def AddPlacement(self, name, **kwargs):
        self.objects.append(Placement(name, **kwargs))

    def AddBLM(self, name, **kwargs):
        self.objects.append(BLM(name, **kwargs))

    def AddRmat(self, name='rmat', length=0.1,
                r11=1.0, r12=0, r13=0, r14=0,
                r21=0, r22=1.0, r23=0, r24=0,
                r31=0, r32=0, r33=1.0, r34=0,
                r41=0, r42=0, r43=0, r44=1.0,
                **kwargs):
        self.Append(Element(name, 'rmatrix', l=length,
                            rmat11=r11, rmat12=r12, rmat13=r13, rmat14=r14,
                            rmat21=r21, rmat22=r22, rmat23=r23, rmat24=r24,
                            rmat31=r31, rmat32=r32, rmat33=r33, rmat34=r34,
                            rmat41=r41, rmat42=r42, rmat43=r43, rmat44=r44,
                            **kwargs))

    def AddThinRmat(self, name='rmatthin',
                    r11=1.0, r12=0, r13=0, r14=0,
                    r21=0, r22=1.0, r23=0, r24=0,
                    r31=0, r32=0, r33=1.0, r34=0,
                    r41=0, r42=0, r43=0, r44=1.0,
                    **kwargs):
        self.Append(Element(name, 'thinrmatrix',
                            rmat11=r11, rmat12=r12, rmat13=r13, rmat14=r14,
                            rmat21=r21, rmat22=r22, rmat23=r23, rmat24=r24,
                            rmat31=r31, rmat32=r32, rmat33=r33, rmat34=r34,
                            rmat41=r41, rmat42=r42, rmat43=r43, rmat44=r44,
                            **kwargs))

# General scripts below this point

def PrepareApertureModel(rowDictionary, default='circular', warningName=""):
    rd = rowDictionary # shortcut
    a1 = rd['APER_1']
    a2 = 0.0
    a3 = 0.0
    a4 = 0.0
    if 'APER_2' in rd:
        a2 = rd['APER_2']
    if 'APER_3' in rd:
        a3 = rd['APER_3']
    if 'APER_4' in rd:
        a4 = rd['APER_4']
    
    if 'APERTYPE' in list(rd.keys()):
        aType = str.lower(rd['APERTYPE'])
        # possible to be 'none' which isn't valid - replace with default
        if aType == 'none':
            aType = default
    else:
        # no type given - let's guess :(
        if a1 == a2 == a3 == a4:
            aType = 'circular'
            a2 = a3 = a4 = 0 # set 0 to save writing needlessly
        else:
            aType = default
    a = ApertureModel(aType,a1,a2,a3,a4,warningName=warningName)
    return a

def CreateDipoleRing(filename, ndipoles=60, circumference=100.0, samplers='first'):
    """
    Create a ring composed of only dipoles
    filename
    ncells        - number of cells, each containing 1 dipole and a drift
    circumference - in metres
    samplers      - 'first', 'last' or 'all'

    """
    ndipoles = int(ndipoles)
    a            = Machine()
    dangle       = 2.0*_math.pi / float(ndipoles)
    dipolelength = circumference / float(ndipoles)
    for i in range(ndipoles):
        a.AddDipole(length=dipolelength, angle=dangle)
    a.AddSampler(samplers)
    a.Write(filename)

def CreateDipoleDriftRing(filename, ncells=60, circumference=100.0, driftfraction=0.1, samplers='first'):
    """
    Create a ring composed of dipoles and drifts
    filename
    ncells        - number of cells, each containing 1 dipole and a drift
    circumference - in metres
    driftfraction - the fraction of drift in each cell (0.0 < driftfraction < 1.0)
    samplers      - 'first', 'last' or 'all'

    """
    ncells = int(ncells)
    if driftfraction > 1.0:
        raise Warning("Fraction of drift must be less than 1.0 -> setting to 0.9")
        driftfraction = 0.9
    if driftfraction < 0.0:
        raise Warning("Fraction of drift must be greater than 1.0 -> setting to 0.1")
        driftfraction = 0.1
    a            = Machine()
    dangle       = 2.0*_math.pi / float(ncells)
    clength      = circumference / float(ncells)
    driftlength  = clength * driftfraction
    dipolelength = clength - driftlength
    for i in range(ncells):
        a.AddDipole(length=dipolelength*0.5, angle=dangle*0.5)
        a.AddDrift(length=driftlength)
        a.AddDipole(length=dipolelength*0.5, angle=dangle*0.5)
    a.AddSampler(samplers)
    a.Write(filename)

def CreateDipoleFodoRing(filename, ncells=60, circumference=200.0, ncellsToMake=None, samplers='first'):
    """
    Create a ring composed of fodo cells with 2 dipoles per fodo cell.

    filename
    ncells         - number of fodo+dipole cells to create
    circumference  - circumference of machine in metres
    ncellsToMake   - number of cells to actually build for part of the machine (None = all)
    samplers       - 'first','last' or 'all'

    Hard coded to produce the following cell fractions:
    50% dipoles
    20% quadrupoles
    30% beam pipe / drift
    """
    a       = Machine()
    cangle  = 2.0*_math.pi / ncells
    clength = float(circumference) / ncells
    #dipole = 0.5 of cell, quads=0.2, drift=0.3, two dipoles
    #dipole:
    dl  = clength * 0.25
    da  = cangle * 0.5
    #quadrupole:
    ql  = clength * 0.2 * 0.5
    k1  = SuggestFodoK(ql,dl)
    #drift:
    drl = clength * 0.3 * 0.25
    #naming
    nplaces  = len(str(ncells))
    basename = 'dfodo_'
    if ncellsToMake is None:
        ncellsToMake = ncells
    for i in range(ncellsToMake):
        cellname = basename + str(i).zfill(nplaces)
        a.AddQuadrupole(cellname+'_qd_a',ql*0.5,k1)
        a.AddDrift(cellname+'_dr_a',drl)
        a.AddDipole(cellname+'_dp_a','sbend',dl,da)
        a.AddDrift(cellname+'_dr_b',drl)
        a.AddQuadrupole(cellname+'_qf_b',ql,k1*-1.0)
        a.AddDrift(cellname+'_dr_c',drl)
        a.AddDipole(cellname+'_dp_b','sbend',dl,da)
        a.AddDrift(cellname+'_dr_d',drl)
        a.AddQuadrupole(cellname+'_qd_c',ql*0.5,k1)
    a.AddSampler(samplers)
    a.Write(filename)

def CreateFodoLine(filename, ncells=10, driftlength=4.0, magnetlength=1.0, samplers='all',**kwargs):
    """
    Create a FODO lattice with ncells.

    ncells       - number of fodo cells
    driftlength  - length of drift segment in between magnets
    magnetlength - length of quadrupoles
    samplers     - 'all','first' or 'last'
    kwargs       - kwargs to supply to quadrupole constructor

    """
    ncells = int(ncells)
    a      = Machine()
    k1     = SuggestFodoK(magnetlength,driftlength)
    a.AddFodoCellSplitDriftMultiple(magnetlength=magnetlength,driftlength=driftlength,kabs=k1,nsplits=10,ncells=ncells,**kwargs)
    a.AddSampler(samplers)
    a.Write(filename)

def SuggestFodoK(magnetlength,driftlength):
    """
    SuggestFodoK(magnetlength,driftlength)

    returns k1 (float) value for matching into next quad in a FODO cell.
    f = 1/(k1 * magnetlength) = driftlength -> solve for k1

    Note the convention in pybdsim.Builder is that the quadrupoles in
    the fodo cell are split in two.  So this is in fact half the integrated
    k you need.  This matches with the other functions in Builder.

    """
    return 1.0 / (float(magnetlength)*(float(magnetlength) + float(driftlength)))

def GenerateSamplersFromBDSIMSurvey(surveyfile,outputfilename,excludesamplers=True):
    """
    Create a gmad file with samplers for all the elements in a beamline
    as described by the survey outline from bdsim

    bdsim --file=mylattice.gmad --outline=survey.dat --outline_type=survey

    excludesamplers - bool - exclude any existing samplers

    """
    a = _Data.Load(surveyfile)
    samplers = []
    for name in a.Name():
        if ('ampler' in name) and excludesamplers:
            pass
        else:
            samplers.append(Sampler(name))

    #write the output
    f = open(outputfilename,'w')
    for sampler in samplers:
        f.write(repr(sampler))
    f.close()
