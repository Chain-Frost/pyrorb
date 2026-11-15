"""Independent hand-calculated S7/C weighted-frequency controls; no native equivalence."""

from __future__ import annotations

from dataclasses import replace

import pytest

from runoff_routing.monte_carlo_frequency import (
    CurvePopulation,
    FrequencyInputError,
    FrequencyScope,
    PeakRecord,
    PeakStatus,
    StratumWeight,
    UnmodelledTails,
    build_frequency_curve,
    build_frequency_curves,
    duration_envelope,
)


def _scope(*, site: str = "site-A", duration: int = 60, scenario: str = "design") -> FrequencyScope:
    return FrequencyScope(f"plan-{duration}", "method-1", "v1", scenario, duration, site)


def _record(
    scope: FrequencyScope,
    stratum: str,
    sample: str,
    peak: float | None,
    *,
    status: PeakStatus = "valid",
    weight: float = 0.5,
) -> PeakRecord:
    return PeakRecord(
        scope,
        stratum,
        sample,
        weight,
        status,
        peak,
        f"event-{sample}" if status == "valid" else None,
        f"manifest-{sample}" if status == "valid" else None,
    )


def _four(*, scope: FrequencyScope | None = None) -> tuple[CurvePopulation, tuple[PeakRecord, ...]]:
    s = scope or _scope()
    # Manually enumerated: 0.25/2 = 0.125 for each h1 event;
    # 0.75/2 = 0.375 for each h2 event.
    p = CurvePopulation(s, (StratumWeight("h1", 0.25, 2), StratumWeight("h2", 0.75, 2)))
    return p, (
        _record(s, "h1", "a", 10, weight=0.125),
        _record(s, "h1", "b", 20, weight=0.125),
        _record(s, "h2", "c", 30, weight=0.375),
        _record(s, "h2", "d", 40, weight=0.375),
    )


def test_exact_unequal_weight_exceedance_and_midpoint_inversion() -> None:
    population, records = _four()
    curve = build_frequency_curve(population, records)
    assert curve.coverage.valid_mass == 1
    assert curve.coverage.complete
    assert curve.exceedance(20).lower_probability == pytest.approx(0.75)  # strict: 20 does not exceed 20
    assert curve.exceedance(30).upper_probability == pytest.approx(0.375)
    assert curve.exceedance(0).lower_probability == 1
    assert curve.exceedance(40).upper_probability == 0
    assert curve.groups[2].midpoint_cdf == pytest.approx(0.4375)
    assert curve.groups[3].midpoint_cdf == pytest.approx(0.8125)
    q = curve.estimate(0.5)
    assert q.status == "estimated"
    # At nonexceedance 0.5: 30 + 10*(0.5-0.4375)/(0.8125-0.4375).
    assert q.peak_m3_s == pytest.approx(31 + 2 / 3)
    assert q.representative is not None
    assert q.representative.sample_id == "c"
    assert q.representative.event_id == "event-c"
    assert q.representative.effective_input_id == "manifest-c"
    assert q.representative.signed_mismatch_m3_s == pytest.approx(-5 / 3)
    assert q.native_equivalence == "not_assessed"
    assert q.statistical_qualification == "not_assessed"


def test_affine_monotone_transform_preserves_analytical_quantiles() -> None:
    population, records = _four()
    basic = build_frequency_curve(population, records)
    transformed = tuple(replace(item, peak_m3_s=float(item.peak_m3_s or 0) * 2 + 3) for item in records)
    scaled = build_frequency_curve(population, transformed)
    for aep in (0.2, 0.3, 0.5, 0.8):
        q1 = basic.estimate(aep)
        q2 = scaled.estimate(aep)
        assert q1.status == q2.status
        if q1.peak_m3_s is not None:
            assert q2.peak_m3_s == pytest.approx(q1.peak_m3_s * 2 + 3)


