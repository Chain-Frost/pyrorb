# Development guide

## Current delivery sequence

The deliverable remains **CLI, Python API and text-file I/O only**. The #119 MVP, #136/#175 deterministic rainfall, #155 persisted reporting, #138–#143 file workflow and #110/#125 independent Python counterparts are delivered. [STATUS.md](STATUS.md) is the current delivery summary and links exact receipts. Full CMD #5, native rainfall/selection and independent engineering accuracy remain separately qualified.

Current work follows [BACKLOG.md](BACKLOG.md): C/#96 upstream producer acceptance, A/#90–#92 genuine native feature/site/edge gaps, B/#100 the comparator, #8/#192/#193 rainfall/ARF science and #152 native representative/critical-duration rules. Monte Carlo #9 stays on draft #151; its current #150/#189/#190/#191/#148 packs build on completed staged software. Completed implementation issues are not reassigned. Advanced #114–#118, #103, #144, #63 and release #10 remain deferred. Preserve the [single matrix](CMD_FEATURE_MATRIX.md).

## Development engines and offline CMD reference

**Temporary product default (owner decision 15 November 2026): `python-cmd/cmd-6.44`.** Newly constructed schema-2 projects, `EngineSelection()` and ordinary project/CLI dispatch now select the pure-Python-compatible CMD backend for the current MVP/source and numerical work. The independent `python/engineering-v1` remains explicitly available and is the **intended long-term default** once its method is ready; `rorb-cmd` remains an explicit optional local native adapter. Never silently switch engines. Preserve historical schema-1 engine-less projects as `python/engineering-v1` and all explicit persisted choices as stored.

The pinned reference is the **original RORB-CMD 6.44 source/report corpus**, preserved byte-for-byte in the one public [regression dataset](REGRESSION_DATASET.md). The existing [`cmd_public_probe.py`](../repo-scripts/cmd_public_probe.py) freshly executes the current `python-cmd` code against the original published input triplets, then compares the complete printed hydrographs and available scalars to separately retained native observations. It runs on Python 3.13/3.14 on Linux or Windows without the native executable, QGIS/GDAL, private checkout or a Windows agent. Re-run it from **both a source checkout and a wheel installed outside the checkout**; record exact revisions, source and wheel hashes, and all pass/unsupported/incomplete states. Its prior `--snapshot` data are not fresh current computation. See [the regression contract](REGRESSION.md) for native-versus-synthetic evidence distinctions.

New synthetic tests should exercise source variations, invariants, conservation, error handling and numerical edge cases without inventing CMD reference outputs. A new synthetic test becomes a CMD **equivalence** comparison only when a genuine RORB-CMD reference for those exact effective inputs, output sites and complete time horizon has been authenticated and admitted to the existing register. After the particular `python-cmd` feature profile is **independently verified** against original RORB-CMD, its pinned computation can also provide a **synthetic, offline comparison baseline** for improving the future default `python` engine: evaluate exactly matched effective inputs, complete discharge series, peaks, times and physical-volume absolute/percentage differences. This requires **no new native launch for each synthetic variation**. Label the result as `python` versus *qualified `python-cmd` proxy*, never as a new original RORB-CMD run; do not use an unsupported/unreviewed CMD feature as a trusted proxy. Direct native equivalence for new source features still requires distinct authentic CMD evidence when applicable.

## Environment and layout

Python 3.13 is the minimum supported interpreter; Python 3.14 is also supported. For current **pure-Python** work, Linux and Windows verification are equivalent: one successful run using **either Python 3.13 or 3.14 on either OS** is sufficient. Two-OS and two-interpreter campaigns are deferred until later development (owner decision 2026-11-15). Windows remains a supported deployment target and is required for native Windows-only executables or explicitly OS-dependent functionality. Use the normal user installation; a virtual environment is not mandatory. Install `py -3.13 -m pip install -e ".[dev]"` on Windows or `python3.13 -m pip install -e '.[dev]'` on Linux; Python 3.14 may be substituted. The routing kernels use the standard library. The package installs the canonical ryan-tools reader from its pinned maintained distribution; edited CATG writing uses the optional pinned PyRomb dependency. Avoid unrelated numerical, GIS, pandas, Excel or acceleration dependencies; retain exact environment versions in acceptance records. Ruff is pinned to 0.16.6 in both its configuration and the development dependency. Other development tools are initially unpinned; reproducible lock/constraint selection is an S0 follow-up, not an assumed environment guarantee.

