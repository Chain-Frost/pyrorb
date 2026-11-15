# Independent default Python control-2 and imperviousness numerical counterpart (#96)

**Parent:** CMD gate #5 / roadmap #1. **Default-engine owner:** A. **Source/parser owner:** C, PR #121/#109 (no domain-model edits here). **Base:** default `python` IL/RoC feature PR #110, head `640d69ad8e689f7076be8e6caa456dc36e3498ea`. **Branch:** `feat/python96-code2-fi-20261115`.

## Delivered bounded numerical behaviour

This PR develops the existing `python/engineering-v1` readable, independent S2 numerical path, **not** CMD legacy stored arithmetic:

- Extend direct typed S2 catchment with optional ordered `impervious_fractions` (default empty, interpreted as all zero without modifying older S2 calls), validate [0,1] and exact source count.
- Distinguish source addition at code 2 from source initialization. For code 1 or 2 encountered with an active hydrograph, add the next complete sampled source to the active branch **before** routing the natural reach, matching the already documented control semantics without using CMD kernels. Code 2 without an active branch rejects.
- Store and **clear** the running branch for code 3, then join code 4; continue to support multiple code-7 print results in original control order.
- For a specific source's FI, charge `(1-FI) * IL` and `(1-FI) * CL * Δt` on the original rainfall bins as separate per-source default-engine floats. For IL/RoC apply the coefficient only to post-initial-loss rainfall. These are independently implemented mathematical rules whose original native quantitative agreement **remains unassessed**.
- Cover original-order reach/source paths, single and multiple print sites, complete horizon, synthetic volume and mean-distance checks, FI=0 baseline behaviour, two distinct loss formulations, invalid FI and invalid control-2.

This does **not** edit `rorb_codec.py`, `integration.py`, S1 typed CATG/domain sources or the programme's single CMD matrix. The **file-backed/typed S1→default S2 bridge** still fail-closes `reach_mode=explicit_reach_types` and nonzero FI until C's independent source PR #121 is integrated and a separate reviewed default admission slice is added. Do not call direct S2 support a completed PR16 import.

## Exporter and source identities

