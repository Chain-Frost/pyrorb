"""Independent, entirely synthetic regression data and read-only integrity checks."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from runoff_routing import regression_dataset as rd

REPO = Path(__file__).absolute().parents[1]


def _stamp(path: Path, content: str) -> dict[str, str | int]:
    path.write_text(content, encoding="utf-8")
    raw = path.read_bytes()
    return {"path": path.name, "size_bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def _fixture(tmp_path: Path, *, missing: bool = False) -> tuple[Path, Path]:
    reference = tmp_path / "original.json"
    stamp = _stamp(
        reference,
        json.dumps(
            {
                "tables": [
                    {
                        "columns": ["Inc", "Time", "Hyd001"],
                        "rows": [["1", "0.50", "0.000"], ["2", "1.00", "1.000"]],
                    }
                ]
            }
        ),
    )
    case: dict[str, Any] = {
        "case_id": "SYN-001",
        "coverage": "selected",
        "sets": ["all", "cmd-selected"],
        "reason": "",
        "reference_kind": "native_printed_interval",
        "files": [stamp],
        "reference": stamp,
        "clock": {"row_count": 2, "timestep_hours": "0.5"},
        "sites": [{"native_column_id": "Hyd001", "model_print_id": "print_1"}],
    }
    if missing:
        case.update(coverage="gap", reason="native data unavailable", sets=["all"])
    manifest = tmp_path / "register.json"
    manifest.write_text(
        json.dumps(
            {
                "format": rd.FORMAT,
                "schema_version": 1,
                "dataset_id": "synthetic",
                "data_root": ".",
                "policies": {
                    "python-cmd": "cmd644-printed-interval-v1",
                    "python": "engineering-analytic-v1",
                },
                "cases": [case],
            }
        ),
        encoding="utf-8",
    )
    predicted = tmp_path / "candidate.csv"
    with predicted.open("w", newline="", encoding="utf-8") as output:
        writer = csv.writer(output)
        writer.writerow(rd.CSV_COLUMNS)
        for index, increment, time, native in (
            (0, "1", "0.50", "0.000"),
            (1, "2", "1.00", "1.000"),
        ):
            writer.writerow(["SYN-001", "computed/pass", "print_1", "Hyd001", index, increment, time, native, native])
    return manifest, predicted


def test_manufactured_source_preflight_and_cached_comparison(tmp_path: Path) -> None:
    register, computed = _fixture(tmp_path)
    assert rd.main(["preflight", str(register)]) == 0
    assert rd.main(["compare", str(register), "--csv", str(computed), "--implementation", "a" * 40]) == 0


def test_missing_coverage_cannot_be_accepted(tmp_path: Path) -> None:
    register, computed = _fixture(tmp_path, missing=True)
    assert rd.main(["preflight", str(register), "--set", "all"]) == 1
    assert rd.main(["compare", str(register), "--set", "all", "--csv", str(computed), "--implementation", "a" * 40]) == 1


def test_original_source_hash_mismatch_is_invalid(tmp_path: Path) -> None:
    register, _ = _fixture(tmp_path)
    (tmp_path / "original.json").write_text("changed", encoding="utf-8")
    result, complete = rd._run(
        register, group="cmd-selected", case_id=None, csv_path=None,
        engine="python-cmd", full_index=False, implementation=None, wheel=None,
    )
    assert not complete
    assert result["cases"][0]["classification"] == "invalid"


@pytest.mark.parametrize(
    "mutation",
    ["duplicate_case", "reorder", "truncate", "clock", "extra_column", "duplicate_site", "nonfinite"],
)
def test_reference_integrity_negative_controls(tmp_path: Path, mutation: str) -> None:
    register, computed = _fixture(tmp_path)
    document = json.loads(register.read_text(encoding="utf-8"))
    case = document["cases"][0]
    source = tmp_path / "original.json"
    original = json.loads(source.read_text(encoding="utf-8"))
    table = original["tables"][0]
    if mutation == "duplicate_case":
        document["cases"].append(dict(case))
    elif mutation == "reorder":
        table["rows"].reverse()
    elif mutation == "truncate":
        table["rows"].pop()
    elif mutation == "clock":
        table["rows"][1][1] = "1.50"
    elif mutation == "extra_column":
        table["columns"].append("Hyd002")
        for row in table["rows"]:
            row.append("2.000")
    elif mutation == "duplicate_site":
        case["sites"].append(case["sites"][0])
    else:
        table["rows"][1][2] = "NaN"
    if mutation in {"reorder", "truncate", "clock", "extra_column", "nonfinite"}:
        fingerprint = _stamp(source, json.dumps(original))
        case["reference"], case["files"] = fingerprint, [fingerprint]
    register.write_text(json.dumps(document), encoding="utf-8")
    assert rd.main(["compare", str(register), "--csv", str(computed), "--implementation", "a" * 40]) != 0


def test_unrecorded_ordinate_and_exclusive_output(tmp_path: Path) -> None:
    register, computed = _fixture(tmp_path)
    with computed.open("a", encoding="utf-8") as stream:
        stream.write("SYN-001,computed/pass,print_2,Hyd002,0,1,0.50,0.000,0.000\n")
    assert rd.main(["compare", str(register), "--csv", str(computed), "--implementation", "a" * 40]) == 1
    report = tmp_path / "outcome.json"
    assert rd.main(["preflight", str(register), "--output", str(report)]) == 0
    assert rd.main(["preflight", str(register), "--output", str(report)]) == 2


def test_public_authored_full_set_and_explicit_gaps() -> None:
    register = REPO / "tests" / "fixtures" / "regression-v1" / "register.json"
    assert rd.main(["preflight", str(register), "--set", "smoke", "--engine", "python"]) == 0
    assert rd.main(["preflight", str(register), "--set", "authored", "--engine", "python"]) == 0
    assert rd.main(["preflight", str(register), "--set", "all", "--engine", "python"]) == 1


def test_missing_candidate_horizon_is_incomplete(tmp_path: Path) -> None:
    register, candidate = _fixture(tmp_path)
    lines = candidate.read_text(encoding="utf-8").splitlines()
    candidate.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
    result, complete = rd._run(
        register, group="cmd-selected", case_id=None, csv_path=candidate,
        engine="python-cmd", full_index=False, implementation="a" * 40, wheel=None,
    )
    assert not complete
    assert result["cases"][0]["classification"] == "incomplete"


def test_native_process_never_launches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import subprocess

    def prohibited(*_args: object, **_kwargs: object) -> None:
        pytest.fail("cached comparison unexpectedly launched a native executable")

    monkeypatch.setattr(subprocess, "run", prohibited)
    monkeypatch.setattr(subprocess, "Popen", prohibited)
    manifest, computed = _fixture(tmp_path)
    assert rd.main(["preflight", str(manifest)]) == 0
    assert rd.main(["compare", str(manifest), "--csv", str(computed), "--implementation", "a" * 40]) == 0
