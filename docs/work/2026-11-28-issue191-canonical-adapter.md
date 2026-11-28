# #191 Phase 2 — canonical printed-observation adaptation (28 November 2026)

Depends on [#247](https://github.com/Chain-Frost/pyrorb/pull/247), exact reviewed reader commit `39153cd650040accfcfea05b6dfaea91feae890d`. This dependent branch adds only the adapter, focused tests and this work/index record. It does not publish additional private artifacts or alter the four approved candidate files. Scientific #150/#148/#228/#9 and native-method qualification remain separate.

## Result and contract

`monte_carlo_report.native_mc_comparison_records(document, cohort_id=..., replication_id=..., scenario_id=...)` consumes the canonical reader document and existing Phase 1 `MCNativeSource`, `MCEventKey`, `MCNativeRecord` and `MCField` contract. It supplies explicit caller cohort/replication/scenario context, source-report/version identity, duration/division/run and native rank, while keeping physical site, source EventID, Python sample identity, peak m3/s, rainfall probability and event weights unavailable.

The canonical report has a unitless printed peak and ambiguous AEP/ARI/1inY wording. Neither may become an available `peak_m3s` or probability field by convention. `native_mc_report_json_ready` therefore preserves the unbound original tokens, lines and report-local output ordinal **separately** from the unchanged Phase 1 comparison record. Printed depth/factor units come from admitted legend labels; missing units remain null. Diagnostics/extrema/selected-probability rows and summary warning markers remain descriptive printed evidence, not native weights, inverse law or sampled-event rows. Parameter echoes are labelled displayed settings, not committed historical effective inputs. No source model paths are exported by this adapter.

Phase 1 readiness is unchanged: exact replay, native weighted reaggregation and published-frequency acceptance remain unavailable; unresolved probability meaning also keeps that input-law lane unavailable. Supplemental printed diagnostics have a separate descriptive-only label. Explicit caller replication IDs do not establish independent native streams. Printed zero is retained as a rounded token, not promoted to exact zero or failure.

## Integrity and precision

`RorbDocument` is mutable. The adapter checks retained-byte digest and reuses the **same canonical reader**, comparing source lines, sections, metadata, kind and validity before accepting observations. This is a binding check, not a second text grammar. Edited tokens, convenient row values, fabricated units/complete flags, missing bytes and substituted context fail closed. Duration-to-whole-minute keys use exact integer-ratio arithmetic independent of ambient Decimal precision; unrepresentable subminute keys are rejected rather than rounded.

The pure adapter does not open files, follow model references, sample, route, launch native code or change frequency/sampler/engine policies. The original Phase 1 module and its tests remain unchanged. No native simulation or original-report publication is authorised or performed.

## Validation and integration boundary

Focused adapter/Phase 1/reader suite: **76 passed**. Full isolated-environment check passed repository hygiene, Ruff 0.16.6 lint/format, strict Pyright and **1,786 tests**, with eight expected Windows symlink-permission/POSIX-path skips, on Windows 10/Python 3.14.6. A separate agent independently executed the 76 focused tests and four additional binding/readiness controls and found no remaining working-tree issues. Installed-wheel/source identity, complete individual 50-case probe equality and final exact-head PR review are recorded in PR/issue receipts before readiness is claimed. Existing pinned public ordinary-reader fixtures are used, not private numerical evidence. Deliberately preserved CRLF fixture bytes belong to the parent reader PR.

F1–F6 is **not** a prerequisite for this bounded adapter. Broader #191 native method, weighting, replay and physical-site comparison remain unresolved and must not be closed because this software is reviewed. Integrate #247 first, then this dependent PR only with owner merge authority. No automatic merge, release or new workflow.
