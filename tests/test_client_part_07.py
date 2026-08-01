from __future__ import annotations

from collections.abc import Mapping
from typing import cast

import pytest
from test_client import (
    FakeResponse,
    FakeSession,
    make_client,
    vehicle_subscription_payload,
    vehicle_subscription_product_payload,
)

from pynissan import (
    ResponseError,
    TemperatureUnit,
    V2LState,
    V2LStatus,
)


@pytest.mark.parametrize(
    ("subscriptions", "match"),
    [
        (None, r"subscriptions is not a list"),
        ([vehicle_subscription_payload(subscriptionId=None)], r"subscriptionId is not a string"),
        ([vehicle_subscription_payload(product=None)], r"product is not an object"),
        (
            [
                vehicle_subscription_payload(
                    product=vehicle_subscription_product_payload(services=None)
                )
            ],
            r"services is not a list",
        ),
        (
            [vehicle_subscription_payload(subscriptionStartDate="2026-01-01T12:00:00")],
            r"subscriptionStartDate is not an ISO-8601 date-time with an offset",
        ),
        (
            [vehicle_subscription_payload(nextBillingDate="not-a-date")],
            r"nextBillingDate is not an ISO-8601 date-time with an offset",
        ),
        ([vehicle_subscription_payload(isActive="true")], r"isActive is not a boolean"),
        (
            [
                vehicle_subscription_payload(
                    product=vehicle_subscription_product_payload(services=[1])
                )
            ],
            r"services\[0\] is not a string",
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_vehicle_subscriptions_rejects_contract_violations(
    subscriptions: object,
    match: str,
) -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "__typename": "BaseVehicle",
                        "capabilities": {
                            "__typename": "VehicleCapability",
                            "subscriptions": subscriptions,
                        },
                    }
                }
            },
        )
    )

    with pytest.raises(ResponseError, match=match):
        await make_client(session).async_get_vehicle_subscriptions("VIN")


@pytest.mark.asyncio
async def test_get_vehicle_capabilities_parses_service_accessories_contract() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "capabilities": {
                            "telematicsProgram": "NISSAN_CONNECT",
                            "status": "ENROLLED",
                            "serviceCapability": [
                                {
                                    "type": "CLIMATE_CONTROL",
                                    "enabled": True,
                                    "subscribed": True,
                                }
                            ],
                            "accessoriesDetails": {
                                "seatHeater": {
                                    "enabled": True,
                                    "accessories": {
                                        "assistantSeat": "HEATING_AND_COOLING",
                                        "driverSeat": "HEATING_AND_COOLING",
                                        "secondCentreSeat": None,
                                        "secondLeftSeat": "HEATING",
                                        "secondRightSeat": "HEATING",
                                        "thirdLeftSeat": None,
                                        "thirdRightSeat": None,
                                    },
                                },
                                "steeringHeat": {"enabled": True},
                                "sunRoof": {"type": "ELECTRIC", "enabled": True},
                                "windowStatus": {"enabled": True},
                                "wayPoint": {"enabled": True, "maxNumber": 5},
                                "hvacTemperatures": {
                                    "unit": "CELSIUS",
                                    "default": 22.0,
                                    "min": 16.0,
                                    "max": 30.0,
                                    "resolution": 0.5,
                                },
                            },
                        }
                    }
                }
            },
        )
    )
    client = make_client(session)

    capabilities = await client.async_get_vehicle_capabilities(
        "JN1TESTVIN",
        temperature_unit=TemperatureUnit.CELSIUS,
    )

    assert capabilities.telematics_program == "NISSAN_CONNECT"
    assert capabilities.enrollment_status == "ENROLLED"
    assert len(capabilities.services) == 1
    assert capabilities.services[0].type == "CLIMATE_CONTROL"
    assert capabilities.accessories_details is not None

    accessories = capabilities.accessories_details
    assert accessories.seat_heater is not None
    assert accessories.seat_heater.enabled is True
    assert accessories.seat_heater.accessories is not None
    seats = accessories.seat_heater.accessories
    assert seats.assistant_seat == "HEATING_AND_COOLING"
    assert seats.driver_seat == "HEATING_AND_COOLING"
    assert seats.second_centre_seat is None
    assert seats.second_left_seat == "HEATING"
    assert seats.second_right_seat == "HEATING"
    assert seats.third_left_seat is None
    assert seats.third_right_seat is None

    assert accessories.steering_heat is not None
    assert accessories.steering_heat.enabled is True
    assert accessories.sun_roof is not None
    assert accessories.sun_roof.type == "ELECTRIC"
    assert accessories.sun_roof.enabled is True
    assert accessories.window_status is not None
    assert accessories.window_status.enabled is True
    assert accessories.way_point is not None
    assert accessories.way_point.enabled is True
    assert accessories.way_point.max_number == 5
    assert accessories.hvac_temperatures is not None
    assert accessories.hvac_temperatures.unit == "CELSIUS"
    assert accessories.hvac_temperatures.default == 22.0
    assert accessories.hvac_temperatures.minimum == 16.0
    assert accessories.hvac_temperatures.maximum == 30.0
    assert accessories.hvac_temperatures.resolution == 0.5

    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "VehicleCapabilities"
    assert payload["variables"] == {"vin": "JN1TESTVIN", "unit": "CELSIUS"}
    assert "accessoriesDetails" in cast(str, payload["query"])


@pytest.mark.asyncio
async def test_get_charge_config_parses_both_limits() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "chargeConfig": {
                            "limits": {
                                "notification": {"percent": 25},
                                "charge": {"percent": 80},
                            }
                        }
                    }
                }
            },
        )
    )
    client = make_client(session)

    config = await client.async_get_charge_config("JN1TESTVIN")

    assert config is not None
    assert config.charge_limit_percent == 80
    assert config.notification_threshold_percent == 25
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "ChargeConfig"
    assert payload["variables"] == {"vin": "JN1TESTVIN"}


@pytest.mark.asyncio
async def test_get_v2l_status_parses_state_and_percentage_levels() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "v2lStatus": {
                            "state": "OUTSIDE_ON",
                            "chargeLimitationLevel": 35,
                            "chargeMinimumLimitationLevel": 10.5,
                        }
                    }
                }
            },
        )
    )
    client = make_client(session)

    status = await client.async_get_v2l_status("JN1TESTVIN")

    assert status == V2LStatus(
        state=V2LState.OUTSIDE_ON,
        charge_limit_percent=35.0,
        minimum_charge_limit_percent=10.5,
    )
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "V2lStatus"
    assert payload["variables"] == {"vin": "JN1TESTVIN"}
    assert "chargeMinimumLimitationLevel" in cast(str, payload["query"])


@pytest.mark.asyncio
async def test_get_v2l_status_preserves_nulls_and_unknown_state() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "v2lStatus": {
                            "state": "FUTURE_STATE",
                            "chargeLimitationLevel": None,
                            "chargeMinimumLimitationLevel": None,
                        }
                    }
                }
            },
        )
    )
    client = make_client(session)

    status = await client.async_get_v2l_status("JN1TESTVIN")

    assert status == V2LStatus(
        state=V2LState.UNKNOWN_VALUE,
        charge_limit_percent=None,
        minimum_charge_limit_percent=None,
    )
