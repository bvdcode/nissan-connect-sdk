from __future__ import annotations

from collections.abc import Mapping

from .exceptions import ResponseError
from .v1g_models import (
    V1GAccountStatus,
    V1GMonitoredChargingAccountData,
    V1GMonitoredChargingAccountStatusResult,
    V1GMonitoredChargingPlanCancellationResult,
    V1GMonitoredChargingPlanEnrollmentData,
    V1GMonitoredChargingPlanEnrollmentResult,
    V1GNotificationPreference,
    V1GNotificationPreferencesUpdateResult,
    V1GTokenizedUrlData,
    V1GTokenizedUrlResult,
)


def parse_v1g_monitored_charging_account_status(
    data: Mapping[str, object],
) -> V1GMonitoredChargingAccountStatusResult | None:
    """Parse the raw nullable V1G monitored-account response."""

    root_field = "v1GMonitoredChargingAccountStatus"
    root = _root(data, root_field)
    if root is None:
        return None

    raw_data = _required_optional_typed_object(root, "data", f"{root_field}.data")
    account_data = None
    if raw_data is not None:
        path = f"{root_field}.data"
        account_data = V1GMonitoredChargingAccountData(
            account_status=_nullable_account_status(
                _required_value(
                    raw_data,
                    "v1GMonitoredChargingAccountStatus",
                    f"{path}.v1GMonitoredChargingAccountStatus",
                ),
                f"{path}.v1GMonitoredChargingAccountStatus",
            ),
            notification_preferences=_required_notification_preferences(
                raw_data,
                "v1GNotificationPreferences",
                f"{path}.v1GNotificationPreferences",
            ),
            vin=_nullable_string(
                _required_value(raw_data, "vin", f"{path}.vin"),
                f"{path}.vin",
            ),
        )

    return V1GMonitoredChargingAccountStatusResult(
        status_code=_nullable_string(
            _required_value(root, "statusCode", f"{root_field}.statusCode"),
            f"{root_field}.statusCode",
        ),
        data=account_data,
    )


def parse_v1g_update_notification_preferences(
    data: Mapping[str, object],
) -> V1GNotificationPreferencesUpdateResult | None:
    """Parse the raw nullable V1G notification-preference update."""

    root_field = "v1GUpdateNotificationPreferences"
    root = _root(data, root_field)
    if root is None:
        return None

    return V1GNotificationPreferencesUpdateResult(
        status_code=_nullable_string(
            _required_value(root, "statusCode", f"{root_field}.statusCode"),
            f"{root_field}.statusCode",
        ),
        status_message=_nullable_string(
            _required_value(root, "statusMessage", f"{root_field}.statusMessage"),
            f"{root_field}.statusMessage",
        ),
        timestamp=_nullable_string(
            _required_value(root, "timestamp", f"{root_field}.timestamp"),
            f"{root_field}.timestamp",
        ),
        notification_preferences=_required_notification_preferences(
            root,
            "v1GNotificationPreferences",
            f"{root_field}.v1GNotificationPreferences",
        ),
    )


def parse_v1g_tokenized_url(
    data: Mapping[str, object],
) -> V1GTokenizedUrlResult | None:
    """Parse the raw nullable V1G tokenized-URL response."""

    root_field = "v1GTokenizedUrl"
    root = _root(data, root_field)
    if root is None:
        return None

    raw_data = _required_optional_typed_object(root, "data", f"{root_field}.data")
    tokenized_url = None
    if raw_data is not None:
        path = f"{root_field}.data"
        tokenized_url = V1GTokenizedUrlData(
            url=_nullable_string(
                _required_value(raw_data, "url", f"{path}.url"),
                f"{path}.url",
            ),
            vin=_nullable_string(
                _required_value(raw_data, "vin", f"{path}.vin"),
                f"{path}.vin",
            ),
        )
    return V1GTokenizedUrlResult(data=tokenized_url)


