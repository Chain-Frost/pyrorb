"""Explicit three-engine project dispatch without implicit fallback.

The established run_model and run_project APIs remain Python-only compatibility
interfaces; run_engine_project is the common product API.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict, replace
from pathlib import Path
from typing import Literal

from .cmd_engine import CMD_PROFILE, CmdBoundaryError, PreparedCmdModel, run_cmd_model
from .engine_provenance import identify_implementation, verify_installed_wheel
from .engine_types import EngineDiagnostic, EngineHydrograph, EngineOutcome, EngineSelection, EngineStatus
from .integration import RunInputError, run_model
from .native_cmd import NativeBoundaryError, NativeConfiguration, run_native_cmd
from .project_json import LoadedProject, load_project
from .rorb_model import to_json
from .single_storm import PreparedCatchment

SelectionSource = Literal["project", "api_override", "cli_override"]


def create_engine_outcome_base(
    loaded: LoadedProject, selection: EngineSelection, source: SelectionSource
) -> EngineOutcome:
    """Report source and effective choices, even for unsuccessful execution."""
    model = loaded.run
    settings: dict[str, str | int] = {
        "timestep_hours": str(model.storm.timestep_hours),
        "calculation_increments": model.storm.calculation_increments,
        "loss_model": model.parameters.loss_model,
        "num_isa": model.parameters.num_isa,
        "num_bursts": model.parameters.num_bursts,
    }
    return EngineOutcome(
        project_id=loaded.project.identifier,
        project_sha256=hashlib.sha256(loaded.original_json_bytes).hexdigest(),
        model_sha256=hashlib.sha256(to_json(model).encode("utf-8")).hexdigest(),
        source_file_hashes=loaded.file_hashes,
        stored_selection=loaded.project.engine,
        effective_selection=selection,
        selection_source=source,
        status="invalid_input",
        event_id=loaded.project.identifier,
        rainfall_profile=loaded.project.rainfall_profile,
        requested_print_ids=tuple(site.identifier for site in model.catchment.print_locations),
        control_order=tuple(step.code for step in model.catchment.controls),
        effective_inputs=settings,
    )


def _failure(
    base: EngineOutcome,
    status: EngineStatus,
    code: str,
    message: str,
    *,
    manifest: Path | None = None,
) -> EngineOutcome:
    return replace(
        base,
        status=status,
        diagnostics=(EngineDiagnostic(code, message),),
        capture_manifest_path=str(manifest.absolute()) if manifest is not None else None,
    )


def attribute_engine_outcome(base: EngineOutcome, wheel_artifact: Path | None) -> EngineOutcome:
    """Bind exact package bytes and, when supplied, a source-matched wheel before dispatch."""
    try:
        identity = identify_implementation()
    except (OSError, ValueError) as exc:
        return _failure(base, "invalid_input", "implementation_identity", str(exc))
    attributed = replace(base, implementation_revision=identity.revision, package_version=identity.package_version)
    if wheel_artifact is None:
        return attributed
    try:
        wheel_hash = verify_installed_wheel(wheel_artifact)
    except (OSError, ValueError) as exc:
        return _failure(attributed, "invalid_input", "wheel_identity", str(exc))
    return replace(attributed, verified_wheel_sha256=wheel_hash)


def _python(loaded: LoadedProject, base: EngineOutcome, *, prepared: PreparedCatchment | None = None) -> EngineOutcome:
    if loaded.project.rainfall_profile == "arr-2026v1":
        return _failure(
            base,
            "unsupported_feature",
            "rainfall_profile",
            "ARR rainfall must be prepared by an independently validated S6 event adapter",
        )
    if any(asset.role != "reference" for asset in loaded.project.assets):
        return _failure(
            base,
            "unsupported_feature",
            "unprepared_rainfall",
            "External rainfall, temporal pattern and curve assets are unprocessed",
        )
    try:
        result = run_model(loaded.run, prepared=prepared)
    except RunInputError as exc:
        state: EngineStatus = (
            "invalid_input"
            if exc.status == "invalid"
            else "numerical_error"
            if exc.code in ("nonfinite_result", "solver_numerical")
            else "unsupported_feature"
        )
        return _failure(base, state, exc.code, str(exc))
    horizon = loaded.run.storm.calculation_increments + 1
    if any(len(point.discharge_m3_s) != horizon for point in result.prints):
        return _failure(base, "incomplete_output", "python_horizon", "Computed hydrograph did not cover full horizon")
    return replace(
        base,
        status="computed_unvalidated",
        hydrographs=tuple(
            EngineHydrograph(point.print_id, point.label, point.discharge_m3_s) for point in result.prints
        ),
        physical_time_hours=tuple(str(index * loaded.run.storm.timestep_hours) for index in range(horizon)),
        internal_quantities="python_available",
        python_diagnostics=asdict(result.numerical),
    )


def _python_cmd(
    loaded: LoadedProject,
    base: EngineOutcome,
    native_config: NativeConfiguration | None,
    *,
    prepared: PreparedCmdModel | None = None,
) -> EngineOutcome:
    """Run only the selected CMD profile; never reuse the improved engine."""

    if native_config is not None:
        return _failure(base, "invalid_input", "unused_native_config", "Native configuration requires rorb-cmd")
    if base.effective_selection.numerical_profile != CMD_PROFILE:
        return _failure(base, "unavailable_engine", "cmd_profile", "Only the cmd-6.44 Python profile is implemented")
    try:
        computed = run_cmd_model(loaded, base.implementation_revision or "unattributed", prepared=prepared)
    except CmdBoundaryError as exc:
        return _failure(base, exc.status, exc.code, str(exc))
    return replace(
        base,
        status="computed_unvalidated",
        hydrographs=computed.hydrographs,
        physical_time_hours=computed.physical_time_hours,
        internal_quantities="python_available",
        python_diagnostics=computed.diagnostics,
    )


def execute_loaded_engine(
    loaded: LoadedProject,
    base: EngineOutcome,
    *,
    project_path: Path,
    native_config: NativeConfiguration | None = None,
    prepared_python: PreparedCatchment | None = None,
    prepared_cmd: PreparedCmdModel | None = None,
) -> EngineOutcome:
    """Dispatch an already verified, in-memory S1 event using its attributed outcome.

    The caller owns source validation and immutable per-event model construction.
    This is the same dispatcher used by single-project and explicit-batch APIs.
    The native adapter always receives the real original project path.
    """
    if base.diagnostics:
        return base
    effective = base.effective_selection
    if effective.engine == "python":
        if native_config is not None:
            return _failure(base, "invalid_input", "unused_native_config", "Native configuration requires rorb-cmd")
        return _python(loaded, base, prepared=prepared_python)
    if effective.engine == "python-cmd":
        return _python_cmd(loaded, base, native_config, prepared=prepared_cmd)
    if native_config is None:
        return _failure(
            base,
            "unavailable_engine",
            "native_config_required",
            "rorb-cmd requires explicit local --native-config with executable SHA-256 and HydNNN mapping",
        )
    if native_config.numerical_profile != effective.numerical_profile:
        return _failure(
            base,
            "unavailable_engine",
            "native_profile_mismatch",
            "Selected numerical profile does not match the reviewed executable configuration",
        )
    try:
        observation = run_native_cmd(loaded, native_config, project_path)
    except NativeBoundaryError as exc:
        return _failure(base, exc.status, exc.code, str(exc), manifest=exc.manifest)
    except (OSError, ValueError, TypeError) as exc:
        return _failure(base, "native_execution_failed", "native_adapter_error", str(exc))
    return replace(
        base,
        status="computed_unvalidated",
        hydrographs=observation.hydrographs,
        physical_time_hours=observation.physical_time_hours,
        native_raw_increment_tokens=observation.raw_increment_tokens,
        native_raw_time_tokens=observation.raw_time_tokens,
        native_clock_convention="cmd-6.44-observed-1-based-no-shift",
        native_executable_sha256=observation.executable_sha256,
        native_observed_version=observation.observed_version,
        native_output_sha256=observation.output_sha256,
        capture_manifest_path=observation.manifest_path,
        internal_quantities="native_unavailable",
    )


def run_engine_project(
    project_path: Path,
    *,
    selection: EngineSelection | None = None,
    selection_source: SelectionSource = "api_override",
    native_config: NativeConfiguration | None = None,
    wheel_artifact: Path | None = None,
) -> EngineOutcome:
    """Verify a project once, then use the shared in-memory event dispatcher.

    An explicit API/CLI selection overrides the stored project choice. The
    original/effective choices remain visible and no engine is substituted.
    """
    loaded = load_project(project_path)
    effective = loaded.project.engine if selection is None else selection
    provenance: SelectionSource = "project" if selection is None else selection_source
    base = attribute_engine_outcome(create_engine_outcome_base(loaded, effective, provenance), wheel_artifact)
    return execute_loaded_engine(loaded, base, project_path=project_path, native_config=native_config)


def write_engine_result(path: Path, outcome: EngineOutcome) -> None:
    """No-clobber project run report, including typed failure details."""
    with path.open("xb") as stream:
        stream.write(outcome.to_json().encode("utf-8"))


def run_cli(argv: list[str]) -> int:
    """The run subcommand: explicit override precedence and opt-in native execution."""
    parser = argparse.ArgumentParser(prog="python -m runoff_routing.project_json run")
    parser.add_argument("project", type=Path)
    parser.add_argument("result", type=Path)
    parser.add_argument("--engine", choices=("python", "python-cmd", "rorb-cmd"))
    parser.add_argument("--numerical-profile")
    parser.add_argument("--native-config", type=Path)
    parser.add_argument("--wheel-artifact", type=Path)
    try:
        options = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2
    if options.engine is None and options.numerical_profile is not None:
        print("--numerical-profile requires an explicit --engine (or edit the project)", file=sys.stderr)
        return 2
    if options.result.exists() or options.result.is_symlink():
        print(f"Result already exists: {options.result}", file=sys.stderr)
        return 2
    try:
        chosen = (
            EngineSelection.for_engine(options.engine, options.numerical_profile)
            if options.engine is not None
            else None
        )
        config = NativeConfiguration.from_file(options.native_config) if options.native_config is not None else None
        outcome = run_engine_project(
            options.project,
            selection=chosen,
            selection_source="cli_override",
            native_config=config,
            wheel_artifact=options.wheel_artifact,
        )
        write_engine_result(options.result, outcome)
    except (OSError, ValueError, TypeError) as exc:
        print(f"Project execution failed: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "status": outcome.status,
                "native_parity_status": outcome.native_parity_status,
                "project_sha256": outcome.project_sha256,
                "model_sha256": outcome.model_sha256,
                "stored_engine": outcome.stored_selection.engine,
                "effective_engine": outcome.effective_selection.engine,
                "implementation_revision": outcome.implementation_revision,
                "verified_wheel_sha256": outcome.verified_wheel_sha256,
                "result": str(options.result),
            },
            sort_keys=True,
        )
    )
    return 0 if outcome.status == "computed_unvalidated" else 2
