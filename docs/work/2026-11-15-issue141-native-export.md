# #141 — bounded portable CMD export implementation

**Date:** 15 November 2026 (implementation); 16 November 2026 (software merge closeout)  
**Owner:** #141 native package/export; #138 shared effective settings, #139 edited CATG/STM writers, #140 PAR import/source bindings/CLI.  
**Initial base inspected:** `main` at `0675d75b05dba7728b389fdd8af743060b4469b2`.  
**Final reviewed PR head:** `280aea19db8b9e52f8115d25f1975b68e537f8de`.  
**Merged software revision:** `766b56a8ba6fe42785f05bb5d8df51a741a07e2c` ([PR #162](https://github.com/Chain-Frost/python-runoff-routing/pull/162), squash to `main`).  
**Disposition:** Bounded software export merged after review; strict native executable/verbosity/numerical gates remain open in #141/#143.

## Delivered in isolated files

- `src/runoff_routing/native_export.py`: typed explicit CMD 6.44 target, effective-event input records, source hash re-verification, source-exact CATG/STM reuse, canonical effective path-rebound PAR, supported semantic STM edits, strict emitted-triplet reparse, independent event folders, safe staging and no-overwrite, hashes/provenance/events/output-status manifest, native-only `run.cmd` and plain README.
- `tests/test_native_export.py`: source-authenticated retained original triplet, relocated package, actual emitted PAR and event semantics, kc/m/loss edits, verbosity 1/2/3, batch isolation, semantic storm writer, overwrite and partial-stage rejection, edited CATG rejection, project source corruption and text-file event-request CLI.
- `docs/NATIVE_CMD_EXPORT.md`: API, standalone CLI, native invocation, evidence distinctions and handoffs.

## Verified current software revision

At exact PR #162 head `280aea19db8b9e52f8115d25f1975b68e537f8de`, [Windows quality #43746408987](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43746408987) completed **SUCCESS** using CPython 3.13.17: repository hygiene 527 files / 0 errors; pinned Ruff lint and format; strict Pyright; **1,198 source tests passed / three expected POSIX-only foreign-path skips**, including the actual PyRomb edited CATG and Windows launcher stub; both required original-source public CMD probe gates; isolated wheel built (SHA-256 `026fe63bebb14615f28f388899a7415c6787a51373c738327eeeba01d4f06b4f`); **177 selected installed-wheel tests passed**; full and partial CLI report/fail-closed controls; installed-wheel CMD probe passed. Both fresh public probes checked 50 original CMD cases with 48 reporting-scalar passes and two preserved incompletes, not a new native run.

The exact-head Codex review completed **without findings** and all historical inline findings were resolved. The PR contained only the four #141-owned files. No GUI, new numerical solver, reference mutation, licensed executable or native-output fabrication was introduced.

## Outstanding independent acceptance

- **Native CMD execution: NOT RUN.** On an authorised Windows system, relocate the generated package, run the *actual emitted* `events/NNN/model.par` with the reviewed RORB CMD 6.44 executable (not a capture-generated substituted PAR), and record exact executable identity/version/SHA-256, working directory, command, PAR hashes before/after and real generated output paths/hashes.
- **Verbosity/output characterisation: NOT VERIFIED.** Run native verbosity 1, 2 and 3 without raising any requested setting, record outputs available for each, and distinguish optional outputs from required inputs. The existing tests verify serialized verbosity and launcher mechanics, not the native executor's output availability.
- **Numerical equivalence: NOT ASSESSED.** When claimed, compare independently authenticated full matched outputs using the existing comparator; never infer parity from parser or wheel software tests. Native/physical site identity and scalar precision remain governed by #5/#143.
- The PyRomb edited writer remains optional and pinned to the reviewed fork pending upstream admission. Unchanged CATG does not need it. No alternate local CATG renderer is introduced.

**Next action:** #143/native acceptance owner should execute, authenticate and independently review a relocated emitted-PAR run under the correct CMD 6.44 executable and record precise gate verdicts. Keep #141 open only for those native acceptance decisions; #5/#7 remain separate until qualified.

The #141 issue remains open for native acceptance; bounded software integration is merged. #7/#5 remain independently open. No CLI GUI, second CATG writer, new solver, broad forensic work or executable redistribution is part of this slice.
