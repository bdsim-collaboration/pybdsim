# Wrapper for pytransport conversion.

from pybdsim import Builder as _pyBuilder
from pybdsim import Options as _Options

from pytransport.Convert import _Convert
from pytransport.Data import ConversionData


def Transport2Gmad(inputfile,
                   particle='proton',
                   distrType='gauss',
                   outputDir='gmad',
                   debug=False,
                   dontSplit=False,
                   keepName=False,
                   combineDrifts=False):
    """
    **Transport2Gmad** convert a Transport input or output file into a gmad input file for bdsim

    +-------------------------------+-------------------------------------------------------------------+
    | **inputfile**                 | dtype = string                                                    |
    |                               | path to the input file                                            |
    +-------------------------------+-------------------------------------------------------------------+
    | **particle**                  | dtype = string. Optional, default = "proton"                      |
    |                               | the particle species                                              |
    +-------------------------------+-------------------------------------------------------------------+
    | **distrType**                 | dtype = string. Optional, Default = "gauss".                      |
    |                               | the beam distribution type. Can be either gauss or gausstwiss.    |
    +-------------------------------+-------------------------------------------------------------------+
    | **outputDir**                 | dtype=string. Optional, default = "gmad"                          |
    |                               | the output directory where the files will be written              |
    +-------------------------------+-------------------------------------------------------------------+
    | **debug**                     | dtype = bool. Optional, default = False                           |
    |                               | output a log file (inputfile_conversion.log) detailing the        |
    |                               | conversion process, element by element                            |
    +-------------------------------+-------------------------------------------------------------------+
    | **dontSplit**                 | dtype = bool. Optional, default = False                           |
    |                               | the converter splits the machine into multiple parts when a beam  |
    |                               | is redefined in a Transport lattice. dontSplit overrides this and |
    |                               | forces the machine to be written to a single file                 |
    +-------------------------------+-------------------------------------------------------------------+
    | **keepName**                  | dtype = bool. Optional, default = False                           |
    |                               | keep the names of elements as defined in the Transport inputfile. |
    |                               | Appends element name with _N where N is an integer if the element |
    |                               | name has already been used                                        |
    +-------------------------------+-------------------------------------------------------------------+
    | **combineDrifts**             | dtype = bool. Optional, default = False                           |
    |                               | combine multiple consecutive drifts into a single drift           |
    +-------------------------------+-------------------------------------------------------------------+

    Example:

    >>> Transport2Gmad(inputfile)

    Writes converted machine to disk. Reader automatically detects if the supplied input file is a Transport input
    file or Transport output file.

    """
    converter = _Convert(ConversionData(inputfile=inputfile, options=_Options.Options(), machine=_pyBuilder.Machine(),
                                        particle=particle, debug=debug, distrType=distrType, gmad=True,
                                        gmadDir=outputDir, madx=False, madxDir='', dontSplit=dontSplit,
                                        keepName=keepName, combineDrifts=combineDrifts))
    # automatically convert
    converter.Convert()

