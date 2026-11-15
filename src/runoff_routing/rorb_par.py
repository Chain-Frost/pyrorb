"""Strict read-only inspection of the documented single-burst RORB_CMD parameter dialect."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from decimal import Decimal
from typing import Literal

from .rorb_documents import (
    Diagnostic,
    Inspection,
    LossParameter,
    ParameterModel,
    RorbSource,
    RoutingParameter,
    SourceField,
    decimal_number,
    positive_integer,
)


@dataclass(slots=True)
class _Cursor:
    source: RorbSource
    position: int = 1
    fields: tuple[SourceField, ...] = ()

    def take(self, label: str) -> SourceField:
        if self.position >= len(self.source.lines) - 1:
            message = f"Missing {label} record at line {self.position + 1}"
            raise ValueError(message)
        line = self.source.lines[self.position]
        current_line = self.position + 1
        self.position += 1
        if len(line) < 11 or line[:10].strip().casefold() != label.casefold():
            message = f"Expected {label!r} field at line {current_line}, columns 1-10"
            raise ValueError(message)
        field = SourceField(current_line, line[:10], line[10:].strip(), line)
        self.fields = (*self.fields, field)
        if not field.value:
            message = f"Empty {label} value at line {current_line}"
            raise ValueError(message)
        return field

    def isa(self, expected: int) -> SourceField:
        if self.position >= len(self.source.lines) - 1:
            message = f"Missing ISA {expected} record at line {self.position + 1}"
            raise ValueError(message)
        prefix = self.source.lines[self.position][:10].strip()
        match = re.fullmatch(r"ISA\s+(\d+)\s*:", prefix, flags=re.IGNORECASE)
        if match is None or int(match[1]) != expected:
            message = f"Expected ISA {expected} at line {self.position + 1}; found {prefix!r}"
            raise ValueError(message)
        return self.take(self.source.lines[self.position][:10].strip())


def _pair(field: SourceField) -> tuple[Decimal, Decimal]:
    values = field.value.split(",")
    if len(values) != 2:
        message = f"Expected exactly two comma-separated values at line {field.line}"
        raise ValueError(message)
    return decimal_number(values[0].strip()), decimal_number(values[1].strip())


def _parse(cursor: _Cursor) -> ParameterModel:
    catchment = cursor.take("Cat file :").value
    storm = cursor.take("Stm file :").value
    flag = cursor.take("Lumped kc:").value.upper()
    if flag not in {"T", "F"}:
        message = "Lumped kc flag must be T or F"
        raise ValueError(message)
    lumped = flag == "T"
    verbosity = positive_integer(cursor.take("Verbosity:").value)
    if verbosity not in (1, 2, 3):
        message = "Verbosity must be 1, 2 or 3"
        raise ValueError(message)
    loss_model = positive_integer(cursor.take("Lossmodel:").value)
    if loss_model not in (1, 2):
        message = f"Unsupported loss-model flag {loss_model}"
        raise NotImplementedError(message)
    isa_count = positive_integer(cursor.take("Num ISA  :").value)
    routing: list[RoutingParameter] = []
    for index in range(1, (1 if lumped else isa_count) + 1):
        field = cursor.isa(index)
        kc, m = _pair(field)
        if kc <= 0 or m <= 0:
            message = f"kc and m must be positive at line {field.line}"
            raise ValueError(message)
        routing.append(RoutingParameter(index, kc, m, field.line))
    bursts = positive_integer(cursor.take("Num burst:").value)
    if bursts != 1:
        message = "Only a single burst is characterised; subsequent record ordering is unknown"
        raise NotImplementedError(message)
    losses: list[LossParameter] = []
    for index in range(1, isa_count + 1):
        field = cursor.isa(index)
        initial, continuing = _pair(field)
        if initial < 0 or continuing < 0:
            message = f"Loss values must be nonnegative at line {field.line}"
            raise ValueError(message)
        losses.append(LossParameter(index, 1, initial, continuing, field.line))
    if cursor.position != len(cursor.source.lines) - 1:
        message = "Additional parameter records are not characterised"
        raise NotImplementedError(message)
    recognised_loss: Literal[1, 2] = 1 if loss_model == 1 else 2
    return ParameterModel(
        catchment, storm, lumped, verbosity, recognised_loss, isa_count, bursts, tuple(routing), tuple(losses)
    )



def _recognised_rorbwin_saved_par(lines: tuple[str, ...]) -> bool:
    """Narrow 6.52-family saved-PAR signature from four retained native GUI captures.

    Original saved files have a directory, run-mode integer, blank separator,
    CATG/STM paths, four control lines, ARR mode header and long numeric tables.
    This is deliberately *not* a broad RORBwin grammar or guessed version.
    """
    if len(lines) < 700 or len(lines) < 20 or lines[2].strip():
        return False
    if not re.fullmatch(r"[123]", lines[1].strip()):
        return False
    if not lines[3].strip().lower().endswith((".catg", ".cat")):
        return False
    if not lines[4].strip().lower().endswith(".stm"):
        return False
    if any(lines[index].strip() for index in (5, 6, 7)):
        return False
    if lines[8].strip() not in {"1", "2", "3"} or lines[9].strip() not in {"T", "F"}:
        return False
    if not all(re.fullmatch(r"[0-9]+", lines[index].strip()) for index in (10, 11, 12)):
        return False
    if len(lines[13].split()) < 8:
        return False
    if not lines[14].strip().startswith(("ARR ", "ARR2016 ")):
        return False
    if lines[15].split() != ["T", "F"]:
        return False
    return sum("-999.00" in line for line in lines[-60:]) >= 5


def inspect_par_bytes(data: bytes, *, source_path: Path | None = None) -> Inspection:
    """Classify PAR bytes without touching the filesystem or following references."""
    try:
        text = data.decode("utf-8-sig")
        encoding = "utf-8-sig"
    except UnicodeDecodeError:
        text = data.decode("cp1252")
        encoding = "cp1252"
    source = RorbSource(
        source_path if source_path is not None else Path("<memory.par>"),
        hashlib.sha256(data).hexdigest(),
        len(data),
        encoding,
        tuple(text.splitlines()),
    )
    return inspect_cmd_parameters(source)


def read_par_file(path: Path) -> Inspection:
    """One explicit filesystem adapter; inspect-only, no reference traversal."""
    return inspect_par_bytes(path.read_bytes(), source_path=path.absolute())


def inspect_cmd_parameters(source: RorbSource) -> Inspection:
    """Only the documented CMD V2 signature is accepted; GUI .par is not CMD."""
    lines = source.lines
    if not lines or lines[0] != "# BEGIN":
        if _recognised_rorbwin_saved_par(lines):
            return Inspection(
                "rorbwin_saved_par",
                "unsupported",
                source,
                (
                    Diagnostic(
                        "rorbwin_saved_par_deferred",
                        "Recognised RORBwin 6.52-family saved PAR; settings import is deferred. "
                        "Use a supported RORB_CMD PAR; do not treat these settings as CMD.",
                        "unsupported",
                    ),
                ),
            )
        return Inspection(
            "unknown_par",
            "unsupported",
            source,
            (
                Diagnostic(
                    "unknown_par_dialect",
                    "Unrecognised PAR content (not a documented CMD # BEGIN file or a "
                    "characterised RORBwin saved-PAR signature)",
                    "unsupported",
                ),
            ),
        )
    if lines[-1] != "# END" or lines.count("# BEGIN") != 1 or lines.count("# END") != 1:
        return Inspection(
            "cmd_par",
            "invalid",
            source,
            (Diagnostic("cmd_boundary", "Expected one column-1 # BEGIN / # END pair", "error"),),
        )
    cursor = _Cursor(source)
    try:
        model = _parse(cursor)
    except NotImplementedError as exc:
        return Inspection(
            "cmd_par",
            "unsupported",
            source,
            (Diagnostic("cmd_variant", str(exc), "unsupported", cursor.position),),
            cursor.fields,
        )
    except ValueError as exc:
        return Inspection(
            "cmd_par",
            "invalid",
            source,
            (Diagnostic("cmd_record", str(exc), "error", max(1, cursor.position - 1)),),
            cursor.fields,
        )
    notes = [Diagnostic("engine_unverified", "Parsed settings are not proof of executable compatibility", "warning")]
    if model.loss_model == 2:
        notes.append(
            Diagnostic("loss_2_unverified", "IL/runoff-coefficient semantics need native verification", "warning")
        )
    return Inspection("cmd_par", "parsed", source, tuple(notes), cursor.fields, parameters=model)
