# Weighted Monte Carlo frequency results — provisional statistical profile

Issue [#147](https://github.com/Chain-Frost/python-runoff-routing/issues/147) owns this **pure result layer**. The scientific-method owner is [#145](https://github.com/Chain-Frost/python-runoff-routing/issues/145); the sample-plan and runner owners are [#146](https://github.com/Chain-Frost/python-runoff-routing/issues/146) and [#149](https://github.com/Chain-Frost/python-runoff-routing/issues/149). This is a reviewable implementation of the explicitly named **`stratified-weighted-midpoint-v1`** empirical estimator, **not** an adopted RORBwin quantile policy, a statistically qualified return-level method or native-equivalence evidence. A's review may require a versioned method change before acceptance. The broader initial plan and published sources are in [PR #151](https://github.com/Chain-Frost/python-runoff-routing/pull/151), pending integration into `docs/MONTE_CARLO.md` by A.

## Boundary and units

`runoff_routing.monte_carlo_frequency` is a pure-Python API. It receives already-evaluated event peaks (`m3/s`) and an explicit, complete immutable **plan-revision** allocation. It does not draw random numbers, compute storms, route events, write files, duplicate the sample-plan schema or interpret native reports. The caller must construct `FrequencyScope(plan_id, policy_id, policy_version, scenario_id, duration_minutes, output_site_id)` and `CurvePopulation(scope, strata, tails)` from B's persisted plan. `plan_id` means the immutable **revision**, not B's stable cross-revision population ID. `StratumWeight` carries `(stratum_id, probability_mass, planned_samples)`, and `UnmodelledTails` carries explicit lower/upper rainfall tails and other unapportioned mass. The combined masses must sum to one within a strictly numeric `1e-12` binary summation allowance; omissions are input errors, **never renormalised**.

`PeakRecord` carries `scope`, `stratum_id`, stable `sample_id`, **current revision's** `event_probability_weight`, normalized result `status`, `peak_m3_s`, `event_id` and `effective_input_id`. Successful rows must contain the actual event and a resolvable effective-input manifest identity. A missing result may be a labelled `missing` row or an absent planned row; both retain their planned probability weight. Failures and unsupported samples retain a separate status and never acquire an inferred peak of zero. The caller must map the existing engine's raw statuses to `valid | failed | missing | unsupported` without discarding its original status/provenance. The normalised `valid` state means that a finite nonnegative peak was **reported**, not that the hydrology is native-qualified.

Mixed plan/policy/scenario/duration/site identities, duplicate sample or event IDs, unknown strata, excess observed rows, stale event weights and unsupported status/peak combinations are errors. For a plan extension, B may reuse stable sample IDs and cached raw outcomes, but E must re-present them with the **new plan revision, allocation and weights** before aggregation. The old weighted ledger is not reused silently.

## Exceedance and accounting

For one **scenario, duration and physical output site**, stratum `h` has rainfall probability mass `w_h` and **planned** conditional-draw count `n_h`; every planned draw's weight is `v_hi = w_h/n_h`. At threshold `q` the reported step statistic is the **strict** exceedance

\[
  \widehat S_{\rm known}(q)
  = \sum_{h:n_h>0}\frac{w_h}{n_h}
    \sum_{i\in\mathrm{valid}(h)}\mathbf 1[Q_{hi}>q].
\]

The `n_h` denominator never shrinks when results fail, are missing or are unsupported. `ProbabilityCoverage` separately reports `valid_mass`, `zero_mass`, `positive_mass`, `failed_mass`, `missing_mass`, `unsupported_mass`, unallocated strata (`n_h=0`), and lower/upper/other unmodelled tails. A valid zero flow contributes its weight to the CDF and is never treated as a failure. For `q >= 0` with unresolved mass `u`, the **conditional-on-known-records** exceedance interval is `[S_known(q), S_known(q)+u]`, capped at one. Negative `q` has exceedance exactly one because supported flows are nonnegative. These are logical bounds on a *partially observed finite population*, not statistical confidence intervals or support extrapolations.

## Quantile inversion (reviewable version 1 rule)

At user AEP `p` in the **open interval** `(0,1)`, use CDF probability `a = 1-p`. Identical exact positive peaks are grouped and their weights summed. Each distinct positive peak `Q_j` has plotting-position knot at

\[
  (F_{j-1}+m_j/2,\;Q_j),
\]

where `F_{j-1}` is the cumulative **absolute** known weight below the group and `m_j` is the group's absolute mass. Between adjacent knots the peak is interpolated **linearly in cumulative probability**, not logarithmic flow or log-AEP. Peak ties give a single knot with their full summed mass; a group of repeated values is **not** treated as independent rank positions. This smooth estimator is deliberately distinct from the strict empirical step exceedance reported above. A physical positive-flow atom beyond the treatment of exact ties would require a new adopted policy.

Zero flow is an explicit point mass. If `m_0 = P(Q=0)>0`, then every `a <= m_0` returns **exactly zero**, rather than interpolating a spurious small positive flood. The first continuous interpolation segment, when used, starts at `(m_0,0)`. An all-equal *complete* observed population returns that common value, with no implied variance precision. Otherwise no estimate is produced outside the first and last adopted plotting knots; `boundary_limited` reports that no probability-tail extrapolation is justified. The result includes whether an extreme knot influences the interpolation and the distance in CDF-probability units to the nearer plotting boundary. Neither the historic native “20%” warning nor a universal accuracy tolerance is applied.

If any **positive probability** remains uncomputed, the result status is `incomplete` for every requested AEP, not a renormalised point estimate. For `a=1-p`, let `F_known` be the weighted empirical step CDF of valid outcomes and let `u` be the missing/failing/unsupported/unmodelled mass. Conditional on the observed positive-weight peaks and only the nonnegative-flow constraint, conservative *finite-ledger* bounds are

\[
  Q_{\mathrm{low}} = \begin{cases}0, & a\le u,\\F_{\rm known}^{-1}(a-u),& a>u,\end{cases}
  \qquad Q_{\mathrm{up}}=F_{\rm known}^{-1}(a).
\]

Here the step inverse returns the smallest observed peak reaching its **un-normalised absolute** cumulative probability, and `Q_up` is unavailable (unbounded) if `a` exceeds the known mass. The bounds correspond to placing every unresolved peak at zero or arbitrarily large flow. They are **not** sampling confidence intervals or claims about the unsampled population's distribution. This implementation deliberately supplies no IID quantile interval for stratified/dependent draws; independent-replication and interval qualification belong to [#148](https://github.com/Chain-Frost/python-runoff-routing/issues/148) and [#150](https://github.com/Chain-Frost/python-runoff-routing/issues/150).

## Duration envelope and representative events

`build_frequency_curves` refuses an input record with no planned population and creates one `FrequencyCurve` per unique scenario/duration/site/plan identity. `duration_envelope` then computes the highest **separately estimated** duration quantile for the same scenario/policy/physical site. No duration weights are invented or pooled. If any duration is `incomplete` or `boundary_limited`, the envelope returns **no qualified point** and retains defensible bounds where possible. For a complete envelope an exact tied maximum selects the **shortest** storm duration; *near* ties are never made exact through a hidden tolerance. A margin to the second-highest estimate and all exactly tied durations remain in the result.

At a qualified quantile, the representative is the **actual positive-weight simulated sample** with minimum `|Q_event-Q_target|`; ties break on lexically smallest `sample_id`, then `event_id`. Its `sample_id`, `event_id`, `stratum_id` and `effective_input_id` permit E to replay the exact materialised event under the saved engine/profile. `target_peak`, `realised_peak`, signed and absolute mismatch are retained. An interpolated target is **not** itself a simulation, and no averaged hydrograph is constructed.

## Hand-calculated controls

Two strata have `(w_1,n_1)=(0.25,2)` with peaks `(10,20)`, and `(w_2,n_2)=(0.75,2)` with peaks `(30,40)` m3/s. Their individual event weights are `(0.125,0.125,0.375,0.375)`. By strict comparison, `S(20)=0.375+0.375=0.75`, and `S(30)=0.375`. The ordered positive group midpoint-CDF positions are `(0.0625,0.1875,0.4375,0.8125)`. For `p=0.5` (target `a=0.5`), linear interpolation between `(0.4375,30)` and `(0.8125,40)` gives `30+10*(0.0625/0.375)=31.6666666667` m3/s. The actual peak-30 event is nearest, with signed mismatch `-1.6666666667` m3/s. Pooling four peaks equally would give the **wrong** weighting.

For a separate example with a `0.4` zero-flow mass and `0.6` at peak `20`, `S(0)=0.6`, and an AEP of `0.65` (`a=0.35`) returns exactly zero. A missing mass of `0.2` above a known `0.8` mass at peaks `0` and `20` gives no finite upper bound at `p=0.1` (`a=0.9`); the lower finite-ledger bound is `20`. These values are checked as *literal expected numbers* in the standalone analytical tests, not obtained by using the estimator to generate its own fixture.

## Acceptance distinction

- **Software:** exact tests protect the implementation and adapter invariants; the current module marks software qualification `provisional` and does not represent a source/installed-wheel or reviewer decision as a native result.
- **Statistical method:** the interpolation rule, probability-domain support, continuity/atom policy and any intervals remain subject to independent #145/#150 review. A version change is required if the adopted rule differs.
- **Native RORBwin equivalence:** **not assessed**. This module has no native observations; F owns current-build sampling/result characterization.
- **Execution/CLI:** not delivered by this module. B provides real persisted plans and E will map event outcomes, write text results and retain replay manifests.
