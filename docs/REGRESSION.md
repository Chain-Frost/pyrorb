# Regression and performance contract

## Evidence layers

1. Parser/model fixtures: structural expectations, malformed inputs and unsupported features.
2. Independent numerical checks: simple/analytic cases, conservation, loss bounds, nonnegative storage/flow and timestep sensitivity.
3. Cached native regression: original inputs and raw results from a pinned CMD or GUI build; no executable needed for routine replay.
4. Explicit native Windows acceptance: verify the capture/run adapter and source/installed-wheel calculations on the actual supported environment.
5. Ensemble and Monte Carlo acceptance: event-level parity first, then sampling/probability and aggregate behaviour.

These layers are complementary. A native engine is a compatibility oracle, not proof of hydrological correctness. Synthetic labels applied to one event are not independent native simulations.

## Current offline CMD-first development oracle

For the current feature and source-admission campaign, the calculation under test is **explicit `python-cmd`**. The numerical reference is the *separately captured original RORB-CMD 6.44 output* for the exact retained native source files. [`cmd_public_probe.py`](../repo-scripts/cmd_public_probe.py) and the one maintained public dataset/comparator implement the routine **fresh-source and externally installed-wheel** check without running RORB_CMD, accessing the private investigation repository or requiring a Windows agent. A passing comparison reports evidence for that tested CMD-compatible profile only; the **temporary** product default is `python-cmd`, while the independently engineered `python` remains the future intended default and requires its own hydrological qualification.

Keep three different classes of evidence explicit: **(a)** authored synthetic/analytical tests that exercise invariants and edge cases but have no native golden; **(b)** actual current `python-cmd` computations compared against authenticated old native CMD inputs/results; and **(c)** any separately authorised new native CMD capture for a missing reference. Do not use the earlier cached, unvalidated candidate `--snapshot` as an expected result for a new engine, generate a golden from the same `python-cmd` run, silently renormalise original storm weights, or turn an unsupported/incomplete scalar into a pass. A manufactured synthetic case may only be labelled **directly RORB-CMD-equivalent** after a real native reference has been admitted and independently compared. Once an implemented `python-cmd` feature/profile has itself been independently matched to native CMD observations, its pinned output can be used as a **secondary offline synthetic proxy** to test the independent default `python` engine, without any native process. This is a valid synthetic *cross-engine regression*, not an additional authenticated native golden; report its source implementation/profile, signed peak and full-hydrograph absolute and percentage differences, times and physical trapezoidal volume separately from original CMD report quantities. Fail explicitly if either engine lacks that feature profile, and do not permit new unqualified CMD features to expand the trusted synthetic proxy set.

## Current development platform rule

Per the owner decision of 2026-11-15, **Linux and Windows with Python 3.13 or 3.14 are equivalent verification environments for pure-Python work at this stage**. One complete platform run is enough for deterministic source tests, lint/type checks, pure-Python numerical checks, cached native regressions and an installed-wheel test on the chosen OS. Do not require both operating systems or repeat a passing Linux run under Windows merely for development signoff. Record which OS, interpreter and installed artifact actually ran; do not claim Windows-specific execution from Linux results. A later cross-platform test campaign is deferred.

This platform equivalence does **not** conflate evidence layers: historical `--snapshot` replay is not a fresh engine run; comparing Python outputs with captured native results does not re-execute RORB. Actual RORB_CMD/RORBwin reference execution, Windows-specific path/process/GUI behaviour and native Windows-only integration still require an appropriate Windows host. Keep independent numerical, hydrological and profile-specific acceptance gates unchanged.

## Capture contract for controlled native reference evidence

Retain each catchment (.cat/.catg or combined .dat), storm (.stm), CMD .par, raw .out/.log and any available hydrograph CSV. Include the generator configuration/revision and event-to-file mapping, not just batch peak summaries. Original source bytes must remain unchanged. Runtime capture is explicit opt-in and uses isolated local directories; do not run reference binaries in ordinary tests.

Every case manifest must record:

