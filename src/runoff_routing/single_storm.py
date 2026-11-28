"""Bounded, independent RORB-style single-storm calculation.

Supports explicit DESIGN storms, one uniform pervious ISA, IL/CL or IL/RoC, natural
reaches and the stack control-vector subset 1/3/4/5/7. No native process,
I/O, GIS, fitted constants or inferred print-site identities are involved.
The first output sample is at t=0; rainfall in a bin enters at its END sample.
The time/phase and independently selected loss-crossing rules are not CMD parity claims.
"""

import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from runoff_routing.reach_routing import RoutingDomainError, RoutingNumericalError, route_reach
from runoff_routing.rorb_model import PatternBasis

ControlCode = Literal[1, 2, 3, 4, 5, 7]


@dataclass(frozen=True, slots=True)
class Control:
    """Route/stack/print operation in original computational order."""

    code: ControlCode
    reach_length_km: float = 0.0


@dataclass(frozen=True, slots=True)
class Storm:
    """Single explicit, uniform temporal pattern; depths are per subarea."""

    timestep_hours: float
    calculation_increments: int
    percentages: tuple[float, ...]
    depths_mm: tuple[float, ...]
    pattern_basis: PatternBasis = PatternBasis.PERCENT_OF_DEPTH
    preburst_bins: int = 0


@dataclass(frozen=True, slots=True)
class Losses:
    initial_mm: float
    continuing_mm_h: float
    runoff_coefficient: float | None = None


@dataclass(frozen=True, slots=True)
class Catchment:
    """Computational vector, not graphical node coordinates."""

    controls: tuple[Control, ...]
    areas_km2: tuple[float, ...]
    impervious_fractions: tuple[float, ...] = ()


@dataclass(frozen=True, slots=True)
class StormResult:
    """Pure calculation output, with no implied native numeric equivalence."""

    outlets_m3_s: tuple[tuple[float, ...], ...]
    rainfall_excess_mm: tuple[tuple[float, ...], ...]
    source_hydrographs_m3_s: tuple[tuple[float, ...], ...]
    average_distance_km: float
    route_factors: tuple[float, ...]
    dt_hours: float


@dataclass(frozen=True, slots=True)
class PreparedCatchment:
    """Only immutable event-independent geometry, ordering and coefficients.

    Rainfall, losses, source, routing, branch stack and output state are
    recomputed for every event. Construct through prepare_catchment.
    """

    catchment: Catchment
    kc: float
    m: float
    average_distance_km: float
    route_factors: tuple[float, ...]
    reach_coefficients: tuple[float, ...]


def _check_finite_nonnegative(value: float, label: str) -> None:
    if not math.isfinite(value) or value < 0:
        message = f"{label} must be finite and nonnegative."
        raise RoutingDomainError(message)


def _check_catchment(catchment: Catchment) -> None:
    if not catchment.areas_km2:
        message = "At least one subarea is required."
        raise RoutingDomainError(message)
    for area in catchment.areas_km2:
        _check_finite_nonnegative(area, "Subarea area")
    if not all(area > 0 for area in catchment.areas_km2):
        message = "All subarea areas must be positive."
        raise RoutingDomainError(message)
    if catchment.impervious_fractions and len(catchment.impervious_fractions) != len(catchment.areas_km2):
        message = "Every source needs one ordered impervious fraction."
        raise RoutingDomainError(message)
    if any(not math.isfinite(fi) or not 0 <= fi <= 1 for fi in catchment.impervious_fractions):
        message = "Impervious fractions must be finite values in [0, 1]."
        raise RoutingDomainError(message)
    if not catchment.controls or catchment.controls[-1].code != 7:
        message = "The model must terminate at a printed outlet."
        raise RoutingDomainError(message)
    for command in catchment.controls:
        if command.code not in {1, 2, 3, 4, 5, 7}:
            message = f"Unsupported control code: {command.code}."
            raise RoutingDomainError(message)
        _check_finite_nonnegative(command.reach_length_km, "Reach length")
        if command.code not in {1, 2, 5} and command.reach_length_km != 0:
            message = "Only control codes 1, 2 and 5 may specify reach length."
            raise RoutingDomainError(message)


