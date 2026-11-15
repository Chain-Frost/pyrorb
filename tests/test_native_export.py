"""Behavior tests for self-contained, exact-copy and edited native CMD input packages."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from runoff_routing.native_export import (
    NativeCmdExportTarget,
    NativeExportError,
    NativeExportEvent,
    export_cmd_package,
    main,
)
from runoff_routing.project_json import LegacyRunFiles, import_rorb_project, load_project, write_project
from runoff_routing.rorb_codec import parse_catg, parse_cmd_par, parse_design_stm
from runoff_routing.rorb_model import RunModel


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _original_project(tmp_path: Path) -> Path:
    """Use authenticated retained original CMD sources, not synthesized native goldens."""
    root = Path(__file__).parent / "fixtures" / "regression-v1"
    register = json.loads((root / "register.json").read_text(encoding="utf-8"))
    case = next(item for item in register["cases"] if item["case_id"] == "review-design-baseline")
    source_dir = tmp_path / "original files"
    source_dir.mkdir()
    selected: dict[str, Path] = {}
    for source in case["files"]:
        original = root / source["path"]
        if original.suffix not in {".par", ".catg", ".stm"}:
            continue
        copied = source_dir / f"native original {original.suffix}"
        copied.write_bytes(original.read_bytes())
        selected[original.suffix] = copied
    assert set(selected) == {".par", ".catg", ".stm"}
    project_path = tmp_path / "project.json"
    project = import_rorb_project(
        project_path,
        identifier="portable_cmd",
        rainfall_profile="legacy-rorb",
        parameters=selected[".par"],
        catchment=selected[".catg"],
        storm=selected[".stm"],
    )
    write_project(project_path, project)
    return project_path


def _model_from_emitted(directory: Path) -> RunModel:
    return RunModel(
        parse_cmd_par((directory / "model.par").read_bytes()).model,
        parse_catg((directory / "catchment.catg").read_bytes()).model,
        parse_design_stm((directory / "storm.stm").read_bytes()).model,
    )


def test_parameter_only_package_is_exact_copy_and_relocatable(tmp_path: Path) -> None:
    project_path = _original_project(tmp_path)
    loaded = load_project(project_path)
    old = loaded.run.parameters
    edited = replace(
        old,
        routing=(replace(old.routing[0], kc=Decimal("6.75"), m=Decimal("0.85")),),
        losses=(replace(old.losses[0], initial_loss_mm=Decimal(24), continuing=Decimal("5.5")),),
    )
    run = replace(loaded.run, parameters=edited)
    package = tmp_path / "export destination with spaces"
    receipt = export_cmd_package(
        project_path,
        package,
        target=NativeCmdExportTarget("cmd-6.44"),
        events=(NativeExportEvent("edited-event", run),),
    )
    assert receipt.destination == package
    assert receipt.native_execution == "not_run"
    assert receipt.numerical_equivalence == "not_assessed"

    old_files = loaded.project.model_source
    assert isinstance(old_files, LegacyRunFiles)
    manifest_data = (package / "manifest.json").read_bytes()
    manifest = json.loads(manifest_data)
    assert receipt.manifest_sha256 == _sha(manifest_data)
    assert manifest["target"] == {"dialect": "cmd_v2", "profile": "cmd-6.44", "native_version": "6.44"}
    event = manifest["events"][0]
    assert event["event_id"] == "edited-event"
    assert event["effective_settings"]["kc_m"][0]["kc"] == "6.75"
    assert event["effective_settings"]["kc_m"][0]["m"] == "0.85"
    assert event["inputs"]["catchment"]["source_bytes_equal"]
    assert event["inputs"]["storm"]["source_bytes_equal"]
    for role, suffix in (("catchment", ".catg"), ("storm", ".stm")):
        exported = package / "events" / "001" / f"{role}{suffix}"
        reference = old_files.catchment if role == "catchment" else old_files.storm
        source = project_path.parent / reference.path
        assert exported.read_bytes() == source.read_bytes()
        assert event["inputs"][role]["exported"]["sha256"] == _sha(source.read_bytes())
    assert event["inputs"]["parameters"]["mode"] == "rebound"
    assert _model_from_emitted(package / "events" / "001") == replace(
        run, parameters=replace(edited, catchment_reference="catchment.catg", storm_reference="storm.stm")
    )

    new_location = tmp_path / "moved bundle"
    shutil.move(str(package), str(new_location))
    shutil.rmtree(project_path.parent / "original files")
    assert _model_from_emitted(new_location / "events" / "001").parameters == replace(
        edited, catchment_reference="catchment.catg", storm_reference="storm.stm"
    )
    assert b"python " not in (new_location / "run.cmd").read_bytes().lower()
    assert b"RORB_CMD" in (new_location / "run.cmd").read_bytes()
    assert manifest["events"][0]["requested_outputs"]["actual_output_filenames"] == "not_characterised"


@pytest.mark.parametrize("verbosity", [1, 2, 3])
def test_native_verbosity_is_not_forced_to_three(tmp_path: Path, verbosity: int) -> None:
    project_path = _original_project(tmp_path)
    model = load_project(project_path).run
    effective = replace(model, parameters=replace(model.parameters, verbosity=verbosity))
    package = tmp_path / f"v{verbosity}"
    export_cmd_package(
        project_path,
        package,
        target=NativeCmdExportTarget("cmd-6.44"),
        events=(NativeExportEvent("mode", effective),),
    )
    exported = parse_cmd_par((package / "events" / "001" / "model.par").read_bytes()).model
    assert exported.verbosity == verbosity
    manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["events"][0]["requested_outputs"]["native_verbosity"] == verbosity
    assert manifest["native_execution"] == "not_run"


def test_selected_batch_is_isolated_and_storm_edit_is_semantic(tmp_path: Path) -> None:
    project_path = _original_project(tmp_path)
    original = load_project(project_path).run
    changed_storm = replace(original.storm, depths_mm=tuple(value * 2 for value in original.storm.depths_mm))
    other = replace(
        original,
        parameters=replace(original.parameters, routing=(replace(original.parameters.routing[0], kc=Decimal(9)),)),
        storm=changed_storm,
    )
    package = tmp_path / "independent events"
    export_cmd_package(
        project_path,
        package,
        target=NativeCmdExportTarget("cmd-6.44"),
        events=(NativeExportEvent("baseline", original), NativeExportEvent("storm-and-kc", other)),
    )
    manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    assert [item["event_id"] for item in manifest["events"]] == ["baseline", "storm-and-kc"]
    assert [item["ordinal"] for item in manifest["events"]] == [1, 2]
    assert manifest["events"][0]["inputs"]["storm"]["mode"] == "source_exact"
    assert manifest["events"][1]["inputs"]["storm"]["mode"] == "semantic_edit"
    assert not manifest["events"][1]["inputs"]["storm"]["source_bytes_equal"]
    assert (package / "events" / "001" / "storm.stm").read_bytes() != (
        package / "events" / "002" / "storm.stm"
    ).read_bytes()
    assert _model_from_emitted(package / "events" / "002").storm == changed_storm
    launcher = (package / "run.cmd").read_bytes()
    assert b"events\\001" in launcher
    assert b"events\\002" in launcher


def test_failures_leave_no_misleading_partial_output(tmp_path: Path) -> None:
    project_path = _original_project(tmp_path)
    base = load_project(project_path).run
    unsupported = replace(base, catchment=replace(base.catchment, title="edited geometry"))
    destination = tmp_path / "should not exist"
    with pytest.raises(NativeExportError, match="PyRomb"):
        export_cmd_package(
            project_path,
            destination,
            target=NativeCmdExportTarget("cmd-6.44"),
            events=(NativeExportEvent("good", base), NativeExportEvent("unrepresentable", unsupported)),
        )
    assert not destination.exists()
    assert not tuple(tmp_path.glob(".native-cmd-stage-*"))
    with pytest.raises(NativeExportError, match="Duplicate"):
        export_cmd_package(
            project_path,
            destination,
            target=NativeCmdExportTarget("cmd-6.44"),
            events=(NativeExportEvent("X", base), NativeExportEvent("x", base)),
        )
    assert not destination.exists()
    with pytest.raises(NativeExportError, match="at least one"):
        export_cmd_package(project_path, destination, target=NativeCmdExportTarget("cmd-6.44"), events=())
    assert not destination.exists()


def test_refuse_overwrite_and_unsupported_target(tmp_path: Path) -> None:
    project_path = _original_project(tmp_path)
    destination = tmp_path / "existing"
    destination.mkdir()
    marker = destination / "keep.txt"
    marker.write_text("original", encoding="utf-8")
    with pytest.raises(FileExistsError, match="already exists"):
        export_cmd_package(project_path, destination, target=NativeCmdExportTarget("cmd-6.44"))
    assert marker.read_text(encoding="utf-8") == "original"
    with pytest.raises(NativeExportError, match=r"only RORB CMD 6\.44"):
        NativeCmdExportTarget("cmd-6.45")


def test_json_event_request_cli_reuses_existing_override_derivation(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    project_path = _original_project(tmp_path)
    requests = tmp_path / "events.json"
    requests.write_text(
        json.dumps(
            {
                "format": "python-runoff-routing-explicit-events",
                "schema_version": 1,
                "events": [
                    {"event_id": "first", "routing": {"kc": "7.5"}},
                    {"event_id": "second", "losses": {"initial_loss_mm": "19", "continuing_loss_mm_h": "5"}},
                ],
            }
        ),
        encoding="utf-8",
    )
    destination = tmp_path / "cli bundle"
    assert main([str(project_path), str(destination), "--target", "cmd-6.44", "--events", str(requests)]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["event_ids"] == ["first", "second"]
    assert _model_from_emitted(destination / "events" / "001").parameters.routing[0].kc == Decimal("7.5")
    assert _model_from_emitted(destination / "events" / "002").parameters.losses[0].initial_loss_mm == Decimal(19)
    assert _model_from_emitted(destination / "events" / "002").parameters.losses[0].continuing == Decimal(5)
    assert main([str(project_path), str(destination), "--target", "cmd-6.44"]) == 2
    assert "already exists" in capsys.readouterr().err


def test_hash_mismatch_refuses_export(tmp_path: Path) -> None:
    project_path = _original_project(tmp_path)
    original = project_path.parent / "original files" / "native original .catg"
    original.write_bytes(original.read_bytes() + b"\n")
    destination = tmp_path / "not published"
    with pytest.raises(ValueError, match="SHA-256"):
        export_cmd_package(project_path, destination, target=NativeCmdExportTarget("cmd-6.44"))
    assert not destination.exists()


@pytest.mark.skipif(sys.platform != "win32", reason="Requires Windows cmd.exe / where.exe")
def test_windows_launcher_passes_actual_par_argument_and_propagates_failures(tmp_path: Path) -> None:
    """A system where.exe stub proves cwd/argv; it is not native RORB execution."""
    project_path = _original_project(tmp_path)
    model = load_project(project_path).run
    package = tmp_path / "native package with spaces"
    export_cmd_package(
        project_path,
        package,
        target=NativeCmdExportTarget("cmd-6.44"),
        events=(NativeExportEvent("first", model), NativeExportEvent("second", model)),
    )
    relocated = tmp_path / "recipient directory with spaces"
    shutil.move(str(package), str(relocated))
    shutil.rmtree(project_path.parent / "original files")
    system_where = Path(os.environ["SYSTEMROOT"]) / "System32" / "where.exe"
    assert system_where.is_file()
    command = [str(relocated / "run.cmd"), str(system_where)]
    success = subprocess.run(  # noqa: S603 -- explicit package script and fixed Windows utility; no shell
        command,
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert success.returncode == 0
    stdout = success.stdout.casefold()
    assert r"events\001\model.par" in stdout
    assert r"events\002\model.par" in stdout

    # Simulate a broken second event *after* export to verify failure propagation,
    # not to claim that this modified package remains a valid native input set.
    (relocated / "events" / "002" / "model.par").unlink()
    failure = subprocess.run(  # noqa: S603 -- same fixed executable, deliberate negative acceptance
        command,
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert failure.returncode != 0
    assert r"events\001\model.par" in failure.stdout.casefold()
    assert r"events\002\model.par" not in failure.stdout.casefold()
