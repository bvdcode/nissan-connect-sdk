from __future__ import annotations

import hashlib
from collections.abc import Mapping
from typing import cast

import pytest
from aiohttp import ClientSession

from pynissan import (
    BatteryStatus,
    ClimateStatus,
    DistanceReading,
    DistanceUnit,
    DoorsStatus,
    NissanClient,
    ResponseError,
    SpeedUnit,
    TemperatureReading,
    TemperatureUnit,
    Tokens,
    VehicleModelYear,
    VehicleNickname,
    VehicleStatus,
    VehicleStatusAndRecalls,
    operations,
)
from pynissan.vehicle_detail_inputs import (
    vehicle_battery_status_variables,
    vehicle_boundary_alerts_variables,
    vehicle_climate_status_variables,
    vehicle_curfew_alerts_variables,
    vehicle_doors_status_variables,
    vehicle_model_year_variables,
    vehicle_nickname_variables,
    vehicle_speed_alerts_variables,
    vehicle_status_and_recalls_variables,
    vehicle_status_variables,
    vehicle_valet_alerts_variables,
)
from pynissan.vehicle_detail_parsing import (
    parse_vehicle_battery_status,
    parse_vehicle_boundary_alerts,
    parse_vehicle_climate_status,
    parse_vehicle_core_status,
    parse_vehicle_curfew_alerts,
    parse_vehicle_doors_status,
    parse_vehicle_model_year,
    parse_vehicle_nickname,
    parse_vehicle_speed_alerts,
    parse_vehicle_status_and_recalls,
    parse_vehicle_valet_alert,
)

EXPECTED_OPERATIONS = {
    "VEHICLE_BATTERY_STATUS": "d157b289331668ddf5f7eecaf93efe73a95f12794d424f5bb3edbbcc1536defc",
    "VEHICLE_BOUNDARY_ALERTS": "1b39f2447a0b7f2b87172930d52884163821cba61390c1ed574f7091eb329590",
    "VEHICLE_CLIMATE_STATUS": "613bc1a2d4fe33cfbcfe05ceb0822fdec1e4b6b44d1c1835614ecff1dda05bbf",
    "VEHICLE_CURFEW_ALERTS": "8c32c5e7976dc8f1f05c02dca78c1b2772b621a67b795f9dd54c1c9c85e6cefe",
    "VEHICLE_DOORS_STATUS": "2615e0f31156f0c197c8cda7fbd5faf242b1be3ee2315323f554361de5ce710d",
    "VEHICLE_MODEL_YEAR": "68caf946fc54a0decc35dd011ab528649823b17d89f60f83d47db0270c89c625",
    "VEHICLE_NICKNAME": "548cbf9cb3accff338e62dc1b03f46e77daf056b13f5e7c71f3318f9bc188255",
    "VEHICLE_SPEED_ALERTS": "3250f9f2c20de1e6635592a1e7e084db04f588930739d58f57b1f6a2557fc553",
    "VEHICLE_STATUS": "fcce613d98daca4c170d6293b45183422a145f9d4c0f6a124b01bdc5405f2407",
    "VEHICLE_STATUS_AND_RECALLS": (
        "1b52ab3c1b996e32f3908ae6f270f87a064516f16b94de07a9f0cc5002687f1e"
    ),
    "VEHICLE_VALET_ALERTS": "9e8b9ea4c2c34471e1f94fa2a81963a1d226fa22cde37c104e31b35b09057a76",
}


@pytest.mark.parametrize(("constant", "expected_id"), EXPECTED_OPERATIONS.items())
def test_vehicle_detail_operations_match_service_documents(
    constant: str,
    expected_id: str,
) -> None:
    document = getattr(operations, constant)
    operation_id = getattr(operations, f"{constant}_OPERATION_ID")

    assert operation_id == expected_id
    assert hashlib.sha256(document.encode()).hexdigest() == expected_id


