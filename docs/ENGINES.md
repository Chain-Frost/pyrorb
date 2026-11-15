# Three product computation engines (issue #74)

The engine selector is **not** a native-parity acceptance result. The shipped package
declares exactly three stable IDs; no private checkout or native program is imported
or launched for normal Python use, inspection, installation or CI.

| Engine | Selection | Availability / numerical qualification | Supported inputs | Outputs |
| --- | --- | --- | --- | --- |
| `python` | Explicit for now; intended future default; `engineering-v1` | Accepted bounded method and explicit-event batches (#6 closed, #97/#99/#101/#102); deferred residual #103, not full scientific qualification | Embedded or original file-backed S1 model, explicit DESIGN storm, supported one-ISA/pervious domain | Full ordered discharge, model-elapsed physical hours (starting 0), available Python numerical diagnostics |
| `python-cmd` | **Temporary default**; `cmd-6.44` | Merged #132/#135/#108/#111/#113/#120; latest reviewed source/installed-wheel original 50 Q / 19,550 ordinates, 48 scalar pass/two undefined zero-time incomplete; full feature/site/physical #5 open | Supported admitted original DESIGN including historical graphical code-2/FI, bounded mode-2 and ordered ordinary code-7 | Complete source/site/clock Q outcomes for qualified profiles, not universal CMD/physical equivalence |
| `rorb-cmd` | Explicit; `cmd-6.44` | User-installed executable; conditional native capture, not scientific approval | Original hash-verified `.par/.catg/.stm` project, DESIGN one ISA/burst/pluviograph, lumped kc, IL/CL | Complete validated native HydNNN discharges, exact raw native clocks/tokens and executable evidence; internal states unavailable |

The bounded [#119 CLI/text-file MVP](https://github.com/Chain-Frost/python-runoff-routing/issues/119) was **delivered by merged #128** with five original seeds / 1,805 printed ordinates and full selected-engine JSON/CSV/text event/batch output; deterministic #136 ARR software uses the same runner. Original upstream PR16 producer, code-11/physical sites, default-engine scientific and generated-storm native claims remain separately open, not hidden by delivered software. Advanced #114–#118 are post-MVP; #96 is the current ordinary PyRomb target. No GUI or general native investigation is in scope.

## JSON schema and selection

Project **schema 2** adds a required top-level field independent of
`rainfall_profile`:

```json
"engine": {"id": "python-cmd", "numerical_profile": "cmd-6.44"}
```

Newly constructed schema-2 projects temporarily default to `python-cmd/cmd-6.44`.
Schema-1 files without an engine preserve their historical implicit
`python/engineering-v1` choice; migration does **not** silently change
computation. The intended long-term default remains the improved `python` engine.
The next serialisation writes schema 2. An unknown engine, profile or field fails closed.
A project does not store an executable path.

`run_engine_project(path)` honours the stored selection. Explicit
`selection=EngineSelection.for_engine("...")` is the **effective API override**,
even if it differs from storage. The original and effective selections, source
of the override, event/project identity, model hash, original source hashes,
effective settings, requested print-site IDs and control order are included in
success **and failure** reports. Overrides are never silently accepted as if
the stored project had changed. The legacy `project_execution.run_project`
is intentionally Python-only and rejects non-Python stored selections.

```python
from pathlib import Path

from runoff_routing.engine_execution import run_engine_project
from runoff_routing.engine_types import CAPABILITIES, EngineSelection

project_path = Path("project.json")
result = run_engine_project(project_path)  # stored engine, as recorded in this project
other = run_engine_project(
    project_path,
    selection=EngineSelection.for_engine("python", "engineering-v1"),
)
assert other.status == "computed_unvalidated"  # computation only; public native parity unassessed
print(result.to_json(), [item.engine for item in CAPABILITIES])
```

## Reproducible command-line project example

From the public checkout, create a complete schema-2 project using the existing
S1 input model and the safe, exclusive-create project writer:

```powershell
py -3.14 examples/create_cmd_project.py
py -3.14 -m runoff_routing.project_json run cmd-example-project.json cmd-example-result.json
```

The generated project explicitly stores `python-cmd/cmd-6.44`. Both the selected
model and printed output site are visible in its JSON. Running the CLI a second
time with the same destination fails without modifying the existing result.
For a comparison, run with an **explicit** `--engine python` override into
a different new output file, or with `--engine rorb-cmd --native-config ...`
for an independently verified local native executable and original file-backed
model. These commands do not claim native equivalence.

```python
from pathlib import Path
from runoff_routing.engine_execution import run_engine_project
from runoff_routing.engine_types import EngineSelection

project = Path("cmd-example-project.json")
cmd = run_engine_project(project)
assert cmd.effective_selection == EngineSelection.for_engine("python-cmd")
assert cmd.status == "computed_unvalidated"
assert cmd.native_parity_status == "not_assessed"
assert len(cmd.hydrographs[0].discharge_m3_s) == 6
```

## CLI

```powershell
py -3.14 -m runoff_routing.project_json run project.json cmd-result.json
py -3.14 -m runoff_routing.project_json run project.json python-result.json --engine python --numerical-profile engineering-v1
py -3.14 -m runoff_routing.project_json run project.json native-result.json --engine rorb-cmd --numerical-profile cmd-6.44 --native-config local-cmd.json
py -3.14 -m runoff_routing.project_json run --help
```

Specifying `--engine` overrides the project choice; `--numerical-profile`
requires `--engine` and neither can quietly change the other. Missing native
config or unsupported CMD profiles/features produce explicit failures, not
Python fallback. Exit code is 0 for a completed (still **unvalidated**)
calculation, 2 for a reported failure or invalid usage/input. Reports use
exclusive-create file writing and never overwrite an earlier run.

## Exact implementation and installed-wheel identity

The package version is not a source revision. Every `EngineOutcome` records
`implementation_revision` as a **versioned SHA-256 fingerprint of the installed
Python package source bytes** (`package-code-v1-sha256:<digest>`). The
`package_version` field is separate. This works from a checkout or an installed
wheel, without Git, private data or a native executable. It identifies the
package's Python source files, **not** the Git commit, input dataset or compiled
third-party libraries. Keep the actual Git commit in the accompanying validation
receipt.

For a stronger installed-wheel attribution, supply the exact wheel file in the
API or CLI. The adapter reads the artifact and verifies that every
`runoff_routing` source file in the wheel matches the installed package
**byte-for-byte**, rejecting added, missing or duplicate package files. Only
then does it populate `verified_wheel_sha256`; otherwise it remains `null`.
An incorrect or missing artifact returns `invalid_input / wheel_identity`
**before any computation or native CMD launch**. The wheel is never installed
by this operation and cannot be silently assumed from a package version.

```python
from pathlib import Path
from runoff_routing.engine_execution import run_engine_project

outcome = run_engine_project(
    Path("project.json"),
    wheel_artifact=Path("dist/python_runoff_routing-0.0.0.dev0-py3-none-any.whl"),
)
print(outcome.implementation_revision, outcome.verified_wheel_sha256)
```

Equivalent CLI:

```powershell
py -3.14 -m runoff_routing.project_json run project.json result.json --wheel-artifact dist/python_runoff_routing-0.0.0.dev0-py3-none-any.whl
```

The installed-wheel quality workflow exercises this path with the actual built
artifact and prints its SHA-256. Source-code and wheel content identity is
distinct from numerical acceptance and physical output-site mapping.

## Optional local CMD configuration

`local-cmd.json` is operator-supplied, machine-specific and **not** included in
a committed project. The two paths below are *examples relative to this local
configuration*, not an installed executable claim. Replace the hash with the
observed SHA-256 of the installed RORB CMD binary, and independently verify its
observed banner/version. The mapping of HydNNN column identities must be
established by the operator; labels alone are insufficient.

```json
{
  "schema_version": 1,
  "executable": "RORB_CMD.exe",
  "executable_sha256": "REPLACE_WITH_VERIFIED_LOWERCASE_64_HEX_SHA256",
  "observed_version": "6.44",
  "observed_banner": "REPLACE_WITH_INDEPENDENTLY_OBSERVED_BANNER",
  "numerical_profile": "cmd-6.44",
  "output_root": ".local/native-runs",
  "print_columns": {"print_1": "Hyd001"},
  "timeout_seconds": 180
}
```

Only the *characterised* `cmd-6.44` adapter boundary is enabled. The
`print_columns` map must cover every ordered S1 print ID exactly once. It is
**caller-asserted**, not an automatic proof of physical site equivalence.
Wrong profile, incorrect SHA-256, unprocessed ARR assets, unsupported
multi-ISA/loss/storm configurations and incomplete print mappings fail before
launch. Native files are neither bundled nor downloaded.

The adapter reuses the S0 fingerprinting, isolated staged-copy run directory,
generated CMD parameter writer, no-clobber capture, binary stdout/stderr,
timeout, source mutation checks and manifest inventory. It verifies S0
records again, reconciles effective parameters and source hashes against
the typed project, checks native diagnostic warnings/errors and requires a
*single complete* S1-inspected report with all requested columns, exact
horizon, native duration and timestep. A zero exit code without these
conditions is not a successful computation. Source `.par` is preserved,
not executed or overwritten; the staged effective `.par` is explicitly recorded.

For the observed CMD 6.44 clock convention, raw increments are 1..N+1
and the first native printed time is at one step, not the Python engine's
model-elapsed zero. The adapter preserves the original native increment,
time and discharge strings; the separately reported native physical-hour
axis is the *validated printed native time* without shifting or aligning it to
Python by assumption. Numerical comparison and scientific approval remain
separate. Native storage, loss internals and routing state are not available
from the supported printed output and are explicitly marked unavailable.

## Structured status and acceptance

The common outcome statuses are `computed_unvalidated`,
`invalid_input`, `unsupported_feature`, `unavailable_engine`,
`numerical_error`, `incomplete_output`, and
`native_execution_failed`. Every failure includes a reason code and never
produces substitute hydrographs. An isolated native capture manifest is
retained on failure when S0 has already created one.

CMD Python computation is a separately isolated complete event path within its
bounded typed-input domain: binary32/53 arithmetic, loss/source conversion,
ordered geometry and coefficient arithmetic, routing and distinct m=0
model/native target diagnostic views. The public typed model currently rejects
m=0, so the private dry-step qualification is not an accessible public feature.
Other unsupported cases reject without implicit fallback. The Python CMD
model-elapsed hour axis does **not** fabricate original one-based native time or
print tokens. Candidate states are computed Python values, not independently
observed native states. Exact ties/sub-print times and network conservation
are not accepted by this integration.

Contract/source tests use manufactured process stubs; ordinary tests, wheel
checks, and hosted Windows CI **do not launch RORB**. Fresh actual source and out-of-tree installed-wheel printed/scalar verification already passed through merged #100. New native CMD 6.44 observations require a separately scoped local check for a concrete unresolved feature; ordinary tests do not launch RORB.
A real CMD success does not imply Python equivalence or prove print-site mapping.

**Coordination:** bounded compatible #75/#79 and maintained regression #100 are delivered. Open CMD feature requirements are #90–#96 under #5; #103 retains deferred default physical/volume qualification after bounded #6 closure. The maintained regression owner controls case bindings, native references and frozen comparison policies. Engine code does not redefine these policies or regenerate baselines.
