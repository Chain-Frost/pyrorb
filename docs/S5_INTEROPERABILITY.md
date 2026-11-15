# RORB CMD interoperability — implemented and deferred capabilities

The current [schema-2 project contract](PROJECT_JSON.md) and
[explicit-event MVP](PROJECT_BATCH_MVP.md) are distinct from the future
portable RORB native import/export workflow ([#7](https://github.com/Chain-Frost/python-runoff-routing/issues/7)).
See the [independent #143 acceptance record](work/2026-11-15-issue143-s5-acceptance.md)
for exact original fixtures, limitations and evidence status.

## Current CLI/text-file workflow (15 November 2026 baseline)

For an existing *supported CMD* PAR, modern graphical CATG and DESIGN STM,
all physically within the target project directory, explicitly supply **all
three file paths**; embedded PAR references are not yet followed:

~~~sh
python -m runoff_routing.project_json import-rorb case-one legacy-rorb "inputs/parameters.par" "inputs/catchment.catg" "inputs/storm.stm" "project.json"
python -m runoff_routing.project_json validate "project.json"
python -m runoff_routing.project_json export-run "project.json" "typed-run.json"
python -m runoff_routing.project_json run "project.json" "computed.json"
~~~

The example assumes those input files exist in the project's directory and
form a supported S1 RunModel. All writes use new output names and refuse
overwrite. The exported typed-run.json is an S1 **JSON** document, not a
portable native project. A newly created schema-2 project uses the temporary
python-cmd/cmd-6.44 default; explicit python/engineering-v1 and optional
rorb-cmd selections remain available. Pure-Python calculated events remain
computed_unvalidated, with no claim of original CMD numerical equivalence.

## Provisional unmerged import/edit/export CLI (not yet in main)

The following commands belong to the separate #140/#141 implementation
branches and were exercised against the temporary #143 integration test tree.
They **must not** be described as implemented in current main until the
implementation owners reconcile and merge the contracts:

~~~sh
python -m runoff_routing.project_json inspect-par "historic/settings.par"
python -m runoff_routing.project_json import-rorb case-one legacy-rorb "historic/settings.par" "project.json" --catchment "actual catchment.catg"
python -m runoff_routing.project_json validate "project.json"
mkdir relocated
python -m runoff_routing.project_json save-run "project.json" "edited-run.json" "relocated/edited-project.json"
python -m runoff_routing.native_export "relocated/edited-project.json" "native-bundle" --target cmd-6.44
~~~

The import resolver uses the original PAR directory unless an explicit
base directory is supplied; selected path overrides take precedence over
embedded PAR references. The optional `--catchment` override is shown to
illustrate a missing/replaced original file. `edited-run.json` is an S1 typed
RunModel after deliberate user edits, not a dynamically invented CMD event.
A successful bundle contains relative native PAR/CATG/STM inputs and may be
moved without referencing the original project. Export status is
`native_execution=not_run` until an authorised native RORB CMD executable
actually launches the emitted relocated PAR; the bundled launcher is not
numeric proof. The demonstrated source/wheel evidence is linked in the
[independent acceptance receipt](work/2026-11-15-issue143-s5-acceptance.md).

## Contract boundaries

| Operation | Baseline support | Remaining integration |
| --- | --- | --- |
| Open | Read supported CMD PAR, graphical CATG (including characterised .cat) and DESIGN STM separately | PAR-only discovery, path overrides, positive RORBwin dialect recognition (#140) |
| Preserve | Original SHA-pinned input bytes and no-clobber JSON project relocation | Native package with relocated internal input references (#141) |
| Edit | Supported typed model/embedded JSON edits and per-event overrides | Shared effective settings API and edited file-backed native round trip (#138–#141) |
| Export | S1 JSON model export; existing local canonical writers are **not** a native package | Direct PyRomb writer integration (#139) and native package export (#141) |
| Inspect reports | Read-only bounded CMD .out parsing | Installed canonical ryan-tools .out/batch.out reader and consumer migration (#142) |
| Execute | Explicit engine selection; optional local verified native CMD adapter | Direct execution of actual **emitted relocated PAR**, separately from numerical acceptance |

Unknown PAR dialects must be rejected rather than guessed from the suffix.
RORBwin saved-PAR editing is deferred to #144; RORBwin-produced report reading
is current #142. Old plain computational CAT and combined DAT are excluded.
No GUI, TOML, independent numerical method or Monte Carlo work is implied.

A source-exact no-op, a semantically equal edited model, a relocatable and
native-runnable package, a faithful native report reader, and numerical
equivalence are independent results. Do not substitute one for another.
