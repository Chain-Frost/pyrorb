"""Read-only, evidence-gated summaries of persisted ARR deterministic results.

This module never routes events or chooses a native representative. Its
observed-peak ranking is diagnostic, not a RORBwin representative rule.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import sys
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha256
from itertools import pairwise
from pathlib import Path
from statistics import fmean, median
from typing import Any, Never, cast

REPORT_FORMAT = "python-runoff-routing-arr2019-result-summary"
EFFECTIVE_FORMAT = "python-runoff-routing-arr2019-effective-events"
ROUTED_FORMAT = "python-runoff-routing-event-results"
REPORT_VERSION = 1
MAX_FILE_BYTES = 128 * 1024 * 1024
NATIVE_PROFILE_UNVERIFIED = "rorbwin-6.52/deterministic-design/report-reference-unqualified"


class ResultSummaryError(ValueError):
    """Invalid or incompatible persisted outcome population."""


def _fail(message: str) -> Never:
    raise ResultSummaryError(message)


def _object(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail(f"{label} must be an object")
    return cast("dict[str, Any]", value)


def _array(value: object, label: str) -> list[Any]:
    if not isinstance(value, list):
        _fail(f"{label} must be an array")
    return cast("list[Any]", value)


def _int(value: object, label: str) -> int:
    if type(value) is not int:
        _fail(f"{label} must be a JSON integer")
    return value


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        _fail(f"{label} must be nonempty text")
    return value


def _finite(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        _fail(f"{label} must be a finite number")
    return float(value)


def _pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for name, value in pairs:
        if name in result:
            _fail(f"Duplicate JSON field: {name}")
        result[name] = value
    return result


def _constant(value: str) -> Never:
    _fail(f"Nonstandard JSON constant: {value}")


def _read_json(path: Path) -> dict[str, Any]:
    if path.stat().st_size > MAX_FILE_BYTES:
        _fail(f"Oversized results file: {path}")
    data = path.read_bytes()
    if not data or len(data) > MAX_FILE_BYTES:
        _fail(f"Empty or changed results file: {path}")
    try:
        parsed: object = json.loads(data.decode("utf-8-sig"), object_pairs_hook=_pairs, parse_constant=_constant)
    except (UnicodeError, ValueError, TypeError) as exc:
        message = f"Invalid JSON in {path}: {exc}"
        raise ResultSummaryError(message) from exc
    return _object(parsed, str(path))


def _format_check(effective: Mapping[str, Any], routed: Mapping[str, Any]) -> None:
    for payload, name, expected in (
        (effective, "effective", EFFECTIVE_FORMAT),
        (routed, "routed", ROUTED_FORMAT),
    ):
        if payload.get("format") != expected or type(payload.get("schema_version")) is not int:
            _fail(f"Unrecognised {name} results contract")
        if payload["schema_version"] != REPORT_VERSION:
            _fail(f"Unsupported {name} results version")
    if effective.get("method_profile") != "arr2019-bom-published-arf-burst-only-v1":
        _fail("Unrecognised generated-rainfall method profile")


def _source_candidates(cell: Mapping[str, Any]) -> list[dict[str, object]]:
    names = _array(cell.get("unqualified_source_candidate_ids", []), "unqualified source IDs")
    orders = _array(cell.get("unqualified_source_candidate_orders", []), "unqualified source orders")
    if len(names) != len(orders):
        _fail("Source candidate ID/order lists disagree")
    return [
        {"original_tp_event_id": _text(name, "candidate EventID"), "source_order": _int(order, "source order")}
        for name, order in zip(names, orders, strict=True)
    ]


def _volume_map(routed: Mapping[str, Any]) -> dict[tuple[str, str], float | None]:
    found: dict[tuple[str, str], float | None] = {}
    for raw in _array(routed.get("volumes"), "routed.volumes"):
        row = _object(raw, "volume row")
        key = (_text(row.get("event_id"), "volume event ID"), _text(row.get("print_id"), "volume site ID"))
        if key in found:
            _fail(f"Repeated physical volume identity: {key}")
        value = row.get("physical_trapezoidal_volume_m3")
        found[key] = None if value is None else _finite(value, "physical volume")
    return found


def _horizon_audit(
    outcome: Mapping[str, Any], observed_samples: int, observed_times: int
) -> tuple[dict[str, Any], float | None]:
    """Get the declared N+1 population and validated timestep without inventing defaults."""
    settings = _object(outcome.get("effective_inputs"), "effective_inputs")
    increments = settings.get("calculation_increments")
    timestep_token = settings.get("timestep_hours")
    declared_count = increments + 1 if type(increments) is int and increments >= 1 else None
    audit = {
        "observed_sample_count": observed_samples,
        "observed_time_count": observed_times,
        "declared_sample_count": declared_count,
        "declared_timestep_hours": timestep_token if isinstance(timestep_token, str) else None,
    }
    if declared_count is None or not isinstance(timestep_token, str):
        return audit, None
    try:
        timestep = float(timestep_token)
    except ValueError:
        return audit, None
    if not math.isfinite(timestep) or timestep <= 0:
        return audit, None
    return audit, timestep


def _clock_matches_declared(times: list[Any], timestep: float) -> bool:
    """Only zero-origin, full-horizon elapsed clocks match the #136 Python result contract."""
    if not all(isinstance(item, str) for item in times):
        return False
    try:
        clock = [float(item) for item in times]
    except ValueError:
        return False
    if any(not math.isfinite(time) for time in clock):
        return False
    if len(clock) < 2 or any(b <= a for a, b in pairwise(clock)):
        return False
    return all(
        math.isclose(time, index * timestep, rel_tol=1e-10, abs_tol=1e-9)
        for index, time in enumerate(clock)
    )


