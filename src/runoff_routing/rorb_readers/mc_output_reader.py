"""Bounded source-preserving RORBWin 6.52 MC printed-report grammar (#232).

Printed observations do not establish physical units/sites, effective events,
probability convention, sampling weights or a native frequency method.
"""

import re
from typing import Never

from .reader_types import Record, RorbDocument, Section, Value, exact_number, integer, number
from .result_readers import report_metadata

_NUMERIC = re.compile(r"\d+(?:\.\d+)?\Z")
_MARKERS = (
    r"Results for Storm Duration of (\d+(?:\.\d+)?) hour",
    r"Rorb model check run completed OK:",
    r"Monte-Carlo sampling undertaken using\s+(\d+) runs over each rainfall interval,",
    r"Label\s+Description",
    r"Div\s+Run\s+AEP\s+Depth\s+TPat\s+I\.L\.\s+IL_F\s+LR_F\s+Peak\s+(\d+)",
    r">>> Distributional check on temporal patterns",
    r">>> Exceedance frequency percentiles check on losses \(prior to factoring\)",
    r">>> Frequency distributional check on losses \(prior to factoring\)",
    r">>> Analysis of flow results",
    re.escape(
        "Peak flows for selected AEPs (* indicates value unreliable, ie bounded by interval contributions to AEP > 20% total)"
    ),
    r"Elapsed Run Time \(hh:mm:ss\) = (\d{2}:[0-5]\d:[0-5]\d)",
)
_EVENT_COLUMNS = ("Div", "Run", "AEP", "Depth", "TPat", "I.L.", "IL_F", "LR_F", "Peak")
_LEGEND = (
    "Div Number of discretised rainfall interval",
    "Run Number of run within given rainfall interval",
    "ARI ARI of stochastic rainfall depth",
    "Depth Depth (mm) of stochastic design rainfall burst",
    "TPat Rank of temporal pattern selected from *_mc.pat file for given duration",
    "I.L. Stochastic factor applied to initial loss parameter",
    "IL_F ARI-dependent deterministic factors applied to initial loss parameter",
    "LR_F ARI-dependent deterministic factors applied to loss rate parameter",
)


class _MCReportError(ValueError):
    def __init__(self, message: str, line: int | None = None) -> None:
        super().__init__(message)
        self.line = line


def _fail(message: str, line: int | None = None) -> Never:
    raise _MCReportError(message, line)


def _one(doc: RorbDocument, pattern: str) -> tuple[int, re.Match[str]]:
    matches = [(i, match) for i, line in enumerate(doc.lines) if (match := re.fullmatch(pattern, line.strip()))]
    if len(matches) != 1:
        _fail("Missing, repeated or unadmitted MC boundary/header.", matches[0][0] + 1 if matches else None)
    return matches[0]


def _body(doc: RorbDocument, start: int, end: int) -> list[tuple[int, str]]:
    return [(i + 1, doc.lines[i].strip()) for i in range(start + 1, end) if doc.lines[i].strip()]


def _numeric(token: str, line: int, *, ordinal: bool = False) -> Value:
    if len(token) > 128 or _NUMERIC.fullmatch(token) is None:
        _fail("Unadmitted/nonfinite MC numeric spelling.", line)
    try:
        return integer(token, 1) if ordinal else number(token)
    except ValueError as exc:
        message = "Invalid/nonfinite MC numeric value."
        raise _MCReportError(message, line) from exc


def _append(section: Section, line: int, tokens: list[str], *, ordinals: tuple[str, ...] = ()) -> None:
    if len(tokens) != len(section.columns):
        _fail("MC table row has the wrong number of columns.", line)
    row: Record = {"line": line}
    for column, token in zip(section.columns, tokens, strict=True):
        row[column] = _numeric(token, line, ordinal=column in ordinals)
    section.rows.append(row)
    section.source_tokens.append(dict(zip(section.columns, tokens, strict=True)))


def _table(doc: RorbDocument, name: str, columns: tuple[str, ...]) -> Section:
    section = Section(name, list(columns), completeness="complete")
    doc.sections.append(section)
    return section


def _head(rows: list[tuple[int, str]], expected: list[str]) -> list[tuple[int, str]]:
    if len(rows) < len(expected) or [" ".join(text.split()) for _, text in rows[: len(expected)]] != expected:
        _fail("Missing or changed MC table column labels.", rows[0][0] if rows else None)
    return rows[len(expected) :]


