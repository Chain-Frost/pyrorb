"""Bounded ARR2019/BoM deterministic design ensembles through the #119 event contract.

Source selection and numerical execution are separate. No generated-input
native acceptance, representative event, critical-duration inference or GUI.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Literal, Never, cast

from .arr_arf import (
    AreaAdjustedHyetograph,
    apply_arr2019_arf_to_bom_storm,
    calculate_arr2019_arf,
    published_coefficients,
)
from .arr_data import ARRDocument, ARRFormatError
from .arr_import import read_arr_file
from .arr_losses import (
    PreburstLossSelection,
    derive_preburst_from_areal_rainfall,
    select_legacy_preburst_loss,
    verify_legacy_bom_source_point,
)
from .arr_patterns import Pattern, PatternSet, read_pattern_file
from .arr_selection import TemporalPatternSelection, select_arr2019_ensemble
from .arr_storm import storm_from_bom
from .bom_ifd import BoMIFD, read_bom_ifd_csv
from .engine_types import EngineSelection
from .project_batch import REQUEST_FORMAT, REQUEST_VERSION, ProjectBatchReport, ProjectEvent, run_project_events
from .project_json import LoadedProject, load_project

DESIGN_FORMAT = "python-runoff-routing-arr2019-design"
EFFECTIVE_FORMAT = "python-runoff-routing-arr2019-effective-events"
DESIGN_VERSION = 1
METHOD_PROFILE = "arr2019-bom-published-arf-burst-only-v1"
LossProfile = Literal["project_il_cl", "legacy_source_depth_burst_only", "legacy_ratio_areal_burst_only"]
PatternKind = Literal["point", "areal"]
MAX_CONFIG_BYTES = 128 * 1024
MAX_DURATION_AXIS = 8
MAX_AEP_AXIS = 6


class DesignConfigError(ValueError):
    """Whole-request error; selected-cell failures are recorded separately."""


@dataclass(frozen=True, slots=True)
class DesignConfig:
    path: Path
    project: Path
    bom_ifd: Path
    temporal_patterns: Path
    pattern_kind: PatternKind
    temporal_region: str
    arf_region: str
    catchment_area_km2: Decimal
    durations_min: tuple[int, ...]
    aep_labels: tuple[str, ...]
    dry_tail_min: int
    engine: EngineSelection
    loss_profile: LossProfile
    legacy_arr_txt: Path | None
    preburst_percentile: Literal[10, 25, 50, 75, 90] | None
    excess_policy: Literal["reject", "clamp_burst_il_to_zero"] | None


@dataclass(frozen=True, slots=True)
class DesignBatchResult:
    """Input audit and unchanged common batch report, with separate qualification."""

    effective: dict[str, object]
    event_request: dict[str, object]
    routed: ProjectBatchReport
    succeeded: bool


def _fail(message: str) -> Never:
    raise DesignConfigError(message)


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            _fail(f"Duplicate config key: {key}")
        result[key] = value
    return result


def _nonfinite(value: str) -> Never:
    _fail(f"Nonstandard JSON constant: {value}")


def _object(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        _fail(f"{label} must be a JSON object")
    return cast("dict[str, object]", value)


def _string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or any(ord(c) < 32 for c in value):
        _fail(f"{label} must be nonempty text without surrounding whitespace or control characters")
    return value


def _decimal(value: object, label: str) -> Decimal:
    if not isinstance(value, str):
        _fail(f"{label} must be a decimal string (not a JSON floating-point number)")
    try:
        number = Decimal(value)
    except InvalidOperation:
        _fail(f"Invalid decimal string for {label}")
    if not number.is_finite() or not 0 < number <= 30000:
        _fail(f"{label} must be finite and in (0, 30000] km2")
    return number


def _positive_int(value: object, label: str, maximum: int) -> int:
    if type(value) is not int or not 0 < value <= maximum:
        _fail(f"{label} must be a whole number in 1..{maximum}")
    return value


def _file(config_path: Path, value: object, label: str) -> Path:
    name = _string(value, label)
    path = Path(name)
    return path.absolute() if path.is_absolute() else config_path.absolute().parent / path


def _axis(value: object, label: str, limit: int) -> list[object]:
    if not isinstance(value, list) or not 1 <= len(value) <= limit:
        _fail(f"{label} must contain between one and {limit} values")
    return cast("list[object]", value)


def _read_loss_config(
    config_path: Path, raw: object
) -> tuple[
    LossProfile,
    Path | None,
    Literal[10, 25, 50, 75, 90] | None,
    Literal["reject", "clamp_burst_il_to_zero"] | None,
]:
    """Validate the method-specific source/preburst options separately from the axes."""
    loss = _object(raw, "loss")
    mode = _string(loss.get("mode"), "loss.mode")
    if mode not in {"project_il_cl", "legacy_source_depth_burst_only", "legacy_ratio_areal_burst_only"}:
        _fail("Unrecognised loss method; no automatic preburst convention")
    legacy_path: Path | None = None
    percentile: Literal[10, 25, 50, 75, 90] | None = None
    excess_policy: Literal["reject", "clamp_burst_il_to_zero"] | None = None
    if mode == "project_il_cl":
        if set(loss) != {"mode"}:
            _fail("project_il_cl may not include a preburst/legacy ARR source")
    else:
        if set(loss) != {"mode", "arr_txt", "percentile", "excess_policy"}:
            _fail("Legacy burst-only requires arr_txt, percentile and excess_policy")
        raw_percentile = loss["percentile"]
        if type(raw_percentile) is not int or raw_percentile not in (10, 25, 50, 75, 90):
            _fail("Preburst percentile must be an explicit supported 10/25/50/75/90")
        raw_policy = loss["excess_policy"]
        if raw_policy not in ("reject", "clamp_burst_il_to_zero"):
            _fail("Unsupported excess-preburst policy")
        percentile = cast("Literal[10, 25, 50, 75, 90]", raw_percentile)
        excess_policy = cast("Literal['reject', 'clamp_burst_il_to_zero']", raw_policy)
        legacy_path = _file(config_path, loss["arr_txt"], "loss.arr_txt")
    return cast("LossProfile", mode), legacy_path, percentile, excess_policy


def read_design_config(path: Path) -> DesignConfig:
    """Read a strict bounded text configuration; paths belong to its directory."""
    if path.stat().st_size > MAX_CONFIG_BYTES:
        _fail("Design configuration exceeds 128 KiB")
    raw = path.read_bytes()
    if not raw or len(raw) > MAX_CONFIG_BYTES:
        _fail("Design configuration is empty, changed or oversized")
    try:
        data: object = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_unique_pairs, parse_constant=_nonfinite)
    except (UnicodeError, ValueError, TypeError) as exc:
        raise DesignConfigError(str(exc)) from exc
    source = _object(data, "Design configuration")
    expected = {
        "format", "schema_version", "project", "bom_ifd", "temporal_patterns", "pattern_kind",
        "temporal_region", "arf_region", "catchment_area_km2", "durations_min", "aep_labels",
        "dry_tail_min", "engine", "numerical_profile", "loss",
    }
    if set(source) != expected or source["format"] != DESIGN_FORMAT or type(source["schema_version"]) is not int:
        _fail("Unknown design configuration format, version or fields")
    if source["schema_version"] != DESIGN_VERSION:
        _fail("Unsupported design configuration version")
    durations = tuple(_positive_int(item, "Duration", 10080) for item in _axis(source["durations_min"], "durations_min", MAX_DURATION_AXIS))
    labels = tuple(_string(item, "AEP label") for item in _axis(source["aep_labels"], "aep_labels", MAX_AEP_AXIS))
    if len(set(durations)) != len(durations) or len(set(labels)) != len(labels):
        _fail("Duplicate duration or AEP label on selected axes")
    dry_tail = source["dry_tail_min"]
    if type(dry_tail) is not int or not 0 <= dry_tail <= 10080:
        _fail("dry_tail_min must be 0..10080 whole minutes")
    kind = _string(source["pattern_kind"], "pattern_kind")
    if kind not in ("point", "areal"):
        _fail("pattern_kind must explicitly be point or areal")
    mode, legacy_path, percentile, excess_policy = _read_loss_config(path, source["loss"])
    selected = EngineSelection.for_engine(
        _string(source["engine"], "engine"), _string(source["numerical_profile"], "numerical_profile")
    )
    if selected.engine == "rorb-cmd":
        _fail("In-memory generated events cannot be represented by the native rorb-cmd file adapter")
    return DesignConfig(
        path=path.absolute(),
        project=_file(path, source["project"], "project"),
        bom_ifd=_file(path, source["bom_ifd"], "bom_ifd"),
        temporal_patterns=_file(path, source["temporal_patterns"], "temporal_patterns"),
        pattern_kind=cast("PatternKind", kind),
        temporal_region=_string(source["temporal_region"], "temporal_region"),
        arf_region=_string(source["arf_region"], "arf_region"),
        catchment_area_km2=_decimal(source["catchment_area_km2"], "catchment_area_km2"),
        durations_min=durations,
        aep_labels=labels,
        dry_tail_min=dry_tail,
        engine=selected,
        loss_profile=cast("LossProfile", mode),
        legacy_arr_txt=legacy_path,
        preburst_percentile=percentile,
        excess_policy=excess_policy,
    )


def _validate_project(config: DesignConfig, loaded: LoadedProject) -> None:
    run = loaded.run
    area = sum((item.area_km2 for item in run.catchment.subareas), Decimal(0))
    if area != config.catchment_area_km2:
        _fail("Configured catchment area must equal the sum of project subareas; no inferred ARF area")
    if run.parameters.loss_model != 1 or run.parameters.num_isa != 1 or len(run.parameters.losses) != 1:
        _fail("Design batch currently requires one ISA and loss model 1 (IL/CL)")
    if any(item.impervious_fraction != 0 for item in run.catchment.subareas):
        _fail("Design batch currently requires entirely pervious subareas")
    if run.storm.pattern_basis != "percent_of_depth" or run.storm.preburst_bins:
        _fail("Design batch cannot silently mix relative-weight or combined preburst storm bases")
    if any(asset.role != "reference" for asset in loaded.project.assets):
        _fail("Unprepared project rainfall/TP/curve assets cannot be silently reused")
    if loaded.project.rainfall_profile not in ("explicit", "legacy-rorb"):
        _fail("Generated legacy ARR2019 storms need an explicit/legacy-rorb project, not ARR2026 mode")


def _loss_for_event(
    config: DesignConfig,
    bom: BoMIFD,
    legacy: ARRDocument | None,
    duration: int,
    aep: Decimal,
    adjusted: AreaAdjustedHyetograph,
    loaded: LoadedProject,
) -> tuple[dict[str, object] | None, dict[str, object]]:
    baseline = loaded.run.parameters.losses[0]
    if config.loss_profile == "project_il_cl":
        return None, {
            "method": "project_il_cl", "storm_initial_loss_mm": str(baseline.initial_loss_mm),
            "burst_initial_loss_mm": str(baseline.initial_loss_mm),
            "continuing_loss_mm_per_hour": str(baseline.continuing),
            "preburst_applied_depth_mm": "0", "preburst_source_depth_mm": None,
            "preburst_ratio": None, "preburst_depth_basis": "none",
            "source_sha256": None, "operations": ["PROJECT_IL_CL_APPLIED_BY_ENGINE_ONCE"],
        }
    if legacy is None or config.preburst_percentile is None or config.excess_policy is None:
        _fail("Legacy loss selection requires an explicit parsed ARR source and preburst policy")
    selected: PreburstLossSelection = select_legacy_preburst_loss(
        legacy, duration_min=duration, aep_percent=aep,
        percentile=config.preburst_percentile, method="burst_only_reduced_il",
        excess_policy=config.excess_policy,
    )
    # Bind the same source point and original BoM bytes before applying losses.
    verify_legacy_bom_source_point(bom, selected, adjusted)
    if config.loss_profile == "legacy_ratio_areal_burst_only":
        selected = derive_preburst_from_areal_rainfall(selected, adjusted)
    if selected.burst_initial_loss_mm is None:
        _fail("A burst-only design cannot use unmaterialised explicit preburst rainfall")
    return {
        "initial_loss_mm": str(selected.burst_initial_loss_mm),
        "continuing": str(selected.continuing_loss_mm_per_hour),
    }, {
        "method": config.loss_profile,
        "storm_initial_loss_mm": str(selected.storm_initial_loss_mm),
        "burst_initial_loss_mm": str(selected.burst_initial_loss_mm),
        "continuing_loss_mm_per_hour": str(selected.continuing_loss_mm_per_hour),
        "preburst_applied_depth_mm": str(selected.preburst_depth_mm),
        "preburst_source_depth_mm": str(selected.source_preburst_depth_mm),
        "preburst_ratio": str(selected.preburst_ratio),
        "preburst_depth_basis": selected.depth_basis,
        "rainfall_basis_total_mm": (
            str(selected.rainfall_basis_total_mm) if selected.rainfall_basis_total_mm is not None else None
        ),
        "source_sha256": selected.source_sha256,
        "policy_version": selected.policy_version,
        "operations": [*selected.operations, "BURST_IL_CL_APPLIED_BY_ENGINE_ONCE"],
    }


def _event(
    config: DesignConfig,
    bom: BoMIFD,
    patterns: PatternSet,
    loaded: LoadedProject,
    legacy: ARRDocument | None,
    *,
    selection: TemporalPatternSelection,
    pattern: Pattern,
    ordinal: int,
    aep_label: str,
    aep_index: int,
    source_ordinal: int,
) -> tuple[ProjectEvent, dict[str, object]]:
    probability = bom.probability(aep_label)
    gross = storm_from_bom(bom, probability, patterns, pattern, convert_intensity=False)
    factor = calculate_arr2019_arf(
        catchment_area_km2=config.catchment_area_km2, duration_min=selection.duration_min,
        aep_percent=selection.aep_percent, coefficients=published_coefficients(config.arf_region),
    )
    areal = apply_arr2019_arf_to_bom_storm(gross, factor)
    if config.dry_tail_min % pattern.timestep_min:
        message = "Requested dry tail is not an integer number of selected temporal-pattern timesteps"
        raise ARRFormatError(message)
    losses, loss_audit = _loss_for_event(
        config, bom, legacy, selection.duration_min, selection.aep_percent, areal, loaded
    )
    event_id = f"arr-d{selection.duration_min}-a{aep_index:02d}-tp{ordinal:02d}"
    override: dict[str, object] = {
        "title": f"ARR2019 {selection.duration_min} min {aep_label} source TP {pattern.event_id}",
        "timestep_hours": str(Decimal(pattern.timestep_min) / Decimal(60)),
        "start_increment": 0,
        "calculation_increments": len(pattern.increments_percent) + config.dry_tail_min // pattern.timestep_min,
        "percentages": [str(value) for value in pattern.increments_percent],
        "depths_mm": [str(areal.total_mm)] * len(loaded.run.storm.subarea_ids),
    }
    record: dict[str, object] = {
        "event_id": event_id, "status": "ready", "duration_min": selection.duration_min,
        "aep_label": aep_label, "aep_percent": str(selection.aep_percent),
        "original_tp_id": pattern.event_id, "source_order": source_ordinal, "ensemble_order": ordinal,
        "tp_region": pattern.region, "tp_aep_band": pattern.aep_band,
        "tp_area_bin": pattern.area_bin, "timestep_min": pattern.timestep_min,
        "raw_pattern_percent": [str(value) for value in pattern.increments_percent],
        "raw_gross_total_mm": str(gross.total_mm),
        "raw_gross_increments_mm": [str(value) for value in gross.increments_mm],
        "areal_total_mm": str(areal.total_mm),
        "areal_increments_mm": [str(value) for value in areal.increments_mm],
        "arf_factor": str(factor.factor), "arf_policy_version": factor.policy_version,
        "arf_coefficient_region": factor.region,
        "arf_coefficient_source": factor.coefficient_origin,
        "source_ifd_depth_mm": str(gross.source_rainfall_depth_mm),
        "source_units": bom.rainfall_unit, "effective_rainfall_units": "mm",
        "loss": loss_audit, "engine_loss_application": "once_by_selected_engine",
        "effective_storm": override, "effective_losses": losses,
        "operations": list(areal.operations),
        "generated_input_reference_status": "not_assessed",
        "routed_native_reference_status": "not_assessed",
    }
    return ProjectEvent(event_id, storm=override, losses=losses), record


def _cell_failure(
    duration: int, label: str, stage: str, error: Exception, patterns: tuple[Pattern, ...]
) -> tuple[dict[str, object], list[dict[str, object]]]:
    reason = str(error)
    cell: dict[str, object] = {
        "duration_min": duration, "aep_label": label, "status": "input_error",
        "error_stage": stage, "error": reason, "expected_count": 10, "ready_count": 0,
        "original_tp_ids": [p.event_id for p in patterns],
    }
    records: list[dict[str, object]] = [
        {
            "event_id": None, "status": "input_error", "duration_min": duration,
            "aep_label": label, "original_tp_id": p.event_id,
            "error_stage": stage, "error": reason,
        }
        for p in patterns
    ]
    return cell, records


def _prepare_cell(
    config: DesignConfig,
    bom: BoMIFD,
    patterns: PatternSet,
    loaded: LoadedProject,
    legacy: ARRDocument | None,
    *,
    duration: int,
    aep_label: str,
    aep_index: int,
    source_orders: dict[Pattern, int],
) -> tuple[dict[str, object], list[ProjectEvent], list[dict[str, object]]]:
    ensemble: TemporalPatternSelection | None = None
    try:
        probability = bom.probability(aep_label)
        if probability.kind != "AEP_PERCENT":
            _fail("Only original BoM percentage AEP labels are supported; EY/ARI are not converted")
        ensemble = select_arr2019_ensemble(
            patterns, catchment_area_km2=config.catchment_area_km2, duration_min=duration,
            aep_percent=probability.value, region=config.temporal_region,
        )
        local: list[ProjectEvent] = []
        records: list[dict[str, object]] = []
        for i, pattern in enumerate(ensemble.patterns, start=1):
            event, audit = _event(
                config, bom, patterns, loaded, legacy, selection=ensemble,
                pattern=pattern, ordinal=i, aep_label=aep_label, aep_index=aep_index,
                source_ordinal=source_orders[pattern],
            )
            local.append(event)
            records.append(audit)
    except (ARRFormatError, ValueError, ArithmeticError) as exc:
        stage = "ensemble_selection" if ensemble is None else "effective_event_preparation"
        cell, rejected = _cell_failure(duration, aep_label, stage, exc, ensemble.patterns if ensemble else ())
        return cell, [], rejected
    cell = {
        "duration_min": duration, "aep_label": aep_label, "aep_percent": str(ensemble.aep_percent),
        "status": "ready", "expected_count": 10, "ready_count": len(local),
        "source_kind": ensemble.source_kind, "area_bin": ensemble.area_bin,
        "frequency_band": ensemble.aep_band, "original_tp_ids": list(ensemble.event_ids),
        "selection_policy": ensemble.policy_version,
    }
    return cell, local, records


def run_design_batch(path: Path) -> DesignBatchResult:
    """Construct all requested input cells, then dispatch only materialised events via #119."""
    config = read_design_config(path)
    loaded = load_project(config.project)
    _validate_project(config, loaded)
    bom = read_bom_ifd_csv(config.bom_ifd)
    patterns = read_pattern_file(config.temporal_patterns, kind=config.pattern_kind)
    legacy = (
        read_arr_file(config.legacy_arr_txt, legacy_profile="arr2016_txt")
        if config.legacy_arr_txt is not None else None
    )
    source_orders = {pattern: i for i, pattern in enumerate(patterns.patterns, start=1)}
    if len(source_orders) != len(patterns.patterns):
        _fail("Original temporal pattern identity/order is ambiguous")
    cells: list[dict[str, object]] = []
    events: list[ProjectEvent] = []
    records: list[dict[str, object]] = []
    for duration in config.durations_min:
        for index, label in enumerate(config.aep_labels, start=1):
            cell, selected, member_records = _prepare_cell(
                config, bom, patterns, loaded, legacy,
                duration=duration, aep_label=label, aep_index=index, source_orders=source_orders,
            )
            cells.append(cell)
            events.extend(selected)
            records.extend(member_records)
    routed = (
        run_project_events(config.project, events, selection=config.engine)
        if events else ProjectBatchReport(())
    )
    if len(routed.outcomes) != len(events):
        _fail("Common #119 execution did not return exactly one outcome per materialised event")
    outcomes = {item.event_id: item for item in routed.outcomes}
    if len(outcomes) != len(events):
        _fail("Common #119 execution lost or duplicated an event identity")
    for record in records:
        identifier = record["event_id"]
        if isinstance(identifier, str):
            outcome = outcomes[identifier]
            record["execution_status"] = outcome.status
            record["execution_error_code"] = outcome.diagnostics[0].code if outcome.diagnostics else None
            record["effective_model_sha256"] = outcome.model_sha256
    expected_count = len(config.durations_min) * len(config.aep_labels) * 10
    input_complete = len(events) == expected_count and all(cell["status"] == "ready" for cell in cells)
    succeeded = input_complete and routed.succeeded
    effective: dict[str, object] = {
        "format": EFFECTIVE_FORMAT, "schema_version": DESIGN_VERSION,
        "method_profile": METHOD_PROFILE, "status": "computed_unvalidated" if succeeded else "incomplete",
        "generated_input_reference_status": "not_assessed",
        "routed_native_reference_status": "not_assessed",
        "representative_event_rule": "not_selected_unverified",
        "critical_duration_rule": "not_selected_unverified",
        "source_files": {
            "design_config": {"path": str(config.path), "sha256": hashlib.sha256(config.path.read_bytes()).hexdigest()},
            "project": {
                "path": str(config.project),
                "sha256": hashlib.sha256(loaded.original_json_bytes).hexdigest(),
                "original_files": list(loaded.file_hashes),
            },
            "bom_ifd": {
                "path": str(config.bom_ifd), "sha256": bom.sha256, "units": bom.rainfall_unit,
                "source_system": bom.source_system, "issued": bom.issued,
            },
            "temporal_patterns": {
                "path": str(config.temporal_patterns), "sha256": patterns.source_sha256,
                "kind": patterns.kind,
                "members": [
                    {"locator": member.locator, "sha256": member.sha256, "byte_length": member.byte_length}
                    for member in patterns.members
                ],
            },
            "legacy_arr": {
                "path": str(config.legacy_arr_txt), "sha256": legacy.source.sha256,
                "profile": legacy.source.compatibility_profile,
            } if legacy is not None else None,
        },
        "selection": {
            "duration_axis_min": list(config.durations_min),
            "aep_label_axis": list(config.aep_labels),
            "catchment_area_km2": str(config.catchment_area_km2),
            "tp_region": config.temporal_region,
            "arf_region": config.arf_region, "pattern_kind": config.pattern_kind,
            "dry_tail_min": config.dry_tail_min,
            "engine": config.engine.engine, "numerical_profile": config.engine.numerical_profile,
            "loss_profile": config.loss_profile,
            "preburst_percentile": config.preburst_percentile,
            "excess_policy": config.excess_policy,
        },
        "expected_population": expected_count, "prepared_population": len(events),
        "input_population_complete": input_complete, "routed_population_complete": routed.succeeded,
        "routing_status_counts": dict(sorted(Counter(outcome.status for outcome in routed.outcomes).items())),
        "cells": cells, "members": records,
    }
    event_request: dict[str, object] = {
        "format": REQUEST_FORMAT, "schema_version": REQUEST_VERSION,
        "events": [
            {
                "event_id": event.event_id,
                "storm": dict(event.storm) if event.storm is not None else {},
                **({"losses": dict(event.losses)} if event.losses is not None else {}),
            }
            for event in events
        ],
    }
    return DesignBatchResult(effective, event_request, routed, succeeded)


