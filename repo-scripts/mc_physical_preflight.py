"""Read-only Monte Carlo #148 physical-study evidence preflight.

This validates declarations, not their authenticity. It never launches a
routing engine, invokes RORBwin, or approves flood-frequency estimates.
"""

from __future__ import annotations

import argparse
import json
import re
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path
from typing import Never, cast

FORMAT = "pyrorb-mc148-physical-study-preflight/1"
RESULT_FORMAT = "pyrorb-mc148-physical-study-preflight-result/1"
_MAX_BYTES = 256 * 1024
_MAX_EVENTS = 1_000_000
_MAX_DURATION_MIN = 10080
_MAX_DECIMAL_DIGITS = 128
_MAX_DECIMAL_EXPONENT = 32
_MIN_DECIMAL_EXPONENT = -128
_DECIMAL_ACCOUNTING_PREC = 256
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}\Z")


class PreflightError(ValueError):
    """Malformed or internally inconsistent study declaration."""


def _fail(reason: str) -> Never:
    raise PreflightError(reason)


def _object(value: object, keys: set[str], label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        _fail(f"{label} must contain exactly {', '.join(sorted(keys))}")
    record = cast("dict[object, object]", value)
    if set(record) != keys:
        _fail(f"{label} must contain exactly {', '.join(sorted(keys))}")
    return cast("dict[str, object]", record)


def _identifier(value: object, label: str, *, optional: bool = False) -> bool:
    if value is None and optional:
        return False
    if not isinstance(value, str) or _IDENTIFIER.fullmatch(value) is None:
        _fail(f"{label} must be a bounded ASCII identifier")
    return True


def _digest(value: object, label: str) -> bool:
    if value is None:
        return False
    if not isinstance(value, str) or _SHA.fullmatch(value) is None:
        _fail(f"{label} must be a lowercase SHA-256 digest")
    return True


def _choice(value: object, label: str, choices: set[str]) -> str:
    if not isinstance(value, str) or value not in choices:
        _fail(f"{label} must be one of {', '.join(sorted(choices))}")
    return value


def _decimal(value: object, label: str, *, optional: bool = False) -> Decimal | None:
    if value is None and optional:
        return None
    if not isinstance(value, str) or not value or value != value.strip() or "_" in value:
        _fail(f"{label} must be a finite decimal string")
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        message = f"{label} must be a finite decimal string"
        raise PreflightError(message) from exc
    if not number.is_finite():
        _fail(f"{label} must be finite")
    exponent = number.as_tuple().exponent
    if (
        not isinstance(exponent, int)
        or exponent < _MIN_DECIMAL_EXPONENT
        or exponent > _MAX_DECIMAL_EXPONENT
        or len(number.as_tuple().digits) > _MAX_DECIMAL_DIGITS
    ):
        _fail(f"{label} exceeds bounded decimal precision")
    return number


def _positive_int(value: object, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1 or value > _MAX_EVENTS:
        _fail(f"{label} must be a bounded positive integer")
    return value


def _identifiers(value: object, label: str) -> list[str]:
    if not isinstance(value, list):
        _fail(f"{label} must be an array")
    raw = cast("list[object]", value)
    for item in raw:
        _identifier(item, label)
    names = cast("list[str]", raw)
    if len(set(names)) != len(names):
        _fail(f"{label} must not contain duplicates")
    return names


def _durations(value: object) -> list[int]:
    if not isinstance(value, list):
        _fail("durations_minutes must be an array")
    raw = cast("list[object]", value)
    for item in raw:
        if _positive_int(item, "duration") > _MAX_DURATION_MIN:
            _fail("duration exceeds 10080 minutes")
    durations = cast("list[int]", raw)
    if len(set(durations)) != len(durations):
        _fail("durations_minutes must not contain duplicates")
    return durations


def _fractions(value: object) -> list[Decimal]:
    if not isinstance(value, list) or not value:
        _fail("target_flood_aep_fractions must be a nonempty array")
    raw = cast("list[object]", value)
    results: list[Decimal] = []
    for text in raw:
        number = _decimal(text, "target flood AEP")
        if number is None or not 0 < number < 1:
            _fail("target flood AEP must be strictly between zero and one")
        results.append(number)
    if len(set(results)) != len(results):
        _fail("duplicate target flood AEP")
    return results


def _missing(checks: tuple[tuple[bool, str], ...]) -> list[str]:
    return [label for valid, label in checks if not valid]


def _status(blockers: list[str]) -> dict[str, object]:
    return {
        "status": "blocked" if blockers else "external_evidence_review_required",
        "missing": blockers,
    }


def _sections(root: dict[str, object]) -> tuple[dict[str, object], ...]:
    specs = (
        ("catchment", {"catchment_id", "model_sha256", "engine_profile", "features_admitted", "site_ids"}),
        ("sources", {"bom_ifd_sha256", "arr_tp_sha256", "loss_sha256", "source_admission"}),
        (
            "population",
            {
                "rainfall_aep_lower",
                "rainfall_aep_upper",
                "modelled_mass",
                "unmodelled_mass",
                "tail_policy",
                "flood_population_interpretation",
            },
        ),
        (
            "observables",
            {
                "durations_minutes",
                "target_flood_aep_fractions",
                "relative_peak_tolerance",
                "absolute_peak_tolerance_m3s",
                "joint_error_allocation_sha256",
                "joint_confidence_level",
                "required_whole_run_pass_probability",
            },
        ),
        (
            "replication",
            {
                "pilot_max_events",
                "pilot_max_seconds",
                "production_events_candidate",
                "reference_plan_sha256",
                "confirmation_plan_sha256",
                "python_stream_independence",
                "native_stream_independence",
            },
        ),
        ("native", {"method_profile", "reader", "probability_weights", "effective_inputs"}),
    )
    return tuple(_object(root[name], fields, name) for name, fields in specs)


def _population(pop: dict[str, object]) -> tuple[Decimal, Decimal, str, str]:
    lower = _decimal(pop["rainfall_aep_lower"], "rainfall_aep_lower")
    upper = _decimal(pop["rainfall_aep_upper"], "rainfall_aep_upper")
    mass = _decimal(pop["modelled_mass"], "modelled_mass")
    missing = _decimal(pop["unmodelled_mass"], "unmodelled_mass")
    if lower is None or upper is None or mass is None or missing is None:
        _fail("rainfall support and masses are required")
    # The bounded input precision is <= 128 digits/decimal places. A 256-digit
    # local context therefore preserves both interval subtractions exactly.
    with localcontext() as ctx:
        ctx.prec = _DECIMAL_ACCOUNTING_PREC
        if not 0 < lower < upper < 1 or mass != upper - lower or missing != 1 - mass:
            _fail("rainfall probability interval/mass accounting is inconsistent")
    choices = {"unqualified", "independently_admitted"}
    tail = _choice(pop["tail_policy"], "tail_policy", choices)
    flood = _choice(pop["flood_population_interpretation"], "flood_population_interpretation", choices)
    return mass, missing, tail, flood


def _observables(obs: dict[str, object]) -> tuple[bool, bool, bool, bool, bool]:
    durations = _durations(obs["durations_minutes"])
    _fractions(obs["target_flood_aep_fractions"])
    relative = _decimal(obs["relative_peak_tolerance"], "relative_peak_tolerance", optional=True)
    absolute = _decimal(obs["absolute_peak_tolerance_m3s"], "absolute_peak_tolerance_m3s", optional=True)
    if relative is not None and not 0 < relative < 1:
        _fail("relative_peak_tolerance must be within (0,1)")
    if absolute is not None and absolute <= 0:
        _fail("absolute_peak_tolerance_m3s must be positive")
    joint = _digest(obs["joint_error_allocation_sha256"], "joint_error_allocation_sha256")
    confidence = _decimal(obs["joint_confidence_level"], "joint_confidence_level", optional=True)
    reliability = _decimal(
        obs["required_whole_run_pass_probability"], "required_whole_run_pass_probability", optional=True
    )
    if confidence is not None and not 0 < confidence < 1:
        _fail("joint_confidence_level must be within (0,1)")
    if reliability is not None and not 0 < reliability < 1:
        _fail("required_whole_run_pass_probability must be within (0,1)")
    return (
        bool(durations),
        relative is not None,
        absolute is not None,
        joint,
        confidence is not None and reliability is not None,
    )


def _replication(reps: dict[str, object]) -> tuple[str, str, bool, bool]:
    for label in ("pilot_max_events", "pilot_max_seconds", "production_events_candidate"):
        _positive_int(reps[label], label)
    choices = {"unverified", "independently_audited"}
    python_seed = _choice(reps["python_stream_independence"], "python_stream_independence", choices)
    native_seed = _choice(reps["native_stream_independence"], "native_stream_independence", choices)
    reference = _digest(reps["reference_plan_sha256"], "reference_plan_sha256")
    confirmation = _digest(reps["confirmation_plan_sha256"], "confirmation_plan_sha256")
    if reference and confirmation and reps["reference_plan_sha256"] == reps["confirmation_plan_sha256"]:
        _fail("reference and confirmation plans must have distinct identities")
    return python_seed, native_seed, reference and confirmation, reps["production_events_candidate"] == 1000


def assess_protocol(payload: object) -> dict[str, object]:
    """Return admission blockers for each lane; never authorise execution."""
    root = _object(
        payload,
        {"format", "study_id", "catchment", "sources", "population", "observables", "replication", "native"},
        "protocol",
    )
    if root["format"] != FORMAT:
        _fail("unsupported preflight format")
    _identifier(root["study_id"], "study_id")
    cat, sources, pop, obs, reps, native = _sections(root)
    _choice(cat["engine_profile"], "engine_profile", {"python-cmd/cmd-6.44"})
    if not isinstance(cat["features_admitted"], bool):
        _fail("features_admitted must be boolean")
    sites = _identifiers(cat["site_ids"], "site_ids")
    has_durations, has_relative, has_absolute, has_joint, has_probability_targets = _observables(obs)
    mass, missing_mass, tail, flood = _population(pop)
    python_seed, native_seed, disjoint_plans, is_1000_event_candidate = _replication(reps)
    source_admission = _choice(sources["source_admission"], "source_admission", {"pending", "independently_admitted"})
    for label, value in native.items():
        _choice(value, f"native.{label}", {"unqualified", "independently_admitted"})
    has_model = _identifier(cat["catchment_id"], "catchment_id", optional=True)
    has_model_hash = _digest(cat["model_sha256"], "model_sha256")
    source_hashes = [_digest(sources[key], key) for key in ("bom_ifd_sha256", "arr_tp_sha256", "loss_sha256")]
    pilot = _missing(
        (
            (has_model and has_model_hash, "qualified_catchment_identity"),
            (cat["features_admitted"] is True, "supported_engine_feature_profile"),
            (bool(sites), "physical_site_ids"),
            (has_durations, "durations_minutes"),
            (all(source_hashes) and source_admission == "independently_admitted", "admitted_ifd_tp_loss_sources"),
        )
    )
    native_blockers = [*pilot]
    native_blockers.extend(
        f"native_{key}"
        for key in ("method_profile", "reader", "probability_weights")
        if native[key] != "independently_admitted"
    )
    if native_seed != "independently_audited":
        native_blockers.append("native_independent_replications")
    replay_blockers = [*native_blockers]
    if native["effective_inputs"] != "independently_admitted":
        replay_blockers.append("exact_native_effective_inputs")
    stability = [*pilot]
    stability.extend(
        _missing(
            (
                (has_relative and has_absolute, "prespecified_relative_and_absolute_peak_margins"),
                (has_joint, "joint_confidence_error_allocation"),
                (has_probability_targets, "prespecified_joint_confidence_and_run_reliability"),
                (disjoint_plans, "disjoint_reference_and_confirmation_plans"),
                (python_seed == "independently_audited", "independent_python_replicates"),
                (is_1000_event_candidate, "production_run_candidate_has_1000_events"),
            )
        )
    )
    full = [*stability]
    full.extend(
        _missing(
            (
                (tail == "independently_admitted", "qualified_unmodelled_rainfall_tails"),
                (flood == "independently_admitted", "annual_maximum_flood_interpretation"),
            )
        )
    )
    return {
        "format": RESULT_FORMAT,
        "study_id": root["study_id"],
        "declaration_only": True,
        "simulation_authorised": False,
        "modelled_rainfall_mass": str(mass),
        "unmodelled_rainfall_mass": str(missing_mass),
        "lanes": {
            "restricted_domain_python_pilot": _status(pilot),
            "native_independent_population_comparison": _status(native_blockers),
            "native_exact_event_replay": _status(replay_blockers),
            "restricted_domain_single_1000_stability": _status(stability),
            "full_annual_design_flood": _status(full),
        },
        "note": (
            "All positive results require external source review; "
            "no native run or flood-AEP conclusion is authorised."
        ),
    }


def _unique_json_members(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Reject ambiguity before semantic validation at every JSON object depth."""
    value: dict[str, object] = {}
    for name, item in pairs:
        if name in value:
            _fail("duplicate JSON member")
        value[name] = item
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("protocol", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.protocol.stat().st_size > _MAX_BYTES:
            _fail("preflight input exceeds 256 KiB")
        payload = json.loads(args.protocol.read_text(encoding="utf-8"), object_pairs_hook=_unique_json_members)
        report = assess_protocol(payload)
    except (OSError, UnicodeError, ValueError) as exc:
        print(json.dumps({"format": RESULT_FORMAT, "status": "invalid_protocol", "reason": str(exc)}))
        return 2
    print(json.dumps(report, sort_keys=True))
    lanes = cast("dict[str, dict[str, object]]", report["lanes"])
    return 1 if any(lane["status"] == "blocked" for lane in lanes.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
