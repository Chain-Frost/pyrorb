# Issue #175: explicit written-depth rainfall and native event materialization

16 November 2026. Parent #8; original-source qualification #137 remains separate.
Owner selected an explicit compatibility profile rather than changing defaults.
Implementation is stacked on portable export PR #162, pinned dependency head
`280aea19db8b9e52f8115d25f1975b68e537f8de`, with public main ancestor
`d33e139b9f595c53977f68e9c8929327ec20a8b8`.

The generator previously supplied the full published adjusted depth, which differs
from the two-decimal totals written in the retained native storm files. The published
equations themselves are not defective. The opt-in `published_arf_stm_2dp` policy
preserves the published calculation, prepares a decimal 0.01 mm HALF_EVEN total,
retains both increment vectors and sends the prepared total to the selected engine.
It does not reconstruct native ARF helpers or declare universal formatter equivalence.
The supported source percentages already have 0.01% resolution, and the bounded loss
profile is pervious project IL/CL without preburst. Unsupported extensions fail explicitly.

The CMD computational kernel is unchanged. Native explicit-event overrides now reuse
the existing portable exporter, preserving original files, verifying emitted models,
and retaining unique prepared input packages alongside genuine capture receipts.
Ordinary unmodified native runs retain their original-source guard. No new engine,
comparator, renderer, private runtime dependency or native executable is included.

Public tests use authored synthetic sources, hand-calculable unit-area depths,
HALF_EVEN ties, unsupported source controls and mocked native execution boundaries.
Original RORBwin data and restricted investigation material remain outside public Git.
The public implementation is independently authored from published rainfall methods
and controlled input/output observations; no proprietary reconstructed code is imported.

Validation in progress: full software stack, isolated wheel, complete maintained
50-case source/wheel reports, private original 60-event prepared-input audit, and a
separately frozen bounded native integration check. Final revisions, actual results,
unexpected skips and remaining reference limitations will be recorded before delivery.
No native reference, tolerance, existing method default or hosted automation is changed.
This work does not close #137/#8/#5 or establish routed RORBwin equivalence.
