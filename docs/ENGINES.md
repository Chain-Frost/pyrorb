# Three product computation engines (issue #74)

The engine selector is **not** a native-parity acceptance result. The shipped package
declares exactly three stable IDs; no private checkout or native program is imported
or launched for normal Python use, inspection, installation or CI.

| Engine | Selection | Availability / numerical qualification | Supported inputs | Outputs |
| --- | --- | --- | --- | --- |
| `python` | Default; `engineering-v1` | Working S1/S2 single-event Python calculations; scientifically unaccepted pending #6 | Embedded or original file-backed S1 model, explicit DESIGN storm, supported one-ISA/pervious domain | Full ordered discharge, model-elapsed physical hours (starting 0), available Python numerical diagnostics |
| `python-cmd` | Explicit; `cmd-6.44` | **Unavailable** pending independently qualified #75 event backend | Future public CMD-compatible adapter; no compatibility arithmetic is shared from `python` | Structured `unavailable_engine` now; no fabricated values |
| `rorb-cmd` | Explicit; `cmd-6.44` | User-installed executable; conditional native capture, not scientific approval | Original hash-verified `.par/.catg/.stm` project, DESIGN one ISA/burst/pluviograph, lumped kc, IL/CL | Complete validated native HydNNN discharges, exact raw native clocks/tokens and executable evidence; internal states unavailable |

## JSON schema and selection

Project **schema 2** adds a required top-level field independent of
`rainfall_profile`:

```json
"engine": {"id": "python", "numerical_profile": "engineering-v1"}
```

Schema-1 files lacking this field still load as `python/engineering-v1`; the next
serialisation writes schema 2. An unknown engine, profile or field fails closed.
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
result = run_engine_project(project_path)  # stored engine, python for migrated projects
other = run_engine_project(
    project_path,
    selection=EngineSelection.for_engine("python-cmd", "cmd-6.44"),
)
assert other.status == "unavailable_engine"  # until issue #75 lands
print(result.to_json(), [item.engine for item in CAPABILITIES])
```

## CLI

```powershell
py -3.14 -m runoff_routing.project_json run project.json python-result.json
py -3.14 -m runoff_routing.project_json run project.json cmd-attempt.json --engine python-cmd --numerical-profile cmd-6.44
py -3.14 -m runoff_routing.project_json run project.json native-result.json --engine rorb-cmd --numerical-profile cmd-6.44 --native-config local-cmd.json
py -3.14 -m runoff_routing.project_json run --help
```

Specifying `--engine` overrides the project choice; `--numerical-profile`
requires `--engine` and neither can quietly change the other. Missing native
config and missing CMD Python backend produce explicit failure reports, not
Python fallback. Exit code is 0 for a completed (still **unvalidated**)
calculation, 2 for a reported failure or invalid usage/input. Reports use
exclusive-create file writing and never overwrite an earlier run.

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

Contract/source tests use manufactured process stubs; ordinary tests, wheel
checks, and hosted Windows CI **do not launch RORB**. An installed-wheel,
real-Windows CMD 6.44 acceptance run remains a separate opt-in local gate.
A real CMD success does not imply Python equivalence or prove print-site mapping.

**Coordination:** #75 owns the complete CMD-compatible Python event backend;
#6 owns engineering method/accuracy and batch optimisation; the offline
regression owner owns case schema, native reference choices and comparison
policies. Engine code does not redefine these policies or regenerate baselines.
