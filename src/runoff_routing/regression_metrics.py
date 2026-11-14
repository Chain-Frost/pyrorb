"""Small field-binding/comparison helpers for #53, not a suite runner or solver.

Reuse the existing public output inspector for hydrograph rows. Scalar selectors
are pinned to the retained CMD report dialect, preserving all original tokens.
"""

import math
import re
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from typing import Literal

from runoff_routing.rorb_documents import HydrographReport, RorbSource

Status = Literal["pass", "fail", "incomplete"]


@dataclass(frozen=True, slots=True)
class ScalarField:
    """Original lexeme and exact one-based report selector."""

    token: str
    line: int
    character: int
    ordinal: int
    unit: str


@dataclass(frozen=True, slots=True)
class SiteMetrics:
    """Explicit report legend identity and three original native scalars."""

    column: str
    label: str
    peak: ScalarField | None
    peak_time: ScalarField | None
    volume: ScalarField | None


@dataclass(frozen=True, slots=True)
class PeakComparison:
    """Native reporting results; exact hidden-state ties remain a distinct gate."""

    magnitude: Status
    time: Status
    time_reason: str
    candidate_tied_indices: tuple[int, ...]
    candidate_peak: Fraction
    candidate_elapsed_hours: Fraction | None


def token_interval(token: str) -> tuple[Fraction, Fraction]:
    """Original inclusive half-last-unit interval, clipped at physical zero."""
    if not token or token != token.strip() or "_" in token:
        message = "Scalar must retain one complete original numeric token"
        raise ValueError(message)
    try:
        value = Decimal(token)
    except InvalidOperation as exc:
        message = "Invalid scalar token"
        raise ValueError(message) from exc
    if not value.is_finite() or value < 0:
        message = "Scalar must be finite and nonnegative"
        raise ValueError(message)
    exponent = value.as_tuple().exponent
    if not isinstance(exponent, int):
        message = "Scalar has no finite decimal precision"
        raise TypeError(message)
    half = Fraction(Decimal(5).scaleb(exponent - 1))
    centre = Fraction(value)
    return max(Fraction(0), centre - half), centre + half


def _scalars(source: RorbSource, prefix: str, unit: str) -> tuple[ScalarField, ...]:
    fields: list[ScalarField] = []
    family = prefix.partition(",")[0] + ","
    for number, line in enumerate(source.lines, 1):
        if line.lstrip().startswith(family) and not line.lstrip().startswith(prefix):
            message = "Native scalar unit/scale differs from the selected reporting profile"
            raise ValueError(message)
        if not line.lstrip().startswith(prefix):
            continue
        offset = line.index(prefix) + len(prefix)
        for ordinal, match in enumerate(re.finditer(r"\S+", line[offset:]), 1):
            token_interval(match[0])
            fields.append(ScalarField(match[0], number, offset + match.start() + 1, ordinal, unit))
    return tuple(fields)


def _site_scalars(fields: tuple[ScalarField, ...], count: int) -> tuple[ScalarField | None, ...]:
    if not fields:
        return (None,) * count
    if len(fields) != count:
        message = "Ambiguous partial or duplicate native scalar population"
        raise ValueError(message)
    return fields


def bind_report_metrics(source: RorbSource, report: HydrographReport) -> tuple[SiteMetrics, ...]:
    """Match scalar flattening to the explicit original HydNNN legend order."""
    summaries = [i for i, line in enumerate(source.lines) if line.strip() == "Hydrograph summary"]
    if len(summaries) != 1:
        message = "Exactly one native hydrograph-summary legend is required"
        raise ValueError(message)
    labels: list[tuple[str, str]] = []
    for line in source.lines[summaries[0] + 1 : report.rows[0].line - 1]:
        match = re.fullmatch(r"\s*(\d{2})\s+(.+?)\s*", line)
        if match:
            labels.append((f"Hyd{int(match[1]):03d}", match[2]))
    count = len(report.columns)
    peaks = _site_scalars(_scalars(source, "Peak discharge,m³/s", "m3/s"), count)
    times = _site_scalars(_scalars(source, "Time to peak,h", "h"), count)
    volumes = _site_scalars(_scalars(source, "Volume,m³", "m3"), count)
    if tuple(name for name, _ in labels) != report.columns:
        message = "Native legend identity/order does not match actual table columns"
        raise ValueError(message)
    return tuple(
        SiteMetrics(column, label, peak, time, volume)
        for (column, label), peak, time, volume in zip(labels, peaks, times, volumes, strict=True)
    )


def _flows(values: Sequence[float]) -> tuple[Fraction, ...]:
    if not values or any(not math.isfinite(value) or value < 0 for value in values):
        message = "Complete finite nonnegative candidate flows are required"
        raise ValueError(message)
    return tuple(Fraction(value) for value in values)


def compare_peak(values: Sequence[float], timestep_hours: Fraction, binding: SiteMetrics) -> PeakComparison:
    """Compare a unique nonzero maximum; never choose a hidden native tie rule."""
    if timestep_hours <= 0:
        message = "Positive actual timestep required"
        raise ValueError(message)
    flows = _flows(values)
    peak = max(flows)
    ties = tuple(i for i, flow in enumerate(flows) if flow == peak)
    magnitude: Status = "incomplete"
    if binding.peak is not None:
        lower, upper = token_interval(binding.peak.token)
        magnitude = "pass" if lower <= peak <= upper else "fail"
    if peak == 0:
        return PeakComparison(magnitude, "incomplete", "zero_flow_time_undefined", ties, peak, None)
    if len(ties) != 1:
        return PeakComparison(magnitude, "incomplete", "native_tie_policy_unresolved", ties, peak, None)
    elapsed = ties[0] * timestep_hours
    if binding.peak_time is None:
        return PeakComparison(magnitude, "incomplete", "native_peak_time_scalar_absent", ties, peak, elapsed)
    lower, upper = token_interval(binding.peak_time.token)
    time: Status = "pass" if lower <= elapsed <= upper else "fail"
    return PeakComparison(magnitude, time, "unique_nonzero_candidate_peak", ties, peak, elapsed)


def compare_reported_volume(values: Sequence[float], duration_seconds: Fraction, binding: SiteMetrics) -> Status:
    """Compare only the frozen native inclusive sum, never physical closure."""
    if duration_seconds <= 0:
        message = "Positive actual duration required"
        raise ValueError(message)
    flows = _flows(values)
    if binding.volume is None:
        return "incomplete"
    value = duration_seconds * sum(flows, start=Fraction(0))
    lower, upper = token_interval(binding.volume.token)
    return "pass" if lower <= value <= upper else "fail"
