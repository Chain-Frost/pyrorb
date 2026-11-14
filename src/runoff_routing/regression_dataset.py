"""Read-only, source-pinned regression dataset and candidate-output comparator.

No native executables, model dispatch, golden regeneration or private imports.
This contract is intentionally separate from the engine/result API in issue #74.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import platform
import re
import sys
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from typing import Any, cast

FORMAT = "runoff-regression-register"
RESULT_FORMAT = "runoff-regression-results"
VERSION = 1
HASH = re.compile(r"[0-9a-f]{64}\Z")
CSV_COLUMNS = (
    "case_id",
    "classification",
    "model_print_id",
    "native_column_id",
    "sample_index",
    "raw_native_increment",
    "raw_native_time",
    "native_discharge_token",
    "python_discharge_m3_s",
)


class RegressionError(ValueError):
    """Malformed, unsafe or otherwise unusable regression evidence."""


def _unique(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            message = f"duplicate JSON key: {key}"
            raise RegressionError(message)
        result[key] = value
    return result


def _nonfinite(token: str) -> None:
    message = f"invalid nonfinite JSON token: {token}"
    raise RegressionError(message)


def _json(path: Path) -> dict[str, Any]:
    if path.stat().st_size > 4_000_000:
        message = f"oversized JSON: {path}"
        raise RegressionError(message)
    item = json.loads(path.read_bytes().decode("utf-8"), object_pairs_hook=_unique, parse_constant=_nonfinite)
    if not isinstance(item, dict):
        message = f"expected a JSON object: {path}"
        raise RegressionError(message)
    return cast("dict[str, Any]", item)


def _scalar(token: object) -> Decimal:
    if not isinstance(token, (str, int)) or isinstance(token, bool):
        message = f"invalid scalar token: {token!r}"
        raise RegressionError(message)
    try:
        value = Decimal(str(token))
    except InvalidOperation as exc:
        message = f"invalid scalar token: {token!r}"
        raise RegressionError(message) from exc
    if not value.is_finite():
        message = f"nonfinite scalar token: {token!r}"
        raise RegressionError(message)
    return value


def _path(root: Path, relative: object) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative or ":" in relative:
        message = f"unsafe relative locator: {relative!r}"
        raise RegressionError(message)
    value = PurePosixPath(relative)
    if value.is_absolute() or any(part in {".", ".."} for part in value.parts):
        message = f"unsafe relative locator: {relative!r}"
        raise RegressionError(message)
    origin = root.resolve(strict=True)
    output = origin.joinpath(*value.parts)
    if not output.is_file():
        message = f"missing original source file: {relative}"
        raise FileNotFoundError(message)
    if output.is_symlink() or not output.resolve().is_relative_to(origin):
        message = f"unsafe original source file: {relative}"
        raise RegressionError(message)
    return output


def _hash(path: Path) -> tuple[int, str]:
    sha = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            sha.update(block)
    return path.stat().st_size, sha.hexdigest()


def _verify(root: Path, locator: dict[str, Any]) -> Path:
    target = _path(root, locator["path"])
    sha = locator.get("sha256")
    if sha is not None:
        if not isinstance(sha, str) or HASH.fullmatch(sha) is None:
            message = f"invalid expected SHA-256: {locator['path']}"
            raise RegressionError(message)
        actual = _hash(target)
    else:
        raw = target.read_bytes()
        actual = (len(raw), hashlib.sha1(f"blob {len(raw)}\0".encode() + raw, usedforsecurity=False).hexdigest())
    expected = (locator["size_bytes"], sha if sha is not None else locator["git_blob_sha1"])
    if actual != expected:
        message = f"changed original bytes {locator['path']}: expected {expected}, got {actual}"
        raise RegressionError(message)
    return target


def _time_and_values(rows: list[list[str]], step: str | None) -> None:
    if not rows:
        message = "empty original reference horizon"
        raise RegressionError(message)
    dt = _scalar(step) if step is not None else None
    for i, row in enumerate(rows, start=1):
        if len(row) < 3 or _scalar(row[0]) != i:
            message = f"shifted, missing or reordered native increment {i}"
            raise RegressionError(message)
        time = _scalar(row[1])
        if i > 1 and time <= _scalar(rows[i - 2][1]):
            message = f"non-increasing original native time {i}"
            raise RegressionError(message)
        if dt is not None:
            half_printed_unit = Decimal(1).scaleb(int(time.as_tuple().exponent)) / 2
            if abs(time - i * dt) > half_printed_unit:
                message = f"original native clock differs from effective step at increment {i}"
                raise RegressionError(message)
        for token in row[2:]:
            _scalar(token)


def _checked_rows(raw_rows: object, column_count: int, expected_count: int) -> list[list[str]]:
    """Retain the original tokens while rejecting missing, extra or malformed ordinates."""
    if not isinstance(raw_rows, list):
        message = "invalid original reference rows"
        raise RegressionError(message)
    row_objects = cast("list[object]", raw_rows)
    if len(row_objects) != expected_count:
        message = "truncated or reordered original reference horizon"
        raise RegressionError(message)
    rows: list[list[str]] = []
    for raw_row in row_objects:
        if not isinstance(raw_row, list):
            message = "ragged original native report"
            raise RegressionError(message)
        cells = cast("list[object]", raw_row)
        if len(cells) != column_count or not all(isinstance(value, str) for value in cells):
            message = "ragged or non-token native report"
            raise RegressionError(message)
        rows.append(cast("list[str]", cells))
    return rows


def _reference(root: Path, case: dict[str, Any]) -> tuple[list[str], list[list[str]]]:
    document = _json(_verify(root, case["reference"]))
    raw_tables: object = document.get("tables")
    if not isinstance(raw_tables, list) or len(raw_tables) != 1:
        message = "reference lacks exactly one complete identifiable table"
        raise RegressionError(message)
    raw_table = cast("list[object]", raw_tables)[0]
    if not isinstance(raw_table, dict):
        message = "reference table is not an object"
        raise RegressionError(message)
    table = cast("dict[str, object]", raw_table)
    raw_columns, raw_rows = table.get("columns"), table.get("rows")
    if not isinstance(raw_columns, list):
        message = "missing or invalid output column list"
        raise RegressionError(message)
    column_objects = cast("list[object]", raw_columns)
    if (
        len(column_objects) < 3
        or column_objects[:2] != ["Inc", "Time"]
        or not all(isinstance(column, str) for column in column_objects)
    ):
        message = "missing, duplicate or reordered output columns"
        raise RegressionError(message)
    columns = cast("list[str]", column_objects)
    if len(set(columns)) != len(columns):
        message = "duplicate output columns"
        raise RegressionError(message)
    rows = _checked_rows(raw_rows, len(columns), case["clock"]["row_count"])
    mapped = [site["native_column_id"] for site in case["sites"]]
    if len(mapped) != len(set(mapped)) or set(mapped) != set(columns[2:]):
        message = "physical print site map is duplicate or does not exhaust actual output columns"
        raise RegressionError(message)
    _time_and_values(rows, case["clock"].get("timestep_hours"))
    return columns, rows


def _load_register(path: Path) -> tuple[dict[str, Any], Path, dict[str, Any], str, str | None]:
    register = _json(path)
    if register.get("format") != FORMAT or register.get("schema_version") != VERSION:
        message = "unrecognised regression register format or version"
        raise RegressionError(message)
    raw_cases: object = register.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        message = "empty regression case population"
        raise RegressionError(message)
    cases: list[dict[str, Any]] = []
    for raw_case in cast("list[object]", raw_cases):
        if not isinstance(raw_case, dict):
            message = "regression case must be an object"
            raise RegressionError(message)
        entry = cast("dict[str, Any]", raw_case)
        if not isinstance(entry.get("case_id"), str) or not isinstance(entry.get("sets"), list):
            message = "regression case requires string case_id and named sets"
            raise RegressionError(message)
        cases.append(entry)
    identifiers = [entry["case_id"] for entry in cases]
    if len(identifiers) != len(set(identifiers)):
        message = "duplicate case IDs"
        raise RegressionError(message)
    register["cases"] = cases
    root = (path.parent / register["data_root"]).resolve(strict=True)
    file_index = register.get("file_index")
    index = _json(_verify(root, file_index)) if file_index is not None else {}
    policy_file = register.get("policy_file")
    policy_hash = _hash(_verify(path.parent, policy_file))[1] if policy_file is not None else None
    return register, root, index, _hash(path)[1], policy_hash


def _verify_index(root: Path, index: dict[str, Any]) -> int:
    raw_listed: object = index.get("files", {})
    if not isinstance(raw_listed, dict):
        message = "corrupt original native FILE_INDEX"
        raise RegressionError(message)
    entries = cast("dict[object, object]", raw_listed)
    for name, raw_fingerprint in entries.items():
        if not isinstance(name, str) or not isinstance(raw_fingerprint, dict):
            message = "invalid file index entry"
            raise RegressionError(message)
        fingerprint = cast("dict[str, Any]", raw_fingerprint)
        _verify(root, {"path": name, **fingerprint})
    return len(entries)


def _cases(register: dict[str, Any], group: str, single: str | None) -> list[dict[str, Any]]:
    matches = [
        entry for entry in register["cases"] if (entry["case_id"] == single if single else group in entry["sets"])
    ]
    if not matches:
        message = f"no registered case(s) for {single or group}"
        raise RegressionError(message)
    return matches


def _predictions(path: Path) -> dict[tuple[str, str, int], dict[str, str]]:
    found: dict[tuple[str, str, int], dict[str, str]] = {}
    with path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None or tuple(reader.fieldnames) != CSV_COLUMNS:
            message = "candidate CSV has omitted, additional or reordered columns"
            raise RegressionError(message)
        for row in reader:
            key = (row["case_id"], row["native_column_id"], int(row["sample_index"]))
            if key in found:
                message = f"duplicate ordinate in candidate CSV: {key}"
                raise RegressionError(message)
            _scalar(row["python_discharge_m3_s"])
            found[key] = row
    return found


def _compare(
    case: dict[str, Any],
    columns: list[str],
    rows: list[list[str]],
    supplied: dict[tuple[str, str, int], dict[str, str]],
    engine: str,
) -> dict[str, Any]:
    expected = {(case["case_id"], point["native_column_id"], i) for point in case["sites"] for i in range(len(rows))}
    observed = {key for key in supplied if key[0] == case["case_id"]}
    additional = sorted(observed - expected)
    if additional:
        return {
            "classification": "invalid",
            "reason": f"unmapped extra candidate output: {additional[:3]}",
            "mismatches": [],
        }
    if expected - observed:
        return {
            "classification": "incomplete",
            "reason": f"{len(expected - observed)} expected ordinates unavailable",
            "mismatches": [],
        }
    differences: list[dict[str, str | int]] = []
    for point in case["sites"]:
        column = point["native_column_id"]
        position = columns.index(column)
        for i, row in enumerate(rows):
            actual = supplied[(case["case_id"], column, i)]
            tokens = (row[0], row[1], row[position])
            retained = (actual["raw_native_increment"], actual["raw_native_time"], actual["native_discharge_token"])
            if retained != tokens or actual["model_print_id"] != point["model_print_id"]:
                return {
                    "classification": "invalid",
                    "reason": f"original clock/value/site identity changed: {column}[{i}]",
                    "mismatches": [],
                }
            target, prediction = _scalar(row[position]), _scalar(actual["python_discharge_m3_s"])
            if case["reference_kind"] == "independent_analytic":
                allowance = Decimal("0.000001") + abs(target) * Decimal("0.000001")
            elif engine == "python-cmd":
                allowance = Decimal(1).scaleb(int(target.as_tuple().exponent)) / 2
            else:
                return {
                    "classification": "incomplete",
                    "reason": "independent engineering accuracy and balance budget unavailable for this native reference",
                    "mismatches": [],
                }
            if abs(prediction - target) > allowance:
                differences.append(
                    {
                        "site": column,
                        "index": i,
                        "expected_token": row[position],
                        "observed": str(prediction),
                        "signed_error": str(prediction - target),
                        "frozen_allowance": str(allowance),
                    }
                )
    return {
        "classification": "fail" if differences else "pass",
        "reason": None,
        "checked_ordinates": len(expected),
        "mismatches": differences,
    }


def _run(
    path: Path,
    *,
    group: str,
    case_id: str | None,
    csv_path: Path | None,
    engine: str,
    full_index: bool,
    implementation: str | None,
    wheel: Path | None,
) -> tuple[dict[str, Any], bool]:
    register, root, index, register_sha, policy_sha = _load_register(path)
    selected = _cases(register, group, case_id)
    checked = _verify_index(root, index) if full_index else 0
    candidates = _predictions(csv_path) if csv_path is not None else {}
    all_case_ids = {entry["case_id"] for entry in register["cases"]}
    if {key[0] for key in candidates} - all_case_ids:
        message = "candidate CSV includes undeclared case IDs"
        raise RegressionError(message)
    if csv_path is not None and not implementation:
        message = "candidate comparison requires exact --implementation revision"
        raise RegressionError(message)
    if implementation is not None and re.fullmatch(r"[0-9a-f]{40}", implementation) is None:
        message = "implementation revision must be a complete 40-character Git SHA"
        raise RegressionError(message)
    results: list[dict[str, Any]] = []
    for item in selected:
        case: dict[str, Any] = {"case_id": item["case_id"], "sets": item["sets"]}
        try:
            for source in item["files"]:
                _verify(root, source)
            if item["coverage"] != "selected":
                case.update(classification="incomplete", reason=item["reason"], mismatches=[])
            else:
                columns, rows = _reference(root, item)
                if csv_path is not None:
                    case.update(_compare(item, columns, rows, candidates, engine))
                else:
                    case.update(
                        classification="verified",
                        reason="original evidence only; candidate not executed",
                        mismatches=[],
                    )
                case["reference_rows"], case["reference_sites"] = len(rows), len(columns) - 2
        except (OSError, KeyError, IndexError, TypeError, ValueError) as exc:
            status = "incomplete" if isinstance(exc, FileNotFoundError) else "invalid"
            case.update(classification=status, reason=str(exc), mismatches=[])
        results.append(case)
    counts = Counter(case["classification"] for case in results)
    complete = all(case["classification"] == ("pass" if csv_path is not None else "verified") for case in results)
    spec = importlib.util.find_spec("runoff_routing")
    outcome = {
        "format": RESULT_FORMAT,
        "schema_version": VERSION,
        "dataset_id": register["dataset_id"],
        "register_sha256": register_sha,
        "policy_sha256": policy_sha,
        "policy_id": register["policies"][engine],
        "engine_id": engine,
        "implementation_revision": implementation,
        "implementation_revision_verified": False,
        "wheel_sha256": _hash(wheel)[1] if wheel is not None else None,
        "wheel_import_match_verified": False,
        "comparison_module_sha256": _hash(Path(__file__))[1],
        "run_kind": "candidate_comparison" if csv_path is not None else "reference_preflight",
        "actual_package_import_origin": spec.origin if spec is not None else None,
        "candidate_csv_sha256": _hash(csv_path)[1] if csv_path is not None else None,
        "python": sys.version,
        "platform": platform.platform(),
        "case_count": len(selected),
        "index_files_verified": checked,
        "counts": dict(counts),
        "complete": complete,
        "cases": results,
    }
    return outcome, complete


def main(argv: list[str] | None = None) -> int:
    """Run source-only preflight or compare externally calculated outputs; no RORB process."""
    parser = argparse.ArgumentParser(description="Read-only offline regression dataset verification.")
    parser.add_argument("command", choices=("preflight", "compare", "diagnose"))
    parser.add_argument("register", type=Path)
    parser.add_argument("--set", default="cmd-selected")
    parser.add_argument("--case")
    parser.add_argument("--csv", type=Path)
    parser.add_argument("--engine", choices=("python", "python-cmd"), default="python-cmd")
    parser.add_argument("--implementation")
    parser.add_argument("--wheel", type=Path)
    parser.add_argument("--full-index", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command != "preflight" and args.csv is None:
            message = "compare/diagnose requires --csv with independently computed candidate ordinates"
            raise RegressionError(message)
        if args.command == "diagnose" and args.case is None:
            message = "diagnose requires one --case"
            raise RegressionError(message)
        result, complete = _run(
            args.register,
            group=args.set,
            case_id=args.case,
            csv_path=args.csv,
            engine=args.engine,
            full_index=args.full_index,
            implementation=args.implementation,
            wheel=args.wheel,
        )
        text = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
        if args.output is not None:
            with args.output.open("x", encoding="utf-8", newline="\n") as file:
                file.write(text)
        print(
            json.dumps(
                {
                    name: result[name]
                    for name in ("dataset_id", "case_count", "counts", "index_files_verified", "complete")
                }
            )
        )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"regression error: {exc}", file=sys.stderr)
        return 2
    return 0 if complete else 1


if __name__ == "__main__":
    sys.exit(main())
