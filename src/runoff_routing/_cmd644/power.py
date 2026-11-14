"""Research-exposed bounded power approximation with exact documented constants.

This is an independently authored transcription of the owner-approved v2 operation
contract; it is not native source, general-purpose pow, or clean-room decoding.
"""

import math
import struct
from fractions import Fraction
from functools import lru_cache

from .precision import (
    UnsupportedNumericPath,
    add53,
    div53,
    fraction,
    internal_store,
    internal_store_rational,
    mul53,
    store,
    sub53,
)

_TABLE_RATIOS: tuple[tuple[int, int], ...] = (
    (1, 1),
    (2351495508712263, 2251799813685248),
    (613901277312157, 562949953421312),
    (1282162017789723, 1125899906842624),
    (5355712719980343, 4503599627370496),
    (5592830379685591, 4503599627370496),
    (1460111533770265, 1125899906842624),
    (6099024776563411, 4503599627370496),
    (3184525836255917, 2251799813685248),
    (3325516840273195, 2251799813685248),
    (6945500098643221, 4503599627370496),
    (3626501829426903, 2251799813685248),
    (946765195599901, 562949953421312),
    (7909456575010961, 4503599627370496),
    (1032454766818819, 562949953421312),
    (8625323556258569, 4503599627370496),
)
TABLE = tuple(Fraction(a, b) for a, b in _TABLE_RATIOS)
LOG_C = (
    Fraction(6004812949407949, 9007199254740992),
    Fraction(225038089494995, 562949953421312),
    Fraction(5390925971852145, 18014398509481984),
)
LOG_FACTOR = Fraction(1624330212139199, 1125899906842624)
EXP_C = (
    Fraction(6243314764586391, 9007199254740992),
    Fraction(8655072069380201, 36028797018963968),
    Fraction(7999219623028855, 144115188075855872),
    Fraction(1386091390059765, 144115188075855872),
)
MAGIC = Fraction(422212465065984)
EXPONENT = store(0.8)


def _split_normalized(base: float) -> tuple[Fraction, int]:
    """Perform the specified integer high/low-word normalisation."""
    encoded = int.from_bytes(struct.pack("<d", base), "little", signed=False)
    low_word = encoded & 0xFFFFFFFF
    high_word = encoded >> 32
    field = high_word & 0x7FF00000
    displacement = field - 0x3FE00000 - ((high_word - 0x6A09E - field) & 0x100000)
    updated_high = (high_word - displacement) & 0xFFFFFFFF
    updated_bits = (updated_high << 32) | low_word
    normalized = struct.unpack("<d", updated_bits.to_bytes(8, "little", signed=False))[0]
    return fraction(normalized), displacement >> 20


def _scaled_log(base: float, exponent: float) -> Fraction:
    """Construct the p53 logarithmic exponent product without transcendentals."""
    normalized, order = _split_normalized(base)
    delta = sub53(normalized, Fraction(1))
    ratio = div53(delta, add53(normalized, Fraction(1)))
    square = mul53(ratio, ratio)
    p0, p1, p2 = LOG_C
    poly = mul53(add53(mul53(p2, square), p1), square)
    poly = add53(poly, p0)
    y = fraction(exponent)
    scale_y = mul53(y, LOG_FACTOR)
    odd = mul53(mul53(square, ratio), scale_y)
    odd = mul53(poly, odd)
    correction = mul53(sub53(mul53(delta, ratio), delta), scale_y)
    return sub53(odd, sub53(correction, mul53(y, Fraction(order))))


def bounded_power(base: float, exponent: float) -> float:
    """Calculate P(base, exponent) for the exact bounded binary32 domain."""
    if (
        not math.isfinite(exponent)
        or exponent < 0
        or store(exponent) != exponent
        or not math.isfinite(base)
        or base < 0
    ):
        message = "power helper exponent/base outside supported domain"
        raise UnsupportedNumericPath(message)
    if internal_store(base) != base:
        message = "power base must be previously stored binary32"
        raise UnsupportedNumericPath(message)
    return _power_stored(base, exponent)


@lru_cache(maxsize=32768)
def _power_stored(base: float, exponent: float) -> float:
    """Core bounded helper with native-like integer and early-zero branches."""
    if exponent == 0:
        return 1.0  # Including 0**0 under this specifically bounded contract.
    if base == 0:
        return 0.0
    if exponent in (1, 2, 3, 4, 5, 6, 7):
        carried = base
        for _ in range(1, int(exponent)):
            carried = internal_store(carried * base)
        return carried
    exponent_product = _scaled_log(base, exponent)
    if exponent_product < -127:
        return 0.0
    if exponent_product >= 128:
        message = "power helper logarithmic product outside ordinary range"
        raise UnsupportedNumericPath(message)
    magic_plus = add53(exponent_product, MAGIC)
    low = int.from_bytes(struct.pack("<d", float(magic_plus)), "little") & 0xFFFFFFFF
    position = low & 0xF
    leftover = add53(sub53(MAGIC, magic_plus), exponent_product)
    top_word = (((low - position) << 16) + 0x3FF00000) & 0xFFFFFFFF
    scale_bits = top_word << 32
    scale = fraction(struct.unpack("<d", scale_bits.to_bytes(8, "little"))[0])
    c0, c1, c2, c3 = EXP_C
    curve_high = mul53(add53(mul53(c3, leftover), c2), mul53(leftover, leftover))
    curve_low = add53(mul53(c1, leftover), c0)
    polynomial = add53(curve_low, curve_high)
    polynomial = mul53(polynomial, mul53(leftover, TABLE[position]))
    polynomial = add53(polynomial, TABLE[position])
    return internal_store_rational(mul53(polynomial, scale))
