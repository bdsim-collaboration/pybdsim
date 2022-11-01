from copy import deepcopy as _deepcopy
import numpy as _np
import math as _math
import pymad8 as _m8
import warnings as _warnings
from .. import Builder as _Builder
from .. import Beam as _Beam
from .. import Data as _Data
from ..Options import Options as _Options
import pybdsim._General

_ignoreableThinElements = {"MONI", "IMON", "BLMO", "MARK", "RCOL", "ECOL", "INST", "WIRE"}


# Constants
# anything below this length is treated as a thin element
_THIN_ELEMENT_THRESHOLD = 1e-6


def Mad8Twiss2Gmad(inputfilename, outputfilename,
				   startindex            = 0,
				   endindex              = -1,
				   stepsize              = 1,
				   ignorezerolengthitems = True,
				   samplers              = 'all',
				   aperturedict          = {},
				   aperlocalpositions    = {},
				   collimatordict        = {},
				   userdict              = {},
				   partnamedict          = {},
				   verbose               = False,
				   beam                  = True,
				   flipmagnets           = None,
				   defaultAperSize       = 0.1,
				   defaultAperShape      = 'circular',
				   biases                = None,
				   materials			  = None,
				   allelementdict        = {},
				   optionsdict           = {},
				   beamparamsdict        = {},
				   linear                = False,
				   overwrite             = True,
				   write                 = True,
				   namePrepend           = ""):

	"""
	**Mad82Gmad** convert a mad8 output file into a gmad tfs file for bdsim

	Example:

	>>> a,b = pybdsim.Convert.MadxTfs2Gmad('twissfile', 'mymachine')

	returns Machine, [omittedItems]

	Returns two pybdsim.Builder.Machine instances. The first desired full conversion.  The second is
	the raw conversion that's not split by aperture. Thirdly, a list of the names of the omitted items
	is returned.

	+-------------------------------+-------------------------------------------------------------------+
	| **inputfilename**             | Path to the Mad8 input file.                                      |
	+-------------------------------+-------------------------------------------------------------------+
	| **outputfilename**            | Requested output file.                                            |
	+-------------------------------+-------------------------------------------------------------------+
	| **startindex**                | Index of the lattice element to start the machine at.             |
	|                               | This item is included in the lattice.                             |
	+-------------------------------+-------------------------------------------------------------------+
	| **endindex**                  | Index of the lattice element to stop the machine at.              |
	|                               | This item is not included in the lattice.                         |
	+-------------------------------+-------------------------------------------------------------------+
	| **stepsize**                  | Slice step size. Default is 1, but -1 also useful for             |
	|                               | reversed line.                                                    |
	+-------------------------------+-------------------------------------------------------------------+
	| **ignorezerolengthitems**     | nothing can be zero length in bdsim as real objects of course     |
	|                               | have some finite size.  Markers, etc are acceptable but for large |
	|                               | lattices this can slow things down. True allows to ignore these   |
	|                               | altogether, which doesn't affect the length of the machine.       |
	+-------------------------------+-------------------------------------------------------------------+
	| **samplers**                  | can specify where to set samplers - options are None, 'all', or a |
	|                               | list of names of elements (normal python list of strings). Note   |
	|                               | default 'all' will generate separate outputfilename_samplers.gmad |
	|                               | with all the samplers which will be included in the main .gmad    |
	|                               | file - you can comment out the include to therefore exclude all   |
	|                               | samplers and retain the samplers file.                            |
	+-------------------------------+-------------------------------------------------------------------+
	| **aperturedict**              | Aperture information. Can either be a dictionary of dictionaries  |
	|                               | with the the first key the exact name of the element and the      |
	|                               | daughter dictionary containing the relevant bdsim parameters as   |
	|                               | keys (must be valid bdsim syntax).                                |
	+-------------------------------+-------------------------------------------------------------------+
	| **aperlocalpositions**        | Dictionary of element indices to local aperture definitions       |
	|                               | of the form                                                       |
	|                               | {1: [(0.0, {"APERTYPE": "circular",   "APER_1": 0.4}),            |
	|                               |      (0.5, {"APERTYPE": "elliptical", "APER_1": 0.3,              |
	|                               |                                       "APER_2": 0.4}),            |
	|                               |      ...],                                                        |
	|                               |  2: [...],                                                        |
	|                               | }                                                                 |
	|                               | This defines apertures in the element at index 1 starting with a  |
	|                               | "circular" aperture from 0.0m (i.e. the start) before changing to |
	|                               | "elliptical" after 0.5m in the element, with possible further     |
	|                               | changes not displayed above.                                      |
	|                               | As the aperture definition in GMAD is tied inseparable from its   |
	|                               | aperture definition, and vice versa, this conversion function     |
	|                               | will automatically split the element at the local aperture points |
	|                               | whilst retaining optical correctness.                             |
	|                               | This kwarg is mutually exclusive with "aperturedict".             |
	+-------------------------------+-------------------------------------------------------------------+
	| **collimatordict**            | A dictionary of dictionaries with collimator information.         |
	|                               | Keys should be exact string match of element name in Mad8 file.   |
	|                               | Value should be dictionary with the following keys:               |
	|                               | "material"         - the material                                 |
	|                               | "tilt"             - rotation angle of collimator in radians      |
	|                               | "xsize"            - x full width in metres                       |
	|                               | "ysize"            - y full width in metres                       |
	+-------------------------------+-------------------------------------------------------------------+
	| **userdict**                  | Dictionary that supply any additional information for an element. |
	|                               | Keys should match the exact element name in the Mad8 file.        |
	|                               | Value should be dictionary itself with key, value pairs of        |
	|                               | parameters and values to be added to that particular element.     |
	+-------------------------------+-------------------------------------------------------------------+
	| **partnamedict**              | Dictionary of dictionaries. The key is a substring of             |
	|                               | that should be matched. ie add the parameter 'vhRatio' : 1 to all |
	|                               | elements with 'MBVA' in their name.                               |
	+-------------------------------+-------------------------------------------------------------------+
	| **verbose**                   | Print out lots of information when building the model.            |
	+-------------------------------+-------------------------------------------------------------------+
	| **beam**                      | True / False - generate an input gauss Twiss beam based on the    |
	|                               | values of the twiss parameters at the beginning of the lattice    |
	|                               | (startname) NOTE - we thoroughly recommend checking these         |
	|                               | parameters and this functionality is only for partial convenience |
	|                               | to have a model that works straight away.                         |
	+-------------------------------+-------------------------------------------------------------------+
	| **flipmagnets**               | True / False - flip the sign of all k values for magnets.         |
	|                               | Mad8 currently tracks particles agnostic of the particle charge.  |
	|                               | BDSIM however, follows the definition strictly :                  |
	|                               | Positive k implies horizontal focussing for positive particles    |
	|                               | therefore, vertical focussing for negative particles.             |
	|                               | Use this flag to flip the sign of all magnets.                    |
	+-------------------------------+-------------------------------------------------------------------+
	| **defaultAperSize**           | Aperture size to assu;e if none is specified. Default is 0.1m     |
	+-------------------------------+-------------------------------------------------------------------+
	| **defaultAperShape**          | Aperture shape to assume if none is specified.                    |
	|                               | Default is 'circular'.                                            |
	+-------------------------------+-------------------------------------------------------------------+
	| **biases**                    | Optional list of bias objects to be defined in own _bias.gmad     |
	|                               | file.  These can then be attached either with allelementdict for  |
	|                               | all components or userdict for individual ones.                   |
	+-------------------------------+-------------------------------------------------------------------+
	| **materials**                 | Optional list of material objects to be defined in own            |
	|                               | _materials.gmad file.  These can then be attached either with     |
	|                               | allelementdict for all components or userdict for individual ones.|
	+---------------------------------------------------------------------------------------------------+
	| **allelementdict**            | Dictionary of parameter/value pairs to be written to all elements |
	+-------------------------------+-------------------------------------------------------------------+
	| **optionsdict**               | Optional dictionary of general options to be written to the       |
	|                               | bdsim model options.                                              |
	+-------------------------------+-------------------------------------------------------------------+
	| **beamparamsdict**            | Optional dictionary of parameters to be passed to the beam.       |
	+-------------------------------+-------------------------------------------------------------------+
	| **linear**                    | Only linear optical components                                    |
	+-------------------------------+-------------------------------------------------------------------+
	| **overwrite**                 | Do not append an integer to the base file name if it already      |
	|                               | exists.  Instead overwrite the files.                             |
	+-------------------------------+-------------------------------------------------------------------+
	| **write**                     | Whether to write the converted machine to file or not.            |
	+-------------------------------+-------------------------------------------------------------------+
	| **namePrepend**               | Optional string prepended to the name of every component.         |
	+-------------------------------+-------------------------------------------------------------------+

	"""

	# test for inputfilename type
	if type(inputfilename) == str:
		twiss = _m8.Output(inputfilename)
		rmat = None
		if twiss.filetype != 'twiss':
			raise ValueError('Expect a twiss file to convert')
		data = twiss.data
	elif type(inputfilename) == dict:
		twiss = _m8.Output(inputfilename['twiss'])
		rmat = _m8.Output(inputfilename['rmat'], 'rmat')
		if twiss.filetype != 'twiss' or rmat.filetype != 'rmat':
			raise ValueError('Expect a twiss file and a rmat file to convert')
		data = twiss.data.merge(rmat.data)
	else:
		raise TypeError('Expect either a twiss file string or a dictionary with twiss and rmat file strings')

	# machine instance that will be added to
	machine = _Builder.Machine()

	# check if dictionaries are dictionaries
	varnames = ['collimatordict', 'userdict', 'partnamedict', 'allelementdict', 'optionsdict', 'beamparamsdict']
	vars     = [collimatordict,   userdict,  partnamedict,  allelementdict,  optionsdict,  beamparamsdict]
	for var, varname in zip(vars, varnames):
		typevar = type(var)
		if typevar not in (dict, _Data.BDSAsciiData):
			raise TypeError("Argument '" + varname + "' is not a dictionary")

	# can't use 'aperturedict' and 'aperlocalpositions' at the same time
	if aperturedict and aperlocalpositions:
		raise TypeError("'aperturedict' and 'aperlocalpositions' are mutually exclusive.")

	# try to check automatically if we need to flip magnets
	if "particletype" in beamparamsdict and flipmagnets is None:
		particletype = beamparamsdict['particletype']
		if particletype == "e-" or particletype == "electron":
			flipmagnets = True
			print('Detected electron in TFS file - changing flipmagnets to True')

	# If we have collimators but no collimator dict then inform that they will be converted to drifts
	if ("RCOL" in data['TYPE'] or "ECOL" in data['TYPE']) and not collimatordict:
		_warnings.warn("No collimatordict provided.  ALL collimators will be converted to DRIFTs.")

	if biases is not None:
		machine.AddBias(biases)

	if materials is not None:
		machine.AddMaterial(materials)

	# keep list of omitted zero length items
	itemsomitted = []

	# ==MAIN LOOP== #
	for item in data.iloc[startindex:endindex][::stepsize].iloc:
		index = item.name
		name = item['NAME']
		t = item['TYPE']
		l = item['L']
		
		# skip ignorable thin elements of zero length
		zerolength = True if l < 1e-9 else False
		if zerolength and t in _ignoreableThinElements:
			if verbose:
				print('skipping zero-length item: {}'.format(name))
			itemsomitted.append(name)
			continue

		gmadElement = _Mad82GmadElementFactory(item, allelementdict, verbose,userdict, collimatordict, partnamedict,
									flipmagnets, linear, zerolength, ignorezerolengthitems, namePrepend="", rmat=rmat)

		if gmadElement is None:  # factory returned nothing, go to next item.
			continue
		elif gmadElement.length == 0.0 and isinstance(gmadElement, _Builder.Drift):  # skip drifts of length 0
			continue
		elif l == 0 or name in collimatordict:  # Don't add apertures to thin elements or collimators
			machine.Append(gmadElement)
		elif aperlocalpositions and index in aperlocalpositions:  # split aperture if provided
			elements_split_with_aper = _GetElementSplitByAperture(gmadElement, aperlocalpositions[index])
			for ele in elements_split_with_aper:
				machine.Append(ele)
		else:  # Get element with single aperture
			element_with_aper = _GetSingleElementWithAper(twiss, item, gmadElement, aperturedict,
														  defaultAperSize, defaultAperShape)
			machine.Append(element_with_aper)

	if samplers is not None:  # Add Samplers
		machine.AddSampler(samplers)

	if beam:  # Add Beam
		bm = Mad82GmadBeam(data, startindex, verbose, extraParamsDict=beamparamsdict)
		machine.AddBeam(bm)

	options = _Options()  # Add Options
	if optionsdict:
		options.update(optionsdict)  # expand with user supplied bdsim options
	machine.AddOptions(options)

	if verbose:
		print('Total length: ', machine.GetIntegratedLength())
		print('Total angle:  ', machine.GetIntegratedAngle())
		print('items omitted: ')
		print(itemsomitted)
		print('number of omitted items: ', len(itemsomitted))

	if write:
		machine.Write(outputfilename, overwrite=overwrite)
	# We return machine twice to not break old interface of returning two machines.
	return machine, itemsomitted


