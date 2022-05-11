import numpy as _np
import pymad8 as _m8
from .. import Builder as _Builder

# Constants
# anything below this length is treated as a thin element
_THIN_ELEMENT_THRESHOLD = 1e-6


def Mad82Gmad(inputfilename,outputfilename
		startname             = None,
		stopname              = None,
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
		usemadxaperture       = False,
		defaultAperture       = 'circular',
		biases                = None,
		allelementdict        = {},
		optionsdict           = {},
		beamparamsdict        = {},
		linear                = False,
		overwrite             = True,
		write                 = True,
		allNamesUnique        = False,
		namePrepend           = ""):

	twiss = _m8.OutputPandas(inputfilename)
	if twiss.filetype != 'twiss':
		return

	machine = _Builder.Machine()
	for item in twiss.data.iloc[startindex:endindex].iloc :
		gmadElement = _Mad82GmadElementFactory(item, allelementdict, verbose,
							userdict, collimatordict, partnamedict, flipmagnets,
							linear, zerolength, ignorezerolengthitems,
							allNamesUnique, namePrepend="")
		machine.Append(gmadElement)

	machine.Write(outputfilename)

def _Mad82GmadElementFactory(item):
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

	if tilt != 0:
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
		return _Builder.Drift(rname, l, **kws)
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
		pass
	#######################################################################
	else :
	#######################################################################