def _metric(outcome: Mapping[str, Any], graph: Mapping[str, Any], volume: float | None) -> dict[str, Any]:
    """Accept only full declared-horizon series; retain audit counts for partial outcomes."""
    values = _array(graph.get("discharge_m3_s"), "discharge")
    times = _array(outcome.get("physical_time_hours"), "physical times")
    audit, timestep = _horizon_audit(outcome, len(values), len(times))
    if timestep is None:
        return {**audit, "metric_status": "incomplete_output", "metric_reason": "invalid_declared_horizon"}
    if len(values) != audit["declared_sample_count"] or len(times) != audit["declared_sample_count"]:
        return {**audit, "metric_status": "incomplete_output", "metric_reason": "declared_horizon_mismatch"}
    if volume is None:
        return {**audit, "metric_status": "incomplete_output", "metric_reason": "missing_physical_volume"}
    if not _clock_matches_declared(times, timestep):
        return {**audit, "metric_status": "incomplete_output", "metric_reason": "declared_time_grid_mismatch"}
    if graph.get("units") != "m3/s":
        return {**audit, "metric_status": "incomplete_output", "metric_reason": "unsupported_discharge_units"}

    discharge = [_finite(item, "discharge ordinate") for item in values]
    peak = max(discharge)
    peak_indices = [index for index, item in enumerate(discharge) if item == peak]
    clock = json.dumps(times, ensure_ascii=False, separators=(",", ":"))
    return {
        **audit,
        "metric_status": "complete",
        "peak_m3_s": peak,
        "peak_sample_indices": peak_indices,
        "peak_time_hours": [times[i] for i in peak_indices],
        "sample_count": len(discharge),
        "time_start_hours": times[0],
        "time_end_hours": times[-1],
        "time_grid_sha256": sha256(clock.encode("utf-8")).hexdigest(),
        "timestep_hours": audit["declared_timestep_hours"],
        "physical_trapezoidal_volume_m3": volume,
        "native_inclusive_reported_volume_m3": None,
    }


