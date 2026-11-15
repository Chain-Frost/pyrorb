# #141 — bounded portable CMD export implementation

**Date:** 15 November 2026  
**Owner:** #141 native package/export; #138 shared effective settings, #139 edited CATG/STM writers, #140 PAR import/source bindings/CLI.  
**Base inspected:** `main` at `0675d75b05dba7728b389fdd8af743060b4469b2`.  
**Branch:** `feat/141-native-cmd-export` (stacked on #138 PR #157).  
**Review/merge:** Review required; do not merge under this scope without owner instruction.

## Delivered in isolated files

- `src/runoff_routing/native_export.py`: typed explicit CMD 6.44 target, effective-event input records, source hash re-verification, source-exact CATG/STM reuse, canonical effective path-rebound PAR, supported semantic STM edits, strict emitted-triplet reparse, independent event folders, safe staging and no-overwrite, hashes/provenance/events/output-status manifest, native-only `run.cmd` and plain README.
- `tests/test_native_export.py`: source-authenticated retained original triplet, relocated package, actual emitted PAR and event semantics, kc/m/loss edits, verbosity 1/2/3, batch isolation, semantic storm writer, overwrite and partial-stage rejection, edited CATG rejection, project source corruption and text-file event-request CLI.
- `docs/NATIVE_CMD_EXPORT.md`: API, standalone CLI, native invocation, evidence distinctions and handoffs.

## Verification and non-acceptance

GitHub Windows quality run `43728094889` passed on `d5f13a6639b78b4d3c40d7729b9be4331f9360bc` (Python 3.13) after correcting the reviewed signed negative-exit handling: source tests, Ruff, strict Pyright, original CMD source regression, wheel build, isolated-wheel tests and original CMD installed-wheel regression. This is a **historical exact-head receipt**; subsequent changes require a fresh head validation. Actual relocated native RORB CMD execution with the real executable remains **not run**.

Each successful software export has an emitted-byte hash and in-process reparse, with manifest state `native_execution=not_run` and `numerical_equivalence=not_assessed`. No new RORB goldens, source reference bytes or numerical comparators are changed. No target output-name/verbosity-output availability claims have been admitted.

## Integration gates / next actions

1. The exporter consumes #138's public `resolve_effective_model`, #140's canonical staged `LegacyRunFiles`, persisted `LoadedProject.run` and serialized input binding provenance. #140 still owns shared project dispatcher delegation; PR #162 remains stacked on #138 PR #157 until the contract is reviewed and integrated.
2. Edited CATG with an explicit validated `GeDrawing` now calls #139's PyRomb-backed `serialize_catg_with_drawing`, and reparses the result. Until #139 PR #166 is present with the reviewed PyRomb dependency, changes fail explicitly; unchanged originals are exact-copied without that dependency. Cross-branch integrated tests are still required.
3. Run focused source tests, Ruff/Pyright, Windows quality CI, and installed-wheel checks on the **exact integrated head**; track exact revisions, skips and failures.
4. On an authorised Windows machine, move the package, execute the *emitted* `model.par` (not S0 capture-generated PAR), hash it before/after, record executable version/SHA/cwd/argv and all actual output/verbosity observations. Only then assess numerical evidence via the existing comparator.

The #141 issue remains open for integration and native acceptance; #7/#5 remain independently open. No CLI GUI, second CATG writer, new solver, broad forensic work or executable redistribution is part of this slice.
