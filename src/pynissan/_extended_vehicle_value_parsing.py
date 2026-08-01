from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from enum import StrEnum

from .exceptions import ResponseError


def _parse_nullable_string_items(
    value: object,
    path: str,
) -> tuple[str | None, ...] | None:
    values = _nullable_list(value, path)
    if values is None:
        return None
    return tuple(_nullable_string(item, f"{path}[{index}]") for index, item in enumerate(values))


def _parse_nullable_int_items(
    value: object,
    path: str,
) -> tuple[int | None, ...] | None:
    values = _nullable_list(value, path)
    if values is None:
        return None
    return tuple(_nullable_int(item, f"{path}[{index}]") for index, item in enumerate(values))


def _vehicle(data: Mapping[str, object]) -> Mapping[str, object] | None:
    if "vehicle" not in data:
        raise ResponseError("vehicle is missing")
    return _optional_typed_object(data.get("vehicle"), "vehicle")


def _object(value: object, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ResponseError(f"{path} is not an object")
    return value


def _typed_object(value: object, path: str) -> Mapping[str, object]:
    result = _object(value, path)
    _string(result.get("__typename"), f"{path}.__typename")
    return result


def _optional_typed_object(
    value: object,
    path: str,
) -> Mapping[str, object] | None:
    if value is None:
        return None
    return _typed_object(value, path)


def _list(value: object, path: str) -> list[object]:
    if not isinstance(value, list):
        raise ResponseError(f"{path} is not a list")
    return value


def _nullable_list(value: object, path: str) -> list[object] | None:
    if value is None:
        return None
    return _list(value, path)


def _string(value: object, path: str) -> str:
    if not isinstance(value, str):
        raise ResponseError(f"{path} is not a string")
    return value


def _nullable_string(value: object, path: str) -> str | None:
    if value is None:
        return None
    return _string(value, path)


def _int(value: object, path: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ResponseError(f"{path} is not an integer")
    return value


def _nullable_int(value: object, path: str) -> int | None:
    if value is None:
        return None
    return _int(value, path)


def _float(value: object, path: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ResponseError(f"{path} is not numeric")
    return float(value)


def _nullable_float(value: object, path: str) -> float | None:
    if value is None:
        return None
    return _float(value, path)


def _nullable_bool(value: object, path: str) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ResponseError(f"{path} is not a boolean")
    return value


def _enum[EnumT: StrEnum](
    value: object,
    enum_type: type[EnumT],
    path: str,
) -> EnumT:
    raw_value = _string(value, path)
    try:
        return enum_type(raw_value)
    except ValueError:
        unknown_value = getattr(enum_type, "UNKNOWN_VALUE", None)
        if isinstance(unknown_value, enum_type):
            return unknown_value
        raise ResponseError(f"{path} has an unsupported value: {raw_value}") from None


def _nullable_enum[EnumT: StrEnum](
    value: object,
    enum_type: type[EnumT],
    path: str,
) -> EnumT | None:
    if value is None:
        return None
    return _enum(value, enum_type, path)


def _nullable_datetime(value: object, path: str) -> datetime | None:
    if value is None:
        return None
    raw_value = _string(value, path)
    normalized = f"{raw_value[:-1]}+00:00" if raw_value.endswith("Z") else raw_value
    try:
        result = datetime.fromisoformat(normalized)
    except ValueError as error:
        raise ResponseError(f"{path} is not an ISO-8601 date-time") from error
    if result.tzinfo is None or result.utcoffset() is None:
        raise ResponseError(f"{path} is not an ISO-8601 date-time with an offset")
    return result