def _json_text(data: dict[str, object]) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n"


def design_summary(result: DesignBatchResult) -> str:
    """Short overall status; full generated-input and routed evidence live in separate files."""
    effective = result.effective
    lines = [
        "ARR2019 deterministic design rainfall (BoM / published ARF)",
        f"Method: {METHOD_PROFILE}",
        f"Input: {effective['prepared_population']}/{effective['expected_population']} events prepared",
        f"Input population complete: {effective['input_population_complete']}",
        f"Routed events: {len(result.routed.outcomes)}",
        f"Routed statuses: {effective['routing_status_counts']}",
        f"Overall: {'computed_unvalidated' if result.succeeded else 'incomplete'}",
        "Generated-input reference acceptance: not assessed",
        "Routed original-native parity: not assessed",
        "Critical duration/representative event: not selected (rule unverified)",
    ]
    lines.extend(
        f"FAILED {cell['duration_min']} min / {cell['aep_label']}: {cell['error']}"
        for cell in cast("list[dict[str, object]]", effective["cells"])
        if cell["status"] != "ready"
    )
    return "\n".join(lines) + "\n"


def write_design_outputs(prefix: Path, result: DesignBatchResult) -> tuple[Path, ...]:
    """Write six text artifacts with exclusive create; roll back only our own files."""
    contents = (
        (".effective.json", _json_text(result.effective)),
        (".events.json", _json_text(result.event_request)),
        (".json", result.routed.to_json()),
        (".csv", result.routed.to_csv()),
        (".txt", result.routed.to_text()),
        (".summary.txt", design_summary(result)),
    )
    paths = tuple(Path(f"{prefix}{suffix}") for suffix, _ in contents)
    if any(path.exists() or path.is_symlink() for path in paths):
        _fail("One or more output destinations already exist; no files overwritten")
    created: list[Path] = []
    try:
        for (_, text), path in zip(contents, paths, strict=True):
            with path.open("xb") as stream:
                created.append(path)
                stream.write(text.encode("utf-8"))
    except OSError:
        for path in created:
            path.unlink(missing_ok=True)
        raise
    return paths


def main(argv: list[str] | None = None) -> int:
    """Run a deterministic source-configured ensemble without a native executable."""
    parser = argparse.ArgumentParser(prog="python -m runoff_routing.arr_design_batch")
    parser.add_argument("config", type=Path, help="bounded design-rainfall JSON configuration")
    parser.add_argument("output_prefix", type=Path, help="new exclusive output prefix")
    try:
        options = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2
    try:
        result = run_design_batch(options.config)
        write_design_outputs(options.output_prefix, result)
    except (DesignConfigError, ARRFormatError, OSError, ValueError, TypeError) as exc:
        print(f"Design rainfall batch failed: {exc}", file=sys.stderr)
        return 2
    print(design_summary(result), end="")
    return 0 if result.succeeded else 2


if __name__ == "__main__":
    raise SystemExit(main())
