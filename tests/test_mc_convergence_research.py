"""Small offline analytical checks for the optional issue #148 research harness."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest


def _research() -> ModuleType:
    path = Path(__file__).parents[1] / "repo-scripts" / "mc_convergence_research.py"
    if not path.exists():  # For local independent authoring outside the repository.
        path = Path(__file__).with_name("mc_convergence_research.py")
    spec = importlib.util.spec_from_file_location("mc_convergence_research", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_exact_integral_and_positive_atom() -> None:
    mc = _research()
    response = mc.Response(1.0, 0.0, 0.0, 1.0)
    assert mc.exact_survival(response, 0.0) == pytest.approx(0.5)
    assert mc.exact_survival(response, 0.5) == pytest.approx(0.125)
    assert mc.exact_quantile(response, 0.125) == pytest.approx(0.5, abs=1e-12)
    assert mc.exact_quantile(response, 0.6) == 0.0
    assert mc.exact_survival(response, 0.5, lower_u=0.0, upper_u=0.4) == 0.0


def test_weighted_inverse_and_missing_probability() -> None:
    mc = _research()
    peaks = [(0.0, 0.6), (10.0, 0.4)]
    assert mc.weighted_quantile(peaks, 0.1) == 10
    assert mc.weighted_quantile(peaks, 0.5) == 0
    assert mc.weighted_quantile(list(reversed(peaks)), 0.1) == 10
    with pytest.raises(ValueError, match="missing probability mass"):
        mc.weighted_quantile([(0.0, 0.6), (10.0, 0.3)], 0.1)
    with pytest.raises(ValueError, match="failed"):
        mc.weighted_quantile([(float("nan"), 1.0)], 0.1)


def test_exact_one_sided_lower_confidence_and_independent_reps() -> None:
    mc = _research()
    assert mc.lower_confidence_bound(0, 30) == 0.0
    assert mc.lower_confidence_bound(30, 30) == pytest.approx(0.05 ** (1 / 30), abs=1e-12)
    assert mc.lower_confidence_bound(30, 30) < 0.95
    assert mc.lower_confidence_bound(100, 100) > 0.95
    assert mc.upper_confidence_bound(2, 100) < 0.1
    assert mc.upper_confidence_bound(100, 100) == 1.0
    assert mc.sd_bootstrap_interval([1.0, 2.0, 5.0, 7.0], "fixed") == mc.sd_bootstrap_interval(
        [1.0, 2.0, 5.0, 7.0], "fixed"
    )
    assert 0.0 < mc.lower_confidence_bound(50, 100) < 0.5


def test_missing_tail_bounds_do_not_normalise_or_invent_upper_quantiles() -> None:
    mc = _research()
    response = mc.RESPONSES["near_tie"]["short"]
    lower, upper = mc.endpoint_quantile_bounds(response, 0.05)
    assert upper is not None
    truth = mc.exact_quantile(response, 0.05)
    assert lower <= truth <= upper
    _, sparse_upper = mc.endpoint_quantile_bounds(response, 0.02)
    assert sparse_upper is None


def test_complete_unequal_strata_and_exact_finite_tp() -> None:
    mc = _research()
    edges = mc.strata_edges(5)
    assert edges[0] == 0
    assert edges[-1] == 1
    assert edges[1] - edges[0] != pytest.approx(edges[3] - edges[2])
    for method in ("random_tp", "paired_tp"):
        peaks = mc.trial_peaks(root=9, stage="test", replication=0, duration="short", strata=5, n=4,
                                tp_method=method)
        assert set(peaks) == {"zero_atom", "near_tie"}
        assert all(len(values) == 20 for values in peaks.values())
        for values in peaks.values():
            assert sum(weight for _, weight in values) == pytest.approx(1.0)
    first = mc.trial_peaks(root=9, stage="test", replication=0, duration="short", strata=5, n=4,
                            tp_method="random_tp")
    repeat = mc.trial_peaks(root=9, stage="test", replication=0, duration="short", strata=5, n=4,
                             tp_method="random_tp")
    changed = mc.trial_peaks(root=9, stage="test", replication=1, duration="short", strata=5, n=4,
                              tp_method="random_tp")
    assert first == repeat
    assert first != changed


def test_envelope_uses_each_duration_and_all_sites() -> None:
    mc = _research()
    rows = mc.one_trial(root=7, stage="test", replication=0, strata=5, n=4,
                        tp_method="random_tp", quantile_method="rank")
    assert len(rows) == 2 * 4 * 3
    for site in mc.RESPONSES:
        for aep in mc.AEPS:
            subset = {row["duration"]: row for row in rows if row["site"] == site and row["aep"] == aep}
            assert subset["envelope"]["estimate"] == max(subset[d]["estimate"] for d in mc.DURATIONS)
            assert subset["envelope"]["exact"] == max(subset[d]["exact"] for d in mc.DURATIONS)
            assert subset["envelope"]["critical_duration"] in mc.DURATIONS
            assert subset["envelope"]["zero_probability"] is None


def test_smoke_writes_immutable_replay_receipts(tmp_path: Path) -> None:
    mc = _research()
    output = tmp_path / "smoke"
    mc.run("smoke", output, root=123, replications=2, max_evaluations=80, max_wall_seconds=30, opt_in=False)
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
    assert manifest["total_evaluations"] == 80
    assert (output / "endpoint_sensitivity.json").exists()
    assert len(summary["metrics"]) == 24
    assert summary["whole_run"][0]["replications"] == 2
    with pytest.raises(FileExistsError):
        mc.run("smoke", output, root=123, replications=2, max_evaluations=80, max_wall_seconds=30, opt_in=False)
    with pytest.raises(ValueError, match="require --opt-in"):
        mc.run("pilot", tmp_path / "pilot", root=123, replications=2, max_evaluations=77000,
               max_wall_seconds=30, opt_in=False)
    with pytest.raises(ValueError, match="exceeds"):
        mc.run("smoke", tmp_path / "over-budget", root=123, replications=2, max_evaluations=79,
               max_wall_seconds=30, opt_in=False)
