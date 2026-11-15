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

## Staged B → E → C text-file workflow

Once the separate #146 sampler and #147 results module are installed from
the **reviewed staging package** (they are not bundled in this isolated E
PR), the same CLI exposes the complete sequence without copying either
implementation:

```sh
python -m runoff_routing.monte_carlo_execution plan mc-spec.json study
python -m runoff_routing.monte_carlo_execution prepare project.json study.plan.json study.samples.jsonl effective.jsonl --ifd bom-source.csv --patterns source-increments.csv --arf-region "South-West Western Australia" --dry-tail-min 120
python -m runoff_routing.monte_carlo_execution validate effective.jsonl
python -m runoff_routing.monte_carlo_execution run project.json effective.jsonl ledger.jsonl --engine python-cmd
python -m runoff_routing.monte_carlo_execution frequency project.json effective.jsonl ledger.jsonl study-frequency --aep 0.01 --aep 0.02
python -m runoff_routing.monte_carlo_execution replay project.json effective.jsonl ledger.jsonl "mc:..." selected
```

`plan` delegates directly to B's **one** sample-plan schema and immutable
JSON/JSONL writer; `prepare` reads B's *persisted, validated* samples with
no RNG, uses B's already z-interpolated gross rainfall depth and the
published once-only ARR ARF, and checks source IDs/order and original BoM
IFD/TP hashes. Source files must lie within the output request's directory
so the effective manifest can pin safe relative paths. The first
integrated subset admits original BoM **depth in mm** (not inferred
EY/ARI/intensity conversion), fixed original kc/m/continuing losses,
a pervious one-ISA model and **zero preburst**. Other explicitly
profiled transformations require separate reviewed inputs; no
unapproved source extrapolation or independent loss draw is supplied.

The effective header includes the *full* original per-stratum planned
allocation, including count-zero strata, source-plan revision and the
separately named rare/frequent unmodelled masses. Positive-weight
failures are retained. A count-zero stratum contributes unresolved mass,
not a fictitious zero hydrograph.

`frequency` passes **verified** per-event physical peaks and explicit
planned weights to the single C/#147 estimator. It writes a streaming
CSV of the **actual attained weighted peak groups** plus compact
JSON/text per-site/duration coverage and requested fraction-AEP quantiles.
It does not implement quantiles itself. **Missing positive weights and
unmodelled probability tails cannot become a complete flood-frequency
curve.** Non-complete results return exit code 2 while retaining
diagnostic output. The complete C method and independent F review
remain separately owned.

CLI plan/prepare/frequency end-to-end acceptance against the **actual
#146/#147 modules** is pending integration of those independent
PRs into staging #151. This E-only PR can validate the bounded
adapter and synthetic explicit-event routing but cannot claim a
production B→E→C source/wheel receipt before those dependencies are
present.

## Streaming effective event request (not B's plan)

One newline-terminated JSON header record (schema v2) contains:

- format = python-runoff-routing-mc-effective-events; schema_version = 1
- plan_sha256: original immutable #146 plan content hash
- policy_id: selected versioned statistical/materialisation policy
- source_files: original input paths relative to this request and exact SHA-256
- populations: each scenario_id, duration_min, modelled_mass and explicitly split rare/frequent missing-tail mass
- strata: every planned scenario/duration/stratum, original probability mass and allocation count (including zero)
- event_count: exact total expected source records

#146's currently generated sample IDs contain colons, whereas the existing
#119 event contract admits a narrower ASCII identifier. The execution adapter
preserves the **original B sample_id verbatim** and uses a separate stable
ProjectEvent event_id: an already-legal sample ID can be used unchanged;
otherwise the engine ID is mc- followed by the SHA-256 of the UTF-8 sample ID.
The checkpoint stores **both IDs**. No sampling identity, source TP EventID,
physical print_id or source ordinal is substituted, and plan extensions
preserve both logical and engine IDs for unchanged samples. Human-readable
policy/scenario/stratum IDs may include separators such as / or : and
remain bounded trimmed/control-free text.

Each following newline-terminated JSON record contains sample_id, scenario_id,
duration_min, stratum_id, stratum_mass, stratum_size,
probability_weight, original_tp_id, original_tp_order,
rainfall_aep_percent, gross_depth_mm, arf_factor, storm_initial_loss_mm,
preburst_depth_mm, loss_policy and event. All noninteger numbers are
exact decimal strings. The event is the existing explicit project event
with the separate deterministic legal engine-event ID, storm with complete percentages/horizon/
once-ARF-adjusted subarea depths, and losses with explicit burst IL
and fixed continuing loss. No second project JSON schema is introduced.

For example, a stratum of mass 0.1 with 100 sampled events has
probability_weight 0.001 for **each** event. The request must contain all
100; neither missing members nor new allocations are silently ignored.
Separate populations preserve probability mass for each duration/scenario;
unmodelled tails (modelled_mass < 1) remain explicit and are not
renormalised. All originally sampled TP IDs and source-order ordinals
are retained; physical print-site identities come from the verified
existing project. The exact sampled depth and loss are retained for replay. The source TP kind, region,\nsource AEP category and area bin are retained separately from the #146 TP conditional-bin ID.

**Deliberate narrower project restriction:** for this first supported MC profile,\npoint TP is accepted only below 75 km2 and areal TP at or above 75 km2.\nRORBwin v6.52 describes this threshold as a recommendation which a user\nmay override, not a mandatory native rule. This software restriction is\nnot a RORBwin compatibility assertion. The sampled source IDs and TP\nfrequency categories are never replaced with an area-only category.\nThe explicitly optional `subtract_clamp` preburst policy is an\n**experimental separate statistical choice**, not `monte-carlo-statistics/1`;\nunder that policy ID it is rejected rather than silently adopted.\n\nThe validator checks original source hashes, all population masses,
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
exact installed-wheel SHA-256. Every event record retains both sample and engine-event identity,
scenario/duration/stratum and **original weight**, effective-event hash,
effective-model hash, typed success/error diagnostics, all requested output
site IDs and, on success, the peak, index and physical time for each site.
A successful zero remains numeric zero; a failed/unsupported sample
retains its probability weight but has no fabricated peak or hydrograph.

**Ledger schema v2** includes a SHA-256 hash chain over *every* result\nrecord, starting from the versioned header digest and continuing through\nall site peaks, physical times, status, diagnostics, plan weights and\nTP/loss/ARF provenance. Resume, inspection and selected replay verify the\nchain, so accidental modification of an existing numerical result fails\neven if the sample/plan identities still match. This is a **checksum, not\na digital signature**: someone who can replace all records can recompute\nthe chain. The CLI prints the complete-ledger SHA-256 for **independent\nexternal retention**. `inspect --expected-ledger-sha256 HASH` verifies such\na separately retained SHA-256; independent scientific authenticity still\nrequires actual input/output custody and selected deterministic replays.\nEarlier v1 ledgers cannot be silently read as v2 checkpoints.\n\nEvery appended row is flushed/fsynced. Resume accepts **only a verified
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
