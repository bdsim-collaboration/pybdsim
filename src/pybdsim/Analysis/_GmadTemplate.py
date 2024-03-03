import jinja2 as _jinja2
import pybdsim.Run as _Run
import os as _os
import pickle as _pickle
import numpy as _np
import itertools as _itertools
import copy as _copy

_np.set_printoptions(edgeitems=30, linewidth=100000, formatter=dict(float=lambda x: "%.3g" % x))

def BeamPrincipleRayTemplate(file_name=None,
                             position_deviation = 1e-6,
                             angular_deviation = 1e-6,
                             time_deviation = 1e-12,
                             energy_deviation = 0.1,
                             particle = "e-",
                             energy = 1,
                             tensor_product = False) :

    particles = []
    particles.append(_np.array([ position_deviation,0,0,0,0,0]))
    particles.append(_np.array([-position_deviation,0,0,0,0,0]))
    particles.append(_np.array([ 0,0,position_deviation,0,0,0]))
    particles.append(_np.array([ 0,0,-position_deviation,0,0,0]))
    particles.append(_np.array([ 0,angular_deviation,0,0,0,0]))
    particles.append(_np.array([ 0,-angular_deviation,0,0,0,0]))
    particles.append(_np.array([ 0,0,0,angular_deviation,0,0]))
    particles.append(_np.array([ 0,0,0,-angular_deviation,0,0]))
    particles.append(_np.array([ 0,0,0,0,time_deviation,0]))
    particles.append(_np.array([ 0,0,0,0,-time_deviation,0]))
    particles.append(_np.array([ 0,0,0,0,0,energy_deviation]))
    particles.append(_np.array([ 0,0,0,0,0,-energy_deviation]))

    # form tensor product
    if tensor_product :
        s = set()
        for i in _itertools.product(range(0,len(particles)), range(0,len(particles))):
            l = list(i)
            l.sort()
            if l[0] != l[1]:
                s.add(tuple(l))

        # add new tensor particles
        for p in s :
            particles.append(particles[p[0]]+particles[p[1]])

    # easier to manipulate if array
    particles = _np.array(particles)

    # put back energy
    particles[:,5] = particles[:,5] + energy

    # write inray file
    if file_name :
        _np.savetxt(file_name,particles)

    return particles


def GmadTemplate(file_name_in, file_name_out, replacement_dict ={}, template_dir="./") :
    """
    **GmadTemplate** render gmad template. Keys in the template should
    be of the form {{ string }}


    Example:

    >>> pybdsim.Analysis.GmadTemplate('drift.tem','drift.gmad',{"string":"value"})

    returns None
    """

    environment = _jinja2.Environment(loader=_jinja2.FileSystemLoader(template_dir))
    template = environment.get_template(file_name_in)

    content = template.render(replacement_dict)

    with open(file_name_out, mode="w", encoding="utf-8") as file:
        file.write(content)
        print(f"... wrote {file_name_out}")

def ScanParameter1D(file_name_in,
                    parameter_key,
                    parameter_steps = [],
                    replacement_dict = {},
                    analysis_function = None,
                    template_dir="./",
                    keep_files = False,
                    numpy_output = False,
                    pickle_output = True,
                    full_file_name = False) :
    """
    **ScanParameter1D** loop variable, render gmad template, run bdsim and perform analysis.
    The variables in the template file need to be in the form {{ key }}

    Example:

    >>> def deltaE(filename) :
   ...:     return pybdsim.Analysis.CalculateEnergyGain(filename,"d1","rf1")
    >>> pybdsim.Analysis.ScanParameter1D(file_name_in = 'drift.tem',
                                         parameter_key = 'RFCAVITY_FREQUENCY',
                                         parameter_steps = [10,20,30],
                                         analysis_function = deltaE)

    +-----------------+---------------------------------------------------------+
    | **Parameters**  | **Description**                                         |
    +-----------------+---------------------------------------------------------+
    | file_name_in    | Template gmad file                                      |
    +-----------------+---------------------------------------------------------+
    | parameter_key   | Template key to scan                                    |
    +-----------------+---------------------------------------------------------+
    | parameter_steps | list or range of parameter steps                        |
    +-----------------+---------------------------------------------------------+
    | replacement_dict| Dict ok template key - value pairs                      |
    +-----------------+---------------------------------------------------------+
    | analysis_funct  | Function to be run for each parameter step              |
    +-----------------+---------------------------------------------------------+
    | template_dir    | Directory of template                                   |
    +-----------------+---------------------------------------------------------+
    | keep_files      | True : keep rendered gmad files and root files          |
    +-----------------+---------------------------------------------------------+
    | numpy_output    | True : Store analysis function output in numpy file     |
    +-----------------+---------------------------------------------------------+
    | pickle_output   | True : Store analysis function output in pickle file    |
    +-----------------+---------------------------------------------------------+
    | full_file_name  | True : Expand replacement_dict for output file names    |
    +-----------------+---------------------------------------------------------+
    returns [parameter_steps, list of analysis_function return type]
    """


    analysis_function_return = []

    # expand parameter dict for name
    extended_file_name = ""

    if full_file_name :
        for k in replacement_dict:
            extended_file_name += "_"+k+"_"+str(replacement_dict[k])

    for parameter in parameter_steps :

        # gmad outout file name
        gmad_name_out = file_name_in.replace(".tem","")+"_"+parameter_key+"_"+str(_np.round(parameter,2))+extended_file_name+".gmad"
        # root output file name
        root_name_out = file_name_in.replace(".tem","")+"_"+parameter_key+"_"+str(_np.round(parameter,2))+extended_file_name

        # add parameter to replacement dict
        replacement_dict[parameter_key] = parameter

        # render template
        GmadTemplate(file_name_in, gmad_name_out, replacement_dict, template_dir)

        # run bdsim
        _Run.Bdsim(gmad_name_out, root_name_out, silent=True, ngenerate=10000)

        # run analysis function
        if analysis_function :
            analysis_return = analysis_function(root_name_out+".root")
            print(analysis_return)
            analysis_function_return.append(analysis_return)

        # run optics program

        # run histomerge

        # clean up files if needed
        if not keep_files :
            # delete gmad file
            if _os.path.exists(gmad_name_out):
                _os.remove(gmad_name_out)

            # delete root file
            if _os.path.exists(root_name_out+".root"):
                _os.remove(root_name_out+".root")

    if pickle_output :
        with open(file_name_in.replace(".tem","")+"_"+parameter_key+".pkl", 'wb') as f:
            _pickle.dump([parameter_steps, analysis_function_return], f)

    if numpy_output :
        with open(file_name_in.replace(".tem","")+"_"+parameter_key+".npy", 'wb') as f:
            _np.save(f, parameter_steps)
            _np.save(f, analysis_function_return)

    return [parameter_steps, analysis_function_return]


