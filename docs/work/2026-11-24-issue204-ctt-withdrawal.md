# Withdraw unqualified GE 6.45 C T T admission (#204)

Owner decision, 24 November 2026: withdraw the separator-only `C T T` admission rather than claim compatibility without authentic source evidence. The [23 November original-source assessment](https://github.com/Chain-Frost/pyrorb/pull/204#issuecomment-7106368266) found five genuine GE 6.45 `C T T` sources, all with inline asset references; none establishes the separator-only contract. This is unavailable qualification evidence, not proof that the signature is invalid in native RORB.

## Change and retained boundaries

Restore acceptance of only the characterised `C T F` background signature. Separator-only `C T T`, `C F F`, unknown flags and inline assets remain explicitly unsupported. Retain the additional guard rejecting substantive records following an otherwise supported `C T F` flag, so the useful asset-payload hardening is independent of the withdrawn admission. No unknown background record is silently discarded.

The former synthetic positive test is replaced by explicit `C T T` rejection tests for both `.cat` and `.catg`, with unchanged-source/hash assertions on the characterised original. Asset-payload negative tests now start from the supported `C T F` signature, ensuring they reach the retained payload guard rather than stop at the flag gate. Original fixtures, computational records, numerical code, goldens, tolerances and engine defaults are unchanged.

## Revision and stack scope

- Starting #204: `67901ce590b664d561e4533b8c7c84f798ed4ae5`.
- Actual parent #203: `ee7ac78e6c438c0c32fbee88a7df1150e101c7a9`.
- Preserved #205: `7d365f84860f33f62b5b9e85600c2c397c2f4a70`.
- Preserved #207: `b13ebe002b160a9a9a471d1d72636d91b2392c23`.

This correction is isolated to #204. Downstream branch compatibility is checked without updating those branches. Their existing trees continue to contain the historical admission until a separately reviewed stack synchronization; they must not be described as inheriting this correction already. Do not merge or retarget downstream PRs as part of this withdrawal.

## Qualification and next action

Focused CATG/source-preservation tests, repository hygiene and exact-head existing Windows CI are recorded on #204 with their actual outcomes. Local tool failures remain failures; successful hosted software checks are distinct receipts. No new native executable run, source-discovery campaign or numerical acceptance is implied.

Keep #204 draft and the original evidence thread unresolved pending fresh independent review of the withdrawal. The reviewer may dispose of the original admission finding as withdrawn; do not claim that its missing source evidence has been supplied. Original-source support remains deferred under #197, which stays open. A future admission requires an authenticated exact source form and its independently accepted preservation/semantics evidence.

Local Windows/Python 3.14 check: the complete CATG roundtrip file passed **104 tests** with the pinned reader and optional PyRomb writer installed in an isolated dependency folder. Repository hygiene passed **550 files / 0 errors**. Local Ruff lint/format and Pyright launches were blocked by endpoint policy (WinError 5); they are not local passes. Exact-head hosted checks and fresh independent review remain required after publication.
