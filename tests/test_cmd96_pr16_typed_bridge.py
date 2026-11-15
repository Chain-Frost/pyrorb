"""PyRomb PR16 typed CATG to actual public CMD event bridge; not native Q parity.

Source grammar is owned by #96; this tests the numerical adapter against
the exact retained historical CATG and a separately authored storm.
"""

from __future__ import annotations

import hashlib
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from typing import cast

from runoff_routing._cmd644.precision import store
from runoff_routing._cmd644.preparation import prepare
from runoff_routing.cmd_engine import adapt_event
from runoff_routing.engine_execution import run_engine_project
from runoff_routing.engine_types import EngineSelection
from runoff_routing.project_json import EmbeddedRun, LegacyRunFiles, Project, SourceFile, load_project, write_project
from runoff_routing.rorb_codec import parse_catg, serialize_cmd_par, serialize_design_stm
from runoff_routing.rorb_model import RunModel, from_json

ROOT = Path(__file__).parents[1]
EXAMPLE = ROOT / "examples" / "synthetic-run.json"
ORIGINAL_SHA = "2ad4663ddeaacdfd4bba4b199a29d3eed7bcb6d9f096ff62f6d9d107330bd247"
ORIGINAL_CATG = ROOT / "tests" / "fixtures" / "regression-v1" / "native-cmd" / "objects" / f"{ORIGINAL_SHA}.catg"


def _event_source() -> RunModel:
    """Original immutable CATG plus an authored, explicitly non-native storm."""
    original = ORIGINAL_CATG.read_bytes()
    assert len(original) == 2913
    assert hashlib.sha256(original).hexdigest() == ORIGINAL_SHA
    catchment = parse_catg(original).model
    assert catchment.reach_mode == "explicit_reach_types"
    template = from_json(EXAMPLE.read_text(encoding="utf-8"))
    assert isinstance(template, RunModel)
    storm = replace(
        template.storm,
        title="Authored PR16 CATG adapter control not a retained native storm",
        timestep_hours=Decimal("0.25"),
        calculation_increments=40,
        subarea_ids=tuple(source.identifier for source in catchment.subareas),
        depths_mm=tuple(Decimal(20) for _ in catchment.subareas),
    )
    routing = replace(template.parameters.routing[0], m=Decimal(1))
    parameters = replace(template.parameters, routing=(routing,))
    return RunModel(parameters, catchment, storm)


def test_original_pyromb_catg_source_admits_code_two_and_fi_without_substitution(tmp_path: Path) -> None:
    model = _event_source()
    path = tmp_path / "event.json"
    write_project(path, Project("cmd_pr16_bridge", "explicit", EmbeddedRun(model)))
    event = adapt_event(load_project(path))
    assert tuple(step.code for step in event.controls) == (1, 3, 1, 4, 2, 3, 1, 2, 4, 5, 2, 7)
    assert event.source_count == 6
    assert event.reach_count == 7
    assert tuple(value.lexeme for value in event.impervious) == ("0", "0.50000", "0.20000", "0", "0", "0")
    assert tuple(value.stored for value in event.impervious) == (0.0, 0.5, store(0.2), 0.0, 0.0, 0.0)
    assert len(event.weights) == 2
    assert tuple(value.stored for value in event.depths) == (20.0,) * 6
    prepared = prepare(event)
    no_fi = prepare(replace(event, impervious=tuple(replace(value, stored=0.0) for value in event.impervious)))
    assert prepared.excess[1] != no_fi.excess[1]
    assert prepared.excess[2] != no_fi.excess[2]
    assert prepared.excess[0] == no_fi.excess[0]


def test_public_cmd_bridge_executes_complete_authored_horizon(tmp_path: Path) -> None:
    model = _event_source()
    path = tmp_path / "event.json"
    write_project(path, Project("cmd_pr16_bridge", "explicit", EmbeddedRun(model)))
    result = run_engine_project(path, selection=EngineSelection.for_engine("python-cmd"))
    assert result.status == "computed_unvalidated", result.diagnostics
    assert result.native_parity_status == "not_assessed"
    assert result.native_raw_time_tokens == ()
    assert result.requested_print_ids == tuple(item.identifier for item in model.catchment.print_locations)
    assert tuple(item.print_id for item in result.hydrographs) == result.requested_print_ids
    assert len(result.hydrographs) == 1
    assert len(result.hydrographs[0].discharge_m3_s) == 41
    assert len(result.physical_time_hours) == 41
    assert result.python_diagnostics is not None
    assert result.python_diagnostics["ordered_source_ids"] == tuple(
        item.identifier for item in model.catchment.subareas
    )
    assert result.python_diagnostics["ordered_reach_ids"] == tuple(item.identifier for item in model.catchment.reaches)
    reaches = cast("list[dict[str, object]]", result.python_diagnostics["reaches"])
    assert len(reaches) == 7


def test_original_catg_fileback_import_executes_same_authored_event(tmp_path: Path) -> None:
    """Exercise supported .catg/.par/.stm project file boundary without PyRomb."""
    model = _event_source()
    names = ("model.par", "model.catg", "model.stm")
    data = (serialize_cmd_par(model.parameters), ORIGINAL_CATG.read_bytes(), serialize_design_stm(model.storm))
    references: list[SourceFile] = []
    for name, raw in zip(names, data, strict=True):
        (tmp_path / name).write_bytes(raw)
        references.append(SourceFile(name, hashlib.sha256(raw).hexdigest()))
    source = tmp_path / "legacy.json"
    write_project(
        source,
        Project(
            "cmd_pr16_fileback",
            "legacy-rorb",
            LegacyRunFiles(references[0], references[1], references[2]),
            engine=EngineSelection.for_engine("python-cmd"),
        ),
    )
    loaded = load_project(source)
    assert loaded.run == model
    assert (names[1], ORIGINAL_SHA) in loaded.file_hashes
    outcome = run_engine_project(source)
    assert outcome.status == "computed_unvalidated", outcome.diagnostics
    assert len(outcome.hydrographs) == 1
    assert len(outcome.hydrographs[0].discharge_m3_s) == 41
