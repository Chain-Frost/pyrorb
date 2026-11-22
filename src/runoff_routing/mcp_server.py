"""Optional local, read-only MCP boundary; never duplicates hydrological kernels.

Install the 'mcp' extra to start this module. Stdout is reserved for MCP frames.
"""

from __future__ import annotations

import inspect
import json
from dataclasses import asdict
from importlib import import_module
from pathlib import Path

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from .arr_result_summary import read_deterministic_results
from .engine_types import CAPABILITIES
from .mcp_catalog import CATALOG, Exposure, find_capability
from .project_batch import load_event_request
from .project_json import EmbeddedRun, load_project
from .rorb_inspect import inspect_file

INSTRUCTIONS = (
    "This local server gives read-only discovery and inspection of python-runoff-routing. "
    "Call list_capabilities, then describe_capability. Staged and planned entries are not runnable. "
    "Parsing and structural validation do not establish native parity, physical accuracy or engineering acceptance. "
    "Do not silently substitute another engine. For execution use the documented CLI/Python API."
)
MAX_INSPECTION_BYTES = 32 * 1024 * 1024
_READ_ONLY = ToolAnnotations(read_only_hint=True, open_world_hint=False)
mcp = MCPServer("python-runoff-routing", instructions=INSTRUCTIONS)


@mcp.tool(annotations=_READ_ONLY)
def list_capabilities(exposure: Exposure | None = None) -> list[dict[str, object]]:
    """List agent-facing functions by state: mcp_tool, python_or_cli, staged or planned."""
    return [asdict(item) for item in CATALOG if exposure is None or item.exposure == exposure]


@mcp.tool(annotations=_READ_ONLY)
def describe_capability(name: str) -> dict[str, object]:
    """Describe only an indexed function, returning its real signature and module documentation."""
    item = find_capability(name)
    if item is None:
        return {"status": "unknown", "available_names": [candidate.name for candidate in CATALOG]}
    details: dict[str, object] = asdict(item)
    if item.entrypoint is not None and item.exposure in {"mcp_tool", "python_or_cli"}:
        module_name, symbol_name = item.entrypoint.rsplit(".", maxsplit=1)
        symbol = getattr(import_module(module_name), symbol_name)
        details["python_signature"] = str(inspect.signature(symbol))
        details["python_docstring"] = (inspect.getdoc(symbol) or "")[:2400]
    return details


@mcp.tool(annotations=_READ_ONLY)
def get_engine_capabilities() -> dict[str, object]:
    """Report the existing three-engine contract without inferring numerical acceptance."""
    return {
        "engines": [asdict(entry) for entry in CAPABILITIES],
        "temporary_project_default": "python-cmd/cmd-6.44",
        "intended_future_default": "python/engineering-v1",
        "scientific_qualification": "unassessed unless separately documented for a named profile",
        "source": "docs/ENGINES.md",
    }


@mcp.tool(annotations=_READ_ONLY)
def inspect_rorb_file(path: str) -> dict[str, object]:
    """Inspect a local RORB document, returning bounded diagnostics rather than raw contents."""
    source_path = Path(path).absolute()
    if source_path.stat().st_size > MAX_INSPECTION_BYTES:
        message = "MCP inspection refuses files larger than 32 MiB"
        raise ValueError(message)
    record = inspect_file(source_path)
    return {
        "path": str(source_path),
        "kind": record.kind,
        "status": record.status,
        "source_sha256": record.source.sha256,
        "source_size_bytes": record.source.size_bytes,
        "encoding": record.source.encoding,
        "diagnostic_count": len(record.diagnostics),
        "diagnostics": [asdict(entry) for entry in record.diagnostics[:50]],
        "diagnostics_truncated": len(record.diagnostics) > 50,
        "source_field_count": len(record.fields),
        "has_parameters": record.parameters is not None,
        "has_catchment": record.catchment is not None,
        "has_storm": record.storm is not None,
        "hydrograph_row_count": len(record.hydrographs.rows) if record.hydrographs is not None else None,
        "native_parity": "not_assessed",
    }


@mcp.tool(annotations=_READ_ONLY)
def validate_project(path: str) -> dict[str, object]:
    """Verify the project's JSON structure and pinned files; do not execute any engine."""
    loaded = load_project(Path(path))
    project = loaded.project
    embedded = isinstance(project.model_source, EmbeddedRun)
    return {
        "project_id": project.identifier,
        "validation_status": loaded.validation_status,
        "rainfall_profile": project.rainfall_profile,
        "source_kind": "embedded-run" if embedded else "rorb-files",
        "stored_engine": str(project.engine.engine),
        "stored_numerical_profile": project.engine.numerical_profile,
        "asset_count": len(project.assets),
        "verified_sources": [{"path": name, "sha256": digest} for name, digest in loaded.file_hashes],
        "original_inputs_match_effective": None if embedded else loaded.original_inputs_match_effective(),
        "numerical_acceptance": "not_assessed",
    }


@mcp.tool(annotations=_READ_ONLY)
def inspect_event_request(path: str) -> dict[str, object]:
    """Verify the versioned request envelope; individual events are checked during execution."""
    events = load_event_request(Path(path))
    return {
        "status": "request_envelope_valid",
        "event_count": len(events),
        "per_event_validation": "not_assessed",
        "notes": "An individual event can still be invalid or unsupported during routing",
    }


@mcp.tool(annotations=_READ_ONLY)
def summarize_arr_results(effective_path: str, routed_path: str) -> dict[str, object]:
    """Read persisted ARR outcomes and return compact summary metadata, not full hydrographs."""
    summary = read_deterministic_results(Path(effective_path), Path(routed_path)).data
    keys = (
        "format", "schema_version", "engine", "numerical_profile", "expected_population",
        "prepared_population", "physical_print_sites", "software_execution_success",
        "software_population_complete", "selection_qualification", "routed_status_counts",
        "routed_native_reference_status", "site_population_count",
    )
    return {name: summary.get(name) for name in keys}


@mcp.resource("runoff-routing://catalog")
def capability_catalog() -> str:
    """Read the documented available and placeholder capabilities."""
    return json.dumps([asdict(item) for item in CATALOG], indent=2)


@mcp.resource("runoff-routing://engines")
def engine_catalog() -> str:
    """Read the package's canonical engine declarations."""
    return json.dumps([asdict(item) for item in CAPABILITIES], indent=2)


@mcp.prompt()
def plan_runoff_work(task: str) -> str:
    """Guide an agent to existing APIs, tests and evidence boundaries for a requested task."""
    return (
        f"Task: {task}\n"
        "Inspect list_capabilities and describe_capability, then AGENTS.md, linked maintained "
        "documentation and current issues. Reuse existing kernels, project dispatcher and the "
        "canonical comparator/reader. Do not call placeholder entries or infer numerical parity "
        "from structural/software success. No GUI work."
    )


def main() -> None:
    """Start local stdio without writing logging or human-readable output to stdout."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
