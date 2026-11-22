"""Exercise release blockers using synthetic source and archive metadata only."""

import io
import json
import runpy
import tarfile
import zipfile
from collections.abc import Callable
from pathlib import Path
from typing import cast

import pytest

CHECKS = runpy.run_path(str(Path(__file__).absolute().parents[1] / "repo-scripts" / "check_release.py"))
CHECK_RELEASE = cast("Callable[[Path, str, Path | None], list[str]]", CHECKS["check_release"])
MAIN = cast("Callable[[list[str]], int]", CHECKS["main"])


def _project(
    root: Path,
    *,
    name: str = "pyrorb",
    version: str = "0.1.0a1",
    dependencies: tuple[str, ...] = ("sample-reader>=1",),
    extra: tuple[str, ...] = ("sample-writer>=2",),
) -> Path:
    path = root / "pyproject.toml"
    path.write_text(
        f"[project]\nname = {json.dumps(name)}\nversion = {json.dumps(version)}\n"
        f"dependencies = {json.dumps(dependencies)}\n[project.optional-dependencies]\ncatg = {json.dumps(extra)}\n",
        encoding="utf-8",
    )
    return path


def _metadata(
    *,
    name: str = "pyrorb",
    version: str = "0.1.0a1",
    requirements: tuple[str, ...] = ("sample-reader>=1", 'sample-writer>=2; extra == "catg"'),
) -> bytes:
    fields = ["Metadata-Version: 2.4", f"Name: {name}", f"Version: {version}", "Provides-Extra: catg"]
    fields.extend(f"Requires-Dist: {requirement}" for requirement in requirements)
    return ("\n".join(fields) + "\n\n").encode()


def _artifacts(root: Path, *, wheel: bytes | None = None, sdist: bytes | None = None) -> Path:
    directory = root / "artifacts"
    directory.mkdir()
    with zipfile.ZipFile(directory / "pyrorb-0.1.0a1-py3-none-any.whl", "w") as archive:
        archive.writestr("pyrorb-0.1.0a1.dist-info/METADATA", _metadata() if wheel is None else wheel)
    raw = _metadata() if sdist is None else sdist
    with tarfile.open(directory / "pyrorb-0.1.0a1.tar.gz", "w:gz") as archive:
        entry = tarfile.TarInfo("pyrorb-0.1.0a1/PKG-INFO")
        entry.size = len(raw)
        archive.addfile(entry, io.BytesIO(raw))
    return directory


def test_selected_alpha_with_index_dependencies_passes(tmp_path: Path) -> None:
    assert CHECK_RELEASE(_project(tmp_path), "v0.1.0a1", _artifacts(tmp_path)) == []


@pytest.mark.parametrize("name", ["PyRORB", "pyrorb"])
def test_distribution_name_uses_packaging_normalization(tmp_path: Path, name: str) -> None:
    assert CHECK_RELEASE(_project(tmp_path, name=name), "v0.1.0a1", None) == []


@pytest.mark.parametrize(
    ("name", "version", "tag", "expected"),
    [
        ("python-runoff-routing", "0.1.0a1", "v0.1.0a1", "expected distribution"),
        ("pyrorb", "0.0.0.dev0", "v0.0.0.dev0", "bootstrap version"),
        ("pyrorb", "0.1.0a1", "v0.1.0", "must equal"),
        ("pyrorb", "0.1.0+private", "v0.1.0+private", "local version"),
        ("pyrorb", "unfinished", "vunfinished", "invalid or missing version"),
    ],
)
def test_source_identity_blockers(tmp_path: Path, name: str, version: str, tag: str, expected: str) -> None:
    errors = CHECK_RELEASE(_project(tmp_path, name=name, version=version), tag, None)
    assert any(expected in error for error in errors)


@pytest.mark.parametrize(
    "requirement",
    [
        "sample-reader @ https://example.invalid/reader.tar.gz",
        'sample-reader @ git+https://example.invalid/reader.git@abc ; python_version < "3.0"',
    ],
)
def test_source_direct_urls_are_rejected_even_with_inactive_markers(tmp_path: Path, requirement: str) -> None:
    errors = CHECK_RELEASE(_project(tmp_path, dependencies=(requirement,), extra=(requirement,)), "v0.1.0a1", None)
    assert sum("direct-URL" in error for error in errors) == 2
    assert any("project.dependencies" in error for error in errors)
    assert any("project.optional-dependencies.catg" in error for error in errors)


