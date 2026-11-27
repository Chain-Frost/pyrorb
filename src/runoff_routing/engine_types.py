"""Stable product-engine choices and engine-independent result/provenance contracts.

A declared engine is never replaced by a different implementation to make a run succeed.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Literal


class EngineKind(StrEnum):
    PYTHON = "python"
    PYTHON_CMD = "python-cmd"
    RORB_CMD = "rorb-cmd"


class ResultStatus(StrEnum):
    COMPUTED_UNVALIDATED = "computed_unvalidated"
    UNAVAILABLE_ENGINE = "unavailable_engine"
    UNSUPPORTED_FEATURE = "unsupported_feature"
    INVALID_INPUT = "invalid_input"
    NUMERICAL_ERROR = "numerical_error"
    INCOMPLETE_OUTPUT = "incomplete_output"
    NATIVE_EXECUTION_FAILED = "native_execution_failed"


EngineId = Literal["python", "python-cmd", "rorb-cmd"]
EngineStatus = Literal[
    "computed_unvalidated",
    "unavailable_engine",
    "unsupported_feature",
    "invalid_input",
    "numerical_error",
    "incomplete_output",
    "native_execution_failed",
]
_DEFAULT_PROFILES: dict[EngineKind, str] = {
    EngineKind.PYTHON: "engineering-v1",
    EngineKind.PYTHON_CMD: "cmd-6.44",
    EngineKind.RORB_CMD: "cmd-6.44",
}


@dataclass(frozen=True, slots=True)
class EngineSelection:
    """Engine identity and versioned arithmetic profile; independent of rainfall preparation."""

    engine: EngineKind | EngineId = EngineKind.PYTHON_CMD
    numerical_profile: str = "cmd-6.44"

    def __post_init__(self) -> None:
        try:
            selected = EngineKind(self.engine)
        except (TypeError, ValueError) as exc:
            message = f"Unknown computation engine: {self.engine}"
            raise ValueError(message) from exc
        object.__setattr__(self, "engine", selected)
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", self.numerical_profile) is None:
            message = "Numerical profile must be a nonempty, versioned ASCII identifier"
            raise ValueError(message)
        if self.engine == "python" and self.numerical_profile != _DEFAULT_PROFILES[EngineKind.PYTHON]:
            message = "The current python backend implements only engineering-v1"
            raise ValueError(message)
        if self.engine != "python" and not self.numerical_profile.startswith("cmd-"):
            message = "CMD engine requires a named cmd-<version> numerical profile"
            raise ValueError(message)

    @classmethod
    def for_engine(cls, engine: str, numerical_profile: str | None = None) -> EngineSelection:
        """Resolve a deliberate override without borrowing another engine's profile."""
        try:
            selected = EngineKind(engine)
        except (TypeError, ValueError) as exc:
            message = f"Unknown computation engine: {engine}"
            raise ValueError(message) from exc
        return cls(selected, numerical_profile if numerical_profile is not None else _DEFAULT_PROFILES[selected])


@dataclass(frozen=True, slots=True)
class EngineCapability:
    """Declared product boundary, not a certificate of scientific acceptance."""

    engine: EngineId
    runtime_available: str
    input_scope: str
    result_scope: str
    numerical_acceptance: Literal["unassessed"] = "unassessed"


CAPABILITIES: tuple[EngineCapability, ...] = (
    EngineCapability(
        "python",
        "installed",
        "S1/S2 explicit DESIGN storm and supported pervious one-ISA routing",
        "Full typed Python hydrographs and Python internal diagnostics; not native-compatible",
    ),
    EngineCapability(
        "python-cmd",
        "installed bounded cmd-6.44 event backend; public native replay outstanding",
        "One explicit DESIGN pluviograph, pervious ISA/burst, lumped kc, IL/CL or IL/RoC, multiple code-7 prints",
        "Full computed hydrograph with separate CMD states/diagnostics; public native parity unaccepted",
    ),
    EngineCapability(
        "rorb-cmd",
        "requires explicit local executable and verified cmd-6.44 configuration",
        "Original file-backed .catg/.stm, one ISA/burst, lumped kc, pervious IL/CL",
        "Complete inspected HydNNN reports; native internal states unavailable",
    ),
)


@dataclass(frozen=True, slots=True)
class EngineDiagnostic:
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class EngineHydrograph:
    """Stable S1 print identity, with separate native column identity when present."""

    print_id: str
    label: str
    discharge_m3_s: tuple[float, ...]
    native_column_id: str | None = None
    native_discharge_tokens: tuple[str, ...] | None = None
    units: Literal["m3/s"] = "m3/s"


DiagnosticFlowKind = Literal[
    "subarea_upstream_flow",
    "rainfall_excess_flow",
    "reach_downstream_flow",
    "reach_upstream_flow",
]


@dataclass(frozen=True, slots=True)
class EngineDiagnosticFlow:
    """Computed diagnostic tap, not an ordinary print site or a native column claim."""

    series_id: str
    quantity_kind: DiagnosticFlowKind
    control_index_one_based: int
    subarea_id: str | None
    reach_id: str | None
    flow_m3_s: tuple[float, ...]
    units: Literal["m3/s"] = "m3/s"


@dataclass(frozen=True, slots=True)
class EngineOutcome:
    """Common output for success or explicit failure, with all engine choices visible."""

    project_id: str
    project_sha256: str
    model_sha256: str
    source_file_hashes: tuple[tuple[str, str], ...]
    stored_selection: EngineSelection
    effective_selection: EngineSelection
    selection_source: Literal["project", "api_override", "cli_override"]
    status: EngineStatus | ResultStatus
    event_id: str
    rainfall_profile: str
    requested_print_ids: tuple[str, ...]
    control_order: tuple[int, ...]
    effective_inputs: dict[str, str | int]
    diagnostics: tuple[EngineDiagnostic, ...] = ()
    hydrographs: tuple[EngineHydrograph, ...] = ()
    physical_time_hours: tuple[str, ...] = ()
    native_raw_increment_tokens: tuple[str, ...] = ()
    native_raw_time_tokens: tuple[str, ...] = ()
    native_clock_convention: str | None = None
    native_executable_sha256: str | None = None
    native_observed_version: str | None = None
    native_output_sha256: str | None = None
    capture_manifest_path: str | None = None
    internal_quantities: Literal["python_available", "native_unavailable", "not_computed"] = "not_computed"
    python_diagnostics: dict[str, object] | None = None
    implementation_revision: str | None = None
    package_version: str | None = None
    verified_wheel_sha256: str | None = None
    numerical_acceptance: Literal["unassessed"] = "unassessed"
    native_parity_status: Literal["not_assessed"] = "not_assessed"
    diagnostic_flows: tuple[EngineDiagnosticFlow, ...] = ()

    def __post_init__(self) -> None:
        try:
            selected = ResultStatus(self.status)
        except (TypeError, ValueError) as exc:
            message = f"Unknown project result status: {self.status}"
            raise ValueError(message) from exc
        object.__setattr__(self, "status", selected)

    @property
    def calculation_status(self) -> ResultStatus:
        """Typed project status; JSON still writes the established native string."""
        return ResultStatus(self.status)

    def to_json(self) -> str:
        """Full result with original native clock tokens and explicit nulls for missing internals."""
        return (
            json.dumps(
                {**asdict(self), "calculation_status": self.calculation_status},
                indent=2,
                sort_keys=True,
                allow_nan=False,
            )
            + "\n"
        )
