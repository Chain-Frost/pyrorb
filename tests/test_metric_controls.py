"""Execute the twelve original MET-NC specifications plus adversarial variants."""

from dataclasses import replace
from fractions import Fraction

import pytest

from runoff_routing.regression_metric_controls import (
    ConservationEvidence,
    SeriesIdentity,
    conservation_gate,
    exact_ties_gate,
    metric_scope_gate,
    printed_peak_gate,
    series_gate,
)
from runoff_routing.regression_metrics import ScalarField, SiteMetrics, compare_peak, compare_reported_volume


def identity() -> SeriesIdentity:
    return SeriesIdentity(("outlet", "internal"), ("1", "2", "3"), ("0.50", "1.00", "1.50"), ("1.000",), 3)


def scalar_binding() -> SiteMetrics:
    return SiteMetrics(
        "Hyd001",
        "authored outlet",
        ScalarField("1.000", 1, 1, 1, "m3/s"),
        ScalarField("0.50", 2, 1, 1, "h"),
        ScalarField("3.00", 3, 1, 1, "m3"),
    )


def evidence() -> ConservationEvidence:
    return ConservationEvidence(("external-a",), ("external-a",), True, True, True, None)


def test_met_nc_001_unique_peak() -> None:
    assert series_gate(identity(), identity()).verdict == "pass"
    result = compare_peak((0.0, 1.0, 0.0), Fraction(1, 2), scalar_binding())
    assert result.magnitude == result.time == "pass"
    assert printed_peak_gate(("0.000", "1.000", "0.000")).verdict == "pass"


def test_met_nc_002_printed_plateau_is_not_exact_native_tie() -> None:
    assert printed_peak_gate(("0.000", "1.000", "1.000")).verdict == "incomplete"
    values = (Fraction(0), Fraction(1), Fraction(1))
    assert exact_ties_gate(None, values).verdict == "incomplete"
    assert exact_ties_gate(values, values).verdict == "pass"
    assert exact_ties_gate(values, (Fraction(0), Fraction(1), Fraction(1, 2))).verdict == "fail"
    assert compare_peak((0.0, 1.0, 1.0), Fraction(1, 2), scalar_binding()).time == "incomplete"


def test_met_nc_003_near_tie_remains_ambiguous() -> None:
    assert printed_peak_gate(("0.000", "1.000", "0.999")).verdict == "incomplete"


def test_met_nc_004_zero_flow_time() -> None:
    assert compare_peak((0.0, 0.0, 0.0), Fraction(1, 2), scalar_binding()).time == "incomplete"


def test_met_nc_005_endpoints_distinguish_volume() -> None:
    assert compare_reported_volume((1.0, 0.0, 2.0), Fraction(1), scalar_binding()) == "pass"
    trapezoid = replace(scalar_binding(), volume=ScalarField("1.50", 3, 1, 1, "m3"))
    assert compare_reported_volume((1.0, 0.0, 2.0), Fraction(1), trapezoid) == "fail"


@pytest.mark.parametrize("field", ["initial_storage_observed", "terminal_storage_observed", "inlet_outlet_observed"])
def test_met_nc_006_missing_independent_state(field: str) -> None:
    actual = replace(evidence(), **{field: False})
    assert conservation_gate(actual).verdict == "incomplete"


def test_met_nc_007_shifted_clock() -> None:
    assert series_gate(identity(), replace(identity(), clocks=("0.00", "0.50", "1.00"))).verdict == "fail"


def test_met_nc_008_original_precision() -> None:
    assert series_gate(identity(), replace(identity(), scalar_tokens=("1.0",))).verdict == "fail"


@pytest.mark.parametrize(
    "sites", [("outlet",), ("outlet", "outlet"), ("internal", "outlet"), ("outlet", "internal", "extra")]
)
def test_met_nc_009_full_site_order(sites: tuple[str, ...]) -> None:
    assert series_gate(identity(), replace(identity(), sites=sites)).verdict == "fail"


def test_met_nc_010_full_horizon() -> None:
    assert series_gate(identity(), replace(identity(), increments=("1", "2"))).verdict == "incomplete"
    assert series_gate(identity(), replace(identity(), increments=("1", "3", "2"))).verdict == "fail"
    shortened = replace(identity(), samples=2, increments=("1", "2"), clocks=("0.50", "1.00"))
    assert series_gate(identity(), shortened).verdict == "incomplete"


def test_met_nc_011_source_double_counting() -> None:
    assert conservation_gate(replace(evidence(), counted_sources=("external-a", "external-a"))).verdict == "fail"


def test_met_nc_012_constant_storage_cannot_be_inferred_from_zero_q() -> None:
    # Authored CMD m=0 example: Q=0 does not imply S=0. Its missing native
    # boundary observation must block acceptance before inspecting any residual.
    storage = (Fraction(7), Fraction(7))
    discharge = (Fraction(0), Fraction(0))
    assert storage[0] == storage[-1] != discharge[-1]
    assert conservation_gate(replace(evidence(), terminal_storage_observed=False)).verdict == "incomplete"
    assert conservation_gate(evidence()).verdict == "incomplete"


def test_budget_eligibility_is_not_balance_acceptance() -> None:
    assert conservation_gate(replace(evidence(), budget_policy="authored-control-only")).verdict == "not_run"
    assert metric_scope_gate(supported=False, requested=True).verdict == "unsupported"
    assert metric_scope_gate(supported=True, requested=False).verdict == "not_run"
