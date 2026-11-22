# PyRORB publication preparation

**Status: preparation only; publication and this draft PR's merge remain deferred until the owner finalises the MVP.** [Issue #213](https://github.com/Chain-Frost/pyrorb/issues/213) owns this work under [release parent #10](https://github.com/Chain-Frost/pyrorb/issues/10). The separate [identity scope #212](https://github.com/Chain-Frost/pyrorb/issues/212) can flow into active feature PRs now.

The [workflow template](../packaging/pypi/publish.yml.in) lives outside `.github/workflows`, so GitHub Actions cannot execute it. The existing workflow allowlist, hosted CI permissions and repository settings are unchanged. No release tag, GitHub environment, PyPI publisher or upload is created by this preparation. A successful metadata check does not authorise publication or establish numerical acceptance.

## Agreed identity

| Surface | Value |
| --- | --- |
| Display name | PyRORB |
| GitHub repository | `Chain-Frost/pyrorb` |
| Distribution name | `pyrorb` (PyPI normalises `PyRORB` to the same name) |
| Python import namespace | `runoff_routing` |
| Existing module CLI entry points | `python -m runoff_routing.<module>` |
| Future publishing workflow filename | `publish.yml` |
| Future publishing environment | `pypi` |

The project name does not require an import rename or a new CLI executable. Serialized format identifiers, fixture bytes and established provenance domains remain unchanged. The [quickstart](QUICKSTART.md) documents the available module commands.

## Current publication blockers

The unchanged development version is `0.0.0.dev0`; it is not a selected release. The owner must choose the first version explicitly, for example `0.1.0a1`, after defining the supported MVP. The example is not a version assignment or a release commitment.

