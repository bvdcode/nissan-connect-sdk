from __future__ import annotations

import base64
import hashlib
import json
from collections.abc import Mapping
from datetime import datetime
from typing import Any, cast

import pytest
from aiohttp import ClientSession

from pynissan import (
    UNSET,
    AddressInput,
    AlertRadiusInput,
    AlertScheduleInput,
    AlertSpeedInput,
    BoundaryAlertInput,
    BoundaryAlertType,
    BoundaryAlertUpdate,
    BreachAlerts,
    CameraPosition,
    CameraService,
    ChargeHistoryAggregator,
    ChargingConnectorType,
    ClimateParameters,
    ClimateSettings,
    CoordinateInput,
    Country,
    CurfewAlertInput,
    DataPrivacyMode,
    DataWipeType,
    DestinationInput,
    DistanceUnit,
    EngineOilDrainRange,
    EVWaypoint,
    EVWaypointLimitReachedError,
    EVWaypointRoute,
    EVWaypointRouteType,
    EVWaypointStatus,
    EVWaypointUnableToCompleteRouteError,
    GraphQLError,
    Journey,
    JourneyWaypoint,
    NavigationAddress,
    NavigationCoordinate,
    NavigationDataSource,
    NavigationDistance,
    NavigationNotificationInterval,
    NavigationRouteWaypoint,
    NavigationTemperature,
    NissanClient,
    NotificationCategory,
    NotificationDestination,
    NotificationIntervalUnit,
    NotificationPreference,
    NotificationPreferenceInput,
    NotificationTypeInput,
    NotificationTypePreference,
    OtaBatteryLevel,
    OtaCampaignDescription,
    OtaUpdate,
    OtaUpdateErrorInfo,
    OtaUpdateProgress,
    OtaUpdateState,
    OtaUpdateStatus,
    PlannedRoute,
    PlannedRouteInput,
    PlannedRouteUpdate,
    PlugConnectorType,
    PointOfInterestDestination,
    PointOfInterestDestinationFolder,
    PointOfInterestFolder,
    ProductType,
    PurchaseType,
    ReadOnlyError,
    RecalculatedWaypointType,
    ReminderNotificationsAfterLeavingVehicle,
    RemoteServiceHistory,
    ResponseError,
    RouteCalculationCondition,
    RouteChargingTimeInput,
    RouteDistanceInput,
    RouteHistoryEntry,
    RouteNotificationIntervalInput,
    RouteStatus,
    RouteTemperatureInput,
    RouteWaypointInput,
    SavedTJunctionLocation,
    SeatClimateOption,
    ServiceRequest,
    ServiceRequestKind,
    ServiceRequestResult,
    ServiceRequestStatus,
    SpeedAlertInput,
    SpeedUnit,
    TemperatureUnit,
    TJunctionLocationInput,
    TJunctionLocations,
    Tokens,
    UnableToCompleteSubStepErrorDetails,
    UnsavedTJunctionLocation,
    V2LState,
    V2LStatus,
    ValetRadiusInput,
    VehicleAlertKind,
    VehicleAlertRequest,
    VehicleAlerts,
    VehicleJourneys,
    VehiclePhoto,
    VehiclePhotos,
    VehiclePlannedRoutes,
    VehiclePointOfInterestDestinations,
    VehiclePreferences,
    VehicleRoutesHistory,
    VehicleSubscription,
    VehicleSubscriptionPendingOrder,
    VehicleSubscriptionProduct,
    VehicleSubscriptions,
    VehicleWifiConsumption,
    WeekDay,
)


class FakeResponse:
    def __init__(
        self,
        status: int,
        payload: object = None,
        *,
        body: str = "",
        url: str = "",
        headers: Mapping[str, str] | None = None,
    ) -> None:
        self.status = status
        self._payload = payload
        self._body = body
        self.url = url
        self.headers = dict(headers or {})

    async def __aenter__(self) -> FakeResponse:
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def json(self, *, content_type: object = None) -> object:
        return self._payload

    async def text(self) -> str:
        return self._body


class FakeSession:
    def __init__(self, *responses: FakeResponse) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def get(self, url: str, **kwargs: object) -> FakeResponse:
        return self._request("GET", url, kwargs)

    def post(self, url: str, **kwargs: object) -> FakeResponse:
        return self._request("POST", url, kwargs)

    def _request(self, method: str, url: str, kwargs: Mapping[str, object]) -> FakeResponse:
        self.calls.append({"method": method, "url": url, **kwargs})
        response = self.responses.pop(0)
        if not response.url:
            response.url = url
        return response


TOKENS = Tokens("access-token", "refresh-token", "id-token")


def jwt_with_expiration(expires_at: int) -> str:
    encoded_payload = (
        base64.urlsafe_b64encode(json.dumps({"exp": expires_at}).encode()).decode().rstrip("=")
    )
    return f"header.{encoded_payload}.signature"


def make_client(
    session: FakeSession,
    *,
    read_only: bool = True,
    tokens: Tokens | None = TOKENS,
) -> NissanClient:
    return NissanClient(
        cast(ClientSession, session),
        read_only=read_only,
        tokens=tokens,
    )


def test_client_uses_requested_country() -> None:
    client = NissanClient(
        cast(ClientSession, FakeSession()),
        country=Country.US,
        tokens=TOKENS,
    )

    assert client.country is Country.US


@pytest.mark.asyncio
async def test_authenticate_normalizes_credentials_and_publishes_tokens() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "access_token": "new-access",
                "refresh_token": "new-refresh",
                "id_token": "new-id",
            },
        )
    )
    published: list[Tokens] = []
    client = NissanClient(
        cast(ClientSession, session),
        oauth_device_id="device-123",
        token_listener=published.append,
    )

    tokens = await client.async_authenticate("OWNER@EXAMPLE.COM", "secret")

    assert tokens == Tokens("new-access", "new-refresh", "new-id")
    assert published == [tokens]
    call = session.calls[0]
    assert str(call["url"]).endswith("/token")
    assert call["data"] == {
        "username": "NISNNAVCS/owner@example.com",
        "password": "secret",
        "scope": "openid device_device-123+internal_login",
        "grant_type": "password",
    }
    headers = cast(Mapping[str, str], call["headers"])
    assert headers["Authorization"].startswith("Basic ")
    assert headers["User-Agent"] == "okhttp/5.2.1"


@pytest.mark.asyncio
async def test_graphql_uses_country_profile_and_identity_token() -> None:
    session = FakeSession(FakeResponse(200, {"data": {"vehicles": []}}))
    client = make_client(session)

    assert await client.async_get_vehicles() == ()

    headers = cast(Mapping[str, str], session.calls[0]["headers"])
    assert headers["Country"] == Country.US
    assert headers["Accept-Language"] == "en-US"
    assert headers["id-token"] == "id-token"
    assert "apollographql-client-name" in headers
    assert "apollographql-client-version" in headers


@pytest.mark.asyncio
async def test_get_vehicle_status_parses_ariya_battery() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "__typename": "ElectricAVK2Vehicle",
                        "batteryStatus": {
                            "level": 73,
                            "isPluggedIn": True,
                            "isCharging": False,
                            "remainingChargeTime": 42,
                            "remainingMileage": {"value": 181, "unit": "MILE"},
                        },
                        "climateStatus": {
                            "state": "OFF",
                            "temperature": {"value": 72.0, "unit": "FAHRENHEIT"},
                        },
                        "doorsStatus": None,
                        "fuelAutonomy": None,
                        "mileage": {"total": 1200, "unit": "MILE", "recordedTime": None},
                        "tirePressure": None,
                        "mils": [],
                    }
                }
            },
        )
    )
    client = make_client(session)

    status = await client.async_get_vehicle_status("JN1TESTVIN")

    assert status.vehicle_type == "ElectricAVK2Vehicle"
    assert status.battery is not None
    assert status.battery.level == 73
    assert status.battery.is_plugged_in is True
    assert status.battery.is_charging is False
    assert status.battery.remaining_charge_time == 42
    assert status.battery.remaining_mileage is not None
    assert status.battery.remaining_mileage.value == 181
    assert status.engine_oil_drain_range is None
    call = session.calls[0]
    headers = cast(Mapping[str, str], call["headers"])
    assert headers["Brand"] == "Nissan"
    assert headers["Country"] == "US"
    assert headers["id-token"] == "id-token"
    assert headers["User-Agent"] == "okhttp/5.2.1"


@pytest.mark.asyncio
async def test_get_vehicle_status_parses_engine_oil_drain_range() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "__typename": "AVK2Vehicle",
                        "batteryStatus": None,
                        "climateStatus": None,
                        "doorsStatus": None,
                        "fuelAutonomy": None,
                        "mileage": None,
                        "tirePressure": None,
                        "mils": [],
                        "engineOilDrainRange": {
                            "range": 4321,
                            "unit": "MILE",
                            "lastUpdatedAt": "2026-07-31T21:45:00Z",
                        },
                    }
                }
            },
        )
    )
    client = make_client(session)

    status = await client.async_get_vehicle_status("JN1TESTVIN")

    engine_oil_drain_range = status.engine_oil_drain_range
    assert engine_oil_drain_range is not None
    assert engine_oil_drain_range == EngineOilDrainRange(
        range=4321,
        unit=DistanceUnit.MILE,
        last_updated_at=engine_oil_drain_range.last_updated_at,
    )
    assert engine_oil_drain_range.last_updated_at.isoformat() == ("2026-07-31T21:45:00+00:00")
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    query = cast(str, payload["query"])
    assert "... on AVK2Vehicle" in query
    assert "... on EVOVehicle" in query
    assert "engineOilDrainRange(unit: $unit)" in query
    assert "lastUpdatedAt" in query


