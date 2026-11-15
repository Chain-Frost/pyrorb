# Default Python engineering method and qualification boundaries (issue #6)

**Current stage status (15 November 2026):** The bounded improved method, explicit-event batches and CMD-referenced deviation audit are delivered through merged #97/#99/#101/#102, and [#6](https://github.com/Chain-Frost/python-runoff-routing/issues/6) is **closed**. The owner accepts approximately 0.3% differences for this stage, not a strict metric-specific limit: maximum peak **0.186%**, maximum ordinate relative to CMD peak **0.334%**, and trapezoidal volume **0.805%** (the last is outside 0.3%). The wider volume/continuity questions remain under [deferred #103](https://github.com/Chain-Frost/python-runoff-routing/issues/103), and source/feature completeness under [#5](https://github.com/Chain-Frost/python-runoff-routing/issues/5). Prospective criteria and numerical discussion below are retained as method context, not grounds to reopen accepted bounded work.


Status: **RORB CMD-referenced default-engine calibration**, with independent
analytic/conservation safeguards and a bounded 36-case post-correction
comparison. Closer CMD agreement is the owner's accuracy objective, except
for separately established CMD defects. This is not bit-exact parity,
unrestricted hydrological acceptance or a substitute for original physical
print-site/time attribution. The earlier prospective controls were recorded
against `main` `c789c58` on 2026-11-15, before examining residuals;
the historical candidate snapshot is not a fresh current computation.

## Scope, quantities and computational order

- This is the `python/engineering-v1` selector, the **default**. The existing
  `python-cmd/cmd-6.44` and `rorb-cmd/cmd-6.44` arithmetic/execution remain
  separate. There is no fallback and no private code, executable, generated event,
  Monte Carlo or RORBwin computation on this path.
- The implemented S1/S2 boundary accepts a DESIGN event, one uniform pervious ISA,
  a single initial/continuing loss pair and natural reaches. Controls 1 (subarea
  and route), 3 (store running branch), 4 (confluence), 5 (route running branch)
  and 7 (print) execute in their **original source order**. Each source must
  appear exactly once in the final printed outlet. Print IDs/labels are not
  inferred from native HydNNN identities.
- Areas `A` are in km², reach lengths in km, rain depths, initial losses and
  rainfall excesses in mm, continuing loss in mm/h, `Q` in m³/s, storage `S`
  in m³ and the fixed time increment `Δt` in hours.
  For natural reaches, `d_av = Σ(A_i L_i)/ΣA_i`, where `L_i` is
  the distance from subarea `i` to the final print; `kr=L_reach/d_av`,
  `k=kc*kr`. `kc` is nonnegative; `k` has units
  `h·(m³/s)^(1-m)`. The nonlinear storage law is
  **`S(Q)=3600 k Q^m`**. `m` is finite and strictly positive.
- The event has `N+1` samples at `t = 0, Δt, …, NΔt`.
  First source discharge is zero. Each rain bin's depth becomes a constant
  source-rate sample at the **end** of the bin:
  `Q_source[j] = A * excess[j-1] / (3.6 Δt)` for `j>=1`.
  Samples after rainfall have zero source rate. Source phase is a declared
  model convention, not a claim about original CMD printed time tokens.
  The calculation horizon must cover every supplied rainfall bin.
- Initial outflow for a prescribed reach is `Qout[0]=Qin[0]`;
  initial storage is consequently `S(Qin[0])`. A generated storm has zero
  initial source, so its reaches start with zero storage. There is no arbitrary
  initial-state or warm-start API in this profile.
