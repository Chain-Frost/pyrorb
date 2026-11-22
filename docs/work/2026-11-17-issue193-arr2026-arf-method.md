# Issue #193: ARR Data Hub 2026v1 versus published ARF method — 17 November 2026

**Scope:** public source/method review and synthetic-only ARF method/provenance regressions. Parent [#8](https://github.com/Chain-Frost/python-runoff-routing/issues/8). Does not duplicate #63 optional PyTUFLOW or #192 RORBwin numerical parity.

## Source review and decision

Official [ARR guideline index](https://www.arr-software.org/arrdocs) offers **ARR Book 2 version 4.2**. Its [change log and Chapter 4](https://www.arr-software.org/pdfs/ARR_190514_Book2_V4.2.pdf) retain the previously implemented ARF equations 2.4.1–2.4.4 and all ten published Table 2.4.2 coefficient sets from [v4.1](https://www.arr-software.org/pdfs/ARR_190514_Book2_V4.1.pdf). ARR Data Hub's [2026v1 changelog](https://data.arr-software.org/changelog) (21 August 2026) does not announce altered ARF equations; it changes input IFD datasets/baselines, rounding and source/outlet selection. Its [API/about page](https://data.arr-software.org/about) explicitly describes outlet-based jurisdiction-sensitive ARF-parameter lookup.

**Disposition:** retain `ARR2019_BOOK2_V4_1_2_4_1_TO_2_4_4`, existing `Decimal` arithmetic and explicit published/legacy origins. No source-backed change to the numerical kernel, defaults, tolerance or event generation. Do not mislabel the Data Hub version as an ARF method version. See [complete delta matrix](../ARR_S6_ARF_2026_METHOD.md).

## Implementation

- Added `tests/test_arr_arf_2026.py`: exact official v4.2 ten-region coefficient table; method branch/version guards; all three 2026v1 default baselines; explicit outlet and source SHA; unprocessed ARFParams/CC-adjusted layers; and failed application of the BoM-only ARF adapter to 2026v1 storms.
- Linked the matrix from the existing ARR ARF method guide and included this dated record in the existing work index.
- Authored synthetic input only: reuses `tests/fixtures/arr/2026v1-minimal.json` and a new in-test, synthetic two-bin pattern; no genuine ARR/BoM exports or private RORB evidence published.

## Verification and remaining limits

**Verified exact-head pre-integration CI:** [Windows quality run 43937998102](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43937998102), Python 3.13, completed successfully on `f129b2b2e24bbf0959e4f9e0f344b8eb8f732bd4`: repository hygiene, pinned Ruff, strict Pyright and source tests, fresh source CMD 36-case regression, wheel build, installed-wheel isolation and 36-case regression. This is a software-quality result, not a new native RORBwin/ARF numerical-parity test. Integrating the subsequent `main` documentation update requires exact-head CI on the integration commit before merging. No extra native, GUI or third-party dependency required.

**Integration review:** the PR changes only a new authored-synthetic test module and its documentation. The ten published coefficient rows are tested independently of the implementation map; the explicit `ARFParams`/climate-layer unprocessed status, provenance hashing, outlet fields and BoM-adapter rejection are preserved. Current `main`'s documentation retirement and index changes are retained on integration; no solver, source reader, default, coefficient or numerical acceptance criterion is modified. The reviewer must not report this as provider-parity acceptance.

2026v1 `ARFParams` numeric semantics, region/jurisdiction selection against original authentic exports and SSP-adjusted data products are **not admitted** by this task; these would require separate source-contract work. No native RORBwin parity, flood-estimation acceptance or climate/preburst method certification follows.
