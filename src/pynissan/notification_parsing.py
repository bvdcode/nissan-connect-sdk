from __future__ import annotations

from collections.abc import Mapping

from .exceptions import ResponseError
from .notification_models import (
    NissanEnergyNotificationPreferences,
    NissanEnergyNotificationPreferencesUpdate,
    NotificationCategory,
    NotificationDestination,
    NotificationPreference,
    NotificationTypePreference,
)


def parse_nissan_energy_notification_preferences(
    data: Mapping[str, object],
) -> NissanEnergyNotificationPreferences | None:
    """Parse the nullable Nissan Energy notification-preference chain."""

    account_status = _required_optional_object(data, "accountStatus", "accountStatus")
    if account_status is None:
        return None
    _string(account_status.get("__typename"), "accountStatus.__typename")
    account_data = _required_optional_object(
        account_status,
        "data",
        "accountStatus.data",
    )
    if account_data is None:
        return None
    _string(account_data.get("__typename"), "accountStatus.data.__typename")
    preferences = _required_optional_object(
        account_data,
        "notificationPreferences",
        "accountStatus.data.notificationPreferences",
    )
    if preferences is None:
        return None
    return _parse_nissan_energy_preferences(
        preferences,
        "accountStatus.data.notificationPreferences",
    )


def parse_update_nissan_energy_notification_preferences(
    data: Mapping[str, object],
) -> NissanEnergyNotificationPreferencesUpdate | None:
    """Parse status and nullable result from the Nissan Energy mutation."""

    path = "updateNotificationPreferences"
    result = _required_optional_object(data, path, path)
    if result is None:
        return None
    _string(result.get("__typename"), f"{path}.__typename")
    preferences_data = _required_optional_object(result, "data", f"{path}.data")
    preferences = (
        _parse_nissan_energy_preferences(preferences_data, f"{path}.data")
        if preferences_data is not None
        else None
    )
    return NissanEnergyNotificationPreferencesUpdate(
        status_code=_nullable_string(result.get("statusCode"), f"{path}.statusCode"),
        status_message=_nullable_string(
            result.get("statusMessage"),
            f"{path}.statusMessage",
        ),
        timestamp=_nullable_string(result.get("timestamp"), f"{path}.timestamp"),
        preferences=preferences,
    )


def parse_notification_preferences(
    data: Mapping[str, object],
    root_field: str = "vehicle",
) -> tuple[NotificationPreference | None, ...] | None:
    """Parse preferences from the vehicle query or preference mutation."""

    container = _optional_object(data.get(root_field), root_field)
    if container is None or "notificationPreferences" not in container:
        return None
    values = _nullable_list(
        container.get("notificationPreferences"),
        f"{root_field}.notificationPreferences",
    )
    if values is None:
        return None

    preferences: list[NotificationPreference | None] = []
    for index, raw_preference in enumerate(values):
        if raw_preference is None:
            preferences.append(None)
            continue
        path = f"{root_field}.notificationPreferences[{index}]"
        preference = _object(raw_preference, path)
        raw_types = _list(
            preference.get("notificationType"),
            f"{path}.notificationType",
        )
        notification_types: list[NotificationTypePreference | None] = []
        for type_index, raw_type in enumerate(raw_types):
            if raw_type is None:
                notification_types.append(None)
                continue
            type_path = f"{path}.notificationType[{type_index}]"
            notification_type = _object(raw_type, type_path)
            notification_types.append(
                NotificationTypePreference(
                    destination=_destination(
                        notification_type.get("destination"),
                        f"{type_path}.destination",
                    ),
                    opt_in=_bool(
                        notification_type.get("optIn"),
                        f"{type_path}.optIn",
                    ),
                )
            )
        preferences.append(
            NotificationPreference(
                notification_category=_category(
                    preference.get("notificationCategory"),
                    f"{path}.notificationCategory",
                ),
                notification_type=tuple(notification_types),
            )
        )
    return tuple(preferences)


def _object(value: object, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ResponseError(f"{path} is not an object")
    return value


def _optional_object(value: object, path: str) -> Mapping[str, object] | None:
    if value is None:
        return None
    return _object(value, path)


def _required_optional_object(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> Mapping[str, object] | None:
    if field not in container:
        raise ResponseError(f"{path} is missing")
    return _optional_object(container.get(field), path)


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


def _bool(value: object, path: str) -> bool:
    if not isinstance(value, bool):
        raise ResponseError(f"{path} is not a boolean")
    return value


def _nullable_bool(value: object, path: str) -> bool | None:
    if value is None:
        return None
    return _bool(value, path)


def _parse_nissan_energy_preferences(
    value: Mapping[str, object],
    path: str,
) -> NissanEnergyNotificationPreferences:
    _string(value.get("__typename"), f"{path}.__typename")
    return NissanEnergyNotificationPreferences(
        email_status=_nullable_bool(value.get("emailStatus"), f"{path}.emailStatus"),
        push_status=_nullable_bool(value.get("pushStatus"), f"{path}.pushStatus"),
        sms_status=_nullable_bool(value.get("smsStatus"), f"{path}.smsStatus"),
    )


def _category(value: object, path: str) -> NotificationCategory:
    raw_value = _string(value, path)
    try:
        return NotificationCategory(raw_value)
    except ValueError:
        return NotificationCategory.UNKNOWN_VALUE


def _destination(value: object, path: str) -> NotificationDestination:
    raw_value = _string(value, path)
    try:
        return NotificationDestination(raw_value)
    except ValueError:
        return NotificationDestination.UNKNOWN_VALUE
