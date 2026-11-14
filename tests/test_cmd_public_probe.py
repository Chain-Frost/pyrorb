"""Engine-facing CMD regression admission and effective-time attribution controls.

Keep these checks independent of the numerical kernel and original CMD reports.
"""

from __future__ import annotations

import runpy
from dataclasses import replace
from pathlib import Path
from typing import Any, cast
from collections.abc import Callable

import pytest

from runoff_routing.engine_execution import run_engine_project
from runoff_routing.engine_types import EngineOutcome, EngineSelection
from runoff_routing.project_json import EmbeddedRun, Project, project_to_json, write_project
from runoff_routing.rorb_model import RunModel, from_json

ROOT = Path(__file__).parents[1]
Checker = Callable[[dict[str, Any], RunModel, EngineOutcome, str], str | None]


def _check() -> Checker:
    namespace = runpy.run_path(str(ROOT / "repo-scripts" / "cmd_public_probe.py"))
    return cast("Checker", namespace["_binding_error"])


def _example(tmp_path: Path) -> tuple[dict[str, Any], RunModel, EngineOutcome, str]:
    model = from_json((ROOT / "examples" / "synthetic-run.json").read_text(encoding="utf-8"))
    assert isinstance(model, RunModel)
    project = Project(
        "case_one",
        "explicit",
        EmbeddedRun(model),
        engine=EngineSelection.for_engine("python-cmd"),
    )
    text = project_to_json(project)
    path = tmp_path / "case.json"
    write_project(path, project)
    outcome = run_engine_project(path)
    assert outcome.status == "computed_unvalidated"
    case: dict[str, Any] = {
        "case_id": "case_one",
        "clock": {"row_count": model.storm.calculation_increments + 1, "timestep_hours": str(model.storm.timestep_hours)},
        "sites": [{"model_print_id": model.catchment.print_locations[0].identifier, "native_column_id": "Hyd001"}],
    }
    return case, model, outcome, text


def test_fresh_probe_accepts_matching_source_clock_and_single_terminal_site(tmp_path: Path) -> None:
    case, model, outcome, text = _example(tmp_path)
    assert _check()(case, model, outcome, text) is None


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("physical_time_hours", ()),
        ("physical_time_hours", ("0.5", "1.0", "1.5", "2.0", "2.5", "3.0")),
        ("project_id", "different"),
        ("event_id", "different"),
        ("model_sha256", "0" * 64),
        ("project_sha256", "0" * 64),
        ("requested_print_ids", ()),
        ("control_order", (7, 1)),
        ("implementation_revision", None),
        ("native_raw_time_tokens", ("0.5",)),
    ],
)
def test_fresh_probe_rejects_attribution_or_generated_axis_changes(
    tmp_path: Path, field: str, invalid: object
) -> None:
    case, model, outcome, text = _example(tmp_path)
    modified = replace(outcome, **{field: invalid})
    assert _check()(case, model, modified, text) is not None


def test_fresh_probe_rejects_wrong_registered_clock_and_print_mapping(tmp_path: Path) -> None:
    case, model, outcome, text = _example(tmp_path)
    case["clock"]["row_count"] += 1
    assert _check()(case, model, outcome, text) is not None
    case["clock"]["row_count"] -= 1
    case["clock"]["timestep_hours"] = "0.75"
    assert _check()(case, model, outcome, text) is not None
    case["clock"]["timestep_hours"] = str(model.storm.timestep_hours)
    case["sites"][0]["model_print_id"] = "other"
    assert _check()(case, model, outcome, text) is not None