def test_zero_flow_atom_ties_and_representative_ties() -> None:
    s = _scope()
    p = CurvePopulation(s, (StratumWeight("dry", 0.4, 2), StratumWeight("wet", 0.6, 2)))
    rows = (
        _record(s, "dry", "zero-b", 0, weight=0.2),
        _record(s, "wet", "wet-b", 20, weight=0.3),
        _record(s, "wet", "wet-a", 20, weight=0.3),
        _record(s, "dry", "zero-a", 0, weight=0.2),
    )
    curve = build_frequency_curve(p, rows)
    assert curve.coverage.zero_mass == pytest.approx(0.4)
    assert curve.exceedance(0).lower_probability == pytest.approx(0.6)
    assert curve.exceedance(20).lower_probability == 0
    assert curve.estimate(0.65).status == "zero_atom"  # 1-AEP = 0.35 < 0.4
    zero = curve.estimate(0.65)
    assert zero.peak_m3_s == 0
    assert zero.representative is not None
    assert zero.representative.sample_id == "zero-a"  # independent of input order
    middle = curve.estimate(0.45)  # 1-AEP = 0.55; between (0.4,0) and (0.7,20)
    assert middle.peak_m3_s == pytest.approx(10)
    assert middle.representative is not None
    assert middle.representative.sample_id == "wet-a"  # 0 and 20 equally near 10, stable lexical ID
    assert build_frequency_curve(p, reversed(rows)).estimate(0.45) == middle


def test_no_extrapolation_at_sparse_probability_boundaries() -> None:
    population, rows = _four()
    curve = build_frequency_curve(population, rows)
    assert curve.estimate(0.01).status == "boundary_limited"  # target above top midpoint 0.8125
    assert curve.estimate(0.99).status == "boundary_limited"  # target below bottom midpoint 0.0625
    assert curve.estimate(0.1875).peak_m3_s == 40  # exactly on highest midpoint
    assert curve.estimate(0.9375).peak_m3_s == 10  # exactly on lowest midpoint
    assert curve.estimate(0.1875).boundary_influenced
    with pytest.raises(FrequencyInputError, match="strictly inside"):
        curve.estimate(0)
    with pytest.raises(FrequencyInputError, match="strictly inside"):
        curve.estimate(1)


def test_failed_missing_and_unmodelled_tails_remain_in_denominators() -> None:
    s = _scope()
    p = CurvePopulation(
        s,
        (StratumWeight("first", 0.4, 2), StratumWeight("second", 0.4, 2)),
        UnmodelledTails(upper_rainfall_mass=0.2),
    )
    rows = (
        _record(s, "first", "valid0", 0, weight=0.2),
        _record(s, "first", "failed", None, status="failed", weight=0.2),
        _record(s, "second", "valid20", 20, weight=0.2),
        # second planned draw is absent; it retains weight 0.2.
    )
    curve = build_frequency_curve(p, rows)
    coverage = curve.coverage
    assert coverage.valid_mass == pytest.approx(0.4)
    assert coverage.zero_mass == pytest.approx(0.2)
    assert coverage.failed_mass == pytest.approx(0.2)
    assert coverage.missing_mass == pytest.approx(0.2)
    assert coverage.tails.total == pytest.approx(0.2)
    assert coverage.unresolved_mass == pytest.approx(0.6)
    assert curve.accounting[1].absent_samples == 1
    assert curve.estimate(0.1).status == "incomplete"
    assert curve.estimate(0.1).peak_m3_s is None
    # Target F=0.9. Putting unknown 0.6 all at +inf gives no finite upper bound;
    # placing it all at zero moves F=0.9 into known observed Q=20.
    bound = curve.estimate(0.1)
    assert bound.lower_bound_m3_s == 20
    assert bound.upper_bound_m3_s is None
    bracket = curve.exceedance(0)
    assert bracket.lower_probability == pytest.approx(0.2)
    assert bracket.upper_probability == pytest.approx(0.8)


def test_unallocated_stratum_and_zero_weight_failures() -> None:
    s = _scope()
    p = CurvePopulation(
        s,
        (StratumWeight("allocated", 0.8, 1), StratumWeight("unallocated", 0.2, 0)),
    )
    curve = build_frequency_curve(p, (_record(s, "allocated", "live", 5, weight=0.8),))
    assert curve.coverage.unallocated_stratum_mass == pytest.approx(0.2)
    assert curve.coverage.missing_mass == 0
    assert curve.estimate(0.5).status == "incomplete"
    assert curve.exceedance(5).upper_probability == pytest.approx(0.2)

    zero_mass_population = CurvePopulation(
        s,
        (StratumWeight("allocated", 1, 1), StratumWeight("unused", 0, 1)),
    )
    with_zero_weight_failure = build_frequency_curve(
        zero_mass_population,
        (_record(s, "allocated", "live", 5, weight=1), _record(s, "unused", "fail", None, status="failed", weight=0)),
    )
    assert with_zero_weight_failure.coverage.complete
    assert with_zero_weight_failure.accounting[1].failed_samples == 1
    assert with_zero_weight_failure.estimate(0.5).peak_m3_s == 5


