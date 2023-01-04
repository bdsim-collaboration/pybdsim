#!/usr/bin/env python2.6

import numpy as _np
import optparse as _op
from collections import OrderedDict

import pymad8

from .. import Builder
from .. import Beam
import pybdsim.Options as Options
import pybdsim.XSecBias as XSecBias

# TODO
# Move name to top of element list
# Factorise component arguments before call
# Add fringe fields
# Flip and scale all magnets
# Check input options
# Check SR scaling

class MAD8ToGMADConversionError(Exception): pass

def Mad8Twiss2GmadNew(inputFileName,
                      outputFileName,
                      rMatFile         = "",
                      mad8FileFileName = "",
                      mad8OutputFile   = "",
                      istart           = 0,
                      iend             = -1,
                      collimatorFile   = "collimators.dat",
                      apertures        = "apertures.dat",
                      beamName         = ["nominal"],
                      beam             = None,
                      options          = None,
                      xSecBias         = [],
                      samplers         = 'all',
                      flipMagnets      = 1,
                      openCollimators  = True,
                      openApertures    = True,
                      enableSextupoles = True, # linear
                      enableSr         = False,
                      enableSrScaling  = False,
                      enableMuon       = False,
                      enableMuonBias   = False) :
    pass

def Mad8Twiss2Gmad(inputFileName,
                   outputFileName,
                   mad8FileName                 = "",
                   mad8OutputFile               = "",
                   istart                       = 0,
                   iend                         = -1,
                   beam                         = ["nominal"],
#                   gemit                        = (1e-10,1e-10),
                   gemit                        = (1e-8,1e-8),
                   collimator                   = "collimator.dat",
                   apertures                    = "apertures.dat",
                   samplers                     = 'all',
                   options                      = True,
                   flip                         = 1,
                   enableSextupoles             = True,
                   openApertures                = True,
                   openCollimators              = True,
                   enableSr                     = False,
                   enableSrScaling              = False,
                   enableMuon                   = False,
                   enableMuonBias               = True,
                   rmat                         = ""):
    """
    Convert MAD8 twiss output to a BDSIM model in GMAD syntax.
    
    :param inputfilename: mad8 TWISS output
    :type  inputfilename: str
    :param outputfilename: desired BDSIM .gmad output name
    :type  outputfilename: str
    :param istart,iend: integer number mad8 elements to begin and end conversion.
    :type istart,iden: int
    :param beam: desired BDSIM beamtype 
    :type beam: str, one of ("reference","nominal","halo")
    :param gemit: geometry emittance tuple in x,y- default (1e-8,1e-8) - or filename of .txm with defined gemit and Esprd (and value, [name] declaration for each).
    :type gemit: tuple(float, float)
    :param collimator: relevant .dat files generated from mad8 model using `pybdsim.Convert.Mad8MakeCollimatorTemplate`.
    :type  collimator: str
    :param apertures: relevant .dat files generated from mad8 model using `pybdsim.Convert.Mad8MakeApertureTemplate`.
    :type  aperturs: str
    :param rmat: mad8 r-matrix output.
    :type rmat: str
    """

    # open mad output
    o = pymad8.Output.OutputReader()
    c, t = o.readFile(inputFileName,'twiss')

    # check type of start
    # if string find element number
    if type(istart) == str :
        print("Mad8Twiss2Gmad> finding start : ", istart)
        istart = c.findByName(istart)[0]
        print("Mad8Twiss2Gmad> using index   : ", istart)

    # load Collimator db or use instance
    if type(collimator) == str :
        collimator = Mad8CollimatorDatabase(collimator)
        if openCollimators :
            collimator.openCollimators()
    # load Aperture db or use instance
    if type(apertures) == str :
        apertures = Mad8ApertureDatabase(apertures)
        if openApertures :
            apertures.openApertures()
    #load r matrices
    if rmat != "":
        c2, rmat = o.readFile(rmat,'rmat')

    print('Collimator database')
    print(collimator)
    print('Aperture database')
    print(apertures)

    #val0=value at 0th element of INPUT mad8 file. val_cut=value at start-point for cut beamlines - i.e. 0th element of OUTPUT bdsim file.
    # Need nominal energy for acceleration and SR calculations
    s           = t.getColumn('suml')
    try:
        elelength = c.getRowByIndex(istart)['l']
    except:
        elelength = 0
    s_cut       = s[istart] - elelength
    print(s_cut)
    energy      = c.getColumn('E')
    energy0     = energy[0]
    energy_cut  = energy[istart]

    print('Initial element              ', istart)
    print('Initial S                    ', s_cut)
    if s_cut!= 0 :
        options = True

    # create machine instance
    # TODO : Need to extract nominal energy from file
    a = Builder.Machine(sr=enableSrScaling, energy0=energy_cut)

    # load mad8
    if mad8FileName != "" :
        particle = 'e+'
        m8 = pymad8.Output.Mad8(mad8FileName)
        if m8.particle == 'ELECTRON':
            particle = 'e-'
            charge   = -1.
            mass     =  0.511
            flip     = -1

        elif m8.particle == 'POSITRON':
            particle = 'e+'
            charge   =  1.
            mass     =  0.511
            flip     =  1

        elif m8.particle == 'PROTON':
            particle = 'proton'
            charge   =  1.
            mass     =  938.
            flip     =  1
    else :
        particle = 'e-'
        charge   = -1.
        mass     = 0.511
        flip     = -1

    # momentum and rigitity
    momentum0 = _np.sqrt(energy0**2-(mass/1000.)**2)
    brho0      = momentum0/charge
    print('particle  ',particle)
    print('charge    ',charge)
    print('mass      ',mass)
    print('energy0   ',energy0)
    print('momentum0 ',momentum0)
    print('brho0     ',brho0)

    # momentum scale
    momentum     = _np.sqrt(energy**2-(mass/1000.)**2)
    momentum_cut = momentum[istart]
    scale        = momentum/momentum_cut

    #scaleToWrite = _np.stack([scale,scale_mom],axis=-1)
    #_np.savetxt("scale.txt",scaleToWrite)

    # create beam (emit and energy spread)
    if mad8OutputFile != "" :
        echoVals = pymad8.Output.EchoValue(mad8OutputFile)
        echoVals.loadValues()
        gemit = _np.zeros(2)
        gemit[0] = echoVals.valueDict['EMITX']
        gemit[1] = echoVals.valueDict['EMITY']
        esprd    = echoVals.valueDict['ESPRD']
        #bleng    = echoVals.valueDict['BLENG']
        bleng    = 0.0
    else:
        esprd = 0.0001
        bleng = 0

    if istart !=0:
        # Relativistic factors at 0
        rGamma0    = (energy0*1000)/(mass)
        rBeta0     = _np.sqrt(1-1/(rGamma0**2))
        # Momentum & relativistic factors at cut
        energy_cut=energy[istart]
        momentum_cut =_np.sqrt(energy_cut**2+mass**2)
        rGamma_cut = (energy_cut*1000)/mass
        rBeta_cut = _np.sqrt(1-(1/(rGamma_cut**2)))
        # Normalised emittance
        Nemitx     = rBeta0*rGamma0*gemit[0]
        Nemity     = rBeta0*rGamma0*gemit[1]
        emitx  = Nemitx/(rBeta_cut*rGamma_cut)
        emity  = Nemity/(rBeta_cut*rGamma_cut)
        gemit=[emitx,emity]


    xdisp=t.getColumn('dx')
    ydisp=t.getColumn('dy')
    xpdisp=t.getColumn('dpx')
    ypdisp=t.getColumn('dpy')
    # create beam
    beamname = beam[0]
    if beamname == "reference" :
        b = Beam.Beam(particle, energy_cut, "reference")
        a.AddBeam(b)

    elif beamname == "nominal" :
        if istart >= 1:
            b = Mad8Twiss2Beam(t,istart-1,particle,energy_cut)
            b._SetDispX(xdisp[istart-1])
            b._SetDispY(ydisp[istart-1])
            b._SetDispXP(xpdisp[istart-1])
            b._SetDispYP(ypdisp[istart-1])
        else:
            b = Mad8Twiss2Beam(t,istart,particle,energy_cut)
            b._SetDispX(xdisp[istart])
            b._SetDispY(ydisp[istart])
            b._SetDispXP(xpdisp[istart])
            b._SetDispYP(ypdisp[istart])
        b._SetEmittanceX(gemit[0],'m')
        b._SetEmittanceY(gemit[1],'m')
        b._SetSigmaE(esprd*energy[0]/energy_cut)
        b._SetSigmaT(bleng)
        b._SetOffsetSampleMean(True)

        a.AddBeam(b)
    elif beamname == "halo" :
        if istart >= 1:
            b = Mad8Twiss2Beam(t,istart-1,particle,energy_cut)
            b.SetDistributionType("halo")
            betx = t.data[istart-1][t.keys['betx']]
            bety = t.data[istart-1][t.keys['bety']]
            alfx = t.data[istart-1][t.keys['alfx']]
            alfy = t.data[istart-1][t.keys['alfy']]
        else:
            b = Mad8Twiss2Beam(t,istart,particle,energy_cut)
            b.SetDistributionType("halo")
            betx = t.data[istart][t.keys['betx']]
            bety = t.data[istart][t.keys['bety']]
            alfx = t.data[istart][t.keys['alfx']]
            alfy = t.data[istart][t.keys['alfy']]


        # 5 13
        # 36 92
        nsigxmin = beam[1]
        nsigxmax = beam[2]
        nsigymin = beam[3]
        nsigymax = beam[4]

        b._SetHaloEmittanceX(nsigxmin**2*gemit[0],'m')
        b._SetHaloEmittanceY(nsigymin**2*gemit[1],'m')
        b._SetHaloEnvelopeEmitX(nsigxmax**2*gemit[0],'m')
        b._SetHaloEnvelopeEmitY(nsigymax**2*gemit[1],'m')
        b._SetEnvelopeX(_np.sqrt(nsigxmax**2*betx*gemit[0]))
        b._SetEnvelopeXP(_np.sqrt(nsigxmax**2*(1+alfx**2)/betx*gemit[0]))
        b._SetEnvelopeY(_np.sqrt(nsigymax**2*betx*gemit[1]))
        b._SetEnvelopeYP(_np.sqrt(nsigymax**2*(1+alfy**2)/bety*gemit[1]))
        b._SetHaloPSWeightParameter(-1.0)
        b._SetHaloPSWeightFunction("oneoverr")
        b._SetSigmaE(esprd)

        a.AddBeam(b)

    # create options
    if options :
        o = Options.ElectronColliderOptions()
        o.SetBuildTunnel(False)
        o.SetBuildTunnelFloor(False)
        o.SetStopSecondaries(False)
        o.SetPrintModuloFraction(1e-2)
        o.SetMagnetGeometryType('"polesfacetcrop"')
        o.SetBeamlineS(s_cut,'m')
        process = 'em'
        if enableSr :
            if process == '' :
                process = 'synchrad'
            else :
                process += ' synchrad'
        if enableMuon :
            if process == '' :
                process = 'muon'
            else :
                process += ' muon'

            o.SetStoreTrajectory(True)
            o.SetStoreTrajectoryParticle("mu+ mu-")


        o.SetPhysicsList(process)
        a.AddOptions(o)

    # create bias options
    biasList = ""
    if enableMuonBias :
        gmb = XSecBias.XSecBias("gmb","gamma","GammaToMuPair","1e2","1")
        pmb = XSecBias.XSecBias("pmb","e+","AnnihiToMuPair","1e2","1")
        a.AddBias(gmb)
        a.AddBias(pmb)

        biasList = "gmb pmb"

    # dictionary of element names
    nameDict = {}

    # iterate through objects and build machine
    if iend == -1 :
        iend = len(c.name)
    else :
        iend += 1
    for i in range(istart,iend,1) :
        # unique(c.type)
        # print element
        # print i,c.name[i],c.type[i]

        # check name dictionary
        try :
            eCount = nameDict[c.name[i]]
        except KeyError :
            nameDict[c.name[i]] = 0
            eCount = nameDict[c.name[i]]

        # check if name starts with a number
        prepend = ''
        if c.name[i][0].isdigit() :
            prepend = 'M_'

