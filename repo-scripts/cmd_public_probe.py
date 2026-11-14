"""Offline public CMD engine applicability probe over the existing curated native controls.

Fresh computations use only the selected public `python-cmd` backend. The retained
RORB reports provide reference tokens, not computational inputs. Diagnostic result
classes are NOT scientific acceptance or proof of full CMD support.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, cast

from runoff_routing.engine_execution import run_engine_project
from runoff_routing.engine_types import EngineOutcome, EngineSelection
from runoff_routing.project_json import EmbeddedRun, Project, project_to_json
from runoff_routing.regression_dataset import compare_fresh_cmd_case
from runoff_routing.rorb_codec import RorbFormatError, parse_catg, parse_cmd_par, parse_design_stm
from runoff_routing.rorb_model import RunModel, to_json

ROOT = Path(__file__).absolute().parents[1] / "tests" / "fixtures" / "regression-v1"
REGISTER = ROOT / "register.json"


def _original_source(case: dict[str, Any], suffix: str) -> bytes:
    matching = [item for item in case["inputs"] if item["path"].endswith(suffix)]
    if len(matching) != 1:
        message = f"{case['case_id']}: expected one {suffix} input"
        raise ValueError(message)
    locator = matching[0]
    path = ROOT / locator["path"]
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
        message = f"{case['case_id']}: unsafe or missing published source"
        raise ValueError(message)
    raw = path.read_bytes()
    if len(raw) != locator["size_bytes"] or hashlib.sha256(raw).hexdigest() != locator["sha256"]:
        message = f"{case['case_id']}: changed source bytes"
        raise ValueError(message)
    return raw


def _typed_model(case: dict[str, Any]) -> RunModel:
    """Use only the maintained S1 decoders; do not create a separate native parser."""
    parameters = parse_cmd_par(_original_source(case, ".par")).model
    catchment = parse_catg(_original_source(case, ".catg")).model
    storm = parse_design_stm(_original_source(case, ".stm")).model
    return RunModel(parameters, catchment, storm)


def _identity_error(case: dict[str, Any], model: RunModel, outcome: EngineOutcome, project_text: str) -> str | None:
    """Bind produced event, typed source, control sequence and terminal outlet."""
    case_id = str(case["case_id"])
    if (
        outcome.status != "computed_unvalidated"
        or outcome.project_id != case_id
        or outcome.event_id != case_id
        or outcome.stored_selection != EngineSelection.for_engine("python-cmd")
        or outcome.effective_selection != EngineSelection.for_engine("python-cmd")
    ):
        return "Fresh CMD computation or project/event/engine identity differs"
    if outcome.project_sha256 != hashlib.sha256(project_text.encode("utf-8")).hexdigest():
        return "Original typed project identity differs"
    if outcome.model_sha256 != hashlib.sha256(to_json(model).encode("utf-8")).hexdigest():
        return "Original typed source/model identity differs"
    if not outcome.implementation_revision or not outcome.implementation_revision.startswith("package-code-v1-sha256:"):
        return "Actual installed CMD package-code revision is unavailable"
    controls = tuple(step.code for step in model.catchment.controls)
    prints = tuple(site.identifier for site in model.catchment.print_locations)
    if outcome.control_order != controls or outcome.requested_print_ids != prints:
        return "Actual ordered source/control or requested print identity differs"
    if len(case["sites"]) != 1 or len(prints) != 1 or not model.catchment.controls:
        return "Expected a single original physical print site"
    terminal = model.catchment.controls[-1]
    if terminal.code != 7 or terminal.print_id != prints[0] or case["sites"][0]["model_print_id"] != prints[0]:
        return "Terminal code-7 original source/print binding differs"
    if len(outcome.hydrographs) != 1 or outcome.hydrographs[0].print_id != prints[0]:
        return "Produced hydrograph is not the source's sole terminal print"
    if outcome.effective_inputs != {
        "timestep_hours": str(model.storm.timestep_hours),
        "calculation_increments": model.storm.calculation_increments,
        "loss_model": model.parameters.loss_model,
        "num_isa": model.parameters.num_isa,
        "num_bursts": model.parameters.num_bursts,
    }:
        return "Effective CMD source/parameter metadata differs"
    return None


def _clock_error(case: dict[str, Any], model: RunModel, outcome: EngineOutcome) -> str | None:
    """Check *produced* elapsed time, never native raw Inc/Time copied as output."""
    full_samples = model.storm.calculation_increments + 1
    if (
        len(outcome.hydrographs[0].discharge_m3_s) != full_samples
        or case["clock"]["row_count"] != full_samples
        or Decimal(case["clock"]["timestep_hours"]) != model.storm.timestep_hours
    ):
        return "Source or native registered full horizon/timestep differs"
    expected_elapsed = tuple(str(index * model.storm.timestep_hours) for index in range(full_samples))
    if outcome.physical_time_hours != expected_elapsed:
        return "Produced physical elapsed time axis differs from source timestep and full horizon"
    if outcome.native_raw_increment_tokens or outcome.native_raw_time_tokens:
        return "Python CMD must not invent observed native raw clock tokens"
    return None


def _binding_error(case: dict[str, Any], model: RunModel, outcome: EngineOutcome, project_text: str) -> str | None:
    """Fail closed on generated CMD metadata before the unchanged Q comparator.

    The native Hyd001 *physical* site mapping still needs independent B review.
    """
    return _identity_error(case, model, outcome, project_text) or _clock_error(case, model, outcome)


def _one(case: dict[str, Any]) -> dict[str, Any]:
    """A full fresh S1->public-CMD project execution, with explicit unsupported states."""
    case_id = str(case["case_id"])
    try:
        model = _typed_model(case)
    except (RorbFormatError, ValueError, TypeError) as exc:
        return {"case_id": case_id, "status": "source_unsupported", "reason": str(exc)}
    project = Project(case_id, "legacy-rorb", EmbeddedRun(model), engine=EngineSelection.for_engine("python-cmd"))
    with TemporaryDirectory(prefix="cmd-public-probe-") as directory:
        path = Path(directory) / "source.json"
        project_text = project_to_json(project)
        # Stable LF source bytes on Windows/Linux; fingerprint the exact written project.
        path.write_bytes(project_text.encode("utf-8"))
        outcome = run_engine_project(path)
    if outcome.status != "computed_unvalidated":
        return {
            "case_id": case_id,
            "status": outcome.status,
            "reason": outcome.diagnostics[0].message if outcome.diagnostics else "Typed calculation unavailable",
        }
    binding_failure = _binding_error(case, model, outcome, project_text)
    if binding_failure is not None:
        return {"case_id": case_id, "status": "unverified_attribution", "reason": binding_failure}
    comparison = compare_fresh_cmd_case(ROOT, case, outcome)
    mismatches = comparison.get("mismatches", [])
    return {
        "case_id": case_id,
        "status": f"printed_{comparison['classification']}",
        "rows": comparison.get("checked_ordinates", 0),
        "mismatch_count": len(mismatches),
        "first_mismatch": mismatches[0] if mismatches else None,
        "reason": comparison.get("reason"),
        "fresh_reporting": comparison.get("fresh_reporting"),
        # The matched Hyd001 column is registered source/control-derived;
        # there is no independently observed native physical-site label.
        "site_identity_evidence": case.get("observations", {}).get("physical_site_identity", "unverified"),
        "site_mapping_scope": "single_terminal_code7_source_derived_not_native_physical_label",
        "model_print_id": outcome.hydrographs[0].print_id,
        "original_native_column_id": case["sites"][0]["native_column_id"],
        "computed_time_scope": "model_elapsed_zero_based_i_times_source_h_not_original_native_Inc_Time",
        "computed_time_start_hours": outcome.physical_time_hours[0],
        "computed_time_end_hours": outcome.physical_time_hours[-1],
        "computed_time_rows": len(outcome.physical_time_hours),
        "original_input_sha256": {Path(source["path"]).suffix: source["sha256"] for source in case["inputs"]},
        "project_sha256": outcome.project_sha256,
        "model_sha256": outcome.model_sha256,
        "implementation_revision": outcome.implementation_revision,
    }


def _fresh_reporting_classification(item: dict[str, Any]) -> str:
    """Do not convert missing/invalid scalar result metadata into a passing status."""
    raw: object = item.get("fresh_reporting")
    if not isinstance(raw, dict):
        return "not_run"
    classification: object = cast("dict[str, object]", raw).get("classification")
    return classification if isinstance(classification, str) else "not_run"


def main() -> int:
    """Return success for a complete diagnostic inventory, not a numerical pass claim."""
    register = json.loads(REGISTER.read_text(encoding="utf-8"))
    cases = [item for item in register["cases"] if "cmd-eligible" in item["sets"]]
    if len(cases) != 50 or len({item["case_id"] for item in cases}) != len(cases):
        print("CMD probe: invalid selected case register", file=sys.stderr)
        return 2
    outcomes = [_one(case) for case in cases]
    counts = dict(sorted(Counter(str(item["status"]) for item in outcomes).items()))
    retained = [case for case in cases if "cmd-reviewed" in case["sets"] or "timestep" in case["sets"]]
    expected = {case["case_id"]: case["clock"]["row_count"] for case in retained}
    observed = {item["case_id"]: item for item in outcomes}
    failures = [
        case_id
        for case_id, length in expected.items()
        if observed[case_id]["status"] != "printed_pass" or observed[case_id].get("rows") != length
    ]
    gate_ok = len(expected) == 36 and sum(expected.values()) == 16_836 and not failures
    scalar_statuses = dict(sorted(Counter(_fresh_reporting_classification(item) for item in outcomes).items()))
    print(
        json.dumps(
            {
                "format": "runoff-public-cmd-fresh-probe-v1",
                "fresh_reporting_status_counts": scalar_statuses,
                "fresh_reporting_full_population": "pass" if scalar_statuses == {"pass": 50} else "incomplete",
                "fresh_reporting_acceptance": "unassessed_pending_independent_review",
                "cases_checked": len(outcomes),
                "status_counts": counts,
                "retained_36_case_printed_baseline": "pass" if gate_ok else "fail",
                "retained_baseline_case_count": len(expected),
                "retained_baseline_expected_rows": sum(expected.values()),
                "retained_baseline_failures": failures,
                "numerical_acceptance": "unassessed",
                "reference_source": "public original CMD 6.44 printed data",
                "calculation_source": "actual installed public python-cmd backend",
                "native_processes": 0,
                "results": outcomes,
            },
            sort_keys=True,
            allow_nan=False,
        )
    )
    return 0 if gate_ok else 1


if __name__ == "__main__":
    sys.exit(main())
