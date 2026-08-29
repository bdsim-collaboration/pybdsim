from . import Data
import ROOT as _ROOT

class RootEventAnalyser :
    def __init__(self):
        self.event = None

    def init(self):
        pass

    def set_event(self, event):
        self.event = event

    def process(self):
        pass

    def terminate(self):
        pass

    def plot(self):
        pass

class RootEventAnalysis:
    def __init__(self, f):
        self.nFilesAnalysed = 0
        self.nEventAnalysed = 0

        self.filenames = []
        self.files = []

        if type(f) == str:
            self.filenames.append(f)
        elif type(f) == _ROOT.DataLoader :
            self.files.append(f)
        elif type(f) == list :
            self.filenames.extend(f)

        for f in self.filenames :
            self.files.append(_ROOT.DataLoader(f))

    def analysis(self, rootEventAnalyser = RootEventAnalyser()):

        rootEventAnalyser.init()

        # loop over files
        for f in self.files :

            # set the event data structure
            rootEventAnalyser.set_event(f.GetEvent())

            # event tree
            et = f.GetEventTree()

            # loop over events
            for ievt in range(0,et.GetEntries(),1) :

                # get event record
                et.GetEntry(ievt)

                # process event
                rootEventAnalyser.process()

                self.nEventAnalysed += 1

            # increment file count
            self.nFilesAnalysed += 1

        rootEventAnalyser.terminate()
        print(f"Analysed {self.nFilesAnalysed} files with {self.nEventAnalysed} events.")
