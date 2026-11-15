"""Issue #119: public JSON-project / selected-engine explicit-event MVP controls."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path

import pytest

from runoff_routing import project_batch
from runoff_routing.engine_execution import run_engine_project
from runoff_routing.engine_types import EngineSelection
from runoff_routing.integration import canonical_run_bytes, read_run_files
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
    LoadedProject,
    Project,
    import_rorb_project,
    load_project,
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
        "computed_unvalidated",
        "computed_unvalidated",
        "invalid_input",
        "invalid_input",
        "invalid_input",
    ]
    assert records.outcomes[3].diagnostics[0].code == "duplicate_event_id"
    assert records.outcomes[4].diagnostics[0].code == "duplicate_event_id"
    other = run_project_events(project, (wet, invalid, base), selection=selected)
    assert [r.status for r in other.outcomes] == [
        "computed_unvalidated",
        "invalid_input",
        "computed_unvalidated",
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
        "computed_unvalidated",
        "unsupported_feature",
        "invalid_input",
        "invalid_input",
        "invalid_input",
        "invalid_input",
        "invalid_input",
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
        json.dumps(
            {
                "format": "python-runoff-routing-explicit-events",
                "schema_version": 1,
                "events": [
                    {"event_id": "original"},
                    {"event_id": "wet", "storm": {"depths_mm": ["40"]}},
                    {"event_id": "bad", "storm": {"calculation_increments": -1}},
                    {"event_id": "wet"},
                ],
            }
        ),
        encoding="utf-8",
    )
    assert len(load_event_request(request_path)) == 4
    prefix = tmp_path / "computed"
    assert main([str(project), str(prefix), "--events", str(request_path), "--engine", "python-cmd"]) == 2
    report = json.loads(Path(f"{prefix}.json").read_text(encoding="utf-8"))
    assert report["requested_event_count"] == 4
    assert report["completed_event_count"] == 2
    assert [item["status"] for item in report["outcomes"]] == [
        "computed_unvalidated",
        "computed_unvalidated",
        "invalid_input",
        "invalid_input",
    ]
    assert all(item["effective_selection"]["engine"] == "python-cmd" for item in report["outcomes"])
    assert Path(f"{prefix}.csv").exists()
    assert "bad: invalid_input" in Path(f"{prefix}.txt").read_text(encoding="utf-8")
    assert Path(f"{prefix}.json").read_text(encoding="utf-8").endswith("\n")


@pytest.mark.parametrize("engine", ["python", "python-cmd"])
def test_decimal_overflow_is_an_event_failure_not_a_batch_abort(tmp_path: Path, engine: str) -> None:
    """Codex P2: malformed decimal arithmetic must not lose adjacent results."""
    project = _project(tmp_path)
    selection = EngineSelection.for_engine(engine)
    requests: tuple[object, ...] = (
        ProjectEvent("before"),
        ProjectEvent("overflow", storm={"percentages": ["1e999999999"]}),
        ProjectEvent("after"),
    )
    report = run_project_events(project, requests, selection=selection)
    assert [item.status for item in report.outcomes] == [
        "computed_unvalidated",
        "invalid_input",
        "computed_unvalidated",
    ]
    assert report.outcomes[1].diagnostics[0].code == "storm_model"
    assert not report.outcomes[1].hydrographs
    assert report.outcomes[0].hydrographs == report.outcomes[2].hydrographs
    assert report.outcomes[0].python_diagnostics == report.outcomes[2].python_diagnostics
    assert not report.succeeded

    request_file = tmp_path / f"overflow-{engine}.json"
    request_file.write_text(
        json.dumps(
            {
                "format": "python-runoff-routing-explicit-events",
                "schema_version": 1,
                "events": [
                    {"event_id": "before"},
                    {"event_id": "overflow", "storm": {"percentages": ["1e999999999"]}},
                    {"event_id": "after"},
                ],
            }
        ),
        encoding="utf-8",
    )
    prefix = tmp_path / f"overflow-{engine}-out"
    assert main([str(project), str(prefix), "--events", str(request_file), "--engine", engine]) == 2
    payload = json.loads(Path(f"{prefix}.json").read_text(encoding="utf-8"))
    assert payload["requested_event_count"] == 3
    assert payload["completed_event_count"] == 2
    assert [item["status"] for item in payload["outcomes"]] == [
        "computed_unvalidated",
        "invalid_input",
        "computed_unvalidated",
    ]
    assert payload["outcomes"][1]["diagnostics"][0]["code"] == "storm_model"
    assert payload["outcomes"][1]["hydrographs"] == []
    assert payload["outcomes"][0]["hydrographs"] == payload["outcomes"][2]["hydrographs"]
    csv_rows = list(csv.DictReader(io.StringIO(Path(f"{prefix}.csv").read_text(encoding="utf-8"))))
    assert sum(row["event_id"] == "overflow" for row in csv_rows) == 1
    summary = Path(f"{prefix}.txt").read_text(encoding="utf-8")
    assert "overflow: invalid_input" in summary


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
    assert outcome["effective_selection"]["engine"] == "python-cmd"
    assert outcome["stored_selection"]["engine"] == "python-cmd"
    assert outcome["effective_selection"]["numerical_profile"] == "cmd-6.44"
    rows = list(csv.DictReader(io.StringIO(Path(f"{prefix}.csv").read_text(encoding="utf-8"))))
    assert len(rows) == 6
    assert [int(row["sample_index"]) for row in rows] == list(range(6))
    assert all(row["print_id"] == "print_1" for row in rows)
    assert float(rows[0]["physical_time_hours"]) == 0.0
    assert float(rows[-1]["physical_time_hours"]) == 2.5


def test_selected_native_fails_explicitly_without_using_python(tmp_path: Path) -> None:
    project = _project(tmp_path)
    native = EngineSelection.for_engine("rorb-cmd")
    report = run_project_events(
        project,
        (ProjectEvent("original"), ProjectEvent("modified", storm={"depths_mm": ["99"]})),
        selection=native,
    )
    assert [item.status for item in report.outcomes] == ["unavailable_engine", "unavailable_engine"]
    assert [item.diagnostics[0].code for item in report.outcomes] == [
        "native_config_required",
        "native_config_required",
    ]
    assert all(item.effective_selection.engine == "rorb-cmd" and not item.hydrographs for item in report.outcomes)


@pytest.mark.parametrize(
    "case_id",
    [
        "review-design-baseline",
        "review-ensemble-tp1",
        "timestep-design-baseline-f2",
        "timestep-ensemble-tp3-f4",
        "zero-loss-ensemble-tp9-f1",
    ],
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
        "computed_unvalidated",
        "invalid_input",
        "computed_unvalidated",
    ]
    assert combined.outcomes[0].hydrographs == single.hydrographs == combined.outcomes[2].hydrographs
    assert combined.outcomes[0].physical_time_hours == single.physical_time_hours
    assert len(single.hydrographs[0].discharge_m3_s) == case["clock"]["row_count"]
    assert single.effective_selection == selection
    assert single.hydrographs[0].print_id == case["sites"][0]["model_print_id"]
    assert len(single.physical_time_hours) == case["clock"]["row_count"]
    assert single.physical_time_hours[0] == "0.00000" or float(single.physical_time_hours[0]) == 0.0
    assert all(item.status != "native_execution_failed" for item in combined.outcomes)
    baseline = combined.outcomes[0]
    assert baseline.model_sha256 == single.model_sha256
    assert baseline.hydrographs[0].discharge_m3_s == single.hydrographs[0].discharge_m3_s
    report_json = json.loads(combined.to_json())
    assert report_json["requested_event_count"] == 3
    assert len(report_json["outcomes"]) == 3
    assert report_json["volumes"][0]["physical_trapezoidal_volume_m3"] is not None
    assert report_json["volumes"][0]["native_inclusive_reported_volume_m3"] is None
    rows = list(csv.DictReader(io.StringIO(combined.to_csv())))
    assert len(rows) == 2 * case["clock"]["row_count"] + 1
    assert rows[0]["event_id"] == "original"
    assert rows[-1]["event_id"] == "again"
    assert rows[case["clock"]["row_count"]]["status"] == "invalid_input"
    assert all(row["engine"] == "python-cmd" for row in rows)
    assert max(float(row["discharge_m3_s"]) for row in rows if row["discharge_m3_s"]) == max(
        single.hydrographs[0].discharge_m3_s
    )
    target_json = tmp_path / "embedded-project.json"
    write_project(
        target_json,
        Project("embedded_cmd", "legacy-rorb", EmbeddedRun(load_project(project).run), engine=selection),
    )
    equivalent = run_project_events(target_json, (ProjectEvent("equivalent"),)).outcomes[0]
    assert equivalent.hydrographs == single.hydrographs
    assert equivalent.physical_time_hours == single.physical_time_hours

    # Exercise the actual installed-wheel-capable CLI entry point for EVERY
    # pinned original case; the batch API alone does not check file I/O/exit.
    requests_path = tmp_path / "original-events.json"
    requests_path.write_text(
        json.dumps(
            {
                "format": "python-runoff-routing-explicit-events",
                "schema_version": 1,
                "events": [
                    {"event_id": "original"},
                    {"event_id": "after", "storm": {"depths_mm": ["invalid"]}},
                    {"event_id": "again"},
                ],
            }
        ),
        encoding="utf-8",
    )
    report_prefix = tmp_path / "original-cli"
    assert main([str(project), str(report_prefix), "--events", str(requests_path), "--engine", "python-cmd"]) == 2
    cli_payload = json.loads(Path(f"{report_prefix}.json").read_text(encoding="utf-8"))
    assert cli_payload["requested_event_count"] == 3
    assert cli_payload["completed_event_count"] == 2
    assert [item["status"] for item in cli_payload["outcomes"]] == [
        "computed_unvalidated",
        "invalid_input",
        "computed_unvalidated",
    ]
    assert [item["event_id"] for item in cli_payload["outcomes"]] == ["original", "after", "again"]
    assert cli_payload["outcomes"][0]["hydrographs"] == cli_payload["outcomes"][2]["hydrographs"]
    assert cli_payload["outcomes"][0]["source_file_hashes"] == [list(pair) for pair in single.source_file_hashes]
    assert cli_payload["outcomes"][0]["effective_selection"]["engine"] == "python-cmd"
    assert cli_payload["outcomes"][0]["physical_time_hours"] == list(single.physical_time_hours)
    cli_rows = list(csv.DictReader(io.StringIO(Path(f"{report_prefix}.csv").read_text(encoding="utf-8"))))
    assert len(cli_rows) == 2 * case["clock"]["row_count"] + 1
    original_rows = [row for row in cli_rows if row["event_id"] == "original"]
    assert len(original_rows) == case["clock"]["row_count"]
    assert tuple(float(row["discharge_m3_s"]) for row in original_rows) == single.hydrographs[0].discharge_m3_s
    assert all(row["print_id"] == case["sites"][0]["model_print_id"] for row in original_rows)
    assert [int(row["sample_index"]) for row in original_rows] == list(range(case["clock"]["row_count"]))
    assert all(row["engine"] == "python-cmd" for row in original_rows)
    assert sum(row["event_id"] == "after" for row in cli_rows) == 1
    assert "after: invalid_input" in Path(f"{report_prefix}.txt").read_text(encoding="utf-8")


def _registered_original_files(root: Path, case_id: str) -> dict[str, Path]:
    """Locate immutable original published sources by maintained case ID."""
    register = json.loads((root / "register.json").read_text(encoding="utf-8"))
    case = next(item for item in register["cases"] if item["case_id"] == case_id)
    return {
        Path(source["path"]).suffix: root / source["path"]
        for source in case["files"]
        if Path(source["path"]).suffix in (".par", ".catg", ".stm")
    }


@pytest.mark.parametrize("engine", ["python", "python-cmd"])
def test_cached_preparation_once_per_invariant_model_and_fresh_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, engine: str
) -> None:
    """Every distinct geometry/routing signature is prepared once, never every storm."""
    project = _project(tmp_path)
    selected = EngineSelection.for_engine(engine)
    calls: list[str] = []
    if engine == "python":
        prepare_once = project_batch.prepare_run_model

        def count_python_preparation(model: RunModel) -> object:
            calls.append(str(model.parameters.routing[0].kc))
            return prepare_once(model)

        monkeypatch.setattr("runoff_routing.project_batch.prepare_run_model", count_python_preparation)
    else:
        prepare_once_cmd = project_batch.prepare_cmd_model

        def count_cmd_preparation(model: LoadedProject) -> object:
            calls.append("cmd")
            return prepare_once_cmd(model)

        monkeypatch.setattr("runoff_routing.project_batch.prepare_cmd_model", count_cmd_preparation)

    events = (
        ProjectEvent("first"),
        ProjectEvent("wet", storm={"depths_mm": ["25.0"]}),
        ProjectEvent("invalid", storm={"calculation_increments": -1}),
        ProjectEvent("different_kc", routing={"kc": "0.8"}),
        ProjectEvent("another_wet", storm={"depths_mm": ["30.0"]}),
        ProjectEvent("last"),
    )
    result = run_project_events(project, events, selection=selected)
    assert [item.status for item in result.outcomes] == [
        "computed_unvalidated",
        "computed_unvalidated",
        "invalid_input",
        "computed_unvalidated",
        "computed_unvalidated",
        "computed_unvalidated",
    ]
    assert len(calls) == 2  # original + changed kc; subsequent original events hit original cache
    assert result.outcomes[0].hydrographs == result.outcomes[-1].hydrographs
    assert result.outcomes[0].model_sha256 == result.outcomes[-1].model_sha256
    assert result.outcomes[3].model_sha256 != result.outcomes[0].model_sha256
    assert not result.outcomes[2].hydrographs


def test_five_authentic_cmd_seed_cases_and_four_event_isolation_with_cli(tmp_path: Path) -> None:
    """The TP1 source is reconstructed via explicit typed storm+kc, not a second CATG parse per event."""
    root = Path(__file__).parent / "fixtures" / "regression-v1"
    baseline_paths = _registered_original_files(root, "review-design-baseline")
    tp1_paths = _registered_original_files(root, "review-ensemble-tp1")
    baseline = read_run_files(baseline_paths[".par"], baseline_paths[".catg"], baseline_paths[".stm"]).model
    tp1 = read_run_files(tp1_paths[".par"], tp1_paths[".catg"], tp1_paths[".stm"]).model
    assert baseline.catchment == tp1.catchment
    project = tmp_path / "baseline.json"
    write_project(
        project,
        Project(
            "cmd_original_seed",
            "legacy-rorb",
            EmbeddedRun(baseline),
            engine=EngineSelection.for_engine("python-cmd"),
        ),
    )
    tp1_event = ProjectEvent(
        "review-ensemble-tp1",
        storm={
            "title": tp1.storm.title,
            "timestep_hours": str(tp1.storm.timestep_hours),
            "calculation_increments": tp1.storm.calculation_increments,
            "start_increment": tp1.storm.start_increment,
            "percentages": [str(item) for item in tp1.storm.percentages],
            "depths_mm": [str(item) for item in tp1.storm.depths_mm],
        },
        routing={"kc": str(tp1.parameters.routing[0].kc)},
    )
    requests: tuple[object, ...] = (
        ProjectEvent("review-design-baseline"),
        tp1_event,
        {"event_id": "mvp-invalid-control", "controls": [{"code": 99}]},
        ProjectEvent("baseline-repeat"),
    )
    report = run_project_events(project, requests)
    assert [item.status for item in report.outcomes] == [
        "computed_unvalidated",
        "computed_unvalidated",
        "invalid_input",
        "computed_unvalidated",
    ]
    first, second, invalid, repeated = report.outcomes
    assert invalid.hydrographs == ()
    assert invalid.diagnostics[0].code == "event_fields"
    assert first.hydrographs == repeated.hydrographs
    assert first.python_diagnostics == repeated.python_diagnostics
    assert first.model_sha256 == repeated.model_sha256
    tp1_reference = tmp_path / "tp1.json"
    write_project(
        tp1_reference,
        Project("tp1_reference", "legacy-rorb", EmbeddedRun(tp1), engine=EngineSelection.for_engine("python-cmd")),
    )
    tp1_single = run_engine_project(tp1_reference)
    assert second.hydrographs == tp1_single.hydrographs
    assert second.physical_time_hours == tp1_single.physical_time_hours
    assert first.physical_time_hours == repeated.physical_time_hours
    assert len(first.hydrographs[0].discharge_m3_s) == 201
    assert len(second.hydrographs[0].discharge_m3_s) == 201
    serialized_events = [
        {"event_id": "review-design-baseline"},
        {
            "event_id": tp1_event.event_id,
            "storm": dict(tp1_event.storm or {}),
            "routing": dict(tp1_event.routing or {}),
        },
        {"event_id": "mvp-invalid-control", "controls": [{"code": 99}]},
        {"event_id": "baseline-repeat"},
    ]
    events_file = tmp_path / "events.json"
    events_file.write_text(
        json.dumps(
            {
                "format": "python-runoff-routing-explicit-events",
                "schema_version": 1,
                "events": serialized_events,
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "cmd-seed"
    assert main([str(project), str(output), "--events", str(events_file), "--engine", "python-cmd"]) == 2
    receipt = json.loads(Path(f"{output}.json").read_text(encoding="utf-8"))
    assert [r["status"] for r in receipt["outcomes"]] == [r.status for r in report.outcomes]
    csv_rows = list(csv.DictReader(io.StringIO(Path(f"{output}.csv").read_text(encoding="utf-8"))))
    assert len(csv_rows) == 604
    assert csv_rows[201 + 201]["error_code"] == "event_fields"
    assert csv_rows[0]["discharge_m3_s"] == csv_rows[-201]["discharge_m3_s"]
    assert "mvp-invalid-control: invalid_input" in Path(f"{output}.txt").read_text(encoding="utf-8")


def test_unsupported_storage_event_is_explicit_and_does_not_change_adjacent_results(tmp_path: Path) -> None:
    project = _project(tmp_path)
    report = run_project_events(
        project,
        (
            ProjectEvent("first"),
            {"event_id": "mvp-unsupported-storage", "storages": [{"type": "reservoir"}]},
            ProjectEvent("last"),
        ),
        selection=EngineSelection.for_engine("python-cmd"),
    )
    assert [outcome.status for outcome in report.outcomes] == [
        "computed_unvalidated",
        "unsupported_feature",
        "computed_unvalidated",
    ]
    assert report.outcomes[1].diagnostics[0].code == "event_storages"
    assert report.outcomes[1].hydrographs == ()
    assert report.outcomes[0].hydrographs == report.outcomes[2].hydrographs


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
