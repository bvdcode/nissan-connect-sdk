from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime

from .exceptions import ResponseError
from .models import (
    CameraPosition,
    CameraService,
    DistanceUnit,
    ProductType,
    PurchaseType,
    SeatClimateOption,
    V2LState,
    WeekDay,
)


def _parse_week_days(value: object, path: str) -> tuple[WeekDay, ...]:
    values = _list(value, path)
    days: list[WeekDay] = []
    for item in values:
        raw = _required_str(item, path)
        try:
            days.append(WeekDay(raw))
        except ValueError:
            days.append(WeekDay.UNKNOWN_VALUE)
    return tuple(days)


def _optional_seat_option(value: object) -> SeatClimateOption | None:
    raw = _optional_str(value)
    if raw is None:
        return None
    try:
        return SeatClimateOption(raw)
    except ValueError:
        return SeatClimateOption.UNKNOWN_VALUE


def _optional_camera_position(value: object) -> CameraPosition | None:
    raw = _optional_str(value)
    if raw is None:
        return None
    try:
        return CameraPosition(raw)
    except ValueError:
        return CameraPosition.UNKNOWN_VALUE


def _optional_camera_service(value: object) -> CameraService | None:
    raw = _optional_str(value)
    if raw is None:
        return None
    try:
        return CameraService(raw)
    except ValueError:
        return CameraService.UNKNOWN_VALUE


def _optional_v2l_state(value: object) -> V2LState | None:
    raw = _optional_str(value)
    if raw is None:
        return None
    try:
        return V2LState(raw)
    except ValueError:
        return V2LState.UNKNOWN_VALUE


def _optional_on_off(value: object) -> bool | None:
    raw = _optional_str(value)
    if raw == "ON":
        return True
    if raw == "OFF":
        return False
    return None


def _nested_optional_str(value: object, key: str) -> str | None:
    item = _optional_object(value, key)
    return _optional_str(item.get(key)) if item is not None else None


def _object(value: object, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ResponseError(f"{path} is not an object")
    return value


def _optional_object(value: object, path: str) -> Mapping[str, object] | None:
    if value is None:
        return None
    return _object(value, path)


def _list(value: object, path: str) -> list[object]:
    if not isinstance(value, list):
        raise ResponseError(f"{path} is not a list")
    return value


def _optional_list(value: object, path: str) -> list[object] | None:
    if value is None:
        return None
    return _list(value, path)


def _required_str(value: object, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise ResponseError(f"{path} is not a non-empty string")
    return value


def _required_graphql_string(value: object, path: str) -> str:
    if not isinstance(value, str):
        raise ResponseError(f"{path} is not a string")
    return value


def _nullable_graphql_string(value: object, path: str) -> str | None:
    if value is None:
        return None
    return _required_graphql_string(value, path)


def _optional_str(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _required_bool(value: object, path: str) -> bool:
    if not isinstance(value, bool):
        raise ResponseError(f"{path} is not a boolean")
    return value


def _required_int(value: object, path: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ResponseError(f"{path} is not an integer")
    return value


def _optional_bool(value: object) -> bool | None:
    return value if isinstance(value, bool) else None


def _nullable_graphql_bool(value: object, path: str) -> bool | None:
    if value is None:
        return None
    return _required_bool(value, path)


def _optional_int(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _required_float(value: object, path: str) -> float:
    result = _optional_float(value)
    if result is None:
        raise ResponseError(f"{path} is not numeric")
    return result


def _required_distance_unit(value: object, path: str) -> DistanceUnit:
    raw = _required_str(value, path)
    try:
        return DistanceUnit(raw)
    except ValueError:
        return DistanceUnit.UNKNOWN_VALUE


def _optional_float(value: object) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


def _required_datetime(value: object, path: str) -> datetime:
    parsed = _optional_datetime(value)
    if parsed is None:
        raise ResponseError(f"{path} is not an ISO-8601 date-time")
    return parsed


def _required_aware_datetime(value: object, path: str) -> datetime:
    if not isinstance(value, str):
        raise ResponseError(f"{path} is not an ISO-8601 date-time with an offset")
    normalized = f"{value[:-1]}+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as error:
        raise ResponseError(f"{path} is not an ISO-8601 date-time with an offset") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ResponseError(f"{path} is not an ISO-8601 date-time with an offset")
    return parsed


def _nullable_aware_datetime(value: object, path: str) -> datetime | None:
    if value is None:
        return None
    return _required_aware_datetime(value, path)


def _optional_datetime(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _nullable_purchase_type(value: object, path: str) -> PurchaseType | str | None:
    if value is None:
        return None
    raw_value = _required_str(value, path)
    try:
        return PurchaseType(raw_value)
    except ValueError:
        return raw_value


def _nullable_product_type(value: object, path: str) -> ProductType | str | None:
    if value is None:
        return None
    raw_value = _required_str(value, path)
    try:
        return ProductType(raw_value)
    except ValueError:
        return raw_value