@pytest.mark.asyncio
async def test_get_photos_around_vehicle_parses_service_contract() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "year": "2026",
                        "model": "ARIYA",
                        "vin": "JN1TESTVIN",
                        "photosAroundVehicle": [
                            {
                                "id": "photo-1",
                                "filename": "front.jpg",
                                "link": "https://example.invalid/front.jpg",
                                "timeStamp": "2026-07-31T20:15:00Z",
                                "cameraPosition": "OUTSIDE_FRONT_CAMERA",
                                "cameraService": "DVR_REMOTE_PHOTO",
                            },
                            None,
                            {
                                "id": None,
                                "filename": None,
                                "link": None,
                                "timeStamp": None,
                                "cameraPosition": "FUTURE_CAMERA",
                                "cameraService": "FUTURE_SERVICE",
                            },
                        ],
                    }
                }
            },
        )
    )
    client = make_client(session)

    result = await client.async_get_photos_around_vehicle("JN1TESTVIN")

    assert result is not None
    assert result.vin == "JN1TESTVIN"
    assert result.year == "2026"
    assert result.model == "ARIYA"
    assert result.photos is not None
    assert len(result.photos) == 3
    first_photo = result.photos[0]
    assert first_photo is not None
    assert first_photo.id == "photo-1"
    assert first_photo.filename == "front.jpg"
    assert first_photo.link == "https://example.invalid/front.jpg"
    assert first_photo.camera_position is CameraPosition.OUTSIDE_FRONT_CAMERA
    assert first_photo.camera_service is CameraService.DVR_REMOTE_PHOTO
    assert first_photo.timestamp is not None
    assert first_photo.timestamp.isoformat() == "2026-07-31T20:15:00+00:00"
    assert result.photos[1] is None
    assert result.photos[2] == VehiclePhoto(
        id=None,
        filename=None,
        link=None,
        timestamp=None,
        camera_position=CameraPosition.UNKNOWN_VALUE,
        camera_service=CameraService.UNKNOWN_VALUE,
    )

    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "PhotosAroundVehicle"
    assert payload["variables"] == {"vin": "JN1TESTVIN"}
    query = cast(str, payload["query"])
    assert "photosAroundVehicle" in query
    assert "timeStamp" in query


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


@pytest.mark.asyncio
async def test_update_boundary_alert_distinguishes_omitted_and_null_fields() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {"data": {"setBoundaryAlert": {"serviceRequestId": "operation-2"}}},
        )
    )
    client = make_client(session, read_only=False)

    request = await client.async_update_boundary_alert(
        "JN1TESTVIN",
        "configured-alert-1",
        BoundaryAlertUpdate(
            name=None,
            radius=UNSET,
            in_vehicle_warning=False,
        ),
    )

    assert request == VehicleAlertRequest("operation-2", VehicleAlertKind.BOUNDARY)
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "SetBoundaryAlert"
    assert payload["variables"] == {
        "vin": "JN1TESTVIN",
        "alert": {
            "serviceRequestId": "configured-alert-1",
            "name": None,
            "inVehicleWarning": False,
        },
    }


@pytest.mark.asyncio
async def test_curfew_alert_create_and_update_use_exact_schedule_contract() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {"data": {"createCurfewAlert": {"serviceRequestId": "curfew-create"}}},
        ),
        FakeResponse(
            200,
            {"data": {"setCurfewAlert": {"serviceRequestId": "curfew-update"}}},
        ),
    )
    client = make_client(session, read_only=False)
    alert = CurfewAlertInput(
        name="Night",
        in_vehicle_warning=True,
        schedule=AlertScheduleInput(
            datetime.fromisoformat("2026-08-01T22:00:00-07:00"),
            "PT8H",
            (WeekDay.FRIDAY, WeekDay.SATURDAY),
        ),
    )

    created = await client.async_create_curfew_alert("JN1TESTVIN", alert)
    updated = await client.async_update_curfew_alert(
        "JN1TESTVIN",
        "configured-curfew-1",
        alert,
    )

    assert created == VehicleAlertRequest("curfew-create", VehicleAlertKind.CURFEW)
    assert updated == VehicleAlertRequest("curfew-update", VehicleAlertKind.CURFEW)
    create_payload = cast(Mapping[str, object], session.calls[0]["json"])
    update_payload = cast(Mapping[str, object], session.calls[1]["json"])
    expected_alert = {
        "name": "Night",
        "inVehicleWarning": True,
        "schedule": {
            "startDateTime": "2026-08-01T22:00:00-07:00",
            "duration": "PT8H",
            "weekDays": ["FR", "SA"],
        },
    }
    assert create_payload["operationName"] == "CreateCurfewAlert"
    assert create_payload["variables"] == {"vin": "JN1TESTVIN", "alert": expected_alert}
    assert update_payload["operationName"] == "SetCurfewAlert"
    assert update_payload["variables"] == {
        "vin": "JN1TESTVIN",
        "serviceRequestId": "configured-curfew-1",
        "alert": expected_alert,
    }


@pytest.mark.asyncio
async def test_curfew_alert_rejects_naive_date_time_before_network_request() -> None:
    session = FakeSession()
    client = make_client(session, read_only=False)
    alert = CurfewAlertInput(
        name="Night",
        in_vehicle_warning=False,
        schedule=AlertScheduleInput(datetime(2026, 8, 1, 22), "PT8H", (WeekDay.MONDAY,)),
    )

    with pytest.raises(ValueError, match="UTC offset"):
        await client.async_create_curfew_alert("JN1TESTVIN", alert)

    assert session.calls == []


@pytest.mark.asyncio
async def test_speed_alert_create_and_update_use_modern_and_legacy_fields() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {"data": {"createSpeedAlert": {"serviceRequestId": "speed-create"}}},
        ),
        FakeResponse(
            200,
            {"data": {"setSpeedAlert": {"serviceRequestId": "speed-update"}}},
        ),
    )
    client = make_client(session, read_only=False)

    created = await client.async_create_speed_alert(
        "JN1TESTVIN",
        SpeedAlertInput(
            in_vehicle_warning=True,
            speed=AlertSpeedInput(SpeedUnit.MPH, 65),
        ),
    )
    updated = await client.async_update_speed_alert(
        "JN1TESTVIN",
        "configured-speed-1",
        SpeedAlertInput(
            in_vehicle_warning=False,
            speed=None,
            speed_in_mph=55,
        ),
    )

    assert created == VehicleAlertRequest("speed-create", VehicleAlertKind.SPEED)
    assert updated == VehicleAlertRequest("speed-update", VehicleAlertKind.SPEED)
    create_payload = cast(Mapping[str, object], session.calls[0]["json"])
    update_payload = cast(Mapping[str, object], session.calls[1]["json"])
    assert create_payload["variables"] == {
        "vin": "JN1TESTVIN",
        "alert": {
            "inVehicleWarning": True,
            "speed": {"type": "MPH", "value": 65},
        },
    }
    assert update_payload["variables"] == {
        "vin": "JN1TESTVIN",
        "alert": {
            "serviceRequestId": "configured-speed-1",
            "speedInMPH": 55,
            "inVehicleWarning": False,
            "speed": None,
        },
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method_name", "args", "kwargs", "operation_name", "root_field", "kind"),
    [
        (
            "async_delete_boundary_alert",
            ("JN1TESTVIN", "configured-1"),
            {},
            "CancelBoundaryAlert",
            "cancelBoundaryAlert",
            VehicleAlertKind.BOUNDARY,
        ),
        (
            "async_toggle_boundary_alert",
            ("JN1TESTVIN", "configured-1"),
            {"enabled": True},
            "ToggleBoundaryAlert",
            "toggleBoundaryAlert",
            VehicleAlertKind.BOUNDARY,
        ),
        (
            "async_delete_curfew_alert",
            ("JN1TESTVIN", "configured-1"),
            {},
            "CancelCurfewAlert",
            "cancelCurfewAlert",
            VehicleAlertKind.CURFEW,
        ),
        (
            "async_toggle_curfew_alert",
            ("JN1TESTVIN", "configured-1"),
            {"enabled": False},
            "ToggleCurfewAlert",
            "toggleCurfewAlert",
            VehicleAlertKind.CURFEW,
        ),
        (
            "async_delete_speed_alert",
            ("JN1TESTVIN", "configured-1"),
            {},
            "CancelSpeedAlert",
            "cancelSpeedAlert",
            VehicleAlertKind.SPEED,
        ),
        (
            "async_toggle_speed_alert",
            ("JN1TESTVIN", "configured-1"),
            {"enabled": True},
            "ToggleSpeedAlert",
            "toggleSpeedAlert",
            VehicleAlertKind.SPEED,
        ),
        (
            "async_deactivate_valet_alert",
            ("JN1TESTVIN", "configured-1"),
            {},
            "DeactivateValetAlert",
            "deactivateValetAlert",
            VehicleAlertKind.VALET,
        ),
    ],
)
async def test_alert_delete_and_toggle_commands_use_exact_operations(
    method_name: str,
    args: tuple[str, str],
    kwargs: dict[str, bool],
    operation_name: str,
    root_field: str,
    kind: VehicleAlertKind,
) -> None:
    session = FakeSession(
        FakeResponse(200, {"data": {root_field: {"serviceRequestId": "operation-1"}}})
    )
    client = make_client(session, read_only=False)

    request = await getattr(client, method_name)(*args, **kwargs)

    assert request == VehicleAlertRequest("operation-1", kind)
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == operation_name
    variables = cast(Mapping[str, object], payload["variables"])
    assert variables["vin"] == "JN1TESTVIN"
    if operation_name.startswith("Toggle"):
        assert variables["alert"] == {
            "serviceRequestId": "configured-1",
            "enable": kwargs["enabled"],
        }
    else:
        assert variables["serviceRequestId"] == "configured-1"


