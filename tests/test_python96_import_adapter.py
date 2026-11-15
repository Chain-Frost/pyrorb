"""Imported ordinary PyRomb graphical source through independent engineering-v1.

The historical CATG bytes are original; the authored percent-of-depth storm
is NOT an authenticated native CMD event or a primary PR16 export.
"""

from __future__ import annotations

import hashlib
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from typing import cast

import pytest

from runoff_routing.engine_execution import run_engine_project
from runoff_routing.engine_types import EngineSelection
from runoff_routing.integration import prepare_run_model, run_model
from runoff_routing.project_batch import ProjectEvent, run_project_events
from runoff_routing.project_json import EmbeddedRun, LegacyRunFiles, Project, SourceFile, write_project
from runoff_routing.rorb_codec import parse_catg, serialize_cmd_par, serialize_design_stm
from runoff_routing.rorb_model import RunModel, from_json

ROOT = Path(__file__).parents[1]
ORIGINAL_SHA = "2ad4663ddeaacdfd4bba4b199a29d3eed7bcb6d9f096ff62f6d9d107330bd247"
ORIGINAL_CATG = ROOT / "tests" / "fixtures" / "regression-v1" / "native-cmd" / "objects" / f"{ORIGINAL_SHA}.catg"
SELECTION = EngineSelection.for_engine("python")


def _imported_model(*, runoff_coefficient: bool = False) -> RunModel:
    original = ORIGINAL_CATG.read_bytes()
    assert len(original) == 2913
    assert hashlib.sha256(original).hexdigest() == ORIGINAL_SHA
    catchment = parse_catg(original).model
    assert catchment.reach_mode == "explicit_reach_types"
    example = from_json((ROOT / "examples" / "synthetic-run.json").read_text(encoding="utf-8"))
    assert isinstance(example, RunModel)
    storm = replace(
        example.storm,
        title="Authored independent Python adapter control, not original CMD storm",
        timestep_hours=Decimal("0.25"),
        calculation_increments=40,
        subarea_ids=tuple(area.identifier for area in catchment.subareas),
        depths_mm=(Decimal(20),) * len(catchment.subareas),
    )
    losses = example.parameters.losses
    parameters = replace(
        example.parameters,
        routing=(replace(example.parameters.routing[0], m=Decimal(1)),),
        loss_model=2 if runoff_coefficient else 1,
        losses=(replace(losses[0], continuing=Decimal("0.6")),) if runoff_coefficient else losses,
    )
    return RunModel(parameters, catchment, storm)


def _project(path: Path, model: RunModel) -> Path:
    write_project(path, Project("independent_import", "explicit", EmbeddedRun(model), engine=SELECTION))
    return path


@pytest.mark.parametrize("runoff_coefficient", [False, True])
def test_imported_code_two_fi_runs_independent_project_and_prepared_api(
    tmp_path: Path, runoff_coefficient: bool
) -> None:
    model = _imported_model(runoff_coefficient=runoff_coefficient)
    source = _project(tmp_path / "import.json", model)
    outcome = run_engine_project(source)
    assert outcome.status == "computed_unvalidated", outcome.diagnostics
    assert outcome.stored_selection == outcome.effective_selection == SELECTION
    assert tuple(step.code for step in model.catchment.controls) == (1, 3, 1, 4, 2, 3, 1, 2, 4, 5, 2, 7)
    assert len(model.catchment.subareas) == 6
    assert len(model.catchment.reaches) == 7
    assert tuple(area.impervious_fraction for area in model.catchment.subareas) == (
        Decimal(0),
        Decimal("0.5"),
        Decimal("0.2"),
        Decimal(0),
        Decimal(0),
        Decimal(0),
    )
    assert len(outcome.hydrographs) == 1
    assert len(outcome.hydrographs[0].discharge_m3_s) == 41
    assert len(outcome.physical_time_hours) == 41
    assert outcome.requested_print_ids == tuple(item.identifier for item in model.catchment.print_locations)
    assert outcome.native_raw_time_tokens == ()
    assert outcome.native_parity_status == "not_assessed"
    direct = run_model(model)
    prepared = run_model(model, prepared=prepare_run_model(model))
    assert direct == prepared
    assert outcome.hydrographs[0].discharge_m3_s == direct.prints[0].discharge_m3_s
    assert outcome.python_diagnostics is not None
    excesses = cast("tuple[tuple[float, ...], ...]", outcome.python_diagnostics["rainfall_excess_mm"])
    assert len(excesses) == 6
    assert excesses[1] != excesses[0]
    no_fi = replace(
        model.catchment,
        subareas=tuple(replace(area, impervious_fraction=Decimal(0)) for area in model.catchment.subareas),
    )
    assert run_model(replace(model, catchment=no_fi)).numerical.rainfall_excess_mm != excesses


