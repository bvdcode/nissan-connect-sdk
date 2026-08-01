from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import date, datetime

from .account_parsing import (
    _required_field,
    _required_nullable_string,
    _required_string,
    _typed_object,
)
from .exceptions import ResponseError


def _nullable_list[ItemT](
    container: Mapping[str, object],
    field: str,
    path: str,
    parser: Callable[[Mapping[str, object], str], ItemT],
) -> tuple[ItemT | None, ...] | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    if not isinstance(value, list):
        raise ResponseError(f"{path} is not a list")
    items: list[ItemT | None] = []
    for index, item in enumerate(value):
        if item is None:
            items.append(None)
            continue
        item_path = f"{path}[{index}]"
        items.append(parser(_typed_object(item, item_path), item_path))
    return tuple(items)


def _required_bool(container: Mapping[str, object], field: str, path: str) -> bool:
    value = _required_field(container, field, path)
    if not isinstance(value, bool):
        raise ResponseError(f"{path} is not a boolean")
    return value


def _required_nullable_float(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> float | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    if not isinstance(value, int | float) or isinstance(value, bool):
        raise ResponseError(f"{path} is not a number")
    return float(value)


def _required_date(container: Mapping[str, object], field: str, path: str) -> date:
    value = _required_string(container, field, path)
    return _parse_date(value, path)


def _required_nullable_date(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> date | None:
    value = _required_nullable_string(container, field, path)
    return None if value is None else _parse_date(value, path)


def _required_nullable_datetime(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> datetime | None:
    value = _required_nullable_string(container, field, path)
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ResponseError(f"{path} is not an ISO date-time") from None


def _parse_date(value: str, path: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ResponseError(f"{path} is not an ISO date") from None
