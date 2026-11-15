"""Read-only public canonical report views, without event execution or report rewrites."""

from __future__ import annotations

import csv
import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

from runoff_routing.rorb_report_views import inspect_report, report_csv, report_json

_ROOT = Path(__file__).resolve().parents[1]
_CLI = _ROOT / "repo-scripts" / "rorb_inspect.py"


def _batch() -> bytes:
    source = (
        "RORBWin Batch Run Summary\nProgram version 6.52\n"
        "Parameters: kc = 10 m = 0.8\n"
        "Loss parameters Initial loss (mm) Cont. loss (mm/h)\n20 2\n"
        "Peak Description\n01 Calculated hydrograph: Outlet\n\n"
        "Run Duration AEP TPat Rain(mm) ARF Peak0001\n"
        "1 24 hour 50% 1 40.20 0.93 55.3000\n"
        "1 24 hour 50% 2 40.20 0.93 6.5D1\n"
        "Run, Representative hydrograph\n1 dur24hour_aep50tp2.out\n"
        "Elapsed Run Time (hh:mm:ss) = 00:00:01\n"
    )
    return source.encode("utf-8")


def test_canonical_json_and_csv_keep_raw_batch_order_and_frequency(tmp_path: Path) -> None:
    path = tmp_path / "test_batch.out"
    original = _batch()
    path.write_bytes(original)
    document = inspect_report(path)
    assert document.kind == "batch_output"
    assert document.status == "partial"
    summary = json.loads(report_json(document))
    assert summary["source_sha256"] == document.sha256
    assert summary["size_bytes"] == len(original)
    assert any(item["name"] == "runs" and item["row_count"] == 2 for item in summary["sections"])
    page = json.loads(report_json(document, section="runs", offset=1, limit=1))
    assert page["selection"]["returned_rows"] == 1
    assert page["selection"]["total_rows"] == 2
    assert page["selection"]["rows"][0]["original_tokens"]["Peak0001"] == "6.5D1"

    rows = list(csv.DictReader(io.StringIO(report_csv(document, "runs", limit=2))))
    assert len(rows) == 2
    assert [row["Run"] for row in rows] == ["1", "1"]
    assert [row["TPat"] for row in rows] == ["1", "2"]
    assert [row["aep_raw"] for row in rows] == ["50%", "50%"]
    assert rows[0]["source_token__Peak0001"] == "55.3000"
    assert rows[1]["source_token__Peak0001"] == "6.5D1"
    assert path.read_bytes() == original


def test_canonical_report_cli_exports_raw_csv_and_preserves_bytes(tmp_path: Path) -> None:
    path = tmp_path / "native_batch.out"
    original = _batch()
    path.write_bytes(original)
    command = [sys.executable, str(_CLI), str(path), "--report", "--section", "runs", "--format", "csv"]
    result = subprocess.run(  # noqa: S603 -- call fixed Python interpreter on repository-owned inspection scriptcommand, cwd=_ROOT, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    entries = list(csv.DictReader(io.StringIO(result.stdout)))
    assert len(entries) == 2
    assert entries[1]["source_token__Peak0001"] == "6.5D1"
    assert path.read_bytes() == original


def test_invalid_canonical_report_never_returns_success(tmp_path: Path) -> None:
    path = tmp_path / "invalid_batch.out"
    path.write_bytes(_batch().replace(b"6.5D1", b"nan"))
    doc = inspect_report(path)
    assert doc.status == "invalid"
    report = json.loads(report_json(doc, section="runs"))
    assert report["status"] == "invalid"
    assert report["diagnostics"]
    result = subprocess.run(  # noqa: S603 -- call fixed Python interpreter on repository-owned inspection script
        [sys.executable, str(_CLI), str(path), "--report", "--section", "runs"],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert json.loads(result.stdout)["status"] == "invalid"


@pytest.mark.parametrize(("section", "offset", "limit"), [("runs", -1, 2), ("runs", 0, 10_001), ("missing", 0, 1)])
def test_report_view_rejects_invalid_selection(tmp_path: Path, section: str, offset: int, limit: int) -> None:
    path = tmp_path / "report.out"
    path.write_bytes(_batch())
    document = inspect_report(path)
    with pytest.raises(ValueError):
        report_csv(document, section, offset=offset, limit=limit)


def test_report_view_never_activates_saved_settings(tmp_path: Path) -> None:
    path = tmp_path / "saved.par"
    path.write_text("Not a RORB report", encoding="utf-8")
    with pytest.raises(ValueError, match="characterised RORB result"):
        inspect_report(path)


def test_signed_hydrograph_csv_preserves_source_clock_and_fortran_values(tmp_path: Path) -> None:
    source = (
        "RORBWin CSV Output File\n"
        "Refer output file for complete listing of inputs and outputs: event.out\n"
        "Inc,Time (hrs),Calculated hydrograph: Outlet\n"
        "0,0.000,0\n1,0.333,5.53D1\n2,0.667,0\n"
    )
    path = tmp_path / "event.csv"
    path.write_bytes(source.encode("utf-8"))
    document = inspect_report(path)
    assert document.kind == "hydrograph_csv"
    assert document.status == "partial"
    rows = list(csv.DictReader(io.StringIO(report_csv(document, "hydrographs"))))
    assert len(rows) == 3
    assert [row["Inc"] for row in rows] == ["0", "1", "2"]
    assert rows[1]["source_token__Time (hrs)"] == "0.333"
    assert rows[1]["source_token__Calculated hydrograph: Outlet"] == "5.53D1"
    shown = json.loads(report_json(document, section="hydrographs", offset=1, limit=1))
    assert shown["selection"]["rows"][0]["original_tokens"]["Time (hrs)"] == "0.333"
    assert path.read_text(encoding="utf-8") == source