#        print c.name[i]+'_'+str(eCount)

        if c.type[i] == '' :
            a.AddMarker(name  = prepend+c.name[i]+'_'+str(eCount))
#       ###################################################################
        elif c.type[i] == 'DRIF' :
            a.AddDrift(name   = prepend+c.name[i]+'_'+str(eCount),
                       length = float(c.data[i][c.keys['drif']['l']]),
                       aper1  = float(apertures.aper[i]))
#       ###################################################################
        elif c.type[i] == 'MARK' :
            a.AddMarker(name     = prepend+c.name[i]+'_'+str(eCount))
#       ###################################################################
        elif c.type[i] == 'SOLE' :
            a.AddSolenoid(name   = prepend+c.name[i]+'_'+str(eCount),
                          length = float(c.data[i][c.keys['sole']['l']]),
                          ks     = float(c.data[i][c.keys['sole']['ks']]))
#       ###################################################################
        elif c.type[i] == 'INST' :
            a.AddMarker(name = prepend+c.name[i]+'_'+str(eCount))
#       ###################################################################
        elif c.type[i] == 'MONI' :
            a.AddMarker(name = prepend+c.name[i]+'_'+str(eCount))
#       ###################################################################
        elif c.type[i] == 'IMON' :
            a.AddMarker(name = prepend+c.name[i]+'_'+str(eCount))
