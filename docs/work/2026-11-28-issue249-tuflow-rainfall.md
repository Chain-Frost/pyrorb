# Issue #249 — RORB-to-TUFLOW rainfall boundary export

## Source and contract review

Start from public main `ef5c985a607545aee9f58d2a0f4f5712c410e46d`. Scope: one standard report, explicit
gross/excess and canonical column selection, API/CLI, no engine execution or release.
[Issue #249](https://github.com/Chain-Frost/pyrorb/issues/249).
The [legacy extractor at 5eda4f0](https://github.com/Chain-Frost/ryan-tools/blob/5eda4f0/ryan-scripts/RORB-python/extract_rainfall-to-TUFLOW.py)
merges a wet first row into the second row, appends a zero row and coerces malformed
numeric fields to zero. A first-interval merge preserves some sums but changes rainfall
timing; the new exporter instead maps every source interval to its own end timestamp.
The final dry row is only needed if the last selected interval remains wet.
Numeric failures are never filled with zero. Legacy callers are left unchanged;
downstream adoption must wait for a qualified published API.

[User contract and BC database example](../TUFLOW_RAINFALL_EXPORT.md).
Direct review of the manual's stepped rainfall convention and the three existing public
reports found the following. Values below were independently summed from the printed
rows, not recomputed by RORB or taken from the Tot. footer.

| Retained report | Series | Rainfall intervals | First depth (mm) | Last depth (mm) | Sum of printed increments (mm) | Printed Tot. (mm) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| CMD 6.44 | Gross A | 72 | 0 | 4 | 69 | 69 |
| CMD 6.44 | Excess catchment | 72 | 0.0 | 3.4 | 58.5 | 58.3 |
| RORBWin 6.45 | Gross Q (page 2) | 24 | 2 | 4 | 92 | 93 |
| RORBWin 6.45 | Excess X (page 2) | 24 | 0 | 0 | 4 | 4 |
| RORBWin 6.52 | Gross A | 72 | 0 | 3 | 47 | 51 |
| RORBWin 6.52 | Excess catchment | 72 | 0.0 | 1.7 | 22.2 | 22.1 |

Each has a printed 0.50 h step and a rainfall Start of 0; the final wet
interval ends at 36 h or 12 h respectively. The printed OUT hydrograph clocks
were also independently checked against the step (301, 501 and 301 labels respectively).
The 6.45 example has two pages for each rainfall kind. Previous canonical numbered
first pages remain unchanged; the continuation sections use a page suffix.
No original fixture is copied or modified.

Sources: existing public CMD object
`00ffce5b02f4972c3db08a9d4811b25320af513f9073f1373daa901f0d40c8d9.out`
and existing public reader-test-data checkout
`4535ff86ea978666b990748d72d927695be2158c`:
`RORB/6.45-490-event-reader-example/RORB_14141_ aep10_du12hourtp1.out`
and `RORB/12hr-areal-example/Fig6_7_ aep0p2EY_du12hourtp1.out`.
The tests use synthetic fixtures and these previously admitted references;
there is no new restricted source material.

## Verification and handoff

Focused tests check literal CSV rows, independent stepped interval consumption,
gross/excess distinction, page selection, dry and wet end, declared start,
exact decimal time boundaries, rounded-source depth totals, output protection and
malformed/ambiguous/incomplete sources. Existing Windows quality workflow gains
the same focused tests in its isolated-wheel reader group; no additional CI lane.
MCP capability and API reference expose discovery as Python/CLI only, not a new
MCP file-write tool.

Repository network checkout and local full quality execution were unavailable in the
chat environment. The branch is a draft implementation pending exact-head source
and installed-wheel tests, pinned Ruff/strict Pyright, existing regression checks
and independent review. Do not interpret the source inspection as executed
converter acceptance.

Native TUFLOW validation remains pending: on an installed metric Classic/HPC build,
configure two non-overlapping RF polygons with the same CSV time column and distinct
depth columns, explicit STEPPED rainfall, no loss or time/depth modifier, start
before the anchor and finish beyond the trailing dry interval. Check the TUFLOW
read/initialisation log, its rainfall time series/check output, first/last wet interval,
interior dry interval, total rainfall depth per polygon and zero rainfall outside the
event. Compare against the literal synthetic CSV and an admitted original report.
Record build, model/control-file hashes, command, actual extracted check data,
per-column depth differences and outcome; use no restricted public data. If no
licensed environment is available, retain native consumption as unverified.

Do not merge, publish or migrate ryan-tools before separate owner approval.
