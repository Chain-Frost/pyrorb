# Source-preserving combined pre-burst engineering execution (#90/#92)

Base `9a9b45c02204b75f95c87ef250014f6479a73187`. Separate implementation slice following the independently
calculated four-profile evidence in #235/#237. The original 102.10% STM has
48 pre-burst bins totalling 2.10 and 24 design-burst bins totalling 100.00;
all source depths are 69.02 mm. Existing evidence discriminates division by
102.10 from unnormalized division by 100 in the retained printed rainfall.
The typed model and source parser already preserve this distinct basis and split.

## Change

- Carry the typed `combined_preburst_percent` basis, pre-burst split and
  original weights across the existing S2 payload into the independent storm
  kernel. Do not recast as ordinary percentages or relative-weight source.
- Validate the split and burst total at the numerical boundary. Reuse the
  existing dimensionless scaled-ratio calculation over the **complete event
  depth**, preserving source ratios, with the existing Decimal-to-float
  proportion guard. Initial loss carries through pre-burst into burst.
- Keep existing IL/CL and IL/RoC, geometry, reach routing, timestep, output
  identities and ordinary percent/relative-weight calculations. No compatible
  CMD arithmetic, native adapter, persisted schema, register, reference,
  tolerance or temporary default changes.

## Verification and qualification

Independent authored controls cover exact pre-burst/burst allocation, initial
loss crossing, both loss models, and invalid split/burst/ordinary basis.
The previously rejected authored combined-storm case and eight retained
same-STM original triplets now require independent execution without a
source rewrite. The four specifically selected original cases
`fig67-ilroc`, `fig67-kc5-m1`, `failure-m-above-one`,
`failure-m-below-one` use the maintained probe, canonical report/scalar
reader, compatible comparator and `assess_cmd_deviation`. The existing
public scalar test group executes them in source and isolated-wheel CI.
Tests require exact source hashes, complete 301-row clocks/terminal print,
compatible printed-Q and direct report-local scalar diagnostics, and explicit
engineering selection. They emit complete candidate Q hex arrays, model and
source/artifact identities, raw versus elapsed peak times, separate native
inclusive volume token, and absolute/CMD-relative peak, max/RMS Q and
trapezoid deviation metrics. Zero denominators use the helper's undefined rule.

The unique terminal code-7 and the original single Hyd001 report column
establish a computational-outlet association; the native physical label is
still unverified. The direct scalar diagnostic does not create a registered
binding or extend the frozen nominal-m=0.8 scalar population. Engineering
differences are diagnostics, not threshold-based qualification, conservation
or proof of a native defect. All four retain gap membership and the
original 85/50/21 population. Other #92 reach cases and #91 code 11 are separate.

Exact-head validation and independent review are pending. Reuse the existing
PR3.11/main3.11+3.14 quality workflow. The remote tool cannot supply a local
full checkout in this session; do not equate source inspection with a
successful local test run. No native executable required or launched.

Matrix and earlier evidence consolidation remain owned by #235. Coordinate
the nearby S2 codec changes with #240 and update the one feature matrix only
after evidence/acceptance review. No issue closure, merge or publication.

## 28 November — independent executed source-kernel calculations

Executed locally with Linux/CPython 3.13.5 in an isolated temporary
directory. Full repository retrieval was blocked by DNS; the three
exact numerical module texts were copied from the GitHub connector and
verified with `git hash-object` against the feature head
`276a2ce86a7540ee3b485bf394a665797fe7b40f`:

| Module | Verified Git blob |
| --- | --- |
| single_storm.py | `fd85a0e9219c3d0c76da0cece812a6e5dfc4652c` |
| reach_routing.py | `fd384df244c0b7c0a052577eb9115ae395f7f161` |
| cmd_deviation.py | `efda5132f97a26188b02b058f49aed4b6e847ff8` |

