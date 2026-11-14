"""Deterministic explicit-event batches for the default engineering-v1 Python engine.

Only validated event-independent catchment preparation is shared. This module
does not prepare generated rainfall, launch native RORB or claim CMD equivalence.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Literal

from .reach_routing import RoutingDomainError, RoutingNumericalError
from .single_storm import Losses, PreparedCatchment, Storm, StormResult, calculate_prepared_storm


@dataclass(frozen=True, slots=True)
class ExplicitEvent:
    """A named, already prepared DESIGN storm with independent per-event losses."""

    event_id: str
    storm: Storm
    losses: Losses

    def __post_init__(self) -> None:
        if (
            not self.event_id
            or self.event_id.strip() != self.event_id
            or any(ord(character) < 32 for character in self.event_id)
        ):
            message = "Event ID must be nonempty, trimmed and free of control characters."
            raise ValueError(message)


BatchStatus = Literal["computed_unvalidated", "invalid_input", "numerical_error"]


@dataclass(frozen=True, slots=True)
class BatchEventOutcome:
    """One explicit input always has one output, including a typed event failure."""

    event_id: str
    status: BatchStatus
    result: StormResult | None
    error_code: str | None = None
    message: str | None = None
    engine: Literal["python"] = "python"
    numerical_profile: Literal["engineering-v1"] = "engineering-v1"


def iter_explicit_events(prepared: PreparedCatchment, events: Iterable[ExplicitEvent]) -> Iterator[BatchEventOutcome]:
    """Stream one independent outcome per event in supplied order.

    A duplicate ID produces an explicit invalid-input record, never a silent
    overwrite. Event-specific routing and input failures do not affect later
    inputs; process-level interrupts and resource failures are not swallowed.
    """
    seen: set[str] = set()
    for event in events:
        identifier = event.event_id
        if identifier in seen:
            yield BatchEventOutcome(identifier, "invalid_input", None, "duplicate_event_id", "Duplicate event ID")
            continue
        seen.add(identifier)
        try:
            result = calculate_prepared_storm(prepared, event.storm, losses=event.losses)
        except RoutingNumericalError as exc:
            yield BatchEventOutcome(identifier, "numerical_error", None, "routing_numerical", str(exc))
        except RoutingDomainError as exc:
            yield BatchEventOutcome(identifier, "invalid_input", None, "event_domain", str(exc))
        except ArithmeticError as exc:
            yield BatchEventOutcome(identifier, "numerical_error", None, "arithmetic", str(exc))
        else:
            yield BatchEventOutcome(identifier, "computed_unvalidated", result)


def run_explicit_batch(prepared: PreparedCatchment, events: Iterable[ExplicitEvent]) -> tuple[BatchEventOutcome, ...]:
    """Materialise ordered results when the caller wishes to retain all events.

    For larger event populations, consume iter_explicit_events incrementally
    to avoid keeping all hydrographs in memory at once.
    """
    return tuple(iter_explicit_events(prepared, events))
