from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime
from enum import StrEnum

from .exceptions import ResponseError

_AVK2_VEHICLE_TYPENAMES = frozenset(
    {
        "AVK2Vehicle",
        "ElectricAVK2Vehicle",
        "ElectricEVOVehicle",
        "EVOVehicle",
    }
)


def _vehicle(data: Mapping[str, object]) -> Mapping[str, object] | None:
    return _root(data, "vehicle")


def _root(
    data: Mapping[str, object],
    root_field: str,
) -> Mapping[str, object] | None:
    if root_field not in data:
        raise ResponseError(f"{root_field} is missing")
    return _optional_typed_object(data[root_field], root_field)


def _required_field(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> object:
    if field not in container:
        raise ResponseError(f"{path} is missing")
    return container[field]


def _typed_object(value: object, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ResponseError(f"{path} is not an object")
    _typename(value, path)
    return value


def _optional_typed_object(
    value: object,
    path: str,
) -> Mapping[str, object] | None:
    if value is None:
        return None
    return _typed_object(value, path)


def _required_optional_typed_object(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> Mapping[str, object] | None:
    return _optional_typed_object(_required_field(container, field, path), path)


def _typename(container: Mapping[str, object], path: str) -> str:
    return _required_string(container, "__typename", f"{path}.__typename")


def _required_list(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> list[object]:
    value = _required_field(container, field, path)
    if not isinstance(value, list):
        raise ResponseError(f"{path} is not a list")
    return value


def _required_nullable_list(
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


def _string(value: object, path: str) -> str:
    if not isinstance(value, str):
        raise ResponseError(f"{path} is not a string")
    return value


def _required_string(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> str:
    return _string(_required_field(container, field, path), path)


def _required_nullable_string(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> str | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    return _string(value, path)


def _int(value: object, path: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ResponseError(f"{path} is not an integer")
    return value


def _required_int(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> int:
    return _int(_required_field(container, field, path), path)


def _required_nullable_int(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> int | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    return _int(value, path)


def _float(value: object, path: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ResponseError(f"{path} is not numeric")
    return float(value)


def _required_float(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> float:
    return _float(_required_field(container, field, path), path)


def _required_bool(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> bool:
    value = _required_field(container, field, path)
    if not isinstance(value, bool):
        raise ResponseError(f"{path} is not a boolean")
    return value


def _required_nullable_bool(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> bool | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ResponseError(f"{path} is not a boolean")
    return value


def _required_enum[EnumT: StrEnum](
    container: Mapping[str, object],
    field: str,
    enum_type: type[EnumT],
    path: str,
) -> EnumT:
    return _enum(_required_field(container, field, path), enum_type, path)


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


def _enum[EnumT: StrEnum](
    value: object,
    enum_type: type[EnumT],
    path: str,
) -> EnumT:
    raw_value = _string(value, path)
    try:
        return enum_type(raw_value)
    except ValueError:
        try:
            return enum_type("UNKNOWN__")
        except ValueError:
            raise ResponseError(f"{path} has an unsupported value: {raw_value}") from None


def _required_datetime(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> datetime:
    return _datetime(_required_field(container, field, path), path)


def _required_nullable_datetime(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> datetime | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    return _datetime(value, path)


def _datetime(value: object, path: str) -> datetime:
    raw_value = _string(value, path)
    normalized = f"{raw_value[:-1]}+00:00" if raw_value.endswith("Z") else raw_value
    try:
        result = datetime.fromisoformat(normalized)
    except ValueError as error:
        raise ResponseError(f"{path} is not an ISO-8601 date-time") from error
    if result.tzinfo is None or result.utcoffset() is None:
        raise ResponseError(f"{path} is not an ISO-8601 date-time with an offset")
    return result


def _required_date(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> date:
    return _date(_required_field(container, field, path), path)


def _required_nullable_date(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> date | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    return _date(value, path)


def _date(value: object, path: str) -> date:
    raw_value = _string(value, path)
    try:
        return date.fromisoformat(raw_value)
    except ValueError as error:
        raise ResponseError(f"{path} is not an ISO-8601 date") from error
