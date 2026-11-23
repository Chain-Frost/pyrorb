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

## Agent contract

- **Read-only tools:** `list_capabilities`, `describe_capability`, `get_engine_capabilities`,
  `inspect_rorb_file`, `validate_project`, `inspect_event_request`,
  `summarize_arr_results`. Inspection returns bounded metadata, not full source bytes or hydrographs.
- **Opt-in compute/write tools:** `run_project`, `run_project_events`, `prepare_arr_design`.
  These delegate to existing engine/project/ARR APIs. Each defaults to `allow_write=false`,
  and requires `allow_write=true`, an unused output filename or prefix and an existing parent directory.
- **Resources:** `runoff-routing://catalog` and `runoff-routing://engines`.
- **Prompt:** `plan_runoff_work(task)`, for locating existing APIs and acceptance limits.
- **Discovery states:** `mcp_tool` means callable here; `python_or_cli` means an
  existing API/CLI that has no MCP action adapter; `staged` and `planned`
  are **non-callable placeholders** with links to tracked work.

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

No remote hosting, native CMD launch, GUI or additional hosted automation is included.
