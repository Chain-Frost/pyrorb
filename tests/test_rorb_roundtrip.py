"""Source preservation and typed/canonical RORB round trips (synthetic, no native tools)."""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from runoff_routing.integration import parse_run_bytes
from runoff_routing.project_json import import_rorb_project, load_project, write_project
from runoff_routing.rorb_codec import (
    FormatProblem,
    original_bytes,
    parse_bytes,
    parse_catg,
    parse_cmd_par,
    parse_design_stm,
    read_file,
    serialize_catg,
    serialize_cmd_par,
    serialize_design_stm,
    to_s2_payload,
    write_new,
)
from runoff_routing.rorb_model import (
    CatchmentModel,
    ControlStep,
    LossValue,
    ParameterSet,
    RoutingValue,
    RunModel,
    SubArea,
    from_dict,
    from_json,
    to_dict,
    to_json,
)


def _catg() -> str:
    return (
        "SYNTHETIC CATCHMENT\n"
        "C RORB_GE 002\n"
        "C #NODES\nC 0\nC #REACHES\nC 0\nC #STORAGES\nC 0\n"
        "C #INFLOW/OUTFLOW\nC 0\nC END RORB_GE\n"
        "1\n"
        "1, 5.000, -99, Reach 1 Sub-area A\n"
        "3, Store hydrograph\n"
        "1, 4.000, -99, Reach 2 Sub-area B\n"
        "4, Join stored hydrograph\n"
        "5, 2.500, -99, Reach 3\n"
        "7, PRINT outlet\n"
        "PRINT outlet\n"
        "0\n"
        "C Sub Area Data\n"
        "30.000, 20.000, -99\n"
        "C Impervious Fraction Data\n"
        "0, -99, No impervious area\n"
    )


def _stm() -> str:
    return (
        "SYNTHETIC DESIGN\n"
        "DESIGN\n"
        "C Example comment not a data record\n"
        "0.500D0,200,1,1,1,-99\n"
        "0, 2\n"
        "Temporal pattern (% of depth)\n"
        "60.0,\t40.0,-99.00\n"
        "C Sub-area rainfall depths\n"
        "100.00,90.0,-99\n"
    )


def _params() -> ParameterSet:
    return ParameterSet(
        "subfolder\\model.catg",
        r"C:\storms\design.stm",
        True,
        3,
        1,
        1,
        1,
        (RoutingValue(1, Decimal("12.0"), Decimal("0.8")),),
        (LossValue(1, 1, Decimal(24), Decimal("5.0")),),
    )


def _run() -> RunModel:
    return RunModel(_params(), parse_catg(_catg().encode()).model, parse_design_stm(_stm().encode()).model)


def test_catchment_unchanged_source_preserves_crlf_comments_and_sha256() -> None:
    raw = _catg().replace("\n", "\r\n").encode("cp1252")
    parsed = parse_catg(raw)
    assert original_bytes(parsed) == raw
    assert parsed.source.sha256 == hashlib.sha256(raw).hexdigest()
    assert parsed.source.newline == "crlf"
    assert parsed.graphical_metadata[0] == "SYNTHETIC CATCHMENT"
    assert [item.code for item in parsed.model.controls] == [1, 3, 1, 4, 5, 7]
    assert [item.identifier for item in parsed.model.subareas] == ["area_1", "area_2"]
    assert [item.label for item in parsed.model.subareas] == ["A", "B"]
    assert [item.length_km for item in parsed.model.reaches] == [Decimal(5), Decimal(4), Decimal("2.5")]
    assert any(span.field == "subarea_area_km2" and span.source_text == "30.000" for span in parsed.source_map)
    edited = replace(parsed.model, title="Changed title")
    with pytest.raises(ValueError, match="cannot represent edits"):
        original_bytes(parsed, current_model=edited)


