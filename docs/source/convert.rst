=================
Converting Models
=================

pybdsim provdies converters to allow BDSIM models to prepared from optical
descriptions of accelerators in other formats such as MADX and MAD8.

The following converters are provided and described here:


* MADX to BDSIM
  
  * `MadxTfs2Gmad`_
  * `MadxTfs2GmadStrength`_

* MAD8 to BDSIM
  
  * :ref:`mad8-twiss-2-gmad`

* Transport to BDSIM
  
  * `pytransport`_

* BDSIM Primary Particle Conversion
  
  * `BDSIM Primaries To Others`_


MadxTfs2Gmad
------------

A MADX lattice can be easily converted to a BDSIM gmad input file using the supplied
python utilities. This is achieved by

1. preparing a tfs file with madx containing all twiss table information
2. converting the tfs file to gmad using pybdsim

Preparing a Tfs File
********************

The twiss file can be prepared by appending the following MADX syntax to the
end of your MADX script::

  select,flag=twiss, clear; 
  twiss,sequence=SEQUENCENAME, file=twiss.tfs;

where `SEQUENCENAME` is the name of the sequence in madx. By not specifying the output
columns, a very large file is produced containing all possible columns.  This is required
to successfully convert the lattice.  If the tfs file contains insufficient information,
pybdsim will not be able to convert the model.

.. note:: The python utilities require "`.tfs`" suffix as the file type to work properly.

Converting the Tfs File
***********************

Once prepared, the Tfs file can be converted. The converter is used as follows::

  >>> pybdsim.Convert.MadxTfs2Gmad('inputfile.tfs', 'latticev1')

The conversion returns three objects, which are the :code:`pybdsim.Builder.Machine`
instance as converted, a second `Machine` that isn't split by aperture and a list
of any ommitted items by name. ::

  >>> a,b,c = pybdsim.Convert.MadxTfs2Gmad('inputfile.tfs', 'latticev1')

where `latticev1` is the output name of the converted model. The converter has the
ability to split items in the original TFS file if an aperture is specified somewhere
inside that element - use for disjoint aperture definitions. If a directory is used
in the output name, this will be created automatically, for example::

  >>> a,o = pybdsim.Convert.MadxTfs2Gmad('inputfile.tfs', 'test/latticev1')

will create a directory `test` if it doesn't exist already.

There are a few options that provide useful functionality for conversion:

.. tabularcolumns:: |p{5cm}|p{10cm}|

