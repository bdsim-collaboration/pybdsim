import numpy as _np
import matplotlib.pyplot as _plt
import pandas as _pd
import fortranformat as _ff


class Output:
	"""
	| Class to load different Mad8 output files in a Pandas DataFrame
	| >>> twiss = pymad8.Output('/twiss.tape')
	| >>> rmat = pymad8.Output('/rmat.tape','rmat')
	| >>> chrom = pymad8.Output('/chrom.tape','chrom')
	| >>> envel = pymad8.Output('/envel.tape','envel')
	| >>> survey = pymad8.Output('/survey.tape','survey')
	| >>> struct = pymad8.Output('/struct.tape','struct')
	| >>> track = pymad8.Output('/track.tape','track')
	| >>> optics = pymad8.Output('/optics.tape','optics')
	|
	| By default the filetype is twiss
	"""

	def __init__(self, filename, filetype='twiss'):
		"""
		Take filename for argument, filetype if specified and save them as internal variables.
		Then test for filetype and call the corresponding subfunction
		"""
		self.filename = filename
		self.filetype = filetype

		self.keys_dict = {'    ': {},
        'DRIF'       :{'L':2,                                                                      'APER':11,'NOTE':12,'E':13},
        'RBEN'       :{'L':2,'ANGLE':3,'K1':4,'K2':5,'TILT' :6,'E1'    :7,'E2'  :8,'H1' :9,'H2':10,'APER':11,'NOTE':12,'E':13},
        'SBEN'       :{'L':2,'ANGLE':3,'K1':4,'K2':5,'TILT' :6,'E1'    :7,'E2'  :8,'H1' :9,'H2':10,'APER':11,'NOTE':12,'E':13},
        'QUAD'       :{'L':2,          'K1':4,       'TILT' :6,                                    'APER':11,'NOTE':12,'E':13},
        'SEXT'       :{'L':2,                 'K2':5,'TILT' :6,                                    'APER':11,'NOTE':12,'E':13},
        'OCTU'       :{'L':2,                        'TILT' :6,'K3'    :7,                         'APER':11,'NOTE':12,'E':13},
        'MULT'       :{      'K0'   :3,'K1':4,'K2':5,'T0'   :6,'K3'    :7,'T1'  :8,'T2' :9,'T3':10,'APER':11,'NOTE':12,'E':13},
        'SOLE'       :{'L':2,                                  'KS'    :7,                         'APER':11,'NOTE':12,'E':13},
        'RFCAVITY'   :{'L':2,                                  'FREQ'  :7,'VOLT':8,'LAG':9,        'APER':11,'NOTE':12,'E':13},
        'ELSEPARATOR':{'L':2,                        'TILT' :6,'EFIELD':7,                         'APER':11,'NOTE':12,'E':13},
        'KICK'       :{'L':2,                        'HKIC' :6,'VKIC'  :7,                         'APER':11,'NOTE':12,'E':13},
        'HKIC'       :{'L':2,                        'HKIC' :6,                                    'APER':11,'NOTE':12,'E':13},
        'VKIC'       :{'L':2,                                  'VKIC'  :7,                         'APER':11,'NOTE':12,'E':13},
        'SROT'       :{'L':2,                                  'ANGLE' :7,                         'APER':11,'NOTE':12,'E':13},
        'YROT'       :{'L':2,                                  'ANGLE' :7,                         'APER':11,'NOTE':12,'E':13},
        'MONI'       :{'L':2,                                                                      'APER':11,'NOTE':12,'E':13},
        'HMONITOR'   :{'L':2,                                                                      'APER':11,'NOTE':12,'E':13},
        'VMONITOR'   :{'L':2,                                                                      'APER':11,'NOTE':12,'E':13},
        'MARK'       :{'L':2,                                                                      'APER':11,'NOTE':12,'E':13},
        'ECOL'       :{'L':2,                        'XSIZE':6,'YSIZE' :7,                         'APER':11,'NOTE':12,'E':13},
        'RCOL'       :{'L':2,                        'XSIZE':6,'YSIZE' :7,                         'APER':11,'NOTE':12,'E':13},
        'INST'       :{'L':2,                                                                                'NOTE':12,'E':13},
        'WIRE'       :{'L':2,                                                                                'NOTE':12,'E':13},
        'IMON'       :{'L':2,                                                                                'NOTE':12,'E':13},
        'PROF'       :{'L':2,                                                                                'NOTE':12,'E':13},
        'BLMO'       :{'L':2,                                                                                'NOTE':12,'E':13},
        'LCAV'       :{'L':2,                                  'FREQ'  :7,'VOLT':8,'LAG':9,        'APER':11,'NOTE':12,'E':13},
        'MATR'       :{'L':2,                                                                      'APER':11,          'E':13}}

		self.colnames_common = ['TYPE', 'NAME', 'L', 'ANGLE', 'K0', 'K1', 'K2', 'K3', 'KS', 'T0', 'T1', 'T2', 'T3',
								'TILT', 'E1', 'E2', 'H1', 'H2', 'APER', 'NOTE', 'E', 'FREQ', 'VOLT', 'LAG', 'EFIELD',
								'HKIC', 'VKIC', 'XSIZE', 'YSIZE']

		if filetype == 'twiss':
			self._readTwissFile()
		if filetype == 'rmat':
			self._readRmatFile()
		if filetype == 'chrom':
			self._readChromFile()
		if filetype == 'envel':
			self._readEnvelopeFile()
		if filetype == 'survey':
			self._readSurveyFile()
		if filetype == 'struct':
			self._readStructureFile()
		if filetype == 'track':
			self._readTrackFile()
		if filetype == 'optics':
			self._readOpticsFile()
		if filetype == 'df':
			self._readDFFile()

	##########################################################################################
	def _readTwissFile(self):
		"""Read and load a Mad8 twiss file in a DataFrame then save it as internal value 'data' """

		colnames_twiss = ['ALPHX', 'BETX', 'MUX', 'DX', 'DPX',
						  'ALPHY', 'BETY', 'MUY', 'DY', 'DPY',
						  'X', 'PX', 'Y', 'PY', 'S']
		colnames = self.colnames_common + colnames_twiss
		self.data = _pd.DataFrame(columns=colnames)

		f = open(self.filename, 'r')

		self.nrec = self._findNelemInFF(f)
		print('Mad8.readTwissFile > nrec='+str(self.nrec))

		ffe1 = _ff.FortranRecordReader('(A4,A16,F12.6,4E16.9,A19,E16.9)')
		ffe2 = _ff.FortranRecordReader('(5E16.9)')

		# loop over entries
		dList = []
		for i in range(0, self.nrec, 1):
			l1 = ffe1.read(f.readline())
			l2 = ffe2.read(f.readline())
			l3 = ffe2.read(f.readline())
			l4 = ffe2.read(f.readline())
			l5 = ffe2.read(f.readline())
			l_common = l1[0:6]+l2+l1[6:9]
			l_twiss = l3+l4+l5
			d = {'TYPE': l_common[0], 'NAME': l_common[1].strip()}
			kt = self.keys_dict[d['TYPE']]
			for k in kt.keys():
				d[k] = l_common[kt[k]]
			for j in range(len(colnames_twiss)):
				d[colnames_twiss[j]] = l_twiss[j]
			dList.append(d)
		f.close()
		self.data = _pd.DataFrame(dList, columns=colnames)
		self.data.at[0, 'E'] = self.data['E'][1]

	##########################################################################################
	def _readRmatFile(self):
		"""Read and load a Mad8 rmat file in a DataFrame then save it as internal value 'data' """

		colnames_rmat = ['R11', 'R12', 'R13', 'R14', 'R15', 'R16',
						 'R21', 'R22', 'R23', 'R24', 'R25', 'R26',
						 'R31', 'R32', 'R33', 'R34', 'R35', 'R36',
						 'R41', 'R42', 'R43', 'R44', 'R45', 'R46',
						 'R51', 'R52', 'R53', 'R54', 'R55', 'R56',
						 'R61', 'R62', 'R63', 'R64', 'R65', 'R66', 'S']
		colnames = self.colnames_common + colnames_rmat
		self.data = _pd.DataFrame(columns=colnames)

		f = open(self.filename, 'r')

		self.nrec = self._findNelemInFF(f)
		print('Mad8.readRmatFile > nrec='+str(self.nrec))

		ffe1 = _ff.FortranRecordReader('(A4,A16,F12.6,4E16.9,A19,E16.9)')
		ffe2 = _ff.FortranRecordReader('(5E16.9)')
		ffe3 = _ff.FortranRecordReader('(6E16.9)')
		ffe4 = _ff.FortranRecordReader('(7E16.9)')

		# loop over entries
		dList = []
		for i in range(0, self.nrec, 1):
			l1 = ffe1.read(f.readline())
			l2 = ffe2.read(f.readline())
			l3 = ffe3.read(f.readline())
			l4 = ffe3.read(f.readline())
			l5 = ffe3.read(f.readline())
			l6 = ffe3.read(f.readline())
			l7 = ffe3.read(f.readline())
			l8 = ffe4.read(f.readline())
			l_common = l1[0:6]+l2+l1[6:9]
			l_rmat = l3+l4+l5+l6+l7+l8

			d = {'TYPE': l_common[0], 'NAME': l_common[1].strip()}
			kt = self.keys_dict[d['TYPE']]
			for k in kt.keys():
				d[k] = l_common[kt[k]]
			for j in range(len(colnames_rmat)):
				d[colnames_rmat[j]] = l_rmat[j]
			dList.append(d)
		f.close()
		self.data = _pd.DataFrame(dList, columns=colnames)
		self.data.at[0, 'E'] = self.data['E'][1]

	##########################################################################################
	def _readChromFile(self):
		"""Read and load a Mad8 chrom file in a DataFrame then save it as internal value 'data' """

		colnames_chrom = ['WX', 'PHIX', 'DMUX', 'DDX', 'DDPX',
						  'WY', 'PHIY', 'DMUY', 'DDY', 'DDPY',
						  'X', 'PX', 'Y', 'PY', 'S']
		colnames = self.colnames_common + colnames_chrom
		self.data = _pd.DataFrame(columns=colnames)

		f = open(self.filename, 'r')

		self.nrec = self._findNelemInFF(f)
		print('Mad8.readChromFile > nrec='+str(self.nrec))

		ffe1 = _ff.FortranRecordReader('(A4,A16,F12.6,4E16.9,A19,E16.9)')
		ffe2 = _ff.FortranRecordReader('(5E16.9)')
		ffe3 = _ff.FortranRecordReader('(5E16.9)')

		# loop over entries
		dList = []
		for i in range(0, self.nrec, 1):
			l1 = ffe1.read(f.readline())
			l2 = ffe2.read(f.readline())
			l3 = ffe3.read(f.readline())
			l4 = ffe3.read(f.readline())
			l5 = ffe3.read(f.readline())
			l_common = l1[0:6]+l2+l1[6:9]
			l_chrom = l3+l4+l5

			d = {'TYPE': l_common[0], 'NAME': l_common[1].strip()}
			kt = self.keys_dict[d['TYPE']]
			for k in kt.keys():
				d[k] = l_common[kt[k]]
			for j in range(len(colnames_chrom)):
				d[colnames_chrom[j]] = l_chrom[j]
			dList.append(d)
		f.close()
		self.data = _pd.DataFrame(dList, columns=colnames)
		self.data.at[0, 'E'] = self.data['E'][1]

	##########################################################################################
	def _readEnvelopeFile(self):
		"""Read and load a Mad8 envelope file in a DataFrame then save it as internal value 'data' """

		colnames_envelop = ['S11', 'S12', 'S13', 'S14', 'S15', 'S16',
							'S21', 'S22', 'S23', 'S24', 'S25', 'S26',
				    		'S31', 'S32', 'S33', 'S34', 'S35', 'S36',
							'S41', 'S42', 'S43', 'S44', 'S45', 'S46',
				    		'S51', 'S52', 'S53', 'S54', 'S55', 'S56',
							'S61', 'S62', 'S63', 'S64', 'S65', 'S66', 'S']
		colnames = self.colnames_common + colnames_envelop
		self.data = _pd.DataFrame(columns=colnames)

		f = open(self.filename, 'r')

		self.nrec = self._findNelemInFF(f)
		print('Mad8.readEnvelopeFile > nrec='+str(self.nrec))

		ffe1 = _ff.FortranRecordReader('(A4,A16,F12.6,4E16.9,A19,E16.9)')
		ffe2 = _ff.FortranRecordReader('(5E16.9)')
		ffe3 = _ff.FortranRecordReader('(6E16.9)')
		ffe4 = _ff.FortranRecordReader('(7E16.9)')

		# loop over entries
		dList = []
		for i in range(0, self.nrec, 1):
			l1 = ffe1.read(f.readline())
			l2 = ffe2.read(f.readline())
			l3 = ffe3.read(f.readline())
			l4 = ffe3.read(f.readline())
			l5 = ffe3.read(f.readline())
			l6 = ffe3.read(f.readline())
			l7 = ffe3.read(f.readline())
			l8 = ffe4.read(f.readline())
			l_common = l1[0:6]+l2+l1[6:9]
			l_envelop = l3+l4+l5+l6+l7+l8

			d = {'TYPE': l_common[0], 'NAME': l_common[1].strip()}
			kt = self.keys_dict[d['TYPE']]
			for k in kt.keys():
				d[k] = l_common[kt[k]]
			for j in range(len(colnames_envelop)):
				d[colnames_envelop[j]] = l_envelop[j]
			dList.append(d)
		f.close()
		self.data = _pd.DataFrame(dList, columns=colnames)
		self.data.at[0, 'E'] = self.data['E'][1]

	##########################################################################################
	def _readSurveyFile(self):
		"""Read and load a Mad8 survey file in a DataFrame then save it as internal value 'data' """

		colnames_survey = ['X', 'Y', 'Z', 'S',
						   'THETA', 'PHI', 'PSI']
		colnames = self.colnames_common + colnames_survey
		self.data = _pd.DataFrame(columns=colnames)

		f = open(self.filename, 'r')

		self.nrec = self._findNelemInFF(f)
		print('Mad8.readSurveyFile> nrec='+str(self.nrec))

		ffe1 = _ff.FortranRecordReader('(A4,A16,F12.6,4E16.9,A19,E16.9)')
		ffe2 = _ff.FortranRecordReader('(5E16.9)')
		ffe3 = _ff.FortranRecordReader('(4E16.9)')
		ffe4 = _ff.FortranRecordReader('(3E16.9)')

		# loop over entries
		dList = []
		for i in range(0, self.nrec, 1):
			l1 = ffe1.read(f.readline())
			l2 = ffe2.read(f.readline())
			l3 = ffe3.read(f.readline())
			l4 = ffe4.read(f.readline())
			l_common = l1[0:6]+l2+l1[6:9]
			l_survey = l3+l4

			d = {'TYPE': l_common[0], 'NAME': l_common[1].strip()}
			kt = self.keys_dict[d['TYPE']]
			for k in kt.keys():
				d[k] = l_common[kt[k]]
			for j in range(len(colnames_survey)):
				d[colnames_survey[j]] = l_survey[j]
			dList.append(d)
		f.close()
		self.data = _pd.DataFrame(dList, columns=colnames)
		self.data.at[0, 'E'] = self.data['E'][1]

	##########################################################################################
	def _readStructureFile(self):
		"""Read and load a Mad8 structure file in a DataFrame then save it as internal value 'data' """

		colnames_survey = ['X', 'Y', 'Z', 'S',
						   'THETA', 'PHI', 'PSI']
		colnames = self.colnames_common + colnames_survey
		self.data = _pd.DataFrame(columns=colnames)

		f = open(self.filename, 'r')

		self.nrec = self._findNelemInFF(f)
		print('Mad8.readSurveyFile> nrec=' + str(self.nrec))

		ffe1 = _ff.FortranRecordReader('(A4,A16,F12.6,4E16.9,A19,E16.9)')
		ffe2 = _ff.FortranRecordReader('(5E16.9)')
		ffe3 = _ff.FortranRecordReader('(4E16.9)')
		ffe4 = _ff.FortranRecordReader('(3E16.9)')

		# loop over entries
		dList = []
		for i in range(0, self.nrec, 1):
			l1 = ffe1.read(f.readline())
			l2 = ffe2.read(f.readline())
			l3 = ffe3.read(f.readline())
			l4 = ffe4.read(f.readline())
			l_common = l1[0:6] + l2 + l1[6:9]
			l_survey = l3 + l4

			d = {'TYPE': l_common[0], 'NAME': l_common[1].strip()}
			kt = self.keys_dict[d['TYPE']]
			for k in kt.keys():
				d[k] = l_common[kt[k]]
			for j in range(len(colnames_survey)):
				d[colnames_survey[j]] = l_survey[j]
			dList.append(d)
		f.close()
		self.data = _pd.DataFrame(dList, columns=colnames)
		self.data.at[0, 'E'] = self.data['E'][1]

	##########################################################################################
	def _readTrackFile(self):
		"""Read and load a Mad8 track file in a DataFrame then save it as internal value 'data' """

		f = open(self.filename, 'r')

		colnames, ffe1 = self._readColumns(f)
		self.header, line = self._readHeader(f)
		ffhr2 = _ff.FortranRecordReader('(A8,3I8)')
		self.nrec = ffhr2.read(line)[-1]
		print('Mad8.readTrackFile> nrec=' + str(self.nrec))

		# loop over entries
		dList = []
		for i in range(0, self.nrec, 1):
			ff_line = ffe1.read(f.readline())
			d = {}
			for j in range(len(colnames)):
				d[colnames[j]] = ff_line[j+1]
			dList.append(d)
		f.close()
		self.data = _pd.DataFrame(dList, columns=colnames)

	##########################################################################################
	def _readOpticsFile(self):
		"""Read and load a Mad8 optics file in a DataFrame then save it as internal value 'data' """

		f = open(self.filename, 'r')

		colnames, ffe1 = self._readColumns(f)
		self.header, line = self._readHeader(f)

		dList = []
		nrec = 0
		# loop over entries
		while line:
			ff_line = ffe1.read(line)
			d = {}
			for j in range(len(colnames)):
				if type(ff_line[j+1]) == str:
					d[colnames[j]] = ff_line[j+1].split()[0].replace('"', '')
				else:
					d[colnames[j]] = ff_line[j+1]
			dList.append(d)

			nrec += 1
			line = f.readline()
		f.close()
		self.nrec = nrec
		self.data = _pd.DataFrame(dList, columns=colnames)
		print('Mad8.readOpticFile> nrec=' + str(self.nrec))

	##########################################################################################
	def _readDFFile(self):
		"""Load DataFrame as Mad8 output file then save it as internal value 'data' """

		df = self.filename
		self.nrec = len(df)
		self.data = df
		print('Mad8.readDFFile> nrec=' + str(self.nrec))

	##########################################################################################
	def _findNelemInFF(self, openfile):
		"""Read the beginig of an opened fortran file and return the number of elements"""

		# Standard header definition
		ffhr1 = _ff.FortranRecordReader('(5A8,I8,L8,I8)')
		ffhr2 = _ff.FortranRecordReader('(A80)')
		# read header
		h1 = ffhr1.read(openfile.readline())
		h2 = ffhr2.read(openfile.readline())
		# number of records
		nrec = h1[7]

		if self.filetype == 'chrom':
			# skip the twiss part at the begining
			for i in range(nrec*5+5):
				openfile.readline()

		return nrec

	def _readHeader(self, openfile):
		header = {}
		ffhr3 = _ff.FortranRecordReader('(A2,A17,A5,A20)')
		ffhr4 = _ff.FortranRecordReader('(A2,A17,A5,E16.9)')
		line = openfile.readline()
		while line[0] == '@':
			if line.split()[2] in ['%08s', '%16s']:
				h3 = ffhr3.read(line)
				header[h3[1].strip()] = h3[3].split()[0].replace('"', '')
			elif line.split()[2] in ['%e', '%le']:
				h4 = ffhr4.read(line)
				header[h4[1].strip()] = h4[3]
			line = openfile.readline()
		return header, line

	def _readColumns(self, openfile):
		colnames = openfile.readline().replace('*', '').split()
		colformat = openfile.readline().replace('$', '').split()
		ff_reader_str = '(A1,'
		for form in colformat:
			if form == '%16s':
				ff_reader_str += 'A20,'
			elif form == '%e':
				ff_reader_str += 'E15.9,'
			elif form == '%hd':
				ff_reader_str += 'I9,'
		ff_reader_str += ')'
		ffer = _ff.FortranRecordReader(ff_reader_str)
		return colnames, ffer

	def Clear(self):
		"""Empties all data structures in this instance"""
		self.__init__()

	####################################################################################
	def getIndexByNames(self, namelist):
		"""Return Index or Index list of elements that are in namelist"""
		return _getValues(self.getRowsByValues(key='NAME', equalValues=namelist).index)

	def getIndexByTypes(self, typelist):
		"""Return Index or Index list of elements that are in typelist"""
		return _getValues(self.getRowsByValues(key='TYPE', equalValues=typelist).index)

	def getIndexByValues(self, **args):
		"""
		| Return Index or Index list of elements that have certain values for a chosen column
		| *Same arguments as getRowsByValues*
		"""
		return _getValues(self.getRowsByValues(**args).index)

	def getIndexByNearestS(self, s):
		"""Return Index of the closest element in the beamline"""
		return _getValues(self.getRowByNearestS(s).index)

	####################################################################################
	def getNamesByIndex(self, indexlist):
		"""Return Name or Name list of elements that are in indexlist"""
		return _getValues(self.getRowsByValues(key=None, equalValues=indexlist)['NAME'])

	def getNamesByTypes(self, typelist):
		"""Return Name or Name list of elements that are in typelist"""
		return _getValues(self.getRowsByValues(key='TYPE', equalValues=typelist)['NAME'])

	def getNamesByValues(self, **args):
		"""
		| Return Name or Name list of elements that have certain values for a chosen column
		| *Same arguments as getRowsByValues*
		"""
		return _getValues(self.getRowsByValues(**args)['NAME'])

	def getNameByNearestS(self, s):
		"""Return Name of the closest element in the beamline"""
		return _getValues(self.getRowByNearestS(s)['NAME'])

	####################################################################################
	def getTypesByIndex(self, indexlist):
		"""Return Type or Type list of elements that are in indexlist"""
		return _getValues(self.getRowsByValues(key=None, equalValues=indexlist)['TYPE'])

	def getTypesByNames(self, namelist):
		"""Return Type or Type list of elements that are in namelist"""
		return _getValues(self.getRowsByValues(key='NAME', equalValues=namelist)['TYPE'])

	def getTypesByValues(self, **args):
		"""
		| Return Type or Type list of elements that have certain values for a chosen column
		| *Same arguments as getRowsByValues*
		"""
		return _getValues(self.getRowsByValues(**args)['TYPE'])

	def getTypeByNearestS(self, s):
		"""Return Type of the closest element in the beamline"""
		return _getValues(self.getRowByNearestS(s)['TYPE'])

	####################################################################################
	def getRowsByIndex(self, indexlist):
		"""Return Rows of elements that are in indexlist"""
		return self.getRowsByValues(equalValues=indexlist)

	def getRowsByNames(self, namelist):
		"""Return Rows of elements that are in namelist"""
		return self.getRowsByValues(key='NAME', equalValues=namelist)

	def getRowsByTypes(self, typelist):
		"""Return Rows of elements that are in typelist"""
		return self.getRowsByValues(key='TYPE', equalValues=typelist)

	def getRowsByValues(self, key=None, minValue=-_np.inf, maxValue=_np.inf, equalValues=None):
		"""Return Rows of elements that have certain values for a chosen column"""
		if key is None:
			if equalValues is not None:
				return self.data.loc[equalValues]
			return self.data.loc[minValue:maxValue]

		column = self.data[key]
		if equalValues is not None:
			if type(equalValues) == list:
				return self.data.loc[column.isin(equalValues)]
			return self.data.loc[column == equalValues]
		return self.data.loc[column >= minValue].loc[column <= maxValue]

	def getRowByNearestS(self, s):
		"""Return Rows of the closest element in the beamline"""
		S = self.data['S'].tolist()
		if s <= S[0]:
			return self.data.iloc[[0]]
		if s >= S[-1]:
			return self.data.iloc[[-1]]
		for index in range(self.nrec - 1):
			if S[index] <= s < S[index + 1]:
				if s - S[index] < S[index + 1] - s:
					return self.data.iloc[[index]]
				else:
					return self.data.iloc[[index + 1]]
		raise ValueError('Closest s value not found')

	def getRowsByFunction(self, f):
		"""Return a sub-datafarme using a boolean function"""
		return self.data.loc[f(self.data)]

	####################################################################################
	def getColumnsByKeys(self, keylist):
		"""Return Columns that ar in keylist"""
		return self.data[keylist]

	####################################################################################
	def getElementByIndex(self, indexlist, keylist):
		"""Return value of elements given their indices and for chosen columns"""
		if type(indexlist) != list:
			indexlist = [indexlist]
		if type(keylist) != list:
			keylist = [keylist]
		elem = self.data.loc[indexlist, keylist]
		if elem.shape == (1, 1):
			return elem.values[0][0]
		return elem

	def getElementByNames(self, namelist, keylist):
		"""Return value of elements given their names and for chosen columns"""
		if type(namelist) != list:
			namelist = [namelist]
		if type(keylist) != list:
			keylist = [keylist]
		elem = self.data.loc[self.data['NAME'].isin(namelist), keylist]
		if elem.shape == (1, 1):
			return elem.values[0][0]
		return elem

	def getElementByNearestS(self, s, keylist):
		"""Return value of elements at a given s position and for chosen columns"""
		if type(keylist) != list:
			keylist = [keylist]
		row = self.getRowByNearestS(s)
		elem = row[keylist]
		if elem.shape == (1, 1):
			return elem.values[0][0]
		return elem

	####################################################################################
	def getAperture(self, index, defaultAperSize=0.1):
		"""
		| Get aperture of an element using corresponding index
		| If none provided or is 0 : set to a default aperture of 0.1m
		"""
		name = self.getNamesByIndex(index)
		aperture = self.data['APER'][index]
		if aperture == 0 or aperture == _np.nan:
			aperture = defaultAperSize
		return aperture

	def subline(self, start, end):
		"""Select only a portion of the inital lattice"""
		if type(start) == str:
			start = self.getIndexByNames(start)
		if type(end) == str:
			end = self.getIndexByNames(end)

		self.data = self.data[start:end]

	def sMin(self):
		"""Return minimal S value"""
		return self.data['S'].min()

	def sMax(self):
		"""Return maximal S value"""
		return self.data['S'].max()

	def plotXY(self, Xkey, Ykey, color=None, label=None):
		"""Quick plot of one colums of our dataframe w.r.t. another"""
		X = self.getColumnsByKeys(Xkey)
		Y = self.getColumnsByKeys(Ykey)
		if label is None:
			label = Ykey
		_plt.plot(X, Y, color=color, label=label)

	def calcBeamSize(self, EmitX, EmitY, Esprd, BunchLen=0):
		"""
		Calculate the beam sizes and beam divergences in both planes for all
		elements Then the four columns are added at the end of the DataFrame
		Works only if a twiss file was loaded previously
		"""
		if self.filetype != 'twiss':
			raise ValueError('The loaded file needs to be a twiss file')

		SigmaX = []
		SigmaY = []
		SigmaXP = []
		SigmaYP = []
		E0 = self.data['E'][1]
		for i in range(0, self.nrec, 1):
			BetaX = self.data['BETX'][i]
			BetaY = self.data['BETY'][i]
			GammaX = (1+self.data['ALPHX'][i]**2)/BetaX
			GammaY = (1+self.data['ALPHY'][i]**2)/BetaY
			DispX = self.data['DX'][i]
			DispY = self.data['DY'][i]
			DispXP = self.data['DPX'][i]
			DispYP = self.data['DPY'][i]

			# Beam size calculation
			SigmaX.append(_np.sqrt(BetaX*EmitX+(DispX*Esprd/E0)**2))
			SigmaY.append(_np.sqrt(BetaY*EmitY+(DispY*Esprd/E0)**2))
			# Beam divergence calculation
			SigmaXP.append(_np.sqrt(GammaX*EmitX+(DispXP*Esprd/E0)**2))
			SigmaYP.append(_np.sqrt(GammaY*EmitY+(DispYP*Esprd/E0)**2))

		self.data = self.data.assign(SIGX=SigmaX)
		self.data = self.data.assign(SIGY=SigmaY)
		self.data = self.data.assign(SIGXP=SigmaXP)
		self.data = self.data.assign(SIGYP=SigmaYP)


def _getValues(data):
	"""
	| Convert pandas elements of length 1 to regular value types
	| If given pandas element of length < 1 : returns a list
	| Otherwise if element is already a string or integer : return unchanged element
	"""
	if type(data) == str or type(data) == int:
		return data
	values_list = data.tolist()
	if len(values_list) == 1 and type(values_list) == list:
		return values_list[0]
	return values_list
