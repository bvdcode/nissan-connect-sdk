from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime
from enum import StrEnum

from .account_parsing import (
    _enum,
    _required_field,
    _typed_object,
)
from .exceptions import ResponseError


def _parse_nullable_object_list[ResultT](
    container: Mapping[str, object],
    field: str,
    parent_path: str,
    parser: Callable[[Mapping[str, object], str], ResultT],
) -> tuple[ResultT | None, ...] | None:
    values = _nullable_list(container, field, f"{parent_path}.{field}")
    if values is None:
        return None
    results: list[ResultT | None] = []
    for index, value in enumerate(values):
        if value is None:
            results.append(None)
            continue
        path = f"{parent_path}.{field}[{index}]"
        results.append(parser(_typed_object(value, path), path))
    return tuple(results)


def _required_typed_object(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> Mapping[str, object]:
    return _typed_object(_required_field(container, field, path), path)


def _required_list(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> list[object]:
    value = _required_field(container, field, path)
    if not isinstance(value, list):
        raise ResponseError(f"{path} is not a list")
    return value


def _nullable_list(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> list[object] | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    if not isinstance(value, list):
        raise ResponseError(f"{path} is not a list")
    return value


def _required_nullable_float(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> float | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ResponseError(f"{path} is not a number")
    return float(value)


def _required_nullable_datetime(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> datetime | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ResponseError(f"{path} is not a date-time string")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ResponseError(f"{path} is not an ISO-8601 date-time") from error


def _required_nullable_enum[EnumT: StrEnum](
    container: Mapping[str, object],
    field: str,
    enum_type: type[EnumT],
    path: str,
) -> EnumT | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    return _enum(value, enum_type, path)
