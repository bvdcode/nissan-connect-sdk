from __future__ import annotations

import hashlib
import re
from collections.abc import Callable, Mapping
from datetime import UTC, datetime, timedelta
from typing import cast

import pytest
from aiohttp import ClientSession

from pynissan import UNSET, NissanClient, ResponseError, Tokens
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
    EmpEvseStatus,
    EmpLocationStatus,
    WeightUnit,
)
from pynissan.extended_vehicle_parsing import (
    parse_driving_history,
    parse_e_vehicle_eligibility,
    parse_ev_charge_stations,
    parse_last_known_camera_usage_counter,
    parse_location_details,
    parse_parking_chargeable,
    parse_shareable_capabilities,
    parse_tariff_pricing,
)
from pynissan.models import DistanceUnit, SpeedUnit
from pynissan.navigation_inputs import PlugConnectorType


class FakeResponse:
    def __init__(self, payload: Mapping[str, object]) -> None:
        self.status = 200
        self._payload = payload

    async def __aenter__(self) -> FakeResponse:
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def json(self, *, content_type: object = None) -> object:
        return self._payload


class FakeSession:
    def __init__(self, *responses: FakeResponse) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, object]] = []

    def post(self, url: str, **kwargs: object) -> FakeResponse:
        self.calls.append({"url": url, **kwargs})
        if not self.responses:
            raise AssertionError("Unexpected HTTP request")
        return self.responses.pop(0)


TOKENS = Tokens("access-token", "refresh-token", "id-token")
EXPECTED_QUERY_TOKEN_HASHES = {
    "DrivingHistory": "55c6560e71d7b5f267e7edfabced0c4dbe9e5240d034b3e8ab579d2ad5b0152e",
    "EVChargeStations": "18b57f6f03c5c1552323f1a95c25af0929be916e190ca7c2be04ab19fa78e383",
    "eVehicleEligibility": "7c2bcccfa5c0d963a580c8aa536a1354b34ac84e69502cc1d66f2e7ce3adca8c",
    "LastKnownCameraUsageCounter": (
        "975fb5c31998d845d5546d71233e53ca45d2c377d823d00fee0c373af111599e"
    ),
    "LocationDetails": "a17394651892824a08fc8ddec625d9aa1641f89f101fad2139235986ca174ffc",
    "ParkingChargeable": "6ec1a2169360a3edd23aab2321a1efa54b81e22f6a0e83a456cbc3413182ee30",
    "ShareableCapabilities": ("46ce25e824af31aea94723979e168bc0494a51a210287c3a314e0d9e0df00c25"),
    "TariffPricing": "8fe80027d8aad800cef5c59ed797854822a2f5c09aaaa684ac49151208823f4f",
}


def graphql_response(data: Mapping[str, object]) -> FakeResponse:
    return FakeResponse({"data": dict(data)})


def make_client(session: FakeSession) -> NissanClient:
    return NissanClient(
        cast(ClientSession, session),
        read_only=True,
        tokens=TOKENS,
    )


def assert_graphql_call(
    session: FakeSession,
    index: int,
    operation_name: str,
    variables: Mapping[str, object],
) -> None:
    payload = session.calls[index].get("json")
    assert isinstance(payload, Mapping)
    assert payload["operationName"] == operation_name
    assert payload["variables"] == variables
    document = payload["query"]
    assert isinstance(document, str)
    tokens = " ".join(re.findall(r"\.\.\.|[_A-Za-z][_0-9A-Za-z]*|[$!():{}\[\]]", document))
    assert (
        hashlib.sha256(tokens.encode()).hexdigest() == EXPECTED_QUERY_TOKEN_HASHES[operation_name]
    )


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


