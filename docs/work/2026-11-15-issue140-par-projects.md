# S5 issue #140 — PAR-led import and source-bound edited projects

**Date:** 15 November 2026. **Branch:** `feat/issue-140-par-import`. **PR:** [#159](https://github.com/Chain-Frost/python-runoff-routing/pull/159), **issue:** [#140](https://github.com/Chain-Frost/python-runoff-routing/issues/140). **Status:** implemented on a separate draft PR; quality/review disposition to be confirmed at the exact final head; no merge.

## Changes and bounded contracts

- A pure content inspector recognises the documented CMD `# BEGIN` layout; a narrow authentic-RORBwin-saved-PAR signature is recognised but deliberately unsupported; other bytes remain unknown or invalid. No suffix-based fallback or RORBwin numerical inference.
- PAR filename discovery and filesystem resolution are kept outside the parser; catchment/storm explicit overrides supersede embedded tokens. Foreign Windows/UNC reference handling refuses speculative POSIX mappings. Missing files produce role/declared-token/override diagnostics.
- Original sources are copied byte-for-byte into role-distinct hash-pinned destination paths, with immutable `source_bindings` retaining original spelling, selected spelling, resolution origin and staged destination. Reopen requires only these staged assets, never the original source location.
- Existing S1 typed `RunModel` is reused; schema-3 project metadata holds `effective_run` when edited. `load_project` and run/result/export-run consumers use that model, while original PAR evidence remains immutable. Older schema-1/2 engine semantics and explicitly selected engines remain unchanged.
- CLI/API cover inspection, PAR-only import, override/base, typed edits, save-as and relocation. Native runnable export remains with #141; domain enum/effective-event edit functions remain with #138; CATG authoring remains with #139.

## Authentic recognition evidence versus tests

The private evidence repository contains four independently inspected native RORBwin saved-PAR captures, all with 755 nonempty/blank record positions plus a terminal newline, directory/CATG/STM field header, expected control/ARR markers and long numeric `-999.00` tables. Distinct Git blob IDs: `c2a07ad26be6775df08cfcf1fa02b601e76a4204`, `67c8b648fd2a767bad98d11d66c993c110a493ef`, `f5a237ed03161e9aeddd8a1228a009a6e71076ca`, `1b489701037f6f6f45dc3d2866a89d833ba0ef27`. The implemented lexical signature was independently checked as positive on all four actual records. This is **structure authentication**, not universal GUI version compatibility. The public tests use a constructed, structure-matching fixture; original private bytes are neither added to the public repo nor made runtime dependencies.

## Validation boundary

Tests for content classification, paths, override precedence, collisions, missing/invalid references, staging, edited/reopened model identity, relocation, no-clobber and CLI are supplied. Final CI outcomes must be attached to the PR at its final head. Strict isolated-wheel and original CMD regression receipts are required before full software closeout. Windows-native run/GUI saved-PAR import and independently runnable CMD export are explicitly **not claimed** here. RORBwin execution remains unsupported. No original golden was updated.

**Next:** complete quality checks and review at exact head, reconcile #138 effective-model interface and #141 CLI/export handoff, leave #140 open until accepted by reviewer.

## Independent review findings addressed on the active PR

Codex reviewed `4dcad73e39` and identified two issues:

1. **P1 native attribution:** the opt-in S0 native capture could silently use original immutable CATG/STM bytes for an effective edited `RunModel`. The native preflight now checks `LoadedProject.original_run` against the requested effective catchment and storm (including per-event changes) and rejects mismatches before invoking any executable. It also refuses verbosity that S0 capture would silently force to 3. Focused tests patch native capture to prove it is never invoked for changed models.
2. **P2 legacy positional CLI:** three-file positional CATG/STM arguments previously belonged to the command working directory. They are now absolutised immediately at the CLI boundary. New explicit `--catchment`, `--storm`, `--base` still resolve relative to the documented PAR/base directory.

The shared project dispatcher now delegates `export-native` to #141's `native_export.main` when available; #141 owns the exporter and #138 owns event edit resolution. Main branch integration preserves newer evidence receipts; tests and exact-head validation will be reported separately. Review findings are not treated as resolved until tested.

## Second independent review — source identity and relocation containment

The next Codex review at `0c3e6cc900` found two more concrete cases, corrected on a later #159 head:

- **Recorded-native review:** `review_project_native_capture` also consumed the effective edited model but compared its original source hashes. The shared `LoadedProject.original_inputs_match_effective()` contract is now applied in both native execution and recorded-capture review. Changed CATG or STM semantics fail with an actionable source-identity diagnostic **before** reported numerical differences can be produced. A manufactured original-source evidence fixture tests both changed roles and confirms the original manifest remains byte-identical.
- **Relocation containment:** a pre-existing destination `sources` symlink previously permitted `mkdir(parents=True)` outside the target *before* a later containment check. The directory walker now checks every existing ancestor for symlinks, creates missing components one at a time under the verified root, and refuses any unsafe parent before outside mutation. A symlink escape regression proves no external directory is created.

The source test suite, strict Ruff/Pyright, fresh original CMD probe and installed-wheel checks are qualified only by CI at the final exact head, not an earlier success. #140 remains a focused PR; there is no native numerical or general GUI PAR support assertion.
