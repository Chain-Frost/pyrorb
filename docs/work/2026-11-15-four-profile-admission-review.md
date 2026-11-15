# Four original CMD feature profiles — separately reviewable admission decision

Status: **bounded diagnostic study, no numeric/reference admission**. Candidate base: evidence PR [#133](https://github.com/Chain-Frost/python-runoff-routing/pull/133), reconciled at `2acaebb126e9f0a81e1272ea6b41c838f6540368` with main `0675d75b05dba7728b389fdd8af743060b4469b2`. Tracks #5 / #90 / #92 / #96. This record does not replace the existing programme matrix, runner or scalar policy.

## Decision and evidence threshold

All four source/report triplets and original case/manifest/index lineage were authenticated in #133. They retain **`coverage: gap`**, native-gaps membership and unassessed `python-cmd` numeric expectations. The unchanged existing `cmd_public_probe.py` uses the maintained S1 decoders, public `python-cmd/cmd-6.44` engine and `compare_fresh_cmd_case`; the focused regression test added on this branch runs the **four cases directly** through that existing implementation. It is executed as part of both normal source pytest and the **out-of-checkout installed-wheel pytest** in the existing Windows/Python 3.13 quality workflow. Neither the CLI's frozen 50 CMD eligible selection nor its baseline 36/50 gates are altered.

The test requires source/executable profile identity, original triplet hashes, one unique terminal code-7 to Hyd001 association, all **301 original Q rows**, frozen printed interval comparison with zero mismatches, separate **0..150 h generated elapsed times** versus the original **Inc 1..301, raw Time 0.50..150.50 h**, and no numeric-reference promotion. Crucially `_fresh_cmd_reporting_metrics` must return `incomplete: Original native scalar binding is unavailable`: the original `scalar_binding` selector/typed source-to-stored h/dt/physical-site evidence has **not** been independently admitted, even though the prior #113-era direct scalar diagnostic passed.

## Exact profile dispositions

| Case | Native original / effective profile | Prior #113 source/wheel diagnostic | Present admission verdict |
| --- | --- | --- | --- |
| `fig67-ilroc` | CMD 6.44 flag 2 IL 20 mm/RoC 0.5; kc=10, m=0.8; peak 122.662 m³/s at raw 37.00 h | 301/301 Q pass, three **direct** scalars pass at historical `ef8cb9a`; peak error -0.000053889%; Q max error 0.000406664% of native peak | **Pending** original registered scalar/site identity; do not equate initial-loss/runoff coefficient to ordinary IL/CL |
| `fig67-kc5-m1` | CMD 6.44 kc=5, m=1; peak 155.494 m³/s at raw 37.50 h | 301/301 Q and three direct scalars pass; signed peak 0.000041372%; Q max error 0.000319988% | **Pending** original registered scalar/site identity and exact current-source/wheel result |
| `failure-m-above-one` | CMD 6.44 m=1.001; **successful native run**, peak 96.3044 m³/s at raw 39.50 h | 301/301 Q and direct scalars pass; signed peak -0.000002510%; Q max error 0.000051686% | **Pending** independently qualified scalar/site evidence; filename does **not** imply rejection |
| `failure-m-below-one` | CMD 6.44 m=0.999; **successful native run**, peak 96.9917 m³/s at raw 39.50 h | 301/301 Q and direct scalars pass; signed peak 0.000014927%; Q max error 0.000051525% | **Pending** original registered scalar/site binding; filename does **not** imply rejection |

The earlier **personally executed Windows/Python 3.14.6** feature-source and externally installed-wheel outputs at `ef8cb9afaa00476db26e0eb10fcbd4eda3f4a632`, including complete full-series binary64 ordinates, remain at `docs/work/2026-11-15-native-closeout/feature-{source,wheel}.json`. They are not presented as execution on current main. Source/wheel outcome equality on the new head must be separately confirmed; performing the same bounded **pass/fail Q check** from each import environment is necessary but is not by itself a byte-for-byte output equality receipt.

## Distinct volume and clock evidence

| Profile | Original native-inclusive reported sum (m³) | Original physical trapezoid of printed Q centres (m³) |
| --- | ---: | ---: |
| `fig67-ilroc` | 3,879,306.000 | 3,879,304.200 |
| `fig67-kc5-m1` | 5,217,157.800 | 5,217,157.800 |
| `failure-m-above-one` | 5,214,701.340 | 5,214,701.340 |
| `failure-m-below-one` | 5,219,603.820 | 5,219,603.820 |

These are independent original-report-table-derived quantities, **not** reconstructed hidden-state CMD conservation truth. Printed Q, original summary peak, original raw peak time, native-inclusive reported volume and quantised-Q trapezoidal volume remain separate; no tolerance or original reference changed. A direct scalar diagnostic at the old tested head does not provide the independently reviewed registered `scalar_binding` currently needed to make those metrics first-class acceptance results.

## Other original captures and next actions

`failure-zero-reach`, `failure-negative-reach` and `failure-negative-reach-repeat` produced complete original native Q but remain typed/physical-site/scientific applicability gaps with #92. The `fig67-code11` original has five distinct 301-row columns, yet typed diagnostic and print meanings remain with #91 / C/#96. Nothing in this review changes any of the eight original gap statuses. The 2,818-byte LF PyRomb PR16 export and historical 2,913-byte CRLF file remain separate preserved source objects without any new native execution.

**To admit a profile:** B owner must independently bind/select the original native report peak/peak-time/volume selectors, verified source-to-stored CMD h/dt, and defensible original physical-site identity in the *existing* register, then execute and inspect the full existing comparator on current source plus truly isolated installed wheel. If any of those remain uncertain, retain an explicitly narrower source/Q-only decision rather than asserting full equivalence. No code-11, nonpositive-reach, wider PyRomb or complete-CMD release gate is delegated to this PR.
