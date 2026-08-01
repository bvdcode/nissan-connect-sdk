"""Validate release metadata and render notes from the committed changelog."""

from __future__ import annotations

import argparse
import logging
import re
import tomllib
from collections.abc import Sequence
from pathlib import Path
from typing import TypedDict, cast

_LOGGER = logging.getLogger(__name__)
_CHANGELOG_HEADING = re.compile(r"^## \[(?P<version>[^]]+)](?: - \d{4}-\d{2}-\d{2})?$")
_LINK_DEFINITION = re.compile(r"^\[[^]]+]:\s+\S+")


class _ProjectTable(TypedDict):
    version: str


class _PyProject(TypedDict):
    project: _ProjectTable


def read_project_version(path: Path) -> str:
    """Read the static project version from a pyproject file."""
    document = cast(
        _PyProject,
        tomllib.loads(path.read_text(encoding="utf-8")),
    )
    try:
        version = document["project"]["version"]
    except (KeyError, TypeError) as error:
        raise ValueError(f"{path} does not define project.version") from error

    if not isinstance(version, str) or not version:
        raise ValueError(f"{path} contains an invalid project.version")
    return version


def extract_release_notes(changelog: str, version: str) -> str:
    """Extract a non-empty version section from Keep a Changelog text."""
    lines = changelog.splitlines()
    section_start: int | None = None
    section_end = len(lines)

    for index, line in enumerate(lines):
        heading = _CHANGELOG_HEADING.fullmatch(line)
        if heading is not None and heading.group("version") == version:
            section_start = index + 1
            continue
        if section_start is not None and (
            line.startswith("## ") or _LINK_DEFINITION.match(line) is not None
        ):
            section_end = index
            break

    if section_start is None:
        raise ValueError(f"CHANGELOG.md has no section for version {version}")

    notes = "\n".join(lines[section_start:section_end]).strip()
    if not notes:
        raise ValueError(f"CHANGELOG.md section for version {version} is empty")
    return f"{notes}\n"


def render_release_notes(
    *,
    tag: str,
    pyproject_path: Path,
    changelog_path: Path,
    output_path: Path,
) -> str:
    """Validate a tag and write its committed changelog section as release notes."""
    version = read_project_version(pyproject_path)
    expected_tag = f"v{version}"
    if tag != expected_tag:
        raise ValueError(f"release tag {tag!r} does not match expected tag {expected_tag!r}")

    notes = extract_release_notes(changelog_path.read_text(encoding="utf-8"), version)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(notes, encoding="utf-8")
    return version


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a release tag and render its changelog section.",
    )
    parser.add_argument("--tag", required=True, help="Release tag, such as v0.1.0")
    parser.add_argument("--output", required=True, type=Path, help="Release notes output path")
    parser.add_argument("--pyproject", type=Path, default=Path("pyproject.toml"))
    parser.add_argument("--changelog", type=Path, default=Path("CHANGELOG.md"))
    return parser


def main(arguments: Sequence[str] | None = None) -> int:
    """Run release metadata validation and note rendering."""
    options = _create_parser().parse_args(arguments)
    version = render_release_notes(
        tag=options.tag,
        pyproject_path=options.pyproject,
        changelog_path=options.changelog,
        output_path=options.output,
    )
    _LOGGER.info("Prepared release notes for pynissan %s", version)
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
