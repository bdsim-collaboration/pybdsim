"""Sampler commands must follow selection of the named sequence."""

import pytest

from pybdsim.Builder import Machine
from pybdsim.Writer import Writer


@pytest.mark.parametrize("mode", ["separate", "singlefile", "mixed"])
@pytest.mark.parametrize("sampler_count", [1, 10, 11])
def test_use_precedes_samplers(tmp_path, mode, sampler_count):
    machine = Machine(sequenceName="three_elements")
    for name in ("D1", "Q1", "D2"):
        machine.AddDrift(name, 1.0)
    machine.AddSampler(["Q1"] * sampler_count)

    writer = Writer()
    if mode == "mixed":
        writer.Sequence.WriteInMain()

    output = tmp_path / "model.gmad"
    writer.WriteMachine(machine, str(output), singlefile=(mode == "singlefile"),
                        sequence_name="three_elements", verbose=False)
    gmad = output.read_text()

    sequence = ("include model_sequence.gmad;" if mode == "separate"
                else "three_elements: line = (three_elements_l0);")
    sampler = ("include model_samplers.gmad;"
               if sampler_count > 10 and mode != "singlefile"
               else "sample, range=Q1;")
    assert gmad.index(sequence) < gmad.index("use, three_elements;") < gmad.index(sampler)
    assert gmad.count("use, three_elements;") == 1

    sampler_file = tmp_path / "model_samplers.gmad"
    if sampler_count > 10 and mode != "singlefile":
        assert gmad.count("include model_samplers.gmad;") == 1
        assert "sample," not in gmad
        assert sampler_file.read_text().count("sample, range=Q1;") == sampler_count
    else:
        assert not sampler_file.exists()
        assert gmad.count("sample, range=Q1;") == sampler_count


@pytest.mark.parametrize("singlefile", [False, True])
def test_no_samplers_written_when_none_requested(tmp_path, singlefile):
    machine = Machine(sequenceName="three_elements")
    machine.AddDrift("D1", 1.0)

    output = tmp_path / "model.gmad"
    Writer().WriteMachine(machine, str(output), singlefile=singlefile,
                          sequence_name="three_elements", verbose=False)

    assert "sample," not in output.read_text()
    assert not (tmp_path / "model_samplers.gmad").exists()


def test_sampler_commands_preserve_all_range_and_options(tmp_path):
    machine = Machine(sequenceName="three_elements")
    machine.AddDrift("Q1", 1.0)
    machine.AddSampler("all")
    machine.AddSampler({"Q1": {"opt": "val"}})

    output = tmp_path / "model.gmad"
    Writer().WriteMachine(machine, str(output), sequence_name="three_elements",
                          verbose=False)

    commands = [line for line in output.read_text().splitlines()
                if line.startswith("sample,")]
    assert commands == ["sample, all;", "sample, range=Q1, opt=val;"]
