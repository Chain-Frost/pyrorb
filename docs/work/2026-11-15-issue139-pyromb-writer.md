# Issue #139 — single PyRomb CATG writer, staged integration

Date: 2026-11-15. Scope: #139 under #3/#7; coordination with #138/#140/#141.

## Source ownership and exact dependency

- Reviewed basis: [upstream PR16](https://github.com/norman-tom/pyromb/pull/16), head `a323d5709f7ce14c6adf46f01e0224b60668340c` at inspection. The older fork PR2/historical 2,913-byte reference is not the current exporter.
- Proposed public ordered-input API: [PyRomb writer branch](https://github.com/phantom-branch/pyromb/tree/feat/ordered-rorb-catg-139), based on PR16, current pinned revision `51cb3880d9017e389a87100e6025c1a5cc160233`. Keep this enhancement **in PyRomb**, never vendored into runoff-routing. The extra API accepts ordered control records plus explicit physical reach lengths, source area/FI and graphical metadata. It shares the existing upstream VectorBlock/GraphicsBlock rendering paths. The GIS Traveller entry point remains.
- Downstream dependency is optional `.[catg]` and is pinned to that exact Git commit; the development extra installs it for writer tests. Source-only parsing and numerical execution do not load PyRomb. Existing PyRomb MIT notice remains at `docs/third_party/PYROMB_LICENSE.txt`.

## Adapter/guard

- Existing `serialize_catg(CatchmentModel)` and `serialize_catg_with_drawing(CatchmentModel, GeDrawing)` are preserved as direct **PyRomb adapter** entry points, not parallel formatters.
- Original `ParsedDocument.source.data` is re-emitted by `original_bytes(parsed)` when the model is unchanged. This preserves exact original byte content, encodings, CRLF and metadata. This is the preferred path for importing unchanged CATG in a parameter-only native export.
- For new/edited CATG, type validation and the existing full-model reparse check enforce matching source order/consumption, controls, physical lengths, areas/FI, native print labels and unsupported flags. A drawing variant verifies identity, endpoint topology, CRS/metre units and physical lengths before invoking PyRomb. **Normalized GE drawing XY is never a length input.**
- Plain model-only modern 6.45 export cannot invent graphical node/reach records: it fails and requests explicit validated drawing. Modern imported CATG need not be redrawn when unchanged.
- The supported modern population is natural reaches, 1/2/3/4/5/7 controls, one terminal print, ordinary fractional FI and print 70/zero excess. Distinct 6.45 code-1/2/5 labels, 3-decimal graphical km length or 6-decimal graphical area/FI precision overflow, additional output flags/types are rejected rather than silently stripped.
- Legacy 002 no-drawing canonical output still goes through **PyRomb**, with its explicitly supported empty scaffold. STM and CMD PAR remain local. Newly serialized combined-preburst DESIGN files carry an explicit **derived export annotation**, not fictional original generator metadata; original source bytes remain untouched.

## Actual checks and limitations

- Focused upstream ordered-writer checks and downstream adapter/reparse, source-identity, modern code-2/FI, physical-geometry and combined-preburst tests were added.
- This record is **implementation pending GitHub Actions exact-head verification and independent review**. No locally executed source/wheel test, native Windows RORB invocation or scientific CMD equivalence is claimed here. The original native CMD reference index and regression goldens are unchanged.
- Before acceptance: review/test the **upstream PyRomb PR first**, update the downstream pin for any upstream fixes, confirm exact-head source checks, wheel import and all relevant retained cases, and obtain independent review. #141 may continue parameter-only exact-source project export in parallel; no GUI or new numerical engine is part of #139.
