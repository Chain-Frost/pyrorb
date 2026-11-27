# Issue #192: ARR2019 ARF — archived RORBwin precision qualification

25 November 2026. Parent [#8](https://github.com/Chain-Frost/pyrorb/issues/8).
Public starting main: `b6788a83fbe5eb9ccd68232fe8d92dfb596e0f6b`.
Scope: read-only retained evidence and independent numerical controls. No native
experiment, production arithmetic, preparation profile, existing test expectation,
fixture, golden, release or routing change. Independent scientific review pending.

## Source register and admission

| Source | Identity and use |
| --- | --- |
| Published method | Ball et al. (eds), ARR 2019, Book 2 v4.1, Chapter 4, Table 2.4.1, equations 2.4.1–2.4.4 (p. 64), Table 2.4.2 (pp. 65–66); [primary PDF](https://www.arr-software.org/pdfs/ARR_190514_Book2_V4.1.pdf). © Commonwealth of Australia (Geoscience Australia) 2019, CC BY 4.0. Chapter 6 worked example 2 is an additional published control. Text extraction inspected directly; PDF page-image fetch exceeded service size limit. |
| Independent script precedent | [Ladson ARF2019.R (2020)](https://gist.github.com/TonyLadson/fc870cf7ebfe39ea3d1a812bcc53c8fb), SW WA e = 3.845E-06; secondary implementation, not a replacement for the table or proof of every legacy export's contents. |
| Authenticated original archive | [#137 preflight](2026-11-15-issue137-independent-rorbwin-preflight.md) and [execution](2026-11-15-issue137-actual-execution.md); original private source revision `f1377860b5678c80ac9972b1a157aad0e08c38fe`, retained investigations main `345b0b00318a663b9c70c2fe421d1c2c283387ef`. Prior independently checked 224/224 archive-relative files (187 primary + 37 repeat). Native build 6.52, 1 June 2023; executable identity recorded in original manifest, not newly rehashed. |
| Written-input contract | [#175 / #177 receipt](2026-11-16-issue175-written-rainfall.md) and [prior independent audit](https://github.com/Chain-Frost/runoff-routing-investigations/pull/88). Immutable private per-event receipts checked read-only, not a new engine replay. |
| Controlled sensitivity | [R1](2026-11-14-s6-r0-timing-r1-arf.md), [N1–N3](2026-11-14-s6-n123-native-precision.md), [N4](2026-11-14-s6-n4-native-result.md), [completion audit](2026-11-14-s6-n4-completion-review.md). Same native build, 100 km², 24 h/1%, 129 mm, areal bin 100, original EventID 9091, ordinal 1, 24 one-hour increments; zero IL/CL. Controlled synthetic TXT coefficients, not three authentic Data Hub exports. |

The two #137 archives retain original BoM IFD, ARR TXT, areal TP CSV, CATG,
saved PAR, STM/OUT/CSV and manifests under **local-only** custody. The primary
60-member archive uses one 158 km² catchment ARF across five subareas, SW WA
long-duration parameters and S-SW Flatlands (West) areal pattern bin 200 km².
The original retained TXT [LONGARF] was inspected directly at the pinned
private revision: version 2016_v1, SW WA, all nine values equal the published
table in this capture. Specifically, e = 3.85E-06, not the script's 3.845E-06.
Do not label the latter as this archive's source coefficient. Short-duration
equation is nationwide and does not use the long-duration coefficient set.
Native comments identify ARR2016; these observations are compared to published
ARR2019 arithmetic, not proof of the internal native method/version.

Published SW WA a–i: 0.183, 0.259, 0.271, 0.33, 3.85E-06, 0.41, 0.55,
0.00817, −0.00045. East Coast North a–i: 0.327, 0.241, 0.448, 0.36,
0.00096, 0.48, −0.21, 0.012, −0.0013. Keep origin and input bytes distinct;
do not use a rounded saved-PAR coefficient cache to reconstruct the source.
The separate [#193 method review](2026-11-17-issue193-arr2026-arf-method.md)
owns 2026 applicability, not this qualification.

The [anonymised site audit](2026-11-19-anonymised-site-validation.md) and
[fifth-set audit](2026-11-19-anonymised-site-e-validation.md) are corroborating
diagnostics only: historical effective areas, versions/source association,
filtering and non-uniform rainfall are not completely established. Ten exact
written-depth matches after using unrounded CATG area demonstrate area
sensitivity; no additional region is admitted to native ARF qualification
from those client records. No original files, source vectors, private paths
or manifests have been reproduced here.

## Predeclared finite comparisons and precision

Before evaluating the independent arithmetic, select:
six native cells (158 km², 720/1080/1440 minutes × 5/2% AEP; ten patterns each);
the 24 h/5% repeat only as a cross-check; the existing R1/N1–N4 100 km²
24 h/1% sensitivity observations; fifteen analytical controls with synthetic
100 mm gross depth (below); and the published East Coast North worked example.
No extrapolation outside the calibrated 30-minute–7-day, 1–50% probability
domain or unsupported area-duration combinations. Native labels are ordinal,
not EventID; bind duration, AEP, EventID, timestep and source order jointly.

Use area km², duration minutes, p = AEP percent / 100. Eq. 2.4.1 is used up
to 720 min, eq. 2.4.2 from 1440 min, linear duration interpolation between.
Area ≤1 km² is unity; 1 < area < 10 uses eq. 2.4.4 from the 10 km² value.
The published cap is 1. Gross areal depth is D × ARF, without intermediate
rounding. One catchment-wide ARF is the approved bounded compatibility
behaviour; this is not multi-outlet design certification.

Comparison intervals are defined by representation, not fitted:
- **Unrounded arithmetic:** independently evaluate published equations with
  60-digit Decimal using exp(ln(x) × exponent) and an ordinary binary64
  expression with separate grouping. Existing independent float checks use
  1e-11 absolute ARF; retain that check. New fixed analytical factors are
  recorded to 12 decimal places; their half-unit representation is 5e-13.
  They are not native observations.
- **Printed ARF and adjusted depth:** native two-decimal tokens imply
  closed half-unit intervals ±0.005 dimensionless and ±0.005 mm respectively
  for nearest rounding; tie mode is not identified. Compare against the
  unrounded calculation using exact retained BoM source depth (not a
  separately rounded ARF). If only rounded gross depth G were available,
  its half-unit uncertainty must propagate through ARF before the depth
  comparison. Here source depths are bound by the prior authenticated audit.
- **Written STM:** two-decimal total and source two-decimal percentage
  tokens are represented exactly as decimals. The written-input mathematical
  increment is written total × original percent / 100; no per-bin rounding
  or invented internal effective precision. Compare #175 prepared increments
  exactly; compare unrounded published versus written increments separately.
  With identical weights the representation bound for each difference is
  0.005 × weight/100 mm. The separate 0.1-mm native rainfall report uses
  ±0.05 mm. Do not combine these into a permissive native-excess tolerance.
- **Native internal ARF/effective rainfall:** not observable at full precision
  from these captures. R1/N4 strict excess comparisons retain the previously
  frozen 0.0000018 mm absolute allowance; no new precision claim follows
  from a rounded STM or a successful written-input replay.

Verdicts: accepted for the specifically tested arithmetic or exact written
representation; precision-limited for observed display agreement; failed for
a violated predeclared comparison; not_assessed for absent or inadmissible
observations. No result at one level upgrades another.

## Independent native-cell results

Residual = native printed minus independently calculated unrounded value.
All 60 primary STM headers were read directly from the pinned private archive
and checked for gross depth, native ordinal, displayed ARF and displayed
adjusted depth. Each group has ten identical scalar tokens. The separate ten
repeat headers also agree. TP/source binding and five-subarea depth identity
are prior authenticated #137 results; this is not a fresh rehash of 224 files.

| AEP | Duration min | EventIDs (each AEP; ordinal 1–10) | Gross mm | Published ARF | Published areal mm | Printed ARF | ARF residual | STM depth mm | Depth residual mm | Header verdict |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 5% | 720 | 8921–8930 | 81.20 | 0.914759275701 | 74.278453187 | 0.91 | −0.004759275701 | 74.28 | +0.001546813 | precision-limited 10/10 |
| 5% | 1080 | 9011–9020 | 91.50 | 0.929370614484 | 85.037411225 | 0.93 | +0.000629385516 | 85.04 | +0.002588775 | precision-limited 10/10 |
| 5% | 1440 | 9101–9110 | 99.40 | 0.943981953267 | 93.831806155 | 0.94 | −0.003981953267 | 93.83 | −0.001806155 | precision-limited 10/10 |
| 2% | 720 | 8921–8930 | 95.00 | 0.908331637457 | 86.291505558 | 0.91 | +0.001668362543 | 86.29 | −0.001505558 | precision-limited 10/10 |
| 2% | 1080 | 9011–9020 | 107.00 | 0.924443427504 | 98.915446743 | 0.92 | −0.004443427504 | 98.92 | +0.004553257 | precision-limited 10/10 |
| 2% | 1440 | 9101–9110 | 116.00 | 0.940555217552 | 109.104405236 | 0.94 | −0.000555217552 | 109.10 | −0.004405236 | precision-limited 10/10 |

The 24 h/5% repeat reuses EventIDs 9101–9110 and 24 one-hour steps, not
additional independent population members. All ten headers pass the same
bounds; original repeat native Q equality is historical, not routed parity.
The largest absolute primary ARF residual is 0.004759275701; largest depth
residual is 0.004553257 mm. Multiplying the displayed 0.91 by 81.20 gives
73.892 mm, not 74.28 mm: the ARF print token cannot be used as the internal
multiplier. The observed depth constrains a compatible multiplier much more
tightly if the source gross and once-only multiplication are assumed, but
that interval does not identify the underlying arithmetic.

### Written representation and rainfall diagnostic

Re-read the retained #137/#175 per-event JSON receipts (60 records each).
Below are aggregate results from those immutable receipts, not fresh native
or product runs. Each 12 h member has 24 × 30-minute increments; 18/24 h
members have 18/24 × 60-minute increments. The exact source-to-written
increment difference is nonzero in all 1,320 cases.

| AEP | Duration h | Exact #175 prepared/written increments | Max abs unrounded vs written (mm) | Written vs 0.1-mm native print failures | Unrounded vs native print failures |
| --- | ---: | ---: | ---: | ---: | ---: |
| 5% | 12 | 240/240 | 0.000258318 | 0 | 0 |
| 5% | 18 | 180/180 | 0.000505329 | 0 | 0 |
| 5% | 24 | 240/240 | 0.000338112 | 0 | 0 |
| 2% | 12 | 240/240 | 0.000251428 | 0 | 0 |
| 2% | 18 | 180/180 | 0.000888796 | 0 | 1 |
| 2% | 24 | 240/240 | 0.000824660 | 0 | 1 |
| Total | | **1,320/1,320** | **0.000888796** | **0/1,320** | **2/1,320** |

Exact written representation accepted for 60/60 events under the opt-in
`published_arf_stm_2dp` profile. The written-versus-printed rainfall
diagnostic is precision-limited. The unrounded-versus-print diagnostic
**failed** at 2%/18 h EventID 9012 step 6 (+0.0500200152 mm native minus
published) and 2%/24 h EventID 9110 step 18 (−0.0500990711 mm).
The published and written representations are different by design; do not
change the published method, reinterpret these failures as zero, or assume
the written representation is the unobserved runtime excess.

### Historical coefficient sensitivity (100 km², 1440 min, 1%, 129 mm)

| Case / explicit coefficient e | Published-method factor with that input | Unrounded areal mm | Printed ARF | Written mm | Written minus unrounded mm | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| R1/N1/N3: 3.85E-06 | 0.944602770885 | 121.853757444227 | 0.94 | 121.85 | −0.003757444227 | precision-limited |
| N2: 3.845E-06 (synthetic script sensitivity) | 0.944605836505 | 121.854152909185 | 0.94 | 121.85 | −0.004152909185 | precision-limited |
| N4: 3.50E-06 (synthetic stronger sensitivity) | 0.944817364273 | 121.881439991274 | 0.94 | 121.88 | −0.001439991274 | precision-limited |

N2 minus N1 is about +0.000395465 mm, unresolvable by the STM's 0.01-mm
total; N4 changes the total by 0.03 mm and all 24 forcing rate tokens
despite the same printed ARF. These are prior native controls, not new runs.
N1/N2/N3 exact export equality does not identify whether coefficient parsing,
total serialization or another quantization stage caused the collapse.
The native strict excess gate remains failed: R1/N1/N2/N3 and N4 each
0/24 versus full source; written-depth replay 23/24 for R1/N1/N2/N3,
22/24 for N4 at the original 0.0000018 mm budget. Subsequent rate-token
reconstruction does not accept internal rainfall; original R2–R7 failures
remain unchanged. No high-precision native ARF observation exists here.

## Independent analytical controls (no native observation)

All use published SW WA coefficients, gross **synthetic 100 mm**, except
the separate East Coast North example. Control grid fixed before evaluating:
158 km² at 720/1080/1440 min, 1%; adjacent minutes 719/721/1439/1441 at
2%; 0.99/1/1.01/9.99/10/10.01 km² at 1080 min, 5%; 30 and 2880 min
representative endpoints. These close coverage gaps in the existing
mostly 1%-AEP equations and transition tests. The test extension uses
only these analytical factors plus the six published-factor controls;
no native observations are used as expected test values.

| Area km² | Duration min | AEP % | ARF (12 dp) | Unrounded-method areal mm (9 dp) |
| ---: | ---: | ---: | ---: | ---: |
| 158 | 720 | 1 | 0.903469316829 | 90.346931683 |
| 158 | 1080 | 1 | 0.920716154441 | 92.071615444 |
| 158 | 1440 | 1 | 0.937962992052 | 93.796299205 |
| 158 | 719 | 2 | 0.908293750869 | 90.829375087 |
| 158 | 721 | 2 | 0.908376392429 | 90.837639243 |
| 158 | 1439 | 2 | 0.940510462579 | 94.051046258 |
| 158 | 1441 | 2 | 0.940567639089 | 94.056763909 |
| 0.99 | 1080 | 5 | 1.000000000000 | 100.000000000 |
| 1 | 1080 | 5 | 1.000000000000 | 100.000000000 |
| 1.01 | 1080 | 5 | 0.999935391559 | 99.993539156 |
| 9.99 | 1080 | 5 | 0.975523035709 | 97.552303571 |
| 10 | 1080 | 5 | 0.975505814868 | 97.550581487 |
| 10.01 | 1080 | 5 | 0.975494314198 | 97.549431420 |
| 158 | 30 | 1 | 0.680472288756 | 68.047228876 |
| 158 | 2880 | 5 | 0.955021061960 | 95.502106196 |

Independent 60-digit Decimal and binary64 evaluations of all 25 distinct
arithmetic cases (6 native-cell inputs + 15 controls + 3 coefficients +
1 published example) agree to a maximum absolute binary64 difference
of 1.1102230246251565e-16 (converted Decimal versus binary64).
This is an arithmetic cross-check, not independent human/agent review.
At the 10 km² boundary, 0.6614 × (10^0.4 − 1) = 0.999961685800436…,
not exactly 1, because the published interpolation coefficient is rounded.
Use the specified area branch; do not fit a continuity coefficient.

Published East Coast North example, 245.07 km², 1440 min, 1%, 504.3 mm:
independent factor 0.929168353408, areal depth 468.579600624 mm,
consistent with the printed 0.929 (±0.0005) and 468.6 mm (±0.05 mm).
The displayed 0.929 alone gives 468.4947 mm; do not multiply rounded
intermediates to infer a defect.

## Reproduction

The following standalone Python 3.11+ standard-library expression uses
the published coefficient tuples above. Supply each listed area/duration/AEP
and gross depth; retain full precision until reporting. For the 158 km²
rows choose the SW tuple, and change only e for the controlled sensitivity
cases. This one-off analytical recipe is not an alternative supported
product kernel or an archive parser.

```python
from decimal import Decimal, localcontext

D = Decimal
SW = tuple(map(D, "0.183 0.259 0.271 0.33 0.00000385 0.41 0.55 0.00817 -0.00045".split()))
EC = tuple(map(D, "0.327 0.241 0.448 0.36 0.00096 0.48 -0.21 0.012 -0.0013".split()))


def reference(area: str, minutes: int, aep: int, coeffs: tuple[Decimal, ...]) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = 60
        area_value, t = D(area), D(minutes)
        if area_value <= 1:
            return D(1)
        x = max(area_value, D(10))
        q = D("0.3") + (D(aep) / 100).log10()
        a, b, c, d, e, f, g, h, i = coeffs

        def power(base: Decimal, exponent: str | Decimal) -> Decimal:
            return (base.ln() * D(exponent)).exp()

        def short(u: Decimal) -> Decimal:
            return min(
                D(1),
                1
                - D("0.287") * (power(x, ".265") - D(".439") * u.log10()) * power(u, "-.36")
                + q
                * (
                    D(".00226") * power(x, ".226") * power(u, ".125")
                    + D(".0141") * power(x, ".213") * power(D(10), -D(".021") * (u - 180) ** 2 / 1440)
                ),
            )

        def long(u: Decimal) -> Decimal:
            return min(
                D(1),
                1
                - a * (power(x, b) - c * u.log10()) * power(u, -d)
                + q * (e * power(x, f) * power(u, g) + h * power(D(10), i * x * u / 1440)),
            )

        if t <= 720:
            v = short(t)
        elif t >= 1440:
            v = long(t)
        else:
            w = (t - 720) / 720
            v = (1 - w) * short(D(720)) + w * long(D(1440))
        return 1 - D(".6614") * (1 - v) * (power(area_value, ".4") - 1) if area_value < 10 else v
```

Use `with localcontext() as ctx: ctx.prec = 60` for multiplying
the reference factor by exact gross depth as well; tabulated precision
is for presentation only. Independent float expressions are already in
[the existing tests](../../tests/test_arr_arf.py). Reproduce the published
controls with `python -m pytest tests/test_arr_arf.py`; test code
does not require the private archive. The pre-existing written profile
tests are in [test_arr_design_batch.py](../../tests/test_arr_design_batch.py).

For authorised read-only retained evidence replay, at private main
`345b0b00318a663b9c70c2fe421d1c2c283387ef`, use the original paths
and manifests documented in public #137 and its private #80/#81 receipts:
`evidence/issue137/multiduration-60-native-preflight.json`,
`evidence/issue137/repeated-24h-ten-native-preflight.json`,
`evidence/issue137/published-vs-written-60-increments.json`, and
`evidence/issue175/per-event.json` / `final-audit.md`.
Use the existing archived methodology and readers, not a duplicate
product comparator. Read the STM gross, ARF, adjusted depth, source
ordinal, percent array and per-subarea depths. Cross-bind source EventID
and original AEP/duration/time step via manifest and source CSV. Compare
the recorded prepared increments and original written-depth reconstruction
as decimals; preserve all mismatches and unavailable fields.

## Applicability and disposition

| Claim | Verdict / boundary |
| --- | --- |
| Published equations and regional coefficient source | accepted for the directly checked SW WA and worked East Coast North cases; no formula defect demonstrated |
| 60 primary + 10 repeated native scalar headers | precision-limited (all within 0.005 intervals), no internal precision claim |
| Opt-in written profile | accepted for the prior 60/1,320 retained exact written-input receipt; no repeat counted as new population |
| Published unrounded source vs native printed rain | failed diagnostic for 2/1,320; distinct representation, no tolerance relaxation |
| Historical strict native excess | failed (R1/N1–N4 residuals preserved) |
| Native ARF helper/internal coefficient and effective rainfall | not_assessed; missing observable precision |
| 1/10 km² and duration neighbors, 1% 158 km², short/long analytical controls | accepted independent arithmetic; native comparisons not_assessed |
| Other regions, client source chain, multiple outlet ARF, rare/sub-30-min or out-of-domain and routed flows/selection | not_assessed here; separate ownership |

Checks executed for this record: Linux CPython 3.13.5 standard-library
independent Decimal/binary64 numerical calculation; read-only 70 original
STM-header checks and private receipt count aggregation. A local Git checkout
could not be fetched from this execution environment (GitHub DNS unavailable);
new product pytest, repository link hygiene, Ruff, strict Pyright and
source/wheel gates are **not run here**. Ordinary exact-head PR quality
is Python 3.11; main-push 3.11+3.14 policy remains unchanged.
Independent scientific review must verify the source equations, precision
bounds, source identity, fixed analytical values and residual signs and
resolve findings before marking this PR ready. No claim of new native
execution, product test success or independent sign-off is made.

Next owner: #192 scientific reviewer, then maintainer after review and exact-head
checks. If essential retained local-only R1/N4 or archive precision evidence
cannot be confirmed from the existing receipts, local evidence custodian
should read original TXT/IFD/STM/OUT/CSV and frozen manifests read-only;
return only admitted aggregate field/residual findings and exact hashes,
not original bytes. If no additional internal observation is retained,
record not_assessed as the bounded conclusion, not a new native experiment
or a blocker to a truthful precision-limited report. No production change
is supported by this work. Parent #8 and routed/representative-event
qualification remain open. No merge or release.
