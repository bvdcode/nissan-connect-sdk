from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .graphql_input import UNSET, UnsetType, optional_input_fields


class V1GNotificationCategory(StrEnum):
    """Known notification-category strings accepted by the V1G API."""

    NEW_PRIME_TIME_HOURS = "New PrimeTime Hours"
    PRIME_TIME_UPCOMING_REMINDER = "PrimeTime Upcoming Reminder"
    MONTHLY_INSIGHTS = "Monthly Insights"
    PRIME_TIME_STATS_UPDATES = "PrimeTime Stats Updates"


@dataclass(frozen=True, slots=True)
class V1GNotificationPreferenceInput:
    """One V1G category patch with independently optional channel flags."""

    notification_category: str
    email_status: bool | UnsetType | None = UNSET
    push_status: bool | UnsetType | None = UNSET
    sms_status: bool | UnsetType | None = UNSET


def v1g_monitored_charging_account_status_variables(vin: str) -> dict[str, object]:
    """Serialize the required VIN for the V1G account-status query."""

    return {"vin": vin}


def v1g_tokenized_url_variables(vin: str) -> dict[str, object]:
    """Serialize the required VIN for the V1G tokenized-URL query."""

    return {"vin": vin}


def v1g_update_notification_preferences_variables(
    vin: str,
    *,
    preferences: (tuple[V1GNotificationPreferenceInput | None, ...] | UnsetType | None) = UNSET,
) -> dict[str, object]:
    """Serialize a V1G preference patch with Apollo omission semantics."""

    return {
        "config": optional_input_fields(
            vin=vin,
            v1GNotificationPreferences=_optional_preferences(preferences),
        )
    }


def v1g_enroll_monitored_charging_plan_variables(
    vin: str,
    model: str,
    year: str,
    *,
    plan: str | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize V1G enrollment without supplying an implicit plan."""

    return {
        "config": optional_input_fields(
            vin=vin,
            plan=plan,
            model=model,
            year=year,
        )
    }


def v1g_cancel_monitored_charging_plan_variables(vin: str) -> dict[str, object]:
    """Serialize the required V1G plan-cancellation input."""

    return {"config": {"vin": vin}}


def v1g_notification_preference_input(
    value: V1GNotificationPreferenceInput,
) -> dict[str, object]:
    """Serialize one nullable-field V1G notification preference."""

    return optional_input_fields(
        v1GNotificationCategory=_notification_category_input(value.notification_category),
        v1GEmailStatus=value.email_status,
        v1GPushStatus=value.push_status,
        v1GSmsStatus=value.sms_status,
    )


def _notification_category_input(value: str) -> str:
    if isinstance(value, V1GNotificationCategory):
        return value.value
    return value


def _optional_preferences(
    value: tuple[V1GNotificationPreferenceInput | None, ...] | UnsetType | None,
) -> object:
    if isinstance(value, UnsetType) or value is None:
        return value
    return [v1g_notification_preference_input(item) if item is not None else None for item in value]