def test_incomplete_quantile_bounds_with_known_zero_and_positive_peaks() -> None:
    s = _scope()
    p = CurvePopulation(s, (StratumWeight("interior", 0.8, 2),), UnmodelledTails(0.2, 0))
    curve = build_frequency_curve(
        p,
        (
            _record(s, "interior", "dry", 0, weight=0.4),
            _record(s, "interior", "wet", 20, weight=0.4),
        ),
    )
    # F=0.1: all missing mass at zero OR at infinity still places target in zero atom.
    q = curve.estimate(0.9)
    assert q.status == "incomplete"
    assert q.lower_bound_m3_s == 0
    assert q.upper_bound_m3_s == 0
    assert q.representative is None
    # F=0.9: upper cannot be inferred because known mass only 0.8.
    q = curve.estimate(0.1)
    assert q.lower_bound_m3_s == 20
    assert q.upper_bound_m3_s is None


def test_incomplete_explicit_statuses_do_not_become_valid_zero() -> None:
    s = _scope()
    p = CurvePopulation(s, (StratumWeight("h", 1, 4),))
    rows = (
        _record(s, "h", "zero", 0, weight=0.25),
        _record(s, "h", "error", None, status="failed", weight=0.25),
        _record(s, "h", "unrun", None, status="missing", weight=0.25),
        _record(s, "h", "unsupported", None, status="unsupported", weight=0.25),
    )
    curve = build_frequency_curve(p, rows)
    assert curve.coverage.valid_mass == 0.25
    assert curve.coverage.failed_mass == 0.25
    assert curve.coverage.missing_mass == 0.25
    assert curve.coverage.unsupported_mass == 0.25
    assert curve.estimate(0.5).status == "incomplete"


def test_input_order_permutations_and_identity_validation() -> None:
    p, rows = _four()
    original = build_frequency_curve(p, rows)
    for ordering in (rows[::-1], (rows[2], rows[0], rows[3], rows[1])):
        current = build_frequency_curve(p, ordering)
        assert current.coverage == original.coverage
        assert current.groups == original.groups
        assert current.estimate(0.5) == original.estimate(0.5)
    with pytest.raises(FrequencyInputError, match="Duplicate sample"):
        build_frequency_curve(p, (*rows, rows[0]))
    with pytest.raises(FrequencyInputError, match="Duplicate event"):
        build_frequency_curve(p, (*rows[:3], replace(rows[3], event_id="event-a")))
    with pytest.raises(FrequencyInputError, match="Mismatched plan"):
        build_frequency_curve(p, (replace(rows[0], scope=replace(p.scope, plan_id="plan-new")),))
    with pytest.raises(FrequencyInputError, match="Mismatched plan"):
        build_frequency_curve(p, (replace(rows[0], scope=replace(p.scope, policy_id="method-new")),))
    with pytest.raises(FrequencyInputError, match="Stale or mixed"):
        build_frequency_curve(p, (replace(rows[0], event_probability_weight=0.25),))
    with pytest.raises(FrequencyInputError, match="More observed samples"):
        build_frequency_curve(p, (*rows, _record(p.scope, "h1", "extra", 50, weight=0.125)))
    with pytest.raises(FrequencyInputError, match="Duplicate stratum"):
        CurvePopulation(p.scope, (StratumWeight("h", 1, 2), StratumWeight("h", 0, 1)))
    with pytest.raises(FrequencyInputError, match="sum to one"):
        CurvePopulation(p.scope, (StratumWeight("h", 0.8, 2),))


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -1, True])
def test_bad_flow_rejected(value: float) -> None:
    with pytest.raises(FrequencyInputError, match="finite nonnegative"):
        _record(_scope(), "h", "s", value)