@pytest.mark.asyncio
async def test_activate_valet_alert_preserves_omitted_and_explicit_null_variables() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {"data": {"activateValetAlert": {"serviceRequestId": "valet-1"}}},
        ),
        FakeResponse(
            200,
            {"data": {"activateValetAlert": {"serviceRequestId": "valet-2"}}},
        ),
        FakeResponse(
            200,
            {"data": {"activateValetAlert": {"serviceRequestId": "valet-3"}}},
        ),
    )
    client = make_client(session, read_only=False)

    await client.async_activate_valet_alert("JN1TESTVIN")
    request_with_radius = await client.async_activate_valet_alert(
        "JN1TESTVIN",
        radius=ValetRadiusInput(1.5),
        location=None,
    )
    request_with_null_radius = await client.async_activate_valet_alert(
        "JN1TESTVIN",
        radius=None,
    )

    assert request_with_radius == VehicleAlertRequest("valet-2", VehicleAlertKind.VALET)
    assert request_with_null_radius == VehicleAlertRequest("valet-3", VehicleAlertKind.VALET)
    omitted_payload = cast(Mapping[str, object], session.calls[0]["json"])
    radius_payload = cast(Mapping[str, object], session.calls[1]["json"])
    null_radius_payload = cast(Mapping[str, object], session.calls[2]["json"])
    assert omitted_payload["variables"] == {"vin": "JN1TESTVIN"}
    assert radius_payload["variables"] == {
        "vin": "JN1TESTVIN",
        "radiusWithUnit": {"value": 1.5},
        "location": None,
    }
    assert null_radius_payload["variables"] == {
        "vin": "JN1TESTVIN",
        "radiusWithUnit": None,
    }


@pytest.mark.asyncio
async def test_alert_commands_respect_read_only_mode() -> None:
    session = FakeSession()
    client = make_client(session)

    with pytest.raises(ReadOnlyError):
        await client.async_create_speed_alert(
            "JN1TESTVIN",
            SpeedAlertInput(
                in_vehicle_warning=True,
                speed=AlertSpeedInput(SpeedUnit.MPH, 65),
            ),
        )

    assert session.calls == []


@pytest.mark.asyncio
async def test_wait_for_alert_request_uses_returned_operation_id() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {"data": {"vehicle": {"boundaryAlert": {"status": "SUCCESS"}}}},
        )
    )
    client = make_client(session)

    status = await client.async_wait_for_alert_request(
        "JN1TESTVIN",
        VehicleAlertRequest("operation-2", VehicleAlertKind.BOUNDARY),
    )

    assert status == "SUCCESS"
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["variables"] == {
        "vin": "JN1TESTVIN",
        "serviceRequestId": "operation-2",
    }


@pytest.mark.asyncio
async def test_get_reminder_notifications_after_leaving_vehicle_parses_service_contract() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "reminderNotificationsAfterLeavingVehicle": {
                            "lock": True,
                            "door": False,
                            "trunk": None,
                            "sunroof": True,
                            "window": False,
                        }
                    }
                }
            },
        )
    )

    result = await make_client(session).async_get_reminder_notifications_after_leaving_vehicle(
        "JN1TESTVIN"
    )

    assert result == ReminderNotificationsAfterLeavingVehicle(
        lock=True,
        door=False,
        trunk=None,
        sunroof=True,
        window=False,
    )
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "ReminderNotificationsAfterLeavingVehicle"
    assert payload["variables"] == {"vin": "JN1TESTVIN"}
    query = cast(str, payload["query"])
    assert "... on BaseAVK2Vehicle" in query
    assert "reminderNotificationsAfterLeavingVehicle" in query
    assert all(field in query for field in ("lock", "door", "trunk", "sunroof", "window"))


@pytest.mark.asyncio
async def test_get_reminder_notifications_preserves_nullable_response_chain() -> None:
    session = FakeSession(
        FakeResponse(200, {"data": {"vehicle": None}}),
        FakeResponse(200, {"data": {"vehicle": {"__typename": "BaseConnectedVehicle"}}}),
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "reminderNotificationsAfterLeavingVehicle": None,
                    }
                }
            },
        ),
    )
    client = make_client(session)

    assert await client.async_get_reminder_notifications_after_leaving_vehicle("VIN") is None
    assert await client.async_get_reminder_notifications_after_leaving_vehicle("VIN") is None
    assert await client.async_get_reminder_notifications_after_leaving_vehicle("VIN") is None


@pytest.mark.asyncio
async def test_toggle_reminder_notifications_sends_only_supplied_patch_fields() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "toggleReminderNotificationsAfterLeavingVehicle": {
                        "success": False,
                    }
                }
            },
        )
    )

    result = await make_client(
        session,
        read_only=False,
    ).async_toggle_reminder_notifications_after_leaving_vehicle(
        "JN1TESTVIN",
        enable_door=False,
        enable_window=True,
    )

    assert result is False
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "ToggleReminderNotificationsAfterLeavingVehicle"
    assert payload["variables"] == {
        "vin": "JN1TESTVIN",
        "reminderNotifications": {
            "enableDoor": False,
            "enableWindow": True,
        },
    }
    query = cast(str, payload["query"])
    assert "$reminderNotifications: ToggleReminderNotificationsAfterLeavingVehicleInput!" in query
    assert "toggleReminderNotificationsAfterLeavingVehicle" in query


@pytest.mark.asyncio
async def test_toggle_reminder_notifications_preserves_nullable_success() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {"data": {"toggleReminderNotificationsAfterLeavingVehicle": None}},
        ),
        FakeResponse(
            200,
            {
                "data": {
                    "toggleReminderNotificationsAfterLeavingVehicle": {
                        "success": None,
                    }
                }
            },
        ),
    )
    client = make_client(session, read_only=False)

    missing_result = await client.async_toggle_reminder_notifications_after_leaving_vehicle(
        "VIN",
        enable_lock=True,
    )
    nullable_success = await client.async_toggle_reminder_notifications_after_leaving_vehicle(
        "VIN",
        enable_lock=False,
    )

    assert missing_result is None
    assert nullable_success is None


@pytest.mark.asyncio
async def test_toggle_reminder_notifications_rejects_empty_patch_before_io() -> None:
    session = FakeSession()

    with pytest.raises(ValueError, match="At least one reminder notification setting"):
        await make_client(
            session,
            read_only=False,
        ).async_toggle_reminder_notifications_after_leaving_vehicle("VIN")

    assert session.calls == []


@pytest.mark.asyncio
async def test_toggle_reminder_notifications_respects_read_only_mode() -> None:
    session = FakeSession()

    with pytest.raises(ReadOnlyError):
        await make_client(session).async_toggle_reminder_notifications_after_leaving_vehicle(
            "VIN",
            enable_trunk=True,
        )

    assert session.calls == []


@pytest.mark.asyncio
async def test_get_vehicle_data_privacy_mode_is_typed_without_on_fallback() -> None:
    session = FakeSession(
        FakeResponse(200, {"data": {"vehicle": {"dataPrivacyMode": "OFF"}}}),
        FakeResponse(200, {"data": {"vehicle": {"dataPrivacyMode": "FUTURE_MODE"}}}),
        FakeResponse(200, {"data": {"vehicle": None}}),
    )
    client = make_client(session)

    assert await client.async_get_vehicle_data_privacy_mode("VIN") is DataPrivacyMode.OFF
    assert await client.async_get_vehicle_data_privacy_mode("VIN") is DataPrivacyMode.UNKNOWN_VALUE
    assert await client.async_get_vehicle_data_privacy_mode("VIN") is None

    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "VehicleDataPrivacyMode"
    assert payload["variables"] == {"vin": "VIN"}
    assert "dataPrivacyMode" in cast(str, payload["query"])


@pytest.mark.asyncio
async def test_get_vehicle_data_privacy_mode_requires_field_when_vehicle_exists() -> None:
    session = FakeSession(FakeResponse(200, {"data": {"vehicle": {"dataPrivacyMode": None}}}))

    with pytest.raises(ResponseError, match=r"vehicle\.dataPrivacyMode"):
        await make_client(session).async_get_vehicle_data_privacy_mode("VIN")


@pytest.mark.asyncio
async def test_get_vehicle_wifi_consumption_parses_required_gigabyte_values() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "capabilities": {
                            "wifiConsumption": {
                                "usagePercent": 12.5,
                                "usageAmount": 1,
                                "dataCapAmount": 8.0,
                                "updatedAt": "2026-07-31T22:15:00Z",
                            }
                        }
                    }
                }
            },
        )
    )

    result = await make_client(session).async_get_vehicle_wifi_consumption("JN1TESTVIN")

    assert result is not None
    assert result == VehicleWifiConsumption(
        usage_percent=12.5,
        usage_amount_gb=1.0,
        data_cap_amount_gb=8.0,
        updated_at=result.updated_at,
    )
    assert result.updated_at.isoformat() == "2026-07-31T22:15:00+00:00"
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "VehicleWifiConsumption"
    assert payload["variables"] == {"vin": "JN1TESTVIN"}
    query = cast(str, payload["query"])
    assert "wifiConsumption" in query
    assert all(
        field in query for field in ("usagePercent", "usageAmount", "dataCapAmount", "updatedAt")
    )