+-------------------------------+-------------------------------------------------------------------+
| **tfs**                       | path to the input tfs file or pymadx.Data.Tfs instance            |
+-------------------------------+-------------------------------------------------------------------+
| **outputfilename**            | requested output file                                             |
+-------------------------------+-------------------------------------------------------------------+
| **startname**                 | the name (exact string match) of the lattice element to start the |
|                               | machine at this can also be an integer index of the element       |
|                               | sequence number in madx tfs.                                      |
+-------------------------------+-------------------------------------------------------------------+
| **stopname**                  | the name (exact string match) of the lattice element to stop the  |
|                               | machine at this can also be an integer index of the element       |
|                               | sequence number in madx tfs.                                      |
+-------------------------------+-------------------------------------------------------------------+
| **stepsize**                  | the slice step size. Default is 1, but -1 also useful for         |
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
|                               | keys (must be valid bdsim syntax). Alternatively, this can be a   |
|                               | pymadx.Aperture instance that will be queried.                    |
+-------------------------------+-------------------------------------------------------------------+
| **aperlocalpositions**        | Dictionary of element indices to a list of pairs of the form      |
|                               | (local_point, aperdict), for example                              |
|                               | (0.1, {"APER1": "CIRCULAR", "APER1": 0.4}).                       |
|                               | This kwarg is mutually exclusive with "aperturedict".             |
+-------------------------------+-------------------------------------------------------------------+
| **collimatordict**            | A dictionary of dictionaries with collimator information keys     |
|                               | should be exact string match of element name in tfs file value    |
|                               | should be dictionary with the following keys:                     |
|                               | "bdsim_material"   - the material                                 |
|                               | "angle"            - rotation angle of collimator in radians      |
|                               | "xsize"            - x full width in metres                       |
|                               | "ysize"            - y full width in metres                       |
+-------------------------------+-------------------------------------------------------------------+
| **userdict**                  | A python dictionary the user can supply with any additional       |
|                               | information for that particular element. The dictionary should    |
|                               | have keys matching the exact element name in the Tfs file and     |
|                               | contain a dictionary itself with key, value pairs of parameters   |
|                               | and values to be added to that particular element.                |
+-------------------------------+-------------------------------------------------------------------+
| **verbose**                   | Print out lots of information when building the model.            |
+-------------------------------+-------------------------------------------------------------------+
| **beam**                      | True \| False - generate an input gauss Twiss beam based on the   |
|                               | values of the twiss parameters at the beginning of the lattice    |
|                               | (startname) NOTE - we thoroughly recommend checking these         |
|                               | parameters and this functionality is only for partial convenience |
|                               | to have a model that works straight away.                         |
+-------------------------------+-------------------------------------------------------------------+
| **flipmagnets**               | True \| False - flip the sign of all k values for magnets - MADX  |
|                               | currently tracks particles agnostic of the particle charge -      |
|                               | BDSIM however, follows the definition strictly -                  |
|                               | positive k -> horizontal focussing for positive particles         |
|                               | therefore, positive k -> vertical focussing for negative          |
|                               | particles. Use this flag to flip the sign of all magnets.         |
+-------------------------------+-------------------------------------------------------------------+
| **usemadxaperture**           | True \| False - use the aperture information in the TFS file if   |
|                               | APER_1 and APER_2 columns exist.  Will only set if they're        |
|                               | non-zero.  Supercedes kwargs `aperturedict` and                   |
|                               | `aperlocalpositions`.                                             |
+-------------------------------+-------------------------------------------------------------------+
| **defaultAperture**           | The default aperture model to assume if none is specified.        |
+-------------------------------+-------------------------------------------------------------------+
| **biases**                    | Optional list of bias objects to be defined in own _bias.gmad     |
|                               | file.  These can then be attached either with allelementdict for  |
|                               | all components or userdict for individual ones.                   |
+-------------------------------+-------------------------------------------------------------------+
| **allelementdict**            | Dictionary of parameter/value pairs to be written to all          |
|                               | components.                                                       |
+-------------------------------+-------------------------------------------------------------------+
| **optionsDict**               | Optional dictionary of general options to be written to the       |
|                               | bdsim model options.                                              |
+-------------------------------+-------------------------------------------------------------------+
| **linear**                    | Only linear optical components                                    |
+-------------------------------+-------------------------------------------------------------------+
| **overwrite**                 | Do not append an integer to the base file name if it already      |
|                               | exists.  Instead overwrite the files.                             |
+-------------------------------+-------------------------------------------------------------------+
| **allNamesUnique**            | Treat every row in the TFS file/instance as a unique element.     |
|                               | This makes it easier to edit individual components as they are    |
|                               | guaranteed to appear only once in the entire resulting GMAD       |
|                               | lattice.                                                          |
+-------------------------------+-------------------------------------------------------------------+


The user may convert only part of the input model by specifying `startname`
and `stopname`.

Generally speaking, extra information can be folded into the conversion via a user
supplied dictionary with extra parameters for a particular element by name. For a
given element, for example 'drift123', extra parameters can be speficied in a dictionary.
This leads to a dictionary of dictionaries being supplied. This is a relatively simple
structure the user may prepare from their own input format and converters in Python.
For example::

  >>> drift123dict = {'aper1':0.03, 'aper2':0.05, 'apertureType':'rectangular'}
  >>> quaddict = {'magnetGeometryType':'polesfacetcrop}
  >>> d = {'drift123':drift123dict, 'qf1x':quaddict}
  >>> a,o = pybdsim.Convert.MadxTfs2Gmad('inputfile.tfs', 'latticev1', userdict=d)


Notes
*****

1) The name must match the name given in the MADX file exactly.
2) Specific arguments may be given for aperture (`aperturedict`), or for collimation
   (`collimatordict`), which are used specifically for those purposes.
