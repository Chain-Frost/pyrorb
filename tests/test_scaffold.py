"""Scaffold checks only; these tests establish no hydrological equivalence."""

import tomllib
from pathlib import Path

ROOT = Path(__file__).absolute().parents[1]


def test_only_owner_approved_hosted_workflow() -> None:
    workflow_dir = ROOT / ".github" / "workflows"
    assert workflow_dir.is_dir()
    assert {path.name for path in workflow_dir.iterdir()} == {"quality.yml", "publish.yml"}


def test_python_target_and_strict_typing() -> None:
    with (ROOT / "pyproject.toml").open("rb") as stream:
        config = tomllib.load(stream)
    assert config["project"]["requires-python"] == ">=3.11"
    assert config["tool"]["pyright"]["typeCheckingMode"] == "strict"


def test_namespace_is_present() -> None:
    assert (ROOT / "src" / "runoff_routing" / "__init__.py").is_file()
    assert (ROOT / "src" / "runoff_routing" / "py.typed").is_file()


def test_canonical_reader_has_no_upstream_distribution_dependency() -> None:
    with (ROOT / "pyproject.toml").open("rb") as stream:
        project = tomllib.load(stream)["project"]
    requirements = [*project["dependencies"]]
    for extra in project["optional-dependencies"].values():
        requirements.extend(extra)
    assert all("ryan-rorb-readers" not in item and "ryan-tools" not in item for item in requirements)
    assert all(" @ " not in item for item in requirements)
    source = ROOT / "src" / "runoff_routing"
    assert all("from ryan_library" not in path.read_text(encoding="utf-8") for path in source.rglob("*.py"))
