"""Reporting-only synthetic population controls for issue #152."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from runoff_routing.arr_design_batch import run_design_batch
from runoff_routing.arr_result_summary import (
    ResultSummaryError,
    main,
    read_deterministic_results,
    summarize_deterministic_results,
    write_summary,
)
from runoff_routing.project_json import EmbeddedRun, Project, write_project
from runoff_routing.rorb_model import RunModel, from_json

EXAMPLES = Path(__file__).parents[1] / "examples"


@pytest.fixture(scope="module")
def sample(tmp_path_factory: pytest.TempPathFactory) -> tuple[dict[str, Any], dict[str, Any]]:
    root = tmp_path_factory.mktemp("arr-results")
    model = from_json((EXAMPLES / "synthetic-run.json").read_text(encoding="utf-8"))
    assert isinstance(model, RunModel)
    project = root / "project.json"
    write_project(project, Project("arr_result_reporting_synthetic", "explicit", EmbeddedRun(model)))
    config: dict[str, object] = {
        "format": "python-runoff-routing-arr2019-design",
        "schema_version": 1,
        "project": str(project),
        "bom_ifd": str(EXAMPLES / "arr-design-synthetic-ifd.csv"),
        "temporal_patterns": str(EXAMPLES / "arr-design-synthetic-patterns.csv"),
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
    path = root / "config.json"
    path.write_text(json.dumps(config) + "\n", encoding="utf-8")
    result = run_design_batch(path)
    assert result.succeeded
    return json.loads(json.dumps(result.effective)), json.loads(result.routed.to_json())


def _copy(sample: tuple[dict[str, Any], dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    return copy.deepcopy(sample)


@pytest.mark.parametrize("profile", ["assumed-native-parity", None, ["unknown"]])
def test_unknown_method_profile_remains_rejected(
    sample: tuple[dict[str, Any], dict[str, Any]], profile: object
) -> None:
    effective, routed = _copy(sample)
    effective["method_profile"] = profile
    with pytest.raises(ResultSummaryError, match="method profile"):
        summarize_deterministic_results(effective, routed)


def test_complete_population_and_distinct_source_native_internal_identities(
    sample: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    effective, routed = _copy(sample)
    report = summarize_deterministic_results(effective, routed)
    data = report.data
    assert data["engine"] == "python-cmd"
    assert data["numerical_profile"] == "cmd-6.44"
    assert data["expected_population"] == data["prepared_population"] == 40
    assert data["software_population_complete"]
    assert len(data["physical_print_sites"]) == 1
    assert len(data["cell_sites"]) == 4
    assert all(cell["complete_comparable_population"] for cell in data["cell_sites"])
    assert all(cell["completed_member_count"] == 10 for cell in data["cell_sites"])
    first, same_duration_other_aep = data["cell_sites"][:2]
    assert [row["original_tp_event_id"] for row in first["members"]] == [
        row["original_tp_event_id"] for row in same_duration_other_aep["members"]
    ]
    assert first["members"][0]["event_id"] != same_duration_other_aep["members"][0]["event_id"]
    assert [row["ensemble_order"] for row in first["members"]] == list(range(1, 11))
    assert [row["source_order"] for row in first["members"]] == list(range(1, 11))
    assert all(row["native_ordinal"] is None for row in first["members"])
    assert all(cell["representative_selection"]["calculated_by_package"] is None for cell in data["cell_sites"])
    assert all(cell["representative_selection"]["reported_by_native"] is None for cell in data["cell_sites"])
    assert all(row["selected_duration_min"] is None for row in data["critical_durations"])
    assert report.to_json() == summarize_deterministic_results(effective, routed).to_json()
    assert report.to_csv() == summarize_deterministic_results(effective, routed).to_csv()


def test_api_file_and_real_cli_agree_and_do_not_modify_hydrographs(
    tmp_path: Path, sample: tuple[dict[str, Any], dict[str, Any]]
) -> None:
    effective, routed = _copy(sample)
    inputs = (tmp_path / "design.effective.json", tmp_path / "design.json")
    for path, data in zip(inputs, (effective, routed), strict=True):
        path.write_text(json.dumps(data), encoding="utf-8")
    before = tuple(path.read_bytes() for path in inputs)
    api = read_deterministic_results(*inputs)
    api_paths = write_summary(tmp_path / "api", api)
    assert main([str(inputs[0]), str(inputs[1]), str(tmp_path / "direct")]) == 0
    # Fixed interpreter and repository module; arguments are local test paths, not shell commands.
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "runoff_routing.arr_result_summary", *map(str, inputs), str(tmp_path / "cli")],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "UNVERIFIED" in result.stdout
    for suffix, path in zip((".analysis.json", ".analysis.csv", ".analysis.txt"), api_paths, strict=True):
        assert path.read_bytes() == Path(f"{tmp_path / 'direct'}{suffix}").read_bytes()
        assert path.read_bytes() == Path(f"{tmp_path / 'cli'}{suffix}").read_bytes()
    assert before == tuple(path.read_bytes() for path in inputs)
    with pytest.raises(ResultSummaryError, match="already exists"):
        write_summary(tmp_path / "api", api)


def test_multiple_physical_sites_remain_separate(sample: tuple[dict[str, Any], dict[str, Any]]) -> None:
    effective, routed = _copy(sample)
    for outcome in routed["outcomes"]:
        second = copy.deepcopy(outcome["hydrographs"][0])
        second["print_id"] = "second-print"
        second["label"] = "Second physical print"
        outcome["requested_print_ids"].append("second-print")
        outcome["hydrographs"].append(second)
    routed["volumes"].extend(
        {
            **volume,
            "print_id": "second-print",
        }
        for volume in list(routed["volumes"])
    )
    report = summarize_deterministic_results(effective, routed)
    assert len(report.data["physical_print_sites"]) == 2
    assert len(report.data["cell_sites"]) == 8
    assert all(cell["complete_comparable_population"] for cell in report.data["cell_sites"])
    assert [row["site_id"] for row in report.data["cell_sites"][:2]] == list(report.data["physical_print_sites"])


def test_failed_member_remains_in_denominator_and_partial_ranking(
    sample: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    effective, routed = _copy(sample)
    record = effective["members"][0]
    outcome = routed["outcomes"][0]
    outcome["status"] = "invalid_input"
    outcome["hydrographs"] = []
    outcome["diagnostics"] = [{"code": "test_failure", "message": "deliberate test failure"}]
    record["execution_status"] = "invalid_input"
    record["execution_error_code"] = "test_failure"
    routed["volumes"] = [row for row in routed["volumes"] if row["event_id"] != record["event_id"]]
    report = summarize_deterministic_results(effective, routed)
    first = report.data["cell_sites"][0]
    assert not report.data["software_population_complete"]
    assert not report.data["software_execution_success"]
    assert first["expected_member_count"] == 10
    assert first["completed_member_count"] == 9
    assert first["failed_or_incomplete_member_count"] == 1
    assert len(first["diagnostic_peak_ranking"]) == 9
    assert first["members"][0]["routing_status"] == "invalid_input"
    assert first["representative_selection"]["rule_status"] == "unverified"


def test_failed_input_cell_preserves_all_candidate_ids_and_missing_ten(
    sample: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    effective, routed = _copy(sample)
    cell = effective["cells"][-1]
    records = effective["members"][-10:]
    discarded = {member["event_id"] for member in records}
    cell.update(
        {
            "status": "input_error",
            "ready_count": 0,
            "unqualified_source_candidate_ids": [item["original_tp_id"] for item in records],
            "unqualified_source_candidate_orders": [item["source_order"] for item in records],
        }
    )
    effective["members"] = [
        *effective["members"][:-10],
        {
            "duration_min": cell["duration_min"],
            "aep_label": cell["aep_label"],
            "original_tp_id": None,
            "event_id": None,
            "status": "input_error",
        },
    ]
    effective["prepared_population"] = 30
    routed["outcomes"] = [outcome for outcome in routed["outcomes"] if outcome["event_id"] not in discarded]
    routed["volumes"] = [volume for volume in routed["volumes"] if volume["event_id"] not in discarded]
    routed["requested_event_count"] = 30
    report = summarize_deterministic_results(effective, routed)
    last = report.data["cell_sites"][-1]
    assert last["not_prepared_member_count"] == 10
    assert last["source_candidate_count"] == 10
    assert last["completed_member_count"] == 0
    assert len(last["unqualified_source_candidates"]) == 10
    assert all(candidate["original_tp_event_id"] is not None for candidate in last["unqualified_source_candidates"])
    assert not last["complete_comparable_population"]
    assert last["representative_selection"]["calculated_by_package"] is None
    assert report.to_csv().count("unqualified_source_candidate") == 10


def test_zero_flow_tie_preserves_all_peak_samples_and_avoids_selection(
    sample: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    effective, routed = _copy(sample)
    ids = {member["event_id"] for member in effective["members"][:10]}
    for outcome in routed["outcomes"]:
        if outcome["event_id"] in ids:
            graph = outcome["hydrographs"][0]
            graph["discharge_m3_s"] = [0.0] * len(graph["discharge_m3_s"])
    for volume in routed["volumes"]:
        if volume["event_id"] in ids:
            volume["physical_trapezoidal_volume_m3"] = 0.0
    report = summarize_deterministic_results(effective, routed)
    first = report.data["cell_sites"][0]
    assert first["observed_peak_median_m3_s"] == 0.0
    assert first["observed_peak_max_m3_s"] == 0.0
    assert len(first["diagnostic_tie_groups"]) == 1
    assert len(first["diagnostic_tie_groups"][0]["event_ids"]) == 10
    assert len(first["members"][0]["peak_sample_indices"]) == first["members"][0]["sample_count"]
    assert first["representative_selection"]["calculated_by_package"] is None


def test_routed_order_is_not_used_as_pattern_or_filename_order(sample: tuple[dict[str, Any], dict[str, Any]]) -> None:
    effective, routed = _copy(sample)
    routed["outcomes"].reverse()
    summary = summarize_deterministic_results(effective, routed)
    assert [row["event_id"] for row in summary.data["cell_sites"][0]["members"]] == [
        member["event_id"] for member in effective["members"][:10]
    ]


@pytest.mark.parametrize("changed", ["engine", "profile", "source", "loss", "site", "missing", "extra_graph"])
def test_reject_mixed_or_unbound_populations(sample: tuple[dict[str, Any], dict[str, Any]], changed: str) -> None:
    effective, routed = _copy(sample)
    outcome = routed["outcomes"][0]
    if changed == "engine":
        outcome["effective_selection"]["engine"] = "python"
    elif changed == "profile":
        outcome["effective_selection"]["numerical_profile"] = "cmd-6.45"
    elif changed == "source":
        outcome["project_sha256"] = "different"
    elif changed == "loss":
        effective["members"][0]["loss"]["method"] = "other"
    elif changed == "site":
        outcome["requested_print_ids"].append("another")
    elif changed == "missing":
        routed["outcomes"].pop(0)
        routed["requested_event_count"] -= 1
    elif changed == "extra_graph":
        outcome["hydrographs"][0]["print_id"] = "undeclared"
    with pytest.raises(ResultSummaryError):
        summarize_deterministic_results(effective, routed)


def test_truncated_member_is_incomplete_but_other_observed_peaks_remain(
    sample: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    effective, routed = _copy(sample)
    outcome = routed["outcomes"][0]
    outcome["physical_time_hours"] = outcome["physical_time_hours"][:-1]
    outcome["hydrographs"][0]["discharge_m3_s"] = outcome["hydrographs"][0]["discharge_m3_s"][:-1]
    report = summarize_deterministic_results(effective, routed)
    first = report.data["cell_sites"][0]
    assert first["completed_member_count"] == 9
    assert first["failed_or_incomplete_member_count"] == 1
    assert first["members"][0]["metric_status"] == "incomplete_output"
    assert first["members"][0]["metric_reason"] == "declared_horizon_mismatch"
    assert first["members"][0]["observed_sample_count"] < first["members"][0]["declared_sample_count"]
    assert not first["complete_comparable_population"]
    assert first["observed_peak_median_m3_s"] is not None
    assert len(first["diagnostic_peak_ranking"]) == 9
    assert all(item["selected_duration_min"] is None for item in report.data["critical_durations"])


def test_uniformly_truncated_hydrographs_cannot_pass_complete_population(
    sample: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    effective, routed = _copy(sample)
    for outcome in routed["outcomes"]:
        outcome["physical_time_hours"] = outcome["physical_time_hours"][:2]
        for graph in outcome["hydrographs"]:
            graph["discharge_m3_s"] = graph["discharge_m3_s"][:2]
        # Deliberately retain the original full-horizon volume record.
    report = summarize_deterministic_results(effective, routed)
    assert report.data["software_execution_success"]
    assert not report.data["software_population_complete"]
    for cell in report.data["cell_sites"]:
        assert cell["completed_member_count"] == 0
        assert cell["failed_or_incomplete_member_count"] == 10
        assert cell["observed_peak_median_m3_s"] is None
        assert cell["diagnostic_peak_ranking"] == []
        assert all(row["metric_reason"] == "declared_horizon_mismatch" for row in cell["members"])
        assert cell["representative_selection"]["calculated_by_package"] is None
    assert "declared_horizon_mismatch" in report.to_json()
    assert "declared_horizon_mismatch" in report.to_csv()
    assert all(row["selected_duration_min"] is None for row in report.data["critical_durations"])


@pytest.mark.parametrize("change", ["shifted", "scaled", "invalid_step", "wrong_step"])
def test_complete_length_requires_declared_physical_clock(
    sample: tuple[dict[str, Any], dict[str, Any]], change: str
) -> None:
    effective, routed = _copy(sample)
    outcome = routed["outcomes"][0]
    if change == "shifted":
        outcome["physical_time_hours"] = [str(float(t) + 1) for t in outcome["physical_time_hours"]]
    elif change == "scaled":
        outcome["physical_time_hours"] = [str(float(t) * 2) for t in outcome["physical_time_hours"]]
    elif change == "invalid_step":
        outcome["effective_inputs"]["timestep_hours"] = "0"
    else:
        outcome["effective_inputs"]["timestep_hours"] = "2"
    report = summarize_deterministic_results(effective, routed)
    first = report.data["cell_sites"][0]
    assert first["members"][0]["metric_status"] == "incomplete_output"
    assert first["members"][0]["metric_reason"] in {"declared_time_grid_mismatch", "invalid_declared_horizon"}
    assert first["completed_member_count"] == 9
    assert not first["complete_comparable_population"]
    assert len(first["diagnostic_peak_ranking"]) == 9


def test_critical_duration_comparison_rejects_missing_grid_in_one_duration(
    sample: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    effective, routed = _copy(sample)
    incomplete_ids = {member["event_id"] for member in effective["members"][:10]}
    for outcome in routed["outcomes"]:
        if outcome["event_id"] in incomplete_ids:
            outcome["physical_time_hours"] = outcome["physical_time_hours"][:2]
            for graph in outcome["hydrographs"]:
                graph["discharge_m3_s"] = graph["discharge_m3_s"][:2]
    report = summarize_deterministic_results(effective, routed)
    relevant = [cell for cell in report.data["cell_sites"] if cell["aep_label"] == effective["cells"][0]["aep_label"]]
    assert len(relevant) == 2
    assert relevant[0]["time_grid_sha256"] is None
    assert not relevant[0]["complete_comparable_population"]
    assert relevant[1]["complete_comparable_population"]
    assert relevant[1]["time_grid_sha256"] is not None
    duration = next(row for row in report.data["critical_durations"] if row["aep_label"] == relevant[0]["aep_label"])
    assert not duration["complete_comparable_within_each_duration"]
    assert not duration["comparable_across_durations"]
    assert duration["selected_duration_min"] is None


def test_critical_duration_comparison_rejects_empty_observed_population(
    sample: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    effective, routed = _copy(sample)
    for outcome in routed["outcomes"]:
        outcome["physical_time_hours"] = outcome["physical_time_hours"][:2]
        for graph in outcome["hydrographs"]:
            graph["discharge_m3_s"] = graph["discharge_m3_s"][:2]
    report = summarize_deterministic_results(effective, routed)
    assert all(row["time_grid_sha256"] is None for row in report.data["cell_sites"])
    assert all(not record["comparable_across_durations"] for record in report.data["critical_durations"])


def test_empty_routed_population_cannot_claim_software_success(
    sample: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    effective, routed = _copy(sample)
    effective["members"] = [
        {
            "duration_min": cell["duration_min"],
            "aep_label": cell["aep_label"],
            "event_id": None,
            "original_tp_id": None,
            "status": "input_error",
        }
        for cell in effective["cells"]
    ]
    for cell in effective["cells"]:
        cell["status"] = "input_error"
        cell["ready_count"] = 0
    effective["prepared_population"] = 0
    routed["outcomes"] = []
    routed["volumes"] = []
    routed["requested_event_count"] = 0
    report = summarize_deterministic_results(effective, routed)
    assert not report.data["software_execution_success"]
    assert not report.data["software_population_complete"]
    assert report.data["physical_print_sites"] == []


def test_truncated_or_duplicate_input_fails_closed(
    tmp_path: Path, sample: tuple[dict[str, Any], dict[str, Any]]
) -> None:
    effective, routed = _copy(sample)
    routed_path = tmp_path / "routed.json"
    routed_path.write_text(json.dumps(routed), encoding="utf-8")
    effective_path = tmp_path / "effective.json"
    effective_path.write_text('{"format":"one","format":"two"}', encoding="utf-8")
    with pytest.raises(ResultSummaryError, match="Duplicate JSON field"):
        read_deterministic_results(effective_path, routed_path)
    effective_path.write_text(json.dumps(effective) + "\n", encoding="utf-8")
    routed_path.write_text('{"format":1,"outcomes":[', encoding="utf-8")
    with pytest.raises(ResultSummaryError, match="Invalid JSON"):
        read_deterministic_results(effective_path, routed_path)