def _distance_analysis(catchment: Catchment) -> tuple[float, tuple[float, ...]]:  # noqa: C901 -- stack machine
    """Area-weighted final-outlet paths; kr=length/dav for natural reaches."""
    _check_catchment(catchment)
    running: dict[int, float] | None = None
    stack: list[dict[int, float]] = []
    source_index = 0
    reaches: list[float] = []
    for command in catchment.controls:
        match command.code:
            case 1 | 2:
                if source_index >= len(catchment.areas_km2):
                    message = "More source operations than subarea areas."
                    raise RoutingDomainError(message)
                if command.code == 2 and running is None:
                    message = "Code 2 requires an existing running branch."
                    raise RoutingDomainError(message)
                running = (
                    {index: distance + command.reach_length_km for index, distance in running.items()}
                    if running is not None
                    else {}
                )
                running[source_index] = command.reach_length_km
                source_index += 1
                reaches.append(command.reach_length_km)
            case 3:
                if running is None:
                    message = "Cannot store an uninitialised running hydrograph."
                    raise RoutingDomainError(message)
                stack.append(dict(running))
                running = None
            case 4:
                if running is None or not stack:
                    message = "Confluence has no running/stored hydrographs."
                    raise RoutingDomainError(message)
                previous = stack.pop()
                if previous.keys() & running.keys():
                    message = "A subarea would be counted twice at a confluence."
                    raise RoutingDomainError(message)
                running = previous | running
            case 5:
                if running is None:
                    message = "Cannot route an uninitialised hydrograph."
                    raise RoutingDomainError(message)
                running = {index: distance + command.reach_length_km for index, distance in running.items()}
                reaches.append(command.reach_length_km)
            case 7:
                if running is None:
                    message = "Cannot print an uninitialised hydrograph."
                    raise RoutingDomainError(message)
    if source_index != len(catchment.areas_km2) or stack:
        message = "Control vector does not consume each source exactly once or leaves stored flows."
        raise RoutingDomainError(message)
    if running is None or set(running) != set(range(source_index)):
        message = "Final printed outlet must contain each subarea once."
        raise RoutingDomainError(message)
    total_area = math.fsum(catchment.areas_km2)
    dav = math.fsum(area * running[index] for index, area in enumerate(catchment.areas_km2)) / total_area
    if not math.isfinite(dav) or dav <= 0:
        message = "Average flow distance must be finite and positive."
        raise RoutingDomainError(message)
    return dav, tuple(length / dav for length in reaches)


def distance_analysis(catchment: Catchment) -> tuple[float, tuple[float, ...]]:
    """Expose the independently testable area-weighted distance factors."""
    return _distance_analysis(catchment)


def rainfall_excess(
    rainfall_mm: Sequence[float], *, losses: Losses, timestep_hours: float, impervious_fraction: float = 0.0
) -> tuple[float, ...]:
    """Apply distinct CMD-referenced IL/CL or IL/RoC pervious loss rules.

    For IL/CL, charge the full CL*dt allowance after IL is exceeded,
    including the crossing bin. For IL/RoC, multiply rainfall after IL by
    the dimensionless coefficient, without a continuing rate.
    At exact IL equality no runoff occurs. IL persists over dry bins.
    """
    _check_finite_nonnegative(losses.initial_mm, "Initial loss")
    _check_finite_nonnegative(losses.continuing_mm_h, "Continuing loss")
    if not math.isfinite(impervious_fraction) or not 0 <= impervious_fraction <= 1:
        message = "Impervious fraction must be between 0 and 1."
        raise RoutingDomainError(message)
    if losses.runoff_coefficient is not None:
        coefficient = losses.runoff_coefficient
        if not math.isfinite(coefficient) or not 0.0 <= coefficient <= 1.0 or losses.continuing_mm_h != 0:
            message = "IL/RoC needs a fractional runoff coefficient and no continuing loss rate."
            raise RoutingDomainError(message)
    if not math.isfinite(timestep_hours) or timestep_hours <= 0:
        message = "Timestep must be finite and positive."
        raise RoutingDomainError(message)
    pervious = 1.0 - impervious_fraction
    continuing_per_bin = losses.continuing_mm_h * timestep_hours * pervious
    if not math.isfinite(continuing_per_bin):
        message = "Continuing loss per increment overflowed."
        raise RoutingDomainError(message)
    initial_remaining = losses.initial_mm * pervious
    excess: list[float] = []
    for rainfall in rainfall_mm:
        _check_finite_nonnegative(rainfall, "Rainfall")
        consumed = min(initial_remaining, rainfall)
        initial_remaining -= consumed
        post_initial_rain = rainfall - consumed
        if post_initial_rain <= 0.0:
            excess.append(0.0)
        elif losses.runoff_coefficient is not None:
            excess.append(post_initial_rain * losses.runoff_coefficient)
        else:
            # Full-bin mode-1 CL after IL exhaustion; no allowance carry-over.
            excess.append(max(0.0, post_initial_rain - continuing_per_bin))
    return tuple(excess)


