# #143 — independent S5 import/edit/export/report qualification

- Date: 15 November 2026.
- Issue: [#143](https://github.com/Chain-Frost/python-runoff-routing/issues/143), parents [#7](https://github.com/Chain-Frost/python-runoff-routing/issues/7) and [#3](https://github.com/Chain-Frost/python-runoff-routing/issues/3).
- Baseline inspected: main **0675d75b05dba7728b389fdd8af743060b4469b2**.
- Primary evidence: [public regression-v1 register](../../tests/fixtures/regression-v1/register.json), Git blob **10a6c6fcedd57f633a5e6b97b8d7066e4ab08d66**. This is a register *Git blob*, not a fixture SHA-256.
- Nature of work: incremental independent acceptance, not a replacement importer/exporter/reader or native numerical campaign. This record must be updated against the actual integrated heads of #138–#142.

## Fixed evidence subset

Use the five original CMD cases already selected for #119: review-design-baseline (201 rows), review-ensemble-tp1 (201), timestep-design-baseline-f2 (401), timestep-ensemble-tp3-f4 (801) and zero-loss-ensemble-tp9-f1 (201). Total **1,805 original printed rows**. These are existing registered identities, not five new independent native observations. Read original PAR/CATG/STM paths, SHA-256 values and exact byte sizes from the single maintained register rather than transcribing or regenerating an alternative catalogue. The test reads each registered checkout object and verifies those original file hashes and sizes independently before staging.

The new [independent acceptance tests](../../tests/test_s5_workflow_acceptance.py) verify unchanged parser source bytes, CMD/CATG/STM typed source assembly, project manifest save/reopen, relinking of unchanged project-local files after relocation, source order and hash retention, no-clobber, tampered/missing assets, unknown PAR and excluded plain CAT/DAT. Edited typed settings are stored as **embedded JSON**, reopened, and executed through single and explicit-event paths with the same stored python-cmd selection. It confirms original file bytes cannot silently mask that edit. Retained native CMD .out reading checks full row count, original one-based increment origin, timestep and source identity; it does not compare computed hydrology.

## Separated acceptance contracts

| Contract | At the inspected baseline | Scope still unqualified |
| --- | --- | --- |
| Source-exact no-op | Existing three-file import plus byte-preserving source/project relocation; new focused cases exercise original registered objects | PAR-only import/overrides and modified file-backed source bindings (#140); a relocated JSON project is not an executable native package |
| Semantic edited round trip | Edited typed RunModel saved and reopened through embedded schema-2 JSON; same selected settings reach single/event execution | Edited native PAR/STM/CATG reparse, explicit effective-model contract and edited structural/storm writer (#138–#141) |
| Portable native package | **Not run**; native package exporter not in baseline main | #141 emitted relocated PAR with dependencies and genuine direct Windows CMD launch without Python/helper rewriting |
| Native report reading | Existing local CMD .out reader records and registered 201/401/801 horizons | Canonical ryan-tools integration, original 6.52 301-row report and 80-row/eight-reference batch (#142) |
| Third-party writer/reader | **Not verified**; baseline pyproject has no runtime dependencies | Actual pinned, installable PyRomb writer called for new CATG (#139); actual ryan-tools canonical reader imported, local duplicate parsing retired (#142) |
| Numerical CMD equivalence | **Not claimed** by these tests | Existing single public comparator, original full Q/peak/clock/volume/status and independent #5 gate |

The original modern graphical source can have a .cat suffix and is admitted by content. Old plain CAT and combined DAT are excluded. Unknown PAR is explicitly unsupported; positive recognition of genuine RORBwin saved PAR with deferred support awaits #140. No invented RORBwin signature is admitted. Validation of both typed loss modes, enum/bool boundaries, event overrides and unsupported edit failures awaits the integrated #138/#140/#141 API. Unchanged PyRomb parameter-only export is a #141 qualification candidate, not a current claim.

## Original RORBwin 6.52 report bytes retained for canonical reader qualification

Two unchanged public source blobs have been admitted solely as a compact
reader-acceptance population in [tests/fixtures/s5-acceptance](../../tests/fixtures/s5-acceptance/README.md).
They came from the pinned
[ryan-tools-test-data revision f3c49e8](https://github.com/Chain-Frost/ryan-tools-test-data/tree/f3c49e867cd8a165e031217a148293a8968c2d88/RORB/12hr-areal-example).
Their exact Git-blob hashes were verified **on copy** (not reconstructed
line-endings or rounded numeric tokens): the 19,020-byte 301-row ordinary
report is `95826bccdbe1f2410ef372ef6b6c2c161d847b99`;
the 8,558-byte 80-event/eight-representative batch is
`08ae1d94ef74d666836c8d3fab842e6421851030`.
Focused tests re-verify both actual checkout objects with the Git-blob
algorithm. **Keeping original bytes is not proof that #142 parses them**:
canonical row and identity assertions are independently exercised only on
the separate unmerged integration snapshot, [test-only PR #172](https://github.com/Chain-Frost/python-runoff-routing/pull/172).

## Verification and execution provenance

The new test file is selected by the existing [approved Windows quality workflow](../../.github/workflows/quality.yml) in both the source suite and the installed wheel-target test suite. The wheel suite already checks the package's import origin outside the checkout; the tests read only the public checked-out fixture paths as evidence data. Repeat after the shared implementation PRs land. This neither adds hosted native execution nor changes the frozen comparator/case register.

Reproduce from the source checkout using Python 3.13 or 3.14 on one supported platform:

~~~sh
python -m pytest tests/test_s5_workflow_acceptance.py -q
python repo-scripts/check_local.py
python -m build --wheel
~~~

**Initial receipt:** this GitHub-only workspace had no local checkout, installed wheel or native Windows executable. Personally executed source tests, Ruff, strict Pyright, isolated-wheel tests and direct Windows CMD run are **not run**, not reported as passes. Add the exact PR head, CI job URL, compiler/tool versions, test counts, source/wheel hashes and observed outcomes after the hosted quality run. A CI result is a reviewed receipt, not a claim that this session ran its commands locally.

**Hosted Windows quality evidence, completed for tested code head `0971223c7de9b7749e330d1f31dbd0eff445896e`:**
[workflow #43725532603](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43725532603),
job `windows-python-313` **success** on CPython **3.13.17**.
The existing `check_local.py` gate reported repository hygiene **505 files/0 errors**,
Ruff **0.16.6** passed, strict Pyright **1.1.414** reported
**0 errors, 0 warnings**, and the source test suite reported
**1,097 passed** (including all 13 new #143 tests). The fresh source
36-case CMD probe passed. The wheel was built, copied outside the checkout and
imported from the separate target (not source). Its SHA-256 was
`f4c210bd8c95a04ed646f5c7596d251697b4f4490563621241b6e1171126b7b1`.
External installed-wheel pytest reported **154 passed**, including the same
13 #143 acceptance tests; the installed-wheel native regression probe and
existing CLI/provenance/negative-control smokes all passed. The maintained
CMD probe reported 50 `printed_pass` classifications; this is existing
computed-vs-retained CMD qualification, not an execution of a native CMD binary
or of the new PyRomb/ryan-tools dependencies. The original Windows quality
[run #43725349868](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43725349868)
had **1,092 passed and five new tests failed** because they incorrectly required
`parsed` rather than the current reader's deliberate `partial` status for
unverified physical print identity. That expectation was fixed in the tested
`0971223c` commit; it was not changed to imply native physical identity.
These results apply to that **exact tested code head and wheel**, not to
later commits or upstream integration.

**Incremental cross-PR review, separately from this tested branch:**
at #138 [PR #157](https://github.com/Chain-Frost/python-runoff-routing/pull/157)
head `74b051f7b055a2e669eb9aaba37317f938432603` the public
`resolve_effective_model` was introduced. At #140
[PR #159](https://github.com/Chain-Frost/python-runoff-routing/pull/159)
head `904d11bc6a3560a6d72e1e05b7ee3fb810612f51`,
the new `par_project_import.py` had an invalid `message = (...) from exc`
assignment and an adjacent duplicated raise; this specific compile blocker
was reported to that owner. At #141
[PR #162](https://github.com/Chain-Frost/python-runoff-routing/pull/162)
head `a8f8116fe563cfa7703b1f5053cecdeb2cb9d54b`, native export's
private `_event_run(loaded, fields)` caller was incompatible with #138's
new `_event_run(current: RunModel, fields)` signature. The owner was asked
to consume the public resolver and add a separate Windows stub-launcher
smoke for directory, arguments and error propagation. These observations
were **source reviews only**, not tests against an integrated build.
Refresh exact heads and verify corrections before clearing either gate.

At the inspected baseline, [PyRomb PR #16](https://github.com/norman-tom/pyromb/pull/16) was open at **a323d5709f7ce14c6adf46f01e0224b60668340c** and [ryan-tools PR #233](https://github.com/Chain-Frost/ryan-tools/pull/233) was open. Neither is an installed dependency acceptance. Record later exact approved upstream revisions, distribution metadata, actual reader/writer entry-point provenance and the consumer wheel hash before marking the dependencies qualified. Do not treat a stub, vendored copy, local fallback or test mock as final.

## Provisional full-workflow integration evidence (after incremental source review)

The implementation owners #138–#142 remain separate and unmerged. To qualify
their actual exposed APIs without overwriting their branches, [temporary
**DO-NOT-MERGE** draft #172](https://github.com/Chain-Frost/python-runoff-routing/pull/172)
assembled an isolated test-only tree on main
`4d7c48a562920767ed00fa23b6da7a17089d201d`. The successful
[Windows source + external-wheel run #43732524791](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43732524791)
applies **only to provisional head**
`5cfc5e114d83d62c568384a768e3676b45b26bde`.
Actual outcome: CPython 3.13.17, Ruff 0.16.6, Pyright 1.1.414 (0 errors),
repository hygiene, **1,151 source tests passed and 3 expected POSIX-only
skips**, original CMD source/installed-wheel probes passed, **168
isolated installed-wheel tests passed**, no native CMD launch.
Verified wheel SHA-256:
`14c59823a1d003a66b8ee2afecd7bd67ab776c201e9bd9615d635ddb8361d3ff`.

The integrated acceptance file at that head independently passed for:
PAR-only import via embedded references, role-distinct immutable staging,
effective kc/loss/storm edit, durable save/reopen after deleting old source
paths, single-event versus batch equivalence, subsequent **portable native
CMD input packaging** and relocation with *emitted* PAR and its original
CATG/edited STM fully reparsed; no-clobber/enum/invalid modes;
actual external PyRomb writer invocation; original RORBwin 6.52
ordinary **301-row** and batch **80-row/eight-reference** parsing by
the real installed ryan-tools reader, preserving AEP labels including
`50%`, `0.5EY`, `0.2EY`, repeated Run/TP and distinct report
identities. That report is reader acceptance, **not generated native
computation**. The integrated tests also exercise the installed writer
and report reader outside the runoff package rather than a stub/vendor
copy. Ordinary RORB GE 6.45 parameter-only source-copy coverage added to
a **later test-only head** has not yet been admitted by that older CI
receipt, and the synthetic tree itself is **not production integration**.

The tested source overlay incorporates exact earlier owner heads
#138 `576b4904d727124e6538bd58421cd05360595458`,
#139 `eba65891ad8b81995684532c7eeac5c0bd6a0022`,
#140 `4dcad73e39652d67355296ced7be45f3327eb98e`,
#141 `d5f13a6639b78b4d3c40d7729b9be4331f9360bc`
and #142 `a0e41a9077fa42d960a35199f832f40cede54fa1`.
Pinned external dependency content at that snapshot:
PyRomb commit `8653babdb544d400775d754b409c1571e773f7bb`
and ryan-tools reader commit
`9b136bcdc449e65a17c87a80650df314ca2b1eb1`.
Files independently reconciled **in the test snapshot only** were
`pyproject.toml` (both dependency pins),
`rorb_codec.py` (typed storm enums and PyRomb adapter),
`test_rorb_roundtrip.py` (typed loss tests and CATG tests) and
navigation docs; those final product merge/ownership decisions remain
with implementation owners.

[Successful current #143 base software run #43732492046](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43732492046)
at source head `15962fca6349c264d201c7ffa25244dcf6821fde`
reported **1,111 source tests, 168 installed-wheel tests,
Ruff/Pyright and both CMD probes passed**, with wheel SHA-256
`053de830f85f0dccfeb2a85ae17d2329aa27b484ba834b65f06c5503a3645055`.
This baseline run proves existing main-source behavior plus immutable
6.52 report source bytes and is **distinct** from the combined snapshot.
The independent Codex review on that base code head reported no major
issues; it does not approve unmerged integrated code.

What is **not** accepted: original Windows CMD 6.44 executing the
relocated emitted PAR, actual produced .out or batch.out from that export,
full #5 numerical equivalence, new executable-dependent verbosity/output
behavior, final source/wheel equality of owners' eventual integrated
merged heads, or upstream private 420-pair reader association recheck.
Do not relabel a green software CI or a stub native launcher as those
missing observations.

## Direct Windows-native portability procedure — outstanding

1. Select a supported registered source and prepare a parameter-only edit, then supported structural/storm edits once #139 can write them. Record original hashes, source bindings and effective selected settings/overrides.
2. Invoke the completed #141 export once. Move the **emitted** package to a fresh directory that cannot read any original files; independently reparse the *emitted* PAR/CATG/STM and validate all contained dependencies.
3. Before execution, hash the **actual relocated PAR**. Record working directory, executable path/version/SHA-256, full arguments and verbosity/output settings. Launch the exact emitted PAR from the relocated directory **without Python**; do not call NativeCmdRunSpec, capture_run or any helper that silently regenerates PAR paths, parameters or verbosity.
4. Hash the relocated PAR again; require its bytes to be unchanged. Inventory genuine outputs and distinguish actual native .out versus batch.out (if the selected CMD target emits batch.out). Independently test the pinned RORBwin 6.52 batch for **80 event rows and eight representative references**, with repeated Run/TP identities kept distinct.
5. Parse emitted-run reports through the real installed #142 reader. Report parser fidelity, native portability and numerical comparison as separate verdicts. Only use the maintained original CMD comparator for a qualified numerical statement.

The actual command syntax must be recorded from the authorised Windows CMD target rather than guessed here. A missing executable or unsupported native setting remains an explicit **not-run** or **unsupported** result and does not invalidate completed pure-Python checks.

**Next action:** inspect integration PRs #138–#142 at their exact tested heads, update the focused cases to their actual public APIs, verify writer/reader provenance, run source/installed-wheel checks and attempt the direct native package procedure if an authorised Windows executable is available. Keep #5 open; do not merge or release this preparatory receipt without review.
