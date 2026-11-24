"""Read-only JSON/CSV presentations of the canonical PyRORB report records.

This module contains no RORB report grammar, event selection, physical-site
mapping, numerical acceptance, source-file mutation or executable invocation.
"""

from __future__ import annotations

import csv
import io
import json
from dataclasses import asdict
from pathlib import Path

from .rorb_readers.reader_types import RorbDocument, Section
from .rorb_readers.readers import read_rorb_file

MAX_VIEW_ROWS = 10_000
_SUPPORTED_REPORTS = frozenset({"standard_output", "batch_output", "hydrograph_csv"})


def inspect_report(path: Path) -> RorbDocument:
    """Open a canonical native result; never activate saved-PAR interpretation."""
    document = read_rorb_file(path)
    if document.kind not in _SUPPORTED_REPORTS:
        message = f"Not a characterised RORB result report: {document.kind}"
        raise ValueError(message)
    return document


def _window(offset: int, limit: int) -> None:
    if isinstance(offset, bool) or isinstance(limit, bool) or offset < 0 or not 0 <= limit <= MAX_VIEW_ROWS:
        message = f"Report offset must be nonnegative and limit must be 0..{MAX_VIEW_ROWS}"
        raise ValueError(message)


def _section(document: RorbDocument, name: str) -> Section:
    selected = next((item for item in document.sections if item.name == name), None)
    if selected is None:
        names = ", ".join(item.name for item in document.sections)
        message = f"Unknown report section {name!r}; available sections: {names}"
        raise ValueError(message)
    return selected


def report_json(document: RorbDocument, *, section: str | None = None, offset: int = 0, limit: int = 100) -> str:
    """Summarise source identity/diagnostics, optionally paging exact source rows."""
    _window(offset, limit)
    payload: dict[str, object] = {
        "path": str(document.path),
        "kind": document.kind,
        "status": document.status,
        "source_sha256": document.sha256,
        "size_bytes": document.size_bytes,
        "encoding": document.encoding,
        "line_count": len(document.lines),
        "metadata": document.metadata,
        "diagnostics": [asdict(item) for item in document.diagnostics],
        "sections": [
            {
                "name": item.name,
                "valid": item.valid,
                "completeness": item.completeness,
                "row_count": len(item.rows),
                "increment_origin": item.increment_origin,
            }
            for item in document.sections
        ],
    }
    if section is not None:
        selected = _section(document, section)
        rows: list[dict[str, object]] = []
        for index in range(offset, min(offset + limit, len(selected.rows))):
            entry: dict[str, object] = {
                "values": selected.rows[index],
                "original_tokens": selected.source_tokens[index] if index < len(selected.source_tokens) else None,
            }
            rows.append(entry)
        payload["selection"] = {
            "section": selected.name,
            "valid": selected.valid,
            "completeness": selected.completeness,
            "columns": selected.columns,
            "offset": offset,
            "returned_rows": len(rows),
            "total_rows": len(selected.rows),
            "rows": rows,
        }
    return json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"


def report_csv(document: RorbDocument, section: str, *, offset: int = 0, limit: int = 100) -> str:
    """Render selected typed rows plus separate exact original token columns."""
    _window(offset, limit)
    selected = _section(document, section)
    value_fields = list(dict.fromkeys([*selected.columns, *(key for row in selected.rows for key in row)]))
    token_fields = list(dict.fromkeys(key for tokens in selected.source_tokens for key in tokens))
    raw_headers = {name: f"source_token__{name}" for name in token_fields}
    headers = [*value_fields, *raw_headers.values()]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=headers, lineterminator="\n")
    writer.writeheader()
    for index in range(offset, min(offset + limit, len(selected.rows))):
        record: dict[str, object] = dict(selected.rows[index])
        if index < len(selected.source_tokens):
            for name, value in selected.source_tokens[index].items():
                record[raw_headers[name]] = value
        writer.writerow(record)
    return output.getvalue()
