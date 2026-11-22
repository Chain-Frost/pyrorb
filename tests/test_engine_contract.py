"""Three-engine project contract and manufactured native process checks; no RORB launches."""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import replace
from decimal import Decimal
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from zipfile import ZipFile

import pytest

from runoff_routing import engine_provenance
from runoff_routing.engine_execution import run_engine_project, write_engine_result
from runoff_routing.engine_provenance import identify_implementation
from runoff_routing.engine_types import CAPABILITIES, EngineSelection
from runoff_routing.integration import canonical_run_bytes
from runoff_routing.native_cmd import NativeConfiguration, NativeObservation
from runoff_routing.project_batch import ProjectEvent, run_project_events
from runoff_routing.project_execution import run_project
from runoff_routing.project_json import (
    EmbeddedRun,
    LegacyRunFiles,
    Project,
    ProjectError,
    SourceFile,
    main,
    project_from_json,
    project_to_json,
    write_project,
)
from runoff_routing.rorb_model import RoutingValue, RunModel, from_json

EXAMPLE = Path(__file__).parents[1] / "examples" / "synthetic-run.json"


def test_native_event_materializes_verified_files_without_changing_originals(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from runoff_routing import native_cmd  # noqa: PLC0415 -- patch the execution boundary, never launch RORB
    from runoff_routing.project_json import LoadedProject, load_project  # noqa: PLC0415 -- test-local boundary

    project_path = _legacy(tmp_path, EngineSelection.for_engine("rorb-cmd"))
    original = load_project(project_path)
    original_hashes = original.file_hashes
    config = _native_config(tmp_path)
    seen: list[LoadedProject] = []

    def observe(loaded: LoadedProject, native: NativeConfiguration, path: Path) -> NativeObservation:
        assert path.is_relative_to(config.output_root)
        assert loaded.original_inputs_match_effective()
        assert loaded.run.storm.depths_mm == (Decimal("12.03"),)
        assert loaded.run.parameters.losses[0].initial_loss_mm == Decimal("3.25")
        seen.append(loaded)
        return NativeObservation((), (), (), (), native.executable_sha256, "6.44", "0" * 64, "synthetic-capture")

    monkeypatch.setattr(native_cmd, "run_native_cmd", observe)
    report = run_project_events(
        project_path,
        (ProjectEvent("prepared_rain", storm={"depths_mm": ["12.03"]}, losses={"initial_loss_mm": "3.25"}),),
        selection=EngineSelection.for_engine("rorb-cmd"),
        native_config=config,
    )
    assert len(seen) == 1
    assert report.succeeded
    outcome = report.outcomes[0]
    manifest_path = Path(str(outcome.effective_inputs["native_prepared_package_manifest"]))
    assert (
        hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        == outcome.effective_inputs["native_prepared_package_sha256"]
    )
    package = json.loads(manifest_path.read_text())
    assert package["events"][0]["event_id"] == "prepared_rain"
    assert package["events"][0]["inputs"]["catchment"]["mode"] == "source_exact"
    assert package["events"][0]["inputs"]["storm"]["mode"] == "semantic_edit"
    assert load_project(project_path).file_hashes == original_hashes


def _model() -> RunModel:
    model = from_json(EXAMPLE.read_text(encoding="utf-8"))
    assert isinstance(model, RunModel)
    return model


def _project(root: Path, engine: EngineSelection | None = None) -> Path:
    path = root / "project.json"
    write_project(
        path, Project("synthetic_event", "explicit", EmbeddedRun(_model()), engine=engine or EngineSelection())
    )
    return path


def _legacy(root: Path, selection: EngineSelection) -> Path:
    model = _model()
    source_files: list[SourceFile] = []
    for name, data in zip(
        ("model.par", "model.catg", "model.stm"),
        canonical_run_bytes(model),
        strict=True,
    ):
        (root / name).write_bytes(data)
        source_files.append(SourceFile(name, hashlib.sha256(data).hexdigest()))
    target = root / "project.json"
    write_project(
        target,
        Project(
            "synthetic_native",
            "legacy-rorb",
            LegacyRunFiles(source_files[0], source_files[1], source_files[2]),
            engine=selection,
        ),
    )
    return target


def _native_config(root: Path) -> NativeConfiguration:
    binary = root / "mock-rorb-cmd.exe"
    binary.write_bytes(b"synthetic executable identity, never executed")
    return NativeConfiguration(
        executable=binary,
        executable_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
        observed_version="6.44",
        observed_banner="synthetic test only",
        numerical_profile="cmd-6.44",
        output_root=root / "captures",
        print_columns=(("print_1", "Hyd001"),),
        timeout_seconds=5,
    )


def test_v1_engine_less_preserves_python_and_new_schema2_defaults_to_python_cmd() -> None:
    new = json.loads(project_to_json(Project("example", "explicit", EmbeddedRun(_model()))))
    assert new["schema_version"] == 2
    assert new["engine"] == {"id": "python-cmd", "numerical_profile": "cmd-6.44"}
    legacy = dict(new)
    legacy["schema_version"] = 1
    del legacy["engine"]
    migrated = project_from_json(json.dumps(legacy))
    assert migrated.engine == EngineSelection.for_engine("python")
    assert project_from_json(project_to_json(migrated)) == migrated


def test_temporary_cmd_default_runs_offline_and_explicit_python_remains_selectable(tmp_path: Path) -> None:
    selected = EngineSelection()
    assert selected == EngineSelection.for_engine("python-cmd", "cmd-6.44")
    source = _project(tmp_path)
    stored = project_from_json(source.read_text(encoding="utf-8"))
    assert stored.engine == selected
    compatible = run_engine_project(source)
    assert compatible.status == "computed_unvalidated"
    assert compatible.effective_selection == compatible.stored_selection == selected
    assert compatible.selection_source == "project"
    assert compatible.python_diagnostics is not None
    assert compatible.python_diagnostics["cmd_profile"] == "cmd-6.44"
    engineering = run_engine_project(source, selection=EngineSelection.for_engine("python"))
    assert engineering.status == "computed_unvalidated"
    assert engineering.stored_selection == selected
    assert engineering.effective_selection == EngineSelection.for_engine("python")
    assert engineering.selection_source == "api_override"
    assert engineering.python_diagnostics is not None
    assert len(engineering.hydrographs[0].discharge_m3_s) == len(compatible.hydrographs[0].discharge_m3_s)


def test_explicit_persisted_engine_and_override_precedence(tmp_path: Path) -> None:
    persisted = EngineSelection.for_engine("python-cmd")
    source = _project(tmp_path, persisted)
    cmd_result = run_engine_project(source)
    assert cmd_result.status == "computed_unvalidated"
    assert cmd_result.effective_selection == persisted
    assert cmd_result.stored_selection == persisted
    assert cmd_result.hydrographs[0].print_id == "print_1"
    assert cmd_result.python_diagnostics is not None
    assert cmd_result.python_diagnostics["cmd_profile"] == "cmd-6.44"
    with pytest.raises(ProjectError, match="Python-only"):
        run_project(source)
    computed = run_engine_project(source, selection=EngineSelection.for_engine("python"))
    assert computed.status == "computed_unvalidated"
    assert computed.stored_selection == persisted
    assert computed.effective_selection.engine == "python"
    assert computed.selection_source == "api_override"
    assert computed.python_diagnostics is not None
    assert computed.internal_quantities == "python_available"
    assert len(computed.hydrographs[0].discharge_m3_s) == len(computed.physical_time_hours) == 6


def test_native_without_explicit_config_is_unavailable_and_does_not_fallback(tmp_path: Path) -> None:
    source = _project(tmp_path, EngineSelection.for_engine("rorb-cmd"))
    result = run_engine_project(source)
    assert result.status == "unavailable_engine"
    assert result.hydrographs == ()
    assert result.diagnostics[0].code == "native_config_required"


def test_cli_existing_result_rejects_before_native_execution(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = _legacy(tmp_path, EngineSelection.for_engine("rorb-cmd"))
    result = tmp_path / "result.json"
    result.write_bytes(b"preserve prior evidence")

    def unexpected_execution(*_args: object, **_kwargs: object) -> None:
        pytest.fail("An existing result must reject before computation or native execution")

    monkeypatch.setattr("runoff_routing.engine_execution.run_engine_project", unexpected_execution)
    assert main(["run", str(source), str(result)]) == 2
    assert result.read_bytes() == b"preserve prior evidence"


def test_capability_matrix_has_exact_three_stable_engines() -> None:
    assert tuple(item.engine for item in CAPABILITIES) == ("python", "python-cmd", "rorb-cmd")
    assert all(item.numerical_acceptance == "unassessed" for item in CAPABILITIES)


def test_engine_schema_rejects_unknown_engine_and_numerical_profile() -> None:
    data = json.loads(project_to_json(Project("example", "explicit", EmbeddedRun(_model()))))
    data["engine"]["id"] = "research"
    with pytest.raises(ProjectError, match="Unknown computation engine"):
        project_from_json(json.dumps(data))
    data["engine"] = {"id": "python", "numerical_profile": "cmd-6.44"}
    with pytest.raises(ProjectError, match="engineering-v1"):
        project_from_json(json.dumps(data))


def test_cli_records_stored_and_effective_engine_and_failure(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = _project(tmp_path, EngineSelection.for_engine("python-cmd"))
    output = tmp_path / "cmd.json"
    assert main(["run", str(source), str(output)]) == 0
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["effective_engine"] == "python-cmd"
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["status"] == "computed_unvalidated"
    assert len(report["hydrographs"][0]["discharge_m3_s"]) == 6
    success = tmp_path / "python.json"
    assert main(["run", str(source), str(success), "--engine", "python"]) == 0
    capsys.readouterr()
    calculated = json.loads(success.read_text(encoding="utf-8"))
    assert calculated["effective_selection"]["engine"] == "python"
    assert calculated["stored_selection"]["engine"] == "python-cmd"
    assert calculated["selection_source"] == "cli_override"
    assert main(["run", str(source), str(success), "--engine", "python"]) == 2
    capsys.readouterr()
    assert main(["run", str(source), str(tmp_path / "bad.json"), "--numerical-profile", "cmd-6.44"]) == 2
    assert not (tmp_path / "bad.json").exists()


def test_native_config_file_round_trip_and_wrong_fingerprint_preflight(tmp_path: Path) -> None:
    config = _native_config(tmp_path)
    settings = tmp_path / "local-native.json"
    settings.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "executable": config.executable.name,
                "executable_sha256": config.executable_sha256,
                "observed_version": config.observed_version,
                "observed_banner": config.observed_banner,
                "numerical_profile": config.numerical_profile,
                "output_root": "captures",
                "print_columns": {"print_1": "Hyd001"},
                "timeout_seconds": 5,
            }
        ),
        encoding="utf-8",
    )
    assert NativeConfiguration.from_file(settings) == config
    source = _legacy(tmp_path, EngineSelection.for_engine("rorb-cmd"))
    config.executable.write_bytes(b"tampered executable")
    result = run_engine_project(source, native_config=config)
    assert result.status == "unavailable_engine"
    assert result.diagnostics[0].code == "native_fingerprint"
    assert not config.output_root.exists()


