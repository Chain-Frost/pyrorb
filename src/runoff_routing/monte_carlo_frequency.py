"""Pure weighted Monte Carlo peak-frequency analysis (issue #147).

Consumes explicit completed/failed samples and their *planned* stratum mass.
No random draws, routing, source-file I/O, hydrograph invention or native claim.
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal, Never

PeakStatus = Literal["valid", "failed", "missing", "unsupported"]
QuantileStatus = Literal["estimated", "zero_atom", "incomplete", "boundary_limited"]
METHOD_PROFILE = "stratified-weighted-midpoint-v1"
_MASS_ROUNDOFF = 1e-12  # Input binary floating-point summation tolerance, never an engineering error band.


class FrequencyInputError(ValueError):
    """Inconsistent plan, probability allocation or peak-result ledger."""


def _fail(message: str) -> Never:
    raise FrequencyInputError(message)


def _identifier(value: str, label: str) -> None:
    if not isinstance(value, str) or not value or value != value.strip() or any(ord(c) < 32 for c in value):
        _fail(f"{label} must be nonempty, trimmed text without controls")


def _probability(value: float, label: str) -> None:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or not 0 <= value <= 1
    ):
        _fail(f"{label} must be a finite probability in [0, 1]")


@dataclass(frozen=True, slots=True)
class FrequencyScope:
    """One immutable sample plan, scenario, storm duration and physical site."""

    plan_id: str
    policy_id: str
    policy_version: str
    scenario_id: str
    duration_minutes: int
    output_site_id: str

    def __post_init__(self) -> None:
        _identifier(self.plan_id, "plan_id")
        _identifier(self.policy_id, "policy_id")
        _identifier(self.policy_version, "policy_version")
        _identifier(self.scenario_id, "scenario_id")
        _identifier(self.output_site_id, "output_site_id")
        if type(self.duration_minutes) is not int or self.duration_minutes <= 0:
            _fail("duration_minutes must be a positive integer")


@dataclass(frozen=True, slots=True)
class StratumWeight:
    """Original conditional-draw allocation, not a reweighted retained-result count."""

    stratum_id: str
    probability_mass: float
    planned_samples: int

    def __post_init__(self) -> None:
        _identifier(self.stratum_id, "stratum_id")
        _probability(self.probability_mass, "stratum probability mass")
        if type(self.planned_samples) is not int or self.planned_samples < 0:
            _fail("planned_samples must be a nonnegative integer")


@dataclass(frozen=True, slots=True)
class UnmodelledTails:
    """Explicit residual rainfall-domain mass; no extrapolated flow assumptions."""

    lower_rainfall_mass: float = 0.0
    upper_rainfall_mass: float = 0.0
    other_mass: float = 0.0

    def __post_init__(self) -> None:
        _probability(self.lower_rainfall_mass, "lower rainfall tail")
        _probability(self.upper_rainfall_mass, "upper rainfall tail")
        _probability(self.other_mass, "other unmodelled mass")

    @property
    def total(self) -> float:
        return math.fsum((self.lower_rainfall_mass, self.upper_rainfall_mass, self.other_mass))


@dataclass(frozen=True, slots=True)
class CurvePopulation:
    """Read-only aggregate view of B's *full* persisted plan, not a second plan schema."""

    scope: FrequencyScope
    strata: tuple[StratumWeight, ...]
    tails: UnmodelledTails = UnmodelledTails()

    def __post_init__(self) -> None:
        if not self.strata:
            _fail("A frequency population needs its complete strata allocation")
        names = [entry.stratum_id for entry in self.strata]
        if len(names) != len(set(names)):
            _fail("Duplicate stratum identifiers")
        mass = math.fsum((*[item.probability_mass for item in self.strata], self.tails.total))
        if not math.isclose(mass, 1.0, rel_tol=0.0, abs_tol=_MASS_ROUNDOFF):
            _fail("Strata and explicitly declared unmodelled tails must sum to one")


