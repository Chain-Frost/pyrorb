"""Multiple code-7 CMD prints: original control order and separate physical identities.

All controls are manufactured. Original code-11 native output remains incomplete.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from typing import cast

import pytest

from runoff_routing._cmd644.models import Event
from runoff_routing._cmd644.reporting import CandidateResult, execute as execute_unmodified
from runoff_routing.engine_execution import run_engine_project
from runoff_routing.engine_types import EngineSelection
from runoff_routing.project_json import EmbeddedRun, Project, write_project
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

