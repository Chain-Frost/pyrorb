# Issue #175: explicit written-depth rainfall and native event materialization

16 November 2026. Parent #8; original-source qualification #137 remains separate.
Owner selected an explicit compatibility profile rather than changing defaults.
Implementation began on portable export PR #162, pinned dependency head
`280aea19db8b9e52f8115d25f1975b68e537f8de`, with public main ancestor
`d33e139b9f595c53977f68e9c8929327ec20a8b8`. PR #162 subsequently merged;
this branch incorporates main `d61ff42` and preserves its updated export guidance.
The tested product code and tests remain identical to implementation revision
`751e7872731255615568433d97626b59cebfe533` after that documentation reconciliation.

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

Validation executed on Windows 10, Python 3.14.6, at implementation revision
`751e7872731255615568433d97626b59cebfe533`:

- Repository checks, pinned Ruff lint/format and strict Pyright passed; **1,207 tests
  passed, five skipped** (three POSIX-only foreign-path controls and two unavailable
  symlink controls). Independent implementation review found no remaining blocker.
- The clean installed wheel was imported with isolated Python from outside the
  checkout. Wheel SHA-256: `9fb246153b5fc78a0b919e9d5ff2dc69cdb527e72957646968ee10928ac49ce3`.
  Source/wheel package-file fingerprint: `d056ec527db5ebdda1cf6dcad1f00ad5cdc643f9835f5448058e5db4a04189f2`.
- The existing fresh public CMD probe produced identical complete 50-case source
  and wheel Q/scalar/status/identity reports: **50 printed passes, 48 complete scalar
  passes and two preserved undefined zero-flow peak-time incompletes**. These were
  fresh Python calculations against retained CMD observations, not new native runs
  or authenticated-snapshot replay. Full-index preflight verified all 254 indexed
  files and all 50 cases in the actual fixture checkout.
- Private original-source checks matched all 60 event identities, timesteps and
  patterns; all **1,320 reconstructed written-input increments matched exactly**.
  Six complete routed source/wheel reports were byte-identical. High-level 18/24h
  runs retain shorter generated dry tails; separately labelled explicit-event
  replays used the original 200-increment horizon. Neither is routed RORBwin acceptance.
- Two bounded events were run once from source and once from the isolated wheel
  through actual pinned CMD 6.44. All four qualified runs returned 201 ordinates
  and passed the existing comparator's unchanged printed-interval allowance.
  Prepared PAR/CATG/STM files and package manifests matched source versus wheel;
  original source inputs remained unchanged. These two new cases retain incomplete
  scalar and native physical-site bindings. One earlier diagnostic run was correctly
  rejected because the caller requested `Hyd0001` instead of observed `Hyd001`;
  its receipt was retained and the plan revised before four qualified calculations.
  Total: five CMD processes, zero new RORBwin processes. This is bounded native
  adapter integration, not the broader moved-package/verbosity campaign of #143.

Full original-source receipts, immutable bindings and independent audit remain in
the private evidence workspace; the public repository contains synthetic controls
and this sanitized result only. Native ARF arithmetic parity is not assessed;
original runtime RORBwin effective arrays remain unmeasured. No universal formatter
tie or routed RORBwin equality claim follows from the matched written inputs.

No native reference, tolerance, existing method default or hosted automation is changed.
This work does not close #137/#8/#5 or establish routed RORBwin equivalence.
Next action: review this bounded implementation PR; merge requires owner approval.