@pytest.mark.asyncio
async def test_get_vehicle_wifi_consumption_preserves_nullable_response_chain() -> None:
    session = FakeSession(
        FakeResponse(200, {"data": {"vehicle": None}}),
        FakeResponse(200, {"data": {"vehicle": {"capabilities": None}}}),
        FakeResponse(
            200,
            {"data": {"vehicle": {"capabilities": {"wifiConsumption": None}}}},
        ),
    )
    client = make_client(session)

    assert await client.async_get_vehicle_wifi_consumption("VIN") is None
    assert await client.async_get_vehicle_wifi_consumption("VIN") is None
    assert await client.async_get_vehicle_wifi_consumption("VIN") is None


@pytest.mark.asyncio
async def test_get_vehicle_wifi_consumption_requires_inner_fields() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "capabilities": {
                            "wifiConsumption": {
                                "usagePercent": 12.5,
                                "usageAmount": 1.0,
                                "dataCapAmount": 8.0,
                                "updatedAt": None,
                            }
                        }
                    }
                }
            },
        )
    )

    with pytest.raises(ResponseError, match=r"wifiConsumption\.updatedAt"):
        await make_client(session).async_get_vehicle_wifi_consumption("VIN")


@pytest.mark.asyncio
async def test_get_vehicle_preferences_preserves_nullable_mil_data_sharing_flags() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "preferences": {
                            "communication": {
                                "milDataSharing": {
                                    "enabled": True,
                                    "text": False,
                                    "phone": None,
                                    "email": True,
                                }
                            }
                        }
                    }
                }
            },
        )
    )

    result = await make_client(session).async_get_vehicle_preferences("JN1TESTVIN")

    assert result == VehiclePreferences(
        enabled=True,
        text=False,
        phone=None,
        email=True,
    )
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "VehiclePreferences"
    assert payload["variables"] == {"vin": "JN1TESTVIN"}
    query = cast(str, payload["query"])
    assert "preferences" in query
    assert "communication" in query
    assert "milDataSharing" in query
    assert all(field in query for field in ("enabled", "text", "phone", "email"))


@pytest.mark.asyncio
async def test_get_vehicle_preferences_preserves_nullable_response_chain() -> None:
    session = FakeSession(
        FakeResponse(200, {"data": {"vehicle": None}}),
        FakeResponse(200, {"data": {"vehicle": {"preferences": None}}}),
        FakeResponse(
            200,
            {"data": {"vehicle": {"preferences": {"communication": None}}}},
        ),
        FakeResponse(
            200,
            {"data": {"vehicle": {"preferences": {"communication": {"milDataSharing": None}}}}},
        ),
    )
    client = make_client(session)

    assert await client.async_get_vehicle_preferences("VIN") is None
    assert await client.async_get_vehicle_preferences("VIN") is None
    assert await client.async_get_vehicle_preferences("VIN") is None
    assert await client.async_get_vehicle_preferences("VIN") is None


@pytest.mark.asyncio
async def test_update_vehicle_preferences_sends_complete_snapshot_with_nulls() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {"data": {"updateVehiclePreferences": {"success": True}}},
        )
    )
    preferences = VehiclePreferences(
        enabled=True,
        text=False,
        phone=None,
        email=True,
    )

    result = await make_client(
        session,
        read_only=False,
    ).async_update_vehicle_preferences("JN1TESTVIN", preferences)

    assert result is True
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "UpdateVehiclePreferences"
    assert payload["variables"] == {
        "vin": "JN1TESTVIN",
        "communication": {
            "milDataSharing": {
                "enabled": True,
                "text": False,
                "phone": None,
                "email": True,
            }
        },
    }
    query = cast(str, payload["query"])
    assert "$communication: UpdateVehiclePreferencesCommunicationInput!" in query
    assert "... on ResponseStatus { success }" in query
    assert "... on GeneralError { message }" in query


@pytest.mark.asyncio
async def test_update_vehicle_preferences_respects_read_only_mode() -> None:
    session = FakeSession()
    preferences = VehiclePreferences(None, None, None, None)

    with pytest.raises(ReadOnlyError):
        await make_client(session).async_update_vehicle_preferences("VIN", preferences)

    assert session.calls == []


@pytest.mark.asyncio
async def test_update_vehicle_preferences_raises_server_message() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "updateVehiclePreferences": {
                        "__typename": "GeneralError",
                        "message": "Rejected",
                    }
                }
            },
        )
    )
    preferences = VehiclePreferences(True, False, None, None)

    with pytest.raises(ResponseError, match="Rejected"):
        await make_client(
            session,
            read_only=False,
        ).async_update_vehicle_preferences("VIN", preferences)


def vehicle_subscription_product_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "__typename": "VehicleSubscriptionProduct",
        "productId": "product-1",
        "marketingName": "Premium",
        "description": "Connected services",
        "services": ["REMOTE_ENGINE"],
    }
    payload.update(overrides)
    return payload


def vehicle_subscription_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "__typename": "VehicleSubscription",
        "subscriptionId": "subscription-1",
        "subscriptionServiceType": "Paid",
        "purchaseType": "SUBSCRIPTION",
        "productType": "TELEMATICS",
        "nextBillingDate": None,
        "goodwillEndDate": None,
        "goodwillStartDate": None,
        "graceEndDate": None,
        "subscriptionStartDate": "2026-01-01T12:00:00Z",
        "subscriptionEndDate": None,
        "isActive": True,
        "npSubscriptionPrice": None,
        "product": vehicle_subscription_product_payload(),
        "pendingOrder": None,
    }
    payload.update(overrides)
    return payload


@pytest.mark.asyncio
async def test_get_vehicle_subscriptions_preserves_wire_values_and_exact_query() -> None:
    subscription = vehicle_subscription_payload(
        subscriptionServiceType="Paid",
        nextBillingDate="2027-02-03T04:05:06Z",
        goodwillEndDate="2027-01-01T00:00:00+00:00",
        goodwillStartDate="2026-12-01T00:00:00-08:00",
        graceEndDate=None,
        subscriptionStartDate="2099-01-01T12:00:00+05:30",
        isActive=False,
        npSubscriptionPrice=" $12.99 ",
        product=vehicle_subscription_product_payload(services=[None, "REMOTE_ENGINE"]),
        pendingOrder={
            "__typename": "VehicleSubscriptionPendingOrder",
            "pendingOrderId": "pending-1",
            "packageName": "Different package",
            "activationDate": None,
        },
    )
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "__typename": "BaseConnectedVehicle",
                        "capabilities": {
                            "__typename": "VehicleCapability",
                            "subscriptions": [None, subscription],
                        },
                    }
                }
            },
        )
    )

    result = await make_client(session).async_get_vehicle_subscriptions("JN1TESTVIN")

    assert result == VehicleSubscriptions(
        vin="JN1TESTVIN",
        subscriptions=(
            None,
            VehicleSubscription(
                subscription_id="subscription-1",
                subscription_service_type="Paid",
                purchase_type=PurchaseType.SUBSCRIPTION,
                product_type=ProductType.TELEMATICS,
                next_billing_date=datetime.fromisoformat("2027-02-03T04:05:06+00:00"),
                goodwill_end_date=datetime.fromisoformat("2027-01-01T00:00:00+00:00"),
                goodwill_start_date=datetime.fromisoformat("2026-12-01T00:00:00-08:00"),
                grace_end_date=None,
                subscription_start_date=datetime.fromisoformat("2099-01-01T12:00:00+05:30"),
                subscription_end_date=None,
                is_active=False,
                np_subscription_price=" $12.99 ",
                product=VehicleSubscriptionProduct(
                    product_id="product-1",
                    marketing_name="Premium",
                    description="Connected services",
                    services=(None, "REMOTE_ENGINE"),
                ),
                pending_order=VehicleSubscriptionPendingOrder(
                    pending_order_id="pending-1",
                    package_name="Different package",
                    activation_date=None,
                ),
            ),
        ),
    )
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "VehicleSubscriptions"
    assert payload["variables"] == {"vin": "JN1TESTVIN"}
    query = cast(str, payload["query"])
    assert hashlib.sha256(query.encode()).hexdigest() == (
        "f73083b80399d14527938d7dfd92db232b5376ea2d36d9bc481e561bae67f566"
    )


@pytest.mark.asyncio
async def test_get_vehicle_subscriptions_distinguishes_nullable_response_branches() -> None:
    session = FakeSession(
        FakeResponse(200, {"data": {"vehicle": None}}),
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "__typename": "BaseVehicle",
                        "capabilities": None,
                    }
                }
            },
        ),
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "__typename": "BaseVehicle",
                        "capabilities": {
                            "__typename": "VehicleCapability",
                            "subscriptions": [],
                        },
                    }
                }
            },
        ),
    )
    client = make_client(session)

    assert await client.async_get_vehicle_subscriptions("VIN") is None
    assert await client.async_get_vehicle_subscriptions("VIN") == VehicleSubscriptions(
        vin="VIN",
        subscriptions=None,
    )
    assert await client.async_get_vehicle_subscriptions("VIN") == VehicleSubscriptions(
        vin="VIN",
        subscriptions=(),
    )


