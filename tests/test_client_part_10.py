from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import cast

import pytest
from test_client import (
    FakeResponse,
    FakeSession,
    jwt_with_expiration,
    make_client,
)

from pynissan import (
    AddressInput,
    ChargingConnectorType,
    CoordinateInput,
    DestinationInput,
    DistanceUnit,
    NavigationDataSource,
    NotificationIntervalUnit,
    PlannedRouteInput,
    PlannedRouteUpdate,
    PointOfInterestFolder,
    RecalculatedWaypointType,
    ResponseError,
    RouteCalculationCondition,
    RouteChargingTimeInput,
    RouteDistanceInput,
    RouteNotificationIntervalInput,
    RouteTemperatureInput,
    RouteWaypointInput,
    ServiceRequest,
    ServiceRequestKind,
    Tokens,
)


@pytest.mark.asyncio
async def test_graphql_401_refreshes_once_and_retries() -> None:
    session = FakeSession(
        FakeResponse(401, {"message": "expired"}),
        FakeResponse(
            200,
            {
                "access_token": "replacement-access",
                "refresh_token": "replacement-refresh",
                "id_token": "replacement-id",
            },
        ),
        FakeResponse(200, {"data": {"vehicles": []}}),
    )
    client = make_client(session)

    vehicles = await client.async_get_vehicles()

    assert vehicles == ()
    assert len(session.calls) == 3
    retry_headers = cast(Mapping[str, str], session.calls[2]["headers"])
    assert retry_headers["Authorization"] == "Bearer replacement-access"


@pytest.mark.asyncio
async def test_expired_jwt_refreshes_before_graphql_request() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "access_token": "replacement-access",
                "refresh_token": "replacement-refresh",
                "id_token": "replacement-id",
            },
        ),
        FakeResponse(200, {"data": {"vehicles": []}}),
    )
    client = make_client(
        session,
        tokens=Tokens(jwt_with_expiration(0), "refresh-token", "id-token"),
    )

    vehicles = await client.async_get_vehicles()

    assert vehicles == ()
    assert len(session.calls) == 2
    assert session.calls[0]["url"] == "https://services.nissanusa.com/token"
    assert session.calls[0]["data"] == {
        "refresh_token": "refresh-token",
        "grant_type": "refresh_token",
    }
    graphql_headers = cast(Mapping[str, str], session.calls[1]["headers"])
    assert graphql_headers["Authorization"] == "Bearer replacement-access"


@pytest.mark.asyncio
async def test_expired_id_token_refreshes_before_graphql_request() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "access_token": "replacement-access",
                "refresh_token": "replacement-refresh",
                "id_token": "replacement-id",
            },
        ),
        FakeResponse(200, {"data": {"vehicles": []}}),
    )
    client = make_client(
        session,
        tokens=Tokens(
            "opaque-access-token",
            "refresh-token",
            jwt_with_expiration(0),
        ),
    )

    vehicles = await client.async_get_vehicles()

    assert vehicles == ()
    assert len(session.calls) == 2
    assert session.calls[0]["url"] == "https://services.nissanusa.com/token"
    graphql_headers = cast(Mapping[str, str], session.calls[1]["headers"])
    assert graphql_headers["Authorization"] == "Bearer replacement-access"
    assert graphql_headers["id-token"] == "replacement-id"


@pytest.mark.asyncio
async def test_send_journey_serializes_optional_inputs_and_kmr_header() -> None:
    session = FakeSession(
        FakeResponse(200, {"data": {"sendJourney": {"success": True}}}),
    )
    client = make_client(session, read_only=False)
    arrival = datetime.fromisoformat("2026-08-01T09:30:00-07:00")

    success = await client.async_send_journey(
        "JN1TESTVIN",
        (
            DestinationInput(
                "Home",
                CoordinateInput(32.7157, -117.1611),
                AddressInput(address1="1 Main St", city="San Diego", country="US"),
                phone_number=None,
                recalculated_waypoint_type=RecalculatedWaypointType.WAYPOINT,
            ),
        ),
        avoid_tolls=None,
        estimated_time_of_arrival=arrival,
        arrival_flag=False,
        data_source=NavigationDataSource.KMR,
    )

    assert success is True
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "SendJourney"
    assert payload["variables"] == {
        "vin": "JN1TESTVIN",
        "waypoints": [
            {
                "name": "Home",
                "phoneNumber": None,
                "coordinate": {"latitude": 32.7157, "longitude": -117.1611},
                "address": {
                    "address1": "1 Main St",
                    "city": "San Diego",
                    "country": "US",
                },
                "recalculatedWaypointType": "WAYPOINT",
            }
        ],
        "avoidTolls": None,
        "estimatedTimeOfArrival": "2026-08-01T09:30:00-07:00",
        "arrivalFlag": False,
    }
    headers = cast(Mapping[str, str], session.calls[0]["headers"])
    assert headers["x-tsp-datasource"] == "KMR"


