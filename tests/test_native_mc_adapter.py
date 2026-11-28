"""Independent-context and source-binding controls for canonical printed MC adaptation."""

import json
from copy import deepcopy
from decimal import localcontext
from pathlib import Path

import pytest

from runoff_routing.monte_carlo_comparison import MCComparisonInputError, assess_native_comparison
from runoff_routing.monte_carlo_report import native_mc_comparison_records, native_mc_report_json_ready
from runoff_routing.rorb_readers.reader_types import RorbDocument
from runoff_routing.rorb_readers.readers import read_rorb_bytes

REPORT = Path(__file__).parent / "fixtures" / "rorb" / "mc-artificial" / "candidate-artificial-mc-report.out"


def _document() -> RorbDocument:
    return read_rorb_bytes(REPORT.read_bytes())


def test_adapter_preserves_source_tokens_unknown_units_and_all_unavailable_gates() -> None:
    doc = _document()
    records = native_mc_comparison_records(doc, cohort_id="cohort_A", replication_id="replicate_A")
    assert len(records) == 25
    first = records[0]
    assert first.source.report_sha256 == doc.sha256
    assert first.source.reported_version == "6.52"
    assert first.source.executable_sha256 is None
    assert first.key.duration_minutes == 2160
    assert first.key.physical_site_id is None
    assert first.peak_m3s.quality == "unavailable"
    assert first.rainfall_probability.quality == "unavailable"
    assert first.native_event_weight.quality == "unavailable"
    assert first.native_tp_rank == 3
    assert first.original_tp_event_id is None
    assert first.python_sample_id is None
    readiness = assess_native_comparison(records)
    assert readiness.input_law == "unavailable"
    assert readiness.exact_event_replay == "unavailable"
    assert readiness.native_weighted_reaggregation == "unavailable"
    assert readiness.native_published_summary == "unavailable"
    result = native_mc_report_json_ready(doc, cohort_id="cohort_A", replication_id="replicate_A")
    rendered = json.dumps(result, allow_nan=False)
    assert '"Peak": "0.00"' in rendered
    assert '"AEP": "2.043"' in rendered
    assert '"Peak": null' in rendered
    assert '"report_local_output_ordinal": "07"' in rendered
    assert '"native_tp_rank": 3' in rendered
    assert "displayed_setting_not_committed_effective_event" in rendered
    assert '"IL": "31.50"' in rendered
    assert doc.original_bytes == REPORT.read_bytes()


def test_adapter_requires_separate_cohort_replication_scope_and_rejects_duplicates() -> None:
    doc = _document()
    first = native_mc_comparison_records(doc, cohort_id="A", replication_id="R1")
    second = native_mc_comparison_records(doc, cohort_id="B", replication_id="R1")
    third = native_mc_comparison_records(doc, cohort_id="A", replication_id="R2")
    assert assess_native_comparison(first + second + third).exact_event_replay == "unavailable"
    with pytest.raises(MCComparisonInputError, match="duplicate"):
        assess_native_comparison(first + first)
    with pytest.raises(MCComparisonInputError, match="cohort_id"):
        native_mc_comparison_records(doc, cohort_id="", replication_id="R1")


@pytest.mark.parametrize("field", ["bytes", "hash", "lines", "tokens", "values", "context", "kind", "validity"])
def test_adapter_rejects_mutated_or_forged_canonical_documents(field: str) -> None:
    doc = deepcopy(_document())
    if field == "bytes":
        doc.original_bytes = None
    elif field == "hash":
        doc.sha256 = "0" * 64
    elif field == "lines":
        doc.lines = ("fabricated",)
    elif field == "tokens":
        doc.section("mc_events").source_tokens[0]["Peak"] = "99.99"
    elif field == "values":
        doc.section("mc_events").rows[0]["Div"] = 99
    elif field == "context":
        doc.metadata["mc_peak_unit"] = "m3/s"
    elif field == "kind":
        doc.kind = "standard_output"
    else:
        doc.section("mc_events").valid = False
    with pytest.raises(MCComparisonInputError):
        native_mc_report_json_ready(doc, cohort_id="A", replication_id="R1")


def test_adapter_refuses_truncation_other_formats_and_fabricated_complete_flag() -> None:
    for raw in (REPORT.read_bytes()[:100], b"unknown report\n"):
        doc = read_rorb_bytes(raw)
        doc.metadata["mc_structure_complete"] = True
        with pytest.raises(MCComparisonInputError, match="admitted complete"):
            native_mc_comparison_records(doc, cohort_id="A", replication_id="R1")


def test_adapter_duration_identity_is_exact_under_low_decimal_context() -> None:
    with localcontext() as context:
        context.prec = 2
        records = native_mc_comparison_records(_document(), cohort_id="A", replication_id="R1")
    assert records[0].key.duration_minutes == 2160
    raw = (
        REPORT.read_bytes()
        .replace(b"Duration(hr)     36.0", b"Duration(hr)     0.001")
        .replace(b"Storm Duration of 36 hour", b"Storm Duration of 0.001 hour")
    )
    doc = read_rorb_bytes(raw)
    assert doc.metadata["mc_structure_complete"] is True
    with pytest.raises(MCComparisonInputError, match="whole-minute"):
        native_mc_comparison_records(doc, cohort_id="A", replication_id="R1")
