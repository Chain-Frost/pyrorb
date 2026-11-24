# PyRORB publication preparation

**Status: preparation #215 is merged; the one-shot activation #220 remains held until canonical-reader migration #233 and final artifact qualification pass.** [Issue #213](https://github.com/Chain-Frost/pyrorb/issues/213) owns this work under [release parent #10](https://github.com/Chain-Frost/pyrorb/issues/10). The separate [identity scope #212](https://github.com/Chain-Frost/pyrorb/issues/212) can flow into active feature PRs now.

The [workflow template](../packaging/pypi/publish.yml.in) remains inert. Draft #220 proposes the separate active one-shot workflow and narrow policy changes. No release tag, repository variable, environment or upload has been created by this reconciliation. A successful metadata check does not authorise publication or establish numerical acceptance.

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

The canonical reader ownership transfer under [#231](https://github.com/Chain-Frost/pyrorb/issues/231) removes the final GitHub archive requirement; the six reader modules are part of the PyRORB distribution. The owner retains the reviewed PR-only PyRomb writer in `requirements-catg.txt`, explicitly installed outside uploaded metadata. No `ryan-rorb-readers` distribution, ryan-tools release or separate reader publisher is needed for PyRORB. PyPI rejects direct URL requirements in uploaded metadata, including extras and inactive markers.

Qualify the migrated canonical source, wheel and sdist reader APIs (including merged #203 site binding), all remaining published extras (MCP, dev and research), and the separately installed PyRomb writer. Preserve the existing numerical and source contracts. Do not execute the superseded standalone reader publisher. Ryan-tools will depend on the verified public PyRORB release only after publication.

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
#220** with the full Python 3.11–3.14 matrix and its fail-closed aggregate. It also requires PYPI_ONE_SHOT_ENABLED=true and no existing pyrorb
PyPI project. Both the quality run and publisher must be first attempts;
reruns are ineligible. Later ordinary main merges are permanently ineligible.
Release preflight, source CMD comparisons and isolated wheel/sdist acceptance
must succeed *before* any GitHub release or tag is created. The published
wheel/sdist come only from that qualified build. The publisher uses a
protected GitHub pypi environment and PyPI Trusted Publishing (OIDC),
rechecking the exact main SHA, tag and PyPI identity before upload.
The `pypi` environment must exist before any publication attempt: GitHub
otherwise creates missing environments without review protection. This
workflow fails closed unless the environment has exactly one required
reviewer, `Chain-Frost`, and custom deployment rules containing exactly one
branch rule named `main` (no tag rules, wildcards or extra branches); both
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

This is a real public release, not TestPyPI. The six canonical readers are now owned by PyRORB under #231/#233. Neither ryan-tools nor a standalone reader distribution is required. PyRomb remains intentionally external to uploaded metadata in `requirements-catg.txt`; do not wait for a PyRomb index release. Fresh release environments verify base installation (including the local canonical reader without ryan_library), all published extras, then the explicitly installed writer. Public engineering and scientific claims remain separate.

Preparation #215 is already merged. Merge and qualify the canonical-reader ownership transfer #233 first; no standalone reader publication is required. The owner reports the PyRORB PyPI account configuration is already complete; verify its matching publisher and protected environment rather than recreating it. Enable PYPI_ONE_SHOT_ENABLED only after all release checks. Confirm #220 contains only activation changes after the dependency work is merged, complete exact-head CI and independent downstream review, then squash-merge the approved activation PR. A pending publisher does not reserve the project name. Its actual merge commit's
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

These are the required matching values; the owner confirms PyPI setup, while live environment and publisher acceptance remain to be verified. A [pending publisher](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/) does not reserve the project name or create a public project until a successful first publication. No PyPI account configuration was inspected during preparation.

## Authoritative references

- [PyPI: using a Trusted Publisher](https://docs.pypi.org/trusted-publishers/using-a-publisher/) describes OIDC, environment matching and job-scoped `id-token: write`.
- [PyPI: creating a project through OIDC](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/) describes pending publishers and first publication.
- [PyPA publishing action](https://github.com/pypa/gh-action-pypi-publish) documents separate build/upload jobs, Linux support and artifact publishing.
- [GitHub: `workflow_dispatch`](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_dispatch) describes manual workflow execution and default-branch availability.
- [GitHub: secure use](https://docs.github.com/en/actions/reference/security/secure-use) describes least privilege, pinned action revisions and safe handling of workflow inputs.
- [Setuptools: direct URL dependencies](https://setuptools.pypa.io/en/latest/userguide/dependency_management.html#direct-url-dependencies) explains why current Git/archive requirements block an index release.


The environment and deployment-branch-policy REST reads require only the existing
job-scoped `actions: read` permission; no administration permission is requested.
See GitHub's [environment endpoint](https://docs.github.com/en/rest/deployments/environments#get-an-environment)
and [deployment policy endpoint](https://docs.github.com/en/rest/deployments/branch-policies#list-deployment-branch-policies).
A protected-branches-only policy is insufficient because it can include branches
other than `main`. API failures or incomplete policy inventories block release.
