"""Multiple code-7 CMD prints: original control order and separate physical identities.

All controls are manufactured. Original code-11 native output remains incomplete.
"""

from __future__ import annotations

import hashlib
import subprocess
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from typing import cast

import pytest

from runoff_routing._cmd644.models import Control, Event, NumberInput
from runoff_routing._cmd644.precision import store
from runoff_routing._cmd644.reporting import CandidateResult
from runoff_routing._cmd644.reporting import execute as execute_unmodified
from runoff_routing.engine_execution import run_engine_project
from runoff_routing.engine_types import EngineSelection
from runoff_routing.integration import canonical_run_bytes
from runoff_routing.native_cmd import NativeConfiguration
from runoff_routing.project_json import EmbeddedRun, LegacyRunFiles, Project, SourceFile, write_project
from runoff_routing.rorb_model import (
    ControlStep,
    PrintLocation,
    Reach,
    RunModel,
    from_json,
)

EXAMPLE = Path(__file__).parents[1] / "examples" / "synthetic-run.json"


def _model() -> RunModel:
    loaded = from_json(EXAMPLE.read_text(encoding="utf-8"))
    assert isinstance(loaded, RunModel)
    return loaded


def _multiple_prints() -> RunModel:
    model = _model()
    catchment = model.catchment
    internal = PrintLocation("interior", "Before downstream reach")
    extension = Reach("downstream_reach", Decimal("2.5"))
    modified = replace(
        catchment,
        reaches=(*catchment.reaches, extension),
        controls=(
            catchment.controls[0],
            ControlStep(7, print_id=internal.identifier),
            ControlStep(5, reach_id=extension.identifier),
            catchment.controls[-1],
        ),
        print_locations=(internal, *catchment.print_locations),
    )
    return replace(model, catchment=modified)


def _project(root: Path, model: RunModel) -> Path:
    path = root / "multisite.json"
    write_project(path, Project("cmd_multisite", "explicit", EmbeddedRun(model)))
    return path


def test_cmd_reports_all_requested_sites_with_full_horizon_and_original_control_order(tmp_path: Path) -> None:
    model = _multiple_prints()
    path = _project(tmp_path, model)
    outcome = run_engine_project(path, selection=EngineSelection.for_engine("python-cmd"))
    assert outcome.status == "computed_unvalidated"
    assert outcome.native_parity_status == "not_assessed"
    assert outcome.control_order == (1, 7, 5, 7)
    assert outcome.requested_print_ids == ("interior", "print_1")
    assert tuple(item.print_id for item in outcome.hydrographs) == outcome.requested_print_ids
    assert tuple(item.label for item in outcome.hydrographs) == (
        "Before downstream reach",
        model.catchment.print_locations[-1].label,
    )
    assert len(outcome.physical_time_hours) == 6
    assert all(len(item.discharge_m3_s) == 6 for item in outcome.hydrographs)
    assert outcome.hydrographs[0].discharge_m3_s != outcome.hydrographs[1].discharge_m3_s
    assert all(item.native_column_id is None for item in outcome.hydrographs)
    assert outcome.native_raw_time_tokens == ()

    assert outcome.python_diagnostics is not None
    sites = cast("tuple[dict[str, object], ...]", outcome.python_diagnostics["print_sites"])
    assert tuple(item["print_id"] for item in sites) == outcome.requested_print_ids
    assert tuple(item["control_index_one_based"] for item in sites) == (2, 4)
    assert sites[0]["source_membership_ids"] == (model.catchment.subareas[0].identifier,)
    assert sites[0]["Q_m3_s_stored"] == outcome.hydrographs[0].discharge_m3_s
    assert sites[1]["Q_m3_s_stored"] == outcome.hydrographs[1].discharge_m3_s

    # These are distinct computed volume definitions, NOT original native reported volumes.
    final = outcome.hydrographs[-1].discharge_m3_s
    dt_seconds = float(model.storm.timestep_hours) * 3600
    inclusive = sum(final) * dt_seconds
    trapezoid = (sum(final) - (final[0] + final[-1]) / 2) * dt_seconds
    assert inclusive > trapezoid > 0


def test_default_engine_preserves_two_requested_sites_without_cmd_fallback(tmp_path: Path) -> None:
    path = _project(tmp_path, _multiple_prints())
    outcome = run_engine_project(path)
    assert outcome.effective_selection.engine == "python"
    assert outcome.status == "computed_unvalidated"
    assert tuple(item.print_id for item in outcome.hydrographs) == ("interior", "print_1")
    assert len(outcome.hydrographs) == 2
    assert all(len(item.discharge_m3_s) == 6 for item in outcome.hydrographs)
    assert outcome.hydrographs[0].discharge_m3_s != outcome.hydrographs[1].discharge_m3_s


