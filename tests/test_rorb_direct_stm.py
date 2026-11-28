"""Format-only synthetic direct-depth DESIGN controls for issue #250."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest

from runoff_routing.rorb_codec import (
    FormatProblem,
    original_bytes,
    parse_design_stm,
    parse_direct_design_stm,
    serialize_direct_design_stm,
)
from runoff_routing.rorb_model import DirectDepthStorm

# Independent literal #118-style synthetic fixture. The routing tail is not rainfall.
DIRECT = (
    b"SYNTHETIC DIRECT\n"
    b"DESIGN\n"
    b"C time increment (hours), run increments, bursts, pluviographs, uniform flag\n"
    b"0.5,200,1,1,0,-99\n"
    b"C start and finish increment of the single rainfall burst\n"
    b"0,4\n"
    b"Pluviograph 1\n"
    b"5.25\n0\n2.5\n0\n-99\n"
)


def test_direct_fixture_and_exact_canonical_bytes() -> None:
    parsed = parse_direct_design_stm(DIRECT)
    model = parsed.model
    assert parsed.dialect == "design_direct_depth"
    assert model == DirectDepthStorm(
        "SYNTHETIC DIRECT", Decimal("0.5"), 200, (Decimal("5.25"), Decimal(0), Decimal("2.5"), Decimal(0))
    )
    assert model.start_increment == 0
    assert model.finish_increment == 4
    assert sum(model.interval_depths_mm) == Decimal("7.75")
    assert model.timestep_hours * model.finish_increment == Decimal(2)
    assert [span.source_text for span in parsed.source_map if span.field == "interval_depth_mm"] == [
        "5.25",
        "0",
        "2.5",
        "0",
    ]
    assert serialize_direct_design_stm(model) == DIRECT
    assert original_bytes(parsed) == DIRECT
    with pytest.raises(ValueError, match="cannot represent edits"):
        original_bytes(parsed, current_model=replace(model, title="Changed"))


@pytest.mark.parametrize("depths", [("0", "0", "0"), ("0", "1.25", "5"), ("8", "0", "3")])
def test_direct_zero_and_nonzero_bins_retained(depths: tuple[str, ...]) -> None:
    model = DirectDepthStorm("Rain", Decimal("0.25"), 2000, tuple(Decimal(item) for item in depths))
    parsed = parse_direct_design_stm(serialize_direct_design_stm(model))
    assert parsed.model == model
    assert parsed.model.finish_increment == len(depths)
    assert sum(parsed.model.interval_depths_mm) == sum(model.interval_depths_mm)


def test_original_crlf_and_fortran_tokens() -> None:
    raw = DIRECT.replace(b"0.5,", b"5D-1,").replace(b"5.25\n", b"5.25D0\n").replace(b"\n", b"\r\n")
    parsed = parse_direct_design_stm(raw)
    assert original_bytes(parsed) == raw
    assert parsed.model == parse_direct_design_stm(DIRECT).model


@pytest.mark.parametrize(
    ("before", "after", "status"),
    [
        (b"1,1,0,-99", b"1,1,1,-99", "unsupported"),
        (b"1,1,0,-99", b"1,2,0,-99", "unsupported"),
        (b"1,1,0,-99", b"2,1,0,-99", "unsupported"),
        (b"0,4\n", b"1,5\n", "unsupported"),
        (b"0,4\n", b"0,3\n", "invalid"),
        (b"0,4\n", b"0,5\n", "invalid"),
        (b"0.5,200", b"0.5,3", "invalid"),
        (b"0.5,200", b"0.5,2001", "invalid"),
        (b"0.5,200", b"0,200", "invalid"),
        (b"0.5,200", b"NaN,200", "invalid"),
        (b"5.25\n", b"-0.1\n", "invalid"),
        (b"5.25\n", b"nan\n", "invalid"),
        (b"5.25\n", b"5,,2\n", "invalid"),
        (b"Pluviograph 1", b"Temporal weights", "unsupported"),
        (b"\n-99\n", b"\n", "invalid"),
        (b"\n-99\n", b"\n-99\n2\n-99\n", "invalid"),
        (b"\n-99\n", b"\n-99,0\n", "invalid"),
    ],
)
def test_direct_rejects_invalid_or_uncharacterised_records(before: bytes, after: bytes, status: str) -> None:
    with pytest.raises(FormatProblem) as exc:
        parse_direct_design_stm(DIRECT.replace(before, after))
    assert exc.value.status == status


def test_weighted_parser_does_not_admit_direct_rainfall_as_weights() -> None:
    with pytest.raises(FormatProblem) as exc:
        parse_design_stm(DIRECT)
    assert exc.value.status == "unsupported"


def test_authored_run_length_and_depth_validation() -> None:
    model = parse_direct_design_stm(DIRECT).model
    with pytest.raises(ValueError, match="run length"):
        replace(model, calculation_increments=3)
    with pytest.raises(ValueError, match="interval depth"):
        replace(model, interval_depths_mm=(Decimal("Infinity"),))
    with pytest.raises(ValueError, match="start increment"):
        replace(model, start_increment=1)
    with pytest.raises(ValueError, match="title"):
        replace(model, title="One\u2028Two")
