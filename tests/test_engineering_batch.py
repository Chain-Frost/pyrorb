"""Explicit batch API and state isolation against the readable single-event path."""

from __future__ import annotations

import math
from dataclasses import FrozenInstanceError

import pytest

from runoff_routing.engineering_batch import ExplicitEvent, iter_explicit_events, run_explicit_batch
from runoff_routing.reach_routing import RoutingDomainError
from runoff_routing.single_storm import (
    Catchment,
    Control,
    Losses,
    Storm,
    calculate_storm,
    prepare_catchment,
)


def _branched_catchment() -> Catchment:
    return Catchment(
        (Control(1, 2.0), Control(3), Control(1, 4.0), Control(4), Control(5, 3.0), Control(7)),
        (1.0, 3.0),
    )


def _event(
    name: str,
    depths: tuple[float, float] = (5.0, 7.0),
    *,
    timestep_hours: float = 0.1,
    calculation_increments: int = 80,
    losses: Losses = Losses(0.5, 0.2),
) -> ExplicitEvent:
    return ExplicitEvent(
        name,
        Storm(timestep_hours, calculation_increments, (40.0, 60.0), depths),
        losses,
    )


def test_preparation_is_frozen_and_event_independent() -> None:
    prepared = prepare_catchment(_branched_catchment(), kc=0.4, m=0.8)
    assert prepared.route_factors == pytest.approx((2 / 6.5, 4 / 6.5, 3 / 6.5))
    assert prepared.reach_coefficients == pytest.approx(tuple(0.4 * factor for factor in prepared.route_factors))
    field = "kc"
    with pytest.raises(FrozenInstanceError):
        setattr(prepared, field, 0.2)


def test_batch_matches_single_run_with_no_cross_event_state() -> None:
    catchment = _branched_catchment()
    prepared = prepare_catchment(catchment, kc=0.4, m=0.8)
    events = (
        _event("A"),
        _event("dry", (0.0, 0.0)),
        _event("B", (6.0, 8.0), timestep_hours=0.05, calculation_increments=120),
        _event("A-repeat"),
        _event("C", (3.0, 4.0), losses=Losses(2.0, 0.0)),
    )
    first = run_explicit_batch(prepared, events)
    second = run_explicit_batch(prepared, events)
    assert first == second
    assert tuple(item.event_id for item in first) == tuple(event.event_id for event in events)
    assert all(item.status == "computed_unvalidated" for item in first)
    for event, entry in zip(events, first, strict=True):
        reference = calculate_storm(catchment, event.storm, losses=event.losses, kc=0.4, m=0.8)
        assert entry.result == reference
        assert entry.result is not None
        assert len(entry.result.outlets_m3_s[0]) == event.storm.calculation_increments + 1
        assert all(math.isfinite(value) and value >= 0.0 for value in entry.result.outlets_m3_s[0])
    assert first[0].result == first[3].result
    dry_result = first[1].result
    assert dry_result is not None
    assert all(value == 0.0 for value in dry_result.outlets_m3_s[0])


def test_shuffled_execution_matches_each_event_identity() -> None:
    prepared = prepare_catchment(_branched_catchment(), kc=0.5, m=1.0)
    events = tuple(_event(f"ev-{number}", (float(number + 1), 4.0)) for number in range(8))
    ordered = run_explicit_batch(prepared, events)
    shuffled = run_explicit_batch(prepared, tuple(reversed(events)))
    assert tuple(item.event_id for item in shuffled) == tuple(reversed(tuple(item.event_id for item in ordered)))
    assert {item.event_id: item for item in ordered} == {item.event_id: item for item in shuffled}


def test_failing_events_do_not_change_adjacent_or_repeated_results() -> None:
    prepared = prepare_catchment(_branched_catchment(), kc=0.4, m=1.0)
    good = _event("good")
    invalid = _event("bad-horizon", calculation_increments=1)
    invalid_loss = _event("bad-loss", losses=Losses(-1.0, 0.0))
    batch = run_explicit_batch(prepared, (invalid, good, invalid_loss, _event("good-again")))
    alone = run_explicit_batch(prepared, (good,))[0]
    assert tuple(item.status for item in batch) == (
        "invalid_input",
        "computed_unvalidated",
        "invalid_input",
        "computed_unvalidated",
    )
    assert batch[0].error_code == "event_domain"
    assert batch[2].error_code == "event_domain"
    assert batch[1].result == alone.result
    assert batch[3].result == alone.result
    assert all(item.result is None for item in (batch[0], batch[2]))


def test_numerical_failure_has_separate_status_and_no_substituted_output() -> None:
    prepared = prepare_catchment(Catchment((Control(1, 3.0), Control(7)), (1.0,)), kc=0.1, m=1.0)
    failure = ExplicitEvent("long-step", Storm(10.0, 5, (100.0,), (3.6,)), Losses(0.0, 0.0))
    good = ExplicitEvent("short-step", Storm(0.1, 8, (100.0,), (3.6,)), Losses(0.0, 0.0))
    outcomes = run_explicit_batch(prepared, (good, failure, good))
    assert outcomes[0].status == "computed_unvalidated"
    assert outcomes[1].status == "numerical_error"
    assert outcomes[1].error_code == "routing_numerical"
    assert outcomes[1].result is None
    # The last duplicate is deliberately flagged instead of silently overwriting its first result.
    assert outcomes[2].status == "invalid_input"
    assert outcomes[2].error_code == "duplicate_event_id"
    after = run_explicit_batch(prepared, (good,))
    assert after[0] == outcomes[0]


def test_streaming_preserves_order_and_error_accounting() -> None:
    prepared = prepare_catchment(_branched_catchment(), kc=0.0, m=1.0)
    events = (_event(f"stream-{number}", (0.0, float(number))) for number in range(30))
    streamed = tuple(iter_explicit_events(prepared, events))
    assert len(streamed) == 30
    assert tuple(item.event_id for item in streamed) == tuple(f"stream-{number}" for number in range(30))
    assert all(item.status == "computed_unvalidated" for item in streamed)
    assert all(item.engine == "python" for item in streamed)
    assert all(item.numerical_profile == "engineering-v1" for item in streamed)


def test_event_identifier_and_prepared_domain_are_fail_closed() -> None:
    with pytest.raises(ValueError, match="Event ID"):
        _event(" leading")
    with pytest.raises(ValueError, match="Event ID"):
        _event("")
    with pytest.raises(RoutingDomainError, match="positive"):
        prepare_catchment(_branched_catchment(), kc=0.4, m=0.0)
    extreme = Catchment(
        (Control(1, 1.0), Control(3), Control(1, 1000.0), Control(4), Control(7)),
        (100.0, 1.0),
    )
    with pytest.raises(RoutingDomainError, match="coefficient"):
        prepare_catchment(extreme, kc=1e308, m=0.8)


def test_empty_event_batch_is_explicitly_empty() -> None:
    prepared = prepare_catchment(_branched_catchment(), kc=1.0, m=1.0)
    assert run_explicit_batch(prepared, ()) == ()
