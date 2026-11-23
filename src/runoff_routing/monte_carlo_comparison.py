"""Source-neutral, nonexecuting RORBwin Monte Carlo comparison evidence contract.

This module neither parses native text nor reconstructs native event weights,
random streams, effective inputs or statistical policies. Only the pinned
canonical ryan-tools reader may admit original source tokens (#191/#334).
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Literal, Never

FieldQuality = Literal["exact_effective", "rounded_print", "displayed_setting", "inferred", "unavailable"]
LaneStatus = Literal["descriptive_only", "unavailable", "not_comparable"]

_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_FIELD_QUALITIES = frozenset(("exact_effective", "rounded_print", "displayed_setting", "inferred", "unavailable"))
_MAX_TOKEN_CHARS = 256
_MAX_TOKEN_EXPONENT = 10_000


class MCComparisonInputError(ValueError):
    """Invalid source identity, scope or source-token classification."""


def _fail(message: str) -> Never:
    raise MCComparisonInputError(message)


def _name(value: str, label: str) -> None:
    if not isinstance(value, str) or not value or value != value.strip() or any(ord(ch) < 32 for ch in value):
        _fail(f"{label} must be nonempty trimmed text without controls")


def _digest(value: str | None, label: str, *, required: bool = False) -> None:
    if value is None and not required:
        return
    if value is None or _SHA256.fullmatch(value) is None:
        _fail(f"{label} must be a lowercase SHA-256 digest")


def _decimal_endpoint(coefficient: int, exponent: int) -> Decimal:
    """Construct an exact decimal endpoint without ambient Context arithmetic."""
    digits = tuple(int(digit) for digit in str(abs(coefficient)))
    return Decimal((int(coefficient < 0), digits, exponent))


@dataclass(frozen=True, slots=True)
class MCNativeSource:
    """Report provenance separate from executable/catchment identity and claims."""

    report_sha256: str
    reported_version: str | None = None
    executable_sha256: str | None = None
    model_sha256: str | None = None

    def __post_init__(self) -> None:
        _digest(self.report_sha256, "report_sha256", required=True)
        _digest(self.executable_sha256, "executable_sha256")
        _digest(self.model_sha256, "model_sha256")
        if self.reported_version is not None:
            _name(self.reported_version, "reported_version")


@dataclass(frozen=True, slots=True)
class MCEventKey:
    """Native row key; neither global run number nor Python sample identity."""

    cohort_id: str
    replication_id: str
    duration_minutes: int
    division: int
    run: int
    scenario_id: str | None = None
    physical_site_id: str | None = None

    def __post_init__(self) -> None:
        _name(self.cohort_id, "cohort_id")
        _name(self.replication_id, "replication_id")
        for label, value in (
            ("duration_minutes", self.duration_minutes),
            ("division", self.division),
            ("run", self.run),
        ):
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                _fail(f"{label} must be a positive integer")
        if self.scenario_id is not None:
            _name(self.scenario_id, "scenario_id")
        if self.physical_site_id is not None:
            _name(self.physical_site_id, "physical_site_id")


@dataclass(frozen=True, slots=True)
class MCField:
    """Retains a canonical reader's source token, never a native internal value."""

    quality: FieldQuality
    token: str | None = None
    unit: str | None = None
    source_line: int | None = None

    def __post_init__(self) -> None:
        if self.quality not in _FIELD_QUALITIES:
            _fail("unsupported field quality")
        if self.quality == "unavailable":
            if self.token is not None or self.unit is not None or self.source_line is not None:
                _fail("unavailable fields cannot have invented values or source lines")
            return
        if self.token is None or self.unit is None:
            _fail("available fields require a source token and unit")
        _name(self.unit, "unit")
        if self.source_line is not None and (
            not isinstance(self.source_line, int) or isinstance(self.source_line, bool) or self.source_line < 1
        ):
            _fail("source_line must be a positive integer")
        _ = self.decimal

    @property
    def decimal(self) -> Decimal | None:
        """Decimal rendering of a *source-validated* token, not a recovered draw."""
        if self.token is None:
            return None
        if not self.token or self.token != self.token.strip() or "_" in self.token:
            _fail("noncanonical source numeric token")
        if len(self.token) > _MAX_TOKEN_CHARS:
            _fail("source numeric token too long")
        try:
            value = Decimal(self.token.replace("D", "E").replace("d", "e"))
        except InvalidOperation as exc:
            message = "invalid source numeric token"
            raise MCComparisonInputError(message) from exc
        if not value.is_finite():
            _fail("nonfinite source numeric token")
        if abs(int(value.as_tuple().exponent)) > _MAX_TOKEN_EXPONENT:
            _fail("source numeric exponent exceeds safe evidence range")
        return value

    def conditional_nearest_print_interval(self) -> tuple[Decimal, Decimal] | None:
        """Half-print-unit bounds **if** the emitter rounded to nearest.

        No evidence currently qualifies RORBwin's actual rounding rule. A
        printed zero or a value inside these bounds is not exact event parity.
        """
        if self.quality != "rounded_print":
            return None
        number = self.decimal
        if number is None:
            _fail("printed field is missing its source token")
        # Construct each endpoint from an exact signed integer coefficient.
        # Decimal arithmetic would depend on the caller's precision and could
        # erase the half-print-unit (especially for printed zeros or long tokens).
        parts = number.as_tuple()
        coefficient = 0
        for digit in parts.digits:
            coefficient = coefficient * 10 + digit
        if parts.sign:
            coefficient = -coefficient
        exponent = int(parts.exponent) - 1
        return _decimal_endpoint(coefficient * 10 - 5, exponent), _decimal_endpoint(coefficient * 10 + 5, exponent)