def _preamble(doc: RorbDocument, duration_index: int, duration: str) -> None:
    patterns = (
        r"RORBWin Monte-Carlo Run Summary",
        r"\*+",
        r"Program version 6\.52 \(last updated .+\)",
        r"Copyright Monash University and Hydrology and Risk Consulting",
        r"Date run:\s+.+",
        r"Catchment file\s*:\s+.+",
        r"Rainfall location:\s+.+",
        r"Spatial pattern\s*:\s+.+",
        r"Areal Red\. Fact\.\s*:\s+.+",
        r"Loss factors\s*:\s+.+",
        r"Temporal pattern\s*:\s+Areal temporal patterns Monte-Carlo sampled from .+ based on\s+\d+ km² sample",
        r"Duration\(hr\)\s+(\d+(?:\.\d+)?)",
        r"Num avail\s+10",
        r"Parameters:\s+kc\s*=\s*\S+\s+m\s*=\s*\S+",
        r"Loss parameters\s+Initial loss \(mm\)\s+Cont\. loss \(mm/h\)",
        r"\S+\s+\S+",
    )
    rows = _body(doc, -1, duration_index)
    if len(rows) != len(patterns):
        _fail("Unadmitted MC preamble/extra records.")
    for (line, text), pattern in zip(rows, patterns, strict=True):
        if re.fullmatch(pattern, text) is None:
            _fail("Changed/unadmitted MC preamble field.", line)
    displayed_duration = rows[11][1].split()[-1]
    if exact_number(displayed_duration) != exact_number(duration):
        _fail("Conflicting MC displayed durations.", rows[11][0])


def _context(doc: RorbDocument, markers: list[tuple[int, re.Match[str]]]) -> tuple[str, int, int, str]:
    duration = markers[0][1][1]
    if _numeric(duration, markers[0][0] + 1) == 0:
        _fail("MC duration must be positive.", markers[0][0] + 1)
    runs = integer(markers[2][1][1], 1)
    allocation = _body(doc, markers[2][0], markers[3][0])
    if len(allocation) != 1:
        _fail("Unsupported MC allocation declaration.", markers[2][0] + 1)
    match = re.fullmatch(r"where the rainfall distribution is discretised into\s+(\d+) intervals\.", allocation[0][1])
    if match is None:
        _fail("Missing MC division declaration.", allocation[0][0])
    divisions = integer(match[1], 1)
    peak = markers[4][1][1]
    legend = _body(doc, markers[3][0], markers[4][0])
    if len(legend) != 10 or re.fullmatch(r"-+\s+-+", legend[0][1]) is None:
        _fail("Unsupported MC legend structure.", markers[3][0] + 1)
    if tuple(" ".join(text.split()) for _, text in legend[1:9]) != _LEGEND:
        _fail("Changed MC field meaning/units in legend.", markers[3][0] + 1)
    output = re.fullmatch(r"Peak\s+(\d+)\s+(.+)", legend[-1][1])
    if output is None or output[1] != peak:
        _fail("Ambiguous MC report-local output identity.", legend[-1][0])
    outputs = _table(doc, "mc_outputs", ("ordinal",))
    _append(outputs, legend[-1][0], [peak], ordinals=("ordinal",))
    outputs.rows[0]["description"] = output[2]
    doc.metadata.update(
        mc_duration_hours_token=duration,
        mc_runs_per_division=runs,
        mc_divisions=divisions,
        mc_peak_ordinal=peak,
    )
    return duration, runs, divisions, peak


def _checks(doc: RorbDocument, start: int, end: int) -> None:
    rows = _body(doc, start, end)
    patterns = (
        r"No\. of time increments in run\s*=\s*(\d+)",
        r"Simulation time increment \(hrs\)\s*=\s*(\d+(?:\.\d+)?)",
        r"Number of incs in rainfall burst\s*=\s*(\d+)",
        r"Number of sub- & intrstn-areas\s*=\s*(\d+)\s+(\d+)",
        r"Number of hydrographs to track\s*=\s*(1)",
    )
    if len(rows) != len(patterns):
        _fail("Unsupported MC model-check display.", start + 1)
    section = _table(doc, "mc_model_check", ())
    for (line, text), pattern in zip(rows, patterns, strict=True):
        match = re.fullmatch(pattern, text)
        if match is None:
            _fail("Unsupported MC model-check field or multiple peak layout.", line)
        tokens = match.groups()
        for token in tokens:
            _numeric(token, line)
        section.rows.append({"line": line, "label": text.split("=", 1)[0].strip()})
        section.source_tokens.append({str(i): token for i, token in enumerate(tokens)})


