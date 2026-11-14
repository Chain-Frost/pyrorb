# Curated public CMD regression transfer

Status: locally verified and pushed for draft review; no numerical stage closure. Updated/reviewed: 2026-11-15 (Australia/Perth). Tracks [public #81](https://github.com/Chain-Frost/python-runoff-routing/issues/81) and [private #56](https://github.com/Chain-Frost/runoff-routing-investigations/issues/56). Stacked on public #80 at `e3a4e5239287195208390ba48e85aa9d8997ae82`; #78/#80 remain draft dependencies, not merged here.

## Revision and transfer

**Exact tested source/data revision: `dd4aade8367eae8369b6fba4295bfbfec55354ea`.** Subsequent changes in this branch are documentation/validation receipts only. Source: private PR #65 at `78d257745e94cdca74d1fdcdc8a615d472a8bf9c`; original register SHA-256 `a9b74dafe5466491a3ed102a3649df72b992e38c915699934f47096a0228e6f7`.

All **50 cases** (44 archive / six supplemental) are available through the existing public register/runner. All 21 native incomplete records and the original 14 authored case records (ten independent controls / four gaps) remain; all analytical reference bytes are unchanged. No second register or testing framework was introduced.

**214 unique payload files / 2,379,558 bytes**, from 245 original-identity ledger records. There are 212 content-addressed objects and two retained candidate snapshot payloads. The ledger has 134 path-sanitised original identities, 110 byte-identical identities and one lossless gzip CSV. Deduplication preserves explicit per-case references and each original hash. Source/event bindings include the required original capture manifests where they are the authenticated binding; unrelated manifests/logs, traces, executables, manuals and research implementations are excluded.

All 1,026 indexed original files authenticated before and after transfer and again after final replay; all 415 independent custody-receipt files authenticated during curation. All six supplementary original model/storm/parameter files, reports and typed/source bindings were authenticated before copying. Independent original-versus-public inspection verifies every one of the 19,550 report rows, raw clock tokens, full horizons, physical sites, effective settings and scalar selectors unchanged. Path derivatives retain byte positions/line endings and distinct original/published hashes. Historical permission text within original bindings describes the capture-date permission; the owner's 2026-11-15 approval supersedes it prospectively without rewriting original bytes.

## Actual verification

[Machine-readable receipt, exact executed commands, hashes and counts](evidence/issue81/verification.json), [all scalar field results](evidence/issue81/full-scalars.json), [all ordinate results](evidence/issue81/full-ordinates.json), [85-case coverage ledger](evidence/issue81/all.json). Published result derivatives replace personal temporary paths with `$Verify`; original local output hashes and published derivative hashes are separate. [Dataset guide and repeatable commands](../REGRESSION_DATASET.md).

Windows / Python **3.14.6**, Ruff **0.16.6** lint/format and strict Pyright pass (zero errors/warnings), repository hygiene passes. **Source full suite: 780 pass / one skip. Fresh installed-wheel full suite: 780 pass / one skip.** The existing `test_symlink_escape_rejected` skips because file symlinks are unavailable on this filesystem; no ACL/elevation change was attempted. All other tests execute. A first wheel-scaffold attempt omitted `.github` and failed its existing workflow-presence test; the documented copy command was corrected and full fresh verification then passed. The final exact revision includes explicit per-case policy labels for mixed native/analytical evidence.

Runner wheel SHA-256: `cc16ccf4fb90cf18942070891a1c3ea7caf9a946b0968f4378e2f0454955e090`. All **40 package members** match tested source, wheel ZIP and installed bytes. Installed commands use an isolated environment, outside-checkout working directory, `-I`, no source PYTHONPATH and an asserted site-packages origin. Tests inspect copied scaffold files but import the installed package.

Source and wheel commands actually exercised preflight, one-case diagnosis, timestep subset, all50 ordinates, all50 scalars, native-all71, all85 and authored controls. Tampered snapshot bytes exit2; focused existing tests cover changed reference tokens/bytes, omitted/extra print columns, shifted clocks, incomplete horizons, duplicate mappings, missing custody, altered source/candidate module/input identities and invalid hexadecimal values including float.fromhex overflow. Source/wheel per-case results agree exactly.

After push, a **fresh HTTPS clone from the public GitHub branch**, without private data or RORB, reproduced full preflight (50 verified / 227 indexed published files) and all50 scalar results using the isolated runner wheel. Its case records agree with source/wheel verification.

| Gate | Result |
| --- | --- |
| Complete ordinate rows | 50 pass / 19,550 rows; exit0 |
| Peak magnitude | 50 pass |
| Peak time | 48 pass / two incomplete: fig67-zero, wheel-zero |
| Native reported volume | 50 pass |
| Complete scalar aggregate | 48 pass / two incomplete; exit1 |
| Native-all71 | 50 verified / 21 incomplete; exit1 |
| All85 | 60 verified / 25 incomplete; exit1 |
| Ten independent authored controls | 10 verified; exit0 |

No differences from the original bounded 50-case numerical baseline. Reported volume remains the native inclusive sample statistic, separate from physical volume/conservation. The candidate is the authenticated **prior source-execution snapshot** at `fea9c80c521127325b779ea0ea87ddf77795b290`, not fresh execution or acceptance of the public production solver. The qualified backend #75, exact native ties, sub-print clocks and independently budgeted conservation remain open.

## Key hashes and next action

- Public register: `59b478181671cb19ff5d2e1df9ed5edf6bddeb3065556a536cf9f2bd5c806b1c`.
- Published file index: `2d7285feb413dea281dbe886042d399ce7ae869d626133de4424557cf5be0c17`.
- Transfer provenance: `77b4273dd1fb5bdd7c85022bc96dbdd881c09976630d69caa16db6bba61bf059`.
- Frozen scalar policy: `a0be5aa27e61813b120a30aaa8527961365c88af81ea77e881585bf68703bd50`.
- Original archive index: `492dd5d160d14fc354d1ac9b7b316f5857bb8ff316f4d56ad3727c645f23265d`.

Next action: review the draft data PR in dependency order after #78/#80; integrate actual backend-generated candidates through this same runner when #75 is qualified. The owner approved only curated run-data publication. Historical authorisation/original bytes remain unchanged. No native run, tolerance/default change, new hosted automation, merge, release or numerical-stage closure occurred. Existing hosted CI is separate from the local source/wheel evidence above.
