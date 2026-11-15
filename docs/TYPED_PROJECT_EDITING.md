# Typed S1 domain and effective project editing (#138)

The immutable S1 `RunModel` remains the calculation-domain contract. This is an interface agreement for other current project owners, not a new numerical engine, project schema or native export implementation.

## Closed choices and wire values

| Public choice | Python type | Native/JSON wire meaning |
| --- | --- | --- |
| CMD loss model | `LossMode(IntEnum)` | `1` initial/continuing; `2` initial/runoff coefficient |
| Catchment control | `ControlCode(IntEnum)` | `1, 2, 3, 4, 5, 7` in original order |
| Reach encoding | `ReachMode(StrEnum)` | `implicit_natural`, `explicit_reach_types` |
| Temporal basis | `PatternBasis(StrEnum)` | `percent_of_depth`, `relative_weights`, `combined_preburst_percent` |
| Engine kind | `EngineKind(StrEnum)` | `python`, `python-cmd`, `rorb-cmd` |
| Project execution status | `ResultStatus(StrEnum)` | Existing engine-result status strings; independent of native-report inspection status |

Identifiers, physical print IDs, labels, source paths, source hashes, model source roles and versioned numerical profile identifiers are **not** enums. PAR dialect classification belongs to #140; generic RORB report reader statuses/types belong to ryan-tools #240 / downstream #142. Existing `EngineStatus` and `EngineId` Literal input aliases remain temporarily accepted in annotated caller boundaries while their stored runtime values are enums; no alternate engine defaults or fallback are created.

All enum values compare with the existing native primitive and serialise through the existing native/JSON format. S1 schema version remains 1; project schema version remains 2. The project manifest's engine-less schema-1 interpretation remains `python/engineering-v1`, while new schema-2 projects default to `python-cmd/cmd-6.44`.

## Loss semantics and immutable editing

`LossValue.continuing` retains the existing source-file scalar and exact Decimal spelling. Its *units depend on* `ParameterSet.loss_model` and must not be guessed without the mode. For type-safe editing, `ParameterSet.loss_policies` projects a tuple of `InitialContinuingLoss(initial_loss_mm, continuing_loss_mm_h)` or `InitialRunoffCoefficientLoss(initial_loss_mm, runoff_coefficient)`. `ParameterSet.with_loss_policies(...)` accepts only the matching alternative and returns a newly validated parameter set. IL and CL must be finite and nonnegative, while RoC is finite and between 0 and 1 inclusive. ISA/burst order is preserved and validated.

`edit_run_model(original, parameters=..., catchment=..., storm=...)` creates a fresh `RunModel` with cross-document identity and count validation. It does not modify `RorbSource`, imported original bytes, referenced paths or other source provenance.

`project_batch.resolve_effective_model(base: RunModel, event: ProjectEvent | dict | None)` returns `EffectiveModel(run, event_id, edited_fields)`. It validates exactly the existing supported one-ISA storm/loss/routing per-event patch, rejects unknown/unsupported or mutually exclusive fields, and is the shared derivation point called by the batch runner. The event loss overlay accepts native `continuing` or its unambiguous mode-specific alternative `continuing_loss_mm_h` / `runoff_coefficient`, but never a mixture. `override_label` retains the existing audit string.

A focused import regression checks that event edits retain the source-project bytes, PAR/CATG/STM fingerprints and original source bindings unchanged; only the newly derived model changes. Actual persisted editable settings and native export integration remain owned by #140/#141.

#140 owns persistence and original-source bindings and must use this effective run rather than a second patch resolver. #141 owns target expressibility and export and should call the same effective resolver; the native target must not silently absorb unsupported edits. #139 owns source writer integration. A resolved model alone does not guarantee runnable native output, semantic CATG export, engine numerical parity or independent source-binding validation.
