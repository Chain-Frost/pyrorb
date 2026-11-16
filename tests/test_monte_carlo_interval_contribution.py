"""Independent finite-ledger 20% rainfall-interval warning controls for #187.

All expected values use hand-calculated weighted probabilities and synthetic
flows. They do not reproduce or qualify native RORBwin 6.52 warning logic.
"""

from __future__ import annotations

import pytest

from runoff_routing.monte_carlo_frequency import (
    CurvePopulation,
    FrequencyCurve,
    FrequencyScope,
    PeakRecord,
    StratumWeight,
    UnmodelledTails,
    build_frequency_curve,
)
from runoff_routing.monte_carlo_frequency_bridge import _format_selected_aep_table


def _curve(
    peaks: tuple[float, ...],
    *,
    site: str = "print_1",
    missing_index: int | None = None,
    tails: UnmodelledTails | None = None,
) -> FrequencyCurve:
    scope = FrequencyScope("plan-187", "independent", "v1", "synthetic", 1440, site)
    tails = tails if tails is not None else UnmodelledTails()
    mass = (1 - tails.total) / len(peaks)
    allocations = tuple(StratumWeight(f"interval-{i}", mass, 1) for i in range(len(peaks)))
    records = tuple(
        PeakRecord(
            scope,
            f"interval-{i}",
            f"sample-{i}",
            mass,
            "missing" if i == missing_index else "valid",
            None if i == missing_index else peak,
            None if i == missing_index else f"event-{i}",
            None if i == missing_index else f"input-{i}",
        )
        for i, peak in enumerate(peaks)
    )
    return build_frequency_curve(CurvePopulation(scope, allocations, tails), records)


def test_exact_20_percent_boundary_has_no_warning() -> None:
    curve = _curve((10.0, 20.0, 30.0, 40.0, 50.0))
    estimate = curve.estimate(0.99)
    assert estimate.peak_m3_s == 10.0
    warning = estimate.interval_contribution_warning
    assert warning is not None
    assert warning.status == "not_flagged"
    assert warning.maximum_stratum_id == "interval-0"
    assert warning.maximum_stratum_share == pytest.approx(0.2)
    assert warning.at_or_above_probability_mass == pytest.approx(1.0)
    assert warning.native_equivalence == "not_assessed"
    assert [row.contributing_samples for row in warning.strata] == [1] * 5
    assert [row.at_or_above_probability_mass for row in warning.strata] == pytest.approx([0.2] * 5)


def test_one_interval_over_20_percent_is_flagged_without_changing_strict_survival() -> None:
    curve = _curve((10.0, 20.0, 30.0, 40.0, 50.0))
    estimate = curve.estimate(0.4)
    assert estimate.peak_m3_s == 30.0
    assert curve.exceedance(30.0).known_exceedance_probability == pytest.approx(0.4)
    warning = estimate.interval_contribution_warning
    assert warning is not None
    assert warning.status == "flagged"
    assert warning.maximum_stratum_id == "interval-2"
    assert warning.maximum_stratum_share == pytest.approx(1 / 3)
    assert warning.at_or_above_probability_mass == pytest.approx(0.6)
    assert [row.contributing_samples for row in warning.strata] == [0, 0, 1, 1, 1]
    assert [row.at_or_above_probability_mass for row in warning.strata] == pytest.approx(
        [0, 0, 0.2, 0.2, 0.2]
    )


def test_zero_atom_and_two_physical_sites_remain_independent() -> None:
    upstream = _curve((10.0, 20.0, 30.0, 40.0, 50.0), site="upstream")
    downstream = _curve((0.0, 0.0, 0.0, 0.0, 0.0), site="downstream")
    up = upstream.estimate(0.4)
    down = downstream.estimate(0.4)
    assert up.interval_contribution_warning is not None
    assert up.interval_contribution_warning.status == "flagged"
    assert down.peak_m3_s == 0.0
    assert down.status == "zero_atom"
    assert downstream.exceedance(0).known_exceedance_probability == 0
    assert down.interval_contribution_warning is not None
    assert down.interval_contribution_warning.status == "not_flagged"
    assert down.interval_contribution_warning.maximum_stratum_share == pytest.approx(0.2)


def test_missing_event_or_tail_requires_unassessed_warning_and_no_point() -> None:
    for curve in (
        _curve((10.0, 20.0, 30.0, 40.0, 50.0), missing_index=0),
        _curve((10.0, 20.0, 30.0, 40.0, 50.0), tails=UnmodelledTails(0.1)),
    ):
        estimate = curve.estimate(0.4)
        assert estimate.status == "incomplete"
        assert estimate.peak_m3_s is None
        assert estimate.interval_contribution_warning is not None
        assert estimate.interval_contribution_warning.status == "not_assessed"


def test_aep_table_contains_row_number_one_in_y_and_provisional_asterisk() -> None:
    curve = _curve((10.0, 20.0, 30.0, 40.0, 50.0))
    targets = (0.99, 0.4)
    estimates = [
        {
            "status": item.status,
            "peak_m3_s": item.peak_m3_s,
            "interval_contribution_warning": {"status": item.interval_contribution_warning.status},
        }
        for item in (curve.estimate(0.99), curve.estimate(0.4))
        if item.interval_contribution_warning is not None
    ]
    lines, flagged = _format_selected_aep_table("print_01", targets, estimates)
    assert flagged
    assert "AEP(1inY)" in lines[1]
    assert "Peak print_01" in lines[1]
    assert "1.01" in lines[2]
    assert "10.00" in lines[2]
    assert "*" not in lines[2]
    assert "2.5" in lines[3]
    assert "30.00*" in lines[3]
    assert "RORBwin equivalence not established" in lines[0]


def test_incomplete_aep_table_says_na_without_a_star() -> None:
    curve = _curve((10.0, 20.0, 30.0, 40.0, 50.0), missing_index=0)
    result = curve.estimate(0.4)
    assert result.interval_contribution_warning is not None
    lines, flagged = _format_selected_aep_table(
        "print_01",
        (0.4,),
        [{"status": result.status, "peak_m3_s": result.peak_m3_s, "interval_contribution_warning": {"status": "not_assessed"}}],
    )
    assert not flagged
    assert "N/A" in lines[2]
    assert "*" not in lines[2]
    assert "incomplete probability support" in lines[3]
