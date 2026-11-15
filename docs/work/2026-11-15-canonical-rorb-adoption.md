# Canonical RORB native report reader adoption — 2026-11-15

## Scope and boundary

Owner: python-runoff-routing #142, source reader ownership in
[ryan-tools #233](https://github.com/Chain-Frost/ryan-tools/pull/233) / #240.
This branch replaces runoff's local Inc/Time grammar with an adapter that
consumes ryan-tools' canonical reader. No runner, numerical solver, regression
comparator, GUI or RORBwin saved-PAR feature is introduced.

The chosen upstream candidate revision is `e7421a18d97ca4b65447ac3f0cdb974ee2684b3a`, pinned
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
`e7421a18d97ca4b65447ac3f0cdb974ee2684b3a`. This is a packaging correction, not a numerical result. Re-run
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
`e7421a18d97ca4b65447ac3f0cdb974ee2684b3a`) to carry the **existing** root PEP 561 marker with its six
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
`e7421a18d97ca4b65447ac3f0cdb974ee2684b3a`; these findings require fresh current-head validation.
