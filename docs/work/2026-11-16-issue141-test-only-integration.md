# TEST-ONLY revised #141 interoperability snapshot (16 November 2026)

**NOT FOR MERGE.** This branch overlays reviewed owner blobs on the earlier #143 synthetic source snapshot, without adopting the other PRs in main.

- #138: 334c576fb97a2b7fc32f4789c0e27a2b786580b8
- #139: previous #143 synthesis uses #139 PR #166 at eba65891ad8b81995684532c7eeac5c0bd6a0022
- #140: 32c03cd6f91504a7d5125b17b9579dd338dc2e54
- #141: f7fec70daf65bb437347f2c78b384a7ace9de497
- #142: 6acd994a71e5cf7a6662c4f9fd47ca994832cbd7 (dependency pin advanced to b246e8c7bd9ddf97d2d286402202b14e9e48e595)
- #143: 54055138f5462bb5758e901babf2f38904f11c09
- Original synthetic base: fee257b9ca04bfdbc64040d29c889ddd03acf394

Previous #143 snapshot already combines the overlapping typed and PyRomb codec/test semantics; this new test-only tree updates the non-overlapping owned code/test blobs. CI (if run) is a **software** test and not proof of native RORB CMD 6.44 execution or a production merge.

Tests should verify import / persisted edit / selected events / export / relocate / exact emitted PAR reparse / authentic PyRomb adapter / canonical ryan-tools outputs, including source and isolated-wheel verification.
