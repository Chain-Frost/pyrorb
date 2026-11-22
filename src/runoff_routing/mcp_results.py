"""Bounded, read-only projection of existing persisted JSON result contracts.

This is an agent summary, not another report reader, validator, numerical
comparator or engineering-acceptance assessment. Full ordinates stay on disk.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Never, cast

from .arr_design_batch import DESIGN_VERSION, EFFECTIVE_FORMAT
from .arr_result_summary import REPORT_FORMAT as ARR_SUMMARY_FORMAT
from .arr_result_summary import REPORT_VERSION as ARR_SUMMARY_VERSION
from .engine_types import ResultStatus
from .project_batch import REPORT_FORMAT as BATCH_FORMAT
from .project_batch import REQUEST_VERSION

MAX_RESULT_BYTES = 64 * 1024 * 1024
MAX_FAILURES = 10


def _fail(message: str) -> Never:
    raise ValueError(message)


def _object(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        _fail(f"{label} must be a JSON object")
    return cast("dict[str, object]", value)


def _string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        _fail(f"{label} must be a nonempty string")
    return value


def _int(value: object, label: str) -> int:
    if type(value) is not int or value < 0:
        _fail(f"{label} must be a nonnegative JSON integer")
    return value


def _pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for name, value in pairs:
        if name in result:
            _fail(f"Duplicate result JSON key: {name}")
        result[name] = value
    return result


def _constant(value: str) -> Never:
    _fail(f"Nonstandard JSON constant: {value}")


def _read(path: Path) -> tuple[dict[str, object], str, int]:
    if path.suffix.lower() != ".json":
        _fail("MCP result inspection accepts only .json files")
    if path.stat().st_size > MAX_RESULT_BYTES:
        _fail("MCP result inspection exceeds the 64 MiB limit")
    data = path.read_bytes()
    if not data or len(data) > MAX_RESULT_BYTES:
        _fail("Result file is empty, changed or oversized")
    try:
        value: object = json.loads(data.decode("utf-8-sig"), object_pairs_hook=_pairs, parse_constant=_constant)
    except (UnicodeError, TypeError, ValueError) as exc:
        message = f"Malformed result JSON: {exc}"
        raise ValueError(message) from exc
    return _object(value, "Result"), hashlib.sha256(data).hexdigest(), len(data)


def _selection(raw: object, label: str) -> dict[str, str]:
    selected = _object(raw, label)
    return {
        "engine": _string(selected.get("engine"), f"{label}.engine"),
        "numerical_profile": _string(selected.get("numerical_profile"), f"{label}.numerical_profile"),
    }


def _single(item: dict[str, object]) -> dict[str, object]:
    status = _string(item.get("status"), "status")
    if status not in {entry.value for entry in ResultStatus}:
        _fail("Unsupported single-project result status")
    graphs = item.get("hydrographs")
    diagnostics = item.get("diagnostics")
    if not isinstance(graphs, list) or not isinstance(diagnostics, list):
        _fail("Single-project result requires hydrographs and diagnostics lists")
    return {
        "kind": "single_project",
        "status": status,
        "project_id": _string(item.get("project_id"), "project_id"),
        "event_id": _string(item.get("event_id"), "event_id"),
        "project_sha256": item.get("project_sha256"),
        "model_sha256": item.get("model_sha256"),
        "stored_selection": _selection(item.get("stored_selection"), "stored_selection"),
        "effective_selection": _selection(item.get("effective_selection"), "effective_selection"),
        "selection_source": item.get("selection_source"),
        "hydrograph_count": len(graphs),
        "diagnostic_count": len(diagnostics),
        "first_diagnostic_codes": [
            entry.get("code") for entry in (_object(value, "diagnostic") for value in diagnostics[:MAX_FAILURES])
        ],
        "native_parity_status": item.get("native_parity_status"),
        "numerical_acceptance": item.get("numerical_acceptance"),
        "implementation_revision": item.get("implementation_revision"),
    }


def _batch(item: dict[str, object]) -> dict[str, object]:
    if item.get("schema_version") != REQUEST_VERSION:
        _fail("Unknown batch result version")
    data = item.get("outcomes")
    if not isinstance(data, list):
        _fail("Batch result is missing the outcomes list")
    rows = [_object(value, "Batch outcome") for value in data]
    expected = _int(item.get("requested_event_count"), "requested_event_count")
    if len(rows) != expected:
        _fail("Batch declared outcome count does not match actual records")
    statuses = [_string(row.get("status"), "outcome.status") for row in rows]
    if any(status not in {entry.value for entry in ResultStatus} for status in statuses):
        _fail("Unrecognised batch outcome status")
    observed = dict(sorted(Counter(statuses).items()))
    if item.get("status_counts") != observed:
        _fail("Persisted batch status counts do not match individual outcomes")
    failures = [row for row in rows if row["status"] != "computed_unvalidated"]
    return {
        "kind": "event_batch",
        "requested_event_count": expected,
        "completed_event_count": statuses.count("computed_unvalidated"),
        "status_counts": observed,
        "failed_event_count": len(failures),
        "first_failures": [
            {
                "event_id": row.get("event_id"),
                "status": row["status"],
                "diagnostic_codes": [
                    entry.get("code")
                    for entry in (
                        _object(value, "diagnostic") for value in cast("list[object]", row.get("diagnostics", []))[:1]
                    )
                ],
            }
            for row in failures[:MAX_FAILURES]
        ],
        "project_ids": sorted({_string(row.get("project_id"), "outcome.project_id") for row in rows})[:MAX_FAILURES],
        "native_parity_status": "not_assessed_by_summary",
    }


def _effective(item: dict[str, object]) -> dict[str, object]:
    if item.get("schema_version") != DESIGN_VERSION:
        _fail("Unknown ARR effective result version")
    fields = (
        "status",
        "method_profile",
        "expected_population",
        "prepared_population",
        "input_population_complete",
        "routing_status_counts",
        "generated_input_reference_status",
        "routed_native_reference_status",
        "representative_event_rule",
        "critical_duration_rule",
    )
    result = {name: item.get(name) for name in fields}
    return {"kind": "arr_effective", **result}


def _arr_summary(item: dict[str, object]) -> dict[str, object]:
    if item.get("schema_version") != ARR_SUMMARY_VERSION:
        _fail("Unknown persisted ARR result-summary version")
    fields = (
        "method_profile",
        "engine",
        "numerical_profile",
        "expected_population",
        "prepared_population",
        "physical_print_sites",
        "software_execution_success",
        "software_population_complete",
        "selection_qualification",
        "routed_native_reference_status",
        "routed_status_counts",
        "site_population_count",
    )
    result = {name: item.get(name) for name in fields}
    sites = result.get("physical_print_sites")
    if isinstance(sites, list):
        result["physical_print_sites"] = sites[:MAX_FAILURES]
        result["site_list_truncated"] = len(sites) > MAX_FAILURES
    return {"kind": "arr_summary", **result}


def summarize_result_file(path: Path) -> dict[str, object]:
    """Summarise known persisted result JSON, with file identity and no copied hydrographs."""
    source = path.absolute()
    record, digest, size = _read(source)
    kind = record.get("format")
    if kind == BATCH_FORMAT:
        report = _batch(record)
    elif kind == EFFECTIVE_FORMAT:
        report = _effective(record)
    elif kind == ARR_SUMMARY_FORMAT:
        report = _arr_summary(record)
    elif kind is None and {"status", "project_id", "effective_selection"} <= record.keys():
        report = _single(record)
    else:
        _fail("Unrecognised persisted runoff-routing result contract")
    return {
        "path": str(source),
        "source_sha256": digest,
        "size_bytes": size,
        "inspection_scope": "read_only_structural_projection_not_engineering_acceptance",
        "full_ordinates": "retained in source file; not included in MCP response",
        **report,
    }
