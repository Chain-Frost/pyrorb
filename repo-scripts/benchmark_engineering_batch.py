"""Opt-in, bounded engineering-v1 explicit-event performance measurement.

Run from the checkout with the package installed. This script does not set
acceptance thresholds, use native programs or generate stochastic events.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
import tracemalloc
from collections.abc import Callable
from dataclasses import asdict
from statistics import median
from time import perf_counter

from runoff_routing.engineering_batch import ExplicitEvent, run_explicit_batch
from runoff_routing.single_storm import (
    Catchment,
    Control,
    Losses,
    Storm,
    calculate_storm,
    prepare_catchment,
)


def _sample(operation: Callable[[], object], repetitions: int) -> dict[str, float]:
    seconds: list[float] = []
    for _ in range(repetitions):
        start = perf_counter()
        operation()
        seconds.append(perf_counter() - start)
    return {"median_s": median(seconds), "min_s": min(seconds), "max_s": max(seconds)}


def _workload(count: int) -> tuple[Catchment, tuple[ExplicitEvent, ...]]:
    catchment = Catchment(
        (Control(1, 2.0), Control(3), Control(1, 4.0), Control(4), Control(5, 3.0), Control(7)),
        (1.0, 3.0),
    )
    storm = Storm(0.1, 120, (40.0, 60.0), (5.0, 7.0))
    loss = Losses(0.5, 0.2)
    return catchment, tuple(ExplicitEvent(f"explicit-{index:05d}", storm, loss) for index in range(count))


def _run_one(size: int, repetitions: int) -> dict[str, object]:
    catchment, events = _workload(size)
    prepared = prepare_catchment(catchment, kc=0.4, m=0.8)
    preparation = _sample(lambda: prepare_catchment(catchment, kc=0.4, m=0.8), repetitions)
    cold = _sample(
        lambda: calculate_storm(catchment, events[0].storm, losses=events[0].losses, kc=0.4, m=0.8),
        repetitions,
    )
    warm = _sample(lambda: run_explicit_batch(prepared, events), repetitions)
    tracemalloc.start()
    records = run_explicit_batch(prepared, events)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    if any(entry.status != "computed_unvalidated" for entry in records):
        message = "Benchmark computation was not complete; timings are not acceptable evidence."
        raise ValueError(message)
    reporting = _sample(lambda: json.dumps([asdict(entry) for entry in records], allow_nan=False), repetitions)
    def end_to_end() -> str:
        fresh = prepare_catchment(catchment, kc=0.4, m=0.8)
        return json.dumps([asdict(entry) for entry in run_explicit_batch(fresh, events)], allow_nan=False)

    complete_run = _sample(end_to_end, repetitions)
    return {
        "event_count": size,
        "source_count": len(catchment.areas_km2),
        "reach_count": len(prepared.route_factors),
        "print_count": len(records[0].result.outlets_m3_s) if records[0].result is not None else None,
        "timestep_hours": events[0].storm.timestep_hours,
        "calculation_increments": events[0].storm.calculation_increments,
        "exponent_m": prepared.m,
        "preparation": preparation,
        "cold_single_event": cold,
        "warm_batch_compute": warm,
        "json_reporting": reporting,
        "preparation_compute_json_total": complete_run,
        "warm_batch_peak_allocated_bytes": peak,
        "status_counts": {"computed_unvalidated": len(records)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", nargs="+", type=int, default=[1, 100, 1000])
    parser.add_argument("--repetitions", type=int, default=5)
    options = parser.parse_args()
    if options.repetitions < 1 or not options.events or any(count < 1 for count in options.events):
        parser.error("All event counts and repetitions must be positive")
    results = {
        "purpose": "opt_in_engineering_batch_measurement_only",
        "engine": "python",
        "profile": "engineering-v1",
        "python": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "repetitions": options.repetitions,
        "workloads": [_run_one(count, options.repetitions) for count in options.events],
    }
    print(json.dumps(results, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
