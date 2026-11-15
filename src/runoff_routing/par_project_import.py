"""PAR-led, byte-preserving source discovery and explicit path selection.

Source location is a one-time import decision. No saved project depends on the
old source tree, the process working directory or a speculative drive mapping.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path, PureWindowsPath
from typing import TYPE_CHECKING

from .rorb_codec import FormatProblem, parse_catg, parse_cmd_par, parse_design_stm
from .rorb_model import RunModel
from .rorb_par import inspect_par_bytes

if TYPE_CHECKING:
    from .project_json import Project, RainfallProfile, SourceBinding


def _reference_path(
    token: str, *, role: str, base: Path, override_flag: str
) -> Path:
    """Interpret quoted/Windows/UNC tokens deliberately on the current OS."""
    from .project_json import ProjectError  # noqa: PLC0415 -- runtime import avoids module cycle

    value = token.strip()
    if len(value) >= 2 and value[0] in {"'", '"'} and value[-1] == value[0]:
        value = value[1:-1]
    elif value.startswith(("'", '"')) or value.endswith(("'", '"')):
        raise ProjectError(f"Unbalanced quotes in {role} reference {token!r}; use {override_flag}")
    if not value or any(ord(char) < 32 for char in value):
        raise ProjectError(f"Invalid {role} reference {token!r}; use {override_flag}")
    win = PureWindowsPath(value)
    if win.drive:
        if os.name != "nt":
            raise ProjectError(
                f"{role} reference {token!r} is an unresolved foreign Windows drive/UNC path; "
                f"use {override_flag} with a local file"
            )
        if not win.is_absolute():
            raise ProjectError(f"Drive-relative {role} reference {token!r} is ambiguous; use {override_flag}")
    elif value.startswith("\\") and os.name != "nt":
        # A single leading Windows-root slash has no portable drive identity.
        raise ProjectError(f"Windows-rooted {role} reference {token!r} is ambiguous; use {override_flag}")
    local = Path(value if os.name == "nt" else value.replace("\\", "/"))
    return local.absolute() if local.is_absolute() else (base / local).absolute()


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
    """Classify PAR, validate the complete selected model, then stage exact bytes."""
    from .project_json import (  # noqa: PLC0415 -- owned entrypoint defines serialisable project model
        LegacyRunFiles,
        Project,
        ProjectError,
        SourceBinding,
        SourceFile,
        _read_bounded,
        _safe_relative,
    )

    destination = target.absolute()
    root = destination.parent
    if not root.is_dir():
        raise ProjectError(f"Project destination directory does not exist: {root}")
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(destination)
    par_path = parameters.absolute()
    par_data = _read_bounded(par_path)
    inspection = inspect_par_bytes(par_data, source_path=par_path)
    if inspection.status != "parsed" or inspection.parameters is None:
        diagnostic = inspection.diagnostics[0]
        raise ProjectError(
            f"Cannot import parameters: {inspection.kind} ({diagnostic.code}): {diagnostic.message}"
        )
    try:
        parameter_model = parse_cmd_par(par_data).model
    except FormatProblem as exc:
        raise ProjectError(f"Cannot import supported CMD PAR: {exc}") from exc

    base = par_path.parent if base_directory is None else base_directory.absolute()
    if not base.is_dir():
        raise ProjectError(f"PAR reference base directory does not exist: {base}")
    chosen: list[tuple[str, str, str, str, Path, bytes]] = [
        ("parameters", str(parameters), str(parameters), "explicit", par_path, par_data)
    ]
    for role, declared, explicit in (
        ("catchment", parameter_model.catchment_reference, catchment),
        ("storm", parameter_model.storm_reference, storm),
    ):
        selected = str(explicit) if explicit is not None else declared
        origin = "override" if explicit is not None else "embedded"
        flag = f"--{role}"
        path = _reference_path(selected, role=role, base=base, override_flag=flag)
        if not path.is_file():
            raise ProjectError(
                f"Missing {role} input: declared {declared!r}, selected {selected!r}. "
                f"Provide {flag} FILE to override the PAR reference."
            )
        try:
            raw = _read_bounded(path)
        except ProjectError as exc:
            raise ProjectError(
                f"Cannot read {role} input: declared {declared!r}, selected {selected!r}; "
                f"use {flag} FILE: {exc}"
            ) from exc
        supported_suffixes = (".catg", ".cat") if role == "catchment" else (".stm",)
        if path.suffix.lower() not in supported_suffixes:
            raise ProjectError(
                f"Unsupported {role} input type {path.suffix!r}: {selected!r}; use {flag} FILE"
            )
        chosen.append((role, declared, selected, origin, path, raw))
    try:
        RunModel(parameter_model, parse_catg(chosen[1][-1]).model, parse_design_stm(chosen[2][-1]).model)
    except (FormatProblem, TypeError, ValueError) as exc:
        raise ProjectError(f"Selected PAR/CATG/STM inputs cannot form a supported run: {exc}") from exc

    # Per-project subdirectory and role-prefixed names avoid source basename collisions.
    # The staged paths alone are authoritative after import; original locations are evidence.
    staged_dir = root / "sources" / destination.stem
    records: list[tuple[str, str, str, str, Path, bytes, SourceFile]] = []
    for role, declared, selected, origin, path, raw in chosen:
        suffix = ".par" if role == "parameters" else path.suffix
        relative = f"sources/{destination.stem}/{role}{suffix}"
        _safe_relative(relative)
        records.append(
            (role, declared, selected, origin, path, raw, SourceFile(relative, hashlib.sha256(raw).hexdigest()))
        )
    files = LegacyRunFiles(records[0][-1], records[1][-1], records[2][-1])
    bindings: tuple[SourceBinding, ...] = tuple(
        SourceBinding(role, declared, selected, origin, str(path), pinned)
        for role, declared, selected, origin, path, _, pinned in records
    )
    project = Project(identifier, rainfall_profile, files, source_bindings=bindings)

    parent = staged_dir.parent
    if parent.is_symlink() or staged_dir.exists() or staged_dir.is_symlink():
        raise ProjectError(f"Unsafe or occupied staged source directory: {staged_dir}")
    try:
        staged_dir.mkdir(parents=True)
        if not staged_dir.resolve(strict=True).is_relative_to(root.resolve(strict=True)):
            raise ProjectError(f"Staged source directory escapes project destination: {staged_dir}")
        for _, _, _, _, _, raw, pinned in records:
            with (root / pinned.path).open("xb") as output:
                output.write(raw)
    except (OSError, ProjectError):
        for _, _, _, _, _, _, pinned in records:
            (root / pinned.path).unlink(missing_ok=True)
        if staged_dir.is_dir():
            staged_dir.rmdir()
        raise
    return project
