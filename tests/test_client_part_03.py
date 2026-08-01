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
    AddressInput,
    AlertRadiusInput,
    BoundaryAlertInput,
    BoundaryAlertType,
    BreachAlerts,
    CoordinateInput,
    DistanceUnit,
    ResponseError,
    VehicleAlertKind,
    VehicleAlertRequest,
)


@pytest.mark.asyncio
async def test_get_vehicle_alerts_rejects_missing_required_alert_field() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "boundaryAlerts": [
                            {
                                "serviceRequestId": None,
                                "alertType": "ON_ENTRY",
                                "name": "Home",
                                "enabled": True,
                                "inVehicleWarning": False,
                                "address": None,
                                "location": None,
                                "radius": None,
                            }
                        ],
                        "curfewAlerts": [],
                        "speedAlerts": [],
                        "valetAlert": None,
                    }
                }
            },
        )
    )

    with pytest.raises(ResponseError, match="serviceRequestId"):
        await make_client(session).async_get_vehicle_alerts("JN1TESTVIN")


@pytest.mark.asyncio
async def test_get_breach_alerts_uses_defaults_and_preserves_raw_values() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "breachAlerts": {
                            "itemsPerPage": 20,
                            "pageNumber": 1,
                            "totalItems": 2,
                            "totalPages": 1,
                            "alerts": [
                                {
                                    "serviceType": "FUTURE_SERVICE",
                                    "breachDateTime": "2026-07-31T20:30:00Z",
                                    "name": "Garage",
                                    "location": {"latitude": 32.8, "longitude": -117.2},
                                },
                                None,
                            ],
                        }
                    }
                }
            },
        )
    )
    client = make_client(session)

    result = await client.async_get_breach_alerts("JN1TESTVIN")

    assert result is not None
    assert result.items_per_page == 20
    assert result.page_number == 1
    assert result.total_items == 2
    assert result.total_pages == 1
    assert result.alerts is not None
    breach = result.alerts[0]
    assert breach is not None
    assert breach.service_type == "FUTURE_SERVICE"
    assert breach.breach_date_time is not None
    assert breach.breach_date_time.isoformat() == "2026-07-31T20:30:00+00:00"
    assert breach.location is not None
    assert breach.location.longitude == -117.2
    assert result.alerts[1] is None

    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "BreachAlerts"
    assert payload["variables"] == {
        "vin": "JN1TESTVIN",
        "pageNumber": 1,
        "itemsPerPage": 20,
    }
    query = cast(str, payload["query"])
    assert "paginate: { itemsPerPage: $itemsPerPage pageNumber: $pageNumber }" in query
    assert "breachDateTime" in query


@pytest.mark.asyncio
async def test_get_breach_alerts_preserves_nullable_page() -> None:
    session = FakeSession(
        FakeResponse(200, {"data": {"vehicle": None}}),
        FakeResponse(200, {"data": {"vehicle": {"breachAlerts": None}}}),
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "breachAlerts": {
                            "itemsPerPage": None,
                            "pageNumber": None,
                            "totalItems": None,
                            "totalPages": None,
                            "alerts": None,
                        }
                    }
                }
            },
        ),
    )
    client = make_client(session)

    missing_vehicle = await client.async_get_breach_alerts("JN1TESTVIN")
    missing_page = await client.async_get_breach_alerts("JN1TESTVIN")
    nullable_page = await client.async_get_breach_alerts("JN1TESTVIN")

    assert missing_vehicle is None
    assert missing_page is None
    assert nullable_page == BreachAlerts(
        items_per_page=None,
        page_number=None,
        total_items=None,
        total_pages=None,
        alerts=None,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("page_number", "items_per_page", "name"),
    [
        (0, 20, "page_number"),
        (-1, 20, "page_number"),
        (True, 20, "page_number"),
        (1, 0, "items_per_page"),
        (1, -1, "items_per_page"),
        (1, False, "items_per_page"),
    ],
)
async def test_get_breach_alerts_rejects_invalid_pagination_before_network(
    page_number: int,
    items_per_page: int,
    name: str,
) -> None:
    session = FakeSession()

    with pytest.raises(ValueError, match=name):
        await make_client(session).async_get_breach_alerts(
            "JN1TESTVIN",
            page_number=page_number,
            items_per_page=items_per_page,
        )

    assert session.calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("alert_kind", "operation_name", "root_field"),
    [
        (VehicleAlertKind.BOUNDARY, "VehicleBoundaryAlert", "boundaryAlert"),
        (VehicleAlertKind.CURFEW, "VehicleCurfewAlert", "curfewAlert"),
        (VehicleAlertKind.SPEED, "VehicleSpeedAlert", "speedAlert"),
        (VehicleAlertKind.VALET, "VehicleValetAlert", "valetAlert"),
    ],
)
async def test_get_alert_request_status_dispatches_exact_read_only_query(
    alert_kind: VehicleAlertKind,
    operation_name: str,
    root_field: str,
) -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {"data": {"vehicle": {root_field: {"status": "FUTURE_STATUS"}}}},
        )
    )
    client = make_client(session)

    status = await client.async_get_alert_request_status(
        "JN1TESTVIN",
        "request-1",
        alert_kind,
    )

    assert status == "FUTURE_STATUS"
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == operation_name
    assert payload["variables"] == {
        "vin": "JN1TESTVIN",
        "serviceRequestId": "request-1",
    }
    query = cast(str, payload["query"])
    assert f"{root_field}(serviceRequestId: $serviceRequestId)" in query


