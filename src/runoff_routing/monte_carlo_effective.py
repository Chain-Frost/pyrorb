"""Explicit, streaming Monte Carlo event boundary; no sampling or solver arithmetic.

#146 owns the stochastic sample-plan schema, probability-to-depth interpolation
and weights. This module accepts its independently materialised events, retains
the exact effective rainfall/loss inputs and prevents double application.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Literal, Never, cast

from .arr_arf import apply_arr2019_arf_to_bom_storm, calculate_arr2019_arf, published_coefficients
from .arr_patterns import PatternSet
from .arr_storm import RawHyetograph
from .project_batch import ProjectEvent
from .project_json import SourceFile
from .rorb_model import RunModel

EFFECTIVE_FORMAT = "python-runoff-routing-mc-effective-events"
EFFECTIVE_VERSION = 1
MAX_LINE_BYTES = 64 * 1024
MAX_EVENTS = 2_000_000
_ID = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,127}\Z")
_SHA = re.compile(r"[0-9a-f]{64}\Z")
LossPolicy = Literal["none", "subtract_reject", "subtract_clamp"]


class MCInputError(ValueError):
    """A malformed, stale or method-incompatible explicit MC request."""


def _fail(message: str) -> Never:
    raise MCInputError(message)


def _decimal(value: object, label: str, *, positive: bool = False) -> Decimal:
    if not isinstance(value, str):
        _fail(f"{label} must be an exact decimal string")
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        message = f"Invalid {label} decimal"
        raise MCInputError(message) from exc
    if not number.is_finite() or number < 0 or (positive and number == 0):
        _fail(f"{label} must be finite and {'positive' if positive else 'nonnegative'}")
    return number


def _id(value: object, label: str) -> str:
    if not isinstance(value, str) or _ID.fullmatch(value) is None:
        _fail(f"{label} must be a stable ASCII identifier")
    return value


def _int(value: object, label: str, *, max_value: int = MAX_EVENTS) -> int:
    if type(value) is not int or not 0 < value <= max_value:
        _fail(f"{label} must be a positive bounded integer")
    return value


def _sha(value: object, label: str) -> str:
    if not isinstance(value, str) or _SHA.fullmatch(value) is None:
        _fail(f"{label} must be a lowercase SHA-256")
    return value


def _obj(value: object, keys: set[str], label: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != keys:
        _fail(f"{label} has an unsupported shape; expected {sorted(keys)}")
    return cast("dict[str, object]", value)


def _pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            _fail(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _constant(value: str) -> Never:
    _fail(f"Nonstandard JSON constant: {value}")


def _line_json(raw: bytes) -> object:
    if not raw.endswith(b"\n") or not 1 <= len(raw) <= MAX_LINE_BYTES:
        _fail("Every effective-event JSONL record must end with newline and fit in 64 KiB")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_constant)
    except (UnicodeError, ValueError, TypeError) as exc:
        message = "Malformed effective-event JSONL record"
        raise MCInputError(message) from exc


def _json_line(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode("utf-8")


@dataclass(frozen=True, slots=True)
class MCPopulation:
    """Probability mass applies separately to every duration and scenario."""

    scenario_id: str
    duration_min: int
    modelled_mass: Decimal

    def __post_init__(self) -> None:
        _id(self.scenario_id, "scenario_id")
        _int(self.duration_min, "duration_min", max_value=10080)
        if not self.modelled_mass.is_finite() or not 0 < self.modelled_mass <= 1:
            _fail("modelled_mass must be in (0, 1]; unmodelled tails are never normalised away")

    def to_dict(self) -> dict[str, object]:
        return {
            "scenario_id": self.scenario_id,
            "duration_min": self.duration_min,
            "modelled_mass": str(self.modelled_mass),
        }


@dataclass(frozen=True, slots=True)
class MCRequestHeader:
    """The canonical sample plan remains with #146; this is its execution boundary."""

    plan_sha256: str
    policy_id: str
    source_files: tuple[SourceFile, ...]
    populations: tuple[MCPopulation, ...]
    event_count: int

    def __post_init__(self) -> None:
        _sha(self.plan_sha256, "plan_sha256")
        _id(self.policy_id, "policy_id")
        _int(self.event_count, "event_count")
        if not self.populations:
            _fail("At least one declared duration/scenario population is required")
        keys = tuple((item.scenario_id, item.duration_min) for item in self.populations)
        if len(set(keys)) != len(keys):
            _fail("Duplicate MC populations")
        paths = tuple(item.path for item in self.source_files)
        if len(set(paths)) != len(paths):
            _fail("Duplicate source-file paths")

    def to_dict(self) -> dict[str, object]:
        return {
            "format": EFFECTIVE_FORMAT,
            "schema_version": EFFECTIVE_VERSION,
            "plan_sha256": self.plan_sha256,
            "policy_id": self.policy_id,
            "source_files": [{"path": item.path, "sha256": item.sha256} for item in self.source_files],
            "populations": [item.to_dict() for item in self.populations],
            "event_count": self.event_count,
        }


