"""Diagnostic absolute and percentage errors against aligned RORB CMD ordinates.

CMD is the reference for engineering-v1 accuracy; numerical error summaries
are not themselves pass/fail policies. Match physical print sites and the
effective time axis *before* using this pure arithmetic helper.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from itertools import pairwise


@dataclass(frozen=True, slots=True)
class CmdDeviation:
    """Model-grid differences; signed percentages always use CMD denominators."""

    sample_count: int
    timestep_hours: float
    cmd_peak_m3_s: float
    python_peak_m3_s: float
    cmd_peak_index: int
    python_peak_index: int
    peak_index_offset: int
    peak_difference_m3_s: float
    peak_difference_pct: float | None
    max_absolute_ordinate_difference_m3_s: float
    max_absolute_ordinate_difference_pct_cmd_peak: float | None
    rms_ordinate_difference_m3_s: float
    rms_ordinate_difference_pct_cmd_peak: float | None
    cmd_trapezoidal_volume_m3: float
    python_trapezoidal_volume_m3: float
    volume_difference_m3: float
    volume_difference_pct: float | None


def _percent(difference: float, reference: float) -> float | None:
    if reference == 0.0:
        return None
    percent = 100.0 * (difference / reference)
    if not math.isfinite(percent):
        msg = "Reference-normalised CMD percentage is not representable."
        raise ValueError(msg)
    return percent


def _physical_trapezoid(values: tuple[float, ...], dt_hours: float) -> float:
    integrated = 1800.0 * dt_hours * math.fsum(a + b for a, b in pairwise(values))
    if not math.isfinite(integrated):
        msg = "Physical horizon volume is not finite."
        raise ValueError(msg)
    return integrated


def assess_cmd_deviation(
    python_m3_s: Sequence[float],
    cmd_m3_s: Sequence[float],
    *,
    timestep_hours: float,
) -> CmdDeviation:
    """Summarise same-site, same-grid full hydrographs using RORB CMD as truth.

    Caller must verify case identity, physical print association, effective
    rainfall, sample time and original/native provenance independently.
    Original CMD inclusive reported volume is not a physical integral.
    Neither zero reference nor tiny individual discharges are made into
    spurious local percentages; the common ordinate denominator is CMD peak.
    """
    if not math.isfinite(timestep_hours) or timestep_hours <= 0.0:
        msg = "Matched CMD timestep must be positive and finite."
        raise ValueError(msg)
    predicted, reference = tuple(python_m3_s), tuple(cmd_m3_s)
    if len(predicted) != len(reference) or len(reference) < 2:
        msg = "CMD comparison requires equal complete time grids with at least two samples."
        raise ValueError(msg)
    if any(not math.isfinite(value) or value < 0.0 for value in (*predicted, *reference)):
        msg = "CMD comparison ordinates must be nonnegative and finite."
        raise ValueError(msg)
    differences = tuple(a - b for a, b in zip(predicted, reference, strict=True))
    absolute = tuple(abs(value) for value in differences)
    max_abs = max(absolute)
    rms = math.sqrt(math.fsum(value * value for value in differences) / len(differences))
    py_peak, cmd_peak = max(predicted), max(reference)
    py_vol = _physical_trapezoid(predicted, timestep_hours)
    cmd_vol = _physical_trapezoid(reference, timestep_hours)
    return CmdDeviation(
        sample_count=len(reference),
        timestep_hours=timestep_hours,
        cmd_peak_m3_s=cmd_peak,
        python_peak_m3_s=py_peak,
        cmd_peak_index=reference.index(cmd_peak),
        python_peak_index=predicted.index(py_peak),
        peak_index_offset=predicted.index(py_peak) - reference.index(cmd_peak),
        peak_difference_m3_s=py_peak - cmd_peak,
        peak_difference_pct=_percent(py_peak - cmd_peak, cmd_peak),
        max_absolute_ordinate_difference_m3_s=max_abs,
        max_absolute_ordinate_difference_pct_cmd_peak=_percent(max_abs, cmd_peak),
        rms_ordinate_difference_m3_s=rms,
        rms_ordinate_difference_pct_cmd_peak=_percent(rms, cmd_peak),
        cmd_trapezoidal_volume_m3=cmd_vol,
        python_trapezoidal_volume_m3=py_vol,
        volume_difference_m3=py_vol - cmd_vol,
        volume_difference_pct=_percent(py_vol - cmd_vol, cmd_vol),
    )
