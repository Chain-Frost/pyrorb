# PyRORB publication preparation

**Status: a one-shot automatic release is staged in an unmerged draft; PyPI activation still requires qualified dependencies and account-level setup.** [Issue #213](https://github.com/Chain-Frost/pyrorb/issues/213) owns this work under [release parent #10](https://github.com/Chain-Frost/pyrorb/issues/10). The separate [identity scope #212](https://github.com/Chain-Frost/pyrorb/issues/212) can flow into active feature PRs now.

The [workflow template](../packaging/pypi/publish.yml.in) lives outside `.github/workflows`, so it cannot execute in the preparation PR. A separate **draft activation PR**, stacked on the preparation PR, proposes a copy at `.github/workflows/publish.yml` and the narrow repository-guard/test changes. That activation change must not merge without owner approval and completion of the release gates below. Neither PR creates a release tag, GitHub environment, PyPI publisher, upload or enabled repository variable. A successful metadata check does not authorise publication or establish numerical acceptance.

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
- Both artifact filenames and internal `METADATA`/`PKG-INFO` agree with the selected name/tag; built versions agree with source. The wheel's `.dist-info` directory must match the wheel filename's distribution/version identity, allowing equivalent historical name/version normalisation.
- Exactly one supported core `Metadata-Version` (currently defined through 2.6), `Name` and `Version` in each built artifact. Missing/duplicate/unsupported versions and detected malformed metadata headers are blocked; unknown future formats must be reviewed before admission.
- Static release identity/dependency fields and declared extras matching source. Parsed PEP 508 `Requires-Dist` entries in **each** artifact must also match the source dependency inventory (including optional-extra and environment markers) after name/extra normalisation; matching wheel and sdist metadata cannot mask shared dependency drift.

The source-only mode explicitly reports that artifacts were not checked. The source-to-artifact comparison is deliberately conservative about marker representation; review any backend-specific marker transformations during final package qualification rather than bypassing a mismatch. Archive metadata is inspected without extracting files. This is a bounded packaging gate: it does not check whether named dependencies exist on PyPI, qualify dependency behaviour, validate the licence, prove reproducibility, inspect every package member or replace [source/installed-wheel acceptance](REGRESSION_DATASET.md#portable-offline-vm-target-installation). `twine check --strict` adds distribution metadata and long-description validation. A later clean install must actually resolve the selected published dependencies.

## One-shot automated PyPI test release (draft #220)

PyRORB will use the same YY.M.D.N date-based versions as ryan-tools and
ryan-culverts, for example v26.11.23.1 if first released on 23 November
2026. The release date uses Australia/Perth. The revision is allocated
monotonically against known release tags. The development checkout retains
0.0.0.dev0 until a qualified release; only the temporary release checkout
is stamped with the selected date version.

Draft PR #220 proposes a single automatic release when existing Windows
quality completes on main for the **exact merged commit of activation PR
#220**. It also requires PYPI_ONE_SHOT_ENABLED=true and no existing pyrorb
PyPI project. Later ordinary main merges are permanently ineligible.
Release preflight, source CMD comparisons and isolated wheel/sdist acceptance
must succeed *before* any GitHub release or tag is created. The published
wheel/sdist come only from that qualified build. The publisher uses a
protected GitHub pypi environment and PyPI Trusted Publishing (OIDC),
rechecking the exact main SHA, tag and PyPI identity before upload.
The `pypi` environment must exist before any publication attempt: GitHub
otherwise creates missing environments without review protection. This
workflow fails closed unless the environment has exactly one required
reviewer, `Chain-Frost`, and a restricted deployment-branch policy; both
conditions are checked before creating the tag and again before upload.
During owner setup, restrict the environment to `main` and confirm its
required reviewer can approve the deployment.

The qualified Git tag is created before PyPI upload. A **public GitHub
Release is created only after upload succeeds**, so failed uploads leave at
most a tag, not a falsely published GitHub Release. A separate
`actions:write` job disables `publish.yml` after the upload succeeds,
even if GitHub Release creation fails. If disabling fails, execute
`gh workflow disable publish.yml` with suitable GitHub permissions. If
GitHub Release creation fails after a successful PyPI upload, verify the
PyPI distributions and create/verify the exact matching GitHub Release
manually; never rerun an upload merely to repair the GitHub Release.

This is a REAL public release and not a TestPyPI simulation. The current
source has direct Git/archive requirements for the canonical reader and
PyRomb writer; these are blocked by PyPI upload metadata policy and the
release checker. Qualify published versions of these dependencies with
the final required fixes; do not substitute outdated distributions merely
to create a release. Public engineering claims and scientific acceptance
remain separate even after the first package is published.

Before merging #215 then #220: establish release scope and dependent
published versions, validate clean source/wheel/sdist installs, configure
a protected GitHub environment named pypi, configure PyPI's matching
Trusted Publisher (Chain-Frost / pyrorb / publish.yml / pypi), and set
the repository variable PYPI_ONE_SHOT_ENABLED=true. The first pending
publisher does not reserve the PyPI name. **After #215 merges, retarget
#220 from the preparation topic branch to `main`, confirm its diff contains
only activation changes, complete exact-head CI/independent Codex review,
and squash-merge the approved activation PR.** Its actual merge commit's
successful main CI is the only eligible automatic release trigger.
Confirm artifacts and attestations, then verify that publish.yml is
disabled. Future normal automatic releases require a separate MVP PR.

The manual-only template under packaging/pypi/publish.yml.in remains an
inert preparation asset of PR #215; this activated one-shot proposal
supersedes that template.

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
