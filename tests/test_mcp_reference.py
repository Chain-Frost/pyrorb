"""Versioned MCP discovery resources use existing public APIs as their source of truth."""

from __future__ import annotations

import asyncio
import inspect
import json
from importlib import import_module
from pathlib import Path
from typing import cast

from jsonschema import Draft202012Validator
from mcp import Client

from runoff_routing.arr_design_batch import read_design_config
from runoff_routing.mcp_catalog import CATALOG
from runoff_routing.mcp_reference import API_AREAS, EXAMPLES, REFERENCE_VERSION, SCHEMAS, api_manifest, schema_manifest
from runoff_routing.mcp_server import mcp
from runoff_routing.project_batch import load_event_request
from runoff_routing.project_json import EmbeddedRun, Project, project_to_dict, project_to_json
from runoff_routing.rorb_model import RunModel, from_json

ROOT = Path(__file__).parents[1]


def test_reference_schema_version_and_example_contracts(tmp_path: Path) -> None:
    assert REFERENCE_VERSION == 1
    example = EXAMPLES["events"]
    event_doc = cast("dict[str, object]", example["document"])
    assert event_doc == json.loads((ROOT / "examples/mvp-events.json").read_text(encoding="utf-8"))
    config_example = EXAMPLES["arr-design"]
    config_doc = cast("dict[str, object]", config_example["document"])
    assert config_doc == json.loads((ROOT / "examples/arr-design-config.json").read_text(encoding="utf-8"))

    model = from_json((ROOT / "examples/synthetic-run.json").read_text(encoding="utf-8"))
    assert isinstance(model, RunModel)
    project = Project("mcp_reference", "explicit", EmbeddedRun(model))
    project_doc = project_to_dict(project)
    assert json.loads(project_to_json(project)) == project_doc

    for name, document in (("project", project_doc), ("events", event_doc), ("arr-design", config_doc)):
        Draft202012Validator.check_schema(SCHEMAS[name])
        Draft202012Validator(SCHEMAS[name]).validate(document)

    request_path = tmp_path / "events.json"
    request_path.write_text(json.dumps(event_doc), encoding="utf-8")
    assert len(load_event_request(request_path)) == 3
    design = read_design_config(ROOT / "examples/arr-design-config.json")
    assert design.engine.engine == "python-cmd"
    assert design.source_sha256
    manifest = schema_manifest()
    assert manifest["validation_scope"] == "structural_discovery_only"
    assert "authoritative_parser" in str(manifest)


def test_api_references_resolve_to_real_functions_and_maintained_files() -> None:
    for entries in API_AREAS.values():
        for entry in entries:
            module_name, function_name = entry.entrypoint.rsplit(".", maxsplit=1)
            function = getattr(import_module(module_name), function_name)
            assert callable(function)
            assert inspect.signature(function)
            assert inspect.getdoc(function)
            assert (ROOT / entry.guide).is_file()
            assert (ROOT / entry.tests).is_file()

    documented = {item.name for item in CATALOG if item.exposure == "mcp_tool"}
    assert "get_api_reference" in documented
    assert "get_result_summary" in documented
    manifest = api_manifest()
    assert manifest["reference_version"] == 1
    assert "model-editing" in str(manifest)


def test_mcp_resource_uris_and_api_discovery_through_client() -> None:
    async def probe() -> None:
        async with Client(mcp, raise_exceptions=True) as client:
            listing = await client.list_resources()
            uris = {str(item.uri) for item in listing.resources}
            assert "runoff-routing://v1/schemas" in uris
            assert "runoff-routing://v1/examples" in uris
            assert "runoff-routing://v1/api" in uris
            schemas = await client.read_resource("runoff-routing://v1/schemas")
            payload = json.loads(schemas.contents[0].text)
            assert payload["reference_version"] == 1
            assert "project" in payload["schemas"]
            examples = await client.read_resource("runoff-routing://v1/examples")
            content = json.loads(examples.contents[0].text)
            assert content["examples"]["events"]["document"]["schema_version"] == 1
            reference = await client.call_tool("get_api_reference", {"area": "model-editing"})
            assert not reference.is_error
            assert "edit_run_model" in str(reference.structured_content)

    asyncio.run(probe())