Primary target upstream unmerged [PyRomb PR #16](https://github.com/norman-tom/pyromb/pull/16), exact head `phantom-branch/pyromb:Shapely-catchment-matching@a323d5709f7ce14c6adf46f01e0224b60668340c`, RORB writer parity baseline 2,818 bytes SHA-256 `67ae955b515a0594298fa1b0e48005d4d12db520e0a7dc582f37e6e06d6ad815` (not recovered here). The historical Chain-Frost/pyromb PR #2 `pyromb-pr2-full` and `pyromb-novel-storm` cases share one **different**, byte-identical 2,913-byte CATG SHA-256 `2ad4663ddeaacdfd4bba4b199a29d3eed7bcb6d9f096ff62f6d9d107330bd247`. Neither establishes the default-engine native accuracy for code 2/FI.

## Separate R / X / O / Q outcomes

| Engine | Recognised (public S1) | Executed | Outputs | Original CMD qualified |
|---|---|---|---|---|
| Default `python` | Via C's unmerged PR #121, typed code2/FI recognised; S1→S2 rejects pending independent adapter | Pure S2 code2/FI controls in this PR | Full direct S2 Q and source arrays | **No** (original clock/site/volume/peak/ordinate comparison missing) |
| `python-cmd` | Via C's unmerged PR #121 | Separate bridge PR #123 and internal guard PR #120 | Authored event Q only; originals depend on #94 storm | **No** (native original comparator pending) |
| `rorb-cmd` | Conditional file-backed | Not qualified for PR16 | Caller-assigned native columns only | **No** |

The accepted old 36-case approximately 0.3% hydrograph/0.805% volume diagnostics are **not** a policy for new code2/FI features. Future original CMD comparisons must record absolute and percentage peak, full hydrograph (CMD-peak-normalized max/RMS), physical trapezoidal volume, native inclusive reported volume and timing, with undefined percentages when the reference is zero. Site/clock/source parity and a confirmed native CMD defect are required for any defensible departure.

**Remaining dependency:** C integrates explicit natural reach/control-2/FI and relative-weight STM source recognition; A later maps those typed S1 operands into the independent default S2 adapter **without borrowing** `_cmd644` precision kernels. The programme owner maintains only `docs/CMD_FEATURE_MATRIX.md`; B/E qualify original reports and any PR16 export fixtures under the one immutable public register. Keep #96/#5 open, no automatic merge, RORBwin work, release or publication.

Exact-head Windows/Python 3.13 source + installed-wheel CI and independent review to be recorded only after checks actually run.


## Reconciliation with current main (2026-11-15)

- Reconcile the existing independent S2 code-2/FI implementation onto #110's current `python/engineering-v1` base. Main's merged #132 typed source, #119 immutable batch preparation, #130 temporary compatible default, #135 reporting fix, and #136 design preparation are retained rather than recreated.
- Direct S2 kernel and authored tests are **software method controls**, not proof of imported-model execution or native numeric parity. A separate follow-on commit adds the narrow existing typed-S1-to-S2 admission and file-backed/batch tests. The old exact-head CI receipts above apply to the *historical* head, not this reconciliation.
- Source/parser and common shared typed contracts remain owned by #96 and #138 respectively. No CMD stored-precision kernel import or change to default selection.

## Separate narrow typed S1→independent S2 admission (2026-11-15)

- Consume the existing, validated S1 source contracts from main/#132: ordered natural reach type-1 lengths for control codes 1/2/5, the original sequence of source/control/physical print IDs, and each source's ordinary impervious fraction. The independently implemented S2 code-2/FI arithmetic remains separate from `_cmd644` stored-precision calculations.
- Carry original `loss_model=1` IL/CL and `loss_model=2` IL/RoC into distinct float operands; guard finite/underflowing Decimal conversions including FI. Reject unsupported relative-weight/combined preburst, other reach types, multi-ISA and unsupported loss profiles instead of silently substituting a different engine or normalising inputs.
- Add actual historical 2,913-byte CATG import with **authored** percent-of-depth storms through embedded, SHA-verified file-backed project, explicit `python/engineering-v1` API and prepared event-batch path. These tests do not create or simulate a new original CMD observation; original historical relative-weight storms and primary 2,818-byte PR16 export remain independently unqualified for default `python` Q comparison.
- Under #138 coordination, do not define a second public edit/effective-model contract. Reconcile enum/loss interfaces when that separate owner lands changes. Leave #96/#90/#5 open for numerical Q/peak/time/physical-volume percent comparison against admitted same-effective-input native originals; no acceptance threshold inferred.

**Software QA:** await exact merged PR head Ruff, strict Pyright, fresh source tests, original CMD baseline, and isolated installed-wheel CI. Prior numerical/CI receipts remain historically pinned.

## Explicit relative-weight S2 input and native-observation diagnostic

The source owner #94 independently admitted the authentic `Temporal weights` dialect in merged #132. The independent S2 `Storm.pattern_basis` now **preserves the distinction** between raw positive relative weights and percentages; both calculate per-bin depth using their actual recorded denominator. Combined preburst/burst patterns still fail closed because they require a separately characterised split/denominator. Neither the typed source tokens nor the common project/event schema are changed.

A focused original-CMD diagnostic test reads SHA/byte-verified historical 2,913-byte CATG, original PAR, original relative-weight STM and original CMD printed table through the maintained `regression_dataset` reference reader; it deliberately selects `python/engineering-v1` and uses the existing `cmd_deviation` metric helper. Its output shows full Python/CMD Q, signed peak differences and percentages, unique peak indices with both native-reported clocks and separate elapsed clocks, CMD-peak-normalised max/RMS ordinates, physical trapezoidal-volume differences and the **separate original inclusive volume token**. The original CMD evidence is the reference; no generated Python-CMD synthetic proxy is called a new native observation. No acceptance threshold is inferred and the resulting figures must be independently assessed under #5/#133.

## Current-main and stacked independent-engine closeout — 15 November 2026

- Preserve #110 independent mode-2 parent (new test and main reconciliation commit `84d9c5f23ad455c43f311fa0f49805817488b2c2`) while merging main `4d7c48a562920767ed00fa23b6da7a17089d201d` #137 documentation into this existing #125 code-2/FI branch. Source/control order, prepared geometry, immutable batch isolation, FI and original register remain unchanged.
- Both independent paths are explicitly selected. The new typed import regression raises if `engine_execution.run_cmd_model` is called and asserts that actual project Q equals direct `run_model` Q; #110 contains the corresponding IL/RoC dispatch guard. Neither test can accidentally pass by computing with the temporary `python-cmd` default.
- Existing exact-head software receipt **before this reconciliation**: `7caa94bc76014afc5d8407d7e28e20b513cb2923`, [Windows/Python 3.13 Actions 43726706464](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43726706464) — passed Ruff/format, strict Pyright, 1,125 source tests, 153 external installed-wheel tests, fresh original CMD regression, original-PyRomb independent diagnostics and failure gates. A new head must have its own quality receipt.
- The two authenticated *original* CMD historical PyRomb profile diagnostics remain unaccepted engineering deviations, not synthetic CMD proxies: `pyromb-pr2-full`, **49 Q rows**, peak +0.1174255%, CMD-peak-normalised maximum/RMS +0.158480%/+0.038478%, physical trapezoidal volume +0.057179%; `pyromb-novel-storm`, **61 Q rows**, peak +0.0127864%, maximum/RMS +0.115002%/+0.051342%, physical trapezoidal volume -0.219011%. Full Q, absolute errors, index/clock and inclusive native volume are in the existing test's diagnostic JSON, PR #125 and CI. No tolerance adopted, original CMD denominators alone used for percentages, and zero denominators remain undefined.
- The actual **2,818-byte** pinned PyRomb PR16 export was authenticated and retained through merged #133/#154; the historical **2,913-byte** CRLF model is a distinct byte representation. PR16 writer-byte identity is not an additional native CMD output qualification. The mode-2 `fig67-ilroc` original source and 301-row Q report now exist but remain **unadmitted** pending site/clock/scalar decisions. Keep #90/#96/#5 open.
- #138's separately owned typed loss/enums/effective-model contract is in unmerged [PR #157](https://github.com/Chain-Frost/python-runoff-routing/pull/157). Do not duplicate it here; when it lands, reconcile this existing S1→S2 adapter with its accepted types. #125 remains a draft stacked onto #110; no merge authorization is assumed.

## Exact-head independent review finding and bounded correction — 15 November 2026

- Automated independent Codex review of `7cece31b0a5340c93a7882df2499987715ce7762` found a P2 failure in relative-weight storms: individually finite `1e308, 1e308` weights raise raw `OverflowError` inside `math.fsum` before either the S1-to-S2 or direct S2 finite-denominator check. This could abort a selected-engine project or a batch instead of returning a typed event failure.
- Correct the existing `_validated_solver_inputs` boundary to report `RunInputError(status="unsupported", code="storm_precision", role="storm")` when the sum overflows, and independently correct the pure S2 `calculate_prepared_storm` boundary to raise `RoutingDomainError`. Do not silently normalise an unrepresentable denominator or borrow CMD kernel arithmetic.
- New tests: direct S2 domain rejection and an explicit-`python` three-member original-PyRomb project batch with baseline → individually finite but total-overflowing relative weights → repeated baseline. Require `computed_unvalidated/unsupported_feature/computed_unvalidated`, `storm_precision`, no failed event Q and identical before/after full Q/time.
- No changes to original sources/reports, case register, tolerance, default engine, external #138 types, CLI schema, private evidence or native golden. The exact-head quality and fresh independent review must be rerun after this correction; prior receipts remain attributed to their tested heads.

## Second independent review finding: relative-weight underflow — 15 November 2026

- New Codex review of `cc6db28a844d48896f7cc1527ef48d099bc33d5d` identified a second P2 boundary defect: individually representable subnormal weights (e.g. `1e-323, 1e-323`) could each be multiplied by a 0.1 mm depth and round to zero before dividing by the tiny total, returning `computed_unvalidated` with false zero rain/Q.
- Relative-weight input now uses a dimensionless ratio: divide each finite source weight by the largest, sum scaled weights, divide by that sum, and only then multiply by source depth. Reject any nonzero relative weight ratio or nonzero rain-bin contribution that would underflow to zero rather than silently dropping it. Continue explicit typed denial of a raw denominator whose original float sum overflows. Ordinary percent-of-depth arithmetic remains unchanged.
- New controls compare equal subnormal vs ordinary relative weights in direct S2 and in an imported six-source project three-event batch, including nonzero rainfall excess, full Q, print/time equality, stored selection and repeated-event state. A separate extreme-ratio control proves fail-closed behaviour.
- These are independent engineering precision guards, not a new CMD native observation or numerical tolerance change. Exact-head quality and independent review must be repeated on the corrected head.