def prepare_catchment(catchment: Catchment, *, kc: float, m: float) -> PreparedCatchment:
    """Validate and compute event-independent natural-reach coefficients once."""
    _check_finite_nonnegative(kc, "kc")
    if not math.isfinite(m) or m <= 0:
        message = "m must be finite and positive."
        raise RoutingDomainError(message)
    dav, factors = _distance_analysis(catchment)
    coefficients = tuple(kc * factor for factor in factors)
    if any(not math.isfinite(value) or value < 0.0 for value in coefficients):
        message = "Prepared reach coefficient overflowed or became negative."
        raise RoutingDomainError(message)
    return PreparedCatchment(catchment, kc, m, dav, factors, coefficients)


def calculate_storm(catchment: Catchment, storm: Storm, *, losses: Losses, kc: float, m: float) -> StormResult:
    """Readable single-event path; perform fresh preparation and fresh routing."""
    return calculate_prepared_storm(prepare_catchment(catchment, kc=kc, m=m), storm, losses=losses)


def _validate_temporal_basis(storm: Storm, total_percent: float) -> None:
    """Preserve the combined-storm split even when ratios use a shared denominator."""
    if type(storm.preburst_bins) is not int:
        message = "Pre-burst split must be an integer."
        raise RoutingDomainError(message)
    if storm.pattern_basis == "combined_preburst_percent":
        split = storm.preburst_bins
        if not 0 < split < len(storm.percentages):
            message = "Combined pre-burst requires a positive prefix and a separate burst."
            raise RoutingDomainError(message)
        prefix = math.fsum(storm.percentages[:split])
        burst = math.fsum(storm.percentages[split:])
        # S1 checks the inclusive Decimal bounds exactly. Permit one adjacent
        # binary64 value at each bound for conversion and fsum roundoff only.
        # This is not an expansion of the source model's tolerance.
        lower = math.nextafter(99.95, -math.inf)
        upper = math.nextafter(100.05, math.inf)
        if prefix <= 0 or not lower <= burst <= upper:
            message = "Combined pre-burst requires positive weights and a full 100% burst segment."
            raise RoutingDomainError(message)
        return
    if storm.preburst_bins != 0:
        message = "Only a combined pre-burst basis may carry a pre-burst split."
        raise RoutingDomainError(message)
    if storm.pattern_basis == "percent_of_depth":
        if not math.isclose(total_percent, 100, rel_tol=0, abs_tol=0.01):
            message = "Temporal pattern percentages must total 100 within printed precision."
            raise RoutingDomainError(message)
    elif storm.pattern_basis != "relative_weights":
        message = "Unsupported temporal basis."
        raise RoutingDomainError(message)


