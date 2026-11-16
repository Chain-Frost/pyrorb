"""ARR Book 2 v4.2 / Data Hub 2026v1 ARF version and input-boundary regressions.

Official reference: ARR Book 2 v4.2, Chapter 4, Table 2.4.2.
Fixtures are authored synthetic inputs, not real rainfall or native RORB evidence.
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from pathlib import Path
from typing import Any, cast

import pytest

from runoff_routing.arr_arf import (
    ARF_POLICY_VERSION,
    apply_arr2019_arf_to_bom_storm,
    calculate_arr2019_arf,
    published_coefficients,
)
from runoff_routing.arr_data import ARRFormatError
from runoff_routing.arr_import import parse_arr_json
from runoff_routing.arr_patterns import Pattern, PatternSet, parse_pattern_csv
from runoff_routing.arr_storm import storm_from_arr_2026

ARR2026_SYNTHETIC = Path(__file__).absolute().parent / "fixtures" / "arr" / "2026v1-minimal.json"

# Source: official ARR Book 2 v4.2, Table 2.4.2. Intentionally independent
# of arr_arf._PUBLISHED_PARAMETERS to catch coefficient substitutions.
V42_BOOK2_COEFFICIENT_ROWS: tuple[tuple[str, str], ...] = (
    ("East Coast North", "0.327 0.241 0.448 0.36 0.00096 0.48 -0.21 0.012 -0.0013"),
    ("Semi-arid Inland Queensland", "0.159 0.283 0.25 0.308 7.3E-07 1 0.039 0 0"),
    ("Tasmania", "0.0605 0.347 0.2 0.283 0.00076 0.347 0.0877 0.012 -0.00033"),
    ("South-West Western Australia", "0.183 0.259 0.271 0.33 3.85E-06 0.41 0.55 0.00817 -0.00045"),
    ("Central New South Wales", "0.265 0.241 0.505 0.321 0.00056 0.414 -0.021 0.015 -0.00033"),
    ("South-East Coast", "0.06 0.361 0 0.317 8.11E-05 0.651 0 0 0"),
    ("Southern Semi-arid", "0.254 0.247 0.403 0.351 0.0013 0.302 0.058 0 0"),
    ("Southern Temperate", "0.158 0.276 0.372 0.315 0.000141 0.41 0.15 0.01 -0.0027"),
    ("Northern Coastal", "0.326 0.223 0.442 0.323 0.0013 0.58 -0.374 0.013 -0.0015"),
    ("Inland Arid", "0.297 0.234 0.449 0.344 0.00142 0.216 0.129 0 0"),
)


@pytest.mark.parametrize(("region", "reference_values"), V42_BOOK2_COEFFICIENT_ROWS)
def test_v42_published_arf_table_matches_existing_versioned_policy(region: str, reference_values: str) -> None:
    coefficients = published_coefficients(region)
    assert coefficients.values == tuple(Decimal(token) for token in reference_values.split())
    assert len(coefficients.values) == 9
    assert coefficients.origin == "arr2019_book2_table_2_4_2"
    assert coefficients.source_sha256 is None


@pytest.mark.parametrize(
    ("area", "duration", "aep", "expected_operation"),
    [
        ("1", 1440, "1", "SMALL_AREA_UNITY"),
        ("5", 1080, "5", "SMALL_AREA_INTERPOLATION_EQ_2_4_4"),
        ("10", 720, "50", "SHORT_DURATION_EQ_2_4_1"),
        ("100", 1080, "2", "DURATION_LINEAR_INTERPOLATION_EQ_2_4_3"),
        ("100", 1440, "1", "LONG_DURATION_EQ_2_4_2"),
        ("100", 10080, "5", "LONG_DURATION_EQ_2_4_2"),
    ],
)
def test_v42_arfs_still_use_existing_method_steps(area: str, duration: int, aep: str, expected_operation: str) -> None:
    result = calculate_arr2019_arf(
        catchment_area_km2=Decimal(area),
        duration_min=duration,
        aep_percent=Decimal(aep),
        coefficients=published_coefficients("South-West Western Australia"),
    )
    assert result.policy_version == ARF_POLICY_VERSION
    assert expected_operation in result.method_steps
    assert Decimal(0) <= result.factor <= Decimal(1)


def _point_patterns() -> tuple[PatternSet, Pattern]:
    # Local source parse is deliberate; pattern source identity is not an ARF parameter.
    pattern_set = parse_pattern_csv(
        b"EventID,Duration,TimeStep,Region,AEP,Increments\n0900,60,30,SYN,rare,25,75\n",
        kind="point",
    )
    return (pattern_set, pattern_set.patterns[0])


@pytest.mark.parametrize(
    ("baseline", "expected_depth"),
    [
        ("current_2030", Decimal("70.000")),
        ("historical_1961_1990", Decimal("60.0")),
        ("native", Decimal("60.0")),
    ],
)
def test_2026_recifd_baselines_are_explicit_unadjusted_by_arf(baseline: str, expected_depth: Decimal) -> None:
    document = parse_arr_json(ARR2026_SYNTHETIC.read_bytes())
    dataset = next(table for table in document.ifd_datasets if table.baseline == baseline)
    patterns, pattern = _point_patterns()
    event = storm_from_arr_2026(document, dataset, Decimal(1), patterns, pattern)
    assert event.total_mm == expected_depth
    assert event.source_label == dataset.name
    assert event.source_sha256 == document.source.sha256
    assert "NO_ARF_NO_CLIMATE_ADJUSTMENT_NO_LOSSES_NO_PREBURST" in event.operations
    assert dataset.climate_policy == "AS_EXPORTED_NO_FURTHER_UPLIFT"


def test_2026_arf_lookup_and_outlet_are_not_an_implicit_method_selection() -> None:
    original = cast("dict[str, Any]", json.loads(ARR2026_SYNTHETIC.read_text(encoding="utf-8")))
    location = cast("dict[str, Any]", original["input_data"])
    location.update({"Outlet Latitude": -30.125, "Outlet Longitude": 150.125})
    layers = cast("dict[str, Any]", original["layers"])
    # The field spelling follows the witnessed public 2026v1 API export; this
    # unparsed layer must not be silently promoted to an admitted method.
    layers["ARFParams"] = {
        "Zone": "East Coast North",
        "a": "0.327",
        "b": "0.241",
        "c": "0.448",
        "d": "0.36",
        "e": "0.00096",
        "f": "0.48",
        "g": "-0.21",
        "h": "0.012",
        "i": "-0.0013",
    }
    layers["CCAdjIFDDatasets"] = {"unreviewed_2026_example": "not a usable IFD table"}
    raw = json.dumps(original).encode("utf-8")
    document = parse_arr_json(raw)

    assert document.source.datahub_version == "2026v1"
    assert document.source.sha256 == hashlib.sha256(raw).hexdigest()
    assert document.location.latitude == Decimal("-30.000")
    assert document.location.longitude == Decimal("150.000")
    assert document.location.outlet_latitude == Decimal("-30.125")
    assert document.location.outlet_longitude == Decimal("150.125")
    assert document.legacy_arf is None
    assert "ARFParams" in document.unprocessed_layers
    assert "CCAdjIFDDatasets" in document.unprocessed_layers

    current = next(table for table in document.ifd_datasets if table.baseline == "current_2030")
    assert current.release_year is None  # No provider/release-year assumption from JSON.
    patterns, pattern = _point_patterns()
    event = storm_from_arr_2026(document, current, Decimal(1), patterns, pattern)
    assert event.total_mm == Decimal("70.000")
    assert event.increments_mm == (Decimal("17.500"), Decimal("52.500"))

    # The old BoM-specific ARF applicator cannot silently reinterpret a Data Hub
    # current/historical/native IFD or accidentally add another ARF/climate step.
    arf = calculate_arr2019_arf(catchment_area_km2=Decimal(100), duration_min=60, aep_percent=Decimal(1))
    with pytest.raises(ARRFormatError, match="unadjusted gross BoM source"):
        apply_arr2019_arf_to_bom_storm(event, arf)
