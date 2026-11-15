"""Issue #119: public JSON-project / selected-engine explicit-event MVP controls."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path

import pytest

from runoff_routing.engine_execution import run_engine_project
from runoff_routing.engine_types import EngineSelection
from runoff_routing.integration import canonical_run_bytes
from runoff_routing.project_batch import (
    ProjectEvent,
    iter_project_events,
    load_event_request,
    main,
    run_project_events,
    write_batch_results,
)
from runoff_routing.project_json import (
    EmbeddedRun,
    Project,
    import_rorb_project,
    write_project,
)
from runoff_routing.rorb_model import RunModel, from_json

EXAMPLE = Path(__file__).parents[1] / "examples" / "synthetic-run.json"


def _model() -> RunModel:
    model = from_json(EXAMPLE.read_text(encoding="utf-8"))
    assert isinstance(model, RunModel)
    return model


def _project(root: Path, engine: EngineSelection | None = None) -> Path:
    path = root / "project.json"
    write_project(
        path,
        Project("mvp_example", "explicit", EmbeddedRun(_model()), engine=engine or EngineSelection()),
    )
    return path


def _original_project(root: Path) -> Path:
    root.mkdir()
    model = _model()
    paths = [root / name for name in ("model.par", "model.catg", "model.stm")]
    for path, contents in zip(paths, canonical_run_bytes(model), strict=True):
        path.write_bytes(contents)
    project_path = root / "original-project.json"
    original = import_rorb_project(
        project_path,
        identifier="original_mvp",
        rainfall_profile="legacy-rorb",
        parameters=paths[0],
        catchment=paths[1],
        storm=paths[2],
    )
    write_project(project_path, original)
    return project_path


@pytest.mark.parametrize("engine", ["python", "python-cmd"])
def test_single_and_batch_use_the_same_selected_numerical_engine(tmp_path: Path, engine: str) -> None:
    selection = EngineSelection.for_engine(engine)
    project = _project(tmp_path)
    single = run_engine_project(project, selection=selection)
    result = run_project_events(project, (ProjectEvent("single"),), selection=selection)
    assert single.status == "computed_unvalidated"
    assert result.succeeded
    batch = result.outcomes[0]
    assert batch.event_id == "single"
    assert batch.effective_selection == single.effective_selection == selection
    assert batch.model_sha256 == single.model_sha256
    assert batch.hydrographs == single.hydrographs
    assert batch.physical_time_hours == single.physical_time_hours
    assert batch.python_diagnostics == single.python_diagnostics
    assert batch.implementation_revision == single.implementation_revision


@pytest.mark.parametrize("engine", ["python", "python-cmd"])
def test_order_repeat_and_intervening_bad_event_do_not_change_results(tmp_path: Path, engine: str) -> None:
    project = _project(tmp_path)
    selected = EngineSelection.for_engine(engine)
    base = ProjectEvent("base")
    wet = ProjectEvent("wet", storm={"depths_mm": ["25.0"]}, losses={"continuing": "0.3"})
    invalid = ProjectEvent("broken", storm={"calculation_increments": 1})
    records = run_project_events(project, (base, wet, invalid, base, wet), selection=selected)
    assert [r.event_id for r in records.outcomes] == ["base", "wet", "broken", "base", "wet"]
    assert [r.status for r in records.outcomes] == [
        "computed_unvalidated", "computed_unvalidated", "invalid_input",
        "invalid_input", "invalid_input",
    ]
    assert records.outcomes[3].diagnostics[0].code == "duplicate_event_id"
    assert records.outcomes[4].diagnostics[0].code == "duplicate_event_id"
    other = run_project_events(project, (wet, invalid, base), selection=selected)
    assert [r.status for r in other.outcomes] == [
        "computed_unvalidated", "invalid_input", "computed_unvalidated",
    ]
    assert other.outcomes[0].hydrographs == records.outcomes[1].hydrographs
    assert other.outcomes[2].hydrographs == records.outcomes[0].hydrographs
    assert other.outcomes[0].model_sha256 == records.outcomes[1].model_sha256
    assert other.outcomes[2].model_sha256 == records.outcomes[0].model_sha256
    assert tuple(iter_project_events(project, (wet, invalid, base), selection=selected)) == other.outcomes


def test_original_rorb_and_equivalent_embedded_json_execute_identically(tmp_path: Path) -> None:
    original = _original_project(tmp_path / "original")
    embedded = _project(tmp_path)
    selected = EngineSelection.for_engine("python-cmd")
    input_event = (ProjectEvent("verified"),)
    a = run_project_events(original, input_event, selection=selected).outcomes[0]
    b = run_project_events(embedded, input_event, selection=selected).outcomes[0]
    assert a.status == b.status == "computed_unvalidated"
    assert a.model_sha256 == b.model_sha256
    assert a.hydrographs == b.hydrographs
    assert a.physical_time_hours == b.physical_time_hours
    assert len(a.source_file_hashes) == 3
    assert b.source_file_hashes == ()
    assert a.project_sha256 != b.project_sha256


def test_invalid_and_unsupported_events_remain_in_full_reports(tmp_path: Path) -> None:
    project = _project(tmp_path, EngineSelection.for_engine("python-cmd"))
    inputs: tuple[object, ...] = (
        ProjectEvent("good"),
        ProjectEvent("unsupported", storm={"subarea_ids": ["other"]}),
        ProjectEvent("invalid", losses={"initial_loss_mm": 123}),
        {"event_id": "bad_fields", "unrecognised": "fail"},
        {"event_id": "good"},
        {"storm": {"depths_mm": ["9"]}},
        "not-an-event",
    )
    report = run_project_events(project, inputs)
    assert len(report.outcomes) == len(inputs)
    assert [item.status for item in report.outcomes] == [
        "computed_unvalidated", "unsupported_feature", "invalid_input",
        "invalid_input", "invalid_input", "invalid_input", "invalid_input",
    ]
    assert report.outcomes[4].diagnostics[0].code == "duplicate_event_id"
    assert report.outcomes[5].event_id == "<request:6>"
    assert report.outcomes[6].event_id == "<request:7>"
    assert not report.succeeded
    json_output = json.loads(report.to_json())
    assert json_output["requested_event_count"] == len(inputs)
    assert len(json_output["outcomes"]) == len(inputs)
    assert len(json_output["volumes"]) == 1
    assert json_output["volumes"][0]["native_inclusive_reported_volume_m3"] is None
    assert json_output["volumes"][0]["physical_trapezoidal_volume_m3"] is not None
    rows = list(csv.DictReader(io.StringIO(report.to_csv())))
    assert len(rows) == len(report.outcomes[0].physical_time_hours) + len(inputs) - 1
    assert sum(row["status"] == "invalid_input" for row in rows) == 5
    assert all(row["native_inclusive_reported_volume_m3"] == "" for row in rows)
    assert rows[0]["physical_trapezoidal_volume_m3"]


def test_event_request_json_and_cli_report_all_requested_failures(tmp_path: Path) -> None:
    project = _project(tmp_path)
    request_path = tmp_path / "events.json"
    request_path.write_text(
        json.dumps({
            "format": "python-runoff-routing-explicit-events",
            "schema_version": 1,
            "events": [
                {"event_id": "original"},
                {"event_id": "wet", "storm": {"depths_mm": ["40"]}},
                {"event_id": "bad", "storm": {"calculation_increments": -1}},
                {"event_id": "wet"},
            ],
        }),
        encoding="utf-8",
    )
    assert len(load_event_request(request_path)) == 4
    prefix = tmp_path / "computed"
    assert main([str(project), str(prefix), "--events", str(request_path), "--engine", "python-cmd"]) == 2
    report = json.loads(Path(f"{prefix}.json").read_text(encoding="utf-8"))
    assert report["requested_event_count"] == 4
    assert report["completed_event_count"] == 2
    assert [item["status"] for item in report["outcomes"]] == [
        "computed_unvalidated", "computed_unvalidated", "invalid_input", "invalid_input",
    ]
    assert all(item["effective_selection"]["engine"] == "python-cmd" for item in report["outcomes"])
    assert Path(f"{prefix}.csv").exists()
    assert "bad: invalid_input" in Path(f"{prefix}.txt").read_text(encoding="utf-8")
    assert Path(f"{prefix}.json").read_text(encoding="utf-8").endswith("\n")


def test_no_clobber_and_malformed_configuration_fail_without_artefacts(tmp_path: Path) -> None:
    project = _project(tmp_path)
    output = tmp_path / "existing"
    existing = Path(f"{output}.csv")
    existing.write_bytes(b"preserve")
    assert main([str(project), str(output)]) == 2
    assert existing.read_bytes() == b"preserve"
    assert not Path(f"{output}.json").exists()
    bad_request = tmp_path / "invalid.json"
    bad_request.write_text(
        '{"format":"python-runoff-routing-explicit-events","schema_version":1,'
        '"events":[{"event_id":"a","event_id":"b"}]}',
        encoding="utf-8",
    )
    fresh = tmp_path / "fresh"
    assert main([str(project), str(fresh), "--events", str(bad_request)]) == 2
    assert not any(Path(f"{fresh}{ext}").exists() for ext in (".json", ".csv", ".txt"))
    assert main([str(project), str(fresh), "--numerical-profile", "cmd-6.44"]) == 2
    assert not Path(f"{fresh}.json").exists()


def test_default_one_event_cli_creates_three_complete_outputs(tmp_path: Path) -> None:
    project = _project(tmp_path)
    prefix = tmp_path / "single"
    assert main([str(project), str(prefix)]) == 0
    report = json.loads(Path(f"{prefix}.json").read_text(encoding="utf-8"))
    assert report["requested_event_count"] == 1
    outcome = report["outcomes"][0]
    assert outcome["event_id"] == "mvp_example"
    assert outcome["effective_selection"]["engine"] == "python"
    rows = list(csv.DictReader(io.StringIO(Path(f"{prefix}.csv").read_text(encoding="utf-8"))))
    assert len(rows) == 6
    assert [int(row["sample_index"]) for row in rows] == list(range(6))
    assert all(row["print_id"] == "print_1" for row in rows)
    assert rows[0]["physical_time_hours"] == "0.0"
    assert rows[-1]["physical_time_hours"] == "2.5"


def test_selected_native_fails_explicitly_without_using_python(tmp_path: Path) -> None:
    project = _project(tmp_path)
    native = EngineSelection.for_engine("rorb-cmd")
    report = run_project_events(
        project,
        (ProjectEvent("original"), ProjectEvent("modified", storm={"depths_mm": ["99"]})),
        selection=native,
    )
    assert [item.status for item in report.outcomes] == ["unavailable_engine", "unsupported_feature"]
    assert [item.diagnostics[0].code for item in report.outcomes] == [
        "native_config_required", "native_event_override",
    ]
    assert all(item.effective_selection.engine == "rorb-cmd" and not item.hydrographs for item in report.outcomes)


@pytest.mark.parametrize(
    "case_id",
    ["review-design-baseline", "review-ensemble-tp1", "timestep-design-baseline-f2"],
)
def test_real_public_original_cmd_inputs_match_single_and_batch(tmp_path: Path, case_id: str) -> None:
    """Original retained inputs, not generated RORB substitutes or cached solver output."""
    root = Path(__file__).parents[0] / "fixtures" / "regression-v1"
    register = json.loads((root / "register.json").read_text(encoding="utf-8"))
    case = next(item for item in register["cases"] if item["case_id"] == case_id)
    originals: dict[str, Path] = {}
    for source in case["files"]:
        location = root / source["path"]
        suffix = location.suffix
        if suffix not in (".par", ".catg", ".stm"):
            continue
        destination = tmp_path / f"original{suffix}"
        destination.write_bytes(location.read_bytes())
        originals[suffix] = destination
    assert set(originals) == {".par", ".catg", ".stm"}
    project = tmp_path / "original-project.json"
    imported = import_rorb_project(
        project,
        identifier="original_cmd",
        rainfall_profile="legacy-rorb",
        parameters=originals[".par"],
        catchment=originals[".catg"],
        storm=originals[".stm"],
    )
    write_project(project, imported)
    selection = EngineSelection.for_engine("python-cmd")
    single = run_engine_project(project, selection=selection)
    combined = run_project_events(
        project,
        (ProjectEvent("original"), ProjectEvent("after", storm={"depths_mm": ["invalid"]}), ProjectEvent("again")),
        selection=selection,
    )
    assert single.status == "computed_unvalidated"
    assert [item.status for item in combined.outcomes] == [
        "computed_unvalidated", "invalid_input", "computed_unvalidated",
    ]
    assert combined.outcomes[0].hydrographs == single.hydrographs == combined.outcomes[2].hydrographs
    assert combined.outcomes[0].physical_time_hours == single.physical_time_hours
    assert len(single.hydrographs[0].discharge_m3_s) == case["clock"]["row_count"]


def test_batch_file_writer_is_exclusive_and_tracked(tmp_path: Path) -> None:
    project = _project(tmp_path)
    report = run_project_events(project, (ProjectEvent("event"),))
    prefix = tmp_path / "batch"
    created = write_batch_results(prefix, report)
    assert tuple(item.suffix for item in created) == (".json", ".csv", ".txt")
    before = tuple(hashlib.sha256(item.read_bytes()).hexdigest() for item in created)
    with pytest.raises(ValueError, match="already exist"):
        write_batch_results(prefix, report)
    assert before == tuple(hashlib.sha256(item.read_bytes()).hexdigest() for item in created)
