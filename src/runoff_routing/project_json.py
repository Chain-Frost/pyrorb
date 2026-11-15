"""Versioned JSON projects backed by the existing immutable S1 RunModel.

External RORB/ARR files are hash verified but never altered or interpreted
through a second grammar. No numerical solver, RORB binary or network access.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path, PureWindowsPath
from typing import Any, Literal, cast

from .engine_types import EngineSelection
from .rorb_codec import FormatProblem, parse_catg, parse_cmd_par, parse_design_stm
from .rorb_model import RunModel, from_dict, to_dict, to_json

PROJECT_VERSION = 2
PROJECT_EDITED_VERSION = 3
PROJECT_FORMAT = "python-runoff-routing-project"
MAX_SOURCE_BYTES = 64 * 1024 * 1024
_HASH = re.compile(r"[a-f0-9]{64}\Z")
_ID = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,127}\Z")
_RESERVED_DEVICES = {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"}

RainfallProfile = Literal["explicit", "legacy-rorb", "arr-2026v1"]
AssetRole = Literal["rainfall", "temporal-pattern", "curve", "reference"]


class ProjectError(ValueError):
    """Invalid or unsupported project, never a numerical-parity verdict."""


def _identifier(value: str, label: str) -> None:
    if _ID.fullmatch(value) is None:
        message = f"{label} must be a stable ASCII identifier of at most 128 characters"
        raise ProjectError(message)


def _has_windows_reserved_component(path: str) -> bool:
    """Reject Windows device aliases and names normalised by Windows APIs."""
    for part in path.split("/"):
        if part.endswith((".", " ")):
            return True
        stem = part.split(".", maxsplit=1)[0].upper()
        if stem in _RESERVED_DEVICES:
            return True
        if len(stem) == 4 and stem[:3] in {"COM", "LPT"} and stem[-1] in "123456789¹²³":
            return True
    return False


def _safe_relative(path: str) -> None:
    """Portable slash paths only; absolute/drive/UNC/traversal paths fail closed."""
    if (
        not path
        or len(path) > 1024
        or "\\" in path
        or ":" in path
        or PureWindowsPath(path).anchor
        or _has_windows_reserved_component(path)
        or path.startswith("/")
        or any(part in {"", ".", ".."} for part in path.split("/"))
        or any(ord(char) < 32 or char in '<>"|?*' for char in path)
    ):
        message = f"Unsafe project-relative path: {path!r}"
        raise ProjectError(message)


@dataclass(frozen=True, slots=True)
class SourceFile:
    """Immutable, hash-pinned project-relative file reference."""

    path: str
    sha256: str

    def __post_init__(self) -> None:
        _safe_relative(self.path)
        if _HASH.fullmatch(self.sha256) is None:
            message = f"Expected lowercase SHA-256 for {self.path}"
            raise ProjectError(message)



@dataclass(frozen=True, slots=True)
class SourceBinding:
    """Selected input role, original PAR token and relocatable staged source.

    Resolved_source records import-time provenance, never a path used on reopen.
    """

    role: Literal["parameters", "catchment", "storm"]
    declared_reference: str
    selected_reference: str
    origin: Literal["explicit", "embedded", "override"]
    resolved_source: str
    staged: SourceFile

    def __post_init__(self) -> None:
        if self.role not in {"parameters", "catchment", "storm"}:
            message = f"Unsupported source binding role: {self.role}"
            raise ProjectError(message)
        if self.origin not in {"explicit", "embedded", "override"}:
            message = f"Unsupported binding origin: {self.origin}"
            raise ProjectError(message)
        if not self.selected_reference or not self.resolved_source:
            message = "Selected source reference and resolved provenance must be nonempty"
            raise ProjectError(message)
        if any(ord(char) < 32 for char in self.declared_reference + self.selected_reference + self.resolved_source):
            message = "Source binding contains a control character"
            raise ProjectError(message)


@dataclass(frozen=True, slots=True)
class EmbeddedRun:
    """Embed the existing versioned S1 model without redefining it."""

    run: RunModel


@dataclass(frozen=True, slots=True)
class LegacyRunFiles:
    """Original RORB inputs; .par's embedded paths are never followed."""

    parameters: SourceFile
    catchment: SourceFile
    storm: SourceFile

    def __post_init__(self) -> None:
        for reference, suffixes in (
            (self.parameters, (".par",)),
            (self.catchment, (".catg", ".cat")),
            (self.storm, (".stm",)),
        ):
            # Graphical CATG bytes may carry the legacy .cat suffix.
            # _resolve_run still uses the one fail-closed CATG decoder.
            if not reference.path.lower().endswith(suffixes):
                message = f"Unsupported RORB source format: {reference.path}"
                raise ProjectError(message)


