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