@pytest.mark.asyncio
async def test_get_vehicle_subscriptions_preserves_novel_enums_nulls_and_order() -> None:
    first = vehicle_subscription_payload(
        subscriptionId="duplicate",
        purchaseType="LOYALTY",
        productType="FUTURE_PRODUCT",
        isActive=None,
        npSubscriptionPrice=None,
    )
    second = vehicle_subscription_payload(
        subscriptionId="duplicate",
        purchaseType=None,
        productType=None,
        isActive=False,
        npSubscriptionPrice="",
    )
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "__typename": "BaseVehicle",
                        "capabilities": {
                            "__typename": "VehicleCapability",
                            "subscriptions": [first, second],
                        },
                    }
                }
            },
        )
    )

    result = await make_client(session).async_get_vehicle_subscriptions("VIN")

    assert result is not None
    assert result.subscriptions is not None
    first_result, second_result = result.subscriptions
    assert first_result is not None
    assert first_result.purchase_type == "LOYALTY"
    assert not isinstance(first_result.purchase_type, PurchaseType)
    assert first_result.product_type == "FUTURE_PRODUCT"
    assert not isinstance(first_result.product_type, ProductType)
    assert first_result.is_active is None
    assert first_result.np_subscription_price is None
    assert second_result is not None
    assert second_result.subscription_id == first_result.subscription_id
    assert second_result.purchase_type is None
    assert second_result.product_type is None
    assert second_result.is_active is False
    assert second_result.np_subscription_price == ""


@pytest.mark.parametrize(
    ("subscriptions", "match"),
    [
        (None, r"subscriptions is not a list"),
        ([vehicle_subscription_payload(subscriptionId=None)], r"subscriptionId is not a string"),
        ([vehicle_subscription_payload(product=None)], r"product is not an object"),
        (
            [
                vehicle_subscription_payload(
                    product=vehicle_subscription_product_payload(services=None)
                )
            ],
            r"services is not a list",
        ),
        (
            [vehicle_subscription_payload(subscriptionStartDate="2026-01-01T12:00:00")],
            r"subscriptionStartDate is not an ISO-8601 date-time with an offset",
        ),
        (
            [vehicle_subscription_payload(nextBillingDate="not-a-date")],
            r"nextBillingDate is not an ISO-8601 date-time with an offset",
        ),
        ([vehicle_subscription_payload(isActive="true")], r"isActive is not a boolean"),
        (
            [
                vehicle_subscription_payload(
                    product=vehicle_subscription_product_payload(services=[1])
                )
            ],
            r"services\[0\] is not a string",
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_vehicle_subscriptions_rejects_contract_violations(
    subscriptions: object,
    match: str,
) -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "__typename": "BaseVehicle",
                        "capabilities": {
                            "__typename": "VehicleCapability",
                            "subscriptions": subscriptions,
                        },
                    }
                }
            },
        )
    )

    with pytest.raises(ResponseError, match=match):
        await make_client(session).async_get_vehicle_subscriptions("VIN")


@pytest.mark.asyncio
async def test_get_vehicle_capabilities_parses_service_accessories_contract() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "capabilities": {
                            "telematicsProgram": "NISSAN_CONNECT",
                            "status": "ENROLLED",
                            "serviceCapability": [
                                {
                                    "type": "CLIMATE_CONTROL",
                                    "enabled": True,
                                    "subscribed": True,
                                }
                            ],
                            "accessoriesDetails": {
                                "seatHeater": {
                                    "enabled": True,
                                    "accessories": {
                                        "assistantSeat": "HEATING_AND_COOLING",
                                        "driverSeat": "HEATING_AND_COOLING",
                                        "secondCentreSeat": None,
                                        "secondLeftSeat": "HEATING",
                                        "secondRightSeat": "HEATING",
                                        "thirdLeftSeat": None,
                                        "thirdRightSeat": None,
                                    },
                                },
                                "steeringHeat": {"enabled": True},
                                "sunRoof": {"type": "ELECTRIC", "enabled": True},
                                "windowStatus": {"enabled": True},
                                "wayPoint": {"enabled": True, "maxNumber": 5},
                                "hvacTemperatures": {
                                    "unit": "CELSIUS",
                                    "default": 22.0,
                                    "min": 16.0,
                                    "max": 30.0,
                                    "resolution": 0.5,
                                },
                            },
                        }
                    }
                }
            },
        )
    )
    client = make_client(session)

    capabilities = await client.async_get_vehicle_capabilities(
        "JN1TESTVIN",
        temperature_unit=TemperatureUnit.CELSIUS,
    )

    assert capabilities.telematics_program == "NISSAN_CONNECT"
    assert capabilities.enrollment_status == "ENROLLED"
    assert len(capabilities.services) == 1
    assert capabilities.services[0].type == "CLIMATE_CONTROL"
    assert capabilities.accessories_details is not None

    accessories = capabilities.accessories_details
    assert accessories.seat_heater is not None
    assert accessories.seat_heater.enabled is True
    assert accessories.seat_heater.accessories is not None
    seats = accessories.seat_heater.accessories
    assert seats.assistant_seat == "HEATING_AND_COOLING"
    assert seats.driver_seat == "HEATING_AND_COOLING"
    assert seats.second_centre_seat is None
    assert seats.second_left_seat == "HEATING"
    assert seats.second_right_seat == "HEATING"
    assert seats.third_left_seat is None
    assert seats.third_right_seat is None

    assert accessories.steering_heat is not None
    assert accessories.steering_heat.enabled is True
    assert accessories.sun_roof is not None
    assert accessories.sun_roof.type == "ELECTRIC"
    assert accessories.sun_roof.enabled is True
    assert accessories.window_status is not None
    assert accessories.window_status.enabled is True
    assert accessories.way_point is not None
    assert accessories.way_point.enabled is True
    assert accessories.way_point.max_number == 5
    assert accessories.hvac_temperatures is not None
    assert accessories.hvac_temperatures.unit == "CELSIUS"
    assert accessories.hvac_temperatures.default == 22.0
    assert accessories.hvac_temperatures.minimum == 16.0
    assert accessories.hvac_temperatures.maximum == 30.0
    assert accessories.hvac_temperatures.resolution == 0.5

    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "VehicleCapabilities"
    assert payload["variables"] == {"vin": "JN1TESTVIN", "unit": "CELSIUS"}
    assert "accessoriesDetails" in cast(str, payload["query"])


@pytest.mark.asyncio
async def test_get_charge_config_parses_both_limits() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "chargeConfig": {
                            "limits": {
                                "notification": {"percent": 25},
                                "charge": {"percent": 80},
                            }
                        }
                    }
                }
            },
        )
    )
    client = make_client(session)

    config = await client.async_get_charge_config("JN1TESTVIN")

    assert config is not None
    assert config.charge_limit_percent == 80
    assert config.notification_threshold_percent == 25
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "ChargeConfig"
    assert payload["variables"] == {"vin": "JN1TESTVIN"}


@pytest.mark.asyncio
async def test_get_v2l_status_parses_state_and_percentage_levels() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "v2lStatus": {
                            "state": "OUTSIDE_ON",
                            "chargeLimitationLevel": 35,
                            "chargeMinimumLimitationLevel": 10.5,
                        }
                    }
                }
            },
        )
    )
    client = make_client(session)

    status = await client.async_get_v2l_status("JN1TESTVIN")

    assert status == V2LStatus(
        state=V2LState.OUTSIDE_ON,
        charge_limit_percent=35.0,
        minimum_charge_limit_percent=10.5,
    )
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "V2lStatus"
    assert payload["variables"] == {"vin": "JN1TESTVIN"}
    assert "chargeMinimumLimitationLevel" in cast(str, payload["query"])


@pytest.mark.asyncio
async def test_get_v2l_status_preserves_nulls_and_unknown_state() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "v2lStatus": {
                            "state": "FUTURE_STATE",
                            "chargeLimitationLevel": None,
                            "chargeMinimumLimitationLevel": None,
                        }
                    }
                }
            },
        )
    )
    client = make_client(session)

    status = await client.async_get_v2l_status("JN1TESTVIN")

    assert status == V2LStatus(
        state=V2LState.UNKNOWN_VALUE,
        charge_limit_percent=None,
        minimum_charge_limit_percent=None,
    )


@pytest.mark.asyncio
async def test_get_charge_history_parses_all_service_fields_and_units() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "chargeHistory": {
                            "charges": [
                                {
                                    "start": "2026-07-01T08:15:00Z",
                                    "end": "2026-07-01T09:45:00Z",
                                    "duration": "PT1H30M",
                                    "recoveredEnergy": 31.25,
                                }
                            ],
                            "chargeSummaries": [
                                {
                                    "day": 1,
                                    "month": 7,
                                    "year": 2026,
                                    "numberOfChargeSessions": 2,
                                    "totalEnergyRecovered": 44.5,
                                    "totalDuration": 135,
                                    "numberOfErrors": 1,
                                    "userId": "driver-1",
                                    "roleType": "PRIMARY",
                                }
                            ],
                        }
                    }
                }
            },
        )
    )
    client = make_client(session)

    history = await client.async_get_charge_history(
        "JN1TESTVIN",
        ChargeHistoryAggregator.DAILY,
    )

    assert history is not None
    assert len(history.charges) == 1
    charge = history.charges[0]
    assert charge.start is not None
    assert charge.start.isoformat() == "2026-07-01T08:15:00+00:00"
    assert charge.end is not None
    assert charge.end.isoformat() == "2026-07-01T09:45:00+00:00"
    assert charge.duration == "PT1H30M"
    assert charge.recovered_energy_kwh == 31.25

    assert len(history.charge_summaries) == 1
    summary = history.charge_summaries[0]
    assert summary.day == 1
    assert summary.month == 7
    assert summary.year == 2026
    assert summary.number_of_charge_sessions == 2
    assert summary.total_energy_recovered_kwh == 44.5
    assert summary.total_duration_minutes == 135
    assert summary.number_of_errors == 1
    assert summary.user_id == "driver-1"
    assert summary.role_type == "PRIMARY"

    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "VehicleChargeHistory"
    assert payload["variables"] == {
        "vin": "JN1TESTVIN",
        "aggregator": "DAILY",
    }


