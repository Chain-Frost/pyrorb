"""Check PyRORB source and built metadata offline; never upload or change files.

Requires the development tool ``packaging`` (also installed by ``build``).
This bounded packaging gate does not establish MVP or numerical acceptance.
"""

import argparse
import sys
import tarfile
import tomllib
import zipfile
from dataclasses import dataclass
from email import policy
from email.parser import BytesParser
from pathlib import Path, PurePosixPath
from typing import cast

from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name, parse_sdist_filename, parse_wheel_filename
from packaging.version import InvalidVersion, Version

ROOT = Path(__file__).absolute().parents[1]
EXPECTED_NAME = "pyrorb"


@dataclass(frozen=True, slots=True)
class DistributionMetadata:
    """Static release fields and every dependency, including optional extras."""

    name: str
    version: str
    requirements: tuple[tuple[str, str], ...]
    extras: frozenset[str]


def _strings(value: object, location: str) -> tuple[str, ...]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in cast("list[object]", value)):
        message = f"{location}: expected a list of strings"
        raise TypeError(message)
    return tuple(cast("list[str]", value))


def _source_metadata(path: Path) -> DistributionMetadata:
    with path.open("rb") as stream:
        document = tomllib.load(stream)
    raw_project: object = document.get("project", {})
    if not isinstance(raw_project, dict):
        message = "project: expected a table"
        raise TypeError(message)
    project = cast("dict[str, object]", raw_project)
    name, version = project.get("name"), project.get("version")
    if not isinstance(name, str) or not isinstance(version, str):
        message = "project.name and project.version must be explicit strings"
        raise TypeError(message)
    requirements = [
        ("project.dependencies", item) for item in _strings(project.get("dependencies", []), "dependencies")
    ]
    optional = project.get("optional-dependencies", {})
    if not isinstance(optional, dict):
        message = "project.optional-dependencies: expected a table"
        raise TypeError(message)
    extras = cast("dict[str, object]", optional)
    for extra, values in extras.items():
        location = f"project.optional-dependencies.{extra}"
        requirements.extend((location, item) for item in _strings(values, location))
    dynamic = _strings(project.get("dynamic", []), "project.dynamic")
    if set(dynamic) & {"name", "version", "dependencies", "optional-dependencies"}:
        message = "Release identity and dependencies must be static in pyproject.toml for this check"
        raise ValueError(message)
    return DistributionMetadata(
        name,
        version,
        tuple(requirements),
        frozenset(canonicalize_name(extra) for extra in extras),
    )


def _identity_errors(name: str, version: str, tag: str, location: str) -> list[str]:
    errors: list[str] = []
    if canonicalize_name(name) != EXPECTED_NAME:
        errors.append(f"{location}: expected distribution {EXPECTED_NAME!r}, found {name!r}")
    try:
        selected = Version(version)
    except InvalidVersion:
        errors.append(f"{location}: invalid or missing version {version!r}")
        return errors
    if selected == Version("0.0.0.dev0"):
        errors.append(f"{location}: bootstrap version {version!r} is not a selected release version")
    if selected.local is not None:
        errors.append(f"{location}: local version {version!r} cannot be uploaded to PyPI")
    if tag != f"v{selected}":
        errors.append(f"{location}: tag {tag!r} must equal 'v{selected}'")
    return errors


def _requirement_errors(metadata: DistributionMetadata, location: str) -> list[str]:
    errors: list[str] = []
    for field, text in metadata.requirements:
        try:
            requirement = Requirement(text)
        except InvalidRequirement:
            errors.append(f"{location} {field}: invalid requirement {text!r}")
            continue
        # Inspect all markers/extras without evaluating them on this interpreter.
        if requirement.url is not None:
            errors.append(f"{location} {field}: direct-URL requirement must use a qualified published version: {text}")
    return errors


def _parse_metadata(raw: bytes) -> DistributionMetadata:
    message = BytesParser(policy=policy.default).parsebytes(raw)
    names = message.get_all("Name", [])
    versions = message.get_all("Version", [])
    if len(names) != 1 or len(versions) != 1:
        detail = "Built metadata must contain exactly one Name and one Version"
        raise ValueError(detail)
    dynamic = {str(value).lower() for value in message.get_all("Dynamic", [])}
    if dynamic & {"name", "version", "requires-dist", "provides-extra"}:
        detail = "Built release identity and dependencies must not be dynamic"
        raise ValueError(detail)
    return DistributionMetadata(
        str(names[0]),
        str(versions[0]),
        tuple(("Requires-Dist", str(value)) for value in message.get_all("Requires-Dist", [])),
        frozenset(canonicalize_name(str(value)) for value in message.get_all("Provides-Extra", [])),
    )