@pytest.mark.parametrize("artifact", ["wheel", "sdist"])
def test_final_built_metadata_is_checked_even_when_source_is_clean(tmp_path: Path, artifact: str) -> None:
    raw = _metadata(requirements=('hidden @ https://example.invalid/hidden.whl ; extra == "dev"',))
    dist = _artifacts(tmp_path, wheel=raw if artifact == "wheel" else None, sdist=raw if artifact == "sdist" else None)
    errors = CHECK_RELEASE(_project(tmp_path), "v0.1.0a1", dist)
    assert any("Requires-Dist: direct-URL" in error for error in errors)


@pytest.mark.parametrize("artifact", ["wheel", "sdist"])
def test_built_identity_must_match_selected_release(tmp_path: Path, artifact: str) -> None:
    raw = _metadata(name="unrelated", version="0.2.0")
    dist = _artifacts(tmp_path, wheel=raw if artifact == "wheel" else None, sdist=raw if artifact == "sdist" else None)
    errors = CHECK_RELEASE(_project(tmp_path), "v0.1.0a1", dist)
    assert any("expected distribution" in error for error in errors)
    assert any("differs from source" in error for error in errors)


def test_wheel_filename_must_match_release(tmp_path: Path) -> None:
    dist = _artifacts(tmp_path)
    (dist / "pyrorb-0.1.0a1-py3-none-any.whl").rename(dist / "pyrorb-0.2.0-py3-none-any.whl")
    errors = CHECK_RELEASE(_project(tmp_path), "v0.1.0a1", dist)
    assert any("filename: tag" in error for error in errors)


def test_identical_wheel_and_sdist_cannot_hide_changed_source_requirements(tmp_path: Path) -> None:
    changed = _metadata(requirements=("sample-reader>=2", 'sample-writer>=2; extra == "catg"'))
    errors = CHECK_RELEASE(_project(tmp_path), "v0.1.0a1", _artifacts(tmp_path, wheel=changed, sdist=changed))
    assert sum("Requires-Dist differs from source project dependencies" in error for error in errors) == 2
    assert not any("Wheel and sdist Requires-Dist fields differ" in error for error in errors)


def test_unlisted_built_dependency_under_declared_extra_is_rejected(tmp_path: Path) -> None:
    extra = _metadata(
        requirements=("sample-reader>=1", 'sample-writer>=2; extra == "catg"', 'unlisted>=9; extra == "catg"')
    )
    errors = CHECK_RELEASE(_project(tmp_path), "v0.1.0a1", _artifacts(tmp_path, wheel=extra, sdist=extra))
    assert sum("Requires-Dist differs from source project dependencies" in error for error in errors) == 2


def test_source_and_built_conditional_extra_markers_agree_after_normalization(tmp_path: Path) -> None:
    project = _project(
        tmp_path,
        dependencies=("Sample_Reader[FAST]>=1",),
        extra=("Sample-Writer>=2; python_version < '3.14' or sys_platform == 'win32'",),
    )
    built = _metadata(
        requirements=(
            "sample-reader[fast]>=1",
            'sample-writer>=2; (python_version < "3.14" or sys_platform == "win32") and extra == "catg"',
        )
    )
    assert CHECK_RELEASE(project, "v0.1.0a1", _artifacts(tmp_path, wheel=built, sdist=built)) == []


@pytest.mark.parametrize("directory", ["unrelated-9.9.dist-info", "pyrorb-0.2.0.dist-info"])
def test_wheel_dist_info_identity_must_match_wheel_filename(tmp_path: Path, directory: str) -> None:
    dist = _artifacts(tmp_path)
    wheel = dist / "pyrorb-0.1.0a1-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr(f"{directory}/METADATA", _metadata())
    errors = CHECK_RELEASE(_project(tmp_path), "v0.1.0a1", dist)
    assert any(".dist-info directory identity differs from wheel filename" in error for error in errors)


def test_wheel_with_second_unrelated_dist_info_directory_is_rejected(tmp_path: Path) -> None:
    dist = _artifacts(tmp_path)
    wheel = dist / "pyrorb-0.1.0a1-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "a") as archive:
        archive.writestr("unrelated-9.9.dist-info/WHEEL", "Wheel-Version: 1.0")
    errors = CHECK_RELEASE(_project(tmp_path), "v0.1.0a1", dist)
    assert any("unrelated top-level .dist-info directory" in error for error in errors)