def test_canonical_catg_roundtrip_and_custom_id_rejection() -> None:
    parsed = parse_catg(_catg().encode())
    exported = serialize_catg(parsed.model)
    updated = parse_catg(exported)
    assert updated.model == parsed.model
    assert b"7, PRINT outlet\nPRINT outlet\n0\n" in exported
    assert b"C #NODES\nC 0" in exported
    assert updated.source.newline == "lf"
    custom = replace(parsed.model.subareas[0], identifier="custom")
    changed_control = replace(parsed.model.controls[0], subarea_id="custom")
    noncanonical = replace(
        parsed.model,
        subareas=(custom, *parsed.model.subareas[1:]),
        controls=(changed_control, *parsed.model.controls[1:]),
    )
    with pytest.raises(ValueError, match="ordinal IDs"):
        serialize_catg(noncanonical)


def test_explicit_storm_original_and_canonical_roundtrips() -> None:
    payload = _stm().encode("utf-8")
    parsed = parse_design_stm(payload)
    assert original_bytes(parsed) == payload
    assert parsed.model.timestep_hours == Decimal("0.5")
    assert parsed.model.percentages == (Decimal("60.0"), Decimal("40.0"))
    assert parsed.model.depths_mm == (Decimal("100.00"), Decimal("90.0"))
    assert len([field for field in parsed.source_map if field.field == "rainfall_depth_mm"]) == 2
    assert parse_design_stm(serialize_design_stm(parsed.model)).model == parsed.model


def test_cmd_par_canonical_and_original_bytes_and_paths() -> None:
    params = _params()
    output = serialize_cmd_par(params)
    assert b"Cat file :subfolder\\model.catg" in output
    assert b"Stm file :C:\\storms\\design.stm" in output
    parsed = parse_cmd_par(output.replace(b"\n", b"\r\n"))
    assert parsed.model == params
    assert original_bytes(parsed) == output.replace(b"\n", b"\r\n")
    assert parse_cmd_par(serialize_cmd_par(parsed.model)).model == params
    assert [item.line for item in parsed.source_map] == list(range(2, 11))


@pytest.mark.parametrize("model", [_params(), _run()])
def test_model_json_roundtrip_and_versioned_units(model: ParameterSet | RunModel) -> None:
    payload = to_dict(model)
    restored = from_dict(payload)
    assert restored == model
    assert from_json(to_json(model)) == model
    assert payload["schema_version"] == 1
    assert payload["units"]["area"] == "km2"
    assert isinstance(json.loads(to_json(model))["model"], dict)


def test_individual_catchment_and_storm_json_roundtrip() -> None:
    run = _run()
    for model in (run.catchment, run.storm):
        assert from_json(to_json(model)) == model


@pytest.mark.parametrize("corruption", ["version", "units", "extra", "flag_type", "numeric_type"])
def test_invalid_json_is_not_coerced(corruption: str) -> None:
    edited: dict[str, Any] = to_dict(_params())
    if corruption == "version":
        edited["schema_version"] = 2
    elif corruption == "units":
        edited["units"] = {"area": "m2"}
    elif corruption == "extra":
        edited["unknown"] = "not permitted"
    elif corruption == "flag_type":
        edited["model"]["verbosity"] = True
    else:
        edited["model"]["routing"] = [{"isa": 1, "kc": 12.5, "m": "0.8"}]
    with pytest.raises((TypeError, ValueError)):
        from_dict(edited)


