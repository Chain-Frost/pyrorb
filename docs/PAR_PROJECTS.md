# PAR-led RORB CMD project import — CLI and Python API

The [bounded import scope #140](https://github.com/Chain-Frost/python-runoff-routing/issues/140) supports **RORB CMD** saved parameter files with the characterised `# BEGIN`/`# END` field layout. A recognised RORBwin saved PAR returns an explicit *unsupported/deferred* diagnostic; old computational CAT and combined DAT inputs are excluded. Parsing or importing does **not** establish numerical equivalence.

## Inspect an existing PAR without loading its dependencies

```sh
python -m runoff_routing.project_json inspect-par "/existing/inputs/model.par"
```

The JSON inspection includes `kind`, `status`, `supported`, original byte SHA-256, original catchment/storm references and parsed parameter values when supported, plus diagnostics. This command does not follow file references. Equivalently:

```python
from pathlib import Path
from runoff_routing.rorb_par import inspect_par_bytes, read_par_file

inspection = read_par_file(Path("/existing/inputs/model.par"))
# For in-memory data: inspection = inspect_par_bytes(source_bytes)
if inspection.parameters is not None:
    print(inspection.parameters.catchment_reference, inspection.parameters.storm_reference)
```

## Import by following the filenames in the CMD PAR

```sh
python -m runoff_routing.project_json import-rorb example legacy-rorb "/existing/inputs/model.par" "/workspace/project.json"
```

The importer selects each embedded CATG/STM filename relative to the **PAR directory**. It never searches the process current directory or arbitrary folders. `--base DIR` explicitly changes the relative reference base, including relative overrides:

```sh
python -m runoff_routing.project_json import-rorb example legacy-rorb "/existing/inputs/model.par" "/workspace/project.json" --base "/separate/input-tree"
```

Existing destination directories must exist. Imports never overwrite the project JSON or an occupied staged asset directory. `sources/<project-stem>/parameters.par`, `catchment.catg` (or supported graphical `.cat`) and `storm.stm` store **original exact bytes** and role-distinct SHA-256 identities. Preserve the entire project directory when relocating it.

## Explicit file overrides

A stale embedded filename or intentionally selected replacement is resolved by its role:

```sh
python -m runoff_routing.project_json import-rorb example legacy-rorb "/existing/inputs/model.par" "/workspace/project.json" --catchment "/overrides/new catchment.catg" --storm "/overrides/updated storm.stm"
```

An override always replaces its embedded reference. The resulting `source_bindings` records `role`, `declared_reference` (PAR spelling), `selected_reference`, `origin` (`explicit`, `embedded`, or `override`), `resolved_source` (import-time evidence only), and `staged` (hash-pinned project-relative path). Reopening uses only staged paths, **not** `resolved_source` or embedded filename spelling.

Quote paths at the shell boundary. The reader handles quoted filename tokens, spaces and backslashes deliberately. POSIX systems refuse foreign absolute Windows drive/UNC references rather than guessing mount points or resolving a same-named file. On Windows, a local drive or UNC reference can be selected normally; a drive-relative path such as `C:folder\\file.catg` is ambiguous and rejected. Diagnostics name the missing role, declared token and `--catchment`/`--storm` override mechanism.

## API, edit, save and reopen

```python
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from runoff_routing.project_json import (
    import_rorb_project, load_project, save_project_as, write_project
)

target = Path("/workspace/project.json")
project = import_rorb_project(
    target,
    identifier="example",
    rainfall_profile="legacy-rorb",
    parameters=Path("/existing/inputs/model.par"),
    catchment=Path("/overrides/new catchment.catg"),  # optional
    # storm=Path("/overrides/event.stm"),             # optional
    # base_directory=Path("/separate/input-tree"),   # optional
)
write_project(target, project)

loaded = load_project(target)
first = loaded.run.parameters.routing[0]
new_routing = (replace(first, kc=Decimal("12.75")), *loaded.run.parameters.routing[1:])
edited_run = replace(
    loaded.run,
    parameters=replace(loaded.run.parameters, routing=new_routing),
)
save_project_as(target, Path("/another-workspace/edited.json"), effective_run=edited_run)
assert load_project(Path("/another-workspace/edited.json")).run == edited_run
```

On save, the effective `RunModel` is stored in schema-3 `effective_run`, while original CATG, STM and PAR evidence and source binding choices remain immutable. The selected engine remains unchanged. `load_project(...).run`, run dispatch, and `export-run` consume the effective model. An S1 run document can also be edited and saved without Python scripting:

```sh
python -m runoff_routing.project_json export-run "/workspace/project.json" "/workspace/effective-run.json"
# Edit the typed S1 run JSON using a text editor.
python -m runoff_routing.project_json save-run "/workspace/project.json" "/workspace/effective-run.json" "/another-workspace/edited.json"
python -m runoff_routing.project_json inspect "/another-workspace/edited.json"
```

**Distinctions:** original-source inspection/re-emission retains original bytes, edited project JSON stores effective semantic values, and standalone native CMD project export is an independent #141 workflow. `export-run` emits **only** S1 JSON; it is not a runnable CMD package. The original PAR remains immutable even when its effective values or selected input path have changed.

## Limits and safety

Only supported modern graphical CATG, DESIGN STM and characterised single-burst CMD PAR inputs are admitted. A known RORBwin saved-PAR cannot execute as CMD through fallback. No native executable is launched during import. Files are size bounded, hash-checked and contained within the project root on reopen; no generated native goldens or original inputs are modified. On systems without the original Windows drive/UNC mapping, supply a local override rather than assuming equivalent filenames.