def test_driving_history_parses_non_null_tuples_dates_and_unknown_enums() -> None:
    history = parse_driving_history(
        {
            "vehicle": {
                "__typename": "ElectricAVK2Vehicle",
                "drivingHistory": {
                    "__typename": "DrivingHistory",
                    "tripSummaries": [
                        {
                            "__typename": "TripSummary",
                            "userId": "driver-1",
                            "day": 31,
                            "month": 7,
                            "year": 2026,
                            "numberOfTrips": 2,
                            "distanceTraveled": {
                                "__typename": "Distance",
                                "unit": "FUTURE_DISTANCE_UNIT",
                                "value": 42.5,
                            },
                            "duration": "PT1H30M",
                            "averageSpeed": {
                                "__typename": "Speed",
                                "type": "FUTURE_SPEED_UNIT",
                                "value": 28.3,
                            },
                            "energyConsumed": 9.75,
                            "co2Saved": {
                                "__typename": "Weight",
                                "unit": "FUTURE_WEIGHT_UNIT",
                                "value": 7.2,
                            },
                        }
                    ],
                    "trips": [
                        {
                            "__typename": "Trip",
                            "distance": {
                                "__typename": "Distance",
                                "unit": "KILOMETER",
                                "value": 21.25,
                            },
                            "startDate": "2026-07-31T12:00:00-07:00",
                            "endDate": "2026-07-31T12:45:00-07:00",
                            "duration": 45,
                            "startLocation": {
                                "__typename": "Location",
                                "latitude": 32.7,
                                "longitude": -117.1,
                            },
                            "endLocation": {
                                "__typename": "Location",
                                "latitude": None,
                                "longitude": None,
                            },
                            "averageSpeed": {
                                "__typename": "Speed",
                                "type": "MPH",
                                "value": 35,
                            },
                            "energyConsumed": 4.5,
                            "energySaved": None,
                            "co2Saved": None,
                            "userId": None,
                        }
                    ],
                },
            }
        }
    )

    assert history is not None
    assert isinstance(history.trip_summaries, tuple)
    assert isinstance(history.trips, tuple)
    summary = history.trip_summaries[0]
    assert summary.distance_traveled is not None
    assert summary.distance_traveled.unit is DistanceUnit.UNKNOWN_VALUE
    assert summary.average_speed is not None
    assert summary.average_speed.type is SpeedUnit.UNKNOWN_VALUE
    assert summary.co2_saved is not None
    assert summary.co2_saved.unit is WeightUnit.UNKNOWN_VALUE
    trip = history.trips[0]
    assert trip.distance is not None
    assert trip.distance.unit is DistanceUnit.KILOMETER
    assert trip.start_date is not None
    assert trip.start_date.utcoffset() == timedelta(hours=-7)
    assert trip.end_date is not None
    assert trip.end_date.utcoffset() == timedelta(hours=-7)
    assert trip.start_location is not None
    assert trip.start_location.latitude == 32.7
    assert trip.end_location is not None
    assert trip.end_location.latitude is None


def test_ev_charge_stations_preserve_nullable_lists_and_unknown_connector_enum() -> None:
    stations = parse_ev_charge_stations(
        {
            "vehicle": {
                "__typename": "ElectricVehicle",
                "evChargeStations": [
                    None,
                    {
                        "__typename": "EvChargeStation",
                        "id": "station-1",
                        "name": "Station",
                        "phoneNumber": None,
                        "address": {
                            "__typename": "Address",
                            "address1": "1 Main St",
                            "address2": None,
                            "city": "San Diego",
                            "country": "US",
                            "postalCode": "92101",
                            "state": "CA",
                        },
                        "location": {
                            "__typename": "Coordinate",
                            "latitude": 32.7157,
                            "longitude": -117.1611,
                        },
                        "connectors": [
                            None,
                            {
                                "__typename": "Connector",
                                "plugConnectorType": "FUTURE_CONNECTOR",
                                "ratedPowerKW": 150,
                                "voltageV": 400,
                                "currentA": 375,
                                "currentType": "DC",
                            },
                        ],
                    },
                ],
            }
        }
    )

    assert stations is not None
    assert isinstance(stations, tuple)
    assert stations[0] is None
    station = stations[1]
    assert station is not None
    assert station.address is not None
    assert station.address.postal_code == "92101"
    assert station.location is not None
    assert station.location.latitude == 32.7157
    assert station.connectors is not None
    assert isinstance(station.connectors, tuple)
    assert station.connectors[0] is None
    connector = station.connectors[1]
    assert connector is not None
    assert connector.plug_connector_type is PlugConnectorType.UNKNOWN_VALUE
    assert connector.rated_power_kw == 150.0


