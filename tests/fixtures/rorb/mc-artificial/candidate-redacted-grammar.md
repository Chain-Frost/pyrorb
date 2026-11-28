# Private candidate: bounded RORBWin MC printed-report grammar

Status: private candidate; explicit owner/custodian sharing permission remains pending. Independent derivative-review disposition is recorded separately. Keep this document, the artificial report and its expected-value sidecar private. No publication or product implementation is authorised by this document.

## Evidence class and limits

This specification describes structure directly inspected in one authenticated retained RORBWin 6.52 report. Its source fingerprint, original line/field values, approval records and private locators are intentionally absent here and retained in a separate private audit. It is a printed-record grammar, not an effective-event, statistical-method or engineering qualification. A version banner alone never authenticates an executable or run.

The accompanying artificial report is **not native output**. All source-specific metadata, settings and measured/printed result values are replaced with authored values. Fixed format/version/copyright words, blank-line/separator layout and count/ordinal/percentile scaffolding remain structural. Artificial duration and output ordinal differ deliberately; they do not establish a second native duration or site. No native program, routing, sampler or Monte Carlo was invoked to make the fixture. Its values are for lexical/structural tests, not hydrological or inference tests. Diagnostic/summary values are authored separately from the artificial event factors and are not asserted to be their statistical transforms; this fixture is not a statistical-consistency golden. Common structural constants and coincidental numeric-token overlaps are not copied source measurements.

The exact newer line map referenced by the upstream progress comment has not been supplied in this task. The independent original audit verifies the existing older printed-field map and supplementary original-line bindings. Do not claim that the separate newer map was reviewed unless its exact bytes are supplied and checked.

## Document recognition and source retention

- First stripped line: `RORBWin Monte-Carlo Run Summary`. This distinct banner should be considered explicitly in the canonical `read_rorb_bytes` dispatcher before generic content fallbacks. Do not reinterpret ordinary batch reports as MC because they contain Run/TP fields.
- Retain original bytes, exact decoded lines, selected encoding and document digest using the existing reader model. The inspected profile has CP1252 text and CRLF records, including a non-ASCII superscript unit glyph. A proposed implementation must use the existing lossless decoder; this observation does not establish all native report encodings.
- Banner underline, program version/copyright, date and named settings precede one duration block. Date, file/reference text and setting descriptions are display provenance, not event identity or effective-input proof. Never follow a displayed path.
- Only one duration block and one peak column are source-evidenced. Multiple-duration/multiple-peak/cohort layouts, alternate native versions, missing headers, failures, representative/extraction records and full hydrographs are **unavailable/unadmitted**, not silently supported through extrapolation.

## Ordered sections

1. Preamble: fixed MC banner/version labels, run-date display, catchment-reference and source/policy descriptions, TP-source description, availability row, routing/loss setting echoes.
2. Duration: `Results for Storm Duration of <duration> hour` and underline. Preserve displayed units and original token; no integer-hour conversion guess.
3. Model-check display: `Rorb model check run completed OK:` followed by labelled counts/time-step displays. These are displayed run checks, not a reconstructed complete effective event.
4. Allocation declaration: `Monte-Carlo sampling undertaken using <runs> runs over each rainfall interval,` then `where the rainfall distribution is discretised into <divisions> intervals.` Treat these as printed positive integer counts. They establish table-shape checks, not probability weights or stream independence.
5. Label/description legend, including separate Div/Run, a probability legend label, Depth/TPat/I.L./IL_F/LR_F definitions and `Peak <ordinal> <description>`. Bind a peak ordinal only within its report; do not invent a physical site.
6. Individual-table header and contiguous rows, terminated by the following diagnostic section, with whitespace-only lines preserved. Require declared unique complete division/run grid for this admitted subset; reject duplicates, missing rows, malformed/trailing unexpected records and ambiguous boundaries. No successful-row renormalisation.
7. TP diagnostic, marker `>>> Distributional check on temporal patterns`, then `Pattern#:` ordinals and `Freq%` values. Separate diagnostic percentages from per-event sampling weights and source EventIDs.
8. Loss percentile diagnostic, marker `>>> Exceedance frequency percentiles check on losses (prior to factoring)`, then `Percentile   Initial Loss` and printed pairs. Preserve the diagnostic wording/direction. Do not infer its percentile algorithm, dimensional loss units or native inverse/sampler from these rows.
9. Loss histogram diagnostic, marker `>>> Frequency distributional check on losses (prior to factoring)`, two-line linear/log upper-limit/Freq(%) header, four-column rows and separate total line. Preserve all four raw tokens and totals; no native probability-law inference.
10. Flow analysis, marker `>>> Analysis of flow results`, report-local peak min/max/description row. Summary extrema are not additional individual events.
11. Selected-probability summary, heading `Peak flows for selected AEPs (* indicates value unreliable, ie bounded by interval contributions to AEP > 20% total)`, then No./AEP(1inY)/Peak header and rows with optional attached `*` marker. These published summary values are not sampled-event peaks or a verified generalized inverse. Preserve warning marker and wording exactly.
12. Labelled `Elapsed Run Time (hh:mm:ss)` display. Retain as printed metadata only; fixture time is fictional and no timing pilot is performed.