def _mock_native(monkeypatch: pytest.MonkeyPatch, *, invalid: str | None = None) -> None:
    def fake_run(*_args: object, **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        root = kwargs["cwd"]
        assert isinstance(root, Path)
        assert (root / "reference.par").is_file()
        if invalid != "missing":
            rows = [
                f"{index + 1} {(index + 1) * 0.5:.2f} {float(index):.2f}"
                for index in range(6 if invalid != "short" else 5)
            ]
            if invalid == "negative":
                rows[-1] = "6 3.00 -1"
            if invalid == "duplicate":
                rows = [f"{row} {float(index):.2f}" for index, row in enumerate(rows)]
            header = "Inc Time Hyd001"
            if invalid == "duplicate":
                header = "Inc Time Hyd001 Hyd001"
            elif invalid == "unmapped":
                header = "Inc Time Hyd002"
            (root / "native.out").write_text(
                "Time increment (hours)= 0.5\n"
                "Duration of calculations: 5\n" + header + "\n" + "\n".join(rows) + "\nEnd\n",
                encoding="utf-8",
            )
        return subprocess.CompletedProcess(["mock"], 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)


def test_mocked_cmd_is_checked_and_has_distinct_raw_clocks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = _legacy(tmp_path, EngineSelection.for_engine("rorb-cmd"))
    before = (tmp_path / "model.par").read_bytes()
    config = _native_config(tmp_path)
    _mock_native(monkeypatch)
    outcome = run_engine_project(source, native_config=config)
    assert outcome.status == "computed_unvalidated"
    assert outcome.effective_selection.engine == "rorb-cmd"
    assert outcome.internal_quantities == "native_unavailable"
    assert outcome.python_diagnostics is None
    assert outcome.native_raw_increment_tokens == ("1", "2", "3", "4", "5", "6")
    assert outcome.native_raw_time_tokens[0] == "0.50"
    assert outcome.physical_time_hours[0] == "0.50"
    assert outcome.hydrographs[0].native_column_id == "Hyd001"
    assert outcome.hydrographs[0].native_discharge_tokens is not None
    assert outcome.hydrographs[0].discharge_m3_s[-1] == 5
    assert outcome.capture_manifest_path is not None
    assert Path(outcome.capture_manifest_path).exists()
    assert (tmp_path / "model.par").read_bytes() == before
    write_engine_result(tmp_path / "result.json", outcome)
    assert json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))["native_executable_sha256"]


