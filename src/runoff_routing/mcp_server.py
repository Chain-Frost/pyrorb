"""Optional local MCP boundary for discovery and explicit, bounded computations.

Install the 'mcp' extra to start this module. Stdout is reserved for MCP frames.
"""

from __future__ import annotations

import inspect
import json
from collections import Counter
from dataclasses import asdict
from importlib import import_module
from pathlib import Path

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from .arr_design_batch import read_design_config, run_design_batch, write_design_outputs
from .arr_result_summary import read_deterministic_results
from .engine_execution import run_engine_project, write_engine_result
from .engine_types import CAPABILITIES, EngineId, EngineSelection
from .mcp_catalog import CATALOG, Exposure, find_capability
from .project_batch import load_event_request, write_batch_results
from .project_batch import run_project_events as execute_project_events
from .project_json import EmbeddedRun, load_project
from .rorb_inspect import inspect_file

INSTRUCTIONS = (
    "This local PyRORB server gives read-only discovery plus explicitly opted-in Python computations. "
    "Call list_capabilities, then describe_capability. Staged and planned entries are not runnable. "
    "Parsing and structural validation do not establish native parity, physical accuracy or engineering acceptance. "
    "Do not silently substitute another engine. Execution requires allow_write=true, new output "
    "destinations and only the python or python-cmd engine. Native CMD is not exposed here."
)
MAX_INSPECTION_BYTES = 32 * 1024 * 1024
MAX_MCP_EVENTS = 500
_READ_ONLY = ToolAnnotations(read_only_hint=True, open_world_hint=False)
_WRITES_RESULTS = ToolAnnotations(
    read_only_hint=False,
    destructive_hint=False,
    idempotent_hint=False,
    open_world_hint=False,
)
mcp = MCPServer("PyRORB", instructions=INSTRUCTIONS)


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
        "format",
        "schema_version",
        "engine",
        "numerical_profile",
        "expected_population",
        "prepared_population",
        "physical_print_sites",
        "software_execution_success",
        "software_population_complete",
        "selection_qualification",
        "routed_status_counts",
        "routed_native_reference_status",
        "site_population_count",
    )
    return {name: summary.get(name) for name in keys}


def _authorize_write(allow_write: bool) -> None:
    """Require deliberate acknowledgement before computing and creating files."""
    if not allow_write:
        message = "Execution is opt-in: set allow_write=true to calculate and create new result files"
        raise ValueError(message)


def _check_new_outputs(paths: tuple[Path, ...]) -> None:
    """Refuse existing destinations before computation; writers recheck using exclusive creation."""
    if len(set(paths)) != len(paths):
        message = "Duplicate MCP output destinations are not permitted"
        raise ValueError(message)
    for path in paths:
        if not path.parent.is_dir():
            message = f"Output directory must already exist: {path.parent}"
            raise ValueError(message)
        if path.exists() or path.is_symlink():
            message = f"Output destination already exists and cannot be overwritten: {path}"
            raise FileExistsError(message)


def _python_selection(
    project_path: Path, engine: EngineId | None, numerical_profile: str | None
) -> tuple[EngineSelection | None, EngineSelection]:
    """Validate the actual stored/overridden engine before any dispatcher can launch native CMD."""
    if engine is None and numerical_profile is not None:
        message = "numerical_profile requires an explicit engine override"
        raise ValueError(message)
    override = EngineSelection.for_engine(engine, numerical_profile) if engine is not None else None
    stored = load_project(project_path).project.engine
    effective = stored if override is None else override
    if effective.engine == "rorb-cmd":
        message = "Native rorb-cmd is not exposed through MCP execution; use the explicit native CLI"
        raise ValueError(message)
    return override, effective


@mcp.tool(annotations=_WRITES_RESULTS)
def run_project(
    project_path: str,
    output_path: str,
    engine: EngineId | None = None,
    numerical_profile: str | None = None,
    allow_write: bool = False,
) -> dict[str, object]:
    """Run one stored project event; explicitly opt in, and write a new JSON without overwriting."""
    _authorize_write(allow_write)
    target = Path(output_path).absolute()
    if target.suffix.lower() != ".json":
        message = "Single-project output must have a .json extension"
        raise ValueError(message)
    _check_new_outputs((target,))
    source = Path(project_path).absolute()
    override, _ = _python_selection(source, engine, numerical_profile)
    outcome = run_engine_project(source, selection=override)
    write_engine_result(target, outcome)
    return {
        "status": str(outcome.status),
        "project_id": outcome.project_id,
        "event_id": outcome.event_id,
        "project_sha256": outcome.project_sha256,
        "model_sha256": outcome.model_sha256,
        "stored_engine": str(outcome.stored_selection.engine),
        "effective_engine": str(outcome.effective_selection.engine),
        "numerical_profile": outcome.effective_selection.numerical_profile,
        "selection_source": outcome.selection_source,
        "native_parity_status": outcome.native_parity_status,
        "numerical_acceptance": outcome.numerical_acceptance,
        "implementation_revision": outcome.implementation_revision,
        "source_file_hashes": list(outcome.source_file_hashes),
        "diagnostics": [asdict(item) for item in outcome.diagnostics[:10]],
        "output_path": str(target),
        "hydrographs_in": str(target),
    }