def calculate_prepared_storm(  # noqa: C901 -- ordered source/control stack
    prepared: PreparedCatchment, storm: Storm, *, losses: Losses
) -> StormResult:
    """Execute a supported event with immutable geometry and fresh local state.

    Q[0]=0, and rainfall-bin source enters at its end sample. No rainfall,
    loss or routing state is cached between events. This is also the readable
    reference path for engineering-v1: no acceleration or fast-math.
    """
    catchment = prepared.catchment
    m = prepared.m
    dav, factors = prepared.average_distance_km, prepared.route_factors
    coefficients = prepared.reach_coefficients
    if not math.isfinite(storm.timestep_hours) or storm.timestep_hours <= 0:
        message = "Timestep must be finite and positive."
        raise RoutingDomainError(message)
    if (
        type(storm.calculation_increments) is not int
        or storm.calculation_increments < len(storm.percentages)
        or not 0 < storm.calculation_increments <= 1_000_000
    ):
        message = "Calculation horizon must cover all rainfall bins."
        raise RoutingDomainError(message)
    if len(storm.depths_mm) != len(catchment.areas_km2):
        message = "Each subarea must have one rainfall depth."
        raise RoutingDomainError(message)
    for depth in storm.depths_mm:
        _check_finite_nonnegative(depth, "Rainfall depth")
    for percent in storm.percentages:
        _check_finite_nonnegative(percent, "Temporal percentage")
    try:
        total_percent = math.fsum(storm.percentages)
    except OverflowError as exc:
        message = "Temporal weights must have a finite positive denominator."
        raise RoutingDomainError(message) from exc
    if not math.isfinite(total_percent) or total_percent <= 0:
        message = "Temporal weights must have a finite positive denominator."
        raise RoutingDomainError(message)
    _validate_temporal_basis(storm, total_percent)
    # Ordinary percent-of-depth storms keep their original arithmetic. Relative
    # weights and combined pre-burst weights use the same scaled-ratio calculation.
    # For a combined storm, depth is the total event depth; carry losses through
    # the preceding bins into the full burst, without changing source tokens.
    relative_shares: tuple[float, ...] = ()
    if storm.pattern_basis in ("relative_weights", "combined_preburst_percent"):
        maximum = max(storm.percentages)
        scaled = tuple(value / maximum for value in storm.percentages)
        scaled_total = math.fsum(scaled)
        relative_shares = tuple(value / scaled_total for value in scaled)
        if any(value > 0 and share == 0 for value, share in zip(storm.percentages, relative_shares, strict=True)):
            message = "Relative storm weight ratios underflow to zero."
            raise RoutingDomainError(message)
    rainfalls = tuple(
        (
            tuple(share * depth for share in relative_shares)
            if relative_shares
            else tuple(percent * depth / total_percent for percent in storm.percentages)
        )
        for depth in storm.depths_mm
    )
    if relative_shares and any(
        depth > 0 and share > 0 and rainfall == 0
        for depth, bins in zip(storm.depths_mm, rainfalls, strict=True)
        for share, rainfall in zip(relative_shares, bins, strict=True)
    ):
        message = "Relative storm depth contribution underflows to zero."
        raise RoutingDomainError(message)
    fractions = catchment.impervious_fractions or (0.0,) * len(catchment.areas_km2)
    excesses = tuple(
        rainfall_excess(rainfall, losses=losses, timestep_hours=storm.timestep_hours, impervious_fraction=fi)
        for rainfall, fi in zip(rainfalls, fractions, strict=True)
    )
    count = storm.calculation_increments + 1
    sources = tuple(
        tuple(
            [0.0]
            + [depth * area / (3.6 * storm.timestep_hours) for depth in excess]
            + [0.0] * (count - len(excess) - 1)
        )
        for area, excess in zip(catchment.areas_km2, excesses, strict=True)
    )
    routed: tuple[float, ...] | None = None
    stack: list[tuple[float, ...]] = []
    outputs: list[tuple[float, ...]] = []
    factor_index = 0
    source_index = 0
    for command in catchment.controls:
        match command.code:
            case 1 | 2:
                if command.code == 2 and routed is None:
                    message = "Code 2 requires an existing running hydrograph."
                    raise RoutingDomainError(message)
                incoming = sources[source_index]
                if routed is not None:
                    incoming = tuple(a + b for a, b in zip(routed, incoming, strict=True))
                    if any(not math.isfinite(value) for value in incoming):
                        message = "Source-addition discharge overflowed."
                        raise RoutingNumericalError(message)
                routed = route_reach(
                    incoming,
                    coefficient_k=coefficients[factor_index],
                    exponent_m=m,
                    time_step_hours=storm.timestep_hours,
                )
                source_index += 1
                factor_index += 1
            case 3:
                if routed is None:
                    message = "No running hydrograph to store."
                    raise RoutingDomainError(message)
                stack.append(routed)
                routed = None
            case 4:
                if routed is None or not stack:
                    message = "No stored hydrograph to join."
                    raise RoutingDomainError(message)
                previous = stack.pop()
                routed = tuple(a + b for a, b in zip(previous, routed, strict=True))
                if any(not math.isfinite(value) for value in routed):
                    message = "Confluence discharge overflowed."
                    raise RoutingNumericalError(message)
            case 5:
                if routed is None:
                    message = "No running hydrograph to route."
                    raise RoutingDomainError(message)
                routed = route_reach(
                    routed,
                    coefficient_k=coefficients[factor_index],
                    exponent_m=m,
                    time_step_hours=storm.timestep_hours,
                )
                factor_index += 1
            case 7:
                if routed is None:
                    message = "No running hydrograph to print."
                    raise RoutingDomainError(message)
                outputs.append(routed)
    return StormResult(tuple(outputs), excesses, sources, dav, factors, storm.timestep_hours)