@pytest.mark.parametrize("directory", ["PyRORB-0.1.0a1.dist-info", "pyrorb-0.1a1.dist-info"])
def test_wheel_dist_info_legacy_equivalent_spelling_is_accepted(tmp_path: Path, directory: str) -> None:
    dist = _artifacts(tmp_path)
    wheel = dist / "pyrorb-0.1.0a1-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr(f"{directory}/METADATA", _metadata())
    assert CHECK_RELEASE(_project(tmp_path), "v0.1.0a1", dist) == []


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (_metadata().replace(b"Metadata-Version: 2.4\n", b""), "exactly one Metadata-Version"),
        (
            _metadata().replace(b"Metadata-Version: 2.4\n", b"Metadata-Version: 2.4\nMetadata-Version: 2.4\n"),
            "exactly one Metadata-Version",
        ),
        (_metadata().replace(b"Metadata-Version: 2.4", b"Metadata-Version: 9.0"), "unsupported Metadata-Version"),
        (_metadata().replace(b"Metadata-Version: 2.4", b"Metadata-Version: 2.7"), "unsupported Metadata-Version"),
        (
            _metadata().replace(b"\n\n", b"\nInvalid header without colon\n\n"),
            "malformed headers",
        ),
    ],
)
@pytest.mark.parametrize("artifact", ["wheel", "sdist"])
def test_invalid_core_metadata_headers_block_built_artifacts(
    tmp_path: Path, raw: bytes, expected: str, artifact: str
) -> None:
    dist = _artifacts(tmp_path, wheel=raw if artifact == "wheel" else None, sdist=raw if artifact == "sdist" else None)
    errors = CHECK_RELEASE(_project(tmp_path), "v0.1.0a1", dist)
    filename_suffix = ".whl" if artifact == "wheel" else ".tar.gz"
    assert any(expected in error and filename_suffix in error for error in errors)


@pytest.mark.parametrize("metadata_version", ["1.2", "2.5", "2.6"])
def test_supported_core_metadata_versions_are_accepted(tmp_path: Path, metadata_version: str) -> None:
    raw = _metadata().replace(b"Metadata-Version: 2.4", f"Metadata-Version: {metadata_version}".encode())
    assert CHECK_RELEASE(_project(tmp_path), "v0.1.0a1", _artifacts(tmp_path, wheel=raw, sdist=raw)) == []


def test_missing_extra_and_different_sdist_requirements_fail(tmp_path: Path) -> None:
    raw = _metadata(requirements=("sample-reader>=2",)).replace(b"Provides-Extra: catg\n", b"")
    errors = CHECK_RELEASE(_project(tmp_path), "v0.1.0a1", _artifacts(tmp_path, sdist=raw))
    assert any("Provides-Extra differs" in error for error in errors)
    assert any("Requires-Dist fields differ" in error for error in errors)


@pytest.mark.parametrize(
    "raw",
    [
        b"Name: pyrorb\n\n",
        b"Name: pyrorb\nName: extra\nVersion: 0.1.0a1\n\n",
        _metadata().replace(b"Metadata-Version:", b"Dynamic: Requires-Dist\nMetadata-Version:"),
    ],
)
def test_required_headers_and_dynamic_dependencies_fail(tmp_path: Path, raw: bytes) -> None:
    errors = CHECK_RELEASE(_project(tmp_path), "v0.1.0a1", _artifacts(tmp_path, wheel=raw))
    assert any("exactly one Name" in error or "must not be dynamic" in error for error in errors)


def test_extra_artifact_prevents_accidental_upload(tmp_path: Path) -> None:
    dist = _artifacts(tmp_path)
    (dist / "old-build.txt").write_text("leftover", encoding="utf-8")
    assert CHECK_RELEASE(_project(tmp_path), "v0.1.0a1", dist) == [
        "Artifact directory must contain exactly one wheel and one .tar.gz sdist, with no other entries"
    ]


def test_missing_metadata_does_not_silently_pass(tmp_path: Path) -> None:
    dist = _artifacts(tmp_path)
    with zipfile.ZipFile(dist / "pyrorb-0.1.0a1-py3-none-any.whl", "w") as archive:
        archive.writestr("pyrorb/__init__.py", "")
    errors = CHECK_RELEASE(_project(tmp_path), "v0.1.0a1", dist)
    assert any("exactly one top-level" in error for error in errors)


def test_command_exit_code_and_source_only_scope(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    project = _project(tmp_path)
    assert MAIN(["--project", str(project), "--tag", "v0.1.0a1"]) == 0
    assert "built artifacts not checked" in capsys.readouterr().out
    assert MAIN(["--project", str(project), "--tag", "v0.9.0"]) == 1
    assert "BLOCKED:" in capsys.readouterr().err
