import pymadx as _pymadx
import pybdsim as _pybdsim

def CompareMadxAndBDSIM(tfsfile,bdssurveyfile):
    if type(tfsfile) == str:
        print 'Loading file using pymadx'
        madx   = _pymadx.Tfs(input)
    else:
        print 'Already a pymadx instance - proceeding'
        madx   = input

    if type(bdssurveyfile) == str:
        print 'Loading file using pybdsim'
        bdsf   = _pybdsim.Data.Load(bdssurveyfile)
    else:
        print 'Already a pymadx instance - proceeding'
        bdsf   = bdssurveyfile


    bx = bdsf.X()
    bz = bdsf.Z()

