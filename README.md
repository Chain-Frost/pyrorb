# PyRORB

**PyRORB** is an **in-development** Python package for selected RORB rainfall–runoff procedures, with a canonical report-reader dependency maintained in ryan-tools. Normal Python runs and the public regression suite require **no private repository and no native RORB executable**. This is not a certified full CMD replacement or a released hydrologic product.

The repository and distribution use `pyrorb`; the Python import namespace remains `runoff_routing`. Install from the public checkout below while PyPI publication is deferred. The [naming and compatibility policy](docs/NAMING.md) distinguishes current branding from stable file-format and provenance identifiers.

## Install and execute a supplied storm

Python **3.13 or 3.14**, on **Linux or Windows**, is supported for pure-Python development. From a checkout of [Chain-Frost/pyrorb](https://github.com/Chain-Frost/pyrorb):

```sh
python -m pip install -e ".[dev]"
python repo-scripts/check_local.py
```

The first command installs the package and development tools; the second runs repository, Ruff, strict Pyright and non-native test checks. A virtual environment is optional. For an existing explicit S1 run document, run the checked-in synthetic example:

```python
from pathlib import Path
from runoff_routing.integration import read_run_json, run_model

model = read_run_json(Path("examples/synthetic-run.json").read_text(encoding="utf-8"))
result = run_model(model)
print(result.to_csv())
```

This executes a supported default-engine single storm. It is a **software smoke example, not unrestricted native/engineering-accuracy acceptance**. The same default engine also has [immutable prepared explicit-event batches](docs/ENGINEERING_BATCHES.md), with separate numerical and performance limits. See the [quickstart](docs/QUICKSTART.md) for JSON projects, engine selection, local native execution, batches, installed wheels and reproducible offline regression.

## Three selectable product engines

| Engine ID | Role | Current `main` availability |
| --- | --- | --- |
| `python` | **Default** maintained improved engineering implementation | Accepted bounded explicit DESIGN method and batches through closed [#6](https://github.com/Chain-Frost/pyrorb/issues/6); deferred volume/continuity [#103](https://github.com/Chain-Frost/pyrorb/issues/103), full features [#5](https://github.com/Chain-Frost/pyrorb/issues/5) |
| `python-cmd` | Explicit CMD 6.44 numerical-compatibility implementation | **Integrated bounded computation** via [merged PR #79](https://github.com/Chain-Frost/pyrorb/pull/79). Independent fresh source/isolated-wheel 36-case printed/scalar checks are delivered by [merged #100](https://github.com/Chain-Frost/pyrorb/pull/100). Bounded #75 port is complete; complete CMD feature and physical acceptance stays open under [#5](https://github.com/Chain-Frost/pyrorb/issues/5) |
| `rorb-cmd` | Explicit, optional user-installed native CMD adapter | Available with a verified local executable/config and supported original inputs; no fallback or bundled binary |

Project schema 2 records the engine/profile separately from rainfall source and method. Schema-1 projects without a selector migrate to `python`. Use the [engine contract](docs/ENGINES.md) for supported subsets, explicit failure/report semantics and source/wheel identity. Do not interpret successful dispatch, a native executable run or a cached snapshot as proof of full CMD equivalence.

## Development priority

The next delivery target is the explicitly supported **CLI/text-file MVP** in [#119](https://github.com/Chain-Frost/pyrorb/issues/119), with bounded JSON projects, explicit event/batch execution and full CSV/JSON/text outcomes. Advanced feature children [#114–#118](https://github.com/Chain-Frost/pyrorb/issues/114) are deferred until after that MVP; ordinary PyRomb code-2/per-source impervious source admission #96 and already selected feature work remain active. [Full CMD replacement #5](https://github.com/Chain-Frost/pyrorb/issues/5) is a separate, later claim and does not block the selected MVP. **There is no graphical-interface deliverable or GUI design work in this programme stage.**

## Regression and outstanding acceptance

The [self-contained public regression guide](docs/REGRESSION_DATASET.md) uses the **one maintained register and CLI** in `runoff_routing.regression_dataset`. Authenticated CMD originals, 50 cached case comparisons, ten independent mathematical controls and 21 individually recorded native gaps are available without the private workspace. The `--snapshot` mode compares historical **unvalidated candidate output**; it does **not** execute the currently installed engine. The two zero-flow peak times remain incomplete. Separately, merged [#79](https://github.com/Chain-Frost/pyrorb/pull/79) and independently checked [#100](https://github.com/Chain-Frost/pyrorb/pull/100) establish **36 original CMD cases / 16,836 original full printed ordinates**, with **14 explicit original source exclusions**. The 36 admitted fresh source and installed-wheel cases passed Q, peak, uniquely defined peak time and native inclusive reported-volume comparisons; the 14 are not silently treated as computed. This is **bounded** evidence, not full CMD/native hidden-state/physical equivalence or general default-engine acceptance. See the [single CMD feature matrix](docs/CMD_FEATURE_MATRIX.md).

The [default-engine method and CMD deviation policy](docs/ENGINEERING_METHOD.md), [explicit batch contract](docs/ENGINEERING_BATCHES.md) and current [backlog and owners](docs/BACKLOG.md), [roadmap #1](https://github.com/Chain-Frost/pyrorb/issues/1) and [capability status](docs/STATUS.md) distinguish completed source work from open numerical/full-feature gates. The [single CMD feature inventory](docs/CMD_FEATURE_MATRIX.md) is now merged via [PR #84](https://github.com/Chain-Frost/pyrorb/pull/84), but the actual [CMD completion gate #5](https://github.com/Chain-Frost/pyrorb/issues/5) remains open. CMD completion precedes expansion of RORBwin-specific features. Monte Carlo, release automation and publication remain deferred.

## Documentation and source custody

- [Quickstart and commands](docs/QUICKSTART.md) · [documentation index](docs/README.md) · [development guide](docs/DEVELOPMENT.md) · [source register](docs/SOURCES.md) · [regression policy](docs/REGRESSION.md).
- Preserve authentic native inputs, original source identities/hashes, exact raw clocks, full horizons and frozen metrics. Approved, path-sanitised public data are versioned test evidence; original and transformed bytes are not interchangeable.
- The private investigations repository is for agent research only. No executable, manual, restricted capture, client data or private installation path is distributed. The optional RORBwin loss profile is experimental and not the default method. This project is not endorsed by RORB's authors or custodians.
