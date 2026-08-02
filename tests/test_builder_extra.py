import pytest

import pybdsim
from pybdsim.Builder import (
    EvaluateLength,
    _scale_element_parameters_by_length,
    Drift,
    Element,
    ElementBase,
    ElementModifier,
    GmadObject,
    Aperture,
    Atom,
    BLM,
    CavityModel,
    Crystal,
    Field,
    Material,
    Modulator,
    NewColour,
    Placement,
    Query,
    Region,
    SamplerPlacement,
    Scorer,
    ScorerMesh,
    Tunnel,
    XSecBias,
    Sampler,
    SBend,
    Machine,
    bdsimcategories,
)


def test_elementbase_string_and_aperture_handling():
    elem = ElementBase("e1")

    elem["label"] = "text"
    elem["quoted"] = '"already_quoted"'
    elem["aperX"] = 1e-7  # below threshold, should be ignored
    elem["aper1"] = 1e-3  # kept

    assert elem["label"] == '"text"'
    assert elem["quoted"] == '"already_quoted"'
    assert "aperX" not in elem._store
    assert elem["aper1"] == 1e-3


def test_element_split_requires_length():
    marker = pybdsim.Builder.Marker("m1")
    with pytest.raises(TypeError):
        marker.split([0.1])


def test_element_division_splits_evenly():
    drift = Drift("d1", 1.0)
    parts = drift / 2
    lengths = [p["l"] for p in parts]
    names = [p.name for p in parts]
    assert lengths == [0.5, 0.5]
    assert names == ["d1_split_0", "d1_split_1"]


def test_element_division_invalid_type():
    drift = Drift("d1", 1.0)
    with pytest.raises(TypeError):
        _ = drift / "not-an-int"


def test_element_split_not_available_on_base_class():
    element = Element("e1", "thinrmatrix", l=1.0)
    with pytest.raises(TypeError):
        element.split([0.5])


def test_element_from_element_appends_category():
    category_name = "customtestelement"
    if category_name in bdsimcategories:
        bdsimcategories.remove(category_name)
    new_element = Element.from_element(category_name, name="base", l=0.2)
    assert category_name in bdsimcategories
    assert new_element.category == category_name
    assert new_element["l"] == 0.2


def test_evaluate_length_supports_units():
    assert EvaluateLength(1.5) == 1.5
    assert EvaluateLength((2.0, "m")) == 2.0
    assert EvaluateLength((300.0, "mm")) == 0.3
    assert EvaluateLength((4000.0, "um")) == 0.004


def test_scale_element_parameters_by_length():
    e1 = Drift("d1", 1.0)
    e2 = Drift("d2", 2.0)
    parameters = [("hkick", 3.0)]
    _scale_element_parameters_by_length(parameters, [e1, e2], 3.0)
    assert e1["hkick"] == pytest.approx(1.0)
    assert e2["hkick"] == pytest.approx(2.0)


def test_dipole_split_copies_edges_and_clears_interior():
    bend = SBend(
        "sb",
        3.0,
        angle=0.3,
        e1=0.1,
        e2=0.2,
        fint=0.01,
        fintx=0.02,
        h1=0.11,
        h2=0.22,
    )
    parts = bend.split([1.0, 2.0])
    assert [p["l"] for p in parts] == [1.0, 1.0, 1.0]
    assert parts[0]["angle"] == pytest.approx(0.1)
    assert parts[2]["angle"] == pytest.approx(0.1)
    assert "fint" in parts[0] and "fintx" in parts[2]
    assert "h1" in parts[0] and "h2" in parts[2]
    assert "fint" not in parts[1]
    assert "h1" not in parts[1]


def test_machine_append_type_validation():
    machine = Machine()
    with pytest.raises(TypeError):
        machine.Append("not-an-element")  # type: ignore[arg-type]


def test_machine_replace_with_element_updates_length_and_lenint():
    machine = Machine()
    machine.AddDrift("d1", 1.0)
    machine.AddDrift("d2", 1.0)
    new = Drift("d1", 2.0)
    machine.ReplaceWithElement("d1", new)
    assert machine.length == pytest.approx(2.0 + 1.0)
    assert machine.lenint[0] == pytest.approx(2.0)
    assert machine.elements["d1"] is new


def test_machine_replace_element_category_and_updates():
    machine = Machine()
    machine.AddDrift("d1", 1.0)
    machine.AddDrift("d2", 1.0)
    machine.ReplaceElementCategory("drift", "gap")
    assert all(e.category == "gap" for e in machine.elements.values())


def test_machine_update_elements_and_category_and_global():
    machine = Machine()
    machine.AddQuadrupole("q1", 1.0, 0.1)
    machine.AddQuadrupole("q2", 1.0, 0.2)
    machine.UpdateElements(["q1"], "k1", 0.5)
    assert machine.elements["q1"]["k1"] == 0.5
    machine.UpdateElements("q", "k1", 0.7, namelocation="start")
    assert machine.elements["q1"]["k1"] == 0.7
    assert machine.elements["q2"]["k1"] == 0.7
    machine.UpdateCategoryParameter("quadrupole", "k1", 0.9)
    assert machine.elements["q1"]["k1"] == 0.9
    machine.UpdateGlobalParameter("l", 2.0)
    assert machine.elements["q1"]["l"] == 2.0
    assert machine.elements["q2"]["l"] == 2.0