def test_status_wrappers_camera_counter_and_shareable_capabilities_parse_exactly() -> None:
    eligibility = parse_e_vehicle_eligibility(
        {
            "eVehicleEligibility": {
                "__typename": "EVehicleEligibilityResponse",
                "statusCode": "1000",
                "statusMessage": None,
                "timestamp": "raw-eligibility-timestamp",
                "data": {
                    "__typename": "EVehicleEligibilityData",
                    "vin": "VIN",
                    "v1GEligible": True,
                },
            }
        }
    )
    assert eligibility is not None
    assert eligibility.status_code == "1000"
    assert eligibility.status_message is None
    assert eligibility.timestamp == "raw-eligibility-timestamp"
    assert eligibility.data is not None
    assert eligibility.data.v1g_eligible is True

    camera = parse_last_known_camera_usage_counter(
        {
            "vehicle": {
                "__typename": "AVK2Vehicle",
                "lastKnownCameraUsageCounter": {
                    "__typename": "CameraUsageCounter",
                    "counter": "00042",
                    "lastUpdateTime": "2026-07-31T19:30:00Z",
                },
            }
        }
    )
    assert camera is not None
    assert camera.counter == "00042"
    assert camera.last_update_time == datetime(2026, 7, 31, 19, 30, tzinfo=UTC)

    parking = parse_parking_chargeable(
        {
            "parkingChargeable": {
                "__typename": "ParkingChargeableResponse",
                "statusCode": "4002",
                "statusMessage": "raw message",
                "timestamp": "raw-parking-timestamp",
                "data": {
                    "__typename": "ParkingChargeableData",
                    "evseId": "EVSE-1",
                    "isParkingChargeable": True,
                    "isCongestionChargeable": None,
                },
            }
        }
    )
    assert parking is not None
    assert parking.status_code == "4002"
    assert parking.status_message == "raw message"
    assert parking.timestamp == "raw-parking-timestamp"
    assert parking.data is not None
    assert parking.data.is_parking_chargeable is True
    assert parking.data.is_congestion_chargeable is None

    shareable = parse_shareable_capabilities(
        {
            "vehicle": {
                "__typename": "ElectricAVK2Vehicle",
                "shareableCapabilities": {
                    "__typename": "ShareableCapabilities",
                    "group": [
                        None,
                        {
                            "__typename": "CapabilityGroup",
                            "id": "B03",
                            "name": None,
                            "shared": True,
                            "capabilities": [
                                None,
                                {
                                    "__typename": "Capability",
                                    "id": "REMOTE_CLIMATE",
                                    "name": "Climate",
                                    "shareable": False,
                                },
                            ],
                        },
                    ],
                },
            }
        }
    )
    assert shareable is not None
    assert isinstance(shareable.groups, tuple)
    assert shareable.groups[0] is None
    group = shareable.groups[1]
    assert group is not None
    assert group.id == "B03"
    assert isinstance(group.capabilities, tuple)
    assert group.capabilities[0] is None
    capability = group.capabilities[1]
    assert capability is not None
    assert capability.id == "REMOTE_CLIMATE"
    assert capability.shareable is False


