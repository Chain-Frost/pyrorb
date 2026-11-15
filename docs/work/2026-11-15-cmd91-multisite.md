# CMD output sites / unresolved code-11 scope (#91)

**Parent:** roadmap #1 / CMD gate #5. **Base:** compatible-mode PR #108 at `55818dcacca366cda58bdc09f345bf470365beca`. **Stack:** `feat/cmd91-multisite-20261115`, review onto #108 before main. Only code-7 multi-output is implemented in this slice; code-11 is not inferred.

## Confirmed software capability

The current S1 catchment model already recognises several ordered code-7 prints and enforces unique identifiers, full source consumption and a final physical outlet. The compatible `python-cmd` backend previously discarded each code-7 print except the last. This slice captures every code-7 result directly at its original control position, retains independent immutable full-horizon Q and source membership and pairs it with the existing S1 `print_id` and label in their validated order. The final print must equal the connected outlet; absent/truncated outputs fail explicitly. Neither code-7 source membership nor the S1 label is a proved native HydNNN physical mapping.

The default `python` engine already independently computes all code-7 prints; new tests prove end-to-end API/CLI source order. The selected `rorb-cmd` adapter already requires a one-to-one caller-supplied site/column map; the new strict multiplicity guard rejects duplicate HydNNN report headers even when their sets match. Native adapter manufactured-process tests reject duplicate/unmapped columns, short reports and absent/negative output. No actual native CMD run is claimed.

## Per-engine status

| Engine | Recognition | Execution | Full output | Original CMD numerical / physical qualification |
| --- | --- | --- | --- | --- |
| Default `python` | Multiple code-7 S1 prints | Existing independent engineering-v1 code-7 path | Tested in this PR | **Not accepted** against original CMD multi-site outputs |
| `python-cmd` | Multiple code-7 prints | Newly captures each control's Q state | Full computed model-clock horizon per site and explicit membership | **Not accepted** for multiple sites |
| `rorb-cmd` | Requires original source and strict caller assertion of each HydNNN column | Existing adapter path; no new native execution | Strict raw output/horizon/column checks, including distinct count | **Native physical mapping unproved** |

Original `fig67-code11` has `incomplete_output` in the 85-case register and **no admitted native source/report objects**. Code 11 may represent a different print/excess control class; do not add it to typed code-7 semantics or generate a fake rainfall-excess or discharge series. E/B must establish the actual field meaning and complete original evidence if possible; C owns necessary parser/domain recognition. Only confirmed output classes should then be implemented and compared. If irrecoverable, record the exact CMD applicability gap with the programme owner.

## Acceptance and quantity boundaries

The maintained original comparison register is unchanged. Re-run fresh source and isolated installed wheel, current 36-case/50-case CMD controls and the tests for two outputs, ordering, source identity, distinct Q, full horizon, missing/ambiguous/duplicate/mismatched sites and original one-based native clock rejection. Independent CMD 6.44 peak, full series, physical trapezoidal volume, native inclusive reported volume and timing comparisons remain **unavailable** until original physical site/clock mappings and native outputs are authenticated. Zero-denominator percentages are undefined; the former 0.3%/0.805% observation is not a new-feature tolerance.

**Coordination:** source admission C (#93–96), B/E original native/comparator, programme owner single `CMD_FEATURE_MATRIX.md`. None are modified here. No private production dependency, reference regeneration, new hosted workflow, auto-merge or release. Leave #91 and #5 open until independently reviewed genuine CMD evidence passes.
