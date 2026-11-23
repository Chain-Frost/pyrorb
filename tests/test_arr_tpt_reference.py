"""Source-cited numerical reference controls; not RORBwin-native observations."""

from __future__ import annotations

import importlib.util
import sys
from decimal import ROUND_DOWN, ROUND_UP, Decimal, Inexact, localcontext
from pathlib import Path
from types import ModuleType

import pytest


def _reference() -> ModuleType:
    path = Path(__file__).parents[1] / "repo-scripts" / "arr_tpt_reference.py"
    spec = importlib.util.spec_from_file_location("arr_tpt_reference", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_arr_d2_2013_table_3_with_documented_outer_interval_assumptions() -> None:
    """D2 §7.4, p.38: printed inputs give 0.057161; reported result 0.0572.

    First/last widths 0.5000/0.0133 represent full tail masses, and their
    conditional values use the explicit D2 boundary geometric assumptions.
    Printed 4dp widths are an example, not a RORBwin-native weight record.
    """
    ref = _reference()
    masses = ("0.5000", "0.3000", "0.1000", "0.0333", "0.0167", "0.0167", "0.0083", "0.0050", "0.0067", "0.0133")
    exceeded = (0, 2, 10, 24, 48, 112, 170, 190, 200, 200)
    intervals = tuple(
        ref.TPTInterval(
            f"published-{index + 1}",
            Decimal(mass),
            count,
            200,
            "frequent" if index == 0 else "rare" if index == 9 else "interior",
        )
        for index, (mass, count) in enumerate(zip(masses, exceeded, strict=True))
    )
    result = ref.total_probability_reference(intervals, boundary_policy="arr2013_illustration")
    assert result.known_exceedance == Decimal("0.057161")
    assert abs(result.known_exceedance - Decimal("0.0572")) < Decimal("0.00005")
    assert result.covers_probability_one
    assert result.unresolved_rainfall_mass == 0
    assert sum((part.unconditional_exceedance for part in result.contributions), Decimal(0)) == result.known_exceedance


def test_arr_book4_v42_table_443_retains_unmodelled_probability() -> None:
    """Book 4 §4.4 Table 4.4.3, p.69: printed values ≈0.014911.

    Six-decimal published widths and conditional counts give 0.0149121. No
    full-tail closure is inferred from the tabulated 1.0-4.0 z interval.
    """
    ref = _reference()
    masses = (
        "0.061855",
        "0.042001",
        "0.026083",
        "0.014813",
        "0.007694",
        "0.003655",
        "0.001588",
        "0.000631",
        "0.000229",
        "0.000076",
    )
    exceeded = (0, 0, 0, 4, 15, 20, 20, 20, 20, 20)
    rows = tuple(
        ref.TPTInterval(f"z-{index + 1}", Decimal(mass), n, 20)
        for index, (mass, n) in enumerate(zip(masses, exceeded, strict=True))
    )
    result = ref.total_probability_reference(rows)
    assert result.known_exceedance == Decimal("0.0149121")
    assert abs(result.known_exceedance - Decimal("0.014911")) < Decimal("0.000002")
    assert result.modelled_rainfall_mass == Decimal("0.158625")
    assert result.unresolved_rainfall_mass == Decimal("0.841375")
    assert not result.covers_probability_one
    assert result.upper_exceedance_bound == Decimal("0.8562871")


def test_hand_calculated_unequal_strata_and_strict_exceedance() -> None:
    ref = _reference()
    dry = (0, 20)
    wet = (10, 10)
    rows = (
        ref.TPTInterval("dry", Decimal("0.2"), sum(q > 10 for q in dry), len(dry)),
        ref.TPTInterval("wet", Decimal("0.8"), sum(q > 10 for q in wet), len(wet)),
    )
    result = ref.total_probability_reference(rows)
    assert result.known_exceedance == Decimal("0.1")
    assert result.covers_probability_one
    assert result.contributions[0].conditional_exceedance == Decimal("0.5")
    assert result.contributions[1].conditional_exceedance == 0


def test_incomplete_annual_probability_support_does_not_renormalise() -> None:
    ref = _reference()
    rows = (ref.TPTInterval("modelled", Decimal("0.49"), 1, 2),)
    result = ref.total_probability_reference(rows)
    assert result.known_exceedance == Decimal("0.245")
    assert result.unresolved_rainfall_mass == Decimal("0.51")
    assert result.upper_exceedance_bound == Decimal("0.755")
    assert not result.covers_probability_one


def test_2013_geometric_boundaries_are_explicit_and_change_result() -> None:
    ref = _reference()
    frequent = ref.TPTInterval("frequent", Decimal("0.5"), 1, 2, "frequent")
    rare = ref.TPTInterval("rare", Decimal("0.5"), 1, 4, "rare")
    with pytest.raises(ValueError, match="explicit boundary"):
        ref.total_probability_reference((frequent, rare))
    actual = ref.total_probability_reference((frequent, rare), boundary_policy="arr2013_illustration")
    with localcontext() as ctx:
        ctx.prec = 48
        expected = Decimal("0.25") * Decimal("0.1").sqrt() + Decimal("0.25")
    assert actual.known_exceedance == expected
    assert actual.boundary_policy == "arr2013_illustration"


def test_2013_boundary_policy_refuses_missing_tails_or_incorrect_order() -> None:
    ref = _reference()
    with pytest.raises(ValueError, match="total probability one"):
        ref.total_probability_reference(
            (
                ref.TPTInterval("a", Decimal("0.3"), 1, 2, "frequent"),
                ref.TPTInterval("b", Decimal("0.3"), 2, 2, "rare"),
            ),
            boundary_policy="arr2013_illustration",
        )
    with pytest.raises(ValueError, match="frequent and rare"):
        ref.total_probability_reference(
            (
                ref.TPTInterval("a", Decimal("0.5"), 1, 2, "rare"),
                ref.TPTInterval("b", Decimal("0.5"), 2, 2, "frequent"),
            ),
            boundary_policy="arr2013_illustration",
        )


def test_result_is_decimal_context_independent() -> None:
    ref = _reference()
    rows = (
        ref.TPTInterval("a", Decimal("0.25"), 1, 3),
        ref.TPTInterval("b", Decimal("0.75"), 2, 7),
    )
    with localcontext() as ctx:
        ctx.prec = 9
        ctx.rounding = ROUND_DOWN
        ctx.traps[Inexact] = True
        a = ref.total_probability_reference(rows)
    with localcontext() as ctx:
        ctx.prec = 60
        ctx.rounding = ROUND_UP
        ctx.traps[Inexact] = False
        b = ref.total_probability_reference(rows)
    assert a == b
    # One-third cannot be represented exactly; it must not inherit caller
    # rounding or trip an enabled ambient Inexact trap.
    third = (ref.TPTInterval("third", Decimal(1), 1, 3),)
    with localcontext() as ctx:
        ctx.prec = 6
        ctx.rounding = ROUND_DOWN
        ctx.traps[Inexact] = True
        low = ref.total_probability_reference(third)
    with localcontext() as ctx:
        ctx.prec = 28
        ctx.rounding = ROUND_UP
        ctx.traps[Inexact] = False
        high = ref.total_probability_reference(third)
    assert low == high
    assert low.known_exceedance > Decimal("0.333333333333333333333333333333")


@pytest.mark.parametrize("mass", [Decimal("NaN"), Decimal("Infinity"), Decimal("-0.1"), Decimal("1.01"), 0.5])
def test_nonfinite_and_float_masses_are_rejected(mass: object) -> None:
    ref = _reference()
    with pytest.raises(ValueError, match="Rainfall mass"):
        ref.TPTInterval("bad", mass, 1, 2)


@pytest.mark.parametrize(("count", "trials"), [(2, 1), (-1, 1), (True, 1), (0, 0), (1, 1.5), (1, True)])
def test_invalid_simulation_counts_are_rejected(count: object, trials: object) -> None:
    ref = _reference()
    with pytest.raises(ValueError, match=r"Exceedances|Simulations"):
        ref.TPTInterval("invalid", Decimal("0.1"), count, trials)


def test_duplicate_ids_mass_overshoot_empty_or_unknown_policy_rejected() -> None:
    ref = _reference()
    a = ref.TPTInterval("same", Decimal("0.6"), 1, 2)
    b = ref.TPTInterval("same", Decimal("0.4"), 1, 2)
    with pytest.raises(ValueError, match="Duplicate"):
        ref.total_probability_reference((a, b))
    with pytest.raises(ValueError, match="exceed probability one"):
        ref.total_probability_reference((a, ref.TPTInterval("different", Decimal("0.6"), 1, 2)))
    with pytest.raises(ValueError, match="At least one"):
        ref.total_probability_reference(())
    with pytest.raises(ValueError, match="Unsupported boundary"):
        ref.total_probability_reference((a,), boundary_policy="guessed_native")
