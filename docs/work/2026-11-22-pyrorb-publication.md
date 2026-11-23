# Deferred PyRORB publication preparation — 22 November 2026

## Scope and state

- **Issue:** [#213](https://github.com/Chain-Frost/pyrorb/issues/213), under deferred release parent [#10](https://github.com/Chain-Frost/pyrorb/issues/10).
- **Status:** preparation implemented and reviewed in held draft PR #215; merge, activation and publication remain deferred until the owner finalises the MVP.
- **Owner:** final package qualification and activation remain unassigned until selected by the owner; this record does not imply ongoing background work.
- **Branch:** `build/pyrorb-publication-preparation-20261122`; originally stacked on [identity PR #214](https://github.com/Chain-Frost/pyrorb/pull/214). PR #214 subsequently merged into `main` at `e773472b6f0386257643a89a66a0b1dfe4a75af1`, retaining the same identity tree. The held publication draft now targets `main` and absorbs that merge without rewriting history.
- **Original identity base:** `5344b95f5dccefc2fb8327d242414501cd9cc0e9`, tree `66eef397d9ca4f5c01cb7abf10065424caf2ab02`. The subsequently merged `main` revision has the identical tree. The original preparation head was `f3986af37127ab4ab51530c381cee4dbacf95a2d` (tree `a4cb953f18e12186b0e274f9c947b59e7050db00`). The final reviewed head is recorded in the PR/issue receipt.
- **Review date:** 22 November 2026; session-based, with no scheduled follow-up.

The [publication guide](../PUBLISHING.md) is the maintained release-preparation contract. The immediate identity/branding scope remains separate and can enter feature PRs without this publication patch.

## Implemented boundaries

The [template](../../packaging/pypi/publish.yml.in) is stored outside `.github/workflows`. It cannot run there. Existing `.github/workflows/quality.yml`, workflow allowlist, its policy test and hosted permissions are unchanged. No environment, publisher, tag, release or upload was created or enabled.

The proposed future workflow is manual-only and checks repository, `main`, an explicit enable variable and a tag matching the exact dispatched revision. It separates read-only build/verification from the protected-environment OIDC upload job. Official upstream action revisions are pinned. It reuses the existing source/installed-wheel probe and provenance verifier; there is no new numerical comparator, runtime dependency or scientific acceptance policy.

The [offline checker](../../repo-scripts/check_release.py) verifies static source identity, selected version/tag, every dependency group, both built artifacts' filenames/internal metadata, declared extras, wheel/sdist dependency agreement and source-to-artifact requirement parity (including optional extras and markers). Every direct-URL requirement is rejected without evaluating markers. The checker does not contact a service, upload, install dependencies or run model code. Its focused tests use synthetic metadata/archives.

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

The following counts and hashes are **historical results for original preparation head `f3986af37127ab4ab51530c381cee4dbacf95a2d`**, not newly executed checks or current digests after the corrective review.

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


## Focused independent corrective review — 22 November 2026

The original preparation head was reviewed against #213, the allowed workflow inventory and the current upstream artifact-download inputs. The existing Windows quality run for that original head completed successfully; its result and the 22 focused release tests above apply only to that revision.

A concrete false-pass was identified: if a build emitted **the same incorrect Requires-Dist fields in both wheel and sdist**, their mutual comparison passed despite disagreement with the release branch's source requirements. The checker now normalises PEP 508 dependency names/extras and adds the correct optional-extra markers before comparing the **complete requirement multiset in each built artifact** against the source declarations. Invalid requirements remain independently blocked. Focused new tests cover shared wheel/sdist dependency drift, an undeclared requirement within an existing extra, and legitimate conditional markers (including disjunctions) as rendered by setuptools.

A separate local Python 3.13.5/setuptools 82.0.1 fixture built a real wheel: the normalised source and wheel requirement inventories agreed, while three mutated requirement inventories were rejected. This fixture validates the comparison design, **not** an execution of this repository's full pytest/Ruff/Pyright suite. The original suite/negative-control hashes remain historical evidence above; new head CI and any further verification are reported separately in the PR/issue. No change was made to the inert workflow template, active hosted workflow, dependency pins, version, publication settings, or scientific acceptance.

## Follow-up to fresh independent review — 22 November 2026

The independent review of corrective head `443ed27c03e4ad8f77686e3da14395c209553b40`
reported two actionable findings: P2, an unrelated internal wheel `.dist-info` name/version
could pass; P3, absent/duplicate/unsupported `Metadata-Version` and malformed header
lines were silently accepted. Full reproduction and real-artifact receipt are in
[the PR's review comment](https://github.com/Chain-Frost/pyrorb/pull/215#issuecomment-7081517147).

Both findings are addressed by bounded changes to the offline checker and focused
negative controls. Wheel directory identity is matched to its parsed filename
with name and PEP 440 version normalisation, accepting legitimate historical spellings.
Built metadata now requires exactly one supported metadata version and rejects parser
header defects. The Core Metadata specification defines versions through 2.6 as of
May 2026; unknown future metadata requires deliberate checker qualification.

The reviewer independently executed 25 release tests (29 with repository guards),
Ruff and strict Pyright successfully on Windows/Python 3.14.6. Its exact-head
wheel and sdist built successfully and the checker returned the expected
**19 bootstrap/direct-URL blockers** without unexpected dependency mismatches.
Those results apply to the *reviewed pre-fix head*, not automatically to these
subsequent changes. Focused correction verification and current CI must be
recorded against the resulting revision. No version, pin, hosted workflow,
permissions, environment, publisher, merge or release decision has changed.

## Separate activation PR staged for review — 23 November 2026

The owner requested a reviewable PyPI publishing workflow PR and comparison with `ryan-tools`. The
`ryan-tools` chain publishes automatically after verified `main` releases, but **PyRORB retains
manual-only dispatch** and its own final-MVP release gates. A separate draft PR stacked on
preparation #215 proposes `.github/workflows/publish.yml` by copying the reviewed inert template,
then narrowly updates the existing workflow allowlist and its exact-policy test. Its merge remains
held pending explicit owner approval; `main` retains only `quality.yml` until then.

The change does not alter release identity/version, dependency pins, action permissions outside
the proposed workflow, publication settings, environment, PyPI account, tags or scientific code.
Only structural checks on the copied workflow and policy edits are established during PR creation;
CI, independent review, exact-head local tests and actual publishing remain separately unverified.
The next release task remains final-MVP dependency qualification and the source/installed-wheel
gates, not an automatic release or scheduled main-merge publication.

## Owner release policy revision — 23 November 2026

The owner prefers an automatic release after successful main CI, but only
one initial real public test publication before disabling the publisher until
a final MVP exists. Use the same YY.M.D.N date versions as ryan-tools and
ryan-culverts (Australia/Perth date, incrementing daily revision). A focused
allocator and local-only checkout stamper, plus synthetic tests, are staged.

The previous PR #220 Windows CI failed only the scaffold test that still
required a single workflow (1 failed, 1307 passed, 3 skipped). That separate
exact-set assertion is now corrected. The **existing one-shot auto-publishing
workflow conversion remains to be reviewed and completed**; the current
publishing workflow is still manual-only. No claim of an automatic release
or production PyPI upload is made. Current Git/archive dependency URLs
still block public package metadata qualification. No merge, release,
tag, publisher/environment setup or upload has been performed.
