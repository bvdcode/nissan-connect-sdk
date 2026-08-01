from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class DeviceOS(StrEnum):
    """Mobile operating systems accepted by Nissan's push API."""

    IOS = "IOS"
    ANDROID = "ANDROID"
    UNKNOWN_VALUE = "UNKNOWN__"


@dataclass(frozen=True, slots=True)
class InVehicleMessageSummary:
    """Nullable summary fields returned for one in-vehicle message."""

    campaign_id: str | None
    created_date_time: datetime | None
    title: str | None
    viewed: bool | None


@dataclass(frozen=True, slots=True)
class InVehicleMessage:
    """Nullable detail fields returned for one in-vehicle message."""

    title: str | None
    campaign_id: str | None
    viewed: bool | None
    text: str | None
    expire_date: datetime | None


@dataclass(frozen=True, slots=True)
class PushNotificationSuccess:
    """Successful result from the current device push API."""

    message: str


@dataclass(frozen=True, slots=True)
class PushNotificationDatabaseError:
    """Database failure returned by the current device push API."""

    error_message: str


@dataclass(frozen=True, slots=True)
class PushNotificationTokenError:
    """Push-token failure returned by the current device push API."""

    error_message: str


type PushNotificationResult = (
    PushNotificationSuccess | PushNotificationDatabaseError | PushNotificationTokenError
)