- Routing uses **trapezoidal discrete continuity** on each reach:
  
  ```text
  k Q[n]^m + Δt/2 Q[n]
      = k Q[n-1]^m + Δt/2 (I[n-1] + I[n] - Q[n-1])
  ΔS = 3600 Δt/2 (I[n-1] + I[n] - Q[n-1] - Q[n])
  ```
  
  The `m=1` step is solved directly. Nonlinear steps use monotone
  bracketing and Illinois false position (256-iteration ceiling); the
  storage-time residual bound is `1e-12 * target` in the equation's
  units, **not** `1e-12 * max(1, target)`. Bracketing starts at
  the endpoint-flow scale and expands if required: trapezoidal discretisation
  may overshoot the inflow endpoints. This is a computational convergence
  choice, not a native iteration/stopping claim. A nonrepresentable target,
  negative target, residual overflow or nonconvergence is a failure; no
  silent negative-flow clipping, artificial water or last-iterate success.
- At each confluence the complete sampled branch hydrographs are summed
  pointwise; a non-finite sum fails. `S(Q)` is applied **per reach**, not
  to the combined catchment outlet as a substitute for internal storages.

## Default engineering loss policy — RORB CMD reference

**Owner acceptance direction (15 November 2026): RORB CMD is the primary
numerical reference for the improved default Python engine.** Match the
original CMD computation as closely as defensible, without requiring
bit-exact Python floating-point evaluation. Analytic, manufactured and
conservation controls remain guards against implementation mistakes and
evidence for any *specific demonstrated* CMD defect; they do not replace
CMD as the selected overall accuracy reference.

The initial engineering-v1 candidate treated the IL-crossing bin as
constant-intensity rainfall, charging continuing loss (CL) for only the
fraction of the bin following initial-loss (IL) exhaustion. The original
CMD 6.44 loss preparation instead charges the **complete** CL allowance
once a bin's rainfall strictly exceeds remaining IL. This is a defensible
discrete-bin model convention; no verified CMD defect justified a departure.
The default now adopts the CMD convention:

```text
consumed_IL = min(remaining_IL, rainfall_bin_depth)
remaining_IL -= consumed_IL
after_IL = rainfall_bin_depth - consumed_IL
excess = max(0, after_IL - CL * Δt)  if after_IL > 0
excess = 0                              otherwise
```

At exact equality `rainfall=remaining_IL`, the crossing bin has no
runoff; CL starts during the next *wet* bin. IL carries across dry bins;
unused CL does not. With `IL=0`, CL applies for the entire wet bin.
For `10 mm` rain, `IL=5 mm`, `CL=2 mm/h` and `Δt=1 h`, both
CMD-style and the revised default yield **3 mm excess** (the former
fractional-bin method gave 4 mm).

Within the declared one-pattern supported domain, near-100% temporal
weights are normalised by their actual sum before calculating rainfall,
like CMD. Inputs further than 0.01 percentage point from 100% remain
outside the current typed default boundary; this change does not
implicitly add the separately tracked 102.10%-weight CMD dialect.

## Boundary semantics

| Case | Explicit engineering-v1 behaviour |
| --- | --- |
| `m>0`, finite `k>=0` | Admitted to the mathematical solver; individual inputs and operations still require representable finite results. No assertion that all positive exponents are calibrated RORB hydrology. |
| `m=0` | **Rejected**, including when `kc=0`. A discharge-independent constant storage does not define a satisfactory zero-flow storage/state transition, and native constant-storage behaviour must not be silently converted into pass-through. A separate qualified policy is required before enabling it. |
| `k=0` for valid `m>0` | Explicit no-storage identity route: output equals prescribed inflow. This is not the `m=0` rule. |
| One zero-length reach with `d_av>0` | `kr=0`, hence pass-through for that reach; source/control order and other reach storages remain intact. |
| Entire geometry with `d_av=0` | **Rejected**: `length/d_av` is indeterminate, even when all lengths are zero; no guessed normalisation. |
| Zero timestep, non-finite values, negative rain/flow/area, missing source, unsupported controls, incomplete rainfall horizon | Explicit failure; no output padded beyond the requested time grid. |
| Trapezoidal negative target during steep recession | Explicit numerical/domain failure suggesting timestep refinement; never clip or claim stability. |
| Last source sample still nonzero | The requested sample horizon is returned, but trapezoidal event-volume accounting remains **open-ended**; add at least one zero-source sample, and extend further if the recession/storage balance is needed. |

