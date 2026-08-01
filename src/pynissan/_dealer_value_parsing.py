from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime

from .account_parsing import (
    _required_field,
    _required_nullable_bool,
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
    result: list[ItemT | None] = []
    for index, item in enumerate(value):
        if item is None:
            result.append(None)
            continue
        item_path = f"{path}[{index}]"
        result.append(parser(_typed_object(item, item_path), item_path))
    return tuple(result)


def _optional_selected_nullable_list[ItemT](
    container: Mapping[str, object],
    field: str,
    parent_path: str,
    parser: Callable[[Mapping[str, object], str], ItemT],
) -> tuple[ItemT | None, ...] | None:
    if field not in container:
        return None
    return _nullable_list(container, field, f"{parent_path}.{field}", parser)


def _required_string_list(
    container: Mapping[str, object],
    field: str,
    parent_path: str,
) -> tuple[str, ...]:
    path = f"{parent_path}.{field}"
    value = _required_field(container, field, path)
    if not isinstance(value, list):
        raise ResponseError(f"{path} is not a list")
    result: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str):
            raise ResponseError(f"{path}[{index}] is not a string")
        result.append(item)
    return tuple(result)


def _optional_selected_nullable_string(
    container: Mapping[str, object],
    field: str,
    parent_path: str,
) -> str | None:
    if field not in container:
        return None
    return _required_nullable_string(container, field, f"{parent_path}.{field}")


def _optional_selected_nullable_bool(
    container: Mapping[str, object],
    field: str,
    parent_path: str,
) -> bool | None:
    if field not in container:
        return None
    return _required_nullable_bool(container, field, f"{parent_path}.{field}")


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


def _required_datetime(container: Mapping[str, object], field: str, path: str) -> datetime:
    value = _required_string(container, field, path)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ResponseError(f"{path} is not an ISO date-time") from None