Blank lines and separator underlines have no scientific meaning but must not disappear from source retention. The fixture intentionally preserves their full arrangement; do not claim arbitrary reordering, wrapped headers or optional section omission are native-qualified. Truncated mandatory sections or unexpected sections require explicit partial/invalid/unsupported status and diagnostics, never a plausible complete event ledger.

## Individual table: exact field meaning

Header spelling is `Div  Run ... AEP  Depth TPat ... I.L.  IL_F  LR_F ... Peak <ordinal>`.

| Position | Printed field | Observable representation and limit |
| --- | --- | --- |
| 1 | Div | Positive printed division ordinal, not a probability mass. |
| 2 | Run | Positive run ordinal within division, not global sample/TP identity. |
| 3 | AEP | Preserve exact integer/decimal token and label. Legend uses ARI while summary uses AEP(1inY); unit/reciprocal/AEP/EY interpretation remains unavailable. No conversion to an exact probability. |
| 4 | Depth | Rounded printed stochastic burst depth; mm explicitly appears in legend. Not full-precision gross or effective rainfall and not an increment array. |
| 5 | TPat | Native duration-local pattern rank. Original source EventID/ordinal mapping unavailable. |
| 6 | I.L. | Printed stochastic factor applied to initial-loss parameter, per legend. Not storm IL in mm or an identified primitive random draw. |
| 7 | IL_F | Printed deterministic ARI-dependent initial-loss factor. Does not recover the native transform or exact effective loss. |
| 8 | LR_F | Printed deterministic ARI-dependent loss-rate factor. Not a full effective CL record. |
| 9 | Peak | Rounded printed peak for one report-local ordinal. **No discharge unit is explicitly printed in this report**; units and physical site binding remain unavailable absent separate admitted evidence. |

Use the printed `Peak <ordinal>` label and description independently of any displayed model path. The canonical reader can expose a report-local output column without promoting it to an authenticated physical site. Future #191 adaptation must require independent external binding where its contract requires physical units/site identity; do not map a local ordinal to an assumed m3/s site.

## Lexical and precision rules

Observed table numeric spellings are unsigned integer and unsigned decimal tokens, separated by horizontal whitespace. Do not claim native evidence for exponent, signed, nonfinite, overflow-star, missing/failure or alternative-locale spellings. Synthetic adversarial variants may test rejection of these unadmitted forms. Retain the entire raw token and its exact source line/column span; parse finite decimal values via canonical `source_tokens`/`source_decimal`, never binary-float normalization. Division/run/TP ordinals require integer syntax.

The inspected individual probability column mixes decimal and integer display forms; precision must follow each token, not one global decimal-place rule. Depth and factor/peak columns also retain their original lexical decimal places. Printed decimal resolution is observable; native rounding/truncation mode and unprinted precision are **not**. A half-unit interval is only conditional on an explicitly named formatting assumption. Printed zero is `rounded_print`, not proof of exact zero, successful routing, failure or absent mass.

In published summary rows, `*` is a separate unreliability flag attached to the peak token; retain full original token and warning while separating its finite numeric component. The marker is source-evidenced only in that summary section, not in individual rows. Do not discard unreliable rows or call them exact events.

## Identity, unavailable fields and implementation boundary

Retain document source identity, line and duration context with division/run and report-local peak ordinal. Cohort, replication and scenario identifiers are external provenance, not inferred from date, filename or a row count. Division/run pairs can repeat in other contexts. Preserve source TP EventID, native rank, Python sample ID and printed summary ordinal as distinct kinds.

Explicitly unavailable from this grammar alone: physical output-site binding; peak discharge unit; probability interpretation; exact sampled AEP/depth; original TP EventID; rainfall/ARF/preburst/effective-loss arrays; per-event weights; RNG stream/independence; native frequency law; representative/extraction/failure grammar; alternate duration/peak layouts. No scientific F1–F6 qualification is required to implement admitted printed records, and parsing must not claim those qualifications.

After independent derivative verification **and explicit sharing approval**, implement one bounded addition inside `runoff_routing.rorb_readers`, reusing `RorbDocument`, `Section`, `Diagnostic`, exact source tokens/decimals and current dispatcher. Preserve all ordinary readers and coordinate active reader changes. Add focused positive/adversarial/source-isolation/wheel checks and independent PR review before merge consideration. Do not create a standalone reader, second parser framework, new numerical method or public private-source fixture.

Then #191 Phase 2 may consume the canonical printed records through the existing comparison evidence contract. Do not weaken Phase 1 readiness rules: absent units/site binding, weights, exact effective state or probability interpretation must continue to produce field-level unavailable/non-comparable lanes. Scientific qualification and publication permission are separate gates; neither can be inferred from successful lexical tests.

## Proposed shareable packet and gate

Candidate files only: this redacted specification, `candidate-artificial-mc-report.out`, `candidate-artificial-expected.json`, and an approved redacted provenance note. The original source, source hashes, paths, original field/line map, generator and detailed independent audit are excluded. Even these artificial structural derivatives remain private until owner/custodian scope is explicitly confirmed. A clean independent review does not itself grant redistribution rights. No public PR or #232/#191 product implementation starts under this proposal before both gates pass.
