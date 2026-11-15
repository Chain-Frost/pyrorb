# Quickstart — current public product

These commands apply to the public repository and need no private workspace. Python 3.13 **or** 3.14 on Linux **or** Windows is sufficient for pure-Python checks; use the interpreter's actual `python`, `py -3.13` or `py -3.14` command as appropriate. Only native RORB/Windows-specific integration needs a Windows host.

**Development priority:** [MVP #119](https://github.com/Chain-Frost/python-runoff-routing/issues/119) is **CLI/text-file only**. The exact five-case original CMD seed (1,805 printed rows), four authored safeguards and planned batch/negative tests are defined in the [single backlog](BACKLOG.md). They are acceptance requirements for the *next* combined implementation, not claims that the complete CLI/batch path already exists. Advanced #114–#118 are post-MVP; ordinary PR16 code-2/per-source impervious remains active #96. The [single CMD matrix](CMD_FEATURE_MATRIX.md) separately retains full feature evidence and unknowns. There is no GUI requirement.

## 1. Installation and quality

```sh
python -m pip install -e ".[dev]"
python repo-scripts/check_local.py
```

Normal package runtime has no third-party dependency. The local checker runs repository/link hygiene, pinned Ruff lint and formatting, strict Pyright and non-native/non-benchmark pytest. It does not launch CMD, require private data or perform a numerical acceptance campaign. [Development details](DEVELOPMENT.md).

## 2. An explicit, single-storm Python calculation

From the checkout root, run this Python code; `examples/synthetic-run.json` is a **typed S1 RunModel**, not a schema-2 project file:

```python
from pathlib import Path
from runoff_routing.integration import read_run_json, run_model

run = read_run_json(Path("examples/synthetic-run.json").read_text(encoding="utf-8"))
report = run_model(run)  # default Python reference/engineering calculation
print(report.to_csv())
```

This checks that an already-supplied supported DESIGN event can execute. It does not validate native parity, physical conservation or a general ARR storm generator.

## 3. JSON project and engine selection

The [S5 interoperability guide](S5_INTEROPERABILITY.md) and
[issue #143 acceptance record](work/2026-11-15-issue143-s5-acceptance.md)
distinguish JSON project results from relocatable native CMD packages.


For an existing supported [JSON project](PROJECT_JSON.md) (`project.json` below), use a *new* output filename:

```sh
python -m runoff_routing.project_json validate project.json
python -m runoff_routing.project_json run project.json result.json
python -m runoff_routing.project_json run project.json python-result.json --engine python --numerical-profile engineering-v1
python -m runoff_routing.project_json run project.json native-result.json --engine rorb-cmd --numerical-profile cmd-6.44 --native-config local-cmd.json
```

New schema-2 projects temporarily default to `python-cmd/cmd-6.44`; existing projects
keep their stored selection, and schema-1 projects preserve their historical
`python/engineering-v1` selection. The improved `python` engine is available
by explicit override and remains the intended future default. The merged bounded [CMD-compatible engine #79](https://github.com/Chain-Frost/python-runoff-routing/pull/79) computes supported DESIGN events separately and returns `computed_unvalidated`, **not** native equivalence. Unsupported features fail closed. To create and execute a complete publicly reproducible CMD example:

```sh
python examples/create_cmd_project.py
python -m runoff_routing.project_json run cmd-example-project.json cmd-example-result.json
```

Use new result names; exclusive-create refuses overwrites. For **PAR-led import**, file overrides, source preservation, editable settings and relocation, see [PAR project workflow](PAR_PROJECTS.md). Native `rorb-cmd` still requires a separately installed hash-checked executable and original file-backed inputs. See [engine selection](ENGINES.md), [project import](PROJECT_JSON.md) and [single CMD feature matrix](CMD_FEATURE_MATRIX.md).

## 4. Explicit-event batches

The independent `python/engineering-v1` engine has a **supported bounded, non-accelerated explicit-event batch API** from [merged PR #99](https://github.com/Chain-Frost/python-runoff-routing/pull/99). Use `prepare_catchment(...)` once, then `run_explicit_batch(prepared, events)` or stream with `iter_explicit_events(...)` for bounded memory. Each `ExplicitEvent` provides a stable ID, explicit Storm and per-event Losses; outcomes independently identify computed/invalid/numerical failures without cross-event state leaks. Full examples, limitations and measured workload are in [ENGINEERING_BATCHES.md](ENGINEERING_BATCHES.md). This is **not** generated ARR rainfall, Monte Carlo or full CMD acceptance; the bounded [#6](https://github.com/Chain-Frost/python-runoff-routing/issues/6) stage is closed, [#103](https://github.com/Chain-Frost/python-runoff-routing/issues/103) retains deferred physical-volume/continuity work and [#5](https://github.com/Chain-Frost/python-runoff-routing/issues/5) retains full feature qualification.

## 5. Public cached regression and mathematical controls

The source-controlled register is `tests/fixtures/regression-v1/register.json`. Create `.local` first (ignored by Git), and use unused output names:

```sh
python -m runoff_routing.regression_dataset preflight tests/fixtures/regression-v1/register.json --set cmd-eligible --full-index --output .local/preflight.json
python -m runoff_routing.regression_dataset diagnose tests/fixtures/regression-v1/register.json --case H1-three-source-asymmetric --snapshot --output .local/one.json
python -m runoff_routing.regression_dataset compare tests/fixtures/regression-v1/register.json --set cmd-eligible --snapshot --output .local/cached.json
python -m runoff_routing.regression_dataset preflight tests/fixtures/regression-v1/register.json --set authored --engine python --output .local/analytic.json
python -m pytest tests/test_regression_dataset.py tests/test_regression_scalars.py tests/test_regression_public_native.py -q
```

The `--snapshot` path authenticates a historical candidate snapshot, *not* a fresh execution of `python` or `python-cmd`. The **all-case scalar cached comparison is intentionally non-success** because two all-zero peak times are unavailable; do not suppress its exit code or claim full success. Ordinary `--csv` submission of `computed_unvalidated` legacy output is deliberately rejected. All original hashes, clocks, horizons, status labels and frozen budgets must remain intact. Use [the maintained regression dataset contract](REGRESSION_DATASET.md) for full/subset/wheel commands and the expected status of each case.

## 6. Installed wheel and acceptance

```sh
python -m build --wheel
```

Verify the resulting wheel with an **out-of-tree installation and import** before claiming wheel behaviour; do not import from the source checkout by accident. The existing CI checks pure-Python software quality and isolated wheel use; it does not run native CMD. Report distinctly: parser/software conformance; cached reference comparison; freshly executed source and installed-wheel computation; CMD-native numerical equivalence; independent engineering accuracy/conservation/refinement; and batch performance. Do not promote one category to another. [Regression policy](REGRESSION.md).
