"""Independent ARR total-probability reference for issue #190 (research only).

Sources: Nathan & Weinmann (2013), ARR Discussion Paper D2, §§4.3, 7.4;
ARR Book 4 v4.2 (2019), §4.4, Table 4.4.3. The optional 2013 outer-bin
geometric assumption is an *illustration*, not the native RORBwin policy.
No production sampler, hydrograph solver or saved method is imported.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Context, Decimal, localcontext
from typing import Literal, Never

Boundary = Literal["interior", "frequent", "rare"]
BoundaryPolicy = Literal["none", "arr2013_illustration"]


def _invalid(message: str) -> Never:
    raise ValueError(message)


def _is_finite_decimal(value: object) -> bool:
    """Defensively check runtime callers without weakening typed dataclass fields."""
    return isinstance(value, Decimal) and value.is_finite()


def _is_exact_integer(value: object) -> bool:
    """Reject booleans and unexpected runtime number types at public boundaries."""
    return isinstance(value, int) and not isinstance(value, bool)


@dataclass(frozen=True, slots=True)
class TPTInterval:
    """One distinct rainfall bin and observed strict exceedance count."""

    identifier: str
    rainfall_mass: Decimal
    exceedances: int
    simulations: int
    boundary: Boundary = "interior"

    def __post_init__(self) -> None:
        if not self.identifier or not self.identifier.strip():
            _invalid("Interval identifier must not be empty")
        if not _is_finite_decimal(self.rainfall_mass):
            _invalid("Rainfall mass must be a finite Decimal, not a float")
        if not 0 <= self.rainfall_mass <= 1:
            _invalid("Rainfall mass must be in [0, 1]")
        if not _is_exact_integer(self.simulations) or self.simulations <= 0:
            _invalid("Simulations must be a positive integer")
        if not _is_exact_integer(self.exceedances) or not 0 <= self.exceedances <= self.simulations:
            _invalid("Exceedances must be an integer between zero and simulations")
        if self.boundary not in ("interior", "frequent", "rare"):
            _invalid("Unrecognised rainfall boundary category")


@dataclass(frozen=True, slots=True)
class TPTContribution:
    """Conditional exceedance and original, unnormalised rainfall mass."""

    identifier: str
    rainfall_mass: Decimal
    conditional_exceedance: Decimal
    unconditional_exceedance: Decimal
    boundary: Boundary


@dataclass(frozen=True, slots=True)
class TPTReferenceResult:
    """A threshold estimate and conservative unmodelled-rainfall bounds.

    Bounds exclude finite-sample uncertainty and any error in the assumed law.
    """

    known_exceedance: Decimal
    modelled_rainfall_mass: Decimal
    unresolved_rainfall_mass: Decimal
    upper_exceedance_bound: Decimal
    boundary_policy: BoundaryPolicy
    contributions: tuple[TPTContribution, ...]

    @property
    def covers_probability_one(self) -> bool:
        return self.unresolved_rainfall_mass == 0


def _validate_reference_policy(intervals: tuple[TPTInterval, ...], policy: BoundaryPolicy) -> None:
    if not intervals:
        _invalid("At least one interval is required")
    if policy not in ("none", "arr2013_illustration"):
        _invalid("Unsupported boundary policy")
    if len({row.identifier for row in intervals}) != len(intervals):
        _invalid("Duplicate interval identifier")
    boundaries = tuple(row.boundary for row in intervals)
    if policy == "none" and any(kind != "interior" for kind in boundaries):
        _invalid("Outer-bin treatment requires explicit boundary policy")
    if policy == "arr2013_illustration" and (
        len(intervals) < 2
        or boundaries[0] != "frequent"
        or boundaries[-1] != "rare"
        or any(kind != "interior" for kind in boundaries[1:-1])
    ):
        _invalid("ARR 2013 illustration requires frequent and rare outer bins in order")


def _conditional_probability(row: TPTInterval, policy: BoundaryPolicy) -> Decimal:
    conditional = Decimal(row.exceedances) / Decimal(row.simulations)
    if policy == "arr2013_illustration":
        if row.boundary == "frequent":
            return conditional * Decimal("0.1").sqrt()
        if row.boundary == "rare":
            return conditional.sqrt()
    return conditional


def total_probability_reference(
    intervals: tuple[TPTInterval, ...], *, boundary_policy: BoundaryPolicy = "none"
) -> TPTReferenceResult:
    """Calculate sum_i p(R_i) * n_i / N_i without renormalising partial support.

    In 'arr2013_illustration', the first/last bins are the paper's explicit
    frequent/rare outer intervals with already full-tail masses. Conditional
    exceedances are replaced by geometric means with 0.1 * p and 1.0.
    This pragmatic illustrative assumption is NOT a RORBwin or product default.
    """
    _validate_reference_policy(intervals, boundary_policy)

    # Context() resets precision, rounding, traps and exponent limits.
    with localcontext(Context(prec=48, rounding=ROUND_HALF_EVEN)):
        mass = sum((row.rainfall_mass for row in intervals), Decimal(0))
        if mass > 1:
            _invalid("Rainfall interval masses exceed probability one")
        if boundary_policy == "arr2013_illustration" and mass != 1:
            _invalid("ARR 2013 full-tail illustration must specify total probability one")

        contributions: list[TPTContribution] = []
        for row in intervals:
            conditional = _conditional_probability(row, boundary_policy)
            contributions.append(
                TPTContribution(
                    row.identifier,
                    row.rainfall_mass,
                    +conditional,
                    +(row.rainfall_mass * conditional),
                    row.boundary,
                )
            )
        known = sum((row.unconditional_exceedance for row in contributions), Decimal(0))
        missing = Decimal(1) - mass
        return TPTReferenceResult(
            +known,
            +mass,
            +missing,
            +min(Decimal(1), known + missing),
            boundary_policy,
            tuple(contributions),
        )