def test_missing_replay_identity_or_invalid_success_status_rejected() -> None:
    s = _scope()
    with pytest.raises(FrequencyInputError, match="replayable"):
        PeakRecord(s, "h", "s", 0.5, "valid", 5)
    with pytest.raises(FrequencyInputError, match="must not carry"):
        PeakRecord(s, "h", "s", 0.5, "failed", 5)
    with pytest.raises(FrequencyInputError, match="Unrecognised"):
        _record(s, "h", "s", None, status="computed_unvalidated")


def test_multiple_physical_sites_and_durations_do_not_pool() -> None:
    s_a = _scope(site="downstream", duration=60)
    s_b = _scope(site="upstream", duration=60)
    s_c = _scope(site="downstream", duration=120)
    pops = tuple(CurvePopulation(s, (StratumWeight("h", 1, 2),)) for s in (s_a, s_b, s_c))
    records = tuple(
        _record(s, "h", f"{s.duration_minutes}-{s.output_site_id}-{number}", peak)
        for s, peaks in ((s_a, (10, 20)), (s_b, (1, 2)), (s_c, (20, 30)))
        for number, peak in enumerate(peaks)
    )
    curves = build_frequency_curves(pops, reversed(records))
    assert len(curves) == 3
    by_scope = {curve.scope: curve for curve in curves}
    assert by_scope[s_b].estimate(0.5).peak_m3_s == pytest.approx(1.5)
    assert by_scope[s_a].estimate(0.5).peak_m3_s == pytest.approx(15)
    assert by_scope[s_c].estimate(0.5).peak_m3_s == pytest.approx(25)
    envelope = duration_envelope((by_scope[s_a], by_scope[s_c]), 0.5)
    assert envelope.peak_m3_s == pytest.approx(25)
    assert envelope.critical_duration_minutes == 120
    assert envelope.margin_to_second_m3_s == pytest.approx(10)
    assert envelope.representative is not None
    assert envelope.representative.event_id.startswith("event-120-downstream")
    with pytest.raises(FrequencyInputError, match="scenarios, policies or sites"):
        duration_envelope((by_scope[s_a], by_scope[s_b]), 0.5)
    with pytest.raises(FrequencyInputError, match="Duplicate duration"):
        duration_envelope((by_scope[s_a], by_scope[s_a]), 0.5)


def test_exact_tie_chooses_shortest_duration_and_near_tie_stays_numeric() -> None:
    def _curve(d: int, upper: float) -> tuple[CurvePopulation, tuple[PeakRecord, ...]]:
        s = _scope(duration=d)
        return CurvePopulation(s, (StratumWeight("h", 1, 2),)), (
            _record(s, "h", f"{d}-a", 10),
            _record(s, "h", f"{d}-b", upper),
        )

    p60, r60 = _curve(60, 30)
    p120, r120 = _curve(120, 30)
    p180, r180 = _curve(180, 30.00000002)
    tied = duration_envelope((build_frequency_curve(p120, r120), build_frequency_curve(p60, r60)), 0.5)
    assert tied.critical_duration_minutes == 60
    assert tied.tied_critical_durations_minutes == (60, 120)
    assert tied.margin_to_second_m3_s == 0
    near = duration_envelope((build_frequency_curve(p60, r60), build_frequency_curve(p180, r180)), 0.5)
    assert near.critical_duration_minutes == 180
    assert near.margin_to_second_m3_s == pytest.approx(1e-8)


def test_unqualified_duration_blocks_envelope_and_preserves_bounds() -> None:
    s1, s2 = _scope(duration=60), _scope(duration=120)
    p1 = CurvePopulation(s1, (StratumWeight("h", 1, 2),))
    p2 = CurvePopulation(s2, (StratumWeight("h", 1, 2),))
    good = build_frequency_curve(p1, (_record(s1, "h", "a", 10), _record(s1, "h", "b", 30)))
    bad = build_frequency_curve(p2, (_record(s2, "h", "a", 20),))  # absent 1/2
    env = duration_envelope((good, bad), 0.5)
    assert env.status == "incomplete"
    assert env.peak_m3_s is None
    assert env.representative is None
    assert env.critical_duration_minutes is None
    assert env.upper_bound_m3_s == 20  # finite bound from known observed mass
