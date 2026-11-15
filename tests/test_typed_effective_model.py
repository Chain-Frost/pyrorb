"""Typed S1 editing and shared event-settings boundary (#138)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from typing import Any, cast

import pytest

from runoff_routing.engine_types import EngineKind, EngineSelection, ResultStatus
from runoff_routing.integration import canonical_run_bytes, parse_run_bytes
from runoff_routing.project_batch import EventConfigError, ProjectEvent, resolve_effective_model, run_project_events
from runoff_routing.project_json import EmbeddedRun, LegacyRunFiles, Project, SourceFile, load_project, write_project
from runoff_routing.rorb_model import (
    ControlCode,
    ControlStep,
    InitialContinuingLoss,
    InitialRunoffCoefficientLoss,
    LossMode,
    LossValue,
    PatternBasis,
    ReachMode,
    RunModel,
    edit_run_model,
    from_dict,
    from_json,
    to_dict,
    to_json,
)

EXAMPLE = Path(__file__).parents[1] / "examples" / "synthetic-run.json"


def _model() -> RunModel:
    parsed = from_json(EXAMPLE.read_text(encoding="utf-8"))
    assert isinstance(parsed, RunModel)
    return parsed


def test_closed_values_are_enums_in_memory_and_native_values_on_the_wire() -> None:
    run = _model()
    assert run.parameters.loss_model is LossMode.INITIAL_CONTINUING
    assert run.catchment.controls[0].code is ControlCode.SOURCE
    assert run.catchment.reach_mode is ReachMode.IMPLICIT_NATURAL
    assert run.storm.pattern_basis is PatternBasis.PERCENT_OF_DEPTH
    document = to_dict(run)
    model = cast("dict[str, Any]", document["model"])
    parameters = cast("dict[str, Any]", model["parameters"])
    catchment = cast("dict[str, Any]", model["catchment"])
    assert type(parameters["loss_model"]) is int
    assert type(catchment["controls"][0]["code"]) is int
    assert from_dict(document) == run
    selected = EngineSelection()
    assert selected.engine is EngineKind.PYTHON_CMD
    assert json.loads(json.dumps(selected.engine)) == "python-cmd"
    assert ResultStatus.COMPUTED_UNVALIDATED == "computed_unvalidated"


def test_closed_codes_and_counts_reject_unknown_values_and_booleans() -> None:
    run = _model()
    for code in (True, False, 6, 11):
        with pytest.raises((TypeError, ValueError), match="control code"):
            ControlStep(cast("ControlCode", code))
    for mode in (True, False, 0, 3):
        with pytest.raises((TypeError, ValueError), match="loss model"):
            replace(run.parameters, loss_model=cast("LossMode", mode))
    with pytest.raises(ValueError, match="one explicit burst"):
        replace(run.parameters, num_bursts=True)
    with pytest.raises(ValueError, match="integers"):
        replace(run.storm, isa_count=True)
    payload = to_dict(run)
    cast("dict[str, Any]", payload["model"])["parameters"]["loss_model"] = True
    with pytest.raises(TypeError, match="integer"):
        from_dict(payload)
    with pytest.raises(ValueError, match="Unknown computation engine"):
        EngineSelection.for_engine("not-an-engine")


def test_loss_policies_discriminate_units_and_immutable_edits() -> None:
    base = _model()
    original_json = to_json(base)
    losses = base.parameters.loss_policies
    assert isinstance(losses[0], InitialContinuingLoss)
    assert losses[0].continuing_loss_mm_h == base.parameters.losses[0].continuing
    selected = base.parameters.with_loss_policies((InitialContinuingLoss(1, 1, Decimal(4), Decimal("0.25")),))
    edited = edit_run_model(base, parameters=selected)
    assert edited.parameters.losses[0].continuing == Decimal("0.25")
    assert to_json(base) == original_json
    assert edited.catchment is base.catchment
    mode_two = replace(
        base.parameters,
        loss_model=LossMode.INITIAL_RUNOFF_COEFFICIENT,
        losses=(LossValue(1, 1, Decimal(4), Decimal("0.5")),),
    )
    assert isinstance(mode_two.loss_policies[0], InitialRunoffCoefficientLoss)
    changed = mode_two.with_loss_policies((InitialRunoffCoefficientLoss(1, 1, Decimal(5), Decimal("0.75")),))
    assert changed.losses[0].continuing == Decimal("0.75")
    with pytest.raises(ValueError, match="incompatible"):
        mode_two.with_loss_policies((InitialContinuingLoss(1, 1, Decimal(5), Decimal(1)),))
    with pytest.raises(ValueError, match="coefficient"):
        InitialRunoffCoefficientLoss(1, 1, Decimal(4), Decimal("1.1"))
    with pytest.raises(ValueError, match="coefficient"):
        replace(mode_two, losses=(LossValue(1, 1, Decimal(4), Decimal("1.1")),))


def test_effective_event_is_identical_for_api_model_and_real_batch(tmp_path: Path) -> None:
    base = _model()
    source_document = to_json(base)
    event = ProjectEvent(
        "wet-tp2",
        storm={"depths_mm": ["25.5"]},
        losses={"continuing_loss_mm_h": "0.25"},
        routing={"kc": "1.5"},
    )
    effective = resolve_effective_model(base, event)
    assert effective.event_id == "wet-tp2"
    assert effective.edited_fields == ("storm", "losses", "routing")
    assert effective.run.storm.depths_mm == (Decimal("25.5"),)
    assert effective.run.parameters.losses[0].continuing == Decimal("0.25")
    assert effective.run.parameters.routing[0].kc == Decimal("1.5")
    assert resolve_effective_model(base).run is base
    assert from_json(to_json(effective.run)) == effective.run
    assert to_json(base) == source_document
    project_path = tmp_path / "project.json"
    write_project(project_path, Project("typed_api", "explicit", EmbeddedRun(base)))
    outcome = run_project_events(project_path, (event,)).outcomes[0]
    assert outcome.status == ResultStatus.COMPUTED_UNVALIDATED
    assert outcome.model_sha256 == hashlib.sha256(to_json(effective.run).encode("utf-8")).hexdigest()
    assert project_path.read_text(encoding="utf-8").find('"25.5"') == -1


def test_effective_resolver_rejects_incompatible_loss_fields_and_cross_model_identities() -> None:
    base = _model()
    with pytest.raises(EventConfigError, match="Mutually exclusive"):
        resolve_effective_model(
            base,
            ProjectEvent("bad", losses={"continuing_loss_mm_h": "0.1", "runoff_coefficient": "0.2"}),
        )
    with pytest.raises(EventConfigError, match="requires loss mode 2"):
        resolve_effective_model(base, ProjectEvent("bad", losses={"runoff_coefficient": "0.2"}))
    with pytest.raises(ValueError, match="Storm depth source order"):
        edit_run_model(base, storm=replace(base.storm, subarea_ids=("other",)))
    with pytest.raises(EventConfigError, match="Event ID"):
        resolve_effective_model(base, {"event_id": True})


def test_imported_source_bytes_and_provenance_survive_event_edit(tmp_path: Path) -> None:
    original = _model()
    names = ("original.par", "original.catg", "original.stm")
    byte_records = canonical_run_bytes(original)
    sources: list[SourceFile] = []
    for name, raw in zip(names, byte_records, strict=True):
        (tmp_path / name).write_bytes(raw)
        sources.append(SourceFile(name, hashlib.sha256(raw).hexdigest()))
    project_path = tmp_path / "imported.json"
    write_project(
        project_path,
        Project(
            "imported",
            "legacy-rorb",
            LegacyRunFiles(sources[0], sources[1], sources[2]),
        ),
    )
    raw_project = project_path.read_bytes()
    loaded = load_project(project_path)
    before = tuple((tmp_path / name).read_bytes() for name in names)
    edited = resolve_effective_model(
        loaded.run,
        ProjectEvent("modified", losses={"continuing_loss_mm_h": "0.2"}, routing={"kc": "2.5"}),
    )
    assert edited.run != loaded.run
    assert edited.run.catchment is loaded.run.catchment
    assert edited.run.storm is loaded.run.storm
    assert edited.run.parameters.losses[0].continuing == Decimal("0.2")
    assert edited.run.parameters.routing[0].kc == Decimal("2.5")
    assert tuple((tmp_path / name).read_bytes() for name in names) == before
    assert tuple(hashlib.sha256(raw).hexdigest() for raw in before) == tuple(source.sha256 for source in sources)
    assert project_path.read_bytes() == raw_project
    reloaded = load_project(project_path)
    assert reloaded.run == loaded.run
    assert reloaded.file_hashes == loaded.file_hashes


def test_raw_event_overlays_remain_unchanged_after_repeated_resolution() -> None:
    base = _model()
    original_model = to_json(base)
    mode_one: dict[str, object] = {
        "event_id": "legacy-1",
        "losses": {"continuing_loss_mm_h": "0.3"},
    }
    for _ in range(2):
        resolved = resolve_effective_model(base, mode_one)
        assert resolved.run.parameters.losses[0].continuing == Decimal("0.3")
    assert mode_one["losses"] == {"continuing_loss_mm_h": "0.3"}

    mode_two = edit_run_model(
        base,
        parameters=replace(
            base.parameters,
            loss_model=LossMode.INITIAL_RUNOFF_COEFFICIENT,
            losses=(replace(base.parameters.losses[0], continuing=Decimal("0.5")),),
        ),
    )
    mode_two_event: dict[str, object] = {
        "event_id": "legacy-2",
        "losses": {"runoff_coefficient": "0.75"},
    }
    for _ in range(2):
        resolved = resolve_effective_model(mode_two, mode_two_event)
        assert resolved.run.parameters.losses[0].continuing == Decimal("0.75")
    assert mode_two_event["losses"] == {"runoff_coefficient": "0.75"}
    assert mode_two.parameters.losses[0].continuing == Decimal("0.5")
    assert to_json(base) == original_model
    with pytest.raises(EventConfigError, match="Mutually exclusive"):
        resolve_effective_model(
            mode_two,
            {"event_id": "invalid", "losses": {"continuing": "0.1", "runoff_coefficient": "0.2"}},
        )


def test_mode_two_native_roundtrip_and_result_status_are_primitive_on_wire(tmp_path: Path) -> None:
    base = _model()
    mode_two = edit_run_model(
        base,
        parameters=replace(
            base.parameters,
            loss_model=LossMode.INITIAL_RUNOFF_COEFFICIENT,
            losses=(replace(base.parameters.losses[0], continuing=Decimal("0.5")),),
        ),
    )
    event = ProjectEvent("runoff", losses={"runoff_coefficient": "0.75"})
    resolved = resolve_effective_model(mode_two, event)
    native_roundtrip = parse_run_bytes(*canonical_run_bytes(resolved.run))
    assert native_roundtrip.model == resolved.run
    project_path = tmp_path / "runoff.json"
    write_project(project_path, Project("runoff_mode_two", "explicit", EmbeddedRun(mode_two)))
    outcome = run_project_events(project_path, (event,)).outcomes[0]
    assert outcome.status is ResultStatus.COMPUTED_UNVALIDATED
    wire = cast("dict[str, Any]", json.loads(outcome.to_json()))
    assert wire["status"] == "computed_unvalidated"
    assert type(wire["status"]) is str
    assert wire["effective_selection"]["engine"] == "python-cmd"
    with pytest.raises(ValueError, match="Unknown project result status"):
        replace(outcome, status=cast("ResultStatus", "unexpected"))
