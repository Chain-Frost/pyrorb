# Deterministic ARR2019 design-rainfall ensembles (issue #8)

This is a **bounded, offline, CLI/text-file** workflow, not a general ARR/RORBwin generator or a certified hydrological method. It consumes the already merged BoM IFD, ARR point/areal temporal-pattern, ARR2019 selection/ARF and legacy Data Hub preburst/loss readers. It runs the generated explicit storms through the existing [#119 event API](PROJECT_BATCH_MVP.md). There is no new numerical kernel, GUI, stochastic sampler, private repository dependency, PyTUFLOW dependency or climate/PMP default.

## Reproducible public-only demonstration

From the checkout root, with Python 3.13 or 3.14 and the package installed:

```sh
python examples/create_cmd_project.py
mkdir -p .local
python -m runoff_routing.arr_design_batch examples/arr-design-config.json .local/arr-design
python -m runoff_routing.project_batch cmd-example-project.json .local/arr-replayed --events .local/arr-design.events.json --engine python-cmd
```

On Windows, create `.local` with `mkdir .local` if absent. Use new filenames for every run: all six output paths are created exclusively and cannot overwrite prior results. The sample IFD and pattern CSV files are authored synthetic controls; **none of their values, coordinates or TP labels is genuine design data**.

The six outputs are:

| File | Meaning |
| --- | --- |
| `PREFIX.effective.json` | Exact-source hashes, BoM input units, original TP IDs/source and ensemble order, gross and once-ARF-adjusted series, raw/applied losses, named method and profile, complete requested axes, failed/unsupported input cells, per-event execution status and missing qualification |
| `PREFIX.events.json` | Standard, replayable [#119 explicit-event request](PROJECT_BATCH_MVP.md) with each prepared storm and applicable loss override; it contains no duplicate rainfall or loss transformation |
| `PREFIX.json` | Unmodified common #119 full structured routed outcomes, sites, complete time/hydrograph series and native-versus-physical volume conventions |
| `PREFIX.csv` | Unmodified common #119 per-event/per-site full-horizon CSV, including failure rows for prepared events that cannot route |
| `PREFIX.txt` | Unmodified common #119 concise routing summary |
| `PREFIX.summary.txt` | Design-level requested/produced population, explicit input-cell failures, overall non-success status and both evidence limitations |

The `.events.json` file is valid for #119 replay **when at least one event was prepared**. When no input cell could be prepared, it contains an empty `events` array for audit only; this is intentionally rejected by the #119 request parser. No invented storm or hydrograph is substituted.

## Strict configuration

The JSON config uses `format=python-runoff-routing-arr2019-design`, `schema_version=1`, and **exactly** the keys in [the runnable sample](../examples/arr-design-config.json). Paths resolve relative to that config. `durations_min` is an ordered axis of 1–8 exact, whole-minute BoM durations; `aep_labels` is an ordered axis of 1–6 **original BoM labels**. Only source `AEP_PERCENT` values supported by the existing ARR2019 ten-member frequency selection (50%, 20%, 10%, 5%, 2%, 1%) are admitted. There is no EY/ARI/one-in-N conversion or nearest/interpolated IFD/TP selection.

The explicit `catchment_area_km2` must equal the sum of the project's source subareas. Below 75 km², `pattern_kind=point`; at or above 75 km², `pattern_kind=areal` and the existing Table 2.5.9 area bin is used. `temporal_region` is exact source metadata, not a guessed spatial join. `arf_region` explicitly selects the *published* ARR2019 Book 2 regional coefficients (no silent Data Hub replacement). ARF eligibility and out-of-range restrictions are inherited unchanged from `arr_arf.py`; no short-duration or rare-extrapolation opt-in is exposed in this bounded workflow. Only depth-in-mm BoM source tables are supported; intensity inputs do not convert implicitly.

Each duration/AEP cell must contain **all ten** source-order patterns. A missing member, non-100% increments, unsupported bin, missing IFD label, incompatible timestep or unsupported loss/preburst adjustment fails that entire cell. Where the required frequency/area bin cannot be accepted, `unqualified_source_candidate_ids` and their original source orders remain visible, explicitly as **unqualified source candidates**, not as an invented accepted ensemble. It remains visible in `.effective.json` and `.summary.txt`; it **does not** become an incomplete ten-event numerical success. When an ensemble has ten selected members but event preparation fails, their original source IDs are still visible as input-error members, not fabricated replacement storms.

`dry_tail_min` provides an explicit, whole-minute dry routing tail; it must divide exactly by every selected TP timestep. For each event, the adjusted ARF rainfall depth is repeated across the original ordered pervious subareas without spatial variability. The published source TP percentages are passed directly to the maintained S1 `StormModel`; no rescaling, filtering, reordering or temporal-pattern renumbering is performed. The source raw rainfall and adjusted increments are both retained. This is an explicit DESIGN burst for one pluviograph/ISA/loss model 1, with existing supported natural network controls and print sites.

## Loss and preburst policies

The required `loss.mode` has three explicit options:

- `project_il_cl`: unchanged project initial/continuing losses, applied by the selected #119 engine **once**. No preburst deduction.
- `legacy_source_depth_burst_only`: use `arr_txt` with `legacy_profile=arr2016`, one exact `percentile` (10/25/50/75/90) and `excess_policy`. The maintained selector computes burst IL = max(0, original storm IL minus **source** preburst depth), once. Pass reduced IL and original CL to the engine, not pre-computed runoff excess.
- `legacy_ratio_areal_burst_only`: same source and controls but explicitly use the maintained, **unaccepted RORBwin-oriented hypothesis** of source preburst ratio × **once-ARF-adjusted** design rainfall depth. The independent original source preburst depth is retained, and no second ARF or IL reduction is performed.

Both legacy methods require exactly matching BoM/ARR requested WGS84 coordinates and original source hashes. The default `excess_policy=reject` must be explicit; `clamp_burst_il_to_zero` is a separately labelled, potentially physically incomplete opt-in. Neither method invents a GSAM/Jordan preburst temporal profile, nor applies the experimental excess kernel as a second loss. For this slice, full explicit preburst temporal distribution is **not supported**; it requires a separately evidenced pattern/profile contract.

`engine` and `numerical_profile` are required, normally `python-cmd` / `cmd-6.44`.
Explicit `python` / `engineering-v1` is allowed but must be independently qualified.
Native `rorb-cmd` execution additionally requires the explicit written-depth profile below,
a hash-pinned file-backed `legacy-rorb` project and a local native configuration.
Each effective event is materialized and reparsed through the portable native exporter;
its original CATG is copied byte-exact, and its new PAR/STM and package manifest persist
under the configured native output root. Original project assets are never overwritten.

## Explicit written-depth preparation

The optional `rainfall_preparation` field defaults to `published_decimal`, preserving
existing saved requests and the full published-ARF calculation. To prepare the
two-decimal storm-depth contract used for the bounded RORBwin comparison, select:

```json
"rainfall_preparation": "published_arf_stm_2dp"
```

This profile first calculates the existing published ARF-adjusted depth, then rounds
that total to 0.01 mm with explicit decimal HALF_EVEN rounding. It disaggregates the
prepared total using the original percentages and supplies that same prepared total
to the selected engine. The engine continues to own its numerical storage,
normalization and loss application; rainfall preparation never applies losses twice.
Source temporal percentages must already have 0.01% resolution. Higher-precision
patterns fail explicitly rather than being silently rounded or renormalized.
Only `loss.mode=project_il_cl`, with no preburst adjustment, is admitted for this profile.

The effective manifest retains `published_areal_total_mm`, the complete published and
prepared increment vectors, `prepared_depth_minus_published_mm`, the selected policy
and actual event input. Existing `areal_total_mm` and `areal_increments_mm` describe
the prepared input passed to execution. The method ID is
`arr2019-bom-published-arf-stm-2dp-burst-only-v1`.

This is a **published-ARF plus written-depth policy**, not an implementation of
RORBwin's internal ARF/transcendental helpers. HALF_EVEN is this policy's specified
tie rule, not a claim that every native formatter tie has been qualified. Agreement
of prepared depths with original native storm files must be assessed for the selected
sources; `native_arf_arithmetic_parity` remains `not_assessed`. Original native
rainfall files remain authoritative when strict input identity is required.
Matching input preparation does not establish RORBwin/CMD solver equivalence.

For a native run, use `engine=rorb-cmd`, `numerical_profile=cmd-6.44` and:

```powershell
py -3.13 -m runoff_routing.arr_design_batch design.json results/design --native-config native.json
```

The native configuration must explicitly bind the installed executable, SHA-256,
version, output root and print mapping. Missing configuration or an unsupported source
fails without selecting a Python engine. Reports bind the prepared package manifest
and native capture separately. Preparing a native package is not a native execution;
only genuine inspected native results populate a successful native outcome.

## Acceptance and limitations

**Two different claims must remain separate.** A run with complete ten-member cells and 100% `computed_unvalidated` routed outcomes is a successful *software workflow*, not generated-input parity against a native RORBwin/CMD effective storm and not routed numerical parity. The manifest retains `generated_input_reference_status=not_assessed` and `routed_native_reference_status=not_assessed` even for a green run. Current loss/preburst and RORBwin rounding precision residuals remain under [#8](https://github.com/Chain-Frost/python-runoff-routing/issues/8); full CMD source/numerical qualification is separately tracked under [#5](https://github.com/Chain-Frost/python-runoff-routing/issues/5).

No universal representative-event rule or critical-duration selection is applied. The manifest records both as **not selected / unverified**. Neither an ensemble median nor first-above-median/tie ordering is asserted without a pinned build/mode-specific reference. Every selected duration, AEP and original TP remains available for a later independently evidenced selection study.

Validation levels: synthetic source/pattern/ARF/IL checks; separate generated-input manifest/replay checks; current #119 routing source/wheel tests; **pending** original-native effective storm comparisons; **pending** generated-storm routed comparisons. Do not promote any one level to a later one. All advanced #114–#118 capabilities and Monte Carlo #9 remain deferred.

**Review correction (15 November 2026):** for the explicit ratio-derived legacy preburst mode, the source preburst depth is audit-only. The selected `excess_policy` is enforced **after** ratio × areal rainfall is materialised, not against the unused exported depth. Source-depth mode continues to reject source preburst greater than storm IL. The regression includes both the above-source-IL/below-applied-IL acceptance case and the above-applied-IL rejection case.
