"""Independent integrated S5 contract tests over unmerged implementation heads.

These tests run against the temporary combined validation tree. Passing them
does not imply native Windows RORB execution or numerical equivalence.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import shutil
from collections import Counter
from dataclasses import replace
from decimal import Decimal
from importlib.metadata import distribution
from pathlib import Path
from typing import Any

import pytest
from ryan_library.functions.RORB.readers import read_rorb_file

from runoff_routing.engine_execution import run_engine_project
from runoff_routing.native_export import NativeCmdExportTarget, NativeExportError, NativeExportEvent, export_cmd_package
from runoff_routing.project_batch import EventConfigError, ProjectEvent, resolve_effective_model, run_project_events
from runoff_routing.project_json import (
    import_rorb_project,
    load_project,
    save_project_as,
    write_project,
)
from runoff_routing.rorb_codec import parse_catg, parse_cmd_par, parse_design_stm, serialize_catg
from runoff_routing.rorb_documents import RorbSource
from runoff_routing.rorb_model import LossMode, RunModel, from_json
from runoff_routing.rorb_out import inspect_output

REGISTER = Path(__file__).absolute().parent / "fixtures" / "regression-v1" / "register.json"
RETENTION = Path(__file__).absolute().parent / "fixtures" / "s5-acceptance"
ROOT = Path(__file__).absolute().parents[1]


def _original_triplet() -> tuple[bytes, bytes, bytes]:
    register: dict[str, Any] = json.loads(REGISTER.read_text(encoding="utf-8"))
    case = next(item for item in register["cases"] if item["case_id"] == "review-design-baseline")
    stored: list[bytes] = []
    for suffix in (".par", ".catg", ".stm"):
        record = next(item for item in case["files"] if item["path"].endswith(suffix))
        payload = (REGISTER.parent / record["path"]).read_bytes()
        assert len(payload) == record["size_bytes"]
        assert hashlib.sha256(payload).hexdigest() == record["sha256"]
        stored.append(payload)
    return stored[0], stored[1], stored[2]


def _project(tmp_path: Path) -> tuple[Path, Path, tuple[bytes, bytes, bytes]]:
    original = tmp_path / "original input dir"
    original.mkdir()
    par, catg, stm = _original_triplet()
    for name, raw in (("model.par", par), ("catchment.catg", catg), ("storm.stm", stm)):
        (original / name).write_bytes(raw)
    destination = tmp_path / "imported case"
    destination.mkdir()
    project_file = destination / "model.json"
    project = import_rorb_project(
        project_file,
        identifier="s5_integrated",
        rainfall_profile="legacy-rorb",
        parameters=original / "model.par",
    )
    write_project(project_file, project)
    return project_file, original, (par, catg, stm)


def _git_blob(data: bytes) -> str:
    """Source Git object ID, not a hydrological model acceptance hash."""
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data, usedforsecurity=False).hexdigest()


def test_par_only_import_edit_save_run_and_native_package_relocation(tmp_path: Path) -> None:
    project, original_dir, input_bytes = _project(tmp_path)
    loaded = load_project(project)
    assert isinstance(loaded.run, RunModel)
    assert [item.origin for item in loaded.project.source_bindings] == ["explicit", "embedded", "embedded"]
    assert tuple((project.parent / item.staged.path).read_bytes() for item in loaded.project.source_bindings) == (
        input_bytes
    )
    assert loaded.project.engine.engine == "python-cmd"

    depth_tokens = [str(value + Decimal("1.25")) for value in loaded.run.storm.depths_mm]
    resolved = resolve_effective_model(
        loaded.run,
        ProjectEvent(
            "edited_event",
            routing={"kc": "12.75"},
            losses={"initial_loss_mm": "15.5"},
            storm={"depths_mm": depth_tokens},
        ),
    )
    assert resolved.event_id == "edited_event"
    assert resolved.run.catchment == loaded.run.catchment
    assert resolved.run.parameters.routing[0].kc == Decimal("12.75")
    assert resolved.run.storm.depths_mm != loaded.run.storm.depths_mm

    new_directory = tmp_path / "relocated editable project"
    new_directory.mkdir()
    saved = new_directory / "effective.json"
    save_project_as(project, saved, effective_run=resolved.run)
    shutil.rmtree(original_dir)
    shutil.rmtree(project.parent)
    reopened = load_project(saved)
    assert reopened.run == resolved.run
    assert reopened.project.effective_run == resolved.run
    assert tuple((saved.parent / item.staged.path).read_bytes() for item in reopened.project.source_bindings) == (
        input_bytes
    )
    single = run_engine_project(saved)
    repeated = run_project_events(saved, (ProjectEvent("same"),)).outcomes[0]
    assert single.status == repeated.status == "computed_unvalidated"
    assert single.model_sha256 == repeated.model_sha256
    assert single.hydrographs == repeated.hydrographs

    bundle = tmp_path / "new native export"
    receipt = export_cmd_package(saved, bundle, target=NativeCmdExportTarget("cmd-6.44"))
    assert receipt.native_execution == "not_run"
    assert receipt.numerical_equivalence == "not_assessed"
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["native_execution"] == "not_run"
    assert manifest["events"][0]["effective_settings"]["kc_m"][0]["kc"] == "12.75"

    package_moved = tmp_path / "moved package without Python"
    shutil.move(str(bundle), str(package_moved))
    shutil.rmtree(new_directory)
    native_dir = package_moved / "events" / "001"
    before = (native_dir / "model.par").read_bytes()
    parsed = parse_cmd_par(before).model
    assert parsed.catchment_reference == "catchment.catg"
    assert parsed.storm_reference == "storm.stm"
    for name in (parsed.catchment_reference, parsed.storm_reference):
        assert not Path(name).is_absolute()
        assert (native_dir / name).is_file()
    assert (native_dir / parsed.catchment_reference).read_bytes() == input_bytes[1]
    assert parse_catg((native_dir / parsed.catchment_reference).read_bytes()).model == resolved.run.catchment
    assert parse_design_stm((native_dir / parsed.storm_reference).read_bytes()).model == resolved.run.storm
    assert parsed.routing == resolved.run.parameters.routing
    assert parsed.losses == resolved.run.parameters.losses
    assert (native_dir / "model.par").read_bytes() == before
    assert b"python " not in (package_moved / "run.cmd").read_bytes().lower()


def test_invalid_override_and_unrepresentable_catchment_fail_closed(tmp_path: Path) -> None:
    project, _, _ = _project(tmp_path)
    loaded = load_project(project)
    with pytest.raises(EventConfigError, match="Mutually exclusive"):
        resolve_effective_model(
            loaded.run, ProjectEvent("bad", losses={"continuing": "2", "continuing_loss_mm_h": "2"})
        )
    with pytest.raises(ValueError, match="loss model"):
        replace(loaded.run.parameters, loss_model=True)
    with pytest.raises(ValueError, match="ISA"):
        replace(loaded.run.parameters, num_isa=True)
    with pytest.raises(FileExistsError):
        write_project(project, loaded.project)

    mode_two = replace(
        loaded.run,
        parameters=replace(
            loaded.run.parameters,
            loss_model=LossMode.INITIAL_RUNOFF_COEFFICIENT,
            losses=(replace(loaded.run.parameters.losses[0], continuing=Decimal("0.7")),),
        ),
    )
    selected = resolve_effective_model(mode_two, ProjectEvent("roc", losses={"runoff_coefficient": "0.65"}))
    assert selected.run.parameters.loss_model == LossMode.INITIAL_RUNOFF_COEFFICIENT
    assert selected.run.parameters.losses[0].continuing == Decimal("0.65")
    with pytest.raises(EventConfigError, match="loss mode"):
        resolve_effective_model(mode_two, ProjectEvent("invalid", losses={"continuing_loss_mm_h": "3"}))
    with pytest.raises(NativeExportError, match="PyRomb"):
        export_cmd_package(
            project,
            tmp_path / "not-written",
            target=NativeCmdExportTarget("cmd-6.44"),
            events=(
                NativeExportEvent(
                    "edited_catg", replace(loaded.run, catchment=replace(loaded.run.catchment, title="different"))
                ),
            ),
        )
    assert not (tmp_path / "not-written").exists()


def test_new_catg_invokes_actual_pinned_pyromb_writer(monkeypatch: pytest.MonkeyPatch) -> None:
    from runoff_routing import rorb_codec  # noqa: PLC0415 -- inspect the real selected writer module

    pyromb = importlib.import_module("pyromb.models.rorb")
    assert callable(getattr(pyromb, "render_ordered_catg", None))
    assert distribution("pyromb").metadata["Name"].lower() == "pyromb"
    assert pyromb.__file__ is not None
    assert not Path(pyromb.__file__).absolute().is_relative_to(Path(rorb_codec.__file__).absolute().parent)

    source = from_json((ROOT / "examples" / "synthetic-run.json").read_text(encoding="utf-8"))
    assert isinstance(source, RunModel)
    current = pyromb.render_ordered_catg
    called = 0

    def observing_writer(*args: object, **kwargs: object) -> str:
        nonlocal called
        called += 1
        return current(*args, **kwargs)

    monkeypatch.setattr(pyromb, "render_ordered_catg", observing_writer)
    emitted = serialize_catg(source.catchment)
    assert called == 1
    assert parse_catg(emitted).model == source.catchment


def test_original_rorbwin_652_reports_preserve_rows_frequencies_and_representatives() -> None:
    from ryan_library.functions.RORB import readers  # noqa: PLC0415 -- inspect actual third-party reader

    assert distribution("ryan-rorb-readers").metadata["Name"].lower() == "ryan-rorb-readers"
    assert readers.read_rorb_file is read_rorb_file
    assert readers.__file__ is not None
    assert not Path(readers.__file__).absolute().is_relative_to(ROOT / "src" / "runoff_routing")

    standard_path = RETENTION / "rorbwin652-12h-standard.out"
    batch_path = RETENTION / "rorbwin652-12h-batch.out"
    standard_bytes = standard_path.read_bytes()
    batch_bytes = batch_path.read_bytes()
    assert len(standard_bytes) == 19_020
    assert len(batch_bytes) == 8_558
    assert _git_blob(standard_bytes) == "95826bccdbe1f2410ef372ef6b6c2c161d847b99"
    assert _git_blob(batch_bytes) == "08ae1d94ef74d666836c8d3fab842e6421851030"

    standard = read_rorb_file(standard_path)
    assert standard.original_bytes == standard_bytes
    assert standard.sha256 == hashlib.sha256(standard_bytes).hexdigest()
    assert standard.kind == "standard_output"
    table = standard.section("hydrographs_1")
    assert table.valid
    assert len(table.rows) == 301
    projected = inspect_output(RorbSource.read(standard_path))
    assert projected.status == "partial"
    assert projected.hydrographs is not None
    assert len(projected.hydrographs.rows) == 301

    batch = read_rorb_file(batch_path)
    assert batch.original_bytes == batch_bytes
    assert batch.kind == "batch_output"
    runs = batch.section("runs")
    representatives = batch.section("representatives")
    assert runs.valid
    assert representatives.valid
    assert len(runs.rows) == 80
    assert len(representatives.rows) == 8
    frequencies = {str(row["aep_raw"]) for row in runs.rows}
    assert {"50%", "0.5EY", "20%", "0.2EY", "10%", "5%", "2%", "1%"} == frequencies
    counts = Counter(int(str(row["Run"])) for row in runs.rows)
    assert counts == dict.fromkeys(range(1, 9), 10)
    ids = {(int(str(row["Run"])), str(row["aep_raw"]), int(str(row["TPat"]))) for row in runs.rows}
    assert len(ids) == 80
    assert len({str(ref["reference"]) for ref in representatives.rows}) == 8
    assert all(str(ref["reference"]).endswith(".out") for ref in representatives.rows)
    assert {row["aep_kind"] for row in runs.rows} == {"percent", "EY"}
