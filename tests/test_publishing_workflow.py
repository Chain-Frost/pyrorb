"""Protect the automated PyPI workflow against broad release triggers."""

import re
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
    assert "needs: [publish, release]" in source
    assert "actions: write" in source
    assert "/actions/workflows/publish.yml/disable" in source
    assert "ref: ${{ github.event.workflow_run.head_sha }}" in source
    assert "ref: ${{ github.sha }}" not in source


def test_all_actions_expressions_are_closed() -> None:
    """Reject unclosed and surplus braces in privileged workflow expressions."""
    expression = re.compile(r"\$\{\{[^{}]+\}\}")
    for line in WORKFLOW.read_text(encoding="utf-8").splitlines():
        if "${{" not in line:
            continue
        without_expressions = expression.sub("", line)
        assert "${{" not in without_expressions, f"Unclosed GitHub expression: {line}"
        assert "{" not in without_expressions, f"Stray GitHub expression brace: {line}"
        assert "}" not in without_expressions, f"Stray GitHub expression brace: {line}"


def test_missing_unprotected_environment_blocks_publication() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    assert source.count("environments/pypi") == 4
    assert source.count('reviewer.login == "Chain-Frost"') == 2
    assert source.count("deployment_branch_policy.custom_branch_policies == true") == 2
    assert source.count("deployment_branch_policy.protected_branches == false") == 2
    assert source.count("deployment-branch-policies?per_page=100") == 2
    assert source.count(".total_count == 1") == 2
    assert source.count("(.branch_policies | length) == 1") == 2
    assert source.count('.branch_policies[0].name == "main"') == 2
    assert source.count('.branch_policies[0].type == "branch"') == 2
    assert source.count("actions: read") == 2


def test_public_github_release_requires_successful_pypi_upload() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    tag_job = source.split("  tag:\n", 1)[1].split("  publish:\n", 1)[0]
    release_job = source.split("  release:\n", 1)[1].split("  disable:\n", 1)[0]
    assert "createRelease" not in tag_job
    assert "createRelease" in release_job
    assert "needs: [build, publish]" in release_job
    assert "needs: [publish, release]" in source
    assert "always() && needs.publish.result == 'success'" in source


def test_reruns_of_quality_or_publisher_are_ineligible() -> None:
    """Both the upstream run and this publisher must be first attempts."""
    source = WORKFLOW.read_text(encoding="utf-8")
    for job in ("build", "publish"):
        block = source.split(f"  {job}:\n", 1)[1].split("    runs-on:", 1)[0]
        assert "github.event.workflow_run.run_attempt == 1" in block
        assert "github.run_attempt == 1" in block


def test_pr_only_writer_is_installed_outside_release_metadata() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    assert ".[dev,catg]" not in source
    assert "[catg]" not in source
    assert "-r requirements-catg.txt -e '.[dev]'" in source
    assert 'pip install "${files[0]}"' in source
    assert 'pip install "${files[0]}[mcp,dev,research]"' in source
    assert '-m pip install -r "$GITHUB_WORKSPACE/requirements-catg.txt"' in source


def test_release_base_uses_internal_canonical_reader() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    assert "from runoff_routing.rorb_readers.output_reader import bind_output_site_columns" in source
    assert "from ryan_library" not in source


def test_activation_requires_read_only_live_configuration_preflight() -> None:
    quality = WORKFLOW.with_name("quality.yml").read_text(encoding="utf-8")
    preflight = quality.split("  release-configuration:\n", 1)[1].split("  windows-python-313:\n", 1)[0]
    assert "github.event.pull_request.number == 220" in preflight
    assert "github.event.pull_request.head.repo.full_name == github.repository" in preflight
    assert "vars.PYPI_ONE_SHOT_ENABLED" in preflight
    assert "id-token:" not in preflight
    assert "actions: write" not in preflight
    assert "contents: write" not in preflight
    assert "actions: read" in preflight
    assert "environment:" not in preflight
    assert "deployment-branch-policies?per_page=100" in preflight
    assert "gh api" in preflight
    aggregate = quality.split("  windows-python-313:\n", 1)[1]
    assert "needs: [windows-python-versions, release-configuration]" in aggregate
    assert "$env:CONFIG_RESULT -ne 'success'" in aggregate
    assert "$env:CONFIG_RESULT -ne 'skipped'" in aggregate
