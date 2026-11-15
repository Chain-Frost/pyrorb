"""Independent #150 sampler controls against the optional #146 public module.

These authored source-free cases check the #145 project policy, not a native
RORBwin default. Until #146 lands in the staging branch, all such checks SKIP.
"""

from __future__ import annotations

import hashlib
import hmac
import importlib
import importlib.util
import json
from collections.abc import Callable
from decimal import Decimal, localcontext
from typing import Any, Protocol, cast

import pytest


class _SamplerAPI(Protocol):
    SamplePlan: Any
    SamplePlanError: type[Exception]
    iter_plan_samples: Callable[..., Any]
    iter_stratum_samples: Callable[..., Any]
    interpolate_ifd_depth: Callable[..., Any]
    inverse_storm_loss: Callable[..., Any]
    select_temporal_pattern: Callable[..., Any]
    validate_sample_records: Callable[..., Any]


def _sampler() -> _SamplerAPI:
    if importlib.util.find_spec("runoff_routing.monte_carlo_plan") is None:
        pytest.skip("#146 sampler not integrated; independent production comparison not run")
    return cast("_SamplerAPI", importlib.import_module("runoff_routing.monte_carlo_plan"))


def _spec() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "policy": {"id": "mc150-independent-law", "version": "1", "status": "provisional"},
        "scenario_id": "synthetic-rainfall-and-loss",
        "duration_min": 60,
        "sources": {
            "ifd": hashlib.sha256(b"original-independent-IFD").hexdigest(),
            "temporal_patterns": hashlib.sha256(b"original-independent-TPs").hexdigest(),
            "initial_loss": hashlib.sha256(b"original-independent-IL").hexdigest(),
        },
        "rng": {
            "algorithm": "hmac-sha256-53-v1",
            "derivation": "canonical-json-domain-separated-v1",
            "root_seed": 27,
        },
        "within_stratum": "uniform_aep_mass_v1",
        "strata": [
            {"id": "rare", "aep_lower": "0.10", "aep_upper": "0.20", "probability_mass": "0.10", "count": 2},
            {"id": "ordinary", "aep_lower": "0.20", "aep_upper": "0.50", "probability_mass": "0.30", "count": 4},
        ],
        "ifd": {
            "source_id": "independently authored two-anchor table",
            "interpolation": "z_linear_depth_v1",
            "points": [
                {"aep": "0.10", "depth_mm": "100"},
                {"aep": "0.50", "depth_mm": "50"},
            ],
        },
        "tp_bins": [
            {
                "id": "rare",
                "aep_lower": "0.10",
                "aep_upper": "0.20",
                "choices": [
                    {"event_id": "0007", "source_order": 7, "probability": "0.25"},
                    {"event_id": "0021", "source_order": 21, "probability": "0.75"},
                ],
            },
            {
                "id": "ordinary",
                "aep_lower": "0.20",
                "aep_upper": "0.50",
                "choices": [{"event_id": "0099", "source_order": 99, "probability": "1"}],
            },
        ],
        "loss": {
            "mode": "empirical_scaled_storm_il",
            "source_id": "authored-example-only-not-RORBwin",
            "median_storm_il_mm": "20",
            "cdf_quantiles": [
                {"nonexceedance": "0", "ratio_to_median": "0"},
                {"nonexceedance": "0.5", "ratio_to_median": "1"},
                {"nonexceedance": "1", "ratio_to_median": "2"},
            ],
        },
        "fixed_parameters": [{"name": "kc", "value": "8", "unit": "model"}],
        "arf_policy": "fixed-catchment-one-application-by-execution-owner",
        "preburst_policy": "none-in-this-control",
        "joint_policy": "conditional-TP-on-AEP; independent-storm-IL-for-synthetic-only",
    }


