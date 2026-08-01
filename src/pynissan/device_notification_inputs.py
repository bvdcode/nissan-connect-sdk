from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .device_notification_models import DeviceOS
from .graphql_input import UNSET, UnsetType, optional_input_fields, serialize_enum

MYNISSAN_ANDROID_APP_NAME: Final = "mynissan-android"


@dataclass(frozen=True, slots=True)
class MobileInput:
    """One mobile device registered to receive Nissan push notifications."""

    device_id: str
    device_os: DeviceOS
    app_name: str
    token: str


@dataclass(frozen=True, slots=True)
class MobileInfoInput:
    """Top-level device input accepted by Nissan's current push API."""

    mobile: MobileInput


def device_os_input(value: DeviceOS) -> str:
    """Serialize a schema-valid mobile operating system."""

    return serialize_enum(value)


def current_device_type_input(value: DeviceOS) -> str:
    """Map the schema enum to the title-cased string used by the current API."""

    raw_value = serialize_enum(value)
    return {"ANDROID": "Android", "IOS": "Ios"}[raw_value]


def mobile_input(value: MobileInput) -> dict[str, object]:
    """Serialize one mobile device using Nissan's GraphQL field names."""

    return {
        "deviceId": value.device_id,
        "deviceType": current_device_type_input(value.device_os),
        "appName": value.app_name,
        "token": value.token,
    }


def mobile_info_input(value: MobileInfoInput) -> dict[str, object]:
    """Serialize the wrapper required by device push registration."""

    return {"mobile": mobile_input(value.mobile)}


def register_push_notifications_variables(
    device_id: str,
    token: str,
    device_os: DeviceOS,
) -> dict[str, object]:
    """Build variables for the legacy push registration mutation."""

    return {
        "deviceId": device_id,
        "token": token,
        "deviceOS": device_os_input(device_os),
    }


def unregister_push_notifications_variables(
    device_id: str,
    device_os: DeviceOS,
) -> dict[str, object]:
    """Build variables for the legacy push unregistration mutation."""

    return {
        "deviceId": device_id,
        "deviceOS": device_os_input(device_os),
    }


def register_device_for_push_notifications_variables(
    value: MobileInfoInput,
) -> dict[str, object]:
    """Build variables for the current device push registration mutation."""

    return {"mobileInfoInput": mobile_info_input(value)}


def unregister_device_for_push_notifications_variables(
    app_name: str,
    device_id: str,
    device_os: DeviceOS,
) -> dict[str, object]:
    """Build variables for the current device push unregistration mutation."""

    return {
        "appName": app_name,
        "deviceId": device_id,
        "deviceType": current_device_type_input(device_os),
    }


def in_vehicle_messages_variables(vin: str) -> dict[str, object]:
    """Build variables for the in-vehicle message list query."""

    return {"vin": vin}


def in_vehicle_message_variables(
    vin: str,
    campaign_id: str,
    push: bool | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Build detail-query variables while preserving omitted and null push values."""

    return optional_input_fields(
        vin=vin,
        campaignId=campaign_id,
        push=push,
    )
