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