3) There are quite a few options and these are described in :ref:`pybdsim-convert`.
4) The BDSIM-provided pymadx package is required for this conversion to work.
5) The converter will alter the names to remove forbidden characters in names
   in BDSIM such as '$' or '!'.

Preparation of a Small Section
******************************

For large accelerators, it is often required to model only a small part of the machine.
We recommend generating a Tfs file for the full lattice by default and trimming as
required. The pymadx.Data.Tfs class provides an easy interface for trimming lattices.
The first argument to the pybdsim.Convert.MadxTfs2Gmad function can be either a string
describing the file location or a pymadx.Data.Tfs instance. The following example
trims a lattice to only the first 100 elements::

  >>> a = pymadx.Data.Tfs("twiss_v5.2.tfs")
  >>> b = a[:100]
  >>> m,o = pybdsim.Convert.MadxTfs2Gmad(b, 'v5.2a')

	  
MadxTfs2GmadStrength
--------------------

This is a utility to prepare a strength file file from a Tfs file. The output gmad
file may then be included in an existing BDSIM gmad model after the lattice definition
which will update the strengths of all the magnets.

.. _mad8-twiss-2-gmad:

Mad8Twiss2Gmad (using saved TWISS output)
-----------------------------------------

.. note:: This requires the `<https://bitbucket.org/jairhul/pymad8>`_ package.

A MAD8 lattice can be easily converted to a BDSIM gmad input file using the supplied
python utilities. This is achieved by

1. preparing twiss, envel, survey and structure tape files with mad8 
2. echo variables in the mad8 job log (SIGPT, SIGT)
3. converting the tape files to gmad using pybdsim

Running mad8 
************
The following variables need to be defined in the Mad8 job from a :code:`BETA0` ::

  EMITX     := 0.01e-6
  EMITY     := 0.01e-6
  BLENG     := 0.3e-3
  ESPRD     := 0.1e-3
  TALFX     := BETA0[alfx]
  TALFY     := BETA0[alfy]
  TBETX     := BETA0[betx]
  TBETY     := BETA0[bety]
  TGAMX     := (1+TALFX*TALFX)/TBETX
  TGAMY     := (1+TALFY*TALFY)/TBETY
  SIG11     := EMITX*TBETX
  SIG21     := -EMITX*TALFX
  SIG22     := EMITX*TGAMX
  SIG33     := EMITY*TBETY
  SIG43     := -EMITY*TALFY
  SIG44     := EMITY*TGAMY
  C21       := SIG21/SQRT(SIG11*SIG22)
  C43       := SIG43/SQRT(SIG33*SIG44)
  S0_I1.G1  : SIGMA0, SIGX=SQRT(SIG11), SIGPX=SQRT(SIG22), R21=C21, &
                      SIGY=SQRT(SIG33), SIGPY=SQRT(SIG44), R43=C43, &
                      SIGT=BLENG, SIGPT=ESPRD

  VALUE, EMITX
  VALUE, EMITY
  VALUE, ESPRD
  VALUE, BLENG

Creating the output files::
 
  use, <latticename>
  twiss, beta0=BETA0, save, tape=twiss_<latticename> , rtape=rmat_<latticename>
  structure, filename=struct_<latticename>
  envelope, sigma0=SIGMA0, save=envelope, tape=envel_<latticename>

Optionally the following files are required::

  survey, tape=survey_<latticename>
  
Running mad8::

  mad8s < <jobfilename> > <jobfilename>.log  