def _events(doc: RorbDocument, start: int, end: int, runs: int, divisions: int) -> None:
    section = _table(doc, "mc_events", _EVENT_COLUMNS)
    seen: set[tuple[int, int]] = set()
    for line, text in _body(doc, start, end):
        _append(section, line, text.split(), ordinals=("Div", "Run", "TPat"))
        division, run = int(str(section.rows[-1]["Div"])), int(str(section.rows[-1]["Run"]))
        if (division, run) in seen or division > divisions or run > runs:
            _fail("Duplicate or out-of-allocation MC event identity.", line)
        seen.add((division, run))
    # Count + unique bounded positive indices proves a full grid without constructing a huge declared grid.
    if len(seen) != runs * divisions:
        _fail("Missing/truncated MC event allocation.", start + 1)


def _tp_diagnostic(doc: RorbDocument, start: int, end: int) -> None:
    rows = _body(doc, start, end)
    if (
        len(rows) != 2
        or re.fullmatch(r"Pattern#:\s+.+", rows[0][1]) is None
        or re.fullmatch(r"Freq%\s*:\s+.+", rows[1][1]) is None
    ):
        _fail("Malformed MC temporal-pattern diagnostic.", start + 1)
    patterns = rows[0][1].split(":", 1)[1].split()
    if ":" not in rows[1][1]:
        _fail("Missing MC TP frequency boundary.", rows[1][0])
    frequencies = rows[1][1].split(":", 1)[1].split()
    if len(patterns) != 10 or len(frequencies) != len(patterns):
        _fail("Unadmitted MC pattern diagnostic width.", rows[0][0])
    section = _table(doc, "mc_tp_diagnostic", ("TPat", "frequency_percent"))
    for pattern, frequency in zip(patterns, frequencies, strict=True):
        _append(section, rows[1][0], [pattern, frequency], ordinals=("TPat",))
        section.rows[-1]["pattern_line"] = rows[0][0]
    _percentages(section, ("frequency_percent",))
    if [row["TPat"] for row in section.rows] != list(range(1, 11)):
        _fail("Ambiguous MC pattern ranks.", rows[0][0])
    for event in doc.section("mc_events").rows:
        if int(str(event["TPat"])) > 10:
            _fail("MC event rank outside printed diagnostic scope.", int(str(event["line"])))


def _percentages(section: Section, columns: tuple[str, ...]) -> None:
    for i, row in enumerate(section.rows):
        for column in columns:
            if not 0 <= section.source_decimal(i, column) <= 100:
                _fail("MC diagnostic percentage outside [0,100].", int(str(row["line"])))


def _loss_diagnostics(doc: RorbDocument, markers: list[tuple[int, re.Match[str]]]) -> None:
    rows = _head(_body(doc, markers[6][0], markers[7][0]), ["Percentile Initial Loss"])
    section = _table(doc, "mc_loss_percentiles", ("percentile", "value"))
    for line, text in rows:
        _append(section, line, text.split())
    if [integer(tokens["percentile"]) for tokens in section.source_tokens] != list(range(0, 101, 5)):
        _fail("Unadmitted/truncated MC percentile grid.", markers[6][0] + 1)
    rows = _head(
        _body(doc, markers[7][0], markers[8][0]),
        ["Upper Limit Init Loss Upper Limit Init Loss", "(Lin intvl) Freq(%) (Log intvl) Freq(%)"],
    )
    if len(rows) != 11:
        _fail("Truncated MC loss histogram or totals.", markers[7][0] + 1)
    histogram = _table(doc, "mc_loss_histogram", ("linear_limit", "linear_percent", "log_limit", "log_percent"))
    for line, text in rows[:-1]:
        _append(histogram, line, text.split())
    _percentages(histogram, ("linear_percent", "log_percent"))
    totals = _table(doc, "mc_loss_histogram_totals", ("linear_percent", "log_percent"))
    _append(totals, rows[-1][0], rows[-1][1].split())
    _percentages(totals, ("linear_percent", "log_percent"))


