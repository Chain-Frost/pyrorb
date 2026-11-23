"""Authored synthetic contract controls; not original RORBwin/native evidence."""

from __future__ import annotations

from dataclasses import replace
from decimal import Context, Decimal, localcontext
from typing import cast

import pytest

from runoff_routing import monte_carlo_comparison as mc


_DIGEST = "a" * 64


def _record(*, cohort: str = "C1", duration: int = 1440, site: str | None = None) -> mc.MCNativeRecord:
    return mc.MCNativeRecord(
        mc.MCNativeSource(_DIGEST, "6.52"),
        mc.MCEventKey(cohort, "R1", duration, 1, 1, physical_site_id=site),
        mc.MCField("rounded_print", "0.00", "m3/s", 12),
        mc.MCField("rounded_print", "1.20D+00", "printed-AEP-unit-unverified", 12),
        native_tp_rank=2,
    )


def test_printed_zero_not_exact_zero_and_fortran_token_preserved() -> None:
    record = _record()
    assert record.peak_m3s.decimal == Decimal(0)
    assert record.peak_m3s.quality == "rounded_print"
    assert record.peak_m3s.conditional_nearest_print_interval() == (Decimal("-0.005"), Decimal("0.005"))
    assert record.rainfall_probability.decimal == Decimal("1.20")
    expected_source_print = "1.20D+00"
    assert record.rainfall_probability.token == expected_source_print
    assert record.rainfall_probability.conditional_nearest_print_interval() == (
        Decimal("1.195"), Decimal("1.205")
    )


def test_unavailable_is_not_inferred_or_assigned_source_identity() -> None:
    record = _record()
    assert record.original_tp_event_id is None
    assert record.python_sample_id is None
    assert record.native_tp_rank == 2
    assert record.native_event_weight == mc.MCField("unavailable")
    assert record.native_event_weight.decimal is None
    assert record.native_event_weight.conditional_nearest_print_interval() is None
    view = mc.assess_native_comparison((record,))
    assert view.input_law == "descriptive_only"
    assert view.exact_event_replay == "unavailable"
    assert view.native_weighted_reaggregation == "unavailable"
    assert view.native_published_summary == "unavailable"


def test_native_identity_must_include_cohort_duration_and_site() -> None:
    records = (_record(cohort="C1"), _record(cohort="C2"), _record(duration=720), _record(site="P1"))
    assert mc.assess_native_comparison(records).input_law == "descriptive_only"
    with pytest.raises(mc.MCComparisonInputError, match="duplicate cohort"):
        mc.assess_native_comparison((_record(), _record()))


@pytest.mark.parametrize("value", ["NaN", "Infinity", "1_2", "1.2 foo", " 1.2", "1.2 "])
def test_invalid_numeric_tokens_fail_closed(value: str) -> None:
    with pytest.raises(mc.MCComparisonInputError, match="source numeric token"):
        mc.MCField("rounded_print", value, "mm", 1)


@pytest.mark.parametrize("count", [0, -1, True])
def test_invalid_event_scope_fails_closed(count: int) -> None:
    with pytest.raises(mc.MCComparisonInputError, match="positive integer"):
        mc.MCEventKey("C", "R", 1440, count, 1)


def test_digest_and_missing_fields_fail_closed() -> None:
    with pytest.raises(mc.MCComparisonInputError, match="SHA-256"):
        mc.MCNativeSource("short")
    with pytest.raises(mc.MCComparisonInputError, match="unavailable fields"):
        mc.MCField("unavailable", "0", "mm")
    with pytest.raises(mc.MCComparisonInputError, match="source_line"):
        mc.MCField("rounded_print", "1", "mm", 0)


def test_no_numeric_or_statistical_admission_from_unsupported_inputs() -> None:
    record = _record()
    assert mc.comparison_json_ready((record,))["schema"] == "pyrorb-native-mc-comparison-evidence/1"
    readiness = cast(dict[str, object], mc.comparison_json_ready((record,))["readiness"])
    assert readiness["native_weighted_reaggregation"] == "unavailable"
    assert mc.assess_native_comparison(()).input_law == "unavailable"
    assert mc.assess_native_comparison((_record(),)).exact_event_replay == "unavailable"


def test_unverified_weight_cannot_enable_native_reaggregation() -> None:
    reported_weight = mc.MCField("rounded_print", "0.20", "unknown-native-weight", 15)
    record = replace(_record(), native_event_weight=reported_weight, original_tp_event_id="A1")
    assert mc.assess_native_comparison((record,)).native_weighted_reaggregation == "unavailable"


def test_print_interval_is_context_independent_for_high_precision() -> None:
    long_print = mc.MCField("rounded_print", "1.2345678901234567890123456789", "mm", 6)
    first = long_print.conditional_nearest_print_interval()
    assert first == (
        Decimal("1.23456789012345678901234567885"),
        Decimal("1.23456789012345678901234567895"),
    )
    with localcontext(Context(prec=3)):
        assert long_print.conditional_nearest_print_interval() == first
        assert mc.MCField("rounded_print", "1234.00", "mm", 7).conditional_nearest_print_interval() == (
            Decimal("1233.995"),
            Decimal("1234.005"),
        )


def test_negative_print_interval_uses_exact_signed_coefficients() -> None:
    with localcontext(Context(prec=3)):
        value = mc.MCField("rounded_print", "-1.20", "mm", 5)
        assert value.conditional_nearest_print_interval() == (Decimal("-1.205"), Decimal("-1.195"))


def test_invalid_field_quality_rejected_at_runtime() -> None:
    with pytest.raises(mc.MCComparisonInputError, match="unsupported field quality"):
        mc.MCField(cast(mc.FieldQuality, "forged"), "1.00", "mm", 10)


@pytest.mark.parametrize("token", ["1E+999999999", "1E-999999999"])
def test_extreme_exponents_fail_closed(token: str) -> None:
    with pytest.raises(mc.MCComparisonInputError, match="exponent exceeds"):
        mc.MCField("rounded_print", token, "mm", 1)


def test_oversized_source_numeric_token_rejected() -> None:
    with pytest.raises(mc.MCComparisonInputError, match="too long"):
        mc.MCField("rounded_print", "1" * 300, "mm", 1)
