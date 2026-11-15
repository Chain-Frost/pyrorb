"""Versioned explicit-event project batches using the established selected-engine dispatcher.

A batch request is not another project schema. One SHA-verified schema-2 project
owns catchment, controls, source ordering, rainfall method and engine selection.
Each event derives a fresh immutable S1 run in memory; no project is rewritten.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import sys
from collections import Counter
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import asdict, dataclass, replace
from itertools import pairwise
from pathlib import Path
from typing import Any, cast

from .engine_execution import (
    SelectionSource,
    _base,
    _with_implementation_identity,
    execute_loaded_engine,
)
from .engine_types import EngineDiagnostic, EngineOutcome, EngineSelection, EngineStatus
from .native_cmd import NativeConfiguration
from .project_json import (
    EmbeddedRun,
    LoadedProject,
    ProjectError,
    _reject_nonfinite,
    _unique_pairs,
    load_project,
)
from .rorb_model import ParameterSet, RunModel, StormModel, from_dict, to_dict, to_json

REQUEST_FORMAT = "python-runoff-routing-explicit-events"
REQUEST_VERSION = 1
_INVALID_INPUT: EngineStatus = "invalid_input"
_UNSUPPORTED_FEATURE: EngineStatus = "unsupported_feature"
REPORT_FORMAT = "python-runoff-routing-event-results"
MAX_REQUEST_BYTES = 8 * 1024 * 1024
_EVENT_ID = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,127}\Z")
_STORM_FIELDS = {
    "title",
    "timestep_hours",
    "calculation_increments",
    "start_increment",
    "percentages",
    "depths_mm",
}
_LOSS_FIELDS = {"initial_loss_mm", "continuing"}
_CSV_HEADER = (
    "event_index", "event_id", "status", "error_code", "error_message",
    "project_id", "project_sha256", "effective_model_sha256", "original_source_sha256_json",
    "stored_engine", "engine", "numerical_profile", "rainfall_profile", "source_kind",
    "timestep_hours", "calculation_increments", "print_id", "print_label", "native_column_id",
    "sample_index", "physical_time_hours", "native_increment_token", "native_time_token",
    "discharge_m3_s", "physical_trapezoidal_volume_m3", "native_inclusive_reported_volume_m3",
    "discharge_units", "volume_units", "clock_convention",
)


class BatchConfigError(ValueError):
    """Malformed whole-batch request or unsafe output configuration."""


class EventConfigError(ValueError):
    """A single invalid/unsupported event that must retain its own outcome."""

    def __init__(self, status: EngineStatus, code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code


@dataclass(frozen=True, slots=True)
class ProjectEvent:
    """Typed public API request; override mappings are read, not mutated."""

    event_id: str
    storm: Mapping[str, object] | None = None
    losses: Mapping[str, object] | None = None


def load_event_request(path: Path) -> tuple[object, ...]:
    """Read a versioned text-file request, preserving malformed individual events.

    Top-level schema/duplicate-key failures invalidate the request. An invalid
    event remains a per-event result rather than vanishing during parsing.
    """
    if path.stat().st_size > MAX_REQUEST_BYTES:
        message = "Event request exceeds the 8 MiB limit"
        raise BatchConfigError(message)
    raw = path.read_bytes()
    if len(raw) > MAX_REQUEST_BYTES:
        message = "Event request changed or exceeds the 8 MiB limit"
        raise BatchConfigError(message)
    try:
        parsed: object = json.loads(
            raw.decode("utf-8-sig"), object_pairs_hook=_unique_pairs, parse_constant=_reject_nonfinite
        )
    except (UnicodeError, ValueError, TypeError) as exc:
        raise BatchConfigError(str(exc)) from exc
    if not isinstance(parsed, dict):
        message = "Event request must be a JSON object"
        raise BatchConfigError(message)
    request = cast("dict[str, object]", parsed)
    if set(request) != {"format", "schema_version", "events"}:
        message = "Event request requires exactly format, schema_version and events"
        raise BatchConfigError(message)
    if request["format"] != REQUEST_FORMAT or type(request["schema_version"]) is not int:
        message = "Unknown event-request format or schema version"
        raise BatchConfigError(message)
    if request["schema_version"] != REQUEST_VERSION:
        message = "Unsupported event-request schema version"
        raise BatchConfigError(message)
    events = request["events"]
    if not isinstance(events, list) or not events:
        message = "Event request needs a nonempty events array"
        raise BatchConfigError(message)
    return tuple(cast("list[object]", events))


def _request_fields(item: object) -> dict[str, object]:
    if isinstance(item, ProjectEvent):
        data: dict[str, object] = {"event_id": item.event_id}
        if item.storm is not None:
            data["storm"] = dict(item.storm)
        if item.losses is not None:
            data["losses"] = dict(item.losses)
        return data
    if not isinstance(item, dict):
        raise EventConfigError(_INVALID_INPUT, "event_record", "Event must be a JSON object")
    data = cast("dict[str, object]", item)
    if set(data) - {"event_id", "storm", "losses"}:
        raise EventConfigError(_INVALID_INPUT, "event_fields", "Unknown event fields")
    return data


def _identifier(item: object, ordinal: int) -> str:
    if isinstance(item, ProjectEvent):
        value: object = item.event_id
    elif isinstance(item, dict):
        value = cast("dict[str, object]", item).get("event_id")
    else:
        value = None
    if isinstance(value, str) and _EVENT_ID.fullmatch(value):
        return value
    return f"<request:{ordinal}>"


def _overlay(raw: object, allowed: set[str], label: str) -> dict[str, object]:
    if not isinstance(raw, dict):
        raise EventConfigError(_INVALID_INPUT, "event_overlay", f"{label} must be a JSON object")
    data = cast("dict[str, object]", raw)
    if set(data) - allowed:
        raise EventConfigError(_UNSUPPORTED_FEATURE, f"{label}_fields", f"Unsupported {label} override fields")
    return data


def _derive_storm(original: StormModel, raw: object) -> StormModel:
    patch = _overlay(raw, _STORM_FIELDS, "storm")
    document = to_dict(original)
    body = cast("dict[str, Any]", document["model"])
    body.update(patch)
    restored = from_dict(document)
    if not isinstance(restored, StormModel):
        message = "Storm override did not produce an S1 storm"
        raise EventConfigError(_INVALID_INPUT, "storm_model", message)
    return restored


def _derive_parameters(original: ParameterSet, raw: object) -> ParameterSet:
    if len(original.losses) != 1:
        raise EventConfigError(
            _UNSUPPORTED_FEATURE, "loss_override_scope", "Only one-ISA explicit event losses can be overridden"
        )
    patch = _overlay(raw, _LOSS_FIELDS, "losses")
    document = to_dict(original)
    body = cast("dict[str, Any]", document["model"])
    losses = cast("list[dict[str, Any]]", body["losses"])
    losses[0].update(patch)
    restored = from_dict(document)
    if not isinstance(restored, ParameterSet):
        message = "Loss override did not produce S1 parameters"
        raise EventConfigError(_INVALID_INPUT, "loss_model", message)
    return restored


def _event_run(loaded: LoadedProject, fields: dict[str, object]) -> tuple[RunModel, str]:
    current = loaded.run
    storm = current.storm
    parameters = current.parameters
    changed: list[str] = []
    if "storm" in fields:
        try:
            storm = _derive_storm(current.storm, fields["storm"])
        except (TypeError, ValueError) as exc:
            if isinstance(exc, EventConfigError):
                raise
            raise EventConfigError(_INVALID_INPUT, "storm_model", str(exc)) from exc
        changed.append("storm")
    if "losses" in fields:
        try:
            parameters = _derive_parameters(current.parameters, fields["losses"])
        except (TypeError, ValueError) as exc:
            if isinstance(exc, EventConfigError):
                raise
            raise EventConfigError(_INVALID_INPUT, "loss_model", str(exc)) from exc
        changed.append("losses")
    try:
        return RunModel(parameters, current.catchment, storm), ",".join(changed) if changed else "none"
    except (TypeError, ValueError) as exc:
        raise EventConfigError(_INVALID_INPUT, "event_model", str(exc)) from exc


def _event_failure(base: EngineOutcome, status: EngineStatus, code: str, message: str) -> EngineOutcome:
    return replace(base, status=status, diagnostics=(EngineDiagnostic(code, message),))


def iter_project_events(
    project_path: Path,
    events: Iterable[object],
    *,
    selection: EngineSelection | None = None,
    selection_source: SelectionSource = "api_override",
    native_config: NativeConfiguration | None = None,
    wheel_artifact: Path | None = None,
) -> Iterator[EngineOutcome]:
    """Execute requested events in order, with one result per input and no file-per-event.

    Source hashes and package/wheel attribution are verified once. The typed
    project source is unchanged; every event has an independent immutable model
    and numerical calculation. No solver or native engine is substituted.
    """
    loaded = load_project(project_path)
    effective = loaded.project.engine if selection is None else selection
    if selection_source not in ("api_override", "cli_override"):
        message = "selection_source must be api_override or cli_override"
        raise BatchConfigError(message)
    source: SelectionSource = "project" if selection is None else selection_source
    attributed = _with_implementation_identity(_base(loaded, effective, source), wheel_artifact)
    source_kind = "embedded-run" if isinstance(loaded.project.model_source, EmbeddedRun) else "rorb-files"
    seen: set[str] = set()
    for ordinal, item in enumerate(events, start=1):
        identifier = _identifier(item, ordinal)
        event_base = replace(
            attributed,
            event_id=identifier,
            effective_inputs={**attributed.effective_inputs, "source_kind": source_kind, "event_overrides": "none"},
        )
        if identifier.startswith("<request:"):
            yield _event_failure(
                event_base, "invalid_input", "event_id", "Event ID must be a stable, nonempty ASCII identifier"
            )
            continue
        if identifier in seen:
            yield _event_failure(event_base, "invalid_input", "duplicate_event_id", "Duplicate event ID")
            continue
        seen.add(identifier)
        try:
            fields = _request_fields(item)
            model, override = _event_run(loaded, fields)
        except EventConfigError as exc:
            yield _event_failure(event_base, exc.status, exc.code, str(exc))
            continue
        effective_settings = {
            **event_base.effective_inputs,
            "timestep_hours": str(model.storm.timestep_hours),
            "calculation_increments": model.storm.calculation_increments,
            "loss_model": model.parameters.loss_model,
            "event_overrides": override,
            "source_kind": source_kind,
        }
        event_base = replace(
            event_base,
            model_sha256=hashlib.sha256(to_json(model).encode("utf-8")).hexdigest(),
            effective_inputs=effective_settings,
        )
        if attributed.diagnostics:
            yield replace(event_base, status=attributed.status)
            continue
        if effective.engine == "rorb-cmd" and override != "none":
            yield _event_failure(
                event_base,
                "unsupported_feature",
                "native_event_override",
                "The native adapter requires unmodified original .par/.catg/.stm bytes for every event",
            )
            continue
        event_loaded = replace(loaded, run=model)
        yield execute_loaded_engine(event_loaded, event_base, project_path=project_path, native_config=native_config)


def _trapezoidal_volume(outcome: EngineOutcome, values: tuple[float, ...]) -> float | None:
    """Derived physical-time integral only; never call it CMD reported volume."""
    if len(values) < 2 or len(values) != len(outcome.physical_time_hours):
        return None
    try:
        times = tuple(float(value) for value in outcome.physical_time_hours)
    except ValueError:
        return None
    if not all(math.isfinite(value) for value in (*times, *values)):
        return None
    if any(b <= a for a, b in pairwise(times)):
        return None
    return 3600.0 * math.fsum(
        0.5 * (a + b) * (end - start)
        for a, b, start, end in zip(values[:-1], values[1:], times[:-1], times[1:], strict=True)
    )


@dataclass(frozen=True, slots=True)
class ProjectBatchReport:
    """Collected full outcomes; streaming API avoids retaining them if unnecessary."""

    outcomes: tuple[EngineOutcome, ...]

    @property
    def succeeded(self) -> bool:
        return bool(self.outcomes) and all(item.status == "computed_unvalidated" for item in self.outcomes)

    def to_json(self) -> str:
        payload = {
            "format": REPORT_FORMAT,
            "schema_version": REQUEST_VERSION,
            "requested_event_count": len(self.outcomes),
            "completed_event_count": sum(item.status == "computed_unvalidated" for item in self.outcomes),
            "status_counts": dict(sorted(Counter(item.status for item in self.outcomes).items())),
            "outcomes": [asdict(item) for item in self.outcomes],
            "volumes": [
                {
                    "event_id": item.event_id,
                    "print_id": graph.print_id,
                    "physical_trapezoidal_volume_m3": _trapezoidal_volume(item, graph.discharge_m3_s),
                    "native_inclusive_reported_volume_m3": None,
                }
                for item in self.outcomes
                for graph in item.hydrographs
            ],
        }
        return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n"

    def to_csv(self) -> str:
        buffer = io.StringIO(newline="")
        writer = csv.writer(buffer, lineterminator="\n")
        writer.writerow(_CSV_HEADER)
        for ordinal, outcome in enumerate(self.outcomes, start=1):
            error_code = outcome.diagnostics[0].code if outcome.diagnostics else ""
            error_message = outcome.diagnostics[0].message if outcome.diagnostics else ""
            common = (
                ordinal, outcome.event_id, outcome.status, error_code, error_message,
                outcome.project_id, outcome.project_sha256, outcome.model_sha256,
                json.dumps(outcome.source_file_hashes, ensure_ascii=False, separators=(",", ":")),
                outcome.stored_selection.engine, outcome.effective_selection.engine,
                outcome.effective_selection.numerical_profile, outcome.rainfall_profile,
                outcome.effective_inputs.get("source_kind", ""),
                outcome.effective_inputs["timestep_hours"], outcome.effective_inputs["calculation_increments"],
            )
            if not outcome.hydrographs:
                writer.writerow((*common, *("" for _ in range(len(_CSV_HEADER) - len(common)))))
                continue
            for graph in outcome.hydrographs:
                volume = _trapezoidal_volume(outcome, graph.discharge_m3_s)
                for index, discharge in enumerate(graph.discharge_m3_s):
                    hour = outcome.physical_time_hours[index] if index < len(outcome.physical_time_hours) else ""
                    inc = outcome.native_raw_increment_tokens[index] if index < len(outcome.native_raw_increment_tokens) else ""
                    raw_time = outcome.native_raw_time_tokens[index] if index < len(outcome.native_raw_time_tokens) else ""
                    writer.writerow((
                        *common, graph.print_id, graph.label, graph.native_column_id or "", index, hour,
                        inc, raw_time, discharge, volume if index == 0 else "", "",
                        graph.units, "m3", outcome.native_clock_convention or "model_elapsed_from_zero",
                    ))
        return buffer.getvalue()

    def to_text(self) -> str:
        counts = Counter(item.status for item in self.outcomes)
        header = ["Runoff routing: explicit event results"]
        if self.outcomes:
            first = self.outcomes[0]
            header.extend((
                f"Project: {first.project_id} ({first.project_sha256})",
                f"Stored engine: {first.stored_selection.engine}/{first.stored_selection.numerical_profile}",
                f"Effective engine: {first.effective_selection.engine}/{first.effective_selection.numerical_profile}",
            ))
        header.append(
            f"Requested: {len(self.outcomes)}  Computed: {counts['computed_unvalidated']}  "
            f"Other: {len(self.outcomes) - counts['computed_unvalidated']}"
        )
        for index, outcome in enumerate(self.outcomes, start=1):
            if len(self.outcomes) > 20 and outcome.status == "computed_unvalidated":
                continue
            reason = f" [{outcome.diagnostics[0].code}]" if outcome.diagnostics else ""
            header.append(f"{index}. {outcome.event_id}: {outcome.status}{reason}")
        header.append("Numerical/native parity: not assessed; physical trapezoidal volume is not CMD reported volume.")
        return "\n".join(header) + "\n"


def run_project_events(
    project_path: Path,
    events: Iterable[object],
    *,
    selection: EngineSelection | None = None,
    selection_source: str = "api_override",
    native_config: NativeConfiguration | None = None,
    wheel_artifact: Path | None = None,
) -> ProjectBatchReport:
    """Materialise the streaming results; never hide failed/unsupported events."""
    outcomes = tuple(
        iter_project_events(
            project_path,
            events,
            selection=selection,
            selection_source=selection_source,
            native_config=native_config,
            wheel_artifact=wheel_artifact,
        )
    )
    if not outcomes:
        message = "An explicit batch must request at least one event"
        raise BatchConfigError(message)
    return ProjectBatchReport(outcomes)


def write_batch_results(prefix: Path, report: ProjectBatchReport) -> tuple[Path, Path, Path]:
    """Exclusive-create JSON, CSV and text. Roll back only files created here."""
    paths = (Path(f"{prefix}.json"), Path(f"{prefix}.csv"), Path(f"{prefix}.txt"))
    if len(set(paths)) != len(paths) or any(item.exists() or item.is_symlink() for item in paths):
        message = "One or more batch result destinations already exist"
        raise BatchConfigError(message)
    contents = (report.to_json(), report.to_csv(), report.to_text())
    created: list[Path] = []
    try:
        for path, content in zip(paths, contents, strict=True):
            with path.open("xb") as stream:
                created.append(path)
                stream.write(content.encode("utf-8"))
    except OSError:
        for path in created:
            path.unlink(missing_ok=True)
        raise
    return paths


def main(argv: list[str] | None = None) -> int:
    """CLI for selected-engine one-event or requested explicit-event batches."""
    parser = argparse.ArgumentParser(prog="python -m runoff_routing.project_batch")
    parser.add_argument("project", type=Path, help="validated versioned project JSON")
    parser.add_argument("output_prefix", type=Path, help="exclusive new .json/.csv/.txt report prefix")
    parser.add_argument("--events", type=Path, help="versioned JSON explicit-event request; default: stored event")
    parser.add_argument("--engine", choices=("python", "python-cmd", "rorb-cmd"))
    parser.add_argument("--numerical-profile")
    parser.add_argument("--native-config", type=Path)
    parser.add_argument("--wheel-artifact", type=Path)
    try:
        options = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2
    if options.engine is None and options.numerical_profile is not None:
        print("--numerical-profile requires an explicit --engine", file=sys.stderr)
        return 2
    prefix: Path = options.output_prefix
    output_paths = tuple(Path(f"{prefix}{suffix}") for suffix in (".json", ".csv", ".txt"))
    if any(path.exists() or path.is_symlink() for path in output_paths):
        print("Batch result destination already exists; no files overwritten", file=sys.stderr)
        return 2
    try:
        selected = (
            EngineSelection.for_engine(options.engine, options.numerical_profile)
            if options.engine is not None else None
        )
        native = NativeConfiguration.from_file(options.native_config) if options.native_config is not None else None
        requested = (
            load_event_request(options.events)
            if options.events is not None
            else (ProjectEvent(load_project(options.project).project.identifier),)
        )
        report = run_project_events(
            options.project,
            requested,
            selection=selected,
            selection_source="cli_override",
            native_config=native,
            wheel_artifact=options.wheel_artifact,
        )
        write_batch_results(prefix, report)
    except (BatchConfigError, ProjectError, OSError, ValueError, TypeError) as exc:
        print(f"Batch execution failed: {exc}", file=sys.stderr)
        return 2
    print(report.to_text(), end="")
    return 0 if report.succeeded else 2


if __name__ == "__main__":
    raise SystemExit(main())
