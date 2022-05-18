from copy import deepcopy as _deepcopy
import numpy as _np
import math as _math
import pymad8 as _m8
import warnings as _warnings
from .. import Builder as _Builder
from .. import Beam as _Beam
from ..Options import Options as _Options
import pybdsim._General

# Constants
# anything below this length is treated as a thin element
_THIN_ELEMENT_THRESHOLD = 1e-6


def Mad82Gmad(inputfilename,outputfilename,
		startindex            = 0,
		endindex              = -1,
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
		usemadxaperture       = False,
		defaultAperture       = 'circular',
		biases                = None,
		allelementdict        = {},
		optionsdict           = {},
		beamparamsdict        = {},
		linear                = False,
		overwrite             = True,
		write                 = True,
		namePrepend           = ""):

	if type(inputfilename) == str:
		twiss = _m8.OutputPandas(inputfilename)
		if twiss.filetype != 'twiss':
			raise ValueError('Expect a twiss file to convert')
		data = twiss.data
	elif type(inputfilename) == dict:
		twiss = inputfilename['twiss']
		rmat = inputfilename['rmat']
		if twiss.filetype != 'twiss' or rmat.filetype != 'rmat':
			raise ValueError('Expect a twiss file and a rmat file to convert')
		data = twiss.data.merge(rmat.data)
	else :
		raise TypeError('Expect either a twiss file string or a dictionary with twiss and rmat file strings')

	machine = _Builder.Machine()
	for item in data.iloc[startindex:endindex].iloc :
		name = item['NAME']
		t = item['TYPE']
		l = item['L']
		
		zerolength = True if l < 1e-9 else False
		gmadElement = _Mad82GmadElementFactory(item, allelementdict, verbose,
							userdict, collimatordict, partnamedict, flipmagnets,
							linear, zerolength, ignorezerolengthitems,namePrepend="")
		if gmadElement is None: # factory returned nothing, go to next item.
			continue
		elif gmadElement.length == 0.0 and isinstance(gmadElement,_Builder.Drift): # skip drifts of length 0
			continue
		elif l == 0 or name in collimatordict: # Don't add apertures to thin elements or collimators
			machine.Append(gmadElement)
		elif aperlocalpositions: # split aperture if provided
			elements_split_with_aper = _GetElementSplitByAperture(gmadElement,aperlocalpositions[i])
			for ele in elements_split_with_aper:
				machine.Append(ele)
		else: # Get element with single aperture
			element_with_aper = _GetSingleElementWithAper(item,gmadElement,aperturedict,defaultAperture)
			machine.Append(element_with_aper)

	if (samplers is not None): # Add Samplers
		machine.AddSampler(samplers)

	if beam: # Add Beam
		bm = Mad82GmadBeam(data, startindex, verbose, extraParamsDict=beamparamsdict)
		machine.AddBeam(bm)

	options = _Options() # Add Options
	if optionsdict:
		options.update(optionsdict)  # expand with user supplied bdsim options
	machine.AddOptions(options)

	machine.Write(outputfilename)