def test_vehicle_detail_variables_preserve_apollo_optionality() -> None:
    assert vehicle_battery_status_variables("VIN") == {"vin": "VIN"}
    assert vehicle_battery_status_variables("VIN", unit=None) == {
        "vin": "VIN",
        "unit": None,
    }
    assert vehicle_battery_status_variables("VIN", unit=DistanceUnit.MILE) == {
        "vin": "VIN",
        "unit": "MILE",
    }
    assert vehicle_boundary_alerts_variables("VIN", distance_unit=DistanceUnit.KILOMETER) == {
        "vin": "VIN",
        "distanceUnit": "KILOMETER",
    }
    assert vehicle_climate_status_variables("VIN", TemperatureUnit.CELSIUS) == {
        "vin": "VIN",
        "temperatureUnit": "CELSIUS",
    }
    assert vehicle_curfew_alerts_variables("VIN") == {"vin": "VIN"}
    assert vehicle_doors_status_variables("VIN") == {"vin": "VIN"}
    assert vehicle_model_year_variables("VIN") == {"vin": "VIN"}
    assert vehicle_nickname_variables("VIN") == {"vin": "VIN"}
    assert vehicle_speed_alerts_variables("VIN", speed_unit=SpeedUnit.MPH) == {
        "vin": "VIN",
        "speedUnit": "MPH",
    }
    assert vehicle_status_variables("VIN", unit=None) == {"vin": "VIN", "unit": None}
    assert vehicle_status_and_recalls_variables("VIN") == {"vin": "VIN"}
    assert vehicle_valet_alerts_variables("VIN") == {"vin": "VIN"}


def test_vehicle_detail_variables_reject_unknown_enum_inputs() -> None:
    with pytest.raises(ValueError, match="UNKNOWN_VALUE cannot be sent"):
        vehicle_battery_status_variables("VIN", unit=DistanceUnit.UNKNOWN_VALUE)
    with pytest.raises(ValueError, match="UNKNOWN_VALUE cannot be sent"):
        vehicle_speed_alerts_variables("VIN", speed_unit=SpeedUnit.UNKNOWN_VALUE)


def test_parse_standalone_battery_climate_and_doors() -> None:
    assert parse_vehicle_battery_status(
        {
            "vehicle": {
                "__typename": "ElectricAVK2Vehicle",
                "batteryStatus": {
                    "__typename": "BatteryStatus",
                    "level": 81,
                    "isPluggedIn": True,
                    "isCharging": False,
                    "remainingChargeTime": 25,
                    "remainingMileage": {
                        "__typename": "Distance",
                        "unit": "MILE",
                        "value": 220,
                    },
                },
            }
        },
        "VIN",
    ) == BatteryStatus(81, True, False, 25, DistanceReading(220, "MILE"))
    assert parse_vehicle_climate_status(
        {
            "vehicle": {
                "__typename": "ElectricAVK2Vehicle",
                "climateStatus": {
                    "__typename": "ClimateStatus",
                    "state": "OFF",
                    "temperature": {
                        "__typename": "Temperature",
                        "value": 21.5,
                        "unit": "CELSIUS",
                    },
                },
            }
        },
        "VIN",
    ) == ClimateStatus("OFF", TemperatureReading(21.5, "CELSIUS"))
    assert parse_vehicle_doors_status(
        {
            "vehicle": {
                "__typename": "AVK2Vehicle",
                "doorsStatus": {
                    "__typename": "DoorsStatus",
                    "lastUpdatedAt": None,
                },
            }
        },
        "VIN",
    ) == DoorsStatus(None, None, None, None, None, None, None, None, None, None)


def test_parse_vehicle_model_year_and_nickname_preserve_nullability() -> None:
    assert parse_vehicle_model_year(
        {
            "vehicle": {
                "__typename": "ElectricAVK2Vehicle",
                "model": "ARIYA",
                "year": "2026",
            }
        }
    ) == VehicleModelYear("ElectricAVK2Vehicle", "ARIYA", "2026")
    assert parse_vehicle_nickname(
        {
            "vehicle": {
                "__typename": "ElectricAVK2Vehicle",
                "nickname": None,
            }
        }
    ) == VehicleNickname("ElectricAVK2Vehicle", None)
    assert parse_vehicle_model_year({"vehicle": None}) is None
    assert parse_vehicle_nickname({"vehicle": None}) is None
    with pytest.raises(ResponseError, match=r"vehicle\.model is not a string"):
        parse_vehicle_model_year(
            {
                "vehicle": {
                    "__typename": "ElectricAVK2Vehicle",
                    "model": None,
                    "year": "2026",
                }
            }
        )


