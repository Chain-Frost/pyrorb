"""Native target views retain the original model trace and accepted state."""

import struct
from dataclasses import replace

from runoff_routing._cmd644.native_diagnostics import TargetOperands, target_diagnostic


def operands() -> TargetOperands:
    return TargetOperands(8, 0.0, 0.0, 3600.0, 0.0, 0.0, 900.0, 0.0)


def test_dry_constant_storage_has_distinct_exact_native_target() -> None:
    actual = target_diagnostic(operands())
    assert actual.model_target == 0.0
    assert struct.pack(">d", actual.native_compatibility_target).hex() == "4010000000000000"
    assert actual.basis == "m0-dry-continuity"


def test_nonzero_exponent_retains_actual_target() -> None:
    actual = target_diagnostic(replace(operands(), exponent=0.8, model_target=0.125))
    assert actual.native_compatibility_target == actual.model_target == 0.125
    assert actual.basis == "v6-model-target"


def test_active_zero_exponent_retains_calculated_target() -> None:
    actual = target_diagnostic(replace(operands(), previous_i=0.25, model_target=4.125))
    assert actual.native_compatibility_target == 4.125
    assert actual.basis == "v6-model-target"


def test_ordinary_zero_storage_stays_zero() -> None:
    actual = target_diagnostic(replace(operands(), previous_s=0.0))
    assert actual.native_compatibility_target == 0.0


def test_projection_does_not_mutate_operands() -> None:
    before = operands()
    target_diagnostic(before)
    assert before == operands()