@dataclass(frozen=True, slots=True)
class ExternalAsset:
    """Provenance only: S6 decides the meaning of rainfall/curve bytes."""

    identifier: str
    role: AssetRole
    data_profile: str
    source: SourceFile

    def __post_init__(self) -> None:
        _identifier(self.identifier, "Asset ID")
        _identifier(self.data_profile, "Data profile")
        if self.role not in {"rainfall", "temporal-pattern", "curve", "reference"}:
            message = "Unrecognised external asset role"
            raise ProjectError(message)


@dataclass(frozen=True, slots=True)
class Project:
    """JSON-only boundary; method profile does not assert model equivalence."""

    identifier: str
    rainfall_profile: RainfallProfile
    model_source: EmbeddedRun | LegacyRunFiles
    assets: tuple[ExternalAsset, ...] = ()
    engine: EngineSelection = field(default_factory=EngineSelection)
    source_bindings: tuple[SourceBinding, ...] = ()
    effective_run: RunModel | None = None

    def __post_init__(self) -> None:
        _identifier(self.identifier, "Project ID")
        if self.rainfall_profile not in {"explicit", "legacy-rorb", "arr-2026v1"}:
            message = "Unknown rainfall-method profile"
            raise ProjectError(message)
        ids = tuple(asset.identifier for asset in self.assets)
        if len(set(ids)) != len(ids):
            message = "Duplicate external asset IDs"
            raise ProjectError(message)
        if self.effective_run is not None and not isinstance(self.model_source, LegacyRunFiles):
            message = "Use EmbeddedRun for an edited source-free project"
            raise ProjectError(message)
        if self.source_bindings:
            if not isinstance(self.model_source, LegacyRunFiles):
                message = "Source bindings require original RORB input files"
                raise ProjectError(message)
            if tuple(item.role for item in self.source_bindings) != ("parameters", "catchment", "storm"):
                message = "Source bindings must contain parameters, catchment, storm in order"
                raise ProjectError(message)
            original = self.model_source
            for binding, pinned in zip(
                self.source_bindings, (original.parameters, original.catchment, original.storm), strict=True
            ):
                if binding.staged != pinned:
                    message = f"{binding.role} binding does not match its hash-pinned source"
                    raise ProjectError(message)


@dataclass(frozen=True, slots=True)
class LoadedProject:
    """Validated S1 model and original provenance, no numerical-parity claim."""

    project: Project
    run: RunModel
    original_json_bytes: bytes
    file_hashes: tuple[tuple[str, str], ...]
    validation_status: Literal["structural_only"] = "structural_only"


def _object(raw: object, fields: set[str], label: str) -> dict[str, object]:
    if not isinstance(raw, dict):
        message = f"{label} must be a JSON object"
        raise ProjectError(message)
    data = cast("dict[str, object]", raw)
    if set(data) != fields:
        message = f"{label} expects exact fields: {sorted(fields)}"
        raise ProjectError(message)
    return data


def _string(raw: object, label: str) -> str:
    if not isinstance(raw, str):
        message = f"{label} must be a JSON string"
        raise ProjectError(message)
    return raw


def _source_file(raw: object) -> SourceFile:
    data = _object(raw, {"path", "sha256"}, "source file")
    return SourceFile(_string(data["path"], "Path"), _string(data["sha256"], "Hash"))


def _binding(raw: object) -> SourceBinding:
    data = _object(
        raw,
        {"role", "declared_reference", "selected_reference", "origin", "resolved_source", "staged"},
        "source binding",
    )
    return SourceBinding(
        cast("Literal['parameters', 'catchment', 'storm']", _string(data["role"], "Binding role")),
        _string(data["declared_reference"], "Declared reference"),
        _string(data["selected_reference"], "Selected reference"),
        cast("Literal['explicit', 'embedded', 'override']", _string(data["origin"], "Binding origin")),
        _string(data["resolved_source"], "Resolved source"),
        _source_file(data["staged"]),
    )