@pytest.mark.parametrize("invalid", ["missing", "short", "negative", "duplicate", "unmapped"])
def test_zero_exit_is_not_sufficient_for_native_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, invalid: str
) -> None:
    source = _legacy(tmp_path, EngineSelection.for_engine("rorb-cmd"))
    config = _native_config(tmp_path)
    _mock_native(monkeypatch, invalid=invalid)
    result = run_engine_project(source, native_config=config)
    assert result.status == "incomplete_output"
    assert result.hydrographs == ()
    assert result.capture_manifest_path is not None
    assert Path(result.capture_manifest_path).exists()


def _manufactured_wheel(root: Path, *, altered: bool = False) -> Path:
    """Source-matched ZIP fixture; actual CI separately verifies a built wheel."""
    package_root = Path(__file__).parents[1] / "src" / "runoff_routing"
    wheel = root / "pyrorb-0.0.0.dev0-py3-none-any.whl"
    with ZipFile(wheel, mode="w") as archive:
        for path in sorted(package_root.rglob("*")):
            if not path.is_file() or not (path.suffix in (".py", ".pyi") or path.name == "py.typed"):
                continue
            contents = path.read_bytes()
            if altered and path.name == "engine_execution.py":
                contents += b"\n# manufactured mismatch\n"
            archive.writestr(f"runoff_routing/{path.relative_to(package_root).as_posix()}", contents)
    return wheel


