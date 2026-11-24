# Canonical reader ownership transfer — 24 November 2026

Owner-approved [#231](https://github.com/Chain-Frost/pyrorb/issues/231) supersedes standalone-reader release preparation. Source: [ryan-tools permanent main 20054b3](https://github.com/Chain-Frost/ryan-tools/tree/20054b30b57b5c9a74ec4c8255265bdfcc28f373/ryan_library/functions/RORB), Sustainable Use License 1.0. The six source blobs were compared across repositories before integration and are byte-identical at this transfer checkpoint. The PyRORB root licence remains applicable; no third-party code is relicensed.

| Canonical module | Original and transferred Git blob |
| --- | --- |
| reader_types.py | d1d3a5b3953d52ba1d1d36cf902280b769b0f5af |
| readers.py | 8c066381caf05c8f55e009ca75d67335b71be752 |
| output_reader.py | 6622737d293c612be1f02e36fd6ff556158d8aa0 |
| parameter_reader.py | 1029473a9e011df891555ff1d5e270c0bc12d8c7 |
| result_readers.py | 64f474ab439a7c15f31f9931088109e461eb9149 |
| associations.py | c7648fef069197493a0f99ec3b31520e8608c506 |

All six are now under `src/runoff_routing/rorb_readers` with relative internal imports unchanged. Downstream PyRORB callers use the local canonical reader. No solver, grammar, token, rounding or scientific status change is intended. No runtime dependency on ryan-tools or standalone ryan-rorb-readers remains. PyRomb remains an explicit separate pinned PR requirement for edited CATG export.

Dependency-light synthetic tests transferred from ryan-tools `tests/functions/RORB/test_readers.py`; dataframe-only assertions stay in the ryan-tools compatibility suite. The original 6.45 (490-event) and 6.52 (640-event) parser acceptance tests transfer with their existing source/manifest rules. The existing quality workflow checks the public ryan-tools-test-data commit `4535ff86ea978666b990748d72d927695be2158c` in its Python 3.11 lane, using a sparse RORB checkout under ignored `.local/reader-test-data`; other lanes and offline local runs may explicitly skip unavailable public fixture-only tests. No new private file, fixture bytes, executable or manual has been copied. Source and isolated-wheel test coverage remains required. Existing 50-case CMD register/fixtures remain unchanged.

## Outstanding gates

- Exact-head independent review, Ruff/strict Pyright, four-version Windows CI, source/installed-wheel reader and original CMD regression acceptance. Do not claim acceptance until completed.
- Reconcile held activation #220 and qualify actual release wheel/sdist; preserve one-shot security and separate owner approval. No standalone reader publication. No PyRomb upstream changes.
- After the PyRORB index release, ryan-tools replaces the six old source modules with explicit re-exports and adds the exact qualified published PyRORB dependency. Pandas convenience wrappers and plotting stay in ryan-tools. Retire unused standalone package/publisher after consumer acceptance. No dependency cycle; only during staged transition does the old immutable source remain available.
- Native MC parser software is [#232](https://github.com/Chain-Frost/pyrorb/issues/232), transferred from ryan-tools #334. No native grammar invented or scientific acceptance claimed.