@pytest.mark.asyncio
async def test_save_and_update_route_preserve_omitted_and_null_fields() -> None:
    session = FakeSession(
        FakeResponse(200, {"data": {"saveRoute": {"serviceRequestId": "save-1"}}}),
        FakeResponse(200, {"data": {"updateRoute": {"serviceRequestId": "update-1"}}}),
    )
    client = make_client(session, read_only=False)
    departure = datetime.fromisoformat("2026-08-02T08:00:00-07:00")
    arrival = datetime.fromisoformat("2026-08-02T09:15:00-07:00")
    route = PlannedRouteInput(
        name="Morning route",
        routes=(
            RouteWaypointInput(
                name="Quick charger",
                coordinate=CoordinateInput(32.8, -117.2),
                phone_number=None,
                charging_output=150,
                charging_time=RouteChargingTimeInput(25),
                charger_type=ChargingConnectorType.QUICK,
                state_of_charge_difference=35,
            ),
            None,
        ),
        estimated_time_of_departure=departure,
        estimated_time_of_arrival=arrival,
        distance=RouteDistanceInput(42, DistanceUnit.MILE),
        temperature=RouteTemperatureInput(70.0, None),
        notification_interval=RouteNotificationIntervalInput(
            15,
            NotificationIntervalUnit.MINUTE,
        ),
        avoid_highway=False,
    )

    created = await client.async_save_route(
        "JN1TESTVIN",
        route,
        arrival_flag=None,
        data_source=NavigationDataSource.KMR,
    )
    updated = await client.async_update_route(
        "JN1TESTVIN",
        PlannedRouteUpdate(
            "route-1",
            name=None,
            routes=None,
            avoid_tolls=False,
        ),
        departure_flag=None,
    )

    assert created == ServiceRequest("save-1", ServiceRequestKind.ROUTE)
    assert updated == ServiceRequest("update-1", ServiceRequestKind.ROUTE)
    save_payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert save_payload["variables"] == {
        "vin": "JN1TESTVIN",
        "plannedRoute": {
            "name": "Morning route",
            "routes": [
                {
                    "name": "Quick charger",
                    "coordinate": {"latitude": 32.8, "longitude": -117.2},
                    "address": {},
                    "phoneNumber": None,
                    "chargingOutput": 150,
                    "chargingTime": {"unit": "MIN", "value": 25},
                    "chargerType": "QUICK",
                    "socDiff": 35,
                },
                None,
            ],
            "estimatedTimeOfDeparture": "2026-08-02T08:00:00-07:00",
            "estimatedTimeOfArrival": "2026-08-02T09:15:00-07:00",
            "distance": {"value": 42, "unit": "MILE"},
            "temperature": {"value": 70.0, "unit": None},
            "notificationInterval": {"value": 15, "unit": "MIN"},
            "avoidHighway": False,
        },
        "arrivalFlag": None,
    }
    save_headers = cast(Mapping[str, str], session.calls[0]["headers"])
    update_headers = cast(Mapping[str, str], session.calls[1]["headers"])
    assert save_headers["x-tsp-datasource"] == "KMR"
    assert "x-tsp-datasource" not in update_headers
    update_payload = cast(Mapping[str, object], session.calls[1]["json"])
    assert update_payload["variables"] == {
        "vin": "JN1TESTVIN",
        "plannedRoute": {
            "id": "route-1",
            "name": None,
            "routes": None,
            "avoidTolls": False,
        },
        "departureFlag": None,
    }


@pytest.mark.asyncio
async def test_navigation_nullable_success_and_limit_error() -> None:
    session = FakeSession(
        FakeResponse(200, {"data": {"sendPlannedRoute": {"success": None}}}),
        FakeResponse(
            200,
            {
                "data": {
                    "sendPointOfInterest": {
                        "__typename": "LimitReachedError",
                        "message": "Destination limit reached",
                    }
                }
            },
        ),
    )
    client = make_client(session, read_only=False)

    success = await client.async_send_planned_route("JN1TESTVIN", "route-1")
    with pytest.raises(ResponseError, match="Destination limit reached"):
        await client.async_send_point_of_interest(
            "JN1TESTVIN",
            PointOfInterestFolder.FAVORITES,
            DestinationInput("Work", CoordinateInput(32.7, -117.1)),
            calculation_condition=RouteCalculationCondition.FASTEST_ROUTE,
        )

    assert success is False
    poi_payload = cast(Mapping[str, object], session.calls[1]["json"])
    assert poi_payload["variables"] == {
        "vin": "JN1TESTVIN",
        "folderName": "FAVORITES",
        "destinationInput": {
            "name": "Work",
            "coordinate": {"latitude": 32.7, "longitude": -117.1},
            "address": {},
        },
        "calculationCondition": "FASTEST_ROUTE",
    }


@pytest.mark.asyncio
async def test_route_and_point_of_interest_deletes_return_upstream_success() -> None:
    session = FakeSession(
        FakeResponse(200, {"data": {"deleteRoute": {"success": True}}}),
        FakeResponse(
            200,
            {"data": {"deleteFavoritePointOfInterest": {"success": False}}},
        ),
    )
    client = make_client(session, read_only=False)

    route_deleted = await client.async_delete_route("JN1TESTVIN", "route-1")
    favorite_deleted = await client.async_delete_favorite_point_of_interest(
        "JN1TESTVIN",
        "destination-1",
    )

    assert route_deleted is True
    assert favorite_deleted is False
