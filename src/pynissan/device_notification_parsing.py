from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime

from .device_notification_models import (
    InVehicleMessage,
    InVehicleMessageSummary,
    PushNotificationDatabaseError,
    PushNotificationResult,
    PushNotificationSuccess,
    PushNotificationTokenError,
)
from .exceptions import ResponseError


def parse_register_push_notifications(data: Mapping[str, object]) -> bool | None:
    """Parse the nullable scalar returned by legacy push registration."""

    return _parse_legacy_push_result(data, "registerNotifications")


def parse_unregister_push_notifications(data: Mapping[str, object]) -> bool | None:
    """Parse the nullable scalar returned by legacy push unregistration."""

    return _parse_legacy_push_result(data, "unregisterNotifications")


def parse_register_device_for_push_notifications(
    data: Mapping[str, object],
) -> PushNotificationResult | None:
    """Parse the typed union returned by current device push registration."""

    return _parse_device_push_result(data, "registerDeviceForPushNotifications")


def parse_unregister_device_for_push_notifications(
    data: Mapping[str, object],
) -> PushNotificationResult | None:
    """Parse the typed union returned by current device push unregistration."""

    return _parse_device_push_result(data, "unregisterDeviceForPushNotifications")


def parse_in_vehicle_messages(
    data: Mapping[str, object],
) -> tuple[InVehicleMessageSummary | None, ...] | None:
    """Parse a nullable message list while preserving nullable list items."""

    vehicle = _vehicle(data)
    if vehicle is None or "inVehicleMessages" not in vehicle:
        return None
    values = _nullable_list(
        vehicle.get("inVehicleMessages"),
        "vehicle.inVehicleMessages",
    )
    if values is None:
        return None

    messages: list[InVehicleMessageSummary | None] = []
    for index, raw_message in enumerate(values):
        if raw_message is None:
            messages.append(None)
            continue
        path = f"vehicle.inVehicleMessages[{index}]"
        message = _object(raw_message, path)
        _string(message.get("__typename"), f"{path}.__typename")
        messages.append(
            InVehicleMessageSummary(
                campaign_id=_nullable_string(
                    message.get("campaignId"),
                    f"{path}.campaignId",
                ),
                created_date_time=_nullable_datetime(
                    message.get("createdDateTime"),
                    f"{path}.createdDateTime",
                ),
                title=_nullable_string(message.get("title"), f"{path}.title"),
                viewed=_nullable_bool(message.get("viewed"), f"{path}.viewed"),
            )
        )
    return tuple(messages)


def parse_in_vehicle_message(data: Mapping[str, object]) -> InVehicleMessage | None:
    """Parse nullable detail for one in-vehicle message."""

    vehicle = _vehicle(data)
    if vehicle is None or "inVehicleMessage" not in vehicle:
        return None
    path = "vehicle.inVehicleMessage"
    message = _optional_object(vehicle.get("inVehicleMessage"), path)
    if message is None:
        return None
    _string(message.get("__typename"), f"{path}.__typename")
    return InVehicleMessage(
        title=_nullable_string(message.get("title"), f"{path}.title"),
        campaign_id=_nullable_string(
            message.get("campaignId"),
            f"{path}.campaignId",
        ),
        viewed=_nullable_bool(message.get("viewed"), f"{path}.viewed"),
        text=_nullable_string(message.get("text"), f"{path}.text"),
        expire_date=_nullable_datetime(
            message.get("expireDate"),
            f"{path}.expireDate",
        ),
    )


def _parse_legacy_push_result(data: Mapping[str, object], root_field: str) -> bool | None:
    if root_field not in data:
        raise ResponseError(f"{root_field} is missing")
    return _nullable_bool(data.get(root_field), root_field)


def _parse_device_push_result(
    data: Mapping[str, object],
    root_field: str,
) -> PushNotificationResult | None:
    if root_field not in data:
        raise ResponseError(f"{root_field} is missing")
    result = _optional_object(data.get(root_field), root_field)
    if result is None:
        return None

    typename = _string(result.get("__typename"), f"{root_field}.__typename")
    if typename == "GeneralMessage":
        return PushNotificationSuccess(
            message=_string(result.get("message"), f"{root_field}.message")
        )
    if typename == "DatabaseError":
        return PushNotificationDatabaseError(
            error_message=_string(
                result.get("errorMessage"),
                f"{root_field}.errorMessage",
            )
        )
    if typename == "TokenError":
        return PushNotificationTokenError(
            error_message=_string(
                result.get("errorMessage"),
                f"{root_field}.errorMessage",
            )
        )
    raise ResponseError(f"Unsupported {root_field} type: {typename}")


def _vehicle(data: Mapping[str, object]) -> Mapping[str, object] | None:
    if "vehicle" not in data:
        raise ResponseError("vehicle is missing")
    vehicle = _optional_object(data.get("vehicle"), "vehicle")
    if vehicle is not None:
        _string(vehicle.get("__typename"), "vehicle.__typename")
    return vehicle


def _object(value: object, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ResponseError(f"{path} is not an object")
    return value


def _optional_object(value: object, path: str) -> Mapping[str, object] | None:
    if value is None:
        return None
    return _object(value, path)


def _nullable_list(value: object, path: str) -> list[object] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        raise ResponseError(f"{path} is not a list")
    return value


def _string(value: object, path: str) -> str:
    if not isinstance(value, str):
        raise ResponseError(f"{path} is not a string")
    return value


def _nullable_string(value: object, path: str) -> str | None:
    if value is None:
        return None
    return _string(value, path)


def _nullable_bool(value: object, path: str) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ResponseError(f"{path} is not a boolean")
    return value


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
