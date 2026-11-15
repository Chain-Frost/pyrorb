"""Engine-facing CMD regression admission and effective-time attribution controls.

Keep these checks independent of the numerical kernel and original CMD reports.
"""

from __future__ import annotations

import json
import runpy
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path
from typing import Any, cast

import pytest

from runoff_routing.engine_execution import run_engine_project
from runoff_routing.engine_types import EngineOutcome, EngineSelection
from runoff_routing.project_json import EmbeddedRun, Project, project_to_json, write_project
from runoff_routing.rorb_model import RunModel, from_json

ROOT = Path(__file__).parents[1]
Checker = Callable[[dict[str, Any], RunModel, EngineOutcome, str], str | None]


def _check() -> Checker:
    namespace = runpy.run_path(str(ROOT / "repo-scripts" / "cmd_public_probe.py"))
    return cast("Checker", namespace["_binding_error"])


def _example(tmp_path: Path) -> tuple[dict[str, Any], RunModel, EngineOutcome, str]:
    model = from_json((ROOT / "examples" / "synthetic-run.json").read_text(encoding="utf-8"))
    assert isinstance(model, RunModel)
    project = Project(
        "case_one",
        "explicit",
        EmbeddedRun(model),
        engine=EngineSelection.for_engine("python-cmd"),
    )
    text = project_to_json(project)
    path = tmp_path / "case.json"
    write_project(path, project)
    outcome = run_engine_project(path)
    assert outcome.status == "computed_unvalidated"
    case: dict[str, Any] = {
        "case_id": "case_one",
        "clock": {
            "row_count": model.storm.calculation_increments + 1,
            "timestep_hours": str(model.storm.timestep_hours),
        },
        "sites": [{"model_print_id": model.catchment.print_locations[0].identifier, "native_column_id": "Hyd001"}],
    }
    return case, model, outcome, text


def test_fresh_probe_accepts_matching_source_clock_and_single_terminal_site(tmp_path: Path) -> None:
    case, model, outcome, text = _example(tmp_path)
    assert _check()(case, model, outcome, text) is None


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("physical_time_hours", ()),
        ("physical_time_hours", ("0.5", "1.0", "1.5", "2.0", "2.5", "3.0")),
        ("project_id", "different"),
        ("event_id", "different"),
        ("model_sha256", "0" * 64),
        ("project_sha256", "0" * 64),
        ("requested_print_ids", ()),
        ("control_order", (7, 1)),
        ("implementation_revision", None),
        ("native_raw_time_tokens", ("0.5",)),
    ],
)
def test_fresh_probe_rejects_attribution_or_generated_axis_changes(tmp_path: Path, field: str, invalid: object) -> None:
    case, model, outcome, text = _example(tmp_path)
    modified = replace(outcome, **{field: invalid})
    assert _check()(case, model, modified, text) is not None


def test_fresh_probe_rejects_wrong_registered_clock_and_print_mapping(tmp_path: Path) -> None:
    case, model, outcome, text = _example(tmp_path)
    case["clock"]["row_count"] += 1
    assert _check()(case, model, outcome, text) is not None
    case["clock"]["row_count"] -= 1
    case["clock"]["timestep_hours"] = "0.75"
    assert _check()(case, model, outcome, text) is not None
    case["clock"]["timestep_hours"] = str(model.storm.timestep_hours)
    case["sites"][0]["model_print_id"] = "other"
    assert _check()(case, model, outcome, text) is not None


