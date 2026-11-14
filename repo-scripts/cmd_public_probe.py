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
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from runoff_routing.engine_execution import run_engine_project
from runoff_routing.engine_types import EngineSelection
from runoff_routing.project_json import EmbeddedRun, Project, project_to_json
from runoff_routing.regression_dataset import compare_fresh_cmd_case
from runoff_routing.rorb_codec import RorbFormatError, parse_catg, parse_cmd_par, parse_design_stm
from runoff_routing.rorb_model import RunModel

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
        path.write_text(project_to_json(project), encoding="utf-8")
        outcome = run_engine_project(path)
    if outcome.status != "computed_unvalidated":
        return {
            "case_id": case_id,
            "status": outcome.status,
            "reason": outcome.diagnostics[0].message if outcome.diagnostics else "Typed calculation unavailable",
        }
    if len(outcome.hydrographs) != 1:
        return {"case_id": case_id, "status": "incomplete_output", "reason": "Unexpected print population"}
    hydrograph = outcome.hydrographs[0]
    if hydrograph.print_id != case["sites"][0]["model_print_id"]:
        return {"case_id": case_id, "status": "unverified_print_mapping", "reason": "Print IDs differ"}
    comparison = compare_fresh_cmd_case(ROOT, case, outcome)
    mismatches = comparison.get("mismatches", [])
    return {
        "case_id": case_id,
        "status": f"printed_{comparison['classification']}",
        "rows": comparison.get("checked_ordinates", 0),
        "mismatch_count": len(mismatches),
        "first_mismatch": mismatches[0] if mismatches else None,
        "reason": comparison.get("reason"),
    }


def main() -> int:
    """Return success for a complete diagnostic inventory, not a numerical pass claim."""
    register = json.loads(REGISTER.read_text(encoding="utf-8"))
    cases = [item for item in register["cases"] if "cmd-eligible" in item["sets"]]
    if len(cases) != 50 or len({item["case_id"] for item in cases}) != len(cases):
        print("CMD probe: invalid selected case register", file=sys.stderr)
        return 2
    outcomes = [_one(case) for case in cases]
    counts = dict(sorted(Counter(str(item["status"]) for item in outcomes).items()))
    print(
        json.dumps(
            {
                "format": "runoff-public-cmd-fresh-probe-v1",
                "cases_checked": len(outcomes),
                "status_counts": counts,
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
