"""Approved artificial structural MC fixtures; no native execution or scientific inference."""

import json
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from typing import Any

import pytest

from runoff_routing.rorb_readers.readers import read_rorb_bytes, read_rorb_file

FIXTURES = Path(__file__).parent / "fixtures" / "rorb" / "mc-artificial"
REPORT = FIXTURES / "candidate-artificial-mc-report.out"


def _changed(line: int, replacement: str) -> bytes:
    lines = REPORT.read_bytes().decode("cp1252").splitlines()
    lines[line - 1] = replacement
    return ("\r\n".join(lines) + "\r\n").encode("cp1252")


def test_mc_full_artificial_expected_tokens_and_source_identity() -> None:
    expected: dict[str, Any] = json.loads((FIXTURES / "candidate-artificial-expected.json").read_text())
    raw = REPORT.read_bytes()
    by_file = read_rorb_file(REPORT)
    doc = read_rorb_bytes(raw, path=REPORT)
    assert doc.kind == "monte_carlo_output"
    assert doc.status == "partial"
    assert doc.original_bytes == by_file.original_bytes == raw
    assert doc.sha256 == by_file.sha256 == sha256(raw).hexdigest()
    assert doc.encoding == "cp1252"
    assert doc.metadata["mc_structure_complete"] is True
    assert doc.metadata["mc_duration_hours_token"] == expected["duration_display_token_hours"]
    assert doc.metadata["mc_peak_ordinal"] == expected["report_local_peak_ordinal"]
    events = doc.section("mc_events")
    assert events.valid
    assert events.completeness == "complete"
    assert len(events.rows) == len(expected["events"]) == 25
    for index, event in enumerate(expected["events"]):
        assert events.rows[index]["line"] == event["source_line"]
        assert list(events.source_tokens[index].values()) == event["tokens"]
        assert events.source_decimal(index, "Peak") == Decimal(event["tokens"][-1])
    summary = doc.section("mc_probability_summary")
    for index, row in enumerate(expected["published_summary_rows"]):
        assert summary.rows[index]["line"] == row["source_line"]
        assert summary.source_tokens[index]["coordinate"] == row["coordinate_token"]
        assert summary.source_tokens[index]["Peak"] == row["peak_token"]
        assert summary.source_tokens[index]["peak_with_marker"] == row["peak_token"] + row["unreliable_marker"]
        assert summary.rows[index]["unreliable"] == bool(row["unreliable_marker"])


def test_mc_sections_and_scientific_absences_are_not_conflated() -> None:
    doc = read_rorb_bytes(REPORT.read_bytes())
    assert len(doc.section("mc_tp_diagnostic").rows) == 10
    assert len(doc.section("mc_loss_percentiles").rows) == 21
    assert len(doc.section("mc_loss_histogram").rows) == 10
    assert len(doc.section("mc_loss_histogram_totals").rows) == 1
    assert len(doc.section("mc_flow_extrema").rows) == 1
    for key in (
        "mc_peak_unit",
        "mc_physical_site_id",
        "mc_probability_interpretation",
        "mc_native_event_weights",
        "mc_frequency_law",
    ):
        assert doc.metadata[key] is None
    assert doc.metadata["mc_exact_effective_inputs"] is False
    assert doc.section("mc_events").source_tokens[0]["Peak"] == "0.00"
    assert doc.section("mc_events").source_tokens[0]["AEP"] == "2.043"
    assert doc.section("mc_events").source_tokens[-1]["AEP"].isdigit()
    assert any(issue.code == "mc_scientific_fields_unavailable" for issue in doc.diagnostics)


@pytest.mark.parametrize("line", [53, 77, 81, 89, 110, 115, 127, 132, 137, 153, 154])
def test_mc_truncated_mandatory_sections_cannot_supply_valid_events(line: int) -> None:
    raw = b"\r\n".join(REPORT.read_bytes().splitlines()[:line])
    doc = read_rorb_bytes(raw)
    assert doc.status == "invalid"
    assert doc.metadata["mc_structure_complete"] is False
    assert all(not section.valid for section in doc.sections if section.name.startswith("mc_"))


@pytest.mark.parametrize(
    ("line", "replacement"),
    [
        (54, " 1 1 2.060 18.5 6 0.28 0.83 1.17 15.34"),
        (54, " 6 1 2.060 18.5 6 0.28 0.83 1.17 15.34"),
        (54, " 1 2 NaN 18.5 6 0.28 0.83 1.17 15.34"),
        (54, " 1 2 2.060 18.5 6 0.28 0.83 1.17 inf"),
        (54, " 1 2 2.060 18.5 6 0.28 0.83 1.17 1e2"),
        (54, " 1 2 2.060 18.5 6 0.28 0.83 1.17 -1.00"),
        (54, " 1 2 2.060 18.5 6 0.28 0.83 1.17 15.34*"),
        (54, " 1 2 2.060 18.5 11 0.28 0.83 1.17 15.34"),
        (54, " 1 2 2.060 18.5 6 0.28 0.83 1.17"),
        (84, "Freq% : 100.01"),
        (84, "Freq%garbage: 10 10 10 10 10 10 10 10 10 10"),
        (84, "Freq%: 100.00000000000000000001 0 0 0 0 0 0 0 0 0"),
        (90, " 5 3.87"),
        (91, " 5.00000000000000000001 3.71"),
        (117, "0.31 10.00 0.25"),
        (117, "0.31 1000.00 0.25 10.00"),
        (127, "1000.00 100.00"),
        (133, " 08 0.00 107.33 ARTIFICIAL_OUTPUT_DESCRIPTION,"),
        (138, " 2 3.000 2.33"),
        (145, " 8 31.000 2.33**"),
        (46, "I.L. Effective storm loss (mm)"),
        (34, "Number of hydrographs to track = 2"),
        (17, "Num avail 11"),
        (16, "Duration(hr) 12.0"),
        (25, "Results for Storm Duration of 48 hour"),
        (24, ">>> Representative records"),
        (155, "Elapsed Run Time (hh:mm:ss) = 00:99:00"),
    ],
)
def test_mc_malformed_or_unadmitted_layouts_fail_closed(line: int, replacement: str) -> None:
    doc = read_rorb_bytes(_changed(line, replacement))
    assert doc.status == "invalid"
    assert doc.metadata["mc_structure_complete"] is False


def test_mc_duplicate_blocks_and_trailing_records_are_rejected() -> None:
    raw = REPORT.read_bytes()
    for changed in (raw + raw, raw + b"unknown appended record\r\n"):
        doc = read_rorb_bytes(changed)
        assert doc.metadata["mc_structure_complete"] is False


def test_mc_version_banner_does_not_authenticate_unknown_profile() -> None:
    doc = read_rorb_bytes(_changed(4, " Program version 6.99 (last updated ARTIFICIAL_DATE)"))
    assert doc.kind == "monte_carlo_output"
    assert doc.status == "partial"
    assert doc.metadata["mc_structure_complete"] is False
    assert all(section.name != "mc_events" for section in doc.sections)
    assert any(issue.code == "mc_profile_not_admitted" for issue in doc.diagnostics)


def test_mc_complete_final_record_without_terminal_newline_is_retained() -> None:
    raw = REPORT.read_bytes().removesuffix(b"\r\n")
    doc = read_rorb_bytes(raw)
    assert doc.metadata["mc_structure_complete"] is True
    assert doc.original_bytes == raw
