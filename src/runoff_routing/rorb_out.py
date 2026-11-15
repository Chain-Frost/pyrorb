"""Bind the canonical ryan-tools RORB report to runoff's existing evidence contract.

All native report grammar, numeric token parsing, source preservation, increment
validation and scalar recognition live in ryan-tools. This adapter supplies only
the project-facing immutable inspection shape consumed by the CMD/regression
contracts. It does not infer physical Hyd identities or shift printed clocks.
"""

from __future__ import annotations

from decimal import Decimal
from hashlib import sha256

from ryan_library.functions.RORB.reader_types import RorbDocument, Section, exact_number
from ryan_library.functions.RORB.readers import read_rorb_bytes, read_rorb_file

from .rorb_documents import Diagnostic, HydrographReport, HydrographRow, Inspection, RorbSource


def _diagnostics(document: RorbDocument) -> list[Diagnostic]:
    """Carry canonical diagnostics and their original source line provenance."""
    return [Diagnostic(item.code, item.message, item.severity, item.line) for item in document.diagnostics]


def _report(document: RorbDocument, table: Section) -> HydrographReport:
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


class SourceChangedError(ValueError):
    """The selected report differs from the previously fingerprinted bytes."""


def _reauthenticated_inline_bytes(source: RorbSource) -> bytes:
    """Recover only an authenticated in-memory source, never infer original line endings.

    The old synthetic evidence tests supply exact lines/size/SHA but no path
    or raw-byte field. A candidate is used only if its *full original byte*
    size and SHA-256 agree; unknown encodings or mixed line endings fail closed.
    This is a source transport step, not a report grammar or numeric parser.
    """
    source_text = "\n".join(source.lines)
    for separator in ("\n", "\r\n"):
        for suffix in ("", separator):
            candidate = (source_text.replace("\n", separator) + suffix).encode(source.encoding)
            if len(candidate) == source.size_bytes and sha256(candidate).hexdigest() == source.sha256:
                return candidate
    message = "Cannot reauthenticate missing source path from original line/byte/hash evidence"
    raise SourceChangedError(message)


def checked_canonical_report(source: RorbSource) -> RorbDocument:
    """Read and authenticate a file or exact in-memory source through ryan-tools."""
    if source.path.is_file():
        canonical = read_rorb_file(source.path)
    else:
        original = _reauthenticated_inline_bytes(source)
        canonical = read_rorb_bytes(original, path=source.path, encoding=source.encoding)
        canonical.issue(
            "source_path_unavailable",
            "Original source path is missing; bytes reauthenticated against supplied full hash and size.",
        )
    if (
        canonical.original_bytes is None
        or canonical.size_bytes != source.size_bytes
        or canonical.sha256 != source.sha256
        or canonical.lines != source.lines
    ):
        message = "Native report bytes changed between source and canonical reads"
        raise SourceChangedError(message)
    return canonical


def _has_non_scalar_errors(diagnostics: list[Diagnostic]) -> bool:
    """Preserve independently valid tables when only a reported scalar failed."""
    scalar_codes = {"reported_scalar_value", "reported_scalar_values", "reported_scalar_layout"}
    return any(diagnostic.severity == "error" and diagnostic.code not in scalar_codes for diagnostic in diagnostics)


def inspect_output(source: RorbSource) -> Inspection:
    """Inspect a selected source via ryan-tools; never infer HydNNN physical sites."""
    try:
        canonical = checked_canonical_report(source)
    except SourceChangedError as exc:
        return Inspection("output_report", "invalid", source, (Diagnostic("source_changed", str(exc), "error"),))
    except (OSError, UnicodeError, ValueError) as exc:
        return Inspection("output_report", "invalid", source, (Diagnostic("reader_error", str(exc), "error"),))
    return _adapt_canonical_output(source, canonical)


def _adapt_canonical_output(source: RorbSource, canonical: RorbDocument) -> Inspection:
    """Keep generic parser outcomes distinct from downstream physical identity."""
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
            (
                *diagnostics,
                Diagnostic("ambiguous_tables", "Multiple hydrograph tables need separate identities", "error"),
            ),
        )
    if not tables[0].valid:
        return Inspection("output_report", "invalid", source, tuple(diagnostics))
    # Scalar parsing is independent of numeric hydrograph parsing. Retain a
    # valid table for diagnostic review even if a scalar is malformed; report
    # status remains invalid and cannot be treated as simulated acceptance.
    if _has_non_scalar_errors(diagnostics):
        return Inspection("output_report", "invalid", source, tuple(diagnostics))
    try:
        report = _report(canonical, tables[0])
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
    status = "invalid" if canonical.status == "invalid" else "partial"
    return Inspection("output_report", status, source, tuple(diagnostics), hydrographs=report)