def _members_by_cell(
    effective: Mapping[str, Any], cells: list[dict[str, Any]]
) -> dict[tuple[int, str], list[dict[str, Any]]]:
    result: dict[tuple[int, str], list[dict[str, Any]]] = {
        (_int(cell.get("duration_min"), "cell.duration_min"), _text(cell.get("aep_label"), "cell.aep_label")): []
        for cell in cells
    }
    for raw in _array(effective.get("members"), "effective.members"):
        member = _object(raw, "member")
        key = (
            _int(member.get("duration_min"), "member.duration_min"),
            _text(member.get("aep_label"), "member.aep_label"),
        )
        if key not in result:
            _fail(f"Member outside declared duration/AEP cells: {key}")
        result[key].append(member)
    return result


def _outcome_index(
    effective: Mapping[str, Any], routed: Mapping[str, Any]
) -> tuple[dict[str, dict[str, Any]], tuple[str, ...]]:
    selection = _object(effective.get("selection"), "effective.selection")
    project = _object(_object(effective.get("source_files"), "source files").get("project"), "project source")
    indexed: dict[str, dict[str, Any]] = {}
    sites: tuple[str, ...] | None = None
    for raw in _array(routed.get("outcomes"), "routed.outcomes"):
        outcome = _object(raw, "outcome")
        identifier = _text(outcome.get("event_id"), "routed event ID")
        if identifier in indexed:
            _fail(f"Duplicate routed event: {identifier}")
        selected = _object(outcome.get("effective_selection"), "effective selection")
        if (selected.get("engine"), selected.get("numerical_profile")) != (
            selection.get("engine"),
            selection.get("numerical_profile"),
        ):
            _fail(f"Mixed engine or numerical method for {identifier}")
        if outcome.get("project_sha256") != project.get("sha256"):
            _fail(f"Mixed project/source SHA-256 for {identifier}")
        requested = tuple(_text(item, "print site ID") for item in _array(outcome.get("requested_print_ids"), "sites"))
        if len(requested) != len(set(requested)) or (sites is not None and requested != sites):
            _fail("Mixed or duplicated physical print-site populations")
        graphs = _array(outcome.get("hydrographs"), "hydrographs")
        if any(_object(graph, "hydrograph").get("print_id") not in requested for graph in graphs):
            _fail(f"Routed hydrograph has undeclared physical print site: {identifier}")
        sites = requested
        indexed[identifier] = outcome
    if _int(routed.get("requested_event_count"), "requested_event_count") != len(indexed):
        _fail("Routed population count does not match the retained outcomes")
    return indexed, sites or ()


def _member_row(
    member: Mapping[str, Any],
    site: str | None,
    outcome: Mapping[str, Any] | None,
    volumes: Mapping[tuple[str, str], float | None],
) -> dict[str, Any]:
    identifier = member.get("event_id")
    status = outcome.get("status") if outcome is not None else member.get("status")
    row: dict[str, Any] = {
        "event_id": identifier,
        "original_tp_event_id": member.get("original_tp_id"),
        "source_order": member.get("source_order"),
        "ensemble_order": member.get("ensemble_order"),
        "native_ordinal": None,  # Not established by #136 or an admitted #142 report.
        "site_id": site,
        "routing_status": status,
        "input_status": member.get("status"),
        "execution_error_code": member.get("execution_error_code"),
        "metric_status": "not_computed",
        "diagnostics": outcome.get("diagnostics") if outcome is not None else None,
    }
    if outcome is None or site is None or status != "computed_unvalidated":
        return row
    graphs = [
        _object(raw, "hydrograph")
        for raw in _array(outcome.get("hydrographs"), "hydrographs")
        if _object(raw, "hydrograph").get("print_id") == site
    ]
    if len(graphs) != 1:
        row["metric_status"] = "incomplete_output"
        return row
    graph = graphs[0]
    row["site_label"] = graph.get("label")
    row["native_column_id"] = graph.get("native_column_id")
    row.update(_metric(outcome, graph, volumes.get((_text(identifier, "event ID"), site))))
    return row


