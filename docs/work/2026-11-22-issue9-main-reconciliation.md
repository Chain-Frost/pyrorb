# Monte Carlo #151 — main reconciliation and PyRORB identity verification

Date: 22 November 2026. Scope: **draft PR #151 only**; programme [#9](https://github.com/Chain-Frost/pyrorb/issues/9). This work is a branch integration, **not** a native-statistical qualification or an authorization to merge into main.

## Frozen integration inputs

- Starting Monte Carlo head: `a80a139f9fdc7ce181ce14852138eb5a8af2fa8b` (tree `8a2f0a1170d34499f51ca9da2e52782300a3161c`).
- Integrated main: `e773472b6f0386257643a89a66a0b1dfe4a75af1` (tree `66eef397d9ca4f5c01cb7abf10065424caf2ab02`), three commits after shared ancestor `1a5175ad9dbf6be03d78b164b169b3ec836e6a9e`.
- Shared identity source: #212 / merged PR #214 (`e773472b6f0386257643a89a66a0b1dfe4a75af1`, based on the original PR head `5344b95f5dccefc2fb8327d242414501cd9cc0e9`). The selected distribution/brand changes were already integrated into the MC branch at `a80a139f9fdc7ce181ce14852138eb5a8af2fa8b`; this merge also incorporates the identity correction on current main. Publication draft #215 is excluded.
- Result: a two-parent integration commit (first parent MC head, second parent the main revision above). The exact resulting head is documented on PR #151 after publication.

## Reconciliation and preserved contract

Two main commits updated delivery/ARR2026 qualification documentation; the third merged #214's PyRORB identity and its quickstart dependency correction. Those changes added `tests/test_arr_arf_2026.py` and two ARR2026 supporting records, and retired six superseded work notes. The MC branch still contained older status/engine descriptions that conflicted with current main. Reconciled maintained programme documentation to main's newer delivery/qualification facts, kept new main additions and retirements, and retained PyRORB branding, stable `runoff_routing` imports and current navigation. In the work index, MC-specific scopes/research/native receipts were brought forward rather than being dropped with outdated programme prose. Historical commit-pinned/source custody links remain historical.

No MC numerical kernel or MC source, research artifact, fixture, probability/weighting policy, plan/replay/checkpoint contract, research dependency, stable `python-runoff-routing/mc-sampler` domain or stored format was intentionally changed. The merge also leaves `pyproject.toml`, `src/runoff_routing/__init__.py`, `src/runoff_routing/engine_provenance.py` and the active quality workflow at their existing staging-tree blobs.

## Verification boundaries

GitHub compare/tree inspection established a two-commit main divergence and confined overlapping changes to maintained documentation; no MC numerical conflict was identified. Git object SHA comparisons against the starting MC tree are used to check unchanged implementation/fixture bytes, plus main-tree blob identity for nonconflicting additions. The remote mergeability and hosted quality run must be checked against the exact resulting merge commit.

**Not executed in this environment:** a local `git merge` worktree, `gh`, Ruff, Pyright, pytest, MC sample/replay/regression tests, build or isolated-wheel/original-CMD checks. The available container has neither `gh` nor DNS access to GitHub; GitHub API tree/commit operations were used instead. Historical checks on #214 and old #151 heads are not represented as new execution. Do not mark local verification passed from this record.

Scientific gates remain open: #148 qualified physical-catchment convergence and uncertainty, #150 native method/effective-input observations, #189 sampling profile, #190 probability support/result rules, and #191 canonical comparison. Existing v1 tails, zero/failed mass, mode selection, independent reference and statistical acceptance limitations are preserved. Draft #151 remains **unmerged into main**.