def test_duplicate_missing_and_mismatched_site_identities_fail_closed() -> None:
    model = _multiple_prints()
    catchment = model.catchment
    with pytest.raises(ValueError, match="Duplicate"):
        replace(
            catchment,
            print_locations=(catchment.print_locations[0], catchment.print_locations[0]),
        )
    with pytest.raises(ValueError, match=r"Unbalanced|Code 7"):
        replace(catchment, print_locations=(catchment.print_locations[0],))
    with pytest.raises(ValueError, match="Code 7"):
        replace(
            catchment,
            controls=(
                catchment.controls[0],
                replace(catchment.controls[1], print_id="unmapped"),
                *catchment.controls[2:],
            ),
        )


def test_unproven_code_eleven_is_explicitly_rejected_not_inferred_from_code_seven() -> None:
    model = _multiple_prints()
    catchment = model.catchment
    with pytest.raises(ValueError, match="Unsupported control code 11"):
        replace(
            catchment,
            controls=(*catchment.controls[:-1], ControlStep(11), catchment.controls[-1]),  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    ("damage", "reason"),
    [
        ("missing", "cmd_print_sites"),
        ("truncated", "cmd_print_sites"),
        ("reversed", "cmd_print_order"),
        ("duplicate_index", "cmd_print_order"),
        ("wrong_final", "cmd_final_print"),
    ],
)
def test_cmd_omitted_truncated_or_wrong_print_never_returns_partial_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, damage: str, reason: str
) -> None:
    """Reject damaged backend output before mapping any physical print identity."""
    path = _project(tmp_path, _multiple_prints())

    def damaged_execute(event: Event, revision: str) -> CandidateResult:
        actual = execute_unmodified(event, revision)
        recorded = actual.network.prints
        if damage == "missing":
            changed = recorded[:-1]
        elif damage == "truncated":
            changed = (replace(recorded[0], q=recorded[0].q[:-1]), *recorded[1:])
        elif damage == "reversed":
            changed = recorded[::-1]
        elif damage == "duplicate_index":
            changed = (recorded[0], replace(recorded[1], control_index_one_based=recorded[0].control_index_one_based))
        else:
            final = recorded[-1]
            changed = (
                *recorded[:-1],
                replace(final, q=(*final.q[:-1], final.q[-1] + 1.0)),
            )
        return replace(actual, network=replace(actual.network, prints=changed))

    monkeypatch.setattr("runoff_routing.cmd_engine.execute", damaged_execute)
    outcome = run_engine_project(path, selection=EngineSelection.for_engine("python-cmd"))

    assert outcome.status == "incomplete_output"
    assert outcome.diagnostics[0].code == reason
    assert outcome.requested_print_ids == ("interior", "print_1")
    assert outcome.hydrographs == ()
    assert outcome.physical_time_hours == ()


@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), -1.0])
def test_cmd_rejects_invalid_numeric_print_ordinates_before_exposing_any_site(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, invalid: float
) -> None:
    """Even a nonterminal site must not leak invalid physical discharge."""
    project = _project(tmp_path, _multiple_prints())

    def corrupted_execute(event: Event, revision: str) -> CandidateResult:
        original = execute_unmodified(event, revision)
        first = original.network.prints[0]
        corrupt = replace(first, q=(*first.q[:2], invalid, *first.q[3:]))
        return replace(original, network=replace(original.network, prints=(corrupt, *original.network.prints[1:])))

    monkeypatch.setattr("runoff_routing.cmd_engine.execute", corrupted_execute)
    outcome = run_engine_project(project, selection=EngineSelection.for_engine("python-cmd"))
    assert outcome.status == "incomplete_output"
    assert outcome.diagnostics[0].code == "cmd_print_values"
    assert outcome.requested_print_ids == ("interior", "print_1")
    assert outcome.hydrographs == ()
    assert outcome.physical_time_hours == ()


def _native_two_prints() -> RunModel:
    """Canonical IDs make this authored multi-site model round-trip via RORB_GE 002."""
    model = _model()
    original = model.catchment
    updated = replace(
        original,
        reaches=(*original.reaches, Reach("reach_2", Decimal("2.5"))),
        controls=(
            original.controls[0],
            ControlStep(7, print_id="print_1"),
            ControlStep(5, reach_id="reach_2"),
            ControlStep(7, print_id="print_2"),
        ),
        print_locations=(
            PrintLocation("print_1", "Before second reach"),
            PrintLocation("print_2", "After second reach"),
        ),
    )
    return replace(model, catchment=updated)


