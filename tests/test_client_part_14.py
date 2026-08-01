from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
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
    NotificationCategory,
    NotificationDestination,
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
    PlugConnectorType,
    PointOfInterestFolder,
    RouteStatus,
    ServiceRequest,
    ServiceRequestKind,
)


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
