# Canonical RORB native report reader adoption — 2026-11-15

## Scope and boundary

Owner: python-runoff-routing #142, source reader ownership in
[ryan-tools #233](https://github.com/Chain-Frost/ryan-tools/pull/233) / #240.
This branch replaces runoff's local Inc/Time grammar with an adapter that
consumes ryan-tools' canonical reader. No runner, numerical solver, regression
comparator, GUI or RORBwin saved-PAR feature is introduced.

The chosen upstream candidate revision is `598e5edea093df426cda64c3a528fd1c5784c612`, pinned
by the immutable reviewed GitHub source-archive dependency on the reader-only distribution at
`packaging/rorb-readers`. That wheel uses the six original upstream modules,
not vendored or duplicated parser implementations. Its Python requirement is
>=3.13; the larger ryan-tools distribution remains >=3.14 and is not selected.
The approved SUL-1.0 licence is copied unmodified as the repository's LICENSE
and declared in metadata.

## Changes

- `rorb_out.inspect_output` is now **thin, read-only conversion** of the
  upstream `read_rorb_file` result to the existing immutable
  `HydrographReport`/evidence-policy presentation types.
- Original bytes, SHA-256, line text and byte count are checked against the
  already authenticated `RorbSource`; mismatches fail closed.
- Canonical `source_tokens` and `source_decimal` supply source-precision
  numbers. There is no reconstructing the upstream rounded float values.
- The originally reported 0-based/1-based `Inc`, exact `Time` tokens,
  absolute clocks, horizon and diagnostics are retained unchanged.
  Hyd labels are not fabricated as physical print sites; source/project
  binding remains downstream.
- Existing project/native/regression callers of `inspect_output` migrate
  transitively. Existing CLI `rorb-inspect` JSON retains its public shape.

## Verification and limitations

Added synthetic direct upstream file/bytes tests, Decimal/Fortran D precision,
both original increment origins, invalid rows, CRLF bytes and source-changing
failure. The upstream unit suite and downstream source/installed-wheel suite
must execute against the pushed heads. This record does **not** present
unexecuted checks as passes.

Outstanding:
- Recheck actual ryan-tools #233 CI against the new head and its private
  420-pair batch/CSV association acceptance.
- Verify the 6.52 retained 80-row/eight-reference batch and 301-row report,
  and independent CMD 6.44 source/wheel regression via the canonical import.
- Finish replacing the legacy `reference._check_report` capture scan under #142,
  taking care not to loosen frozen source/capture policy; the scalar and legend
  scans are already migrated to upstream `reported_scalars` and `sites` sections.
- Qualify direct source Git dependency/isolated installed wheel under
  Python 3.13, without editable or source-tree imports.
- General CLI CSV report views, contextual association overrides and remaining
  multi-table settings are not asserted as completed.

The local report adapter does not run any RORB executable. No native
scientific acceptance, merge or release is claimed.

## CI blocker and correction

The first hosted Windows job failed **at dev dependency installation**, not
in parser tests. Pip recursively fetched the unrelated ryan-tools test-data
submodule during a `git+https` dependency checkout and hit Windows
`Filename too long`. The dependency is now an **exact-commit GitHub source
archive**, without submodule payload or Git checkout, pinned to upstream
`b246e8c7bd9ddf97d2d286402202b14e9e48e595`. This is a packaging correction, not a numerical result. Re-run
installed-wheel and regression checks for the new head.

The frozen scalar binding now gets only generic original scalar and site
records from the canonical reader. Downstream enforces exact native unit,
site order, report summary count and scalar population, without rescanning
native source text. No new scalar convention is accepted.

## Source and wheel PEP 561 typing gate

The first archive-based Windows 3.13 source install succeeded; Ruff and
formatter checks passed after fixes. Strict Pyright then reported missing
type stubs because the minimal wheel had omitted `ryan_library/py.typed`.
Upstream revised focused setuptools packaging (reviewed candidate
`b246e8c7bd9ddf97d2d286402202b14e9e48e595`) to carry the **existing** root PEP 561 marker with its six
canonical reader modules, without broadening dependencies. A clean local
package-layout wheel test verified the marker was included; hosted strict
type checking and installed-wheel regressions must now rerun.

Upstream added conditional original RORBWin 6.52 fixtures for the 301-row
ordinary report and 80-row/eight-reference batch. These require the pinned
fixture submodule; no CI pass is claimed where that submodule is absent.

## PEP 561 namespace packaging refinement

The `a00f41cfe2fa5b20491698eb5c8af5e265dcd086` hosted wheel contained a `py.typed` root marker, but strict
Pyright still reported all `ryan_library.functions.RORB` modules as missing
typing stubs. The focused setuptools wheel has now been revised to carry both
upstream regular parent package initialisers (`ryan_library` and
`ryan_library.functions`) with the marker and the same six canonical reader
modules. A clean local wheel-layout build confirmed both initialisers and the
marker are present; downstream hosted Pyright/installed-wheel checks remain
the completion gate for this change.

## Eight-finding Windows test closeout

At the previous Python 3.13 archive head, lint, formatter and **strict
Pyright passed** and 1,094 of 1,102 source tests passed. Eight fail-closed
compatibility findings were classified: three mocked CMD captures use the
characterised standalone `End` terminator, four independent metric tests
supply hash-authenticated in-memory source evidence rather than an existing
file path, and one new scalar test uses a legitimate Fortran D exponent.

The reader keeps the `End` terminator and invalid original scalar lexemes
upstream. The downstream adapter now recovers only original in-memory byte
candidates matching **both SHA-256 and byte count**; a changed existing
file is never replaced by a reconstructed source. This is neither source-line
parsing nor a general unverified fallback. A hydrograph remains inspectable
for malformed independent scalar records, but overall report status stays
invalid and scalar qualification rejects it. The comparator's existing
half-last-digit interval policy remains unchanged while D exponents are
converted for exact Decimal evaluation. The amended pinned upstream is
`b246e8c7bd9ddf97d2d286402202b14e9e48e595`; these findings require fresh current-head validation.

## Canonical native capture scan replacement

The remaining `reference._check_report` independently parsed Inc/Time native
capture fragments. It now invokes **upstream**
`read_rorb_table_file`, a bounded explicit source snapshot through exactly
the same canonical numeric/time grammar. Bare unversioned fragments stay
`isolated_hydrograph_table` with the explicit unverified-source warning;
ordinary report reading remains strict. Downstream still applies
`expected_prints`, `expected_steps` and exact zero-flow classification,
retains raw `Time` labels, and does not infer a physical site identity,
scientific validity or a native executable. All local report lexical parsing
has been removed from `reference._check_report`, `regression_metrics` and
`rorb_out`. Existing capture-specific synthetic tests plus a new two-site
bare-table/negative admission test are the acceptance gate. Current reviewed
dependency revision: `598e5edea093df426cda64c3a528fd1c5784c612`.

## Read-only canonical report views

The maintained `repo-scripts/rorb_inspect.py` entry point now has an opt-in
`--report` mode for standard `.out`, `batch.out` and signed hydrograph CSV.
`--section runs --format csv --limit 1000` writes an ordered typed view to
stdout, with separate `source_token__` columns retaining every original
printed token. Default `--report` emits bounded JSON section inventories,
status, diagnostics, SHA-256 and source size. `--section` pages exact token
records; neither view reparses lines, infers print identities, selects events,
launches RORB nor modifies the source. Invalid canonical reports remain
non-success exits, with retained diagnostics; saved-PAR remains inactive.

The existing non-report inspection mode retains its historical API and CLI
output. Synthetic CLI/API tests cover same-source bytes, distinct event/TP
rows, Fortran D tokens, non-success invalid reports and selection guards.


## 2026-11-15 original-case and exact-head integration receipt

Independent **source-level inspection**, not executed reader tests, of
[ryan-tools-test-data at f3c49e867cd8a165e031217a148293a8968c2d88](https://github.com/Chain-Frost/ryan-tools-test-data/tree/f3c49e867cd8a165e031217a148293a8968c2d88/RORB/12hr-areal-example):
`Fig6_7_batch.out` (Git blob `08ae1d94ef74d666836c8d3fab842e6421851030`)
contains 80 original run/TP rows and eight distinct reported representative paths
across 50%, 0.5EY, 20%, 0.2EY, 10%, 5%, 2%, 1%; the ordinary
`Fig6_7_ aep0p2EY_du12hourtp1.out` (blob
`95826bccdbe1f2410ef372ef6b6c2c161d847b99`) contains original 301
increments 0..300, times 0.00..150.00 hours at 0.50 hours. Those sources
establish expected acceptance; they do not prove the new parser passed.

**Last fully green downstream exact-head receipt before the report-view
addition:** Windows Python 3.13 CI
[run 43730017092](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43730017092)
at `a0e41a9077fa42d960a35199f832f40cede54fa1`: repository hygiene,
Ruff lint/format, strict Pyright 0 findings, **1,103 source tests**,
original CMD source regression, a wheel with SHA-256
`1916144baeadb5847cc9c3e5169cf6d26f7e3f352aa83cd0a9cfde771d86a141`,
**153 installed-wheel tests**, native-negative-control propagation and fresh
installed-wheel original CMD regression. These observations are pinned to that
head, **not** to the later report-view/override commits. No native executable
was run. Additional canonical view tests and upstream exact-revision override
tests await their own execution.

Upstream #233 now supports explicit companion CSV overrides under the five-part
source event key (Run, duration token/unit, raw frequency label, TP); it still
rejects unknown event keys and unverified/missing companions. This repo pins
the upstream override revision `598e5edea093df426cda64c3a528fd1c5784c612`; it does not copy or maintain an
association parser.


## 16 November 2026 — canonical reader full original-fixture acceptance

[Upstream ryan-tools PR #233](https://github.com/Chain-Frost/ryan-tools/pull/233)
at exact code revision `598e5edea093df426cda64c3a528fd1c5784c612` passed all six hosted checks in
[run 43748737493](https://github.com/Chain-Frost/ryan-tools/actions/runs/43748737493).
Windows Python 3.14 hosted regression: **3,371 passed, 16 skipped,
eight deselected**. The three new original-fixture tests exercised all
**640 accessible RORBwin 6.52 batch/CSV companions**, grouped as 80
12-hour, 80 24-hour, and 480 multi-duration members. Exact-head Codex
review reported no major issues. The P2 incorrect-success finding for
missing or partial site description mappings is corrected with fail-closed
full-flow-site coverage checks and synthetic negative/positive cases.
Python 3.13 grammar is guarded in the narrow reader sources.

The **distinct private 420-event RORBWin 6.45 source set** was not found
in the repositories accessible through the connected GitHub app:
`ryan-tools-test-data` contains 6.52 inputs (80/80/480), and
`runoff-routing-investigations` has eight smaller GUI batch reports and
150 companion CSVs on current branches. An earlier validation instruction
identifies the 420-event set as local private Windows inputs. Their
previous 420/420 receipt predates revised peak precision and cannot be
relabelled current; a local read-only recheck is still necessary before
treating that exact population as admitted. Do not copy private inputs
into public GitHub or run native RORB.

This downstream PR now pins the exact successfully tested reader commit
`598e5edea093df426cda64c3a528fd1c5784c612` via the archive-based small distribution. Review and source/installed
wheel CI on the downstream commit containing this new pin are a separate
acceptance and cannot be inherited from the earlier head.

## 2026-11-16 owner-authorised public 6.45 corpus and current evidence

The owner authorised input/output fixture publication and allowed an authentic
alternative to the unlocated historical 420-event source. Public
[ryan-tools-test-data PR #4](https://github.com/Chain-Frost/ryan-tools-test-data/pull/4)
at exact commit `af0d24b7640c6a40ed4384b8f04710a91b0e3a26`
provides a RORBWin-**reported** 6.45 batch of **490 event/CSV pairs**,
490 individual reports, 491 STM inputs, a 1,472-file original/distributed
SHA-256 manifest and per-event association receipts. Only absolute
Windows directory prefixes were changed in distributed copies. The version
banner does not authenticate the executable, and the model CATG is absent:
this is a reader source corpus, not a numerical-model replay.

The data custodian verified **490 corroborated, zero missing/ambiguous/
mismatched**, against exact canonical reader code
`598e5edea093df426cda64c3a528fd1c5784c612`, under Windows
Python 3.14.6. The receiving agent then added an *independent hosted*
public reader check to upstream PR #233 at commit `a037461d`:
[CI run 43753671346](https://github.com/Chain-Frost/ryan-tools/actions/runs/43753671346)
passed on **Windows Python 3.13 and 3.14**. It verified all 1,472
distributed file hashes, all 490 composite event-key/CSV corroborations,
and preserved 501 ordinary report/CSV rows with matching flows and the
unmodified **+0.5-hour CSV minus report offset**. Full upstream CI at
`a037461d` was still running when this record was written; the parser
modules are unchanged since earlier reviewed 6/6-green commit `598e5ede`.

This consumer still pins the same reviewed reader *code* `598e5ede` in
its minimal installed distribution: the later upstream commit changes tests,
CI and docs only. The previous downstream Windows source/installed-wheel
check [run 43749720170](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43749720170)
passed at `fe000668`. This consumer branch also integrates the separate
main-branch #175 written-rainfall change as a merge parent, preserving its
source files and requiring fresh current-branch CI.

**The historical 420-event data was not found or revalidated.** The 490
population is the owner-authorised alternate real-file *reader* acceptance,
not a 420/420 verification, native numerical equality, physical-site
identification, representative-event or critical-duration selection proof.
No numerical solver, GUI, native RORB execution, external package repin,
fixture gitlink, main-branch PR merge or release was introduced.
