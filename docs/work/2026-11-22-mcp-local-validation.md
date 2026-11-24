# Local MCP integration and validation — 22 November 2026

Status: dated 22 November source/wheel review of the then-open PR stack; see the later actual Codex CLI acceptance below.
Owner: local development agent. Review/update date: 2026-11-22.

## Identity and scope

Branch: `feat/codex-mcp-discovery-results-20261122`, based on
`9ecf1f3d43808d929147f8644c6d2615ca1253bd` ([PR #211](https://github.com/Chain-Frost/python-runoff-routing/pull/211)),
stacked on [#209](https://github.com/Chain-Frost/python-runoff-routing/pull/209)
and [#208](https://github.com/Chain-Frost/python-runoff-routing/pull/208).
The commit containing this receipt records the final test/documentation changes.

Personally executed on Windows 10 build 19045, CPython 3.14.6 x64,
distribution `python-runoff-routing==0.0.0.dev0`, MCP SDK 2.3.0.
The source environment is an isolated editable development installation under
ignored `.local/mcp-validation/venv`. A separate installed-wheel environment
outside the checkout proves imports from its own `site-packages`, with `-I`.

Package-code identity (identical source and installed wheel):
`package-code-v1-sha256:4602c7ac8887348c6f85ea1ba2f3904f7f091e340e419979fd1d2e69a8834e07`.
Wheel SHA-256:
`40af0325af3f5d7d6feadb64eb842d8244c25b4ec8876b7ccda1bf13484bfe78`.
The existing `verify_installed_wheel` independently matched every package source
member to the wheel. Neither the wheel nor machine-specific configuration is committed.

## Protocol and discovery

Registered `runoff-routing` using `codex mcp add` and the actual isolated
interpreter, then verified the saved stdio command with `codex mcp get`.
Other MCP registrations were preserved. The current agent session did not reload
the tool registry; connectivity was independently verified by subprocess clients.

The separate SDK client initialized and discovered **12 tools, five resources,
one prompt**. It read every resource and retrieved `plan_runoff_work`.
A second raw JSON-RPC subprocess probe negotiated protocol `2025-11-25`, checked
every stdout line as a JSON-RPC message and exited zero. No ordinary stdout
output corrupted the transport.

All six API-reference areas resolve to live signatures, maintained guides and
test owners: model editing, interoperability, execution, rainfall, reporting
and verification. Project construction and exclusive-create writing were missing
from that crosswalk and are now explicitly linked to `Project` and `write_project`.
Creation/editing/import/export remain existing Python/CLI operations rather than
new MCP actions. Schemas remain versioned structural discovery aids; original
Python validators retain authority. Checked-in examples and referenced functions,
documentation and tests pass the existing contract checks. Monte Carlo #151 is
still staged/non-callable; deferred structures remain planned.

## Actual synthetic calculations

`tests/test_mcp_stdio.py` starts a separate server in a working directory containing
spaces and Unicode, creates the project through the existing typed API, and runs
the following through MCP:

- Project validation and single-event execution with `python-cmd/cmd-6.44`, plus
  explicit `python/engineering-v1`. Complete JSON reports equal direct API output,
  including hydrographs, event identities and provenance. The CMD synthetic
  example has six ordinates and peak `8.351851463317871 m3/s`.
- Three successful explicit events and a separate three-event request retaining
  its unsupported event. JSON, CSV and text equal direct API serialization;
  the latter MCP aggregate remains `incomplete`.
- One 60-minute / 1% AEP synthetic ARR cell, ten members prepared and routed.
  All six artifacts are byte-identical to direct API output. Result summaries
  inspect single, batch and ARR effective records; paired ARR reporting also works.

Missing paths, malformed project/event JSON, unsupported result formats, results
over 64 MiB, missing write opt-in, existing output destinations, invalid engine/
profile combinations and stored/overridden native selections return errors.
Input bytes and existing output bytes remain unchanged; blocked requests produce
no output. Unsupported event failures remain in the full batch reports.
Existing tests additionally cover the 500-event cap and native ARR refusal.
No native RORB executable was launched.

## Quality and original-reference checks

- `python repo-scripts/check_local.py`: repository checks, Ruff lint/format and
  strict Pyright passed; **1,281 passed, five skipped**. Three skips are POSIX-only
  foreign-path diagnostics, two are unavailable filesystem symlink operations.
- Requested three MCP modules plus the new stdio test: **20 passed** from source
  and **20 passed** against the isolated installed wheel. The final inspection
  assertion also passed the affected source rerun (four tests).
- Full indexed-fixture preflight: **50 verified cases, 254 indexed files**.
- Existing `cmd_public_probe.py`: fresh source and wheel execution against the
  authenticated original inputs; **50 printed-Q passes / 19,550 ordinates**,
  **48 reporting-scalar passes, two undefined zero-flow peak-time incompletes**.
  Complete individual source/wheel reports match, including identities, Q,
  scalar differences and statuses; no historical snapshot is treated as execution.

Local raw logs and full reports are under ignored `.local/mcp-validation/`:
`final-quality.log`, `mcp-tests.log`, `wheel-tests.log`, `raw-stdio.json`,
`wheel-identity.log`, `final-preflight.json`, `final-source-cmd.json`, `wheel-cmd.json`.
The full numerical reports use the existing comparator; no new campaign runner
or numerical acceptance policy was introduced. Hosted CI is a separate receipt.

## Conclusion and next action

Ready for routine local Codex development-agent use through stdio, with explicit
write opt-in and the documented Python-engine limits. A fresh Codex session can
load the saved registration. The registered development installation follows
this feature checkout, so retain its branch/environment while using the server.

This validates software integration. It adds no new original-native observations,
general CMD equivalence, rainfall/selection qualification or independent
engineering accuracy. The broader gates in [STATUS](../STATUS.md) and the
[single CMD feature matrix](../CMD_FEATURE_MATRIX.md) remain unchanged.
Next action: review PR #211's validation changes and its existing stack; no merge,
release, publication or additional hosted automation is authorised.

## Subsequent actual Codex CLI acceptance - 23 November 2026

**Status: local MCP installation and software integration acceptance complete.**
This is an operator-supplied result following the 22 November source/stdio tests
above; this documentation update did not repeat that local execution.

The accepted configuration used main `83ae609`, a dedicated wheel-installed
`pyrorb==0.0.0.dev0` environment with Python 3.14.6, MCP SDK 2.3.0 and
Codex CLI `0.171.0-alpha.13`. The global `runoff-routing` registration
points to the environment's absolute Python executable. Source imports
resolve to `Lib/site-packages/runoff_routing`, not the checkout.
A new Codex session exited successfully (0).

The operator exercised **12 tools**, read **five resources**, checked six
API areas and **19 signatures**. The `python-cmd/cmd-6.44` single result
had six ordinates; the event batch was **3/3 computed_unvalidated** and
the ARR population **10/10 prepared/routed**. All persisted single, batch,
and six ARR artifacts matched direct Python APIs. Missing write consent,
existing outputs, native selections, absent/malformed inputs and invalid/
oversized results were refused. Source hashes were unchanged. Server stdout
was JSON-RPC-only. No native launch, push, merge or publication was performed
during the local test.

The Codex CLI does not directly expose MCP prompt retrieval; a separate raw
stdio client verified the prompt. Generic display of expected tool failures
is tracked separately in [#221](https://github.com/Chain-Frost/pyrorb/issues/221).
This limitation does not invalidate the **accepted local software workflow**.

Machine-specific registration paths and the original evidence remain only
under ignored `.local/mcp-codex-acceptance-20261123/`; they are not committed.
See [MCP.md](../MCP.md) for portable dedicated-wheel setup and upgrading.

This closes only the local **software** integration task. Original CMD/native
equivalence, rainfall selection, unimplemented features and scientific or
physical accuracy remain separate outstanding work.