The numerical kernel imports only the source model's three-value
`PatternBasis` enum; its exact definition was extracted, not the full
typed parser. This is **kernel execution**, not a full-package checkout,
project/API execution or installed-wheel qualification. No replacement
solver was written. The 18 ordered control steps, nine reach lengths,
five areas, pervious fractions, loss flag/parameters, 72 original weights,
69.02 mm depths and 300 increments were transcribed from reauthenticated
published CATG/STM/PAR bytes. Connector text's original single-byte
encoding was reversed; all source/report SHA-256 and sizes matched
the maintained index before extraction. Weight-token vector SHA-256
(join original tokens with one ASCII space):
`4a88156a1287955e90d9bbdf75c67557705eb0acd32506b3107a46860d860a03`.
The original 301-row Q tokens were extracted in order from each report,
their 1..301 original Inc/Time grid checked, and the space-joined Q-token
vectors hash-verified after transfer into the local environment. The
complete calculated Q arrays were compared using the exact existing
`assess_cmd_deviation`; prepared and fresh execution agreed exactly.

| Case | Original Q token-vector SHA-256 | Calculated Q float.hex vector SHA-256 |
| --- | --- | --- |
| fig67-ilroc | `3d1498d6894cfed28d37bc3d0e84cd743e4a7e3d083ce63618751589cf76786a` | `02c0a15bb5ee933a43b08ff409d74158f10e5029a47ebd7cdc7b562f972599b3` |
| fig67-kc5-m1 | `02ed2b560969d311fd30a923911d7f1cc92c73457e198b9dab16e02b3dfb29d2` | `8724a9791f3c3681c9b5ac506283991dc74441264ddc20337ad0659b0a797666` |
| failure-m-above-one | `1eb99075e8568a484c0983055794e9fd6902d54e145092e7d35be36b8b6c5c37` | `49ae36bf017e2e3104cbf6a0a389cb20f403797d6fd5db85a330a64f8a5fcdf9` |
| failure-m-below-one | `bf49f3d1e0e2d59405b64b9922234ff9ecd51f5d67459594911046a284f9b835` | `e099a8daa530572439ab1713f636b0913db71895aeeee0f6bb58d40c0caccee5` |

The hash of a calculated vector is SHA-256 of its 301 canonical
float.hex strings joined by one ASCII space, no trailing newline.
All four produce 301 nonnegative finite values and the same native
peak index (73, 74, 78, 78). Average path distance is 8.984177215189874 km;
computed excess is 24.51 mm (IL/RoC) and 33.02 mm (IL/CL) for each source,
consistent with the independently derived source calculation.

| Case | CMD peak | Engineering peak | Signed peak error (m³/s) | Signed peak error (%) | Max Q error (m³/s / % of CMD peak) | RMS Q error (m³/s / % of CMD peak) |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| fig67-ilroc | 122.6620 | 122.616883 | -0.045117 | -0.036781323 | 0.068745270 / 0.056044472 | 0.024166043 / 0.019701328 |
| fig67-kc5-m1 | 155.4940 | 155.494080 | +0.000080 | +0.000051557 | 0.000497562 / 0.000319988 | 0.000156744 / 0.000100804 |
| failure-m-above-one | 96.3044 | 96.335746 | +0.031346 | +0.032549149 | 0.033459663 / 0.034743650 | 0.010331621 / 0.010728089 |
| failure-m-below-one | 96.9917 | 96.960484 | -0.031216 | -0.032184168 | 0.033490939 / 0.034529696 | 0.010298530 / 0.010617949 |

| Case | Native raw / both elapsed peak h | Native printed-Q trapezoid (m³) | Engineering trapezoid (m³) | Signed volume error (m³ / %) | Original inclusive summary token (m³) |
| --- | --- | ---: | ---: | --- | --- |
| fig67-ilroc | 37.0 / 36.5 | 3,879,304.20 | 3,872,412.106685 | -6,892.093315 / -0.177663131 | 3.88E+06 |
| fig67-kc5-m1 | 37.5 / 37.0 | 5,217,157.80 | 5,217,160.000000 | +2.200000 / +0.000042169 | 5.22E+06 |
| failure-m-above-one | 39.5 / 39.0 | 5,214,701.34 | 5,217,159.995042 | +2,458.655042 / +0.047148530 | 5.21E+06 |
| failure-m-below-one | 39.5 / 39.0 | 5,219,603.82 | 5,217,159.993427 | -2,443.826573 / -0.046820155 | 5.22E+06 |

Absolute peak/volume errors are the magnitudes of the signed columns.
The linear m=1 differences are on the scale of printed-Q precision;
nonlinear differences are measured, not assigned a post hoc acceptance
budget. No native defect, hidden-state conservation or independently
observed physical-name claim follows. Formal Q/scalar register
admission remains open. The complete package test will independently
verify the typed-source path, both explicitly selected engines,
report-local scalar adapter, full arrays, and isolated wheel identity.

