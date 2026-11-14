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

## Bounded measured sample (2026-11-15)

The opt-in script was executed once on the existing Windows Python quality
runner at commit `3db16e673be0c14c4b524cf7c2d88ef9fe133dbb`, workflow
run `43647326912`. This temporary profiling CI step was **removed after
measurement**, leaving the existing quality workflow unchanged except for the
non-native installed-wheel batch smoke. Python 3.13.17/AMD64,
Windows Server 2025; two timing repetitions, a two-subarea/three-reach
nonlinear `m=0.8` case, `Δt=0.1 h`, 120 increments, one print site;
all event statuses `computed_unvalidated`:

| Event count | Preparation median | Warm compute median | JSON report median | Python allocation peak |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 0.0196 ms | 1.808 ms | 0.206 ms | 13,840 B |
| 25 | 0.0135 ms | 44.617 ms | 4.120 ms | 174,456 B |
| 100 | 0.0140 ms | 179.740 ms | 17.878 ms | 669,848 B |

The 100-event cold single-event median was **1.808 ms per event**.
The prepared batch's approximate 1.797 ms/event does **not** establish
a meaningful speedup (only two repetitions, host scheduling variance,
small geometry). Compute dominates; preparation costs about 0.014 ms
per model here, so an acceleration complexity increase is not supported
by this evidence. Reporting is separately measured and accounts for
about one tenth of the 100-event warm computation time. Allocation peak
is Python `tracemalloc` memory, **not** total process RSS. This
evidence supports bounded scaling of the tested synthetic case, not
a production batch performance guarantee.

## Owner stopping rule and measured 1,000-event gate (15 November 2026)

Owner decision: **if 1,000 explicit-event simulations finish in under 10 s
total on a representative model, no further performance optimisation is
required for this development stage**. The elapsed measurement covers
immutable model preparation, all event calculations, and JSON serialisation.
It excludes event generation, Monte Carlo/frequency analysis, external
application startup and native execution. A different/larger catchment or
longer horizon needs its own representative acceptance before applying this
rule generally.

The bounded existing **two-subarea, three-natural-reach, one-print,
120-increment, 0.1-h, `m=0.8`** synthetic workload passed at
[`f351805e`](https://github.com/Chain-Frost/python-runoff-routing/commit/f351805edbfeb7cded94fe29793763f22246103a),
Windows Server 2025 / Python 3.13.17 (AMD64),
[quality run 43648286419](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43648286419).
Three repetitions: direct prepare + compute + JSON **total median 1.584 s**,
min 1.579 s and max 1.592 s, with **1,000/1,000 computed outcomes**.
Separately, median warm calculation was 1.461 s, serialisation 0.140 s,
and preparation 0.0125 ms; the measured `tracemalloc` Python allocation
peak was 6,562,352 bytes (not process RSS). Exact environment/run hashes
and the older 1/25/100 samples remain in
[the performance receipt](work/2026-11-15-issue6-batch-performance.md).

**Result:** the tested 1,000-event workload meets the 10-second stopping
rule with substantial margin. No additional acceleration, compiled
dependency or concurrency framework is warranted for this case.
Do not imply this proves a 1,000-run bound for larger real catchments,
new forcing modes, or RORBwin Monte Carlo. RORBwin's multi-minute
runtime is a motivation, **not a directly comparable measurement**.

The single temporary profiling step used to collect this receipt was
removed from the approved quality workflow; the opt-in benchmark script
remains for locally initiated representative checks. The gate is a
performance decision, not a scientific/numerical acceptance claim.
