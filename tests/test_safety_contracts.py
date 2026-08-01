from __future__ import annotations

from datetime import UTC, datetime
from typing import cast

import pytest
from aiohttp import ClientSession

from pynissan import (
    AlertScheduleInput,
    ChargeScheduleInput,
    ClimateSettings,
    CurfewAlertInput,
    DistanceUnit,
    NissanClient,
    ServiceRequestStatus,
    SpeedUnit,
    TemperatureUnit,
    Tokens,
    WeekDay,
)
from pynissan.parsing import parse_service_request_result


class NoNetworkSession:
    def post(self, url: str, **kwargs: object) -> None:
        raise AssertionError(f"unexpected network request to {url}")


def make_client() -> NissanClient:
    return NissanClient(
        cast(ClientSession, NoNetworkSession()),
        tokens=Tokens("access", "refresh", "identity"),
        read_only=False,
    )


@pytest.mark.asyncio
async def test_core_unknown_input_enums_are_rejected_before_network() -> None:
    client = make_client()

    with pytest.raises(ValueError, match="UNKNOWN_VALUE"):
        await client.async_get_vehicle_status("VIN", distance_unit=DistanceUnit.UNKNOWN_VALUE)
    with pytest.raises(ValueError, match="UNKNOWN_VALUE"):
        await client.async_get_vehicle_alerts("VIN", speed_unit=SpeedUnit.UNKNOWN_VALUE)
    with pytest.raises(ValueError, match="UNKNOWN_VALUE"):
        await client.async_start_climate(
            "VIN",
            ClimateSettings(72, TemperatureUnit.UNKNOWN_VALUE),
        )
    with pytest.raises(ValueError, match="UNKNOWN_VALUE"):
        await client.async_create_charge_schedule(
            "VIN",
            ChargeScheduleInput(
                datetime(2026, 8, 1, tzinfo=UTC),
                "PT1H",
                (WeekDay.UNKNOWN_VALUE,),
            ),
        )
    with pytest.raises(ValueError, match="UNKNOWN_VALUE"):
        await client.async_create_curfew_alert(
            "VIN",
            CurfewAlertInput(
                "Night",
                True,
                AlertScheduleInput(
                    datetime(2026, 8, 1, tzinfo=UTC),
                    "PT1H",
                    (WeekDay.UNKNOWN_VALUE,),
                ),
            ),
        )


def test_unrecognized_service_request_status_is_not_terminal() -> None:
    result = parse_service_request_result(
        {"checkDoorRequest": {"status": "FUTURE_IN_PROGRESS_STATUS"}},
        "checkDoorRequest",
        "VIN",
    )

    assert result.status is ServiceRequestStatus.UNKNOWN_VALUE
    assert result.is_terminal is False
    assert result.is_success is False