def _Mad82GmadElementFactory(item, allelementdict, verbose,
				userdict, collimatordict, partnamedict, flipmagnets,
				linear, zerolength, ignorezerolengthitems, namePrepend):
	if isinstance(item, _Builder.Element):
		return item

	factor = 1
	if flipmagnets is not None:
		factor = -1 if flipmagnets else 1  # flipping magnets

	kws = {} # ensure empty
	kws = _deepcopy(allelementdict) # deep copy as otherwise allelementdict gets irreparably changed!
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
	if name in userdict: # name appears in the madx.  try this first.
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
		return _Builder.Drift(rname,l,**kws)
	#######################################################################
	elif Type == 'MARK':
		if not ignorezerolengthitems:
			return _Builder.Marker(rname)
	#######################################################################
	elif Type == 'SOLE':
		if l == 0.0 :
			return None # thin solenoid is omitted
		return _Builder.Solenoid(rname,l,ks=item['KS']/l,**kws)
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
		if zerolength or l < _THIN_ELEMENT_THRESHOLD:
			k1 = item['K1'] * factor
			return _Builder.ThinMultipole(rname, knl=(k1,), **kws)
		k1 = item['K1'] / l * factor
		return _Builder.Quadrupole(rname, l, k1, **kws)
	#######################################################################
	elif Type == 'SEXT':
		if zerolength or l < _THIN_ELEMENT_THRESHOLD:
			k2 = item['K2'] * factor if not linear else 0
			return _Builder.ThinMultipole(rname, knl=(0, k2), **kws)
		k2 = item['K2'] / l * factor if not linear else 0
		return _Builder.Sextupole(rname, l, k2, **kws)
	#######################################################################
	elif Type == 'OCTU':
		if zerolength or l < _THIN_ELEMENT_THRESHOLD:
			k3 = item['K3'] * factor if not linear else 0
			return _Builder.ThinMultipole(rname, knl=(0, 0, k3), **kws)
		k3 = item['K3'] / l * factor if not linear else 0
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
			return _Builder.ThinMultipole(rname, knl=(k1,k2,k3), ksl=ks, **kws)
		else:
			return _Builder.Multipole(rname, l, knl=(k1,k2,k3), ksl=ks, **kws)
	#######################################################################
	elif Type == 'HKIC':
		if verbose:
			print('HKICKER', rname)
		if not zerolength:
			if l > _THIN_ELEMENT_THRESHOLD:
				kws['l'] = l
		return _Builder.HKicker(name,hkick=item['HKIC']*factor,**kws)
	#######################################################################
	elif Type == 'VKIC':
		if verbose:
			print('VKICKER', rname)
		if not zerolength:
			if l > _THIN_ELEMENT_THRESHOLD:
				kws['l'] = l
		return _Builder.VKicker(name,vkick=item['VKIC']*factor,**kws)
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
			k1 = k1 / l
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

		if angle != 0: #protect against 0 angle rbends
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
			k1 = k1 / l
			kws['k1'] = k1
		return _Builder.RBend(rname, chordLength, angle=angle, **kws)
	#######################################################################
	elif Type == 'LCAV':
		volt = item['VOLT']
		freq = item['FREQ']
		lag = item ['LAG']
		gradient = volt/l
		phase = lag * 2 * _np.pi

		if freq != 0:
			kws['freq'] = freq
		if phase != 0:
			kws['phase'] = phase
		return _Builder.RFCavity(rname, l, gradient=gradient, **kws)
	#######################################################################
	elif Type in {'ECOL','RCOL'}:
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
				xsize = colld['XSIZE']
				ysize = colld['YSIZE']
				if verbose:
					print('collimator x,y size ', xsize, ysize)
				if 'outerDiameter' in colld:
					kws['outerDiameter'] = colld['outerDiameter']
				else:
					kws['outerDiameter'] = max([0.5,xsize * 2.5,ysize * 2.5])
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
				" necessarily wrong!".format(t, name))
			_warnings.warn(msg)
			return _Builder.Drift(rname, l, **kws)
		# if user didn't provide a collimatordict at all.
		else:
			return _Builder.Drift(rname, l, **kws)
	#######################################################################
	elif Type == 'MATR':
		if 'rmat' not in inputfilename :
			raise ValueError('No Rmat file to extract element')
		index = item.name
		item = rmat.data.iloc[index]
		previtem = rmat.data.iloc[index-1]
		POSTMATRIX = _np.matrix([[item['R11'],item['R12'],item['R13'],item['R14']],
					[item['R21'],item['R22'],item['R23'],item['R24']],
					[item['R31'],item['R32'],item['R33'],item['R34']],
					[item['R41'],item['R42'],item['R43'],item['R44']]])
		PRIORMATRIX = _np.matrix([[previtem['R11'],previtem['R12'],previtem['R13'],previtem['R14']],
					[previtem['R21'],previtem['R22'],previtem['R23'],previtem['R24']],
					[previtem['R31'],previtem['R32'],previtem['R33'],previtem['R34']],
					[previtem['R41'],previtem['R42'],previtem['R43'],previtem['R44']]])

		RMAT=(POSTMATRIX*PRIORMATRIX.I)
		return _Builder.Rmat(rname, l, r11=RMAT[0,0], r12=RMAT[0,1], r13=RMAT[0,2], r14=RMAT[0,3],
						r21=RMAT[1,0], r22=RMAT[1,1], r23=RMAT[1,2], r24=RMAT[1,3],
						r31=RMAT[2,0], r32=RMAT[2,1], r33=RMAT[2,2], r34=RMAT[2,3],
						r41=RMAT[3,0], r42=RMAT[3,1], r43=RMAT[3,2], r44=RMAT[3,3], **kws)
	#######################################################################
	else :
		print('unknown element type:', t, 'for element named: ', name)
		if zerolength and not ignorezerolengthitems:
			print('putting marker in instead as its zero length')
			return _Builder.Marker(rname)
		print('putting drift in instead as it has a finite length')
		return _Builder.Drift(rname, l)
	#######################################################################

def _GetSingleElementWithAper(item, gmadElement,aperturedict, defaultAperture):
	"""Returns the raw aperture model (i.e. unsplit), and a list of split apertures."""
	gmadElement = _deepcopy(gmadElement)
	name = item["NAME"]
	# note SORIGINAL not S.  This is so it works still after slicing.
	sMid = item["S"] - item["L"] / 2.0
	aper = {}
	try:
		aper = _Builder.PrepareApertureModel(aperturedict.GetApertureAtS(sMid), defaultAperture)
	except AttributeError:
		pass
	try:
		this_aperdict = aperturedict[name]
	except KeyError:
		pass
	else:
		aper = _Builder.PrepareApertureModel(this_aperdict, defaultAperture)

	gmadElement.update(aper)
	return gmadElement

def Mad82GmadBeam(data, startindex=0, verbose=False, extraParamsDict={}):
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

	ex = 		extraParamsDict.pop('EX')
	ey = 		extraParamsDict.pop('EY')
	sigmae = 	extraParamsDict.pop('Esprd')
	particle = 	extraParamsDict.pop('particletype')

	if particle != 'e-' and particle != 'e+' and particle != 'proton':
		raise ValueError("Unsupported particle : " + particle)
		
	# return _Beam.Beam('e-',16.5,'gausstwiss')
	beam =  _Beam.Beam(particle,energy,'gausstwiss')
	if ex != 0:
		beam.SetEmittanceX(ex, 'm')
	if ey != 0:
		beam.SetEmittanceY(ey, 'm')
	beam.SetSigmaE(sigmae)

	beamparams = {"SetBetaX":'BETX',"SetBetaY":'BETY',"SetAlphaX":'ALPHX',"SetAlphaY":'ALPHY',
			"SetDispX":'DX',"SetDispY":'DY',"SetDispXP":'DPX',"SetDispYP":'DPY',
			"SetXP0": 'PX',"SetYP0": 'PY',"SetX0": 'X',"SetY0": 'Y'}

	for func,parameter in beamparams.items():
		if parameter in list(data.keys()):
			getattr(beam, func)(data[parameter][startindex])

	for k, v in extraParamsDict.items():
		beam[k] = v

	return beam
