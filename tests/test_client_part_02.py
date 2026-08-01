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
    DistanceUnit,
    RemoteServiceHistory,
    SpeedUnit,
    VehicleAlerts,
    VehiclePhotos,
)


@pytest.mark.asyncio
async def test_get_photos_around_vehicle_preserves_nullable_result() -> None:
    session = FakeSession(
        FakeResponse(200, {"data": {"vehicle": None}}),
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "year": "2026",
                        "model": "ARIYA",
                        "vin": "JN1TESTVIN",
                        "photosAroundVehicle": None,
                    }
                }
            },
        ),
    )
    client = make_client(session)

    missing_vehicle = await client.async_get_photos_around_vehicle("JN1TESTVIN")
    missing_photos = await client.async_get_photos_around_vehicle("JN1TESTVIN")

    assert missing_vehicle is None
    assert missing_photos == VehiclePhotos(
        vin="JN1TESTVIN",
        year="2026",
        model="ARIYA",
        photos=None,
    )


@pytest.mark.asyncio
async def test_get_remote_service_history_parses_service_contract_and_raw_enums() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "remoteServiceHistory": {
                            "pageNumber": 2,
                            "itemsPerPage": 10,
                            "totalItems": 11,
                            "totalPages": 2,
                            "history": [
                                {
                                    "serviceRequestId": "request-1",
                                    "status": "FUTURE_STATUS",
                                    "serviceType": "FUTURE_SERVICE",
                                    "statusChangeDateTime": "2026-07-31T20:30:00Z",
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

    result = await client.async_get_remote_service_history(
        "JN1TESTVIN",
        page_number=2,
        items_per_page=10,
    )

    assert result is not None
    assert result.page_number == 2
    assert result.items_per_page == 10
    assert result.total_items == 11
    assert result.total_pages == 2
    assert result.history is not None
    assert len(result.history) == 2
    entry = result.history[0]
    assert entry is not None
    assert entry.service_request_id == "request-1"
    assert entry.status == "FUTURE_STATUS"
    assert entry.service_type == "FUTURE_SERVICE"
    assert entry.status_change_date_time is not None
    assert entry.status_change_date_time.isoformat() == "2026-07-31T20:30:00+00:00"
    assert result.history[1] is None

    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "RemoteServiceHistory"
    assert payload["variables"] == {
        "vin": "JN1TESTVIN",
        "pageNumber": 2,
        "itemsPerPage": 10,
    }
    query = cast(str, payload["query"])
    assert "paginate: { pageNumber: $pageNumber itemsPerPage: $itemsPerPage }" in query
    assert "statusChangeDateTime" in query


@pytest.mark.asyncio
async def test_get_remote_service_history_preserves_nullable_page_and_list() -> None:
    session = FakeSession(
        FakeResponse(200, {"data": {"vehicle": None}}),
        FakeResponse(200, {"data": {"vehicle": {"remoteServiceHistory": None}}}),
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "remoteServiceHistory": {
                            "pageNumber": None,
                            "itemsPerPage": None,
                            "totalItems": None,
                            "totalPages": None,
                            "history": None,
                        }
                    }
                }
            },
        ),
    )
    client = make_client(session)

    missing_vehicle = await client.async_get_remote_service_history(
        "JN1TESTVIN", page_number=1, items_per_page=10
    )
    missing_page = await client.async_get_remote_service_history(
        "JN1TESTVIN", page_number=1, items_per_page=10
    )
    nullable_page = await client.async_get_remote_service_history(
        "JN1TESTVIN", page_number=1, items_per_page=10
    )

    assert missing_vehicle is None
    assert missing_page is None
    assert nullable_page == RemoteServiceHistory(
        page_number=None,
        items_per_page=None,
        total_items=None,
        total_pages=None,
        history=None,
    )