def parse_v1g_enroll_monitored_charging_plan(
    data: Mapping[str, object],
) -> V1GMonitoredChargingPlanEnrollmentResult | None:
    """Parse the raw nullable V1G monitored-plan enrollment response."""

    root_field = "v1GEnrollMonitoredChargingPlan"
    root = _root(data, root_field)
    if root is None:
        return None

    raw_data = _required_optional_typed_object(root, "data", f"{root_field}.data")
    enrollment = None
    if raw_data is not None:
        path = f"{root_field}.data"
        enrollment = V1GMonitoredChargingPlanEnrollmentData(
            account_status=_nullable_account_status(
                _required_value(
                    raw_data,
                    "v1GMonitoredChargingAccountStatus",
                    f"{path}.v1GMonitoredChargingAccountStatus",
                ),
                f"{path}.v1GMonitoredChargingAccountStatus",
            )
        )
    return V1GMonitoredChargingPlanEnrollmentResult(data=enrollment)


def parse_v1g_cancel_monitored_charging_plan(
    data: Mapping[str, object],
) -> V1GMonitoredChargingPlanCancellationResult | None:
    """Parse the raw nullable V1G monitored-plan cancellation response."""

    root_field = "v1GCancelMonitoredChargingPlan"
    root = _root(data, root_field)
    if root is None:
        return None
    return V1GMonitoredChargingPlanCancellationResult(
        status_code=_nullable_string(
            _required_value(root, "statusCode", f"{root_field}.statusCode"),
            f"{root_field}.statusCode",
        )
    )


def _root(
    data: Mapping[str, object],
    root_field: str,
) -> Mapping[str, object] | None:
    return _required_optional_typed_object(data, root_field, root_field)


def _required_optional_typed_object(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> Mapping[str, object] | None:
    value = _required_value(container, field, path)
    if value is None:
        return None
    return _typed_object(value, path)


def _typed_object(value: object, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ResponseError(f"{path} is not an object")
    _string(
        _required_value(value, "__typename", f"{path}.__typename"),
        f"{path}.__typename",
    )
    return value


def _required_value(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> object:
    if field not in container:
        raise ResponseError(f"{path} is missing")
    return container[field]


def _required_notification_preferences(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> tuple[V1GNotificationPreference | None, ...] | None:
    value = _required_value(container, field, path)
    if value is None:
        return None
    if not isinstance(value, list):
        raise ResponseError(f"{path} is not a list")

    preferences: list[V1GNotificationPreference | None] = []
    for index, item in enumerate(value):
        if item is None:
            preferences.append(None)
            continue
        preferences.append(_parse_notification_preference(item, f"{path}[{index}]"))
    return tuple(preferences)


def _parse_notification_preference(
    value: object,
    path: str,
) -> V1GNotificationPreference:
    preference = _typed_object(value, path)
    return V1GNotificationPreference(
        notification_category=_nullable_string(
            _required_value(
                preference,
                "v1GNotificationCategory",
                f"{path}.v1GNotificationCategory",
            ),
            f"{path}.v1GNotificationCategory",
        ),
        email_status=_nullable_bool(
            _required_value(preference, "v1GEmailStatus", f"{path}.v1GEmailStatus"),
            f"{path}.v1GEmailStatus",
        ),
        push_status=_nullable_bool(
            _required_value(preference, "v1GPushStatus", f"{path}.v1GPushStatus"),
            f"{path}.v1GPushStatus",
        ),
        sms_status=_nullable_bool(
            _required_value(preference, "v1GSmsStatus", f"{path}.v1GSmsStatus"),
            f"{path}.v1GSmsStatus",
        ),
    )


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


def _nullable_account_status(
    value: object,
    path: str,
) -> V1GAccountStatus | None:
    raw_value = _nullable_string(value, path)
    if raw_value is None:
        return None
    try:
        return V1GAccountStatus(raw_value)
    except ValueError:
        return V1GAccountStatus.UNKNOWN_VALUE