def test_scalar_failure_forces_nonzero_even_when_every_retained_q_passes(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Exercise the actual bounded CLI exit gate with one manufactured failed scalar."""
    namespace = runpy.run_path(str(ROOT / "repo-scripts" / "cmd_public_probe.py"))
    main = cast("Callable[[], int]", namespace["main"])

    def fake_one(case: dict[str, Any]) -> dict[str, Any]:
        retained = "cmd-reviewed" in case["sets"] or "timestep" in case["sets"]
        if not retained:
            return {"case_id": case["case_id"], "status": "source_unsupported"}
        return {
            "case_id": case["case_id"],
            "status": "printed_pass",
            "rows": case["clock"]["row_count"],
            "fresh_reporting": {"classification": "fail" if case["case_id"] == "review-design-baseline" else "pass"},
        }

    monkeypatch.setitem(main.__globals__, "_one", fake_one)
    assert main() == 1
    report = json.loads(capsys.readouterr().out)
    assert report["retained_36_case_printed_baseline"] == "pass"
    assert report["retained_36_case_fresh_scalar_baseline"] == "fail"
    assert report["retained_scalar_baseline_failures"] == ["review-design-baseline"]
    assert report["fresh_reporting_full_population"] == "fail"
    assert report["cases_checked"] == 50


def test_scalar_baseline_pass_retains_full_population_incomplete(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """All admitted scalar passes cannot erase 14 explicitly uncomputed source cases."""
    namespace = runpy.run_path(str(ROOT / "repo-scripts" / "cmd_public_probe.py"))
    main = cast("Callable[[], int]", namespace["main"])

    def fake_one(case: dict[str, Any]) -> dict[str, Any]:
        retained = "cmd-reviewed" in case["sets"] or "timestep" in case["sets"]
        if not retained:
            return {"case_id": case["case_id"], "status": "source_unsupported"}
        return {
            "case_id": case["case_id"],
            "status": "printed_pass",
            "rows": case["clock"]["row_count"],
            "fresh_reporting": {"classification": "pass"},
        }

    monkeypatch.setitem(main.__globals__, "_one", fake_one)
    assert main() == 0
    report = json.loads(capsys.readouterr().out)
    assert report["retained_36_case_printed_baseline"] == "pass"
    assert report["retained_36_case_fresh_scalar_baseline"] == "pass"
    assert report["retained_scalar_baseline_failures"] == []
    assert report["fresh_reporting_full_population"] == "incomplete"


@pytest.mark.parametrize(
    ("status", "scalar_classification", "row_override"),
    [
        ("printed_fail", "pass", None),
        ("printed_invalid", "pass", None),
        ("printed_pass", "fail", None),
        ("printed_pass", "invalid", None),
        ("printed_pass", "not_run", None),
        ("printed_pass", "unexpected", None),
        ("printed_pass", "pass", 1),
        ("unverified_attribution", "not_run", None),
    ],
)
def test_unretained_admitted_failure_is_not_masked_by_the_retained_baseline(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    status: str,
    scalar_classification: str,
    row_override: int | None,
) -> None:
    """A new H1 Q/scalar failure must fail the same public probe, not disappear."""
    namespace = runpy.run_path(str(ROOT / "repo-scripts" / "cmd_public_probe.py"))
    main = cast("Callable[[], int]", namespace["main"])
    affected = "H1-three-source-asymmetric"

    def fake_one(case: dict[str, Any]) -> dict[str, Any]:
        case_id = str(case["case_id"])
        if "cmd-reviewed" in case["sets"] or "timestep" in case["sets"]:
            return {
                "case_id": case_id,
                "status": "printed_pass",
                "rows": case["clock"]["row_count"],
                "fresh_reporting": {"classification": "pass"},
            }
        if case_id == affected:
            return {
                "case_id": case_id,
                "status": status,
                "rows": case["clock"]["row_count"] if row_override is None else row_override,
                "fresh_reporting": {"classification": scalar_classification},
                "first_mismatch": {"sample_index": 2},
            }
        return {"case_id": case_id, "status": "source_unsupported"}

    monkeypatch.setitem(main.__globals__, "_one", fake_one)
    assert main() == 1
    report = json.loads(capsys.readouterr().out)
    assert report["cases_checked"] == 50
    assert report["retained_36_case_printed_baseline"] == "pass"
    assert report["retained_36_case_fresh_scalar_baseline"] == "pass"
    assert report["nonretained_case_failure_gate"] == "fail"
    assert report["nonretained_case_diagnostic_failures"] == [affected]
    assert next(item for item in report["results"] if item["case_id"] == affected)["first_mismatch"] == {
        "sample_index": 2
    }


def test_new_admission_with_incomplete_scalar_is_reported_without_fake_failure(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """H2 and zero-flow incomplete fields must remain incomplete, not failed or passing."""
    namespace = runpy.run_path(str(ROOT / "repo-scripts" / "cmd_public_probe.py"))
    main = cast("Callable[[], int]", namespace["main"])

    def fake_one(case: dict[str, Any]) -> dict[str, Any]:
        case_id = str(case["case_id"])
        if "cmd-reviewed" in case["sets"] or "timestep" in case["sets"]:
            return {
                "case_id": case_id,
                "status": "printed_pass",
                "rows": case["clock"]["row_count"],
                "fresh_reporting": {"classification": "pass"},
            }
        if case_id == "H2-four-source-nested-odd-rain":
            return {
                "case_id": case_id,
                "status": "printed_pass",
                "rows": case["clock"]["row_count"],
                "fresh_reporting": {"classification": "incomplete", "reason": "Unqualified stored timestep"},
            }
        return {"case_id": case_id, "status": "source_unsupported"}

    monkeypatch.setitem(main.__globals__, "_one", fake_one)
    assert main() == 0
    report = json.loads(capsys.readouterr().out)
    assert report["nonretained_case_failure_gate"] == "pass"
    assert report["nonretained_case_diagnostic_failures"] == []
    assert report["fresh_reporting_status_counts"]["incomplete"] == 1
    assert report["fresh_reporting_full_population"] == "incomplete"


@pytest.mark.parametrize(
    ("admission_status", "scalar_classification", "expected_exit", "expected_incomplete"),
    [
        ("source_unsupported", "not_run", 1, []),
        ("printed_pass", "incomplete", 0, ["H1-three-source-asymmetric"]),
        ("printed_pass", "pass", 0, []),
        ("printed_pass", "not_run", 1, []),
        ("printed_invalid", "pass", 1, []),
    ],
)
def test_required_admission_must_not_be_omitted_or_turned_into_false_scalar_success(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    admission_status: str,
    scalar_classification: str,
    expected_exit: int,
    expected_incomplete: list[str],
) -> None:
    """Only a named, computed and correctly classified new case can satisfy coverage."""
    namespace = runpy.run_path(str(ROOT / "repo-scripts" / "cmd_public_probe.py"))
    main = cast("Callable[[tuple[str, ...]], int]", namespace["main"])
    case_required = "H1-three-source-asymmetric"

    def fake_one(case: dict[str, Any]) -> dict[str, Any]:
        case_id = str(case["case_id"])
        if "cmd-reviewed" in case["sets"] or "timestep" in case["sets"]:
            return {
                "case_id": case_id,
                "status": "printed_pass",
                "rows": case["clock"]["row_count"],
                "fresh_reporting": {"classification": "pass"},
            }
        if case_id == case_required:
            return {
                "case_id": case_id,
                "status": admission_status,
                "rows": case["clock"]["row_count"] if admission_status != "source_unsupported" else 0,
                "fresh_reporting": {"classification": scalar_classification},
            }
        return {"case_id": case_id, "status": "source_unsupported"}

    monkeypatch.setitem(main.__globals__, "_one", fake_one)
    assert main((case_required,)) == expected_exit
    report = json.loads(capsys.readouterr().out)
    assert report["retained_36_case_printed_baseline"] == "pass"
    assert report["retained_36_case_fresh_scalar_baseline"] == "pass"
    assert report["required_case_ids"] == [case_required]
    assert report["required_case_scalar_incomplete"] == expected_incomplete
    assert report["required_case_gate"] == ("pass" if expected_exit == 0 else "fail")
    assert report["required_case_diagnostic_failures"] == ([] if expected_exit == 0 else [case_required])
    assert next(x for x in report["results"] if x["case_id"] == case_required)["status"] == admission_status


def test_required_case_selection_rejects_unknown_or_duplicate_without_computing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    namespace = runpy.run_path(str(ROOT / "repo-scripts" / "cmd_public_probe.py"))
    main = cast("Callable[[tuple[str, ...]], int]", namespace["main"])

    def must_not_run(_case: dict[str, Any]) -> dict[str, Any]:
        pytest.fail("Invalid required-case selection must fail before running any simulation")

    monkeypatch.setitem(main.__globals__, "_one", must_not_run)
    assert main(("unknown-original-id",)) == 2
    assert main(("H1-three-source-asymmetric", "H1-three-source-asymmetric")) == 2
    assert "--require-case must name distinct registered CMD-eligible" in capsys.readouterr().err