def test_machine_update_elements_invalid_location():
    machine = Machine()
    machine.AddQuadrupole("qa", 1.0, 0.1)
    with pytest.raises(ValueError):
        machine.UpdateElements("qa", "k1", 0.2, namelocation="middle")


def test_machine_insert_with_after_and_substitute_and_string_lookup():
    machine = Machine()
    machine.AddDrift("d1", 1.0)
    machine.AddDrift("d2", 1.0)
    new = Drift("insert", 0.5)
    machine.Insert(new, index="d1", after=True)
    assert machine.sequence == ["d1", "insert", "d2"]
    # substitute existing name
    replacement = Drift("insert", 0.25)
    machine.Insert(replacement, index=1, substitute=True)
    assert machine.elements["insert"]["l"] == 0.25
    # insert by referencing existing string
    machine.Insert("d1", index=0)
    assert machine.sequence[0] == "d1"


def test_machine_insert_errors():
    machine = Machine()
    machine.AddDrift("d1", 1.0)
    with pytest.raises(ValueError):
        machine.Insert(Drift("d2", 0.5), index=5)
    with pytest.raises(ValueError):
        machine.Insert("missing", index=0)


def test_machine_insert_and_replace_splits_and_recomputes_lenint():
    machine = Machine()
    # Use Drift instances directly so split is available (Element instances cannot be split)
    machine.Append(Drift("d0", 1.0))
    machine.Append(Drift("d1", 1.0))
    new = Drift("mid", 0.5)
    machine.InsertAndReplace(new, sLocation=1.0)
    assert pytest.approx(machine.lenint[-1]) == 2.0
    assert any("mid" in name for name in machine.sequence)


def test_machine_add_sampler_with_dict_and_list():
    machine = Machine()
    machine.AddDrift("d1", 1.0)
    machine.AddDrift("d2", 1.0)
    machine.AddSampler({"d1": {"opt": "v1"}, "d2": {"opt": "v2"}})
    assert len(machine.samplers) == 2
    machine.AddSampler(["d1", "d2"])
    assert len(machine.samplers) == 4


def test_machine_add_sampler_first_last_and_invalid():
    machine = Machine()
    machine.AddDrift("d1", 0.5)
    machine.AddDrift("d2", 0.5)
    machine.AddSampler("first")
    machine.AddSampler("last")
    assert [repr(s).strip() for s in machine.samplers] == [
        "sample, range=d1;",
        "sample, range=d2;",
    ]
    with pytest.raises(ValueError):
        machine.AddSampler("not-in-sequence")


def test_machine_add_dipole_validation():
    machine = Machine()
    with pytest.raises(ValueError):
        machine.AddDipole(category="wrong")
    with pytest.raises(TypeError):
        machine.AddDipole(angle=None, b=None)


def test_machine_add_dipole_with_b_field_sets_angle_from_brho_zero():
    machine = Machine()
    machine.AddDipole(name="db", category="sbend", length=1.0, b=0.0)
    assert "db" in machine.elements


def test_machine_add_beam_type_check():
    machine = Machine()
    with pytest.raises(TypeError):
        machine.AddBeam(beam="not-a-beam")  # type: ignore[arg-type]


def test_gmadobject_repr_with_tuple_and_list():
    obj = GmadObject("testobject", "custom", a=(1.0, "m"), b=[1, 2, 3], c="val")
    text = repr(obj)
    assert "a=1.0*m" in text
    assert "b={1,2,3}" in text
    assert 'c="val"' in text


def test_material_and_add_material_list_and_invalid():
    m1 = Material("mat1", density=(1.0, "g/cm3"))
    machine = Machine()
    machine.AddMaterial([m1])
    assert m1 in machine.material
    with pytest.raises(TypeError):
        machine.AddMaterial(123)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "cls,objecttype",
    [
        (Aperture, "aperture"),
        (Atom, "atom"),
        (BLM, "blm"),
        (CavityModel, "cavitymodel"),
        (Crystal, "crystal"),
        (Field, "field"),
        (Material, "matdef"),
        (Modulator, "modulator"),
        (NewColour, "newcolour"),
        (Placement, "placement"),
        (Query, "query"),
        (Region, "region"),
        (SamplerPlacement, "samplerplacement"),
        (Scorer, "scorer"),
        (ScorerMesh, "scorermesh"),
        (Tunnel, "tunnel"),
        (XSecBias, "xsecBias"),
    ],
)
def test_gmadobject_subclasses_init_and_repr(cls, objecttype):
    obj = cls("name", a=(1.0, "m"), values=[1, 2])
    text = repr(obj)
    assert objecttype in text
    assert "a=1.0*m" in text


def test_sampler_repr_all_and_range():
    assert repr(Sampler("all")).strip() == "sample, all;"
    assert repr(Sampler("RANGE", options={"opt": "val"})).strip() == 'sample, range=RANGE, opt=val;'


def test_element_modifier_updates_repr():
    base = Element("q1", "quadrupole", l=1.0, k1=0.1)
    mod = ElementModifier("q1", k1=0.2)
    assert "k1=0.2" in repr(mod)