@mcp.tool(annotations=_WRITES_RESULTS)
def run_project_events(
    project_path: str,
    events_path: str,
    output_prefix: str,
    engine: EngineId | None = None,
    numerical_profile: str | None = None,
    allow_write: bool = False,
) -> dict[str, object]:
    """Run a bounded, versioned event request; write new JSON/CSV/text and retain failed events."""
    _authorize_write(allow_write)
    prefix = Path(output_prefix).absolute()
    outputs = tuple(Path(f"{prefix}{suffix}") for suffix in (".json", ".csv", ".txt"))
    _check_new_outputs(outputs)
    source = Path(project_path).absolute()
    override, effective = _python_selection(source, engine, numerical_profile)
    events = load_event_request(Path(events_path).absolute())
    if len(events) > MAX_MCP_EVENTS:
        message = f"MCP batch exceeds the limit of {MAX_MCP_EVENTS} events"
        raise ValueError(message)
    report = execute_project_events(source, events, selection=override)
    written = write_batch_results(prefix, report)
    first = report.outcomes[0]
    failed = [outcome for outcome in report.outcomes if outcome.status != "computed_unvalidated"]
    return {
        "succeeded": report.succeeded,
        "status": "computed_unvalidated" if report.succeeded else "incomplete",
        "project_id": first.project_id,
        "project_sha256": first.project_sha256,
        "stored_engine": str(first.stored_selection.engine),
        "effective_engine": str(effective.engine),
        "numerical_profile": effective.numerical_profile,
        "selection_source": first.selection_source,
        "requested_event_count": len(report.outcomes),
        "status_counts": dict(sorted(Counter(str(item.status) for item in report.outcomes).items())),
        "failed_event_count": len(failed),
        "first_failures": [
            {
                "event_id": item.event_id,
                "status": str(item.status),
                "error_code": item.diagnostics[0].code if item.diagnostics else None,
            }
            for item in failed[:10]
        ],
        "implementation_revision": first.implementation_revision,
        "native_parity_status": "not_assessed",
        "numerical_acceptance": "unassessed",
        "output_paths": [str(path) for path in written],
        "full_diagnostics_in": str(written[0]),
    }


@mcp.tool(annotations=_WRITES_RESULTS)
def prepare_arr_design(config_path: str, output_prefix: str, allow_write: bool = False) -> dict[str, object]:
    """Prepare AND route a bounded ARR/BoM design ensemble, saving six existing report formats."""
    _authorize_write(allow_write)
    prefix = Path(output_prefix).absolute()
    outputs = tuple(
        Path(f"{prefix}{suffix}")
        for suffix in (".effective.json", ".events.json", ".json", ".csv", ".txt", ".summary.txt")
    )
    _check_new_outputs(outputs)
    source = Path(config_path).absolute()
    config = read_design_config(source)
    if config.engine.engine == "rorb-cmd":
        message = "Native rorb-cmd ARR batches are not exposed through MCP; use the explicit native CLI"
        raise ValueError(message)
    if len(config.durations_min) * len(config.aep_labels) * 10 > MAX_MCP_EVENTS:
        message = f"MCP design ensemble exceeds the limit of {MAX_MCP_EVENTS} events"
        raise ValueError(message)
    result = run_design_batch(source)
    written = write_design_outputs(prefix, result)
    effective = result.effective
    return {
        "succeeded": result.succeeded,
        "status": effective["status"],
        "method_profile": effective["method_profile"],
        "engine": str(config.engine.engine),
        "numerical_profile": config.engine.numerical_profile,
        "rainfall_preparation": config.rainfall_preparation,
        "expected_population": effective["expected_population"],
        "prepared_population": effective["prepared_population"],
        "input_population_complete": effective["input_population_complete"],
        "routing_status_counts": effective["routing_status_counts"],
        "source_files": effective["source_files"],
        "generated_input_reference_status": effective["generated_input_reference_status"],
        "routed_native_reference_status": effective["routed_native_reference_status"],
        "representative_event_rule": effective["representative_event_rule"],
        "critical_duration_rule": effective["critical_duration_rule"],
        "output_paths": [str(path) for path in written],
        "full_diagnostics_in": str(written[0]),
    }


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