@dataclass(frozen=True, slots=True)
class PeakRecord:
    """One sample/site ledger row; E maps the original engine status explicitly.

    For a valid row, event_id and effective_input_id identify an actual replayable
    simulation, not an interpolated or averaged hydrograph. Engine acceptance
    is intentionally NOT implied by `valid`.
    """

    scope: FrequencyScope
    stratum_id: str
    sample_id: str
    event_probability_weight: float
    status: PeakStatus
    peak_m3_s: float | None = None
    event_id: str | None = None
    effective_input_id: str | None = None

    def __post_init__(self) -> None:
        _identifier(self.stratum_id, "stratum_id")
        _identifier(self.sample_id, "sample_id")
        _probability(self.event_probability_weight, "event probability weight")
        if self.status not in ("valid", "failed", "missing", "unsupported"):
            _fail("Unrecognised peak-result status")
        if self.event_id is not None:
            _identifier(self.event_id, "event_id")
        if self.effective_input_id is not None:
            _identifier(self.effective_input_id, "effective_input_id")
        if self.status == "valid":
            if (
                self.event_id is None
                or self.effective_input_id is None
                or self.peak_m3_s is None
                or isinstance(self.peak_m3_s, bool)
                or not isinstance(self.peak_m3_s, (int, float))
                or not math.isfinite(self.peak_m3_s)
                or self.peak_m3_s < 0
            ):
                _fail("Valid peaks require finite nonnegative flow and replayable event/input IDs")
        elif self.peak_m3_s is not None:
            _fail("Failed/missing/unsupported rows must not carry an accepted peak")


@dataclass(frozen=True, slots=True)
class StratumAccounting:
    stratum_id: str
    probability_mass: float
    planned_samples: int
    observed_samples: int
    valid_zero_samples: int
    valid_positive_samples: int
    failed_samples: int
    explicit_missing_samples: int
    absent_samples: int
    unsupported_samples: int
    sample_probability_weight: float | None


@dataclass(frozen=True, slots=True)
class ProbabilityCoverage:
    """Absolute probability masses, not conditional on successful computations."""

    valid_mass: float
    zero_mass: float
    positive_mass: float
    failed_mass: float
    missing_mass: float
    unsupported_mass: float
    unallocated_stratum_mass: float
    tails: UnmodelledTails

    @property
    def unresolved_mass(self) -> float:
        return math.fsum(
            (
                self.failed_mass,
                self.missing_mass,
                self.unsupported_mass,
                self.unallocated_stratum_mass,
                self.tails.total,
            )
        )

    @property
    def complete(self) -> bool:
        return self.unresolved_mass == 0.0


@dataclass(frozen=True, slots=True)
class WeightedPeak:
    record: PeakRecord
    weight: float


@dataclass(frozen=True, slots=True)
class PeakGroup:
    """Exact numeric peak ties are one weighted plotting-position knot."""

    peak_m3_s: float
    probability_mass: float
    cumulative_mass: float
    midpoint_cdf: float


@dataclass(frozen=True, slots=True)
class ExceedanceBounds:
    threshold_m3_s: float
    known_exceedance_probability: float
    lower_probability: float
    upper_probability: float
    unresolved_probability_mass: float


@dataclass(frozen=True, slots=True)
class RepresentativeEvent:
    sample_id: str
    event_id: str
    effective_input_id: str
    stratum_id: str
    realised_peak_m3_s: float
    target_peak_m3_s: float
    signed_mismatch_m3_s: float
    absolute_mismatch_m3_s: float


@dataclass(frozen=True, slots=True)
class QuantileEstimate:
    aep: float
    status: QuantileStatus
    peak_m3_s: float | None
    lower_bound_m3_s: float | None
    upper_bound_m3_s: float | None
    representative: RepresentativeEvent | None
    interpolation_peaks_m3_s: tuple[float, float] | None
    boundary_influenced: bool
    nearest_plotting_boundary_distance: float | None
    method: str = METHOD_PROFILE
    software_qualification: Literal["provisional"] = "provisional"
    statistical_qualification: Literal["not_assessed"] = "not_assessed"
    native_equivalence: Literal["not_assessed"] = "not_assessed"


