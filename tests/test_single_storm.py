"""Synthetic S2 event checks. Historical corpus remains in the private repo."""

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


def test_initial_loss_crossing_and_dry_bins() -> None:
    assert rainfall_excess((2.0, 2.0, 10.0, 0.0), losses=Losses(3.0, 2.0), timestep_hours=1) == (0.0, 0.0, 8.0, 0.0)


def test_runoff_coefficient_applies_after_initial_loss_and_not_as_continuing_rate() -> None:
    rain = (2.0, 1.0, 7.0, 0.0, 5.0)
    assert rainfall_excess(rain, losses=Losses(3.0, 0.0, 0.6), timestep_hours=0.5) == (0.0, 0.0, 4.2, 0.0, 3.0)
    assert rainfall_excess(rain, losses=Losses(3.0, 0.6), timestep_hours=0.5) != rainfall_excess(
        rain, losses=Losses(3.0, 0.0, 0.6), timestep_hours=0.5
    )
    assert rainfall_excess(rain, losses=Losses(3.0, 0.0, 0.0), timestep_hours=0.5) == (0.0,) * 5
    assert rainfall_excess(rain, losses=Losses(3.0, 0.0, 1.0), timestep_hours=0.5) == (0.0, 0.0, 7.0, 0.0, 5.0)


@pytest.mark.parametrize("coefficient", [-0.1, 1.01, math.inf, math.nan])
def test_runoff_coefficient_requires_dimensionless_fraction(coefficient: float) -> None:
    with pytest.raises(RoutingDomainError, match="runoff coefficient"):
        rainfall_excess((3.0, 4.0), losses=Losses(1.0, 0.0, coefficient), timestep_hours=1)


def test_no_loss_when_zero() -> None:
    assert rainfall_excess((1.0, 0.0, 3.0), losses=Losses(0, 0), timestep_hours=0.25) == (1, 0, 3)


def test_one_natural_reach_mass_and_horizon() -> None:
    model = Catchment((Control(1, 2), Control(7)), (10.0,))
    storm = Storm(1.0, 10, (50, 50), (10.0,))
    result = calculate_storm(model, storm, losses=Losses(0, 0), kc=0, m=0.8)
    assert result.average_distance_km == 2
    assert result.route_factors == (1,)
    assert result.rainfall_excess_mm == ((5.0, 5.0),)
    assert result.outlets_m3_s[0] == pytest.approx((0.0, 50 / 3.6, 50 / 3.6, *([0.0] * 8)))
    assert math.fsum(result.outlets_m3_s[0]) * 3600 == pytest.approx(100_000)


def test_branching_average_distance_and_confluence() -> None:
    model = Catchment((Control(1, 2), Control(3), Control(1, 4), Control(4), Control(5, 3), Control(7)), (1, 3))
    dav, factors = distance_analysis(model)
    assert dav == pytest.approx((1 * 5 + 3 * 7) / 4)
    assert factors == pytest.approx((2 / dav, 4 / dav, 3 / dav))
    storm = Storm(1.0, 4, (100.0,), (3.6, 3.6))
    out = calculate_storm(model, storm, losses=Losses(0, 0), kc=0.0, m=1.0)
    assert out.outlets_m3_s == ((0.0, 4.0, 0.0, 0.0, 0.0),)


def test_two_print_locations_with_same_final_outlet() -> None:
    model = Catchment((Control(1, 3), Control(7), Control(5, 1), Control(7)), (2,))
    result = calculate_storm(model, Storm(1.0, 3, (100,), (3.6,)), losses=Losses(0, 0), kc=0, m=1)
    assert len(result.outlets_m3_s) == 2
    assert result.average_distance_km == 4


@pytest.mark.parametrize(
    "model",
    [
        Catchment((Control(7),), (1,)),
        Catchment((Control(1, 1), Control(3), Control(7)), (1,)),
        Catchment((Control(1, 1), Control(4), Control(7)), (1,)),
        Catchment((Control(1, 0), Control(7)), (1,)),
        Catchment((Control(1, -1), Control(7)), (1,)),
        Catchment((Control(1, 2), Control(7)), (1, 2)),
        Catchment((Control(1, 2), Control(3), Control(1, 2), Control(4), Control(7)), (1,)),
    ],
)
def test_invalid_topology_fails_closed(model: Catchment) -> None:
    with pytest.raises(RoutingDomainError):
        calculate_storm(model, Storm(1, 3, (100,), (1,) * len(model.areas_km2)), losses=Losses(0, 0), kc=1, m=1)


def test_bad_horizon_or_depths_fail() -> None:
    model = Catchment((Control(1, 1), Control(7)), (1,))
    with pytest.raises(RoutingDomainError, match="horizon"):
        calculate_storm(model, Storm(1, 1, (50, 50), (1,)), losses=Losses(0, 0), kc=1, m=1)
    with pytest.raises(RoutingDomainError, match="depth"):
        calculate_storm(model, Storm(1, 2, (100,), ()), losses=Losses(0, 0), kc=1, m=1)


@pytest.mark.parametrize(
    ("losses", "expected"),
    [(Losses(25, 2), (0.0, 24.0, 69.0)), (Losses(25, 0, 0.5), (0.0, 12.5, 35.0))],
)
def test_combined_preburst_normalizes_total_depth_and_carries_loss(
    losses: Losses, expected: tuple[float, ...]
) -> None:
    model = Catchment((Control(1, 1), Control(7)), (1.0,))
    storm = Storm(0.5, 5, (20.0, 30.0, 70.0), (120.0,), PatternBasis.COMBINED_PREBURST_PERCENT, 1)
    result = calculate_storm(model, storm, losses=losses, kc=0, m=1)
    assert result.rainfall_excess_mm[0] == pytest.approx(expected)
    assert result.outlets_m3_s[0] == pytest.approx((0.0, *(value / 1.8 for value in expected), 0.0, 0.0))
    assert storm.percentages == (20.0, 30.0, 70.0)
    assert storm.preburst_bins == 1


@pytest.mark.parametrize(
    ("basis", "weights", "split"),
    [
        (PatternBasis.COMBINED_PREBURST_PERCENT, (20.0, 100.0), 0),
        (PatternBasis.COMBINED_PREBURST_PERCENT, (20.0, 100.0), 2),
        (PatternBasis.COMBINED_PREBURST_PERCENT, (20.0, 100.0), True),
        (PatternBasis.COMBINED_PREBURST_PERCENT, (0.0, 100.0), 1),
        (PatternBasis.COMBINED_PREBURST_PERCENT, (20.0, 90.0), 1),
        (PatternBasis.PERCENT_OF_DEPTH, (20.0, 80.0), 1),
        (PatternBasis.PERCENT_OF_DEPTH, (20.0, 100.0), 0),
        (PatternBasis.RELATIVE_WEIGHTS, (20.0, 100.0), 1),
    ],
)
def test_combined_preburst_does_not_admit_ambiguous_patterns(
    basis: PatternBasis, weights: tuple[float, ...], split: int
) -> None:
    model = Catchment((Control(1, 1), Control(7)), (1.0,))
    storm = Storm(0.5, 5, weights, (120.0,), basis, split)
    with pytest.raises(RoutingDomainError, match=r"pre-burst|Pre-burst|percentages must total"):
        calculate_storm(model, storm, losses=Losses(0, 0), kc=0, m=1)
