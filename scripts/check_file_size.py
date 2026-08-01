import sys
from pathlib import Path

MAX_MEANINGFUL_LINES = 500
SOURCE_ROOTS = (Path("src"), Path("tests"), Path("scripts"))
EXEMPT_FILES = {
    Path("src/pynissan/__init__.py"): "public export barrel",
    Path("src/pynissan/operations.py"): "declarative GraphQL document catalog",
}


def meaningful_line_count(path: Path) -> int:
    """Count non-empty lines that are not comment-only lines."""

    return sum(
        1
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )


def oversized_files() -> tuple[tuple[Path, int], ...]:
    """Return handwritten Python files that exceed the repository limit."""

    violations: list[tuple[Path, int]] = []
    for root in SOURCE_ROOTS:
        for path in root.rglob("*.py"):
            normalized_path = Path(path.as_posix())
            if normalized_path in EXEMPT_FILES:
                continue
            line_count = meaningful_line_count(path)
            if line_count > MAX_MEANINGFUL_LINES:
                violations.append((normalized_path, line_count))
    return tuple(sorted(violations))


def main() -> int:
    """Validate the repository's Python file-size boundary."""

    violations = oversized_files()
    if not violations:
        return 0

    for path, line_count in violations:
        sys.stderr.write(
            f"{path}: {line_count} meaningful lines (maximum {MAX_MEANINGFUL_LINES})\n"
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
