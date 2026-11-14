# 2026-11-14 — Three-engine computation contract and native CMD adapter

**Issue:** [#74](https://github.com/Chain-Frost/python-runoff-routing/issues/74)
**Scope:** Common project/API/CLI selection, structured engine result, opt-in
native CMD 6.44 via existing S0 capture, manufactured tests, schema migration.
**State:** Reviewable contract implementation; neither numerical nor local
native Windows acceptance is claimed.

- Preserve `run_model` as the existing bounded pure Python S2 kernel and
  `run_project` as a legacy Python-only convenience API. The new typed
  `run_engine_project` dispatches `python`, `python-cmd`, or `rorb-cmd`.
- Project schema 2 stores a numerical engine/profile separately from rainfall
  profile. Existing schema 1 imports deterministically as
  `python/engineering-v1`; API/CLI overrides record stored and effective choices.
- `python-cmd` selection returns `unavailable_engine` until #75 qualifies and
  integrates a complete event backend. No private repo or native binary is
  required for Python installation.
- `rorb-cmd` is opt-in, fingerprint-verified, local-only, one-ISA/burst
  `cmd-6.44`. Uses S0 staging, timeouts, identity/inventory checks and S1
  complete report inspection. No accepted internal state is inferred.
- Common outcomes preserve event/source/parameter/output provenance,
  ordered requested site IDs, original native time/print tokens and
  structured failure reasons. Native-site association remains caller-asserted.
- No arithmetic changes, ARR forcing changes, tolerance changes, native
  campaigns, automatic merge, publication or hosted native execution.

**Verification:** see draft PR check runs for pinned source/wheel quality.
Ordinary regression is a source-quality gate only. Real Windows native CMD
acceptance and independent review of physical HydNNN print-site mapping
remain **outstanding**.

**Next actions:** obtain independent contract review with the clean-data
owner (maintained case/result format), integrate #75 only after candidate
qualification and validate #6 independently; execute an explicitly bounded
real-Windows native one-case receipt with original executable hash and
physical print mapping before native-adapter acceptance.
