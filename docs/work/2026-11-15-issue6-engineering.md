# Issue #6 — default Python engineering method, batches and acceptance evidence

**Status (15 November 2026):** Method/correctness and explicit batches merged;
independent analytic/manufactured scope tested. **Broader CMD/physical accuracy
is unassessed**; issue #6 remains open for causal attribution of material
differences, not performance work.

## Source and software evidence

- Method, arithmetic and independent tests: [PR #97](https://github.com/Chain-Frost/python-runoff-routing/pull/97),
  squash commit `ac73820434ce051ccbb56db6aeaa2547630526f6`.
- Frozen preparation, deterministic event isolation/error reporting and
  opt-in batch benchmark: [PR #99](https://github.com/Chain-Frost/python-runoff-routing/pull/99),
  squash commit `e0c108cd0cc84723efd584bd7bcd9c74749b39de`.
- Post-merge [main quality run 43651065811](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43651065811):
  Windows Server 2025/Python 3.13.17, **885 tests passed**, Ruff/strict
  Pyright clean, wheel build, isolated wheel controls, CMD failure-propagation
  negative check and **fresh installed-wheel 36-case CMD printed regression**
  passed. Wheel SHA-256
  `083157e56a93f3d31ba51e907303040b5a35de0009dfa1dcda08fd95fdaca841`.
- The owner accepts Python 3.13 **or** 3.14 for pure-Python development
  checks. No native program/private checkout required, and the default
  remains `python/engineering-v1` without fallback.

## Independent physical/mathematical controls

[The frozen method and prospective criteria](../ENGINEERING_METHOD.md) are
tested for linear closed-form response, manufactured nonlinear refinement,
zero/equilibrium/initial state, branch conservation and end storage, tiny
flow via independent bisection, loss crossing/equality, overshoot and
long-step failures. The result scope is **only these declared tests and
admissible conditions**; a self-generated prediction is not a native
engineering validation oracle.

Immutable catchment preparation and per-event fresh state are covered by
the public batch source and installed-wheel tests. The 1,000-event direct
prepare + compute + JSON median is **1.5843574 s** (three Windows runs,
1.5789743–1.5915099 s), with 1,000/1,000 explicit outcomes on the
two-subarea/three-reach/120-step synthetic workload. See
[bounded performance receipt](2026-11-15-issue6-batch-performance.md).
The owner set a **10-second** threshold; do not pursue further acceleration
for that tested workload or claim larger catchments are benchmarked.

## Matched fresh public CMD diagnostic — policy-separated

One-time [PR #101](https://github.com/Chain-Frost/python-runoff-routing/pull/101)
captured a source-based, original-public-input **diagnostic only**:
[workflow run 43651310519](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43651310519),
candidate source commit `bcbb1898f2b2d713fae50887af77e10050a4825e`,
on base `e0c108cd0cc84723efd584bd7bcd9c74749b39de`.
The temporary Python-in-PowerShell computation step was **removed before
merge**; no extra permanent runner, new workflow, private data, native
executable, tolerance or fixture changes remain.

Each eligible event used hash-verified retained original .catg/.par/.stm
from the **existing** 50-case register, the public S1 parser, a single
identical stored embedded project, and explicit default `python` and
`python-cmd` runs with matching source SHA/control/print IDs and complete
model-elapsed time axes. The maintained fresh CMD comparator was used
unchanged for its **own** printed-tolerance gate. Native raw increments
and time tokens were not shifted into the Python physical clock.
Full per-case binary64 hydrographs plus original native discharge tokens
were included in the audit digest (not published as another dataset):
`d9de53bbccb2d3b419e11e25bf1faa5116712b17081e3349db4f063d04dc939e`.

| Measured classification | Count |
| --- | ---: |
| Registered CMD cases visited | 50 |
| Supported, freshly computed by both Python engines | 36 |
| Complete matched index ordinates in those cases | 16,836 |
| Frozen `python-cmd` printed-policy case passes | 36 |
| Default `python` differs from `python-cmd` in output | 36 |
| S1 source-unsupported records, **not numerical failures** | 14 |

### Observed diagnostic differences (not acceptance bounds)

| Case | Maximum absolute default−CMD discharge (m³/s) | Default model-grid peak (m³/s) | CMD model-grid peak (m³/s) | Trapezoidal volume default−CMD (m³) |
| --- | ---: | ---: | ---: | ---: |
| `review-ensemble-tp9` | 9.05548024 | 77.17023931 | 69.85532379 | +200,043.54 |
| `review-ensemble-tp3` | 7.95649427 | 58.19604552 | 55.89519882 | +201,723.51 |
| `review-design-baseline` | 2.37946693 | 190.98002133 | 190.24740601 | +29,726.57 |
| `timestep-ensemble-tp3-f4` | 1.97881339 | 59.55988711 | 59.05885315 | +43,006.64 |
| `zero-loss-ensemble-tp9-f4` | 0.35700536 | 273.19956341 | 273.34765625 | −31,483.49 |

These are **same-index diagnostics** on the original complete arrays,
not claims that a one-based native printed time equals the Python
zero-based elapsed time. Peak *time* differs by one sample index in one
of the 36 computed cases; raw native clock labels were not normalised.
The CMD native reported inclusive volume is not used as the physical
trapezoidal integral. For example, `review-ensemble-tp3` has computed
default source trapezoidal volume **2,629,619.35 m³**,
default outlet volume **2,629,548.51 m³**, and their difference
**70.84 m³** includes remaining terminal network storage; it is not a
measured continuity defect.

The supported 36 cases include nontrivial IL/CL crossing and zero-loss
inputs; **different within-bin continuing-loss treatment alone is not a
demonstrated explanation of all material discrepancies**. Relevant
separate hypotheses include rainfall/source conversion and clock phase,
floating-point/coefficient precision, routing integration and finite
recession horizon. The 14 excluded originals include invalid temporal
patterns, missing pattern markers, unsupported control stack topology
and graphical headers; they are still indexed as coverage gaps by B.

## Disposition and next numerical gate

**Software/analytic subset and bounded batch performance: complete.**
**Default engine's broader engineering accuracy versus CMD: not accepted.**
Resolve/quantify source runoff/loss differences separately from routed
numerics for the existing 36 cases, beginning with `review-ensemble-tp3`
and the zero-loss `zero-loss-ensemble-tp9-f4` control. Confirm
native physical-site/time mapping before treating original CMD output as
a physical-time observation. Apply independent, prospective engineering
criteria from the method document; do not tune acceptance to CMD printed
tokens or convert cached candidate snapshots into new executions.

B owns regression schema/case policy/fixture selection and independent
qualification; C owns CMD capability matrix. This work retains no
performance optimisation or additional research engine task.