#       ###################################################################
        elif c.type[i] == 'BLMO' :
            a.AddMarker(name = prepend+c.name[i]+'_'+str(eCount))
#       ###################################################################
        elif c.type[i] == 'WIRE' :
            a.AddMarker(name = prepend+c.name[i]+'_'+str(eCount))
#       ###################################################################
        elif c.type[i] == 'QUAD' :
            if float(c.data[i][c.keys['quad']['l']]) < 1e-7 :
                a.AddMarker(name = prepend+c.name[i]+'_'+str(eCount))
            else :
                a.AddQuadrupole(name    = prepend+c.name[i]+'_'+str(eCount),
                                k1      = float(c.data[i][c.keys['quad']['k1']])*flip,
                                length  = float(c.data[i][c.keys['quad']['l']]),
                                tilt    = float(c.data[i][c.keys['quad']['tilt']]),
                                aper1   = float(apertures.aper[i]),
                                scaling = scale[i])
#       ###################################################################
        elif c.type[i] == 'SEXT' :
            l = float(c.data[i][c.keys['sext']['l']])
            if l < 1e-7 :
                a.AddDrift(name   = prepend+c.name[i]+'_'+str(eCount),
                           length = l,
                           aper1  = apertures.aper[i])
            else :
                if enableSextupoles :
                    k2in=float(c.data[i][c.keys['sext']['k2']])*flip
                else :
                    k2in=0.0
                a.AddSextupole(name    = prepend+c.name[i]+'_'+str(eCount),
                               length  = l,
                               k2      = k2in,
                               aper1   = apertures.aper[i],
                               scaling = scale[i])
