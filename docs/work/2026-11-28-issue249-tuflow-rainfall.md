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

## Follow-up on initial hosted quality run

At `927bc6e53ed5c8406b82eefbd351b557dffe6c32`, the [Windows 3.11 run](https://github.com/Chain-Frost/pyrorb/actions/runs/46107570860) passed repository hygiene (683 files, zero errors), then stopped at seven Ruff findings. No source tests, wheel or regression verification ran on that attempt. The follow-up replaces successive-pair zip with pairwise, introduces a typed ValueError subclass for rainfall admission refusals, removes the unused suppression, strengthens negative-test diagnostic matching and adds source/destination protection checks. Rules and existing CI lanes are unchanged. Fresh exact-head quality evidence is required.

TUFLOW 2026.3 manual section 8.4.3.2.1 identifies the actual native inspection outputs: `2d_bc_tables` and .tlf entries labelled `Rainfall histogram after Rainfall Boundary Factor adjustment` and `RF Rainfall histogram conversion`. Section 8.4.3.2.2 identifies RFR and RFC map outputs for rainfall rate and cumulative rainfall. Use these in the pending native polygon check rather than relying on solver success alone. Section 8.5 Table 8.13 confirms the named Column 1 and Column 2 mappings. See [manual](https://docs.tuflow.com/classic-hpc/manual/2026.3/07-Boundaries-and-Initial-Conditions.html).

## Rounded OUT clocks and retained report extension

The second hosted quality attempt at `291ee1595b1da43e6e0f588c6f3887c5ffc17c11` ([run](https://github.com/Chain-Frost/pyrorb/actions/runs/46108689397)) stopped at two RUF043 regex-intent findings; the follow-up fixes both without changing lint policy.

A targeted inspection of eleven public CMD objects across short, long, wet-start, dry-end and multi-subarea cases found nine with fully consistent printed clocks and two with a header of 0.12 h but cumulative labels 0.12, 0.25, 0.38, 0.50, etc. The existing register binds both to 0.125 h STM inputs; their matching raw STM records were inspected. The exact clock is not identifiable from the rounded header alone.

| Register case | Report SHA-256 prefix | STM SHA-256 prefix | Rainfall intervals | Gross A first / last / sum (mm) | Finish with source step (h) |
| --- | --- | --- | ---: | --- | ---: |
| H3-single-source-equality-chain | 437bd8d0 | e1d037f8 | 5 | 3 / 7 / 13 | 0.625 |
| timestep-design-baseline-f4 | 1507a183 | edd936af | 96 | 1 / 1 / 96 | 12 |

Default report-only refusal is preserved. An explicit caller-known exact source timestep is admitted only if it lies within the printed header resolution and agrees with a complete OUT clock covering the rainfall horizon and every printed time label. Both reported and selected values and the clock basis are returned. No external file is discovered or automatically read by the converter; the caller owns source association. Two retained-report tests cover default refusal, wrong supplied steps and the independently known 0.125 h option. Fresh exact-head execution is pending.

## Native-layout follow-up and current-main reconciliation

The [previous hosted run](https://github.com/Chain-Frost/pyrorb/actions/runs/46112045768) at `4da13d2c9dcb07200fc90d3100efbf1dba64d430` passed repository hygiene, Ruff lint and formatting, and strict Pyright (zero errors/warnings). Pytest ran 1852 cases: 1848 passed, three POSIX-only skips, one failure due to a too-broad test replacement corrupting two sections and expecting the wrong refusal diagnostic. The converter refused the malformed file. The corrected test removes only the intended complete interior row; no acceptance condition or unrelated test is relaxed. Wheel/regression workflow steps after the failed quality command did not run.

The [fresh RORBwin 6.52 report comparison](https://github.com/Chain-Frost/pyrorb/pull/253#issuecomment-7239193027) and [paired native receipt](https://github.com/Chain-Frost/ryan-tools/issues/349#issuecomment-7239183411) exposed two further layouts: uniform direct-depth reports have only a Time/Catch series, and both direct and weighted five-minute reports can print the catchment total directly adjacent to the Tot. marker, e.g. Tot.105.0. The canonical reader now recognises the explicit uniform catchment-only header and the compact total prefix. It does not synthesize subarea identities or assume physical mappings. New artificial cases exercise the reported grammar, both compact and separated totals, a caller-known 0.08333333333 h source step, exact printed increments and refusals. Native source files and full native captures remain in local custody; the artificial fixtures are not copies of those reports. Replay the two actual OUT files on the revised head before declaring those layouts native-qualified.

Reconcile with current main `175feac7b525e96eb7be1750f16926ef6d270e50` (merged #252, direct-depth STM #250); preserve its codec/model/tests and work-index entry, as well as the existing export workflow and source bytes. #251 remains a separate open calibration-fragment change; no merge or publication performed. Fresh combined-head CI and independent review remain required. Native TUFLOW consumption remains pending and the literal delayed-start control is in [issue #249](https://github.com/Chain-Frost/pyrorb/issues/249#issuecomment-7234680895).
