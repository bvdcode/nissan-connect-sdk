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
    ClimateParameters,
    ClimateSettings,
    ServiceRequest,
    ServiceRequestKind,
    ServiceRequestResult,
    ServiceRequestStatus,
    TemperatureUnit,
)


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

    monkeypatch.setattr("pynissan._client_base.asyncio.sleep", fake_sleep)

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

    monkeypatch.setattr("pynissan._client_base.asyncio.sleep", fail_if_called)

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

    monkeypatch.setattr("pynissan._client_base.asyncio.sleep", fake_sleep)

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
