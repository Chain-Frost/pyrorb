# Command-line, versioned JSON and explicit-event MVP (#119)

This is the **current bounded implementation**, not full CMD replacement,
native numerical acceptance, Monte Carlo or an additional JSON project schema.
The [schema-2 project contract](PROJECT_JSON.md), [engine contract](ENGINES.md),
[default batch method](ENGINEERING_BATCHES.md) and [original regression policy](REGRESSION_DATASET.md)
remain authoritative for their respective scopes. Parent: #7; roadmap: #1.

## Named supported common model

The initial public example is `examples/synthetic-run.json`: one subarea,
one natural reach and one final code-7 print, one DESIGN pluviograph, one ISA
and one burst, pervious IL/CL (loss model 1), lumped kc, explicit temporal
pattern and depths, fixed computational control order and full N+1 model-elapsed
samples. It is an **authored software control**, not native calibration data.
For `python-cmd/cmd-6.44`, this is the intended reproducible MVP reference
engine. `python/engineering-v1` remains the default, is separately computed,
and must never masquerade as a CMD-compatible result.

The public original-input acceptance population includes existing maintained
register IDs `review-design-baseline`, `review-ensemble-tp1`,
`timestep-design-baseline-f2`, `timestep-ensemble-tp3-f4` and
`zero-loss-ensemble-tp9-f1` (**1,805 original printed ordinates**). The previously retained public source/wheel
CMD probe records these as among 36 printed-Q/scalar-supported cases; its
comparison policy and exact original output files are **not** reimplemented
here. New batch tests use those identities and original .par/.catg/.stm
bytes through the existing import/decoder. These are bounded supported inputs
only, not a statement that all 50 original eligible CMD cases or the
upstream PyRomb PR16 exporter are now admitted. PyRomb
`pyromb-pr2-full` / `pyromb-novel-storm` and more recent exporter
features remain under #96 until a separately reviewed source revision passes.

Current CMD compatibility is limited to the engine's supported one-ISA,
one-burst, one-pluviograph DESIGN, lumped kc, IL/CL, supported ordinary
control codes and characterised print path. Additional code-7 sites remain
subject to concurrent #91/PR #113; the generic batch report preserves every
ordered site returned by an engine and never assumes a single site.
Other parser, loss and feature additions remain under #90–#96. External
unprepared rainfall/curves, unsupported routing/storage/control families,
other CMD profiles and generated ARR events are explicit non-success outcomes.

## Workflow

The normal `project_json` CLI already supports `import-rorb`,
`validate`, `inspect` and the existing single-project `run`.
The new `project_batch` entry point supports *one project event by default*
or a versioned request containing ordered event variants.

From the public repository, with this package installed:

```sh
python -m runoff_routing.project_json import-rorb case-one legacy-rorb model.par model.catg design.stm project.json
python -m runoff_routing.project_json validate project.json
python -m runoff_routing.project_batch project.json run-one --engine python-cmd
python -m runoff_routing.project_batch project.json run-many --events examples/mvp-events.json --engine python-cmd
```

For the fully reproducible authored example without external original files:

```sh
python examples/create_cmd_project.py
python -m runoff_routing.project_json validate cmd-example-project.json
python -m runoff_routing.project_batch cmd-example-project.json mvp-results --events examples/mvp-events.json
python -m runoff_routing.project_batch cmd-example-project.json mvp-failed --events examples/mvp-events-with-failure.json
```

The last command **deliberately exits 2** while writing a report containing
all three outcomes (one explicit unsupported source-order request). The
successful command exits 0. Use a *new* output prefix on every rerun;
`mvp-results.json`, `mvp-results.csv` and `mvp-results.txt` are exclusively
created, never overwritten. A failure in whole-request syntax, source
validation, engine selection or existing destination exits 2 without
substituting another engine. `--numerical-profile` requires `--engine`.
A local native attempt additionally requires `--engine rorb-cmd` and
`--native-config`. In-memory storm/loss overrides explicitly reject
on `rorb-cmd`: its verified executable must use unchanged original
source files, not an unrepresentable Python-side event.

### Installed wheel (Python 3.13/3.14, Linux or Windows)

Build once in the public checkout, then install the built wheel into a fresh
environment outside the checkout; execute with that interpreter:

```sh
python -m build --wheel
python -m venv /tmp/runoff-mvp-wheel
/tmp/runoff-mvp-wheel/bin/python -m pip install dist/python_runoff_routing-0.0.0.dev0-py3-none-any.whl
/tmp/runoff-mvp-wheel/bin/python examples/create_cmd_project.py
/tmp/runoff-mvp-wheel/bin/python -m runoff_routing.project_batch cmd-example-project.json wheel-mvp --events examples/mvp-events.json --engine python-cmd --wheel-artifact dist/python_runoff_routing-0.0.0.dev0-py3-none-any.whl
```