@dataclass(frozen=True, slots=True)
class EffectiveMCEvent:
    """A completed B draw with once-applied ARF and burst IL, ready for the #119 runner."""

    sample_id: str
    scenario_id: str
    duration_min: int
    stratum_id: str
    stratum_mass: Decimal
    stratum_size: int
    probability_weight: Decimal
    original_tp_id: str
    original_tp_order: int
    rainfall_aep_percent: Decimal
    gross_depth_mm: Decimal
    arf_factor: Decimal
    storm_initial_loss_mm: Decimal
    preburst_depth_mm: Decimal
    loss_policy: LossPolicy
    event: ProjectEvent

    def __post_init__(self) -> None:
        self._validate_identity()
        self._validate_probabilities()
        self._validate_preburst()
        self._validate_overrides()

    def _validate_identity(self) -> None:
        for value, label in (
            (self.sample_id, "sample_id"),
            (self.scenario_id, "scenario_id"),
            (self.stratum_id, "stratum_id"),
        ):
            _id(value, label)
        _int(self.duration_min, "duration_min", max_value=10080)
        _int(self.stratum_size, "stratum_size")
        _int(self.original_tp_order, "original_tp_order")
        if not self.original_tp_id or any(ord(char) < 32 for char in self.original_tp_id):
            _fail("An original TP source identifier is mandatory")
        if self.event.event_id != self.sample_id or self.event.routing is not None:
            _fail("MC event ID must equal its sample ID; routing coefficients remain fixed")

    def _validate_probabilities(self) -> None:
        if (
            not all(
                value.is_finite()
                for value in (
                    self.stratum_mass,
                    self.probability_weight,
                    self.rainfall_aep_percent,
                    self.gross_depth_mm,
                    self.arf_factor,
                    self.storm_initial_loss_mm,
                    self.preburst_depth_mm,
                )
            )
            or not 0 < self.stratum_mass <= 1
            or not 0 < self.probability_weight <= 1
            or self.probability_weight != self.stratum_mass / self.stratum_size
            or not 1 <= self.rainfall_aep_percent <= 50
            or self.gross_depth_mm < 0
            or not 0 <= self.arf_factor <= 1
            or self.storm_initial_loss_mm < 0
            or self.preburst_depth_mm < 0
        ):
            _fail("Invalid MC probability, rainfall/ARF or storm-loss values")

    def _validate_preburst(self) -> None:
        if self.loss_policy not in {"none", "subtract_reject", "subtract_clamp"}:
            _fail("Unsupported preburst transformation policy")
        if self.loss_policy == "none" and self.preburst_depth_mm != 0:
            _fail("No-preburst policy cannot consume a positive preburst depth")
        if self.loss_policy == "subtract_reject" and self.preburst_depth_mm > self.storm_initial_loss_mm:
            _fail("Preburst exceeds sampled storm IL; explicit clamp policy required")

    def _validate_overrides(self) -> None:
        if self.event.storm is None or self.event.losses is None:
            _fail("MC events must include explicit storm and loss overrides")
        storm = self.event.storm
        losses = self.event.losses
        if not {"percentages", "depths_mm", "timestep_hours", "calculation_increments"}.issubset(storm):
            _fail("Effective storm must contain its complete hyetograph and horizon")
        percentages = storm["percentages"]
        depths = storm["depths_mm"]
        if not isinstance(percentages, list) or not percentages or not isinstance(depths, list) or not depths:
            _fail("Effective rainfall increments and subarea depths must be nonempty arrays")
        if sum((_decimal(v, "pattern percentage") for v in percentages), Decimal(0)) != 100:
            _fail("Original pattern percentages must total exactly 100, without renormalisation")
        total = self.gross_depth_mm * self.arf_factor
        if any(_decimal(v, "areal rainfall") != total for v in depths):
            _fail("Every pervious subarea needs gross rainfall multiplied by ARF exactly once")
        timestep = _decimal(storm["timestep_hours"], "timestep_hours", positive=True)
        if timestep * len(percentages) * 60 != self.duration_min:
            _fail("Temporal-pattern timestep and duration disagree")
        _int(storm["calculation_increments"], "calculation_increments")
        if cast("int", storm["calculation_increments"]) < len(percentages):
            _fail("Routing horizon must include the full storm")
        burst = max(Decimal(0), self.storm_initial_loss_mm - self.preburst_depth_mm)
        if _decimal(losses.get("initial_loss_mm"), "effective burst IL") != burst:
            _fail("Effective loss must be sampled storm IL minus preburst exactly once")
        _decimal(losses.get("continuing"), "fixed continuing loss")

    def to_dict(self) -> dict[str, object]:
        return {
            "sample_id": self.sample_id,
            "scenario_id": self.scenario_id,
            "duration_min": self.duration_min,
            "stratum_id": self.stratum_id,
            "stratum_mass": str(self.stratum_mass),
            "stratum_size": self.stratum_size,
            "probability_weight": str(self.probability_weight),
            "original_tp_id": self.original_tp_id,
            "original_tp_order": self.original_tp_order,
            "rainfall_aep_percent": str(self.rainfall_aep_percent),
            "gross_depth_mm": str(self.gross_depth_mm),
            "arf_factor": str(self.arf_factor),
            "storm_initial_loss_mm": str(self.storm_initial_loss_mm),
            "preburst_depth_mm": str(self.preburst_depth_mm),
            "loss_policy": self.loss_policy,
            "event": {
                "event_id": self.sample_id,
                "storm": dict(self.event.storm or {}),
                "losses": dict(self.event.losses or {}),
            },
        }

    def digest(self) -> str:
        """Bind a result to all exact effective inputs, not merely its logical sample ID."""
        return hashlib.sha256(_json_line(self.to_dict())).hexdigest()


