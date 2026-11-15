"""Original RORB-CMD versus separate Python-engine physical-output diagnostics.

No invented native references, new comparator, alternative numerical runner,
golden regeneration, relaxed acceptance policy or original-report rewriting.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path
from typing import Any, cast

import pytest

from runoff_routing import regression_dataset
from runoff_routing.cmd_deviation import assess_cmd_deviation
from runoff_routing.engine_execution import run_engine_project
from runoff_routing.engine_types import EngineSelection
from runoff_routing.project_json import LegacyRunFiles, Project, SourceFile, write_project
from runoff_routing.regression_scalar_adapter import bind_scalars
from runoff_routing.rorb_documents import RorbSource

ROOT = Path(__file__).parents[1] / "tests" / "fixtures" / "regression-v1"
REGISTER = ROOT / "register.json"
ENGINE = EngineSelection.for_engine("python")


def _verified_object(item: dict[str, Any]) -> bytes:
    """Original exact bytes, not a second source/report parser."""
    target = ROOT / str(item["path"])
    assert target.is_file() and not target.is_symlink()
    assert target.resolve().is_relative_to(ROOT.resolve())
    raw = target.read_bytes()
    assert len(raw) == item["size_bytes"]
    assert hashlib.sha256(raw).hexdigest() == item["sha256"]
    return raw


def _registered_case(case_id: str) -> dict[str, Any]:
    register = cast("dict[str, Any]", json.loads(REGISTER.read_text(encoding="utf-8")))
    cases = cast("list[dict[str, Any]]", register["cases"])
    matching = tuple(case for case in cases if case["case_id"] == case_id)
    assert len(matching) == 1
    return matching[0]


@pytest.mark.parametrize("case_id", ["pyromb-pr2-full", "pyromb-novel-storm"])
def test_original_cmd_comparison_reports_unaccepted_engineering_differences(
    tmp_path: Path, case_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    case = _registered_case(case_id)
    assert case["observations"]["physical_site_identity"] == "authenticated"
    sites = cast("list[dict[str, Any]]", case["sites"])
    assert len(sites) == 1
    source_records = cast("list[dict[str, Any]]", case["inputs"])
    sources: dict[str, SourceFile] = {}
    for suffix in (".par", ".catg", ".stm"):
        matching = tuple(item for item in source_records if str(item["path"]).endswith(suffix))
        assert len(matching) == 1
        item = matching[0]
        raw = _verified_object(item)
        target_name = f"original{suffix}"
        (tmp_path / target_name).write_bytes(raw)
        sources[suffix] = SourceFile(target_name, hashlib.sha256(raw).hexdigest())
    reference = cast("dict[str, Any]", case["reference"])
    _verified_object(reference)
    project = tmp_path / "original-project.json"
    write_project(
        project,
        Project(
            case_id,
            "legacy-rorb",
            LegacyRunFiles(sources[".par"], sources[".catg"], sources[".stm"]),
            engine=ENGINE,
        ),
    )
    outcome = run_engine_project(project)
    assert outcome.status == "computed_unvalidated", outcome.diagnostics
    assert outcome.stored_selection == outcome.effective_selection == ENGINE
    assert outcome.native_raw_time_tokens == ()
    assert outcome.native_parity_status == "not_assessed"
    assert len(outcome.hydrographs) == 1
    site = sites[0]
    assert outcome.hydrographs[0].print_id == site["model_print_id"]
    assert outcome.requested_print_ids == (site["model_print_id"],)
    assert len(outcome.physical_time_hours) == case["clock"]["row_count"]
    # Reuse the maintained original reference reader for original one-based
    # clock and HydNNN ordinates; never parse the report independently.
    columns, rows = regression_dataset._reference(ROOT, case)
    original_column = columns.index(str(site["native_column_id"]))
    original_q = tuple(float(row[original_column]) for row in rows)
    computed_q = outcome.hydrographs[0].discharge_m3_s
    assert len(computed_q) == len(original_q) == case["clock"]["row_count"]
    timestep = Decimal(str(case["clock"]["timestep_hours"]))
    expected_clock = tuple(str(index * timestep) for index in range(len(computed_q)))
    assert outcome.physical_time_hours == expected_clock
    comparison = assess_cmd_deviation(computed_q, original_q, timestep_hours=float(timestep))
    original_report = ROOT / str(reference["path"])
    bound = bind_scalars(RorbSource.read(original_report), case["scalar_binding"])
    assert bound.column == site["native_column_id"]
    # Native *reported inclusive volume* is not a physical trapezoidal integral.
    native_inclusive_volume_token = bound.volume.token if bound.volume is not None else None
    receipt = {
        "case_id": case_id,
        "reference_type": "authenticated_original_CMD_6.44",
        "native_reference_sha256": reference["sha256"],
        "source_sha256": {key: value.sha256 for key, value in sources.items()},
        "independent_engine": ENGINE.engine,
        "numerical_profile": ENGINE.numerical_profile,
        "physical_site_id": site["physical_site_id"],
        "source_model_print_id": site["model_print_id"],
        "native_column_id": site["native_column_id"],
        "native_inclusive_reported_volume_original_token_m3": native_inclusive_volume_token,
        "cmd_peak_original_increment": rows[comparison.cmd_peak_index][0],
        "cmd_peak_original_time_token_hours": rows[comparison.cmd_peak_index][1],
        "cmd_peak_model_elapsed_hours": str(comparison.cmd_peak_index * timestep),
        "python_peak_model_elapsed_hours": str(comparison.python_peak_index * timestep),
        "original_full_cmd_q_m3_s": original_q,
        "computed_full_python_q_m3_s": computed_q,
        "deviations": asdict(comparison),
        "numerical_acceptance": "unassessed",
        "zero_cmd_denominator_percentage": "undefined_not_zero",
        "comparison_class": "direct_original_diagnostic_not_parity_certification",
    }
    with capsys.disabled():
        print(json.dumps(receipt, sort_keys=True, allow_nan=False))
