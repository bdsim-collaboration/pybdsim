from . import Data
import numpy as np
import json
import re

try:
    import ROOT as _ROOT
except ImportError:
    _useRoot = False
    pass

class RootEventAnalyser :
    def __init__(self):
        self.event = None
        self._persistent_data = {}

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

    def get_persistent_data(self):
        return self._persistent_data

    def add_persistent_data(self, key, value):
        self._persistent_data[key] = value

    def write_persistent_data(self, filename):
        # recursively search for arrays and convert to lists
        data_list = convert_data_to_lists(self._persistent_data)

        with open(filename, "w") as f:
            json_str = json.dumps(data_list, indent=2)
            #json_str_compact = compact_lists(json_str)
            f.write(json_str)

def convert_data_to_lists(data):
    if isinstance(data, dict):
        return {k: convert_data_to_lists(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_data_to_lists(v) for v in data]
    elif isinstance(data, tuple):
        return tuple(convert_data_to_lists(v) for v in data)
    elif isinstance(data, np.ndarray):
        return data.tolist()
    elif isinstance(data, np.generic):
        # numpy scalars (e.g. np.int64, np.float32) -> native Python
        return data.item()
    else:
        return data

def compact_lists(json_str):
    # Collapse arrays that were split across multiple lines back onto one line
    pattern = re.compile(r'\[\s*((?:[^\[\]]|\n)*?)\s*\](?![^\[]*\])', re.MULTILINE)

    def collapse(match):
        content = match.group(1)
        items = [item.strip() for item in content.split(',')]
        return '[' + ', '.join(items) + ']'

    # Repeat until no more nested arrays get collapsed (handles nested lists)
    prev = None
    while prev != json_str:
        prev = json_str
        json_str = pattern.sub(collapse, json_str)
    return json_str

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
