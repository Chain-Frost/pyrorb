# Offline CMD-first development policy — 15 November 2026

**Scope:** Existing public CMD gate [#5](https://github.com/Chain-Frost/python-runoff-routing/issues/5), source admission [#93–#96](https://github.com/Chain-Frost/python-runoff-routing/issues/96), and CLI/text-file MVP [#119](https://github.com/Chain-Frost/python-runoff-routing/issues/119). No new implementation owner, oracle, parser, solver or comparison runner.

## Owner decision

- **Ultimate product:** `python` is the default improved, independent pure-Python engine. Keep its API/CLI default and separate hydrological engineering method.
- **Current development:** explicitly use `python-cmd` as the test implementation for source admission, CMD-compatible numerics, synthetic controls and the finite MVP. Frozen, authenticated original RORB-CMD 6.44 full-horizon outputs are the numerical references; no native Windows launch is needed for routine regression.
- **Synthetic controls:** locally manufactured events are analytical/software checks only unless a separate authentic CMD computation for that event was captured and admitted; no circular golden generation.
- **Execution:** one Windows **or** Linux Python 3.13/3.14 quality run, original source input hash/preflight, fresh actual `python-cmd` source and independently installed-wheel comparison. The private investigation workspace is never a dependency. Keep exact unknown/unsupported/incomplete states.

## Grounded scope and latest evidence

The public `main` default has not been changed. At this decision's refresh, `main` was `d90de041139998efafd2c7cbc97710d4a338f223`: programme docs #105 were merged, source admission #93–#96 and CMD code-2/FI adapter remain **draft**. The nonmergeable cross-owner smoke [PR #127](https://github.com/Chain-Frost/python-runoff-routing/pull/127), tested head `da4d7146acbb9aa9cdd79fcffc709b53ade01503`, [Windows/Python 3.13 CI 43686246136](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43686246136), performed **50 fresh original CMD printed-Q passes / 19,550 full-horizon rows** identically from source and installed wheel, with **45 scalar pass and five incomplete**. These are *candidate* results, not independent B acceptance or accepted `main` capability. The PR16 **2,818-byte actual exporter source** is not yet recovered and differs from the older **2,913-byte historical PyRomb CATG**; no unqualified importer claim. Do not merge disposable PR #127.

## Concrete next acceptance

1. Continue separate C source PRs and A numerical adapter PRs, with the existing fixed original inputs unchanged and zero silent compatibility fallback.
2. Run the **existing** `repo-scripts/cmd_public_probe.py` and maintained public comparator from source and a separately installed wheel, on Linux **or** Windows. Match all individual case statuses, full original hydrograph ordinates, original source hashes, output-site identities and native versus model clocks; preserve reported-volume versus physical-volume definitions.
3. B independently checks new original observations and five remaining incomplete scalar qualifications. Confirm that new-case unsupported demotion cannot pass solely on the retained old 36-case gate. Only then propose feature qualification to the single CMD matrix owner.
4. For **new PR16 interoperability**, obtain its actual unchanged 2,818-byte RORB export from upstream PR16 pinned source + the complete four-layer exporter fixture, separately from the historical original 2,913-byte tests. Do not claim that upstream writer-byte parity is native hydrology acceptance.

No additional Windows/native tests, GUI work, default-engine reimplementation, broad #114–#118 features, new goldens or private-repo runtime dependencies are introduced by this policy-only change.