def _Mad82GmadElementFactory(item, allelementdict, verbose,userdict, collimatordict, partnamedict,
							 flipmagnets, linear, zerolength, ignorezerolengthitems, namePrepend, rmat=None):
	"""
	Function which makes the correct GMAD element given a Mad8 element.
	"""
	# if it's already a prepared element, just return it
	if isinstance(item, _Builder.Element):
		return item

	factor = 1
	if flipmagnets is not None:
		factor = -1 if flipmagnets else 1  # flipping magnets

	kws = {}  # ensure empty
	kws = _deepcopy(allelementdict)  # deep copy as otherwise allelementdict gets irreparably changed!
	if verbose:
		print('Starting key word arguments from all element dict')
		print(kws)

	Type = item['TYPE']
	name = item['NAME']
	l = item['L']
	tilt = item['TILT']

	rname = pybdsim._General.PrepareReducedName(name)
	rname = namePrepend + rname
	
	# append any user defined parameters for this element into the kws dictionary
	if name in userdict:  # name appears in the madx.  try this first.
		kws.update(userdict[name])
	elif rname in userdict:  # rname appears in the gmad
		kws.update(userdict[rname])

	for partname in partnamedict:
		if partname in name:
			kws.update(partnamedict[partname])

	if verbose:
		print('Full set of key word arguments:')
		print(kws)

	if tilt != 0 and not _math.isnan(tilt):
		kws['tilt'] = tilt

	#######################################################################
	if Type == '    ':
		if not ignorezerolengthitems:
			return _Builder.Marker(rname)
	#######################################################################
	elif Type == 'DRIF':
		return _Builder.Drift(rname, l, **kws)
	#######################################################################
	elif Type == 'MARK':
		if not ignorezerolengthitems:
			return _Builder.Marker(rname)
	#######################################################################
	elif Type == 'SOLE':
		if l == 0.0 :
			return None # thin solenoid is omitted
		return _Builder.Solenoid(rname, l, ks=item['KS']/l, **kws)
	#######################################################################
	elif Type == 'INST':
		if zerolength and not ignorezerolengthitems:
			return _Builder.Marker(rname)
	#######################################################################
	elif Type == 'MONI':
		if zerolength and not ignorezerolengthitems:
			return _Builder.Marker(rname)
	#######################################################################
	elif Type == 'IMON':
		if not ignorezerolengthitems:
			return _Builder.Marker(rname)
	#######################################################################
	elif Type == 'BLMO':
		if not ignorezerolengthitems:
			return _Builder.Marker(rname)
	#######################################################################
	elif Type == 'WIRE':
		if not ignorezerolengthitems:
			return _Builder.Marker(rname)
	#######################################################################
	elif Type == 'QUAD':
		k1 = item['K1'] * factor
		return _Builder.Quadrupole(rname, l, k1, **kws)
	#######################################################################
	elif Type == 'SEXT':
		k2 = item['K2'] * factor if not linear else 0
		return _Builder.Sextupole(rname, l, k2, **kws)
	#######################################################################
	elif Type == 'OCTU':
		k3 = item['K3'] * factor if not linear else 0
		return _Builder.Octupole(rname, l, k3=k3, **kws)
	#######################################################################
	elif Type == 'DECU':
		pass
	#######################################################################
	elif Type == 'MULT':
		k1 = item['K1'] * factor
		k2 = item['K2'] * factor if not linear else 0
		k3 = item['K3'] * factor if not linear else 0
		ks = item['KS'] * factor
		if zerolength or l < _THIN_ELEMENT_THRESHOLD:
			return _Builder.ThinMultipole(rname, knl=(k1, k2, k3), ksl=ks, **kws)
		else:
			return _Builder.Multipole(rname, l, knl=(k1, k2, k3), ksl=ks, **kws)
	#######################################################################
	elif Type == 'HKIC':
		if verbose:
			print('HKICKER', rname)
		if not zerolength:
			if l > _THIN_ELEMENT_THRESHOLD:
				kws['l'] = l
		return _Builder.HKicker(rname, hkick=item['HKIC']*factor, **kws)
	#######################################################################
	elif Type == 'VKIC':
		if verbose:
			print('VKICKER', rname)
		if not zerolength:
			if l > _THIN_ELEMENT_THRESHOLD:
				kws['l'] = l
		return _Builder.VKicker(rname, vkick=item['VKIC']*factor, **kws)
	#######################################################################
	elif Type == 'KICK':
		if verbose:
			print('KICKER', rname)
		hkick = item['HKIC'] * factor
		vkick = item['VKIC'] * factor
		if not zerolength:
			if l > _THIN_ELEMENT_THRESHOLD:
				kws['l'] = l
		return _Builder.Kicker(rname, hkick=hkick, vkick=vkick, **kws)
	#######################################################################
	elif Type == 'SBEN':
		angle = item['ANGLE']
		e1 = item['E1'] if 'E1' in item else 0
		e2 = item['E2'] if 'E2' in item else 0
		h1 = item['H1'] if 'H1' in item else 0
		h2 = item['H2'] if 'H2' in item else 0
		k1 = item['K1']
		if e1 != 0:
			kws['e1'] = e1
		if e2 != 0:
			kws['e2'] = e2
		if h1 != 0:
			kws['h1'] = h1
		if h2 != 0:
			kws['h2'] = h2
		if k1 != 0:
			# NOTE we're not using factor for magnet flipping here
			kws['k1'] = k1
		return _Builder.SBend(rname, l, angle=angle, **kws)
	#######################################################################
	elif Type == 'RBEN':
		angle = item['ANGLE']
		e1 = item['E1'] if 'E1' in item else 0
		e2 = item['E2'] if 'E2' in item else 0
		h1 = item['H1'] if 'H1' in item else 0
		h2 = item['H2'] if 'H2' in item else 0
		k1 = item['K1']

		if angle != 0:  #protect against 0 angle rbends
			chordLength = 2 * (l / angle) * _np.sin(angle / 2.)
		else :
			# set element length to be the chord length - tfs output rbend length is arc length
			chordLength = l

		# subtract dipole angle/2 added on to poleface angles internally by madx
		poleInAngle = e1 - 0.5 * angle
		poleOutAngle = e2 - 0.5 * angle
		if poleInAngle != 0:
			kws['e1'] = poleInAngle
		if poleOutAngle != 0:
			kws['e2'] = poleOutAngle
		if h1 != 0:
			kws['h1'] = h1
		if h2 != 0:
			kws['h2'] = h2
		if k1 != 0:
			# NOTE we don't use factor here for magnet flipping
			kws['k1'] = k1
		return _Builder.RBend(rname, chordLength, angle=angle, **kws)
	#######################################################################
	elif Type == 'LCAV':
		volt = item['VOLT']
		freq = item['FREQ']
		lag = item['LAG']
		gradient = volt/l
		phase = lag * 2 * _np.pi

		if freq != 0:
			kws['freq'] = freq
		if phase != 0:
			kws['phase'] = phase
		return _Builder.RFCavity(rname, l, gradient=gradient, **kws)
	#######################################################################
	elif Type in {'ECOL', 'RCOL'}:
		if name in collimatordict:
			# gets a dictionary then extends kws dict with that dictionary
			colld = collimatordict[name]

			# collimator defined by external geometry file
			if 'geometryFile' in colld:
				kws['geometryFile'] = colld['geometryFile']
				k = 'outerDiameter'  # key
				if k not in kws:
					# not already specified via other dictionaries
					if k in colld:
						kws[k] = colld[k]
					else:
						kws[k] = 1  # ensure there's a default as not in madx
				return _Builder.ExternalGeometry(rname, l, **kws)
			else:
				kws['material'] = colld.get('material', 'copper')
				tilt = colld.get('tilt', 0)
				if tilt != 0:
					kws['tilt'] = tilt
				xsize = colld['xsize']
				ysize = colld['ysize']
				if verbose:
					print('collimator x,y size ', xsize, ysize)
				if 'outerDiameter' in colld:
					kws['outerDiameter'] = colld['outerDiameter']
				else:
					kws['outerDiameter'] = max([0.5, xsize * 2.5, ysize * 2.5])
				if Type == 'RCOL':
					return _Builder.RCol(rname, l, xsize, ysize, **kws)
				else:
					return _Builder.ECol(rname, l, xsize, ysize, **kws)
		# dict is incomplete or the component is erroneously
		# reffered to as a collimator even when it can be thought
		# of as a drift (e.g. LHC TAS).
		elif collimatordict != {}:
			msg = ("{} {} not found in collimatordict."
				" Will instead convert to a DRIFT!  This is not"
				" necessarily wrong!".format(Type, name))
			_warnings.warn(msg)
			return _Builder.Drift(rname, l, **kws)
		# if user didn't provide a collimatordict at all.
		else:
			return _Builder.Drift(rname, l, **kws)
	#######################################################################
	elif Type == 'MATR':
		if not isinstance('R11', item):
			raise ValueError('No Rmat file to extract element')
		index = item.name
		item = rmat.data.iloc[index]
		previtem = rmat.data.iloc[index-1]
		POSTMATRIX = _np.matrix([[item['R11'], item['R12'], item['R13'], item['R14']],
								 [item['R21'], item['R22'], item['R23'], item['R24']],
								 [item['R31'], item['R32'], item['R33'], item['R34']],
								 [item['R41'], item['R42'], item['R43'], item['R44']]])
		PRIORMATRIX = _np.matrix([[previtem['R11'], previtem['R12'], previtem['R13'], previtem['R14']],
								  [previtem['R21'], previtem['R22'], previtem['R23'], previtem['R24']],
								  [previtem['R31'], previtem['R32'], previtem['R33'], previtem['R34']],
								  [previtem['R41'], previtem['R42'], previtem['R43'], previtem['R44']]])

		RMAT = (POSTMATRIX*PRIORMATRIX.I)
		return _Builder.Rmat(rname, l, r11=RMAT[0, 0], r12=RMAT[0, 1], r13=RMAT[0, 2], r14=RMAT[0, 3],
							 		   r21=RMAT[1, 0], r22=RMAT[1, 1], r23=RMAT[1, 2], r24=RMAT[1, 3],
							 		   r31=RMAT[2, 0], r32=RMAT[2, 1], r33=RMAT[2, 2], r34=RMAT[2, 3],
							 		   r41=RMAT[3, 0], r42=RMAT[3, 1], r43=RMAT[3, 2], r44=RMAT[3, 3], **kws)
	#######################################################################
	else:
		print('unknown element type:', Type, 'for element named: ', name)
		if zerolength and not ignorezerolengthitems:
			print('putting marker in instead as its zero length')
			return _Builder.Marker(rname)
		print('putting drift in instead as it has a finite length')
		return _Builder.Drift(rname, l)
	#######################################################################


