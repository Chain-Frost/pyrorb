# 2026-11-14 — public analytical regression controls and cached comparison

**Status:** Draft PR [#78](https://github.com/Chain-Frost/python-runoff-routing/pull/78), exact-head `5a0ef323b69d726594448bf230833cddd838dfd1`; verified software and installed-wheel CLI only, not numerical or physical acceptance. Coordination: public roadmap #1, three-engine contract #74, private issue #56 and public PR #58.

## Delivered and independently checkable

The permission-cleared, standalone [public dataset](../REGRESSION_DATASET.md) contains **ten authored analytic source/flow controls** with real SHA-256 and original byte sizes. A new source-independent test recomputes all 10 complete arrays using exact continuous linear-reservoir, junction, IL equality/crossing and zero-event formulas. **Four** additional invalid/unsupported/nonlinear/state-isolation specifications remain explicit coverage gaps; the public `all` set returns non-success until those have executable independent contracts. A three-case smoke subset never replaces the ten-case authored set or complete private regression.

The public `regression_dataset` CLI owns only read-only source preflight and comparison of independently computed **external** ordinate CSV against authenticated reference arrays; it does not run any of the three engines or launch native CMD. It validates case/site identities, original printed tokens, native clocks, full horizon, complete columns, output completeness and type/finite constraints. The result records case-level statuses, per-ordinate errors, actual comparator module hash, SHA-pinned register/policy/candidate input, and optional externally asserted wheel/source identities. Unverified source/wheel concordance is explicitly marked unverified; no acceptance is inferred from a submitted SHA alone.

## Exact-head executed software evidence

[Windows/Python 3.14.10 hosted quality #43616206274](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43616206274) at `5a0ef323b69d726594448bf230833cddd838dfd1`:

- **701 non-native tests passed**, zero failures; all ten authored reference equations and manufactured comparator negative controls included.
- Pinned Ruff 0.16.6 lint and formatting clean; strict Pyright zero errors/warnings; repository hygiene 174 files/zero errors.
- Public wheel built and installed separately outside checkout.
- The **installed wheel CLI executed** `preflight .../tests/fixtures/regression-v1/register.json --set authored --engine python` from `RUNNER_TEMP` with `PYTHONPATH` explicitly restricted to its isolated target, reporting **10 verified / 10 requested, complete=true, exit 0**. No private fixture or RORB executable accessed.

## Private counterpart and remaining gates

The private canonical register in [PR #63](https://github.com/Chain-Frost/runoff-routing-investigations/pull/63), head `744d0ffdf94e810a9a0a135d70f8418b47e8aed5`, retains **65 original captures** with 1,026 unchanged indexed files, plus **six separately named supplemental evidence cases** outside the original archive. Of 71 entries, **36 original successful CMD cases** are the current full eligible captured-event comparison selection; **35** remain explicit unreviewed, negative, GUI, incomplete or external-evidence gaps. Historical candidate/field-level v6 reviewed results are source/wheel/profile pinned, but the added six external-custody cases have no fabricated portable source files. The 50-case metric evidence lane is not a fresh maintained scalar replay. Earlier Windows 36-case preflight/16,836-row candidate comparisons used a prior register/runner revision and remain historical, not repeated here.

**Open:** fresh exact-head Windows/Python 3.14.6 cached replay against the new 71-entry private register; independent source/wheel candidate export and installation identity authentication; six protected original native report/typed input local evidence packages; eight legacy archive migration cases; physical print-site mapping, reporting-scalar adapter and independently approved conservation/refinement/stability/peak-tie-time gates. Public PR #58 typed invalid/incomplete/status work at `5fe496f7b82a3100b062a5a705334abf4d919c10` remains unverified on its exact head; keep that fix on #58 rather than duplicate it here.

No native launches, original/golden replacement, engine dispatch/default changes, batch optimisation, automatic merge, release or acceptance closure were performed by this PR.