def test_location_details_preserves_emp_status_and_nested_nullable_lists() -> None:
    details = parse_location_details(
        {
            "locationDetails": {
                "__typename": "LocationDetailsResponse",
                "statusCode": "1000",
                "statusMessage": None,
                "timestamp": "raw-location-timestamp",
                "data": [
                    None,
                    {
                        "__typename": "LocationData",
                        "locationId": "location-1",
                        "locationType": "FUTURE_LOCATION_TYPE",
                        "locationName": "Charging Plaza",
                        "locationLogo": None,
                        "locationOperatorName": "Operator",
                        "locationSubOperatorName": None,
                        "locationAddress": "1 Main St",
                        "locationCity": "San Diego",
                        "locationState": "CA",
                        "locationCountry": "US",
                        "locationPostalCode": "92101",
                        "locationTwentyfourseven": True,
                        "locationOpeningTimings": [
                            None,
                            {
                                "__typename": "OpeningTiming",
                                "weekday": 5,
                                "periodBegin": "08:00",
                                "periodEnd": None,
                            },
                        ],
                        "locationInNetwork": False,
                        "phone": None,
                        "locationCoordinates": {
                            "__typename": "Coordinates",
                            "latitude": "32.7157",
                            "longitude": "-117.1611",
                        },
                        "evses": [
                            None,
                            {
                                "__typename": "Evse",
                                "evseId": "EVSE-1",
                                "evseLocationId": None,
                                "evseStatus": "FUTURE_EVSE_STATUS",
                                "evseCapability": ["PLUG_AND_CHARGE_CAPABLE"],
                                "evsePhysicalReference": "A-1",
                                "connector": [
                                    None,
                                    {
                                        "__typename": "Connector",
                                        "connectorId": "connector-1",
                                        "connectorType": "CCS",
                                        "connectorPowerRating": "150 kW",
                                        "connectorDescription": None,
                                    },
                                ],
                            },
                        ],
                    },
                ],
            }
        }
    )

    assert details is not None
    assert details.status_code == "1000"
    assert details.status_message is None
    assert details.timestamp == "raw-location-timestamp"
    assert details.data is not None
    assert isinstance(details.data, tuple)
    assert details.data[0] is None
    location = details.data[1]
    assert location is not None
    assert location.location_type is EmpLocationStatus.UNKNOWN_VALUE
    assert location.location_twenty_four_seven is True
    assert location.opening_timings is not None
    assert location.opening_timings[0] is None
    assert location.coordinates is not None
    assert location.coordinates.latitude == "32.7157"
    assert location.evses is not None
    assert location.evses[0] is None
    evse = location.evses[1]
    assert evse is not None
    assert evse.evse_status is EmpEvseStatus.UNKNOWN_VALUE
    assert evse.evse_capability == ("PLUG_AND_CHARGE_CAPABLE",)
    assert evse.connectors is not None
    assert evse.connectors[0] is None
    connector = evse.connectors[1]
    assert connector is not None
    assert connector.connector_power_rating == "150 kW"