@pytest.mark.asyncio
async def test_get_climate_schedules_parses_accessories_and_delayed_schedule() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "climateSchedules": [
                            {
                                "id": "schedule-1",
                                "state": "ON",
                                "startDateTime": "2026-08-01T07:30:00Z",
                                "weekDays": ["MO", "WE"],
                                "temperature": {
                                    "value": 21.5,
                                    "unit": "CELSIUS",
                                },
                            }
                        ],
                        "climateSchedulesAccessories": {
                            "defrostAndDeicerState": "ON",
                            "steeringWheelHeaterState": "OFF",
                            "seatsClimate": {
                                "frontDriverState": "HEAT",
                                "frontPassengerState": "OFF",
                                "rearLeftPassengerState": "COOL",
                                "rearRightPassengerState": None,
                                "rearCenterPassengerState": None,
                                "thirdLeftState": None,
                                "thirdRightState": None,
                            },
                        },
                        "delayedClimateSchedule": {"startDateTime": "2026-08-01T08:15:00Z"},
                    }
                }
            },
        )
    )
    client = make_client(session)

    result = await client.async_get_climate_schedules(
        "JN1TESTVIN",
        temperature_unit=TemperatureUnit.CELSIUS,
    )

    assert len(result.schedules) == 1
    schedule = result.schedules[0]
    assert schedule.id == "schedule-1"
    assert schedule.state == "ON"
    assert schedule.start_date_time.isoformat() == "2026-08-01T07:30:00+00:00"
    assert tuple(day.value for day in schedule.week_days) == ("MO", "WE")
    assert schedule.temperature.value == 21.5
    assert schedule.temperature.unit == "CELSIUS"

    assert result.accessories is not None
    assert result.accessories.defrost_and_deicer is True
    assert result.accessories.steering_wheel_heater is False
    assert result.accessories.seats is not None
    assert result.accessories.seats.front_driver is SeatClimateOption.HEAT
    assert result.accessories.seats.front_passenger is SeatClimateOption.OFF
    assert result.accessories.seats.rear_left is SeatClimateOption.COOL
    assert result.accessories.seats.rear_right is None
    assert result.accessories.seats.rear_center is None
    assert result.accessories.seats.third_left is None
    assert result.accessories.seats.third_right is None

    assert result.delayed_schedule is not None
    assert result.delayed_schedule.start_date_time is not None
    assert result.delayed_schedule.start_date_time.isoformat() == "2026-08-01T08:15:00+00:00"

    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "VehicleClimateSchedules"
    assert payload["variables"] == {
        "vin": "JN1TESTVIN",
        "temperatureUnit": "CELSIUS",
    }


@pytest.mark.asyncio
async def test_graphql_keeps_partial_vehicle_data() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "__typename": "ElectricAVK2Vehicle",
                        "batteryStatus": {"level": 11},
                    }
                },
                "errors": [{"message": "An unrelated field could not be resolved"}],
            },
        )
    )
    client = make_client(session)

    status = await client.async_get_vehicle_status("JN1TESTVIN")

    assert status.battery is not None
    assert status.battery.level == 11


@pytest.mark.asyncio
async def test_graphql_raises_operation_error_when_all_data_is_null() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {"startClimate": None},
                "errors": [{"message": "Unauthorized field or type"}],
            },
        )
    )
    client = make_client(session, read_only=False)

    with pytest.raises(GraphQLError) as raised:
        await client.async_start_climate(
            "JN1TESTVIN",
            ClimateSettings(72.0, TemperatureUnit.FAHRENHEIT),
        )

    assert raised.value.messages == ("Unauthorized field or type",)


@pytest.mark.asyncio
async def test_graphql_omits_id_token_header_when_not_issued() -> None:
    session = FakeSession(FakeResponse(200, {"data": {"vehicles": []}}))
    client = make_client(session, tokens=Tokens("access-token", "refresh-token"))

    vehicles = await client.async_get_vehicles()

    assert vehicles == ()
    headers = cast(Mapping[str, str], session.calls[0]["headers"])
    assert "id-token" not in headers


@pytest.mark.asyncio
async def test_read_only_blocks_commands_before_network_request() -> None:
    session = FakeSession()
    client = make_client(session)

    with pytest.raises(ReadOnlyError):
        await client.async_start_climate(
            "JN1TESTVIN",
            ClimateSettings(72.0, TemperatureUnit.FAHRENHEIT),
        )

    assert session.calls == []


@pytest.mark.asyncio
async def test_set_charge_notification_threshold_respects_read_only_mode() -> None:
    session = FakeSession()
    client = make_client(session)

    with pytest.raises(ReadOnlyError):
        await client.async_set_charge_notification_threshold("JN1TESTVIN", 25)

    assert session.calls == []


@pytest.mark.asyncio
async def test_set_charge_notification_threshold_returns_request() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {"data": {"setChargeNotificationThreshold": {"serviceRequestId": "request-456"}}},
        )
    )
    client = make_client(session, read_only=False)

    request = await client.async_set_charge_notification_threshold("JN1TESTVIN", 25)

    assert request == ServiceRequest(
        "request-456",
        ServiceRequestKind.CHARGE_CONFIGURATION,
    )
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "SetNotificationLimit"
    assert payload["variables"] == {"vin": "JN1TESTVIN", "percent": 25}


@pytest.mark.asyncio
async def test_set_v2l_minimum_battery_level_respects_read_only_mode() -> None:
    session = FakeSession()
    client = make_client(session)

    with pytest.raises(ReadOnlyError):
        await client.async_set_v2l_minimum_battery_charge_level("JN1TESTVIN", 30)

    assert session.calls == []


@pytest.mark.asyncio
async def test_set_v2l_minimum_battery_level_returns_request() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {"data": {"setV2L": {"serviceRequestId": "request-v2l"}}},
        )
    )
    client = make_client(session, read_only=False)

    request = await client.async_set_v2l_minimum_battery_charge_level(
        "JN1TESTVIN",
        30,
    )

    assert request == ServiceRequest("request-v2l", ServiceRequestKind.V2L)
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "SetV2L"
    assert payload["variables"] == {
        "vin": "JN1TESTVIN",
        "input": {"minimumBatteryChargeLevel": 30},
    }


@pytest.mark.asyncio
async def test_start_climate_serializes_accessories_and_returns_request() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "startClimate": {
                        "serviceRequestId": "request-123",
                        "additionalData": {
                            "__typename": "SetClimateDefaultsResponse",
                            "success": True,
                        },
                    }
                }
            },
        )
    )
    client = make_client(session, read_only=False)

    request = await client.async_start_climate(
        "JN1TESTVIN",
        ClimateSettings(
            72.0,
            TemperatureUnit.FAHRENHEIT,
            ClimateParameters(steering_wheel_heater=True, defrost_and_deicer=False),
        ),
        set_as_default=True,
    )

    assert request == ServiceRequest(
        "request-123",
        ServiceRequestKind.CLIMATE,
        climate_defaults_success=True,
    )
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "StartClimate"
    assert "... on SetClimateDefaultsResponse { success }" in cast(str, payload["query"])
    assert "... on SetClimateDefaultsError { message }" in cast(str, payload["query"])
    assert payload["variables"] == {
        "vin": "JN1TESTVIN",
        "climate": {"unit": "FAHRENHEIT", "temperatureValue": 72.0},
        "parameters": {
            "steeringWheelHeaterState": "ON",
            "defrostAndDeicerState": "OFF",
        },
        "setAsDefault": True,
    }


@pytest.mark.asyncio
async def test_adjust_climate_returns_climate_defaults_error() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "adjustClimate": {
                        "serviceRequestId": "request-adjust",
                        "additionalData": {
                            "__typename": "SetClimateDefaultsError",
                            "message": "Defaults could not be saved",
                        },
                    }
                }
            },
        )
    )
    client = make_client(session, read_only=False)

    request = await client.async_adjust_climate(
        "JN1TESTVIN",
        ClimateSettings(22.0, TemperatureUnit.CELSIUS),
        set_as_default=True,
    )

    assert request == ServiceRequest(
        "request-adjust",
        ServiceRequestKind.CLIMATE,
        climate_defaults_error_message="Defaults could not be saved",
    )
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "AdjustClimate"
    query = cast(str, payload["query"])
    assert "... on SetClimateDefaultsResponse { success }" in query
    assert "... on SetClimateDefaultsError { message }" in query


@pytest.mark.asyncio
async def test_start_engine_returns_climate_defaults_result() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "engineStart": {
                        "serviceRequestId": "request-engine",
                        "additionalData": {
                            "__typename": "SetClimateDefaultsResponse",
                            "success": False,
                        },
                    }
                }
            },
        )
    )
    client = make_client(session, read_only=False)

    request = await client.async_start_engine(
        "JN1TESTVIN",
        climate=ClimateSettings(70.0, TemperatureUnit.FAHRENHEIT),
        set_as_default=True,
    )

    assert request == ServiceRequest(
        "request-engine",
        ServiceRequestKind.ENGINE,
        climate_defaults_success=False,
    )
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "EngineStart"
    query = cast(str, payload["query"])
    assert "... on SetClimateDefaultsResponse { success }" in query
    assert "... on SetClimateDefaultsError { message }" in query


