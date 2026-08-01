from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from enum import StrEnum

from .exceptions import ResponseError

_BASE_CONNECTED_VEHICLE_TYPES = frozenset(
    {
        "AVK2Vehicle",
        "AVKVehicle",
        "ConnectedVehicle",
        "ElectricAVK2Vehicle",
        "ElectricEVOVehicle",
        "ElectricVehicle",
        "EVOVehicle",
    }
)
_DRIVER_INVITES_ERROR_TYPES = frozenset(
    {
        "GeneralErrors",
        "DatabaseError",
        "BrandError",
        "TokenError",
        "VinValidationError",
    }
)
_INVITE_DRIVER_ERROR_TYPES = frozenset(
    {
        "FirstNameValidationError",
        "LastNameValidationError",
        "EmailValidationError",
        "PhoneValidationError",
        "ExistingInviteError",
        "MaxInvitesReachedError",
    }
)
_DRIVER_INVITE_ACTION_ERROR_TYPES = frozenset(
    {
        "GeneralErrors",
        "DatabaseError",
        "InvalidInviteIdError",
        "TokenError",
        "BrandError",
        "TermsAndConditionsError",
        "CountryError",
    }
)


def _root(
    data: Mapping[str, object],
    root_field: str,
) -> Mapping[str, object] | None:
    value = _required_value(data, root_field, root_field)
    if value is None:
        return None
    return _typed_object(value, root_field)


def _typed_object(value: object, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ResponseError(f"{path} is not an object")
    _typename(value, path)
    return value


def _typename(container: Mapping[str, object], path: str) -> str:
    return _required_string(container, "__typename", f"{path}.__typename")


def _required_value(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> object:
    if field not in container:
        raise ResponseError(f"{path} is missing")
    return container[field]


def _required_string(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> str:
    return _string(_required_value(container, field, path), path)


def _required_nullable_string(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> str | None:
    value = _required_value(container, field, path)
    if value is None:
        return None
    return _string(value, path)


def _required_bool(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> bool:
    value = _required_value(container, field, path)
    if not isinstance(value, bool):
        raise ResponseError(f"{path} is not a boolean")
    return value


def _required_nullable_bool(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> bool | None:
    value = _required_value(container, field, path)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ResponseError(f"{path} is not a boolean")
    return value


def _required_list(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> list[object]:
    value = _required_value(container, field, path)
    if not isinstance(value, list):
        raise ResponseError(f"{path} is not a list")
    return value


def _nullable_list(value: object, path: str) -> list[object] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        raise ResponseError(f"{path} is not a list")
    return value


def _required_string_tuple(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> tuple[str, ...]:
    values = _required_list(container, field, path)
    return tuple(_string(value, f"{path}[{index}]") for index, value in enumerate(values))


def _string(value: object, path: str) -> str:
    if not isinstance(value, str):
        raise ResponseError(f"{path} is not a string")
    return value


def _required_datetime(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> datetime:
    raw_value = _required_string(container, field, path)
    normalized = f"{raw_value[:-1]}+00:00" if raw_value.endswith("Z") else raw_value
    try:
        result = datetime.fromisoformat(normalized)
    except ValueError as error:
        raise ResponseError(f"{path} is not an ISO-8601 date-time") from error
    if result.tzinfo is None or result.utcoffset() is None:
        raise ResponseError(f"{path} is not an ISO-8601 date-time with an offset")
    return result


def _required_enum[EnumT: StrEnum](
    container: Mapping[str, object],
    field: str,
    enum_type: type[EnumT],
    path: str,
) -> EnumT:
    return _enum(_required_value(container, field, path), enum_type, path)


def _required_nullable_enum[EnumT: StrEnum](
    container: Mapping[str, object],
    field: str,
    enum_type: type[EnumT],
    path: str,
) -> EnumT | None:
    value = _required_value(container, field, path)
    if value is None:
        return None
    return _enum(value, enum_type, path)


def _enum[EnumT: StrEnum](value: object, enum_type: type[EnumT], path: str) -> EnumT:
    raw_value = _string(value, path)
    try:
        return enum_type(raw_value)
    except ValueError:
        return enum_type("UNKNOWN__")
