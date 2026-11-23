"""Synthetic controls for the nonexecuting #148 physical-catchment preflight."""

from __future__ import annotations

import importlib.util
import json
from collections.abc import Callable
from decimal import localcontext
from pathlib import Path
from types import ModuleType
from typing import cast

import pytest

ROOT = Path(__file__).parents[1]
TEMPLATE = ROOT / "docs" / "research" / "issue148" / "physical_study_preflight.json"


def _module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "mc_physical_preflight", ROOT / "repo-scripts" / "mc_physical_preflight.py"
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _template() -> dict[str, object]:
    return cast("dict[str, object]", json.loads(TEMPLATE.read_text(encoding="utf-8")))


def _record(payload: dict[str, object]) -> dict[str, object]:
    fn = cast("Callable[[object], dict[str, object]]", _module().assess_protocol)
    return fn(payload)


def _lane(result: dict[str, object], name: str) -> dict[str, object]:
    return cast("dict[str, dict[str, object]]", result["lanes"])[name]


def _source_ready() -> dict[str, object]:
    payload = _template()
    cat = cast("dict[str, object]", payload["catchment"])
    cat.update({"catchment_id": "test_site", "model_sha256": "a" * 64, "features_admitted": True, "site_ids": ["Q1"]})
    sources = cast("dict[str, object]", payload["sources"])
    sources.update(
        {
            "bom_ifd_sha256": "b" * 64,
            "arr_tp_sha256": "c" * 64,
            "loss_sha256": "d" * 64,
            "source_admission": "independently_admitted",
        }
    )
    cast("dict[str, object]", payload["observables"])["durations_minutes"] = [1440]
    return payload


def test_unadmitted_template_fails_closed_in_all_lanes() -> None:
    result = _record(_template())
    assert result["declaration_only"] is True
    assert result["simulation_authorised"] is False
    for lane in cast("dict[str, dict[str, object]]", result["lanes"]).values():
        assert lane["status"] == "blocked"
    missing = cast("list[str]", _lane(result, "restricted_domain_python_pilot")["missing"])
    assert "admitted_ifd_tp_loss_sources" in missing
    assert result["modelled_rainfall_mass"] == "0.49"
    assert result["unmodelled_rainfall_mass"] == "0.51"


def test_source_declarations_only_advance_restricted_pilot_to_external_review() -> None:
    result = _record(_source_ready())
    assert _lane(result, "restricted_domain_python_pilot")["status"] == "external_evidence_review_required"
    assert _lane(result, "full_annual_design_flood")["status"] == "blocked"
    assert _lane(result, "native_independent_population_comparison")["status"] == "blocked"
    assert result["simulation_authorised"] is False


def test_native_lanes_distinguish_independent_population_from_exact_replay() -> None:
    payload = _source_ready()
    native = cast("dict[str, object]", payload["native"])
    for key in ("method_profile", "reader", "probability_weights"):
        native[key] = "independently_admitted"
    cast("dict[str, object]", payload["replication"])["native_stream_independence"] = "independently_audited"
    result = _record(payload)
    assert _lane(result, "native_independent_population_comparison")["status"] == "external_evidence_review_required"
    assert "exact_native_effective_inputs" in cast("list[str]", _lane(result, "native_exact_event_replay")["missing"])
    native["effective_inputs"] = "independently_admitted"
    assert _lane(_record(payload), "native_exact_event_replay")["status"] == "external_evidence_review_required"


def test_joint_stability_and_annual_tail_are_separate() -> None:
    payload = _source_ready()
    obs = cast("dict[str, object]", payload["observables"])
    obs.update(
        {
            "relative_peak_tolerance": "0.02",
            "absolute_peak_tolerance_m3s": "0.1",
            "joint_error_allocation_sha256": "e" * 64,
            "joint_confidence_level": "0.95",
            "required_whole_run_pass_probability": "0.95",
        }
    )
    reps = cast("dict[str, object]", payload["replication"])
    reps.update(
        {
            "reference_plan_sha256": "f" * 64,
            "confirmation_plan_sha256": "0" * 64,
            "python_stream_independence": "independently_audited",
        }
    )
    result = _record(payload)
    assert _lane(result, "restricted_domain_single_1000_stability")["status"] == "external_evidence_review_required"
    assert _lane(result, "full_annual_design_flood")["status"] == "blocked"
    pop = cast("dict[str, object]", payload["population"])
    pop["tail_policy"] = "independently_admitted"
    pop["flood_population_interpretation"] = "independently_admitted"
    accepted = _record(payload)
    assert _lane(accepted, "full_annual_design_flood")["status"] == "external_evidence_review_required"
    assert accepted["simulation_authorised"] is False


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-0.5", "1.2", "1_2"])
def test_bad_probability_rejected(value: str) -> None:
    payload = _template()
    cast("dict[str, object]", payload["population"])["rainfall_aep_lower"] = value
    with pytest.raises(ValueError, match="rainfall"):
        _record(payload)


@pytest.mark.parametrize("value", ["0.48", "0.50", "NaN"])
def test_probability_mass_accounting_rejects_invention(value: str) -> None:
    payload = _template()
    cast("dict[str, object]", payload["population"])["modelled_mass"] = value
    with pytest.raises(ValueError, match=r"modelled_mass|probability interval"):
        _record(payload)


