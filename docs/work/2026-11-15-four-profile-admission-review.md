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

## 25 November 2026 — current-main source and reporting-field qualification

This dated follow-up supersedes the earlier pending *evidence inspection*, not its non-admission
decision. Audit base `b6788a83fbe5eb9ccd68232fe8d92dfb596e0f6b`, tree
`5f3d6cd02e0d486df03379d5e91eb1786b418ff6`. No open PRs at the ownership checks;
A/#90 and #92 retain feature qualification, #91 retains physical/diagnostic-site ownership,
B/#100/#135 retains the single comparator, and the programme editor retains #5/STATUS.
No register, comparator, solver, reference, policy or default edits are proposed.

### Immutable source and computational site

Independently rechecked the register-pinned public native index (53,400 bytes, SHA-256
`0a132bb113f704b7d4d863336ff442e21da3556a1ada87f514ea4b8c1e7597d3`).
All 14 distinct indexed objects used by the four cases (one CATG, one STM, four PAR,
four OUT, four capture manifests; 20 per-case bindings) match their registered and indexed
SHA-256 and size. The remote text interface re-encoded the shared STM and four OUT files;
reversing the observed single-byte superscript characters recovered the exact indexed hashes
and sizes. This is a byte authentication of the published objects, not a new private original
capture or a full-index checkout run. Original-to-public path-only derivatives retain the
independently reviewed #133 custody lineage. The original generator revision is still unknown.

The shared Figure 6.7 CATG is 6,787 bytes, SHA-256
`5ca232d0ac52719458b39582f28b2634012325329345816f3b4daf74140bba07`;
the published STM is 1,310 bytes, SHA-256
`4371d9e952d3ba6ea9cd7b226c2f2b19a9998bce4186aab83cf61de91a9ccc3b`.
The original computational source order is A, B, C, E, D, areas 30, 28, 25, 35, 40 km²
(total 158 km²), no impervious areas; all nine natural reach lengths positive.
The controls are 1,3,1,4,5,3,1,4,5,3,1,4,5,3,1,4,5,7, with a single terminal
code-7 after reach 9. The graphical source has outlet node 10, print flag 70.
The original native report data check says code no. 18, 7.0, with the location read
as blank; its only legend is 01 Calculated hydrograph, and its table is Hyd001.
This establishes source-derived terminal `print_1` ↔ `Hyd001` computational
association, **not independently observed native physical node 10 ↔ Hyd001**.
The report's blank location cannot be filled from the graphic, inferred from the
hydrograph shape or relabelled as an authenticated physical-site observation.

The exact supplied DESIGN STM specifies h=0.50000 h, 300 calculation increments,
one burst/gauge/ISA, rainfall start 0/finish 72, five depths 69.02 mm; preserve its
raw temporal-weight tokens and the existing parser basis (no regeneration or normalization).
The descriptive 12-hour storm title does not shorten the retained calculation horizon.
The PAR controls specify lumped kc, verbosity 3 and one ISA/burst:

| Case | Loss flag / exact parameters | Native rounded parameter echo |
| --- | --- | --- |
| `fig67-ilroc` | 2; kc=10, m=0.8, IL=20 mm, RoC=0.5 dimensionless | kc 10.00, m 0.80; runoff-coefficient model selected |
| `fig67-kc5-m1` | 1; kc=5, m=1, IL=20 mm, CL=2 mm/h | kc 5.00, m 1.00 |
| `failure-m-above-one` | 1; kc=10, m=1.001, IL=20 mm, CL=2 mm/h | kc 10.00, m 1.00 |
| `failure-m-below-one` | 1; kc=10, m=0.999, IL=20 mm, CL=2 mm/h | kc 10.00, m 1.00 |

The two boundary reports round m to 1.00; exact exponents are authenticated PAR
values, not higher-precision native state inferred from that echo. All four are
successful original CMD 6.44 complete-table captures. The two failure names are
historical IDs, not native rejections.

### Original clock and scalar selectors

Each Hyd001 table has 301 contiguous rows, Inc 1–301, raw Time 0.50–150.50 h.
The separately defined elapsed calculation grid is 0–150 h (300 intervals).
The source-derived stored-clock candidate is h=0x1.0000000000000p-1 h and
dt=0x1.c200000000000p+10 s (1800 s), exactly representable using the existing
binary32 h/dt derivation; this does not assert an independent native memory observation.
No table shift or interpolation is made. The original scalar selectors are the same
in all four reports: line 391, character 26, ordinal 1, m3/s (peak);
line 392, character 27, ordinal 1, h (peak time); line 393, character 23,
ordinal 1, m3 (volume). Lines and character offsets are one-based.

| Case | Printed Q max (m³/s) / Inc / raw h | Original summary peak / time (h) / volume (m³), literal tokens | Inclusive printed-Q sum (m³) | Trapezoid of printed Q (m³) |
| --- | --- | --- | ---: | ---: |
| `fig67-ilroc` | 122.662 / 74 / 37.00 | 122.7 / 36.5 / 3.88E+06 | 3,879,306.00 | 3,879,304.20 |
| `fig67-kc5-m1` | 155.494 / 75 / 37.50 | 155.5 / 37.0 / 5.22E+06 | 5,217,157.80 | 5,217,157.80 |
| `failure-m-above-one` | 96.3044 / 79 / 39.50 | 96.30 / 39.0 / 5.21E+06 | 5,214,701.34 | 5,214,701.34 |
| `failure-m-below-one` | 96.9917 / 79 / 39.50 | 96.99 / 39.0 / 5.22E+06 | 5,219,603.82 | 5,219,603.82 |

