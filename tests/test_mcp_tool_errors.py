"""Expected MCP refusals remain actionable without changing direct Python exceptions."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest
from mcp import Client
from mcp.types import TextContent

from runoff_routing.engine_types import EngineSelection
from runoff_routing.mcp_server import mcp, run_project
from runoff_routing.project_json import MAX_SOURCE_BYTES, EmbeddedRun, Project, write_project
from runoff_routing.rorb_model import RunModel, from_json

EXAMPLE = Path(__file__).parents[1] / "examples" / "synthetic-run.json"


def _project(tmp_path: Path, *, name: str, engine: str = "python-cmd") -> Path:
    run = from_json(EXAMPLE.read_text(encoding="utf-8"))
    assert isinstance(run, RunModel)
    project = tmp_path / f"{name}.json"
    write_project(project, Project(name, "explicit", EmbeddedRun(run), engine=EngineSelection.for_engine(engine)))
    return project


def test_mcp_expected_refusals_have_codes_and_preserve_files(tmp_path: Path) -> None:
    project = _project(tmp_path, name="project")
    native = _project(tmp_path, name="native", engine="rorb-cmd")
    malformed = tmp_path / "malformed.json"
    malformed.write_text("{", encoding="utf-8")
    unknown = tmp_path / "unknown.json"
    unknown.write_text('{"format":"unknown"}', encoding="utf-8")
    present = tmp_path / "present.json"
    present.write_text("existing result\n", encoding="utf-8")
    request = tmp_path / "too_many.json"
    request.write_text(
        json.dumps(
            {
                "format": "python-runoff-routing-explicit-events",
                "schema_version": 1,
                "events": [{"event_id": f"event_{index}"} for index in range(501)],
            }
        ),
        encoding="utf-8",
    )
    private_key = "SECRET_DUPLICATE_INPUT_KEY_DO_NOT_DISCLOSE"
    duplicate = tmp_path / "private-duplicate.json"
    duplicate.write_text(json.dumps({private_key: "first"})[:-1] + f',"{private_key}":"second"' + "}", encoding="utf-8")
    oversized = tmp_path / "private-oversize.json"
    with oversized.open("wb") as stream:
        stream.seek(MAX_SOURCE_BYTES)
        stream.write(b"x")
    blocked = tmp_path / "blocked.json"
    original = {path: path.read_bytes() for path in (project, native, malformed, unknown, present, request, duplicate)}

    cases: tuple[tuple[str, dict[str, object], str], ...] = (
        (
            "run_project",
            {"project_path": str(project), "output_path": str(blocked)},
            "write_consent_required",
        ),
        (
            "run_project",
            {"project_path": str(project), "output_path": str(present), "allow_write": True},
            "output_exists",
        ),
        (
            "run_project",
            {
                "project_path": str(project),
                "output_path": str(tmp_path / "no_directory" / "output.json"),
                "allow_write": True,
            },
            "output_directory_missing",
        ),
        (
            "run_project",
            {"project_path": str(native), "output_path": str(blocked), "allow_write": True},
            "native_engine_not_available",
        ),
        (
            "run_project",
            {
                "project_path": str(project),
                "output_path": str(blocked),
                "numerical_profile": "cmd-6.44",
                "allow_write": True,
            },
            "invalid_engine_selection",
        ),
        (
            "run_project",
            {"project_path": str(tmp_path / "not-found.json"), "output_path": str(blocked), "allow_write": True},
            "input_missing",
        ),
        ("validate_project", {"path": str(oversized)}, "input_limit_exceeded"),
        ("validate_project", {"path": str(duplicate)}, "invalid_input"),
        ("validate_project", {"path": str(malformed)}, "invalid_input"),
        ("inspect_event_request", {"path": str(malformed)}, "invalid_input"),
        ("get_result_summary", {"path": str(unknown)}, "invalid_input"),
        (
            "run_project_events",
            {
                "project_path": str(project),
                "events_path": str(request),
                "output_prefix": str(tmp_path / "large_batch"),
                "allow_write": True,
            },
            "event_limit_exceeded",
        ),
    )

    async def probe() -> None:
        async with Client(mcp) as client:
            for name, arguments, code in cases:
                response = await client.call_tool(name, arguments)
                assert response.is_error, (name, code)
                assert response.structured_content is None
                message = " ".join(part.text for part in response.content if isinstance(part, TextContent))
                assert f"[{code}]" in message, (name, message)
                assert len(message) <= 380, (name, len(message))
                assert "Traceback" not in message
                assert 'File "' not in message
                assert private_key not in message
                assert str(duplicate) not in message
                assert str(oversized) not in message

    asyncio.run(probe())
    assert not blocked.exists()
    assert not (tmp_path / "large_batch.json").exists()
    assert {path: path.read_bytes() for path in original} == original
    assert oversized.stat().st_size == MAX_SOURCE_BYTES + 1


def test_mcp_wrapping_does_not_change_direct_python_errors(tmp_path: Path) -> None:
    project = _project(tmp_path, name="direct")
    output = tmp_path / "result.json"
    with pytest.raises(ValueError, match="allow_write=true"):
        run_project(str(project), str(output))
    assert not output.exists()
    output.write_text("original", encoding="utf-8")
    with pytest.raises(FileExistsError, match="already exists"):
        run_project(str(project), str(output), allow_write=True)
    assert output.read_text(encoding="utf-8") == "original"
