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

## Software review correction (14 November 2026)

Owner-approved transfer to PR #77: software commit
`5f8e790e31bc7f8a91a2ad302239092d120e3ef7` rejects an existing result file or
symlink before CLI dispatch, avoiding an unnecessary computation/native launch.
Final result writing still uses exclusive creation. The focused regression checks
that dispatch is never called and prior result bytes remain unchanged.

Refreshed Windows/Python 3.14.6 local quality: **695 passed, 1 skipped**, Ruff
lint/format passed, strict Pyright **0 errors / 0 warnings**. The existing skip
is unavailable file-symlink creation. The software revision's wheel was built
and exercised outside the checkout. Hosted checks must be attributed to the new
remote head separately. Private native receipts and inputs are not transferred.

The original review identified `implementation_revision="0.0.0.dev0"` as
insufficient exact-build provenance. The follow-up records a versioned,
deterministic fingerprint of all installed Python package source bytes,
separately from package version. An optionally supplied wheel is accepted as
the running wheel identity only after its package-source bytes match the
installation exactly. Missing or altered wheels fail before native launch;
the exact wheel SHA-256 is then retained in the result. This is not a Git
commit hash, so exact Git source attribution remains in the validation
receipt, not in an invented package field. Independent software review of
this correction and exact-head Windows/source/wheel tests are required.
The initial native-acceptance status above describes the original implementation
handoff; later local evidence is held privately and is not a general acceptance
claim. PR #77 remains draft; numerical equivalence remains unaccepted.

## 2026-11-15 — Review failure-path corrections (pending exact-head checks)

Independent review at `e7e2415806d80eaaabfab4704101f8b69cb3f8f3`
identified two reproducible error-path defects, and the Codex inline review
identified a third relative-native-executable path defect.

- Reject encrypted ZIP wheel entries before reading them. Translate ZIP
  reader failures into `invalid_input/wheel_identity` rather than allowing
  an uncaught exception. A manufactured encrypted-entry regression proves
  that native execution is not dispatched.
- Catch invalid native configuration types in the CLI and return the
  documented exit status 2, without a traceback, output write or engine launch.
  Negative tests cover a JSON array, wrong print-column type and wrong
  timeout type.
- Preserve relative executable configuration at the API boundary but write
  its `Path.absolute()` spelling to the temporary S0 capture specification.
  An isolated mocked CMD run verifies that the executable is found and the
  source-capture identity stays intact.

The owner's separately recorded [private native acceptance PR #62](https://github.com/Chain-Frost/runoff-routing-investigations/pull/62)
retains the latest exact-head 201-row token-matched native receipt. This
software-only fix does not launch RORB, modify native inputs/captures, adjust
numeric tolerances or claim Python/CMD equivalence. The latest Windows
CI, source and installed-wheel checks must be attributed to the new PR
revision separately before recommending integration. Do not merge or close
issue #74 on the basis of software-only validation.
