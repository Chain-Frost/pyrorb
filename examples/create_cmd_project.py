"""Create one distributable CMD example project from the existing public typed model.

Run from the repository root: py -3.14 examples/create_cmd_project.py
The output uses exclusive creation and never overwrites an existing project.
"""

from pathlib import Path

from runoff_routing.engine_types import EngineSelection
from runoff_routing.project_json import EmbeddedRun, Project, write_project
from runoff_routing.rorb_model import RunModel, from_json


def main() -> None:
    """Write the only example project; do not launch any numerical engine."""

    source = Path(__file__).absolute().parent / "synthetic-run.json"
    model = from_json(source.read_text(encoding="utf-8"))
    if not isinstance(model, RunModel):
        message = "The example must contain a complete S1 RunModel"
        raise ValueError(message)
    write_project(
        Path("cmd-example-project.json"),
        Project("cmd_example", "explicit", EmbeddedRun(model), engine=EngineSelection.for_engine("python-cmd")),
    )


if __name__ == "__main__":
    main()