@pytest.mark.parametrize("complete", [True, False])
def test_mocked_native_two_site_columns_preserve_identities_or_reject_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, complete: bool
) -> None:
    """Actual selected native adapter, manufactured process: no RORB parity claim."""
    model = _native_two_prints()
    files: list[SourceFile] = []
    for name, data in zip(("model.par", "model.catg", "model.stm"), canonical_run_bytes(model), strict=True):
        (tmp_path / name).write_bytes(data)
        files.append(SourceFile(name, hashlib.sha256(data).hexdigest()))
    project = tmp_path / "legacy-project.json"
    write_project(
        project,
        Project(
            "native_two_prints",
            "legacy-rorb",
            LegacyRunFiles(files[0], files[1], files[2]),
            engine=EngineSelection.for_engine("rorb-cmd"),
        ),
    )
    executable = tmp_path / "mock-cmd.exe"
    executable.write_bytes(b"manufactured native multi-site adapter test only")
    config = NativeConfiguration(
        executable=executable,
        executable_sha256=hashlib.sha256(executable.read_bytes()).hexdigest(),
        observed_version="6.44",
        observed_banner="synthetic mocked CMD output",
        numerical_profile="cmd-6.44",
        output_root=tmp_path / "captures",
        print_columns=(("print_1", "Hyd001"), ("print_2", "Hyd002")),
        timeout_seconds=5,
    )

    def fake_run(*_args: object, **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        root = kwargs["cwd"]
        assert isinstance(root, Path)
        assert (root / "reference.par").is_file()
        head = "Inc Time Hyd001 Hyd002" if complete else "Inc Time Hyd001"
        records = [
            f"{index} {index * 0.5:.2f} {index - 1:.4f}" + (f" {2 * (index - 1):.4f}" if complete else "")
            for index in range(1, 7)
        ]
        (root / "native.out").write_text(
            "Time increment (hours)= 0.5\nDuration of calculations: 5\n" + head + "\n" + "\n".join(records) + "\nEnd\n",
            encoding="utf-8",
        )
        return subprocess.CompletedProcess([executable.name], 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = run_engine_project(project, native_config=config)
    assert result.effective_selection.engine == "rorb-cmd"
    assert result.requested_print_ids == ("print_1", "print_2")
    assert result.capture_manifest_path is not None
    if not complete:
        assert result.status == "incomplete_output"
        assert result.hydrographs == ()
        return
    assert result.status == "computed_unvalidated", result.diagnostics
    assert tuple(h.print_id for h in result.hydrographs) == ("print_1", "print_2")
    assert tuple(h.native_column_id for h in result.hydrographs) == ("Hyd001", "Hyd002")
    assert result.hydrographs[0].discharge_m3_s == (0, 1, 2, 3, 4, 5)
    assert result.hydrographs[1].discharge_m3_s == (0, 2, 4, 6, 8, 10)
    assert result.hydrographs[1].native_discharge_tokens == (
        "0.0000",
        "2.0000",
        "4.0000",
        "6.0000",
        "8.0000",
        "10.0000",
    )
    assert result.native_raw_increment_tokens == ("1", "2", "3", "4", "5", "6")
    assert result.native_raw_time_tokens == ("0.50", "1.00", "1.50", "2.00", "2.50", "3.00")
    assert result.physical_time_hours == result.native_raw_time_tokens

def _synthetic_number(value: float) -> NumberInput:
    return NumberInput(str(value), value, store(value))


@pytest.mark.parametrize("loss_model", [1, 2])
def test_code_two_and_impervious_fraction_preserve_ordered_multiple_prints(loss_model: int) -> None:
    """Internal #96/#91 interoperation: authored controls, not a PR16 original CMD golden."""
    number = _synthetic_number
    event = Event(
        "authored_code2_two_prints",
        "not-an-original-source-hash",
        "{}",
        (
            Control(1, number(1.0)),
            Control(7, number(0.0)),
            Control(2, number(2.0)),
            Control(7, number(0.0)),
        ),
        (number(2.0), number(3.0)),
        (number(10.0), number(20.0)),
        (number(0.5), number(0.2)),
        (number(50.0), number(50.0)),
        number(0.5),
        number(5.0),
        number(1.0),
        number(2.0),
        number(0.5),
        4,
        loss_model,
    )
    candidate = execute_unmodified(event, "authored")
    print_records = candidate.network.prints
    assert tuple(site.control_index_one_based for site in print_records) == (2, 4)
    assert tuple(site.membership for site in print_records) == ((1,), (1, 2))
    assert len(candidate.network.reaches) == 2
    assert candidate.network.reaches[0].membership == (1,)
    assert candidate.network.reaches[1].membership == (1, 2)
    assert all(len(site.q) == event.n + 1 for site in print_records)
    assert print_records[0].q == candidate.network.reaches[0].q
    assert print_records[1].q == candidate.network.outlet
    assert print_records[0].q != print_records[1].q

    no_impervious = replace(event, impervious=(number(0.0), number(0.0)))
    unmodified = execute_unmodified(no_impervious, "authored")
    assert candidate.preparation.excess[0] != unmodified.preparation.excess[0]
    assert candidate.preparation.excess[1] != unmodified.preparation.excess[1]
    assert print_records[0].q != unmodified.network.prints[0].q
    assert print_records[1].q != unmodified.network.prints[1].q

