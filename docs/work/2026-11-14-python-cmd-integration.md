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

## Executed public whole-event/native-reference intake — 15 November 2026

The [fresh current public-code installed-wheel run](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43637009435) at `e7b4978fe81d94ca9cb646b07d9d0579f32a2942` verified **849 Windows/Python 3.14.10 non-native source tests**, Ruff/format, strict Pyright, a newly installed public wheel and a full, fresh original-input CMD probe over all 50 public cases. See [machine-readable per-case receipt](evidence/issue75/public_cmd_fresh_50_replay_20261115.json).

The probe **actually parses original published `.par/.catg/.stm` using the existing S1 codecs, builds one source-bound typed project, runs the selected public `python-cmd` in the isolated installed wheel**, and compares its freshly generated Q to original native `.out` over complete original rows using one maintained frozen printed-token comparator. Historical `candidate-snapshot.csv.gz` is not fed as a calculated result and RORB is not launched.

| Observed status | Cases / rows | Meaning |
| --- | --- | --- |
| `printed_pass` | 36 / **16,836 full original ordinates** | All original printed discharge tokens match within the *unchanged profile-specific printed unit budget* |
| `source_unsupported` | 14 | Genuine pre-computation S1 source/profile gates; not counted as numerical passes, fails or native model equivalence |
| `printed_fail` | 0 of 36 executable | No observed printed-budget mismatch within the qualified S1-input intersection |

The 14 specific gaps are eight archive events with original temporal pattern percentages outside the current strict S1 100%-total criterion and six supplementary events with missing recognised pattern markers, control-stack representation or required RORB_GE graphical dialect. All fourteen source identity/case IDs and diagnostic reasons remain in the public register/receipt. Do not silently renormalise original storm percentages, reinterpret RORB controls, synthesize source operands or weaken the general S1 parser to manufacture coverage.

**This bounded match is an actual comparison of fresh integrated `python-cmd` outputs with independent original native CMD printed records, but not a general native numerical-equivalence/physical acceptance:** it does not qualify the excluded 14 inputs, exact hidden native Q/S state, sub-print time/tie policy, independently budgeted physical conservation, other CMD dialects, or default improved Python accuracy. Original candidate `fea9c80` and newly integrated public code/wheel are distinct software identities.

For durable continuous integration the probe now explicitly checks that all 36 already admitted `cmd-reviewed` or `timestep` cases retain their `printed_pass` status and full **16,836** retained rows. It returns non-success if any of those proven bounded observations regresses; unsupported new cases are still reported individually and do not become an implicit acceptance pass. This baseline is an *input/output printed-diagnostic software regression*, not a universal numerical acceptance policy.

**Next tasks:** independent exact-head adapter review (including nonzero Decimal -> binary64 underflow), source+wheel requalification of public code versus the maintained private #56 candidate/internals where available, then targeted source-boundary qualification of the 14 absent cases before extending declared CMD input scope. The engineering and tie/time gates remain under private #53/#66 and public #5.

## 15 November 2026 — fail-closed regression and admission handoff

The earlier **36-case / 16,836-ordinate** source-and-wheel result applies to its specifically identified earlier Git revision. The quality workflow now executes the newly installed-wheel CMD regression probe in its own fail-closed step. An additional PowerShell negative control forces a synthetic probe to exit **37**, followed by a succeeding smoke command that would otherwise mask its failure, and verifies that the shell still reports 37. A new exact-head CI run is required before applying that prior computation result to the revised source.

### Effective-event review: maintained bounded path

