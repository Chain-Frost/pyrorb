"""Opt-in native RORB CMD product adapter built on the original S0 capture machinery.

Only the fingerprinted CMD 6.44 single-ISA, pervious DESIGN boundary is enabled.
This module never runs an executable at import, inspection or configuration time.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, cast

from .engine_types import EngineHydrograph, EngineStatus
from .project_json import LegacyRunFiles, LoadedProject
from .project_native_review import _check_capture_settings
from .reference import capture_cmd, fingerprint, verify_manifest
from .rorb_documents import RorbSource
from .rorb_out import inspect_output

_SUPPORTED_PROFILE = "cmd-6.44"
_SHA256 = re.compile(r"[a-f0-9]{64}\Z")
_HYDRO = re.compile(r"Hyd[0-9]+\Z")


class NativeBoundaryError(ValueError):
    """Fail-closed native preflight or inspection with stable machine-readable status."""

    def __init__(
        self, message: str, *, status: EngineStatus, code: str, manifest: Path | None = None
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.manifest = manifest


@dataclass(frozen=True, slots=True)
class NativeConfiguration:
    """Local-only executable profile and caller-established model print mapping."""

    executable: Path
    executable_sha256: str
    observed_version: str
    observed_banner: str
    numerical_profile: str
    output_root: Path
    print_columns: tuple[tuple[str, str], ...]
    timeout_seconds: float = 180.0

    def __post_init__(self) -> None:
        if self.numerical_profile != _SUPPORTED_PROFILE or self.observed_version != "6.44":
            message = "Only the observed cmd-6.44 native profile is characterised for this adapter"
            raise ValueError(message)
        if _SHA256.fullmatch(self.executable_sha256) is None or not self.observed_banner.strip():
            message = "Native configuration requires a reviewed executable SHA-256 and observed banner"
            raise ValueError(message)
        if not math.isfinite(self.timeout_seconds) or self.timeout_seconds <= 0:
            message = "Native timeout must be a positive finite number"
            raise ValueError(message)
        sites = [site for site, _ in self.print_columns]
        columns = [column for _, column in self.print_columns]
        if (
            not sites
            or len(set(sites)) != len(sites)
            or len(set(columns)) != len(columns)
            or any(not site or _HYDRO.fullmatch(column) is None for site, column in self.print_columns)
        ):
            message = "Native print_columns must be unique model IDs mapped one-to-one to HydNNN columns"
            raise ValueError(message)

    @classmethod
    def from_file(cls, path: Path) -> NativeConfiguration:
        """Read a machine-local configuration; relative paths belong to that file."""
        data: object = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            message = "Native configuration must be a JSON object"
            raise TypeError(message)
        raw = cast("dict[str, object]", data)
        fields = {
            "schema_version", "executable", "executable_sha256", "observed_version", "observed_banner",
            "numerical_profile", "output_root", "print_columns", "timeout_seconds",
        }
        if set(raw) != fields or type(raw["schema_version"]) is not int or raw["schema_version"] != 1:
            message = "Native configuration expects exact schema-1 fields"
            raise ValueError(message)
        names = ("executable", "executable_sha256", "observed_version", "observed_banner", "numerical_profile", "output_root")
        if any(not isinstance(raw[name], str) or not raw[name] for name in names):
            message = "Native configuration has missing or invalid string fields"
            raise ValueError(message)
        mapping = raw["print_columns"]
        if not isinstance(mapping, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in mapping.items()):
            message = "Native print_columns must be a string-to-string mapping"
            raise ValueError(message)
        timeout = raw["timeout_seconds"]
        if type(timeout) not in (int, float):
            message = "Native timeout_seconds must be a number"
            raise ValueError(message)
        base = path.absolute().parent

        def local_path(name: str) -> Path:
            selected = Path(cast("str", raw[name]))
            return (selected if selected.is_absolute() else base / selected).absolute()

        return cls(
            local_path("executable"),
            cast("str", raw["executable_sha256"]),
            cast("str", raw["observed_version"]),
            cast("str", raw["observed_banner"]),
            cast("str", raw["numerical_profile"]),
            local_path("output_root"),
            tuple(cast("dict[str, str]", mapping).items()),
            float(timeout),
        )


@dataclass(frozen=True, slots=True)
class NativeObservation:
    """Inspected native result, not a substituted Python hydrograph."""

    hydrographs: tuple[EngineHydrograph, ...]
    physical_time_hours: tuple[str, ...]
    raw_increment_tokens: tuple[str, ...]
    raw_time_tokens: tuple[str, ...]
    executable_sha256: str
    observed_version: str
    output_sha256: str
    manifest_path: str


def _preflight(loaded: LoadedProject, config: NativeConfiguration) -> LegacyRunFiles:
    model = loaded.run
    source = loaded.project.model_source
    if not isinstance(source, LegacyRunFiles) or loaded.project.rainfall_profile != "legacy-rorb":
        message = "Native CMD requires verified original .par/.catg/.stm file-backed legacy-rorb inputs"
        raise NativeBoundaryError(message, status="unsupported_feature", code="native_source_boundary")
    if any(asset.role != "reference" for asset in loaded.project.assets):
        message = "Native adapter cannot silently prepare external rainfall/curve data"
        raise NativeBoundaryError(message, status="unsupported_feature", code="unprepared_rainfall")
    params = model.parameters
    storm = model.storm
    if (
        not params.lumped_kc or params.num_isa != 1 or params.num_bursts != 1 or params.loss_model != 1
        or storm.isa_count != 1 or storm.burst_count != 1 or storm.pluviograph_count != 1
        or storm.start_increment != 0
    ):
        message = "CMD adapter supports one ISA/burst/pluviograph, lumped kc, IL/CL and zero event start"
        raise NativeBoundaryError(message, status="unsupported_feature", code="native_model_boundary")
    expected = {site.identifier for site in model.catchment.print_locations}
    supplied = {site for site, _ in config.print_columns}
    if expected != supplied or len(expected) != len(config.print_columns):
        message = "Native print mapping must cover every requested S1 site exactly once"
        raise NativeBoundaryError(message, status="invalid_input", code="print_site_mapping")
    exe = config.executable
    if not exe.is_file() or exe.is_symlink():
        message = "Configured native executable is missing, a symlink or not a regular file"
        raise NativeBoundaryError(message, status="unavailable_engine", code="native_executable")
    if fingerprint(exe)["sha256"] != config.executable_sha256:
        message = "Native executable bytes do not match the reviewed profile fingerprint"
        raise NativeBoundaryError(message, status="unavailable_engine", code="native_fingerprint")
    if config.output_root.is_symlink():
        message = "Native output parent must not be a symlink"
        raise NativeBoundaryError(message, status="invalid_input", code="native_output_parent")
    return source


def _make_spec(
    loaded: LoadedProject, config: NativeConfiguration, source: LegacyRunFiles, root: Path, source_root: Path
) -> Path:
    model = loaded.run
    params = model.parameters
    def original(relative: str) -> str:
        return str((source_root / relative).absolute())

    mapping = {column: f"caller_asserted:{site}" for site, column in config.print_columns}
    project_hash = hashlib.sha256(loaded.original_json_bytes).hexdigest()
    document: dict[str, Any] = {
        "schema_version": 1,
        "case_id": f"{loaded.project.identifier[:40]}-{project_hash[:12]}",
        "engine_kind": "RORB_CMD",
        "executable": str(config.executable),
        "observed_banner": config.observed_banner,
        "observed_version": config.observed_version,
        "documentation_version": None,
        "catchment": original(source.catchment.path),
        "storm": original(source.storm.path),
        "parameters": {
            "kc": str(params.routing[0].kc),
            "m": str(params.routing[0].m),
            "loss_model": params.loss_model,
            "initial_loss_mm": str(params.losses[0].initial_loss_mm),
            "continuing": str(params.losses[0].continuing),
        },
        "timeout_seconds": config.timeout_seconds,
        "provenance": {"source": "hash-verified JSON project", "redistribution": "operator-managed; not bundled"},
        "generator": {"name": "python-runoff-routing", "revision": "project-schema-2", "event_to_file": loaded.project.identifier},
        "effective_settings": {
            "timestep_hours": str(model.storm.timestep_hours),
            "horizon": model.storm.calculation_increments,
            "isa_mapping": [1],
            "burst_mapping": [1],
            "calculation_order": [step.code for step in model.catchment.controls],
        },
        "requested_print_locations": mapping,
        "expected_steps": model.storm.calculation_increments + 1,
    }
    spec_path = root / "native-spec.json"
    spec_path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
    return spec_path


def _inspect(  # noqa: C901 -- report verification deliberately checks each independent native failure state
    manifest_path: Path, loaded: LoadedProject, config: NativeConfiguration
) -> NativeObservation:
    if verify_manifest(manifest_path):
        message = "S0 evidence inventory or staged input fingerprint failed verification"
        raise NativeBoundaryError(message, status="incomplete_output", code="native_manifest", manifest=manifest_path)
    manifest: dict[str, Any] = json.loads(manifest_path.read_text(encoding="utf-8"))
    outcome: object = manifest.get("outcome")
    if outcome not in ("success", "zero_runoff"):
        status: EngineStatus = (
            "incomplete_output" if outcome in ("incomplete_output", "missing_output", "captured_unverified")
            else "native_execution_failed"
        )
        message = f"S0 native capture did not validate: {outcome}; see retained manifest diagnostics"
        raise NativeBoundaryError(status, "native_capture_outcome", message, manifest_path)
    if (
        manifest.get("provenance_gaps")
        or manifest.get("diagnostics") != {"errors": [], "warnings": []}
        or manifest.get("expected_steps") != loaded.run.storm.calculation_increments + 1
        or manifest["requested_print_locations"] != {
            column: f"caller_asserted:{site}" for site, column in config.print_columns
        }
    ):
        message = "S0 reported missing identity evidence or native diagnostic errors/warnings"
        raise NativeBoundaryError(message, status="incomplete_output", code="native_diagnostics", manifest=manifest_path)
    if manifest["engine"]["executable"]["sha256"] != config.executable_sha256:
        message = "Captured native executable fingerprint differs from configuration"
        raise NativeBoundaryError(message, status="native_execution_failed", code="native_executable_changed", manifest=manifest_path)
    source = loaded.project.model_source
    if not isinstance(source, LegacyRunFiles):
        message = "Native source identity is no longer file-backed"
        raise TypeError(message)
    try:
        _check_capture_settings(manifest, source, loaded.run)
    except (ValueError, KeyError, TypeError) as exc:
        raise NativeBoundaryError(str(exc), status="incomplete_output", code="effective_input_mismatch", manifest=manifest_path) from exc
    outputs = manifest["outputs"]
    reports = [item for item in outputs if str(item["path"]).lower().endswith(".out")]
    if len(reports) != 1:
        message = "Native CMD must produce exactly one retained .out report"
        raise NativeBoundaryError(message, status="incomplete_output", code="native_report_count", manifest=manifest_path)
    target = manifest_path.absolute().parent / str(reports[0]["path"])
    source_report = RorbSource.read(target)
    inspected = inspect_output(source_report)
    report = inspected.hydrographs
    expected_rows = loaded.run.storm.calculation_increments + 1
    required_columns = {column for _, column in config.print_columns}
    if (
        report is None
        or report.time_increment_hours != loaded.run.storm.timestep_hours
        or report.reported_duration_increments != loaded.run.storm.calculation_increments
        or len(report.rows) != expected_rows
        or set(report.columns) != required_columns
    ):
        message = "Native output timestep, duration, columns or complete horizon failed S1 inspection"
        raise NativeBoundaryError(message, status="incomplete_output", code="native_report_shape", manifest=manifest_path)
    if source_report.sha256 != reports[0]["sha256"]:
        message = "Native output bytes changed since S0 inventory"
        raise NativeBoundaryError(message, status="incomplete_output", code="native_report_hash", manifest=manifest_path)
    for index, row in enumerate(report.rows, start=1):
        if row.increment != index:
            message = "CMD 6.44 output must retain the observed 1-based increment convention"
            raise NativeBoundaryError(message, status="incomplete_output", code="native_clock_convention", manifest=manifest_path)
        if any(flow < 0 for flow in row.values):
            message = "Native printed discharge contains negative values"
            raise NativeBoundaryError(message, status="incomplete_output", code="native_negative_flow", manifest=manifest_path)
        # Allow only the printed clock resolution; preserve the unrounded raw token separately.
        target_hour = index * loaded.run.storm.timestep_hours
        resolution = Decimal(1).scaleb(row.time_hours.as_tuple().exponent)
        if abs(row.time_hours - target_hour) > resolution / 2:
            message = "Native raw time token does not match the declared CMD 6.44 clock convention"
            raise NativeBoundaryError(message, status="incomplete_output", code="native_clock_convention", manifest=manifest_path)
    raw = tuple(source_report.lines[row.line - 1].split() for row in report.rows)
    outputs_by_site: list[EngineHydrograph] = []
    for location in loaded.run.catchment.print_locations:
        column = dict(config.print_columns)[location.identifier]
        position = report.columns.index(column)
        tokens = tuple(items[position + 2] for items in raw)
        values = tuple(float(row.values[position]) for row in report.rows)
        if any(not math.isfinite(value) for value in values):
            message = "Native discharge overflows the common finite float boundary"
            raise NativeBoundaryError(message, status="incomplete_output", code="native_float_boundary", manifest=manifest_path)
        outputs_by_site.append(EngineHydrograph(location.identifier, location.label, values, column, tokens))
    return NativeObservation(
        tuple(outputs_by_site),
        tuple(str(row.time_hours) for row in report.rows),
        tuple(fields[0] for fields in raw),
        tuple(row.raw_time for row in report.rows),
        config.executable_sha256,
        config.observed_version,
        source_report.sha256,
        str(manifest_path.absolute()),
    )


def run_native_cmd(loaded: LoadedProject, config: NativeConfiguration, project_path: Path) -> NativeObservation:
    """Isolated capture with a strict S0 manifest/S1 report gate; never infer internal state."""
    source = _preflight(loaded, config)
    # Only the temporary specification is deleted; S0 records persist in exclusive directories.
    with TemporaryDirectory(prefix="runoff-routing-cmd-") as temporary:
        # The source owner is the original project, not the temporary spec folder.
        spec = _make_spec(loaded, config, source, Path(temporary), project_path.absolute().parent)
        manifest = capture_cmd(spec, config.output_root, execute=True)
    if manifest is None:
        message = "Opt-in S0 capture unexpectedly returned without execution"
        raise NativeBoundaryError(message, status="native_execution_failed", code="native_not_executed")
    return _inspect(manifest, loaded, config)
