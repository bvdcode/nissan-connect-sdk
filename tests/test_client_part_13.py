from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import cast

import pytest
from test_client import (
    FakeResponse,
    FakeSession,
    make_client,
)

from pynissan import (
    CoordinateInput,
    DistanceUnit,
    EVWaypoint,
    EVWaypointLimitReachedError,
    EVWaypointRoute,
    EVWaypointRouteType,
    EVWaypointStatus,
    EVWaypointUnableToCompleteRouteError,
    NavigationAddress,
    NavigationCoordinate,
    NavigationDataSource,
    NavigationDistance,
    PlugConnectorType,
    ResponseError,
    RouteWaypointInput,
    SavedTJunctionLocation,
    TJunctionLocations,
    UnableToCompleteSubStepErrorDetails,
    UnsavedTJunctionLocation,
)


@pytest.mark.asyncio
async def test_get_t_junction_locations_parses_required_location_fields() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "unsavedTJunctionLocations": [
                            {
                                "id": "unsaved-1",
                                "latitude": 32.71,
                                "longitude": -117.16,
                                "direction": 180.0,
                                "launchDate": "2026-08-01T12:00:00Z",
                                "address": None,
                            }
                        ],
                        "savedTJunctionLocations": [
                            {
                                "id": "saved-1",
                                "latitude": 32.72,
                                "longitude": -117.17,
                                "direction": 90.0,
                                "locationName": "Downtown",
                                "address": {
                                    "address1": None,
                                    "address2": None,
                                    "city": "San Diego",
                                    "state": "CA",
                                    "country": "US",
                                    "postalCode": None,
                                },
                            }
                        ],
                    }
                }
            },
        ),
    )
    client = make_client(session)

    locations = await client.async_get_t_junction_locations("JN1TESTVIN")

    assert locations == TJunctionLocations(
        unsaved_t_junction_locations=(
            UnsavedTJunctionLocation(
                id="unsaved-1",
                latitude=32.71,
                longitude=-117.16,
                direction=180.0,
                launch_date=datetime.fromisoformat("2026-08-01T12:00:00+00:00"),
                address=None,
            ),
        ),
        saved_t_junction_locations=(
            SavedTJunctionLocation(
                id="saved-1",
                latitude=32.72,
                longitude=-117.17,
                direction=90.0,
                location_name="Downtown",
                address=NavigationAddress(
                    address1=None,
                    address2=None,
                    city="San Diego",
                    state="CA",
                    postal_code=None,
                    country="US",
                ),
            ),
        ),
    )


@pytest.mark.asyncio
async def test_get_vehicle_ev_waypoints_serializes_kmr_request_and_success() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "evWaypoints": {
                            "__typename": "EVWaypoint",
                            "departureTime": "2026-08-03T15:00:00Z",
                            "arrivalTime": None,
                            "totalChargingTimeInSeconds": 1500,
                            "totalTravelTimeInSeconds": 7200,
                            "totalDistance": {"unit": "MILE", "value": 84},
                            "routes": [
                                None,
                                {
                                    "name": "Fast charger",
                                    "arrivalTime": "2026-08-03T16:00:00Z",
                                    "chargingTimeInSeconds": 1500,
                                    "level": 25,
                                    "type": "CHARGING_STATION",
                                    "address": None,
                                    "location": {
                                        "latitude": 33.0,
                                        "longitude": -117.5,
                                    },
                                    "status": "AVAILABLE",
                                    "chargingOutput": 150,
                                },
                            ],
                        }
                    }
                }
            },
        ),
    )
    client = make_client(session)

    result = await client.async_get_vehicle_ev_waypoints(
        "JN1TESTVIN",
        (
            RouteWaypointInput(
                "Destination",
                CoordinateInput(33.1, -117.6),
                phone_number=None,
            ),
            None,
        ),
        (PlugConnectorType.CCS, None),
        depart_at=datetime.fromisoformat("2026-08-03T08:00:00-07:00"),
        arrived_by=None,
        state_of_charge_at_destination=20,
        distance_unit=DistanceUnit.MILE,
        estimated_battery_level_at_departure=85,
        minimum_power=50.0,
        use_hvac=False,
        data_source=NavigationDataSource.KMR,
    )

    assert result == EVWaypoint(
        departure_time=datetime.fromisoformat("2026-08-03T15:00:00+00:00"),
        arrival_time=None,
        total_charging_time_in_seconds=1500,
        total_travel_time_in_seconds=7200,
        total_distance=NavigationDistance(84, DistanceUnit.MILE),
        routes=(
            None,
            EVWaypointRoute(
                name="Fast charger",
                arrival_time=datetime.fromisoformat("2026-08-03T16:00:00+00:00"),
                charging_time_in_seconds=1500,
                level=25,
                type=EVWaypointRouteType.CHARGING_STATION,
                address=None,
                location=NavigationCoordinate(33.0, -117.5),
                status=EVWaypointStatus.AVAILABLE,
                charging_output=150,
            ),
        ),
    )
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "VehicleEVWaypoints"
    assert payload["variables"] == {
        "vin": "JN1TESTVIN",
        "departAt": "2026-08-03T08:00:00-07:00",
        "arrivedBy": None,
        "socAtDestination": 20,
        "routes": [
            {
                "name": "Destination",
                "coordinate": {"latitude": 33.1, "longitude": -117.6},
                "address": {},
                "phoneNumber": None,
            },
            None,
        ],
        "distanceUnit": "MILE",
        "plugConnectorTypes": ["CCS", None],
        "estimatedBatteryLevelAtDeparture": "85",
        "minPower": 50.0,
        "socAtStop": 20,
        "useHvac": False,
    }
    headers = cast(Mapping[str, str], session.calls[0]["headers"])
    assert headers["x-tsp-datasource"] == "KMR"


