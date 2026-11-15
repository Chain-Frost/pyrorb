# Issue #149 bounded Monte Carlo execution — 15 November 2026

Baseline: main 0675d75b05dba7728b389fdd8af743060b4469b2.
Branch: feat/mc149-streamed-execution-20261115.
Ownership: S7 E only. Interface proposals posted to issues #146 and #147.

## Implementation

- An explicit, immutable effective-event JSONL boundary around the
  existing #119 project iterator. No second sampler, solver, native
  executable, rainfall depth interpolation or statistical quantile method.
- Source-hash, plan/policy and stratum weight/total mass validation;
  no double ARR ARF or preburst adjustment.
- One prepared-model iterator per execution/resume, compact per-event
  physical-site peaks and typed failures in a resumable JSONL ledger.
- Stale/mixed plan, revised engine code, changed source, duplicate and
  truncated checkpoint safeguards; only an exact source-plan prefix resumes.
- Selective representative-event replay into the ordinary batch
  JSON/CSV/text full hydrograph output using saved effective inputs.

## Evidence status and handoff

Synthetic checks cover direct-runner equivalence, once-only ARF/preburst,
CLI/replay, exact-prefix resume, stale inputs, invalid plan probabilities
and positive-weight failure accounting. Source/wheel quality and
independent review require exact checked revision receipts before
software acceptance. No new native observations or hydrological
acceptance claims were made.

End-to-end B-created persisted plan, C-weighted frequency CLI, an
explicit audited extended-plan computation-reuse/reweighting workflow,
and measured throughput/memory receipt remain pending. These must
not be represented as existing functionality merely because the
bounded execution adapter is present.

## 16 November follow-up — independent #150 review findings

- Review F flagged unauthenticated output-peak mutation and a misleading\n  native TP-kind interpretation. Ledger schema v2 now checksum-chains the\n  numerical result, physical-site/time evidence and effective-event ID.\n  An optional separately retained file SHA-256 verifies against a trusted\n  external receipt; a self-checksum alone does **not** establish\n  authenticity. A positive result still requires selected full-event replay.\n- Documented the strict <75-km2 point/areal choice as **our narrower\n  project limitation**, not a required RORBwin restriction. Retain the\n  real source TP area/AEP category/region plus B's conditional-bin ID.\n  Versioned clamp is rejected under the adopted baseline policy.\n- Added regression checks for tampered numeric results, external pinned\n  hash mismatch and zero-flow mass. Source/full-wheel quality must be\n  attached to the exact new PR revision, not inherited from prior head.\n- The earlier exact-head Windows software/source/wheel CI\n  [43727500931](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43727500931)\n  **passed** on `6570268430b6d88b4d5a7984e55df43a99adbfdc`.\n
## B/C integration and explicit extension — 16 November 2026

- B #146 and C #147 are now merged into the separate #151 integration
  branch, and this E PR is based on that exact staging lineage.
- Added actual B plan creation/roundtrip via CLI and B-sampled BoM z-linear
  gross depths, original temporal-pattern identities, one-time published
  ARR ARF and fixed single-ISA IL/CL materialisation. A source-backed
  end-to-end test calls B/E/C on the public synthetic fixtures.
- Added a C-owned strict weighted frequency CLI/report adapter, preserving
  positive-weight failure, zero-flow, unallocated stratum and both tail masses.
  Missing tail mass returns incomplete, not a fabricated flood-frequency AEP.
- Added explicit B plan extension into a new immutable checkpoint with
  parent/population/source checks, full retained effective-sample comparison,
  temporary disk-indexed scalar reuse, recomputed full stratum weights
  and fresh route execution for new events. Tests compare reused and entirely
  rerouted extended ledgers byte-for-byte.
- The Windows quality run on pre-extension combined head
  `16acb03ca149275701446ec13f161ae509d0b9c8` reached **1182 passed / 1 failed**;
  the single failure exposed a nonassociative Decimal sum-vs-product audit
  defect on large synthetic gross depths. The validator now checks exactly
  the maintained #136 increment-distribute, once-ARF, sum operation order.
  This does not relax input or routing tolerances.
- New code still requires an exact-head full Ruff/Pyright/pytest/source
  CMD/installed-wheel CI receipt and proportionate independent #150 review
  before stage merge. Scientific/native compatibility remains pending.