def read_header(path: Path) -> MCRequestHeader:
    with path.open("rb") as stream:
        raw = stream.readline(MAX_LINE_BYTES + 1)
    data = _obj(
        _line_json(raw),
        {"format", "schema_version", "plan_sha256", "policy_id", "source_files", "populations", "event_count"},
        "MC header",
    )
    if (
        data["format"] != EFFECTIVE_FORMAT
        or type(data["schema_version"]) is not int
        or data["schema_version"] != EFFECTIVE_VERSION
    ):
        _fail("Unknown MC effective-event schema/format")
    raw_sources = data["source_files"]
    raw_populations = data["populations"]
    if not isinstance(raw_sources, list) or not isinstance(raw_populations, list):
        _fail("MC header source_files and populations must be arrays")
    sources = tuple(
        SourceFile(
            cast("str", _obj(item, {"path", "sha256"}, "source file")["path"]),
            _sha(_obj(item, {"path", "sha256"}, "source file")["sha256"], "source sha256"),
        )
        for item in raw_sources
    )
    populations = tuple(
        MCPopulation(
            _id(_obj(item, {"scenario_id", "duration_min", "modelled_mass"}, "population")["scenario_id"], "scenario"),
            _int(
                _obj(item, {"scenario_id", "duration_min", "modelled_mass"}, "population")["duration_min"], "duration"
            ),
            _decimal(
                _obj(item, {"scenario_id", "duration_min", "modelled_mass"}, "population")["modelled_mass"], "mass"
            ),
        )
        for item in raw_populations
    )
    return MCRequestHeader(
        plan_sha256=_sha(data["plan_sha256"], "plan hash"),
        policy_id=_id(data["policy_id"], "policy_id"),
        source_files=sources,
        populations=populations,
        event_count=_int(data["event_count"], "event count"),
    )


