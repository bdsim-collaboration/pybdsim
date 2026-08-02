from . import Output as _Output
import warnings


def MakeTrackFiles(savelineFileName, line, outputFileNameStub):
    sl  = _Output.Saveline(savelineFileName, line)
    sl.removeDuplicates()
    sl.writeRenamed(outputFileNameStub+"_renamed.mad8")

    observeElements = []
    observeIndex    = [] 
    for e in sl.expandedLineRenamed:
        d = sl.findRenamedNamedDict(e) 
        if d['type'] != 'DRIFT':
            observeElements.append(e)
            observeIndex.append(sl.expandedLineRenamed.index(e))

    MakeObserveFile(observeElements, outputFileNameStub+"_observe.mad8")
    MakeTableArchiveFile(observeElements, outputFileNameStub+"_archive.mad8")
    MakeTableMapFile(observeElements, observeIndex, outputFileNameStub+"_trackFileMap.mad8")
    MakeInraysFile(bdsimOutput, outputFileNameStub+"_inrays.mad8")
    MakeTrackCallingFile(outputFileNameStub)


def MakeTrackCallingFile(fileNameStub):
    pass


def MakeTableMapFile(observeElements, observeIndex, filename):
    f = open(filename, 'w')
    
    for i in range(0, len(observeElements)):
        f.write(str(observeIndex[i])+' '+observeElements[i]+'\n')

    f.close()


def MakeObserveFile(elementlist, filename):
    f = open(filename, 'w')
    for e in elementlist:
        ws = 'OBSERVE, PLACE="'+e+'", TABLE="'+e+'"\n'
        f.write(ws)
    f.close()


def MakeTableArchiveFile(elementlist, filename):
    f = open(filename, 'w')
    for e in elementlist:
        ws = 'ARCHIVE, TABLE="'+e+'", FILENAME="./track/'+e+'"\n'
        f.write(ws)
    f.close()
