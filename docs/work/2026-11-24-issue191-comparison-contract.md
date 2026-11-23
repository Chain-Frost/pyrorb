# Issue #191: source-neutral native MC comparison evidence gate — 24 November 2026

**Status: bounded software foundation, not native scientific qualification.** Parent [#9](https://github.com/Chain-Frost/pyrorb/issues/9) and scientific [#148](https://github.com/Chain-Frost/pyrorb/issues/148), [#150](https://github.com/Chain-Frost/pyrorb/issues/150), [#189](https://github.com/Chain-Frost/pyrorb/issues/189), [#190](https://github.com/Chain-Frost/pyrorb/issues/190), and [#191](https://github.com/Chain-Frost/pyrorb/issues/191) remain OPEN.

## Source and ownership boundary

- The pinned canonical `ryan-rorb-readers` dependency from ryan-tools revision `8940f46b251f4d2ba6e52d6cb2ef74cd71fbe33f` handles standard/batch/CSV/CMD reader forms, but the examined reader does **not** expose an admitted MC individual-run/diagnostic grammar. The upstream source-admission work is tracked separately under [ryan-tools #334](https://github.com/Chain-Frost/ryan-tools/issues/334).
- Do not parse native report text here, reinterpret standard batch rows as MC, invent event weights, or treat printed values as exact effective inputs. No private RORBwin report, original source path, manual, screenshot, raw observation or unapproved digest is included in this change.
- The added `monte_carlo_comparison.py` is a **pure read-only typed evidence contract**, not a second native parser, Monte Carlo estimator or native equivalence test. Other B/E/C policy IDs, HMAC RNG domains, numerical kernels, native readers and saved-plan identities remain unchanged.

## Bounded implementation

- A stable `pyrorb-native-mc-comparison-evidence/1` JSON-compatible presentation of source/version hashes, cohort/replication/scenario/duration/division/run/physical-site keys, distinct TP rank/original EventID/Python sample ID, per-field original token, line, unit and evidence quality.
- Explicit duplicate-event-key and invalid/missing-field checks. A native report banner does **not** authenticate the installed executable: these remain separate optional identities.
- Printed decimal values preserve their visible precision. `conditional_nearest_print_interval()` provides a half-print-unit interval **only under an unverified nearest-rounding assumption**. In particular `0.00` is not an exact-zero finding.
- `assess_native_comparison()` permits only **descriptive** input diagnostics; it explicitly refuses exact-event replay, native weighted reaggregation and native summary method acceptance, even when a constructed row supplies an apparent weight or an `exact_effective` label. These gates can only change after separate source/rule admission, not by a reported value alone.
- Focused synthetic tests cover invalid/nonfinite tokens, print precision, unknown EventID and weight, duplicate cohort-scoped identity, separated sites/durations and fail-closed comparison status.

## Follow-up: independent numerical-precision review

The first exact-head Codex review identified ambient Decimal precision as a real P2 threat to printed-token uncertainty. The correction now constructs half-print-unit bounds as exact integer-coefficient Decimal tuples, independent of the caller's arithmetic context. New high-precision/precision-3/negative-token synthetic controls cover the corrected contract. The first hosted run also exposed four test-only Ruff issues (imports, S105 token-assertion false positive and PT007 list conventions), corrected in the same follow-up. Fresh exact-head CI and Codex review are required; the original failed run is not acceptance.

## Verification and next decision

Author-created local Python 3.13.5 synthetic tests: **17 passed**, no skips, using only this bounded source file and test module. No checkout of the full repository or locally installed canonical reader was available in this environment; this **does not** establish full source/wheel compatibility. Hosted exact-head Windows source, Ruff, strict Pyright, wheel, CLI and CMD checks and fresh independent Codex review are required before considering integration. Keep the PR **draft and unmerged** pending results and owner approval.

Next independently owned work: authenticate a publishable/synthetic MC grammar in [upstream #334](https://github.com/Chain-Frost/ryan-tools/issues/334) before requesting a reviewed reader revision or changing the dependency pin; then add a *separate* source-admitted canonical adapter and comparison lanes under #191. The older [#150 effective-state handoff](https://github.com/Chain-Frost/pyrorb/issues/150#issuecomment-7106607565) remains a stop decision: no new native runs or extrapolated full-annual-probability equivalence claim.