def _expected_uniform(population_id: str, spec: dict[str, Any], stratum: dict[str, Any], purpose: str) -> Decimal:
    """Calculate a reference HMAC vector without calling B's internal RNG."""
    payload: dict[str, object] = {
        "namespace": "python-runoff-routing/mc-sampler",
        "version": 1,
        "population_id": population_id,
        "policy": spec["policy"],
        "sources": spec["sources"],
        "scenario_id": spec["scenario_id"],
        "duration_min": spec["duration_min"],
        "stratum_id": stratum["id"],
        "aep_lower": stratum["aep_lower"],
        "aep_upper": stratum["aep_upper"],
        "index": 0,
        "purpose": purpose,
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    key = (27).to_bytes(8, "big")
    digest = hmac.new(key, canonical.encode("utf-8"), hashlib.sha256).digest()
    first53 = int.from_bytes(digest[:8], "big") >> 11
    with localcontext() as ctx:
        ctx.prec = 60
        return Decimal(2 * first53 + 1) / Decimal(2**54)


def test_independent_sampler_mass_tail_and_normal_coordinate_depth() -> None:
    api = _sampler()
    plan = api.SamplePlan.create(_spec())
    rows = list(api.iter_plan_samples(plan))
    assert len(rows) == 6
    assert [row.event_probability_weight for row in rows] == [Decimal("0.05")] * 2 + [Decimal("0.075")] * 4
    assert sum((row.event_probability_weight for row in rows), Decimal()) == Decimal("0.40")
    domain = plan.to_dict()["domain"]
    assert Decimal(domain["modelled_mass"]) == Decimal("0.4")
    assert Decimal(domain["lower_unmodelled_mass"]) == Decimal("0.1")
    assert Decimal(domain["upper_unmodelled_mass"]) == Decimal("0.5")

    # Published Normal quantiles: Phi^-1(0.7)=0.524400512708, Phi^-1(0.9)=1.281551565545.
    # Linear in rainfall AEP would instead produce 75 mm (not the adopted v1 choice).
    z_linear = api.interpolate_ifd_depth(plan, Decimal("0.30"))
    assert abs(z_linear - Decimal("70.4595947134283")) < Decimal("0.0000001")
    assert abs(z_linear - Decimal(75)) > Decimal(4)
    with pytest.raises(api.SamplePlanError):
        api.interpolate_ifd_depth(plan, Decimal("0.01"))

    for row in rows[:2]:
        assert Decimal("0.10") < row.aep_fraction < Decimal("0.20")
        assert row.tp_event_id in {"0007", "0021"}
        assert row.tp_source_order in {7, 21}
    for row in rows[2:]:
        assert Decimal("0.20") < row.aep_fraction < Decimal("0.50")
        assert row.tp_event_id == "0099"
        assert row.tp_source_order == 99


def test_independent_loss_inverse_and_tp_eligibility_edges() -> None:
    api = _sampler()
    plan = api.SamplePlan.create(_spec())
    assert api.inverse_storm_loss(plan, Decimal(0)) == (Decimal(0), Decimal(0))
    assert api.inverse_storm_loss(plan, Decimal("0.5")) == (Decimal(1), Decimal(20))
    assert api.inverse_storm_loss(plan, Decimal("0.75")) == (Decimal("1.5"), Decimal(30))
    assert api.select_temporal_pattern(plan, Decimal("0.19"), Decimal("0.2499")) == ("rare", "0007", 7)
    assert api.select_temporal_pattern(plan, Decimal("0.19"), Decimal("0.25")) == ("rare", "0021", 21)
    assert api.select_temporal_pattern(plan, Decimal("0.20"), Decimal(0)) == ("ordinary", "0099", 99)
    with pytest.raises(api.SamplePlanError):
        api.select_temporal_pattern(plan, Decimal("0.75"), Decimal("0.5"))


def test_independent_hmac_stream_and_immutable_extension() -> None:
    api = _sampler()
    spec = _spec()
    plan = api.SamplePlan.create(spec)
    first = list(api.iter_plan_samples(plan))
    stratum = spec["strata"][0]
    rainfall_uniform = _expected_uniform(plan.population_id, spec, stratum, "rainfall")
    tp_uniform = _expected_uniform(plan.population_id, spec, stratum, "tp")
    loss_uniform = _expected_uniform(plan.population_id, spec, stratum, "loss")
    with localcontext() as ctx:
        ctx.prec = 60
        assert first[0].aep_fraction == Decimal("0.10") + Decimal("0.10") * rainfall_uniform
    assert first[0].tp_uniform == tp_uniform
    assert first[0].loss_uniform == loss_uniform

    extended = plan.extend({"rare": 4})
    later = list(api.iter_plan_samples(extended))
    by_id = {row.sample_id: row for row in later}
    assert plan.population_id == extended.population_id
    assert plan.plan_id != extended.plan_id
    assert len(later) == 8
    for original in first:
        updated = by_id[original.sample_id]
        assert updated.aep_fraction == original.aep_fraction
        assert updated.gross_ifd_depth_mm == original.gross_ifd_depth_mm
        assert updated.tp_event_id == original.tp_event_id
        assert updated.storm_initial_loss_mm == original.storm_initial_loss_mm
        if original.stratum_id == "rare":
            assert updated.event_probability_weight == original.event_probability_weight / 2
        else:
            assert updated.event_probability_weight == original.event_probability_weight
    with pytest.raises(api.SamplePlanError):
        api.validate_sample_records(extended, first)
    api.validate_sample_records(extended, later)
