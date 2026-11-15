# CMD 6.44 scalar timestep-storage comparator correction — 15 November 2026

**Scope:** B/#100 maintained original comparator under full CMD gate #5; no separate runner or data set. The published case register, golden source and native reports, raw one-based CMD clocks, frozen printed-Q interval and scalar token policies remain unchanged. Both public numerical engines and the optional native adapter are untouched.

## Evidence-backed correction

The original source-to-stored reference bindings in the unchanged register specify **binary32(h)** followed by **binary32(p53(stored_h * 3600))**. In the fresh-source branch of `regression_dataset._fresh_cmd_reporting_metrics`, the old `float(source_hours)` and `float(Decimal(source_hours) * 3600)` retained binary64 values. H2 (source h=0.3), N4 (h=0.2), and `pyromb-novel-storm` (h=0.2) therefore stopped with `incomplete: Unqualified source-to-stored CMD time representation` before their original reported peak/time/inclusive volume could be evaluated.

The bounded fix uses a standalone standard-library `struct` binary32 store for h, performs exactly one binary64 multiplication by 3600.0 and stores the product as binary32. This verification helper lives in the *existing scalar adapter*, not the CMD engine, to preserve the comparator's independent implementation. It rejects invalid, nonfinite or unrepresentable positive time inputs explicitly, and retains the original registered hex binding gate (any unexplained disagreement is still **incomplete**, not silently accepted). The source/model generated elapsed clock and original native one-based `Inc/Time` tokens are not shifted.

| Original case | Source h (h) | Authenticated stored-h | Authenticated stored-dt (s) |
| --- | ---: | --- | --- |
| H2 | 0.3 | `0x1.3333340000000p-2` | `0x1.0e00000000000p+10` |
| N4 | 0.2 | `0x1.99999a0000000p-3` | `0x1.6800000000000p+9` |
| pyromb-novel-storm | 0.2 | `0x1.99999a0000000p-3` | `0x1.6800000000000p+9` |

New tests exercise authentic source → typed project → current `python-cmd` → unchanged original CMD report for all three cases, including all scalar verdicts, and explicitly retain the two all-zero original series' undefined uniquely timed peak.

## Qualification boundary

This changes a **substantive comparator implementation**, not native truth or production arithmetic. **Independent code review is mandatory before promoting any new scalar pass to numerical acceptance.** CI must prove the 50-case source/wheel complete report objects agree, the exact original reference index verifies, retained 36-case results remain unchanged, new original cases have no Q mismatches, and the zero-flow peak-time classification remains incomplete. If an actual original peak, time or volume fails after the clock is bound, preserve the failure and investigate the original selector rather than relaxing the frozen policy.

The unchanged authoritative matrix and issues #5/#94/#95/#96 retain source, native/physical, default-engine and upstream PyRomb qualification gates. The private investigations workspace, Ghidra and new native reference launches are not required for this bounded software comparison.
