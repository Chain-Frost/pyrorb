# Issue #6 — default Python engineering method, batches and acceptance evidence

**Status (15 November 2026):** Method/correctness and explicit batches merged.
The owner subsequently selected **original RORB CMD as the numerical accuracy
reference**, with independently evidenced CMD defects as the only accepted
departure. The default loss calculation is corrected in PR #102 and the
post-correction CMD percentage discrepancies are measured below.
**Broader physical/native numerical acceptance remains open** pending
independent defect attribution and time/site review; performance is closed.

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
a physical-time observation. Apply the **owner-selected RORB CMD reference**,
including peak/ordinate/volume percentage differences; independent
mathematical and conservation controls are safeguards, not another
overall benchmark. Retain separate native exact-printed qualification;
do not convert cached candidate snapshots into new executions.

B owns regression schema/case policy/fixture selection and independent
qualification; C owns CMD capability matrix. This work retains no
performance optimisation or additional research engine task.

## Current CMD reference policy and post-fix receipt

Owner direction (public [issue #6](https://github.com/Chain-Frost/python-runoff-routing/issues/6)):
**RORB CMD defines acceptable numerical accuracy** for the default
Python engine wherever the reference is supported and attributable.
Prefer close agreement without requiring bitwise matching. A deliberate
departure is acceptable **only** for a named, independently substantiated
CMD defect; synthetic/mathematical controls are necessary safeguards,
not a proposed substitute for native comparison. Report both signed
percentage and absolute discharge/volume errors and peak-index/timing;
near-zero original discharges are not suitable individual percentage
denominators.

### Corrected method

[PR #102](https://github.com/Chain-Frost/python-runoff-routing/pull/102)
changes only the default method's **initial/continuing-loss crossing**
to full-bin CL once IL is strictly exceeded, plus divides near-100%
temporal weights by their actual total. Separate `python-cmd`
arithmetic, B's dataset/comparator and C's matrix are untouched.
The prior fractional-CL candidate produced **+8.50%** extra source
runoff in `review-ensemble-tp3` and **+9.30%** in
`review-ensemble-tp9`, relative to CMD-style source runoff.
Both discrepancies are now eliminated to at most **0.0000383%**
across all 36 computed cases.

### Fresh full-model regression and percentage comparison

- Public source branch `c9553efe96ac2ed924856beef70c5415b0798ea7`,
  [Windows/Python 3.13.17 workflow run 43675053165](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43675053165).
- Normal quality checks **918 tests passed**, Ruff 0.16.6, strict
  Pyright, wheel build and outside-checkout smoke. Exact wheel SHA-256
  `aae429968172e0be62622c178ca60c3f4403c6f9f6f088c7e8fd9360d8c7838a`.
  The existing fresh source and installed-wheel CMD baseline gates passed.
- A one-time diagnostic compared **the same 50 retained original
  public sources** through the current default `python`, compatible
  `python-cmd` and original CMD 6.44 printed observations, on
  identified full model/print/horizon and separate native clocks.
  It was **removed** from the normal workflow after collecting
  [the exact receipt](../ENGINEERING_METHOD.md#fresh-cmd-alignment--current-evidence-15-november-2026).
  No additional runner, private files, native executable,
  reference changes, or new comparison tolerance are retained.
- **36 supported / 16,836 complete indexed samples**; separate
  compatible CMD pass **36/36** native printed-policy case comparisons.
  **14 S1 source-unsupported** remain indexed, not silently excluded.
- **Worst** absolute peak difference relative CMD: **0.185986%**.
  Worst full-ordinate absolute error: **0.334365% of CMD peak**.
  Worst model-grid trapezoidal volume difference: **0.804717%**.
  All 36 peak indices match. These are actual measured errors,
  not approved pass thresholds. Original native printed-reference
  errors are of the same scale.
- Original ordered model/source/native-result plus complete source and
  outlet binary64 comparison digest:
  `e0f2acda323269648fe22aafd2a98ef73e097b6c81e50fd3065d4d97cd1fa362`.
  Native original raw 1-based time labels were never shifted onto
  the model's elapsed-from-zero clock.

| Case | Default peak vs CMD before → after | Default volume vs CMD before → after |
| --- | --- | --- |
| `review-ensemble-tp3` | +4.1164% → **+0.00531%** | +8.3088% → **−0.17333%** |
| `review-ensemble-tp9` | +10.4715% → **+0.05278%** | +8.8243% → **−0.43742%** |
| `review-design-baseline` | +0.3851% → **−0.01097%** | +0.5761% → **−0.26546%** |
| `zero-loss-ensemble-tp9-f4` | −0.05418% → **−0.05418%** | −0.21192% → **−0.21192%** |

### Bounded source-to-outlet continuity candidate

All 36 CMD-compatible source-volumes minus outlet trapezoidal
integrals are **negative**, while the default's difference remains
nonnegative in those same cases. In the public zero-loss
`zero-loss-ensemble-tp9-f4`, model/source rainfall volume
is approximately **14,825,140 m³** and the CMD-compatible terminal
outlet integral is **14,856,543 m³**, an excess of approximately
**31,402 m³ (+0.212%)**. Original CMD discharge print tokens
corroborate the excess to their published precision. This is a
**candidate native CMD continuity defect**, not yet a reviewed
exception: check native printed site/time attribution and
endpoint-storage conventions independently with B before authorising
a departure. Native reported inclusive volume is **not** equated
to model-grid trapezoidal volume.

### Remaining work in issue #6

Numerical acceptance is **still unassessed** pending a causal and
independently reviewed explanation for the residual routing errors
and any approved named CMD defect exception. CMD's print-site/time
review and exact native-profile qualification remain B/C scopes.
Do not lower numerical precision or imitate a suspected continuity
error without that evidence. No further acceleration; the
1,000-event owner target remains achieved on its prior synthetic model.
