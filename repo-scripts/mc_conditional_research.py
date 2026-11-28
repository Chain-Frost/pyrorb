"""Read-only #148 conditional research aggregation; not the production flood estimator."""

from __future__ import annotations

import math
from bisect import bisect_left, bisect_right
from collections.abc import Iterable, Mapping
from decimal import Decimal
from fractions import Fraction
from itertools import accumulate
from pathlib import Path
from typing import NamedTuple, Never, cast

DOMAIN = Fraction(49, 100)
MAX_DRAWS = 1_000_000
UNKNOWN_STATUSES = {
    "unsupported_feature",
    "unavailable_engine",
    "invalid_input",
    "numerical_error",
    "incomplete_output",
    "native_execution_failed",
}


class Artifact(NamedTuple):
    """Externally pinned immutable artifact, not a self-authenticating hash."""

    path: Path
    sha256: str


class ConditionalCurve(NamedTuple):
    """Logical finite-ledger bounds, not population confidence intervals."""

    known: tuple[tuple[Fraction, Fraction], ...]
    cumulative: tuple[Fraction, ...]
    unknown_mass: Fraction
    status_counts: dict[str, int]
    planned_count: int

    def cdf(self, threshold: Fraction) -> tuple[Fraction, Fraction]:
        """Conditional CDF bounds at a finite nonnegative flow threshold."""
        if threshold < 0:
            _fail("Expected a nonnegative threshold")
        index = bisect_right(self.known, (threshold, DOMAIN))
        observed = self.cumulative[index - 1] if index else Fraction(0)
        return observed / DOMAIN, (observed + self.unknown_mass) / DOMAIN

    def survival(self, threshold: Fraction) -> tuple[Fraction, Fraction]:
        """Strict exceedance, including ties and exact zero."""
        lower, upper = self.cdf(threshold)
        return 1 - upper, 1 - lower

    def quantile(self, exceedance: Fraction) -> tuple[Fraction, Fraction | None]:
        """Attained inverse bounds; None means no finite upper bound."""
        if not 0 < exceedance < 1:
            _fail("Conditional response exceedance must be inside (0,1)")
        target = DOMAIN * (1 - exceedance)
        lower = Fraction(0) if self.unknown_mass >= target else self._inverse(target - self.unknown_mass)
        if lower is None:
            _fail("Inconsistent conditional ledger mass")
        return lower, self._inverse(target)

    def _inverse(self, target: Fraction) -> Fraction | None:
        index = bisect_left(self.cumulative, target)
        return self.known[index][0] if index < len(self.known) else None


def _fail(message: str) -> Never:
    raise ValueError(message)


def _allocations(allocations: Mapping[str, tuple[Decimal, int]]) -> dict[str, tuple[Fraction, int]]:
    result: dict[str, tuple[Fraction, int]] = {}
    for key, (mass, count) in allocations.items():
        if not key or not mass.is_finite() or not 0 < mass <= 1:
            _fail("Invalid stratum identity or mass")
        if type(count) is not int or not 0 < count <= MAX_DRAWS:
            _fail("Every positive-mass stratum needs a bounded positive planned allocation")
        result[key] = (Fraction(mass), count)
    if sum((mass for mass, _ in result.values()), Fraction(0)) != DOMAIN:
        _fail("Expected exact restricted rainfall mass 0.49")
    if sum(count for _, count in result.values()) > MAX_DRAWS:
        _fail("Planned draw cap exceeded")
    return result


def _site_peak(row: dict[str, object], site_id: str) -> tuple[str, Fraction | None]:
    status = row.get("status")
    if not isinstance(status, str):
        _fail("Missing verified result status")
    if status in UNKNOWN_STATUSES:
        return status, None
    if status != "computed_unvalidated":
        _fail("Unexpected verified result status")
    return _computed_peak(row, site_id)


def _computed_peak(row: dict[str, object], site_id: str) -> tuple[str, Fraction | None]:
    sites = row.get("sites")
    if not isinstance(sites, list):
        _fail("Missing computed site list")
    matches: list[dict[str, object]] = []
    for site in cast("list[object]", sites):
        if not isinstance(site, dict):
            _fail("Malformed computed site record")
        entry = cast("dict[str, object]", site)
        if entry.get("print_id") == site_id:
            matches.append(entry)
    if not matches:
        return "missing_site", None
    if len(matches) != 1:
        _fail("Ambiguous computed site identity")
    return "valid", _peak(matches[0].get("peak_m3_s"))


def _peak(peak: object) -> Fraction:
    if not isinstance(peak, (int, float)) or isinstance(peak, bool) or peak < 0:
        _fail("Invalid computed site peak")
    if isinstance(peak, float) and not math.isfinite(peak):
        _fail("Nonfinite computed site peak")
    return Fraction(peak)