def _flow_summary(doc: RorbDocument, markers: list[tuple[int, re.Match[str]]], peak: str) -> None:
    rows = _head(_body(doc, markers[8][0], markers[9][0]), ["Peak Min Value Max value Description"])
    if len(rows) != 1:
        _fail("Unadmitted multiple/missing MC peak extrema.", markers[8][0] + 1)
    tokens = rows[0][1].split(maxsplit=3)
    if len(tokens) != 4 or tokens[0] != peak:
        _fail("Ambiguous MC extrema output identity.", rows[0][0])
    extrema = _table(doc, "mc_flow_extrema", ("ordinal", "minimum", "maximum"))
    _append(extrema, rows[0][0], tokens[:3], ordinals=("ordinal",))
    extrema.rows[0]["description"] = tokens[3]
    if extrema.source_decimal(0, "minimum") > extrema.source_decimal(0, "maximum"):
        _fail("Reversed MC displayed extrema.", rows[0][0])
    rows = _head(_body(doc, markers[9][0], markers[10][0]), [f"No. AEP(1inY) Peak {peak}"])
    if len(rows) != 16:
        _fail("Truncated/unadmitted MC selected-probability summary.", markers[9][0] + 1)
    summary = _table(doc, "mc_probability_summary", ("ordinal", "coordinate", "Peak"))
    for line, text in rows:
        tokens = text.split()
        flagged = bool(tokens and tokens[-1].endswith("*"))
        raw_peak = tokens[-1] if tokens else ""
        if flagged:
            tokens[-1] = raw_peak[:-1]
        _append(summary, line, tokens, ordinals=("ordinal",))
        summary.rows[-1]["unreliable"] = flagged
        summary.source_tokens[-1]["peak_with_marker"] = raw_peak
    if [row["ordinal"] for row in summary.rows] != list(range(1, 17)):
        _fail("Duplicate/out-of-order MC summary ordinals.", markers[9][0] + 1)


def _read_structure(doc: RorbDocument) -> None:
    markers = [_one(doc, pattern) for pattern in _MARKERS]
    indices = [line for line, _ in markers]
    if indices != sorted(set(indices)):
        _fail("MC sections are repeated, reordered or overlap.")
    _preamble(doc, indices[0], markers[0][1][1])
    underline = _body(doc, indices[0], indices[1])
    if len(underline) != 1 or re.fullmatch(r"~+", underline[0][1]) is None:
        _fail("Unadmitted MC duration block.", indices[0] + 1)
    if any(line.strip() for line in doc.lines[indices[-1] + 1 :]):
        _fail("Unadmitted trailing MC records.", indices[-1] + 2)
    duration, runs, divisions, peak = _context(doc, markers)
    doc.metadata["mc_elapsed_token"] = markers[-1][1][1]
    _checks(doc, indices[1], indices[2])
    _events(doc, indices[4], indices[5], runs, divisions)
    _tp_diagnostic(doc, indices[5], indices[6])
    _loss_diagnostics(doc, markers)
    _flow_summary(doc, markers, peak)
    doc.metadata["mc_duration_hours_token"] = duration


def read_mc_output(doc: RorbDocument) -> None:
    """Parse the admitted one-duration/one-output printed subset, without scientific inference."""
    report_metadata(doc)
    doc.metadata.update(
        mc_structure_complete=False,
        mc_peak_unit=None,
        mc_physical_site_id=None,
        mc_probability_interpretation=None,
        mc_native_event_weights=None,
        mc_exact_effective_inputs=False,
        mc_frequency_law=None,
    )
    versions = [
        line.split()[2] for line in doc.lines if line.strip().startswith("Program version ") and len(line.split()) > 2
    ]
    if versions != ["6.52"]:
        doc.issue("mc_profile_not_admitted", "Only the source-admitted 6.52 printed layout is supported.")
        return
    if any(diagnostic.severity == "error" for diagnostic in doc.diagnostics):
        return
    try:
        _read_structure(doc)
    except ValueError as exc:
        for section in doc.sections:
            if section.name.startswith("mc_"):
                section.valid, section.completeness = False, "incomplete"
        doc.issue("mc_invalid_structure", str(exc), getattr(exc, "line", None), error=True)
        return
    if any(diagnostic.severity == "error" for diagnostic in doc.diagnostics):
        return
    doc.metadata["mc_structure_complete"] = True
    doc.issue(
        "mc_scientific_fields_unavailable",
        "Printed MC structure only: peak units/site, probability convention, weights and effective events remain unavailable.",
    )
    # Partial means the printed subset is usable but not a fully interpreted native/scientific document.
