"""Independent linear controls and existing typed CMD boundary checks for issue #92.

These controls are manufactured/analytical, not original CMD observations.
"""

from __future__ import annotations

import math
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from runoff_routing._cmd644.geometry import ReachGeometry
from runoff_routing._cmd644.routing import route_reach as route_cmd_reach
from runoff_routing.cmd_engine import adapt_event
from runoff_routing.project_json import EmbeddedRun, Project, load_project, write_project
from runoff_routing.reach_routing import route_reach as route_default_reach
from runoff_routing.rorb_model import Reach, RoutingValue, RunModel, from_json

EXAMPLE = Path(__file__).parents[1] / "examples" / "synthetic-run.json"


def _model() -> RunModel:
    model = from_json(EXAMPLE.read_text(encoding="utf-8"))
    assert isinstance(model, RunModel)
    return model


def test_cmd_linear_m_one_has_complete_analytic_discrete_pulse() -> None:
    """For k=5h and h=0.5h, the linear reservoir ratio is 19/21."""
    geometry = ReachGeometry(1, 1.0, 1.0, 5.0, 18000.0)
    incoming = (0.0, 1.0, 0.0, 0.0)
    result = route_cmd_reach(incoming, geometry, 1800.0, (1,), exponent=1.0, hours=0.5)
    expected = (0.0, 1 / 21, 40 / 441, 760 / 9261)
    assert result.is_linear
    assert result.steps == ()
    assert len(result.q) == len(result.s) == len(incoming)
    assert result.q == pytest.approx(expected, rel=1e-6, abs=1e-8)
    assert result.s[1] == pytest.approx(result.q[1] * 18000, rel=1e-6)
    assert result.processed_peak == 1.0


def test_default_linear_m_one_has_independent_analytic_pulse() -> None:
    incoming = (0.0, 1.0, 0.0, 0.0)
    result = route_default_reach(incoming, coefficient_k=5.0, exponent_m=1.0, time_step_hours=0.5)
    assert result == pytest.approx((0.0, 1 / 21, 40 / 441, 760 / 9261), rel=1e-10, abs=1e-12)


@pytest.mark.parametrize("exponent", ["0.6", "1.2"])
def test_positive_nonunit_m_is_preserved_at_typed_cmd_boundary(tmp_path: Path, exponent: str) -> None:
    original = _model()
    routing = replace(original.parameters.routing[0], m=Decimal(exponent))
    model = replace(original, parameters=replace(original.parameters, routing=(routing,)))
    source = tmp_path / "event.json"
    write_project(source, Project("m_bound", "explicit", EmbeddedRun(model)))
    event = adapt_event(load_project(source))
    assert event.m.lexeme == exponent
    assert event.m.stored == float(exponent)
    # Typed source admission is distinct from executing and qualifying native CMD m>1.


@pytest.mark.parametrize("length", [Decimal(0), Decimal(-1)])
def test_nonpositive_reaches_rejected_by_s1_without_guessing_native_outcome(length: Decimal) -> None:
    with pytest.raises(ValueError, match="positive"):
        Reach("bad", length)


def test_zero_m_is_rejected_at_typed_domain_not_silently_routed() -> None:
    with pytest.raises(ValueError, match="positive"):
        RoutingValue(1, Decimal(5), Decimal(0))


def test_default_zero_storage_is_not_equivalent_to_zero_exponent() -> None:
    incoming = (0.0, 1.0, 0.5, 0.0)
    assert route_default_reach(incoming, coefficient_k=0.0, exponent_m=0.8, time_step_hours=0.5) == incoming
    assert all(math.isfinite(v) for v in incoming)
