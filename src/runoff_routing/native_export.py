"""Portable, relocatable RORB CMD V2 project export; no native process is launched.

The package layer consumes resolved immutable events. Import/editing and the
effective-event contract belong to the project owners; graphical CATG rendering
belongs to PyRomb. Source-exact unchanged CATG is usable before that writer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from .project_json import MAX_SOURCE_BYTES, LegacyRunFiles, LoadedProject, SourceFile, load_project
from .rorb_codec import FormatProblem, parse_catg, parse_cmd_par, parse_design_stm, serialize_cmd_par, serialize_design_stm
from .rorb_model import RunModel, to_json

_EVENT_ID = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,127}\Z")
_TARGET_PROFILE = "cmd-6.44"


class NativeExportError(ValueError):
    """An unsupported or unsafe native export, never a native-execution verdict."""


@dataclass(frozen=True, slots=True)
class NativeCmdExportTarget:
    """Explicit CMD dialect/profile, not a choice of Python execution engine."""

    profile: str
    native_version: str = "6.44"

    def __post_init__(self) -> None:
        if self.profile != _TARGET_PROFILE or self.native_version != "6.44":
            message = "Portable native export currently supports only RORB CMD 6.44 / cmd-6.44"
            raise NativeExportError(message)


@dataclass(frozen=True, slots=True)
class NativeExportEvent:
    """Already-resolved effective event; the caller owns deriving its overrides."""

    event_id: str
    run: RunModel

    def __post_init__(self) -> None:
        if not isinstance(self.event_id, str) or _EVENT_ID.fullmatch(self.event_id) is None:
            message = "Native export event IDs must be unique stable ASCII identifiers"
            raise NativeExportError(message)
        if not isinstance(self.run, RunModel):
            message = "Native export requires a fully resolved RunModel for every event"
            raise NativeExportError(message)


@dataclass(frozen=True, slots=True)
class NativeExportReceipt:
    """A published input package; execution and numerical equivalence are not assessed."""

    destination: Path
    manifest_sha256: str
    event_ids: tuple[str, ...]
    target_profile: str
    native_execution: str = "not_run"
    numerical_equivalence: str = "not_assessed"

    def to_json(self) -> str:
        return (
            json.dumps(
                {
                    "destination": str(self.destination),
                    "manifest_sha256": self.manifest_sha256,
                    "event_ids": list(self.event_ids),
                    "target_profile": self.target_profile,
                    "native_execution": self.native_execution,
                    "numerical_equivalence": self.numerical_equivalence,
                },
                sort_keys=True,
                indent=2,
            )
            + "\n"
        )


@dataclass(frozen=True, slots=True)
class _OriginalInputs:
    files: LegacyRunFiles
    parameters: bytes
    catchment: bytes
    storm: bytes
    run: RunModel


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_pinned(directory: Path, source: SourceFile) -> bytes:
    """Recheck containment, size and hash at copy time, not only at project-load time."""
    try:
        base = directory.resolve(strict=True)
        selected = (directory / source.path).resolve(strict=True)
        if not selected.is_relative_to(base) or not selected.is_file():
            message = f"Native export source escapes the project or is not a file: {source.path}"
            raise NativeExportError(message)
        size = selected.stat().st_size
        if size > MAX_SOURCE_BYTES:
            message = f"Native export source exceeds size limit: {source.path}"
            raise NativeExportError(message)
        payload = selected.read_bytes()
    except OSError as exc:
        message = f"Native export cannot read source: {source.path}"
        raise NativeExportError(message) from exc
    if len(payload) > MAX_SOURCE_BYTES or _sha256(payload) != source.sha256:
        message = f"Native export source changed or failed SHA-256: {source.path}"
        raise NativeExportError(message)
    return payload


def _original_inputs(loaded: LoadedProject, project_path: Path) -> _OriginalInputs:
    files = loaded.project.model_source
    if not isinstance(files, LegacyRunFiles) or loaded.project.rainfall_profile != "legacy-rorb":
        message = "CMD package export requires hash-pinned CMD PAR, graphical CATG and DESIGN STM sources"
        raise NativeExportError(message)
    if any(asset.role != "reference" for asset in loaded.project.assets):
        message = "Native export cannot package unresolved rainfall, temporal-pattern or curve assets"
        raise NativeExportError(message)
    directory = project_path.absolute().parent
    parameters = _read_pinned(directory, files.parameters)
    catchment = _read_pinned(directory, files.catchment)
    storm = _read_pinned(directory, files.storm)
    try:
        run = RunModel(parse_cmd_par(parameters).model, parse_catg(catchment).model, parse_design_stm(storm).model)
    except (FormatProblem, TypeError, ValueError) as exc:
        message = f"Native CMD sources are not the characterised three-file model: {exc}"
        raise NativeExportError(message) from exc
    return _OriginalInputs(files, parameters, catchment, storm, run)


def _events(loaded: LoadedProject, events: tuple[NativeExportEvent, ...] | None) -> tuple[NativeExportEvent, ...]:
    selected = (NativeExportEvent("default", loaded.run),) if events is None else events
    if not selected:
        message = "Native export requires at least one selected event"
        raise NativeExportError(message)
    names: set[str] = set()
    for event in selected:
        if not isinstance(event, NativeExportEvent):
            message = "Native export events must be NativeExportEvent records"
            raise NativeExportError(message)
        folded = event.event_id.casefold()
        if folded in names:
            message = f"Duplicate native export event ID: {event.event_id}"
            raise NativeExportError(message)
        names.add(folded)
    return selected


def _written(root: Path, relative: Path, data: bytes) -> dict[str, Any]:
    file_path = root / relative
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("xb") as stream:
        stream.write(data)
    return {"path": relative.as_posix(), "sha256": _sha256(data), "bytes": len(data)}


def _role_record(
    source: SourceFile, original: bytes, output: dict[str, Any], data: bytes, *, mode: str
) -> dict[str, Any]:
    return {
        "original": {"path": source.path, "sha256": source.sha256, "bytes": len(original)},
        "exported": output,
        "mode": mode,
        "source_bytes_equal": data == original,
    }


def _reparse_staged(
    event_dir: Path, cat_name: str, intended: RunModel
) -> None:
    """Prove the actual staged PAR/CATG/STM recover the selected effective model."""
    try:
        recovered = RunModel(
            parse_cmd_par((event_dir / "model.par").read_bytes()).model,
            parse_catg((event_dir / cat_name).read_bytes()).model,
            parse_design_stm((event_dir / "storm.stm").read_bytes()).model,
        )
    except (OSError, FormatProblem, TypeError, ValueError) as exc:
        message = f"Emitted CMD inputs do not reparse: {exc}"
        raise NativeExportError(message) from exc
    if recovered != intended:
        message = "Emitted native files do not recover the selected effective model; export aborted"
        raise NativeExportError(message)


def _stage_event(
    root: Path, ordinal: int, event: NativeExportEvent, source: _OriginalInputs
) -> dict[str, Any]:
    model = event.run
    if model.catchment != source.run.catchment:
        message = (
            f"Event {event.event_id}: edited CATG needs the #139 PyRomb writer; "
            "no local CATG renderer or patch fallback is permitted"
        )
        raise NativeExportError(message)
    cat_suffix = Path(source.files.catchment.path).suffix.lower()
    if cat_suffix not in {".cat", ".catg"}:
        message = "Only modern graphical .catg and characterised graphical .cat aliases can be exported"
        raise NativeExportError(message)
    cat_name = f"catchment{cat_suffix}"
    storm_changed = model.storm != source.run.storm
    try:
        stm_data = serialize_design_stm(model.storm) if storm_changed else source.storm
        parameters = replace(model.parameters, catchment_reference=cat_name, storm_reference="storm.stm")
        par_data = serialize_cmd_par(parameters)
        intended = RunModel(parameters, model.catchment, model.storm)
    except (NotImplementedError, TypeError, ValueError) as exc:
        message = f"Event {event.event_id}: effective CMD settings cannot be written: {exc}"
        raise NativeExportError(message) from exc

    relative = Path("events") / f"{ordinal:03d}"
    event_dir = root / relative
    cat_output = _written(root, relative / cat_name, source.catchment)
    stm_output = _written(root, relative / "storm.stm", stm_data)
    par_output = _written(root, relative / "model.par", par_data)
    _reparse_staged(event_dir, cat_name, intended)
    return {
        "event_id": event.event_id,
        "ordinal": ordinal,
        "effective_model_sha256": _sha256(to_json(model).encode("utf-8")),
        "native_effective_model_sha256": _sha256(to_json(intended).encode("utf-8")),
        "effective_settings": {
            "kc_m": [{"isa": v.isa, "kc": str(v.kc), "m": str(v.m)} for v in parameters.routing],
            "loss_model": int(parameters.loss_model),
            "losses": [
                {
                    "isa": v.isa,
                    "burst": v.burst,
                    "initial_loss_mm": str(v.initial_loss_mm),
                    "continuing": str(v.continuing),
                }
                for v in parameters.losses
            ],
            "verbosity": int(parameters.verbosity),
            "storm_timestep_hours": str(model.storm.timestep_hours),
            "calculation_increments": model.storm.calculation_increments,
        },
        "inputs": {
            "parameters": _role_record(source.files.parameters, source.parameters, par_output, par_data, mode="rebound"),
            "catchment": _role_record(
                source.files.catchment, source.catchment, cat_output, source.catchment, mode="source_exact"
            ),
            "storm": _role_record(
                source.files.storm,
                source.storm,
                stm_output,
                stm_data,
                mode="semantic_edit" if storm_changed else "source_exact",
            ),
        },
        "invocation": {
            "working_directory": relative.as_posix(),
            "argv": ["<operator-supplied RORB CMD 6.44 executable>", "model.par"],
        },
        "requested_outputs": {
            "directory": relative.as_posix(),
            "native_verbosity": int(parameters.verbosity),
            "actual_output_filenames": "not_characterised",
        },
        "native_execution": "not_run",
        "numerical_equivalence": "not_assessed",
    }


def _launcher(number_of_events: int) -> bytes:
    """Native Windows CMD launcher: neither Python nor a bundled executable is used."""
    lines = [
        "@echo off",
        "setlocal",
        'if "%~1"=="" (',
        '  echo Usage: run.cmd "C:\\full\\path\\to\\RORB_CMD.exe" 1>&2',
        "  exit /b 2",
        ")",
        'set "NATIVE_EXE=%~1"',
        'if not exist "%NATIVE_EXE%" (',
        "  echo RORB CMD executable not found 1>&2",
        "  exit /b 2",
        ")",
        'set "FAILED=0"',
    ]
    for ordinal in range(1, number_of_events + 1):
        lines.extend((f'call :run_case "events\\{ordinal:03d}"', 'if errorlevel 1 set "FAILED=1"'))
    lines.extend(
        (
            "exit /b %FAILED%",
            ":run_case",
            'pushd "%~dp0%~1"',
            "if errorlevel 1 exit /b 2",
            '"%NATIVE_EXE%" "model.par"',
            'set "CASE_RESULT=%errorlevel%"',
            "popd",
            "exit /b %CASE_RESULT%",
        )
    )
    return ("\r\n".join(lines) + "\r\n").encode("ascii")


def _readme(target: NativeCmdExportTarget, selected: tuple[NativeExportEvent, ...]) -> bytes:
    lines = [
        f"Portable RORB CMD project inputs - native target {target.native_version} ({target.profile})",
        "",
        "This package contains native CMD inputs only. It does not include a RORB executable,",
        "Python, the original project directory or an executable fingerprint.",
        "",
        "On Windows, supply the actual local RORB CMD 6.44 executable:",
        '  run.cmd "C:\\full\\path\\to\\RORB_CMD.exe"',
        "",
        "The launcher changes working directory to each event folder and invokes",
        'the supplied native executable with exactly "model.par" as its argument.',
        "Each PAR references the CATG and STM in that same folder by relative name.",
        "For manual invocation, change into the event folder and run:",
        '  "C:\\full\\path\\to\\RORB_CMD.exe" "model.par"',
        "",
        "Event folders in stable request order:",
    ]
    lines.extend(f"  events/{ordinal:03d}  event_id={event.event_id}" for ordinal, event in enumerate(selected, start=1))
    lines.extend(
        (
            "",
            "Output files, report content and optional verbosity-dependent artifacts are",
            "created by the installed native executable; names and availability have not",
            "been verified by export. Existing output files are not managed by this package.",
            "The manifest records the requested native verbosity without raising it to 3.",
            "",
            "Package creation re-parses each emitted native input and authenticates copied",
            "bytes, but no native command or numerical comparator has been run.",
            "For a native acceptance record execute the actual relocated model.par,",
            "preserve its SHA-256 before and after, and record the executable SHA-256,",
            "exact command, working directory, observed outputs and numerical findings.",
            "",
        )
    )
    return "\n".join(lines).encode("utf-8")


def export_cmd_package(
    project_path: Path,
    destination: Path,
    *,
    target: NativeCmdExportTarget,
    events: tuple[NativeExportEvent, ...] | None = None,
) -> NativeExportReceipt:
    """Stage, validate, then publish an exclusive native-only CMD input package.

    Only original graphical catchment bytes are currently accepted; when a
    catchment changes, the PyRomb writer owner supplies the edited-asset adapter.
    No Python numerical engine is selected or executed by this function.
    """
    if not isinstance(target, NativeCmdExportTarget):
        message = "An explicit NativeCmdExportTarget is required"
        raise NativeExportError(message)
    target.__post_init__()
    project = load_project(project_path)
    original = _original_inputs(project, project_path)
    selected = _events(project, events)
    chosen = destination.absolute()
    if chosen.exists() or chosen.is_symlink():
        message = f"Native export destination already exists: {chosen}"
        raise FileExistsError(message)
    parent = chosen.parent.resolve(strict=True)
    with TemporaryDirectory(prefix=".native-cmd-stage-", dir=parent) as scratch:
        staging = Path(scratch) / "package"
        staging.mkdir()
        records = tuple(_stage_event(staging, index, item, original) for index, item in enumerate(selected, start=1))
        manifest: dict[str, Any] = {
            "format": "python-runoff-routing-native-cmd-package",
            "schema_version": 1,
            "target": {"dialect": "cmd_v2", "profile": target.profile, "native_version": target.native_version},
            "source_project": {
                "project_id": project.project.identifier,
                "sha256": _sha256(project.original_json_bytes),
                "stored_engine": project.project.engine.engine,
                "stored_engine_profile": project.project.engine.numerical_profile,
            },
            "required_input_roles": ["parameters", "catchment", "storm"],
            "native_executable_included": False,
            "native_execution": "not_run",
            "numerical_equivalence": "not_assessed",
            "events": list(records),
        }
        serialized = (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
        _written(staging, Path("manifest.json"), serialized)
        _written(staging, Path("README.txt"), _readme(target, selected))
        _written(staging, Path("run.cmd"), _launcher(len(selected)))
        if chosen.exists() or chosen.is_symlink():
            message = f"Native export destination appeared during staging: {chosen}"
            raise FileExistsError(message)
        # A same-filesystem rename publishes only complete, already-validated inputs.
        # stdlib rename's preflight is not an atomic no-replace guarantee against
        # another process racing to create an empty directory on POSIX.
        os.rename(staging, chosen)
    return NativeExportReceipt(chosen, _sha256(serialized), tuple(item.event_id for item in selected), target.profile)


def _requested_events(project_path: Path, requests: Path) -> tuple[NativeExportEvent, ...]:
    """Consume the existing #119 event derivation, not an independent override grammar."""
    from .project_batch import (  # noqa: PLC0415 -- CLI-only dependency; avoids project dispatcher import loops
        _event_run,  # pyright: ignore[reportPrivateUsage] -- #138 will publish the shared effective-run boundary
        _request_fields,  # pyright: ignore[reportPrivateUsage] -- same #119 event source/validation contract
        load_event_request,
    )

    loaded = load_project(project_path)
    selected: list[NativeExportEvent] = []
    for item in load_event_request(requests):
        fields = _request_fields(item)
        identifier = fields.get("event_id")
        if not isinstance(identifier, str):
            message = "Every native export event must have an explicit event_id"
            raise NativeExportError(message)
        effective_run, _ = _event_run(loaded, fields)
        selected.append(NativeExportEvent(identifier, effective_run))
    return tuple(selected)


def main(argv: list[str] | None = None) -> int:
    """Standalone CLI until the #140 project dispatcher integrates this handler."""
    parser = argparse.ArgumentParser(prog="python -m runoff_routing.native_export")
    parser.add_argument("project", type=Path, help="hash-verified RORB CMD JSON project")
    parser.add_argument("destination", type=Path, help="new portable package directory, no overwrite")
    parser.add_argument("--target", choices=(_TARGET_PROFILE,), required=True)
    parser.add_argument("--events", type=Path, help="existing versioned #119 explicit event request")
    arguments = parser.parse_args(argv)
    try:
        target = NativeCmdExportTarget(arguments.target)
        events = _requested_events(arguments.project, arguments.events) if arguments.events is not None else None
        receipt = export_cmd_package(arguments.project, arguments.destination, target=target, events=events)
    except (OSError, TypeError, ValueError) as exc:
        print(f"Native CMD export failed: {exc}", file=sys.stderr)
        return 2
    print(receipt.to_json(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
