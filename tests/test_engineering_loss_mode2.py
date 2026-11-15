"""Independent default-engine IL/RoC controls; CMD original reference remains unadmitted."""

from __future__ import annotations

import math
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from runoff_routing.engine_execution import run_engine_project
from runoff_routing.engine_types import EngineSelection
from runoff_routing.integration import run_model
from runoff_routing.project_json import EmbeddedRun, Project, write_project
from runoff_routing.rorb_model import RunModel, from_json

EXAMPLE = Path(__file__).parents[1] / "examples" / "synthetic-run.json"


def _mode_two_model(*, initial: str = "5", coefficient: str = "0.5") -> RunModel:
    model = from_json(EXAMPLE.read_text(encoding="utf-8"))
    assert isinstance(model, RunModel)
    loss = replace(
        model.parameters.losses[0],
        initial_loss_mm=Decimal(initial),
        continuing=Decimal(coefficient),
    )
    return replace(model, parameters=replace(model.parameters, loss_model=2, losses=(loss,)))


def _project(path: Path, model: RunModel) -> Path:
    write_project(path, Project("engineering_ilroc", "explicit", EmbeddedRun(model), engine=EngineSelection()))
    return path


def test_default_engine_mode_two_full_horizon_and_physical_source_volume(tmp_path: Path) -> None:
    model = _mode_two_model()
    source = _project(tmp_path / "run.json", model)
    result = run_engine_project(source)
    assert result.status == "computed_unvalidated"
    assert result.effective_selection.engine == "python"
    assert result.native_parity_status == "not_assessed"
    assert result.native_raw_time_tokens == ()
    assert result.python_diagnostics is not None
    excess = result.python_diagnostics["rainfall_excess_mm"]
    assert excess == ((3.5, 4.0),)
    assert len(result.hydrographs) == 1
    assert len(result.hydrographs[0].discharge_m3_s) == 6
    assert result.physical_time_hours == ("0.0", "0.5", "1.0", "1.5", "2.0", "2.5")
    sources = result.python_diagnostics["source_hydrographs_m3_s"]
    assert isinstance(sources, tuple)
    assert math.fsum(sources[0]) * 1800 == pytest.approx(7500, abs=1e-8)
    assert result.hydrographs[0].discharge_m3_s == run_model(model).prints[0].discharge_m3_s


@pytest.mark.parametrize(
    ("initial", "coefficient", "expected"),
    [
        ("12", "0.5", (0.0, 4.0)),
        ("5", "0", (0.0, 0.0)),
        ("5", "1", (7.0, 8.0)),
        ("30", "0.7", (0.0, 0.0)),
    ],
)
def test_default_mode_two_coefficient_edges_and_equality(
    tmp_path: Path, initial: str, coefficient: str, expected: tuple[float, float]
) -> None:
    source = _project(tmp_path / "run.json", _mode_two_model(initial=initial, coefficient=coefficient))
    result = run_engine_project(source)
    assert result.status == "computed_unvalidated"
    assert result.python_diagnostics is not None
    assert result.python_diagnostics["rainfall_excess_mm"] == (expected,)


def test_default_mode_two_never_interprets_coefficient_as_continuing_rate(tmp_path: Path) -> None:
    model = _mode_two_model()
    source = _project(tmp_path / "mode2.json", model)
    mode_two = run_engine_project(source)
    mode_one = run_model(replace(model, parameters=replace(model.parameters, loss_model=1)))
    assert mode_two.python_diagnostics is not None
    assert mode_two.python_diagnostics["rainfall_excess_mm"] == ((3.5, 4.0),)
    assert mode_one.numerical.rainfall_excess_mm == ((6.75, 7.75),)
    assert mode_one.prints[0].discharge_m3_s != mode_two.hydrographs[0].discharge_m3_s


def test_default_mode_two_rejects_out_of_range_coefficient(tmp_path: Path) -> None:
    source = _project(tmp_path / "run.json", _mode_two_model(coefficient="1.01"))
    result = run_engine_project(source)
    assert result.status == "unsupported_feature"
    assert result.diagnostics[0].code == "unsupported_s2_profile"
    assert "Runoff coefficient" in result.diagnostics[0].message
    assert not result.hydrographs
