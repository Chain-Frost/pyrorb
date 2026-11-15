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

At initial authoring this run uses GitHub connector writes; the local environment cannot clone GitHub, and no supported Windows native executable is available here. The source/wheel quality checks and required relocated *native Windows* execution are **not run** by this authoring session. Subsequent exact-head repository CI and independent review must be checked at the PR head; a green CI report is not native execution.

Each successful software export has an emitted-byte hash and in-process reparse, with manifest state `native_execution=not_run` and `numerical_equivalence=not_assessed`. No new RORB goldens, source reference bytes or numerical comparators are changed. No target output-name/verbosity-output availability claims have been admitted.

## Integration gates / next actions

1. #138/#140 should expose the selected effective `RunModel` and retained source-role bindings for run/save/native export, and wire the new command handler to their shared project dispatcher. The standalone CLI now imports #138's public `resolve_effective_model`, not private #119 helpers; PR #162 is stacked on #138 PR #157 until that shared contract merges.
2. #139 should provide the reviewed PyRomb edited-CATG adapter; the exporter intentionally rejects changed catchments until an actual upstream writer can round-trip their order, physical lengths, FI and metadata.
3. Run focused source tests, Ruff/Pyright, Windows quality CI, and installed-wheel checks on the **exact integrated head**; track exact revisions, skips and failures.
4. On an authorised Windows machine, move the package, execute the *emitted* `model.par` (not S0 capture-generated PAR), hash it before/after, record executable version/SHA/cwd/argv and all actual output/verbosity observations. Only then assess numerical evidence via the existing comparator.

The #141 issue remains open for integration and native acceptance; #7/#5 remain independently open. No CLI GUI, second CATG writer, new solver, broad forensic work or executable redistribution is part of this slice.
