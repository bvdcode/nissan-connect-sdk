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
    DistanceUnit,
    NavigationCoordinate,
    NavigationDataSource,
    NavigationDistance,
    NavigationNotificationInterval,
    NavigationRouteWaypoint,
    NavigationTemperature,
    NotificationIntervalUnit,
    PlannedRoute,
    PointOfInterestDestination,
    PointOfInterestDestinationFolder,
    RecalculatedWaypointType,
    RouteHistoryEntry,
    RouteStatus,
    TemperatureUnit,
    VehicleJourneys,
    VehiclePlannedRoutes,
    VehiclePointOfInterestDestinations,
    VehicleRoutesHistory,
)


@pytest.mark.asyncio
async def test_get_vehicle_planned_routes_parses_typed_fields_and_kmr_header() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "plannedRoutes": [
                            None,
                            {
                                "id": "route-1",
                                "name": "Morning",
                                "estimatedTimeOfDeparture": "2026-08-02T15:00:00Z",
                                "estimatedTimeOfArrival": "2026-08-02T16:15:00Z",
                                "distance": {"value": 42, "unit": "MILE"},
                                "temperature": {"value": 70.0, "unit": "FAHRENHEIT"},
                                "routes": [
                                    None,
                                    {
                                        "name": "Charger",
                                        "phoneNumber": None,
                                        "address": None,
                                        "location": {
                                            "latitude": 32.8,
                                            "longitude": -117.2,
                                        },
                                        "recalculatedWaypointType": "FUTURE_VALUE",
                                        "chargingOutput": 150,
                                    },
                                ],
                                "avoidHighway": False,
                                "avoidTolls": True,
                                "avoidFerries": None,
                                "shouldRecalculateRoute": True,
                                "shouldEnableNotification": True,
                                "notificationInterval": {"value": 15, "unit": "MIN"},
                                "arrivalFlag": False,
                                "departureFlag": True,
                            },
                        ]
                    }
                }
            },
        ),
    )
    client = make_client(session)

    routes = await client.async_get_vehicle_planned_routes(
        "JN1TESTVIN",
        distance_unit=DistanceUnit.MILE,
        temperature_unit=TemperatureUnit.FAHRENHEIT,
        data_source=NavigationDataSource.KMR,
    )

    assert routes == VehiclePlannedRoutes(
        (
            None,
            PlannedRoute(
                id="route-1",
                name="Morning",
                estimated_time_of_departure=datetime.fromisoformat("2026-08-02T15:00:00+00:00"),
                estimated_time_of_arrival=datetime.fromisoformat("2026-08-02T16:15:00+00:00"),
                distance=NavigationDistance(42, DistanceUnit.MILE),
                temperature=NavigationTemperature(70.0, TemperatureUnit.FAHRENHEIT),
                routes=(
                    None,
                    NavigationRouteWaypoint(
                        name="Charger",
                        phone_number=None,
                        address=None,
                        location=NavigationCoordinate(32.8, -117.2),
                        recalculated_waypoint_type=RecalculatedWaypointType.UNKNOWN_VALUE,
                        charging_output=150,
                    ),
                ),
                avoid_highway=False,
                avoid_tolls=True,
                avoid_ferries=None,
                should_recalculate_route=True,
                should_enable_notification=True,
                notification_interval=NavigationNotificationInterval(
                    15,
                    NotificationIntervalUnit.MINUTE,
                ),
                arrival_flag=False,
                departure_flag=True,
            ),
        )
    )
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["variables"] == {
        "vin": "JN1TESTVIN",
        "distanceUnit": "MILE",
        "temperatureUnit": "FAHRENHEIT",
    }
    headers = cast(Mapping[str, str], session.calls[0]["headers"])
    assert headers["x-tsp-datasource"] == "KMR"


