# Issue #6 — engineering-v1 method and independent controls

- **Status:** Draft method and correctness slice; no numerical acceptance or batch-performance claim.
- **Owner/front:** default `python/engineering-v1`; separate from B's dataset/comparator, C's CMD feature matrix and the `python-cmd` implementation.
- **Baseline:** public `main` `c789c58fc7605c2341fef969ca426d30c3a477bf`.
- **Method and prospective gates:** [ENGINEERING_METHOD.md](../ENGINEERING_METHOD.md); limits and the non-parity status are part of the contract.
- **Source changes:** relative nonlinear residual and non-arbitrary bracketing for tiny positive hydrographs; physically explicit uniform-bin IL-to-CL crossing; fail-closed confluence overflow. Preserve the readable S2 solver for the later batch reference.
- **New independent tests:** [test_engineering_accuracy.py](../../tests/test_engineering_accuracy.py) checks closed-form linear response, manufactured nonlinear solution/refinement, independently computed continuity, event-level branch storage, crossing/equality and adverse cases.
- **Source/wheel/CMD gates:** Do not claim an executed result until validation evidence is recorded. The cached CMD snapshot is historical candidate output, not engineering proof.
- **Next action:** Run focused and previous-stage tests and static checks, independent review, update exact source/wheel receipts and numerical restrictions before a later *separate* immutable-preparation/batch PR. Do not optimise before this method's narrow criteria are accepted.

No native files, CMD arithmetic, public regression schema, executor selection, baseline fixtures or new dependencies changed.
