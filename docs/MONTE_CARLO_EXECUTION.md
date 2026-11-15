# S7 Monte Carlo effective-event execution boundary (#149)

**Status:** Bounded, explicit-input execution adapter. Not a sampler, frequency estimator or qualified RORBwin Monte Carlo implementation. Scope [#146](https://github.com/Chain-Frost/python-runoff-routing/issues/146) owns sample plans, probability-to-depth interpolation and the stochastic sampler; [#147](https://github.com/Chain-Frost/python-runoff-routing/issues/147) owns weighted results; [#145](https://github.com/Chain-Frost/python-runoff-routing/issues/145) owns adopted probability/distribution policy. This interface routes already-materialised events using the [existing #119 runner](PROJECT_BATCH_MVP.md), without replacing its geometry cache or numerical solver.

## API and CLI

The public API in monte_carlo_effective provides MCRequestHeader,
MCPopulation, EffectiveMCEvent, write_effective_request,
validate_effective_request and materialise_arr_sample. The last function
transforms an **already sampled** BoM gross depth, exact TP source ordinal,
rainfall AEP and storm IL into pervious IL/CL explicit ProjectEvent overrides.
It uses the existing ARR2019 published ARF calculation exactly once. Its
preburst policy is explicit (none, subtract_reject, subtract_clamp);
a positive preburst is never silently subtracted twice. It does not draw
random numbers, interpolate IFDs, assume a source CDF or extend the valid
ARF domain.

The public API in monte_carlo_execution provides execute_mc_request,
summarise_ledger and replay_mc_event. These call the established prepared
iter_project_events and the standard report/export layer, not a second
numerical engine. Native file-backed rorb-cmd and independent python are
explicitly **unsupported** by this first adapter. The only supported
execution choice is python-cmd/cmd-6.44, without silent fallback.

CLI, with one existing project and a fully materialised request:

    python -m runoff_routing.monte_carlo_execution validate effective.jsonl
    python -m runoff_routing.monte_carlo_execution run project.json effective.jsonl ledger.jsonl --engine python-cmd
    python -m runoff_routing.monte_carlo_execution run project.json effective.jsonl ledger.jsonl --resume
    python -m runoff_routing.monte_carlo_execution inspect project.json effective.jsonl ledger.jsonl
    python -m runoff_routing.monte_carlo_execution replay project.json effective.jsonl ledger.jsonl sample-1 selected-event

The last command exclusively creates selected-event.json, selected-event.csv
and selected-event.txt, retaining the full ordinary hydrograph, time and
project/engine provenance.

## Streaming effective event request (not B's plan)

One newline-terminated JSON header record contains:

- format = python-runoff-routing-mc-effective-events; schema_version = 1
- plan_sha256: original immutable #146 plan content hash
- policy_id: selected versioned statistical/materialisation policy
- source_files: original input paths relative to this request and exact SHA-256
- populations: each scenario_id, duration_min, modelled_mass decimal string
- event_count: exact total expected source records

Each following newline-terminated JSON record contains sample_id, scenario_id,
duration_min, stratum_id, stratum_mass, stratum_size,
probability_weight, original_tp_id, original_tp_order,
rainfall_aep_percent, gross_depth_mm, arf_factor, storm_initial_loss_mm,
preburst_depth_mm, loss_policy and event. All noninteger numbers are
exact decimal strings. The event is the existing explicit project event
with event_id equal to sample_id, storm with complete percentages/horizon/
once-ARF-adjusted subarea depths, and losses with explicit burst IL
and fixed continuing loss. No second project JSON schema is introduced.

For example, a stratum of mass 0.1 with 100 sampled events has
probability_weight 0.001 for **each** event. The request must contain all
100; neither missing members nor new allocations are silently ignored.
Separate populations preserve probability mass for each duration/scenario;
unmodelled tails (modelled_mass < 1) remain explicit and are not
renormalised. All originally sampled TP IDs and source-order ordinals
are retained; physical print-site identities come from the verified
existing project. The exact sampled depth and loss are retained for replay.

The validator checks original source hashes, all population masses,
per-stratum allocations and weights, duplicate samples, exact 100% TP
percentages, original source IDs, duration/timestep consistency, one-time
ARF application, and exact burst initial-loss reduction. The execution
boundary additionally restricts the project to fully pervious single-ISA,
single-burst, IL/CL and fixed continuing/routing parameters. It does
not independently qualify the probability interpolation or sample
selection performed under B.

## Compact checkpoint and resume

The ledger JSONL header binds the full effective-request SHA-256, B plan
SHA-256, policy ID, original sources, project JSON/original-file hashes,
explicit engine/profile, running package-code fingerprint and optional
exact installed-wheel SHA-256. Every event record retains sample identity,
scenario/duration/stratum and **original weight**, effective-event hash,
effective-model hash, typed success/error diagnostics, all requested output
site IDs and, on success, the peak, index and physical time for each site.
A successful zero remains numeric zero; a failed/unsupported sample
retains its probability weight but has no fabricated peak or hydrograph.

Every appended row is flushed/fsynced. Resume accepts **only a verified
unchanged prefix** of the same request and engine implementation. It
rejects changed plan/policy/source/engine code, mixed samples/weights,
truncated JSONL and duplicate events. A changed/extended #146 plan needs
a **new** effective request and ledger. Reusing prior computations across
an explicit extension requires a separate reviewed identity/reweighting
adapter; it is not silently emulated by resuming the old ledger. A new
plan may preserve logical samples but change every affected stratum
weight (w_h / n_h).

Hydrographs are not accumulated across events in the ledger; ordinary
full Q is available by replay of any completed selected sample. Exact
quantile processing can consume compact per-event records without
imposing a lossy approximate quantile estimator. The validator currently
retains sample IDs and stratum counters, not Q arrays. This is a
small O(n) metadata cost; numerical Q storage is bounded to one event.

**A complete routed ledger is a software-complete run, not a frequency
curve.** Failed positive-weight events, missing tails and interrupted
runs are not reported as complete frequency estimates. #147 must consume
these exact weighted records and report its own completeness/quantile/
envelope policies; the CLI deliberately does not invent those results.

## Outstanding gates

- A/B: adopt and review policy/distributions, arbitrary-depth interpolation,
  conditional TP selection, plan creation and conversion into these
  exact effective records.
- C: weighted frequency, duration envelopes and representative-event
  selection over this ledger; no independently implemented estimator here.
- E: independent code review, source and isolated-wheel tests and bounded
  memory/throughput receipt must be recorded at the exact PR revision.
  Explicit cross-plan computation reuse/reweighting remains outstanding.
- F/#150: actual RORBwin MC distribution, source-preparation, native
  comparison and statistical qualification remain not assessed.

Neither a green execution test nor this adapter closes parent
[#9](https://github.com/Chain-Frost/python-runoff-routing/issues/9),
scientific rainfall qualification [#8](https://github.com/Chain-Frost/python-runoff-routing/issues/8),
or the full CMD gate [#5](https://github.com/Chain-Frost/python-runoff-routing/issues/5).
