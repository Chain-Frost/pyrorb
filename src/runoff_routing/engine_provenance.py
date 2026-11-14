"""Reproducible identity for the installed Python code and an optional wheel artifact.

A package version is not an exact implementation revision. Hash actual installed
source bytes, and only attribute a wheel when all installed package sources are
verified byte-for-byte against the explicitly supplied wheel.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from functools import cache
from importlib.metadata import PackageNotFoundError, version
from io import BytesIO
from pathlib import Path
from zipfile import BadZipFile, ZipFile

_MAX_MODULE_BYTES = 8 * 1024 * 1024
_MAX_WHEEL_BYTES = 64 * 1024 * 1024
_SOURCE_DOMAIN = b"python-runoff-routing:package-code-v1\x00"
_PACKAGE_NAME = "python-runoff-routing"


@dataclass(frozen=True, slots=True)
class ImplementationIdentity:
    """Hash of current package source bytes; not a Git commit or wheel digest."""

    revision: str
    package_version: str | None


def _source_file(name: str) -> bool:
    return name.endswith((".py", ".pyi")) or name == "py.typed"


def _installed_sources() -> dict[str, bytes]:
    root = Path(__file__).absolute().parent
    entries: dict[str, bytes] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or not _source_file(path.name):
            continue
        if path.is_symlink() or path.stat().st_size > _MAX_MODULE_BYTES:
            message = f"Package source is a symlink or exceeds the bounded size: {path.name}"
            raise ValueError(message)
        contents = path.read_bytes()
        if len(contents) > _MAX_MODULE_BYTES:
            message = f"Package source exceeds the bounded size: {path.name}"
            raise ValueError(message)
        entries[f"runoff_routing/{path.relative_to(root).as_posix()}"] = contents
    if not entries:
        message = "Cannot identify the installed runoff_routing package source files"
        raise ValueError(message)
    return entries


@cache
def identify_implementation() -> ImplementationIdentity:
    """Return a content-addressed identity independent of Git access and package version."""
    digest = hashlib.sha256()
    digest.update(_SOURCE_DOMAIN)
    for name, contents in sorted(_installed_sources().items()):
        digest.update(name.encode("utf-8"))
        digest.update(b"\x00")
        digest.update(len(contents).to_bytes(8, "big"))
        digest.update(contents)
    try:
        package_version = version(_PACKAGE_NAME)
    except PackageNotFoundError:
        package_version = None
    return ImplementationIdentity(f"package-code-v1-sha256:{digest.hexdigest()}", package_version)


def _compare_wheel_sources(wheel_bytes: bytes, sources: dict[str, bytes]) -> None:
    with ZipFile(BytesIO(wheel_bytes)) as archive:
        entries = tuple(
            item for item in archive.infolist()
            if item.filename.startswith("runoff_routing/") and not item.is_dir()
        )
        names = tuple(item.filename for item in entries)
        if len(names) != len(set(names)) or any(
            not _source_file(name.rsplit("/", maxsplit=1)[-1]) for name in names
        ):
            message = "Wheel has duplicate or unreviewed package source entries"
            raise ValueError(message)
        members = {item.filename: item for item in entries}
        if set(members) != set(sources):
            message = "Wheel package source file inventory differs from the running installation"
            raise ValueError(message)
        for name, info in members.items():
            if info.file_size > _MAX_MODULE_BYTES or archive.read(info) != sources[name]:
                message = f"Wheel package source bytes disagree with the running installation: {name}"
                raise ValueError(message)


def verify_installed_wheel(wheel_path: Path) -> str:
    """Hash a supplied wheel only when its package sources equal this installation.

    This does not infer the Git commit or verify private reference data. A mismatch
    is an input failure; callers must not report the wheel as the running build.
    """
    wheel = wheel_path.absolute()
    if wheel.suffix.lower() != ".whl" or wheel.is_symlink() or not wheel.is_file():
        message = "Wheel evidence must be an existing, non-symlink .whl file"
        raise ValueError(message)
    if wheel.stat().st_size > _MAX_WHEEL_BYTES:
        message = "Wheel evidence exceeds the bounded 64 MiB limit"
        raise ValueError(message)
    wheel_bytes = wheel.read_bytes()
    if len(wheel_bytes) > _MAX_WHEEL_BYTES:
        message = "Wheel evidence exceeds the bounded 64 MiB limit"
        raise ValueError(message)
    sources = _installed_sources()
    try:
        _compare_wheel_sources(wheel_bytes, sources)
    except BadZipFile as exc:
        message = "Wheel evidence is not a valid ZIP archive"
        raise ValueError(message) from exc
    return hashlib.sha256(wheel_bytes).hexdigest()
