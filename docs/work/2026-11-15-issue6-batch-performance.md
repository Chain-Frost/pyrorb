# Issue #6 — measured batch performance and quality receipt

Scoped draft PRs: phase-1 [#97](https://github.com/Chain-Frost/python-runoff-routing/pull/97)
and stacked phase-2 [#99](https://github.com/Chain-Frost/python-runoff-routing/pull/99).
No public numerical or performance qualification is implied.

## Exact reviewed source and wheel evidence

- Phase-1 method and independent engineering checks: `1673fdede3fd9a721c5d6d37f5e76d39a2f68236`;
  Windows Server 2025 / CPython 3.13.17, 833 tests passed, Ruff/Pyright
  0 issues, isolated wheel/built-artifact identity and seven regression
  suite installed-wheel checks passed. Exact wheel SHA-256:
  `c5989d2f17cdcb85f7e28e3eebf587cb59463ca0d5f556a3120d3b0d7eac8b19`.
- Phase-2 batch source and wheel controls: `2fd2d353c641a59d7ba42d4f94871907451e7a22`;
  Windows Server 2025 / CPython 3.13.17, 841 tests passed, Ruff/Pyright
  0 issues, wheel build, new installed-wheel engineering-batch smoke and
  existing engine selector and seven regression wheel checks passed.
  Wheel SHA-256:
  `309b746f7dd85b0c6e6336b6128911426bf3e81490fa17587c39b2afb22285fc`.
- One-time bounded benchmark, exact source `3db16e673be0c14c4b524cf7c2d88ef9fe133dbb`
  (same calculation/benchmark code; only the existing quality workflow
  had a **temporary additional profiling step**). Workflow run:
  `43647326912`, success including wheel smoke. Removed temporary
  benchmark step from branch after collecting logs.

## Separate wall-clock and allocation costs

AMD64 Windows Server 2025, Python 3.13.17; 2 repetitions per size.
Two sources, 3 natural reaches, 1 outlet, 120 steps of 0.1 h,
`kc=0.4,m=0.8`; all outcomes `computed_unvalidated`.
Values below are *medians* of the two runs, not statistically stable
speed comparisons.

| Explicit events | Preparation, ms | Cold single event, ms | Warm all-event computation, ms | JSON reporting, ms | Traced peak Python allocations, bytes |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.0196 | 1.897 | 1.808 | 0.206 | 13,840 |
| 25 | 0.0135 | 1.844 | 44.617 | 4.120 | 174,456 |
| 100 | 0.0140 | 1.808 | 179.740 | 17.878 | 669,848 |

At 100 events, warm computed time is ~1.797 ms/event, versus cold
single-run ~1.808 ms. These two repeated synthetic observations **do not
justify a material speedup claim**. For this small geometry,
event computation, not route-factor preparation, dominates; JSON report
time is ~10% of warm computation. The traced allocation peak is
`tracemalloc` memory **not RSS**, and sample rates, OS scheduler and
CPU frequency were uncontrolled. Future representative 1000/10000-event
benchmarks, multiple larger branching models and additional repetitions
can be opt-in, not CI gates.

## Engineering / regression acceptance separation

The independent continuous/manufactured phase-1 criteria remain
prospective and are exercised by source tests; B controls maintained
cached/fresh case comparison and C controls feature qualification.
The default engineering engine remains unassessed against the
historical native CMD snapshots. Its explicit uniform-bin IL/CL
crossing differs intentionally from full-bin CL, and numerical
outcomes are not declared bit-exact.

Conservation and nonnegativity have been independently checked for
the chosen analytic/branched cases; this is not a general catchment
accuracy certificate. No numerical fast path, extra dependency,
concurrency framework, baseline update or native subprocess was
introduced. The only performance optimisation at present is reuse of
event-independent geometry/coefficients.

## Owner's 10-second stopping rule — verified 1,000-event sample

The user set a practical performance limit: if 1,000 simulations,
**including model preparation, computation and reporting**, complete in
less than 10 seconds on a representative workload, stop optimisation.
A new direct end-to-end measure was added to the existing opt-in
`repo-scripts/benchmark_engineering_batch.py`; it does not change
the numerical method or enable background benchmarks.

Exact source `f351805edbfeb7cded94fe29793763f22246103a`;
[Windows quality run 43648286419](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43648286419);
Windows Server 2025 AMD64, Python 3.13.17. Three repetitions
(`python repo-scripts/benchmark_engineering_batch.py --events 1000
--repetitions 3`), two sources, three natural reaches, one outlet,
120 timesteps, `m=0.8`, `Δt=0.1 h`. Exactly 1,000 outcomes reported
`computed_unvalidated` with no failed or omitted events.

| 1,000-event metric | Result |
| --- | ---: |
| **End-to-end prepare + compute + JSON median** | **1.5843574 s** |
| Direct total min–max | 1.5789743–1.5915099 s |
| Warm batch numerical computation median | 1.4610127 s |
| JSON report median | 0.1401813 s |
| Geometry preparation median | 0.0000125 s |
| Python `tracemalloc` allocation peak | 6,562,352 bytes |
| Events accounted for | 1,000 / 1,000 |

The workflow's pinned Ruff/format, strict Pyright and all **842 non-native,
non-benchmark tests** passed, as did the isolated wheel checks; benchmark
source wheel SHA-256
`dcf37c53a5431bd77e8e46dc9ad721660266477f53acaccbbe1f29a583764ee5`.
Preparation, warm compute and JSON metrics are separately timed samples;
only the **direct total**, not their sum, is compared with the 10-second
criterion. `tracemalloc` excludes process RSS.

**Disposition:** performance is sufficient for this tested model and
horizon; **stop further optimisation for this workload**. Larger models
and actual MC event generation remain unqualified and outside this
explicit-event performance receipt. RORBwin's multi-minute Monte Carlo
run is not the same workload and is not used as a claimed speed ratio.
The temporary extra profiling CI step has been removed; normal quality
CI remains non-benchmark.