@pytest.mark.asyncio
async def test_request_status_check_is_allowed_in_read_only_mode() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {"data": {"checkRemoteClimateRequest": {"status": "PENDING"}}},
        )
    )
    client = make_client(session)

    result = await client.async_check_service_request(
        "JN1TESTVIN",
        ServiceRequest("request-123", ServiceRequestKind.CLIMATE),
    )

    assert result.status.value == "PENDING"


def test_service_request_result_status_properties_cover_all_known_statuses() -> None:
    successful = {
        ServiceRequestStatus.SUCCESS,
        ServiceRequestStatus.SUCCESS_EXECUTION_CONFIRMED,
        ServiceRequestStatus.CANCELLATION_SUCCESS,
        ServiceRequestStatus.CANCEL_UPDATE_SUCCESS,
        ServiceRequestStatus.UPDATE_SUCCESS,
    }
    failed = {
        ServiceRequestStatus.FAILED,
        ServiceRequestStatus.CANCELLATION_FAILED,
        ServiceRequestStatus.CANCEL_UPDATE_FAILED,
        ServiceRequestStatus.UPDATE_FAILED,
    }

    for status in ServiceRequestStatus:
        result = ServiceRequestResult(status)

        assert result.is_terminal is (status in successful | failed)
        assert result.is_success is (status in successful)

    pending_without_status = ServiceRequestResult(None)
    assert pending_without_status.is_terminal is False
    assert pending_without_status.is_success is False


@pytest.mark.asyncio
async def test_wait_for_service_request_checks_immediately_and_sleeps_between_checks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = FakeSession(
        FakeResponse(200, {"data": {"checkRemoteClimateRequest": {"status": "PENDING"}}}),
        FakeResponse(200, {"data": {"checkRemoteClimateRequest": {"status": "SENT"}}}),
        FakeResponse(200, {"data": {"checkRemoteClimateRequest": {"status": "SUCCESS"}}}),
    )
    client = make_client(session)
    sleep_calls: list[float] = []

    async def fake_sleep(delay: float) -> None:
        sleep_calls.append(delay)
        assert len(session.calls) == len(sleep_calls)

    monkeypatch.setattr("pynissan.client.asyncio.sleep", fake_sleep)

    result = await client.async_wait_for_service_request(
        "JN1TESTVIN",
        ServiceRequest("request-123", ServiceRequestKind.CLIMATE),
        poll_interval_seconds=2.5,
    )

    assert result.status is ServiceRequestStatus.SUCCESS
    assert result.is_terminal is True
    assert result.is_success is True
    assert sleep_calls == [2.5, 2.5]
    assert len(session.calls) == 3


@pytest.mark.asyncio
async def test_wait_for_service_request_returns_terminal_failure_without_sleep(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = FakeSession(
        FakeResponse(200, {"data": {"checkEngineServiceRequest": {"status": "FAILED"}}}),
    )
    client = make_client(session)

    async def fail_if_called(delay: float) -> None:
        raise AssertionError(f"unexpected sleep for {delay} seconds")

    monkeypatch.setattr("pynissan.client.asyncio.sleep", fail_if_called)

    result = await client.async_wait_for_service_request(
        "JN1TESTVIN",
        ServiceRequest("request-engine", ServiceRequestKind.ENGINE),
    )

    assert result.status is ServiceRequestStatus.FAILED
    assert result.is_terminal is True
    assert result.is_success is False
    assert len(session.calls) == 1


@pytest.mark.asyncio
async def test_route_waiter_continues_through_unknown_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {"data": {"checkRouteServiceRequest": {"status": "UNKNOWN__"}}},
        ),
        FakeResponse(
            200,
            {"data": {"checkRouteServiceRequest": {"status": "SUCCESS"}}},
        ),
    )
    client = make_client(session)
    sleep_calls: list[float] = []

    async def fake_sleep(delay: float) -> None:
        sleep_calls.append(delay)

    monkeypatch.setattr("pynissan.client.asyncio.sleep", fake_sleep)

    result = await client.async_wait_for_service_request(
        "JN1TESTVIN",
        ServiceRequest("route-request", ServiceRequestKind.ROUTE),
        poll_interval_seconds=1.5,
    )

    assert result.status is ServiceRequestStatus.SUCCESS
    assert sleep_calls == [1.5]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("poll_interval_seconds", "timeout_seconds"),
    [
        (0.0, 210.0),
        (-1.0, 210.0),
        (float("nan"), 210.0),
        (float("inf"), 210.0),
        (3.0, 0.0),
        (3.0, -1.0),
        (3.0, float("nan")),
        (3.0, float("inf")),
    ],
)
async def test_wait_for_service_request_validates_timings_before_network(
    poll_interval_seconds: float,
    timeout_seconds: float,
) -> None:
    session = FakeSession()
    client = make_client(session)

    with pytest.raises(ValueError, match="positive finite number"):
        await client.async_wait_for_service_request(
            "JN1TESTVIN",
            ServiceRequest("request-123", ServiceRequestKind.CLIMATE),
            poll_interval_seconds=poll_interval_seconds,
            timeout_seconds=timeout_seconds,
        )

    assert session.calls == []


@pytest.mark.asyncio
async def test_v2l_request_status_uses_matching_check_operation() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {"data": {"checkV2LServiceRequest": {"status": "SUCCESS"}}},
        )
    )
    client = make_client(session)

    result = await client.async_check_service_request(
        "JN1TESTVIN",
        ServiceRequest("request-v2l", ServiceRequestKind.V2L),
    )

    assert result.status.value == "SUCCESS"
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "CheckV2LServiceRequest"
    assert payload["variables"] == {
        "vin": "JN1TESTVIN",
        "serviceRequestId": "request-v2l",
    }


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


@pytest.mark.asyncio
async def test_navigation_unknown_input_enums_are_rejected_before_network() -> None:
    session = FakeSession()
    client = make_client(session, read_only=False)

    with pytest.raises(ValueError, match="UNKNOWN_VALUE"):
        await client.async_get_vehicle_routes_history(
            "JN1TESTVIN",
            status=RouteStatus.UNKNOWN_VALUE,
        )
    with pytest.raises(ValueError, match="UNKNOWN_VALUE"):
        await client.async_get_vehicle_ev_waypoints(
            "JN1TESTVIN",
            (),
            (PlugConnectorType.UNKNOWN_VALUE,),
        )
    with pytest.raises(ValueError, match="UNKNOWN_VALUE"):
        await client.async_send_point_of_interest(
            "JN1TESTVIN",
            PointOfInterestFolder.UNKNOWN_VALUE,
            DestinationInput("Home", CoordinateInput(32.7, -117.1)),
        )

    assert session.calls == []


@pytest.mark.asyncio
async def test_get_ota_update_parses_exact_service_contract() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "otaUpdate": {
                            "campaignOperationId": "campaign-1",
                            "status": {
                                "status": "READY_FOR_ACTIVATION",
                                "activationTimerValue": "2026-08-01T10:00:00Z",
                                "progress": 82,
                                "countDownTimeStart": None,
                                "countDownDelay": 30,
                            },
                            "campaignDescription": {
                                "globalReleaseNote": "Release notes",
                                "downloadDisclaimer": None,
                                "activationDisclaimer": "Park the vehicle",
                                "activationEstimatedTime": "20 minutes",
                            },
                            "batteryLevel": {
                                "activationEnabled": True,
                                "stateOfCharge": 78.5,
                                "activationMinimumBatteryLevel": 20,
                            },
                            "size": 1048576,
                            "lastChecked": "2026-08-01T09:30:00-07:00",
                            "activationTimerValue": None,
                        }
                    }
                }
            },
        ),
    )

    result = await make_client(session).async_get_ota_update("JN1TESTVIN")

    assert result == OtaUpdate(
        campaign_operation_id="campaign-1",
        status=OtaUpdateStatus(
            status=OtaUpdateState.READY_FOR_ACTIVATION,
            activation_timer_value=datetime.fromisoformat("2026-08-01T10:00:00+00:00"),
            progress=82,
            count_down_time_start=None,
            count_down_delay=30,
        ),
        campaign_description=OtaCampaignDescription(
            global_release_note="Release notes",
            download_disclaimer=None,
            activation_disclaimer="Park the vehicle",
            activation_estimated_time="20 minutes",
        ),
        battery_level=OtaBatteryLevel(
            activation_enabled=True,
            state_of_charge=78.5,
            activation_minimum_battery_level=20.0,
        ),
        size=1048576,
        last_checked=datetime.fromisoformat("2026-08-01T09:30:00-07:00"),
        activation_timer_value=None,
    )
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "OtaUpdate"
    assert payload["variables"] == {"vin": "JN1TESTVIN"}


@pytest.mark.asyncio
async def test_ota_reads_preserve_branch_absence_and_unknown_state() -> None:
    session = FakeSession(
        FakeResponse(200, {"data": {"vehicle": {}}}),
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "otaUpdateProgress": {
                            "status": "FUTURE_STATE",
                            "percentage": None,
                            "errorInfo": [
                                {
                                    "errorCode": "E1",
                                    "errorMessage": "Retry later",
                                    "isRetryable": True,
                                }
                            ],
                        }
                    }
                }
            },
        ),
    )
    client = make_client(session)

    update = await client.async_get_ota_update("JN1TESTVIN")
    progress = await client.async_get_ota_update_progress("JN1TESTVIN", "campaign-1")

    assert update is None
    assert progress == OtaUpdateProgress(
        status=OtaUpdateState.UNKNOWN_VALUE,
        percentage=None,
        error_info=(OtaUpdateErrorInfo("E1", "Retry later", True),),
    )
    payload = cast(Mapping[str, object], session.calls[1]["json"])
    assert payload["variables"] == {
        "campaignOperationId": "campaign-1",
        "vin": "JN1TESTVIN",
    }


