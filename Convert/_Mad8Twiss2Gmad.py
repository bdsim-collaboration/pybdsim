#!/usr/bin/env python2.6

import numpy as _np
import optparse as _op

import pymad8
import Builder
import Beam

def Mad8Twiss2Gmad(inputFileName, outputFileName, istart = 0, beam=True, gemit=(1e-10,1e-10), collimator=None, samplers='all') :         

    # open mad output
    o = pymad8.Mad8.OutputReader()
    c, t = o.readFile(inputFileName,'twiss')

    # check type of start 
    # if string find element number
    if type(istart) == str : 
        print "Mad8Twiss2Gmad> finding start : ",istart 
        istart = c.findByName(istart)[0]
        print "Mad8Twiss2Gmad> using index   : ",istart
        
    # load Collimator db or use instance
    if type(collimator) == str : 
        collimator = Mad8CollimatorDatabase(collimator) 

    # create machine instance 
    a = Builder.Machine()    

    # create beam 
    if beam : 
        E = c.data[istart][c.keys['drif']['E']] 
        b = Mad8Twiss2Beam(t,istart,"e-",E)
        b.SetEmittanceX(gemit[0],'m')
        b.SetEmittanceY(gemit[1],'m')
        a.AddBeam(b)

    # iterate through objects and build machine 
    for i in range(istart,len(c.name),1) : 
# unique(c.type)
# ['', 'BLMO', 'DRIF', 'ECOL', 'HKIC', 'IMON', 'INST', 'LCAV', 'MARK',
#       'MATR', 'MONI', 'PROF', 'QUAD', 'RCOL', 'SBEN', 'SOLE', 'VKIC',
#       'WIRE']

        # print element
#        print i,c.name[i],c.type[i]

        if c.type[i] == '' : 
            a.AddMarker(c.name[i])
        elif c.type[i] == 'DRIF' : 
            a.AddDrift(c.name[i],length=c.data[i][c.keys['drif']['l']])
        elif c.type[i] == 'MARK' : 
            a.AddMarker(c.name[i]) 
        elif c.type[i] == 'SOLE' : 
            a.AddMarker(c.name[i])
        elif c.type[i] == 'INST' : 
            a.AddMarker(c.name[i]) 
        elif c.type[i] == 'MONI' : 
            a.AddMarker(c.name[i])
        elif c.type[i] == 'IMON' :
            a.AddMarker(c.name[i])
        elif c.type[i] == 'BLMO' : 
            a.AddMarker(c.name[i])
        elif c.type[i] == 'WIRE' :
            a.AddMarker(c.name[i])
        elif c.type[i] == 'QUAD' : 
            if c.data[i][c.keys['quad']['l']] < 1e-7 : 
                a.AddMarker(c.name[i])
            else : 
                a.AddQuadrupole(c.name[i],
                                k1     = c.data[i][c.keys['quad']['k1']],
                                length = c.data[i][c.keys['quad']['l']],
                                tilt   = c.data[i][c.keys['quad']['tilt']])
        elif c.type[i] == 'HKIC' : 
            a.AddDrift(c.name[i],length=c.data[i][c.keys['hkic']['l']])
        elif c.type[i] == 'VKIC' : 
            a.AddDrift(c.name[i],length=c.data[i][c.keys['vkic']['l']])
        elif c.type[i] == 'SBEN' : 
            if c.data[i][c.keys['sben']['l']] < 1e-7 : 
                a.AddMarker(c.name[i])
            else : 
                a.AddDipole(c.name[i],'sbend',
                            length=c.data[i][c.keys['sben']['l']], 
                            angle =c.data[i][c.keys['sben']['angle']])
        elif c.type[i] == 'LCAV' : 
            length   = c.data[i][c.keys['rfcavity']['l']]
            deltaE   = (c.data[i][c.keys['rfcavity']['E']]-c.data[i-1][c.keys['rfcavity']['E']])*1000 # MeV 
            gradient = deltaE/length
            a.AddRFCavity(c.name[i],length=length, gradient=-gradient)            
        elif c.type[i] == 'ECOL' : 
            if collimator == None : 
                if (c.data[i][c.keys['rcol']['xsize']] != 0) and (c.data[i][c.keys['rcol']['ysize']]) != 0 : 
                    a.AddECol(c.name[i], 
                              length  = c.data[i][c.keys['rcol']['l']], 
                              xsize   = c.data[i][c.keys['rcol']['xsize']], 
                              ysize   = c.data[i][c.keys['rcol']['ysize']],
                              material= 'Copper')                    
                else : 
                    a.AddMarker(c.name[i])
            else : 
                # make collimator from file
                if (c.data[i][c.keys['rcol']['xsize']] != 0) and (c.data[i][c.keys['rcol']['ysize']]) != 0 : 
                    a.AddECol(c.name[i], 
                              length  = c.data[i][c.keys['rcol']['l']], 
                              xsize   = collimator.GetCollimator(c.name[i])['xsize'], 
                              ysize   = collimator.GetCollimator(c.name[i])['ysize'],
                              material= collimator.GetCollimator(c.name[i])['bdsim_material'])                  
                else : 
                    a.AddMarker(c.name[i])

        elif c.type[i] == 'RCOL' : 
            if collimator == None : 
                if (c.data[i][c.keys['rcol']['xsize']] != 0) and (c.data[i][c.keys['rcol']['ysize']]) != 0 : 
                    a.AddRCol(c.name[i], 
                              length  = c.data[i][c.keys['rcol']['l']], 
                              xsize   = c.data[i][c.keys['rcol']['xsize']], 
                              ysize   = c.data[i][c.keys['rcol']['ysize']],
                              material= 'Copper')            
                else : 
                    a.AddMarker(c.name[i])
            else : 
                # make collimator from file
                if (c.data[i][c.keys['rcol']['xsize']] != 0) and (c.data[i][c.keys['rcol']['ysize']]) != 0 : 
                    a.AddRCol(c.name[i], 
                              length  = c.data[i][c.keys['rcol']['l']], 
                              xsize   = collimator.GetCollimator(c.name[i])['xsize'], 
                              ysize   = collimator.GetCollimator(c.name[i])['ysize'],
                              material= collimator.GetCollimator(c.name[i])['bdsim_material'])           
                else : 
                    a.AddMarker(c.name[i])
    a.AddSampler(samplers)
    a.WriteLattice(outputFileName)

