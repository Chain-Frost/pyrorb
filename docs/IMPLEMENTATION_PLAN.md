# Implementation and acceptance sequence — CMD first

**Current authority:** [roadmap #1](https://github.com/Chain-Frost/python-runoff-routing/issues/1). See [backlog and owners](BACKLOG.md), [public quickstart](QUICKSTART.md), [engine contract](ENGINES.md) and the [single merged CMD feature inventory](CMD_FEATURE_MATRIX.md) from [PR #84](https://github.com/Chain-Frost/python-runoff-routing/pull/84). Do not use old S0–S8 handoffs to reopen completed work.

## Three numerical engines

| Engine | Product role | Required acceptance |
| --- | --- | --- |
| **python** | Default improved engineering engine, maintained as a product implementation | Independent analytic/manufactured cases, conservation, refinement, stability, failure semantics and repeatable explicit batches; no CMD bit-for-bit obligation |
| **python-cmd** | Explicit CMD 6.44-compatible Python implementation, isolated arithmetic | Correct versioned effective inputs, original ordering, full output horizons and native policy on the required CMD feature population |
| **rorb-cmd** | Optional, explicit user-installed native CMD adapter | Verified executable/input identities, complete source/output/time controls and structured failures; no bundled binary or fallback |

Installed software, supported input recognition, cached output matching, actual computation, native numerical equivalence and independent engineering accuracy are **not interchangeable**. Native inclusive reported volume is not by itself a physical water-balance measurement.

## Current implementation order

1. **Already merged:** engine selector and native adapter via [#77](https://github.com/Chain-Frost/python-runoff-routing/pull/77), and public curated dataset/comparator/analytical controls via [#78](https://github.com/Chain-Frost/python-runoff-routing/pull/78), [#80](https://github.com/Chain-Frost/python-runoff-routing/pull/80), [#82](https://github.com/Chain-Frost/python-runoff-routing/pull/82) and [#83](https://github.com/Chain-Frost/python-runoff-routing/pull/83). Historical candidate snapshots remain explicitly separate from fresh execution.
2. **A:** bounded `python-cmd` whole-event implementation merged via [PR #79](https://github.com/Chain-Frost/python-runoff-routing/pull/79); [#75](https://github.com/Chain-Frost/python-runoff-routing/issues/75) retains current source/wheel/native acceptance and original excluded-feature obligations. Keep compatible arithmetic isolated, preserve all source identities and unchanged evidence policies.
3. **B:** maintain the one published regression register/CLI and independently distinguish computed, excluded and incomplete cases. Retire older [S5 draft #58](https://github.com/Chain-Frost/python-runoff-routing/pull/58) only after its unique evidence-status, hash, site/time and no-clobber protections have current tests or a deliberate migration.
4. **C:** [CMD feature gate #5](https://github.com/Chain-Frost/python-runoff-routing/issues/5) now uses the **merged** [single matrix from #84](CMD_FEATURE_MATRIX.md), distinguishing parsed, executable, output-supported and independently qualified cases. Continue the actual feature qualifications through #90–#96 without claiming the inventory alone completes CMD replacement.
5. **D:** phase-one [improved-engine method and independent controls](ENGINEERING_METHOD.md) merged via [#97](https://github.com/Chain-Frost/python-runoff-routing/pull/97). Continue full prospective engineering numerical/conservation acceptance and [phase-two prepared in-memory batches #99](https://github.com/Chain-Frost/python-runoff-routing/pull/99) under [#6](https://github.com/Chain-Frost/python-runoff-routing/issues/6); measure performance only after correctness and state-isolation rules are met.
6. **E and F:** public cleanup [#76](https://github.com/Chain-Frost/python-runoff-routing/issues/76) removes obsolete scripts/handoffs only after callers and migration are understood. Private investigations index unique historical evidence but are never a public package, solver, runtime dependency or required checkout.
7. **CMD replacement gate:** both Python engines must meet every required CMD row for their declared policy, or have an owner-approved explicit exclusion. The native adapter cannot substitute for an absent Python implementation. An accepted subset is not a full replacement.
8. **Only after CMD completion:** expand RORBwin-specific storm features [#8](https://github.com/Chain-Frost/python-runoff-routing/issues/8) and optional interoperability [#63](https://github.com/Chain-Frost/python-runoff-routing/issues/63). Stratified Monte Carlo [#9](https://github.com/Chain-Frost/python-runoff-routing/issues/9) and publication/release [#10](https://github.com/Chain-Frost/python-runoff-routing/issues/10) remain independent deferred stages.

## Existing stage boundaries

- **S0/S1 [#2](https://github.com/Chain-Frost/python-runoff-routing/issues/2)/[#3](https://github.com/Chain-Frost/python-runoff-routing/issues/3):** source-preserving restricted RORB inputs, typed model, capture/inspection and fail-closed unsupported dialects. General parser/native feature acceptance remains open.
- **S2 [#4](https://github.com/Chain-Frost/python-runoff-routing/issues/4):** a bounded supplied-DESIGN storm calculation exists in the default Python engine; the historical native parity failures remain historical, and fresh compatible/default-engine acceptance is separately tracked.
- **S3 [#5](https://github.com/Chain-Frost/python-runoff-routing/issues/5):** the current issue is the CMD feature-completeness gate, **not** an instruction to expand GUI-only storage and FIT features before CMD is complete.
- **S4 [#6](https://github.com/Chain-Frost/python-runoff-routing/issues/6):** validated deterministic explicit-event computation precedes claimed in-memory batch acceleration.
- **S5 [#7](https://github.com/Chain-Frost/python-runoff-routing/issues/7):** JSON schema-2 projects and current diagnostic adapters exist. TOML is **owner-deferred**; not a required current input or release format.
- **S6 [#8](https://github.com/Chain-Frost/python-runoff-routing/issues/8):** bounded ARR/BoM rainfall source/method functions exist, but generated-input and routed native equivalence remains open.
- **S7/S8 [#9](https://github.com/Chain-Frost/python-runoff-routing/issues/9)/[#10](https://github.com/Chain-Frost/python-runoff-routing/issues/10):** Monte Carlo and release are deferred; neither follows automatically from a green CI run.

## Computational and verification safeguards

Keep source, typed model, rainfall preparation, deterministic state and reporting distinct. Preserve input lexemes when compatibility requires them, original control/topological order, complete event horizons, raw native clocks/tokens and immutable source fingerprints. Existing [source citations](SOURCES.md), [compatibility requirements](COMPATIBILITY.md) and [regression policies](REGRESSION.md) govern detailed mathematics. Avoid duplicate legacy parsers, research runners, hidden private imports and unmeasured acceleration. The default engine's engineering policy is independent; do not fit its tolerance to CMD printing. No new hosted native workflow, licence/release decision, or native source modification is authorised here.
