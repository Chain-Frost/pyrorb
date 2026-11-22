"""Local MCP capability-status, protocol and read-only adapter tests."""

from __future__ import annotations

import asyncio
from pathlib import Path

from mcp import Client

from runoff_routing.mcp_catalog import CATALOG, find_capability
from runoff_routing.mcp_server import inspect_rorb_file, mcp


def test_catalog_has_explicit_placeholders() -> None:
    mc = find_capability("monte_carlo")
    assert mc is not None and mc.exposure == "staged"
    special = find_capability("advanced_structures")
    assert special is not None and special.exposure == "planned"
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
            }
            assert all(entry.annotations is not None and entry.annotations.read_only_hint for entry in listing.tools)
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
            assert len(resources.resources) == 2
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