def Mad8Twiss2Beam(t, istart, particle, energy) :            
    
    betx = t.data[istart][t.keys['betx']]
    bety = t.data[istart][t.keys['bety']]
    alfx = t.data[istart][t.keys['alfx']]
    alfy = t.data[istart][t.keys['alfy']]

    beam = Beam.Beam(particle,energy,'gausstwiss')
    beam.SetBetaX(betx)
    beam.SetBetaY(bety)
    beam.SetAlphaX(alfx)
    beam.SetAlphaY(alfy)
    
    return beam

def Mad8MakeCollimatorTemplate(inputFileName,outputFileName) : 
    '''
    Read Twiss file and generate template of collimator file 
    inputFileName  = "twiss.tape"
    outputFileName = "collimator.dat"
    collimator.dat must be edited to provide types and materials, apertures will be defined from lattice   
    '''
    pass


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
        self.LoadCollimatorDb(self.collimatorFileName) 
        
    def LoadCollimatorDb(self,collimatorFileName) : 
        f = open(collimatorFileName) 

        inx = 0 

        self._coll = {}
        for l in f : 
            t = l.split()
            name     = t[0]
            type     = t[1]
            length   = float(t[2])
            xsize    = float(t[3])
            ysize    = float(t[4]) 
            material = t[5]
            geom     = t[6]
            inx = inx + 1 

            d = {'index':inx, 'type':type, 'l':length, 'xsize':xsize,
                 'ysize':ysize, 'bdsim_material':material, 'bdsim_geom':geom}

            self._coll[name] = d     
        
    def OpenCollimators(self,openHalfSizeX=0.1, openHalfSizeY=0.1) : 
        for c in self._coll.keys() :
            self._coll[c]['xsize'] = openHalfSizeX
            self._coll[c]['ysize'] = openHalfSizeY
    
    def GetCollimators(self) : 
        return self._coll.keys()

    def GetCollimator(self, name) : 
        return self._coll[name]

    def GetDict(self) : 
        return self._coll
        
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
        print "_Mad8Twiss2Gmad> Require input file name"
        parser.print_usage()
        return 
    print '_Mad8Twiss2Gmad> inputFileName,outputFileName,start,samplers,beam,gemitx,gemity'
    print '_Mad8Twiss2Gmad>', options.inputFileName,options.outputFileName,options.start,options.samplers,options.beam,options.gemitx,options.gemity
    
    # try to decode the start point either value or name
    try :
        options.start = int(options.start) 
    except ValueError : 
        pass 
    
    Mad8Twiss2Gmad(options.inputFileName, options.outputFileName, options.start, options.beam, (options.gemitx,options.gemity),options.coll,options.samplers)
    
if __name__ == "__main__":
    main()