@pytest.mark.asyncio
async def test_get_notification_preferences_preserves_nullable_items() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "notificationPreferences": [
                            None,
                            {
                                "notificationCategory": "FUTURE_CATEGORY",
                                "notificationType": [
                                    None,
                                    {
                                        "destination": "FUTURE_DESTINATION",
                                        "optIn": True,
                                    },
                                ],
                            },
                        ]
                    }
                }
            },
        ),
    )

    result = await make_client(session).async_get_notification_preferences("JN1TESTVIN")

    assert result == (
        None,
        NotificationPreference(
            notification_category=NotificationCategory.UNKNOWN_VALUE,
            notification_type=(
                None,
                NotificationTypePreference(
                    NotificationDestination.UNKNOWN_VALUE,
                    True,
                ),
            ),
        ),
    )


@pytest.mark.asyncio
async def test_set_notification_preferences_serializes_and_returns_server_state() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "setNotificationPreferences": {
                        "notificationPreferences": [
                            {
                                "notificationCategory": "ENGINE",
                                "notificationType": [{"destination": "PUSH", "optIn": False}],
                            }
                        ]
                    }
                }
            },
        ),
    )
    client = make_client(session, read_only=False)

    result = await client.async_set_notification_preferences(
        "JN1TESTVIN",
        (
            None,
            NotificationPreferenceInput(
                NotificationCategory.ENGINE,
                (None, NotificationTypeInput(NotificationDestination.PUSH, False)),
            ),
        ),
    )

    assert result == (
        NotificationPreference(
            NotificationCategory.ENGINE,
            (NotificationTypePreference(NotificationDestination.PUSH, False),),
        ),
    )
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["variables"] == {
        "vin": "JN1TESTVIN",
        "preferences": [
            None,
            {
                "notificationCategory": "ENGINE",
                "notificationType": [
                    None,
                    {"destination": "PUSH", "optIn": False},
                ],
            },
        ],
    }


@pytest.mark.asyncio
async def test_ota_commands_serialize_inputs_and_return_service_requests() -> None:
    accepted_fields = (
        "downloadOTAUpdate",
        "activateOTAUpdate",
        "cancelActivationOTAUpdate",
        "scheduleActivationOTAUpdate",
        "updateScheduledActivationOTAUpdate",
        "cancelScheduledActivationOTAUpdate",
    )
    session = FakeSession(
        *(
            FakeResponse(
                200,
                {"data": {field: {"serviceRequestId": f"request-{index}"}}},
            )
            for index, field in enumerate(accepted_fields, start=1)
        )
    )
    client = make_client(session, read_only=False)
    scheduled_date = datetime.fromisoformat("2026-08-05T18:00:00-07:00")

    requests = (
        await client.async_download_ota_update("JN1TESTVIN", "ota-1"),
        await client.async_activate_ota_update("JN1TESTVIN", "ota-1"),
        await client.async_cancel_ota_activation("JN1TESTVIN", "ota-1"),
        await client.async_schedule_ota_activation(
            "JN1TESTVIN",
            "ota-1",
            scheduled_date,
        ),
        await client.async_update_scheduled_ota_activation(
            "JN1TESTVIN",
            "ota-1",
            scheduled_date,
        ),
        await client.async_cancel_scheduled_ota_activation("JN1TESTVIN", "ota-1"),
    )

    assert requests == tuple(
        ServiceRequest(f"request-{index}", ServiceRequestKind.OTA) for index in range(1, 7)
    )
    download_payload = cast(Mapping[str, object], session.calls[0]["json"])
    schedule_payload = cast(Mapping[str, object], session.calls[3]["json"])
    assert download_payload["variables"] == {
        "vin": "JN1TESTVIN",
        "input": {"otaUpdateId": "ota-1"},
    }
    assert schedule_payload["variables"] == {
        "vin": "JN1TESTVIN",
        "input": {
            "otaUpdateId": "ota-1",
            "scheduledDate": "2026-08-05T18:00:00-07:00",
        },
    }


@pytest.mark.asyncio
async def test_download_ota_update_surfaces_operation_in_progress_error() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "downloadOTAUpdate": {
                        "__typename": "OperationInProgressError",
                        "message": "Another operation is active",
                    }
                }
            },
        ),
    )

    with pytest.raises(ResponseError, match="Another operation is active"):
        await make_client(session, read_only=False).async_download_ota_update(
            "JN1TESTVIN",
            "ota-1",
        )


@pytest.mark.asyncio
async def test_data_wipe_preserves_omitted_null_and_enum_inputs() -> None:
    session = FakeSession(
        FakeResponse(200, {"data": {"dataWipe": {"serviceRequestId": "wipe-1"}}}),
        FakeResponse(200, {"data": {"dataWipe": {"serviceRequestId": "wipe-2"}}}),
        FakeResponse(200, {"data": {"dataWipe": {"serviceRequestId": "wipe-3"}}}),
    )
    client = make_client(session, read_only=False)

    omitted = await client.async_wipe_vehicle_data("JN1TESTVIN")
    null = await client.async_wipe_vehicle_data("JN1TESTVIN", data_wipe_type=None)
    tcu = await client.async_wipe_vehicle_data(
        "JN1TESTVIN",
        data_wipe_type=DataWipeType.TCU_WIPE,
    )

    assert omitted == ServiceRequest("wipe-1", ServiceRequestKind.DATA_WIPE)
    assert null == ServiceRequest("wipe-2", ServiceRequestKind.DATA_WIPE)
    assert tcu == ServiceRequest("wipe-3", ServiceRequestKind.DATA_WIPE)
    variables = [
        cast(Mapping[str, object], cast(Mapping[str, object], call["json"])["variables"])
        for call in session.calls
    ]
    assert variables == [
        {"vin": "JN1TESTVIN"},
        {"vin": "JN1TESTVIN", "dataWipeType": None},
        {"vin": "JN1TESTVIN", "dataWipeType": "TCU_WIPE"},
    ]

    with pytest.raises(
        ResponseError,
        match="does not expose a status operation for data_wipe requests",
    ):
        await client.async_check_service_request("JN1TESTVIN", tcu)
    assert len(session.calls) == 3


@pytest.mark.asyncio
async def test_check_ota_service_request_uses_exact_poller() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {"data": {"checkOtaUpdateServiceRequest": {"status": None}}},
        ),
    )
    client = make_client(session)

    result = await client.async_check_service_request(
        "JN1TESTVIN",
        ServiceRequest("ota-request", ServiceRequestKind.OTA),
    )

    assert result == ServiceRequestResult(status=None)
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "CheckOtaUpdateServiceRequest"
    assert payload["variables"] == {
        "vin": "JN1TESTVIN",
        "serviceRequestId": "ota-request",
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "terminal_status",
    ["UPDATE_SUCCESS", "CANCELLATION_SUCCESS"],
)
async def test_wait_for_ota_request_accepts_common_terminal_statuses(
    terminal_status: str,
) -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {"data": {"checkOtaUpdateServiceRequest": {"status": terminal_status}}},
        ),
    )
    client = make_client(session)

    result = await client.async_wait_for_service_request(
        "JN1TESTVIN",
        ServiceRequest("ota-request", ServiceRequestKind.OTA),
        poll_interval_seconds=0.001,
        timeout_seconds=1,
    )

    assert result.status == ServiceRequestStatus(terminal_status)
    assert len(session.calls) == 1


@pytest.mark.asyncio
async def test_ota_and_notification_writes_respect_read_only_mode() -> None:
    session = FakeSession()
    client = make_client(session)

    with pytest.raises(ReadOnlyError):
        await client.async_download_ota_update("JN1TESTVIN", "ota-1")
    with pytest.raises(ReadOnlyError):
        await client.async_wipe_vehicle_data("JN1TESTVIN")
    with pytest.raises(ReadOnlyError):
        await client.async_set_notification_preferences("JN1TESTVIN", ())

    assert session.calls == []


@pytest.mark.asyncio
async def test_ota_and_notification_inputs_reject_invalid_values_before_io() -> None:
    session = FakeSession()
    client = make_client(session, read_only=False)

    with pytest.raises(ValueError, match="UNKNOWN_VALUE"):
        await client.async_wipe_vehicle_data(
            "JN1TESTVIN",
            data_wipe_type=DataWipeType.UNKNOWN_VALUE,
        )
    with pytest.raises(ValueError, match="UTC offset"):
        await client.async_schedule_ota_activation(
            "JN1TESTVIN",
            "ota-1",
            datetime(2026, 8, 5, 18, 0),
        )
    with pytest.raises(ValueError, match="UNKNOWN_VALUE"):
        await client.async_set_notification_preferences(
            "JN1TESTVIN",
            (
                NotificationPreferenceInput(
                    NotificationCategory.UNKNOWN_VALUE,
                    (),
                ),
            ),
        )
    with pytest.raises(ValueError, match="UNKNOWN_VALUE"):
        await client.async_set_notification_preferences(
            "JN1TESTVIN",
            (
                NotificationPreferenceInput(
                    NotificationCategory.ENGINE,
                    (
                        NotificationTypeInput(
                            NotificationDestination.UNKNOWN_VALUE,
                            True,
                        ),
                    ),
                ),
            ),
        )

    assert session.calls == []