@pytest.mark.parametrize("package_version", ["0.0.0.dev0", None])
def test_pyrorb_metadata_lookup_preserves_legacy_source_fingerprint(
    monkeypatch: pytest.MonkeyPatch, package_version: str | None
) -> None:
    def installed_version(name: str) -> str:
        assert name == "pyrorb"
        if package_version is None:
            raise PackageNotFoundError(name)
        return package_version

    monkeypatch.setattr(engine_provenance, "version", installed_version)
    monkeypatch.setattr(
        engine_provenance, "_installed_sources", lambda: {"runoff_routing/__init__.py": b"example = 1\n"}
    )
    identity = identify_implementation.__wrapped__()
    assert identity.package_version == package_version
    # Frozen package-code-v1 vector: display/distribution renames must retain the original hash domain.
    assert (
        identity.revision == "package-code-v1-sha256:4966c32e4e9540b4d64958bef19f8e618f3c7f8770229f51ac79581a3b55b260"
    )


def test_implementation_identity_is_exact_code_content_not_package_version(tmp_path: Path) -> None:
    project = _project(tmp_path, EngineSelection.for_engine("python"))
    python_result = run_engine_project(project)
    unavailable = run_engine_project(project, selection=EngineSelection.for_engine("python-cmd"))
    expected = identify_implementation()
    assert python_result.implementation_revision == expected.revision
    revision = python_result.implementation_revision
    assert revision is not None
    assert revision.startswith("package-code-v1-sha256:")
    assert len(revision.split(":")[-1]) == 64
    assert unavailable.implementation_revision == python_result.implementation_revision
    assert python_result.package_version == expected.package_version
    assert python_result.verified_wheel_sha256 is None