Use src/runoff_routing for reusable code, tests for focused tests, repo-scripts for developer tools, docs for maintained contracts and useful dated evidence, and ignored .local for local native/reference material. Reusable report-reader changes belong in ryan-tools; this repository consumes the merged canonical reader through thin adapters. Do not vendor, copy or retain a second parser/fallback. The existing Python 3.13/3.14 installable dependency boundary and owner-approved reuse/licence decision remain in force.

Inspired by ryan-tools: Python 3.13-compatible typing, Ruff at 120 columns, strict Pyright, single-platform pure-Python development verification, installed-wheel checks, safe mapped/UNC paths, coherent batch pushes, focused tests and one authoritative work record. Do not inherit automatic version bumps, bundled wheels, broad GIS dependencies, submodules, recurring audits or release-on-main automation.

## Ruff policy

[`ruff.toml`](../ruff.toml) is the single lint configuration. It adopts all 41 explicit rule families selected in the reviewed ryan-tools configuration, plus annotation checks (`ANN`): 42 families covering correctness, modern Python, imports, naming, security, exceptions, logging, complexity, paths, performance, NumPy/pandas and pytest. Python 3.13 syntax compatibility and 120-column formatting are retained. Ruff 0.16.6 is required; upgrades must change the dependency and configuration together and review the resulting diagnostics.

This greenfield package does not inherit ryan-tools' legacy exceptions. Global ignores are limited to formatter overlap/line wrapping. Tests permit assertions and non-package discovery; developer entry points permit non-package discovery. Subprocess exemptions are confined to reviewed fixed-command call sites, with comments; the security family remains enabled elsewhere. Complexity is capped at 10. Broad exceptions, unused suppressions, old NumPy RNG APIs and parser code do not get automatic exemptions.

Lint and format checks are read-only. Preview rules and unsafe fixes are off; use deliberate, reviewed fixes rather than an automatic baseline rewrite. Tests protect the policy itself but are not substitutes for executing Ruff and Pyright. Missing tools or an unrun target environment must not be reported as a passing gate.

## Local checks

```powershell
py -3.13 repo-scripts/check_local.py
py -3.13 -m build
```

On Linux, use the equivalent Python 3.13 commands (Python 3.14 is also valid):

```sh
python3.13 repo-scripts/check_local.py
python3.13 -m build
```

The first command runs repository hygiene, Ruff lint/format checks, strict Pyright, then non-native/non-benchmark tests. It stops on failure and does not install dependencies or launch reference programs. `check_local.cmd` is the double-click, pause-at-end equivalent. The source-only hygiene check can also run independently: `python repo-scripts/check_repository.py`.

