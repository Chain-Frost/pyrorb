# 2026-11-15 — S6 deterministic-results reporting (#152)

Parent [#8](https://github.com/Chain-Frost/python-runoff-routing/issues/8); source and event runner already merged via #136/#119. Implementation branch: feat/152-deterministic-result-summaries.

## Bounded implementation

Read-only arr_result_summary.py reads current persisted .effective.json and event-result .json, emits three exclusive new files with source/source-order/event/site identity, exact requested/observed counts, untouched original full-horizon outcomes, observed peak statistics, exact ties and machine-readable unverified selection records. It does **not** select a representative event or critical duration. Strict engine/numerical-profile, source identity, site and time-grid guards prevent mixed populations. Failed/partial output states remain explicit, unqualified source candidates are never treated as accepted events.

Runnable authored control and supported-rule/limitation definitions: [ARR_DETERMINISTIC_RESULTS.md](../ARR_DETERMINISTIC_RESULTS.md). Focused synthetic API/CLI/corrupt/missing/multi-site/tie tests: tests/test_arr_result_summary.py.

## Independent admission and handoff

- #137 owns authentic source/effective-input and routed comparisons, not established by these synthetic metrics.
- #142 owns typed .out and batch.out rows and **native-reported** selections; no grammar or invented native selection is added here.
- #138 owns shared enums and contracts. This module consumes the unchanged #136/#119 outputs and owns only the reporting presentation.
- Candidate native profile: RORBwin 6.52 deterministic design batch, **unqualified**. Need pinned native complete peak rows, TP EventIDs versus ordinals, physical print site, selected reference, version/mode, qualified inputs/outcomes and distinguishing tie/missing/rank cases before claiming a compatible rule.
- Until admission, representative_selection and critical_durations report **unverified/null**. Do not close #8 or #152 for native selection.

## Independent review corrections (15 November 2026)

Review of PR #155 at its original head `2b171ba` identified an invalid complete-population claim for uniformly truncated saved hydrographs. The branch now verifies each event's declared `calculation_increments + 1` samples and the saved zero-origin elapsed timestep clock, retaining declared/observed sample counts and explicit partial reasons. Added one-member, entire-ensemble, shifted/scaled and invalid-clock controls. A second independent review at `fa40ac28` identified a false-positive cross-duration comparability diagnostic when one duration lacked a valid grid. Corrected this to require complete populations and non-null identical grid hashes at **every** considered duration, with missing/empty-duration synthetic controls. Both corrections retain all records and unverified/null native selections.

**Verification attribution:** previous passing Windows/Python 3.13 CI [43725767825](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43725767825) applies to original PR head `2b171ba` only; it cannot certify these review corrections. Revised exact-head source/installed-wheel validation and independent re-review are required. No native reference equivalence is claimed from this software work.

## Remaining bounded handoff

#137 has since completed original-event source/wheel software runs and reviewed custody but the source-derived effective rainfall differs from native-written-depth reconstruction for all 1,320 increment pairs, and high-precision native excess remains unresolved; zero common-effective native routed pairs are admitted. #142/upstream ryan-tools PR #233 remains open without an adopted typed reported-reference + physical site binding. Need an evidenced native build/mode, complete per-cell native peak population and failed rows, native original TP/source/native ordinal mapping, reported reference/site, and rule-discriminating statistics/ties/missing population plus duration aggregation. Keep #152 and #8 open for native-selection acceptance, and do not impose it as a blocker on complete software reporting.
