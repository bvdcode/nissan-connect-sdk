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
    DataWipeType,
    NotificationCategory,
    NotificationDestination,
    NotificationPreferenceInput,
    NotificationTypeInput,
    ReadOnlyError,
    ResponseError,
    ServiceRequest,
    ServiceRequestKind,
    ServiceRequestResult,
    ServiceRequestStatus,
)


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
