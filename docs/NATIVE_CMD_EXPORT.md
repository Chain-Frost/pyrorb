# S5 - portable native RORB CMD export (issue #141)

**Software implementation merged:** [PR #162](https://github.com/Chain-Frost/pyrorb/pull/162), 16 November 2026, squash `766b56a8ba6fe42785f05bb5d8df51a741a07e2c`. The exact-head source/installed-wheel quality and package/launcher software tests passed. **Native RORB CMD executable acceptance remains `not_run`; numerical equivalence remains `not_assessed`.**

The native export is distinct from S1 `export-run`, which writes a typed JSON model, and from S0 `capture_cmd`, which constructs its *own* PAR with verbosity 3. The native exporter stages and reparses **the exact PAR handed to a recipient**, without running Python or regenerating a different PAR at native execution time.

## Current bounded capability

- Explicit target: RORB CMD 6.44 / `cmd-6.44`, CMD V2 PAR; **not** an automatic selection of the project's Python numerical engine.
- Input: a SHA-verified project with original CMD PAR, modern graphical CATG (including previously characterised graphical `.cat` aliases) and DESIGN STM. The project must have `legacy-rorb` input profile.
- Selected events: the existing versioned explicit-event request, with the shared #119 storm, losses and routing overrides. API consumers can pass a tuple of *already-resolved* `NativeExportEvent(event_id, run)` records. Export never runs a Python or native solver.
- Parameter edits: canonical rebound CMD PAR through the existing `serialize_cmd_par`. Preserve effective kc, m, loss mode, loss values and **verbosity 1/2/3 as requested**. The original PAR is not changed.
- Unchanged imported CATG and STM: copied byte-for-byte, including encoding, line endings and metadata. Supported edited storm: use the existing STM writer, then reparse and prove the complete intended effective model. Edited CATG can be exported only through the reviewed #139 `serialize_catg_with_drawing` thin adapter, with an explicit validated projected-metre `GeDrawing` supplied as `NativeExportEvent(..., catchment_drawing=drawing)`. The adapter invokes pinned PyRomb, and the written bytes must reparse to the exact effective catchment. Without that upstream adapter, its optional dependency, or valid drawing/source semantics, export fails with an actionable diagnostic. No local CATG renderer or patch fallback is used.
- The portable package contains `events/001/model.par`, `events/001/catchment.catg` or `catchment.cat` and `events/001/storm.stm` for each event, plus `manifest.json`, `README.txt` and `run.cmd`. Every event's input paths are relative, and the native launcher changes working directory into that event folder. Distinct numbered folders prevent same-basename collisions.
- Each export checks source hashes again, validates the effective domain and reparses the *written* triplet. All event staging occurs outside the published destination; on a validation/writer failure no partial package is published. Existing destinations are rejected and never intentionally overwritten. Filesystem namespace races are not a stdlib atomic no-replace guarantee on POSIX; this is not a transactional multi-writer filesystem service.
- The manifest distinguishes source original and exported SHA-256, byte counts, byte-exact versus rewritten inputs, event IDs/order, effective settings, requested event working/output directories, verbosity, launch arguments, stored Python engine attribution and **native_execution: not_run** / **numerical_equivalence: not_assessed**. For #140's schema-3 projects it records source binding origins and declared/selected tokens without including local resolved-source machine paths.

## Text-file CLI

First import or reopen a verified RORB CMD source project with the maintained project APIs. Then:

```powershell
py -3.13 -m runoff_routing.project_json export-native "C:\models\project.json" "C:\deliveries\portable case" --target cmd-6.44
py -3.13 -m runoff_routing.project_json export-native "C:\models\project.json" "C:\deliveries\selected batch" --target cmd-6.44 --events "C:\models\events.json"

# Equivalent standalone exporter entry point:
py -3.13 -m runoff_routing.native_export "C:\models\project.json" "C:\deliveries\portable case" --target cmd-6.44
```

The second command accepts the existing `python-runoff-routing-explicit-events` schema-1 JSON request used by `project_batch`, with all event edits resolved through #138's shared `resolve_effective_model` function (including named continuing-loss input). The `export-native` command is now integrated into the shared project JSON dispatcher through merged #140, and delegates to the same exporter API; the standalone `native_export` CLI remains available. A malformed or unsupported selected event fails the whole export rather than silently omitting the event.

## Python API

```python
from pathlib import Path
from dataclasses import replace
from decimal import Decimal
from runoff_routing.native_export import NativeCmdExportTarget, NativeExportEvent, export_cmd_package
from runoff_routing.project_json import load_project

project = Path("project.json")
model = load_project(project).run
parameters = replace(model.parameters, verbosity=1)
event = NativeExportEvent("first", replace(model, parameters=parameters))
receipt = export_cmd_package(
    project,
    Path("portable-new"),
    target=NativeCmdExportTarget("cmd-6.44"),
    events=(event,),
)
print(receipt.to_json())
```

## Native execution and independent acceptance

The export package is runnable *in intent*, but source/wheel Python tests do **not** establish native CMD interpretation of relative references, output filenames, scientific agreement or executable version identity. On a suitable Windows machine, move the completed package to a separate directory, supply the separately installed reviewed executable and run:

```cmd
cd /d "C:\relocated\portable case"
run.cmd "C:\path\to\RORB_CMD.exe"
```

The launcher changes working directory to `events\001`, and executes **that directory's actual `model.par`**, without invoking a Python capture helper. For a direct manual command, change into an event folder and run `"C:\path\to\RORB_CMD.exe" "model.par"`. The executable is not redistributed.

For acceptance record the native executable's original SHA-256 and observed version, exact cwd/argv, each emitted PAR SHA-256 before and after the native run, event/source identity, actual outputs and their hashes, requested versus observed verbosity, and any native failure diagnostics. Run the independent existing comparator on matched effective inputs before asserting numerical parity. A successful reparse is only a **semantic export check**, never an assertion of a native run.

### Remaining dependencies and limits

- Merged #138 [PR #157](https://github.com/Chain-Frost/pyrorb/pull/157) supplies the public typed `resolve_effective_model` that native export and Python event selection share. Persisted engine choices and schema-1 historical meaning are retained.
- Merged #140 [PR #159](https://github.com/Chain-Frost/pyrorb/pull/159) supplies PAR-led binding, schema-3 effective editing, `LoadedProject.run` and the shared `export-native` CLI delegation. Export copies the selected staged inputs and does not follow original embedded paths or package local `resolved_source` paths.
- Merged #139 [PR #166](https://github.com/Chain-Frost/pyrorb/pull/166) supplies the optional pinned PyRomb writer and STM serializer. The positive edited-CATG test ran as part of the merged-main PR #162 source suite. Exact unmodified CATG copy does not need PyRomb; edited graphical input still requires a valid `GeDrawing` and the optional writer dependency.
- Optional external rainfall/curve/temporal-pattern inputs cannot be inferred from metadata. Non-reference external assets currently fail closed rather than yield an incomplete native package. RORBwin saved PAR, plain computational CAT and DAT remain unsupported.
- Native output names, verbosity-dependent available reports and actual CMD success are **not characterised in this bounded software slice**. An export remains marked native-not-run until the actual relocated-par Windows acceptance case is performed. No native executable, numerical method, private data dependency, GUI, second comparator or feature matrix is added.

The independent #143 qualification owner must still check actual native CMD execution of the **relocated emitted PAR**, exact native output/verbosity availability and any numerical comparator verdict against the merged integration revision. Keep #7 and native/numerical gate #5 open until their separate requirements are genuinely met.