def test_tariff_pricing_preserves_raw_status_and_every_nullable_tier_list() -> None:
    pricing = parse_tariff_pricing(
        {
            "tariffPricing": {
                "__typename": "TariffPricingResponse",
                "statusCode": "1000",
                "statusMessage": None,
                "timestamp": "raw-tariff-timestamp",
                "data": {
                    "__typename": "TariffPricingData",
                    "locationId": "location-1",
                    "maxChargeLimit": "80",
                    "tariffDetails": [
                        None,
                        {
                            "__typename": "TariffDetail",
                            "connectorType": "CCS",
                            "connectorPower": "150 kW",
                            "sessionFee": "1.00",
                            "tariffAltText": {
                                "__typename": "TariffAltText",
                                "en": "English",
                                "fr": None,
                            },
                            "idleFees": {
                                "__typename": "IdleFees",
                                "gracePeriod": "10",
                                "idleFeesTier": [
                                    None,
                                    {
                                        "__typename": "IdleFeeTier",
                                        "congestionLevel": "HIGH",
                                        "timeStart": "08:00",
                                        "timeEnd": "18:00",
                                        "durationStart": "0",
                                        "durationEnd": "60",
                                        "durationUnit": "MINUTE",
                                        "price": "0.50",
                                        "unit": "USD_PER_MINUTE",
                                    },
                                ],
                            },
                            "congestionFees": {
                                "__typename": "CongestionFees",
                                "gracePeriod": None,
                                "congestionTier": [
                                    None,
                                    {
                                        "__typename": "CongestionTier",
                                        "congestionLevel": "MEDIUM",
                                        "vehicleSOCLimit": "90",
                                        "price": "2.00",
                                        "unit": "USD",
                                    },
                                ],
                            },
                            "energyFees": {
                                "__typename": "EnergyFees",
                                "energyFeeTier": [
                                    None,
                                    {
                                        "__typename": "EnergyFeeTier",
                                        "applicableDay": [1, 2, 3],
                                        "timeStart": "00:00",
                                        "timeEnd": "23:59",
                                        "durationStart": None,
                                        "durationEnd": None,
                                        "durationUnit": None,
                                        "minRange": "0",
                                        "maxRange": "100",
                                        "rangeUnit": "KWH",
                                        "price": "0.40",
                                        "unit": "USD_PER_KWH",
                                    },
                                ],
                            },
                        },
                    ],
                },
            }
        }
    )

    assert pricing is not None
    assert pricing.status_code == "1000"
    assert pricing.status_message is None
    assert pricing.timestamp == "raw-tariff-timestamp"
    assert pricing.data is not None
    assert pricing.data.tariff_details is not None
    assert pricing.data.tariff_details[0] is None
    detail = pricing.data.tariff_details[1]
    assert detail is not None
    assert detail.alternative_text is not None
    assert detail.alternative_text.fr is None
    assert detail.idle_fees is not None
    assert detail.idle_fees.tiers is not None
    assert detail.idle_fees.tiers[0] is None
    assert detail.congestion_fees is not None
    assert detail.congestion_fees.tiers is not None
    assert detail.congestion_fees.tiers[0] is None
    assert detail.energy_fees is not None
    assert detail.energy_fees.tiers is not None
    assert detail.energy_fees.tiers[0] is None
    energy_tier = detail.energy_fees.tiers[1]
    assert energy_tier is not None
    assert energy_tier.applicable_day == (1, 2, 3)


def test_nullable_roots_fragments_lists_and_items_are_preserved() -> None:
    assert parse_driving_history({"vehicle": None}) is None
    assert parse_driving_history({"vehicle": {"__typename": "Vehicle"}}) is None
    assert (
        parse_ev_charge_stations(
            {
                "vehicle": {
                    "__typename": "ElectricVehicle",
                    "evChargeStations": None,
                }
            }
        )
        is None
    )
    assert (
        parse_ev_charge_stations(
            {
                "vehicle": {
                    "__typename": "ElectricVehicle",
                    "evChargeStations": [],
                }
            }
        )
        == ()
    )
    assert parse_e_vehicle_eligibility({"eVehicleEligibility": None}) is None
    assert parse_last_known_camera_usage_counter({"vehicle": None}) is None
    assert parse_location_details({"locationDetails": None}) is None
    assert parse_parking_chargeable({"parkingChargeable": None}) is None
    assert parse_shareable_capabilities({"vehicle": None}) is None
    assert parse_tariff_pricing({"tariffPricing": None}) is None

    location_details = parse_location_details(
        {
            "locationDetails": {
                "__typename": "LocationDetailsResponse",
                "statusCode": None,
                "statusMessage": None,
                "timestamp": None,
                "data": None,
            }
        }
    )
    assert location_details is not None
    assert location_details.data is None


