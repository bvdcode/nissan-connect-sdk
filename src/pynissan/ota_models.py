from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class OtaUpdateState(StrEnum):
    """Known software-update states reported by Nissan."""

    READY_FOR_DOWNLOAD = "READY_FOR_DOWNLOAD"
    DOWNLOADING = "DOWNLOADING"
    INSTALLING = "INSTALLING"
    READY_FOR_ACTIVATION = "READY_FOR_ACTIVATION"
    ACTIVATION_SCHEDULED = "ACTIVATION_SCHEDULED"
    ACTIVATING = "ACTIVATING"
    ACTIVATION_COMPLETED = "ACTIVATION_COMPLETED"
    ACTIVATION_FAILED_RETRYABLE = "ACTIVATION_FAILED_RETRYABLE"
    ACTIVATION_FAILED_NOT_RETRYABLE = "ACTIVATION_FAILED_NOT_RETRYABLE"
    UNKNOWN_VALUE = "UNKNOWN__"


class DataWipeType(StrEnum):
    """Vehicle components accepted by Nissan's remote data-wipe operation."""

    WIPE = "WIPE"
    TCU_WIPE = "TCU_WIPE"
    HU_WIPE = "HU_WIPE"
    UNKNOWN_VALUE = "UNKNOWN__"


@dataclass(frozen=True, slots=True)
class OtaUpdateStatus:
    """Current state and optional timing details for an OTA campaign."""

    status: OtaUpdateState | None
    activation_timer_value: datetime | None
    progress: int | None
    count_down_time_start: datetime | None
    count_down_delay: int | None


@dataclass(frozen=True, slots=True)
class OtaCampaignDescription:
    """Optional release notes and disclaimers for an OTA campaign."""

    global_release_note: str | None
    download_disclaimer: str | None
    activation_disclaimer: str | None
    activation_estimated_time: str | None


@dataclass(frozen=True, slots=True)
class OtaBatteryLevel:
    """Battery requirements reported for OTA activation."""

    activation_enabled: bool
    state_of_charge: float | None
    activation_minimum_battery_level: float | None


@dataclass(frozen=True, slots=True)
class OtaUpdate:
    """An OTA campaign currently associated with a vehicle."""

    campaign_operation_id: str
    status: OtaUpdateStatus
    campaign_description: OtaCampaignDescription
    battery_level: OtaBatteryLevel
    size: int | None
    last_checked: datetime | None
    activation_timer_value: datetime | None


@dataclass(frozen=True, slots=True)
class OtaUpdateErrorInfo:
    """One non-null error returned while an OTA campaign is progressing."""

    error_code: str
    error_message: str
    is_retryable: bool


@dataclass(frozen=True, slots=True)
class OtaUpdateProgress:
    """Latest progress and errors for one OTA campaign."""

    status: OtaUpdateState | None
    percentage: int | None
    error_info: tuple[OtaUpdateErrorInfo, ...] | None
