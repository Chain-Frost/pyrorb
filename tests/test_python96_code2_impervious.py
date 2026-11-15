"""Independent default-engine source addition and impervious loss controls (#96).

These pure-Python S2 controls are not original RORB CMD / PyRomb parity results.
"""

from __future__ import annotations

import math

import pytest

from runoff_routing.reach_routing import RoutingDomainError
from runoff_routing.rorb_model import PatternBasis
from runoff_routing.single_storm import (
    Catchment,
    Control,
    Losses,
    Storm,
    calculate_storm,
    distance_analysis,
    rainfall_excess,
)

CONTROLS = (Control(1, 2.0), Control(2, 3.0), Control(7))
STORM = Storm(0.5, 12, (50.0, 50.0), (10.0, 10.0))


def test_default_code_two_adds_new_source_before_second_reach() -> None:
    model = Catchment(CONTROLS, (1.0, 2.0), (0.5, 0.2))
    mean, factors = distance_analysis(model)
    assert mean == pytest.approx(11.0 / 3.0)
    assert factors == pytest.approx((6.0 / 11.0, 9.0 / 11.0))

    result = calculate_storm(model, STORM, losses=Losses(2.0, 0.5), kc=3.0, m=1.0)
    assert len(result.outlets_m3_s) == 1
    assert len(result.outlets_m3_s[0]) == 13
    assert len(result.source_hydrographs_m3_s) == 2
    assert result.rainfall_excess_mm[0] == pytest.approx((3.875, 4.875))
    assert result.rainfall_excess_mm[1] == pytest.approx((3.2, 4.8))
    source_volume = math.fsum(math.fsum(q) for q in result.source_hydrographs_m3_s) * 1800
    assert source_volume == pytest.approx(24_750.0, abs=1e-7)
    assert all(q >= 0 and math.isfinite(q) for q in result.outlets_m3_s[0])

    without_fi = calculate_storm(Catchment(CONTROLS, (1.0, 2.0)), STORM, losses=Losses(2, 0.5), kc=3, m=1)
    assert result.rainfall_excess_mm != without_fi.rainfall_excess_mm
    assert result.outlets_m3_s != without_fi.outlets_m3_s


def test_default_code_two_preserves_multiple_prints_and_complete_times() -> None:
    controls = (Control(1, 2), Control(7), Control(2, 3), Control(7))
    result = calculate_storm(Catchment(controls, (1.0, 2.0), (0.5, 0.2)), STORM, losses=Losses(2, 0.5), kc=3, m=1)
    assert len(result.outlets_m3_s) == 2
    assert all(len(series) == 13 for series in result.outlets_m3_s)
    assert result.outlets_m3_s[0] != result.outlets_m3_s[1]


def test_default_fi_with_runoff_coefficient_does_not_reuse_continuing_loss() -> None:
    rain = (5.0, 5.0, 0.0)
    assert rainfall_excess(
        rain, losses=Losses(2.0, 0.0, 0.6), timestep_hours=0.5, impervious_fraction=0.5
    ) == pytest.approx((2.4, 3.0, 0.0))
    assert rainfall_excess(rain, losses=Losses(2.0, 0.5), timestep_hours=0.5, impervious_fraction=0.5) == pytest.approx(
        (3.875, 4.875, 0.0)
    )
    assert rainfall_excess(rain, losses=Losses(2.0, 0.5), timestep_hours=0.5, impervious_fraction=0.0) == pytest.approx(
        (2.75, 4.75, 0.0)
    )


def test_direct_subnormal_relative_weights_preserve_rainfall_and_full_q() -> None:
    model = Catchment(CONTROLS, (1.0, 2.0))
    normal = Storm(0.5, 12, (1.0, 1.0), (0.1, 0.1), PatternBasis.RELATIVE_WEIGHTS)
    subnormal = Storm(0.5, 12, (1e-323, 1e-323), (0.1, 0.1), PatternBasis.RELATIVE_WEIGHTS)
    reference = calculate_storm(model, normal, losses=Losses(0, 0), kc=3, m=1)
    calculated = calculate_storm(model, subnormal, losses=Losses(0, 0), kc=3, m=1)
    assert reference.rainfall_excess_mm[0] == pytest.approx((0.05, 0.05))
    assert calculated.rainfall_excess_mm == reference.rainfall_excess_mm
    assert calculated.outlets_m3_s == reference.outlets_m3_s


def test_direct_unrepresentable_relative_weight_ratio_is_explicitly_rejected() -> None:
    storm = Storm(0.5, 12, (1e-320, 1e308), (0.1, 0.1), PatternBasis.RELATIVE_WEIGHTS)
    with pytest.raises(RoutingDomainError, match="Relative storm weight ratios"):
        calculate_storm(Catchment(CONTROLS, (1.0, 2.0)), storm, losses=Losses(0, 0), kc=3, m=1)


def test_direct_independent_relative_weight_overflow_is_a_domain_rejection() -> None:
    storm = Storm(0.5, 12, (1e308, 1e308), (10.0, 10.0), PatternBasis.RELATIVE_WEIGHTS)
    with pytest.raises(RoutingDomainError, match="Temporal weights"):
        calculate_storm(Catchment(CONTROLS, (1.0, 2.0)), storm, losses=Losses(0, 0), kc=3, m=1)


@pytest.mark.parametrize("fractions", [(1.2, 0.0), (-0.01, 0.0), (math.nan, 0.0), (0.2,)])
def test_impervious_domain_rejected_before_source_preparation(fractions: tuple[float, ...]) -> None:
    model = Catchment(CONTROLS, (1.0, 2.0), fractions)
    with pytest.raises(RoutingDomainError, match=r"impervious|Impervious"):
        calculate_storm(model, STORM, losses=Losses(0, 0), kc=3, m=1)


def test_code_two_without_running_branch_is_rejected_not_implicitly_code_one() -> None:
    model = Catchment((Control(2, 1.0), Control(7)), (1.0,))
    with pytest.raises(RoutingDomainError, match="Code 2 requires"):
        calculate_storm(model, Storm(0.5, 4, (100.0,), (10.0,)), losses=Losses(0, 0), kc=3, m=1)


def test_adjacent_code_one_addition_and_code_three_cleared_branches() -> None:
    confluence = Catchment(
        (Control(1, 2), Control(3), Control(1, 4), Control(4), Control(7)),
        (1.0, 2.0),
    )
    assert distance_analysis(confluence)[0] == pytest.approx((1.0 * 2.0 + 2.0 * 4.0) / 3)
    result = calculate_storm(confluence, STORM, losses=Losses(0, 0), kc=3, m=1)
    assert len(result.outlets_m3_s[0]) == 13

    adjacent = Catchment((Control(1, 2), Control(1, 3), Control(7)), (1.0, 2.0))
    assert distance_analysis(adjacent)[0] == pytest.approx(11.0 / 3.0)
    added = calculate_storm(adjacent, STORM, losses=Losses(0, 0), kc=3, m=1)
    assert any(q > 0 for q in added.outlets_m3_s[0][1:])
