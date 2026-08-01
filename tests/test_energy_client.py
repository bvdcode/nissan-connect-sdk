from __future__ import annotations

from collections.abc import Mapping
from typing import cast

import pytest
from aiohttp import ClientSession

from pynissan import (
    EnergyAccountStatus,
    NissanClient,
    ReadOnlyError,
    Tokens,
    V1GNotificationCategory,
    V1GNotificationPreferenceInput,
)


class FakeResponse:
    def __init__(self, payload: Mapping[str, object]) -> None:
        self.status = 200
        self._payload = payload

    async def __aenter__(self) -> FakeResponse:
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def json(self, *, content_type: object = None) -> object:
        return self._payload


class FakeSession:
    def __init__(self, *responses: FakeResponse) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, object]] = []

    def post(self, url: str, **kwargs: object) -> FakeResponse:
        self.calls.append({"url": url, **kwargs})
        if not self.responses:
            raise AssertionError("Unexpected HTTP request")
        return self.responses.pop(0)


def graphql_response(data: Mapping[str, object]) -> FakeResponse:
    return FakeResponse({"data": dict(data)})


def make_client(session: FakeSession, *, read_only: bool = True) -> NissanClient:
    return NissanClient(
        cast(ClientSession, session),
        tokens=Tokens("access-token", "refresh-token", "id-token"),
        read_only=read_only,
    )


async def test_energy_and_v1g_client_wires_exact_operations() -> None:
    session = FakeSession(
        graphql_response({"accountStatus": None}),
        graphql_response({"v1GMonitoredChargingAccountStatus": None}),
        graphql_response({"v1GTokenizedUrl": None}),
        graphql_response({"vehicles": None}),
        graphql_response({"v1GEnrollMonitoredChargingPlan": None}),
        graphql_response({"v1GCancelMonitoredChargingPlan": None}),
        graphql_response({"v1GUpdateNotificationPreferences": None}),
    )
    client = make_client(session, read_only=False)

    assert await client.async_get_energy_account_status("VIN") is None
    assert await client.async_get_v1g_monitored_charging_account_status("VIN") is None
    assert await client.async_get_v1g_tokenized_url("VIN") is None
    assert await client.async_get_vehicles_with_capabilities() is None
    assert (
        await client.async_enroll_v1g_monitored_charging_plan(
            "VIN",
            "ARIYA",
            "2026",
            plan="CUSTOM-PLAN",
        )
        is None
    )
    assert await client.async_cancel_v1g_monitored_charging_plan("VIN") is None
    assert (
        await client.async_update_v1g_notification_preferences(
            "VIN",
            preferences=(
                V1GNotificationPreferenceInput(
                    V1GNotificationCategory.MONTHLY_INSIGHTS,
                    email_status=None,
                    push_status=True,
                ),
                None,
            ),
        )
        is None
    )

    payloads = [call["json"] for call in session.calls]
    assert all(isinstance(payload, Mapping) for payload in payloads)
    assert [payload["operationName"] for payload in payloads] == [
        "AccountStatus",
        "V1GMonitoredChargingAccountStatus",
        "V1GTokenizedUrl",
        "WearableVehicles",
        "V1GEnrollMonitoredChargingPlan",
        "V1GCancelMonitoredChargingPlan",
        "V1GUpdateNotificationPreferences",
    ]
    assert [payload["variables"] for payload in payloads] == [
        {"vin": "VIN"},
        {"vin": "VIN"},
        {"vin": "VIN"},
        {},
        {
            "config": {
                "vin": "VIN",
                "plan": "CUSTOM-PLAN",
                "model": "ARIYA",
                "year": "2026",
            }
        },
        {"config": {"vin": "VIN"}},
        {
            "config": {
                "vin": "VIN",
                "v1GNotificationPreferences": [
                    {
                        "v1GNotificationCategory": "Monthly Insights",
                        "v1GEmailStatus": None,
                        "v1GPushStatus": True,
                    },
                    None,
                ],
            }
        },
    ]


async def test_v1g_mutations_respect_read_only_before_io() -> None:
    session = FakeSession()
    client = make_client(session)

    with pytest.raises(ReadOnlyError):
        await client.async_enroll_v1g_monitored_charging_plan("VIN", "ARIYA", "2026")
    with pytest.raises(ReadOnlyError):
        await client.async_cancel_v1g_monitored_charging_plan("VIN")
    with pytest.raises(ReadOnlyError):
        await client.async_update_v1g_notification_preferences("VIN")

    assert session.calls == []


async def test_energy_account_waiter_matches_service_retry_states() -> None:
    def status_response(status: str | None) -> FakeResponse:
        return graphql_response(
            {
                "accountStatus": {
                    "__typename": "EmpAccountStatusResponse",
                    "data": {
                        "__typename": "EmpAccountStatusData",
                        "status": status,
                    },
                }
            }
        )

    session = FakeSession(
        graphql_response({"accountStatus": None}),
        status_response("ENROLLING"),
        status_response("ACTIVE"),
    )

    result = await make_client(session).async_wait_for_energy_account_status(
        "VIN",
        poll_interval_seconds=0.001,
        timeout_seconds=1,
    )

    assert result is not None
    assert result.data is not None
    assert result.data.status is EnergyAccountStatus.ACTIVE
    assert len(session.calls) == 3


async def test_energy_account_waiter_validates_and_times_out_without_extra_io() -> None:
    invalid_session = FakeSession()
    invalid_client = make_client(invalid_session)

    with pytest.raises(ValueError, match="poll_interval_seconds"):
        await invalid_client.async_wait_for_energy_account_status(
            "VIN",
            poll_interval_seconds=0,
        )
    with pytest.raises(ValueError, match="timeout_seconds"):
        await invalid_client.async_wait_for_energy_account_status(
            "VIN",
            timeout_seconds=float("nan"),
        )
    assert invalid_session.calls == []

    timeout_session = FakeSession(graphql_response({"accountStatus": None}))
    timeout_result = await make_client(timeout_session).async_wait_for_energy_account_status(
        "VIN",
        poll_interval_seconds=1,
        timeout_seconds=0.001,
    )
    assert timeout_result is None
    assert len(timeout_session.calls) == 1