The existing S1 source converter restricts some **zero-length imported reach**
records before the pure S2 solver; its capability is narrower than the pure
zero-length numerical case. This is a declared input-support difference, not
permission to bypass parser/native rules in the shared adapter.

## Owner CMD-reference comparison and percentage reporting policy

**Current policy supersedes any earlier text characterising native CMD as
merely optional contextual evidence for overall engineering-v1 acceptance.**
CMD output is the primary accuracy target for the default engine where
matched effective input, site and clock identities are available. Differences
need a causal explanation; an exception requires a **known, demonstrated**
CMD defect and a specific independently reviewed justification. The native
CMD-compatible Python engine remains separately strict to its frozen printed
policy; no comparison budget or fixture is loosened to favour the default.

Report both absolute and percentage discrepancies:
- Peak discharge: `100*(Qpeak_python-Qpeak_CMD)/Qpeak_CMD`
  (signed) and the peak-index/time shift on the matched model grid.
- Full hydrograph: maximum `|Qpython-QCMD|` and RMS error,
  each in m³/s and as **percentage of the CMD peak**. Do not divide
  individual low/zero discharges by near-zero reference ordinates.
- Model-grid trapezoidal volume: `100*(Vpython-VCMD)/VCMD`
  (signed). This is **not** the native inclusive printed-volume statistic.
- If the CMD peak or volume is zero, its relative percentage is
  **undefined**; disclose the absolute discrepancy and zero reference
  instead of silently presenting 0% or infinity.
- Compare every ordered ordinate with exact source/clock/site identities.
  Record excluded/unsupported events and never remove them from counts.

Percentages are diagnostics, **not retroactively selected pass tolerances**.
No overall acceptance threshold has been approved. Establish the
post-correction residuals and causal classification before proposing a
reviewed tolerance; preserve the native original one-based report labels.

## Independent accuracy and conservation gates (frozen prospectively)

These are mathematical and physical *guardrail tests*, not a separate
approved accuracy reference. Overall default-engine accuracy is evaluated
against matched CMD cases unless an independently evidenced CMD defect
justifies a named exception. These thresholds were originally set without
access to the CMD residuals and are retained as supplemental safeguards.

1. **Analytic controls:** zero-source and zero-storage events are exact;
   constant-inflow equilibrium is preserved; `m=1` agrees with its
   closed-form trapezoidal recurrence. Independently integrate the
   continuous linear ODE for `I(t)=a+b exp(-λt)` with `Q(0)=I(0)`.
   At `Δt=(0.5,0.25,0.125)` hours, the final error must fall by at least
   a factor `1/0.3` per refinement and the coarse error be below
   `0.002 m³/s` for the declared `a=2,b=3,λ=0.3,k=1,T=4 h` control.
2. **Manufactured nonlinear physics:** choose
   `Q(t)=2+0.04 t²` and
   `I(t)=Q(t)+k m Q(t)^(m-1) dQ/dt`
   with `k=1,m=0.8,T=4 h`, which satisfies `Q(0)=I(0)`.
   Using the same three refinements, final errors must contract by
   at least `0.3` each time, with coarse error under
   `1e-4 m³/s`. This continuous equation is independent of the
   implemented root algorithm.
3. **Local continuity:** for representative `m=0.6,0.8,1,1.3`,
   the absolute stepwise difference between `ΔS` and the
   trapezoidal input-minus-output volume is at most
   `1e-9` times the largest magnitude of the local storage change,
   input/output integral or `1e-12 m³` (explicit numerical scale,
   not a gauge-resolution or CMD printed-token interval).
   Nonnegative, finite states are mandatory, regardless of residual.
4. **Network conservation:** for a branched, two-source/three-reach
   120-step event, trapezoidal input volume minus terminal outlet volume
   equals the sum of **each reach's remaining storage**, within
   `1e-9` relative and `1e-7 m³` absolute. Terminal storage is
   reported, not erased; a separately specified full-recession case must
   fall below `1e-5 m³`.