- schema version, case ID, feature tags and provenance/redistribution status;
- engine kind, executable SHA-256, observed banner/version and operating environment;
- SHA-256/size and relative locator for each input and raw output;
- effective kc/m, loss-model semantics, loss values/units, burst/ISA mapping, timestep, horizon and print-location identities;
- GUI effective settings and saved/generated inputs when GUI execution is the reference;
- command/working-directory policy, exit status, diagnostics, outcome and elapsed-time measurement context;
- expected output locations, raw-to-canonical field/time mappings, tolerance-policy ID and known differences.

Absolute private paths and executables stay local. Keep small permission-cleared fixtures in tests/fixtures/rorb with byte-preserving attributes; keep bulky/private evidence under ignored .local and reference it through approved manifests. Do not claim the uploaded SampleData.zip covers a feature until its cases are inventoried and executed.

## Comparison gates

Require complete case and print-location coverage, exact IDs/counts and unmodified source hashes. Compare rainfall totals/excess, contributing areas and reach/ISA metadata before hydrographs. Compare every ordinate, peak magnitude, peak index/time, horizon, volume/centroid where supported, and independent water balance. Missing or duplicate columns, NaN/overflow, truncated records and unexpected warnings must not disappear during parsing.

Use reviewed absolute plus relative numeric tolerances, with a near-zero floor and output-rounding allowance. Derive acceptance budgets from native output precision, repeatability and routing conventions. Freeze each tolerance policy before accepting comparisons; do not choose a loose percentage after seeing a mismatch. Timing must match the characterised grid; any allowed conversion is explicit and version-aware. Test flat peaks with a documented tie policy.

Report pass, fail, unsupported and not-run separately. Missing native binaries/data must fail the requested native acceptance campaign or produce an explicitly incomplete result, never a green acceptance claim. Cached tests can run without binaries. A failed event cannot be removed from an ensemble or probability denominator without invalidating acceptance.

Golden changes require an explicit update operation, regenerated provenance and a reviewed diff. Ordinary tests must never update expected outputs. Run reference inputs before/after and verify hashes. Installed-wheel checks run outside the checkout and verify the imported module location.

## Performance protocol

Measure single-event cold end-to-end time separately from warm in-memory numerical time. For 1, 100, 1000 and 10000 identical explicit events, record model size, increments, requested outputs, repetitions, median/spread, hardware/OS, dependency versions, thread/worker settings, elapsed time and peak memory. Record JIT compilation independently if used. Compare serial and parallel results and reset all event state.

Repeated RORB_CMD launches include process startup and file I/O. Native RORBwin internal ensembles/Monte Carlo are a different baseline. Missing GUI timing is recorded as missing, not inferred. Benchmarking against a subprocess wrapper does not establish an advantage over compiled in-process RORB. Performance changes must retain the same accepted numerical corpus.

## Monte Carlo-specific gate

Persist the full sample plan with RNG algorithm/version, seed, event IDs, duration, probability strata/masses, sampled depth, loss draw and TP identity. Worker scheduling must not change draws. Different RNGs with the same seed do not constitute matched samples.

Validate weighted total probability, sampling bounds/tails, zero-runoff mass, frequency conversions, interpolation, per-duration curves and critical-duration rules using independently checkable cases. Never use unweighted percentiles for unequal-probability strata, pool unrelated durations or silently renormalise omitted tails. Separate exact deterministic replay from aggregate statistical agreement with GUI runs. Compare increasing sample sizes and independent seeds, and label sampling uncertainty separately from parameter/model uncertainty.

Representative hydrographs must identify the actual sampled event and selection rule. A representative at one print point is not necessarily representative at every other point. Do not imply that the published manual fully specifies every implementation detail; unresolved details remain open until probed or clarified.

Owner approval on 2026-11-15 (#81) permits the curated original CMD input and standard-run result subset under `tests/fixtures/regression-v1/native-cmd/`. It excludes executables, manuals, OS traces and unrelated research. Historical authorisation is unchanged. Published derivatives identify original and sanitised hashes separately; Python outputs are candidate snapshots, never native observations. See [REGRESSION_DATASET.md](REGRESSION_DATASET.md).
