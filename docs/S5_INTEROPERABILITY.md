# RORB CMD interoperability — current capability and evidence

The merged #138–#141 CLI/Python/text-file implementation supports PAR-led
import of supported RORB CMD documents, SHA-verified modern graphical
CATG (including characterised graphical `.cat`) and DESIGN STM, source-role
overrides, schema-3 effective-model edits, and portable per-event native
CMD package export. See the [quickstart](QUICKSTART.md),
[PAR projects](PAR_PROJECTS.md), [native export](NATIVE_CMD_EXPORT.md)
and [#143 evidence record](work/2026-11-15-issue143-s5-acceptance.md).
There is no GUI deliverable.

The original files remain byte-exact in staged project copies. Edited
effective models are independently resolved, and exported PAR/CATG/STM
are reparsed with relative self-contained dependencies. Changed CATG
requires a supported graphical drawing and the pinned external PyRomb
writer; unsupported changes fail closed. The merged native adapter
rejects original CATG/STM execution when these do not match edited
effective catchment/storm data. No engine is silently substituted.

## Native and report acceptance

[Five real Windows RORB CMD 6.44 native executions](work/2026-11-16-issue143-native-acceptance.md)
passed using actual relocated emitted `model.par` files without Python
or access to original project/source directories. All five native
processes exited 0 without timeout; all 15 emitted input pre/post
hashes match. Observed verbosity levels 1/2/3 produced genuinely
different reports. The now merged
[#142 canonical ryan-tools reader](https://github.com/Chain-Frost/python-runoff-routing/pull/165)
retained 1,005 native hydrograph ordinates, clocks and source tokens.

The canonical reader integration is **merged**. Owner-authorised authentic RORBWin 6.45 alternative reader acceptance passed 490/490 associations, preserving 1,472 original/distributed file identities. The older distinct 420-event source corpus was not located and is not claimed as validated. The five installed canonical reader results
retain `partial` warnings and unverified completion/sections.
Original physical print-site identification and matched edited-event
references remain unavailable: numerical equivalence is
**incomplete/not_assessed**, not passed. No native executable/raw evidence
was committed to the public repo; the complete ZIP remains locally
held under the SHA-256 recorded in the receipt. Scientific/numerical gate #5 and physical-site/representative-selection qualifications remain open. #142's software reader-population acceptance was admitted with the explicitly identified 490-event alternative; it does not establish historical 420/420 or physical/numerical equivalence.

Unknown PAR dialects, RORBwin saved-PAR editing, plain computational CAT,
combined DAT, general external rainfall source conversion, unqualified
representative/critical-duration rules and any GUI are excluded.
Source-exact round trip, semantic edited model, runnable native package,
report fidelity and numerical/physical parity are distinct contracts.
