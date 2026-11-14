"""Explicit native target view; the frozen v6 target and numerical state stay intact.

The m=0 dry shortcut emits a model trace placeholder, whereas retained CMD records
contain the continuity target with constant storage. This view reports both values.
It is not a replacement routing step or permission to change the v6 fixture schema.
"""

from dataclasses import dataclass
from typing import Literal

from .precision import safe64

DIAGNOSTIC_PROFILE = "cmd644-native-target-diagnostics-v1"


@dataclass(frozen=True, slots=True)
class TargetOperands:
    """Actual emitted candidate operands; durations are stored seconds."""

    sample_index: int
    exponent: float
    previous_q: float
    previous_s: float
    previous_i: float
    current_i: float
    duration_seconds: float
    model_target: float


@dataclass(frozen=True, slots=True)
class TargetDiagnostic:
    """Distinct historical model and native-continuity diagnostic identities."""

    sample_index: int
    model_target: float
    native_compatibility_target: float
    basis: Literal["v6-model-target", "m0-dry-continuity"]


def target_diagnostic(operands: TargetOperands) -> TargetDiagnostic:
    """Interpret the dry m=0 target without mutating or rerouting accepted states.

    Only the existing m=0 dry shortcut is projected. All other targets are preserved
    directly from the actual calculation, including clamping and precision decisions.
    """
    dry_constant_storage = (
        operands.exponent == 0.0
        and operands.previous_q == 0.0
        and operands.previous_i == 0.0
        and operands.current_i == 0.0
    )
    if dry_constant_storage:
        target = max(0.0, safe64(operands.previous_s / operands.duration_seconds))
        return TargetDiagnostic(operands.sample_index, operands.model_target, target, "m0-dry-continuity")
    return TargetDiagnostic(operands.sample_index, operands.model_target, operands.model_target, "v6-model-target")