def test_fileback_catg_import_matches_explicit_embedded_python(tmp_path: Path) -> None:
    model = _imported_model()
    embedded = _project(tmp_path / "embedded.json", model)
    names = ("model.par", "model.catg", "model.stm")
    objects = (serialize_cmd_par(model.parameters), ORIGINAL_CATG.read_bytes(), serialize_design_stm(model.storm))
    sources: list[SourceFile] = []
    for name, raw in zip(names, objects, strict=True):
        (tmp_path / name).write_bytes(raw)
        sources.append(SourceFile(name, hashlib.sha256(raw).hexdigest()))
    path = tmp_path / "fileback.json"
    write_project(
        path,
        Project(
            "independent_fileback",
            "legacy-rorb",
            LegacyRunFiles(sources[0], sources[1], sources[2]),
            engine=SELECTION,
        ),
    )
    actual, expected = run_engine_project(path), run_engine_project(embedded)
    assert actual.status == expected.status == "computed_unvalidated", actual.diagnostics
    assert actual.effective_selection == expected.effective_selection == SELECTION
    assert actual.model_sha256 == expected.model_sha256
    assert actual.hydrographs == expected.hydrographs
    assert actual.physical_time_hours == expected.physical_time_hours
    assert (names[1], ORIGINAL_SHA) in actual.source_file_hashes
    assert not expected.source_file_hashes


def test_imported_code_two_fi_event_batch_keeps_fresh_state_and_failures(tmp_path: Path) -> None:
    project = _project(tmp_path / "batch.json", _imported_model())
    requests = (
        ProjectEvent("before"),
        ProjectEvent("bad", storm={"calculation_increments": 1}),
        ProjectEvent("after"),
    )
    report = run_project_events(project, requests, selection=SELECTION)
    assert [item.status for item in report.outcomes] == [
        "computed_unvalidated",
        "invalid_input",
        "computed_unvalidated",
    ]
    first, invalid, last = report.outcomes
    assert first.effective_selection == invalid.effective_selection == last.effective_selection == SELECTION
    assert first.model_sha256 == last.model_sha256
    assert first.hydrographs == last.hydrographs
    assert first.python_diagnostics == last.python_diagnostics
    assert first.hydrographs == run_engine_project(project).hydrographs
    assert not invalid.hydrographs


def test_relative_weights_are_explicit_and_not_substituted_for_percentages(tmp_path: Path) -> None:
    model = _imported_model()
    relative = replace(model.storm, pattern_basis="relative_weights", percentages=(Decimal(3), Decimal(1)))
    percentages = replace(model.storm, pattern_basis="percent_of_depth", percentages=(Decimal(75), Decimal(25)))
    relative_project = _project(tmp_path / "relative.json", replace(model, storm=relative))
    result = run_engine_project(relative_project)
    assert result.status == "computed_unvalidated", result.diagnostics
    assert result.effective_selection == SELECTION
    assert run_model(replace(model, storm=relative)).prints == run_model(replace(model, storm=percentages)).prints
    assert result.native_parity_status == "not_assessed"


def test_combined_preburst_remains_explicitly_unsupported(tmp_path: Path) -> None:
    model = _imported_model()
    storm = replace(
        model.storm,
        pattern_basis="combined_preburst_percent",
        percentages=(Decimal(20), Decimal(100)),
        preburst_bins=1,
    )
    project = _project(tmp_path / "preburst.json", replace(model, storm=storm))
    result = run_engine_project(project)
    assert result.status == "unsupported_feature"
    assert result.effective_selection == SELECTION
    assert result.diagnostics[0].code == "unsupported_s2_profile"
    assert not result.hydrographs
