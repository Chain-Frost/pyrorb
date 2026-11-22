# PyRORB identity and release-preparation handoff — 22 November 2026

## Owner direction and boundaries

The existing repository was renamed to `Chain-Frost/pyrorb`, retaining GitHub repository ID `1451502813`. The owner selected **PyRORB**, requested straightforward identity work now so existing open PRs inherit it, and deferred publication and its integration until the MVP is finalised.

The immediate scope is [#212](https://github.com/Chain-Frost/pyrorb/issues/212). The held publication scope is [#213](https://github.com/Chain-Frost/pyrorb/issues/213), under the existing [release backlog #10](https://github.com/Chain-Frost/pyrorb/issues/10). This record is the handoff for those scopes; it does not replace the scientific feature matrix or change acceptance claims.

## Work packs

| Pack | Timing | Deliverable and acceptance |
| --- | --- | --- |
| A — public identity | Implement now | PyRORB display name, current repository/navigation URLs, `pyrorb` distribution metadata and matching installed-version lookup. Keep the import namespace and compatibility identifiers. |
| B — active stacks | Implement now | Carry the shared changes into Monte Carlo #151, source #198/#201/#202/#203/#204/#205/#207 and MCP #208/#209/#211; preserve branch bases and all unrelated work. |
| C — focused verification | Implement now | Repository/link checks, metadata/provenance tests, isolated renamed-wheel import and existing source/wheel original-CMD checks. Preserve all fixture bytes and existing incomplete cases. |
| D — publication preparation | Draft PR now, held for MVP | Inert workflow template outside `.github/workflows`, offline metadata/artifact readiness checks, and a documented activation procedure. The existing quality workflow remains the only active workflow. |
| E — dependency/package qualification | Before publication | Qualify published canonical reader and PyRomb versions containing final-MVP fixes; remove direct URLs from uploaded requirements including extras; select release version and audit package contents/licence. |
| F — MVP activation | Later owner instruction | Select final integrated supported scope, complete applicable qualification, activate `publish.yml` and `pypi` environment/Trusted Publisher, and perform an explicitly selected release. |

## Compatibility decisions

The distribution becomes `pyrorb`; Python imports remain `runoff_routing`. The package stays at `0.0.0.dev0` with the same licence and dependency pins. A repository/package rename does not rename existing JSON format values, provenance labels, hashing/RNG domains, MCP resource schemes/schema URNs, client registration keys or engine IDs/defaults. Historical receipts and source/fixture identities retain their recorded names and hashes. See the maintained [naming policy](../NAMING.md).

## Publication gates

The current GitHub archive requirement for `ryan-rorb-readers` and Git requirement for PyRomb prevent PyPI publication. Optional extras are still uploaded dependency metadata. In particular, source PR #203 uses a newer canonical-reader revision than main: select dependencies against the final integrated MVP, not against whichever release is available first. Reuse the canonical reader and writer; do not introduce local substitutes.

Desired future publisher: project `PyRORB`, owner `Chain-Frost`, repository `pyrorb`, workflow `publish.yml`, environment `pypi`. No publisher/account/environment configuration was changed by this scope. Registering a pending publisher alone does not reserve the PyPI project name.

## Verification and delivery record

The shared identity change was prepared against main `9c2a87bafdf53f1b1eadc08cd7a1414387551176` and checked on Linux/Python 3.13.5. The changed runtime files are the package description and installed-version lookup; numerical implementations are unchanged.

| Check | Result |
| --- | --- |
| Repository/relative-link hygiene | 541 files; zero errors. |
| Full existing local quality command | Ruff lint/format and strict Pyright passed; **1,267 tests passed, one expected Windows-only skip**. |
| Independent identity review | Preserved identifiers/evidence confirmed; five runnable wheel-filename examples corrected to the renamed artifact. |
| Isolated installed wheel | Imported from a separate virtual environment outside the checkout; `py.typed` present; `version("pyrorb") == identify_implementation().package_version == "0.0.0.dev0"`; no old distribution installed. |
| Exact wheel provenance | `verify_installed_wheel` confirmed the installed source inventory matches the supplied wheel byte for byte. |
| Existing fresh original-CMD probe, source and wheel | Both passed: **50/50 printed-Q cases, 19,550 ordinates, 48 scalar passes and two existing incomplete all-zero unique peak times**. Complete per-case JSON is identical. No native process was launched; wider scientific acceptance remains unassessed. |
| Diff/fixture review | Clean whitespace; no frozen fixtures, research or pre-existing dated receipts changed. |

Checked package-code revision: `package-code-v1-sha256:3d458a2ff0b534170ca4b3e8b127b025890729c7fe00fb4fce5e22e65f87de95`.

Built artifact: `pyrorb-0.0.0.dev0-py3-none-any.whl`; SHA-256 `215c83cec35470e3418e622b47c0e80561ce2e196b20c75409745eeec5f64ebf`. Identical complete source/wheel probe JSON SHA-256: `641199d51af655e7f7ba2c99fa3966b87db78df6a5f29bddfe3775fc304f287c`. These identify this shared identity build, not later branch-specific scientific or MCP code.

Reproduce with the existing `repo-scripts/check_local.py`, a fresh wheel build/install outside the checkout, and `repo-scripts/cmd_public_probe.py` from both environments. Preserve exact artifact and interpreter identity when recording a later run.

Branch propagation and final remote commit identities are tracked in #212 and the affected PR descriptions. The Monte Carlo branch receives only the selected identity patch, preserving its separate baseline and work. The source and MCP stacks inherit the shared change through their existing parents; branch-specific maintained links and the MCP server display name are included without changing protocol identifiers. The held publication draft stays separate. No merge to main, release, package upload or new hosted publishing automation is part of this work.
