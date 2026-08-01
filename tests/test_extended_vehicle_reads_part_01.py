from __future__ import annotations

from collections.abc import Callable, Mapping

import pytest
from test_extended_vehicle_reads import (
    FakeSession,
    assert_graphql_call,
    graphql_response,
    make_client,
)

from pynissan import UNSET
from pynissan.common_inputs import CoordinateInput
from pynissan.extended_vehicle_inputs import (
    EmpConnectorLevelInput,
    EmpEvseStatusInput,
    driving_history_variables,
    ev_charge_stations_variables,
    location_details_variables,
)
from pynissan.extended_vehicle_models import (
    DrivingHistoryAggregator,
    WeightUnit,
)
from pynissan.models import DistanceUnit, SpeedUnit
from pynissan.navigation_inputs import PlugConnectorType


async def test_extended_reads_use_exact_documents_and_apollo_variables() -> None:
    vehicle_null = {"vehicle": None}
    responses = [
        graphql_response(vehicle_null),
        graphql_response(vehicle_null),
        graphql_response(vehicle_null),
        graphql_response(vehicle_null),
        graphql_response(vehicle_null),
        graphql_response(vehicle_null),
        graphql_response({"eVehicleEligibility": None}),
        graphql_response(vehicle_null),
        graphql_response({"locationDetails": None}),
        graphql_response({"locationDetails": None}),
        graphql_response({"locationDetails": None}),
        graphql_response({"parkingChargeable": None}),
        graphql_response(vehicle_null),
        graphql_response(vehicle_null),
        graphql_response(vehicle_null),
        graphql_response({"tariffPricing": None}),
    ]
    session = FakeSession(*responses)
    client = make_client(session)
    coordinate = CoordinateInput(32.7157, -117.1611)

    assert (
        await client.async_get_driving_history(
            "VIN",
            DrivingHistoryAggregator.DAILY,
            distance_unit=UNSET,
            weight_unit=UNSET,
            speed_unit=UNSET,
        )
        is None
    )
    assert (
        await client.async_get_driving_history(
            "VIN",
            DrivingHistoryAggregator.MONTHLY,
            distance_unit=None,
            weight_unit=None,
            speed_unit=None,
        )
        is None
    )
    assert (
        await client.async_get_driving_history(
            "VIN",
            DrivingHistoryAggregator.YEARLY,
            distance_unit=DistanceUnit.KILOMETER,
            weight_unit=WeightUnit.KILOGRAM,
            speed_unit=SpeedUnit.KPH,
        )
        is None
    )

    assert (
        await client.async_get_ev_charge_stations(
            "VIN",
            coordinate,
            plug_connector_types=UNSET,
            enable_within_range_restriction=UNSET,
        )
        is None
    )
    assert (
        await client.async_get_ev_charge_stations(
            "VIN",
            coordinate,
            plug_connector_types=None,
            enable_within_range_restriction=None,
        )
        is None
    )
    assert (
        await client.async_get_ev_charge_stations(
            "VIN",
            coordinate,
            plug_connector_types=(PlugConnectorType.CCS, None, PlugConnectorType.NACS),
            enable_within_range_restriction=True,
        )
        is None
    )

    assert await client.async_get_e_vehicle_eligibility("VIN") is None
    assert await client.async_get_last_known_camera_usage_counter("VIN") is None

    assert (
        await client.async_get_location_details(
            "VIN",
            "32.7157",
            "-117.1611",
            True,
            25,
            operator_names=UNSET,
            evse=UNSET,
            plug_types=UNSET,
            charge_level=UNSET,
            pnc_stations_only=UNSET,
        )
        is None
    )
    assert (
        await client.async_get_location_details(
            "VIN",
            "32.7157",
            "-117.1611",
            True,
            25,
            operator_names=None,
            evse=None,
            plug_types=None,
            charge_level=None,
            pnc_stations_only=None,
        )
        is None
    )
    assert (
        await client.async_get_location_details(
            "VIN",
            "32.7157",
            "-117.1611",
            False,
            50,
            operator_names=("Operator", None),
            evse=EmpEvseStatusInput.AVAILABLE,
            plug_types=("CCS", None),
            charge_level=EmpConnectorLevelInput.L3,
            pnc_stations_only=False,
        )
        is None
    )

    assert await client.async_get_parking_chargeable("EVSE-1") is None
    assert await client.async_get_shareable_capabilities("VIN", driver_id=UNSET) is None
    assert await client.async_get_shareable_capabilities("VIN", driver_id=None) is None
    assert await client.async_get_shareable_capabilities("VIN", driver_id="driver-1") is None
    assert await client.async_get_tariff_pricing("VIN", "location-1") is None

    required_location_variables = {
        "vin": "VIN",
        "latitude": "32.7157",
        "longitude": "-117.1611",
        "inNetworkOnly": True,
        "range": 25,
    }
    expected_calls: list[tuple[str, Mapping[str, object]]] = [
        ("DrivingHistory", {"vin": "VIN", "aggregator": "DAILY"}),
        (
            "DrivingHistory",
            {
                "vin": "VIN",
                "aggregator": "MONTHLY",
                "distanceUnit": None,
                "weightUnit": None,
                "speedUnit": None,
            },
        ),
        (
            "DrivingHistory",
            {
                "vin": "VIN",
                "aggregator": "YEARLY",
                "distanceUnit": "KILOMETER",
                "weightUnit": "KILOGRAM",
                "speedUnit": "KPH",
            },
        ),
        (
            "EVChargeStations",
            {
                "vin": "VIN",
                "coordinate": {"latitude": 32.7157, "longitude": -117.1611},
            },
        ),
        (
            "EVChargeStations",
            {
                "vin": "VIN",
                "coordinate": {"latitude": 32.7157, "longitude": -117.1611},
                "plugConnectorTypes": None,
                "enableWithinRangeRestriction": None,
            },
        ),
        (
            "EVChargeStations",
            {
                "vin": "VIN",
                "coordinate": {"latitude": 32.7157, "longitude": -117.1611},
                "plugConnectorTypes": ["CCS", None, "NACS"],
                "enableWithinRangeRestriction": True,
            },
        ),
        ("eVehicleEligibility", {"vin": "VIN"}),
        ("LastKnownCameraUsageCounter", {"vin": "VIN"}),
        ("LocationDetails", required_location_variables),
        (
            "LocationDetails",
            {
                **required_location_variables,
                "operatorName": None,
                "evse": None,
                "plugType": None,
                "chargeLevel": None,
                "pncStationsOnly": None,
            },
        ),
        (
            "LocationDetails",
            {
                "vin": "VIN",
                "latitude": "32.7157",
                "longitude": "-117.1611",
                "inNetworkOnly": False,
                "range": 50,
                "operatorName": ["Operator", None],
                "evse": "AVAILABLE",
                "plugType": ["CCS", None],
                "chargeLevel": "L3",
                "pncStationsOnly": False,
            },
        ),
        ("ParkingChargeable", {"evseId": "EVSE-1"}),
        ("ShareableCapabilities", {"vin": "VIN"}),
        ("ShareableCapabilities", {"vin": "VIN", "driverId": None}),
        ("ShareableCapabilities", {"vin": "VIN", "driverId": "driver-1"}),
        ("TariffPricing", {"vin": "VIN", "locationId": "location-1"}),
    ]
    assert len(session.calls) == len(expected_calls)
    for index, (operation_name, variables) in enumerate(expected_calls):
        assert_graphql_call(session, index, operation_name, variables)