The build command is a separate package milestone check. Install the wheel outside the repository either into a fresh virtual environment or a fresh `pip --target` directory; **the latter is equivalent** when the installed package origin is strictly inside that destination, no editable checkout is imported, and exact source/installed-wheel results are compared. Record wheel hash, source/merge-tree identity, selected runtime, per-case output and statuses. The approved CI workflow already uses an external `--target` installation; an extra site-packages-only replay is not required for ordinary pure-Python acceptance. An offline VM can reuse this layout with an authenticated checkout and wheel; it cannot execute the project without the repository and its original indexed fixtures. See [portable verification](REGRESSION_DATASET.md#portable-offline-vm-target-installation). Record source and wheel outcomes separately. Current main implements bounded `python-cmd` matching 50 original CMD Q cases / 19,550 ordinates with 48 complete reporting-scalar passes and two undefined zero-flow peak-time incompletes at independently reviewed #135/#113 revisions. This is not complete CMD-native feature/site/physical scientific qualification or qualified independent `python` accuracy. A green build, parser test or installed-wheel replay does not establish native numerical validity.

Documentation changes require relative-link and factual-claim review. Numerical/parser changes require focused tests plus affected prior-stage regressions and native evidence where the contract changes. For pure-Python software checks, deterministic cached regressions and installed-wheel tests, a complete Python 3.13 or 3.14 run on **either Linux or Windows** satisfies the current development gate; neither platform needs to be repeated on the other. Record the actual OS and interpreter, and retain separate source/wheel evidence. Windows is still required when the tested behaviour depends on RORB executables, Windows path/process/GUI semantics or platform-specific packaging. This does not substitute for fresh native observation or numerical acceptance. Report every missing tool, failed check and unexpected skip; do not downgrade the target interpreter to manufacture a pass.

Planning/scaffold and S0/S1 code have merged after recorded Windows quality and package checks. These do not close independent S0-S7 native, hydrological or numerical acceptance gates.

## CI policy for the public repository (owner-approved 2026-11-10)

The owner explicitly authorised adding helpful CI now that this repository is public. Only `.github/workflows/quality.yml` is allowed by the repository checker. Pull requests and pushes to main run a scoped **Windows/Python 3.13** check with read-only GitHub permissions and cancellation of superseded runs. It installs the lightweight dev extras, runs the unchanged local repository hygiene, pinned Ruff lint/format checks, strict Pyright and all non-native/non-benchmark pytest cases, builds a wheel, and imports that installed wheel from outside the checkout.

Do not execute RORB_CMD/RORBwin, use client fixtures, access private executables, run expensive benchmarks or publish packages on hosted runners. CI validates *software quality*, not native numerical equivalence or Windows permission-cleared reference execution. Native and historical acceptance must be recorded separately on an actual reference machine.

The existing workflow intentionally has one Windows lane and no release/dependency-update job; it is **not** a requirement to duplicate an otherwise complete Linux/Python 3.13 or 3.14 pure-Python validation. Cache pip dependencies and cancel stale PR runs to limit costs. Keep the workflow explicitly reviewed, without unapproved matrix expansion, automatic publication or runtime secrets. A CI green result does not close S0-S7.

## Git and data safety

Topic branches and reviewable PRs; never merge or publish without owner instruction. Preserve concurrent/unrelated work and re-read the target head before publishing a batch. Do not force-push. Keep versions unchanged unless a version change is selected; bootstrap version is 0.0.0.dev0.

Ignore generated directories rather than all .out/.dat/.csv files: these extensions can be legitimate regression inputs. Original approved RORB fixtures under tests/fixtures/rorb are byte-preserved. The hygiene checker enforces no reference executables/manual PDFs/wheels, private local folders, generated results or files over the 1 MB bootstrap review threshold. This is a guard, not a comprehensive secret scanner or a substitute for provenance review.

Use no-clobber defaults; no silent destructive cleans or baseline regeneration. Preserve Windows path spelling and resolve paths relative to their owning configuration. Kernels have no filesystem side effects or process-level logging setup.

## Work tracking and completion

[docs/work/README.md](work/README.md) indexes useful evidence. Current state belongs in STATUS/BACKLOG and the selected GitHub issue; completed prose handoffs may be retired to Git history after replacement/link checks. Preserve unique hashes, source observations, frozen policies and independent numerical results. Keep at most one working record per active work front; stage issues hold detailed task scope. Record status, owner (Unassigned unless accepted), update/review date, branch/revision, exact validation, blockers and one concrete next action. Do not imply an agent is running in the background. Review dates are session-driven, not scheduled tasks.

Distinguish implemented, validated, committed, pushed, reviewed, merged and released. Link limitations rather than closing them implicitly. The selected licence and notices are recorded in the repository LICENSE and package metadata. Release/publication remains a separate owner decision; do not reopen the accepted reader reuse or dependency decision.
