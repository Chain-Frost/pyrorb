"""Evidence gates for the existing #53 comparator, without a second case register.

The maintained runner may adapt its authenticated records to these small immutable
inputs. These helpers never acquire evidence or promote inferred states to observed.
"""

from dataclasses import dataclass
from fractions import Fraction
from typing import Literal

from runoff_routing.regression_metrics import token_interval

Verdict = Literal["pass", "fail", "unsupported", "incomplete", "not_run"]


@dataclass(frozen=True, slots=True)
class Gate:
    """A structured field result, not a whole-case scientific acceptance."""

    verdict: Verdict
    reason: str


@dataclass(frozen=True, slots=True)
class SeriesIdentity:
    """Ordered original site/row/clock tokens and sample count from a frozen binding."""

    sites: tuple[str, ...]
    increments: tuple[str, ...]
    clocks: tuple[str, ...]
    scalar_tokens: tuple[str, ...]
    samples: int


def series_gate(expected: SeriesIdentity, actual: SeriesIdentity) -> Gate:
    """Reject loss, duplication, reordering, precision drift or raw-clock changes."""
    for record in (expected, actual):
        if not record.sites or len(record.sites) != len(set(record.sites)):
            return Gate("fail", "missing_or_duplicate_site")
        if record.samples < 2 or len(record.increments) != record.samples or len(record.clocks) != record.samples:
            return Gate("incomplete", "full_horizon_missing")
        if record.increments != tuple(str(i + 1) for i in range(record.samples)):
            return Gate("fail", "increment_order")
    if actual.sites != expected.sites:
        return Gate("fail", "ordered_site_population")
    if actual.samples != expected.samples:
        return Gate("incomplete", "full_horizon_missing")
    if actual.clocks != expected.clocks:
        return Gate("fail", "original_raw_clock_tokens")
    if actual.scalar_tokens != expected.scalar_tokens:
        return Gate("fail", "original_scalar_precision_or_value")
    return Gate("pass", "complete_original_identity")


def printed_peak_gate(tokens: tuple[str, ...]) -> Gate:
    """Classify interval ambiguity without inventing native stored-Q ties."""
    if not tokens:
        return Gate("incomplete", "native_printed_series_missing")
    intervals = tuple(token_interval(token) for token in tokens)
    largest_lower = max(lower for lower, _ in intervals)
    possible = tuple(i for i, (_, upper) in enumerate(intervals) if upper >= largest_lower)
    if len(possible) != 1:
        return Gate("incomplete", "printed_intervals_do_not_determine_native_maximum")
    return Gate("pass", "unique_print_interval_maximum_only")


def exact_ties_gate(native: tuple[Fraction, ...] | None, candidate: tuple[Fraction, ...]) -> Gate:
    """Compare exact tied indices only with a complete independent stored-Q oracle."""
    if native is None:
        return Gate("incomplete", "independent_native_stored_q_missing")
    if not native or len(native) != len(candidate):
        return Gate("incomplete", "full_native_stored_q_horizon_missing")
    native_ties = tuple(i for i, value in enumerate(native) if value == max(native))
    candidate_ties = tuple(i for i, value in enumerate(candidate) if value == max(candidate))
    return Gate("pass" if native_ties == candidate_ties else "fail", "exact_observed_tied_indices")


@dataclass(frozen=True, slots=True)
class ConservationEvidence:
    """Availability only; no residual or candidate-derived replacement observations."""

    expected_sources: tuple[str, ...]
    counted_sources: tuple[str, ...]
    initial_storage_observed: bool
    terminal_storage_observed: bool
    inlet_outlet_observed: bool
    budget_policy: str | None


def conservation_gate(evidence: ConservationEvidence) -> Gate:
    """Check ownership and native observations before any balance calculation."""
    sources = evidence.counted_sources
    if len(sources) != len(set(sources)) or sources != evidence.expected_sources:
        return Gate("fail", "external_source_ownership_or_double_counting")
    observations = (
        evidence.initial_storage_observed,
        evidence.terminal_storage_observed,
        evidence.inlet_outlet_observed,
    )
    if not all(observations):
        return Gate("incomplete", "independent_initial_terminal_or_flux_observation_missing")
    if evidence.budget_policy is None:
        return Gate("incomplete", "independently_justified_budget_missing")
    return Gate("not_run", "eligible_for_separate_budgeted_balance_evaluation")


def metric_scope_gate(*, supported: bool, requested: bool) -> Gate:
    """Preserve supported execution, requested execution and acceptance distinctions."""
    if not supported:
        return Gate("unsupported", "outside_frozen_metric_profile")
    return Gate("not_run", "evaluation_pending" if requested else "metric_not_requested")