@pytest.mark.parametrize(
    "serializer",
    [
        lambda: driving_history_variables("VIN", DrivingHistoryAggregator.UNKNOWN_VALUE),
        lambda: driving_history_variables(
            "VIN",
            DrivingHistoryAggregator.DAILY,
            distance_unit=DistanceUnit.UNKNOWN_VALUE,
        ),
        lambda: driving_history_variables(
            "VIN",
            DrivingHistoryAggregator.DAILY,
            weight_unit=WeightUnit.UNKNOWN_VALUE,
        ),
        lambda: driving_history_variables(
            "VIN",
            DrivingHistoryAggregator.DAILY,
            speed_unit=SpeedUnit.UNKNOWN_VALUE,
        ),
        lambda: ev_charge_stations_variables(
            "VIN",
            CoordinateInput(1.0, 2.0),
            plug_connector_types=(PlugConnectorType.UNKNOWN_VALUE,),
        ),
        lambda: location_details_variables(
            "VIN",
            "1",
            "2",
            False,
            5,
            evse=EmpEvseStatusInput.UNKNOWN_VALUE,
        ),
        lambda: location_details_variables(
            "VIN",
            "1",
            "2",
            False,
            5,
            charge_level=EmpConnectorLevelInput.UNKNOWN_VALUE,
        ),
    ],
)
def test_unknown_enum_sentinels_cannot_be_serialized(
    serializer: Callable[[], object],
) -> None:
    with pytest.raises(ValueError, match="UNKNOWN_VALUE"):
        serializer()
