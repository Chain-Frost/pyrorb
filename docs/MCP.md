# PyRORB local MCP server for Codex

This optional **local stdio** adapter makes existing Python/CLI functions discoverable to Codex and
adds opt-in, bounded Python calculation tools. It does not create another engine, parser,
numerical evidence, GUI or network service.

## Install and connect

Use Python 3.13 or 3.14 and an environment in which the package is installed:

```sh
python -m pip install -e ".[mcp]"
codex mcp add runoff-routing -- python -m runoff_routing.mcp_server
codex mcp list
```

Use the actual installed interpreter, e.g. `py -3.14` on Windows. An optional
project-scoped `.codex/config.toml` in a trusted checkout can contain:

```toml
[mcp_servers.runoff_routing]
command = "python"
args = ["-m", "runoff_routing.mcp_server"]
```

Do not commit machine-specific Python paths. MCP uses stdin/stdout for protocol data;
server diagnostics must not print to stdout.

For an isolated Windows installation, obtain the interpreter path with
`python -c "import sys; print(sys.executable)"` inside that environment and pass
that absolute executable to `codex mcp add` in place of `python`. This avoids
depending on Codex's inherited PATH. Check the saved command using
`codex mcp get runoff-routing`. If the current agent cannot reload the new server,
start a new session; the subprocess test below independently verifies stdio.

## Accepted dedicated-wheel Codex installation

The 23 November 2026 **operator-reported** local Codex acceptance used:
Codex CLI `0.171.0-alpha.13`, Windows CPython `3.14.6`,
`pyrorb==0.0.0.dev0` from a **dedicated wheel-installed virtual environment**,
MCP SDK `2.3.0`, and source main `83ae609`. The Codex process used an
absolute interpreter path and loaded `runoff_routing` from that environment's
`Lib/site-packages`, not the source checkout or another global installation.

The reported fresh Codex session exited successfully; 12 tools and five
resources were exercised, all six API areas and 19 live signatures checked,
and single/batch/ten-member ARR calculations matched the established Python
API outputs. Refusals, input hashes and protocol-only stdout were checked.
The host's CLI did not provide MCP prompt retrieval, although a separate raw
stdio client retrieved the existing development prompt. This is **local software
integration**, not RORB native-equivalence or scientific acceptance.

To reproduce the robust installation on Windows, build an exact source wheel
and use a dedicated interpreter, not a mutable development editable install:

```powershell
py -3.14 -m venv .local/mcp-codex/venv
$python = (Resolve-Path ".local/mcp-codex/venv/Scripts/python.exe").Path
& $python -m pip install build
& $python -m build --wheel
$wheel = (Get-ChildItem .\dist\pyrorb-*.whl |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
& $python -m pip install --force-reinstall $wheel "mcp>=2.3,<3"
& $python -I -c "import sys, runoff_routing; print(sys.executable); print(runoff_routing.__file__)"
codex mcp get runoff-routing
```

Check the existing registration first. If `runoff-routing` points to an old
interpreter, replace **only that named entry**, after preserving its current
settings, with:

```powershell
codex mcp remove runoff-routing
codex mcp add runoff-routing -- $python -m runoff_routing.mcp_server
codex mcp get runoff-routing
codex mcp list
```

Do not put the machine-specific interpreter path in this repository. Start a
**fresh** Codex CLI session to reload the registration. Updating an existing
`0.0.0.dev0` wheel may require `--force-reinstall`; a correct registration
alone does not prove that the installed wheel contains the latest source.
After source updates, rebuild and reinstall the new wheel deliberately.
Unrelated Codex registrations must remain unchanged.

## Expected MCP refusal diagnostics

The MCP adapter exposes **anticipated** file, input, engine and write-protection
failures as short, stable coded tool errors. For example,
`[write_consent_required]`, `[output_exists]`, `[input_missing]`,
`[invalid_engine_selection]`, `[native_engine_not_available]` and
`[input_limit_exceeded]` include a corrective action. The result retains
`is_error=true`; it is **not** returned as a successful JSON result and must
not be mistaken for `computed_unvalidated`. The SDK returns these messages in
tool `content`, not `structured_content`.

Messages originating from existing parsers are classified but **never echoed**
verbatim: their exception text can include absolute filesystem paths or raw
JSON keys. For example, oversize inputs receive a fixed
`[input_limit_exceeded]` message and duplicate JSON keys receive an
`[invalid_input]` message without reproducing the key. The original Python
API exceptions remain available to a caller explicitly using that API.

Unexpected programming failures remain deliberately sanitised by the MCP SDK;
full tracebacks and raw filesystem exceptions are not disclosed to the agent.
Only the MCP protocol boundary converts expected exceptions; direct Python
calls retain their established exception classes. Client presentation may
still be restricted by the Codex host, so examine the returned tool content
rather than relying solely on an outer UI summary.

## Agent contract

- **Read-only tools:** `list_capabilities`, `describe_capability`, `get_engine_capabilities`,
  `get_api_reference`, `inspect_rorb_file`, `validate_project`, `inspect_event_request`,
  `summarize_arr_results`, `get_result_summary`. Inspection returns bounded metadata,
  not full source bytes or hydrographs.
- **Opt-in compute/write tools:** `run_project`, `run_project_events`, `prepare_arr_design`.
  These delegate to existing engine/project/ARR APIs. Each defaults to `allow_write=false`,
  and requires `allow_write=true`, an unused output filename or prefix and an existing parent directory.
- **Resources:** `runoff-routing://catalog`, `runoff-routing://engines`, and
  versioned `runoff-routing://v1/schemas`, `runoff-routing://v1/examples`,
  `runoff-routing://v1/api`.
