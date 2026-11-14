# 2026-11-14 — CMD 6.44 bounded public event engine integration

**Issue:** [#75](https://github.com/Chain-Frost/python-runoff-routing/issues/75).
**Base:** Stacked on public draft [PR #77](https://github.com/Chain-Frost/python-runoff-routing/pull/77); not merged.
**Status:** Implemented for review; public source/installed-wheel native acceptance is **not yet recorded**.

## Reviewed candidate and exact inventory

- Original repaired numerical routing candidate: private `7d6985523e0b0e096fd63315ff702776c3b26e4d`.
- Independently reviewed additive diagnostic: private `fea9c80c521127325b779ea0ea87ddf77795b290`.
- Reviewed native-target diagnostic receipt `5be37dc0bfb12a7931efc29473f95b4edfe82e8c`, bounded transfer contract `02aa4ee425713b154ca3730a99edcc1ccdf0aefa`.
- Original candidate exact private wheel SHA-256: `3ad88f4d9127eafa79858c9aa93d04e4b3e4c4e4091a948038927416b92f2225`, **not** the public wheel.
- Native CMD 6.44 reference executable SHA-256: `10999ca29f9516c6a7abd26df37cafd433a1cd4ae70d7ac61aa7213845c5ab6f`; no executable is distributed or launched by ordinary tests.
- **Included source:** `models.py` (`10de728f`), `precision.py` (`6bb3662c`), `power.py` (`22090dd8`), `preparation.py` (`14362fb0`), `geometry.py` (`ec13bfa2`), `routing.py` (`eef4fdf0`), `reporting.py` (`07777935`), `native_diagnostics.py` (`6ec83c28`). Git blob abbreviations refer to original private candidate at `fea9c80`. Numerical expressions and evaluation order are unchanged; imports are made relative, line endings normalised, and research-only report identity text relabelled.
- **Included test:** independently reviewed synthetic diagnostic test `test_native_target_diagnostics.py` (`d67ee5fa`); additional public authored typed-adapter, complete-horizon, routing and negative-control tests.
- **Excluded:** private standalone JSON parser and CLI, reference fixture packets, native reports/states/traces, binaries, manuals, absolute paths, machine-specific runner, comparison scripts, research branch/history, old experiments, unredistributed datasets.
- New `cmd_engine.py` adapts existing S1 `RunModel` exactly once. It does not import the private repo, parse legacy files, use expected output as an oracle, or invoke improved Python rainfall/routing. Existing S1 typed readers remain authoritative.

## Declared capability boundary

Explicit `python-cmd/cmd-6.44` only: pre-supplied DESIGN storm, one pervious ISA/burst/pluviograph, lumped kc, IL/CL, natural reaches, code 1/3/4/5/7, one terminal print, preserved control and source order, full specified horizon and zero initial state for m>0. Typed decimal representation is preserved through `Decimal` and its spelling; original source-file bytes remain independently hash-bound, not re-parsed by candidate JSON.

The public typed domain does not represent nonzero impervious fractions/code 2 and forbids m=0. In particular, dry-step m=0 diagnostic native qualification does **not** establish an accessible m=0 public feature. More than one print site, other ISAs/storms, special storage, unprepared generated rainfall, other executable versions and wider source dialects remain unsupported. Candidate native/model-only comparisons comprise overlapping cases, not 167 independent catchments. The current `python-cmd` physical time axis is model-elapsed; it does not fabricate native one-based raw print clocks.

## Evidence and mandatory next gate

Private retained-native qualification of the standalone candidate: 2,982 Q/S, 84 coefficients, 3,272 inflows, 827 helper returns, 48,467 native printed ordinates. Reporting scalar evidence for 50 selected nominal-m=0.8 case instances: 50 peak pass, 48 qualifying peak-time pass with two zero-flow incompletes, 50 inclusive native volume pass. These are **upstream exact-candidate receipts only**, not results for this public source or wheel. Frozen scalar policy `d4bbec2213f2224f1c5e5dc7dc49381769e8d8f6`.

Mandatory independently reproduced `#56` replay: original source hashes, effective input preparation, print sites, full horizons and raw native clocks before unchanged printed-precision/model-only comparisons. Execute installed public wheel **out of tree** with actual import and wheel SHA-256, separate model-only suite, typed unsupported/invalid controls and every adverse case. Do not regenerate goldens or launch native software in cached comparisons. No independently accepted physical network conservation budget, full CMD completeness, or public parity yet.

## Public-native current code applicability probe

A public-only, **fresh computation** probe is added at `repo-scripts/cmd_public_probe.py` and called by the **existing** non-native Windows quality job from its isolated installed wheel. It uses only public SHA-pinned original CMD input/reference bytes, the existing S1 source parsers, explicit `python-cmd` project dispatch, and the maintained printed-token comparator. It does not import private data, execute RORB, manufacture missing inputs or rewrite expected values.

It inventories every one of the 50 eligible public cases with distinct `source_unsupported`, typed engine failure, `printed_pass`, `printed_fail`, and `incomplete_output` states; it prints each case and its first discrepancy, without claiming any scientific gate passed. **A completed probe is not successful numerical equivalence.** It is an explicit visibility step for exactly which captured cases the current public typed input path can actually execute. This should feed the next #75 adapter/coverage decisions, not change the frozen #56/#53 acceptance thresholds. Results must be recorded against the exact CI source and wheel revision; independent local native/model conformance remains a separate gate.
