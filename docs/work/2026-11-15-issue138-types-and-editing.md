# Issue #138 — typed domain and effective event edits (15 Nov 2026)

## Delivered boundary

- **Ownership and branch:** issue [#138](https://github.com/Chain-Frost/python-runoff-routing/issues/138), [PR #157](https://github.com/Chain-Frost/python-runoff-routing/pull/157) on `feat/issue138-typed-effective-model-20261115`. Original feature base `0675d75b05dba7728b389fdd8af743060b4469b2`; concurrent main advances are reconciled on this branch without replacing their evidence receipts.
- **Domain:** closed S1 numeric control and loss codes, stable textual reach/pattern modes, engine IDs and project-result statuses have enums with source-native wire meanings. Source order and typed immutable `RunModel` identity checks remain authoritative.
- **Loss alternatives:** separate IL/CL (mm/h) and IL/runoff coefficient (dimensionless 0–1) loss-policy editing dataclasses; reject unknown/boolean codes, invalid loss values, mutually exclusive aliases and inconsistent model/ISA identities before writing.
- **Effective-event contract:** `edit_run_model` and `resolve_effective_model` return immutable validated models. The batch runner consumes this same resolver that native export #141 now imports. The resolver is pure for both `ProjectEvent` and caller-owned raw JSON dictionaries; loss alias normalization cannot modify input dictionaries.
- **Preservation:** original immutable source PAR/CATG/STM bytes, source hashes, model/print identities and existing S1 native numeric/JSON codes are unchanged. Source-supported `python-cmd/cmd-6.44` remains the temporary default; explicitly selected `python/engineering-v1` remains available and historical schema-1 engine-less semantics are retained. Project schema-3 editing and source-binding persistence are implemented separately in #140, not duplicated here.

## Verification, with provenance

- **Personally performed:** inspected current GitHub source, interfaces, issue/PR state and the [completed Windows CI run #43726177211](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43726177211) for `576b4904d727124e6538bd58421cd05360595458`. This is an audit of the existing CI receipt, not a separately executed Windows/native RORB run.
- **CI evidence (Windows Python 3.13.17):** repository hygiene; Ruff lint and format; strict Pyright (0 errors); **1,090 non-native source tests passed**; fresh source and installed-wheel CMD public probes **50 cases each: 48 passes, 2 retained incompletes**; wheel build/install, isolated wheel import and **141 wheel-target tests passed**; installed-wheel MVP CLI/full reports and fail-closed PowerShell control passed. Wheel SHA-256 **`f6243c03c51b5bbf4608cc24ca0d0c68f5f629816f226b5b16abe6ac23a57ca8`**. Native RORB executable runs and scientific/numerical equivalence are not asserted.
- **Current change:** additional raw-dictionary mutation and two-mode native/result serialization tests; its new exact-head CI must be assessed separately from the completed earlier receipt.

## Integration and completion limit

- [#140 / PR #159](https://github.com/Chain-Frost/python-runoff-routing/pull/159) owns PAR dialect, source-bound schema-3 persistence and `LoadedProject.run` effective settings; its own Windows source/wheel verification passed. [#141 / PR #162](https://github.com/Chain-Frost/python-runoff-routing/pull/162) is stacked on #138 and consumes public `resolve_effective_model` for native event selection; its independent Windows software checks have passed, but actual relocated native execution is a separate #143 acceptance.
- [#139 / PR #166](https://github.com/Chain-Frost/python-runoff-routing/pull/166) owns optional PyRomb CATG writer and STM source formatting; [#142](https://github.com/Chain-Frost/python-runoff-routing/issues/142) owns importing generic native-report records/enums from ryan-tools. Those modules and dependencies are not implemented here.
- **Next action:** independent review of this exact PR head, confirm subsequent full CI green; #143 independently verifies the joined project import/edit/save/export/report workflow after the owner's PRs integrate. Do not merge, release or close unrelated numerical acceptance gates from this receipt.