def _asset(raw: object) -> ExternalAsset:
    data = _object(raw, {"id", "role", "data_profile", "source"}, "external asset")
    role = _string(data["role"], "Asset role")
    if role not in {"rainfall", "temporal-pattern", "curve", "reference"}:
        message = f"Unsupported external asset role: {role}"
        raise ProjectError(message)
    return ExternalAsset(
        _string(data["id"], "Asset ID"),
        cast("AssetRole", role),
        _string(data["data_profile"], "Data profile"),
        _source_file(data["source"]),
    )


def _model_source(raw: object) -> EmbeddedRun | LegacyRunFiles:
    if not isinstance(raw, dict):
        message = "Model source must be a JSON object"
        raise ProjectError(message)
    source = cast("dict[str, object]", raw)
    kind = _string(source.get("kind"), "Model source kind")
    if kind == "embedded-run":
        data = _object(source, {"kind", "run"}, "embedded model")
        run_document = _object(data["run"], {"schema_version", "kind", "units", "model"}, "S1 run")
        try:
            model = from_dict(cast("dict[str, Any]", run_document))
        except (TypeError, ValueError) as exc:
            message = f"Invalid S1 embedded run: {exc}"
            raise ProjectError(message) from exc
        if not isinstance(model, RunModel):
            message = "Embedded S1 input must be a complete RunModel"
            raise ProjectError(message)
        return EmbeddedRun(model)
    if kind == "rorb-files":
        data = _object(source, {"kind", "parameters", "catchment", "storm"}, "RORB file source")
        return LegacyRunFiles(
            _source_file(data["parameters"]), _source_file(data["catchment"]), _source_file(data["storm"])
        )
    message = f"Unsupported model source kind: {kind}"
    raise ProjectError(message)


def asset_signatures(assets: tuple[ExternalAsset, ...]) -> tuple[tuple[str, str, str, str], ...]:
    """Ordered asset provenance, excluding transport-specific relative paths."""
    return tuple((asset.identifier, asset.role, asset.data_profile, asset.source.sha256) for asset in assets)


def _file_dict(source: SourceFile) -> dict[str, str]:
    return {"path": source.path, "sha256": source.sha256}


def project_to_dict(project: Project) -> dict[str, Any]:
    """Versioned JSON; immutable source evidence is separate from editable settings."""
    if isinstance(project.model_source, EmbeddedRun):
        source: dict[str, Any] = {"kind": "embedded-run", "run": to_dict(project.model_source.run)}
    else:
        files = project.model_source
        source = {
            "kind": "rorb-files",
            "parameters": _file_dict(files.parameters),
            "catchment": _file_dict(files.catchment),
            "storm": _file_dict(files.storm),
        }
    edited = bool(project.source_bindings) or project.effective_run is not None
    result: dict[str, Any] = {
        "format": PROJECT_FORMAT,
        "schema_version": PROJECT_EDITED_VERSION if edited else PROJECT_VERSION,
        "project_id": project.identifier,
        "rainfall_profile": project.rainfall_profile,
        "engine": {"id": project.engine.engine, "numerical_profile": project.engine.numerical_profile},
        "model_source": source,
        "external_assets": [
            {
                "id": asset.identifier,
                "role": asset.role,
                "data_profile": asset.data_profile,
                "source": _file_dict(asset.source),
            }
            for asset in project.assets
        ],
    }
    if edited:
        result["source_bindings"] = [
            {
                "role": item.role,
                "declared_reference": item.declared_reference,
                "selected_reference": item.selected_reference,
                "origin": item.origin,
                "resolved_source": item.resolved_source,
                "staged": _file_dict(item.staged),
            }
            for item in project.source_bindings
        ]
        result["effective_run"] = to_dict(project.effective_run) if project.effective_run is not None else None
    return result


