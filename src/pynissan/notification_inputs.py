from __future__ import annotations

from dataclasses import dataclass

from .graphql_input import UNSET, UnsetType, optional_input_fields, serialize_enum
from .notification_models import NotificationCategory, NotificationDestination


@dataclass(frozen=True, slots=True)
class NotificationTypeInput:
    """Required opt-in value for one notification delivery channel."""

    destination: NotificationDestination
    opt_in: bool


@dataclass(frozen=True, slots=True)
class NotificationPreferenceInput:
    """Required notification category and its channel preferences."""

    notification_category: NotificationCategory
    notification_type: tuple[NotificationTypeInput | None, ...]


def notification_type_input(value: NotificationTypeInput) -> dict[str, object]:
    """Serialize one notification-channel preference."""

    return {
        "destination": notification_destination_input(value.destination),
        "optIn": value.opt_in,
    }


def notification_preference_input(value: NotificationPreferenceInput) -> dict[str, object]:
    """Serialize one notification-category preference."""

    return {
        "notificationCategory": notification_category_input(value.notification_category),
        "notificationType": [
            notification_type_input(item) if item is not None else None
            for item in value.notification_type
        ],
    }


def notification_preferences_input(
    values: tuple[NotificationPreferenceInput | None, ...],
) -> list[object]:
    """Serialize the non-null preferences list accepted by Nissan."""

    return [notification_preference_input(value) if value is not None else None for value in values]


def notification_category_input(value: NotificationCategory) -> str:
    """Serialize a schema-valid notification category."""

    return serialize_enum(value)


def notification_destination_input(value: NotificationDestination) -> str:
    """Serialize a schema-valid notification destination."""

    return serialize_enum(value)


def update_nissan_energy_notification_preferences_variables(
    vin: str,
    *,
    email_status: bool | UnsetType | None = UNSET,
    push_status: bool | UnsetType | None = UNSET,
    sms_status: bool | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Build the Nissan Energy patch while preserving omitted and null values."""

    return {
        "config": optional_input_fields(
            vin=vin,
            emailStatus=email_status,
            pushStatus=push_status,
            smsStatus=sms_status,
        )
    }
