# Default Python engineering method and prospective acceptance (issue #6)

Status: **prospective engineering-v1 contract and focused synthetic checks**, not a
certificate of RORB CMD equality, catchment calibration, or unrestricted hydrological
accuracy. First recorded against public `main` `c789c58` on 2026-11-15,
before inspecting any improved-engine CMD residuals. The complete 50-case cached
CMD snapshot and the independently qualified compatible-engine gate have *different*
reference purposes; their printed-token intervals are not these criteria.

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

## Default engineering loss policy

Under the declared **uniform rainfall intensity within each bin**, initial
loss `IL` is consumed first and carried across bins, including dry intervals.
If rainfall depth `p` first exhausts remaining `r` initial loss *inside*
a bin, continuing loss `CL` begins only for its remaining fraction:

```text
consumed_IL = min(r, p)
remaining_rain = p - consumed_IL
remaining_bin_fraction = remaining_rain / p   (when remaining_rain > 0)
excess = max(0, remaining_rain - CL * Δt * remaining_bin_fraction)
```

At exact equality `p=r`, continuing loss has no time to act within that
bin; it applies during subsequent wet bins. With `IL=0`, `CL` operates
through the entire wet bin. Unused continuing loss is not carried across
dry intervals. Every input and computed excess must be finite/nonnegative.

This fraction-of-bin rule is **intentional** and differs from a full-bin
continuing loss at the IL-crossing increment. For example, one 10 mm,
one-hour bin with `IL=5 mm` and `CL=2 mm/h` gives **4 mm** under
this method versus **3 mm** under full-bin CL. This is a mathematical
constant-intensity assumption, **not** a claim of native bug or CMD parity.
A different within-bin rainfall profile would require a different method.

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

## Independent accuracy and conservation gates (frozen prospectively)

These are checks on the stated discrete/continuous mathematics, **not**
tolerances selected after comparing with CMD.

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
