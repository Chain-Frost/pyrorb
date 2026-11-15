"""Independent S5 source/project and retained-report acceptance, without native execution.

The original case identities and file hashes belong to the one public regression
register. These tests do not produce new native references or infer CMD parity.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from runoff_routing.engine_execution import run_engine_project
from runoff_routing.engine_types import EngineSelection
from runoff_routing.project_batch import ProjectEvent, run_project_events
from runoff_routing.project_json import (
    EmbeddedRun,
    ExternalAsset,
    LegacyRunFiles,
    Project,
    ProjectError,
    SourceFile,
    compare_project_files,
    import_rorb_project,
    load_project,
    write_project,
)
from runoff_routing.rorb_codec import (
    FormatProblem,
    original_bytes,
    parse_bytes,
    parse_catg,
    parse_cmd_par,
    parse_design_stm,
)
from runoff_routing.rorb_documents import RorbSource
from runoff_routing.rorb_model import RunModel
from runoff_routing.rorb_out import inspect_output

DATA = Path(__file__).absolute().parent / "fixtures" / "regression-v1"
SOURCE_CASE_IDS = (
    "review-design-baseline",
    "review-ensemble-tp1",
    "timestep-design-baseline-f2",
    "timestep-ensemble-tp3-f4",
    "zero-loss-ensemble-tp9-f1",
)


def _case(case_id: str) -> dict[str, Any]:
    register = json.loads((DATA / "register.json").read_text(encoding="utf-8"))
    return next(item for item in register["cases"] if item["case_id"] == case_id)


def _source_files(case_id: str) -> tuple[tuple[str, bytes, str], ...]:
    case = _case(case_id)
    verified: list[tuple[str, bytes, str]] = []
    for suffix in (".par", ".catg", ".stm"):
        record = next(item for item in case["files"] if item["path"].endswith(suffix))
        raw = (DATA / record["path"]).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        assert (len(raw), digest) == (record["size_bytes"], record["sha256"])
        verified.append((suffix, raw, digest))
    return tuple(verified)


def _stage(root: Path, case_id: str) -> tuple[Path, tuple[Path, ...], tuple[bytes, ...]]:
    """Stage copies in a directory with spaces, never editing registered objects."""
    source = _source_files(case_id)
    folder = root / "Source assets with spaces"
    folder.mkdir(parents=True)
    paths = tuple(folder / f"Selected model {suffix}" for suffix, _, _ in source)
    for path, (_, raw, _) in zip(paths, source, strict=True):
        path.write_bytes(raw)
    target = root / "project.json"
    project = import_rorb_project(
        target,
        identifier="s5_case",
        rainfall_profile="legacy-rorb",
        parameters=paths[0],
        catchment=paths[1],
        storm=paths[2],
    )
    write_project(target, project)
    return target, paths, tuple(raw for _, raw, _ in source)


@pytest.mark.parametrize("case_id", SOURCE_CASE_IDS)
def test_registered_original_triplet_survives_project_save_and_move(tmp_path: Path, case_id: str) -> None:
    """Byte equality is not native-run portability or numerical equivalence."""
    original_folder = tmp_path / "original project"
    project_path, paths, raw = _stage(original_folder, case_id)
    expected = RunModel(parse_cmd_par(raw[0]).model, parse_catg(raw[1]).model, parse_design_stm(raw[2]).model)
    assert original_bytes(parse_cmd_par(raw[0])) == raw[0]
    assert original_bytes(parse_catg(raw[1])) == raw[1]
    assert original_bytes(parse_design_stm(raw[2])) == raw[2]
    loaded = load_project(project_path)
    assert loaded.run == expected
    assert loaded.original_json_bytes == project_path.read_bytes()
    assert [sha for _, sha in loaded.file_hashes] == [hashlib.sha256(item).hexdigest() for item in raw]
    assert tuple(path.read_bytes() for path in paths) == raw

    relocated_folder = tmp_path / "relocated project with spaces"
    original_folder.rename(relocated_folder)
    relocated = relocated_folder / project_path.name
    reopened = load_project(relocated)
    assert not original_folder.exists()
    assert reopened.run == expected
    assert reopened.project == loaded.project
    assert reopened.original_json_bytes == loaded.original_json_bytes
    assert tuple((relocated_folder / path.relative_to(original_folder)).read_bytes() for path in paths) == raw
    assert [sha for _, sha in reopened.file_hashes] == [hashlib.sha256(item).hexdigest() for item in raw]


def test_edited_json_model_survives_reopen_and_execution_without_masking_originals(tmp_path: Path) -> None:
    """Current edited representation is embedded JSON, not edited native PAR/CATG/STM."""
    root = tmp_path / "original project"
    source_project, paths, raw = _stage(root, "review-design-baseline")
    original = load_project(source_project).run
    routing = replace(original.parameters.routing[0], kc=original.parameters.routing[0].kc * Decimal("1.1"))
    loss = replace(original.parameters.losses[0], initial_loss_mm=original.parameters.losses[0].initial_loss_mm + 1)
    parameters = replace(
        original.parameters,
        verbosity=2 if original.parameters.verbosity != 2 else 1,
        routing=(routing,),
        losses=(loss,),
    )
    storm = replace(original.storm, depths_mm=tuple(depth + 1 for depth in original.storm.depths_mm))
    edited = replace(original, parameters=parameters, storm=storm)
    evidence = tuple(
        ExternalAsset(
            f"original_{index}",
            "reference",
            "preedit_source",
            SourceFile(path.relative_to(root).as_posix(), hashlib.sha256(contents).hexdigest()),
        )
        for index, (path, contents) in enumerate(zip(paths, raw, strict=True), start=1)
    )
    edited_project = root / "edited.json"
    write_project(
        edited_project,
        Project(
            "s5_edited",
            "legacy-rorb",
            EmbeddedRun(edited),
            assets=evidence,
            engine=EngineSelection.for_engine("python-cmd"),
        ),
    )
    reopened = load_project(edited_project)
    assert reopened.run == edited
    assert reopened.run.catchment.controls == original.catchment.controls
    assert reopened.run.catchment.subareas == original.catchment.subareas
    assert reopened.run.parameters.routing[0].kc == routing.kc
    assert reopened.run.parameters.losses[0].initial_loss_mm == loss.initial_loss_mm
    assert reopened.run.storm.depths_mm == storm.depths_mm
    assert tuple(path.read_bytes() for path in paths) == raw
    assert not compare_project_files(source_project, edited_project).model_equal

    one = run_engine_project(edited_project)
    batch = run_project_events(edited_project, (ProjectEvent("edited"),)).outcomes[0]
    assert one.status == batch.status == "computed_unvalidated"
    assert one.effective_selection == batch.effective_selection == EngineSelection.for_engine("python-cmd")
    assert one.model_sha256 == batch.model_sha256
    assert one.hydrographs == batch.hydrographs
    assert one.physical_time_hours == batch.physical_time_hours
    assert one.source_file_hashes == batch.source_file_hashes


def test_no_clobber_and_changed_or_missing_originals_fail_closed(tmp_path: Path) -> None:
    project_path, paths, original = _stage(tmp_path / "protected sources", "review-design-baseline")
    project = load_project(project_path).project
    manifest_before = project_path.read_bytes()
    with pytest.raises(FileExistsError):
        write_project(project_path, project)
    assert project_path.read_bytes() == manifest_before
    assert tuple(path.read_bytes() for path in paths) == original

    # Only the project's selected hash-pinned source may affect reopen.
    # PAR-led import (#140) stages a copy, while the older three-file
    # importer binds the originals. Both are tested via the effective binding.
    pinned = project.model_source
    assert isinstance(pinned, LegacyRunFiles)
    bound = tuple(project_path.parent / ref.path for ref in (pinned.parameters, pinned.catchment, pinned.storm))
    assert tuple(path.read_bytes() for path in bound) == original
    bound[1].write_bytes(original[1] + b"\nC tampered source\n")
    with pytest.raises(ProjectError, match="SHA-256"):
        load_project(project_path)
    bound[1].write_bytes(original[1])
    bound[2].unlink()
    with pytest.raises(ProjectError, match="Missing project source"):
        load_project(project_path)
    assert project_path.read_bytes() == manifest_before


def test_source_gate_does_not_admit_unknown_par_or_old_plain_formats() -> None:
    with pytest.raises(FormatProblem) as unknown:
        parse_cmd_par(b"UNRECOGNISED PAR DIALECT\n")
    assert unknown.value.status == "unsupported"
    for suffix in (".cat", ".dat"):
        with pytest.raises(FormatProblem) as excluded:
            parse_bytes(b"1\n2\n0\n", suffix)
        assert excluded.value.status == "unsupported"

    original_catg = _source_files("review-design-baseline")[1][1]
    assert parse_bytes(original_catg, ".cat").model == parse_catg(original_catg).model


@pytest.mark.parametrize("case_id", SOURCE_CASE_IDS)
def test_existing_retained_cmd_report_preserves_registered_rows_and_clock(case_id: str) -> None:
    """Current .out baseline only: final ryan-tools dependency acceptance is separate."""
    case = _case(case_id)
    reference = case["reference"]
    source = RorbSource.read(DATA / reference["path"])
    assert (source.size_bytes, source.sha256) == (reference["size_bytes"], reference["sha256"])
    inspected = inspect_output(source)
    assert inspected.status == "partial"
    assert any(item.code == "print_identity_unverified" for item in inspected.diagnostics)
    assert inspected.hydrographs is not None
    rows = inspected.hydrographs.rows
    assert len(rows) == case["clock"]["row_count"]
    assert tuple(row.increment for row in rows) == tuple(range(1, len(rows) + 1))
    assert inspected.hydrographs.time_increment_hours == Decimal(case["clock"]["timestep_hours"])
    assert all(row.raw_time and row.values for row in rows)


@pytest.mark.parametrize(
    ("filename", "size_bytes", "git_blob"),
    [
        ("rorbwin652-12h-standard.out", 19_020, "95826bccdbe1f2410ef372ef6b6c2c161d847b99"),
        ("rorbwin652-12h-batch.out", 8_558, "08ae1d94ef74d666836c8d3fab842e6421851030"),
    ],
)
def test_public_rorbwin_652_original_report_bytes_are_authenticated(
    filename: str, size_bytes: int, git_blob: str
) -> None:
    """Pin exact public GUI bytes; installed ryan-tools parsing is a distinct gate."""
    path = DATA.parent / "s5-acceptance" / filename
    data = path.read_bytes()
    assert len(data) == size_bytes
    header = f"blob {len(data)}\0".encode("ascii")
    assert hashlib.sha1(header + data, usedforsecurity=False).hexdigest() == git_blob