def project_to_json(project: Project) -> str:
    return json.dumps(project_to_dict(project), ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            message = f"Duplicate JSON object key: {key}"
            raise ProjectError(message)
        result[key] = value
    return result


def _reject_nonfinite(value: str) -> None:
    message = f"Nonstandard JSON constant: {value}"
    raise ProjectError(message)


def _decode_effective_run(raw: object) -> RunModel | None:
    if raw is None:
        return None
    run_document = _object(raw, {"schema_version", "kind", "units", "model"}, "effective run")
    try:
        parsed = from_dict(cast("dict[str, Any]", run_document))
    except (TypeError, ValueError) as exc:
        message = f"Invalid effective run: {exc}"
        raise ProjectError(message) from exc
    if not isinstance(parsed, RunModel):
        message = "Effective model must be a complete S1 RunModel"
        raise ProjectError(message)
    return parsed


def _read_engine(data: dict[str, object], version: int) -> EngineSelection:
    if version == 1:
        return EngineSelection.for_engine("python")
    raw_engine = _object(data["engine"], {"id", "numerical_profile"}, "engine selection")
    try:
        return EngineSelection.for_engine(
            _string(raw_engine["id"], "Engine ID"),
            _string(raw_engine["numerical_profile"], "Numerical profile"),
        )
    except ValueError as exc:
        raise ProjectError(str(exc)) from exc


def _v3_bindings(data: dict[str, object], version: int) -> tuple[SourceBinding, ...]:
    if version != 3:
        return ()
    raw_bindings = data["source_bindings"]
    if not isinstance(raw_bindings, list):
        message = "Source bindings must be a JSON array"
        raise ProjectError(message)
    return tuple(_binding(item) for item in cast("list[object]", raw_bindings))


def project_from_json(text: str) -> Project:
    """Fail closed for duplicate keys, unexpected fields and schema versions."""
    try:
        raw: object = json.loads(text, object_pairs_hook=_unique_pairs, parse_constant=_reject_nonfinite)
    except (TypeError, ValueError) as exc:
        raise ProjectError(str(exc)) from exc
    if not isinstance(raw, dict):
        message = "Project must be a JSON object"
        raise ProjectError(message)
    header = cast("dict[str, object]", raw)
    version = header.get("schema_version")
    if header.get("format") != PROJECT_FORMAT or type(version) is not int or version not in (1, 2, 3):
        message = "Unsupported JSON project format or version"
        raise ProjectError(message)
    fields = {"format", "schema_version", "project_id", "rainfall_profile", "model_source", "external_assets"}
    if version >= 2:
        fields.add("engine")
    if version == 3:
        fields.update({"source_bindings", "effective_run"})
    data = _object(header, fields, "project")
    profile = _string(data["rainfall_profile"], "Rainfall profile")
    if profile not in {"explicit", "legacy-rorb", "arr-2026v1"}:
        message = f"Unknown rainfall-method profile: {profile}"
        raise ProjectError(message)
    items = data["external_assets"]
    if not isinstance(items, list):
        message = "External assets must be a JSON array"
        raise ProjectError(message)
    return Project(
        _string(data["project_id"], "Project ID"),
        cast("RainfallProfile", profile),
        _model_source(data["model_source"]),
        tuple(_asset(item) for item in cast("list[object]", items)),
        _read_engine(data, version),
        _v3_bindings(data, version),
        _decode_effective_run(data["effective_run"]) if version == 3 else None,
    )


def _read_bounded(path: Path) -> bytes:
    try:
        if path.stat().st_size > MAX_SOURCE_BYTES:
            message = f"Source exceeds {MAX_SOURCE_BYTES} byte limit: {path}"
            raise ProjectError(message)
        contents = path.read_bytes()
    except OSError as exc:
        message = f"Cannot read project source: {path}"
        raise ProjectError(message) from exc
    if len(contents) > MAX_SOURCE_BYTES:
        message = f"Source changed or exceeds maximum size: {path}"
        raise ProjectError(message)
    return contents


def _source_bytes(directory: Path, reference: SourceFile) -> bytes:
    """Resolve symlinks deliberately for containment; retain source spelling."""
    base = directory.resolve(strict=True)
    try:
        physical = (directory / reference.path).resolve(strict=True)
    except OSError as exc:
        message = f"Missing project source: {reference.path}"
        raise ProjectError(message) from exc
    if not physical.is_relative_to(base):
        message = f"Source symlink escapes project directory: {reference.path}"
        raise ProjectError(message)
    raw = _read_bounded(physical)
    if hashlib.sha256(raw).hexdigest() != reference.sha256:
        message = f"Source SHA-256 mismatch: {reference.path}"
        raise ProjectError(message)
    return raw


def _resolve_run(directory: Path, source: EmbeddedRun | LegacyRunFiles) -> tuple[RunModel, tuple[SourceFile, ...]]:
    if isinstance(source, EmbeddedRun):
        return source.run, ()
    references = (source.parameters, source.catchment, source.storm)
    raw = tuple(_source_bytes(directory, item) for item in references)
    try:
        parameters = parse_cmd_par(raw[0]).model
        catchment = parse_catg(raw[1]).model
        storm = parse_design_stm(raw[2]).model
        run = RunModel(parameters, catchment, storm)
    except (FormatProblem, TypeError, ValueError) as exc:
        message = f"RORB source cannot form supported S1 RunModel: {exc}"
        raise ProjectError(message) from exc
    return run, references


def load_project(path: Path) -> LoadedProject:
    """Validate JSON and source hashes; no solver or external process."""
    source = _read_bounded(path)
    try:
        project = project_from_json(source.decode("utf-8-sig"))
    except UnicodeError as exc:
        message = "Project JSON must be valid UTF-8"
        raise ProjectError(message) from exc
    directory = path.absolute().parent
    original_run, references = _resolve_run(directory, project.model_source)
    run = project.effective_run if project.effective_run is not None else original_run
    all_files = (*references, *(asset.source for asset in project.assets))
    for asset in project.assets:
        _source_bytes(directory, asset.source)
    return LoadedProject(project, run, source, tuple((item.path, item.sha256) for item in all_files))


def write_project(path: Path, project: Project) -> None:
    """Never overwrite an original file."""
    with path.open("xb") as stream:
        stream.write(project_to_json(project).encode("utf-8"))


def import_rorb_project(
    target: Path,
    *,
    identifier: str,
    rainfall_profile: RainfallProfile,
    parameters: Path,
    catchment: Path | None = None,
    storm: Path | None = None,
    base_directory: Path | None = None,
) -> Project:
    """Stage verified original PAR/CATG/STM bytes, resolving PAR references by role.

    Default relative references and relative override paths use the PAR directory;
    callers may supply base_directory explicitly. No process-CWD search occurs.
    """
    from .par_project_import import import_from_par  # noqa: PLC0415 -- narrow filesystem adapter avoids cycle

    return import_from_par(
        target,
        identifier=identifier,
        rainfall_profile=rainfall_profile,
        parameters=parameters,
        catchment=catchment,
        storm=storm,
        base_directory=base_directory,
    )



def _relocated_source_files(source: Path, target: Path, project: Project) -> None:
    """Copy verified immutable asset closure, rolling back only files we created."""
    refs: list[SourceFile] = []
    if isinstance(project.model_source, LegacyRunFiles):
        original = project.model_source
        refs.extend((original.parameters, original.catchment, original.storm))
    refs.extend(asset.source for asset in project.assets)
    unique: dict[str, SourceFile] = {}
    for reference in refs:
        if reference.path in unique and unique[reference.path].sha256 != reference.sha256:
            message = f"Conflicting immutable source path: {reference.path}"
            raise ProjectError(message)
        unique[reference.path] = reference
    planned: list[tuple[Path, bytes]] = []
    for reference in unique.values():
        output = target / reference.path
        if output.exists() or output.is_symlink():
            message = f"Relocated source already exists: {reference.path}"
            raise ProjectError(message)
        planned.append((output, _source_bytes(source, reference)))
    written: list[Path] = []
    try:
        for output, raw in planned:
            output.parent.mkdir(parents=True, exist_ok=True)
            _ensure_relocation_directory(output.parent, target)
            with output.open("xb") as stream:
                stream.write(raw)
            written.append(output)
    except (OSError, ProjectError):
        for output in written:
            output.unlink(missing_ok=True)
        raise


def _ensure_relocation_directory(directory: Path, target: Path) -> None:
    if not directory.resolve(strict=True).is_relative_to(target.resolve(strict=True)):
        message = f"Relocated source directory escapes destination: {directory}"
        raise ProjectError(message)


def save_project_as(
    source: Path, destination: Path, *, effective_run: RunModel | None = None
) -> Project:
    """Save typed edits into a new project, copying exact pinned assets when relocated.

    Never overwrites destination files. Original PAR/CATG/STM bytes and bindings
    are retained; reopened calculations use the explicit effective_run overlay.
    """
    loaded = load_project(source)
    project = loaded.project
    if effective_run is not None:
        if isinstance(project.model_source, EmbeddedRun):
            project = replace(project, model_source=EmbeddedRun(effective_run))
        else:
            project = replace(project, effective_run=effective_run)
    if destination.exists():
        raise FileExistsError(destination)
    origin = source.absolute().parent
    target = destination.absolute().parent
    if not target.is_dir():
        message = f"Destination directory does not exist: {target}"
        raise ProjectError(message)
    if origin == target:
        write_project(destination, project)
        return project
    _relocated_source_files(origin, target, project)
    try:
        write_project(destination, project)
    except OSError:
        # Keep hash-pinned sources for a retry only when destination write races.
        # The JSON is still exclusive; no original data are ever overwritten.
        raise
    return project


MAX_DIFFERENCE_PATHS = 24


@dataclass(frozen=True, slots=True)
class ProjectComparison:
    """Exact typed-model and project-method comparison, without solver execution."""

    left_project_id: str
    right_project_id: str
    left_source_kind: Literal["embedded-run", "rorb-files"]
    right_source_kind: Literal["embedded-run", "rorb-files"]
    model_equal: bool
    rainfall_profile_equal: bool
    external_assets_equal: bool
    external_asset_paths_equal: bool
    engine_selection_equal: bool
    configuration_equal: bool
    first_differences: tuple[str, ...]
    numerical_parity: Literal["not_assessed"] = "not_assessed"

    def to_json(self) -> str:
        """Stable machine-readable model comparison, not a native routing verdict."""
        return json.dumps(asdict(self), indent=2, sort_keys=True, allow_nan=False) + "\n"


def _first_differences(left: object, right: object, path: str, differences: list[str]) -> None:
    """Report bounded field-level mismatches without changing source order."""
    if len(differences) >= MAX_DIFFERENCE_PATHS or left == right:
        return
    if isinstance(left, dict) and isinstance(right, dict):
        _difference_mapping(cast("dict[str, object]", left), cast("dict[str, object]", right), path, differences)
    elif isinstance(left, list) and isinstance(right, list):
        _difference_sequence(cast("list[object]", left), cast("list[object]", right), path, differences)
    else:
        differences.append(path)


def _difference_mapping(first: dict[str, object], second: dict[str, object], path: str, differences: list[str]) -> None:
    for key in sorted(first.keys() | second.keys()):
        if len(differences) >= MAX_DIFFERENCE_PATHS:
            break
        label = f"{path}.{key}"
        if key not in first or key not in second:
            differences.append(label)
        else:
            _first_differences(first[key], second[key], label, differences)


def _difference_sequence(first: list[object], second: list[object], path: str, differences: list[str]) -> None:
    if len(first) != len(second):
        differences.append(f"{path}.length")
    for index, (a, b) in enumerate(zip(first, second, strict=False)):
        if len(differences) >= MAX_DIFFERENCE_PATHS:
            break
        _first_differences(a, b, f"{path}[{index}]", differences)


def _source_kind(source: EmbeddedRun | LegacyRunFiles) -> Literal["embedded-run", "rorb-files"]:
    return "embedded-run" if isinstance(source, EmbeddedRun) else "rorb-files"


def compare_project_files(left: Path, right: Path) -> ProjectComparison:
    """Compare two fully verified JSON projects using S1's typed model.

    Exact S1 model identity is not native hydrograph or rainfall-method parity.
    """
    a = load_project(left)
    b = load_project(right)
    model_equal = a.run == b.run
    profile_equal = a.project.rainfall_profile == b.project.rainfall_profile
    assets_equal = asset_signatures(a.project.assets) == asset_signatures(b.project.assets)
    engine_equal = a.project.engine == b.project.engine
    asset_paths_equal = tuple(item.source.path for item in a.project.assets) == tuple(
        item.source.path for item in b.project.assets
    )
    differences: list[str] = []
    if not model_equal:
        _first_differences(to_dict(a.run), to_dict(b.run), "run", differences)
    if not profile_equal:
        differences.append("rainfall_profile")
    if not engine_equal:
        differences.append("engine")
    if not assets_equal:
        _first_differences(
            list(asset_signatures(a.project.assets)),
            list(asset_signatures(b.project.assets)),
            "external_assets",
            differences,
        )
    return ProjectComparison(
        a.project.identifier,
        b.project.identifier,
        _source_kind(a.project.model_source),
        _source_kind(b.project.model_source),
        model_equal,
        profile_equal,
        assets_equal,
        asset_paths_equal,
        engine_equal,
        model_equal and profile_equal and assets_equal and engine_equal,
        tuple(differences[:MAX_DIFFERENCE_PATHS]),
    )


def export_run_json(project_path: Path, destination: Path) -> str:
    """Write verified S1 RunModel JSON; the project retains source provenance.

    The exported S1 model intentionally omits project rainfall-method and
    external source metadata. Returns the SHA-256 of the new JSON file.
    """
    model = load_project(project_path).run
    contents = to_json(model).encode("utf-8")
    with destination.open("xb") as stream:
        stream.write(contents)
    return hashlib.sha256(contents).hexdigest()


def _validated_profile(value: str) -> RainfallProfile:
    if value not in {"explicit", "legacy-rorb", "arr-2026v1"}:
        message = f"Unknown rainfall-method profile: {value}"
        raise ProjectError(message)
    return cast("RainfallProfile", value)



def _cli_save_run(source: str, edited: str, destination: str) -> None:
    edited_bytes = _read_bounded(Path(edited))
    parsed = from_dict(cast("dict[str, Any]", json.loads(edited_bytes.decode("utf-8-sig"))))
    if not isinstance(parsed, RunModel):
        message = "save-run requires an S1 complete run document"
        raise ProjectError(message)
    saved = save_project_as(Path(source), Path(destination), effective_run=parsed)
    print(json.dumps({"status": "written", "project_id": saved.identifier, "path": destination}, sort_keys=True))


def _cli_import_rorb(args: list[str]) -> None:
    _, identifier, profile, par, *remaining = args
    selected_profile = _validated_profile(profile)
    overrides: dict[str, Path] = {}
    if len(remaining) == 3 and not any(item.startswith("--") for item in remaining):
        catg, stm, destination = remaining
        overrides = {"catchment": Path(catg), "storm": Path(stm)}
    else:
        destination, *options = remaining
        if len(options) % 2:
            message = "Import flags require value pairs"
            raise ProjectError(message)
        for flag, path_value in zip(options[::2], options[1::2], strict=True):
            key = {"--catchment": "catchment", "--storm": "storm", "--base": "base_directory"}.get(flag)
            if key is None or key in overrides:
                message = f"Unknown or repeated PAR import flag: {flag}"
                raise ProjectError(message)
            overrides[key] = Path(path_value)
    target = Path(destination)
    project = import_rorb_project(
        target,
        identifier=identifier,
        rainfall_profile=selected_profile,
        parameters=Path(par),
        **overrides,
    )
    write_project(target, project)
    print(
        json.dumps(
            {"status": "written", "path": str(target), "source_bindings": len(project.source_bindings)},
            sort_keys=True,
        )
    )


def main(argv: list[str] | None = None) -> int:
    """Small Windows-friendly CLI without argparse, native calls or side effects."""
    args = sys.argv[1:] if argv is None else argv
    if args and args[0] == "run":
        from .engine_execution import run_cli  # noqa: PLC0415 -- avoids a JSON/dispatch import cycle

        return run_cli(args[1:])
    try:
        if len(args) == 8 and args[0] == "review-native":
            from .project_native_review import (  # noqa: PLC0415 -- CLI-only, depends on S5 source validation
                review_project_native_capture,
                write_native_review_json,
            )

            _, project_path, manifest_path, manifest_hash, executable_hash, print_id, column_id, output_path = args
            review = review_project_native_capture(
                Path(project_path),
                Path(manifest_path),
                manifest_sha256=manifest_hash,
                engine_executable_sha256=executable_hash,
                model_print_id=print_id,
                native_column_id=column_id,
            )
            write_native_review_json(Path(output_path), review)
            print(
                json.dumps(
                    {
                        "review_status": review.review_status,
                        "numerical_acceptance": review.numerical_acceptance,
                        "manifest_sha256": review.manifest_sha256,
                        "native_output_sha256": review.native_output_sha256,
                        "printed_within_budget": review.printed.printed_discharge_parity.within_print_budget,
                    },
                    sort_keys=True,
                )
            )
            return 0
        if len(args) == 3 and args[0] == "compare-runs":
            from .project_execution import (  # noqa: PLC0415 -- CLI-only import avoids project_json execution cycle
                compare_routed_projects,
            )

            comparison = compare_routed_projects(Path(args[1]), Path(args[2]))
            print(comparison.to_json(), end="")
            return 0 if comparison.identical else 1
        if len(args) == 3 and args[0] == "compare":
            report = compare_project_files(Path(args[1]), Path(args[2]))
            print(report.to_json(), end="")
            return 0 if report.configuration_equal else 1
        if len(args) == 3 and args[0] == "export-run":
            source_path, destination_path = Path(args[1]), Path(args[2])
            fingerprint = export_run_json(source_path, destination_path)
            print(
                json.dumps(
                    {"status": "written", "sha256": fingerprint, "numerical_parity": "not_assessed"},
                    sort_keys=True,
                )
            )
            return 0
        if len(args) == 2 and args[0] == "inspect-par":
            from .rorb_par import inspect_par_bytes  # noqa: PLC0415 -- CLI-only reader

            source_path = Path(args[1])
            inspection = inspect_par_bytes(_read_bounded(source_path), source_path=source_path.absolute())
            print(
                json.dumps(
                    {
                        "kind": inspection.kind,
                        "status": inspection.status,
                        "supported": inspection.status == "parsed",
                        "sha256": inspection.source.sha256,
                        "references": (
                            {
                                "catchment": inspection.parameters.catchment_reference,
                                "storm": inspection.parameters.storm_reference,
                            }
                            if inspection.parameters is not None
                            else None
                        ),
                        "parameters": asdict(inspection.parameters) if inspection.parameters is not None else None,
                        "diagnostics": [asdict(item) for item in inspection.diagnostics],
                    },
                    sort_keys=True,
                    default=str,
                )
            )
            return 0 if inspection.status == "parsed" else 1
        if len(args) == 4 and args[0] == "save-run":
            _cli_save_run(args[1], args[2], args[3])
            return 0
        if len(args) == 2 and args[0] in {"validate", "inspect"}:
            loaded = load_project(Path(args[1]))
            print(
                json.dumps(
                    {
                        "status": loaded.validation_status,
                        "project_id": loaded.project.identifier,
                        "rainfall_profile": loaded.project.rainfall_profile,
                        "engine": loaded.project.engine.engine,
                        "numerical_profile": loaded.project.engine.numerical_profile,
                        "source_files": len(loaded.file_hashes),
                        "source_bindings": [
                            {
                                "role": binding.role,
                                "declared_reference": binding.declared_reference,
                                "selected_reference": binding.selected_reference,
                                "origin": binding.origin,
                                "staged_path": binding.staged.path,
                            }
                            for binding in loaded.project.source_bindings
                        ],
                        "effective_run_edited": loaded.project.effective_run is not None,
                        "subareas": len(loaded.run.catchment.subareas),
                        "print_locations": len(loaded.run.catchment.print_locations),
                        "numerical_parity": "not_assessed",
                    },
                    sort_keys=True,
                )
            )
            return 0
        if len(args) >= 5 and args[0] == "import-rorb":
            _cli_import_rorb(args)
            return 0
    except (ProjectError, OSError, TypeError, ValueError, UnicodeError) as exc:
        print(f"Project validation failed: {exc}", file=sys.stderr)
        return 2
    print(
        "Usage: python -m runoff_routing.project_json (validate|inspect) <project.json> "
        "| inspect-par <source.par> "
        "| import-rorb <id> <rainfall-profile> <par> <project.json> "
        "[--catchment FILE] [--storm FILE] [--base DIR] "
        "| save-run <project.json> <edited-run.json> <new-project.json> "
        "| export-run <project.json> <run.json> | compare <left.json> <right.json> "
        "| run <project.json> <result.json> [--engine ID --numerical-profile PROFILE] "
        "[--native-config LOCAL.json] | compare-runs <left.json> <right.json> "
        "| review-native <project.json> <manifest.json> <manifest-sha256> "
        "<engine-sha256> <print-id> <native-column> <review.json>",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
