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

from runoff_routing import regression_dataset as regression
from runoff_routing.engine_execution import run_engine_project
from runoff_routing.engine_types import EngineSelection
from runoff_routing.project_json import EmbeddedRun, Project, project_to_json
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
    path = regression._verify(ROOT, locator)  # noqa: SLF001 -- exact maintained fixture SHA/locator validation
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != locator["sha256"]:
        message = f"{case['case_id']}: changed source bytes"
        raise ValueError(message)
    return raw


def _typed_model(case: dict[str, Any]) -> RunModel:
    """Use only the maintained S1 decoders; do not create a separate native parser."""
    parameters = parse_cmd_par(_original_source(case, ".par")).model
    catchment = parse_catg(_original_source(case, ".catg")).model
    storm = parse_design_stm(_original_source(case, ".stm")).model
    return RunModel(parameters, catchment, storm)


def _compare_case(case: dict[str, Any], discharge: tuple[float, ...]) -> dict[str, Any]:
    """Use the existing frozen native printed-token comparator, not a new tolerance."""
    columns, rows = regression._reference(ROOT, case)  # noqa: SLF001 -- reuse frozen native table/clock validation
    sites = case["sites"]
    if len(sites) != 1 or len(columns) != 3 or len(rows) != len(discharge):
        return {"status": "incomplete_output", "reason": "Original printed site/complete horizon differs"}
    site = sites[0]
    column = site["native_column_id"]
    if columns[2] != column:
        return {"status": "invalid_mapping", "reason": "Original native print column differs"}
    candidate = {
        (case["case_id"], column, index): {
            "case_id": case["case_id"],
            "classification": "computed/pass",
            "model_print_id": site["model_print_id"],
            "native_column_id": column,
            "sample_index": str(index),
            "raw_native_increment": row[0],
            "raw_native_time": row[1],
            "native_discharge_token": row[2],
            "python_discharge_m3_s": repr(flow),
        }
        for index, (row, flow) in enumerate(zip(rows, discharge, strict=True))
    }
    result = regression._compare(case, columns, rows, candidate, "python-cmd")  # noqa: SLF001 -- one frozen comparator
    mismatches = result.get("mismatches", [])
    return {
        "status": f"printed_{result['classification']}",
        "rows": len(rows),
        "mismatch_count": len(mismatches),
        "first_mismatch": mismatches[0] if mismatches else None,
        "reason": result.get("reason"),
    }


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
    comparison = _compare_case(case, hydrograph.discharge_m3_s)
    return {"case_id": case_id, **comparison}


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
