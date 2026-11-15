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
Also test the legitimate new-case incomplete scalar classification. Computed new-case
`not_run` or unknown scalar classifications now fail, rather than being
silently treated as legitimate incompletes.

A repeatable `--require-case CASE_ID` argument (or several arguments) pins
exact registered CMD-eligible source-admission IDs for a selected feature.
A required case reverting to `source_unsupported`, lacking a complete printed
horizon, or missing/failing its scalar classification forces exit 1 without
relabeling that case. A correctly `incomplete` scalar is reported in
`required_case_scalar_incomplete` and **does not masquerade as a scalar pass**.
Unknown or repeated required IDs fail before any simulation. This is
required-case coverage control, not an acceptance of an incomplete field.

**Limitations:** this guard does not silently promote unadmitted cases.
Previously unadmitted `source_unsupported` cases remain honestly excluded
unless the verifier explicitly supplies their IDs with `--require-case`.
Feature owners and the verifier must name the exact accepted original
population and distinguish incomplete scalar fields from accepted passes.
A clean out-of-checkout installed wheel can use a verified `pip --target`
directory or a venv `site-packages` under the separate reviewed isolation
policy proposed in #126; original CMD fields/clock/site still require evidence.
The guard requires separate independent review before its result is used to
qualify any #90–96 engine revision. No new source/wheel execution, native CMD
run, feature signoff or gate #5 closure is claimed by this work record.