def _GetElementSplitByAperture(gmadElement, localApertures):
	"""Return an element with splited aperture"""
	# tolerate any bad apertures - like only a few - and just don't append them
	apertures = []
	for point, aper in localApertures:
		try:
			arp = _Builder.PrepareApertureModel(aper, warningName=gmadElement.name)
			apertures.append(arp)
		except ValueError:
			pass

	if localApertures[0][0] != 0.0:
		raise ValueError("No aperture defined at start of element.")
	if len(localApertures) > 1:
		split_points = [point for point, _ in localApertures[1:]]
		split_elements = gmadElement.split(split_points)
		for aper, split_element in zip(apertures, split_elements):
			split_element.update(aper)
		return split_elements
	elif len(localApertures) == 1:
		gmadElement = _deepcopy(gmadElement)
		gmadElement.update(apertures[0])
		return [gmadElement]
	raise ValueError("Unable to split element by apertures.")


def _GetSingleElementWithAper(twiss, item, gmadElement, aperturedict, defaultAperSize, defaultAperShape):
	"""Return an element with unsplit aperture"""
	gmadElement = _deepcopy(gmadElement)
	name = item["NAME"]
	index = item.name
	aper = {}
	if name in aperturedict:
		aper = _Builder.PrepareApertureModel(aperturedict[name], defaultAperShape)
	else:
		this_aperdict = {'APER_1' : twiss.getAperture(index, defaultAperSize)}
		aper = _Builder.PrepareApertureModel(this_aperdict, defaultAperShape)

	gmadElement.update(aper)
	return gmadElement


