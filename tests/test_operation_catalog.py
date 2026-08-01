from __future__ import annotations

import hashlib

from pynissan import operations


def test_full_operation_catalog_has_exact_hash_identifiers() -> None:
    documents: list[tuple[str, str]] = []
    for constant, value in vars(operations).items():
        if isinstance(value, str) and value.startswith(("query ", "mutation ")):
            documents.append((constant, value))

    assert len(documents) == 285
    assert sum(document.startswith("query ") for _, document in documents) == 129
    assert sum(document.startswith("mutation ") for _, document in documents) == 156
    for constant, document in documents:
        operation_id = getattr(operations, f"{constant}_OPERATION_ID")
        assert hashlib.sha256(document.encode()).hexdigest() == operation_id