All four printed maxima are unique; the raw increment minus one gives the
corresponding elapsed peak index and summary peak time. Printed-table peak and
inclusive sum are consistent with their rounded summary tokens. The last printed
mode-2 ordinate is 0.002 m³/s, not zero; its inclusive minus trapezoidal volume
is 1.80 m³. The other three have printed zero endpoints. Inclusive volume is
1800 × sum(Q[0..300]); the physical-horizon statistic is 1800 ×
(Q[0]/2 + sum(Q[1..299]) + Q[300]/2). These are quantized-table statistics,
not independently observed hidden storage/conservation values. They are not
a current registered scalar-comparison pass. Keep the original summary tokens
rather than replacing them with table-derived precision.

### Reuse current exact-main execution evidence

Audited [main push quality run 45604248310](https://github.com/Chain-Frost/pyrorb/actions/runs/45604248310):
exact head `b6788a83fbe5eb9ccd68232fe8d92dfb596e0f6b`, success on Windows/Python 3.11 and 3.14.
The [Python 3.14 job](https://github.com/Chain-Frost/pyrorb/actions/runs/45604248310/job/139170838147)
used Python 3.14.10, strict Pyright zero diagnostics, 1,705 source tests passed
(13 skips) and 231 installed-wheel tests in the public regression test group.
The unchanged `tests/test_regression_public_native.py::test_original_feature_profile_q_study_retains_unadmitted_scalar_status`
is parameterized over exactly these four cases and runs the existing probe
`_one` from source and from the installed wheel. The job ran that test file in
both environments. Thus the four 301/301 printed-Q assertions and the four
explicit scalar-incomplete assertions passed on this base; 1,204 Q rows remain
outside the original 50 eligible cases. This is a hosted-log audit, not a personal
engine execution or a new native run.

The installed import was
`D:\\a\\_temp\\runoff-wheel-smoke\\runoff_routing\\__init__.py`;
wheel SHA-256
`dc07552e4d5d843db0aecb501e8f95bd785fcd16ccc7217bb9bde789d48dc238`.
The isolated-wheel import/artifact guard and maintained full-index preflight
succeeded. Compared the two complete fresh 50-case JSON result arrays in the
job log, not just totals: identical, package fingerprint
`package-code-v1-sha256:2c920e35b76494a1dd6108f8c1bc6e1ad289ab2b642e246d3ef41ff73499efdf`,
50 printed passes / 19,550 ordinates, 48 reporting passes and two zero-flow
time incompletes. The four additional tests establish the same Q pass/fail
assertions in both environments; they do not emit paired full four-case Q arrays
or prove bit-identical internal values. Preserve historical `ef8cb9a` direct
scalar diagnostics as historical only.

### Finite admission decisions

| Case | Source/computational Q | Registered reporting scalars | Physical/engineering and register disposition |
| --- | --- | --- | --- |
| `fig67-ilroc` | Source/clock/selector observation qualified; current-base compatible printed Q 301/301 | Incomplete: no independent scalar/source binding | Physical Hyd001 unverified; explicit engineering CMD-relative deviations not run/qualified; retain gap |
| `fig67-kc5-m1` | Same; 301/301 printed Q, successful native m=1 | Incomplete; no independent binding or approved exponent extension of scalar-policy scope | Physical Hyd001 unverified; engineering deviation not run/qualified; retain gap |
| `failure-m-above-one` | Same; 301/301 printed Q, successful native m=1.001 | Incomplete; same scope/binding limitation | Physical Hyd001 unverified; engineering deviation not run/qualified; retain gap |
| `failure-m-below-one` | Same; 301/301 printed Q, successful native m=0.999 | Incomplete; same scope/binding limitation | Physical Hyd001 unverified; engineering deviation not run/qualified; retain gap |

The frozen `scalar-policy.md` explicitly limits its selected gate to the original
50 nominal-m=.8 profiles and excludes other exponents. B must independently
approve any new scope/bindings without altering the interval, clock or volume
rules. The existing probe test explicitly asserts no `scalar_binding` on these
four. Do not add one simply because the selectors can be located. In particular
the `cmd_deviation.assess_cmd_deviation` contract requires independent matching
of physical site, effective rainfall and clock; the existing #96 deviation test
requires authenticated physical identity. Do not bypass that condition or present
historical compatible-engine metrics as `python/engineering-v1` deviations.
Where a physical binding is independently established, use that existing
helper and maintained source/output paths to report full Q max/RMS absolute
and CMD-peak-relative errors, signed/absolute peak and trapezoidal-volume
differences, peak index/time offsets and the raw inclusive volume token separately.
Zero reference denominators remain undefined. No new engineering threshold.

**Next finite handoff:** B/#100/#135 and #91 independently review the selectors,
source binding, physical site and policy scope with A/#90/#92. First inspect
the authenticated original manifests, existing #133 custody ledger and any
retained independent source-to-native site observation. A rerun of the same
unlabelled report cannot establish missing physical-site evidence. If no such
observation exists, record explicit incomplete; only a necessary predeclared
#5 observation (exact source hashes, pinned executable hash, single observable
and stop condition) may use the standing local permission. No native launch
is required for the present document-only finding. Do not broaden to the
`failure-zero-reach`, `failure-negative-reach`, `failure-negative-reach-repeat`
cases: these are separately unresolved typed/physical #92 gaps with complete
native tables, not proof of rejection; the two negative captures share Q and
clock but differ in parameter identity. Invalid/omitted reach or other domain
claims are not established by this four-profile study. #91 code-11 remains separate.

All 85 case records, 50 CMD-eligible cases, 21 native gaps and eight preserved
gap classifications remain unchanged. No claim of registered scalar/physical
admission, independent engineering accuracy, full CMD closure or publication.