def _row_identity(row: dict[str, object], scenario: str, duration: int) -> tuple[str, str]:
    if row.get("scenario_id") != scenario or row.get("duration_min") != duration:
        _fail("Mixed scenario or duration in conditional cohort")
    sample, stratum = row.get("sample_id"), row.get("stratum_id")
    if not isinstance(sample, str) or not sample or not isinstance(stratum, str) or not stratum:
        _fail("Missing verified sample or stratum identity")
    return sample, stratum


def conditional_curve(
    allocations: Mapping[str, tuple[Decimal, int]],
    rows: Iterable[dict[str, object]],
    *,
    scenario: str,
    duration: int,
    site_id: str,
) -> ConditionalCurve:
    """Consume a FULL verified prefix; use exact allocation masses, never rounded row weights.

    Caller must establish the row identities against the immutable plan. Empty rows
    represent a wholly unknown planned cohort, not evidence of zero discharge.
    Bounds assume a defined nonnegative latent response, not a scientific admission.
    """
    if not scenario or not site_id or type(duration) is not int or duration <= 0:
        _fail("Invalid cohort scope")
    planned = _allocations(allocations)
    total = sum(count for _, count in planned.values())
    seen: set[str] = set()
    counts: dict[str, int] = dict.fromkeys(planned, 0)
    statuses: dict[str, int] = {}
    groups: dict[Fraction, Fraction] = {}
    for row in rows:
        sample, stratum = _row_identity(row, scenario, duration)
        if sample in seen or stratum not in planned:
            _fail("Duplicate sample or undeclared stratum")
        seen.add(sample)
        mass, count = planned[stratum]
        counts[stratum] += 1
        if counts[stratum] > count:
            _fail("Recorded rows exceed planned allocation")
        status, peak = _site_peak(row, site_id)
        statuses[status] = statuses.get(status, 0) + 1
        if peak is not None:
            groups[peak] = groups.get(peak, Fraction(0)) + mass / count
    statuses["unrecorded"] = total - len(seen)
    known = tuple(sorted(groups.items()))
    cumulative = tuple(accumulate(mass for _, mass in known))
    unknown = DOMAIN - (cumulative[-1] if cumulative else Fraction(0))
    return ConditionalCurve(known, cumulative, unknown, statuses, total)


def read_verified_cohort(
    project: Artifact,
    request: Artifact,
    ledger: Artifact,
    *,
    site_id: str,
    wheel: Artifact | None = None,
) -> ConditionalCurve:
    """Read one already-recorded Python CMD cohort; never execute or write anything.

    Pins must come from external immutable custody. An entirely unstarted cohort
    has no verified ledger; use the pure kernel only after plan admission.
    """
    # Keep standalone mathematical controls usable without the product installed.
    from runoff_routing.monte_carlo_effective import read_header, sha256_file  # noqa: PLC0415
    from runoff_routing.monte_carlo_execution import iter_verified_mc_results  # noqa: PLC0415
    from runoff_routing.project_json import load_project  # noqa: PLC0415

    artifacts = (project, request, ledger) if wheel is None else (project, request, ledger, wheel)

    def verify() -> None:
        for artifact in artifacts:
            if sha256_file(artifact.path) != artifact.sha256:
                _fail("Externally pinned artifact digest mismatch")

    verify()
    header = read_header(request.path)
    if len(header.populations) != 1 or not header.strata or header.policy_id != "monte-carlo-statistics/1":
        _fail("Expected one explicit v1 scenario/duration population")
    pop = header.populations[0]
    if (pop.modelled_mass, pop.rare_unmodelled_mass, pop.frequent_unmodelled_mass) != (
        Decimal("0.49"),
        Decimal("0.01"),
        Decimal("0.50"),
    ):
        _fail("Expected fixed restricted support and explicit excluded tails")
    loaded = load_project(project.path)
    engine = loaded.project.engine
    if (engine.engine, engine.numerical_profile) != ("python-cmd", "cmd-6.44"):
        _fail("Expected stored Python CMD profile")
    sites = tuple(item.identifier for item in loaded.run.catchment.print_locations)
    if sites.count(site_id) != 1:
        _fail("Unknown or ambiguous project print ID")
    allocations = {item.stratum_id: (item.probability_mass, item.planned_samples) for item in header.strata}
    if len(allocations) != len(header.strata):
        _fail("Duplicate header stratum identity")
    rows = iter_verified_mc_results(
        project.path, request.path, ledger.path, wheel_artifact=None if wheel is None else wheel.path
    )
    curve = conditional_curve(allocations, rows, scenario=pop.scenario_id, duration=pop.duration_min, site_id=site_id)
    verify()
    return curve
