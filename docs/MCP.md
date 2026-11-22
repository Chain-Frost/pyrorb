# PyRORB local MCP server for Codex

This optional **local stdio** adapter makes the existing Python/CLI surface discoverable to Codex.
It does not create another engine, a new parser, numerical evidence, a GUI, or a network service.

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

- **Tools:** `list_capabilities`, `describe_capability`, `get_engine_capabilities`,
  `inspect_rorb_file`, `validate_project`, `inspect_event_request`,
  `summarize_arr_results`. All are read-only; the inspector limits source size
  and returns diagnostics/identities rather than raw source bytes or large hydrographs.
- **Resources:** `runoff-routing://catalog` and `runoff-routing://engines`.
- **Prompt:** `plan_runoff_work(task)`, for locating existing APIs and acceptance limits.
- **Discovery states:** `mcp_tool` means callable here; `python_or_cli` means an
  existing API/CLI that has no MCP action adapter; `staged` and `planned`
  are **non-callable placeholders** with links to tracked work.

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
5. After read-only review, add opt-in run/batch/rainfall execution adapters with
   explicit engine choice, bounded output and refusal to overwrite existing files.

The optional dependency uses the official Python MCP SDK **v2** and
`mcp.server.MCPServer`, not the v1 `FastMCP` import.
Local test: `python -m pytest tests/test_mcp_server.py -q`.

No remote hosting, native CMD launch or additional hosted automation is included.