def _event_from_dict(raw: object) -> EffectiveMCEvent:
    keys = {
        "sample_id",
        "scenario_id",
        "duration_min",
        "stratum_id",
        "stratum_mass",
        "stratum_size",
        "probability_weight",
        "original_tp_id",
        "original_tp_order",
        "rainfall_aep_percent",
        "gross_depth_mm",
        "arf_factor",
        "storm_initial_loss_mm",
        "preburst_depth_mm",
        "loss_policy",
        "event",
    }
    item = _obj(raw, keys, "effective MC event")
    event = _obj(item["event"], {"event_id", "storm", "losses"}, "project event")
    storm = event["storm"]
    losses = event["losses"]
    if not isinstance(storm, dict) or not isinstance(losses, dict):
        _fail("MC project storm and losses must be JSON objects")
    policy = item["loss_policy"]
    if policy not in {"none", "subtract_reject", "subtract_clamp"}:
        _fail("Unknown effective event loss policy")
    if not isinstance(item["original_tp_id"], str):
        _fail("Temporal pattern source ID must be text")
    return EffectiveMCEvent(
        sample_id=_id(item["sample_id"], "sample_id"),
        scenario_id=_id(item["scenario_id"], "scenario_id"),
        duration_min=_int(item["duration_min"], "duration_min", max_value=10080),
        stratum_id=_id(item["stratum_id"], "stratum_id"),
        stratum_mass=_decimal(item["stratum_mass"], "stratum mass", positive=True),
        stratum_size=_int(item["stratum_size"], "stratum size"),
        probability_weight=_decimal(item["probability_weight"], "sample weight", positive=True),
        original_tp_id=item["original_tp_id"],
        original_tp_order=_int(item["original_tp_order"], "TP source order"),
        rainfall_aep_percent=_decimal(item["rainfall_aep_percent"], "AEP", positive=True),
        gross_depth_mm=_decimal(item["gross_depth_mm"], "gross depth"),
        arf_factor=_decimal(item["arf_factor"], "ARF"),
        storm_initial_loss_mm=_decimal(item["storm_initial_loss_mm"], "storm IL"),
        preburst_depth_mm=_decimal(item["preburst_depth_mm"], "preburst depth"),
        loss_policy=cast("LossPolicy", policy),
        event=ProjectEvent(
            event_id=_id(event["event_id"], "event_id"),
            storm=cast("Mapping[str, object]", storm),
            losses=cast("Mapping[str, object]", losses),
        ),
    )


def iter_effective_events(path: Path) -> Iterator[EffectiveMCEvent]:
    """Streaming JSONL records; no eager 8 MiB array loader or hydrographs."""
    with path.open("rb") as stream:
        if not stream.readline(MAX_LINE_BYTES + 1):
            _fail("Empty effective-event request")
        for ordinal, raw in enumerate(iter(lambda: stream.readline(MAX_LINE_BYTES + 1), b""), start=1):
            if not raw or len(raw) > MAX_LINE_BYTES:
                _fail(f"Effective record {ordinal} exceeds 64 KiB")
            yield _event_from_dict(_line_json(raw))