@pytest.mark.asyncio
async def test_get_alert_request_status_preserves_nullable_valet_status() -> None:
    session = FakeSession(
        FakeResponse(200, {"data": {"vehicle": {"valetAlert": {"status": None}}}}),
        FakeResponse(200, {"data": {"vehicle": None}}),
    )
    client = make_client(session)

    nullable_status = await client.async_get_alert_request_status(
        "JN1TESTVIN",
        "request-1",
        VehicleAlertKind.VALET,
    )
    missing_vehicle = await client.async_get_alert_request_status(
        "JN1TESTVIN",
        "request-1",
        VehicleAlertKind.BOUNDARY,
    )

    assert nullable_status is None
    assert missing_vehicle is None


@pytest.mark.asyncio
async def test_get_alert_request_status_requires_boundary_status_when_present() -> None:
    session = FakeSession(
        FakeResponse(200, {"data": {"vehicle": {"boundaryAlert": {"status": None}}}})
    )

    with pytest.raises(ResponseError, match=r"boundaryAlert\.status"):
        await make_client(session).async_get_alert_request_status(
            "JN1TESTVIN",
            "request-1",
            VehicleAlertKind.BOUNDARY,
        )


@pytest.mark.asyncio
async def test_create_boundary_alert_serializes_complete_typed_input() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {"data": {"createBoundaryAlert": {"serviceRequestId": "operation-1"}}},
        )
    )
    client = make_client(session, read_only=False)

    request = await client.async_create_boundary_alert(
        "JN1TESTVIN",
        BoundaryAlertInput(
            name="Home",
            coordinate=CoordinateInput(32.72, -117.16),
            address=AddressInput(
                address1="100 Main St",
                city="San Diego",
                state="CA",
                postal_code="92101",
                country="US",
                district=None,
            ),
            radius=AlertRadiusInput(2.5, DistanceUnit.MILE),
            in_vehicle_warning=True,
            alert_type=BoundaryAlertType.ON_EXIT,
        ),
    )

    assert request == VehicleAlertRequest("operation-1", VehicleAlertKind.BOUNDARY)
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "CreateBoundaryAlert"
    assert payload["variables"] == {
        "vin": "JN1TESTVIN",
        "alert": {
            "name": "Home",
            "coordinate": {"latitude": 32.72, "longitude": -117.16},
            "address": {
                "address1": "100 Main St",
                "city": "San Diego",
                "state": "CA",
                "postalCode": "92101",
                "country": "US",
                "district": None,
            },
            "radius": {"value": 2.5, "unit": "MILE"},
            "inVehicleWarning": True,
            "alertType": "ON_EXIT",
        },
    }