- **Prompt:** `plan_runoff_work(task)`, for locating existing APIs and acceptance limits.
- **Discovery states:** `mcp_tool` means callable here; `python_or_cli` means an
  existing API/CLI that has no MCP action adapter; `staged` and `planned`
  are **non-callable placeholders** with links to tracked work.

### Versioned agent references and saved-result inspection

`get_api_reference(area)` returns an allowlisted module/function crosswalk with the
**live Python signature**, authoritative documentation and associated test file.
Available areas: `model-editing`, `interoperability`, `execution`, `rainfall`,
`reporting`, and `verification`. It guides use of the existing APIs; it does
not introduce editing, export or parsing logic into MCP.

The `runoff-routing://v1/schemas` resource contains JSON Schema 2020-12
**structural discovery** definitions for project, explicit-event and ARR-design
JSON, with a named authoritative Python parser for each. These schemas describe
the outer structure and are deliberately **not complete validation substitutes**:
nested S1 models, file hashes, rainfall method choices, event failure isolation
and physical/numerical support must still pass the package's original validators.
A schema match never implies that the engine can execute the input.

`runoff-routing://v1/examples` gives the real checked-in synthetic project
generation steps and the event/ARR example payloads. Contract tests ensure the
embedded event/ARR examples match the files under `examples/`. No authentic
engineering rainfall or native parity is claimed. `runoff-routing://v1/api`
provides the same maintained module crosswalk in one resource, while
`get_api_reference` is preferable for one area at a time.

`get_result_summary(path)` inspects an **existing** JSON report, returning
file SHA-256, result kind, status counts, failed-event identifiers, engine
selections and existing qualification labels where supported. It recognises
single project results, event batches, persisted ARR effective-population
records and persisted ARR summaries. It refuses unknown formats, non-finite/
duplicate JSON fields and files larger than **64 MiB**, and rejects summary
responses larger than **32 KiB**. It does not return full hydrographs or modify
any file. This is a bounded metadata projection, **not
a second numerical comparator, parser certification or scientific acceptance**.

Example local Codex workflow: list capabilities, request the `model-editing`
API area, read the versioned schema and example resources, validate a project,
run it with an explicitly new output path and `allow_write=true`, then call
`get_result_summary` on the generated JSON. Read the full existing report
when detailed ordinates are actually required.

### Execution tool contracts

| Tool | Source | Artifacts | Limits |
| --- | --- | --- | --- |
| `run_project` | Existing project JSON | One new `.json` report | Python or python-cmd only |
| `run_project_events` | Project + versioned event request JSON | New `.json`, `.csv`, `.txt` | Maximum 500 events |
| `prepare_arr_design` | ARR/BoM deterministic config JSON | New `.effective.json`, `.events.json`, `.json`, `.csv`, `.txt`, `.summary.txt` | Existing bounded duration/AEP axes; **prepares and routes** its events |

The established output writers use exclusive creation and reject overwrites. Existing batch/ARR
writers roll back files they created if a write fails. Results may contain invalid/unsupported
events; the MCP summary cannot be substituted for the full persisted reports. The input model,
source files and rainfall sources are never modified. An ignored `.local` directory is
recommended for disposable results; the directory must be created separately.

MCP execution deliberately **cannot launch native `rorb-cmd`**. If the stored project
or ARR config selects it, the tool refuses to run. For native execution use the explicit
CLI with a verified local native configuration. A deliberately overridden project engine
must be identified as such in the output. No silent fallback occurs.

**MCP availability is not engineering qualification.** Parsing, source-hash/structural
validation, `computed_unvalidated`, native equivalence and physical accuracy are distinct.
The new-project default remains `python-cmd/cmd-6.44`, independent `python/engineering-v1`
is explicitly selectable and intended as the future default, and `rorb-cmd` is a
separately installed native option. No automatic engine substitution is permitted.

The catalogue is a *navigation* index, not another feature matrix or regression
comparator. For support/qualification consult [CMD feature matrix](CMD_FEATURE_MATRIX.md),
[current status](STATUS.md), [engine contract](ENGINES.md), [quickstart](QUICKSTART.md)
and [backlog](BACKLOG.md).

## Adding an MCP action

1. Implement and validate the business operation in its existing module, with established
   source hashes, exclusive-create output and input validation still enforced.
2. Add one explicit capability with its real Python entry point, current documentation,
   limitations and issue/PR. Keep unmerged features `staged`.
3. Add a typed, narrow adapter to `mcp_server.py` **delegating** to that API.
   Do not add arbitrary shell execution, dynamic Python imports or a second parser.
4. Test via an in-memory MCP `Client(mcp)`; check tool schemas, errors,
   read-only behaviour and evidence/status distinctions.
5. For additional compute tools, require explicit opt-in, bounded work, exclusive
   new outputs and a status/provenance response. Keep unmerged features non-callable.

The optional dependency uses the official Python MCP SDK **v2** and
`mcp.server.MCPServer`, not the v1 `FastMCP` import.
Local test: `python -m pytest tests/test_mcp_server.py -q`.

Full MCP check:
`python -m pytest tests/test_mcp_server.py tests/test_mcp_reference.py tests/test_mcp_results.py tests/test_mcp_stdio.py -q`.
The stdio test starts a separate server process with the current interpreter,
reads every resource and the prompt, calls all API-reference areas, and compares
complete synthetic single-event, successful/incomplete batch and ten-member ARR
artifacts with the existing Python APIs. It also checks opt-in, no-overwrite,
native refusal and malformed/oversized input handling. These remain software
checks, with no native process launch or scientific acceptance claim.

No remote hosting, native CMD launch, GUI or additional hosted automation is included.