#       ###################################################################
        elif c.type[i] == 'OCTU' :
            if c.data[i][c.keys['octu']['l']] > 1e-7 :
                a.AddDrift(name   = prepend+c.name[i]+'_'+str(eCount),
                           length = float(c.data[i][c.keys['octu']['l']]),
                           aper1  = apertures.aper[i])
            else :
                a.AddMarker(prepend+c.name[i]+'_'+str(eCount))
#       ###################################################################
        elif c.type[i] == 'DECU' :
            pass
#       ###################################################################
        elif c.type[i] == 'MULT' :
                a.AddMarker(name = prepend+c.name[i]+'_'+str(eCount))
#       ###################################################################
        elif c.type[i] == 'HKIC' :
            a.AddDrift(name   = prepend+c.name[i]+'_'+str(eCount),
                       length = float(c.data[i][c.keys['hkic']['l']]),
                       aper1  = float(apertures.aper[i]))
#       ###################################################################
        elif c.type[i] == 'VKIC' :
            a.AddDrift(name   = prepend+c.name[i]+'_'+str(eCount),
                       length = float(c.data[i][c.keys['vkic']['l']]),
                       aper1  = float(apertures.aper[i]))
#       ###################################################################
        elif c.type[i] == 'KICK' :
            a.AddDrift(name   = prepend+c.name[i]+'_'+str(eCount),
                       length = float(c.data[i][c.keys['kick']['l']]),
                       aper1   = float(apertures.aper[i]))
#       ###################################################################
        elif c.type[i] == 'SBEN' :
            if float(c.data[i][c.keys['sben']['l']]) < 1e-7 :
                a.AddMarker(prepend+c.name[i]+'_'+str(eCount))
            else :
                length = float(c.data[i][c.keys['sben']['l']])
                angle  = float(c.data[i][c.keys['sben']['angle']])
                aper   = float(apertures.aper[i])
                k1     = float(c.data[i][c.keys['sben']['k1']])
                e1in   = float(c.data[i][c.keys['sben']['e1']])
                e2in   = float(c.data[i][c.keys['sben']['e2']])
                tilt   = float(c.data[i][c.keys['sben']['tilt']])

                # energy variation
                if scale[i] != 1.0 :
                    pass

                a.AddDipole(name     = prepend+c.name[i]+'_'+str(eCount),
                            category = 'sbend',
                            length   = length,
                            angle    = angle,
                            aper     = aper,
                            k1       = k1,
                            e1       = e1in,
                            e2       = e2in,
                            tilt     = tilt,
                            scaling  = scale[i])

