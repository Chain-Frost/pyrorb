"""Authenticated native scalar adapter for the existing maintained dataset runner."""

from __future__ import annotations

import math
from dataclasses import asdict
from fractions import Fraction
from typing import Any

from .regression_metrics import SiteMetrics, bind_report_metrics, compare_peak, compare_reported_volume
from .rorb_documents import RorbSource
from .rorb_out import inspect_output

POLICY = "cmd644-report-scalars-v1"


def bind_scalars(source: RorbSource, binding: dict[str, Any]) -> SiteMetrics:
    """Re-extract original tokens and enforce exact site/unit/selector bindings."""
    inspection = inspect_output(source)
    report = inspection.hydrographs
    if report is None or any(item.severity == "error" for item in inspection.diagnostics):
        message = "Original native report is missing a valid complete hydrograph table"
        raise ValueError(message)
    sites = bind_report_metrics(source, report)
    if len(sites) != 1 or sites[0].column != binding["native_column"]:
        message = "Scalar adapter requires the authenticated single terminal print site"
        raise ValueError(message)
    site = sites[0]
    for name, attribute in (("peak", site.peak), ("peak_time", site.peak_time), ("volume", site.volume)):
        if attribute is None:
            continue
        selector = asdict(attribute)
        selector.pop("token")
        if selector != binding["scalar_selectors"][name]:
            message = f"Original scalar selector/unit mismatch: {name}"
            raise ValueError(message)
    return site


def stored_float(token: object) -> float:
    """Require canonical finite nonnegative binary64 hexadecimal representations."""
    if not isinstance(token, str):
        message = "Candidate values must be canonical float.hex strings"
        raise TypeError(message)
    value = float.fromhex(token)
    if not math.isfinite(value) or value < 0 or value.hex() != token:
        message = "Candidate values must be finite nonnegative canonical float.hex strings"
        raise ValueError(message)
    return value


def compare_scalars(series: dict[str, Any], site: SiteMetrics) -> dict[str, Any]:
    """Attempt peak/time first, then independently evaluate reported volume."""
    flows = tuple(stored_float(value) for value in series["q_hex"])
    hours = Fraction(stored_float(series["h_hex"]))
    seconds = Fraction(stored_float(series["dt_hex"]))
    peak = compare_peak(flows, hours, site)
    volume = compare_reported_volume(flows, seconds, site)
    actual_volume = seconds * sum(map(Fraction, flows), start=Fraction(0))
    fields: dict[str, Any] = {
        "peak_magnitude": {"verdict": peak.magnitude, "actual_exact": str(peak.candidate_peak)},
        "peak_time": {
            "verdict": peak.time,
            "reason": peak.time_reason,
            "actual_exact": str(peak.candidate_elapsed_hours) if peak.candidate_elapsed_hours is not None else None,
            "tied_indices": peak.candidate_tied_indices,
        },
        "native_reported_volume": {"verdict": volume, "actual_exact": str(actual_volume)},
    }
    for name, original in (
        ("peak_magnitude", site.peak),
        ("peak_time", site.peak_time),
        ("native_reported_volume", site.volume),
    ):
        fields[name]["reference"] = asdict(original) if original is not None else None
    return fields
