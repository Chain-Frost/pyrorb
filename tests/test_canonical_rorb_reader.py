"""Cross-repository canonical reader consumption; no native RORB execution."""

from __future__ import annotations

import hashlib
from decimal import Decimal
from pathlib import Path

from ryan_library.functions.RORB.reader_types import RorbDocument
from ryan_library.functions.RORB.readers import read_rorb_bytes, read_rorb_file
from runoff_routing.rorb_documents import RorbSource
from runoff_routing.rorb_out import inspect_output


def _report(increments: str = "1 0.50 0.000\n2 1.00 12.345000\n3 1.50 0.000\n") -> bytes:
    source = (
        " RORBWin Output File\nProgram version 6.44\n"
        "Time increment (hours)= 0.50\nDuration of calculations: 2\n"
        "Hydrograph summary\nSite Description\n01 Calculated hydrograph,\n\n"
        "Inc Time Hyd001\n" + increments + "End of hydrograph\n"
    )
    return source.replace("\n", "\r\n").encode("cp1252")


def test_canonical_reader_preserves_native_bytes_and_one_based_report(tmp_path: Path) -> None:
    path = tmp_path / "cmd.out"
    raw = _report()
    path.write_bytes(raw)
    by_file: RorbDocument = read_rorb_file(path)
    by_bytes = read_rorb_bytes(raw, path=path)
    assert by_file.original_bytes == by_bytes.original_bytes == raw
    assert by_file.size_bytes == len(raw)
    assert by_file.sha256 == by_bytes.sha256 == hashlib.sha256(raw).hexdigest()
    assert by_file.section("hydrographs_1").increment_origin == 1
    assert by_file.section("hydrographs_1").source_decimal(1, "Hyd001") == Decimal("12.345000")
    inspected = inspect_output(RorbSource.read(path))
    assert inspected.hydrographs is not None
    assert inspected.status == "partial"
    assert [row.increment for row in inspected.hydrographs.rows] == [1, 2, 3]
    assert [row.raw_time for row in inspected.hydrographs.rows] == ["0.50", "1.00", "1.50"]
    assert [row.time_hours for row in inspected.hydrographs.rows] == [
        Decimal("0.50"), Decimal("1.00"), Decimal("1.50"),
    ]
    assert inspected.hydrographs.rows[1].values[0] == Decimal("12.345000")
    assert inspected.hydrographs.time_increment_hours == Decimal("0.50")
    assert inspected.hydrographs.reported_duration_increments == 2
    assert any(d.code == "print_identity_unverified" for d in inspected.diagnostics)


def test_canonical_reader_zero_origin_and_malformed_record(tmp_path: Path) -> None:
    output = tmp_path / "zero.out"
    output.write_bytes(_report("0 0.00 0\n1 0.50 12\n2 1.00 0\n"))
    canonical = read_rorb_file(output)
    assert canonical.section("hydrographs_1").increment_origin == 0
    converted = inspect_output(RorbSource.read(output)).hydrographs
    assert converted is not None
    assert [row.increment for row in converted.rows] == [0, 1, 2]
    output.write_bytes(_report("1 0.50 0\n2 1.00 12junk\n3 1.50 0\n"))
    rejected = inspect_output(RorbSource.read(output))
    assert rejected.status == "invalid"
    assert rejected.hydrographs is None
    assert any(d.severity == "error" for d in rejected.diagnostics)


def test_canonical_reader_preserves_fortran_tokens_without_float_roundtrip(tmp_path: Path) -> None:
    output = tmp_path / "exponent.out"
    output.write_bytes(_report("1 0.50 0\n2 1.00 1.234567890123456789D+1\n3 1.50 0\n"))
    canonical = read_rorb_file(output)
    table = canonical.section("hydrographs_1")
    assert table.source_tokens[1]["Hyd001"] == "1.234567890123456789D+1"
    assert table.source_decimal(1, "Hyd001") == Decimal("12.34567890123456789")
    report = inspect_output(RorbSource.read(output)).hydrographs
    assert report is not None
    assert report.rows[1].values[0] == Decimal("12.34567890123456789")


def test_source_replacement_is_rejected_between_inspection_reads(tmp_path: Path) -> None:
    """Source mutation cannot change the verified snapshot the consumer trusts."""
    file_path = tmp_path / "original.out"
    file_path.write_bytes(_report())
    source = RorbSource.read(file_path)
    altered = _report("1 0.50 0\n2 1.00 1\n3 1.50 0\n")
    file_path.write_bytes(altered)
    check = inspect_output(source)
    assert check.status == "invalid"
    assert check.hydrographs is None
    assert any(d.code == "source_changed" for d in check.diagnostics)


def test_canonical_scalar_records_bind_exact_legacy_selectors(tmp_path: Path) -> None:
    """Native scalar policy still requires exact units, ordinals and Hyd order."""
    from runoff_routing.regression_metrics import bind_report_metrics

    source = (
        "Time increment (hours)= 0.50\nDuration of calculations: 1\n"
        "Peak discharge,m³/s 1.000\nTime to peak,h 0.50\nVolume,m³ 1.800D+3\n"
        "Hydrograph summary\nSite Description\n01 Synthetic outlet\n"
        "Inc Time Hyd001\n1 0.50 0.000\n2 1.00 1.000\n"
    )
    path = tmp_path / "scalar.out"
    path.write_bytes(source.encode("utf-8"))
    document = read_rorb_file(path)
    assert document.status == "partial"
    section = document.section("reported_scalars")
    assert [(r["family"], r["unit"], r["token"]) for r in section.rows] == [
        ("Peak discharge", "m³/s", "1.000"),
        ("Time to peak", "h", "0.50"),
        ("Volume", "m³", "1.800D+3"),
    ]
    original = RorbSource.read(path)
    converted = inspect_output(original)
    assert converted.hydrographs is not None
    sites = bind_report_metrics(original, converted.hydrographs)
    assert len(sites) == 1 and sites[0].label == "Synthetic outlet"
    assert sites[0].column == "Hyd001"
    assert sites[0].peak is not None and sites[0].peak.token == "1.000"
    assert sites[0].peak.line == 3
    assert sites[0].peak.character == source.splitlines()[2].index("1.000") + 1
    assert sites[0].volume is not None and sites[0].volume.token == "1.800D+3"

    path.write_bytes(source.replace("Peak discharge,m³/s", "Peak discharge,L/s").encode("utf-8"))
    invalid = RorbSource.read(path)
    changed = inspect_output(invalid)
    assert changed.hydrographs is not None
    from pytest import raises

    with raises(ValueError, match="unit/scale"):
        bind_report_metrics(invalid, changed.hydrographs)
