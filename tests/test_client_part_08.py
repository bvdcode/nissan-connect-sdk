from __future__ import annotations

from collections.abc import Mapping
from typing import cast

import pytest
from test_client import (
    FakeResponse,
    FakeSession,
    make_client,
)

from pynissan import (
    ChargeHistoryAggregator,
    ClimateSettings,
    GraphQLError,
    ReadOnlyError,
    SeatClimateOption,
    ServiceRequest,
    ServiceRequestKind,
    TemperatureUnit,
    Tokens,
)


@pytest.mark.asyncio
async def test_get_charge_history_parses_all_service_fields_and_units() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "chargeHistory": {
                            "charges": [
                                {
                                    "start": "2026-07-01T08:15:00Z",
                                    "end": "2026-07-01T09:45:00Z",
                                    "duration": "PT1H30M",
                                    "recoveredEnergy": 31.25,
                                }
                            ],
                            "chargeSummaries": [
                                {
                                    "day": 1,
                                    "month": 7,
                                    "year": 2026,
                                    "numberOfChargeSessions": 2,
                                    "totalEnergyRecovered": 44.5,
                                    "totalDuration": 135,
                                    "numberOfErrors": 1,
                                    "userId": "driver-1",
                                    "roleType": "PRIMARY",
                                }
                            ],
                        }
                    }
                }
            },
        )
    )
    client = make_client(session)

    history = await client.async_get_charge_history(
        "JN1TESTVIN",
        ChargeHistoryAggregator.DAILY,
    )

    assert history is not None
    assert len(history.charges) == 1
    charge = history.charges[0]
    assert charge.start is not None
    assert charge.start.isoformat() == "2026-07-01T08:15:00+00:00"
    assert charge.end is not None
    assert charge.end.isoformat() == "2026-07-01T09:45:00+00:00"
    assert charge.duration == "PT1H30M"
    assert charge.recovered_energy_kwh == 31.25

    assert len(history.charge_summaries) == 1
    summary = history.charge_summaries[0]
    assert summary.day == 1
    assert summary.month == 7
    assert summary.year == 2026
    assert summary.number_of_charge_sessions == 2
    assert summary.total_energy_recovered_kwh == 44.5
    assert summary.total_duration_minutes == 135
    assert summary.number_of_errors == 1
    assert summary.user_id == "driver-1"
    assert summary.role_type == "PRIMARY"

    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "VehicleChargeHistory"
    assert payload["variables"] == {
        "vin": "JN1TESTVIN",
        "aggregator": "DAILY",
    }


@pytest.mark.asyncio
async def test_get_climate_schedules_parses_accessories_and_delayed_schedule() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "climateSchedules": [
                            {
                                "id": "schedule-1",
                                "state": "ON",
                                "startDateTime": "2026-08-01T07:30:00Z",
                                "weekDays": ["MO", "WE"],
                                "temperature": {
                                    "value": 21.5,
                                    "unit": "CELSIUS",
                                },
                            }
                        ],
                        "climateSchedulesAccessories": {
                            "defrostAndDeicerState": "ON",
                            "steeringWheelHeaterState": "OFF",
                            "seatsClimate": {
                                "frontDriverState": "HEAT",
                                "frontPassengerState": "OFF",
                                "rearLeftPassengerState": "COOL",
                                "rearRightPassengerState": None,
                                "rearCenterPassengerState": None,
                                "thirdLeftState": None,
                                "thirdRightState": None,
                            },
                        },
                        "delayedClimateSchedule": {"startDateTime": "2026-08-01T08:15:00Z"},
                    }
                }
            },
        )
    )
    client = make_client(session)

    result = await client.async_get_climate_schedules(
        "JN1TESTVIN",
        temperature_unit=TemperatureUnit.CELSIUS,
    )

    assert len(result.schedules) == 1
    schedule = result.schedules[0]
    assert schedule.id == "schedule-1"
    assert schedule.state == "ON"
    assert schedule.start_date_time.isoformat() == "2026-08-01T07:30:00+00:00"
    assert tuple(day.value for day in schedule.week_days) == ("MO", "WE")
    assert schedule.temperature.value == 21.5
    assert schedule.temperature.unit == "CELSIUS"

    assert result.accessories is not None
    assert result.accessories.defrost_and_deicer is True
    assert result.accessories.steering_wheel_heater is False
    assert result.accessories.seats is not None
    assert result.accessories.seats.front_driver is SeatClimateOption.HEAT
    assert result.accessories.seats.front_passenger is SeatClimateOption.OFF
    assert result.accessories.seats.rear_left is SeatClimateOption.COOL
    assert result.accessories.seats.rear_right is None
    assert result.accessories.seats.rear_center is None
    assert result.accessories.seats.third_left is None
    assert result.accessories.seats.third_right is None

    assert result.delayed_schedule is not None
    assert result.delayed_schedule.start_date_time is not None
    assert result.delayed_schedule.start_date_time.isoformat() == "2026-08-01T08:15:00+00:00"

    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "VehicleClimateSchedules"
    assert payload["variables"] == {
        "vin": "JN1TESTVIN",
        "temperatureUnit": "CELSIUS",
    }


