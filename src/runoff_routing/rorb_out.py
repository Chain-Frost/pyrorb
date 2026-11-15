"""Bind the canonical ryan-tools RORB report to runoff's existing evidence contract.

All native report grammar, numeric token parsing, source preservation, increment
validation and scalar recognition live in ryan-tools. This adapter supplies only
the project-facing immutable inspection shape consumed by the CMD/regression
contracts. It does not infer physical Hyd identities or shift printed clocks.
"""

from __future__ import annotations

from decimal import Decimal

from ryan_library.functions.RORB.reader_types import RorbDocument, Section, exact_number
from ryan_library.functions.RORB.readers import read_rorb_file

from .rorb_documents import Diagnostic, HydrographReport, HydrographRow, Inspection, RorbSource


def _diagnostics(document: RorbDocument) -> list[Diagnostic]:
    """Carry canonical diagnostics and their original source line provenance."""
    return [Diagnostic(item.code, item.message, item.severity, item.line) for item in document.diagnostics]


def _report(source: RorbSource, document: RorbDocument, table: Section) -> HydrographReport:
    """Project view over validated canonical tokens; no source lines are reparsed."""
    if not table.valid or not table.rows or len(table.source_tokens) != len(table.rows):
        msg = "Canonical report table is incomplete or lacks exact source tokens"
        raise ValueError(msg)
    if table.columns[:3] != ["line", "Inc", "Time"]:
        msg = "Canonical report columns do not identify Inc and Time"
        raise ValueError(msg)
    columns = tuple(table.columns[3:])
    if not columns:
        msg = "Native report has no hydrograph ordinate columns"
        raise ValueError(msg)
    rows = tuple(
        HydrographRow(
            int(str(row["line"])),
            int(str(row["Inc"])),
            table.source_decimal(index, "Time"),
            tuple(table.source_decimal(index, column) for column in columns),
            table.source_tokens[index]["Time"],
        )
        for index, row in enumerate(table.rows)
    )
    timestep_raw = document.metadata.get("time_increment_raw")
    timestep: Decimal | None = exact_number(timestep_raw) if isinstance(timestep_raw, str) else None
    duration_raw = document.metadata.get("reported_duration_increments")
    duration = duration_raw if isinstance(duration_raw, int) and not isinstance(duration_raw, bool) else None
    return HydrographReport(columns, rows, timestep, duration)


def inspect_output(source: RorbSource) -> Inspection:
    """Inspect exactly the already-selected report source through ryan-tools.

    File and byte fingerprints must match the original RorbSource. A change
    between reads is an error, never a reason to use a different snapshot.
    Inspection never launches RORB or establishes physical site identities.
    """
    try:
        canonical = read_rorb_file(source.path)
    except (OSError, UnicodeError, ValueError) as exc:
        return Inspection("output_report", "invalid", source, (Diagnostic("reader_error", str(exc), "error"),))
    if (
        canonical.original_bytes is None
        or canonical.size_bytes != source.size_bytes
        or canonical.sha256 != source.sha256
        or canonical.lines != source.lines
    ):
        return Inspection(
            "output_report",
            "invalid",
            source,
            (Diagnostic("source_changed", "Native report bytes changed between source and canonical reads", "error"),),
        )
    if canonical.kind != "standard_output":
        return Inspection(
            "output_report",
            "unsupported",
            source,
            (Diagnostic("no_supported_table", "No characterised native Inc/Time report structure", "unsupported"),),
        )

    diagnostics = _diagnostics(canonical)
    tables = [section for section in canonical.sections if section.name.startswith("hydrographs_")]
    if not tables:
        status = "invalid" if canonical.status == "invalid" else "unsupported"
        severity = "error" if status == "invalid" else "unsupported"
        return Inspection(
            "output_report",
            status,
            source,
            (*diagnostics, Diagnostic("no_supported_table", "No valid Inc/Time HydNNN summary", severity)),
        )
    if len(tables) != 1:
        return Inspection(
            "output_report",
            "invalid",
            source,
            (*diagnostics, Diagnostic("ambiguous_tables", "Multiple hydrograph tables need separate identities", "error")),
        )
    if canonical.status == "invalid" or not tables[0].valid:
        return Inspection("output_report", "invalid", source, tuple(diagnostics))
    try:
        report = _report(source, canonical, tables[0])
    except (ValueError, IndexError, KeyError) as exc:
        return Inspection(
            "output_report", "invalid", source, (*diagnostics, Diagnostic("canonical_binding", str(exc), "error"))
        )

    diagnostics.append(
        Diagnostic("print_identity_unverified", "HydNNN labels do not establish native print locations", "warning")
    )
    if report.reported_duration_increments is None and not any(d.code == "completion_unverified" for d in diagnostics):
        diagnostics.append(
            Diagnostic("completion_unverified", "Cannot verify completion without a reported duration", "warning")
        )
    if report.time_increment_hours is None:
        diagnostics.append(Diagnostic("timestep_unverified", "No reported timestep; raw labels preserved", "warning"))
    return Inspection("output_report", "partial", source, tuple(diagnostics), hydrographs=report)