@pytest.mark.parametrize(
    ("source", "extension", "status"),
    [
        (b"GUI saved profile", ".par", "unsupported"),
        (b"legacy combined file", ".dat", "unsupported"),
        (b"legacy text catchment", ".cat", "unsupported"),
        (_stm().replace("DESIGN", "FIT").encode(), ".stm", "unsupported"),
        (_stm().replace("200,1,1,1", "200,2,1,1").encode(), ".stm", "unsupported"),
        (_catg().replace("\n7, PRINT outlet", "\n11, PRINT outlet").encode(), ".catg", "unsupported"),
        (_catg().replace("C #STORAGES\nC 0", "C #STORAGES\nC 1").encode(), ".catg", "unsupported"),
        (_catg().replace("0, -99, No impervious area", "2, -99").encode(), ".catg", "unsupported"),
        (_stm().replace("100.00,90.0,-99", "100.00,90.0").encode(), ".stm", "invalid"),
        (_stm().replace("0, 2", "0, 3").encode(), ".stm", "invalid"),
        (_catg().replace("3, Store hydrograph", "4, Store hydrograph").encode(), ".catg", "invalid"),
        (_catg().replace("30.000, 20.000, -99", "30.000, -99").encode(), ".catg", "invalid"),
        (_catg().replace("7, PRINT outlet", "7, PRINT outlet\nEXTRA").encode(), ".catg", "invalid"),
        (_catg().replace("5, 2.500, -99, Reach 3", "5, 2.500, 100, Reach 3").encode(), ".catg", "invalid"),
        (_stm().replace("60.0,", "NaN,").encode(), ".stm", "invalid"),
        (_stm().replace("60.0,", "1_0.0,").encode(), ".stm", "invalid"),
        (_stm().replace("100.00,90.0,-99", "100.00,-99,90.0").encode(), ".stm", "invalid"),
    ],
)
def test_unrecognised_and_invalid_constructs_fail_explicitly(source: bytes, extension: str, status: str) -> None:
    with pytest.raises(FormatProblem) as caught:
        parse_bytes(source, extension)
    assert caught.value.status == status


def test_duplicate_json_identifiers_and_impossible_controls_rejected() -> None:
    model = _run().catchment
    with pytest.raises(ValueError, match="Duplicate"):
        replace(model, print_locations=(model.print_locations[0], model.print_locations[0]))
    with pytest.raises(ValueError, match=r"Unbalanced|Code 4|Code 3"):
        replace(model, controls=(ControlStep(4), *model.controls))
    with pytest.raises(ValueError, match="positive"):
        replace(model, subareas=(SubArea("area_1", Decimal(0)), *model.subareas[1:]))


def test_s2_boundary_converts_once_and_rejects_unverified_losses() -> None:
    run = _run()
    adapter = to_s2_payload(run)
    assert adapter.controls == ((1, 5.0), (3, 0.0), (1, 4.0), (4, 0.0), (5, 2.5), (7, 0.0))
    assert adapter.areas_km2 == (30.0, 20.0)
    assert adapter.kc == 12.0
    unsupported = replace(run, parameters=replace(run.parameters, loss_model=2))
    with pytest.raises(ValueError, match="IL/CL"):
        to_s2_payload(unsupported)


def test_s2_float_boundary_rejects_nonzero_underflow() -> None:
    run = _run()
    tiny = Decimal("1e-400")
    changed_reach = replace(run.catchment.reaches[0], length_km=tiny)
    changed_catchment = replace(run.catchment, reaches=(changed_reach, *run.catchment.reaches[1:]))
    with pytest.raises(ValueError, match="underflowed"):
        to_s2_payload(replace(run, catchment=changed_catchment))

    changed_loss = replace(run.parameters.losses[0], initial_loss_mm=tiny)
    changed_parameters = replace(run.parameters, losses=(changed_loss,))
    with pytest.raises(ValueError, match="underflowed"):
        to_s2_payload(replace(run, parameters=changed_parameters))


