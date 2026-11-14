"""Exact scalar p53 and binary32 stores for the bounded numerical profile.

This module has no filesystem, environment, or process effects. The host binary64
values are considered exact rationals on entry to a rounding operation.
"""

import math
import struct
from fractions import Fraction


class UnsupportedNumericPathError(ArithmeticError):
    """Operation leaves the bounded finite/ordinary arithmetic domain."""


# Preserve the submitted public exception import and catch identity.
UnsupportedNumericPath = UnsupportedNumericPathError


def nearest_binary(value: Fraction, significant_bits: int) -> Fraction:
    """Round an exact rational to the nearest binary significand; ties go to even."""
    if not value:
        return Fraction()
    magnitude = abs(value)
    logarithm_floor = magnitude.numerator.bit_length() - magnitude.denominator.bit_length()
    base = Fraction(2) ** logarithm_floor
    if magnitude < base:
        logarithm_floor -= 1
    step = Fraction(2) ** (logarithm_floor + 1 - significant_bits)
    scaled = magnitude / step
    integer, remainder = divmod(scaled.numerator, scaled.denominator)
    twice = 2 * remainder
    if twice > scaled.denominator or (twice == scaled.denominator and integer % 2 != 0):
        integer += 1
    return (1 if value > 0 else -1) * step * integer


def r53(value: Fraction) -> Fraction:
    """Perform one exact-rational binary64-significand operation."""
    return nearest_binary(value, 53)


def add53(a: Fraction, b: Fraction) -> Fraction:
    """R53(a + b)."""
    return r53(a + b)


def sub53(a: Fraction, b: Fraction) -> Fraction:
    """R53(a - b)."""
    return r53(a - b)


def mul53(a: Fraction, b: Fraction) -> Fraction:
    """R53(a * b)."""
    return r53(a * b)


def div53(a: Fraction, b: Fraction) -> Fraction:
    """R53(a / b), excluding zero denominator."""
    if b == 0:
        message = "zero denominator"
        raise UnsupportedNumericPath(message)
    return r53(a / b)


def fraction(value: float) -> Fraction:
    """Return an exact rational corresponding to a finite binary64 operand."""
    if not math.isfinite(value):
        message = "nonfinite binary64 operand"
        raise UnsupportedNumericPath(message)
    return Fraction(value)


_MAX_F32 = Fraction(2) ** 128 - Fraction(2) ** 104
_MIN_NORMAL_F32 = Fraction(2) ** -126


def store_rational(value: Fraction) -> float:
    """Round to normal binary32 (or +0) without binary64 double rounding."""
    stored = nearest_binary(value, 24)
    if stored and not _MIN_NORMAL_F32 <= abs(stored) <= _MAX_F32:
        message = "outside finite normal binary32 range"
        raise UnsupportedNumericPath(message)
    if value and not stored:
        message = "positive value underflowed to binary32 zero"
        raise UnsupportedNumericPath(message)
    return float(stored)


def direct_binary32(value: Fraction) -> Fraction:
    """Round to a normal/subnormal binary32 grid without double rounding."""
    if not value:
        return Fraction()
    if abs(value) >= _MIN_NORMAL_F32:
        return nearest_binary(value, 24)
    scaled = abs(value) * (2**149)
    whole, remainder = divmod(scaled.numerator, scaled.denominator)
    if remainder * 2 > scaled.denominator or (remainder * 2 == scaled.denominator and whole % 2):
        whole += 1
    return (1 if value > 0 else -1) * Fraction(whole, 2**149)


def internal_store_rational(value: Fraction) -> float:
    """Round an internal value to binary32 including gradual underflow."""
    result = direct_binary32(value)
    if abs(result) > _MAX_F32:
        message = "internal binary32 overflow"
        raise UnsupportedNumericPath(message)
    return float(result)


def internal_store(value: float) -> float:
    """Finite internal binary32 store; exact positive zero is permitted."""
    if value == 0.0 and math.copysign(1.0, value) < 0:
        message = "negative zero is excluded"
        raise UnsupportedNumericPath(message)
    return internal_store_rational(fraction(value))


def store(value: float) -> float:
    """Store one finite binary64 float as nearest-even normal binary32."""
    if value == 0.0 and math.copysign(1.0, value) < 0:
        message = "negative zero is excluded"
        raise UnsupportedNumericPath(message)
    return store_rational(fraction(value))


def binary32_hex(value: float) -> str:
    """Emit eight big-endian hex digits for an actual stored binary32."""
    if internal_store(value) != value:
        message = "value is not a stored binary32"
        raise UnsupportedNumericPath(message)
    return struct.pack(">f", value).hex()


def binary64_hex(value: float) -> str:
    """Emit sixteen big-endian hex digits for an actual binary64 operand."""
    return struct.pack(">d", value).hex()


def safe64(value: float) -> float:
    """Reject nonfinite results and arithmetic underflow unsupported by this profile."""
    if not math.isfinite(value):
        message = "nonfinite binary64 result"
        raise UnsupportedNumericPath(message)
    if value != 0 and abs(value) < math.ldexp(1.0, -1022):
        message = "binary64 subnormal result unsupported"
        raise UnsupportedNumericPath(message)
    return value