- Public original `.par/.catg/.stm` bytes are hash-bound to the one register; `cmd_public_probe.py` invokes the maintained S1 `parse_cmd_par`, `parse_catg` and `parse_design_stm`. Typed `RunModel` carries source order, control stack, subareas, reaches and the sole terminal physical print identity; failed source admission never creates a computed success.
- `cmd_engine.adapt_event` retains source `Decimal` lexemes, widened binary64 and stored binary32 operations. Nonzero decimal-to-binary64 underflow rejects with `unsupported_feature/cmd_input_representation`; true zero operands remain valid and typed m=0 stays excluded. Storm start is represented by leading zero bins; existing depths, raw positive weights, one pervious ISA/burst and IL/CL are not normalised, reordered or replaced.
- Isolated `_cmd644.reporting.execute` calls the frozen `compute_geometry`, `prepare` and `route_network`. Source distances, rainfall/loss preparation, inflows, geometry/coefficient arithmetic, ordered controls 1/3/4/5 and final 7, stack membership, stored state, candidate convergence and distinct historic model-vs-observed-native target diagnostics remain inside this engine. No improved-engine rainfall, coefficient or routing result is borrowed.
- Output conversion checks all reach populations and the **`n+1` complete outlet horizon**, maps to the original sole physical print ID and records elapsed model time separately from raw native CMD `Inc/Time` tokens. The unchanged comparator checks the original registered physical site, full printed horizon and frozen printed-interval policy; `candidate-snapshot.csv.gz` is never used as an engine output.
- Three-engine dispatch remains `python` (improved default), `python-cmd/cmd-6.44` (explicit qualified-profile selection) and `rorb-cmd` (explicit optional native execution). Unsupported/unavailable cases return a typed failure and no hydrograph. No fallback, private runtime import, native launch or expected-output substitution.

### Dispositions of all 50 authentic CMD cases (last fresh execution)

| Status | Case IDs | Scope boundary / owner |
| --- | --- | --- |
| `printed_pass` — 36 cases and **16,836 rows** | Eleven `review-*`, twenty-two `timestep-*`, three `zero-loss-*` (full individual case IDs retained in the machine-readable receipt) | This installed-wheel printed-interval software regression must remain green; independent B review still required |
| `source_unsupported` — 8 | `failure-baseline-after`, `failure-baseline-before`, `fig67-ilcl-confirmed`, `fig67-ilcl-low`, `fig67-ilcl-probe`, `fig67-zero`, `wheel-ilcl-confirmed`, `wheel-zero` | Original DESIGN weights total **102.10%**, exceeding the S1 typed 100%-total condition; C must qualify native positive-total source semantics without changing or normalising original weights |
| `source_unsupported` — 3 | `H1-three-source-asymmetric`, `H2-four-source-nested-odd-rain`, `H3-single-source-equality-chain` | Original DESIGN source lacks expected literal temporal-pattern marker; C owns dialect characterisation in the maintained parser |
| `source_unsupported` — 1 | `N4-six-source-serial-nested` | Original control stack would overwrite an unstored running hydrograph; requires separate state/control semantics qualification before admission |
| `source_unsupported` — 2 | `pyromb-pr2-full`, `pyromb-novel-storm` | Existing graphical decoder recognises only one `RORB_GE 002` header; C owns qualification of the original header form(s) |

The fourteen excluded cases retain **2,714 original printed rows** but are not counted as actual integrated numerical matches; historical cached 50/19,550 candidate results are separate older-source evidence. No originals, numerical tolerances, parser recognitions, source order or frozen CMD arithmetic were altered to make this integration pass.

### Scope B exact-revision verification instrument

Freeze the new CI Git head, freshly built wheel SHA-256, installed module/package-code identity, original register/index hashes, and the specific immutable source/reference inputs. With the same public checkout, run `python -m runoff_routing.regression_dataset preflight tests/fixtures/regression-v1/register.json --set cmd-eligible --full-index`. From **outside the source checkout with only the installed wheel on PYTHONPATH**, run `python /absolute/checkout/repo-scripts/cmd_public_probe.py`. The resulting full 50-case JSON explicitly includes each `EngineOutcome` classification, checked rows and reason.

