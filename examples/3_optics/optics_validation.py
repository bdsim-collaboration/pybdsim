import pandas as _pd
import numpy as _np
import matplotlib.pyplot as plt
from cpymad.madx import Madx

import pymadx
import pybdsim
from pybdsim.DataUproot import BDSIMOutput
from pybdsim.Optics import Twiss
import georges_core
from georges_core.units import ureg as _ureg


if __name__ == "__main__":

    madx_input = f"""
        BEAM, PARTICLE=PROTON, PC = 2.794987;
        BRHO      := BEAM->PC * 3.3356;

        call, file="madx/ps_mu.seq";
        call, file="madx/ps_ss.seq";
        call, file="madx/scenarios/{name_path}/{sub_scenario}/{scenario}.beam";
        call, file="madx/scenarios/{name_path}/{sub_scenario}/{scenario}.str";

        use, sequence=PS;
        select,flag=twiss, clear;
        twiss, sequence=PS, file='madx_optics/{name_path}.tfs';
        
        stop;
    """
    madx = Madx()
    madx.input(madx_input)
    tw = madx.table['twiss'].dframe()

    ps_machine = pybdsim.Convert.CPyMad2Gmad(madx_instance=madx,
                                             model_file=f"model/{model_type}.yml")(with_bdsim_beam=False)
    madx_beam = madx.sequence['ps'].beam
    offset = 1e-5
    x0 = tw.iloc[0]['x']
    y0 = tw.iloc[0]['y']
    xp0 = tw.iloc[0]['px']
    yp0 = tw.iloc[0]['py']

    twiss_beam = _np.array([[x0, xp0, y0, yp0, madx_beam['pc']],
                            [x0 + offset, xp0, y0, yp0, madx_beam['pc']],
                            [x0, xp0 + offset, y0, yp0, madx_beam['pc']],
                            [x0, xp0, y0 + offset, yp0, madx_beam['pc']],
                            [x0, xp0, y0, yp0 + offset, madx_beam['pc']],
                            [x0, xp0, y0, yp0, (1 + offset) * madx_beam['pc']],
                            [x0 - offset, xp0, y0, yp0, madx_beam['pc']],
                            [x0, xp0 - offset, y0, yp0, madx_beam['pc']],
                            [x0, xp0, y0 - offset, yp0, madx_beam['pc']],
                            [x0, xp0, y0, yp0 - offset, madx_beam['pc']],
                            [x0, xp0, y0, yp0, (1 - offset) * madx_beam['pc']]
                            ])

    _np.savetxt(f'{path}twiss_coordinates.dat', twiss_beam, delimiter=' ', fmt='%.8e')

    bdsim_beam = pybdsim.Beam.Beam(particletype=madx_beam['particle'],
                                   energy=madx_beam['energy'],
                                   distrtype="userfile",
                                   distrFile="\"twiss_coordinates.dat\"",
                                   distrFileFormat="\"x[m]:xp[rad]:y[m]:yp[rad]:P[GeV]\"")
    ps_machine.AddBeam(bdsim_beam)
    ps_machine.options['samplersSplitLevel'] = 0
    ps_machine.Write(filename=f'{path}ps.gmad')

    # Add sample all at the end of the main file
    with open(f"{path}ps.gmad", 'a') as f:
        f.write('sample, all;')

    # opening the file in read mode
    file = open(f"{path}ps_beam.gmad", "r")
    replacement = ""
    # using the for loop
    for line in file:
        line = line.strip()
        if 'energy' in line:
            changes = f"momentum = {madx_beam['pc']}*GeV,"
        else:
            changes = line
        replacement = replacement + changes + "\n"

    file.close()
    # opening the file in write mode
    fout = open(f"{path}ps_beam.gmad", "w")
    fout.write(replacement)
    fout.close()

    pybdsim.Run.Bdsim(gmadpath=f"{path}ps.gmad",
                      outfile=f"{path}results/output_{scenario}_{model_type}",
                      ngenerate=11,
                      batch=True,
                      bdsimExecutable="/Users/rtesse/packages/bdsim-build-clion/install/bin/bdsim")

    samplers = pybdsim.Data.Load(filepath=f"{path}results/output_{scenario}_{model_type}.root")
    sampler_name = list(map(str, list(samplers.GetSamplerNames())))[0:-2]  # last element has no data if circular
    sampler_name[0] = 'drift_0.'
    samplers_data = {}

    for idx, sm in enumerate(sampler_name):
        # Careful, order matters
        data_samplers = _pd.DataFrame(data=dict((k,
                                                 pybdsim.Data.SamplerData(samplers, sm).data[k]) for k in
                                                ('x', 'xp', 'y', 'yp', 'S', 'p')))

        samplers_data[sm] = data_samplers

    tw_init = {'ALPHA11': tw.iloc[0]['alfx'], 'ALPHA22': tw.iloc[0]['alfy'],
               'BETA11': tw.iloc[0]['betx'], 'BETA22': tw.iloc[0]['bety'],
               'DISP1': tw.iloc[0]['dx'] * beta_rel, 'DISP2': tw.iloc[0]['dpx'] * beta_rel,
               'DISP3': tw.iloc[0]['dy'] * beta_rel, 'DISP4': tw.iloc[0]['dpy'] * beta_rel
               }

    tw_init['GAMMA11'] = (1 + tw.iloc[0]['alfx'] ** 2) / tw.iloc[0]['betx']
    tw_init['GAMMA22'] = (1 + tw.iloc[0]['alfy'] ** 2) / tw.iloc[0]['bety']