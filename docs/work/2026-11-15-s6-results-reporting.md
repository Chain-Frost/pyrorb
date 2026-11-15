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

Local checks and CI receipts must be recorded against the reviewed PR head. These source files alone do not establish source/wheel or native numerical qualification.
