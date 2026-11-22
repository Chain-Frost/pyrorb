# Deferred PyRORB publication preparation — 22 November 2026

## Scope and state

- **Issue:** [#213](https://github.com/Chain-Frost/pyrorb/issues/213), under deferred release parent [#10](https://github.com/Chain-Frost/pyrorb/issues/10).
- **Status:** preparation implemented and locally checked; prepare a separate draft PR, with merge, activation and publication held until the owner finalises the MVP.
- **Owner:** final package qualification and activation remain unassigned until selected by the owner; this record does not imply ongoing background work.
- **Branch:** `build/pyrorb-publication-preparation-20261122`, stacked on the shared identity draft [PR #214](https://github.com/Chain-Frost/pyrorb/pull/214).
- **Base identity revision:** `5344b95f5dccefc2fb8327d242414501cd9cc0e9`, tree `66eef397d9ca4f5c01cb7abf10065424caf2ab02`. Local verification began from the identical tree at `b9719cd07f24a1aed50426312fd475b41ff49706` and added the publication files described here. The published preparation head belongs in the PR/issue receipt.
- **Review date:** 22 November 2026; session-based, with no scheduled follow-up.

The [publication guide](../PUBLISHING.md) is the maintained release-preparation contract. The immediate identity/branding scope remains separate and can enter feature PRs without this publication patch.

## Implemented boundaries

The [template](../../packaging/pypi/publish.yml.in) is stored outside `.github/workflows`. It cannot run there. Existing `.github/workflows/quality.yml`, workflow allowlist, its policy test and hosted permissions are unchanged. No environment, publisher, tag, release or upload was created or enabled.

The proposed future workflow is manual-only and checks repository, `main`, an explicit enable variable and a tag matching the exact dispatched revision. It separates read-only build/verification from the protected-environment OIDC upload job. Official upstream action revisions are pinned. It reuses the existing source/installed-wheel probe and provenance verifier; there is no new numerical comparator, runtime dependency or scientific acceptance policy.

The [offline checker](../../repo-scripts/check_release.py) verifies static source identity, selected version/tag, every dependency group, both built artifacts' filenames/internal metadata, declared extras and wheel/sdist dependency agreement. Every direct-URL requirement is rejected without evaluating markers. The checker does not contact a service, upload, install dependencies or run model code. Its focused tests use synthetic metadata/archives.

## Verification

Executed on Linux using Python **3.13.5**, `packaging` **26.3**, Ruff **0.16.6**, strict Pyright and the existing development environment:

| Check | Result |
| --- | --- |
| Ruff on checker and focused tests | Passed |
| Ruff format check on checker and focused tests | Passed |
| Strict Pyright on checker and focused tests | 0 errors, 0 warnings |
| Focused release metadata tests | 22 passed |
| Existing repository-guard tests alongside release tests | 26 total passed |
| Repository hygiene and local Markdown links | Passed; only the existing quality workflow remains executable |
| Template YAML parse, manual-only trigger and job permissions | Passed |
| Template shell syntax | All four `run` blocks passed `bash -n`; embedded Python syntax checked independently |
| Wheel and sdist build from branded preparation workspace | Passed using `python -m build --installer uv`; isolated backend `setuptools==84.2.1` |
| Real source/wheel/sdist release-readiness negative control | Correctly blocked current bootstrap version/tag and URL requirements |
| Independent code/template review | Passed; no blocking finding |

The first default isolated build attempt encountered the local interpreter's unavailable `ensurepip`. Selecting the existing `uv` installer completed the same source/wheel build without changing package dependencies. The release template retains ordinary `python -m build` for a provisioned GitHub runner; no hosted run was attempted.

The real branded negative control produced **19 blockers**, including **9 direct-URL detections**: base reader, CATG writer and development-extra writer in each of source, wheel and sdist. The remainder are repeated bootstrap-version and selected-tag mismatches across source/artifact filenames/internal metadata. It reported **zero distribution-name errors** after the identity change and no extra/dependency consistency mismatch between the two built artifacts. This expected failure is evidence that blocked metadata is rejected, not a failed implementation test or a publishable package.

| Verified object | SHA-256 |
| --- | --- |
| `repo-scripts/check_release.py` | `ccb3db55e93e15390c4bcb1822e0cce1e0e1846e80ab7dab646e82a89e8a1a5d` |
| `packaging/pypi/publish.yml.in` | `a6e50c68ee03525ae48ab6ee5f5e99303c8cdb79e0b2f1620d151829c48a9e95` |
| Negative-control `pyrorb-0.0.0.dev0-py3-none-any.whl` | `87ec6aee37066d518cb10ccd7d7a2b6871bc5cb2e4b47ddbc5435d77530c219d` |
| Negative-control `pyrorb-0.0.0.dev0.tar.gz` | `4b9e6b9937e4caf147ab3311ba97bfa582ec8ffbded51f27bb91fc39f670a538` |

Artifacts were built outside the checkout and are not committed. These wheel/sdist hashes identify local negative-control artifacts, not release candidates. The shared identity [receipt](2026-11-22-pyrorb-identity.md) carries the unchanged product's applicable full source/wheel checks; this offline tooling scope does not claim a new numerical campaign. `twine check`, clean index installation with future published dependencies, the hosted publication workflow and upload have not been executed as release acceptance.

## Held work and next action

The bootstrap version and direct reader/PyRomb source pins remain unchanged. Final qualification must use the integrated MVP's required APIs/fixes, including the newer reader consumed by source PR #203 and any final MCP extra. Select published dependency versions, a release version, release constraints and supported public claims before activation. Preserve canonical reader/writer reuse and existing licence/provenance decisions.

**Next action:** keep this preparation PR in draft while the owner assembles the MVP and final dependency requirements. Once the owner selects release scope, complete the guide's qualification/acceptance gates, then obtain the explicit merge/activation/publication instruction. Configure the actual `pypi` environment and matching Trusted Publisher only at that later stage. No automatic merge, tag-triggered release or publication is authorised by this record.
