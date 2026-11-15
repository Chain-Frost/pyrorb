"""Pure CMD-referenced percentage and near-zero metric controls."""

from __future__ import annotations

import math

import pytest

from runoff_routing.cmd_deviation import assess_cmd_deviation


def test_peak_hydrograph_and_physical_volume_use_cmd_as_denominator() -> None:
    result = assess_cmd_deviation(
        (0.0, 1.1, 2.2, 1.1, 0.0),
        (0.0, 1.0, 2.0, 1.0, 0.0),
        timestep_hours=0.5,
    )
    assert result.sample_count == 5
    assert result.peak_difference_pct == pytest.approx(10.0)
    assert result.max_absolute_ordinate_difference_m3_s == pytest.approx(0.2)
    assert result.max_absolute_ordinate_difference_pct_cmd_peak == pytest.approx(10.0)
    assert result.rms_ordinate_difference_pct_cmd_peak == pytest.approx(math.sqrt(0.06 / 5) / 2 * 100)
    assert result.cmd_trapezoidal_volume_m3 == pytest.approx(7200.0)
    assert result.python_trapezoidal_volume_m3 == pytest.approx(7920.0)
    assert result.volume_difference_pct == pytest.approx(10.0)
    assert result.peak_index_offset == 0


def test_signed_peak_volume_and_peak_index_offset() -> None:
    comparison = assess_cmd_deviation((0.0, 1.0, 0.5), (0.0, 2.0, 1.0), timestep_hours=0.25)
    assert comparison.peak_difference_m3_s == -1.0
    assert comparison.peak_difference_pct == -50.0
    assert comparison.volume_difference_pct == pytest.approx(-50.0)
    assert comparison.peak_index_offset == 0
    shifted = assess_cmd_deviation((0.0, 1.0, 3.0), (0.0, 2.0, 1.0), timestep_hours=0.25)
    assert shifted.peak_index_offset == 1
    assert shifted.peak_difference_pct == pytest.approx(50.0)


def test_zero_cmd_reference_has_undefined_percent_not_zero_or_infinity() -> None:
    zero = assess_cmd_deviation((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), timestep_hours=1.0)
    assert zero.peak_difference_pct is None
    assert zero.max_absolute_ordinate_difference_pct_cmd_peak is None
    assert zero.rms_ordinate_difference_pct_cmd_peak is None
    assert zero.volume_difference_pct is None
    nonzero = assess_cmd_deviation((0.0, 2.0, 0.0), (0.0, 0.0, 0.0), timestep_hours=1.0)
    assert nonzero.peak_difference_pct is None
    assert nonzero.max_absolute_ordinate_difference_m3_s == 2.0
    assert nonzero.volume_difference_m3 == pytest.approx(7200.0)


def test_tiny_but_nonzero_reference_does_not_use_an_arbitrary_ordinate_floor() -> None:
    small = assess_cmd_deviation((0.0, 2e-18, 0.0), (0.0, 1e-18, 0.0), timestep_hours=0.5)
    assert small.peak_difference_pct == pytest.approx(100.0)
    assert small.max_absolute_ordinate_difference_pct_cmd_peak == pytest.approx(100.0)


@pytest.mark.parametrize(
    ("python", "cmd", "hours"),
    [
        ((0.0,), (0.0,), 1.0),
        ((0.0, 1.0), (0.0,), 1.0),
        ((0.0, -1.0), (0.0, 1.0), 1.0),
        ((0.0, math.inf), (0.0, 1.0), 1.0),
        ((0.0, 1.0), (0.0, 1.0), 0.0),
    ],
)
def test_rejects_incomplete_invalid_or_misaligned_inputs(
    python: tuple[float, ...], cmd: tuple[float, ...], hours: float
) -> None:
    with pytest.raises(ValueError, match="CMD comparison|CMD timestep"):
        assess_cmd_deviation(python, cmd, timestep_hours=hours)
