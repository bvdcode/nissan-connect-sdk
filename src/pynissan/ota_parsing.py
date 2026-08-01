from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime

from .exceptions import ResponseError
from .ota_models import (
    OtaBatteryLevel,
    OtaCampaignDescription,
    OtaUpdate,
    OtaUpdateErrorInfo,
    OtaUpdateProgress,
    OtaUpdateState,
    OtaUpdateStatus,
)


def parse_ota_update(data: Mapping[str, object]) -> OtaUpdate | None:
    """Parse the OTA campaign exposed by a compatible EVO vehicle."""

    vehicle = _optional_object(data.get("vehicle"), "vehicle")
    if vehicle is None or "otaUpdate" not in vehicle:
        return None

    path = "vehicle.otaUpdate"
    value = _object(vehicle.get("otaUpdate"), path)
    status = _object(value.get("status"), f"{path}.status")
    campaign = _object(
        value.get("campaignDescription"),
        f"{path}.campaignDescription",
    )
    battery = _object(value.get("batteryLevel"), f"{path}.batteryLevel")
    return OtaUpdate(
        campaign_operation_id=_string(
            value.get("campaignOperationId"),
            f"{path}.campaignOperationId",
        ),
        status=OtaUpdateStatus(
            status=_nullable_state(status.get("status"), f"{path}.status.status"),
            activation_timer_value=_nullable_datetime(
                status.get("activationTimerValue"),
                f"{path}.status.activationTimerValue",
            ),
            progress=_nullable_int(status.get("progress"), f"{path}.status.progress"),
            count_down_time_start=_nullable_datetime(
                status.get("countDownTimeStart"),
                f"{path}.status.countDownTimeStart",
            ),
            count_down_delay=_nullable_int(
                status.get("countDownDelay"),
                f"{path}.status.countDownDelay",
            ),
        ),
        campaign_description=OtaCampaignDescription(
            global_release_note=_nullable_string(
                campaign.get("globalReleaseNote"),
                f"{path}.campaignDescription.globalReleaseNote",
            ),
            download_disclaimer=_nullable_string(
                campaign.get("downloadDisclaimer"),
                f"{path}.campaignDescription.downloadDisclaimer",
            ),
            activation_disclaimer=_nullable_string(
                campaign.get("activationDisclaimer"),
                f"{path}.campaignDescription.activationDisclaimer",
            ),
            activation_estimated_time=_nullable_string(
                campaign.get("activationEstimatedTime"),
                f"{path}.campaignDescription.activationEstimatedTime",
            ),
        ),
        battery_level=OtaBatteryLevel(
            activation_enabled=_bool(
                battery.get("activationEnabled"),
                f"{path}.batteryLevel.activationEnabled",
            ),
            state_of_charge=_nullable_float(
                battery.get("stateOfCharge"),
                f"{path}.batteryLevel.stateOfCharge",
            ),
            activation_minimum_battery_level=_nullable_float(
                battery.get("activationMinimumBatteryLevel"),
                f"{path}.batteryLevel.activationMinimumBatteryLevel",
            ),
        ),
        size=_nullable_int(value.get("size"), f"{path}.size"),
        last_checked=_nullable_datetime(
            value.get("lastChecked"),
            f"{path}.lastChecked",
        ),
        activation_timer_value=_nullable_datetime(
            value.get("activationTimerValue"),
            f"{path}.activationTimerValue",
        ),
    )


def parse_ota_update_progress(
    data: Mapping[str, object],
) -> OtaUpdateProgress | None:
    """Parse progress for one OTA campaign on a compatible EVO vehicle."""

    vehicle = _optional_object(data.get("vehicle"), "vehicle")
    if vehicle is None or "otaUpdateProgress" not in vehicle:
        return None

    path = "vehicle.otaUpdateProgress"
    value = _object(vehicle.get("otaUpdateProgress"), path)
    raw_errors = _nullable_list(value.get("errorInfo"), f"{path}.errorInfo")
    errors: tuple[OtaUpdateErrorInfo, ...] | None = None
    if raw_errors is not None:
        parsed_errors: list[OtaUpdateErrorInfo] = []
        for index, raw_error in enumerate(raw_errors):
            error_path = f"{path}.errorInfo[{index}]"
            error = _object(raw_error, error_path)
            parsed_errors.append(
                OtaUpdateErrorInfo(
                    error_code=_string(error.get("errorCode"), f"{error_path}.errorCode"),
                    error_message=_string(
                        error.get("errorMessage"),
                        f"{error_path}.errorMessage",
                    ),
                    is_retryable=_bool(
                        error.get("isRetryable"),
                        f"{error_path}.isRetryable",
                    ),
                )
            )
        errors = tuple(parsed_errors)

    return OtaUpdateProgress(
        status=_nullable_state(value.get("status"), f"{path}.status"),
        percentage=_nullable_int(value.get("percentage"), f"{path}.percentage"),
        error_info=errors,
    )


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


def _bool(value: object, path: str) -> bool:
    if not isinstance(value, bool):
        raise ResponseError(f"{path} is not a boolean")
    return value


def _nullable_int(value: object, path: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise ResponseError(f"{path} is not an integer")
    return value


def _nullable_float(value: object, path: str) -> float | None:
    if value is None:
        return None
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ResponseError(f"{path} is not numeric")
    return float(value)


def _nullable_state(value: object, path: str) -> OtaUpdateState | None:
    if value is None:
        return None
    raw_value = _string(value, path)
    try:
        return OtaUpdateState(raw_value)
    except ValueError:
        return OtaUpdateState.UNKNOWN_VALUE


def _nullable_datetime(value: object, path: str) -> datetime | None:
    if value is None:
        return None
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