def _rank_observed(rows: list[dict[str, Any]]) -> list[dict[str, object]]:
    """Competition ranks of observed peaks only; ties never select an event."""
    valid = [row for row in rows if row["metric_status"] == "complete"]
    sorted_rows = sorted(valid, key=lambda row: -_finite(row["peak_m3_s"], "peak"))
    ranks: list[dict[str, object]] = []
    for ordinal, row in enumerate(sorted_rows, start=1):
        peak = _finite(row["peak_m3_s"], "peak")
        rank = ranks[-1]["rank"] if ranks and ranks[-1]["peak_m3_s"] == peak else ordinal
        ranks.append(
            {
                "rank": rank,
                "peak_m3_s": peak,
                "event_id": row["event_id"],
                "original_tp_event_id": row["original_tp_event_id"],
                "source_order": row["source_order"],
                "ensemble_order": row["ensemble_order"],
                "native_ordinal": None,
            }
        )
    return ranks


def _site_summary(
    cell: Mapping[str, Any], site: str | None, rows: list[dict[str, Any]], expected: int
) -> dict[str, Any]:
    complete = [row for row in rows if row["metric_status"] == "complete"]
    peaks = [_finite(row["peak_m3_s"], "peak") for row in complete]
    signatures = {(row["time_grid_sha256"], row["timestep_hours"], row.get("site_label")) for row in complete}
    accepted_members = [row for row in rows if isinstance(row["event_id"], str)]
    eligible = (
        cell.get("status") == "ready"
        and site is not None
        and len(accepted_members) == expected
        and len(complete) == expected
        and len(signatures) == 1
    )
    # Do not pool peaks from incompatible physical time grids or site labels.
    comparable = len(signatures) <= 1
    ranking = _rank_observed(rows) if comparable else []
    ties = [
        {"rank": rank, "event_ids": [item["event_id"] for item in ranking if item["rank"] == rank]}
        for rank in dict.fromkeys(item["rank"] for item in ranking)
        if sum(item["rank"] == rank for item in ranking) > 1
    ]
    return {
        "duration_min": cell["duration_min"],
        "aep_label": cell["aep_label"],
        "aep_percent": cell.get("aep_percent"),
        "site_id": site,
        "expected_member_count": expected,
        "prepared_member_count": len(accepted_members),
        "completed_member_count": len(complete),
        "failed_or_incomplete_member_count": len(accepted_members) - len(complete),
        "not_prepared_member_count": expected - len(accepted_members),
        "source_candidate_count": len(cell.get("unqualified_source_candidate_ids", [])),
        "horizon_and_site_comparable": len(signatures) == 1 and bool(complete),
        "time_grid_sha256": complete[0]["time_grid_sha256"] if comparable and complete else None,
        "complete_comparable_population": eligible,
        "observed_peak_min_m3_s": min(peaks) if comparable and peaks else None,
        "observed_peak_median_m3_s": median(peaks) if comparable and peaks else None,
        "observed_peak_mean_m3_s": fmean(peaks) if comparable and peaks else None,
        "observed_peak_max_m3_s": max(peaks) if comparable and peaks else None,
        "diagnostic_peak_ranking": ranking,
        "diagnostic_tie_groups": ties,
        "members": rows,
        "unqualified_source_candidates": _source_candidates(cell),
        "representative_selection": {
            "candidate_native_profile": NATIVE_PROFILE_UNVERIFIED,
            "statistic": "peak_m3_s_observed_diagnostic_only",
            "population_complete": eligible,
            "rule_status": "unverified",
            "reported_by_native": None,
            "calculated_by_package": None,
            "selection_reason": "No qualified #142 native reported-reference binding and distinguishing rule evidence",
        },
    }


