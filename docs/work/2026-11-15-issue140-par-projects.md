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