def Mad82GmadBeam(data, startindex=0, verbose=False, extraParamsDict={}):
	"""
	Takes a pymad8 dataframe and extracts beam information from extraParamsDict
	to create a BDSIM beam definition in a pybdsim.Beam object.
	Note that if kwarg startname is used, the optics are retrieved at the
	start of the element, i.e. you do not need to get the optics of
	the previous element, this function does that automatically.

	Works for e+, e- and proton.

	"""

	# MADX defines parameters at the end of elements so need to go 1 element back if we can
	if startindex > 0:
		startindex -= 1

	energy = data['E'][startindex]
	if 'EX' not in extraParamsDict or 'EY' not in extraParamsDict:
		raise ValueError('Missing emittance description in extraParamsDict')
	if 'Esprd' not in extraParamsDict:
		raise ValueError('Missing energy spread in extraParamsDict')
	if 'particletype' not in extraParamsDict:
		raise ValueError('Missing particle type in extraParamsDict')

	ex =		extraParamsDict.pop('EX')
	ey =		extraParamsDict.pop('EY')
	sigmae =	extraParamsDict.pop('Esprd')
	particle =	extraParamsDict.pop('particletype')

	if particle != 'e-' and particle != 'e+' and particle != 'proton':
		raise ValueError("Unsupported particle : " + particle)
		
	# return _Beam.Beam('e-',16.5,'gausstwiss')
	beam = _Beam.Beam(particle, energy, 'gausstwiss')
	if ex != 0:
		beam._SetEmittanceX(ex, 'm')
	if ey != 0:
		beam._SetEmittanceY(ey, 'm')
	beam._SetSigmaE(sigmae)

	beamparams = {"SetBetaX": 'BETX', "SetBetaY": 'BETY', "SetAlphaX": 'ALPHX', "SetAlphaY": 'ALPHY',
				  "SetDispX":'DX', "SetDispY": 'DY', "SetDispXP": 'DPX', "SetDispYP": 'DPY',
				  "SetXP0": 'PX', "SetYP0": 'PY', "SetX0": 'X', "SetY0": 'Y'}

	for func, parameter in beamparams.items():
		if parameter in list(data.keys()):
			getattr(beam, func)(data[parameter][startindex])

	for k, v in extraParamsDict.items():
		beam[k] = v

	return beam
