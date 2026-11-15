"""Resumable Monte Carlo execution through the existing prepared #119 event iterator.

Sampling, probability-to-depth conversion and frequency interpolation are owned by
#146 and #147. This implementation stores no full batch of Q arrays in memory.
The JSONL execution request is an immutable boundary, not a second sample plan.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass
from decimal import Decimal
from itertools import islice
from pathlib import Path
from typing import cast

from .engine_provenance import identify_implementation, verify_installed_wheel
from .engine_types import EngineOutcome, EngineSelection
from .monte_carlo_effective import (
    MAX_LINE_BYTES,
    EffectiveMCEvent,
    encode_jsonl_line,
    parse_jsonl_line,
    sha256_file,
    iter_effective_events,
    read_header,
    validate_effective_request,
)
from .project_batch import ProjectBatchReport, iter_project_events, run_project_events, write_batch_results
from .project_json import LoadedProject, load_project

LEDGER_FORMAT = "python-runoff-routing-mc-event-ledger"
LEDGER_VERSION = 1
_STATUS_OK = "computed_unvalidated"
_LEDGER_ROW_KEYS = {
    "sample_id",
    "scenario_id",
    "duration_min",
    "stratum_id",
    "probability_weight",
    "effective_event_sha256",
    "effective_model_sha256",
    "status",
    "diagnostics",
    "requested_print_ids",
    "sites",
}


class MCRunError(ValueError):
    """A stale checkpoint, unsupported engine or invalid model/ledger."""


@dataclass(frozen=True, slots=True)
class MCRunSummary:
    expected: int
    recorded: int
    status_counts: dict[str, int]
    zero_peak_events: int

    @property
    def complete(self) -> bool:
        return self.recorded == self.expected and self.status_counts == {_STATUS_OK: self.expected}

    def to_text(self) -> str:
        return (
            f"MC events: {self.recorded}/{self.expected} checkpointed\n"
            f"Statuses: {json.dumps(self.status_counts, sort_keys=True)}\n"
            f"All-site zero-peak successful events: {self.zero_peak_events}\n"
            f"Software execution complete: {str(self.complete).lower()}\n"
            "Flood-frequency estimate: not calculated here (#147). Native/statistical parity: not assessed.\n"
        )


def _project_subset(loaded: LoadedProject) -> None:
    run = loaded.run
    if (
        run.parameters.num_isa != 1
        or run.parameters.loss_model != 1
        or len(run.parameters.losses) != 1
        or run.parameters.num_bursts != 1
        or run.storm.pattern_basis != "percent_of_depth"
        or run.storm.preburst_bins
        or any(subarea.impervious_fraction != 0 for subarea in run.catchment.subareas)
        or len(run.storm.subarea_ids) != len(run.catchment.subareas)
        or any(asset.role != "reference" for asset in loaded.project.assets)
        or loaded.project.rainfall_profile not in ("explicit", "legacy-rorb")
    ):
        message = "MC execution currently requires a fully pervious, single-ISA, IL/CL explicit-storm project"
        raise MCRunError(message)


def _fixed_parameters(record: EffectiveMCEvent, loaded: LoadedProject) -> None:
    losses = record.event.losses
    storm = record.event.storm
    if losses is None or storm is None:
        message = "Explicit storm and losses required"
        raise MCRunError(message)
    if Decimal(cast("str", losses["continuing"])) != loaded.run.parameters.losses[0].continuing or len(
        cast("list[object]", storm["depths_mm"])
    ) != len(loaded.run.storm.subarea_ids):
        message = "MC subset fixes continuing loss and pervious subarea source population"
        raise MCRunError(message)


def _header(
    project: LoadedProject,
    input_sha256: str,
    *,
    selection: EngineSelection,
    wheel_artifact: Path | None,
    request_path: Path,
) -> dict[str, object]:
    if selection.engine != "python-cmd" or selection.numerical_profile != "cmd-6.44":
        message = "Current MC routing supports only explicitly selected python-cmd/cmd-6.44"
        raise MCRunError(message)
    identity = identify_implementation()
    wheel_sha256 = verify_installed_wheel(wheel_artifact) if wheel_artifact is not None else None
    header = read_header(request_path)
    return {
        "format": LEDGER_FORMAT,
        "schema_version": LEDGER_VERSION,
        "request_sha256": input_sha256,
        "plan_sha256": header.plan_sha256,
        "policy_id": header.policy_id,
        "source_files": [{"path": f.path, "sha256": f.sha256} for f in header.source_files],
        "populations": [p.to_dict() for p in header.populations],
        "expected_event_count": header.event_count,
        "project_sha256": hashlib.sha256(project.original_json_bytes).hexdigest(),
        "project_file_hashes": [list(pair) for pair in project.file_hashes],
        "engine": selection.engine,
        "numerical_profile": selection.numerical_profile,
        "implementation_revision": identity.revision,
        "package_version": identity.package_version,
        "wheel_sha256": wheel_sha256,
    }


def _event_row(event: EffectiveMCEvent, result: EngineOutcome) -> dict[str, object]:
    sites: list[dict[str, object]] = []
    status = result.status
    diagnostics = [{"code": item.code, "message": item.message} for item in result.diagnostics]
    if status == _STATUS_OK:
        if len(result.hydrographs) != len(result.requested_print_ids) or {
            item.print_id for item in result.hydrographs
        } != set(result.requested_print_ids):
            status = "incomplete_output"
            diagnostics.append({"code": "mc_missing_site", "message": "Missing or duplicate requested output site"})
        for graph in result.hydrographs:
            ordinates = graph.discharge_m3_s
            if not ordinates or not all(math.isfinite(value) for value in ordinates):
                status = "incomplete_output"
                diagnostics.append({"code": "mc_nonfinite_peak", "message": "Unusable discharge series"})
                break
            peak = max(ordinates)
            index = ordinates.index(peak)
            sites.append(
                {
                    "print_id": graph.print_id,
                    "label": graph.label,
                    "peak_m3_s": peak,
                    "peak_index": index,
                    "peak_time_hours": (
                        result.physical_time_hours[index] if index < len(result.physical_time_hours) else None
                    ),
                }
            )
        if status != _STATUS_OK:
            sites = []
    return {
        "sample_id": event.sample_id,
        "scenario_id": event.scenario_id,
        "duration_min": event.duration_min,
        "stratum_id": event.stratum_id,
        "probability_weight": str(event.probability_weight),
        "effective_event_sha256": event.digest(),
        "effective_model_sha256": result.model_sha256,
        "status": status,
        "diagnostics": diagnostics,
        "requested_print_ids": list(result.requested_print_ids),
        "sites": sites,
    }


def _read_ledger(path: Path) -> Iterator[dict[str, object]]:
    with path.open("rb") as stream:
        first = stream.readline(MAX_LINE_BYTES + 1)
        if not first:
            message = "Empty MC ledger"
            raise MCRunError(message)
        raw_header = parse_jsonl_line(first)
        if not isinstance(raw_header, dict):
            message = "Invalid MC ledger header"
            raise MCRunError(message)
        yield cast("dict[str, object]", raw_header)
        for ordinal, raw in enumerate(iter(lambda: stream.readline(MAX_LINE_BYTES + 1), b""), start=1):
            parsed = parse_jsonl_line(raw)
            if not isinstance(parsed, dict):
                message = f"Invalid ledger event record at row {ordinal}"
                raise MCRunError(message)
            row = cast("dict[str, object]", parsed)
            if set(row) != _LEDGER_ROW_KEYS:
                message = f"Invalid ledger event record at row {ordinal}"
                raise MCRunError(message)
            yield row


def _existing_prefix(path: Path, expected: dict[str, object], request_path: Path) -> int:
    """Only an unchanged complete-prefix checkpoint may be resumed.

    A new extended plan revision changes the request SHA and weights. It must
    use a new ledger and reaggregate under all of the new weights.
    """
    recorded = _read_ledger(path)
    actual_header = next(recorded)
    if actual_header != expected:
        message = "MC checkpoint belongs to a different plan/policy/source/engine/code revision"
        raise MCRunError(message)
    count = 0
    effective = iter_effective_events(request_path)
    for row in recorded:
        candidate = next(effective, None)
        if candidate is None:
            message = "Ledger contains more events than the request"
            raise MCRunError(message)
        if (
            row["sample_id"] != candidate.sample_id
            or row["scenario_id"] != candidate.scenario_id
            or row["duration_min"] != candidate.duration_min
            or row["stratum_id"] != candidate.stratum_id
            or row["probability_weight"] != str(candidate.probability_weight)
            or row["effective_event_sha256"] != candidate.digest()
        ):
            message = f"Mixed or reordered checkpoint at event {count + 1}"
            raise MCRunError(message)
        count += 1
    return count


def _new_ledger(path: Path, header: dict[str, object]) -> None:
    if path.exists() or path.is_symlink():
        message = "MC ledger already exists; specify --resume for an unchanged plan"
        raise MCRunError(message)
    with path.open("xb") as stream:
        stream.write(encode_jsonl_line(header))
        stream.flush()
        os.fsync(stream.fileno())


def _append_ledger(path: Path, record: dict[str, object]) -> None:
    encoded = encode_jsonl_line(record)
    if len(encoded) > MAX_LINE_BYTES:
        message = "Compact MC ledger record exceeds bounded line length"
        raise MCRunError(message)
    with path.open("ab") as stream:
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())


def summarise_ledger(path: Path, request_path: Path, expected: dict[str, object]) -> MCRunSummary:
    """Count all planned success/zero/failure states; never call partial a curve."""
    completed = _existing_prefix(path, expected, request_path)
    counts: Counter[str] = Counter()
    zeros = 0
    rows = _read_ledger(path)
    next(rows)
    for record in rows:
        status = record["status"]
        if not isinstance(status, str):
            message = "Invalid MC ledger status"
            raise MCRunError(message)
        counts[status] += 1
        sites = record["sites"]
        if not isinstance(sites, list):
            message = "Invalid MC ledger site collection"
            raise MCRunError(message)
        sites_list = cast("list[object]", sites)
        if (
            status == _STATUS_OK
            and sites_list
            and all(
                isinstance(site, dict) and cast("dict[str, object]", site).get("peak_m3_s") == 0
                for site in sites_list
            )
        ):
            zeros += 1
    return MCRunSummary(
        int(cast("int", expected["expected_event_count"])), completed, dict(sorted(counts.items())), zeros
    )


def execute_mc_request(
    project_path: Path,
    request_path: Path,
    ledger_path: Path,
    *,
    resume: bool = False,
    selection: EngineSelection | None = None,
    wheel_artifact: Path | None = None,
) -> MCRunSummary:
    """Checkpoint each completed event, streaming the existing runner and prepared geometry.

    No full routed hydrographs persist in the compact ledger. Use replay_mc_event
    for a selected complete event's unchanged full ordinary batch output.
    """
    _, request_hash = validate_effective_request(request_path)
    loaded = load_project(project_path)
    _project_subset(loaded)
    for planned in iter_effective_events(request_path):
        _fixed_parameters(planned, loaded)
    selected = loaded.project.engine if selection is None else selection
    header = _header(loaded, request_hash, selection=selected, wheel_artifact=wheel_artifact, request_path=request_path)
    if ledger_path.is_symlink():
        message = "MC ledger symlinks are not accepted"
        raise MCRunError(message)
    if resume:
        completed = _existing_prefix(ledger_path, header, request_path)
    else:
        _new_ledger(ledger_path, header)
        completed = 0
    remaining = islice(iter_effective_events(request_path), completed, None)
    # Two bounded iterators over the same immutable request are intentional:
    # iter_project_events consumes its own source once, maintaining one geometry
    # cache across the whole remaining batch, while the outer stream retains
    # the weight/identity corresponding to each reported EngineOutcome.
    model_events = (record.event for record in islice(iter_effective_events(request_path), completed, None))
    outcomes = iter_project_events(
        project_path,
        model_events,
        selection=selected,
        selection_source="api_override",
        wheel_artifact=wheel_artifact,
    )
    for record, outcome in zip(remaining, outcomes, strict=True):
        _fixed_parameters(record, loaded)
        if outcome.event_id != record.sample_id:
            message = "Existing runner returned an outcome with a different event ID"
            raise MCRunError(message)
        _append_ledger(ledger_path, _event_row(record, outcome))
    if sha256_file(request_path) != request_hash:
        message = "MC request changed during execution; checkpoint is not reusable"
        raise MCRunError(message)
    return summarise_ledger(ledger_path, request_path, header)


def replay_mc_event(
    project_path: Path,
    request_path: Path,
    ledger_path: Path,
    sample_id: str,
    output_prefix: Path,
    *,
    selection: EngineSelection | None = None,
    wheel_artifact: Path | None = None,
) -> ProjectBatchReport:
    """Replay an actual retained effective event with the original selected engine."""
    _, request_hash = validate_effective_request(request_path)
    loaded = load_project(project_path)
    _project_subset(loaded)
    selected = loaded.project.engine if selection is None else selection
    expected = _header(
        loaded, request_hash, selection=selected, wheel_artifact=wheel_artifact, request_path=request_path
    )
    _existing_prefix(ledger_path, expected, request_path)
    match: EffectiveMCEvent | None = None
    for item in iter_effective_events(request_path):
        if item.sample_id == sample_id:
            match = item
            break
    if match is None:
        message = f"Sample {sample_id!r} absent from explicit request"
        raise MCRunError(message)
    rows = _read_ledger(ledger_path)
    next(rows)
    recorded = next((row for row in rows if row["sample_id"] == sample_id), None)
    if recorded is None or recorded["status"] != _STATUS_OK:
        message = "Representative-event replay requires a successfully checkpointed actual sample"
        raise MCRunError(message)
    _fixed_parameters(match, loaded)
    report = run_project_events(project_path, (match.event,), selection=selected, wheel_artifact=wheel_artifact)
    outcome = report.outcomes[0]
    replayed = _event_row(match, outcome)
    for key in ("effective_event_sha256", "effective_model_sha256", "status", "sites"):
        if replayed[key] != recorded[key]:
            message = f"MC representative replay diverged from checkpoint: {key}"
            raise MCRunError(message)
    write_batch_results(output_prefix, report)
    return report


def main(argv: list[str] | None = None) -> int:
    """Explicit-event MC CLI: validate, stream, resume, inspect and deterministic replay."""
    parser = argparse.ArgumentParser(prog="python -m runoff_routing.monte_carlo_execution")
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="verify all effective events and original source hashes")
    validate.add_argument("request", type=Path)
    run = commands.add_parser("run", help="run or resume an exact effective request")
    run.add_argument("project", type=Path)
    run.add_argument("request", type=Path)
    run.add_argument("ledger", type=Path)
    run.add_argument("--resume", action="store_true")
    replay = commands.add_parser("replay", help="re-execute one checkpointed representative event")
    replay.add_argument("project", type=Path)
    replay.add_argument("request", type=Path)
    replay.add_argument("ledger", type=Path)
    replay.add_argument("sample_id")
    replay.add_argument("output_prefix", type=Path)
    inspect = commands.add_parser("inspect", help="report checkpoint completeness without a frequency estimate")
    inspect.add_argument("project", type=Path)
    inspect.add_argument("request", type=Path)
    inspect.add_argument("ledger", type=Path)
    for sub in (run, replay, inspect):
        sub.add_argument("--engine", choices=("python", "python-cmd", "rorb-cmd"))
        sub.add_argument("--numerical-profile")
        sub.add_argument("--wheel-artifact", type=Path)
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2
    try:
        if args.command == "validate":
            header, digest = validate_effective_request(args.request)
            print(f"Valid effective request: {header.event_count} samples; SHA-256 {digest}")
            return 0
        if args.numerical_profile is not None and args.engine is None:
            message = "--numerical-profile requires --engine"
            raise MCRunError(message)
        selected = EngineSelection.for_engine(args.engine, args.numerical_profile) if args.engine is not None else None
        if args.command == "run":
            report = execute_mc_request(
                args.project,
                args.request,
                args.ledger,
                resume=args.resume,
                selection=selected,
                wheel_artifact=args.wheel_artifact,
            )
            print(report.to_text(), end="")
            return 0 if report.complete else 2
        if args.command == "replay":
            report = replay_mc_event(
                args.project,
                args.request,
                args.ledger,
                args.sample_id,
                args.output_prefix,
                selection=selected,
                wheel_artifact=args.wheel_artifact,
            )
            print(report.to_text(), end="")
            return 0 if report.succeeded else 2
        _, digest = validate_effective_request(args.request)
        loaded = load_project(args.project)
        _project_subset(loaded)
        selected = loaded.project.engine if selected is None else selected
        expected = _header(
            loaded, digest, selection=selected, wheel_artifact=args.wheel_artifact, request_path=args.request
        )
        result = summarise_ledger(args.ledger, args.request, expected)
        print(result.to_text(), end="")
    except (OSError, ValueError, TypeError, ArithmeticError) as exc:
        print(f"MC execution failed: {exc}", file=sys.stderr)
        return 2
    else:
        return 0 if result.complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
