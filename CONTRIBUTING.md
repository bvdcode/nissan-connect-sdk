# Contributing

Contributions that improve correctness, type safety, test coverage, or supported vehicle
features are welcome.

## Development setup

```bash
python -m venv .venv
python -m pip install -e ".[test]"
```

Run the complete quality gate before opening a pull request:

```bash
python -m ruff check .
python -m ruff format --check .
python -m mypy
python scripts/check_file_size.py
python -m pytest
python -m build
```

## Code guidelines

- Add precise type hints to all new functions, methods, and attributes.
- Add concise English docstrings to public classes, functions, and methods.
- Keep request serialization, transport, response parsing, and domain models separate.
- Preserve nullable fields and unknown upstream values instead of inventing defaults.
- Add focused tests for request variables, response parsing, errors, and read-only behavior.
- Keep state-changing operations behind the client's read-only guard.
- Keep handwritten Python files at or below 500 non-empty, non-comment lines. Prefer
  300–400 lines and split by responsibility before reaching the hard limit.

The only size-limit exceptions are the public export barrel in `src/pynissan/__init__.py`
and the declarative GraphQL document catalog in `src/pynissan/operations.py`.

## Test data

Use neutral fixtures. Never commit credentials, OAuth tokens, vehicle identifiers, account
details, private URLs, or captured customer responses.

## Pull requests

Keep each pull request focused and describe the product behavior it changes. Include tests for
new behavior and note any vehicle capability required to exercise it.