#       ###################################################################
        elif c.type[i] == 'RBEN' :
            length   = float(c.data[i][c.keys['rben']['l']])
            angle    = float(c.data[i][c.keys['rben']['angle']])
            aper     = float(apertures.aper[i])
            k1       = float(c.data[i][c.keys['sben']['k1']])
            e1in     = float(c.data[i][c.keys['rben']['e1']])
            e2in     = float(c.data[i][c.keys['rben']['e2']])
            tilt     = float(c.data[i][c.keys['rben']['tilt']])

            a.AddDipole(name     = prepend+c.name[i]+"_"+str(eCount),
                        category = 'rbend',
                        length   = length,
                        angle    = angle,
                        aper     = aper,
                        k1       = k1,
                        e1       = e1in,
                        e2       = e2in,
                        tilt     = tilt,
                        scaling  = scale[i])
#       ###################################################################
        elif c.type[i] == 'LCAV' :
            length   = float(c.data[i][c.keys['lcav']['l']])
            deltaE   = (float(c.data[i][c.keys['lcav']['E']])-float(c.data[i-1][c.keys['lcav']['E']]))*1000 # MeV #Gives undesirable results if phase=/=0 as is Actual energy change, not wave amplitude.
            volt   = float(c.data[i][c.keys['lcav']['volt']]) #value labelled 'volt' in pymad8 is amplitude of cavity field.
            freq     = float(c.data[i][c.keys['lcav']['freq']])
            lag      = float(c.data[i][c.keys['lcav']['lag']])
            gradient = volt/length

            a.AddRFCavity(name      = prepend+c.name[i]+'_'+str(eCount),
                          length    = length,
                          gradient  = gradient,
                          phase     = lag * 2 * _np.pi,
                          frequency = freq,# * 2 * _np.pi,
                          aper1     = apertures.aper[i])
#       ###################################################################
        elif c.type[i] == 'ECOL' :

            if collimator == None :
                # make collimator from mad8 file
#                print "ECOL> ",c.name[i], "mad8 file"
                print(c.data[i][c.keys['ecol']['xsize']],c.data[i][c.keys['ecol']['ysize']])
                if (c.data[i][c.keys['ecol']['xsize']] != 0) and (c.data[i][c.keys['rcol']['ysize']]) != 0 :
                    a.AddECol(name     = prepend+c.name[i]+'_'+str(eCount),
                              length   = float(c.data[i][c.keys['ecol']['l']]),
                              xsize    = float(c.data[i][c.keys['ecol']['xsize']]),
                              ysize    = float(c.data[i][c.keys['ecol']['ysize']]),
                              material = 'Copper')
                else :
                    a.AddDrift(name    = c.name[i]+'_'+str(eCount),
                               length  = c.data[i][c.keys['ecol']['l']])
            else :
                # make collimator from file
#                print "ECOL> ",c.name[i], "coll file"
                length=float(c.data[i][c.keys['rcol']['l']])
                xsize = float(collimator.getCollimator(c.name[i])['xsize'])
                ysize = float(collimator.getCollimator(c.name[i])['ysize'])
                mater = collimator.getCollimator(c.name[i])['bdsim_material']
                if xsize != 0 and ysize == 0 :
                    ysize = 0.2
                if xsize == 0 and ysize != 0 :
                    xsize = 0.2

                if (xsize != 0 and ysize != 0):
                    a.AddECol(name     = prepend+c.name[i]+'_'+str(eCount),
                              length   = length,
                              xsize    = xsize,
                              ysize    = ysize,
                              material = mater)
#                              bias     = biasList)
                else :
                    a.AddDrift(prepend+c.name[i]+'_'+str(eCount),float(c.data[i][c.keys['ecol']['l']]))
#       ###################################################################
        elif c.type[i] == 'RCOL' :
            if collimator == None :