@dataclass(frozen=True, slots=True)
class MCNativeRecord:
    """One supported observed/partial record, never a complete effective event."""

    source: MCNativeSource
    key: MCEventKey
    peak_m3s: MCField
    rainfall_probability: MCField
    native_tp_rank: int | None = None
    original_tp_event_id: str | None = None
    python_sample_id: str | None = None
    native_event_weight: MCField = field(default_factory=lambda: MCField("unavailable"))

    def __post_init__(self) -> None:
        if self.native_tp_rank is not None and (
            not isinstance(self.native_tp_rank, int) or isinstance(self.native_tp_rank, bool) or self.native_tp_rank < 1
        ):
            _fail("native_tp_rank must be a positive integer")
        if self.original_tp_event_id is not None:
            _name(self.original_tp_event_id, "original_tp_event_id")
        if self.python_sample_id is not None:
            _name(self.python_sample_id, "python_sample_id")


@dataclass(frozen=True, slots=True)
class ComparisonReadiness:
    """Explicitly unsupported scientific lanes cannot be silently promoted."""

    input_law: LaneStatus
    exact_event_replay: LaneStatus
    native_weighted_reaggregation: LaneStatus
    native_published_summary: LaneStatus
    reasons: tuple[str, ...]


def assess_native_comparison(records: tuple[MCNativeRecord, ...]) -> ComparisonReadiness:
    """Admit only descriptive printed fields; do not invent weights or replay."""
    if not records:
        return ComparisonReadiness("unavailable", "unavailable", "unavailable", "unavailable", ("no_native_records",))
    seen: set[MCEventKey] = set()
    for record in records:
        if record.key in seen:
            _fail("duplicate cohort/replication/duration/division/run/site identity")
        seen.add(record.key)
    has_diagnostic = any(r.rainfall_probability.quality in {"rounded_print", "exact_effective"} for r in records)
    # No current admitted exact effective-input ledger, source EventID binding or
    # native probability-weight law; a field claiming 'exact' cannot waive gates.
    return ComparisonReadiness(
        "descriptive_only" if has_diagnostic else "unavailable",
        "unavailable",
        "unavailable",
        "unavailable",
        (
            "native_original_event_inputs_unavailable",
            "native_interval_weights_unqualified",
            "native_frequency_policy_unqualified",
            "reported_values_are_not_a_native_equivalence_test",
        ),
    )


def comparison_json_ready(records: tuple[MCNativeRecord, ...]) -> dict[str, object]:
    """Stable JSON-compatible report with full provenance and evidence labels."""
    readiness = assess_native_comparison(records)
    return {
        "schema": "pyrorb-native-mc-comparison-evidence/1",
        "records": [asdict(r) for r in records],
        "readiness": asdict(readiness),
    }