@dataclass(frozen=True, slots=True)
class DeterministicSummary:
    """Derived aggregate; original full hydrographs remain in the input results file."""

    data: dict[str, Any]

    def to_json(self) -> str:
        return json.dumps(self.data, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"

    def to_csv(self) -> str:
        columns = (
            "duration_min",
            "aep_label",
            "site_id",
            "event_id",
            "original_tp_event_id",
            "source_order",
            "ensemble_order",
            "native_ordinal",
            "input_status",
            "routing_status",
            "metric_status",
            "metric_reason",
            "declared_sample_count",
            "observed_sample_count",
            "observed_time_count",
            "declared_timestep_hours",
            "peak_m3_s",
            "peak_time_hours",
            "physical_trapezoidal_volume_m3",
            "diagnostic_peak_rank",
            "selection_status",
        )
        output = io.StringIO(newline="")
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(columns)
        for cell in _array(self.data["cell_sites"], "cell_sites"):
            ranks = {item["event_id"]: item["rank"] for item in cell["diagnostic_peak_ranking"]}
            for member in cell["members"]:
                fields = {
                    **member,
                    "duration_min": cell["duration_min"],
                    "aep_label": cell["aep_label"],
                    "diagnostic_peak_rank": ranks.get(member["event_id"]),
                    "selection_status": "unverified",
                }
                if fields.get("peak_time_hours") is not None:
                    fields["peak_time_hours"] = json.dumps(fields["peak_time_hours"], separators=(",", ":"))
                writer.writerow([fields.get(key) for key in columns])
            for candidate in cell["unqualified_source_candidates"]:
                # Candidates are visible, but are not accepted ensemble members.
                fields = {
                    "duration_min": cell["duration_min"],
                    "aep_label": cell["aep_label"],
                    "site_id": cell["site_id"],
                    "original_tp_event_id": candidate["original_tp_event_id"],
                    "source_order": candidate["source_order"],
                    "input_status": "unqualified_source_candidate",
                    "routing_status": "not_dispatched",
                    "metric_status": "not_computed",
                    "selection_status": "unverified",
                }
                writer.writerow([fields.get(key) for key in columns])
        return output.getvalue()

    def to_text(self) -> str:
        lines = [
            "ARR2019 deterministic outcome summaries (observed software metrics)",
            f"Engine: {self.data['engine']}/{self.data['numerical_profile']}",
            f"Prepared events: {self.data['prepared_population']}/{self.data['expected_population']}",
            f"Software population complete: {self.data['software_population_complete']}",
            f"Physical print sites: {self.data['physical_print_sites']}",
            "Generated-input qualification: not_assessed; routed native qualification: not_assessed",
            "Native representative and critical-duration selection: UNVERIFIED (no event/duration selected)",
        ]
        lines.extend(
            f"{cell['duration_min']} min / {cell['aep_label']} / {cell['site_id'] or 'SITE UNKNOWN'}: "
            f"complete {cell['completed_member_count']}/{cell['expected_member_count']}; "
            f"observed peak min/median/max (m3/s): "
            f"{cell['observed_peak_min_m3_s']}/{cell['observed_peak_median_m3_s']}/"
            f"{cell['observed_peak_max_m3_s']}; comparable={cell['complete_comparable_population']}"
            for cell in self.data["cell_sites"]
        )
        return "\n".join(lines) + "\n"


def _validate_ready_members(
    cell: Mapping[str, Any],
    selected: list[dict[str, Any]],
    selection: Mapping[str, Any],
    key: tuple[int, str],
) -> None:
    """Reject missing or re-ordered eligible members and mixed design-loss policies."""
    if cell.get("status") != "ready":
        return
    if len(selected) != _int(cell["expected_count"], "expected count"):
        _fail(f"Ready cell has a missing temporal pattern: {key}")
    orders = [_int(row.get("ensemble_order"), "ensemble order") for row in selected]
    if orders != list(range(1, len(orders) + 1)):
        _fail(f"Ensemble ordinal is not preserved for {key}")
    for row in selected:
        _text(row.get("original_tp_id"), "original source EventID")
        _int(row.get("source_order"), "original source order")
        loss = _object(row.get("loss"), "effective loss selection")
        if loss.get("method") != selection.get("loss_profile"):
            _fail(f"Mixed design-loss method for {key}")


def _validate_population(
    effective: Mapping[str, Any],
    routed: Mapping[str, Any],
    cells: list[dict[str, Any]],
    selection: Mapping[str, Any],
) -> tuple[dict[tuple[int, str], list[dict[str, Any]]], dict[str, dict[str, Any]], tuple[str, ...]]:
    """Bind exactly the generated event ledger to all existing routed outcomes."""
    members = _members_by_cell(effective, cells)
    outcomes, sites = _outcome_index(effective, routed)
    seen: set[str] = set()
    for cell in cells:
        key = (_int(cell["duration_min"], "duration"), _text(cell["aep_label"], "AEP"))
        selected = [row for row in members[key] if isinstance(row.get("event_id"), str)]
        if len(selected) != _int(cell.get("ready_count"), "cell.ready_count"):
            _fail(f"Prepared event count inconsistent for {key}")
        _validate_ready_members(cell, selected, selection, key)
        for row in selected:
            event_id = _text(row.get("event_id"), "member.event_id")
            if event_id in seen or event_id not in outcomes:
                _fail(f"Missing or duplicated routed member: {event_id}")
            seen.add(event_id)
            outcome = outcomes[event_id]
            if row.get("execution_status") != outcome.get("status"):
                _fail(f"Execution status mismatch for {event_id}")
            if row.get("effective_model_sha256") != outcome.get("model_sha256"):
                _fail(f"Effective model SHA-256 mismatch for {event_id}")
    if set(outcomes) != seen or len(seen) != _int(effective.get("prepared_population"), "prepared_population"):
        _fail("Persisted routing population is not the generated design population")
    if sum(_int(cell.get("expected_count"), "expected count") for cell in cells) != _int(
        effective.get("expected_population"), "expected_population"
    ):
        _fail("Expected population is inconsistent with its per-cell denominators")
    return members, outcomes, sites


def _critical_duration_records(
    aeps: list[Any], sites: tuple[str, ...], summaries: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Retain all duration candidates; forbid unevidenced native duration selection."""
    critical: list[dict[str, Any]] = []
    for aep in aeps:
        for site in sites or (None,):
            population = [row for row in summaries if row["aep_label"] == aep and row["site_id"] == site]
            critical.append(
                {
                    "aep_label": aep,
                    "site_id": site,
                    "considered_durations_min": [row["duration_min"] for row in population],
                    "complete_comparable_within_each_duration": all(
                        row["complete_comparable_population"] for row in population
                    ),
                    "comparable_across_durations": len(
                        {row["time_grid_sha256"] for row in population if row["time_grid_sha256"] is not None}
                    )
                    == 1
                    and bool(population),
                    "duration_aggregation_rule": None,
                    "selected_duration_min": None,
                    "selection_status": "unverified",
                    "reason": "No qualified native duration-aggregation/representative rule or common-horizon policy",
                }
            )
    return critical


def _bound_outcome(member: Mapping[str, Any], outcomes: Mapping[str, dict[str, Any]]) -> dict[str, Any] | None:
    """An unprepared input candidate has no synthetic routing identity."""
    identifier = member.get("event_id")
    return outcomes.get(identifier) if isinstance(identifier, str) else None


def summarize_deterministic_results(effective: Mapping[str, Any], routed: Mapping[str, Any]) -> DeterministicSummary:
    """Summarise existing #136/#119 persisted structures without re-execution or native claims."""
    _format_check(effective, routed)
    selection = _object(effective.get("selection"), "selection")
    durations = _array(selection.get("duration_axis_min"), "duration axis")
    aeps = _array(selection.get("aep_label_axis"), "AEP axis")
    axes = [(_int(duration, "duration"), _text(aep, "AEP")) for duration in durations for aep in aeps]
    cells = [_object(raw, "cell") for raw in _array(effective.get("cells"), "cells")]
    if [(cell.get("duration_min"), cell.get("aep_label")) for cell in cells] != axes:
        _fail("Cell order/population differs from the recorded duration/AEP axes")
    members, outcomes, sites = _validate_population(effective, routed, cells, selection)
    volumes = _volume_map(routed)
    summaries: list[dict[str, Any]] = []
    for cell in cells:
        key = (cell["duration_min"], cell["aep_label"])
        for site in sites or (None,):
            rows = [_member_row(member, site, _bound_outcome(member, outcomes), volumes) for member in members[key]]
            summaries.append(_site_summary(cell, site, rows, _int(cell["expected_count"], "expected count")))
    critical = _critical_duration_records(aeps, sites, summaries)
    complete = bool(sites) and all(row["complete_comparable_population"] for row in summaries)
    software_execution_success = bool(outcomes) and all(
        item.get("status") == "computed_unvalidated" for item in outcomes.values()
    )
    return DeterministicSummary(
        {
            "format": REPORT_FORMAT,
            "schema_version": REPORT_VERSION,
            "source_effective_format": EFFECTIVE_FORMAT,
            "source_routed_format": ROUTED_FORMAT,
            "method_profile": effective.get("method_profile"),
            "engine": selection.get("engine"),
            "numerical_profile": selection.get("numerical_profile"),
            "duration_axis_min": durations,
            "aep_label_axis": aeps,
            "source_files": effective.get("source_files"),
            "expected_population": effective["expected_population"],
            "prepared_population": len(outcomes),
            "physical_print_sites": list(sites),
            "site_identity_status": "from_common_requested_print_ids" if sites else "unknown_no_routed_outcome",
            "software_execution_success": software_execution_success,
            "software_population_complete": complete,
            "generated_input_reference_status": effective.get("generated_input_reference_status"),
            "routed_native_reference_status": effective.get("routed_native_reference_status"),
            "selection_qualification": "unverified",
            "native_reference_profile_candidate": NATIVE_PROFILE_UNVERIFIED,
            "site_population_count": len(summaries),
            "cell_sites": summaries,
            "critical_durations": critical,
            "routed_status_counts": dict(
                sorted(Counter(outcome.get("status") for outcome in outcomes.values()).items())
            ),
            "original_full_hydrographs_preserved_in": "input routed JSON; this report is non-destructive",
        }
    )


def read_deterministic_results(effective_path: Path, routed_path: Path) -> DeterministicSummary:
    """Read exactly the two current persisted output contracts, never source project files."""
    return summarize_deterministic_results(_read_json(effective_path), _read_json(routed_path))


def write_summary(prefix: Path, summary: DeterministicSummary) -> tuple[Path, Path, Path]:
    """Exclusive output with rollback; original ensemble and hydrograph files are untouched."""
    paths = tuple(Path(f"{prefix}{suffix}") for suffix in (".analysis.json", ".analysis.csv", ".analysis.txt"))
    if any(path.exists() or path.is_symlink() for path in paths):
        _fail("Summary destination already exists; no files overwritten")
    contents = (summary.to_json(), summary.to_csv(), summary.to_text())
    created: list[Path] = []
    try:
        for path, content in zip(paths, contents, strict=True):
            with path.open("xb") as handle:
                created.append(path)
                handle.write(content.encode("utf-8"))
    except OSError:
        for path in created:
            path.unlink(missing_ok=True)
        raise
    return cast("tuple[Path, Path, Path]", paths)


def main(argv: list[str] | None = None) -> int:
    """Summarise persisted .effective.json and .json files without re-running routing."""
    parser = argparse.ArgumentParser(prog="python -m runoff_routing.arr_result_summary")
    parser.add_argument("effective", type=Path)
    parser.add_argument("routed", type=Path)
    parser.add_argument("output_prefix", type=Path)
    try:
        options = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2
    try:
        summary = read_deterministic_results(options.effective, options.routed)
        write_summary(options.output_prefix, summary)
    except (ResultSummaryError, OSError, ValueError, TypeError, KeyError) as exc:
        print(f"Deterministic result summary failed: {exc}", file=sys.stderr)
        return 2
    print(summary.to_text(), end="")
    return 0 if summary.data["software_population_complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