5. **Loss and boundary cases:** separately exercise IL crossing, equality,
   dry-bin memory, no IL, no storage, zero-reach bypass, invalid `m=0`,
   all-zero/undefined `d_av`, long-timestep negative target,
   finite/nonnegative states, fixed horizon, and a tiny positive nonlinear
   discharge against an independently coded bisection reference (relative
   `1e-8`, zero absolute tolerance).
6. **Acceptance beyond synthetic tests:** every retained CMD case must
   declare its engine, input/storm/control identities, site/time mapping,
   outcome completeness and one applicable *case-specific* engineering
   accuracy policy before any CMD comparison. Record full ordinate,
   peak/time, physical trapezoidal input/output volume and storage
   residual **separately from** the native inclusive reported volume.
   Differences must be attributed to source, loss, storage/routing,
   finite horizon, clock, or unresolved mechanisms. A historical
   `computed_unvalidated` cached candidate is not independent
   production-engine computation.

Passing these analytic and synthetic controls qualifies their **tested
mathematical subset only**. It does not establish performance, calibrated
catchment accuracy, native source interpretation or numerical equivalence.
The default remains `computed_unvalidated` / `numerical_acceptance=unassessed`
until the broader evidence is independently reviewed.

## Source/installed-wheel and follow-on batch boundary

Run focused synthetic source tests, the affected prior tests and the common
contract/regression preflight; build and exercise an **isolated installed wheel**
separately on a permitted Python runtime. Log exact revision, interpreter,
test counts, environment and failures; a passed source run is not a wheel
run. No private checkout or native binary should be required for routine
tests. The maintained B comparison tools own fixture selection and schemas;
C owns the overall per-engine feature/qualification matrix. A batch API must
only reuse immutable event-independent geometry and parameters, never
rainfall/loss/event state, and must verify event-alone/batch equality
against this readable `calculate_storm` path before optimisation.

## Registered CMD comparison — evidence, not a new acceptance policy

