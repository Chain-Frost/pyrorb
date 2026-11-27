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