@dataclass(frozen=True, slots=True)
class FrequencyCurve:
    scope: FrequencyScope
    accounting: tuple[StratumAccounting, ...]
    coverage: ProbabilityCoverage
    groups: tuple[PeakGroup, ...]
    positive_weight_observations: tuple[WeightedPeak, ...]
    method: str = METHOD_PROFILE

    def exceedance(self, threshold_m3_s: float) -> ExceedanceBounds:
        """Strict P(Q > q); unknown outcomes only widen the absolute bounds."""
        if (
            isinstance(threshold_m3_s, bool)
            or not isinstance(threshold_m3_s, (int, float))
            or not math.isfinite(threshold_m3_s)
        ):
            _fail("Exceedance threshold must be finite")
        if threshold_m3_s < 0:
            return ExceedanceBounds(threshold_m3_s, self.coverage.valid_mass, 1.0, 1.0, 0.0)
        known = math.fsum(
            item.weight
            for item in self.positive_weight_observations
            if item.record.peak_m3_s is not None and item.record.peak_m3_s > threshold_m3_s
        )
        return ExceedanceBounds(
            threshold_m3_s,
            known,
            known,
            min(1.0, math.fsum((known, self.coverage.unresolved_mass))),
            self.coverage.unresolved_mass,
        )

    def estimate(self, aep: float) -> QuantileEstimate:
        """Invert weighted midpoint knots, with an exact zero-flow point mass.

        This is a stated smooth empirical estimator, NOT the inverse of the
        step-valued strict exceedance function. Incomplete curves instead have
        conservative nonnegative-support *empirical* quantile bounds; these are
        neither confidence intervals nor guarantees about unsampled populations.
        """
        _probability(aep, "AEP")
        if not 0 < aep < 1:
            _fail("AEP must be strictly inside (0, 1); no endpoint extrapolation")
        nonexceedance = 1.0 - aep
        if not self.coverage.complete:
            lower, upper = _incomplete_bounds(self.groups, nonexceedance, self.coverage.unresolved_mass)
            return QuantileEstimate(aep, "incomplete", None, lower, upper, None, None, False, None)
        if not self.groups:
            _fail("Complete populations must contain positive-weight observed peaks")
        if len(self.groups) == 1:
            peak = self.groups[0].peak_m3_s
            status: QuantileStatus = "zero_atom" if peak == 0 else "estimated"
            return self._result(aep, peak, status, (peak, peak), False, None)
        if self.coverage.zero_mass > 0 and nonexceedance <= self.coverage.zero_mass:
            return self._result(aep, 0.0, "zero_atom", (0.0, 0.0), False, None)

        anchors = _plotting_anchors(self.groups)
        first_p, _ = anchors[0]
        last_p, _ = anchors[-1]
        if nonexceedance < first_p or nonexceedance > last_p:
            return QuantileEstimate(aep, "boundary_limited", None, None, None, None, None, True, 0.0)
        distance = min(nonexceedance - first_p, last_p - nonexceedance)
        for index, (position, peak) in enumerate(anchors):
            if nonexceedance == position:
                boundary = index in (0, len(anchors) - 1)
                return self._result(aep, peak, "estimated", (peak, peak), boundary, distance)
            if nonexceedance < position:
                left_p, left_q = anchors[index - 1]
                fraction = (nonexceedance - left_p) / (position - left_p)
                result = left_q + fraction * (peak - left_q)
                boundary = index == 1 or index == len(anchors) - 1
                return self._result(aep, result, "estimated", (left_q, peak), boundary, distance)
        _fail("Internal frequency plotting-position inconsistency")

    def _result(
        self,
        aep: float,
        peak: float,
        status: QuantileStatus,
        bracket: tuple[float, float],
        boundary: bool,
        distance: float | None,
    ) -> QuantileEstimate:
        selected = min(
            self.positive_weight_observations,
            key=lambda item: (
                abs(float(item.record.peak_m3_s or 0) - peak),
                item.record.sample_id,
                item.record.event_id or "",
            ),
        ).record
        actual = float(selected.peak_m3_s or 0)
        representative = RepresentativeEvent(
            selected.sample_id,
            selected.event_id or "",
            selected.effective_input_id or "",
            selected.stratum_id,
            actual,
            peak,
            actual - peak,
            abs(actual - peak),
        )
        return QuantileEstimate(aep, status, peak, None, None, representative, bracket, boundary, distance)


def _plotting_anchors(groups: tuple[PeakGroup, ...]) -> tuple[tuple[float, float], ...]:
    anchors: list[tuple[float, float]] = []
    if groups[0].peak_m3_s == 0:
        anchors.append((groups[0].cumulative_mass, 0.0))
    anchors.extend((group.midpoint_cdf, group.peak_m3_s) for group in groups if group.peak_m3_s > 0)
    return tuple(anchors)


def _inverse_step(groups: tuple[PeakGroup, ...], probability: float) -> float | None:
    if probability <= 0:
        return 0.0
    for group in groups:
        if group.cumulative_mass >= probability:
            return group.peak_m3_s
    return None


def _incomplete_bounds(
    groups: tuple[PeakGroup, ...], nonexceedance: float, unresolved: float
) -> tuple[float | None, float | None]:
    """All unknown nonnegative peaks at zero versus all at +infinity."""
    lower = 0.0 if nonexceedance <= unresolved else _inverse_step(groups, nonexceedance - unresolved)
    upper = _inverse_step(groups, nonexceedance)
    return lower, upper


