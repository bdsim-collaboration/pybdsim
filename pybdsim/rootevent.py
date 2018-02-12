import ROOT
import collections
import numpy as np

if ROOT.gSystem.Load("librebdsimLib") == -1:
    raise ImportError("Cannot find librebdsimLib root library.")

# These must be hardcoded, I think, as C++ has no reflection.
# These are per component variables.
_COMPONENT_VARS = frozenset({"componentName",
                             "placementName",
                             "componentType",
                             "length",
                             "staPos",
                             "midPos",
                             "endPos",
                             "staRot",
                             "midRot",
                             "endRot",
                             "staRefPos",
                             "midRefPos",
                             "endRefPos",
                             "staRefRot",
                             "midRefRot",
                             "endRefRot",
                             "staS",
                             "midS",
                             "endS",
                             "beamPipeType",
                             "beamPipeAper1",
                             "beamPipeAper2",
                             "beamPipeAper3",
                             "beamPipeAper4"})

# These are variables which are not per component.
_MISC_VARIABLES = frozenset({"samplerNamesUnique"})

class AxisAngle(collections.namedtuple("AxisAngle", ["axis",
                                                     "angle"])):

    def __eq__(self, other):
        return (all((self.axis == other.axis))
                and self.angle == other.angle)

    def __ne__(self, other):
        return not (self == other)

class Component(collections.namedtuple("Component",
                                       _COMPONENT_VARS | {"index"})):
    """Simple class for representing a component read out of the
    BDSOutputROOTEventModel tree from BDSIM rootevent output.

    """
    # Default repr would be too big so redefine to something
    # human-readable and useful:
    def __repr__(self):
        return "<{}: {}, S={}m ...>".format(self.componentName,
                                            self.componentType,
                                            self.staS)

class Model(list):
    """Simple class used for inspecting BDSIM rootevent models."""
    def __init__(self, path):
        # Load the ROOT model
        data_loader = ROOT.DataLoader(path)
        model = data_loader.GetModel()
        model_tree = data_loader.GetModelTree()
        model_tree.GetEntry(0)
        model = model.model

        # Add the miscellaneous variables.
        for variable in _MISC_VARIABLES:
            sequence = list(getattr(model, variable))
            setattr(self, variable, sequence)

        # Give the model a copy of the component variables for convenience.
        self.component_variables = _COMPONENT_VARS

        # Add the per component variables.
        for index, _ in enumerate(model.componentName):
            component_vars = {variable:
                              _try_coercion(getattr(model, variable)[index])
                              for variable in _COMPONENT_VARS}
            self.append(Component(index=index, **component_vars))
        self.smax = self[-1].endS

    def get_component_column(self, variable):
        """Returns a list of all the component's attribute according
        to the variable provided."""
        return [getattr(component, variable) for component in self]

    def __repr__(self):
        return "<Model: {} components; length = {}m>".format(len(self),
                                                               self.smax)

    def index_from_s(self, s):
        """
        index_from_s(S)

        return the index of the beamline element which CONTAINS the
        position S.

        Note:  For small values beyond smax, the index returned will
        be -1 (i.e. the last element).

        """
        if s > self.smax or s < 0.0:
            raise ValueError("S is out of bounds.")

        for i, element in enumerate(self):
            sLow = element.staS
            sHigh = element.endS
            if (s >= sLow and s < sHigh):
                return i

    def position_from_s(self, s):
        """Return the global coordinate position of the position at S."""
        index = self.index_from_s(self)
        if (self[index].staRot != self[index].endRot
            or self[index].staRot != self[index].midRot):
            raise ValueError("Element at S is not straight!")

        # Get fractional position along the length of the element.
        start_s = self[index].staS
        end_s = self[index].endS
        fraction = (s - start_s) / (end_s - start_s)

        # Get start and end of element in global coordsto construct
        # the unit vector.
        start_pos = self[index].staPos
        end_pos = self[index].endPos
        direction = end_pos - start_pos

        return start_pos + fraction * direction

    def indices_between_s(self, s_start, s_end):
        start_index = self.index_from_s(s_start)
        end_index = self.index_from_s(s_end)
        return range(start_index, end_index + 1)

    def variable_between_s(self, variable, s_start, s_end):
        return [getattr(self[i], variable)
                for i in self.indices_between_s(s_start, s_end)]

    def element_from_s(self, s):
        return self[self.index_from_s(s)]

def _coerce_tvector3(tvector):
    return np.array([tvector.X(), tvector.Y(), tvector.Z()])

def _coerce_trotation(trotation):
    angle = ROOT.Double()
    axis = ROOT.TVector3()
    trotation.AngleAxis(angle, axis)
    axis = _coerce_tvector3(axis)
    angle = float(angle)
    return AxisAngle(axis, angle)

def _try_coercion(var):
    try:
        return _coerce_trotation(var)
    except AttributeError:
        pass
    try:
        return _coerce_tvector3(var)
    except AttributeError:
        return var