def _digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_effective_request(path: Path) -> tuple[MCRequestHeader, str]:
    """Validate full population mass/counts and source hashes without loading routed Q."""
    header = read_header(path)
    for source in header.source_files:
        candidate = path.absolute().parent / source.path
        if not candidate.is_file() or candidate.is_symlink() or _digest_file(candidate) != source.sha256:
            _fail(f"MC source is missing, modified or a symlink: {source.path}")
    target = {(p.scenario_id, p.duration_min): p.modelled_mass for p in header.populations}
    strata: dict[tuple[str, int, str], tuple[Decimal, int, int]] = {}
    seen: set[str] = set()
    count = 0
    for record in iter_effective_events(path):
        count += 1
        key = (record.scenario_id, record.duration_min, record.stratum_id)
        if record.sample_id in seen or (record.scenario_id, record.duration_min) not in target:
            _fail("Duplicate sample ID or an undeclared scenario/duration")
        seen.add(record.sample_id)
        mass, size, actual = strata.get(key, (record.stratum_mass, record.stratum_size, 0))
        if (mass, size) != (record.stratum_mass, record.stratum_size):
            _fail("Inconsistent stratum probability mass/allocation within a plan")
        strata[key] = (mass, size, actual + 1)
    if count != header.event_count:
        _fail("Effective event count differs from the immutable request header")
    sums: dict[tuple[str, int], Decimal] = defaultdict(Decimal)
    for (scenario, duration, _), (mass, size, actual) in strata.items():
        if size != actual:
            _fail("Missing or excessive event members for a declared stratum")
        sums[(scenario, duration)] += mass
    if sums != target:
        _fail("A scenario/duration population omits probability strata or exceeds declared modelled mass")
    return header, _digest_file(path)


def write_effective_request(path: Path, header: MCRequestHeader, records: Iterable[EffectiveMCEvent]) -> None:
    """Exclusive-create a streaming B-to-E execution file; no stochastic draws occur here."""
    created = False
    try:
        with path.open("xb") as stream:
            created = True
            stream.write(_json_line(header.to_dict()))
            count = 0
            for item in records:
                count += 1
                if count > header.event_count:
                    _fail("Too many explicit events for header")
                encoded = _json_line(item.to_dict())
                if len(encoded) > MAX_LINE_BYTES:
                    _fail("Oversized explicit MC event")
                stream.write(encoded)
            if count != header.event_count:
                _fail("Missing explicit events for header")
        validate_effective_request(path)
    except (OSError, ValueError):
        if created:
            path.unlink(missing_ok=True)
        raise