Converting the Mad8 files
*************************

Two steps are required to create the model from the Mad8 files, first to create 
template files for the collimators and apertures from the Mad8, this is done by 
running the following commands ::

  pybdsim.Convert.Mad8MakeCollimatorTemplate(<inputtwissfilename>,<collimatordbfilename>)
  pybdsim.Convert.Mad8MakeApertureTemplate(<inputtwissfilename>,<aperturedbfilename>)

Copy the <collimatordbfilename> to :code:`collimator.dat` and <aperturedbfilename> to :code:`apertures.dat`
Once prepared, the Tape files can be converted. The converter is used as follows::

  pybdsim.Convert.Mad8Twiss2Gmad(<inputtwissfilename>,<outputgamdfilename>)


pytransport
-----------

`<https://bitbucket.org/jairhul/pytransport>`_ is a separate utility to convert transport
models into BDSIM ones.


BDSIM Primaries To Others
-------------------------

The particle coordinates recorded by BDSIM may be read from an output ROOT file and written
to another format. This can be used for example to ensure the exact same coordinates are used
in multiple BDSIM simulations, or to when comparing BDSIM to other tracking codes such as PTC.
It can also be used for example to pass coordinates from one BDSIM simulation to another where a
detailed simulation of a region of the machine may be desired without the need to simulate the
preceding section of the machine.

For the conversion to PTC coordinate convension, it is assumed that PTC calculations are performed
in 6D, and that the `TIME` flag in the `PTC_CREATE_LAYOUT` routine is false, meaning the
fifth and sixth coordinates are :math:`-pathlength` and :math:`\delta p = \frac{(p - p_0)}{p_0}`
respectively.

For all converters, a `start` number, `n` can be specified which converts from the nth particle
onwards. The number of particles converted can be specified with the `ninrays` argument. For example,
to convert particles 2 to 10 only, the arguments supplied would be :code:`start=2, ninrays=9`.

BdsimPrimaries2Ptc
******************

The primary BDSIM coordinates are converted to PTC format. The converter is used as follows:

  >>> pybdsim.Convert.BdsimPrimaries2Ptc('output.root', 'inrays.dat')

BdsimSampler2Ptc
****************

The BDSIM coordinates from a provided sampler name are converted to PTC format. The converter
is used as follows:

  >>> pybdsim.Convert.BdsimSampler2Ptc('output.root', 'inrays.dat','DR1')

This will convert the coordinates recorded in sampler `DR1`. Only the primary particles are
converted.

BdsimPrimaries2BdsimUserFile
****************************

The primary BDSIM coordinates are converted to a BDSIM `userFile` format. The converter is used
as follows:

  >>> pybdsim.Convert.BdsimPrimaries2BdsimUserFile('output.root', 'inrays.dat')


BdsimSampler2BdsimUserFile
**************************

The BDSIM coordinates from a provided sampler name are converted to a BDSIM `userFile` format.
The converter is used as follows:

  >>> pybdsim.Convert.BdsimSampler2BdsimUserFile('output.root', 'inrays.dat','DR1')

The time coordinate recorded in the input file will be finite if the sampler being converted is
not at the start of the machine. This function is intended to convert particles into a primary
distribution, therefore the time coordinate must be centred around `t=0`. As the nominal time
is not recorded, the mean time is subtracted from all particles. Note that at low particle numbers,
statistical fluctuations may result in the mean time being significantly different from the nominal
time.

BdsimPrimaries2Madx
*******************

The primary BDSIM coordinates are converted to madx format. The converter is used as follows:

  >>> pybdsim.Convert.BdsimPrimaries2Madx('output.root', 'inrays.dat')

BdsimPrimaries2Mad8
*******************

The primary BDSIM coordinates are converted to mad8 format. The converter is used as follows:

  >>> pybdsim.Convert.BdsimPrimaries2Mad8('output.root', 'inrays.dat')
