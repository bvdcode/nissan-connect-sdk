from __future__ import annotations

from datetime import datetime
from enum import Enum, StrEnum
from typing import Final


class UnsetType(Enum):
    """Marker for an optional GraphQL input field that must be omitted."""

    UNSET = "UNSET"


UNSET: Final = UnsetType.UNSET


def serialize_datetime(value: datetime) -> str:
    """Serialize an offset-aware date-time for Nissan's GraphQL API."""

    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Nissan date-time inputs must include a UTC offset")
    return value.isoformat()


def serialize_enum(value: StrEnum) -> str:
    """Serialize a schema-valid GraphQL enum value."""

    if value.value == "UNKNOWN__":
        raise ValueError("UNKNOWN_VALUE cannot be sent to Nissan as an input enum")
    return value.value


def optional_input_fields(**values: object) -> dict[str, object]:
    """Keep explicitly supplied GraphQL fields, including explicit nulls."""

    return {key: value for key, value in values.items() if value is not UNSET}