def _planned_records(population: CurvePopulation, records: Iterable[PeakRecord]) -> dict[str, list[PeakRecord]]:
    """Validate the complete current plan revision before calculating weights."""
    strata = {entry.stratum_id: entry for entry in population.strata}
    by_stratum: dict[str, list[PeakRecord]] = defaultdict(list)
    seen_samples: set[str] = set()
    seen_events: set[str] = set()
    for record in records:
        if record.scope != population.scope:
            _fail("Mismatched plan, policy, scenario, duration or physical output-site identity")
        if record.stratum_id not in strata:
            _fail("Peak refers to a stratum outside the immutable plan")
        if record.sample_id in seen_samples:
            _fail("Duplicate sample identifier in the same curve")
        seen_samples.add(record.sample_id)
        if record.event_id is not None:
            if record.event_id in seen_events:
                _fail("Duplicate event identifier in the same curve")
            seen_events.add(record.event_id)
        entry = strata[record.stratum_id]
        expected = entry.probability_mass / entry.planned_samples if entry.planned_samples else None
        if expected is None or not math.isclose(record.event_probability_weight, expected, rel_tol=1e-12, abs_tol=0.0):
            _fail("Stale or mixed plan-revision event weights; reaggregate using the complete current plan")
        by_stratum[record.stratum_id].append(record)
    return by_stratum


def _account_observations(
    population: CurvePopulation, by_stratum: dict[str, list[PeakRecord]]
) -> tuple[tuple[StratumAccounting, ...], list[WeightedPeak], ProbabilityCoverage]:
    """Retain planned denominators, zero outcomes and every unresolved mass."""
    accounting: list[StratumAccounting] = []
    weighted: list[WeightedPeak] = []
    failed: list[float] = []
    missing: list[float] = []
    unsupported: list[float] = []
    unallocated: list[float] = []
    for stratum in population.strata:
        entries = by_stratum[stratum.stratum_id]
        n = stratum.planned_samples
        if len(entries) > n:
            _fail("More observed samples than the planned stratum allocation")
        unit = stratum.probability_mass / n if n else None
        if unit is None:
            unallocated.append(stratum.probability_mass)
        counts = {
            status: sum(item.status == status for item in entries)
            for status in ("valid", "failed", "missing", "unsupported")
        }
        absent = n - len(entries)
        valid = tuple(item for item in entries if item.status == "valid")
        valid_zeros = sum(item.peak_m3_s == 0 for item in valid)
        valid_positive = len(valid) - valid_zeros
        if unit is not None:
            weighted.extend(WeightedPeak(item, unit) for item in valid if unit > 0)
            failed.append(counts["failed"] * unit)
            missing.append((counts["missing"] + absent) * unit)
            unsupported.append(counts["unsupported"] * unit)
        accounting.append(
            StratumAccounting(
                stratum.stratum_id,
                stratum.probability_mass,
                n,
                len(entries),
                valid_zeros,
                valid_positive,
                counts["failed"],
                counts["missing"],
                absent,
                counts["unsupported"],
                unit,
            )
        )
    zero_mass = math.fsum(item.weight for item in weighted if item.record.peak_m3_s == 0)
    coverage = ProbabilityCoverage(
        math.fsum(item.weight for item in weighted),
        zero_mass,
        math.fsum(item.weight for item in weighted if item.record.peak_m3_s != 0),
        math.fsum(failed),
        math.fsum(missing),
        math.fsum(unsupported),
        math.fsum(unallocated),
        population.tails,
    )
    return tuple(accounting), weighted, coverage


def _group_peaks(weighted: list[WeightedPeak]) -> tuple[PeakGroup, ...]:
    """Merge exact numeric ties while retaining the original individual samples."""
    weighted.sort(key=lambda item: (float(item.record.peak_m3_s or 0), item.record.sample_id))
    groups: list[PeakGroup] = []
    total = 0.0
    position = 0
    while position < len(weighted):
        peak = float(weighted[position].record.peak_m3_s or 0)
        end = position + 1
        while end < len(weighted) and weighted[end].record.peak_m3_s == peak:
            end += 1
        mass = math.fsum(item.weight for item in weighted[position:end])
        new_total = math.fsum((total, mass))
        groups.append(PeakGroup(peak, mass, new_total, math.fsum((total, mass / 2))))
        total = new_total
        position = end
    return tuple(groups)


def build_frequency_curve(population: CurvePopulation, records: Iterable[PeakRecord]) -> FrequencyCurve:
    """Aggregate exactly the planned samples for ONE scope, ignoring input ordering."""
    by_stratum = _planned_records(population, records)
    accounting, weighted, coverage = _account_observations(population, by_stratum)
    return FrequencyCurve(population.scope, accounting, coverage, _group_peaks(weighted), tuple(weighted))


