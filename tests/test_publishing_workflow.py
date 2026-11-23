"""Protect the automated PyPI workflow against broad release triggers."""

from pathlib import Path

WORKFLOW = Path(__file__).absolute().parents[1] / ".github" / "workflows" / "publish.yml"


def test_publisher_requires_only_one_successful_main_ci_merge() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    assert "workflow_run:" in source
    assert "workflows: [Windows quality]" in source
    assert "workflow_dispatch:" not in source
    assert "github.event.workflow_run.event == 'push'" in source
    assert "github.event.workflow_run.conclusion == 'success'" in source
    assert "PYPI_ONE_SHOT_ENABLED" in source
    assert "pulls/220" in source


def test_publisher_permissions_and_one_shot_disable() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    assert source.count("id-token: write") == 1
    assert "needs: publish" in source
    assert "actions: write" in source
    assert "/actions/workflows/publish.yml/disable" in source
    assert "ref: ${{ github.event.workflow_run.head_sha }}" in source
    assert "ref: ${{ github.sha }}" not in source


def test_all_actions_expressions_are_closed() -> None:
    """Reject unclosed and surplus braces in privileged workflow expressions."""
    import re

    expression = re.compile(r"\\$\\{\\{[^{}]+\\}\\}")
    for line in WORKFLOW.read_text(encoding="utf-8").splitlines():
        if "${{" not in line:
            continue
        without_expressions = expression.sub("", line)
        assert "${{" not in without_expressions, f"Unclosed GitHub expression: {line}"
        assert "{" not in without_expressions and "}" not in without_expressions, (
            f"Stray GitHub expression brace: {line}"
        )
