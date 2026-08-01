from __future__ import annotations

from collections.abc import Mapping
from typing import cast

import pytest
from aiohttp import ClientSession
from test_client import (
    TOKENS,
    FakeResponse,
    FakeSession,
    make_client,
)

from pynissan import (
    AuthenticationError,
    CameraPosition,
    CameraService,
    Country,
    DistanceUnit,
    EngineOilDrainRange,
    NissanClient,
    RequestProof,
    Tokens,
    VehiclePhoto,
)


def test_request_proof_and_provider_are_mutually_exclusive() -> None:
    async def provider(force_refresh: bool) -> RequestProof:
        return RequestProof("provided-attestation", str(force_refresh))

    with pytest.raises(ValueError, match="cannot be combined"):
        NissanClient(
            cast(ClientSession, FakeSession()),
            request_proof=RequestProof("static-attestation", "device-status"),
            request_proof_provider=provider,
        )


@pytest.mark.asyncio
async def test_application_graphql_uses_application_token_and_request_proof() -> None:
    session = FakeSession(
        FakeResponse(200, {"access_token": "application-access"}),
        FakeResponse(200, {"data": {"validateNissanID": None}}),
    )
    client = NissanClient(
        cast(ClientSession, session),
        oauth_device_id="device-123",
        request_proof=RequestProof("api-attestation", "device-status"),
    )

    assert await client.async_validate_nissan_id("owner@example.test") is None

    token_call, graphql_call = session.calls
    assert token_call["data"] == {
        "client_id": "6wYMOME6Rs4kWVxS4i6b2RUsR4Ma",
        "client_secret": "fWp6esCzsq3vCY6RLf3p_CV_ukAa",
        "scope": "openid device_device-123",
        "grant_type": "client_credentials",
    }
    headers = cast(Mapping[str, str], graphql_call["headers"])
    assert headers["Authorization"] == "Bearer application-access"
    assert headers["X-API-Attestation"] == "api-attestation"
    assert headers["X-Device-Status"] == "device-status"
    assert headers["apollographql-client-name"] == "com.nissan.mynissan:android"
    assert headers["apollographql-client-version"] == "6.9.110"
    assert "id-token" not in headers


@pytest.mark.asyncio
async def test_application_graphql_requires_request_proof_before_network() -> None:
    session = FakeSession()
    client = NissanClient(cast(ClientSession, session))

    with pytest.raises(AuthenticationError, match="requires request proof"):
        await client.async_validate_nissan_id("owner@example.test")

    assert session.calls == []


@pytest.mark.asyncio
async def test_rejected_request_proof_is_refreshed_once() -> None:
    requests: list[bool] = []

    async def provider(force_refresh: bool) -> RequestProof:
        requests.append(force_refresh)
        suffix = "fresh" if force_refresh else "initial"
        return RequestProof(f"attestation-{suffix}", f"status-{suffix}")

    session = FakeSession(
        FakeResponse(200, {"access_token": "application-access"}),
        FakeResponse(403, {"message": "request rejected"}),
        FakeResponse(200, {"data": {"validateNissanID": None}}),
    )
    client = NissanClient(
        cast(ClientSession, session),
        request_proof_provider=provider,
    )

    assert await client.async_validate_nissan_id("owner@example.test") is None

    assert requests == [False, True]
    retry_headers = cast(Mapping[str, str], session.calls[2]["headers"])
    assert retry_headers["X-API-Attestation"] == "attestation-fresh"
    assert retry_headers["X-Device-Status"] == "status-fresh"


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