B independently validates its existing comparator/instrument, source/effective input identity, source/control order, per-case original `model_print_id` vs native `Hyd001` site mapping, native raw `Inc/Time` tokens, physical zero-based `n+1` engine horizon and actual original printed intervals. B owns maintained generic runner/schema, internal model/native and physical metrics; this engine owner does not write B's numerical acceptance. No new native process is required to verify retained reference data. The public CMD replacement gate #5 and private #56/#53 remain open.

## 15 November 2026 — completed exact-head public software/installed-wheel receipt

**Software head:** `c05319eb89888514a7707ca01ff48f322c39a084` (includes current main `c789c58fc7605c2341fef969ca426d30c3a477bf`). **Hosted [quality run #43645236994](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43645236994): SUCCESS** (job `132601399255`). Windows CPython **3.13.17** under the approved Python >=3.13 pure-Python development policy, with **849 passed** public source tests, Ruff and formatting and strict Pyright passing, wheel built and installed outside checkout, **7 passed** independent public native-fixture verification tests, indexed CMD preflight **50 cases / 227 original public files verified**, and a source-external `python-cmd` engine smoke with verified artifact/code identity.

**Freshly built installed public wheel SHA-256:** `cf20491ab49d42e5d8bfb723f0db42577a722cd1a7f7e3be8025f25a5c75471a`. This is not the private candidate wheel `3ad88f4...`, nor the earlier public `a2ef467...` wheel. The newly built package's source-import location, `package-code-v1-sha256:` provenance form, and artifact-to-installed-package consistency were exercised by the hosted wheel smoke. The independent local verifier must capture the *full* runtime implementation-revision string in its own result.

CI's deliberate **synthetic CMD probe failure** exited 37 from a child PowerShell file, and the harness verified `Process.ExitCode == 37` before continuing; the would-be following successful smoke was unreachable. The real fresh CMD probe then ran as an **independent step with immediate `$LASTEXITCODE` propagation**, succeeded, and reported `retained_36_case_printed_baseline: pass`, **36/36 original retained cases, 16,836/16,836 checked full printed rows**, `retained_baseline_failures: []`, `cases_checked: 50`, `printed_pass: 36`, `source_unsupported: 14`. All source exclusions match the prior original-ID ledger without changing native reports, source weights or numerical tolerances. The full 50-case original printed population is 19,550, but this exact public wheel computed only the 36 admitted cases, so the remaining 2,714 rows **are not fresh execution passes**.

The installed-wheel source/printed-interval comparison verifies a **bounded public computation baseline**; it does not independently establish hidden native states, general numerical equivalence, exact tie/time selection, physical continuity or full CMD replacement. B must independently confirm original site/time/effective-input mappings, actual current source/wheel comparison and private model/physical gates. C's separately tracked source-admission work is [#93](https://github.com/Chain-Frost/python-runoff-routing/issues/93), [#94](https://github.com/Chain-Frost/python-runoff-routing/issues/94), [#95](https://github.com/Chain-Frost/python-runoff-routing/issues/95) and [#96](https://github.com/Chain-Frost/python-runoff-routing/issues/96); the revised CMD capability matrix is [PR #84](https://github.com/Chain-Frost/python-runoff-routing/pull/84). Neither C's deferred dialect qualification nor B's independent numerical gate is implicitly resolved by this software result.

**Artifact reproducibility:** checkout the exact stated Git revision; install with the pinned dev policy; use the existing `repo-scripts/check_local.py` and `python -m build --wheel` followed by an out-of-tree wheel installation. Authenticate the single public 50-case register with `python -m runoff_routing.regression_dataset preflight tests/fixtures/regression-v1/register.json --set cmd-eligible --full-index`; use the checked-out absolute `repo-scripts/cmd_public_probe.py` path while the working directory is outside the checkout and `PYTHONPATH` names only the freshly installed wheel directory. Its JSON output preserves all original IDs, counts, inputs, reasons and named printed comparisons. Independent B results must cite the exact source and freshly built wheel and must not substitute the legacy `--snapshot` data. No new native process is required.