def test_parse_standalone_alerts_preserves_null_and_empty_values() -> None:
    assert (
        parse_vehicle_boundary_alerts(
            {"vehicle": {"__typename": "AVK2Vehicle", "boundaryAlerts": []}}
        )
        == ()
    )
    assert (
        parse_vehicle_curfew_alerts(
            {"vehicle": {"__typename": "AVK2Vehicle", "curfewAlerts": None}}
        )
        is None
    )
    assert (
        parse_vehicle_speed_alerts({"vehicle": {"__typename": "AVK2Vehicle", "speedAlerts": []}})
        == ()
    )
    assert (
        parse_vehicle_valet_alert({"vehicle": {"__typename": "AVK2Vehicle", "valetAlert": None}})
        is None
    )


def test_parse_vehicle_core_status_and_combined_recalls() -> None:
    vehicle = {
        "__typename": "AVK2Vehicle",
        "doorsStatus": None,
        "fuelAutonomy": None,
        "mileage": None,
        "tirePressure": None,
        "mils": [],
    }
    expected_status = VehicleStatus(
        vin="VIN",
        vehicle_type="AVK2Vehicle",
        battery=None,
        climate=None,
        doors=None,
        fuel_range=None,
        mileage=None,
        tire_pressure=None,
        maintenance_indicators=(),
    )

    assert parse_vehicle_core_status({"vehicle": vehicle}, "VIN") == expected_status
    assert parse_vehicle_status_and_recalls(
        {"vehicle": {**vehicle, "recalls": []}},
        "VIN",
    ) == VehicleStatusAndRecalls(expected_status, ())
    assert parse_vehicle_core_status({"vehicle": None}, "VIN") is None
    assert parse_vehicle_status_and_recalls({"vehicle": None}, "VIN") is None


class FakeResponse:
    def __init__(self) -> None:
        self.status = 200

    async def __aenter__(self) -> FakeResponse:
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def json(self, *, content_type: object = None) -> object:
        return {"data": {"vehicle": None}}


class FakeSession:
    def __init__(self, response_count: int) -> None:
        self.responses = [FakeResponse() for _ in range(response_count)]
        self.calls: list[dict[str, object]] = []

    def post(self, url: str, **kwargs: object) -> FakeResponse:
        self.calls.append({"url": url, **kwargs})
        if not self.responses:
            raise AssertionError("Unexpected HTTP request")
        return self.responses.pop(0)


async def test_vehicle_detail_client_wires_all_exact_operations() -> None:
    session = FakeSession(11)
    client = NissanClient(
        cast(ClientSession, session),
        tokens=Tokens("access", "refresh", "id"),
    )

    assert await client.async_get_vehicle_battery_status("VIN") is None
    assert await client.async_get_vehicle_boundary_alerts("VIN") is None
    assert await client.async_get_vehicle_climate_status("VIN", TemperatureUnit.FAHRENHEIT) is None
    assert await client.async_get_vehicle_curfew_alerts("VIN") is None
    assert await client.async_get_vehicle_doors_status("VIN") is None
    assert await client.async_get_vehicle_model_year("VIN") is None
    assert await client.async_get_vehicle_nickname("VIN") is None
    assert await client.async_get_vehicle_speed_alerts("VIN") is None
    assert await client.async_get_vehicle_core_status("VIN") is None
    assert await client.async_get_vehicle_status_and_recalls("VIN") is None
    assert await client.async_get_vehicle_valet_alert("VIN") is None

    payloads: list[Mapping[str, object]] = []
    for call in session.calls:
        payload = call["json"]
        assert isinstance(payload, Mapping)
        payloads.append(payload)
    assert [payload["operationName"] for payload in payloads] == [
        "VehicleBatteryStatus",
        "VehicleBoundaryAlerts",
        "VehicleClimateStatus",
        "VehicleCurfewAlerts",
        "VehicleDoorsStatus",
        "VehicleModelYear",
        "VehicleNickname",
        "VehicleSpeedAlerts",
        "VehicleStatus",
        "VehicleStatusAndRecalls",
        "VehicleValetAlerts",
    ]
    assert [payload["variables"] for payload in payloads] == [
        {"vin": "VIN"},
        {"vin": "VIN"},
        {"vin": "VIN", "temperatureUnit": "FAHRENHEIT"},
        {"vin": "VIN"},
        {"vin": "VIN"},
        {"vin": "VIN"},
        {"vin": "VIN"},
        {"vin": "VIN"},
        {"vin": "VIN"},
        {"vin": "VIN"},
        {"vin": "VIN"},
    ]
