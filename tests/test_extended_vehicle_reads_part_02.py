from __future__ import annotations

from datetime import UTC, datetime, timedelta

from pynissan.extended_vehicle_models import (
    WeightUnit,
)
from pynissan.extended_vehicle_parsing import (
    parse_driving_history,
    parse_e_vehicle_eligibility,
    parse_ev_charge_stations,
    parse_last_known_camera_usage_counter,
    parse_parking_chargeable,
    parse_shareable_capabilities,
)
from pynissan.models import DistanceUnit, SpeedUnit
from pynissan.navigation_inputs import PlugConnectorType


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
