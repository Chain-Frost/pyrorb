# Current implementation and acceptance status

**Reconciled on 17 November 2026 against public main [`1a5175ad`](https://github.com/Chain-Frost/python-runoff-routing/commit/1a5175ad9dbf6be03d78b164b169b3ec836e6a9e).** This page is the current delivery summary. [BACKLOG.md](BACKLOG.md) assigns remaining work; the [single CMD feature matrix](CMD_FEATURE_MATRIX.md) retains feature-level evidence and the [work index](work/README.md) links dated receipts. Historical work notes describe their recorded revisions and do not assign new work.

## Product boundary and engines

Deliverables are CLI, Python API and text-file inputs/outputs. The temporary project/CLI default is `python-cmd/cmd-6.44`. Independent `python/engineering-v1` remains explicitly selectable and the intended long-term default; `rorb-cmd` is explicit and optional. Engine-less schema-1 projects retain their historical `python` meaning, and stored choices never migrate silently. Modern graphical CATG (including characterised content named `.cat`), STM and CMD PAR are supported within their documented subsets. Old plain computational CAT and combined DAT are excluded; saved RORBwin PAR remains deferred under #144. No GUI work or planning is included.

## Delivered on main

| Delivery | Current result and maintained guide |
| --- | --- |
| CLI/text-file MVP #119 / PR #128 | Selected-engine single/ordered explicit events, prepared model reuse, complete JSON/CSV/text and failure isolation. [Project/batch workflow](PROJECT_BATCH_MVP.md). |
| Original-source and compatible feature software | #132 admitted the 14 former original-source exclusions; #108/#111/#113/#120 deliver bounded loss, reach, ordinary code-7 and code-2 controls. Native feature/physical gates remain #90–#92/#96. |
| Independent Python counterparts #110/#125 | Merged mode-2, code-2/per-source impervious computation and typed adapter. [Engineering method](ENGINEERING_METHOD.md); wider accuracy and deferred #103 remain separate. |
| Typed editing, PyRomb writing and PAR import #138–#140 | Complete through #157/#166/#159. [Typed editing](TYPED_PROJECT_EDITING.md), [PAR projects](PAR_PROJECTS.md), [PyRomb authoring](RORB_GE_AUTHORING.md). The owner-accepted pinned PyRomb writer remains the sole edited-CATG renderer. |
| Portable export #141 and independent acceptance #143 | Complete through #162/#160. Five actual relocated CMD packages ran successfully, with 15 unchanged input hashes and 1,005 parsed native ordinates. [Export](NATIVE_CMD_EXPORT.md), [interoperability](S5_INTEROPERABILITY.md), [final acceptance](https://github.com/Chain-Frost/python-runoff-routing/issues/143#issuecomment-6906855635). |
| Canonical report reader #142 | Complete through upstream ryan-tools #233 and downstream #165/#185; installed dependency pinned to permanent merge `8940f46b251f4d2ba6e52d6cb2ef74cd71fbe33f`. The authorised 490-event RORBwin 6.45 alternative and 640 RORBwin 6.52 associations are accepted reader evidence. The historical 420-pair population was not rechecked and is no longer an admission blocker. [Reader closeout](https://github.com/Chain-Frost/python-runoff-routing/issues/142#issuecomment-6906627408). |
| Deterministic rainfall #136 and explicit written-depth profile #175/#177 | Delivered. The opt-in `published_arf_stm_2dp` profile matches all 60 original written storms / 1,320 reconstructed increments; the existing published-method default is preserved. [ARR design workflow](ARR_DESIGN_BATCH.md). |
| Deterministic result reporting #155 | Read-only persisted-result summaries are delivered. #152 remains open only for separately qualified native representative/critical-duration rules. [Result summaries](ARR_DETERMINISTIC_RESULTS.md). |

The bounded evidence tasks #137 and #175 are closed. Their closure does not establish original RORBwin internal effective-input arrays, native ARF arithmetic, routed equivalence or selection rules. The earlier 1,320-increment mismatch remains a valid historical observation for the former full-precision preparation; it is not the current result of the explicit written-depth profile.

## Verification and remaining scientific limits

Main's [post-merge CI](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43800975583) passed. The [#143 final receipt](https://github.com/Chain-Frost/python-runoff-routing/issues/143#issuecomment-6906855635) records the tested source/merged-tree identity, 1,243 source tests, three expected skips and 204 isolated-wheel tests. These are audited existing results, not a new simulation run for this documentation update.

The maintained original CMD population retains **50/50 printed Q cases / 19,550 ordinates**, **48 reporting-scalar passes and two undefined all-zero unique peak-time incompletes**. The [original register and comparator](REGRESSION_DATASET.md) preserve source, raw-clock, site and metric distinctions. Cached `--snapshot` output is historical candidate computation, not execution of today's engine.

The reopened [CMD gate #5](https://github.com/Chain-Frost/python-runoff-routing/issues/5) retains full feature, physical-site and scientific requirements. Successful native process execution and reader fidelity do not establish numerical equivalence; #143's native reader outcomes remain partial and physical-site/reference limits remain explicit. Original code-11/site, mode-2, reach/error and distinct PR16 producer qualification remain #90–#92/#96. Independent Python accuracy is not inferred from CMD-compatible printed matches.

## Active work outside the delivered slices

- **Rainfall science #8:** [#192](https://github.com/Chain-Frost/python-runoff-routing/issues/192) qualifies ARR2019 ARF arithmetic against observable native evidence; [#193](https://github.com/Chain-Frost/python-runoff-routing/issues/193) verifies ARR2026 ARF applicability and any authoritative method changes. A documented no-change result is valid for #193. Neither reopens the completed #137/#175 scopes.
- **Deterministic selection #152:** bind complete native populations, physical sites and effective events; establish an evidenced statistic, ties/missing-member policy and duration rule. Use the merged canonical reader. Current native representative and critical-duration selections remain null/unverified.
- **Monte Carlo #9:** active only on draft [PR #151](https://github.com/Chain-Frost/python-runoff-routing/pull/151), not delivered on main. Specification, sampler, frequency analysis, execution/replay and bounded reporting slices #145/#146/#147/#149/#187 are complete in staging. The [current five-pack plan](https://github.com/Chain-Frost/python-runoff-routing/blob/ce51b2f975b92952315d957e6ecd31b8bcd342f2/docs/work/2026-11-17-issue9-rorb-statistical-method-scopes.md) assigns native evidence #150, versioned sampling #189, probability support/frequency policy #190, canonical comparison adaptation #191 and larger-sample comparison/budgets #148. Staging completion does not authorise a main merge or native-equivalence claim.

Advanced #114–#118, physical #103, saved RORBwin PAR #144, optional #63 and release #10 remain separately tracked and deferred. Completed #75/#6/#76/#104/#119/#137/#138–#143/#175 stay completed within their finite scopes.
