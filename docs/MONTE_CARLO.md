# Monte Carlo statistical basis and work scopes

## Status and purpose

This is the initial specification and research plan for [issue #9](https://github.com/Chain-Frost/python-runoff-routing/issues/9), reviewed for planning on 15 November 2026. It is **not an implemented Monte Carlo capability or an accepted RORBwin compatibility claim**. Source-derived guidance, proposed project decisions and unresolved native details are distinguished below. Scope A owns the enduring adopted method; measured convergence results belong in a linked dated research report.

The product surface remains CLI, Python API and text files. Current development executes explicit events with `python-cmd/cmd-6.44`. The independent `python/engineering-v1` remains the intended future default. The sampling policy has its own identity, separate from the selected event engine.

## What is ready

The inspected baseline is main `0675d75b05dba7728b389fdd8af743060b4469b2`:

- [#119](https://github.com/Chain-Frost/python-runoff-routing/issues/119) supplies the common [explicit-event and batch contract](PROJECT_BATCH_MVP.md), including prepared geometry reuse and per-event outcomes.
- Merged [#136](https://github.com/Chain-Frost/python-runoff-routing/pull/136) supplies [deterministic design rainfall](ARR_DESIGN_BATCH.md). Its source readers, temporal-pattern, ARF and loss/preburst components are reusable.
- The existing deterministic design workflow accepts exact source AEPs of 50%, 20%, 10%, 5%, 2% and 1%. It does not implement arbitrary-AEP sampling/interpolation, probability-tail modelling, a Monte Carlo sampler or weighted frequency analysis.
- [#8](https://github.com/Chain-Frost/python-runoff-routing/issues/8) and [#137](https://github.com/Chain-Frost/python-runoff-routing/issues/137) retain rainfall preparation/qualification work. Full CMD [#5](https://github.com/Chain-Frost/python-runoff-routing/issues/5), advanced capabilities and future RORBwin PAR [#144](https://github.com/Chain-Frost/python-runoff-routing/issues/144) are separate.

Statistical design, analytic controls and the research harness can proceed now. Real-model conclusions require an explicit, qualified rainfall/loss policy and a supported event feature population. They do not require completion of every unrelated advanced capability.

## Primary sources and their limits

The [source register](SOURCES.md) identifies the supplied 2010 RORB manual (R1, chapter 8) and cumulative v6.52 release notes (R3). A historical manual, an advertised version and an observed executable are different evidence identities.

| Source | Relevant evidence | Limit |
| --- | --- | --- |
| [ARR Book 4 v4.2](https://www.arr-software.org/pdfs/ARR_190514_Book4_V4.2.pdf), chapter 4, sections 4.3.2–4.3.3 | Sampling, dependence, stratified probability estimation and indicative counts | General method guidance; not a complete specification of a particular RORBwin executable. |
| [Nathan and Weinmann, 2013](https://arr.ga.gov.au/__data/assets/pdf_file/0017/40562/ARR_DiscussionPaper_MonteCarlo.pdf), sections 3–5 and 7 | Worked probability treatment, losses, duration envelope and diagnostics | Historical discussion paper; distinguish its recommendations from later software behaviour. |
| [ARR Book 5 v4.2](https://www.arr-software.org/pdfs/ARR_190514_Book5_V4.2.pdf), chapter 3, section 3.6 and Table 5.3.13 | Empirical standardised loss distributions and dependence | Edition, probability direction, scale and corrections must be reconciled before adopting a numerical table. |
| [HARC v6.32 announcement](https://harc.com.au/forums/topic/rorbwin-version-6-32/) | Default MC initial-loss distribution changed; accompanying correction notes an error in the referenced ARR table | Does not identify the exact effective table or interpolation in the selected 6.52 binary. |
| [HARC temporal-pattern clarification](https://harc.com.au/forums/topic/selection-of-temporal-patterns/) | MC uses rainfall AEP categories; deterministic selection uses an explicit index | A dated implementation statement, not a new current-build observation. |
| [HARC pervious/impervious loss clarification](https://harc.com.au/forums/topic/monte-carlo-with-arr-2019-impervious-losses/) | Historical MC varied pervious losses and held impervious losses fixed | Do not apply a rural loss distribution indiscriminately to urban surfaces. |
| [HARC frequency-summary discussion](https://harc.com.au/forums/topic/monte-carlo-simulation-summary-results/) | Rainfall input must bracket target probabilities; boundary influence can make reported estimates unreliable | Exact boundary calculations and warning logic still require version-specific evidence. |
| [Dong and Nakayama, 2020](https://web.njit.edu/~marvin/papers/qtut-r2.pdf), sections 4–6 | Quantile error, stratified estimation, variance reduction and confidence intervals | Interval assumptions must match the sampling design and output distribution. |

The [HARC product page](https://harc.com.au/software/rorb/) listed 6.52 at this review. Existing retained source research should be reconciled before new observations; a previously proposed experiment is not an executed validation receipt. No manual or executable is added to the public repository.

## Quantities and proposed initial subset

The initial method concerns event-to-event hydrological variability and its integration into flood-frequency estimates. Monte Carlo sampling error is a separate numerical uncertainty. Uncertainty in calibration parameters or the assumed distribution is a further layer; more samples do not remove it.

| Quantity | Proposed baseline treatment | Decision/evidence required |
| --- | --- | --- |
| Rainfall probability and depth | Stratified probability sampling, mapped through a depth-frequency relationship | Probability convention, range, within-bin draw, interpolation and tails. |
| Temporal pattern | Draw an identified member of the eligible discrete population | Conditional duration/AEP/region population, weights, edges and original source identity. |
| Pervious initial loss | Sample the adopted empirical standardised storm-loss relationship, scaled by the adopted catchment median storm initial loss | Exact table/version, exceedance direction, scale, endpoints and interpolation. |
| Preburst and effective burst loss | Explicit configured transformation under one adopted policy; no independent preburst draw | Storm versus burst loss, dependence and no double subtraction. |
| Continuing/proportional loss | Fixed for the initial scope unless the selected reference explicitly requires otherwise | A deterministic AEP adjustment, if adopted, is distinct from an independent stochastic draw. |
| Routing `kc` and `m` | Fixed | Parameter-uncertainty analysis is a separate model, not an implicit addition. |
| ARF | Derive from the adopted catchment-area, duration and sampled-probability policy | Apply ARF once; retain the existing catchment-wide treatment. |
| Spatial pattern | Fixed for the initial subset | Any stochastic spatial pattern requires a separately adopted source/dependence model. |
| Duration | Separate simulation and frequency result for each configured duration | An explicit envelope rule; no invented duration probability weights. |
| Impervious, multiple-ISA and advanced features | Outside the first pervious single-ISA population unless separately supported and qualified | Existing feature owners retain their scope. |

Uniform spacing on a standard-normal probability coordinate does not imply a Normal rainfall-depth distribution [ARR Book 4, section 4.3.3.3]. Uniform draws in depth, cumulative probability and transformed-normal coordinate are also different procedures. The within-bin rule must be specified, not inferred from how boundaries are spaced.

Marginal distributions alone do not define a joint distribution. Each independence assumption or conditional rule must be recorded. For example, temporal-pattern eligibility can depend on sampled rainfall probability; storm loss and preburst must not be combined using incompatible interpretations.

## Statistical estimand and weighting

For a fixed scenario, duration and output location, let stratum $h$ have rainfall probability mass $w_h$, with $n_h$ samples drawn from its adopted conditional distribution. Let $Q_{hi}$ be the resulting peak. For complete modelled strata:

$
\widehat S(q)=\widehat{\Pr}(Q>q)
=\sum_h w_h\,\frac{1}{n_h}\sum_{i=1}^{n_h}\mathbf 1(Q_{hi}>q).
$

Each sample therefore contributes weight $w_h/n_h$. Unequal rainfall-stratum probabilities cannot be replaced by an unweighted percentile of all event peaks. Invert the weighted curve using an explicit quantile, tie and interpolation rule. Calling its result a flood AEP additionally depends on the adopted rainfall-probability and event-model assumptions; a conditional ensemble at one rainfall AEP is a different estimand [Nathan and Weinmann, sections 4.3–4.4].

Complete accounting requires:

- Modelled interior strata plus explicit upper/lower-tail treatment. If the domain is incomplete, report the missing mass and supported bounds; do not renormalise it away.
- A valid zero-runoff event remains in the probability calculation.
- A failed event retains its planned identity and probability weight. Missing positive-weight results cannot disappear from the denominator or become valid zeros.
- A reported point estimate must meet the adopted completeness rule. Otherwise return incomplete/unavailable or justified bounds.
- Separate curves by physical site, duration and scenario. The duration envelope is formed afterward under the selected method; durations are not pooled as independent samples.
- Representative hydrographs identify actual sampled events and their effective inputs. Report the difference between the selected event peak and the target quantile. An interpolated quantile does not itself supply a simulated hydrograph.

Scope C must independently verify unequal-weight mixtures, monotone transformations, ties, zero-flow atoms, failures and tails. Sparse strata and zero observed exceedances must not be mistaken for proof of zero uncertainty.

## Reproducibility and execution contract

A sample plan must record policy/schema version, source hashes, probability support, stratum bounds/mass/allocation, duration/scenario, stable sample ID, selected TP source ID, primitive and effective values, fixed parameters, RNG algorithm/version and stream/seed derivation. Persisted effective values enable replay without sampling again. Resuming an unchanged plan differs from extending it. An extension may preserve earlier draws and logical IDs, but creates a new immutable plan revision and recomputes every affected stratum weight using its new sample count. Reject mixed old/new weights; extended-plan reaggregation must match a fresh full-plan calculation.

Keep the transformations explicit:

1. Generate the sample plan under the selected probability model.
2. Materialise exact rainfall and parameter values under the selected preparation policy. Scope B owns probability-to-depth/IFD interpolation; E consumes the sampled depth and owns explicit-storm/ARF/preburst materialisation.
3. Execute ordinary deterministic events through `ProjectEvent` and `iter_project_events`.
4. Associate results and statuses with their planned weights, then calculate frequency outputs.

The same materialised event can later be evaluated using another supported engine. That comparison changes the event engine, not the stochastic input population. Matching an integer seed across different RNG implementations does not establish matching draws.

Use prepared catchment geometry with fresh loss/routing state for each event. The current request-file array loader and materialised batch outcomes need a bounded adapter for large plans: stream or chunk plans/results, validate checkpoint identities and reject duplicate or mixed-policy resumes. Compact peak/result ledgers can support frequency calculations; full hydrographs may be retained selectively or replayed from saved events. No new GUI or general execution framework is needed.

## Research question: is 1,000 enough?

There is no accepted universal simulation count. ARR Book 4 section 4.3.3.3 gives indicative guidance of about 50 probability intervals and 50–200 simulations per interval, depending on input variability. This corresponds to 2,500–10,000 event evaluations per duration, not a guarantee and not proof of a current RORBwin default.

The proposed pilot below deliberately includes smaller budgets so the research can determine where 1,000 is adequate.

| Samples per stratum | Strata | Events per duration/scenario |
| ---: | ---: | ---: |
| 5 | 50 | 250 |
| 10 | 50 | 500 |
| 20 | 50 | 1,000 |
| 50 | 50 | 2,500 |
| 100 | 50 | 5,000 |
| 200 | 50 | 10,000 |

These are **proposed study settings**. Begin with a small timing pilot, then record the total event budget and wall-time cap before larger catchment runs. Extend only to resolve a remaining question. Count replications and durations explicitly; multiple output sites from one routed event do not multiply event evaluations.

Use approximately 30 independent replications to locate promising budgets, then independently confirm any proposed acceptance boundary. Measure variability of an individual production run, not merely the standard error of the average of all research runs.

For each site/AEP/duration and the final envelope, retain:

- Individual replication estimates, between-run SD/CV and run-to-run spread with its uncertainty.
- Error against analytical truth or an independently established higher-precision reference.
- Remaining reference uncertainty, failure/missing mass and probability-boundary diagnostics.
- Critical-duration selection frequency, including near-ties.
- Event evaluations, elapsed time and memory.

A high-count simulation is a reference estimate, not ground truth. Compare separate bin-allocation/refinement and rainfall-endpoint/interpolation sensitivity. Correct conditional sampling can be unbiased for any valid partition; any approximation error must be traced to the actual algorithm rather than assumed to arise from bin count alone.

Evaluate 1%, 2% and 5% relative precision bands with a declared absolute tolerance near zero. These are research options, **not ARR standards or adopted engineering tolerances**. Define whole-result success if claiming that all required outputs are stable, and quantify uncertainty in its observed success rate. Before labelling a budget adequate, declare the required pass probability and confidence level. An illustrative research target is at least 95% of independent runs passing, supported by a one-sided 95% lower confidence bound; this remains a proposed project choice. Alternatively report pass rates and uncertainty without an adopted adequacy verdict. Thirty pilot replications do not establish that reliability claim. Use predefined study stages and independent confirmation rather than repeatedly testing an ordinary confidence interval until it passes.

Variance reduction is a later research comparison: balanced treatment of finite TP populations, revised allocation, Latin hypercube or randomized quasi-Monte Carlo. Compare bias, uncertainty and cost under the same intended joint distribution. More resampling from ten patterns does not enlarge the underlying hydrological evidence base. Common random numbers can aid scenario comparisons; independent replications are still needed to assess between-run stability.

The existing performance target of 1,000 events under ten seconds is distinct from statistical sufficiency. No new performance claim or benchmark was produced by this scoping work.

## Native inspection and compatibility

A small, version-pinned observation of the existing RORBwin interface and emitted MC records is useful where a named question remains: loss-table values/interpolation, TP edges, effective preburst/ARF settings, exposed RNG controls, probability boundaries, failure handling or representative extraction. Capture the settings and actual effective inputs/outputs; screenshots alone do not prove semantics.

The [HARC extraction discussion](https://harc.com.au/forums/topic/extracting-mc-hydrographs/) describes a historical failure when a sampled routing run does not converge and recommends reconstructing individual events. It is a test lead, not proof that all selected-build scenarios share the defect.

No Ghidra/decompilation work is scheduled. Current [AGENTS.md](../AGENTS.md) prohibits decompilation. Documentation, retained evidence and ordinary controlled observations come first. An unresolved exact-stream or internal-rule question must name the claim it blocks and a proposed bounded follow-up; it need not block an explicitly specified independent sampler.

Preserve `cmd-6.44` and RORBwin profiles separately. Where effective native draws are recoverable, compare identical events. Otherwise evaluate aggregate statistical agreement with suitable uncertainty and label it accordingly. A routing difference must be resolved or isolated before attributing aggregate differences to the sampler.

Fresh native observations require a finite experiment plan under existing local permissions. Reuse retained private evidence under its existing permission. New unapproved raw captures, screenshots and traces remain local outside Git until the applicable separate custody/publication approval exists; this is not permission to expand raw evidence in the private repository. Public CMD-fixture approval does not automatically authorise RORBwin-data transfer.

## Work allocation and completion

| Scope | Tracker | Start and dependency |
| --- | --- | --- |
| A — statistical specification and source reconciliation | [#145](https://github.com/Chain-Frost/python-runoff-routing/issues/145) | Start now; owns the adopted method and gap register. |
| B — persisted sample plans and sampler | [#146](https://github.com/Chain-Frost/python-runoff-routing/issues/146) | Schema/analytic design now; implementation after A's baseline contract. |
| C — weighted frequency/results | [#147](https://github.com/Chain-Frost/python-runoff-routing/issues/147) | Analytic controls now; agree A/B schema before implementation. |
| D — simulation-budget/convergence research | [#148](https://github.com/Chain-Frost/python-runoff-routing/issues/148) | Analytic harness now; catchment results after A/B/C/E and feature qualification. |
| E — prepared execution and CLI integration | [#149](https://github.com/Chain-Frost/python-runoff-routing/issues/149) | Reuse current interfaces; complete against A/B/C contracts. |
| F — independent native/statistical qualification | [#150](https://github.com/Chain-Frost/python-runoff-routing/issues/150) | Reconcile evidence now; small observations for A's gaps, final qualification after implementation. |

The issue bodies contain the authoritative handoff prompts and acceptance criteria. This is not a second capability matrix. Keep [#9](https://github.com/Chain-Frost/python-runoff-routing/issues/9) open until the selected implementation, statistical, effective-input, native and reproducibility gates are supported by independent evidence. Software implementation and source documentation may finish earlier and must be labelled accordingly.
