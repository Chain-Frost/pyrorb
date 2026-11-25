"""Canonical reader package consumption; no native RORB execution."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from decimal import Decimal
from importlib.resources import files
from pathlib import Path

import pytest

from runoff_routing.regression_metrics import bind_report_metrics
from runoff_routing.rorb_documents import RorbSource
from runoff_routing.rorb_out import inspect_output
from runoff_routing.rorb_readers.output_reader import bind_cmd_diagnostic_columns, bind_output_site_columns
from runoff_routing.rorb_readers.reader_types import RorbDocument
from runoff_routing.rorb_readers.readers import read_rorb_bytes, read_rorb_file, read_rorb_table_file
from runoff_routing.rorb_report_views import report_csv, report_json


def _report(increments: str = "1 0.50 0.000\n2 1.00 12.345000\n3 1.50 0.000\n") -> bytes:
    source = (
        " RORBWin Output File\nProgram version 6.44\n"
        "Time increment (hours)= 0.50\nDuration of calculations: 2\n"
        "Hydrograph summary\nSite Description\n01 Calculated hydrograph,\n\n"
        "Inc Time Hyd001\n" + increments + "End of hydrograph\n"
    )
    return source.replace("\n", "\r\n").encode("cp1252")


def test_canonical_reader_package_is_pep561_typed() -> None:
    assert files("runoff_routing").joinpath("py.typed").is_file()


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
        Decimal("0.50"),
        Decimal("1.00"),
        Decimal("1.50"),
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
    assert len(sites) == 1
    assert sites[0].label == "Synthetic outlet"
    assert sites[0].column == "Hyd001"
    assert sites[0].peak is not None
    assert sites[0].peak.token == source.splitlines()[2].split()[-1]
    assert sites[0].peak.line == 3
    assert sites[0].peak.character == source.splitlines()[2].index("1.000") + 1
    assert sites[0].volume is not None
    assert sites[0].volume.token == source.splitlines()[4].split()[-1]

    path.write_bytes(source.replace("Peak discharge,m³/s", "Peak discharge,L/s").encode("utf-8"))
    invalid = RorbSource.read(path)
    changed = inspect_output(invalid)
    assert changed.hydrographs is not None
    with pytest.raises(ValueError, match="unit/scale"):
        bind_report_metrics(invalid, changed.hydrographs)


def test_canonical_bare_table_preserves_exact_values_without_engine_claim(tmp_path: Path) -> None:
    """Bare source inspection never establishes a verified report identity."""
    path = tmp_path / "raw-table.out"
    path.write_bytes(b"Inc Time Hyd001 Hyd002\r\n1 0.00 0.000 0\r\n2 0.50 3.500000 0\r\nEnd\r\n")
    unqualified = read_rorb_file(path)
    assert unqualified.kind == "unsupported"
    raw = read_rorb_table_file(path)
    assert raw.kind == "isolated_hydrograph_table"
    assert raw.status == "partial"
    assert any(d.code == "unverified_table_source" for d in raw.diagnostics)
    section = raw.section("hydrographs_1")
    assert section.valid
    assert section.columns[1:] == ["Inc", "Time", "Hyd001", "Hyd002"]
    assert len(section.rows) == 2
    assert section.increment_origin == 1
    assert [r["Time"] for r in section.source_tokens] == ["0.00", "0.50"]
    assert section.source_decimal(1, "Hyd001") == Decimal("3.500000")
    path.write_bytes(b"Inc Time Hyd001 Hyd002\n1 0 0 0\n2 0.5 nan 0\nEnd\n")
    malformed = read_rorb_table_file(path)
    assert malformed.status == "invalid"
    assert any(d.code == "output_record" for d in malformed.diagnostics)


@pytest.mark.parametrize("original_encoding", ["utf-8", "utf-8-sig"])
def test_missing_report_path_preserves_bom_and_bom_free_utf8_bytes(tmp_path: Path, original_encoding: str) -> None:
    """UTF-8 decoder selection does not imply the original source contained a BOM."""
    path = tmp_path / "original.out"
    raw = _report().decode("cp1252").encode(original_encoding)
    path.write_bytes(raw)
    source = RorbSource.read(path)
    assert source.encoding == "utf-8-sig"
    assert source.size_bytes == len(raw)
    assert source.sha256 == hashlib.sha256(raw).hexdigest()
    path.unlink()
    inspected = inspect_output(source)
    assert inspected.status == "partial"
    assert inspected.hydrographs is not None
    assert inspected.hydrographs.rows[1].raw_time == "1.00"
    assert any(d.code == "source_path_unavailable" for d in inspected.diagnostics)


_CODE11_REPORT_SHA = "abf184be82df77a081799ebe1bfc68b4b37e1ba1eef069298c0203483796aa13"
_CODE11_KINDS = (
    "subarea_upstream_flow",
    "rainfall_excess_flow",
    "reach_downstream_flow",
    "reach_upstream_flow",
    "calculated_flow",
)


def test_cmd_diagnostic_original_legend_and_horizon() -> None:
    """Use the authenticated published report, not a generated native golden."""
    path = Path(__file__).absolute().parent / "fixtures/regression-v1/native-cmd/objects" / f"{_CODE11_REPORT_SHA}.out"
    raw = path.read_bytes()
    assert len(raw) == 32805
    assert hashlib.sha256(raw).hexdigest() == _CODE11_REPORT_SHA
    document = read_rorb_bytes(raw, path=path)
    assert document.original_bytes == raw
    columns = bind_cmd_diagnostic_columns(document)
    assert tuple(item.column for item in columns) == ("Hyd001", "Hyd002", "Hyd003", "Hyd004", "Hyd005")
    assert tuple(item.quantity_kind for item in columns) == _CODE11_KINDS
    assert all(item.units == "m3/s" for item in columns)
    table = document.section("hydrographs_1")
    assert len(table.rows) == 301
    assert table.increment_origin == 1
    assert table.source_tokens[0]["Time"] == "0.50"
    assert table.source_tokens[-1]["Time"] == "150.50"
    peaks = tuple(max(table.source_decimal(index, item.column) for index in range(len(table.rows))) for item in columns)
    assert peaks == tuple(map(Decimal, ("0.0000", "49.9197", "34.9086", "49.9197", "170.782")))
    assert all(row["Hyd002"] == row["Hyd004"] for row in table.source_tokens)
    # Equal effective parameters and original storm; no new comparator or parity promotion.
    ordinary_sha = "5ee8604dd981b9c9c3a5dc64f2d578590d9e7107174f63f293c464ac38488e99"
    ordinary_raw = path.with_name(f"{ordinary_sha}.out").read_bytes()
    assert len(ordinary_raw) == 19721
    assert hashlib.sha256(ordinary_raw).hexdigest() == ordinary_sha
    ordinary = read_rorb_bytes(ordinary_raw).section("hydrographs_1")
    assert ordinary.valid
    assert len(ordinary.rows) == 301
    assert [(row["Inc"], row["Time"], row["Hyd005"]) for row in table.source_tokens] == [
        (row["Inc"], row["Time"], row["Hyd001"]) for row in ordinary.source_tokens
    ]
    with pytest.raises(ValueError, match="diagnostic columns"):
        bind_output_site_columns(document, allow_unnamed=True)


def _diagnostic_report() -> str:
    return (
        "RORBWin Output File\nProgram version 6.44\n"
        "Time increment (hours)= 0.50\nDuration of calculations: 2\n"
        "Peak discharge,m³/s 0 2\nPeak discharge,m³/s 1 2\nPeak discharge,m³/s 3\n"
        "Hydrograph summary\nSite Description\n"
        "01 Sub-area inflow point, sub-area A - Upstream\n"
        "02 Sub-area inflow point, sub-area A - Rain ex.\n"
        "03 Normal storage, reach no.   0   1 - Downstream\n"
        "04 Normal storage, reach no.   0   1 - Upstream\n"
        "05 Calculated hydrograph,\n\n"
        "Inc Time Hyd001 Hyd002 Hyd003 Hyd004 Hyd005\n"
        "1 0.50 0 0 0 0 0\n2 1.00 0 2 1 2 3\n3 1.50 0 0 0 0 0\n"
    )


def test_cmd_diagnostic_binding_uses_id_not_column_position_and_exports_roles() -> None:
    source = _diagnostic_report().replace("Hyd001 Hyd002 Hyd003 Hyd004 Hyd005", "Hyd005 Hyd003 Hyd002 Hyd001 Hyd004")
    source = source.replace("2 1.00 0 2 1 2 3", "2 1.00 3 1 2 0 2")
    document = read_rorb_bytes(source.encode("utf-8"))
    columns = bind_cmd_diagnostic_columns(document)
    assert tuple(item.column for item in columns) == ("Hyd005", "Hyd003", "Hyd002", "Hyd001", "Hyd004")
    assert tuple(item.quantity_kind for item in columns) == (
        "calculated_flow",
        "reach_downstream_flow",
        "rainfall_excess_flow",
        "subarea_upstream_flow",
        "reach_upstream_flow",
    )
    section = document.section("cmd_diagnostic_sites")
    assert section.valid
    page = json.loads(report_json(document, section=section.name))
    assert page["selection"]["rows"][2]["values"]["quantity_kind"] == "rainfall_excess_flow"
    assert page["selection"]["rows"][2]["values"]["physical_site_verified"] is False
    rows = list(csv.DictReader(io.StringIO(report_csv(document, section.name))))
    assert tuple(item.site_id_token for item in columns) == ("05", "03", "02", "01", "04")
    assert rows[2]["source_token__id_token"] == columns[2].site_id_token
    assert rows[2]["units"] == "m3/s"


@pytest.mark.parametrize(
    ("original", "replacement"),
    [
        ("Hyd001 Hyd002", "Hyd001 Hyd0001"),
        ("02 Sub-area", "01 Sub-area"),
        (" - Rain ex.", " - Unknown"),
        ("m³/s 0 2", "mm 0 2"),
        ("3 1.50 0 0 0 0 0\n", ""),
        ("1 0.50 0 0 0 0 0", "1 0.00 0 0 0 0 0"),
        ("2 1.00 0 2 1 2 3", "2 1.00 0 -2 1 2 3"),
    ],
)
def test_cmd_diagnostic_unsupported_or_ambiguous_layout_never_binds(original: str, replacement: str) -> None:
    source = _diagnostic_report().replace(original, replacement)
    document = read_rorb_bytes(source.encode("utf-8"))
    with pytest.raises(
        ValueError,
        match="structurally valid|Incomplete or invalid|Ambiguous physical|Duplicate hydrograph|Unsupported CMD|"
        "complete one-based|Unsupported negative",
    ):
        bind_cmd_diagnostic_columns(document)
    with pytest.raises(ValueError, match="diagnostic columns"):
        bind_output_site_columns(document, allow_unnamed=True)
    section = document.section("cmd_diagnostic_sites")
    assert not section.valid
    assert not section.rows


@pytest.mark.parametrize("version_line", ["Program version 6.52\n", ""])
def test_cmd_diagnostic_other_native_version_is_not_admitted(version_line: str) -> None:
    source = _diagnostic_report().replace("Program version 6.44\n", version_line)
    document = read_rorb_bytes(source.encode("utf-8"))
    with pytest.raises(ValueError, match=r"6\.44"):
        bind_cmd_diagnostic_columns(document)
    with pytest.raises(ValueError, match="diagnostic columns"):
        bind_output_site_columns(document, allow_unnamed=True)
    assert not document.section("cmd_diagnostic_sites").valid
