import jinja2 as _jinja2
import pybdsim.Run as _Run
import os as _os
import pickle as _pickle
import numpy as _np
import itertools as _itertools

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
    particles.append(_np.array([ 0,0,0,0,energy_deviation,0]))
    particles.append(_np.array([ 0,0,0,0,-energy_deviation,0]))
    particles.append(_np.array([ 0,0,0,0,0,time_deviation]))
    particles.append(_np.array([ 0,0,0,0,0,-time_deviation]))

    # form tensor product
    if tensor_product :
        s = set()
        for i in _itertools.product(range(0,len(particles)), range(0,len(particles))):
            l = list(i)
            l.sort()
            if l[0] != l[1]:
                print(l)
                s.add(tuple(l))

        # add new tensor particles
        for p in s :
            particles.append(particles[p[0]]+particles[p[1]])

    # easier to manipulate if array
    particles = _np.array(particles)

    # put back energy
    particles[:,4] = particles[:,4] + energy

    # write inray file
    if file_name :
        _np.savetxt(file_name,particles)

    return particles


def GmadTemplate(file_name_in, file_name_out, replacement_dict ={}, template_dir="./") :
    """
    **GmadTemplate** render gmad template. Keys in the template should be of the form {{ string }}


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

def ScanParameter(file_name_in,
                  parameter_key,
                  parameter_steps = [],
                  replacement_dict = {},
                  analysis_function = None,
                  template_dir="./",
                  keep_files = False,
                  numpy_output = True,
                  pickle_output = True) :
    """
    **ScanParameter** loop variable, render gmad templat, run bdsim and perform analysis. The variables in the template
    file need to be in the form {{ key }}

    Example:

    >>> def deltaE(filename) :
   ...:     return pybdsim.Analysis.CalculateEnergyGain(filename,"d1","rf1")
    >>> pybdsim.Analysis.ScanParameter('drift.tem','RFCAVITY_FREQUENCY',range(0,100,10), analysis_function = deltaE)

    returns [parameter_steps, list of analysis_function return type]
    """


    analysis_function_return = []

    for parameter in parameter_steps :

        # gmad outout file name
        gmad_name_out = file_name_in.replace(".tem","")+"_"+parameter_key+"_"+str(parameter)+".gmad"
        # root output file name
        root_name_out = file_name_in.replace(".tem","")+"_"+parameter_key+"_"+str(parameter)

        # add parameter to replacement dict
        replacement_dict[parameter_key] = parameter

        # render template
        GmadTemplate(file_name_in, gmad_name_out, replacement_dict, template_dir)

        # run bdsim
        _Run.Bdsim(gmad_name_out, root_name_out, silent=True, ngenerate=25000)

        # run analysis function
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

def LoadScanOutput(file_name) :
    with open(file_name, 'rb') as f:
        if file_name.find("pkl") != - 1:
            data = _pickle.load(f)
        elif file_name.find("npy") != -1:
            data1 = _np.load(f)
            data2 = _np.load(f)
            data = [data1,data2]

    return data