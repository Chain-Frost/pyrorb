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
