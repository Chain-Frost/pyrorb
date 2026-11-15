# CMD linear/exponent/reach boundaries — scoped control qualification (#92)

**Base:** `916636a8ae610f09b1174f1263d4c11d30799722`. **Proposed branch:** `test/cmd92-linear-boundary-20261115`. **Roadmap:** #1; full CMD gate #5.

The existing `python-cmd` implementation already contains a separate `m=1` linear binary32-emitting recurrence and a positive-`m` nonlinear solver. The default `python` engine has its own analytic linear branch and explicitly rejects `m=0`, while allowing `k=0, m>0` as no-storage routing. No source/reach semantics are changed in this bounded control slice; it adds **independent analytical software tests** for a linear pulse and typed error/admission boundaries without copying CMD kernel arithmetic or asserting new native behaviour.

## Original archive classification

Each of the following remains **evidence-incomplete** in the current public 85-case register: `fig67-kc5-m1`, `failure-m-above-one`, `failure-m-below-one`, `failure-zero-reach`, `failure-negative-reach`, `failure-negative-reach-repeat`. These have historical native capture manifest identities but **no admitted original source/report file objects**, and their original native outcomes were not independently reviewed. The reference owner must distinguish *native-valid / native-rejected / original-evidence-incomplete* before modifying compatible input policies. In particular, a manufactured linear test does not prove `fig67-kc5-m1` agreement, and S1's strict positive-reach restriction is **not** proof that original CMD rejected zero or negative reach records.

| Feature | `python-cmd` | Default `python` | `rorb-cmd` |
| --- | --- | --- | --- |
| Positive non-unit `m` | Recognised, existing nonlinear path; original above/below-one numerical qualification missing | Recognised, separate nonlinear path; original CMD comparison missing | Native adapter requires file-backed valid S1; original outcome incomplete |
| `m=1` | Existing linear execution/full Q; analytic manufactured control here; original m=1 comparison outstanding | Independent linear execution/control; original CMD comparison outstanding | Physical source/report not admitted |
| `m=0` | Typed S1 rejects; **no instantaneous-route assumption** | Typed S1 rejects; no-storage `k=0,m>0` is a separate valid concept | Native zero-exponent outcome not established |
| Zero/negative reach | Current typed S1 rejects; do not equate this to native behaviour | S1 rejects; pure S2's bounded isolated zero-reach policy differs | Original native verdict unreviewed |

**Verification:** reuse the unchanged original reference register, authentic original case metadata and the single comparator after E/B qualify individual failures. Compare full Q, original one-based native clock and printed inclusive volume only for genuine successful native outputs; separately measure peak/ordinate errors, percentage with undefined zero denominators, physical trapezoidal volume, convergence behaviour and timing. Do not regenerate original references or infer a universal tolerance.

**Remaining owners:** E/B authenticate original outcomes and classify valid/native error/evidence gaps. The numerical owner then implements only proven boundary behaviour in `python-cmd`, with an independent default feature owner reviewing any default change. Programme owner maintains the one CMD matrix. Run exact-head source/wheel tests; keep #92/#5 open for unqualified original cases. No native executable launch, new hosted workflow or private dependency in this PR.

## Retained CMD 6.44 original boundary observations (15 Nov 2026; not newly admitted)

**Important classification correction:** historical case IDs prefixed `failure-` are campaign names, **not proof that native CMD rejected the inputs**. Read-only checks of the private retained native-corpus original manifests, source .par/.catg and .out plus 301-row `Hyd001` tables show:

| Original case | Named effective source operand | Actual retained CMD output | Qualification disposition |
| --- | --- | --- | --- |
| `fig67-kc5-m1` | `kc=5, m=1` | one 301-row Hyd001 and completed data check | `captured_unverified`; genuine positive linear candidate, not publicly admitted |
| `failure-m-above-one` | `kc=10,m=1.001` | one 301-row nonzero Hyd001 | `captured_unverified`; **not native-rejected** by name |
| `failure-m-below-one` | `kc=10,m=0.999` | one 301-row nonzero Hyd001 | `captured_unverified`; **not native-rejected** by name |
| `failure-zero-reach` | first code-1 reach **0.000 km** | one 301-row Hyd001, completed data check | `captured_unverified`; real native-computed output, physical/numerical validity undecided |
| `failure-negative-reach` | first code-1 reach **−5.000 km** | one 301-row Hyd001, completed data check | `captured_unverified`; real native-computed output, **not a defensible positive-reach hydrological admission** |
| `failure-negative-reach-repeat` | same negative original source length −5.000 km | one 301-row Hyd001 | `captured_unverified`; repeat identity/outcome independently needs verification |

The native executable identity in the maintained register is CMD 6.44 SHA-256 `10999ca29f9516c6a7abd26df37cafd433a1cd4ae70d7ac61aa7213845c5ab6f`. Private manifests retain **generator name/revision/event-to-file provenance gaps** and were not admitted into public `tests/fixtures/regression-v1/register.json` (case entries have no public comparison files). They are not yet B-independent original-source/site/clock/printing/scalar qualification. In particular, `m=0` is a *different*, unsupported exponent and has **no established instantaneous-routing behaviour**. Negative reach lengths remain rejected by the current positive-reach S1 contract, despite native output; scientific acceptance cannot be inferred from an executable generating a table. For the CLI/text-file MVP #119 the **declared common model remains positive natural reaches and supported positive exponents**, not the entire extreme-boundary archive.

**Original reference-admission next action:** B/#100 and programme #5 should review the six precise original manifests/source/effective controls, raw time labels 0.50…150.50 h, positive/rejected applicability, output Q/printed peak/time/inclusive volume and site attribution, then admit only proven eligible references into the single maintained register. A may then compare actual source/isolated installed wheel full Q, physical trapezoidal volume and default `python` absolute/percentage max/RMS/peak/volume/timing under frozen policy. No golden, threshold, parsed domain or numerical kernel was modified in this evidence update.

**Exact previously validated authored control PR head:** `8e7a1ae90bef6f5061d4572a77e87973509fb051`; [CI 43683292731](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43683292731) passed Python 3.13 Windows pinned Ruff/Pyright, 919 source tests, 98 installed-wheel tests, full-index plus preserved 36 original CMD Q/scalar cases (16,836 ordinates), with identical source/wheel 50-case results (36 pass, 14 source-unsupported). Wheel SHA `dd948071e478f7657043046ddca1d16cc51aa2b37d9713fc162695840ef11f41`. That receipt is software/old-domain only; the new retained native boundary cases remain unqualified.
