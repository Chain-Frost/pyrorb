# Canonical RORB native report reader adoption — 2026-11-15

## Scope and boundary

Owner: python-runoff-routing #142, source reader ownership in
[ryan-tools #233](https://github.com/Chain-Frost/ryan-tools/pull/233) / #240.
This branch replaces runoff's local Inc/Time grammar with an adapter that
consumes ryan-tools' canonical reader. No runner, numerical solver, regression
comparator, GUI or RORBwin saved-PAR feature is introduced.

The chosen upstream candidate revision is \`20f0d9c9ab49f9759877c8cd98b515f57150154f\`, pinned
by a direct source-control dependency on the reader-only distribution at
\`packaging/rorb-readers\`. That wheel uses the six original upstream modules,
not vendored or duplicated parser implementations. Its Python requirement is
>=3.13; the larger ryan-tools distribution remains >=3.14 and is not selected.
The approved SUL-1.0 licence is copied unmodified as the repository's LICENSE
and declared in metadata.

## Changes

- \`rorb_out.inspect_output\` is now **thin, read-only conversion** of the
  upstream \`read_rorb_file\` result to the existing immutable
  \`HydrographReport\`/evidence-policy presentation types.
- Original bytes, SHA-256, line text and byte count are checked against the
  already authenticated \`RorbSource\`; mismatches fail closed.
- Canonical \`source_tokens\` and \`source_decimal\` supply source-precision
  numbers. There is no reconstructing the upstream rounded float values.
- The originally reported 0-based/1-based \`Inc\`, exact \`Time\` tokens,
  absolute clocks, horizon and diagnostics are retained unchanged.
  Hyd labels are not fabricated as physical print sites; source/project
  binding remains downstream.
- Existing project/native/regression callers of \`inspect_output\` migrate
  transitively. Existing CLI \`rorb-inspect\` JSON retains its public shape.

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
- Finish replacing the separate report scans in \`reference._check_report\`
  and \`regression_metrics._scalars\` / \`bind_report_metrics\` under #142,
  taking care not to loosen frozen scalar and capture policies.
- Qualify direct source Git dependency/isolated installed wheel under
  Python 3.13, without editable or source-tree imports.
- General CLI CSV report views, contextual association overrides and remaining
  multi-table settings are not asserted as completed.

The local report adapter does not run any RORB executable. No native
scientific acceptance, merge or release is claimed.
