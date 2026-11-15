# Independent CMD probe failure-propagation control (2026-11-15)

**Scope:** issue #5, new #90–96 feature reviews, separately reviewable comparator/status guard.

The maintained `cmd_public_probe.py` already hard-gates 36 originally retained cases.
Newly admitted cases could otherwise have a printed-discharge or scalar comparator
failure without making that probe's exit status nonzero. This patch adds a strictly
**diagnostic** nonretained-case failure gate. A nonretained computation's
`printed_fail`, `printed_invalid`, attribution error, truncated sample count,
or qualified fresh-scalar `fail`/`invalid` now causes nonzero exit, retaining the
case's original `first_mismatch`/reason in its JSON record. `source_unsupported`
remains explicit/not admitted and does **not** become an acceptance pass. Fresh
scalar `incomplete` (H2 time, undefined zero-flow peak) remains incomplete
without artificial all-metrics success.

**Policies unchanged:** `cmd644-printed-interval-v1` / `cmd644-report-scalars-v1`.
No tolerance, reference object, original timestamp, original site mapping,
case register, numeric engine, runner, CMD executable or golden changes.
The historical snapshot and independent reference evidence remain separate.

**New tests:** manufactured failure states for Q, invalid comparison,
scalar failure/invalid, wrong horizon and attribution; retained 36 cases
still pass in these controls, so a new-case failure cannot hide behind them.
Also test the legitimate new-case incomplete scalar classification.

**Limitations:** this is not a coverage-promotion gate: previously unadmitted
`source_unsupported` cases remain honestly excluded. Feature owners and the
independent verifier must explicitly pin and check required new case IDs at
acceptance, along with a site-packages installed wheel and original CMD fields.
The guard requires separate independent review before its result is used to
qualify any #90–96 engine revision. No new source/wheel execution, native CMD
run, feature signoff or gate #5 closure is claimed by this work record.
