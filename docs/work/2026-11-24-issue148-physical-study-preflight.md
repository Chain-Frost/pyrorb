# Issue #148 physical-catchment study: source-admission preflight — 24 November 2026

**Status: blocked on genuine matched physical inputs.** This is a bounded, read-only study-protocol preflight, not a new Monte Carlo engine, sampled event, routed calculation, accepted native profile, or conclusion about the sufficiency of 1,000 simulations. The original independently reviewed #148 synthetic populations and results remain unchanged.

## Purpose and output

The machine-readable template at [physical_study_preflight.json](../research/issue148/physical_study_preflight.json) declares the information needed *before* a physical RORB/Python study can be preregistered. The standard-library tool at [mc_physical_preflight.py](../../repo-scripts/mc_physical_preflight.py) validates its shape and explicit probability accounting, then reports separate blockers for:

1. A **restricted 1%–50% rainfall-domain** source-backed Python routing pilot (diagnostic only).
2. An **independent native/Python population** comparison, requiring an admitted native method/reader/weights and independent native replications.
3. **Exact native-event replay**, which additionally requires actual recovered effective inputs.
4. A single-production-run **1,000-event restricted-domain stability** study, with prespecified peak error margins, disjoint reference/confirmation plans, independent Python streams and joint uncertainty allocation.
5. A **full-annual design-flood** result, which also requires separately qualified rainfall tails and a justified annual maximum flood interpretation.

A report status of `external_evidence_review_required` means that all *self-declared fields* are present for **external scientific review**. It does **not** certify their authenticity, qualify a physical catchment or authorise any calculation. The report always says `simulation_authorised=false`, never launches RORBwin/CMD/Python routing, never reads or verifies the referenced source bytes, and never writes a simulated result.

### Running the offline source preflight

```sh
python repo-scripts/mc_physical_preflight.py docs/research/issue148/physical_study_preflight.json
python -m pytest -q tests/test_mc_physical_preflight.py
```

The **checked-in unadmitted template** deliberately returns exit code **1** and five `blocked` lanes. Exit code **2** identifies a malformed/inconsistent declaration. Exit code **0** only means the declared fields are complete *enough to be submitted for external review*; it is never permission to simulate. The emitted JSON is a diagnostic on stdout, without creating files. New protocols remain under external scientific approval and the existing issue #148 experiment/cost restrictions.

## Current evidence assessment and precise missing inputs

The template does **not** invent a physical catchment, project/IFD/TP/loss SHA-256, a named Hydro site, source admission, effective/native observations, a real-catchment tolerance, or a joint uncertainty strategy. Those fields remain null, empty, pending or unqualified. Each eventual identity must be substantiated from approved sources, not merely populated with plausible hashes or a status string.

- The currently adopted nonextrapolated rainfall support `p=0.01..0.50` has exactly **0.49 modelled** and **0.51 unmodelled** annual rainfall-probability mass. The preflight rejects inconsistent declared bounds/masses and never interprets the partial domain as full flood AEP.
- The template's 250-event/60-second pilot cap and 1,000-event candidate are **planning placeholders**, not an authorised native launch, a proved throughput result or a production recommendation. Their inclusion does not substitute for a qualified real-model cost pilot.
- Site/duration/target-AEP declarations require explicit identities. For the future study, define the joint claimed output vector (site × duration × AEP plus duration envelope and any critical-duration claim), site-specific absolute floor in m³/s, selected relative margin, reference uncertainty, genuine seed independence and one joint confidence allocation *before* confirmatory observation. The preflight also demands separate declared joint confidence and whole-run reliability targets, distinct reference/confirmation plan SHA-256s, and exactly 1,000 candidate events before the specifically named 1,000-event stability lane can advance even to external review.
- Native source interpretation is independently blocked. [#150](https://github.com/Chain-Frost/pyrorb/issues/150) and the merged [#218 receipt](https://github.com/Chain-Frost/pyrorb/pull/218) found no suitable nonexecuting **complete exact-effective-input** export among the examined retained surfaces, with the saved PAR excluded for drift. [#191](https://github.com/Chain-Frost/pyrorb/issues/191) and upstream [ryan-tools #334](https://github.com/Chain-Frost/ryan-tools/issues/334) retain the bounded reader/record admission. Missing native method laws/weights/replays cannot be substituted with printed 25-event summaries.

This preflight intentionally does not decide annual-flood design tolerances, a native statistical method or a confirmation sample size. The existing research [synthetic convergence report](../research/MONTE_CARLO_CONVERGENCE.md) already shows populations where 1,000 events succeed and others where they fail under specifically labelled synthetic study settings; **there is no general catchment-based 1,000-event acceptance**.

## Delivery and acceptance boundaries

- Only one **opt-in research-only** standard-library CLI, one machine-readable unadmitted protocol, focused synthetic fail-closed tests and this indexed work note are proposed. No edits to B/E/C source, numerical policies, RORB CMD goldens, source hashes, native readers, published-wheel metadata, project plan formats, scripts for running experiments, or hosted workflows.
- The author ran **20 focused synthetic tests** locally on CPython **3.13.5/Linux** using the exact isolated script/test bytes represented in this PR; no full repository checkout, source/wheel test or native RORBwin process was executed by this local authoring step. Hosted exact-head CI and a fresh independent Codex review are required before any merge.
- The preflight is a **protocol admissibility aid**, not the source of truth for scientific qualification; the broader decision remains under [#148](https://github.com/Chain-Frost/pyrorb/issues/148), [#9](https://github.com/Chain-Frost/pyrorb/issues/9) and their dependency issues. They all remain open. No raw or private native evidence is published.

**Next condition:** supply one independently admissible physical catchment and matched BoM IFD, ARR TP and loss sources with physical site IDs and an eligible supported engine profile. Fill the template only against that source evidence, review the restricted-domain protocol and cost cap, then separately decide whether to authorise a *bounded* Python pilot. RORBwin experiments remain stopped until #150's distinct evidence trigger is met.

### Additional independent-review corrections

The original exact-head Codex review found strict typed-container narrowing, ambiguous duplicate JSON keys and ambient-context Decimal rounding deficiencies. The updated preflight uses validated typed collection boundaries, rejects repeated JSON object members at every depth, bounds numeric token exponent/precision and checks annual-probability masses inside a sufficiently precise local Decimal context. New synthetic tests demonstrate rejection of duplicate fields, extreme exponents and high-precision mass drift even with a caller precision of 3. No statistical distribution, sample stream, event runner or native acceptance is changed.
