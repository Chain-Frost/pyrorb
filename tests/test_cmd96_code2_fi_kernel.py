"""Manufactured code-2/FI CMD kernel controls for upstream PyRomb PR #16.

The existing public S1 importer has not yet admitted the source-domain grammar.
These controls do not establish original CMD 6.44 output/physical-site parity.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from runoff_routing._cmd644.geometry import compute_geometry
from runoff_routing._cmd644.models import Control, Event, NumberInput
from runoff_routing._cmd644.precision import UnsupportedNumericPath, store
from runoff_routing._cmd644.preparation import prepare
from runoff_routing._cmd644.reporting import execute


def _number(value: float) -> NumberInput:
    return NumberInput(str(value), value, store(value))


def _event() -> Event:
    """Two ordered source reaches: code 1 then source-addition code 2."""
    return Event(
        "manufactured_pr16_code2_fi",
        "manufactured-not-a-native-source-hash",
        "{}",
        (Control(1, _number(1.0)), Control(2, _number(2.0)), Control(7, _number(0.0))),
        (_number(2.0), _number(3.0)),
        (_number(10.0), _number(20.0)),
        (_number(0.5), _number(0.2)),
        (_number(50.0), _number(50.0)),
        _number(0.5),
        _number(5.0),
        _number(1.0),
        _number(2.0),
        _number(0.5),
        4,
    )


def test_original_control_order_code_two_adds_second_source_then_routes() -> None:
    event = _event()
    geom = compute_geometry(event)
    assert event.source_count == event.reach_count == 2
    assert geom.distances == (3.0, 2.0)
    assert geom.mean_distance == pytest.approx(2.4, abs=1e-6)
    result = execute(event, "manufactured")
    assert len(result.network.reaches) == 2
    assert result.network.reaches[0].membership == (1,)
    assert result.network.reaches[1].membership == (1, 2)
    assert len(result.network.outlet) == event.n + 1
    assert result.network.outlet == result.network.reaches[-1].q
    assert result.network.outlet[0] == 0.0
    assert any(q > 0 for q in result.network.outlet[1:])


def test_impervious_fraction_changes_per_source_effective_loss_not_only_graphics() -> None:
    event = _event()
    prepared = prepare(event)
    assert prepared.rain[0] == (5.0, 5.0)
    assert prepared.rain[1] == (10.0, 10.0)
    assert prepared.excess[0] == pytest.approx((3.875, 4.875), rel=1e-6, abs=1e-6)
    assert prepared.excess[1] == pytest.approx((8.2, 9.8), rel=1e-6, abs=1e-6)
    assert len(prepared.hydrographs) == 2
    assert all(len(row) == event.n + 1 for row in prepared.hydrographs)
    physical_source_volume = sum(sum(series) for series in prepared.hydrographs) * prepared.seconds
    expected_source_volume = (2 * (3.875 + 4.875) + 3 * (8.2 + 9.8)) * 1000
    assert physical_source_volume == pytest.approx(expected_source_volume, abs=0.02)
    unmodified = replace(event, impervious=(_number(0.0), _number(0.0)))
    without_fi = prepare(unmodified)
    assert sum(map(sum, prepared.excess)) > sum(map(sum, without_fi.excess))
    assert execute(event, "manufactured").network.outlet != execute(unmodified, "manufactured").network.outlet


@pytest.mark.parametrize("invalid", [-0.2, 1.2])
def test_unphysical_per_source_impervious_fraction_rejected_before_routing(invalid: float) -> None:
    original = _event()
    event = replace(original, impervious=(original.impervious[0], _number(invalid)))
    with pytest.raises(UnsupportedNumericPath, match="impervious fraction outside"):
        prepare(event)


def test_code_two_cannot_start_without_existing_running_hydrograph() -> None:
    original = _event()
    event = replace(
        original,
        controls=(Control(2, _number(1.0)), Control(7, _number(0.0))),
        areas=(original.areas[0],),
        depths=(original.depths[0],),
        impervious=(original.impervious[0],),
    )
    with pytest.raises(UnsupportedNumericPath, match="code-2 source needs an existing running"):
        compute_geometry(event)