@pytest.mark.parametrize("value", [0, -1, True, 1_000_001])
def test_bounded_pilot_events_are_required(value: int) -> None:
    payload = _template()
    cast("dict[str, object]", payload["replication"])["pilot_max_events"] = value
    with pytest.raises(ValueError, match="pilot_max_events"):
        _record(payload)


def test_unknown_fields_and_duplicate_output_sites_fail_closed() -> None:
    payload = _template()
    payload["unreviewed_scientific_override"] = True
    with pytest.raises(ValueError, match="protocol must contain exactly"):
        _record(payload)
    payload = _template()
    cast("dict[str, object]", payload["catchment"])["site_ids"] = ["Q1", "Q1"]
    with pytest.raises(ValueError, match="duplicates"):
        _record(payload)


def test_bad_source_digest_and_unknown_native_status_fail_closed() -> None:
    payload = _template()
    cast("dict[str, object]", payload["sources"])["bom_ifd_sha256"] = "not-a-hash"
    with pytest.raises(ValueError, match="SHA-256"):
        _record(payload)
    payload = _template()
    cast("dict[str, object]", payload["native"])["reader"] = "native_equal"
    with pytest.raises(ValueError, match=r"native\.reader"):
        _record(payload)


def test_stability_requires_joint_confidence_run_reliability_and_exact_candidate_count() -> None:
    payload = _source_ready()
    obs = cast("dict[str, object]", payload["observables"])
    obs.update(
        {
            "relative_peak_tolerance": "0.02",
            "absolute_peak_tolerance_m3s": "0.1",
            "joint_error_allocation_sha256": "e" * 64,
        }
    )
    reps = cast("dict[str, object]", payload["replication"])
    reps.update(
        {
            "reference_plan_sha256": "f" * 64,
            "confirmation_plan_sha256": "0" * 64,
            "python_stream_independence": "independently_audited",
        }
    )
    missing = cast("list[str]", _lane(_record(payload), "restricted_domain_single_1000_stability")["missing"])
    assert "prespecified_joint_confidence_and_run_reliability" in missing
    obs.update({"joint_confidence_level": "0.95", "required_whole_run_pass_probability": "0.95"})
    reps["production_events_candidate"] = 500
    missing = cast("list[str]", _lane(_record(payload), "restricted_domain_single_1000_stability")["missing"])
    assert missing == ["production_run_candidate_has_1000_events"]


@pytest.mark.parametrize("name", ["joint_confidence_level", "required_whole_run_pass_probability"])
def test_invalid_statistical_thresholds_rejected(name: str) -> None:
    payload = _template()
    cast("dict[str, object]", payload["observables"])[name] = "1.0"
    with pytest.raises(ValueError, match=name):
        _record(payload)


def test_reference_confirmation_plan_hashes_must_be_distinct() -> None:
    payload = _template()
    replications = cast("dict[str, object]", payload["replication"])
    replications["reference_plan_sha256"] = "a" * 64
    replications["confirmation_plan_sha256"] = "a" * 64
    with pytest.raises(ValueError, match="distinct identities"):
        _record(payload)


def test_high_precision_mass_accounting_is_exact_under_changed_context() -> None:
    payload = _template()
    cast("dict[str, object]", payload["population"])["rainfall_aep_lower"] = "0.0100000000000000000000000000001"
    with pytest.raises(ValueError, match="probability interval"):
        _record(payload)
    with localcontext() as ctx:
        ctx.prec = 3
        valid = _record(_template())
    assert valid["modelled_rainfall_mass"] == "0.49"


@pytest.mark.parametrize("token", ["1E-9999999", "0." + "1" * 200])
def test_unbounded_decimal_inputs_are_rejected(token: str) -> None:
    payload = _template()
    cast("dict[str, object]", payload["population"])["rainfall_aep_lower"] = token
    with pytest.raises(ValueError, match="precision"):
        _record(payload)


def test_cli_rejects_duplicate_json_members(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    fn = cast("Callable[[list[str]], int]", _module().main)
    source = TEMPLATE.read_text(encoding="utf-8")
    altered = source.replace(
        '"source_admission": "pending"',
        '"source_admission": "pending", "source_admission": "independently_admitted"',
    )
    assert altered != source
    target = tmp_path / "duplicate.json"
    target.write_text(altered, encoding="utf-8")
    assert fn([str(target)]) == 2
    assert "duplicate JSON member" in str(json.loads(capsys.readouterr().out)["reason"])


def test_cli_prints_blocked_without_writing_or_launching(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    fn = cast("Callable[[list[str]], int]", _module().main)
    target = tmp_path / "study.json"
    target.write_text(TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")
    assert fn([str(target)]) == 1
    result = json.loads(capsys.readouterr().out)
    assert result["simulation_authorised"] is False
    assert result["lanes"]["restricted_domain_python_pilot"]["status"] == "blocked"
    assert sorted(path.name for path in tmp_path.iterdir()) == ["study.json"]


def test_cli_rejects_oversized_or_malformed_input(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    fn = cast("Callable[[list[str]], int]", _module().main)
    candidate = tmp_path / "bad.json"
    candidate.write_text("{" + " " * 263_000, encoding="utf-8")
    assert fn([str(candidate)]) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "invalid_protocol"
