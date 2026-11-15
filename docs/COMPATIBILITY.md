# Compatibility contract

Source references R1–R6 are in [SOURCES.md](SOURCES.md). Temporary project/CLI default is pure-Python `python-cmd/cmd-6.44`, explicit independent `python/engineering-v1` is the **intended long-term default**, and optional native `rorb-cmd` is explicit. Previously persisted choices and historical engine-less schema-1 `python` semantics remain unchanged. Bounded CLI/text-file [#119](https://github.com/Chain-Frost/python-runoff-routing/issues/119) and deterministic ARR/BoM [#136](https://github.com/Chain-Frost/python-runoff-routing/pull/136) software are **merged**; full CMD #5 and rainfall #137/#8 scientific qualification remain open.

Current independently reviewed actual original CMD source/isolated-wheel result is **50/50 printed Q / 19,550 ordinates passed**, **48 reporting-scalar passes and two legitimately undefined all-zero peak times**, zero scalar failures (merged [#135](https://github.com/Chain-Frost/python-runoff-routing/pull/135), [#113](https://github.com/Chain-Frost/python-runoff-routing/pull/113)). Earlier #100 36/16,836 with 14 source exclusions and disposable #127 45/5 are *dated historical results*, not present source admission. Printed-reference matching does not establish physical conservation/site identity, all native features, default `python` accuracy or generated ARR native methods. Bounded engineering #6 is closed, deferred physical #103 remains, and cached `--snapshot` is not fresh software execution. See [status](STATUS.md), [single matrix](CMD_FEATURE_MATRIX.md) and [original register](REGRESSION_DATASET.md).

## Separate reference identities

Use an engine profile keyed by engine kind (RORB_CMD or RORBwin), executable SHA-256 and observed version/banner. Keep the manual/release-note version separate from the executable version. R2 identifies a 6.31 base; R3 subsequently describes CMD-specific fixes. Neither establishes the actual build of a supplied binary.

Keep separate expected outputs when GUI and CMD disagree. Do not average them, select whichever is easier to match or silently normalise a numerical difference. A mismatch record must identify whether it is input preparation, file interpretation, numerical computation, reporting, an upstream defect or unresolved. Compatibility exceptions require a named profile, fixture, rationale and owner review.

## Historical source/compatibility leads — not active GUI/native tasks

The matrix below records source-derived questions for named CMD version profiles. **It does not authorise** a RORBwin GUI test campaign, save/reload probes, ProcMon, binary inspection, or speculative native experiments. Completed #119 is the foundation for current typed text-file import/edit/export/report #138–#143 work. Broad [issue #16](https://github.com/Chain-Frost/python-runoff-routing/issues/16) is **closed as superseded**; explicitly named native CMD applicability remains under #5 and must be bounded to one evidence-backed unanswered question. RORBwin-only and advanced DCIA/ICIA features are post-MVP #118; ordinary PyRomb per-source impervious/code-2 requirements remain active #96.

## Historical probe matrix

| Concern | Source evidence | Required treatment |
| --- | --- | --- |
| CMD parameter dialect | R2: fixed parameter order; values begin at column 11 except begin/end flags. | Preserve raw values and source locations; distinguish GUI .par files. |
| Loss-model flag | R2 maps 1 to IL/CL and 2 to IL/runoff coefficient; supplied example uses flag 2 with values 20,2. | Treat the historic example as ambiguous, not a hydrological default. Compatible flag-2 software merged #108, but genuine original-native mode-2 effective-input/scalar qualification remains under #90/#5; do not swap flags to make a case pass. |
| GUI-only impervious features | R3 section 1.7 describes DCIA/ICIA; R4 reports CMD lacks this functionality. | Start with the supported pervious MVP. GUI/DCIA/ICIA studies are post-MVP and not scheduled by this evidence note. The historic forum statement is not proof for every future CMD build. |
| Rainfall-excess print code 11 | R3 section 1.8 records a CMD bug fix. | Capture actual supported behaviour and error handling; do not assume the fix from the filename. |
| Time labels | R3 section 1.8 records text/CSV timestep corrections. | Retain raw time labels and a documented version-aware interpretation. Never silently shift a series to improve agreement. |
| Names and calculation order | R1 sections 6.1/6.10; R3 sections 1.4/1.6. | Match stable computational IDs plus raw labels; preserve imported traversal, subarea, gauge and ISA ordering. Duplicate labels are not unique IDs. |
| Design rainfall | R3: IFDs, patterns, ARFs, pre-burst, spatial patterns and filtering. | Compare effective supplied storms first. Separate generated-input parity from solver parity. |
| Ensemble representative | R3 section 1.6 describes first-above-median selection. | Treat selection as build/mode-specific and probe it; keep original TP IDs distinct from ordinal labels. |
| Monte Carlo | R1 chapter 8; R3 extraction/filtering changes. | CMD deterministic ensembles do not validate GUI stochastic sampling or frequency calculations. |
| Errors/output | R2: errors can be in .out or log, successful log may be empty. | Exit status alone is insufficient. Distinguish valid zero runoff, missing outputs, truncated data and failed routing. |

## Parsing and feature states

Use explicit states: unknown dialect, malformed, recognised but unsupported, executable but unvalidated, validated for named profiles. Keep this distinction in inspection reports and the capability matrix. Failed preflight must not produce a plausible discharge file.

Current inputs are modern graphical .catg (including characterised graphical content named .cat), .stm and CMD .par. **Old plain computational CAT and combined DAT are excluded.** #140 owns CMD/recognised RORBwin/unknown PAR classification and path overrides; #142 owns .out/batch.out reading including RORBwin-produced text; saved RORBwin PAR remains deferred #144. Preserve raw inputs and hashes. Do not rewrite original files just to make a parser accept them. Parse comments, separators, terminators, exponent notation, line endings, counts and source references deliberately. Numeric compatibility must not depend on graphical layout.

Validate the control-vector stack and operation ordering, not merely graph acyclicity. RORB can represent diversions and rejoining paths; support for these comes later and must preserve the specified execution semantics. Do not infer fractional control codes through imprecise float equality.

Maintain field-level mapping for catchment area, reaches, pluviographs, bursts, ISA parameters and print locations. A topology reorder can change dav or event mappings. Unknown numerical data must fail explicitly; optional graphics metadata can only be ignored when its non-computational role is established.

## Numerical conventions to characterise

The [opt-in RORBwin 6.52 loss candidate](EXPERIMENTAL_RORBWIN_652_LOSSES.md) is experimental.
Its recorded IL/CL crossing behaviour does not establish native precision, timestamp,
preburst-default or routed-output acceptance. The existing ARR2019 method remains unchanged.

Record units at boundaries: rainfall/initial loss in mm, continuing loss in mm/h, areas in km2, reaches in km, flows in m3/s, storage in m3, time increment in hours and other legacy times in increments (R1 Table 5-1).

Verify reach-type factors, slope bounds, dav/kr calculation, initial storage/outflow, time-zero and half-step rainfall-excess conventions, IL crossing within an increment, continuing/proportional losses, dry steps and burst transitions. The manual specifies Regula Falsi for nonlinear routing and a stated convergence criterion; linear routing and special-storage timestep subdivision need their own tests (R1 sections 2.2.5 and 2.4.5.4).

Do not hard-code an arbitrary universal tolerance or assume the integral used for independent water balance is identical to the legacy reported hydrograph-volume statistic. Verify and label both. Preserve truncation, plateau/tie and nonconvergence behaviour as explicit contracts. A documented implementation improvement is not automatically a compatible replacement.