def _wheel_metadata(path: Path) -> DistributionMetadata:
    with zipfile.ZipFile(path) as archive:
        entries = [
            entry
            for entry in archive.infolist()
            if len(PurePosixPath(entry.filename).parts) == 2
            and PurePosixPath(entry.filename).parts[0].endswith(".dist-info")
            and PurePosixPath(entry.filename).name == "METADATA"
        ]
        if len(entries) != 1:
            message = "Wheel must contain exactly one top-level .dist-info/METADATA"
            raise ValueError(message)
        return _parse_metadata(archive.read(entries[0]))


def _sdist_metadata(path: Path) -> DistributionMetadata:
    with tarfile.open(path, "r:gz") as archive:
        entries = [
            entry for entry in archive.getmembers() if entry.name == f"{path.name.removesuffix('.tar.gz')}/PKG-INFO"
        ]
        if len(entries) != 1 or not entries[0].isfile():
            message = "Sdist must contain exactly one regular root PKG-INFO matching its filename"
            raise ValueError(message)
        stream = archive.extractfile(entries[0])
        if stream is None:
            message = "Sdist PKG-INFO is unreadable"
            raise ValueError(message)
        with stream:
            return _parse_metadata(stream.read())


def _artifact_metadata(path: Path) -> tuple[str, str, DistributionMetadata]:
    if path.suffix == ".whl":
        name, version, _, _ = parse_wheel_filename(path.name)
        return name, str(version), _wheel_metadata(path)
    name, version = parse_sdist_filename(path.name)
    return name, str(version), _sdist_metadata(path)


def _artifact_errors(
    path: Path, source: DistributionMetadata, tag: str
) -> tuple[list[str], DistributionMetadata | None]:
    try:
        name, version, metadata = _artifact_metadata(path)
    except (OSError, ValueError, zipfile.BadZipFile, tarfile.TarError) as exc:
        return [f"{path.name}: {exc}"], None
    errors = _identity_errors(name, version, tag, f"{path.name} filename")
    errors.extend(_identity_errors(metadata.name, metadata.version, tag, f"{path.name} metadata"))
    errors.extend(_requirement_errors(metadata, path.name))
    if metadata.version != source.version:
        errors.append(f"{path.name}: metadata version {metadata.version!r} differs from source {source.version!r}")
    if metadata.extras != source.extras:
        errors.append(f"{path.name}: Provides-Extra differs from project.optional-dependencies")
    return errors, metadata


def _distribution_errors(directory: Path, source: DistributionMetadata, tag: str) -> list[str]:
    if not directory.is_dir():
        return [f"Artifact directory does not exist: {directory}"]
    paths = sorted(directory.iterdir())
    wheels = [path for path in paths if path.is_file() and path.suffix == ".whl"]
    sdists = [path for path in paths if path.is_file() and path.name.endswith(".tar.gz")]
    if len(wheels) != 1 or len(sdists) != 1 or len(paths) != 2:
        return ["Artifact directory must contain exactly one wheel and one .tar.gz sdist, with no other entries"]
    errors: list[str] = []
    metadata: list[DistributionMetadata] = []
    for path in (*wheels, *sdists):
        problems, parsed = _artifact_errors(path, source, tag)
        errors.extend(problems)
        if parsed is not None:
            metadata.append(parsed)
    if len(metadata) == 2 and metadata[0].requirements != metadata[1].requirements:
        # Setuptools writes the same Requires-Dist sequence to both artifacts.
        errors.append("Wheel and sdist Requires-Dist fields differ; inspect both artifacts before release")
    return errors


def check_release(project: Path, tag: str, dist: Path | None = None) -> list[str]:
    """Return every applicable source/artifact blocker without network access."""
    try:
        source = _source_metadata(project)
    except (OSError, TypeError, ValueError) as exc:
        return [f"{project}: {exc}"]
    errors = _identity_errors(source.name, source.version, tag, str(project))
    errors.extend(_requirement_errors(source, str(project)))
    if dist is not None:
        errors.extend(_distribution_errors(dist, source, tag))
    return errors


def main(arguments: list[str] | None = None) -> int:
    """Run a source preflight, optionally also checking the exact built pair."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=ROOT / "pyproject.toml")
    parser.add_argument("--tag", required=True, help="Selected tag, exactly v followed by the project version")
    parser.add_argument("--dist", type=Path, help="Directory containing exactly the wheel and sdist to upload")
    options = parser.parse_args(arguments)
    errors = check_release(options.project, options.tag, options.dist)
    if errors:
        for error in errors:
            print(f"BLOCKED: {error}", file=sys.stderr)
        return 1
    scope = "source and built artifacts" if options.dist is not None else "source only; built artifacts not checked"
    print(f"Release metadata checks passed ({scope}). MVP acceptance and publication approval remain separate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