On Windows use `py -3.13 -m venv <new-folder>` and
`<new-folder>\\Scripts\\python.exe` instead of the Unix executable
path. Build and inspect the real artifact filename; the wheel flag is
optional but, when used, must match installed source bytes. The existing
single-platform pure-Python verification policy applies. No native binary
is included or required for either Python engine.

## JSON event request contract

A *request file*, separate from the versioned project, has exactly:

```json
{
  "format": "python-runoff-routing-explicit-events",
  "schema_version": 1,
  "events": [
    {"event_id": "original"},
    {"event_id": "variant", "storm": {"depths_mm": ["25.0"]}},
    {"event_id": "another", "losses": {"initial_loss_mm": "5", "continuing": "0.2"}}
  ]
}
```

Storm keys are a strict subset of the existing S1 `StormModel` schema:
`title`, `timestep_hours`, `calculation_increments`,
`start_increment`, `percentages` and `depths_mm`. Unspecified keys
inherit the project storm exactly. Decimals remain strings; counts are JSON
integers. Ordered `subarea_ids`, ISA, burst count and pluviograph count
cannot be overridden. Loss overrides accept only S1
`initial_loss_mm` and `continuing` for the one-ISA case.
A `routing` override may specify `kc` and `m` for the supported single
lumped routing group; this is re-prepared as a **new invariant parameter
combination**, never reused with a different set of route coefficients.
The `continuing` loss
is **mm/hour** in this IL/CL subset. Imported original catchment and
parameters otherwise remain immutable. Each event's effective model is
constructed through the maintained S1 model and validation and is
never written to a temporary project file.

### In-memory preparation lifecycle

The verified project/immutable typed CATG, PAR and STM is resolved once per
batch, not re-read per event. Both Python engines now reuse their existing
**immutable** prepared routing geometry and coefficient structures, keyed
strictly by typed catchment computational order/areas and routing parameters
(including kc/m). Different routing parameters produce independent prepared
entries. Neither engine caches per-event rainfall, loss memory, reach storage,
branch stacks, routing iteration state or Q. No global/path-based cache is
retained between independent runs, so modifying a source file requires loading
and hash-validating a new project; corrupt original bytes are never bypassed.
Unprepared single-event execution uses the same kernels and is an independent
bitwise-value equality control. This is not a new numerical engine.

Original CMD source reference case IDs `review-design-baseline`,
`review-ensemble-tp1`, `timestep-design-baseline-f2`,
`timestep-ensemble-tp3-f4`, `zero-loss-ensemble-tp9-f1` are tested
through the **batch API and complete CSV/JSON/text reporting**, not merely
through the pre-existing numerical probe. The required four-event sequence
contains baseline, TP1 with separately resolved storm/kc, a negative
`mvp-invalid-control` with no fabricated Q, and an equivalent baseline
under a *different* ID. `mvp-unsupported-storage` remains an explicitly
rejected event. Independent authored controls retain analytical, not
authenticated native, reference status.


Event IDs are ASCII, unique within the request and retain request order.
Malformed event entries, malformed IDs (given an ordinal placeholder),
duplicate IDs, unsupported features and individual numerical failures
each generate a typed outcome; the next event continues independently.
Malformed *top-level* JSON, duplicate JSON keys, unsupported request
version, missing input project and invalid selection reject the request.
An empty batch is invalid.

## Results and time/volume conventions

The ordered public API is `iter_project_events(project, events, ...)`.
`run_project_events(...)` collects a `ProjectBatchReport` with full
`EngineOutcome` records, counts and `.to_json()`, `.to_csv()`,
`.to_text()`. Event records preserve the original project SHA-256 and
source-file hashes, effective S1 model SHA-256, stored/effective engine,
selected arithmetic profile, rainfall profile, control and print order,
effective timestep, horizon and type-specific failure code. Each computed
site contributes all N+1 ordinate rows and ordered native tokens if present.
A failed event contributes one CSV row with no fabricated hydrograph.

CSV uses `physical_time_hours` exactly as supplied by the selected
engine: the Python engines use elapsed-from-zero; native CMD preserves
its separately validated printed time and raw one-based clock tokens.
Physical trapezoidal volume in m3 is derived only from a complete
monotone physical time axis and discharge series. The separate
`native_inclusive_reported_volume_m3` field remains **null/blank** unless
an independently supplied native-inclusive report quantity becomes
available; it is never estimated from trapezoidal integration.
An eligible calculation still carries `computed_unvalidated` and
`native_parity_status=not_assessed`. Reports preserve all non-success
statuses and return nonzero overall exit on any non-success event.

## Scope exclusions

No GUI work or planning, TOML, new numerical kernel, alternative regression
runner, private repository requirement, optimisation campaign or Monte Carlo.
Advanced #114–#118, optional #63, residual #103 and Monte Carlo #9
are **not** MVP gates. Full CMD gate #5 remains open for its broader
original-input and numerical/scientific claims.
