"""Three-engine project contract and manufactured native process checks; no RORB launches."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from runoff_routing.engine_execution import run_engine_project, write_engine_result
from runoff_routing.engine_types import CAPABILITIES, EngineSelection
from runoff_routing.integration import canonical_run_bytes
from runoff_routing.native_cmd import NativeConfiguration
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
from runoff_routing.rorb_model import RunModel, from_json

EXAMPLE = Path(__file__).parents[1] / "examples" / "synthetic-run.json"


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


def test_v1_engine_less_migrates_to_default_python_and_v2_round_trip() -> None:
    new = json.loads(project_to_json(Project("example", "explicit", EmbeddedRun(_model()))))
    assert new["schema_version"] == 2
    assert new["engine"] == {"id": "python", "numerical_profile": "engineering-v1"}
    legacy = dict(new)
    legacy["schema_version"] = 1
    del legacy["engine"]
    migrated = project_from_json(json.dumps(legacy))
    assert migrated.engine == EngineSelection()
    assert project_from_json(project_to_json(migrated)) == migrated


def test_explicit_persisted_engine_and_override_precedence(tmp_path: Path) -> None:
    persisted = EngineSelection.for_engine("python-cmd")
    source = _project(tmp_path, persisted)
    unavailable = run_engine_project(source)
    assert unavailable.status == "unavailable_engine"
    assert unavailable.effective_selection == persisted
    assert unavailable.stored_selection == persisted
    assert unavailable.hydrographs == ()
    assert unavailable.diagnostics[0].code == "python_cmd_pending"
    with pytest.raises(ProjectError, match="Python-only"):
        run_project(source)
    computed = run_engine_project(source, selection=EngineSelection())
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
    failure = tmp_path / "unavailable.json"
    assert main(["run", str(source), str(failure)]) == 2
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["effective_engine"] == "python-cmd"
    report = json.loads(failure.read_text(encoding="utf-8"))
    assert report["status"] == "unavailable_engine"
    assert report["hydrographs"] == []
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
            (root / "native.out").write_text(
                "Time increment (hours)= 0.5\n"
                "Duration of calculations: 5\n"
                "Inc Time Hyd001\n" + "\n".join(rows) + "\nEnd\n",
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


@pytest.mark.parametrize("invalid", ["missing", "short", "negative"])
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