def test_explicit_matching_wheel_is_verified_in_result_and_cli(tmp_path: Path) -> None:
    source = _project(tmp_path)
    wheel = _manufactured_wheel(tmp_path)
    expected_sha = hashlib.sha256(wheel.read_bytes()).hexdigest()
    outcome = run_engine_project(source, wheel_artifact=wheel)
    assert outcome.status == "computed_unvalidated"
    assert outcome.verified_wheel_sha256 == expected_sha
    assert outcome.implementation_revision == identify_implementation().revision
    target = tmp_path / "wheel-report.json"
    assert main(["run", str(source), str(target), "--wheel-artifact", str(wheel)]) == 0
    receipt = json.loads(target.read_text(encoding="utf-8"))
    assert receipt["verified_wheel_sha256"] == expected_sha
    assert receipt["implementation_revision"] == outcome.implementation_revision


@pytest.mark.parametrize("altered", [True, False])
def test_missing_or_mismatched_wheel_fails_before_native_launch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, altered: bool
) -> None:
    source = _legacy(tmp_path, EngineSelection.for_engine("rorb-cmd"))
    config = _native_config(tmp_path)
    wheel = _manufactured_wheel(tmp_path, altered=True) if altered else tmp_path / "missing.whl"

    def prohibited(*_args: object, **_kwargs: object) -> None:
        pytest.fail("Wrong wheel attribution must fail before starting native CMD")

    monkeypatch.setattr("runoff_routing.engine_execution.run_native_cmd", prohibited)
    result = run_engine_project(source, native_config=config, wheel_artifact=wheel)
    assert result.status == "invalid_input"
    assert result.diagnostics[0].code == "wheel_identity"
    assert result.hydrographs == ()
    assert result.verified_wheel_sha256 is None
    assert result.implementation_revision == identify_implementation().revision
    assert not config.output_root.exists()


def _mark_first_wheel_entry_encrypted(wheel: Path) -> None:
    """Manufacture the encrypted ZIP flag without using an encrypted archive or native data."""
    data = bytearray(wheel.read_bytes())
    assert data[:4] == b"PK\x03\x04"
    central_header = data.index(b"PK\x01\x02")
    data[6] |= 1  # local-header general-purpose flag
    data[central_header + 8] |= 1  # matching central-directory flag
    wheel.write_bytes(data)
    with ZipFile(wheel) as archive:
        assert archive.infolist()[0].flag_bits & 1


