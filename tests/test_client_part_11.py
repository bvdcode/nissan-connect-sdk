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
    CoordinateInput,
    DestinationInput,
    Journey,
    JourneyWaypoint,
    NavigationAddress,
    NavigationCoordinate,
    NavigationDataSource,
    PointOfInterestFolder,
    ReadOnlyError,
    ServiceRequest,
    ServiceRequestKind,
    ServiceRequestResult,
    ServiceRequestStatus,
    TJunctionLocationInput,
    VehicleJourneys,
)


@pytest.mark.asyncio
async def test_t_junction_mutations_use_exact_required_input_shapes() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {"data": {"saveTJunctionLocations": {"serviceRequestId": "save-tj"}}},
        ),
        FakeResponse(
            200,
            {"data": {"updateSavedTJunctionLocation": {"serviceRequestId": "update-tj"}}},
        ),
        FakeResponse(
            200,
            {"data": {"deleteSavedTJunctionLocations": {"serviceRequestId": "delete-saved-tj"}}},
        ),
        FakeResponse(
            200,
            {
                "data": {
                    "deleteUnsavedTJunctionLocations": {"serviceRequestId": "delete-unsaved-tj"}
                }
            },
        ),
    )
    client = make_client(session, read_only=False)

    saved = await client.async_save_t_junction_locations(
        "JN1TESTVIN",
        "2026-08-01T12:00:00Z",
        (TJunctionLocationInput("location-1", "Downtown"),),
    )
    updated = await client.async_update_saved_t_junction_location(
        "JN1TESTVIN",
        "location-1",
        "Main and First",
    )
    deleted_saved = await client.async_delete_saved_t_junction_locations(
        "JN1TESTVIN",
        ("location-1", "location-2"),
        last_updated_at="",
    )
    deleted_unsaved = await client.async_delete_unsaved_t_junction_locations(
        "JN1TESTVIN",
        ("location-3",),
    )

    assert saved == ServiceRequest("save-tj", ServiceRequestKind.T_JUNCTION)
    assert updated == ServiceRequest("update-tj", ServiceRequestKind.T_JUNCTION)
    assert deleted_saved == ServiceRequest("delete-saved-tj", ServiceRequestKind.T_JUNCTION)
    assert deleted_unsaved == ServiceRequest("delete-unsaved-tj", ServiceRequestKind.T_JUNCTION)
    variables = [
        cast(Mapping[str, object], cast(Mapping[str, object], call["json"])["variables"])
        for call in session.calls
    ]
    assert variables == [
        {
            "input": {
                "vin": "JN1TESTVIN",
                "lastUpdatedAt": "2026-08-01T12:00:00Z",
                "locationIds": [{"id": "location-1", "name": "Downtown"}],
            }
        },
        {
            "input": {
                "vin": "JN1TESTVIN",
                "id": "location-1",
                "locationName": "Main and First",
            }
        },
        {
            "input": {
                "vin": "JN1TESTVIN",
                "locationIds": ["location-1", "location-2"],
                "lastUpdatedAt": "",
            }
        },
        {"input": {"vin": "JN1TESTVIN", "locationIds": ["location-3"]}},
    ]


@pytest.mark.asyncio
async def test_navigation_request_status_dispatches_route_and_t_junction_checks() -> None:
    session = FakeSession(
        FakeResponse(200, {"data": {"checkRouteServiceRequest": {"status": None}}}),
        FakeResponse(
            200,
            {
                "data": {
                    "checkTJunctionServiceRequest": {
                        "status": "FAILED",
                        "statusDetails": "TIMED_OUT",
                    }
                }
            },
        ),
    )
    client = make_client(session)

    route = await client.async_check_service_request(
        "JN1TESTVIN",
        ServiceRequest("route-request", ServiceRequestKind.ROUTE),
    )
    t_junction = await client.async_check_service_request(
        "JN1TESTVIN",
        ServiceRequest("t-junction-request", ServiceRequestKind.T_JUNCTION),
    )

    assert route == ServiceRequestResult(None)
    assert route.is_terminal is False
    assert t_junction == ServiceRequestResult(
        ServiceRequestStatus.FAILED,
        status_details="TIMED_OUT",
    )
    operation_names = [
        cast(Mapping[str, object], call["json"])["operationName"] for call in session.calls
    ]
    assert operation_names == ["CheckRouteServiceRequest", "CheckTJunctionServiceRequest"]


@pytest.mark.asyncio
async def test_navigation_commands_respect_read_only_mode() -> None:
    session = FakeSession()
    client = make_client(session)
    destination = DestinationInput("Home", CoordinateInput(32.7, -117.1))

    with pytest.raises(ReadOnlyError):
        await client.async_send_journey("JN1TESTVIN", (destination,))
    with pytest.raises(ReadOnlyError):
        await client.async_send_point_of_interest(
            "JN1TESTVIN",
            PointOfInterestFolder.RECENTS,
            destination,
        )
    with pytest.raises(ReadOnlyError):
        await client.async_delete_route("JN1TESTVIN", "route-1")
    with pytest.raises(ReadOnlyError):
        await client.async_delete_unsaved_t_junction_locations(
            "JN1TESTVIN",
            ("location-1",),
        )

    assert session.calls == []


@pytest.mark.asyncio
async def test_kmr_header_is_preserved_after_token_refresh_retry() -> None:
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
        FakeResponse(200, {"data": {"sendPlannedRoute": {"success": True}}}),
    )
    client = make_client(session, read_only=False)

    success = await client.async_send_planned_route(
        "JN1TESTVIN",
        "route-1",
        data_source=NavigationDataSource.KMR,
    )

    assert success is True
    initial_headers = cast(Mapping[str, str], session.calls[0]["headers"])
    retry_headers = cast(Mapping[str, str], session.calls[2]["headers"])
    assert initial_headers["x-tsp-datasource"] == "KMR"
    assert retry_headers["x-tsp-datasource"] == "KMR"
    assert retry_headers["Authorization"] == "Bearer replacement-access"


@pytest.mark.asyncio
async def test_get_vehicle_journeys_preserves_nullable_lists_and_items() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "journeys": [
                            None,
                            {
                                "waypoints": [
                                    None,
                                    {
                                        "id": "waypoint-1",
                                        "name": "Home",
                                        "phoneNumber": None,
                                        "address": {
                                            "address1": "1 Main St",
                                            "address2": None,
                                            "city": "San Diego",
                                            "state": "CA",
                                            "postalCode": "92101",
                                            "country": "US",
                                        },
                                        "coordinate": {
                                            "latitude": 32.7157,
                                            "longitude": -117.1611,
                                        },
                                    },
                                ]
                            },
                        ]
                    }
                }
            },
        ),
    )
    client = make_client(session)

    journeys = await client.async_get_vehicle_journeys("JN1TESTVIN")

    assert journeys == VehicleJourneys(
        (
            None,
            Journey(
                (
                    None,
                    JourneyWaypoint(
                        id="waypoint-1",
                        name="Home",
                        address=NavigationAddress(
                            address1="1 Main St",
                            address2=None,
                            city="San Diego",
                            state="CA",
                            postal_code="92101",
                            country="US",
                        ),
                        coordinate=NavigationCoordinate(32.7157, -117.1611),
                        phone_number=None,
                    ),
                )
            ),
        )
    )
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "VehicleJourneys"
    assert payload["variables"] == {"vin": "JN1TESTVIN"}