@pytest.mark.asyncio
async def test_get_vehicle_alerts_parses_service_contract_and_preserves_raw_enums() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "boundaryAlerts": [
                            {
                                "serviceRequestId": "boundary-1",
                                "alertType": "FUTURE_BOUNDARY",
                                "name": "Home",
                                "enabled": True,
                                "inVehicleWarning": False,
                                "address": {
                                    "address1": "1 Main St",
                                    "address2": None,
                                    "city": "San Diego",
                                    "state": "CA",
                                    "country": "US",
                                    "postalCode": "92101",
                                },
                                "location": {"latitude": 32.7, "longitude": -117.1},
                                "radius": {"value": 2.5, "unit": "FUTURE_DISTANCE"},
                            },
                            None,
                        ],
                        "curfewAlerts": [
                            {
                                "serviceRequestId": "curfew-1",
                                "name": "Night",
                                "enabled": False,
                                "inVehicleWarning": True,
                                "schedule": {
                                    "allDay": None,
                                    "startDateTime": "2026-08-01T22:00:00-07:00",
                                    "duration": "PT8H",
                                    "weekDays": ["MO", None, "FUTURE_DAY"],
                                },
                            }
                        ],
                        "speedAlerts": [
                            {
                                "serviceRequestId": "speed-1",
                                "name": "Freeway",
                                "enabled": True,
                                "inVehicleWarning": True,
                                "speedThreshold": {"type": "FUTURE_SPEED", "value": 65},
                            }
                        ],
                        "valetAlert": {
                            "serviceRequestId": None,
                            "radius": {"unit": None, "value": 0.5},
                        },
                    }
                }
            },
        )
    )
    client = make_client(session)

    result = await client.async_get_vehicle_alerts(
        "JN1TESTVIN",
        speed_unit=SpeedUnit.MPH,
        distance_unit=DistanceUnit.MILE,
    )

    assert result is not None
    assert result.boundary_alerts is not None
    boundary = result.boundary_alerts[0]
    assert boundary is not None
    assert boundary.alert_type == "FUTURE_BOUNDARY"
    assert boundary.address is not None
    assert boundary.address.postal_code == "92101"
    assert boundary.location is not None
    assert boundary.location.latitude == 32.7
    assert boundary.radius is not None
    assert boundary.radius.value == 2.5
    assert boundary.radius.unit == "FUTURE_DISTANCE"
    assert result.boundary_alerts[1] is None

    assert result.curfew_alerts is not None
    curfew = result.curfew_alerts[0]
    assert curfew is not None
    assert curfew.schedule is not None
    assert curfew.schedule.start_date_time.isoformat() == "2026-08-01T22:00:00-07:00"
    assert curfew.schedule.week_days == ("MO", None, "FUTURE_DAY")

    assert result.speed_alerts is not None
    speed = result.speed_alerts[0]
    assert speed is not None
    assert speed.threshold is not None
    assert speed.threshold.unit == "FUTURE_SPEED"
    assert speed.threshold.value == 65.0

    assert result.valet_alert is not None
    assert result.valet_alert.service_request_id is None
    assert result.valet_alert.radius is not None
    assert result.valet_alert.radius.unit is None

    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "VehicleAlerts"
    assert payload["variables"] == {
        "vin": "JN1TESTVIN",
        "speedUnit": "MPH",
        "distanceUnit": "MILE",
    }
    query = cast(str, payload["query"])
    assert "fragment BoundaryAlertDetails on BoundaryAlert" in query
    assert "fragment CurfewAlertDetails on CurfewAlert" in query
    assert "fragment SpeedAlertDetails on SpeedAlert" in query
    assert "fragment ValetAlertDetails on ValetAlert" in query


@pytest.mark.asyncio
async def test_get_vehicle_alerts_preserves_nullable_fragment_and_lists() -> None:
    session = FakeSession(
        FakeResponse(200, {"data": {"vehicle": None}}),
        FakeResponse(200, {"data": {"vehicle": {"__typename": "BaseVehicle"}}}),
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "boundaryAlerts": None,
                        "curfewAlerts": None,
                        "speedAlerts": None,
                        "valetAlert": None,
                    }
                }
            },
        ),
    )
    client = make_client(session)

    missing_vehicle = await client.async_get_vehicle_alerts("JN1TESTVIN")
    unsupported_vehicle = await client.async_get_vehicle_alerts("JN1TESTVIN")
    nullable_alerts = await client.async_get_vehicle_alerts("JN1TESTVIN")

    assert missing_vehicle is None
    assert unsupported_vehicle is None
    assert nullable_alerts == VehicleAlerts(
        boundary_alerts=None,
        curfew_alerts=None,
        speed_alerts=None,
        valet_alert=None,
    )
    for call in session.calls:
        payload = cast(Mapping[str, object], call["json"])
        assert payload["variables"] == {"vin": "JN1TESTVIN"}
