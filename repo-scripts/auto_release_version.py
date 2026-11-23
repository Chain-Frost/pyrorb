"""Select YY.M.D.N releases and stamp only a temporary checkout."""

import argparse
import datetime as dt
import json
import re
import sys
import tomllib
from pathlib import Path
from typing import cast

BOOTSTRAP = "0.0.0.dev0"
CALENDAR = re.compile(r"^(?P<year>\d{2})\.(?P<month>\d{1,2})\.(?P<day>\d{1,2})\.(?P<revision>[1-9]\d*)$")
SECTION = re.compile(r"(?ms)^(\[project\]\s*\n)(.*?)(?=^\[|\Z)")
VERSION = re.compile(r'(?m)^version[ \t]*=[ \t]*"([^"]+)"[ \t]*$')


def calendar_parts(value: str) -> tuple[int, int, int, int]:
    """Validate the YY.M.D.N form and actual calendar date."""
    match = CALENDAR.fullmatch(value)
    if match is None:
        message = f"Invalid calendar release version {value!r}"
        raise ValueError(message)
    year = int(match["year"]) + 2000
    month, day, revision = (int(match[key]) for key in ("month", "day", "revision"))
    dt.date(year, month, day)
    return year, month, day, revision


def next_version(current: str, tags: list[str], today: dt.date) -> str:
    """Allocate strictly later than existing calendar tags and source version."""
    known: list[tuple[int, int, int, int]] = []
    if current != BOOTSTRAP:
        known.append(calendar_parts(current))
    known.extend(
        calendar_parts(tag[1:]) for tag in tags if tag.startswith("v") and tag != "v0.0.0.dev0" and tag[1:2].isdigit()
    )
    if not 2000 <= today.year <= 2099:
        message = "YY calendar versions require a year between 2000 and 2099"
        raise ValueError(message)
    baseline = max(known, default=(0, 0, 0, 0))
    now = (today.year, today.month, today.day)
    candidate = (*now, 1) if now > baseline[:3] else (*baseline[:3], baseline[3] + 1)
    return f"{candidate[0] - 2000}.{candidate[1]}.{candidate[2]}.{candidate[3]}"


def stamp(root: Path, tag: str) -> None:
    """Write only local pyproject.toml; never change Git tags or remote refs."""
    if not tag.startswith("v"):
        message = "Release tag must begin with v"
        raise ValueError(message)
    chosen = tag[1:]
    selected = calendar_parts(chosen)
    path = root / "pyproject.toml"
    original = path.read_text(encoding="utf-8")
    current = tomllib.loads(original)["project"]["version"]
    if not isinstance(current, str):
        message = "Source project.version must be an explicit string"
        raise TypeError(message)
    if current != BOOTSTRAP and selected < calendar_parts(current):
        message = "Release version predates the source version"
        raise ValueError(message)
    section = SECTION.search(original)
    if section is None:
        message = "Missing [project] table"
        raise ValueError(message)
    found = list(VERSION.finditer(section[2]))
    if len(found) != 1 or found[0][1] != current:
        message = "Expected exactly one source version assignment"
        raise ValueError(message)
    start, end = found[0].span(1)
    changed = section[2][:start] + chosen + section[2][end:]
    updated = original[: section.start(2)] + changed + original[section.end(2) :]
    if tomllib.loads(updated)["project"]["version"] != chosen:
        message = "Release metadata stamping check failed"
        raise ValueError(message)
    path.write_text(updated, encoding="utf-8")


def main() -> int:
    """Read version-planning JSON or locally stamp the tagged checkout."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("next")
    chosen = commands.add_parser("stamp")
    chosen.add_argument("tag")
    args = parser.parse_args()
    if args.command == "stamp":
        stamp(Path.cwd(), args.tag)
        print(f"Stamped checkout for {args.tag}")
        return 0
    document: object = json.load(sys.stdin)
    if not isinstance(document, dict):
        message = "Expected version-planning JSON object"
        raise TypeError(message)
    request = cast("dict[str, object]", document)
    current, tags, today = request.get("current"), request.get("tags"), request.get("today")
    if not isinstance(current, str) or not isinstance(tags, list) or not isinstance(today, str):
        message = "Expected current/today strings and tags list"
        raise TypeError(message)
    values = cast("list[object]", tags)
    if any(not isinstance(value, str) for value in values):
        message = "Every tag must be a string"
        raise TypeError(message)
    print(next_version(current, cast("list[str]", values), dt.date.fromisoformat(today)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
