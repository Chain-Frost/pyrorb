"""Exercise a separate real stdio server against the established Python APIs."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import cast

from mcp import Client, StdioServerParameters

from runoff_routing.arr_design_batch import run_design_batch, write_design_outputs
from runoff_routing.engine_execution import run_engine_project
from runoff_routing.engine_types import EngineSelection
from runoff_routing.project_batch import load_event_request, run_project_events
from runoff_routing.project_json import EmbeddedRun, MAX_SOURCE_BYTES, Project, write_project
from runoff_routing.rorb_model import RunModel, from_json

ROOT = Path(__file__).absolute().parents[1]
EXAMPLES = ROOT / "examples"


def test_stdio_discovery_calculation_and_safeguards(tmp_path: Path) -> None:
    """Use Windows-safe paths and an out-of-checkout server working directory."""
    workspace = tmp_path / "MCP spaces and Unicode δ"
    workspace.mkdir()
    model = from_json((EXAMPLES / "synthetic-run.json").read_text(encoding="utf-8"))
    assert isinstance(model, RunModel)
    project = workspace / "project.json"
    write_project(project, Project("stdio_example", "explicit", EmbeddedRun(model)))
    native = workspace / "native.json"
    write_project(
        native,
        Project("native_refused", "explicit", EmbeddedRun(model), engine=EngineSelection.for_engine("rorb-cmd")),
    )
    design = json.loads((EXAMPLES / "arr-design-config.json").read_text(encoding="utf-8"))
    design.update(
        project=str(project),
        bom_ifd=str(EXAMPLES / "arr-design-synthetic-ifd.csv"),
        temporal_patterns=str(EXAMPLES / "arr-design-synthetic-patterns.csv"),
        durations_min=[60],
        aep_labels=["1%"],
    )
    config = workspace / "design.json"
    config.write_text(json.dumps(design), encoding="utf-8")
    malformed = workspace / "malformed.json"
    malformed.write_text("{", encoding="utf-8")
    unknown = workspace / "unknown.json"
    unknown.write_text('{"format":"unsupported"}', encoding="utf-8")
    huge = workspace / "huge.json"
    with huge.open("wb") as stream:
        stream.seek(64 * 1024 * 1024)
        stream.write(b"x")
    private_key = "SECRET_STDIO_DUPLICATE_KEY_DO_NOT_DISCLOSE"
    duplicate = workspace / "private-duplicate.json"
    duplicate.write_text(json.dumps({private_key: "one"})[:-1] + f',"{private_key}":"two"' + "}", encoding="utf-8")
    oversized_project = workspace / "private-oversize.json"
    with oversized_project.open("wb") as stream:
        stream.seek(MAX_SOURCE_BYTES)
        stream.write(b"x")
    inputs = (project, native, config, malformed, unknown, duplicate)
    original = [path.read_bytes() for path in inputs]

    async def probe() -> None:
        server = StdioServerParameters(command=sys.executable, args=["-m", "runoff_routing.mcp_server"], cwd=workspace)
        async with Client(server, read_timeout_seconds=60) as client:
            tools = await client.list_tools()
            assert len(tools.tools) == 12
            resources = await client.list_resources()
            assert len(resources.resources) == 5
            for resource in resources.resources:
                content = await client.read_resource(resource.uri)
                assert content.contents
            prompts = await client.list_prompts()
            assert len(prompts.prompts) == 1
            prompt = await client.get_prompt("plan_runoff_work", {"task": "validate synthetic routing"})
            assert prompt.messages
            catalog = await client.call_tool("list_capabilities", {})
            assert not catalog.is_error
            for name in ("validate_project", "monte_carlo", "export_cmd_package"):
                detail = await client.call_tool("describe_capability", {"name": name})
                assert not detail.is_error
            for area in ("model-editing", "interoperability", "execution", "rainfall", "reporting", "verification"):
                reference = await client.call_tool("get_api_reference", {"area": area})
                assert not reference.is_error
                assert "python_signature" in str(reference.structured_content)
            engines = await client.call_tool("get_engine_capabilities", {})
            assert not engines.is_error
            validated = await client.call_tool("validate_project", {"path": str(project)})
            assert not validated.is_error
            inspected = await client.call_tool("inspect_rorb_file", {"path": str(unknown)})
            assert not inspected.is_error
            assert "unsupported" in str(inspected.structured_content)

            single = workspace / "single.json"
            for engine in ("python-cmd", "python"):
                target = single if engine == "python-cmd" else workspace / "engineering.json"
                result = await client.call_tool(
                    "run_project",
                    {
                        "project_path": str(project),
                        "output_path": str(target),
                        "engine": engine,
                        "allow_write": True,
                    },
                )
                assert not result.is_error
                expected = run_engine_project(project, selection=EngineSelection.for_engine(engine))
                assert json.loads(target.read_text(encoding="utf-8")) == json.loads(expected.to_json())
                summary = await client.call_tool("get_result_summary", {"path": str(target)})
                assert not summary.is_error

            for request_name in ("mvp-events.json", "mvp-events-with-failure.json"):
                events = EXAMPLES / request_name
                prefix = workspace / request_name.removesuffix(".json")
                result = await client.call_tool(
                    "run_project_events",
                    {
                        "project_path": str(project),
                        "events_path": str(events),
                        "output_prefix": str(prefix),
                        "allow_write": True,
                    },
                )
                assert not result.is_error
                expected_batch = run_project_events(project, load_event_request(events))
                assert Path(f"{prefix}.json").read_text(encoding="utf-8") == expected_batch.to_json()
                assert Path(f"{prefix}.csv").read_text(encoding="utf-8") == expected_batch.to_csv()
                assert Path(f"{prefix}.txt").read_text(encoding="utf-8") == expected_batch.to_text()
                metadata = cast("dict[str, object]", result.structured_content)
                assert metadata["succeeded"] == expected_batch.succeeded
                assert metadata["failed_event_count"] == sum(
                    item.status != "computed_unvalidated" for item in expected_batch.outcomes
                )

            arr = await client.call_tool(
                "prepare_arr_design",
                {"config_path": str(config), "output_prefix": str(workspace / "arr"), "allow_write": True},
            )
            assert not arr.is_error
            expected_design = run_design_batch(config)
            assert expected_design.succeeded
            assert expected_design.effective["prepared_population"] == 10
            direct_paths = write_design_outputs(workspace / "direct-arr", expected_design)
            for path in direct_paths:
                actual = workspace / path.name.replace("direct-arr", "arr", 1)
                assert actual.read_bytes() == path.read_bytes()
                if actual.suffix == ".json" and not actual.name.endswith("events.json"):
                    summary = await client.call_tool("get_result_summary", {"path": str(actual)})
                    assert not summary.is_error
            summary = await client.call_tool(
                "summarize_arr_results",
                {"effective_path": str(workspace / "arr.effective.json"), "routed_path": str(workspace / "arr.json")},
            )
            assert not summary.is_error

            blocked = str(workspace / "blocked.json")
            base: dict[str, object] = {"project_path": str(project), "output_path": blocked, "allow_write": True}
            failures: tuple[tuple[str, dict[str, object]], ...] = (
                ("validate_project", {"path": str(oversized_project)}),
                ("validate_project", {"path": str(duplicate)}),
                ("validate_project", {"path": str(workspace / "missing.json")}),
                ("validate_project", {"path": str(malformed)}),
                ("inspect_event_request", {"path": str(malformed)}),
                ("get_result_summary", {"path": str(unknown)}),
                ("get_result_summary", {"path": str(huge)}),
                ("run_project", {**base, "allow_write": False}),
                ("run_project", {**base, "output_path": str(single)}),
                ("run_project", {**base, "engine": "python", "numerical_profile": "cmd-6.44"}),
                ("run_project", {**base, "project_path": str(native)}),
                ("run_project", {**base, "engine": "rorb-cmd"}),
            )
            saved = single.read_bytes()
            expected_codes = (
                "input_limit_exceeded",
                "invalid_input",
                "input_missing",
                "invalid_input",
                "invalid_input",
                "invalid_input",
                "input_limit_exceeded",
                "write_consent_required",
                "output_exists",
                "invalid_engine_selection",
                "native_engine_not_available",
                "native_engine_not_available",
            )
            for (tool, arguments), code in zip(failures, expected_codes, strict=True):
                result = await client.call_tool(tool, arguments)
                assert result.is_error, (tool, arguments)
                assert result.structured_content is None
                assert f"[{code}]" in str(result.content), (tool, code, result.content)
                assert private_key not in str(result.content)
                assert str(oversized_project) not in str(result.content)
                assert str(duplicate) not in str(result.content)
            assert not Path(blocked).exists()
            assert single.read_bytes() == saved

    asyncio.run(probe())
    assert [path.read_bytes() for path in inputs] == original