#               print "RCOL> ",c.name[i], "mad8 file"
                print(c.data[i][c.keys['rcol']['xsize']],c.data[i][c.keys['rcol']['ysize']])
                if (c.data[i][c.keys['rcol']['xsize']] != 0) and (c.data[i][c.keys['rcol']['ysize']]) != 0 :
                    a.AddRCol(name     = prepend+c.name[i]+'_'+str(eCount),
                              length   = float(c.data[i][c.keys['rcol']['l']]),
                              xsize    = float(c.data[i][c.keys['rcol']['xsize']]),
                              ysize    = float(c.data[i][c.keys['rcol']['ysize']]),
                              material = 'Copper')
                else :
                    a.AddDrift(name   = prepend+c.name[i]+'_'+str(eCount),
                               length = c.data[i][c.keys['rcol']['l']])
            else :
                # make collimator from file
#               print "RCOL> ",c.name[i], "coll file"
                length= float(c.data[i][c.keys['rcol']['l']])
                xsize = float(collimator.getCollimator(c.name[i])['xsize'])
                ysize = float(collimator.getCollimator(c.name[i])['ysize'])
                mater = collimator.getCollimator(c.name[i])['bdsim_material']
                if xsize != 0 and ysize == 0 :
                    ysize = 0.2
                if xsize == 0 and ysize != 0 :
                    xsize = 0.2

                if (xsize != 0 and ysize != 0) :
                    a.AddRCol(name     = prepend+c.name[i]+'_'+str(eCount),
                              length   = length,
                              xsize    = xsize,
                              ysize    = ysize,
                              material = mater)
#                              bias     = biasList)
                else :
                    a.AddDrift(name    = prepend+c.name[i]+'_'+str(eCount),
                               length  = float(c.data[i][c.keys['rcol']['l']]))

#       ###################################################################
        elif c.type[i] == 'MATR' :
            #print "RMAT> ",c.name[i]
            if rmat == "":
                raise MAD8ToGMADConversionError("Trying to convert MATR but"
                                                " RMAT tape is missing.")
            rmat.data[i]
            RMATRIX=rmat.data[i]
            RMATPRIOR=rmat.data[i-1]
            length=float(c.data[i][c.keys['matr']['l']])

            #Mad8 rmatrix elements are cumulative, code finds current element by finding difference between rmat [i] and [i-1].
            PRIORMATRIX = _np.matrix(str(RMATPRIOR[0]) + " " + str(RMATPRIOR[1]) + " " + str(RMATPRIOR[2]) + " " + str(RMATPRIOR[3]) + "; " + str(RMATPRIOR[6]) + " " + str(RMATPRIOR[7]) + " " + str(RMATPRIOR[8]) + " " + str(RMATPRIOR[9]) + "; " + str(RMATPRIOR[12]) + " " + str(RMATPRIOR[13]) + " " + str(RMATPRIOR[14]) + " " + str(RMATPRIOR[15]) + "; " + str(RMATPRIOR[18]) + " " + str(RMATPRIOR[19]) + " " + str(RMATPRIOR[20]) + " " + str(RMATPRIOR[21]))
            POSTMATRIX = _np.matrix(str(RMATRIX[0]) + " " + str(RMATRIX[1]) + " " + str(RMATRIX[2]) + " " + str(RMATRIX[3]) + "; " + str(RMATRIX[6]) + " " + str(RMATRIX[7]) + " " + str(RMATRIX[8]) + " " + str(RMATRIX[9]) + "; " + str(RMATRIX[12]) + " " + str(RMATRIX[13]) + " " + str(RMATRIX[14]) + " " + str(RMATRIX[15]) + "; " + str(RMATRIX[18]) + " " + str(RMATRIX[19]) + " " + str(RMATRIX[20]) + " " + str(RMATRIX[21]))
            EFFECTMATRIX=(POSTMATRIX*PRIORMATRIX.I)
            a.AddRmat(name      = prepend+c.name[i]+'_'+str(eCount),
                      length    = float(c.data[i][c.keys['matr']['l']]),
                      r11       = EFFECTMATRIX[0,0],
                      r12       = EFFECTMATRIX[0,1],
                      r13       = EFFECTMATRIX[0,2],
                      r14       = EFFECTMATRIX[0,3],
                      r21       = EFFECTMATRIX[1,0],
                      r22       = EFFECTMATRIX[1,1],
                      r23       = EFFECTMATRIX[1,2],
                      r24       = EFFECTMATRIX[1,3],
                      r31       = EFFECTMATRIX[2,0],
                      r32       = EFFECTMATRIX[2,1],
                      r33       = EFFECTMATRIX[2,2],
                      r34       = EFFECTMATRIX[2,3],
                      r41       = EFFECTMATRIX[3,0],
                      r42       = EFFECTMATRIX[3,1],
                      r43       = EFFECTMATRIX[3,2],
                      r44       = EFFECTMATRIX[3,3])

