# Current implementation and acceptance status

**Original reconciliation on 17 November 2026 against main [`1a5175ad`](https://github.com/Chain-Frost/python-runoff-routing/commit/1a5175ad9dbf6be03d78b164b169b3ec836e6a9e); provisional MC software admission updated 23 November 2026.** This page is the current delivery summary. [BACKLOG.md](BACKLOG.md) assigns remaining work; the [single CMD feature matrix](CMD_FEATURE_MATRIX.md) retains feature-level evidence and the [work index](work/README.md) links dated receipts. Historical work notes describe their recorded revisions and do not assign new work.

## Product boundary and engines

Deliverables are CLI, Python API and text-file inputs/outputs. The temporary project/CLI default is `python-cmd/cmd-6.44`. Independent `python/engineering-v1` remains explicitly selectable and the intended long-term default; `rorb-cmd` is explicit and optional. Engine-less schema-1 projects retain their historical `python` meaning, and stored choices never migrate silently. Modern graphical CATG (including characterised content named `.cat`), STM and CMD PAR are supported within their documented subsets. Old plain computational CAT and combined DAT are excluded; saved RORBwin PAR remains deferred under #144. No GUI work or planning is included.

## Delivered on main

| Delivery | Current result and maintained guide |
| --- | --- |
| CLI/text-file MVP #119 / PR #128 | Selected-engine single/ordered explicit events, prepared model reuse, complete JSON/CSV/text and failure isolation. [Project/batch workflow](PROJECT_BATCH_MVP.md). |
| Original-source and compatible feature software | #132 admitted the 14 former original-source exclusions; #108/#111/#113/#120 deliver bounded loss, reach, ordinary code-7 and code-2 controls. Native feature/physical gates remain #90–#92/#96. |
| Independent Python counterparts #110/#125 | Merged mode-2, code-2/per-source impervious computation and typed adapter. [Engineering method](ENGINEERING_METHOD.md); wider accuracy and deferred #103 remain separate. |
| Typed editing, PyRomb writing and PAR import #138–#140 | Complete through #157/#166/#159. [Typed editing](TYPED_PROJECT_EDITING.md), [PAR projects](PAR_PROJECTS.md), [PyRomb authoring](RORB_GE_AUTHORING.md). The owner-accepted pinned PyRomb writer remains the sole edited-CATG renderer. |
| Portable export #141 and independent acceptance #143 | Complete through #162/#160. Five actual relocated CMD packages ran successfully, with 15 unchanged input hashes and 1,005 parsed native ordinates. [Export](NATIVE_CMD_EXPORT.md), [interoperability](S5_INTEROPERABILITY.md), [final acceptance](https://github.com/Chain-Frost/pyrorb/issues/143#issuecomment-6906855635). |
| Canonical report reader #142 | Complete through upstream ryan-tools #233 and downstream #165/#185; installed dependency pinned to permanent merge `8940f46b251f4d2ba6e52d6cb2ef74cd71fbe33f`. The authorised 490-event RORBwin 6.45 alternative and 640 RORBwin 6.52 associations are accepted reader evidence. The historical 420-pair population was not rechecked and is no longer an admission blocker. [Reader closeout](https://github.com/Chain-Frost/pyrorb/issues/142#issuecomment-6906627408). |
| Deterministic rainfall #136 and explicit written-depth profile #175/#177 | Delivered. The opt-in `published_arf_stm_2dp` profile matches all 60 original written storms / 1,320 reconstructed increments; the existing published-method default is preserved. [ARR design workflow](ARR_DESIGN_BATCH.md). |
| Deterministic result reporting #155 | Read-only persisted-result summaries are delivered. #152 remains open only for separately qualified native representative/critical-duration rules. [Result summaries](ARR_DETERMINISTIC_RESULTS.md). |
| **Provisional Monte Carlo #9 — PR #151** | Versioned B/E/C sampler, persisted sample plans, routed events, immutable replay/extension, per-site weighted frequencies and text reporting are admitted as **software only**, with the adopted `monte-carlo-statistics/1` method. Native RORBwin sampling/frequency agreement, full flood-AEP probability support, physical-catchment convergence and engineering acceptance are **not assessed**. [MC method](MONTE_CARLO.md), [execution](MONTE_CARLO_EXECUTION.md), [frequency limitations](MONTE_CARLO_FREQUENCY.md). |

The bounded evidence tasks #137 and #175 are closed. Their closure does not establish original RORBwin internal effective-input arrays, native ARF arithmetic, routed equivalence or selection rules. The earlier 1,320-increment mismatch remains a valid historical observation for the former full-precision preparation; it is not the current result of the explicit written-depth profile.

## Verification and remaining scientific limits

Main's [post-merge CI](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43800975583) passed. The [#143 final receipt](https://github.com/Chain-Frost/pyrorb/issues/143#issuecomment-6906855635) records the tested source/merged-tree identity, 1,243 source tests, three expected skips and 204 isolated-wheel tests. These are audited existing results, not a new simulation run for this documentation update.

The maintained original CMD population retains **50/50 printed Q cases / 19,550 ordinates**, **48 reporting-scalar passes and two undefined all-zero unique peak-time incompletes**. The [original register and comparator](REGRESSION_DATASET.md) preserve source, raw-clock, site and metric distinctions. Cached `--snapshot` output is historical candidate computation, not execution of today's engine.

The reopened [CMD gate #5](https://github.com/Chain-Frost/pyrorb/issues/5) retains full feature, physical-site and scientific requirements. Successful native process execution and reader fidelity do not establish numerical equivalence; #143's native reader outcomes remain partial and physical-site/reference limits remain explicit. Original code-11/site, mode-2, reach/error and distinct PR16 producer qualification remain #90–#92/#96. Independent Python accuracy is not inferred from CMD-compatible printed matches.

## Active work outside the delivered slices

- **PyRORB identity and release preparation — 22 November 2026:** [#212](https://github.com/Chain-Frost/pyrorb/issues/212) carries current branding, repository links and the `pyrorb` distribution name into the open PR stacks, preserving `runoff_routing` imports and compatibility identifiers. [#213](https://github.com/Chain-Frost/pyrorb/issues/213) prepares a separate inactive publication draft under #10; final dependency qualification, release selection and activation remain deferred until the MVP is finalised. See the [scope and verification record](work/2026-11-22-pyrorb-identity.md).

- **Rainfall science #8:** [#192](https://github.com/Chain-Frost/pyrorb/issues/192) qualifies ARR2019 ARF arithmetic against observable native evidence; [#193](https://github.com/Chain-Frost/pyrorb/issues/193) verifies ARR2026 ARF applicability and any authoritative method changes. A documented no-change result is valid for #193. Neither reopens the completed #137/#175 scopes.
- **Deterministic selection #152:** bind complete native populations, physical sites and effective events; establish an evidenced statistic, ties/missing-member policy and duration rule. Use the merged canonical reader. Current native representative and critical-duration selections remain null/unverified.
- **Monte Carlo science #9 remains OPEN after provisional software delivery:** [#151](https://github.com/Chain-Frost/pyrorb/pull/151) admits only B/E/C software and bounded synthetic controls; [#150](https://github.com/Chain-Frost/pyrorb/issues/150) has no authenticated complete exact effective-event export, and #189/#190/#191/#148 retain native law, frequency/tail, canonical comparison and real-catchment replication/budget questions. The 25-event RORBwin pilot is not an equivalence or 1,000-run adequacy study. No release or publication through draft #215.

Advanced #114–#118, physical #103, saved RORBwin PAR #144, optional #63 and release #10 remain separately tracked and deferred. Completed #75/#6/#76/#104/#119/#137/#138–#143/#175 stay completed within their finite scopes.
