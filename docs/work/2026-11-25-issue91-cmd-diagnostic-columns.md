# Issue #91 — bounded CMD diagnostic report binding (25 November 2026)

Base: `b6788a83fbe5eb9ccd68232fe8d92dfb596e0f6b`. Tracks [#91](https://github.com/Chain-Frost/pyrorb/issues/91)
under [#5](https://github.com/Chain-Frost/pyrorb/issues/5). Existing #113 ordinary code-7 output is unchanged.
Concurrent #235/#237 own matrix/status edits; #232 retains MC grammar, #100 the sole comparator,
and #90/#92 their feature qualifications. No shared matrix/register edits here.

## Retained observation and scope

The existing [register](../../tests/fixtures/regression-v1/register.json) and
[original authentication](2026-11-15-native-closeout/original-authentication.json) bind the complete
fig67-code11 report to a source that changes only the first computational code 1 to 11 (5.000, -99).
The published CATG and retained ordinary CATG were compared byte-for-byte after this one-character substitution.
All five published code-11 file sizes and SHA-256 hashes match the register; CP1252 bytes were recovered
from connector text for STM and OUT before hashing. This authenticates the published objects, not a new
independent audit of their private-original provenance.
With the same STM and effective PAR parameters (kc=10, m=0.8, IL=20 mm, CL=2 mm/h), all 301 raw
(Inc, Time, Hyd005) tokens exactly match (Inc, Time, Hyd001) in both fig67-ilcl-confirmed and
fig67-ilcl-probe. A retained-pair test pins the confirmed report hash and compares original tokens.
This is evidence for unchanged terminal routing in this specific first-control case, not a general
code-11 execution rule or independent binding of the four diagnostic taps.
The legend identifies five report-local quantities: A upstream, A rainfall-excess flow,
reach 0 1 downstream, reach 0 1 upstream, calculated flow. All five use m³/s in the retained discharge
summaries; rainfall-excess **depth** is not any of these five columns. Hyd002 and Hyd004 have identical
printed values in this observation but remain distinct report identities. Native raw Inc 1–301 / Time
0.50–150.50 h are retained; physical elapsed time and native reported time-to-peak are separate.
The all-zero Hyd001 series has no unique physical peak time. Native inclusive and physical
trapezoidal volumes are not interchangeable. No reference bytes, tolerances or register membership change.

The canonical reader binds the observed five-column legend by ordinal, checks the characterised
version, units, complete one-based clock and nonnegative values. It exposes a read-only
`cmd_diagnostic_sites` section through existing JSON/CSV views, with unverified physical identity.
The ordinary physical binder and selected native ordinary-print adapter reject this diagnostic family.
This is a **report software slice only**; it does not prove executable identity, model/control binding,
summary-to-column scalar binding or routing semantics. It does not implement executable code 11 or alter
EngineOutcome/EngineHydrograph. Other diagnostic layouts remain unadmitted.

## Outstanding checks and ownership

C/#3 and A/#91: agree and implement the smallest typed control/diagnostic result contract before enabling
code 11; preserve computational order and source identities. Establish the diagnostic source/reach taps
and excess-flow conversion independently; do not fabricate ordinary code-7 sites or substitute engines.
B/#100: independently bind all five columns and full clocks/scalars using the existing comparator;
preserve separate volume definitions. A/#91: native-adapter negative control for matching ordinary
column count is authored; execution and independent review of that test, engine/report integration and
native numerical qualification remain outstanding. No new native run is
required until a named indispensable discriminator is predeclared under #5.

Initial PR Python 3.11 CI failed on three Ruff findings in the new tests; corrections were committed.
Successful source and isolated-wheel execution and independent domain/output/code review remain outstanding.
Run the existing PR Python 3.11 quality workflow, focused reader and native-output controls,
and full-index/source-wheel procedure in [REGRESSION_DATASET.md](../REGRESSION_DATASET.md).
Record exact source/wheel identity, actual imported path and complete results. No default, reference,
CI workflow, scientific status, merge or release change is authorised. Keep #91 and #5 open.


## 28 November continuation: bounded execution and separate offline arithmetic check

Starting reader head `57113d16c1d69a67e65658b2e887a6cdbf3899dd` passed the existing
[3.11 CI](https://github.com/Chain-Frost/pyrorb/actions/runs/45713954391).
The current main advanced to `9a9b45c02204b75f95c87ef250014f6479a73187` with #148
documentation only; its changed files do not intersect this feature. No work from other open
PRs was overwritten.

### Source and calculation

The original computational vector is
`11,3,1,4,5,3,1,4,5,3,1,4,5,3,1,4,5,7`. Control 11 consumes the first
area/reach (A, 30 km²; 5 km, terminator -99) before any branch exists. The other original areas
are 28, 25, 35 and 40 km²; preserve their encounter order, including E before D. The 72 weights
sum to 102.10, and the original combined preburst/burst total depth is 69.02 mm. At h=0.5 h,
IL=20 mm and CL=2 mm/h, the binary32-compatible preparation crosses initial loss in bin 57.
The diagnostic source flow is the per-increment excess times 30,000/1,800, in m³/s;
the zero upstream tap is the absence of any prior running branch. The first reach incoming
series equals the source flow in this particular initial-control case.

Source distances are 12.5, 11.5, 9.5, 7, 6 km. Area-weighted mean = 8.98417721519 km
(stored 8.984177589416504); stored first reach k = 5.565340042114258 at kc=10.
An independent implicit trapezoidal nonlinear solution at m=0.8 gives a peak of 34.909851
and only 68/301 first-reach samples within native printed precision. That mathematical
solution is not the CMD arithmetic oracle and was not substituted into the product.

A separate JavaScript binary64/binary32 calculation of the existing documented CMD
preparation, geometry, power and alternating-coordinate routing operations (not native or
production Python execution) used only the original source inputs for calculation, then
checked all original printed tokens. It reproduced all five 301-sample series:

| Native column / distinct quantity | Within printed half-unit | Max absolute error (m³/s) | Computed peak (m³/s) | Peak elapsed (h) | Candidate inclusive sum (m³) | Candidate trapezoidal integral (m³) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Hyd001 upstream before source | 301 | 0 | 0 | undefined | 0 | 0 |
| Hyd002 rainfall-excess flow | 301 | 0.0000494873 | 49.9197158813 | 30.5 | 990599.940419 | 990599.940419 |
| Hyd003 reach downstream | 301 | 0.0000499409 | 34.9085731506 | 36.0 | 991552.774967 | 991552.567752 |
| Hyd004 reach upstream | 301 | 0.0000494873 | 49.9197158813 | 30.5 | 990599.940419 | 990599.940419 |
| Hyd005 terminal ordinary print | 301 | 0.0004946567 | 170.7816009521 | 36.5 | 5225539.191360 | 5225537.510597 |

These are independent-of-the-production-run candidate diagnostics, not independent reviewer
approval or new native observations. The retained report's groups at lines 387–393,
400–406 and 413–419 explicitly name upstream/subarea, downstream/upstream and calculated
quantities. The exact scalar selectors (line, character, ordinal) are pinned in the
existing comparator, and the canonical reader supplies the original tokens. In particular,
Hyd001's native 32.2 h is not a unique peak of its zero series. Native raw Inc/Time
1–301/0.50–150.50 h and generated elapsed 0–150 h remain distinct. The native inclusive
reported scalar and separately calculated trapezoidal flow integral are not interchangeable
or conservation proof.

### Software scope

First and only code 11, implicit natural positive reaches, one terminal code 7, one ISA/burst,
pervious IL/CL, m=0.8 and zero rainfall start. Existing source order is preserved; code 11
remains code 11 in the typed model and kernel. Four typed diagnostic flow series refer to
the first source/reach and are not additional physical print locations. The ordinary outlet
is still the sole EngineHydrograph. JSON, batch CSV and text identify diagnostic flow roles
separately. The independent Python and selected native adapter remain explicitly unsupported;
edited CATG export is rejected, with original byte copying left intact. No broader code-11
placement, repeated control, alternative reach/loss/exponent profile, native executable or
physical node identity is admitted.

The existing regression comparator checks the exact retained input/report identities,
all 1,505 ordinates and the original group-specific scalar selectors, without altering
its printing/tolerance arithmetic. Its separate code-11 diagnostic result remains outside
the original 50-case admitted population; the existing probe includes the full diagnostic
candidate float.hex arrays and elapsed clock for source/installed-wheel equality. Added
adverse identity, units, clock, truncation, unsupported-engine and output-product controls.

Production Python tests, updated-head wheel verification and independent code/domain review
must pass before promoting even this bounded software result. The separate research
calculation is not a substitute for these gates. #91 and #5 remain open; no new native
process, default change, reference/tolerance change, merge or release.

The frozen `cmd644-report-scalars-v1` gate selects the 50 original terminal prints. This new
case uses the unchanged arithmetic and intervals only as a diagnostic study outside that population;
no policy scope extension or independent admission is claimed.

## Independent exact-head review — 28 November 2026

**Decision: ACCEPT the bounded software and retained-report numerical comparison at
`5d273167c209afa6ef334090b116a11af0007bbf`. No substantive software defect found.**
This is an independent review of the production changes and existing evidence, not the
author's JavaScript calculation. No RORB process, research replay, CI rerun, merge, release,
default change or issue closure was performed. #91/#5 remain open for their wider gates.
This receipt is committed on a separate review branch so the reviewed feature head stays fixed.

### Source admission, computation and output

Reviewed all 19 changed files against base `b6788a83fbe5eb9ccd68232fe8d92dfb596e0f6b`.
CATG parsing, JSON round-trip and typed stack validation retain control 11 as the first and
only implicit-natural source/reach, with one terminal code 7. Source encounter order and
branch membership remain intact. Geometry and routing treat that source/reach through the
existing arithmetic; no native tokens, report values or new numerical method feed computation.
The first-control position makes pre-source inflow structurally zero. Source excess flow is
the existing area/depth/time conversion in m3/s, and the first reach's upstream/downstream taps
come from actual kernel state. Equal rainfall-excess and reach-upstream arrays retain distinct
roles. Four diagnostic series remain separate from the sole ordinary EngineHydrograph, including
JSON, CSV fields, elapsed clock and text. Native inclusive reported volume remains separate from
the derived trapezoidal flow integral; neither establishes physical conservation.

The canonical reader checks the retained version, legend, units, ordinal identities and complete
one-based report clock. Scalar selectors were independently checked against the raw report's
three named summary groups and exact token positions. Ordinary physical-site binding rejects
diagnostic legends. Physical node identity remains unverified; report-local roles and source
identities do not establish it. Independent Python execution, selected native diagnostic capture,
edited CATG export and broader layouts remain unsupported without fallback.

Supplementary local boundary checks on Windows/Python 3.14 rejected IL/RoC, nonzero rainfall start,
impervious area and a terminal zero-length reach with `unsupported_feature/cmd_code11_profile`
and no output arrays. Typed construction rejected explicit reach types, repeated code 11 and
nonfirst code 11. Existing CI tests cover the other exponent, engines, malformed report layouts,
missing/duplicate diagnostic roles, source attribution, truncation, negative flow and clocks.
These checks add boundary evidence; they do not repeat the original calculation or establish
native equivalence for unsupported variants.

### CI and independent numerical audit

Inspected [run 46040292492](https://github.com/Chain-Frost/pyrorb/actions/runs/46040292492),
job `140645999622`, including checkout, failure propagation, source execution, build, installed
import origin and complete probe records. It checked out merge commit
`c3221a48ed82ff81ea0426cf7d9c621581855096`, whose parents are main
`9a9b45c02204b75f95c87ef250014f6479a73187` and the requested feature head. Its source,
developer-script and test trees equal the reviewed feature head. This is an audit of the
approved CI receipt, not a personally executed second source/wheel quality campaign.

- Actual environment: Windows Server 2025, CPython 3.11.9. Repository check 667 files/0 errors;
  Ruff lint and format 341 files; strict Pyright 0 errors/warnings; source 1,737 passed and three
  explicitly POSIX-only skips. Installed-wheel suites: 241 + 41 + 115 = 397 passed. Both
  activation-only release checks were appropriately skipped. Required aggregate succeeded.
- Wheel SHA-256: `72150f090a99c5c4ade9e27442817970cac8306a9c692b269ae1ef0b956dab74`.
  Import was `D:\a\_temp\runoff-wheel-smoke\runoff_routing\__init__.py`, outside the checkout.
  The explicit wheel-to-installed-source provenance check succeeded. Full-index preflight
  authenticated all 254 indexed files. No downloadable workflow artifacts exist; the evidence
  used here is the detailed retained job log, not an independently downloaded wheel binary.
- Package fingerprint: `package-code-v1-sha256:5f80989bb10f2828d54004c5c897dc5612c4429784e519e0df976df4ad39cb2b`.
  Independently recomputed it from the exact-head checkout bytes. Both complete logged JSON
  objects are equal, including all individual 50-case Q/scalar/status/source/model/project
  records and the new diagnostic identities, clocks and full float.hex arrays.
- Independently extracted the retained report bytes, verified all five registered file
  sizes/hashes, and compared the logged production binary64 arrays using exact rational
  half-last-printed-unit intervals, without importing the product comparator or rerunning the
  solver. **1,505/1,505 ordinates pass.** Recomputed peaks, elapsed peak times and inclusive
  volumes directly from those arrays and checked the original scalar tokens/positions:
  **14/14 defined fields pass; Hyd001 peak time is correctly incomplete/undefined.** Its 301
  tied zero ordinates do not justify adopting the printed native 32.2 h as a physical peak.

| Column | Samples | Maximum absolute Q difference (m3/s) | Unique elapsed peak (h) |
| --- | ---: | ---: | ---: |
| Hyd001 | 301 | 0 | undefined |
| Hyd002 | 301 | 0.0000494873046875 | 30.5 |
| Hyd003 | 301 | 0.0000499408781528 | 36.0 |
| Hyd004 | 301 | 0.0000494873046875 | 30.5 |
| Hyd005 | 301 | 0.000494656741619 | 36.5 |

All native Inc/Time tokens remain 1–301/0.50–150.50 h; generated elapsed times are 0–150 h.
The largest absolute signed peak percentage difference relative to the original printed series
is 0.000233659198% (Hyd005, signed negative); the largest absolute trapezoidal-integral percentage
difference is 0.000193078383% (also Hyd005, signed negative). These are diagnostics, not new
tolerances. Zero reference denominators remain undefined.

### Regression policies, compatibility and remaining limits

All 50 existing individual records match source to wheel: 19,550 printed ordinate passes,
48 complete scalar passes and the two existing zero-flow peak-time incompletes. Exact input
identities and horizons were checked per case. The retained-36 gate, nonretained gate and
synthetic nonzero-exit propagation controls passed. Native references, register/index, snapshots,
`.gitattributes`, tolerance arithmetic, scalar policy, 50-case membership, defaults and workflow
are unchanged. The new code-11 study remains outside the frozen terminal scalar-policy population;
its register coverage stays `gap` and result status stays `computed_unvalidated`.

Remote heads were re-read: feature remains the requested SHA; current main is
`cadd930db3e8ce8ea75bf9278ebc85bd06314bbd`. Its three commits since the original base have
no changed-file intersection with this PR. A nonmutating `git merge-tree --write-tree` succeeds
with tree `61ecfa30e5ac6a3b13ae3d7a6a2613ec88097d5c`; its product source and developer-script
trees equal the reviewed head. This establishes clean integration and unchanged reviewed runtime
code, not a claim that CI executed that future merge tree.

No software repair or duplicate full CI run is warranted by the audit. The bounded first-control
profile and original retained numerical observations are independently accepted at the exact head.
General code-11 semantics, independently observed physical sites, broader native/scientific CMD
acceptance, engineering-engine accuracy and release remain separate. Next action: owner disposition
of PR #240; keep #91/#5 open and do not extend acceptance to unreviewed profiles or future heads.