#       ###################################################################
        else :
            print("UNKN> ",c.type[i])
#       ###################################################################
        nameDict[c.name[i]] += 1

    a.AddSampler(samplers)
    a.Write(outputFileName)

    return a

def Mad8Twiss2Beam(t, istart, particle, energy) :

    betx = t.data[istart][t.keys['betx']]
    bety = t.data[istart][t.keys['bety']]
    alfx = t.data[istart][t.keys['alfx']]
    alfy = t.data[istart][t.keys['alfy']]

    beam = Beam.Beam(particle,energy,'gausstwiss')
    beam._SetBetaX(betx)
    beam._SetBetaY(bety)
    beam._SetAlphaX(alfx)
    beam._SetAlphaY(alfy)

    return beam


def Mad8MakeOptions(inputTwissFile, inputEchoFile) :
    # open mad output
    o = pymad8.Output.OutputReader()
    c, t = o.readFile(inputFileName,'twiss')

    # get initial beam pipe size
    a = c.getApertures(raw=False)
#    a = c.getApertures(raw=True)

    # get values from echo of mad8 output (particle type, beam energy, energy spread)
    echoVals = pymad8.Output.EchoValue(inputEchoFile)
    echoVals.loadValues()

def Mad8MakeApertureTemplate(inputFileName, outputFileName="apertures_template.dat") :
    # open mad output
    o = pymad8.Output.OutputReader()
    c, t = o.readFile(inputFileName,'twiss')
    a = c.getApertures(raw=False)
#    a = c.getApertures(raw=True)

    # write apertures to file
    f = open(outputFileName,"w")

    for i in range(0,len(c.name),1) :
        f.write(c.name[i]+' '+str(a[i])+'\n');
    f.close()

def Mad8MakeCollimatorTemplate(inputFileName,outputFileName="collimator_template.dat") :
    '''
    Read Twiss file and generate template of collimator file
    inputFileName  = "twiss.tape"
    outputFileName = "collimator.dat"
    collimator.dat must be edited to provide types and materials, apertures will be defined from lattice
    '''
    # open mad output
    o = pymad8.Output.OutputReader()
    c, t = o.readFile(inputFileName,'twiss')

    # open collimator output file
    f = open(outputFileName,"w")

    for i in range(0,len(c.name),1) :
        if c.type[i] == 'RCOL' :
            f.write(c.name[i]+"\t"+"TYPE"+"\t"+str(c.data[i][c.keys['rcol']['l']])+"\t"+str(c.data[i][c.keys['rcol']['xsize']])+
                    "\t"+str(c.data[i][c.keys['rcol']['ysize']])+"\t"+"Copper"+"\t"+"GEOM"+"\t"+"SIGMA"+"\n")
        if c.type[i] == 'ECOL' :
            f.write(c.name[i]+"\t"+"TYPE"+"\t"+str(c.data[i][c.keys['ecol']['l']])+"\t"+str(c.data[i][c.keys['ecol']['xsize']])+
                    "\t"+str(c.data[i][c.keys['ecol']['ysize']])+"\t"+"Copper"+"\t"+"GEOM"+"\t"+"SIGMA"+"\n")
    f.close()

class Mad8ApertureDatabase:
    def __init__(self,apertureFileName) :
        self.apertureFileName = apertureFileName
        self.loadApertures(self.apertureFileName)

    def loadApertures(self,fileName) :
        f = open(fileName)
        self.name = []
        self.aper = []
        for l in f :
            t = l.split()
            self.name.append(t[0])
            self.aper.append(float(t[1]))

    def openApertures(self,size = 0.1) :
        for i in range(0,len(self.aper)):
            self.aper[i] = size