@pytest.mark.asyncio
async def test_graphql_keeps_partial_vehicle_data() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "__typename": "ElectricAVK2Vehicle",
                        "batteryStatus": {"level": 11},
                    }
                },
                "errors": [{"message": "An unrelated field could not be resolved"}],
            },
        )
    )
    client = make_client(session)

    status = await client.async_get_vehicle_status("JN1TESTVIN")

    assert status.battery is not None
    assert status.battery.level == 11


@pytest.mark.asyncio
async def test_graphql_raises_operation_error_when_all_data_is_null() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {"startClimate": None},
                "errors": [{"message": "Unauthorized field or type"}],
            },
        )
    )
    client = make_client(session, read_only=False)

    with pytest.raises(GraphQLError) as raised:
        await client.async_start_climate(
            "JN1TESTVIN",
            ClimateSettings(72.0, TemperatureUnit.FAHRENHEIT),
        )

    assert raised.value.messages == ("Unauthorized field or type",)


@pytest.mark.asyncio
async def test_graphql_omits_id_token_header_when_not_issued() -> None:
    session = FakeSession(FakeResponse(200, {"data": {"vehicles": []}}))
    client = make_client(session, tokens=Tokens("access-token", "refresh-token"))

    vehicles = await client.async_get_vehicles()

    assert vehicles == ()
    headers = cast(Mapping[str, str], session.calls[0]["headers"])
    assert "id-token" not in headers


@pytest.mark.asyncio
async def test_read_only_blocks_commands_before_network_request() -> None:
    session = FakeSession()
    client = make_client(session)

    with pytest.raises(ReadOnlyError):
        await client.async_start_climate(
            "JN1TESTVIN",
            ClimateSettings(72.0, TemperatureUnit.FAHRENHEIT),
        )

    assert session.calls == []


@pytest.mark.asyncio
async def test_set_charge_notification_threshold_respects_read_only_mode() -> None:
    session = FakeSession()
    client = make_client(session)

    with pytest.raises(ReadOnlyError):
        await client.async_set_charge_notification_threshold("JN1TESTVIN", 25)

    assert session.calls == []


@pytest.mark.asyncio
async def test_set_charge_notification_threshold_returns_request() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {"data": {"setChargeNotificationThreshold": {"serviceRequestId": "request-456"}}},
        )
    )
    client = make_client(session, read_only=False)

    request = await client.async_set_charge_notification_threshold("JN1TESTVIN", 25)

    assert request == ServiceRequest(
        "request-456",
        ServiceRequestKind.CHARGE_CONFIGURATION,
    )
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "SetNotificationLimit"
    assert payload["variables"] == {"vin": "JN1TESTVIN", "percent": 25}


@pytest.mark.asyncio
async def test_set_v2l_minimum_battery_level_respects_read_only_mode() -> None:
    session = FakeSession()
    client = make_client(session)

    with pytest.raises(ReadOnlyError):
        await client.async_set_v2l_minimum_battery_charge_level("JN1TESTVIN", 30)

    assert session.calls == []


@pytest.mark.asyncio
async def test_set_v2l_minimum_battery_level_returns_request() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {"data": {"setV2L": {"serviceRequestId": "request-v2l"}}},
        )
    )
    client = make_client(session, read_only=False)

    request = await client.async_set_v2l_minimum_battery_charge_level(
        "JN1TESTVIN",
        30,
    )

    assert request == ServiceRequest("request-v2l", ServiceRequestKind.V2L)
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "SetV2L"
    assert payload["variables"] == {
        "vin": "JN1TESTVIN",
        "input": {"minimumBatteryChargeLevel": 30},
    }