The exact proposed `tests/test_single_storm.py` blob
`4088f2b993f4aa2fa5ca751eb84dc306f3e4cab4` was also copied and hash-
verified; **28 passed**, including the ten new controls, in the same
extracted kernel environment. No full repository tests claimed locally.
Initial hosted quality run [46040598666](https://github.com/Chain-Frost/pyrorb/actions/runs/46040598666)
passed repository hygiene but failed on one I001 import formatting
finding in the new scalar test. Fix the import and function formatting
without numerical changes. Main advanced through the consolidated
documentation PR #235 only; the integration retains those docs and
unchanged source/fixtures. The new exact-head CI is required for the
full adapter/installed-wheel receipts.

## Independent boundary review and uncertainty assessment

[Review finding](https://github.com/Chain-Frost/pyrorb/pull/242#discussion_r4722145334)
at `6076ca760647ccf064036fe39cd2c08a7f39210b`: valid inclusive Decimal burst totals of 99.95
(0.07 + 99.88) and 100.05 (0.01 + 100.04) can round to the adjacent
binary64 values 99.94999999999999 and 100.05000000000001. Personally
reproduced both with Linux/Python 3.13.5 and math.fsum. A strict comparison
against the binary64 endpoint constants rejects them. The proposed fix
uses math.nextafter toward the outside once per endpoint; the original
Decimal S1 tolerance is unchanged. Independently verified both example
endpoints and rejection of 99.949999999999 / 100.050000000001. The kernel
test also checks rejection two binary64 steps outside the original
bounds. New typed-path and direct-kernel controls require exact-head
CI. This changes validation only, not the storm shares, routing,
losses or comparator; the retained 100.00 burst is interior to the
bounds. On the preceding head the Windows/Python 3.11 strict local
quality step (repository checks, Ruff, strict Pyright and non-native
pytest) passed in [46041301565](https://github.com/Chain-Frost/pyrorb/actions/runs/46041301565).
Do not transfer that receipt to the new head or claim the new wheel
until it completes.

### Reference-printing uncertainty versus engineering deviations

Using the executed kernel receipt above and the exact native Q intervals
in [the four-profile record](2026-11-15-four-profile-admission-review.md),
propagate original display uncertainty, not a new engineering threshold.
Peak bounds below are engineering peak minus the native peak interval
endpoints. Max-error lower bound is max(0, observed max error minus one
native half-last-place unit), using the uniform native Q precision
(0.001 m³/s for the first two profiles, 0.0001 m³/s for the last two).
The signed trapezoid difference range subtracts the native upper/lower
trapezoid bounds from the engineering trapezoid. Values below are
rounded from the recorded kernel results.

| Case | Peak difference range (m³/s) | Minimum possible max-Q difference (m³/s) | Signed trapezoid difference range (m³) |
| --- | --- | ---: | --- |
| fig67-ilroc | -0.045617 to -0.044617 | 0.068245 | -7,162.093 to -6,672.943 |
| fig67-kc5-m1 | -0.000420 to +0.000580 | 0 | -267.800 to +83.200 |
| failure-m-above-one | +0.031296 to +0.031396 | 0.033410 | +2,431.655 to +2,475.485 |
| failure-m-below-one | -0.031266 to -0.031166 | 0.033441 | -2,470.827 to -2,426.907 |

For the linear m=1 calculation, the reported max Q difference
(0.000497562 m³/s) is below 0.0005 m³/s, so every computed ordinate is
consistent with original native printed precision, and peak and volume
differences are not distinguishable from original print rounding.
For the three nonlinear cases the observed differences cannot be
explained by original printed-Q rounding alone. This does not identify
a particular native defect or justify accepting a different numerical
method; the native hidden storage/source states and independent physical
site remain unqualified. Do not assign an acceptance budget after seeing
these differences. The four registered gap dispositions stay unchanged.
No native run occurred.

The single matrix now records the bounded #242 **candidate** execution
for the eight same-storm imports and four original diagnostic profiles.
The full exact-head source/wheel and independent review receipts remain
required before merge; no Q promotion or broader engine qualification.
