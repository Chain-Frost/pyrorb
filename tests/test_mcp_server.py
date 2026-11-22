"""Local MCP capability-status, protocol and read-only adapter tests."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import cast

import pytest
from mcp import Client

from runoff_routing.engine_types import EngineSelection
from runoff_routing.mcp_catalog import CATALOG, find_capability
from runoff_routing.mcp_server import (
    inspect_rorb_file,
    mcp,
    prepare_arr_design,
    run_project,
    run_project_events,
)
from runoff_routing.project_json import EmbeddedRun, Project, write_project
from runoff_routing.rorb_model import RunModel, from_json


def test_catalog_has_explicit_placeholders() -> None:
    mc = find_capability("monte_carlo")
    assert mc is not None
    assert mc.exposure == "staged"
    special = find_capability("advanced_structures")
    assert special is not None
    assert special.exposure == "planned"
    assert find_capability("missing_api") is None
    assert len({entry.name for entry in CATALOG}) == len(CATALOG)


def test_in_process_mcp_discovery() -> None:
    async def probe() -> None:
        async with Client(mcp, raise_exceptions=True) as client:
            listing = await client.list_tools()
            assert {entry.name for entry in listing.tools} == {
                "list_capabilities",
                "describe_capability",
                "get_engine_capabilities",
                "inspect_rorb_file",
                "validate_project",
                "inspect_event_request",
                "summarize_arr_results",
                "get_api_reference",
                "get_result_summary",
                "run_project",
                "run_project_events",
                "prepare_arr_design",
            }
            read_only = {
                "list_capabilities",
                "describe_capability",
                "get_engine_capabilities",
                "inspect_rorb_file",
                "validate_project",
                "inspect_event_request",
                "summarize_arr_results",
            }
            for entry in listing.tools:
                assert entry.annotations is not None
                assert entry.annotations.read_only_hint is (entry.name in read_only)
                if entry.name not in read_only:
                    assert not entry.annotations.destructive_hint
            staged = await client.call_tool("list_capabilities", {"exposure": "staged"})
            assert not staged.is_error
            assert "monte_carlo" in str(staged.structured_content)
            detail = await client.call_tool("describe_capability", {"name": "validate_project"})
            assert not detail.is_error
            assert "load_project" in str(detail.structured_content)
            engines = await client.call_tool("get_engine_capabilities", {})
            assert not engines.is_error
            assert "python-cmd" in str(engines.structured_content)
            resources = await client.list_resources()
            assert len(resources.resources) == 5
            prompts = await client.list_prompts()
            assert any(entry.name == "plan_runoff_work" for entry in prompts.prompts)

    asyncio.run(probe())


def test_inspection_is_read_only_and_bounded(tmp_path: Path) -> None:
    path = tmp_path / "sample.unknown"
    path.write_text("not a RORB source\n", encoding="utf-8")
    before = path.read_bytes()
    result = inspect_rorb_file(str(path))
    assert result["status"] == "unsupported"
    assert result["native_parity"] == "not_assessed"
    assert result["hydrograph_row_count"] is None
    assert path.read_bytes() == before


EXAMPLES = Path(__file__).parents[1] / "examples"


def _project(directory: Path, *, engine: str = "python-cmd") -> Path:
    model = from_json((EXAMPLES / "synthetic-run.json").read_text(encoding="utf-8"))
    assert isinstance(model, RunModel)
    path = directory / "project.json"
    write_project(
        path,
        Project("mcp_example", "explicit", EmbeddedRun(model), engine=EngineSelection.for_engine(engine)),
    )
    return path


def _events(directory: Path, *, count: int = 2) -> Path:
    records: list[dict[str, object]] = [{"event_id": f"event_{index}"} for index in range(count)]
    if count == 2:
        records[1]["storm"] = {"subarea_ids": ["unrecognised"]}
    request = {
        "format": "python-runoff-routing-explicit-events",
        "schema_version": 1,
        "events": records,
    }
    path = directory / "events.json"
    path.write_text(json.dumps(request) + "\n", encoding="utf-8")
    return path


def _design(directory: Path, project: Path) -> Path:
    data = {
        "format": "python-runoff-routing-arr2019-design",
        "schema_version": 1,
        "project": str(project),
        "bom_ifd": str(EXAMPLES / "arr-design-synthetic-ifd.csv"),
        "temporal_patterns": str(EXAMPLES / "arr-design-synthetic-patterns.csv"),
        "pattern_kind": "point",
        "temporal_region": "SyntheticPoint",
        "arf_region": "South-West Western Australia",
        "catchment_area_km2": "2",
        "durations_min": [60],
        "aep_labels": ["1%"],
        "dry_tail_min": 120,
        "engine": "python-cmd",
        "numerical_profile": "cmd-6.44",
        "loss": {"mode": "project_il_cl"},
    }
    path = directory / "design.json"
    path.write_text(json.dumps(data) + "\n", encoding="utf-8")
    return path


def test_mcp_single_run_requires_opt_in_and_keeps_engine_provenance(tmp_path: Path) -> None:
    project = _project(tmp_path)
    target = tmp_path / "single.json"
    with pytest.raises(ValueError, match="allow_write=true"):
        run_project(str(project), str(target))
    assert not target.exists()
    result = run_project(str(project), str(target), engine="python", allow_write=True)
    assert result["status"] == "computed_unvalidated"
    assert result["stored_engine"] == "python-cmd"
    assert result["effective_engine"] == "python"
    assert result["numerical_profile"] == "engineering-v1"
    assert result["selection_source"] == "api_override"
    assert result["native_parity_status"] == "not_assessed"
    assert result["numerical_acceptance"] == "unassessed"
    assert result["implementation_revision"] is not None
    raw = target.read_bytes()
    actual = json.loads(raw)
    assert actual["effective_selection"]["engine"] == "python"
    assert actual["project_sha256"] == result["project_sha256"]
    with pytest.raises(FileExistsError, match="cannot be overwritten"):
        run_project(str(project), str(target), allow_write=True)
    assert target.read_bytes() == raw


def test_mcp_stored_selection_and_bad_override_are_explicit(tmp_path: Path) -> None:
    project = _project(tmp_path)
    stored = run_project(str(project), str(tmp_path / "stored.json"), allow_write=True)
    assert stored["selection_source"] == "project"
    assert stored["effective_engine"] == "python-cmd"
    with pytest.raises(ValueError, match="requires an explicit engine"):
        run_project(str(project), str(tmp_path / "wrong.json"), numerical_profile="cmd-6.44", allow_write=True)
    assert not (tmp_path / "wrong.json").exists()


def test_mcp_native_is_refused_without_launch_or_output(tmp_path: Path) -> None:
    stored_native = _project(tmp_path, engine="rorb-cmd")
    with pytest.raises(ValueError, match="not exposed through MCP"):
        run_project(str(stored_native), str(tmp_path / "native.json"), allow_write=True)
    with pytest.raises(ValueError, match="not exposed through MCP"):
        run_project(str(stored_native), str(tmp_path / "native2.json"), engine="rorb-cmd", allow_write=True)
    assert not (tmp_path / "native.json").exists()
    assert not (tmp_path / "native2.json").exists()


def test_mcp_batch_keeps_failures_in_report_and_never_overwrites(tmp_path: Path) -> None:
    project = _project(tmp_path)
    events = _events(tmp_path)
    prefix = tmp_path / "batch"
    with pytest.raises(ValueError, match="allow_write=true"):
        run_project_events(str(project), str(events), str(prefix))
    assert not (tmp_path / "batch.json").exists()
    result = run_project_events(str(project), str(events), str(prefix), allow_write=True)
    assert result["succeeded"] is False
    assert result["status"] == "incomplete"
    assert result["requested_event_count"] == 2
    assert result["status_counts"] == {"computed_unvalidated": 1, "unsupported_feature": 1}
    assert result["failed_event_count"] == 1
    assert result["native_parity_status"] == "not_assessed"
    assert result["selection_source"] == "project"
    paths = [Path(path) for path in cast("list[str]", result["output_paths"])]
    assert len(paths) == 3
    assert all(path.is_file() for path in paths)
    actual = json.loads(paths[0].read_text(encoding="utf-8"))
    assert len(actual["outcomes"]) == 2
    assert actual["outcomes"][1]["status"] == "unsupported_feature"
    saved = tuple(path.read_bytes() for path in paths)
    with pytest.raises(FileExistsError, match="cannot be overwritten"):
        run_project_events(str(project), str(events), str(prefix), allow_write=True)
    assert saved == tuple(path.read_bytes() for path in paths)


def test_mcp_batch_rejects_oversize_request_before_execution(tmp_path: Path) -> None:
    project = _project(tmp_path)
    events = _events(tmp_path, count=501)
    with pytest.raises(ValueError, match="limit of 500 events"):
        run_project_events(str(project), str(events), str(tmp_path / "too_many"), allow_write=True)
    assert not (tmp_path / "too_many.json").exists()


def test_mcp_arr_design_executes_ten_member_population_without_native_claims(tmp_path: Path) -> None:
    project = _project(tmp_path)
    config = _design(tmp_path, project)
    prefix = tmp_path / "design_results"
    with pytest.raises(ValueError, match="allow_write=true"):
        prepare_arr_design(str(config), str(prefix))
    assert not (tmp_path / "design_results.json").exists()
    result = prepare_arr_design(str(config), str(prefix), allow_write=True)
    assert result["succeeded"] is True
    assert result["status"] == "computed_unvalidated"
    assert result["expected_population"] == 10
    assert result["prepared_population"] == 10
    assert result["engine"] == "python-cmd"
    assert result["generated_input_reference_status"] == "not_assessed"
    assert result["routed_native_reference_status"] == "not_assessed"
    assert result["representative_event_rule"] == "not_selected_unverified"
    paths = [Path(path) for path in cast("list[str]", result["output_paths"])]
    assert len(paths) == 6
    assert all(path.is_file() for path in paths)
    assert json.loads((tmp_path / "design_results.events.json").read_text())["events"]
    before = tuple(path.read_bytes() for path in paths)
    with pytest.raises(FileExistsError, match="cannot be overwritten"):
        prepare_arr_design(str(config), str(prefix), allow_write=True)
    assert before == tuple(path.read_bytes() for path in paths)


def test_mcp_arr_rejects_native_configuration_before_routing(tmp_path: Path) -> None:
    project = _project(tmp_path)
    config = _design(tmp_path, project)
    data = json.loads(config.read_text(encoding="utf-8"))
    data["engine"] = "rorb-cmd"
    data["rainfall_preparation"] = "published_arf_stm_2dp"
    config.write_text(json.dumps(data) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="not exposed through MCP"):
        prepare_arr_design(str(config), str(tmp_path / "blocked"), allow_write=True)
    assert not (tmp_path / "blocked.json").exists()


def test_mcp_protocol_can_call_opted_in_project_execution(tmp_path: Path) -> None:
    project = _project(tmp_path)
    output = tmp_path / "via_mcp.json"

    async def probe() -> None:
        async with Client(mcp, raise_exceptions=True) as client:
            result = await client.call_tool(
                "run_project",
                {"project_path": str(project), "output_path": str(output), "allow_write": True},
            )
            assert not result.is_error
            assert "computed_unvalidated" in str(result.structured_content)

    asyncio.run(probe())
    assert output.exists()