Current package metadata includes a direct archive URL for `ryan-rorb-readers` and a direct Git URL for PyRomb in the `catg` and `dev` extras. PyPI rejects direct-URL dependencies in uploaded distribution metadata; hiding them behind an extra or an inactive environment marker does not remove them from `Requires-Dist`. Pip accepting a local source checkout is not evidence that the same distribution can be uploaded. See [setuptools' direct-URL dependency guidance](https://setuptools.pypa.io/en/latest/userguide/dependency_management.html#direct-url-dependencies).

Qualify published versions containing the actual reader/writer APIs and fixes consumed by the **final integrated MVP**. The staged source work in [PR #203](https://github.com/Chain-Frost/pyrorb/pull/203) consumes a newer reader revision than main; do not pick a release solely because it is available on an index. Preserve the canonical `ryan-rorb-readers` and PyRomb implementations and the accepted reuse/licence decision. Development-only source pins can move to development constraints or requirements outside uploaded metadata when appropriate; they must not remain in an uploaded `dev` extra. Review every final extra, including the separately staged MCP dependency, before selecting a release.

The identity work, source integration and release scope must be assembled before package qualification. This preparation does not select published dependency versions, change the version, or claim that a clean PyPI installation currently works. The existing [compatibility qualifications](COMPATIBILITY.md), [feature matrix](CMD_FEATURE_MATRIX.md) and [status](STATUS.md) continue to define the supported numerical scope.

## Offline readiness check

[`check_release.py`](../repo-scripts/check_release.py) reads files only. It uses `packaging` to parse requirements and versions and never contacts an index, installs a dependency, launches a native engine or uploads a file. Install release tooling in a development environment:

```sh
python -m pip install build packaging twine
```

A source-only preflight reports the current blockers. This example is expected to fail against the unchanged bootstrap version and URL requirements:

```sh
python repo-scripts/check_release.py --tag v0.1.0a1
```

After an explicitly selected version and dependency update, build into a **new, empty directory outside the repository** and inspect that exact pair. Replace `../pyrorb-release-artifacts` if it already exists; do not mix older builds with a candidate or silently clear another working directory.

```sh
python -m build --outdir ../pyrorb-release-artifacts
python -m twine check --strict ../pyrorb-release-artifacts/*
python repo-scripts/check_release.py --tag v0.1.0a1 --dist ../pyrorb-release-artifacts
```

The checker enforces:

- Normalised distribution name `pyrorb`, an explicitly non-bootstrap version, no PyPI-ineligible local version suffix, and the exact `v<version>` tag spelling.
- No direct-URL requirement in **any** source dependency group or built `Requires-Dist`, regardless of extra or environment marker.
- Exactly one wheel and one `.tar.gz` sdist with no other entries in the upload directory.
- Both artifact filenames and internal `METADATA`/`PKG-INFO` agree with the selected name/tag; built versions agree with source.
- Static release identity/dependency fields, declared extras matching source, and matching `Requires-Dist` fields in the wheel and sdist.

The source-only mode explicitly reports that artifacts were not checked. Archive metadata is inspected without extracting files. This is a bounded packaging gate: it does not check whether named dependencies exist on PyPI, qualify dependency behaviour, validate the licence, prove reproducibility, inspect every package member or replace [source/installed-wheel acceptance](REGRESSION_DATASET.md#portable-offline-vm-target-installation). `twine check --strict` adds distribution metadata and long-description validation. A later clean install must actually resolve the selected published dependencies.

## Proposed manual workflow

The template becomes runnable only after a separately approved activation change. It has **only `workflow_dispatch`**, requires `main` in `Chain-Frost/pyrorb` and repository variable `PYPI_PUBLISH_ENABLED=true`, and checks that the supplied existing `v<version>` tag points to the exact dispatched commit. It never creates a tag or a GitHub release. Dispatch from another branch, or dispatch with an older tag against a newer main commit, cannot publish. Retrying an interrupted release requires reviewing its state; the upload action keeps `skip-existing=false` so an existing file is not silently treated as a complete release.

The build job has read-only repository access and no OIDC publishing permission. It runs the existing pure-Python quality suite and original-CMD fixture probe, builds and checks both artifacts, installs wheel and sdist into separate fresh environments outside the checkout, and checks import origin and installed version. The existing `verify_installed_wheel` function verifies that both installations' package sources match the exact built wheel before recording its digest and package-code fingerprint. The job then compares the complete source and installed-wheel probe JSON, preserving per-case Q/scalar/status details. This reuses the existing comparator and retains its numerical limitations; it is not a second feature matrix or a new scientific acceptance runner. The provisional install selection includes the `catg` extra; revisit that selection against all extras and supported workflows in the final MVP.

The publish job receives only the checked distribution artifact by its same-run immutable artifact ID, with download digest mismatch treated as an error. It performs no source checkout, project dependency installation or build. Only that job requests `id-token: write`, enters environment `pypi` and uses the official PyPA publishing action with Trusted Publishing and attestations. The environment must be configured with the owner-selected review/protection settings **before** activation; merely naming an environment in YAML does not configure a review gate. Keep any required reviewer gate ahead of upload so the exact build receipts can be examined.

Successful runs retain artifact hashes, exact source commit/tag, tool/dependency versions and complete existing source/wheel CMD JSON for 30 days. Copy the selected receipts to the established work record/evidence location before retention expires. The same built wheel and sdist are transferred for upload. The template uses a Linux/Python 3.13 release build, consistent with the current single-platform pure-Python policy; it neither launches native RORB nor claims a Windows-native execution result.

### Action revisions

These pins were resolved from official upstream refs on 22 November 2026. Re-read the current action and PyPI guidance and review newer fixes before activation; the preparation date is not a permanent approval of a dependency revision.

| Action | Reviewed upstream ref | Commit used by template |
| --- | --- | --- |
| `actions/checkout` | [`v7`](https://github.com/actions/checkout/tree/v7) | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| `actions/setup-python` | [`v7`](https://github.com/actions/setup-python/tree/v7) | `6d4fd22b20465ccc0f7354476588e8df7c9ca0e0` |
| `actions/upload-artifact` | [`v7.0.2`](https://github.com/actions/upload-artifact/releases/tag/v7.0.2) | `cf430e030ddbb5b0abf93d22962f4752f3646cd9` |
| `actions/download-artifact` | [`v8.0.2`](https://github.com/actions/download-artifact/releases/tag/v8.0.2) | `9000827ccba6bdab643e8b6fd33ac0654aef8333` |
| `pypa/gh-action-pypi-publish` | [`v1.14.3`](https://github.com/pypa/gh-action-pypi-publish/releases/tag/v1.14.3) | `7245906fb61fa33a13554f9d5fb856fe61758086` |

The template keeps development tools consistent with the repository's current dependency policy; it does not introduce a release lock. Select and record reproducible release build/dependency constraints during final package qualification, and update the template's install commands if that decision requires them.

## Later activation sequence

1. **Select the MVP and integrated revision.** Confirm which active PRs enter the release and document supported behaviour, incomplete outcomes and deferred capability/scientific work. A bounded alpha need not close every full-CMD or post-MVP issue, but its claims must match its evidence.
2. **Qualify dependencies and package contents.** Obtain suitable published canonical reader/PyRomb versions, remove direct URLs from all uploaded extras, select the version and release constraints, and review notices/licence, provenance, public data and included files. Confirm source, wheel and sdist imports and each supported optional workflow in fresh environments with index dependencies.
3. **Complete applicable acceptance.** Use the existing local/approved quality tools and source/installed-wheel procedure. Retain exact revision, wheel/sdist hashes, package-code fingerprint, interpreter/platform, complete per-case reports and every relevant limitation. Keep independent scientific qualification separate from software checks.
4. **Obtain the owner's instruction to merge and activate.** The preparation PR remains draft/held until that instruction. Re-review this template and its pins, move it to `.github/workflows/publish.yml`, and narrowly update the existing workflow allowlist/test and CI policy for the selected publishing workflow. Do not weaken the current guard during preparation.
5. **Configure the real environment and publisher.** Create/configure `pypi`, select its reviewers/branch restrictions, and configure the matching PyPI Trusted Publisher. Inspect any existing publisher targeting the previous repository name and replace its repository binding as appropriate; a GitHub rename does not rewrite that external configuration. Set `PYPI_PUBLISH_ENABLED=true` only as part of the approved activation.
6. **Select and execute the release.** With explicit publication instruction, create the chosen `v<version>` tag on the reviewed main commit, dispatch from that same commit, inspect the exact artifacts/receipts before environment approval, then verify published metadata and an isolated index installation. Record the resulting release URL and acceptance receipt. Neither the template nor this document performs those actions now.

### PyPI pending-publisher fields

| Form field | Enter at approved setup |
| --- | --- |
| PyPI Project Name | `PyRORB` |
| Owner | `Chain-Frost` |
| Repository name | `pyrorb` |
| Workflow name | `publish.yml` (filename only, not the display name or full path) |
| Environment name | `pypi` |

These are planned matching values, not confirmation that the environment or publisher exists. A [pending publisher](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/) does not reserve the project name or create a public project until a successful first publication. No PyPI account configuration was inspected during preparation.

## Authoritative references

- [PyPI: using a Trusted Publisher](https://docs.pypi.org/trusted-publishers/using-a-publisher/) describes OIDC, environment matching and job-scoped `id-token: write`.
- [PyPI: creating a project through OIDC](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/) describes pending publishers and first publication.
- [PyPA publishing action](https://github.com/pypa/gh-action-pypi-publish) documents separate build/upload jobs, Linux support and artifact publishing.
- [GitHub: `workflow_dispatch`](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_dispatch) describes manual workflow execution and default-branch availability.
- [GitHub: secure use](https://docs.github.com/en/actions/reference/security/secure-use) describes least privilege, pinned action revisions and safe handling of workflow inputs.
- [Setuptools: direct URL dependencies](https://setuptools.pypa.io/en/latest/userguide/dependency_management.html#direct-url-dependencies) explains why current Git/archive requirements block an index release.