@pytest.mark.asyncio
async def test_get_vehicle_routes_history_preserves_status_and_nulls() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "routeHistory": [
                            {
                                "id": None,
                                "name": "Completed trip",
                                "estimatedTimeOfDeparture": None,
                                "estimatedTimeOfArrival": None,
                                "status": "DEPARTURED",
                                "distance": None,
                                "temperature": None,
                                "routes": None,
                                "arrivalFlag": None,
                                "departureFlag": False,
                            }
                        ]
                    }
                }
            },
        ),
    )
    client = make_client(session)

    history = await client.async_get_vehicle_routes_history(
        "JN1TESTVIN",
        status=RouteStatus.COMPLETED,
    )

    assert history == VehicleRoutesHistory(
        (
            RouteHistoryEntry(
                id=None,
                name="Completed trip",
                estimated_time_of_departure=None,
                estimated_time_of_arrival=None,
                status=RouteStatus.DEPARTURED,
                distance=None,
                temperature=None,
                routes=None,
                arrival_flag=None,
                departure_flag=False,
            ),
        )
    )
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "RoutesHistory"
    assert payload["variables"] == {"vin": "JN1TESTVIN", "status": "COMPLETED"}


@pytest.mark.asyncio
async def test_get_vehicle_point_of_interest_destinations_defaults_to_both() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "pointOfInterestDestination": {
                            "folders": [
                                None,
                                {
                                    "folderName": "CUSTOM_FOLDER_LABEL",
                                    "destinations": [
                                        None,
                                        {
                                            "id": "destination-1",
                                            "phoneNumber": "555-0100",
                                            "name": "Work",
                                            "address": None,
                                            "coordinate": {
                                                "latitude": None,
                                                "longitude": -117.1,
                                            },
                                        },
                                    ],
                                },
                            ]
                        }
                    }
                }
            },
        ),
    )
    client = make_client(session)

    destinations = await client.async_get_vehicle_point_of_interest_destinations("JN1TESTVIN")

    assert destinations == VehiclePointOfInterestDestinations(
        (
            None,
            PointOfInterestDestinationFolder(
                folder_name="CUSTOM_FOLDER_LABEL",
                destinations=(
                    None,
                    PointOfInterestDestination(
                        id="destination-1",
                        phone_number="555-0100",
                        name="Work",
                        address=None,
                        coordinate=NavigationCoordinate(None, -117.1),
                    ),
                ),
            ),
        )
    )
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["variables"] == {"vin": "JN1TESTVIN", "folderName": "BOTH"}


@pytest.mark.asyncio
async def test_navigation_reads_distinguish_absent_branches_from_null_lists() -> None:
    session = FakeSession(
        FakeResponse(200, {"data": {"vehicle": {}}}),
        FakeResponse(200, {"data": {"vehicle": {"journeys": None}}}),
        FakeResponse(200, {"data": {"vehicle": {}}}),
        FakeResponse(200, {"data": {"vehicle": {"plannedRoutes": None}}}),
        FakeResponse(200, {"data": {"vehicle": {}}}),
        FakeResponse(200, {"data": {"vehicle": {"routeHistory": None}}}),
        FakeResponse(200, {"data": {"vehicle": {}}}),
        FakeResponse(
            200,
            {"data": {"vehicle": {"pointOfInterestDestination": None}}},
        ),
        FakeResponse(
            200,
            {"data": {"vehicle": {"pointOfInterestDestination": {"folders": None}}}},
        ),
    )
    client = make_client(session)

    assert await client.async_get_vehicle_journeys("JN1TESTVIN") is None
    assert await client.async_get_vehicle_journeys("JN1TESTVIN") == VehicleJourneys(None)
    assert await client.async_get_vehicle_planned_routes("JN1TESTVIN") is None
    assert await client.async_get_vehicle_planned_routes("JN1TESTVIN") == VehiclePlannedRoutes(None)
    assert await client.async_get_vehicle_routes_history("JN1TESTVIN") is None
    assert await client.async_get_vehicle_routes_history("JN1TESTVIN") == VehicleRoutesHistory(None)
    assert await client.async_get_vehicle_point_of_interest_destinations("JN1TESTVIN") is None
    assert await client.async_get_vehicle_point_of_interest_destinations("JN1TESTVIN") is None
    assert await client.async_get_vehicle_point_of_interest_destinations(
        "JN1TESTVIN"
    ) == VehiclePointOfInterestDestinations(None)