def test_non_null_driving_history_and_shareable_lists_are_enforced() -> None:
    with pytest.raises(ResponseError, match=r"tripSummaries is not a list"):
        parse_driving_history(
            {
                "vehicle": {
                    "__typename": "ElectricVehicle",
                    "drivingHistory": {
                        "__typename": "DrivingHistory",
                        "tripSummaries": None,
                        "trips": [],
                    },
                }
            }
        )

    with pytest.raises(ResponseError, match=r"tripSummaries\[0\] is not an object"):
        parse_driving_history(
            {
                "vehicle": {
                    "__typename": "ElectricVehicle",
                    "drivingHistory": {
                        "__typename": "DrivingHistory",
                        "tripSummaries": [None],
                        "trips": [],
                    },
                }
            }
        )

    with pytest.raises(ResponseError, match=r"shareableCapabilities.group is not a list"):
        parse_shareable_capabilities(
            {
                "vehicle": {
                    "__typename": "AVK2Vehicle",
                    "shareableCapabilities": {
                        "__typename": "ShareableCapabilities",
                        "group": None,
                    },
                }
            }
        )

    with pytest.raises(ResponseError, match=r"capabilities is not a list"):
        parse_shareable_capabilities(
            {
                "vehicle": {
                    "__typename": "AVK2Vehicle",
                    "shareableCapabilities": {
                        "__typename": "ShareableCapabilities",
                        "group": [
                            {
                                "__typename": "CapabilityGroup",
                                "id": "group-1",
                                "name": None,
                                "shared": None,
                                "capabilities": None,
                            }
                        ],
                    },
                }
            }
        )


def test_nullable_nested_list_items_are_preserved() -> None:
    location_details = parse_location_details(
        {
            "locationDetails": {
                "__typename": "LocationDetailsResponse",
                "statusCode": None,
                "statusMessage": None,
                "timestamp": None,
                "data": [
                    {
                        "__typename": "LocationData",
                        "evses": [
                            {
                                "__typename": "Evse",
                                "evseCapability": [None, "REMOTE_START"],
                            }
                        ],
                    }
                ],
            }
        }
    )
    assert location_details is not None
    assert location_details.data is not None
    location = location_details.data[0]
    assert location is not None
    assert location.evses is not None
    evse = location.evses[0]
    assert evse is not None
    assert evse.evse_capability == (None, "REMOTE_START")

    tariff_pricing = parse_tariff_pricing(
        {
            "tariffPricing": {
                "__typename": "TariffPricingResponse",
                "statusCode": None,
                "statusMessage": None,
                "timestamp": None,
                "data": {
                    "__typename": "TariffPricingData",
                    "tariffDetails": [
                        {
                            "__typename": "TariffDetail",
                            "energyFees": {
                                "__typename": "EnergyFees",
                                "energyFeeTier": [
                                    {
                                        "__typename": "EnergyFeeTier",
                                        "applicableDay": [1, None],
                                    }
                                ],
                            },
                        }
                    ],
                },
            }
        }
    )
    assert tariff_pricing is not None
    assert tariff_pricing.data is not None
    assert tariff_pricing.data.tariff_details is not None
    detail = tariff_pricing.data.tariff_details[0]
    assert detail is not None
    assert detail.energy_fees is not None
    assert detail.energy_fees.tiers is not None
    tier = detail.energy_fees.tiers[0]
    assert tier is not None
    assert tier.applicable_day == (1, None)


def test_extended_parsers_reject_naive_datetime_and_wrong_nullable_scalar_type() -> None:
    with pytest.raises(ResponseError, match="date-time with an offset"):
        parse_last_known_camera_usage_counter(
            {
                "vehicle": {
                    "__typename": "AVK2Vehicle",
                    "lastKnownCameraUsageCounter": {
                        "__typename": "CameraUsageCounter",
                        "counter": None,
                        "lastUpdateTime": "2026-07-31T19:30:00",
                    },
                }
            }
        )

    with pytest.raises(ResponseError, match=r"statusCode is not a string"):
        parse_e_vehicle_eligibility(
            {
                "eVehicleEligibility": {
                    "__typename": "EVehicleEligibilityResponse",
                    "statusCode": 1000,
                    "statusMessage": None,
                    "timestamp": None,
                    "data": None,
                }
            }
        )
