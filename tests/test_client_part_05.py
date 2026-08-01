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
    DataPrivacyMode,
    ReadOnlyError,
    ReminderNotificationsAfterLeavingVehicle,
    ResponseError,
    VehicleAlertKind,
    VehicleAlertRequest,
    VehicleWifiConsumption,
)


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
