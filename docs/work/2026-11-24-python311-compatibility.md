# Python 3.11 compatibility migration

| Field | Value |
| --- | --- |
| Status | Needs review: current-main local four-version validation passes; final hosted gate pending |
| Updated | 2026-11-24 |
| Next review | 2026-11-25 |
| Original baseline | a080d005051fe2d15b93e46491e0f857ac3384e3 |
| Current integration base | 0526aa2b8e91cce4665aaa6d686d272911065808 |
| Branch | compat/python311 |
| Issue | [#226](https://github.com/Chain-Frost/pyrorb/issues/226) |

Support Python 3.11, 3.12, 3.13 and 3.14; prefer 3.14 for development.
Exact standalone Python 3.11.11 is the owner's ArcGIS Pro interpreter target;
ArcGIS Pro itself and its Python environment are untouched and not qualified.

## Changes

Replace PEP 695 generic declarations with TypeVar/Generic/ParamSpec while preserving typed signatures,
bounds and inferred variance. typing_extensions is declared for the latter backport.
Lower package, Ruff and strict Pyright targets to 3.11 and extend only the existing Windows quality workflow.
Native-process tests warm Windows platform discovery before mocking subprocess, because Python 3.11
uses subprocess for that discovery; no native solver behaviour is changed.

Use the independently built canonical ryan-rorb-readers source from the ryan-tools compatibility PR,
and the reviewed PyRomb dependency revision ecd5caa45e5c9204233d9a793e4cae9656bbe778 from
[phantom-branch/pyromb #3](https://github.com/phantom-branch/pyromb/pull/3).
No local filesystem dependency reference is committed. There is still only one canonical reader implementation.

## Evidence

Original-base Windows isolated checks: Python 3.11.11, 3.12.14, 3.13.15 and 3.14.6;
1,526 tests pass on each, with platform/privilege skips (seven in the final 3.11 run).
The complete local quality runner on 3.11.11 passes pinned Ruff, strict Pyright and pytest.
Wheel and sdist construction pass. Current-main installation and strict typing pass on all four interpreters. The integrated suite passes **1,554 tests / seven skips on each interpreter**. Final clean-wheel receipts are recorded in the PR.

The fresh public CMD probe executes all 50 registered cases with no native process: 50 printed-output passes;
fresh scalar/reporting status remains 48 pass and two incomplete. Both original 36-case retained gates pass.
These preserve existing acceptance limits, supported/incomplete statuses and numerical tolerances.
No RORBwin sampling, Monte Carlo statistical or engineering qualification is claimed.

The PyRomb metadata-only dependency update passes 199 tests / 55 QGIS-dependent skips on 3.11.11,
with independent extracted-wheel review. Optional/native QGIS, RORB and ArcGIS Pro acceptance remain separate.
Initial migration Ruff safe fixes corrected four findings automatically; five generated TypeVar names
were corrected manually. Subsequent import-only safe fixes are logged locally.

## Integration and delivery

The owner merged physical-catchment preflight #225 while migration validation was running.
Integrate that accepted main revision without bringing any unmerged Monte Carlo staging branch into this PR.
Preserve its methods/contracts and rerun compatibility checks. Original unrelated local work remains in its original checkout.
Evidence lives at E:/Github/compat311-evidence. Current hosted results and independent final-head review belong in the PR.
No merge or package publication is authorized by the compatibility task.

## Next action

Complete current-main integration, clean wheel/source numerical equivalence and independent review; publish the compatibility PR.

## Final review checkpoint

Independent review identified a required-check naming regression: a bare matrix replaces the protected
windows-python-313 context with suffixed names. Preserve that exact required check through a fail-closed
aggregate job over every version lane. The original workflow/action/security controls remain unchanged.
The reviewer independently passed 3.11.11 generic specialization, variance, annotation, decorator and byte-roundtrip checks.
