"""Candidate-authored reporting and rational metrics, separate from all kernels."""

import json
import platform
import sys
from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any

from .geometry import Geometry, compute_geometry
from .models import Event
from .power import bounded_power
from .precision import binary32_hex, binary64_hex, fraction
from .preparation import Preparation, prepare
from .routing import CandidateRecord, NetworkResult, ReachResult, State, route_network

CONTRACT_ID = "cmd644-bounded-reference-v6"


@dataclass(frozen=True, slots=True)
class CandidateResult:
    """Successful bounded result and all unmodified actual calculation structures."""

    event: Event
    geometry: Geometry
    preparation: Preparation
    network: NetworkResult
    revision: str


def execute(event: Event, revision: str) -> CandidateResult:
    """Execute one event without touching the filesystem or process state."""
    geometry = compute_geometry(event)
    preparation = prepare(event)
    network = route_network(event, geometry, preparation)
    return CandidateResult(event, geometry, preparation, network, revision)


def _rational(value: Fraction) -> str:
    return str(value)


def _stored(value: float) -> dict[str, float | str]:
    return {"value": value, "binary32_be": binary32_hex(value)}


def _wide(value: float) -> dict[str, float | str]:
    return {"value": value, "binary64_be": binary64_hex(value)}


def _state(state: State) -> dict[str, Any]:
    return {"q": _stored(state.q), "s": _stored(state.s), "residual": _wide(state.r)}


def _candidate(item: CandidateRecord) -> dict[str, Any]:
    return {
        "iteration": item.iteration,
        "coordinate": item.coordinate,
        "trial": _state(item.trial),
        "anchor": _state(item.anchor),
        "candidate": _state(item.candidate),
        "epsilon": _wide(item.budget),
        "accepted": item.accepted,
    }


def _metrics(reach: ReachResult) -> dict[str, Any]:
    flows = [fraction(q) for q in reach.q]
    storages = [fraction(s) for s in reach.s]
    incoming = [fraction(v) for v in reach.incoming]
    seconds = fraction(reach.duration_seconds)
    peak = max(reach.q)
    ties = [i for i, value in enumerate(reach.q) if value == peak]
    full_sum = seconds * sum(flows, start=Fraction())
    trapezoid = seconds * (flows[0] / 2 + sum(flows[1:-1], start=Fraction()) + flows[-1] / 2)
    continuity: list[str] = []
    storage_relation: list[str] = []
    a = fraction(reach.coefficient_seconds)
    for sample in range(1, len(flows)):
        defect = (
            storages[sample]
            - storages[sample - 1]
            - seconds * (incoming[sample - 1] + incoming[sample] - flows[sample - 1] - flows[sample]) / 2
        )
        continuity.append(_rational(defect))
    for sample in range(len(flows)):
        difference = storages[sample] - a * fraction(bounded_power(reach.q[sample], reach.exponent))
        storage_relation.append(_rational(difference))
    return {
        "peak": _stored(peak),
        "tied_peak_indices": ties,
        "tied_elapsed_seconds_exact": [_rational(i * seconds) for i in ties],
        "inclusive_sum_volume_m3_exact": _rational(full_sum),
        "physical_horizon_trapezoid_m3_exact": _rational(trapezoid),
        "continuity_defect_per_sample_m3_exact": continuity,
        "continuity_defect_sum_m3_exact": _rational(sum((Fraction(v) for v in continuity), start=Fraction())),
        "storage_end_minus_start_m3_exact": _rational(storages[-1] - storages[0]),
        "storage_relation_defect_per_sample_m3_exact": storage_relation,
        "candidate_metrics_not_native_acceptance": True,
    }


