# Immutable preparation and explicit-event batches (issue #6)

Status: initial **non-accelerated, deterministic** `python/engineering-v1`
batch API. Requires reviewed [engineering method and prospective accuracy
controls](ENGINEERING_METHOD.md). This feature is not a separate numerical
engine and does not alter the named `python-cmd` or native `rorb-cmd` paths.

## API

```python
from runoff_routing.engineering_batch import (
    ExplicitEvent,
    iter_explicit_events,
    run_explicit_batch,
)
from runoff_routing.single_storm import (
    Catchment,
    Control,
    Losses,
    Storm,
    prepare_catchment,
)

catchment = Catchment((Control(1, 3.0), Control(7)), (2.0,))
prepared = prepare_catchment(catchment, kc=0.5, m=0.8)
events = (
    ExplicitEvent("design-A", Storm(0.25, 32, (50.0, 50.0), (10.0,)), Losses(2.0, 0.5)),
    ExplicitEvent("design-B", Storm(0.25, 32, (40.0, 60.0), (12.0,)), Losses(2.0, 0.5)),
)
records = run_explicit_batch(prepared, events)
assert [record.event_id for record in records] == ["design-A", "design-B"]
assert all(record.status == "computed_unvalidated" for record in records)

# For larger populations, consume and persist one outcome at a time:
for record in iter_explicit_events(prepared, events):
    if record.status == "computed_unvalidated":
        assert record.result is not None
    else:
        print(record.event_id, record.error_code, record.message)
```

The `Catchment` controls/areas, `kc`, `m`, `d_av`, route factors and
individual reach `kc*kr` coefficients are prepared **once** into a frozen,
slotted `PreparedCatchment`. The model is not mutated by computation.
Input events are explicit `Storm`+per-event `Losses`, not ARR generated
storms; they can vary timestep, duration, depths, loss quantities and pattern
within the supported one-ISA DESIGN domain. A prepared catchment cannot be
reused for changed geometry, route parameters, control order or source count;
call `prepare_catchment` again.

For every event, rainfall excess, loss memory, source hydrographs, complete
reach routing, branch stack and output hydrographs are allocated locally
from fresh state. They are never cached or shared between event calls.
`calculate_storm` is retained as the readable fresh-preparation single-run
reference and delegates into the same reviewed numerical method.

## Identity, failure and memory semantics

- Event identity is explicitly supplied, nonempty, trimmed and free of
  control characters. Input **order** is the result order, with no hidden
  sorting, scheduling or parallel execution. The same event produces the
  same ordinates alone, repeated in a separate batch, shuffled or beside a
  failing event. No promises are made about floating-point results under
  future parallel reduction or fast-math modes, because neither is enabled.
- One `BatchEventOutcome` is emitted for each supplied event.
  `computed_unvalidated` contains a full `StormResult` (at all requested
  print sites for all `N+1` samples). `invalid_input` and
  `numerical_error` contain **no** fabricated result and a stable
  `error_code` plus message. Repeated IDs within one population produce an
  explicit `invalid_input/duplicate_event_id` outcome, never overwrite a
  previous result. Invalid model-level preparation rejects the entire
  attempted batch before execution.
- Per-event `RoutingDomainError`, `RoutingNumericalError` and arithmetic
  failures are isolated. A numerical negative target, root overflow,
  nonconvergence or confluence overflow is reported as
  `numerical_error`; input/horizon/loss-domain failures are
  `invalid_input`. Process termination, `KeyboardInterrupt` and
  `MemoryError` are **not** suppressed.
- `run_explicit_batch` materialises all event records and complete
  hydrographs; memory necessarily grows with event count, source count,
  print count and time-grid length. `iter_explicit_events` yields each
  result immediately, allowing the caller to store reports incrementally
  without retaining every hydrograph. It retains only the small set of seen
  event IDs plus the immutable prepared catchment.
- No native CMD programs, private workspace, stochastic sampling,
  frequency calculations, threads, workers or optional libraries are
  imported or used. The engine stays `python/engineering-v1` and its
  results stay `computed_unvalidated` until separately qualified.

## Verification and performance scope

`tests/test_engineering_accuracy.py` provides independent analytical and
conservation criteria; `tests/test_engineering_batch.py` verifies exact
single-run/batch equality, repeated and reversed-order determinism,
individual error accounting, invalid event isolation, numerical-error
isolation, frozen preparation, complete horizons, zero-flow and streaming.
The package's existing common engine selector/default remain unchanged.
Tests do not launch native executables or modify B's regression data.

Opt-in local measurements (source checkout, no native binary, no generated
rainfall) are available using:

```sh
python repo-scripts/benchmark_engineering_batch.py --events 1 100 1000 --repetitions 5
```

Use `--events 10000` only when affordable. The script reports **separately**
model preparation, one cold single-event calculation, warm prepared-batch
calculation, output JSON reporting and warm-batch Python allocation peak.
It records Python version, platform and architecture, numeric/event profile,
population, repetitions and median/min/max timings. The measured workload is
a deterministic two-subarea/three-reach 120-step nonlinear case. It is not a
representative RORB model suite by itself. Retain the exact source revision,
wheel hash and hardware details with any performance claim.

A speedup is not established merely by moving preparation outside a loop:
compare recorded cold and warm timings on identical workloads; include JSON
cost for the intended delivery format. The implementation makes **no**
fast-math or compiled-acceleration claim. The source/`calculate_storm`
path remains the reference for subsequent optimisation under the separately
frozen engineering criteria. Public CMD cached replay, fresh engine
computation and engineering acceptance must remain distinct.