def test_file_adapters_are_read_only_and_no_clobber(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def prohibited(*_args: object, **_kwargs: object) -> None:
        pytest.fail("Parser must never start RORB")

    monkeypatch.setattr(subprocess, "run", prohibited)
    source = tmp_path / "source.catg"
    source.write_bytes(_catg().encode())
    before = source.read_bytes()
    assert isinstance(read_file(source).model, CatchmentModel)
    assert source.read_bytes() == before
    target = tmp_path / "canonical.catg"
    write_new(target, serialize_catg(parse_catg(before).model))
    assert parse_catg(target.read_bytes()).model == parse_catg(before).model
    with pytest.raises(FileExistsError):
        write_new(target, b"no overwriting")
    assert source.read_bytes() == before


def test_stable_model_outside_checkout_requires_no_source_file() -> None:
    payload = to_json(_run())
    assert isinstance(from_json(payload), RunModel)
    assert "original_bytes" not in payload


def test_cp1252_labels_preserve_original_encoding() -> None:
    raw = _catg().replace("PRINT outlet", "PRINT café").encode("cp1252")
    parsed = parse_catg(raw)
    assert parsed.source.encoding == "cp1252"
    assert parsed.model.print_locations[0].label == "PRINT café"
    assert original_bytes(parsed) == raw


def test_code7_physical_location_is_authoritative_not_inline_annotation() -> None:
    source = _catg().replace("7, PRINT outlet\nPRINT outlet", "7, metadata only\nNative outlet")
    parsed = parse_catg(source.encode())
    assert parsed.model.print_locations[0].label == "Native outlet"
    assert any(item.field == "print_location" and item.source_text == "Native outlet" for item in parsed.source_map)
    assert original_bytes(parsed) == source.encode()
    assert parsed.model.controls[-1].label == "metadata only"
    assert b"7, metadata only\nNative outlet\n0\n" in serialize_catg(parsed.model)
    assert parse_catg(serialize_catg(parsed.model)).model == parsed.model


def test_code7_without_its_physical_location_is_invalid() -> None:
    invalid = _catg().replace("7, PRINT outlet\nPRINT outlet\n0", "7, PRINT outlet\n0")
    with pytest.raises(FormatProblem) as caught:
        parse_catg(invalid.encode())
    assert caught.value.status == "invalid"


def test_code7_rejects_ambiguous_zero_even_with_a_second_terminator() -> None:
    ambiguous = _catg().replace("7, PRINT outlet\nPRINT outlet\n0", "7, metadata\n0\n0")
    with pytest.raises(FormatProblem, match="location record distinct"):
        parse_catg(ambiguous.encode("utf-8"))


def test_code7_blank_physical_location_is_not_the_inline_annotation() -> None:
    source = _catg().replace("7, PRINT outlet\nPRINT outlet", "7, metadata only\n    ")
    parsed = parse_catg(source.encode())
    assert parsed.model.print_locations[0].label == ""
    assert parsed.model.controls[-1].label == "metadata only"
    assert b"7, metadata only\n\n0\n" in serialize_catg(parsed.model)
    assert parse_catg(serialize_catg(parsed.model)).model == parsed.model


def _registered_pyromb_originals() -> tuple[bytes, dict[str, Any]]:
    """Both PyRomb cases use one authenticated, unchanged original CATG."""
    root = Path(__file__).parent / "fixtures" / "regression-v1"
    register: dict[str, Any] = json.loads((root / "register.json").read_text(encoding="utf-8"))
    cases = tuple(
        next(item for item in register["cases"] if item["case_id"] == case_id)
        for case_id in ("pyromb-pr2-full", "pyromb-novel-storm")
    )
    files = [next(item for item in case["files"] if item["path"].endswith(".catg")) for case in cases]
    assert files[0] == files[1]
    original = (root / files[0]["path"]).read_bytes()
    assert hashlib.sha256(original).hexdigest() == files[0]["sha256"]
    assert len(original) == files[0]["size_bytes"] == 2913
    assert [case["clock"]["row_count"] for case in cases] == [49, 61]
    return original, register


def test_original_pyromb_645_mode_zero_preserves_code2_impervious_and_graphical_ids() -> None:
    original, _register = _registered_pyromb_originals()
    parsed = parse_catg(original)
    model = parsed.model
    assert parsed.dialect == "rorb_ge_645"
    assert model.reach_mode == "explicit_reach_types"
    assert original_bytes(parsed) == original
    assert len(model.subareas) == 6
    assert len(model.reaches) == 7
    assert [step.code for step in model.controls] == [1, 3, 1, 4, 2, 3, 1, 2, 4, 5, 2, 7]
    assert [step.subarea_id for step in model.controls if step.code in (1, 2)] == [
        f"area_{index}" for index in range(1, 7)
    ]
    assert tuple(area.impervious_fraction for area in model.subareas) == (
        Decimal(0),
        Decimal("0.50000"),
        Decimal("0.20000"),
        Decimal(0),
        Decimal(0),
        Decimal(0),
    )
    assert [s.source_text for s in parsed.source_map if s.field == "graphical_node_id"] == [
        str(index) for index in range(1, 9)
    ]
    assert [s.source_text for s in parsed.source_map if s.field == "graphical_reach_id"] == [
        str(index) for index in range(1, 8)
    ]
    assert model.print_locations[0].label == ""
    assert from_json(to_json(model)) == model
    assert parse_bytes(original, ".cat").model == model
    assert parse_bytes(original, ".catg").model == model
    with pytest.raises(ValueError, match="No verified canonical CATG writer"):
        serialize_catg(model)


@pytest.mark.parametrize(
    ("before", "after", "status"),
    [
        ("C RORB_GE 6.45", "C RORB_GE 6.46", "unsupported"),
        ("C RORB_GE 6.45", "C RORB_GE 6.45\\nC RORB_GE 6.45", "unsupported"),
        ("C #NODES", "C #UNKNOWN SECTION\\nC 0\\nC #NODES", "unsupported"),
        ("C #FILE COMMENTS", "C #FILE COMMENTS\\nC 0\\nC #FILE COMMENTS", "unsupported"),
        ("C #STORAGES\\nC      0", "C #STORAGES\\nC      1", "unsupported"),
        ("C #INFLOW/OUTFLOW\\nC      0", "C #INFLOW/OUTFLOW\\nC      1", "unsupported"),
        ("C #BACKGROUND IMAGE\\nC  T  F", "C #BACKGROUND IMAGE\\nC  T  T", "unsupported"),
        ("C END RORB_GE", "C END RORB_GE\\nC END RORB_GE", "invalid"),
    ],
)
def test_pyromb_graphical_rejects_unrecognised_sections_without_source_mutation(
    before: str, after: str, status: str
) -> None:
    original, _register = _registered_pyromb_originals()
    text = original.decode("utf-8").replace("\r\n", "\n")
    edited = text.replace(before.replace("\\n", "\n"), after.replace("\\n", "\n"))
    assert text != edited
    with pytest.raises(FormatProblem) as caught:
        parse_catg(edited.encode("utf-8"))
    assert caught.value.status == status


@pytest.mark.parametrize(
    ("before", "after", "status"),
    [
        ("\\n0\\n1,1,0.112,-99", "\\n1\\n1,1,0.112,-99", "unsupported"),
        ("1,1,0.112,-99", "1,2,0.112,0.001,-99", "unsupported"),
        ("1,1,0.112,-99", "1,1,0,-99", "invalid"),
        ("1,1,0.112,-99", "1,1,-0.112,-99", "invalid"),
        ("1,1,0.112,-99", "1,1,0.112,NOT_TERMINATED", "invalid"),
        ("C Impervious Fraction Data\\n 1 ,", "C Impervious Fraction Data\\n 2 ,", "invalid"),
        ("C Impervious Fraction Data\\n 1 ,", "C Impervious Fraction Data\\n 1, 0.0", "invalid"),
        ("      0.00000,      0.50000,", "      0.00000,      1.50000,", "invalid"),
        ("      0.00000,      0.50000,", "      0.00000,      -0.50000,", "invalid"),
        ("C      8         92.500", "C      9         92.500", "invalid"),
    ],
)
def test_pyromb_pr16_source_rejects_invalid_control_and_fraction_records(before: str, after: str, status: str) -> None:
    original, _register = _registered_pyromb_originals()
    text = original.decode("utf-8").replace("\r\n", "\n")
    edited = text.replace(before.replace("\\n", "\n"), after.replace("\\n", "\n"))
    assert edited != text
    with pytest.raises(FormatProblem) as caught:
        parse_catg(edited.encode())
    assert caught.value.status == status


def test_pyromb_pr16_original_source_rejects_unqualified_reach_type_and_unsafe_flags() -> None:
    source, _register = _registered_pyromb_originals()
    text = source.decode("utf-8").replace("\r\n", "\n")
    cases = (
        ("C #STORAGES\\nC      0", "C #STORAGES\\nC      1"),
        ("C #INFLOW/OUTFLOW\\nC      0", "C #INFLOW/OUTFLOW\\nC      1"),
        ("C      8         92.500", "C      8         92.500"),  # unchanged control checked below
    )
    for before, after in cases[:2]:
        edited = text.replace(before.replace("\\n", "\n"), after.replace("\\n", "\n"))
        assert edited != text
        with pytest.raises(FormatProblem):
            parse_catg(edited.encode())
    # An unknown per-node extra output is a source *capability rejection*,
    # never a new printed-hydrograph column accepted from raw graphics alone.
    graph_node = next(line for line in text.splitlines() if line.strip().startswith("C      8 "))
    assert graph_node.split()[-3:] == ["70", "0", "0"]
    modified = graph_node.replace("70  0  0", "71  0  0")
    assert modified != graph_node
    with pytest.raises(FormatProblem) as caught:
        parse_catg(text.replace(graph_node, modified).encode())
    assert caught.value.status == "unsupported"


def test_pyromb_pr16_typed_stack_rejects_genuine_invalid_running_state() -> None:
    source, _register = _registered_pyromb_originals()
    model = parse_catg(source).model
    controls = list(model.controls)
    code2_index = next(index for index, step in enumerate(controls) if step.code == 2)
    controls[code2_index] = replace(controls[code2_index], subarea_id="area_1")
    with pytest.raises(ValueError, match="Code 2"):
        replace(model, controls=tuple(controls))
    controls = list(model.controls)
    controls[0] = replace(controls[0], code=2)
    with pytest.raises(ValueError, match="needs a running hydrograph"):
        replace(model, controls=tuple(controls))
    with pytest.raises(ValueError, match="unity"):
        replace(model, subareas=(replace(model.subareas[0], impervious_fraction=Decimal("1.01")), *model.subareas[1:]))


@pytest.mark.parametrize("suffix", [".catg", ".cat"])
def test_pyromb_pr16_graphical_cat_suffix_loads_through_real_project_import(tmp_path: Path, suffix: str) -> None:
    original, register = _registered_pyromb_originals()
    root = Path(__file__).parent / "fixtures" / "regression-v1"
    historical = next(item for item in register["cases"] if item["case_id"] == "pyromb-pr2-full")
    record = next(item for item in historical["files"] if item["path"].endswith(".par"))
    params = (root / record["path"]).read_bytes()
    assert hashlib.sha256(params).hexdigest() == record["sha256"]
    # Synthetic percent-based storm used solely to exercise the current
    # legacy project entry point independently of #94's temporal-weight work.
    storm = (
        b"synthetic six-source storm\nDESIGN\n0.25,48,1,1,1,-99\n0,2\n"
        b"Temporal pattern (% of depth)\n40,60,-99\nC Sub-area rainfall depths\n40,40,40,40,40,40,-99\n"
    )
    source_cat = tmp_path / f"original{suffix}"
    source_cat.write_bytes(original)
    p = tmp_path / "original.par"
    p.write_bytes(params)
    s = tmp_path / "synthetic.stm"
    s.write_bytes(storm)
    parsed = parse_run_bytes(params, original, storm).model
    assert parsed.catchment.reach_mode == "explicit_reach_types"
    assert from_json(to_json(parsed)) == parsed
    project_file = tmp_path / "pr16-cat-project.json"
    project = import_rorb_project(
        project_file,
        identifier="pr16-cat-source-test",
        rainfall_profile="legacy-rorb",
        parameters=p,
        catchment=source_cat,
        storm=s,
    )
    write_project(project_file, project)
    loaded = load_project(project_file)
    assert loaded.run == parsed
    assert loaded.file_hashes[1][1] == hashlib.sha256(original).hexdigest()
    # S2 must not silently map nonzero fractions/code 2 to a pervious run.
    with pytest.raises(ValueError, match="control code 2"):
        to_s2_payload(parsed)