def test_encrypted_wheel_is_structured_failure_before_native_launch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = _legacy(tmp_path, EngineSelection.for_engine("rorb-cmd"))
    config = _native_config(tmp_path)
    wheel = _manufactured_wheel(tmp_path)
    _mark_first_wheel_entry_encrypted(wheel)

    def unexpected_execution(*_args: object, **_kwargs: object) -> None:
        pytest.fail("Encrypted wheel must fail verification before native execution")

    monkeypatch.setattr("runoff_routing.engine_execution.run_native_cmd", unexpected_execution)
    result = run_engine_project(source, native_config=config, wheel_artifact=wheel)
    assert result.status == "invalid_input"
    assert result.diagnostics[0].code == "wheel_identity"
    assert "Encrypted wheel" in result.diagnostics[0].message
    assert result.hydrographs == ()
    assert result.verified_wheel_sha256 is None
    assert not config.output_root.exists()


@pytest.mark.parametrize("malformed", ["top-level-array", "print-columns", "timeout-seconds"])
def test_malformed_native_config_returns_cli_exit_two_without_dispatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    malformed: str,
) -> None:
    source = _legacy(tmp_path, EngineSelection.for_engine("rorb-cmd"))
    config = _native_config(tmp_path)
    settings: dict[str, object] = {
        "schema_version": 1,
        "executable": str(config.executable),
        "executable_sha256": config.executable_sha256,
        "observed_version": config.observed_version,
        "observed_banner": config.observed_banner,
        "numerical_profile": config.numerical_profile,
        "output_root": str(config.output_root),
        "print_columns": {"print_1": "Hyd001"},
        "timeout_seconds": config.timeout_seconds,
    }
    if malformed == "print-columns":
        settings["print_columns"] = ["Hyd001"]
    elif malformed == "timeout-seconds":
        settings["timeout_seconds"] = "not a number"
    payload: object = [] if malformed == "top-level-array" else settings
    local_config = tmp_path / "malformed-cmd.json"
    local_config.write_text(json.dumps(payload), encoding="utf-8")
    destination = tmp_path / "should-not-exist.json"

    def unexpected_execution(*_args: object, **_kwargs: object) -> None:
        pytest.fail("Malformed native configuration must not enter product dispatch")

    monkeypatch.setattr("runoff_routing.engine_execution.run_engine_project", unexpected_execution)
    assert main(["run", str(source), str(destination), "--native-config", str(local_config)]) == 2
    stderr = capsys.readouterr().err
    assert "Project execution failed:" in stderr
    assert "Traceback" not in stderr
    assert not destination.exists()
    assert not config.output_root.exists()


def test_relative_native_executable_is_absolute_in_staged_spec(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = _legacy(tmp_path, EngineSelection.for_engine("rorb-cmd"))
    config = _native_config(tmp_path)
    relative_config = replace(config, executable=Path(config.executable.name))
    _mock_native(monkeypatch)
    monkeypatch.chdir(tmp_path)
    result = run_engine_project(source, native_config=relative_config)
    assert result.status == "computed_unvalidated"
    assert result.native_executable_sha256 == config.executable_sha256
    assert result.capture_manifest_path is not None
    manifest = json.loads(Path(result.capture_manifest_path).read_text(encoding="utf-8"))
    assert manifest["engine"]["executable"]["sha256"] == config.executable_sha256


def test_default_engine_reports_actual_numerical_failure_not_feature_gap(tmp_path: Path) -> None:
    original = _model()
    parameters = replace(
        original.parameters,
        routing=(RoutingValue(1, Decimal("0.1"), Decimal("1.0")),),
    )
    storm = replace(
        original.storm,
        timestep_hours=Decimal(10),
        calculation_increments=6,
        percentages=(Decimal(100),),
        depths_mm=tuple(Decimal(20) for _ in original.storm.depths_mm),
    )
    numerical_event = replace(original, parameters=parameters, storm=storm)
    source = tmp_path / "numerical-failure.json"
    write_project(source, Project("numerical_failure", "explicit", EmbeddedRun(numerical_event)))
    result = run_engine_project(source, selection=EngineSelection.for_engine("python"))
    assert result.status == "numerical_error"
    assert result.hydrographs == ()
    assert result.diagnostics[0].code == "solver_numerical"
    assert "timestep" in result.diagnostics[0].message
