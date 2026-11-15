# Default Python IL/RoC counterpart — independent feature slice (#90)

**Direction:** CMD gate #5 and roadmap #1. **Base:** `916636a8ae610f09b1174f1263d4c11d30799722`; branch `feat/python90-ilroc-20261115`. This **separate** default-engine PR does not contain the `python-cmd` implementation from draft PR #108.

## Implementation

- The existing S1 parameter field retains its original `loss_model=2` and dimensionless RoC. At the S1→S2 numerical boundary, `continuing_loss_mm_h=0` and **separate** `runoff_coefficient` is supplied. No silent mode-1 substitution, percentage conversion or use of CMD floating-point kernels.
- Independent default arithmetic: carry initial loss across bins; at equality give zero excess; after IL, multiply remaining positive rainfall by the coefficient. Mode 1 continues subtracting full-bin CL/h. Reject ambiguous simultaneous continuing-loss and coefficient inputs, and coefficients outside [0, 1].
- Retain default `engineering-v1`, requested print site(s), complete event horizon and original model identity; keep no native-fallback behaviour.
- Source integration and S2 tests cover positive/zero/one coefficient, equality, no crossing, distinct CL mode, invalid coefficients, physical source-volume control and full typed output.

## Engine ownership / acceptance

| Engine | R | X | O | Q against original CMD |
| --- | --- | --- | --- | --- |
| `python` | Y | Software execution implemented here | Complete default Q and separate physical loss/source arrays | **Unassessed** |
| `python-cmd` | Y | Separate bounded work PR #108 | Separate CMD stored-precision engine | **Unassessed for flag 2** |
| `rorb-cmd` | Y | Native adapter still rejects mode 2 | Not established | **Unassessed** |

The original `fig67-ilroc` entry remains `captured_unverified` with no admissible public source/report objects, so neither the native original profile's coefficients nor the peak, per-ordinate, percent, clock and physical-volume errors can be reported legitimately yet. An analytical source-volume check is **not** a substitute for original CMD comparison. The previously observed 0.3%/0.805% differences are not adopted as mode-2 thresholds. The reference/comparator owner must first admit and validate the original printed source and output, then run and report absolute/percentage comparisons and timing. Native inclusive reported volume and trapezoidal physical volume remain separate.

**Parallel ownership:** C's in-flight PR #107 owns the `relative_weights` DESIGN grammar and its fail-closed S2 exclusion. This slice changes only the S1→S2 **loss-mode** boundary; reconcile/rebase after source admission changes without weakening the relative-weight rejection or editing source grammar. No changes to C's typed domain model or programme matrix, and no new reference files, CI workflow, original data or native executable. Record actual source/installed-wheel CI after it runs. Leave #90/#5 open until qualification is complete.


## Reconciled main and independent-selection regression — 15 November 2026

- This historical independent #90 slice is reconciled against public main after merged source admission #132, temporary default #130, prepared batch #119, comparator correction #135, and design workflow #136. Historical quality/numerical receipts above remain attributed to their **original** tested revision.
- Test projects now explicitly persist `EngineSelection.for_engine("python")` and assert both the stored and effective independent engine. New schema-2/EngineSelection() defaults remain `python-cmd/cmd-6.44`; schema-1 implicit engine retains `python/engineering-v1` and stored choices are never replaced.
- This mode-2 calculation is the independent S2 implementation, not a wrapper around CMD stored precision. Missing native mode-2 reference must not be represented as numerical acceptance. Existing #133/#5 evidence ownership is unaffected.
- The existing #125 code-2/FI branch remains stacked on this PR and requires the separate S1→S2 admission, exact-revision quality checks and numerical review before merge.
