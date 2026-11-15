"""#149: stream/checkpoint/replay explicit MC samples without drawing or new solvers."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from typing import cast

import pytest

from runoff_routing.arr_patterns import read_pattern_file
from runoff_routing.engine_types import EngineSelection
from runoff_routing.monte_carlo_effective import (
    EffectiveMCEvent,
    MCInputError,
    MCPopulation,
    MCRequestHeader,
    materialise_arr_sample,
    validate_effective_request,
    write_effective_request,
)
from runoff_routing.monte_carlo_execution import (
    MCRunError,
    execute_mc_request,
    main,
    replay_mc_event,
    summarise_ledger,
)
from runoff_routing.project_batch import ProjectEvent, run_project_events
from runoff_routing.project_json import EmbeddedRun, Project, SourceFile, write_project
from runoff_routing.rorb_model import RunModel, from_json

ROOT = Path(__file__).parents[1]
EXAMPLES = ROOT / "examples"
SOURCE_PATTERNS = EXAMPLES / "arr-design-synthetic-patterns.csv"
MODEL = EXAMPLES / "synthetic-run.json"
CMD = EngineSelection.for_engine("python-cmd")


def _source_model() -> RunModel:
    model = from_json(MODEL.read_text(encoding="utf-8"))
    assert isinstance(model, RunModel)
    return model


def _input(
    directory: Path,
    *,
    count: int = 2,
    bad: bool = False,
    extension: bool = False,
) -> tuple[Path, Path, list[EffectiveMCEvent]]:
    model = _source_model()
    project = directory / "project.json"
    write_project(project, Project("mc_synthetic", "explicit", EmbeddedRun(model), engine=CMD))
    source = directory / "patterns.csv"
    source.write_bytes(SOURCE_PATTERNS.read_bytes())
    patterns = read_pattern_file(source, kind="point")
    events: list[EffectiveMCEvent] = []
    for index in range(count):
        item = materialise_arr_sample(
            model=model,
            pattern_set=patterns,
            pattern_source_order=1 + index % 2,
            sample_id=f"sample-{index + 1}",
            scenario_id="base",
            stratum_id="h1",
            stratum_mass=Decimal(1),
            stratum_size=count,
            rainfall_aep_percent=Decimal(2),
            gross_depth_mm=Decimal(20 + index),
            bom_source_sha256=hashlib.sha256(b"synthetic_B_sampled_IFD").hexdigest(),
            arf_region="South-West Western Australia",
            storm_initial_loss_mm=Decimal(6),
            preburst_depth_mm=Decimal(1),
            preburst_policy="subtract_reject",
            dry_tail_min=120,
        )
        events.append(item)
    if bad:
        record = events[0]
        assert record.event.storm is not None
        assert record.event.losses is not None
        events[0] = replace(
            record,
            event=ProjectEvent(
                record.sample_id,
                storm={**record.event.storm, "start_increment": 100},
                losses=record.event.losses,
            ),
        )
    header = MCRequestHeader(
        plan_sha256=hashlib.sha256(b"extended" if extension else b"initial").hexdigest(),
        policy_id="authored_control_v1",
        source_files=(SourceFile("patterns.csv", hashlib.sha256(source.read_bytes()).hexdigest()),),
        populations=(MCPopulation("base", 60, Decimal(1)),),
        event_count=count,
    )
    request = directory / "effective.jsonl"
    write_effective_request(request, header, events)
    return project, request, events


def _rows(ledger: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]


def test_materialise_once_and_replay_matches_existing_event_runner(tmp_path: Path) -> None:
    project, request, events = _input(tmp_path)
    _, digest = validate_effective_request(request)
    assert len(digest) == 64
    sample = events[0]
    assert sample.event.storm is not None
    assert sample.event.losses is not None
    expected_areal_depth = sample.gross_depth_mm * sample.arf_factor
    assert sample.event.storm["depths_mm"] == [str(expected_areal_depth)]
    assert sample.event.losses["initial_loss_mm"] == "5"
    direct = run_project_events(project, (sample.event,), selection=CMD).outcomes[0]
    ledger = tmp_path / "ledger.jsonl"
    report = execute_mc_request(project, request, ledger)
    assert report.complete
    site_records = cast("list[dict[str, object]]", _rows(ledger)[1]["sites"])
    assert site_records[0]["peak_m3_s"] == max(direct.hydrographs[0].discharge_m3_s)
    prefix = tmp_path / "selected"
    replayed = replay_mc_event(project, request, ledger, sample.sample_id, prefix, selection=CMD)
    assert replayed.outcomes[0].model_sha256 == direct.model_sha256
    assert replayed.outcomes[0].hydrographs == direct.hydrographs
    assert replayed.outcomes[0].physical_time_hours == direct.physical_time_hours
    assert (tmp_path / "selected.json").is_file()
    assert (tmp_path / "selected.csv").is_file()
    assert (tmp_path / "selected.txt").is_file()


def test_resume_exact_prefix_without_rerouting_or_weight_change(tmp_path: Path) -> None:
    project, request, _ = _input(tmp_path, count=3)
    ledger = tmp_path / "ledger.jsonl"
    original = execute_mc_request(project, request, ledger)
    assert original.complete
    original_lines = ledger.read_bytes().splitlines(keepends=True)
    ledger.write_bytes(b"".join(original_lines[:2]))
    resumed = execute_mc_request(project, request, ledger, resume=True)
    assert resumed.complete
    assert ledger.read_bytes() == b"".join(original_lines)
    with pytest.raises(MCRunError, match="already exists"):
        execute_mc_request(project, request, ledger)
    assert summarise_ledger(ledger, request, _rows(ledger)[0]).complete


def test_changed_request_or_engine_rejected_even_with_same_sample_id(tmp_path: Path) -> None:
    project, request, _ = _input(tmp_path)
    ledger = tmp_path / "ledger.jsonl"
    assert execute_mc_request(project, request, ledger).complete
    data = request.read_bytes()
    request.write_bytes(data.replace(b'"policy_id":"authored_control_v1"', b'"policy_id":"modified_control_v1"'))
    with pytest.raises(MCRunError, match="different plan/policy/source/engine/code"):
        execute_mc_request(project, request, ledger, resume=True)
    request.write_bytes(data)
    with pytest.raises(MCRunError, match="only explicitly selected python-cmd"):
        execute_mc_request(project, request, tmp_path / "python.jsonl", selection=EngineSelection.for_engine("python"))
    assert not (tmp_path / "python.jsonl").exists()


def test_positive_weight_failure_never_disappears_or_becomes_zero(tmp_path: Path) -> None:
    project, request, events = _input(tmp_path, bad=True)
    ledger = tmp_path / "failures.jsonl"
    summary = execute_mc_request(project, request, ledger)
    assert not summary.complete
    rows = _rows(ledger)
    assert len(rows) == 3
    assert rows[1]["sample_id"] == events[0].sample_id
    assert rows[1]["probability_weight"] == "0.5"
    assert rows[1]["status"] != "computed_unvalidated"
    assert rows[1]["sites"] == []
    assert rows[2]["status"] == "computed_unvalidated"
    assert main(["inspect", str(project), str(request), str(ledger)]) == 2
    with pytest.raises(MCRunError, match="successfully checkpointed"):
        replay_mc_event(project, request, ledger, events[0].sample_id, tmp_path / "invalid")


def test_duplicate_samples_missing_strata_and_double_transform_rejected(tmp_path: Path) -> None:
    project, request, events = _input(tmp_path)
    del project
    raw = request.read_bytes()
    assert events[0].event.storm is not None
    assert events[0].event.losses is not None
    modified = ProjectEvent(
        events[0].sample_id,
        storm={**events[0].event.storm, "depths_mm": [str(events[0].gross_depth_mm)]},
        losses=events[0].event.losses,
    )
    with pytest.raises(MCInputError, match="ARF exactly once"):
        replace(events[0], event=modified)
    parts = raw.splitlines(keepends=True)
    request.write_bytes(parts[0] + parts[1] + parts[1])
    with pytest.raises(MCInputError, match="Duplicate sample"):
        validate_effective_request(request)
    request.write_bytes(parts[0] + parts[1])
    with pytest.raises(MCInputError, match="event count differs"):
        validate_effective_request(request)


def test_truncated_checkpoint_rejected_and_unfinished_not_complete(tmp_path: Path) -> None:
    project, request, _ = _input(tmp_path)
    ledger = tmp_path / "ledger.jsonl"
    assert execute_mc_request(project, request, ledger).complete
    parts = ledger.read_bytes().splitlines(keepends=True)
    ledger.write_bytes(parts[0] + parts[1])
    assert not summarise_ledger(ledger, request, _rows(ledger)[0]).complete
    ledger.write_bytes(parts[0] + parts[1] + parts[2][:-1])
    with pytest.raises(MCInputError, match="end with newline"):
        execute_mc_request(project, request, ledger, resume=True)


def test_engine_selection_and_simple_cli(tmp_path: Path) -> None:
    project, request, _ = _input(tmp_path, count=1)
    ledger = tmp_path / "cli.jsonl"
    assert main(["validate", str(request)]) == 0
    assert main(["run", str(project), str(request), str(ledger), "--engine", "python-cmd"]) == 0
    assert main(["run", str(project), str(request), str(ledger)]) == 2
    assert main(["run", str(project), str(request), str(ledger), "--resume"]) == 0
    assert main(["replay", str(project), str(request), str(ledger), "sample-1", str(tmp_path / "cli-replay")]) == 0
