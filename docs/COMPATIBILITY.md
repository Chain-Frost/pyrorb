# Compatibility contract

Source references R1–R6 are defined in [SOURCES.md](SOURCES.md). Public `main` has a restricted S1 typed model/source parser, bounded **default `python`** S2 calculations, JSON project support and explicit native CMD adapter. The bounded `python-cmd` compatible backend has merged via [PR #79](https://github.com/Chain-Frost/python-runoff-routing/pull/79), with original unsupported sources still explicit. Independent [merged #100](https://github.com/Chain-Frost/python-runoff-routing/pull/100) verified **36/36** admitted cases for fresh public source and installed-wheel CMD Q/scalars. Remaining features/physical acceptance belong to [#5](https://github.com/Chain-Frost/python-runoff-routing/issues/5) and #90–#96; default volume/continuity residuals are deferred to [#103](https://github.com/Chain-Frost/python-runoff-routing/issues/103). **Neither complete CMD replacement nor broad physical engineering acceptance is established; bounded default stage #6 is closed.** The original 36 computed/failing CMD catchments and the S5 201-row comparison describe an **older default Python** implementation, not the newer merged `python-cmd` backend, which has independently verified **36 original CMD cases/16,836 printed ordinates** from a fresh public source/wheel at a pinned revision and retains **14 unsupported source cases**. The revised default method from [#102](https://github.com/Chain-Frost/python-runoff-routing/pull/102) adopts CMD's discrete-bin IL/CL behaviour and reports separate peak/ordinate/physical-volume percentage differences; full physical and feature qualification remains open. The [public cached regression](REGRESSION_DATASET.md) replays a different, historical **unvalidated candidate**, never a current fresh source/wheel execution. Retain the limited CMD 6.44 and GUI 6.52 native source evidence ([S0 record](work/2026-11-11-s0-native.md)) and frozen policies separately. The [current backlog](BACKLOG.md) and [single merged CMD feature matrix](CMD_FEATURE_MATRIX.md) own current status and coverage.

## Separate reference identities

Use an engine profile keyed by engine kind (RORB_CMD or RORBwin), executable SHA-256 and observed version/banner. Keep the manual/release-note version separate from the executable version. R2 identifies a 6.31 base; R3 subsequently describes CMD-specific fixes. Neither establishes the actual build of a supplied binary.

Keep separate expected outputs when GUI and CMD disagree. Do not average them, select whichever is easier to match or silently normalise a numerical difference. A mismatch record must identify whether it is input preparation, file interpretation, numerical computation, reporting, an upstream defect or unresolved. Compatibility exceptions require a named profile, fixture, rationale and owner review.

## Initial probe matrix

| Concern | Source evidence | Required treatment |
| --- | --- | --- |
| CMD parameter dialect | R2: fixed parameter order; values begin at column 11 except begin/end flags. | Preserve raw values and source locations; distinguish GUI .par files. |
| Loss-model flag | R2 maps 1 to IL/CL and 2 to IL/runoff coefficient; supplied example uses flag 2 with values 20,2. | Treat the example as ambiguous, not a valid hydrological default. Probe both flags with distinguishable losses and inspect echoed parameters; do not swap flags to make a case pass. |
| GUI-only impervious features | R3 section 1.7 describes DCIA/ICIA; R4 reports CMD lacks this functionality. | Start with pervious MVP; version-specific GUI tests are required for these features. The historic forum statement is not proof for every future CMD build. |
| Rainfall-excess print code 11 | R3 section 1.8 records a CMD bug fix. | Capture actual supported behaviour and error handling; do not assume the fix from the filename. |
| Time labels | R3 section 1.8 records text/CSV timestep corrections. | Retain raw time labels and a documented version-aware interpretation. Never silently shift a series to improve agreement. |
| Names and calculation order | R1 sections 6.1/6.10; R3 sections 1.4/1.6. | Match stable computational IDs plus raw labels; preserve imported traversal, subarea, gauge and ISA ordering. Duplicate labels are not unique IDs. |
| Design rainfall | R3: IFDs, patterns, ARFs, pre-burst, spatial patterns and filtering. | Compare effective supplied storms first. Separate generated-input parity from solver parity. |
| Ensemble representative | R3 section 1.6 describes first-above-median selection. | Treat selection as build/mode-specific and probe it; keep original TP IDs distinct from ordinal labels. |
| Monte Carlo | R1 chapter 8; R3 extraction/filtering changes. | CMD deterministic ensembles do not validate GUI stochastic sampling or frequency calculations. |
| Errors/output | R2: errors can be in .out or log, successful log may be empty. | Exit status alone is insufficient. Distinguish valid zero runoff, missing outputs, truncated data and failed routing. |

## Parsing and feature states

Use explicit states: unknown dialect, malformed, recognised but unsupported, executable but unvalidated, validated for named profiles. Keep this distinction in inspection reports and the capability matrix. Failed preflight must not produce a plausible discharge file.

Initial readers cover supported subsets of .cat, .catg, combined .dat, .stm and CMD .par; retained .out is the first reference-output format. Preserve raw inputs and hashes. Do not rewrite original files just to make a parser accept them. Parse comments, separators, terminators, exponent notation, line endings, counts and source references deliberately. Numeric compatibility must not depend on graphical layout.

Validate the control-vector stack and operation ordering, not merely graph acyclicity. RORB can represent diversions and rejoining paths; support for these comes later and must preserve the specified execution semantics. Do not infer fractional control codes through imprecise float equality.

Maintain field-level mapping for catchment area, reaches, pluviographs, bursts, ISA parameters and print locations. A topology reorder can change dav or event mappings. Unknown numerical data must fail explicitly; optional graphics metadata can only be ignored when its non-computational role is established.

## Numerical conventions to characterise

The [opt-in RORBwin 6.52 loss candidate](EXPERIMENTAL_RORBWIN_652_LOSSES.md) is experimental.
Its recorded IL/CL crossing behaviour does not establish native precision, timestamp,
preburst-default or routed-output acceptance. The existing ARR2019 method remains unchanged.

Record units at boundaries: rainfall/initial loss in mm, continuing loss in mm/h, areas in km2, reaches in km, flows in m3/s, storage in m3, time increment in hours and other legacy times in increments (R1 Table 5-1).

Verify reach-type factors, slope bounds, dav/kr calculation, initial storage/outflow, time-zero and half-step rainfall-excess conventions, IL crossing within an increment, continuing/proportional losses, dry steps and burst transitions. The manual specifies Regula Falsi for nonlinear routing and a stated convergence criterion; linear routing and special-storage timestep subdivision need their own tests (R1 sections 2.2.5 and 2.4.5.4).

Do not hard-code an arbitrary universal tolerance or assume the integral used for independent water balance is identical to the legacy reported hydrograph-volume statistic. Verify and label both. Preserve truncation, plateau/tie and nonconvergence behaviour as explicit contracts. A documented implementation improvement is not automatically a compatible replacement.
