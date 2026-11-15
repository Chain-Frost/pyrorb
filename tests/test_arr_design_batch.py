"""Deterministic S6 input-population and #119 dispatch contracts (synthetic only)."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from pathlib import Path
from typing import Any, cast

import pytest

from runoff_routing.arr_design_batch import (
    DesignBatchResult,
    DesignConfigError,
    read_design_config,
    run_design_batch,
    write_design_outputs,
)
from runoff_routing.engine_types import EngineSelection
from runoff_routing.project_batch import load_event_request, run_project_events
from runoff_routing.project_json import EmbeddedRun, Project, write_project
from runoff_routing.rorb_model import RunModel, from_json

EXAMPLES = Path(__file__).parents[1] / "examples"
IFD = EXAMPLES / "arr-design-synthetic-ifd.csv"
PATTERNS = EXAMPLES / "arr-design-synthetic-patterns.csv"
MODEL = EXAMPLES / "synthetic-run.json"
LEGACY = Path(__file__).parent / "fixtures" / "arr" / "2016-era-synthetic.txt"


def _audit(result: DesignBatchResult) -> dict[str, Any]:
    """Test-only nested JSON manifest view; preserve typed model interfaces."""
    return cast("dict[str, Any]", result.effective)


def _project(directory: Path) -> Path:
    run = from_json(MODEL.read_text(encoding="utf-8"))
    assert isinstance(run, RunModel)
    path = directory / "project.json"
    write_project(path, Project("arr_design_synthetic", "explicit", EmbeddedRun(run)))
    return path


def _config(directory: Path, *, ifd: Path = IFD, patterns: Path = PATTERNS) -> tuple[Path, dict[str, object]]:
    project = _project(directory)
    data: dict[str, object] = {
        "format": "python-runoff-routing-arr2019-design",
        "schema_version": 1,
        "project": str(project),
        "bom_ifd": str(ifd),
        "temporal_patterns": str(patterns),
        "pattern_kind": "point",
        "temporal_region": "SyntheticPoint",
        "arf_region": "South-West Western Australia",
        "catchment_area_km2": "2",
        "durations_min": [60, 120],
        "aep_labels": ["1%", "2%"],
        "dry_tail_min": 120,
        "engine": "python-cmd",
        "numerical_profile": "cmd-6.44",
        "loss": {"mode": "project_il_cl"},
    }
    path = directory / "design.json"
    path.write_text(json.dumps(data) + "\n", encoding="utf-8")
    return path, data


def _write_config(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data) + "\n", encoding="utf-8")


def test_complete_duration_aep_tp_population_replays_through_common_api(tmp_path: Path) -> None:
    config, _ = _config(tmp_path)
    result = run_design_batch(config)
    assert result.succeeded
    assert _audit(result)["expected_population"] == 40
    assert _audit(result)["prepared_population"] == 40
    assert _audit(result)["input_population_complete"] is True
    assert all(item.status == "computed_unvalidated" for item in result.routed.outcomes)
    records = _audit(result)["members"]
    assert isinstance(records, list)
    assert [record["original_tp_id"] for record in records[:10]] == [f"{value:04d}" for value in range(1, 11)]
    assert [record["source_order"] for record in records[:10]] == list(range(1, 11))
    assert [record["ensemble_order"] for record in records[:10]] == list(range(1, 11))
    assert [record["original_tp_id"] for record in records[20:30]] == [f"{value:04d}" for value in range(101, 111)]
    assert [item["status"] for item in _audit(result)["cells"]] == ["ready"] * 4
    assert len({outcome.event_id for outcome in result.routed.outcomes}) == 40
    assert _audit(result)["generated_input_reference_status"] == "not_assessed"
    assert _audit(result)["critical_duration_rule"] == "not_selected_unverified"
    assert _audit(result)["representative_event_rule"] == "not_selected_unverified"

    sources = _audit(result)["source_files"]
    assert sources["bom_ifd"]["sha256"] == hashlib.sha256(IFD.read_bytes()).hexdigest()
    assert sources["temporal_patterns"]["sha256"] == hashlib.sha256(PATTERNS.read_bytes()).hexdigest()
    assert sources["temporal_patterns"]["members"][0]["sha256"] == hashlib.sha256(PATTERNS.read_bytes()).hexdigest()
    assert all(record["effective_losses"] is None for record in records)
    for record in records:
        assert Decimal(record["raw_gross_total_mm"]) == sum(
            (Decimal(value) for value in record["raw_gross_increments_mm"]), Decimal(0)
        )
        assert Decimal(record["areal_total_mm"]) == sum(
            (Decimal(value) for value in record["areal_increments_mm"]), Decimal(0)
        )
        assert record["arf_factor"] is not None
        assert record["effective_storm"]["depths_mm"] == [record["areal_total_mm"]]
        assert record["execution_status"] == "computed_unvalidated"
    paths = write_design_outputs(tmp_path / "design-results", result)
    assert len(paths) == 6
    request = load_event_request(tmp_path / "design-results.events.json")
    replay = run_project_events(tmp_path / "project.json", request, selection=EngineSelection.for_engine("python-cmd"))
    assert replay.succeeded
    assert [(a.event_id, a.model_sha256, a.hydrographs, a.physical_time_hours) for a in replay.outcomes] == [
        (a.event_id, a.model_sha256, a.hydrographs, a.physical_time_hours) for a in result.routed.outcomes
    ]
    assert json.loads((tmp_path / "design-results.json").read_text())["requested_event_count"] == 40
    assert "computed_unvalidated" in (tmp_path / "design-results.txt").read_text()
    assert "Input: 40/40" in (tmp_path / "design-results.summary.txt").read_text()
    before = tuple(path.read_bytes() for path in paths)
    with pytest.raises(DesignConfigError, match="already exist"):
        write_design_outputs(tmp_path / "design-results", result)
    assert before == tuple(path.read_bytes() for path in paths)


def test_missing_tenth_tp_is_incomplete_without_substitution(tmp_path: Path) -> None:
    source = tmp_path / "missing.csv"
    rows = PATTERNS.read_text(encoding="utf-8").splitlines()
    source.write_text("\n".join(line for line in rows if not line.startswith("0110,")) + "\n")
    config, _ = _config(tmp_path, patterns=source)
    result = run_design_batch(config)
    assert not result.succeeded
    assert _audit(result)["expected_population"] == 40
    assert _audit(result)["prepared_population"] == 20
    assert [cell["status"] for cell in _audit(result)["cells"]] == ["ready", "ready", "input_error", "input_error"]
    assert all(cell["expected_count"] == 10 for cell in _audit(result)["cells"])
    assert all(cell["ready_count"] == 0 for cell in _audit(result)["cells"][2:])
    assert len(result.routed.outcomes) == 20
    assert all(outcome.status == "computed_unvalidated" for outcome in result.routed.outcomes)
    assert _audit(result)["status"] == "incomplete"
    write_design_outputs(tmp_path / "incomplete", result)
    assert "FAILED 120 min" in (tmp_path / "incomplete.summary.txt").read_text()
    assert (tmp_path / "incomplete.events.json").exists()


def test_source_label_does_not_convert_ey_to_aep(tmp_path: Path) -> None:
    config, data = _config(tmp_path)
    data["aep_labels"] = ["0.5EY"]
    _write_config(config, data)
    result = run_design_batch(config)
    assert not result.succeeded
    assert _audit(result)["expected_population"] == 20
    assert _audit(result)["prepared_population"] == 0
    assert len(result.routed.outcomes) == 0
    assert all(cell["status"] == "input_error" for cell in _audit(result)["cells"])
    assert all("not present" in cell["error"] for cell in _audit(result)["cells"])


@pytest.mark.parametrize(
    ("mode", "expected_source_il"),
    [
        ("legacy_source_depth_burst_only", "14.00"),
        ("legacy_ratio_areal_burst_only", None),
    ],
)
def test_legacy_burst_only_losses_applied_by_engine_once(
    tmp_path: Path, mode: str, expected_source_il: str | None
) -> None:
    config, data = _config(tmp_path)
    data["aep_labels"] = ["1%"]
    data["durations_min"] = [60]
    data["loss"] = {"mode": mode, "arr_txt": str(LEGACY), "percentile": 50, "excess_policy": "reject"}
    _write_config(config, data)
    result = run_design_batch(config)
    assert result.succeeded
    assert len(result.routed.outcomes) == 10
    for record in _audit(result)["members"]:
        applied = record["loss"]
        assert applied["preburst_source_depth_mm"] == "7.00"
        assert applied["storm_initial_loss_mm"] == "21.0"
        assert applied["continuing_loss_mm_per_hour"] == "2.00"
        if expected_source_il is not None:
            assert applied["burst_initial_loss_mm"] == expected_source_il
            assert applied["preburst_depth_basis"] == "as_exported_depth"
        else:
            assert applied["preburst_depth_basis"] == "ratio_x_areal_reduced_design_depth"
            assert applied["rainfall_basis_total_mm"] == record["areal_total_mm"]
        assert record["effective_losses"]["initial_loss_mm"] == applied["burst_initial_loss_mm"]
        assert record["engine_loss_application"] == "once_by_selected_engine"
    assert _audit(result)["source_files"]["legacy_arr"]["sha256"] == hashlib.sha256(LEGACY.read_bytes()).hexdigest()


def test_unsafe_or_unsupported_config_rejected_before_execution(tmp_path: Path) -> None:
    config, data = _config(tmp_path)
    data["engine"] = "rorb-cmd"
    _write_config(config, data)
    with pytest.raises(DesignConfigError, match="native rorb-cmd"):
        read_design_config(config)
    data["engine"] = "python-cmd"
    data["durations_min"] = [60, 60]
    _write_config(config, data)
    with pytest.raises(DesignConfigError, match="Duplicate duration"):
        read_design_config(config)
    data["durations_min"] = [60]
    data["catchment_area_km2"] = "3"
    _write_config(config, data)
    with pytest.raises(DesignConfigError, match="sum of project subareas"):
        run_design_batch(config)


def test_missing_arf_or_time_grid_is_explicit_failure(tmp_path: Path) -> None:
    config, data = _config(tmp_path)
    data["dry_tail_min"] = 50
    _write_config(config, data)
    result = run_design_batch(config)
    assert not result.succeeded
    assert _audit(result)["prepared_population"] == 0
    assert all(cell["status"] == "input_error" for cell in _audit(result)["cells"])
    assert all("dry tail" in cell["error"] for cell in _audit(result)["cells"])