@pytest.mark.asyncio
async def test_get_vehicle_ev_waypoints_returns_typed_errors() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "evWaypoints": {
                            "__typename": "LimitReachedError",
                            "message": "Route limit reached",
                        }
                    }
                }
            },
        ),
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "evWaypoints": {
                            "__typename": "UnableToCompleteRouteError",
                            "reason": "NO_ROUTE",
                            "message": "Unable to complete",
                            "details": {
                                "__typename": "UnableToCompleteSubStepErrorDetails",
                                "start": "A",
                                "end": "B",
                                "distance": None,
                                "speed": None,
                                "slope": None,
                                "startingBattery": "80",
                                "batteryCapacity": None,
                                "batteryConsumption": None,
                                "socAfterChargingNearStart": None,
                                "minimumBattery": "10",
                                "chargingStationMaxPower": None,
                            },
                        }
                    }
                }
            },
        ),
    )
    client = make_client(session)

    limit = await client.async_get_vehicle_ev_waypoints("JN1TESTVIN", (), ())
    unable = await client.async_get_vehicle_ev_waypoints("JN1TESTVIN", (), ())

    assert limit == EVWaypointLimitReachedError("Route limit reached")
    assert unable == EVWaypointUnableToCompleteRouteError(
        reason="NO_ROUTE",
        message="Unable to complete",
        details=UnableToCompleteSubStepErrorDetails(
            start="A",
            end="B",
            distance=None,
            speed=None,
            slope=None,
            starting_battery="80",
            battery_capacity=None,
            battery_consumption=None,
            soc_after_charging_near_start=None,
            minimum_battery="10",
            charging_station_max_power=None,
        ),
    )


@pytest.mark.asyncio
async def test_get_vehicle_ev_waypoints_rejects_unsupported_result_type() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {"data": {"vehicle": {"evWaypoints": {"__typename": "FutureResult"}}}},
        ),
    )
    client = make_client(session)

    with pytest.raises(
        ResponseError,
        match=r"Unsupported vehicle\.evWaypoints type: FutureResult",
    ):
        await client.async_get_vehicle_ev_waypoints("JN1TESTVIN", (), ())


@pytest.mark.asyncio
async def test_get_vehicle_ev_waypoints_rejects_unsupported_error_details_type() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "evWaypoints": {
                            "__typename": "UnableToCompleteRouteError",
                            "reason": "NO_ROUTE",
                            "message": "Unable to complete",
                            "details": {"__typename": "FutureDetails"},
                        }
                    }
                }
            },
        ),
    )
    client = make_client(session)

    with pytest.raises(
        ResponseError,
        match=r"Unsupported vehicle\.evWaypoints\.details type: FutureDetails",
    ):
        await client.async_get_vehicle_ev_waypoints("JN1TESTVIN", (), ())
