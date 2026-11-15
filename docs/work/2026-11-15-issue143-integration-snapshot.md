# Temporary #143 integration snapshot — DO NOT MERGE

This synthetic verification tree overlays unmerged implementation files on main
without merging any owner PR into main, and resolves only their overlapping
files for testability. It is **not** a reference implementation or release.

- Main base `4d7c48a562920767ed00fa23b6da7a17089d201d`
- #138 `576b4904d727124e6538bd58421cd05360595458`
- #140 `4dcad73e39652d67355296ced7be45f3327eb98e`
- #141 `d5f13a6639b78b4d3c40d7729b9be4331f9360bc`
- #139 `eba65891ad8b81995684532c7eeac5c0bd6a0022`
- #142 `a0e41a9077fa42d960a35199f832f40cede54fa1`
- #143 `2814a7aab9de3de32cc2297b855bb603b6c922aa`

The shared code path `rorb_codec.py` incorporates #138's typed enum
construction atop #139's external PyRomb writer; `test_rorb_roundtrip.py`
combines each owner's expected behavior. `pyproject.toml` retains both the
runtime canonical ryan-reader pin and the opt-in PyRomb writer pin. General
README navigation is combined for test use only. All other implementation
source objects retain their respective owner branch Git blobs unchanged.

No native executable is installed or launched by the approved CI. Source/wheel
checks against this tree demonstrate provisional software integration only.

## Independent software verification on initial combined head

[Windows quality run #43732524791](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43732524791)
completed successfully at exact source head
`5cfc5e114d83d62c568384a768e3676b45b26bde`
(Windows, CPython 3.13.17, Ruff 0.16.6, strict Pyright 1.1.414).
It verified repository hygiene, strict static checks, **1,151 source tests
passing / 3 expected POSIX-only skips**, the maintained fresh original CMD
source probe, and **168 installed-wheel tests passing** from an external
installation. Both maintained CMD probes, wheel provenance and CLI/negative
smokes completed. Wheel SHA-256:
`14c59823a1d003a66b8ee2afecd7bd67ab776c201e9bd9615d635ddb8361d3ff`.

The four integrated contract tests passed at that exact head (PAR-only import,
typed edits, relocated emitted PAR/source files, actual imported PyRomb renderer,
original 301-row RORBwin ordinary output and **80-row/eight-reference** original
batch via actual ryan-tools reader). No host RORB CMD binary was executed;
the 80-row batch is retained 6.52 native output, not a new CMD result.

**Later unverified changes on this test-only branch:** additional parameter-only
export coverage of the original ordinary `pyromb-pr2-full` graphical 6.45
CATG with code 2/FI and explicit test selection in the external wheel suite.
They are pending an exact later-head CI receipt; the above numbers must not
be attributed to those new tests until run. Source heads of the implementation
owners may also advance independently; this synthetic tree is frozen at the
listed earlier source revision snapshots.
