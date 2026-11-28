"""Canonical printed-report adaptation for #191; no independent report grammar.

Unbound printed peaks/probability tokens remain supplemental source observations,
never guessed m3/s values, physical sites or exact native effective inputs.
"""

from dataclasses import asdict
from decimal import Decimal
from hashlib import sha256
from typing import Never

from .monte_carlo_comparison import (
    MCComparisonInputError,
    MCEventKey,
    MCField,
    MCNativeRecord,
    MCNativeSource,
    comparison_json_ready,
)
from .rorb_readers.reader_types import RorbDocument
from .rorb_readers.readers import read_rorb_bytes


def _fail(message: str) -> Never:
    raise MCComparisonInputError(message)


def _verified_document(document: RorbDocument) -> RorbDocument:
    if document.original_bytes is None or sha256(document.original_bytes).hexdigest() != document.sha256:
        _fail("Canonical MC document requires its unchanged original-byte identity.")
    # RorbDocument is mutable. Reuse the ONE canonical grammar to bind its fields
    # to retained bytes; never accept a fabricated complete flag or edited tokens.
    try:
        canonical = read_rorb_bytes(document.original_bytes, path=document.path, encoding=document.encoding)
    except (UnicodeError, LookupError, ValueError) as exc:
        message = "Canonical MC source bytes/encoding are invalid."
        raise MCComparisonInputError(message) from exc
    if (
        canonical.kind != "monte_carlo_output"
        or canonical.status == "invalid"
        or canonical.metadata.get("mc_structure_complete") is not True
    ):
        _fail("Native MC report has no admitted complete canonical printed structure.")
    if (
        document.kind != canonical.kind
        or document.status != canonical.status
        or document.lines != canonical.lines
        or document.sections != canonical.sections
        or document.metadata != canonical.metadata
    ):
        _fail("Canonical MC fields/context differ from their retained source bytes.")
    return canonical


def _records(
    document: RorbDocument, cohort_id: str, replication_id: str, scenario_id: str | None
) -> tuple[MCNativeRecord, ...]:
    hours = Decimal(str(document.metadata["mc_duration_hours_token"]))
    numerator, denominator = hours.as_integer_ratio()
    minutes, remainder = divmod(numerator * 60, denominator)
    if remainder or minutes < 1:
        _fail("Printed native duration is unavailable as a positive whole-minute event key.")
    source = MCNativeSource(document.sha256, reported_version=str(document.metadata["program_version"]))
    return tuple(
        MCNativeRecord(
            source,
            MCEventKey(
                cohort_id,
                replication_id,
                minutes,
                int(str(row["Div"])),
                int(str(row["Run"])),
                scenario_id=scenario_id,
                physical_site_id=None,
            ),
            MCField("unavailable"),
            MCField("unavailable"),
            native_tp_rank=int(str(row["TPat"])),
        )
        for row in document.section("mc_events").rows
    )


def native_mc_comparison_records(
    document: RorbDocument, *, cohort_id: str, replication_id: str, scenario_id: str | None = None
) -> tuple[MCNativeRecord, ...]:
    """Adapt source-bound identities/ranks, preserving all Phase 1 unavailable gates.

    Cohort/replication/scenario are explicit caller provenance, never inferred from
    a filename, date, run ordinal or native RNG. Printed unknown-unit values are
    available separately through native_mc_report_json_ready(), not peak_m3s.
    """
    return _records(_verified_document(document), cohort_id, replication_id, scenario_id)


def native_mc_report_json_ready(
    document: RorbDocument, *, cohort_id: str, replication_id: str, scenario_id: str | None = None
) -> dict[str, object]:
    """JSON-compatible printed evidence plus unchanged source-neutral comparison I/O."""
    canonical = _verified_document(document)
    records = _records(canonical, cohort_id, replication_id, scenario_id)
    events = canonical.section("mc_events")
    printed_rows = [
        {
            "key": asdict(record.key),
            "report_local_output_ordinal": canonical.metadata["mc_peak_ordinal"],
            "source_line": row["line"],
            "source_tokens": dict(tokens),
            "quantity_units": {"AEP": None, "Depth": "mm", "I.L.": "1", "IL_F": "1", "LR_F": "1", "Peak": None},
            "value_quality": "rounded_print",
            "identity_quality": "report_local_ordinals_and_caller_context_only",
        }
        for record, row, tokens in zip(records, events.rows, events.source_tokens, strict=True)
    ]
    printed_sections = [
        {
            "name": section.name,
            "columns": list(section.columns),
            "display_rows": [dict(row) for row in section.rows],
            "source_tokens": [dict(tokens) for tokens in section.source_tokens],
            "interpretation": (
                "displayed_setting_not_committed_effective_event"
                if section.name == "parameters"
                else "descriptive_only_not_native_weights_or_frequency_method"
            ),
        }
        for section in canonical.sections
        if section.name == "parameters" or (section.name.startswith("mc_") and section.name != "mc_events")
    ]
    return {
        "schema": "pyrorb-canonical-native-mc-report-evidence/1",
        "source": asdict(records[0].source),
        "comparison": comparison_json_ready(records),
        "printed_rows": printed_rows,
        "printed_sections": printed_sections,
        "printed_diagnostics_status": "descriptive_only",
        "authoritative_numeric_evidence": "source_tokens_not_float_convenience_views",
        "external_context": "caller_labels_do_not_establish_independent_native_replications",
        "unavailable": [
            "peak_discharge_unit",
            "physical_site_binding",
            "native_probability_interpretation",
            "native_event_weights",
            "original_source_TP_EventID",
            "exact_native_effective_inputs",
            "native_RNG_or_independent_streams",
            "native_frequency_law",
        ],
    }