def materialise_arr_sample(
    *,
    model: RunModel,
    pattern_set: PatternSet,
    pattern_source_order: int,
    sample_id: str,
    scenario_id: str,
    stratum_id: str,
    stratum_mass: Decimal,
    stratum_size: int,
    rainfall_aep_percent: Decimal,
    gross_depth_mm: Decimal,
    bom_source_sha256: str,
    arf_region: str,
    storm_initial_loss_mm: Decimal,
    preburst_depth_mm: Decimal,
    preburst_policy: LossPolicy,
    dry_tail_min: int,
) -> EffectiveMCEvent:
    """Materialise B's sampled depth/TP/IL using established ARR ARF exactly once.

    No rainfall-depth interpolation, TP draw or stochastic loss draw is made here.
    Only fixed IL/CL, one ISA/pluviograph, pervious subareas and fixed kc/m apply.
    """
    if (
        model.parameters.num_isa != 1
        or model.parameters.loss_model != 1
        or len(model.parameters.losses) != 1
        or model.parameters.num_bursts != 1
        or len(model.storm.subarea_ids) != len(model.catchment.subareas)
        or any(area.impervious_fraction != 0 for area in model.catchment.subareas)
        or model.storm.preburst_bins
        or model.storm.pattern_basis != "percent_of_depth"
    ):
        _fail("MC materialisation requires one pervious ISA/burst/pluviograph with IL/CL")
    if not isinstance(dry_tail_min, int) or isinstance(dry_tail_min, bool) or dry_tail_min < 0:
        _fail("dry_tail_min must be a nonnegative whole number")
    _sha(bom_source_sha256, "BoM input SHA-256")
    if pattern_source_order <= 0 or pattern_source_order > len(pattern_set.patterns):
        _fail("TP source ordinal is missing from the original pattern file")
    pattern = pattern_set.patterns[pattern_source_order - 1]
    if pattern_set.kind != ("point" if sum(a.area_km2 for a in model.catchment.subareas) < 75 else "areal"):
        _fail("Point/areal TP source selection disagrees with the catchment area")
    if pattern.duration_min % pattern.timestep_min or dry_tail_min % pattern.timestep_min:
        _fail("Storm duration and dry tail must divide exactly by the source TP timestep")
    if sum(pattern.increments_percent, Decimal(0)) != 100:
        _fail("MC requires exact original 100% TP increments")
    if not gross_depth_mm.is_finite() or gross_depth_mm < 0:
        _fail("B-sampled gross depth is not finite and nonnegative mm")
    area = sum((part.area_km2 for part in model.catchment.subareas), Decimal(0))
    gross = RawHyetograph(
        duration_min=pattern.duration_min,
        timestep_min=pattern.timestep_min,
        pattern_event_id=pattern.event_id,
        pattern_region=pattern.region,
        pattern_aep_band=pattern.aep_band,
        pattern_area_bin=pattern.area_bin,
        source_label="BoM 2016 IFD (raw gross rainfall)",
        source_sha256=bom_source_sha256,
        pattern_source_sha256=pattern_set.source_sha256,
        probability_label=f"{rainfall_aep_percent}%",
        source_rainfall_depth_mm=gross_depth_mm,
        increments_mm=tuple(gross_depth_mm * step / 100 for step in pattern.increments_percent),
        end_times_min=tuple(range(pattern.timestep_min, pattern.duration_min + 1, pattern.timestep_min)),
        total_mm=gross_depth_mm,
        operations=("B_EXPLICIT_GROSS_DEPTH_MM", "SOURCE_TP_PERCENT_ONLY", "NO_ARF_OR_LOSS_YET"),
    )
    factor = calculate_arr2019_arf(
        catchment_area_km2=area,
        duration_min=pattern.duration_min,
        aep_percent=rainfall_aep_percent,
        coefficients=published_coefficients(arf_region),
    )
    areal = apply_arr2019_arf_to_bom_storm(gross, factor)
    if preburst_policy == "none" and preburst_depth_mm != 0:
        _fail("No-preburst policy cannot subtract a positive preburst")
    if preburst_policy == "subtract_reject" and preburst_depth_mm > storm_initial_loss_mm:
        _fail("Preburst exceeds sampled storm IL; explicit clamp policy required")
    burst_initial_loss = max(Decimal(0), storm_initial_loss_mm - preburst_depth_mm)
    override: dict[str, object] = {
        "title": f"MC {pattern.duration_min} min {rainfall_aep_percent}% TP {pattern.event_id}",
        "timestep_hours": str(Decimal(pattern.timestep_min) / 60),
        "start_increment": 0,
        "calculation_increments": len(pattern.increments_percent) + dry_tail_min // pattern.timestep_min,
        "percentages": [str(value) for value in pattern.increments_percent],
        "depths_mm": [str(areal.total_mm)] * len(model.storm.subarea_ids),
    }
    return EffectiveMCEvent(
        sample_id=sample_id,
        scenario_id=scenario_id,
        duration_min=pattern.duration_min,
        stratum_id=stratum_id,
        stratum_mass=stratum_mass,
        stratum_size=stratum_size,
        probability_weight=stratum_mass / stratum_size,
        original_tp_id=pattern.event_id,
        original_tp_order=pattern_source_order,
        rainfall_aep_percent=rainfall_aep_percent,
        gross_depth_mm=gross_depth_mm,
        arf_factor=factor.factor,
        storm_initial_loss_mm=storm_initial_loss_mm,
        preburst_depth_mm=preburst_depth_mm,
        loss_policy=preburst_policy,
        event=ProjectEvent(
            sample_id,
            storm=override,
            losses={
                "initial_loss_mm": str(burst_initial_loss),
                "continuing": str(model.parameters.losses[0].continuing),
            },
        ),
    )
