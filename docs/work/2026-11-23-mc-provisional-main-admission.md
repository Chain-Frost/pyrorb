# Provisional Monte Carlo main admission — 23 November 2026

## Owner direction and scope

The owner explicitly approved integrating **the verified bounded B/E/C Monte Carlo CLI/API/text implementation** into `main` as a **provisional software capability**, rather than holding all usable software until RORBwin scientific qualification becomes feasible. This later direction supersedes the previous software-merge hold recorded under [#9](https://github.com/Chain-Frost/pyrorb/issues/9) and [PR #151](https://github.com/Chain-Frost/pyrorb/pull/151), **only for software admission**. The parent scientific issue and dependent native/statistical issues remain open; no engineering design-flood acceptance is granted.

## What the main branch contains

- Versioned `monte-carlo-statistics/1` **project method**, reproducible HMAC-separated stratum sampling and source-pinned persisted plans; plan extensions retain logical identities and use new probability weights.
- Explicit prepared rainfall/TP/loss events and `python-cmd/cmd-6.44` routing for the selected fully pervious, one-ISA feature subset, without a second solver or changed engine default.
- Bounded event-ledger persistence, fail-closed source and engine provenance, no-clobber output, integrity-checked pause/resume/extension and replay of an actual selected event.
- Per-duration/per-physical-site weighted frequency calculations, exact rational step inverse, zero-runoff atoms, failure/missing/unallocated mass, explicit unknown tails and separately labelled project sampling screens. Only an actually completed, supported population is eligible for a complete point estimate.
- Narrow independently reviewed #151 defects corrected in [#217](https://github.com/Chain-Frost/pyrorb/pull/217) and [#219](https://github.com/Chain-Frost/pyrorb/pull/219): reject ghost zero-count population allocations, reject wrong ARR2019 areal TP bins and reject source-path escape through symlinked ancestors.

Other software on main, including optional local MCP discovery/execution from #208/#209/#211, is retained without silently expanding the Monte Carlo MCP surface. The SUL 1.0 licence, `pyrorb` distribution, `runoff_routing` import identity, source/fixture hashes, historical HMAC namespace and supported Python 3.13/3.14 contracts are unchanged.

## Evidence and hard scientific limits

- The pre-admission staged code through `2a20753df945f9919ec530134ab6cdf1da21417c` passed [Windows quality #45170623382](https://github.com/Chain-Frost/pyrorb/actions/runs/45170623382), and its P2 repair stack had exact-head independent Codex reviews. The integrated MCP/main merge needs its own fresh CI and review before release to main; a prior run is **not** proof of this not-yet-tested integration tree.
- The native RORBwin 6.52 approved 5×5/24-hour cohort establishes 25 **printed** event records, not complete exact input/replay, independent-seed sampling or native flood-frequency agreement. The saved `owner-review.par` was drifted and excluded. The separate retained-evidence inspection found **no reliable nonexecuting exact-effective-input export** among the examined sources; this is a bounded negative finding, not a proof of general impossibility. See [#150 evidence](https://github.com/Chain-Frost/pyrorb/issues/150#issuecomment-7088939706) and separate draft [#218](https://github.com/Chain-Frost/pyrorb/pull/218).
- The initial published-ARF project policy models rainfall AEP fractions `0.01..0.50`, mass **0.49**, with **0.51** outside the rainfall support. Unknown tail mass is not renormalised away, substituted with zero flow or extrapolated; many requested full-population flood-AEP quantiles remain `incomplete`.
- Native probability conventions/within-stratum draws, loss and TP laws, effective ARF/preburst transformation, native frequency interpolation/inversion/weights/warnings and event/site identity have **not** been scientifically qualified. The project step-quantile policy is **not** RORBwin's accepted summary method.
- Independent real-catchment source-backed RORB/Python comparisons and a declared uncertainty/joint-pass analysis for a single 1,000-event production run have not established accuracy/stability. Synthetic controls and source/wheel CMD regression qualify bounded software, **not** native Monte Carlo science or engineering use.

**Scientific follow-up remains OPEN:** [#150](https://github.com/Chain-Frost/pyrorb/issues/150) native evidence, [#189](https://github.com/Chain-Frost/pyrorb/issues/189) sampling profile, [#190](https://github.com/Chain-Frost/pyrorb/issues/190) frequency/tails, [#191](https://github.com/Chain-Frost/pyrorb/issues/191) canonical comparison adapter and [#148](https://github.com/Chain-Frost/pyrorb/issues/148) convergence/budget, under parent #9. New scientific-method changes require separate versions, independently authored controls and source/installed-wheel verification. Future work branches from **current main**, not the historical #151 staging root. The [separate publication draft #215](https://github.com/Chain-Frost/pyrorb/pull/215) remains inert: no PyPI tag, trusted publisher activation, upload or external release follows from this main source merge.

## Integration rules and final receipt

- Integrate latest main through `83ae60981829c29d412e54104c5ffde99c43bc88` (optional MCP #208/#209/#211) with the bounded #151 code and all existing regression/research artifacts; resolve overlapping documentation and `pyproject.toml` without dropping either the `mcp` or research-only `scipy` extra.
- Require current-head Windows 3.13 quality, complete non-native tests, source and installed-wheel original CMD probes and independent review. Do not regard an unrun native RORBwin process as a pass. Use a **squash PR merge** to main after readiness; main branch ruleset stays active. Record the actual merge SHA, CI run and independent review on [PR #151](https://github.com/Chain-Frost/pyrorb/pull/151) and #9; no further numerical or scientific acceptance is implied.

## Additional pre-merge P2 category-eligibility review

An independent exact-head Codex review triggered when #151 became ready identified one further bounded fail-closed defect: a source TP member can have `frequent` AEP metadata while B's sampled conditional bin is `rare`, even if both source hash and EventID match. No native method or rainfall-probability boundary is inferred from this finding.

Software correction: when an original pattern includes its AEP category, compare it to the saved plan's existing conditional-bin ID before routing; retain source-areal files without AEP metadata under their existing area-only policy. This is a stricter source-eligibility check, not a new interpolation, numerical model, sampler stream, schema version or revised weight. Add one actual B→E negative test with hash-updated mismatched source, plus positive and negative areal-category controls. This does not establish RORBwin category thresholds. Require a new exact-head full CI and independent review before main admission; previous green receipts belong to earlier source revisions only.
