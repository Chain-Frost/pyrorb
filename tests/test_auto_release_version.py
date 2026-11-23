"""Check calendar release allocation without creating tags or publishing."""

import datetime as dt
import runpy
from collections.abc import Callable
from pathlib import Path
from typing import cast

import pytest

S = runpy.run_path(str(Path(__file__).absolute().parents[1] / "repo-scripts" / "auto_release_version.py"))
NEXT = cast("Callable[[str, list[str], dt.date], str]", S["next_version"])
STAMP = cast("Callable[[Path, str], None]", S["stamp"])
PARTS = cast("Callable[[str], tuple[int, int, int, int]]", S["calendar_parts"])


def test_first_pyrorb_release_matches_sibling_calendar_format() -> None:
    assert NEXT("0.0.0.dev0", [], dt.date(2026, 11, 23)) == "26.11.23.1"


def test_same_day_release_revision_and_next_day_reset() -> None:
    assert NEXT("0.0.0.dev0", ["v26.11.23.1"], dt.date(2026, 11, 23)) == "26.11.23.2"
    assert NEXT("0.0.0.dev0", ["v26.11.23.2"], dt.date(2026, 11, 24)) == "26.11.24.1"


def test_clock_rollback_keeps_monotonic_release_order() -> None:
    assert NEXT("0.0.0.dev0", ["v26.11.23.2"], dt.date(2026, 11, 22)) == "26.11.23.3"


def test_dated_source_version_is_lower_bound() -> None:
    assert NEXT("26.11.23.1", [], dt.date(2026, 11, 23)) == "26.11.23.2"


@pytest.mark.parametrize("version", ["2026.11.23.1", "26.2.30.1", "26.13.1.1", "26.11.23.0"])
def test_invalid_calendar_releases_rejected(version: str) -> None:
    with pytest.raises(ValueError):
        PARTS(version)


def test_unrelated_tags_do_not_affect_calendar_allocation() -> None:
    assert NEXT("0.0.0.dev0", ["internal-test", "v0.0.0.dev0"], dt.date(2026, 11, 23)) == "26.11.23.1"


def test_malformed_numeric_calendar_tag_is_not_silently_skipped() -> None:
    with pytest.raises(ValueError):
        NEXT("0.0.0.dev0", ["v26.11.23.0"], dt.date(2026, 11, 23))


def test_stamping_is_local_and_preserves_unrelated_toml(tmp_path: Path) -> None:
    project = tmp_path / "pyproject.toml"
    project.write_text('[project]\nversion = "0.0.0.dev0"\n[tool.test]\na = 1\n', encoding="utf-8")
    STAMP(tmp_path, "v26.11.23.1")
    assert project.read_text(encoding="utf-8") == (
        '[project]\nversion = "26.11.23.1"\n[tool.test]\na = 1\n'
    )


def test_invalid_stamp_keeps_file_identical(tmp_path: Path) -> None:
    project = tmp_path / "pyproject.toml"
    original = '[project]\nversion = "0.0.0.dev0"\n'
    project.write_text(original, encoding="utf-8")
    with pytest.raises(ValueError):
        STAMP(tmp_path, "v26.2.30.1")
    assert project.read_text(encoding="utf-8") == original
