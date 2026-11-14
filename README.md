# Python runoff routing

An **in-development**, standard-library-runtime Python package for selected RORB rainfall–runoff procedures. Normal Python runs and the public regression suite require **no private repository and no native RORB executable**. This is not a certified full CMD replacement or a released hydrologic product.

## Install and execute a supplied storm

Python **3.13 or 3.14**, on **Linux or Windows**, is supported for pure-Python development. From a public checkout:

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

This executes the default Python calculation; it is a **software smoke example, not a native or engineering-accuracy acceptance test**. See the [quickstart](docs/QUICKSTART.md) for JSON projects, engine selection, local native execution, batches, installed wheels and reproducible offline regression.

## Three selectable product engines

| Engine ID | Role | Current `main` availability |
| --- | --- | --- |
| `python` | **Default** maintained improved engineering implementation | Bounded explicit DESIGN single-event execution; independent engineering acceptance remains open under [#6](https://github.com/Chain-Frost/python-runoff-routing/issues/6) |
| `python-cmd` | Explicit CMD 6.44 numerical-compatibility implementation | Not yet on `main`: public [draft PR #79](https://github.com/Chain-Frost/python-runoff-routing/pull/79) / [#75](https://github.com/Chain-Frost/python-runoff-routing/issues/75) is separately being validated; requesting it on `main` returns an unavailable status |
| `rorb-cmd` | Explicit, optional user-installed native CMD adapter | Available with a verified local executable/config and supported original inputs; no fallback or bundled binary |

Project schema 2 records the engine/profile separately from rainfall source and method. Schema-1 projects without a selector migrate to `python`. Use the [engine contract](docs/ENGINES.md) for supported subsets, explicit failure/report semantics and source/wheel identity. Do not interpret successful dispatch, a native executable run or a cached snapshot as proof of full CMD equivalence.

## Regression and outstanding acceptance

The [self-contained public regression guide](docs/REGRESSION_DATASET.md) uses the **one maintained register and CLI** in `runoff_routing.regression_dataset`. Authenticated CMD originals, 50 cached case comparisons, ten independent mathematical controls and 21 individually recorded native gaps are available without the private workspace. The `--snapshot` mode compares historical **unvalidated candidate output**; it does **not** execute the currently installed engine. The two zero-flow peak times remain incomplete. Fresh engine computation and independent accuracy checks must be reported separately.

The current [backlog and owners](docs/BACKLOG.md), [roadmap #1](https://github.com/Chain-Frost/python-runoff-routing/issues/1) and [capability status](docs/STATUS.md) distinguish completed source work from open numerical/full-feature gates. The [single CMD feature inventory](docs/CMD_FEATURE_MATRIX.md) is now merged via [PR #84](https://github.com/Chain-Frost/python-runoff-routing/pull/84), but the actual [CMD completion gate #5](https://github.com/Chain-Frost/python-runoff-routing/issues/5) remains open. CMD completion precedes expansion of RORBwin-specific features. Monte Carlo, release automation and publication remain deferred.

## Documentation and source custody

- [Quickstart and commands](docs/QUICKSTART.md) · [documentation index](docs/README.md) · [development guide](docs/DEVELOPMENT.md) · [source register](docs/SOURCES.md) · [regression policy](docs/REGRESSION.md).
- Preserve authentic native inputs, original source identities/hashes, exact raw clocks, full horizons and frozen metrics. Approved, path-sanitised public data are versioned test evidence; original and transformed bytes are not interchangeable.
- The private investigations repository is for agent research only. No executable, manual, restricted capture, client data or private installation path is distributed. The optional RORBwin loss profile is experimental and not the default method. This project is not endorsed by RORB's authors or custodians.
