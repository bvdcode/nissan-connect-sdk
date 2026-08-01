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
    UNSET,
    AlertScheduleInput,
    AlertSpeedInput,
    BoundaryAlertUpdate,
    CurfewAlertInput,
    ReadOnlyError,
    SpeedAlertInput,
    SpeedUnit,
    ValetRadiusInput,
    VehicleAlertKind,
    VehicleAlertRequest,
    WeekDay,
)


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
