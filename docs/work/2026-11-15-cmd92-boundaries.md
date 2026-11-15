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
