# Deterministic ARR result summaries (#152)

This is a **read-only post-processing step** for the merged [#136](ARR_DESIGN_BATCH.md) deterministic ARR2019/BoM ten-member design ensemble and the unchanged [#119](PROJECT_BATCH_MVP.md) routed event-result contract. It neither recomputes rainfall nor invokes a numerical or native engine. Only CLI, Python API and persisted JSON/CSV/text files are in scope.

## Runnable synthetic example

From the public checkout with the package installed, create the existing synthetic project, execute the existing deterministic source selection, and then summarise **persisted files**:

~~~sh
python examples/create_cmd_project.py
mkdir -p .local
python -m runoff_routing.arr_design_batch examples/arr-design-config.json .local/demo
python -m runoff_routing.arr_result_summary .local/demo.effective.json .local/demo.json .local/summary
~~~

Create the .local directory first. Use new prefixes when rerunning: output files are **exclusive create** and never overwrite existing files. The first command writes cmd-example-project.json in the current directory. Input examples are authored synthetic control data, not original native rainfall or a hydrological design. Source preparation writes the six original #136 artifacts; this reporting step writes three non-destructive files:

| Output | Scope |
| --- | --- |
| PREFIX.analysis.json | Complete duration × AEP × physical print-site aggregates, known member ledger, original source identity, partial-state counts, diagnostic peak ranks/ties, selection/critical-duration decisions explicitly unverified |
| PREFIX.analysis.csv | One row per identified member and requested print site, including non-success input/routing status and individual peak/physical-volume metrics where available |
| PREFIX.analysis.txt | Concise population/site/statistic and separate qualification overview |

If source selection failed for a cell, the original cell's **unqualified source candidates** are retained in a separate JSON collection with their original EventIDs and source orders. They are **not** treated as selected/accepted events or used to fill missing denominators. Candidate IDs also appear as explicitly unqualified rows in the summary CSV; their ranks, routed IDs and hydrograph metrics remain empty. An unidentifiable member remains unidentifiable; no missing TP identity or print site is invented. A failed/incomplete member is never silently omitted from the expected ten-member count. When no routed result exists, requested physical print sites cannot be recovered from these two persisted artifacts; a null/unknown site is emitted instead of a fabricated node.

### API

~~~python
from pathlib import Path

from runoff_routing.arr_result_summary import (
    read_deterministic_results,
    summarize_deterministic_results,
    write_summary,
)

# Persisted-file API: exactly the same data and checks as the CLI.
report = read_deterministic_results(
    Path(".local/demo.effective.json"),
    Path(".local/demo.json"),
)
print(report.to_text())
write_summary(Path(".local/api-report"), report)

# In-memory #136/#119: pass result.effective and
# json.loads(result.routed.to_json()) to summarize_deterministic_results(...).
# No new batch runner is provided.
~~~

## Contract and statistical interpretation

- Source order (source_order), filtered ensemble order (ensemble_order), original source TP EventID (original_tp_event_id) and internal routed event_id are **different fields**. Repeated source EventIDs across different duration/AEP cells are valid. native_ordinal remains **null** until a source-qualified #142 report establishes it. Source/cell axis order is retained, not filename or sorted EventID order.
- Each cell and requested S1 print ID has the exact expected denominator from #136 (ten for admitted ARR2019 selection cells); failures are distinguished as *not prepared*, *prepared but failed/partial*, and *computed with complete comparable output*. Unqualified source candidates have their own count/identities.
- Peak is the maximum of the full **saved** discharge series (m³/s). Every exact-equality peak time/sample is preserved, including all samples for a zero-flow series. Physical volume comes from the existing #119 volumes array: no duplicate integration, native inclusive-volume substitution or second comparator is introduced.
- Observed min/median/mean/max are statistics of **member peak discharges**, not an ARR design-flow quantile or a representative-event algorithm. The even-member median is the arithmetic average of the two centre values **for diagnostic display only**. Descending diagnostic ranks use competition ranking (1, 2, 2, 4) with all equal peaks retained in tie groups; no tie is broken by source, filename or event ID. The software does **not** select from this ranking.
- A cell/site is a complete comparable population only when all ten distinct prepared events have computed outcomes, a complete valid series/volume, exactly one graph for that print ID and identical physical time grid, timestep and site label. Each computed series must contain exactly `calculation_increments + 1` samples and its physical clock must follow the #136 Python-backend elapsed-time convention `t[i] = i × timestep_hours` (relative tolerance 1e-10, absolute tolerance 1e-9 hours); a uniformly truncated or shifted ensemble is incomplete, even if all saved member grids match. For incomplete series, JSON/CSV retain declared versus observed sample counts and a `metric_reason`, and do not attach potentially stale saved volume as a valid derived metric. Incompatible observed horizons/site labels suppress pooled statistics and ranking, while preserving per-member metrics. Partial *observed* statistics are allowed for a common-grid subset but never labelled a complete selection population. Different print sites, effective engines/numerical profiles, source project hashes and design-loss profiles cannot be mixed.
- Critical duration has **no calculated winner** at this evidence stage. Even complete per-duration cells require an expressly declared comparable cross-duration population and independently supported duration aggregation. Native representative and critical-duration decisions always emit null with unverified status. The `comparable_across_durations` diagnostic is true only if **every** considered duration/AEP/site cell has its entire eligible complete population and a non-null common full-horizon time-grid signature, with equal signatures across all durations. A missing, partial or internally non-comparable duration makes this diagnostic false; it never creates a selected duration.
- Software success, #137 generated-input qualification, routed-native qualification and native-selection qualification are distinct. Routing computed_unvalidated never means a native match.

## Native-selection evidence gate

Candidate reference profile for investigation: **RORBwin 6.52, deterministic GUI design-ensemble batch**, not RORB-CMD 6.44 or a generic ARR2019 rule. Existing [#142](https://github.com/Chain-Frost/pyrorb/issues/142) reader scope identifies a pinned 12-hour batch with **80 run rows and eight native-reported representative references**. However, #142's typed reported-reference record has not yet been merged or cross-bound to #136/#119 outcomes, and physical print identity is unresolved in the identified ordinary report. [#137](https://github.com/Chain-Frost/pyrorb/issues/137) has not admitted full sixty-storm effective-input/routed parity. Historical manual wording does **not** decide statistic, eligible population, upper/first/median choice, tie precedence or missing-member handling.

To enable **one** compatible rule, admit authentic report rows with exact version/build and mode, source hashes, each duration/AEP/source TP EventID, native ordinal and run identity, physical site and complete eligible peak population including failures, reported selected file/event, and effective-input/peak correspondence. Independently check discriminating cases for central-order statistics, exact ties and failures. Define the statistic, population, ranking, ties, missing-member behaviour and duration aggregation for that *specific* build/mode; review against original reports. No native selection is implemented without admission.

Open [#152](https://github.com/Chain-Frost/pyrorb/issues/152) tracks this evidence and later #142 typed-record consumption. No new report grammar, GUI procedure, PAR dialect, Monte Carlo method, project schema, numerical-engine change or private runtime dependency is introduced.

## Source/installed-wheel verification

Run python -m pytest tests/test_arr_result_summary.py and the standard [development checks](DEVELOPMENT.md) against source. Build the supported wheel, install **outside** the checkout, verify the imported runoff_routing package path is inside the installed wheel destination, and rerun the three CLI commands in the example plus the in-memory/file API outside the source tree. Compare complete .analysis.json/.analysis.csv/.analysis.txt bytes and the original routed outcomes between source and wheel. This is **software agreement** only, not RORBwin equivalence.
