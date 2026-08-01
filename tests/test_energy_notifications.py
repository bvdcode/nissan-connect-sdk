from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from typing import cast

import pytest
from aiohttp import ClientSession

from pynissan import (
    UNSET,
    NissanClient,
    NissanEnergyNotificationPreferences,
    NissanEnergyNotificationPreferencesUpdate,
    ReadOnlyError,
    ResponseError,
    Tokens,
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


TOKENS = Tokens("access-token", "refresh-token", "id-token")
EXPECTED_QUERY_TOKEN_HASHES = {
    "NissanEnergyNotificationPreferences": (
        "5dbb8c7ef7184562f4f3631bdf3df8f5cb515d3f5e536dd0662dddb0921fb813"
    ),
    "UpdateNotificationPreferences": (
        "c7c1f767fc2b0c5486ff4109196190c65022b28b25931de0a3d3c6c7ad189685"
    ),
}


def graphql_response(data: Mapping[str, object]) -> FakeResponse:
    return FakeResponse({"data": dict(data)})


def make_client(session: FakeSession, *, read_only: bool = True) -> NissanClient:
    return NissanClient(
        cast(ClientSession, session),
        read_only=read_only,
        tokens=TOKENS,
    )


def assert_graphql_call(
    session: FakeSession,
    index: int,
    operation_name: str,
    variables: Mapping[str, object],
) -> None:
    payload = session.calls[index].get("json")
    assert isinstance(payload, Mapping)
    assert payload["operationName"] == operation_name
    assert payload["variables"] == variables
    document = payload["query"]
    assert isinstance(document, str)
    tokens = " ".join(re.findall(r"\.\.\.|[_A-Za-z][_0-9A-Za-z]*|[$!():{}\[\]]", document))
    assert (
        hashlib.sha256(tokens.encode()).hexdigest() == EXPECTED_QUERY_TOKEN_HASHES[operation_name]
    )


async def test_get_nissan_energy_notification_preferences_uses_exact_contract() -> None:
    session = FakeSession(
        graphql_response(
            {
                "accountStatus": {
                    "__typename": "EmpAccountStatusResponse",
                    "data": {
                        "__typename": "EmpAccountStatusData",
                        "notificationPreferences": {
                            "__typename": "EmpNotificationPreferencesData",
                            "emailStatus": True,
                            "pushStatus": None,
                            "smsStatus": False,
                        },
                    },
                }
            }
        )
    )

    result = await make_client(session).async_get_nissan_energy_notification_preferences("VIN")

    assert result == NissanEnergyNotificationPreferences(
        email_status=True,
        push_status=None,
        sms_status=False,
    )
    assert_graphql_call(
        session,
        0,
        "NissanEnergyNotificationPreferences",
        {"vin": "VIN"},
    )


async def test_get_nissan_energy_preferences_preserves_nullable_response_chain() -> None:
    session = FakeSession(
        graphql_response({"accountStatus": None}),
        graphql_response(
            {
                "accountStatus": {
                    "__typename": "EmpAccountStatusResponse",
                    "data": None,
                }
            }
        ),
        graphql_response(
            {
                "accountStatus": {
                    "__typename": "EmpAccountStatusResponse",
                    "data": {
                        "__typename": "EmpAccountStatusData",
                        "notificationPreferences": None,
                    },
                }
            }
        ),
    )
    client = make_client(session)

    assert await client.async_get_nissan_energy_notification_preferences("VIN") is None
    assert await client.async_get_nissan_energy_notification_preferences("VIN") is None
    assert await client.async_get_nissan_energy_notification_preferences("VIN") is None


async def test_update_nissan_energy_preferences_preserves_patch_values() -> None:
    session = FakeSession(
        graphql_response(
            {
                "updateNotificationPreferences": {
                    "__typename": "EmpUpdateNotificationPreferencesResponse",
                    "statusCode": "1000",
                    "statusMessage": None,
                    "timestamp": "2026-07-31T18:30:00Z",
                    "data": {
                        "__typename": "EmpNotificationPreferencesData",
                        "emailStatus": True,
                        "pushStatus": None,
                        "smsStatus": False,
                    },
                }
            }
        ),
        graphql_response({"updateNotificationPreferences": None}),
    )
    client = make_client(session, read_only=False)

    result = await client.async_update_nissan_energy_notification_preferences(
        "VIN",
        email_status=True,
        push_status=None,
        sms_status=False,
    )
    null_result = await client.async_update_nissan_energy_notification_preferences(
        "VIN",
        email_status=UNSET,
        push_status=UNSET,
        sms_status=UNSET,
    )

    assert result == NissanEnergyNotificationPreferencesUpdate(
        status_code="1000",
        status_message=None,
        timestamp="2026-07-31T18:30:00Z",
        preferences=NissanEnergyNotificationPreferences(True, None, False),
    )
    assert null_result is None
    assert_graphql_call(
        session,
        0,
        "UpdateNotificationPreferences",
        {
            "config": {
                "vin": "VIN",
                "emailStatus": True,
                "pushStatus": None,
                "smsStatus": False,
            }
        },
    )
    assert_graphql_call(
        session,
        1,
        "UpdateNotificationPreferences",
        {"config": {"vin": "VIN"}},
    )


async def test_update_nissan_energy_preferences_respects_read_only_mode() -> None:
    session = FakeSession()

    with pytest.raises(ReadOnlyError):
        await make_client(session).async_update_nissan_energy_notification_preferences(
            "VIN",
            push_status=True,
        )

    assert session.calls == []


async def test_nissan_energy_preferences_reject_malformed_response_fields() -> None:
    session = FakeSession(
        graphql_response({}),
        graphql_response(
            {
                "accountStatus": {
                    "__typename": "EmpAccountStatusResponse",
                    "data": {
                        "__typename": "EmpAccountStatusData",
                        "notificationPreferences": {
                            "__typename": "EmpNotificationPreferencesData",
                            "emailStatus": "yes",
                        },
                    },
                }
            }
        ),
    )
    client = make_client(session)

    with pytest.raises(ResponseError, match="accountStatus is missing"):
        await client.async_get_nissan_energy_notification_preferences("VIN")
    with pytest.raises(ResponseError, match="emailStatus is not a boolean"):
        await client.async_get_nissan_energy_notification_preferences("VIN")
