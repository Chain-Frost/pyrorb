"""PAR-led, byte-preserving source discovery and explicit path selection.

Source location is a one-time import decision. Saved projects refer only to
staged hash-pinned files, never old source trees or guessed drive mappings.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path, PureWindowsPath
from typing import TYPE_CHECKING, Literal

from .rorb_codec import FormatProblem, parse_catg, parse_cmd_par, parse_design_stm
from .rorb_model import RunModel
from .rorb_par import inspect_par_bytes

if TYPE_CHECKING:
    from .project_json import Project, RainfallProfile

InputRole = Literal["parameters", "catchment", "storm"]
InputOrigin = Literal["explicit", "embedded", "override"]
SelectedSource = tuple[InputRole, str, str, InputOrigin, Path, bytes]


def _reference_path(token: str, *, role: InputRole, base: Path, override_flag: str) -> Path:
    """Resolve a token deliberately, without foreign drive mapping or CWD search."""
    from .project_json import ProjectError  # noqa: PLC0415 -- import boundary avoids cycle

    value = token.strip()
    if len(value) >= 2 and value[0] in {"'", '"'} and value[-1] == value[0]:
        value = value[1:-1]
    elif value.startswith(("'", '"')) or value.endswith(("'", '"')):
        message = f"Unbalanced quotes in {role} reference {token!r}; use {override_flag}"
        raise ProjectError(message)
    if not value or any(ord(char) < 32 for char in value):
        message = f"Invalid {role} reference {token!r}; use {override_flag}"
        raise ProjectError(message)
    windows = PureWindowsPath(value)
    if windows.drive:
        if os.name != "nt":
            message = (
                f"{role} reference {token!r} is an unresolved foreign Windows drive/UNC path; "
                f"use {override_flag} with a local file"
            )
            raise ProjectError(message)
        if not windows.is_absolute():
            message = f"Drive-relative {role} reference {token!r} is ambiguous; use {override_flag}"
            raise ProjectError(message)
    elif value.startswith("\\") and os.name != "nt":
        message = f"Windows-rooted {role} reference {token!r} is ambiguous; use {override_flag}"
        raise ProjectError(message)
    local = Path(value if os.name == "nt" else value.replace("\\", "/"))
    return local.absolute() if local.is_absolute() else (base / local).absolute()


def _selected_input(
    role: Literal["catchment", "storm"], declared: str, explicit: Path | None, base: Path
) -> SelectedSource:
    from .project_json import ProjectError, _read_bounded  # noqa: PLC0415 -- filesystem adapter boundary

    selected = str(explicit) if explicit is not None else declared
    origin: InputOrigin = "override" if explicit is not None else "embedded"
    flag = f"--{role}"
    path = _reference_path(selected, role=role, base=base, override_flag=flag)
    if not path.is_file():
        message = (
            f"Missing {role} input: declared {declared!r}, selected {selected!r}. "
            f"Provide {flag} FILE to override the PAR reference."
        )
        raise ProjectError(message)
    try:
        contents = _read_bounded(path)
    except ProjectError as exc:
        message = f"Cannot read {role} input: declared {declared!r}, selected {selected!r}; use {flag} FILE: {exc}"
        raise ProjectError(message) from exc
    suffixes = (".catg", ".cat") if role == "catchment" else (".stm",)
    if path.suffix.lower() not in suffixes:
        message = f"Unsupported {role} input type {path.suffix!r}: {selected!r}; use {flag} FILE"
        raise ProjectError(message)
    return role, declared, selected, origin, path, contents


def _create_staged_directory(root: Path, destination: Path) -> Path:
    from .project_json import ProjectError  # noqa: PLC0415 -- filesystem adapter boundary

    staged_dir = root / "sources" / destination.stem
    if staged_dir.parent.is_symlink() or staged_dir.exists() or staged_dir.is_symlink():
        message = f"Unsafe or occupied staged source directory: {staged_dir}"
        raise ProjectError(message)
    staged_dir.mkdir(parents=True)
    if not staged_dir.resolve(strict=True).is_relative_to(root.resolve(strict=True)):
        message = f"Staged source directory escapes project destination: {staged_dir}"
        staged_dir.rmdir()
        raise ProjectError(message)
    return staged_dir


def _stage_selected(
    root: Path,
    destination: Path,
    selected: list[SelectedSource],
    *,
    identifier: str,
    rainfall_profile: RainfallProfile,
) -> Project:
    from .project_json import (  # noqa: PLC0415 -- typed project model is the shared project boundary
        LegacyRunFiles,
        Project,
        SourceBinding,
        SourceFile,
        _safe_relative,
    )

    records: list[tuple[SelectedSource, SourceFile]] = []
    for source in selected:
        role, _, _, _, path, raw = source
        suffix = ".par" if role == "parameters" else path.suffix.lower()
        relative = f"sources/{destination.stem}/{role}{suffix}"
        _safe_relative(relative)
        pinned = SourceFile(relative, hashlib.sha256(raw).hexdigest())
        records.append((source, pinned))

    model_sources = LegacyRunFiles(records[0][1], records[1][1], records[2][1])
    bindings = tuple(
        SourceBinding(role, declared, selected_name, origin, str(path), pinned)
        for (role, declared, selected_name, origin, path, _), pinned in records
    )
    project = Project(identifier, rainfall_profile, model_sources, source_bindings=bindings)
    stage_dir = _create_staged_directory(root, destination)
    try:
        for source, pinned in records:
            with (root / pinned.path).open("xb") as output:
                output.write(source[-1])
    except OSError:
        for _, pinned in records:
            (root / pinned.path).unlink(missing_ok=True)
        stage_dir.rmdir()
        raise
    return project


def import_from_par(
    target: Path,
    *,
    identifier: str,
    rainfall_profile: RainfallProfile,
    parameters: Path,
    catchment: Path | None,
    storm: Path | None,
    base_directory: Path | None,
) -> Project:
    """Inspect PAR, choose its complete input closure, then stage exact bytes."""
    from .project_json import ProjectError, _read_bounded  # noqa: PLC0415 -- entrypoint defines project model

    destination = target.absolute()
    root = destination.parent
    if not root.is_dir():
        message = f"Project destination directory does not exist: {root}"
        raise ProjectError(message)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(destination)
    par_path = parameters.absolute()
    par_data = _read_bounded(par_path)
    inspection = inspect_par_bytes(par_data, source_path=par_path)
    if inspection.status != "parsed" or inspection.parameters is None:
        diagnostic = inspection.diagnostics[0]
        message = f"Cannot import parameters: {inspection.kind} ({diagnostic.code}): {diagnostic.message}"
        raise ProjectError(message)
    try:
        params = parse_cmd_par(par_data).model
    except FormatProblem as exc:
        message = f"Cannot import supported CMD PAR: {exc}"
        raise ProjectError(message) from exc

    base = par_path.parent if base_directory is None else base_directory.absolute()
    if not base.is_dir():
        message = f"PAR reference base directory does not exist: {base}"
        raise ProjectError(message)
    selected: list[SelectedSource] = [
        ("parameters", str(parameters), str(parameters), "explicit", par_path, par_data),
        _selected_input("catchment", params.catchment_reference, catchment, base),
        _selected_input("storm", params.storm_reference, storm, base),
    ]
    try:
        RunModel(params, parse_catg(selected[1][-1]).model, parse_design_stm(selected[2][-1]).model)
    except (FormatProblem, TypeError, ValueError) as exc:
        message = f"Selected PAR/CATG/STM inputs cannot form a supported run: {exc}"
        raise ProjectError(message) from exc
    return _stage_selected(root, destination, selected, identifier=identifier, rainfall_profile=rainfall_profile)
