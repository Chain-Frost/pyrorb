# Issue #139 — PyRomb CATG/STM writer, implementation closeout

**Status:** implementation complete; independently reviewed and validated for the bounded supported population. PR [#166](https://github.com/Chain-Frost/python-runoff-routing/pull/166) remains **unmerged**. Reviewed 15 November 2026, after owner approval of the pinned dependency. Owners #138 (types), #140 (PAR/path), #141 (native package export), #96 (source admission) and #5 (numerics) remain independent.

## Accepted writer dependency

The owner **accepts the exact Git-commit-pinned PyRomb revision now**. Neither [upstream PyRomb PR #16](https://github.com/norman-tom/pyromb/pull/16) remaining open nor absence of a released package blocks this bounded writer scope; further upstream review/version maintenance is deferred until the maintainer acts. This is acceptance of the development dependency, not blanket acceptance of native RORB/CMD numerical behaviour.

- Upstream reviewed PR16 base: `a323d5709f7ce14c6adf46f01e0224b60668340c`.
- Ordered-record extension: [phantom-branch/pyromb PR #3](https://github.com/phantom-branch/pyromb/pull/3). Pinned **writer-code** revision: `8653babdb544d400775d754b409c1571e773f7bb`. The later PR head `e48afab9bdeca08af76c9ac840296008650417ef` differs by a test-only correction.
- `pyproject.toml` exposes optional `.[catg]` and writer-enabled `.[dev]` extras pinned to that exact commit. Parsing and numerical routing do not import PyRomb. Its MIT notice remains in `docs/third_party/PYROMB_LICENSE.txt`. Nothing is vendored.
- Historical PR16 2,818-byte LF exporter output and separate 2,913-byte CRLF original remain separately authenticated under #96/#133; no originals or native goldens are regenerated.

## Implemented behaviour

1. `serialize_catg(model)` (legacy graphical 002 no-drawing subset) and `serialize_catg_with_drawing(model, drawing)` (bounded 6.45) call **the same public ordered PyRomb writer**. Both old local vector layout and graphical CATG format rendering were removed. Existing callers and regression tests use the adapter.
2. Existing parsed source documents use `original_bytes(parsed)` for exact unchanged CATG/STM, including comments, encodings, line endings, graphical metadata and source order. Parameter-only native export can copy exact assets without PyRomb.
3. New/edited 6.45 needs an explicitly validated projected-metre drawing. Physical reach lengths, source identity, order and membership come from the typed controls and explicit physical model, **not normalized drawing XY**. The bounded population includes natural reach, code 2, ordinary per-source impervious fractions and characterised single-outlet print 70/zero-excess. Legacy 002 multiple code-7 prints are preserved.
4. Reject unsupported independent labels, three-decimal kilometre or six-decimal graphical area/FI precision overflow, extra graphical output flags, unsupported reach types, mismatched area/FI/physical graphical values, incorrect source ordering and overwidth graphical labels instead of fabricating data. Reparse the complete exported model and require typed-model equality. `canonical_run_bytes` distinguishes semantic loss from other unsupported cases.
5. STM and CMD PAR writers remain local. `serialize_design_stm` supports characterised combined-preburst storms and clearly labels newly **derived export annotations** rather than representing them as original generator metadata.

## Exact-source QA and independent review

[Windows quality run 43728316566](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43728316566) passed against exact prior implementation head `9df11fc9d0a42955b50d378530321cb0eef81ea2`, on Windows Python 3.13.17: repository hygiene (504 files, 0 errors), Ruff 0.16.6 lint/format, strict Pyright (zero errors/warnings), **1,100 source tests**, authenticated source CMD regression, wheel build and isolated installation, **153 installed-wheel tests**, indexed fixture preflight, CLI/batch negative gates and installed-wheel CMD regression. The isolated wheel SHA-256 was `90a1965291bee8034a829214134d7aa07b63630af119b43e2b808cefc0b00ffa`.

[Independent Codex review of #166](https://github.com/Chain-Frost/python-runoff-routing/pull/166) on `9df11fc` reported **no major issues**. Upstream PyRomb Codex raised graphical field-width and graph/computation mismatches, fixed in `8653bab`; later test-only assertion correction reached `e48afab`. Final upstream Codex review found **no major issues**, and three inline threads were resolved with dispositions.

These are audited hosted checks, **not** personal native execution or proof of scientific CMD/RORBwin parity. Original source/Q/print-site/clock acceptance remains with #5/#96/#137, and wider 6.45 output modes remain outside #139. Historically incomplete native scalar-time cases are not relabelled as passes.

## Completion boundary

The pinned dependency is owner-accepted. #139 has no remaining implementation or upstream-release dependency gate. This final documentation/main-branch reconciliation is reviewable independently of numerical changes. **Do not merge or release without an explicit merge instruction**; upstream maintainer follow-up, parent #3/#7 and parallel #138/#140/#141 work remain separately tracked.
