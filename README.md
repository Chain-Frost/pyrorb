# PyRORB

**PyRORB** is an **in-development** Python package for selected RORB rainfall–runoff procedures, including canonical dependency-light RORB report readers maintained in PyRORB. Normal Python runs and the public regression suite require **no private repository and no native RORB executable**. This is not a certified full CMD replacement or a scientifically accepted hydrologic product. A preliminary package is published; final MVP release acceptance remains open.

The repository and distribution use `pyrorb`; the Python import namespace remains `runoff_routing`. Use the public checkout instructions below for development; the preliminary package is also published. The [naming and compatibility policy](docs/NAMING.md) distinguishes current branding from stable file-format and provenance identifiers.

## Install and execute a supplied storm

Python **3.11, 3.12, 3.13 or 3.14** (3.14 preferred for development), on **Linux or Windows**, is supported for pure-Python development. From a checkout of [Chain-Frost/pyrorb](https://github.com/Chain-Frost/pyrorb):

```sh
python -m pip install -r requirements-catg.txt -e ".[dev]"
python repo-scripts/check_local.py
```

The first command installs the package, development tools and the optional PR-pinned PyRomb writer. To install only the core checkout, use `python -m pip install -e .`; edited CATG export requires the separately installed writer. See [CATG authoring](docs/RORB_GE_AUTHORING.md). the second runs repository, Ruff, strict Pyright and non-native test checks. A virtual environment is optional. For an existing explicit S1 run document, run the checked-in synthetic example:

```python
from pathlib import Path
from runoff_routing.integration import read_run_json, run_model

model = read_run_json(Path("examples/synthetic-run.json").read_text(encoding="utf-8"))
result = run_model(model)
print(result.to_csv())
```

This executes the supported direct S2 engineering API. Schema-based project and CLI execution uses the temporary `python-cmd` default described below. The example is a software smoke check, not unrestricted native/engineering-accuracy acceptance. See the [quickstart](docs/QUICKSTART.md) for projects, explicit engine selection, batches, installed wheels and reproducible offline regression.

## Three selectable product engines

| Engine ID | Role | Current main availability |
| --- | --- | --- |
| `python-cmd` | **Temporary project/CLI default**, CMD 6.44 compatible arithmetic | Bounded computation and original-source regression; full feature/physical qualification remains under #5. |
| `python` | Explicit independent engineering implementation; **intended long-term default** | Supported event/batch method, including merged #110/#125 mode-2 and code-2/impervious counterparts; broader accuracy remains separately qualified. |
| `rorb-cmd` | Explicit optional user-installed native CMD adapter | Verified local executable/configuration and supported inputs; no bundled binary or engine fallback. |

Projects preserve the engine/profile separately from rainfall source and method. Historical engine-less schema-1 projects retain `python`; explicitly stored choices never migrate silently. See the [engine contract](docs/ENGINES.md) and [current status](docs/STATUS.md) for supported subsets and acceptance limits.

## Development priority

The CLI/text-file MVP #119, deterministic rainfall preparation #136/#175, reporting #155 and the import/edit/export/reader programme #138–#143 are **delivered on main**. Current work includes the owner-approved **provisional** Monte Carlo CLI/API/text implementation from [PR #151](https://github.com/Chain-Frost/pyrorb/pull/151). Its reproducible sampling, routed-event and weighted-frequency software is available on main, but RORBwin statistical equivalence, full probability support and design-flood engineering accuracy are **not qualified**. See [method and limitations](docs/MONTE_CARLO.md). [Current status](docs/STATUS.md) and [the backlog](docs/BACKLOG.md) identify remaining work. Advanced #114–#118 and saved RORBwin PAR #144 remain deferred. Deliverables are CLI, Python API and text files; no graphical-interface implementation, design or planning is included.

## Regression and outstanding acceptance

The [self-contained public regression guide](docs/REGRESSION_DATASET.md) uses one maintained register and comparator. Current bounded original-CMD evidence is **50/50 printed Q cases / 19,550 ordinates**, **48 reporting-scalar passes and two undefined all-zero peak-time incompletes**. The former 14 source exclusions were admitted by #132; 36-case results are historical. Original native gaps, authored controls and unresolved feature/site/physical qualifications remain explicit. `--snapshot` compares historical candidate outputs and does not execute the installed engine. Exact source/wheel receipts are linked from [current status](docs/STATUS.md).

The [engineering method and CMD deviation policy](docs/ENGINEERING_METHOD.md), [batch contract](docs/ENGINEERING_BATCHES.md), [single CMD feature matrix](docs/CMD_FEATURE_MATRIX.md) and open [CMD gate #5](https://github.com/Chain-Frost/pyrorb/issues/5) distinguish delivered software from scientific acceptance. Monte Carlo's independently verified software subset is admitted **provisionally**, while [#9](https://github.com/Chain-Frost/pyrorb/issues/9) remains open for native/source/statistical/physical-catchment qualification. [preliminary v26.11.24.1](https://github.com/Chain-Frost/pyrorb/releases/tag/v26.11.24.1) is published; final MVP release remains separately gated under #10/#213. Canonical reader transfer #233 and downstream compatibility migration [ryan-tools #340](https://github.com/Chain-Frost/ryan-tools/issues/340) are complete; [#231](https://github.com/Chain-Frost/pyrorb/issues/231) is closed.

## Documentation and source custody

- [Quickstart and commands](docs/QUICKSTART.md) · [documentation index](docs/README.md) · [development guide](docs/DEVELOPMENT.md) · [source register](docs/SOURCES.md) · [regression policy](docs/REGRESSION.md).
- Preserve authentic native inputs, original source identities/hashes, exact raw clocks, full horizons and frozen metrics. Approved, path-sanitised public data are versioned test evidence; original and transformed bytes are not interchangeable.
- The private investigations repository is for agent research only. No executable, manual, restricted capture, client data or private installation path is distributed. The optional RORBwin loss profile is experimental and not the default method. This project is not endorsed by RORB's authors or custodians.

Python compatibility: [24 November 2026 migration receipt](docs/work/2026-11-24-python311-compatibility.md).