def build_frequency_curves(
    populations: Iterable[CurvePopulation], records: Iterable[PeakRecord]
) -> tuple[FrequencyCurve, ...]:
    """Build site/duration/scenario curves first; never pool these populations."""
    by_scope: dict[FrequencyScope, CurvePopulation] = {}
    for population in populations:
        if population.scope in by_scope:
            _fail("Duplicate curve population scope")
        by_scope[population.scope] = population
    ledger: dict[FrequencyScope, list[PeakRecord]] = defaultdict(list)
    for record in records:
        if record.scope not in by_scope:
            _fail("A peak ledger row has no matching planned population")
        ledger[record.scope].append(record)
    return tuple(
        build_frequency_curve(population, ledger[scope])
        for scope, population in sorted(
            by_scope.items(),
            key=lambda entry: (
                entry[0].scenario_id,
                entry[0].output_site_id,
                entry[0].duration_minutes,
                entry[0].plan_id,
            ),
        )
    )


@dataclass(frozen=True, slots=True)
class DurationEnvelope:
    scenario_id: str
    policy_id: str
    policy_version: str
    output_site_id: str
    aep: float
    status: QuantileStatus
    peak_m3_s: float | None
    critical_duration_minutes: int | None
    representative: RepresentativeEvent | None
    lower_bound_m3_s: float | None
    upper_bound_m3_s: float | None
    margin_to_second_m3_s: float | None
    tied_critical_durations_minutes: tuple[int, ...]
    duration_estimates: tuple[tuple[int, QuantileEstimate], ...]
    software_qualification: Literal["provisional"] = "provisional"
    statistical_qualification: Literal["not_assessed"] = "not_assessed"
    native_equivalence: Literal["not_assessed"] = "not_assessed"


def duration_envelope(curves: Iterable[FrequencyCurve], aep: float) -> DurationEnvelope:
    """Maximum of *separate* duration quantiles; smallest duration breaks exact ties."""
    source = tuple(curves)
    if not source:
        _fail("Duration envelope needs at least one curve")
    first = source[0].scope
    if any(
        item.scope.scenario_id != first.scenario_id
        or item.scope.policy_id != first.policy_id
        or item.scope.policy_version != first.policy_version
        or item.scope.output_site_id != first.output_site_id
        for item in source
    ):
        _fail("Duration envelope must not combine different scenarios, policies or sites")
    if len({item.scope.duration_minutes for item in source}) != len(source):
        _fail("Duplicate duration in duration envelope")
    estimates = tuple(
        (curve.scope.duration_minutes, curve.estimate(aep))
        for curve in sorted(source, key=lambda item: item.scope.duration_minutes)
    )
    available = [(duration, estimate) for duration, estimate in estimates if estimate.peak_m3_s is not None]
    if len(available) != len(estimates):
        state: QuantileStatus = (
            "incomplete" if any(item.status == "incomplete" for _, item in estimates) else "boundary_limited"
        )
        lower_candidates = [
            item.peak_m3_s if item.peak_m3_s is not None else item.lower_bound_m3_s for _, item in estimates
        ]
        upper_candidates = [
            item.peak_m3_s if item.peak_m3_s is not None else item.upper_bound_m3_s for _, item in estimates
        ]
        lower = (
            max(float(value) for value in lower_candidates) if all(v is not None for v in lower_candidates) else None
        )
        upper = (
            max(float(value) for value in upper_candidates) if all(v is not None for v in upper_candidates) else None
        )
        return DurationEnvelope(
            first.scenario_id,
            first.policy_id,
            first.policy_version,
            first.output_site_id,
            aep,
            state,
            None,
            None,
            None,
            lower,
            upper,
            None,
            (),
            estimates,
        )
    ranked = sorted(available, key=lambda pair: (-float(pair[1].peak_m3_s or 0), pair[0]))
    selected_duration, selected = ranked[0]
    selected_peak = float(selected.peak_m3_s or 0)
    runner_up = float(ranked[1][1].peak_m3_s or 0) if len(ranked) > 1 else None
    tied = tuple(duration for duration, item in ranked if item.peak_m3_s == selected_peak)
    return DurationEnvelope(
        first.scenario_id,
        first.policy_id,
        first.policy_version,
        first.output_site_id,
        aep,
        selected.status,
        selected_peak,
        selected_duration,
        selected.representative,
        None,
        None,
        selected_peak - runner_up if runner_up is not None else None,
        tied,
        estimates,
    )