The source-only one-time audit at [run 43651310519](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43651310519)
reused the public 50-case register, hash-verified original inputs, the maintained
S1 decoders, both explicit Python engine dispatches and the unmodified CMD
printed comparator. The generated project, effective model SHA, ordered
controls, print IDs, complete horizons and *Python model-elapsed* clocks were
matched before comparing output arrays. Original CMD raw one-based timestamps
were retained **without pretending to be the same physical time axis**.
See the [issue #6 work record](work/2026-11-15-issue6-engineering.md) for exact
revision and the individual diagnostic evidence fingerprint.

- 36 models computed by both engines, **16,836 full indexed ordinates**;
  `python-cmd` passes the case-specific frozen printed comparison in all
  36. The default `python` differs on all 36; its largest max absolute
  difference is **9.055480239753422 m³/s**. No common CMD tolerance is
  adopted for `engineering-v1`, and no such difference is accepted merely
  because native printing passes for `python-cmd`.
- The remaining 14 records cannot enter the common typed S1 execution
  boundary; they are **source-unsupported**, not numeric passes or failures.
- Model-grid trapezoidal physical volume calculations are distinguished from
  the original inclusive CMD reported-volume statistic. Input-minus-output
  volume contains terminal network storage and is **not** a measured
  continuity defect. Historical CMD raw print labels and the derived
  model-elapsed axis remain distinct.
- A different IL/CL crossing convention and floating-point/storage order
  can explain some potential divergences but have **not been independently
  apportioned** in this audit. Zero-loss cases also differ, so loss crossing
  cannot be invoked as a universal explanation.

**Historical (pre-loss-fix) qualification verdict:** The independently
manufactured mathematical scope and batch isolation retain their test
results. This comparison predates the corrected CMD full-bin CL policy.
Additional CMD cases and physical-site/clock mapping remain
`numerical_acceptance: unassessed` until a post-fix fresh comparison,
including percentages, demonstrates defensible agreement or pinpoints
a known CMD defect. No alternative overall validation reference is proposed. No edited
reference data, new regression schema, baseline updates or native process
execution were used for this audit.

## Fresh CMD alignment — current evidence (15 November 2026)

The earlier 50-case diagnostic below was captured **before** adopting
CMD's full-bin continuing-loss and near-100% weight normalisation. Its
large runoff differences are historical, not today's engine results.

A new **fresh, actual computation** used the identical current public
source-bound projects with explicit default `python` and separately
qualified `python-cmd`, plus the retained original CMD 6.44 printed
discharges: [run 43675053165](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43675053165),
source `c9553efe96ac2ed924856beef70c5415b0798ea7`. The one-off
diagnostic was removed from CI after recording its receipt; the published
product retains only the pure `cmd_deviation.assess_cmd_deviation` metric
helper and its tests.

**36/50 cases computed through both public engines, 16,836 full ordered
ordinates; 14 original-source profiles were unsupported at the existing
S1 typed-reader boundary.** The compatible `python-cmd` output passes
36/36 independently frozen native printed-policy case comparisons.
RORB CMD remains the accuracy reference; all original native time labels,
input/source identities and model/print-site mappings were retained.
These comparisons align array indices under the existing verified
single-terminal-source policy; independent native physical time/site
qualification remains a separate unresolved gate.

| Metric | Worst observed, 36 computed CMD cases |
| --- | ---: |
| Absolute peak discharge difference, as % of CMD peak | **0.185986%** |
| Maximum ordinate absolute error, as % of CMD peak | **0.334365%** |
| Absolute model-grid trapezoidal volume error, as % of CMD volume | **0.804717%** |
| Total source-runoff volume mismatch, as % of compatible CMD source runoff | **0.0000383%** |
| Peak-index offsets | **0 for all 36** |

The percentage formulae and zero-reference handling are specified in
the policy section above, with no after-the-fact pass tolerance.
Source and output results (selected before/after percentages):

| Original case | Peak before | Peak after | Volume before | Volume after |
| --- | ---: | ---: | ---: | ---: |
| `review-ensemble-tp3` | +4.1164% | **+0.00531%** | +8.3088% | **−0.17333%** |
| `review-ensemble-tp9` | +10.4715% | **+0.05278%** | +8.8243% | **−0.43742%** |
| `review-design-baseline` | +0.3851% | **−0.01097%** | +0.5761% | **−0.26546%** |
| `zero-loss-ensemble-tp9-f4` | −0.05418% | −0.05418% | −0.21192% | −0.21192% |

The relative differences from the **original native printed CMD**,
not merely the compatible Python backend, are of the same scale:
worst observed absolute peak **0.186096%**, worst ordinate
relative to native peak **0.335304%**, and worst trapezoidal-volume
difference **0.804081%**. The eligible original physical records are
not replaced by generated goldens. The exact full source/output/native
audit fingerprint is
`e0f2acda323269648fe22aafd2a98ef73e097b6c81e50fd3065d4d97cd1fa362`.

### Outstanding routing differences and CMD-defect investigation

All 36 computed source-volume values now agree to 0.0000383%,
whereas residual peak/volume differences remain. The compatible
CMD implementation's source-volume minus integrated outlet-volume is
**negative in all 36** cases (maximum magnitude ~31,402 m³ in the
zero-loss TP9 refinement). The conservative default instead retains
nonnegative modelled terminal storage (roughly 50–436 m³ for these
complete horizons). This is strong evidence of a *possible* CMD
numerical continuity defect under the retained source/terminal-output
mapping, **not yet an independently approved named native defect**:
the original native physical site and one-based time semantics still
require B's separate confirmation. Do not modify the default's
mass-conserving routing to mimic a potential numerical error just to
lower the comparison percentage.

**Current disposition:** the code/analytic/batch and corrected
source-preparation work is complete. Native-reference error statistics
are quantified, and all computed CMD cases have peak-index agreement.
No universal acceptance percentage is authorised yet; accept a
remaining departure **only with a reviewed, specific CMD-defect record**
or correct any newly found default calculation mistake. The 14
unsupported original source records remain C/B capability work, not
numerical passes.
