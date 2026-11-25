# PR-only writer release preparation — 24 November 2026

Scope: [#213](https://github.com/Chain-Frost/pyrorb/issues/213), after merged Python 3.11 compatibility #227. Owner directs PyRomb to remain PR-only; no further upstream review/merge/release is a prerequisite. Preserve its exact source commit and the sole ordered writer implementation.

- Migrate the PyRomb Git source requirement to `requirements-catg.txt`. CI and full development instructions install it explicitly. Core users need no writer; edited CATG export reports the separate installation requirement. No numerical algorithms or format contracts change.
- Bind the mandatory reader to permanent merged ryan-tools `df6e8bc2dda24d2b376e888156e4105588f028fa` rather than its earlier PR SHA. The standalone release is tracked in [ryan-tools #337](https://github.com/Chain-Frost/ryan-tools/issues/337) and [PR #338](https://github.com/Chain-Frost/ryan-tools/pull/338). Do not replace the reader URL with an unavailable PyPI version.
- This preparation is not release acceptance. Exact-head hosted matrix, independent downstream review, published reader wheel, final metadata replacement, clean index-resolving wheel/sdist installations, all extra workflows and activation reconciliation #220 remain required. No publication trigger or repository configuration has been changed. No native RORB/MC scientific claim.