def result_dict(result: CandidateResult) -> dict[str, Any]:
    """Emit complete actual binary32/64 states, decimal identity and separately tagged acceptance."""
    event, geom, prep, network = result.event, result.geometry, result.preparation, result.network
    reach_results = [_reach_dict(reach) for reach in network.reaches]
    number_tokens = {
        "controls": [[c.code, c.length.lexeme] for c in event.controls],
        "areas": [v.lexeme for v in event.areas],
        "depths": [v.lexeme for v in event.depths],
        "impervious": [v.lexeme for v in event.impervious],
        "weights": [v.lexeme for v in event.weights],
        "h": event.h.lexeme,
        "kc": event.kc.lexeme,
        "m": event.m.lexeme,
        "il": event.il.lexeme,
        "cl": event.cl.lexeme,
        "n": event.n,
    }
    return {
        "contract_id": CONTRACT_ID,
        "backend": "python-cmd-public-bounded-v6",
        "status": "complete_candidate_result",
        "native_acceptance": "not_evaluated",
        "algorithm_conformance": "not_evaluated_by_report",
        "event_id": event.event_id,
        "input_sha256": event.input_sha256,
        "candidate_revision": result.revision,
        "runtime": {
            "python": platform.python_version(),
            "implementation": sys.implementation.name,
            "platform": platform.platform(),
        },
        "raw_number_tokens": number_tokens,
        "geometry": {
            "source_distances_km": [_stored(x) for x in geom.distances],
            "total_area_km2": _stored(geom.total_area),
            "weighted_total": _stored(geom.weighted_total),
            "mean_distance_km": _stored(geom.mean_distance),
            "reaches": [asdict(item) for item in geom.reaches],
        },
        "preparation": {
            "denominator": _stored(prep.denominator),
            "rain": [[_stored(x) for x in row] for row in prep.rain],
            "after_initial": [[_stored(x) for x in row] for row in prep.after_initial],
            "excess": [[_stored(x) for x in row] for row in prep.excess],
            "hydrographs": [[_stored(x) for x in row] for row in prep.hydrographs],
            "crossings": [
                {
                    "source_id": c.source_id,
                    "bin_one_based": c.bin_one_based,
                    "signed_remaining_exact": _rational(c.signed_remaining),
                    "equality_bins_before_crossing": list(c.equality_bins_before_crossing),
                }
                for c in prep.crossings
            ],
            "duration_seconds": _stored(prep.seconds),
            "continuing_allowance_exact": _rational(prep.continuing_allowance),
        },
        "reaches": reach_results,
        "outlet": [_stored(x) for x in network.outlet],
        "unvalidated_native_metrics": ["exact-ties/subprint-time", "physical-conservation"],
    }


def deterministic_json(report: dict[str, Any]) -> str:
    """Serialize deterministically with finite numbers and no undocumented precision trimming."""
    return json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n"


def _reach_dict(reach: ReachResult) -> dict[str, Any]:
    return {
        "reach_id": reach.reach_id,
        "members": list(reach.membership),
        "coefficient": _stored(reach.coefficient),
        "coefficient_seconds": _stored(reach.coefficient_seconds),
        "duration_seconds": _stored(reach.duration_seconds),
        "exponent": _stored(reach.exponent),
        "incoming": [_stored(v) for v in reach.incoming],
        "processed_peak": _stored(reach.processed_peak),
        "epsilon": _wide(reach.epsilon),
        "linear_storage_is_derived": reach.is_linear,
        "Q": [_stored(v) for v in reach.q],
        "S": [_stored(v) for v in reach.s],
        "steps": [
            {
                "sample_index": step.index,
                "target": _wide(step.target),
                "previous_q": _stored(step.previous_q),
                "previous_s": _stored(step.previous_s),
                "previous_i": _stored(step.previous_i),
                "current_i": _stored(step.current_i),
                "candidates": [_candidate(c) for c in step.candidates],
                "carry": {
                    "q": _stored(step.carried_q),
                    "s": _stored(step.carried_s),
                    "i": _stored(step.carried_i),
                },
            }
            for step in reach.steps
        ],
        "metrics": _metrics(reach),
    }
