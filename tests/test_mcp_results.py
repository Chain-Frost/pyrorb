"""MCP saved-result summaries must stay bounded, read-only and non-certifying."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest
from mcp import Client

from runoff_routing.arr_design_batch import DESIGN_VERSION, EFFECTIVE_FORMAT
from runoff_routing.arr_result_summary import REPORT_FORMAT as ARR_SUMMARY_FORMAT
from runoff_routing.engine_execution import run_engine_project, write_engine_result
from runoff_routing.mcp_results import MAX_RESULT_BYTES, MAX_SUMMARY_BYTES, summarize_result_file
from runoff_routing.mcp_server import get_result_summary, mcp
from runoff_routing.project_batch import ProjectEvent, run_project_events, write_batch_results
from runoff_routing.project_json import EmbeddedRun, Project, write_project
from runoff_routing.rorb_model import RunModel, from_json

EXAMPLE = Path(__file__).parents[1] / "examples/synthetic-run.json"


def _project(tmp_path: Path) -> Path:
    run = from_json(EXAMPLE.read_text(encoding="utf-8"))
    assert isinstance(run, RunModel)
    project = tmp_path / "project.json"
    write_project(project, Project("mcp_result", "explicit", EmbeddedRun(run)))
    return project


def test_single_result_inspection_does_not_copy_hydrograph(tmp_path: Path) -> None:
    project = _project(tmp_path)
    outcome = run_engine_project(project)
    path = tmp_path / "single.json"
    write_engine_result(path, outcome)
    before = path.read_bytes()
    result = get_result_summary(str(path))
    assert result["kind"] == "single_project"
    assert result["status"] == "computed_unvalidated"
    assert result["native_parity_status"] == "not_assessed"
    assert result["numerical_acceptance"] == "unassessed"
    assert result["hydrograph_count"] == 1
    assert result["source_sha256"]
    assert "discharge_m3_s" not in json.dumps(result)
    assert path.read_bytes() == before


def test_batch_result_preserves_failures_and_declared_counts(tmp_path: Path) -> None:
    project = _project(tmp_path)
    report = run_project_events(
        project,
        (
            ProjectEvent("ok"),
            ProjectEvent("unsupported", storm={"subarea_ids": ["unrecognised"]}),
        ),
    )
    path = write_batch_results(tmp_path / "batch", report)[0]
    result = summarize_result_file(path)
    assert result["kind"] == "event_batch"
    assert result["requested_event_count"] == 2
    assert result["completed_event_count"] == 1
    assert result["status_counts"] == {"computed_unvalidated": 1, "unsupported_feature": 1}
    assert result["failed_event_count"] == 1
    assert "discharge_m3_s" not in json.dumps(result)
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw["status_counts"]["unsupported_feature"] = 2
    altered = tmp_path / "altered.json"
    altered.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ValueError, match="counts do not match"):
        summarize_result_file(altered)


def test_arr_effective_and_summary_metadata_do_not_infer_selection(tmp_path: Path) -> None:
    effective = {
        "format": EFFECTIVE_FORMAT,
        "schema_version": DESIGN_VERSION,
        "status": "incomplete",
        "method_profile": "arr2019-bom-published-arf-burst-only-v1",
        "expected_population": 60,
        "prepared_population": 50,
        "input_population_complete": False,
        "routing_status_counts": {"computed_unvalidated": 50},
        "generated_input_reference_status": "not_assessed",
        "routed_native_reference_status": "not_assessed",
        "representative_event_rule": "not_selected_unverified",
        "critical_duration_rule": "not_selected_unverified",
        "members": [{"effective_storm": {"depths_mm": ["100"]}}],
    }
    effective_path = tmp_path / "effective.json"
    effective_path.write_text(json.dumps(effective), encoding="utf-8")
    result = summarize_result_file(effective_path)
    assert result["kind"] == "arr_effective"
    assert result["prepared_population"] == 50
    assert result["critical_duration_rule"] == "not_selected_unverified"
    assert "effective_storm" not in json.dumps(result)

    arr_summary = {
        "format": ARR_SUMMARY_FORMAT,
        "schema_version": 1,
        "method_profile": "arr2019-bom-published-arf-burst-only-v1",
        "selection_qualification": "unverified",
        "physical_print_sites": [f"site_{i}" for i in range(12)],
        "site_population_count": 12,
    }
    summary_path = tmp_path / "arr-summary.json"
    summary_path.write_text(json.dumps(arr_summary), encoding="utf-8")
    summary = summarize_result_file(summary_path)
    assert summary["kind"] == "arr_summary"
    assert summary["selection_qualification"] == "unverified"
    assert summary["site_list_truncated"] is True
    assert summary["physical_print_sites"] == [f"site_{i}" for i in range(10)]


def test_bad_json_and_excessive_size_fail_closed(tmp_path: Path) -> None:
    unknown = tmp_path / "unknown.json"
    unknown.write_text('{"format":"unknown","status":"computed_unvalidated"}', encoding="utf-8")
    with pytest.raises(ValueError, match="Unrecognised"):
        summarize_result_file(unknown)
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text('{"format":"x","format":"y"}', encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate"):
        summarize_result_file(duplicate)
    huge = tmp_path / "huge.json"
    with huge.open("wb") as stream:
        stream.seek(MAX_RESULT_BYTES)
        stream.write(b"x")
    with pytest.raises(ValueError, match="64 MiB"):
        summarize_result_file(huge)
    invalid_suffix = tmp_path / "fake.txt"
    invalid_suffix.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match=r"only \.json"):
        summarize_result_file(invalid_suffix)


def test_large_metadata_cannot_be_copied_into_mcp_summary(tmp_path: Path) -> None:
    """Known report formats cannot smuggle large data through metadata fields."""
    metadata = tmp_path / "large-metadata.json"
    metadata.write_text(
        json.dumps(
            {
                "format": EFFECTIVE_FORMAT,
                "schema_version": DESIGN_VERSION,
                "status": "incomplete",
                "method_profile": "x" * MAX_SUMMARY_BYTES,
            }
        ),
        encoding="utf-8",
    )
    before = metadata.read_bytes()
    with pytest.raises(ValueError, match="32 KiB response limit"):
        summarize_result_file(metadata)
    assert metadata.read_bytes() == before


def test_duplicate_key_error_does_not_echo_unbounded_input(tmp_path: Path) -> None:
    large_key = "x" * (MAX_SUMMARY_BYTES + 1)
    path = tmp_path / "duplicate-large-key.json"
    path.write_text(
        "{" + json.dumps(large_key) + ": 0, " + json.dumps(large_key) + ": 1}",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Duplicate result JSON key") as error:
        summarize_result_file(path)
    assert large_key not in str(error.value)
    assert len(str(error.value)) < 256


def test_mcp_client_reads_existing_result_without_writing(tmp_path: Path) -> None:
    project = _project(tmp_path)
    outcome = run_engine_project(project)
    path = tmp_path / "result.json"
    write_engine_result(path, outcome)
    before = path.read_bytes()

    async def probe() -> None:
        async with Client(mcp, raise_exceptions=True) as client:
            result = await client.call_tool("get_result_summary", {"path": str(path)})
            assert not result.is_error
            assert "computed_unvalidated" in str(result.structured_content)

    asyncio.run(probe())
    assert path.read_bytes() == before
