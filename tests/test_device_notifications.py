from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import cast

import pytest
from aiohttp import ClientSession

from pynissan import (
    MYNISSAN_ANDROID_APP_NAME,
    UNSET,
    DeviceOS,
    InVehicleMessage,
    InVehicleMessageSummary,
    MobileInfoInput,
    MobileInput,
    NissanClient,
    PushNotificationDatabaseError,
    PushNotificationSuccess,
    PushNotificationTokenError,
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
MOBILE_INFO = MobileInfoInput(
    MobileInput(
        device_id="device-id",
        device_os=DeviceOS.ANDROID,
        app_name=MYNISSAN_ANDROID_APP_NAME,
        token="push-token",
    )
)
EXPECTED_QUERY_TOKEN_HASHES = {
    "RegisterPushNotifications": "118a49693d702b093b1f92efb311cd2ecb42c8697a9ff4cb531316d435447642",
    "UnregisterPushNotifications": (
        "367c95b02f2fd00560fc8f1c8d03d16934b8866a2e2451caf5e587deb5d25d30"
    ),
    "RegisterDeviceForPushNotifications": (
        "d356471fbe210816e27877f5985be89b3cdd64921a73251ea6d1712f5973150e"
    ),
    "UnregisterDeviceForPushNotifications": (
        "56021d08614d36b731ef64c70791326b275103eb6b34bcf45ff46719784e8d06"
    ),
    "InVehicleMessages": "7a7ef1869e65662f33a1c19c74e0294faf8d2d39e6ef8dd5a08563e3493bea49",
    "InVehicleMessage": "65fef6d6be6121fd4fc8805b5938703c70a8087e8fd0a701f12d9bf75ffc909c",
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


async def test_legacy_push_mutations_use_exact_contracts_and_nullable_results() -> None:
    session = FakeSession(
        graphql_response({"registerNotifications": True}),
        graphql_response({"registerNotifications": None}),
        graphql_response({"unregisterNotifications": False}),
        graphql_response({"unregisterNotifications": None}),
    )
    client = make_client(session, read_only=False)

    assert (
        await client.async_register_push_notifications(
            "device-id",
            "push-token",
            DeviceOS.ANDROID,
        )
        is True
    )
    assert (
        await client.async_register_push_notifications(
            "device-id",
            "push-token",
            DeviceOS.ANDROID,
        )
        is None
    )
    assert await client.async_unregister_push_notifications("device-id", DeviceOS.IOS) is False
    assert await client.async_unregister_push_notifications("device-id", DeviceOS.IOS) is None

    register_variables = {
        "deviceId": "device-id",
        "token": "push-token",
        "deviceOS": "ANDROID",
    }
    unregister_variables = {"deviceId": "device-id", "deviceOS": "IOS"}
    assert_graphql_call(session, 0, "RegisterPushNotifications", register_variables)
    assert_graphql_call(session, 1, "RegisterPushNotifications", register_variables)
    assert_graphql_call(session, 2, "UnregisterPushNotifications", unregister_variables)
    assert_graphql_call(session, 3, "UnregisterPushNotifications", unregister_variables)


async def test_register_device_push_parses_every_union_type_and_nullable_result() -> None:
    root_field = "registerDeviceForPushNotifications"
    session = FakeSession(
        graphql_response({root_field: {"__typename": "GeneralMessage", "message": "registered"}}),
        graphql_response({root_field: {"__typename": "DatabaseError", "errorMessage": "database"}}),
        graphql_response({root_field: {"__typename": "TokenError", "errorMessage": "token"}}),
        graphql_response({root_field: None}),
    )
    client = make_client(session, read_only=False)

    assert await client.async_register_device_for_push_notifications(
        MOBILE_INFO
    ) == PushNotificationSuccess("registered")
    assert await client.async_register_device_for_push_notifications(
        MOBILE_INFO
    ) == PushNotificationDatabaseError("database")
    assert await client.async_register_device_for_push_notifications(
        MOBILE_INFO
    ) == PushNotificationTokenError("token")
    assert await client.async_register_device_for_push_notifications(MOBILE_INFO) is None

    variables = {
        "mobileInfoInput": {
            "mobile": {
                "deviceId": "device-id",
                "deviceType": "Android",
                "appName": "mynissan-android",
                "token": "push-token",
            }
        }
    }
    for index in range(4):
        assert_graphql_call(
            session,
            index,
            "RegisterDeviceForPushNotifications",
            variables,
        )


async def test_unregister_device_push_parses_every_union_type_and_nullable_result() -> None:
    root_field = "unregisterDeviceForPushNotifications"
    session = FakeSession(
        graphql_response({root_field: {"__typename": "GeneralMessage", "message": "unregistered"}}),
        graphql_response({root_field: {"__typename": "DatabaseError", "errorMessage": "database"}}),
        graphql_response({root_field: {"__typename": "TokenError", "errorMessage": "token"}}),
        graphql_response({root_field: None}),
    )
    client = make_client(session, read_only=False)

    assert await client.async_unregister_device_for_push_notifications(
        MYNISSAN_ANDROID_APP_NAME,
        "device-id",
        DeviceOS.ANDROID,
    ) == PushNotificationSuccess("unregistered")
    assert await client.async_unregister_device_for_push_notifications(
        MYNISSAN_ANDROID_APP_NAME,
        "device-id",
        DeviceOS.ANDROID,
    ) == PushNotificationDatabaseError("database")
    assert await client.async_unregister_device_for_push_notifications(
        MYNISSAN_ANDROID_APP_NAME,
        "device-id",
        DeviceOS.ANDROID,
    ) == PushNotificationTokenError("token")
    assert (
        await client.async_unregister_device_for_push_notifications(
            MYNISSAN_ANDROID_APP_NAME,
            "device-id",
            DeviceOS.ANDROID,
        )
        is None
    )

    variables = {
        "appName": "mynissan-android",
        "deviceId": "device-id",
        "deviceType": "Android",
    }
    for index in range(4):
        assert_graphql_call(
            session,
            index,
            "UnregisterDeviceForPushNotifications",
            variables,
        )


async def test_current_push_api_maps_ios_to_the_service_device_type_string() -> None:
    session = FakeSession(
        graphql_response(
            {
                "unregisterDeviceForPushNotifications": {
                    "__typename": "GeneralMessage",
                    "message": "unregistered",
                }
            }
        )
    )
    client = make_client(session, read_only=False)

    result = await client.async_unregister_device_for_push_notifications(
        MYNISSAN_ANDROID_APP_NAME,
        "device-id",
        DeviceOS.IOS,
    )

    assert result == PushNotificationSuccess("unregistered")
    assert_graphql_call(
        session,
        0,
        "UnregisterDeviceForPushNotifications",
        {
            "appName": "mynissan-android",
            "deviceId": "device-id",
            "deviceType": "Ios",
        },
    )


async def test_device_push_rejects_unknown_union_typenames() -> None:
    session = FakeSession(
        graphql_response(
            {"registerDeviceForPushNotifications": {"__typename": "UnexpectedPushResult"}}
        ),
        graphql_response(
            {"unregisterDeviceForPushNotifications": {"__typename": "UnexpectedPushResult"}}
        ),
    )
    client = make_client(session, read_only=False)

    with pytest.raises(ResponseError, match="Unsupported registerDeviceForPush"):
        await client.async_register_device_for_push_notifications(MOBILE_INFO)
    with pytest.raises(ResponseError, match="Unsupported unregisterDeviceForPush"):
        await client.async_unregister_device_for_push_notifications(
            MYNISSAN_ANDROID_APP_NAME,
            "device-id",
            DeviceOS.ANDROID,
        )


async def test_in_vehicle_messages_preserve_nullable_list_items_fields_and_dates() -> None:
    session = FakeSession(
        graphql_response(
            {
                "vehicle": {
                    "__typename": "BaseConnectedVehicle",
                    "inVehicleMessages": [
                        None,
                        {
                            "__typename": "InVehicleMessage",
                            "campaignId": None,
                            "createdDateTime": None,
                            "title": None,
                            "viewed": None,
                        },
                        {
                            "__typename": "InVehicleMessage",
                            "campaignId": "campaign-id",
                            "createdDateTime": "2026-07-31T10:20:30Z",
                            "title": "Service notice",
                            "viewed": False,
                        },
                    ],
                }
            }
        )
    )
    client = make_client(session)

    result = await client.async_get_in_vehicle_messages("VIN")

    assert result == (
        None,
        InVehicleMessageSummary(None, None, None, None),
        InVehicleMessageSummary(
            "campaign-id",
            datetime(2026, 7, 31, 10, 20, 30, tzinfo=UTC),
            "Service notice",
            False,
        ),
    )
    assert_graphql_call(session, 0, "InVehicleMessages", {"vin": "VIN"})


async def test_in_vehicle_message_preserves_unset_null_and_boolean_push_values() -> None:
    detail = {
        "__typename": "InVehicleMessage",
        "title": "Campaign",
        "campaignId": "campaign-id",
        "viewed": None,
        "text": None,
        "expireDate": "2026-08-01T12:30:00-07:00",
    }
    session = FakeSession(
        graphql_response(
            {
                "vehicle": {
                    "__typename": "BaseConnectedVehicle",
                    "inVehicleMessage": detail,
                }
            }
        ),
        graphql_response({"vehicle": None}),
        graphql_response({"vehicle": None}),
        graphql_response({"vehicle": None}),
        graphql_response({"vehicle": None}),
    )
    client = make_client(session, read_only=False)

    assert await client.async_get_in_vehicle_message("VIN", "campaign-id") == InVehicleMessage(
        title="Campaign",
        campaign_id="campaign-id",
        viewed=None,
        text=None,
        expire_date=datetime.fromisoformat("2026-08-01T12:30:00-07:00"),
    )
    assert await client.async_get_in_vehicle_message("VIN", "campaign-id", push=UNSET) is None
    assert await client.async_get_in_vehicle_message("VIN", "campaign-id", push=None) is None
    assert await client.async_get_in_vehicle_message("VIN", "campaign-id", push=False) is None
    assert await client.async_get_in_vehicle_message("VIN", "campaign-id", push=True) is None

    base_variables = {"vin": "VIN", "campaignId": "campaign-id"}
    assert_graphql_call(session, 0, "InVehicleMessage", {**base_variables, "push": False})
    assert_graphql_call(session, 1, "InVehicleMessage", base_variables)
    assert_graphql_call(session, 2, "InVehicleMessage", {**base_variables, "push": None})
    assert_graphql_call(session, 3, "InVehicleMessage", {**base_variables, "push": False})
    assert_graphql_call(session, 4, "InVehicleMessage", {**base_variables, "push": True})


async def test_in_vehicle_messages_handle_missing_and_null_response_chains() -> None:
    session = FakeSession(
        graphql_response({}),
        graphql_response({"vehicle": None}),
        graphql_response({"vehicle": {"__typename": "BaseConnectedVehicle"}}),
        graphql_response(
            {
                "vehicle": {
                    "__typename": "BaseConnectedVehicle",
                    "inVehicleMessages": None,
                }
            }
        ),
    )
    client = make_client(session)

    with pytest.raises(ResponseError, match="vehicle is missing"):
        await client.async_get_in_vehicle_messages("VIN")
    assert await client.async_get_in_vehicle_messages("VIN") is None
    assert await client.async_get_in_vehicle_messages("VIN") is None
    assert await client.async_get_in_vehicle_messages("VIN") is None


async def test_in_vehicle_message_handles_missing_and_null_response_chains() -> None:
    session = FakeSession(
        graphql_response({}),
        graphql_response({"vehicle": None}),
        graphql_response({"vehicle": {"__typename": "BaseConnectedVehicle"}}),
        graphql_response(
            {
                "vehicle": {
                    "__typename": "BaseConnectedVehicle",
                    "inVehicleMessage": None,
                }
            }
        ),
    )
    client = make_client(session, read_only=False)

    with pytest.raises(ResponseError, match="vehicle is missing"):
        await client.async_get_in_vehicle_message("VIN", "campaign-id")
    assert await client.async_get_in_vehicle_message("VIN", "campaign-id") is None
    assert await client.async_get_in_vehicle_message("VIN", "campaign-id") is None
    assert await client.async_get_in_vehicle_message("VIN", "campaign-id") is None


async def test_in_vehicle_message_dates_require_an_explicit_offset() -> None:
    session = FakeSession(
        graphql_response(
            {
                "vehicle": {
                    "__typename": "BaseConnectedVehicle",
                    "inVehicleMessages": [
                        {
                            "__typename": "InVehicleMessage",
                            "createdDateTime": "2026-07-31T10:20:30",
                        }
                    ],
                }
            }
        ),
        graphql_response(
            {
                "vehicle": {
                    "__typename": "BaseConnectedVehicle",
                    "inVehicleMessage": {
                        "__typename": "InVehicleMessage",
                        "expireDate": "2026-08-01T12:30:00",
                    },
                }
            }
        ),
    )
    client = make_client(session, read_only=False)

    with pytest.raises(ResponseError, match=r"createdDateTime.*with an offset"):
        await client.async_get_in_vehicle_messages("VIN")
    with pytest.raises(ResponseError, match=r"expireDate.*with an offset"):
        await client.async_get_in_vehicle_message("VIN", "campaign-id")


async def test_state_changing_notification_operations_respect_read_only_mode() -> None:
    session = FakeSession()
    client = make_client(session)

    with pytest.raises(ReadOnlyError):
        await client.async_register_push_notifications(
            "device-id",
            "push-token",
            DeviceOS.ANDROID,
        )
    with pytest.raises(ReadOnlyError):
        await client.async_unregister_push_notifications("device-id", DeviceOS.ANDROID)
    with pytest.raises(ReadOnlyError):
        await client.async_register_device_for_push_notifications(MOBILE_INFO)
    with pytest.raises(ReadOnlyError):
        await client.async_unregister_device_for_push_notifications(
            MYNISSAN_ANDROID_APP_NAME,
            "device-id",
            DeviceOS.ANDROID,
        )
    with pytest.raises(ReadOnlyError):
        await client.async_get_in_vehicle_message("VIN", "campaign-id")

    assert session.calls == []


async def test_unknown_device_os_is_rejected_before_io() -> None:
    session = FakeSession()
    client = make_client(session, read_only=False)

    with pytest.raises(ValueError, match="UNKNOWN_VALUE"):
        await client.async_register_push_notifications(
            "device-id",
            "push-token",
            DeviceOS.UNKNOWN_VALUE,
        )
    with pytest.raises(ValueError, match="UNKNOWN_VALUE"):
        await client.async_unregister_push_notifications(
            "device-id",
            DeviceOS.UNKNOWN_VALUE,
        )
    unknown_mobile_info = MobileInfoInput(
        MobileInput(
            device_id="device-id",
            device_os=DeviceOS.UNKNOWN_VALUE,
            app_name=MYNISSAN_ANDROID_APP_NAME,
            token="push-token",
        )
    )
    with pytest.raises(ValueError, match="UNKNOWN_VALUE"):
        await client.async_register_device_for_push_notifications(unknown_mobile_info)
    with pytest.raises(ValueError, match="UNKNOWN_VALUE"):
        await client.async_unregister_device_for_push_notifications(
            MYNISSAN_ANDROID_APP_NAME,
            "device-id",
            DeviceOS.UNKNOWN_VALUE,
        )

    assert session.calls == []