def ScanParameter2D(file_name_in,
                    parameter_key1,
                    parameter_key2,
                    parameter_steps1 = [],
                    parameter_steps2 = [],
                    replacement_dict = {},
                    analysis_function = None,
                    template_dir="./",
                    keep_files = False,
                    numpy_output = False,
                    pickle_output = True) :
    """
    **ScanParameter2D** double loop over 2 variable variable , render gmad template,
    run bdsim and perform analysis. The variables in the template file need to be in
    the form {{ key }}

    Example:

    >>> pybdsim.Analysis.ScanParameter2D(file_name_in = 'drift.tem',
                                         parameter_key1 = 'RBEND_LENGTH',
                                         parameter_key2 = 'RBEND_ANGLE',
                                         parameter_steps1 = [1,2,3],
                                         parameter_steps2 = [0.05,0.10,0.15],
                                         analysis_function = None)

    +-----------------+---------------------------------------------------------+
    | **Parameters**  | **Description**                                         |
    +-----------------+---------------------------------------------------------+
    | file_name_in    | Template gmad file                                      |
    +-----------------+---------------------------------------------------------+
    | parameter_key1  | First template key to scan                              |
    +-----------------+---------------------------------------------------------+
    | parameter_key2  | Second template key to scan                             |
    +-----------------+---------------------------------------------------------+
    | parameter_steps1| list or range of parameter steps for key1               |
    +-----------------+---------------------------------------------------------+
    | parameter_steps2| list or range of parameter steps for key2               |
    +-----------------+---------------------------------------------------------+
    | replacement_dict| Dict ok template key - value pairs                      |
    +-----------------+---------------------------------------------------------+
    | analysis_funct  | Function to be run for each parameter step              |
    +-----------------+---------------------------------------------------------+
    | template_dir    | Directory of template                                   |
    +-----------------+---------------------------------------------------------+
    | keep_files      | True : keep rendered gmad files and root files          |
    +-----------------+---------------------------------------------------------+
    | numpy_output    | True : Store analysis function output in numpy file     |
    +-----------------+---------------------------------------------------------+
    | pickle_output   | True : Store analysis function output in pickle file    |
    +-----------------+---------------------------------------------------------+
    | full_file_name  | True : Expand replacement_dict for output file names    |
    +-----------------+---------------------------------------------------------+
    returns [parameter_steps, list of analysis_function return type]
    """

    parameter_steps = []
    analysis_function_return = []

    for parameter1 in parameter_steps1 :
        replacement_dict_new = _copy.copy(replacement_dict)
        replacement_dict_new[parameter_key1] = parameter1
        r = ScanParameter1D(file_name_in, parameter_key2, parameter_steps2,
                            replacement_dict_new, analysis_function, template_dir,
                            keep_files = keep_files,
                            numpy_output = False,
                            pickle_output = False,
                            full_file_name= True)

        analysis_function_return.append(r)


    if pickle_output :
        with open(file_name_in.replace(".tem","")+"_"+parameter_key1+"_"+parameter_key2+".pkl", 'wb') as f:
            _pickle.dump([parameter_steps1, analysis_function_return], f)

    if numpy_output :
        with open(file_name_in.replace(".tem","")+"_"+parameter_key1+"_"+parameter_key2+".npy", 'wb') as f:
            _np.save(f, parameter_steps)
            _np.save(f, analysis_function_return)

def LoadScanOutput(file_name) :
    with open(file_name, 'rb') as f:
        if file_name.find("pkl") != - 1:
            data = _pickle.load(f)
        elif file_name.find("npy") != -1:
            data1 = _np.load(f)
            data2 = _np.load(f)
            data = [data1,data2]

    return data