"""Per-source rainfall and IL/CL state transitions for the bounded start-zero event."""

from dataclasses import dataclass
from fractions import Fraction

from .models import Event, NumberInput
from .precision import (
    UnsupportedNumericPath,
    add53,
    div53,
    fraction,
    mul53,
    store_rational,
    sub53,
)


@dataclass(frozen=True, slots=True)
class LossCrossing:
    """One-based diagnostic crossing bin; None when initial loss never crosses."""

    source_id: int
    bin_one_based: int | None
    signed_remaining: Fraction
    equality_bins_before_crossing: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class Preparation:
    """All bins and source arrays, preserving input source order."""

    denominator: float
    rain: tuple[tuple[float, ...], ...]
    after_initial: tuple[tuple[float, ...], ...]
    excess: tuple[tuple[float, ...], ...]
    hydrographs: tuple[tuple[float, ...], ...]
    crossings: tuple[LossCrossing, ...]
    seconds: float
    continuing_allowance: Fraction


def _pervious_fraction(value: NumberInput, source_id: int) -> Fraction:
    """Validate a physical FI fraction before applying the existing loss operands."""
    if not 0 <= value.stored <= 1:
        message = f"source {source_id}: impervious fraction outside [0, 1]"
        raise UnsupportedNumericPath(message)
    return sub53(Fraction(1), fraction(value.stored))


def prepare(event: Event) -> Preparation:
    """Apply C06-C10 with separately rounded p53 operations and source ownership."""
    total = Fraction()
    for weight in event.weights:
        total = add53(total, fraction(weight.stored))
    denominator = store_rational(total)
    if denominator <= 0:
        message = "stored rainfall weight denominator nonpositive"
        raise UnsupportedNumericPath(message)
    duration = store_rational(mul53(fraction(event.h.stored), Fraction(3600)))
    if duration <= 0:
        message = "stored timestep duration nonpositive"
        raise UnsupportedNumericPath(message)
    reciprocal_duration = div53(Fraction(1), fraction(duration))
    allowance = mul53(fraction(event.cl.stored), fraction(event.h.stored))
    all_rain: list[tuple[float, ...]] = []
    all_post: list[tuple[float, ...]] = []
    all_excess: list[tuple[float, ...]] = []
    all_flows: list[tuple[float, ...]] = []
    crossings: list[LossCrossing] = []

    for source_index, (area, depth, impervious) in enumerate(
        zip(event.areas, event.depths, event.impervious, strict=True), 1
    ):
        flow_scale = mul53(mul53(Fraction(1000), fraction(area.stored)), reciprocal_duration)
        pervious = _pervious_fraction(impervious, source_index)
        remaining = mul53(pervious, fraction(event.il.stored))
        effective_allowance = mul53(allowance, pervious)
        crossed = False
        crossing_bin: int | None = None
        equality_bins: list[int] = []
        rain: list[float] = []
        post: list[float] = []
        excess: list[float] = []
        flow: list[float] = [0.0]
        for bin_index, weight in enumerate(event.weights, 1):
            amount = store_rational(
                mul53(div53(fraction(weight.stored), fraction(denominator)), fraction(depth.stored))
            )
            rain.append(amount)
            if crossed:
                after = amount
            else:
                remaining = sub53(remaining, fraction(amount))
                if remaining < 0:
                    crossing_bin = bin_index
                    crossed = True
                    after = store_rational(-remaining)
                else:
                    after = 0.0
                    if remaining == 0:
                        equality_bins.append(bin_index)
            post.append(after)
            excess_amount = store_rational(max(Fraction(), sub53(fraction(after), effective_allowance)))
            excess.append(excess_amount)
            flow.append(store_rational(mul53(fraction(excess_amount), flow_scale)))
        flow.extend(0.0 for _ in range(event.n - len(event.weights)))
        all_rain.append(tuple(rain))
        all_post.append(tuple(post))
        all_excess.append(tuple(excess))
        all_flows.append(tuple(flow))
        crossings.append(LossCrossing(source_index, crossing_bin, remaining, tuple(equality_bins)))
    return Preparation(
        denominator,
        tuple(all_rain),
        tuple(all_post),
        tuple(all_excess),
        tuple(all_flows),
        tuple(crossings),
        duration,
        allowance,
    )
