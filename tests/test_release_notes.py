from pathlib import Path

import pytest

from scripts.release_notes import extract_release_notes, render_release_notes


def test_extract_release_notes_returns_only_requested_version() -> None:
    changelog = """# Changelog

## [Unreleased]

- Pending change.

## [1.2.0] - 2026-07-31

- Added a feature.
- Fixed a bug.

## [1.1.0] - 2026-07-01

- Previous release.

[Unreleased]: https://example.com/compare/v1.2.0...HEAD
[1.2.0]: https://example.com/releases/tag/v1.2.0
"""

    assert extract_release_notes(changelog, "1.2.0") == ("- Added a feature.\n- Fixed a bug.\n")


def test_extract_release_notes_rejects_missing_version() -> None:
    with pytest.raises(ValueError, match=r"no section for version 1\.2\.0"):
        extract_release_notes("# Changelog\n\n## [Unreleased]\n", "1.2.0")


def test_extract_release_notes_rejects_empty_section() -> None:
    changelog = """# Changelog

## [1.2.0] - 2026-07-31

## [1.1.0] - 2026-07-01

- Previous release.
"""

    with pytest.raises(ValueError, match=r"section for version 1\.2\.0 is empty"):
        extract_release_notes(changelog, "1.2.0")


def test_extract_release_notes_excludes_link_definitions_after_latest_release() -> None:
    changelog = """# Changelog

## [1.2.0] - 2026-07-31

- Added a feature.

[Unreleased]: https://example.com/compare/v1.2.0...HEAD
[1.2.0]: https://example.com/releases/tag/v1.2.0
"""

    assert extract_release_notes(changelog, "1.2.0") == "- Added a feature.\n"


def test_render_release_notes_validates_tag_and_writes_notes(tmp_path: Path) -> None:
    pyproject_path = tmp_path / "pyproject.toml"
    changelog_path = tmp_path / "CHANGELOG.md"
    output_path = tmp_path / "release-notes.md"
    pyproject_path.write_text('[project]\nversion = "1.2.0"\n', encoding="utf-8")
    changelog_path.write_text(
        "# Changelog\n\n## [1.2.0] - 2026-07-31\n\n- Added a feature.\n",
        encoding="utf-8",
    )

    version = render_release_notes(
        tag="v1.2.0",
        pyproject_path=pyproject_path,
        changelog_path=changelog_path,
        output_path=output_path,
    )

    assert version == "1.2.0"
    assert output_path.read_text(encoding="utf-8") == "- Added a feature.\n"


def test_render_release_notes_rejects_mismatched_tag(tmp_path: Path) -> None:
    pyproject_path = tmp_path / "pyproject.toml"
    changelog_path = tmp_path / "CHANGELOG.md"
    pyproject_path.write_text('[project]\nversion = "1.2.0"\n', encoding="utf-8")
    changelog_path.write_text(
        "# Changelog\n\n## [1.2.0] - 2026-07-31\n\n- Added a feature.\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="does not match expected tag"):
        render_release_notes(
            tag="v1.2.1",
            pyproject_path=pyproject_path,
            changelog_path=changelog_path,
            output_path=tmp_path / "release-notes.md",
        )