class Mad8CollimatorDatabase:
    '''
    Load collimator file into memory and functions to open and manipulate collimator system
    c = Mad8CollimatorDataBase(fileName)
    fileName = "collimator.dat"
    file format
    <name> <type> <length> <x_size/2> <ysize/2> <material> <geom>
    <length> includes the tapers, so entire length along machine
    '''

    def __init__(self,collimatorFileName) :
        self.collimatorFileName = collimatorFileName
        self.loadCollimatorDb(self.collimatorFileName)

    def loadCollimatorDb(self,collimatorFileName) :
        f = open(collimatorFileName)

        inx = 0

        self._coll = OrderedDict()
        self._collNames = []
        for l in f :
            t = l.split()
            name     = t[0]
            type     = t[1]
            length   = float(t[2])
            xsize    = float(t[3])
            ysize    = float(t[4])
            material = t[5]
            geom     = t[6]
            setting = t[7]
            inx = inx + 1

            d = {'index':inx, 'type':type, 'l':length, 'xsize':xsize,
                 'ysize':ysize, 'bdsim_material':material, 'bdsim_geom':geom, 'setting':setting}

            self._coll[name] = d
            self._collNames.append(name)

    def openCollimators(self,openHalfSizeX=0.2, openHalfSizeY=0.2) :
        for c in list(self._coll.keys()) :
            self._coll[c]['xsize'] = openHalfSizeX
            self._coll[c]['ysize'] = openHalfSizeY

    def setCollimator(self,collimator,halfSizeX,halfSizeY) :
        self._coll[collimator]['xsize'] = halfSizeX
        self._coll[collimator]['ysize'] = halfSizeY

    def getCollimators(self) :
#        return self._coll.keys()
        return self._collNames

    def getCollimator(self, name) :
        return self._coll[name]

    def getDict(self) :
        return self._coll

    def __str__(self) :
        s = ''
        for k in self.getCollimators() :
            s += (k+"\t"+self._coll[k]['type']+"\t\t"+str(self._coll[k]['l'])+"\t"+str(self._coll[k]['xsize'])+"\t"+
                  str(self._coll[k]['ysize'])+"\t"+self._coll[k]['bdsim_material']+"\t"+self._coll[k]['bdsim_geom']+
                  "\t"+self._coll[k]['setting']+"\n")
        return s

    def write(self,fileName) :
        f = open(fileName,"w")

        for k in self.getCollimators() :
            f.write(k+"\t"+self._coll[k]['type']+"\t"+str(self._coll[k]['l'])+"\t"+str(self._coll[k]['xsize'])+"\t"+
                    str(self._coll[k]['ysize'])+"\t"+self._coll[k]['bdsim_material']+"\t"+self._coll[k]['bdsim_geom']+
                    "\t"+self._coll[k]['setting']+"\n")


def main() :
    usage = "usage : %prog [inputFileName]"
    parser = _op.OptionParser(usage)
    parser.add_option("-i","--input",  action="store",   type="string",     dest="inputFileName",                           help="Input file name")
    parser.add_option("-o","--ouput",  action="store",   type="string",     dest="outputFileName",default="output",         help="output base file name")
    parser.add_option("-s","--start",  action="store",   type="string",     dest="start",         default="0",              help="starting element (named or index)")
    parser.add_option("-b","--beam",   action="store_true",                 dest="beam",          default=True,             help="generate beam")
    parser.add_option("-x","--emitx",  action="store",   type="float",      dest="gemitx",        default=1e-10,            help="geometric emittance in x")
    parser.add_option("-y","--emity",  action="store",   type="float",      dest="gemity",        default=1e-10,            help="geometric emittance in x")
    parser.add_option("-c","--coll",   action="store",   type="string",     dest="coll",          default="collimator.dat", help="collimator defn file")
    parser.add_option("-a","--sampler",action="store",   type="string",     dest="samplers",      default="all",            help="samplers (all|)")

    (options, args) = parser.parse_args()

    if options.inputFileName == None :
        print("_Mad8Twiss2Gmad> Require input file name")
        parser.print_usage()
        return
    print('_Mad8Twiss2Gmad> inputFileName,outputFileName,start,samplers,beam,gemitx,gemity')
    print('_Mad8Twiss2Gmad>', options.inputFileName,options.outputFileName,options.start,options.samplers,options.beam,options.gemitx,options.gemity)

    # try to decode the start point either value or name
    try :
        options.start = int(options.start)
    except ValueError :
        pass

    Mad8Twiss2Gmad(options.inputFileName, options.outputFileName, options.start, options.beam, (options.gemitx,options.gemity),options.coll,options.samplers)

if __name__ == "__main__":
    main()
