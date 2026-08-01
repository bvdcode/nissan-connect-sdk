from __future__ import annotations

from collections.abc import Awaitable, Mapping
from datetime import date
from typing import cast

import pytest
from aiohttp import ClientSession

from pynissan import (
    CreateEmergencyContactInput,
    CreatePartsReminderInput,
    DistanceUnit,
    DriverInviteAction,
    DriverInviteActionInput,
    DriverInviteInput,
    EmergencyContactRelationship,
    InviteNotificationType,
    NcarIcarRegisterAccountAddressInput,
    NcarIcarRegisterAccountInput,
    NissanClient,
    OwnerInviteAction,
    OwnerInviteActionInput,
    PastServiceInput,
    ReadOnlyError,
    ResetPartsReminderInput,
    Tokens,
    UpdateDriverInput,
    UpdateEmergencyContactInput,
    UpdatePartsReminderInput,
    UpdatePastServiceInput,
    VehicleHologram,
)
from pynissan.driver_inputs import (
    create_emergency_contact_variables,
    create_rsa_link_variables,
    delete_driver_variables,
    delete_emergency_contact_variables,
    driver_invite_action_variables,
    driver_invites_variables,
    emergency_contacts_variables,
    invite_driver_variables,
    owner_invite_action_variables,
    update_driver_variables,
    update_emergency_contact_variables,
)
from pynissan.garage_inputs import (
    add_vehicle_variables,
    apc_agreement_variables,
    apc_document_url_variables,
    connected_terms_and_conditions_by_vin_variables,
    create_apc_agreement_variables,
    delete_vehicle_variables,
    ncar_icar_add_vehicle_variables,
    onboarding_features_variables,
    ownership_status_variables,
    pending_vehicles_variables,
    update_apc_agreement_variables,
    update_vehicle_manual_mileage_variables,
    update_vehicle_nickname_variables,
    update_vehicle_variables,
    upload_ownership_verification_variables,
)
from pynissan.maintenance_inputs import (
    add_past_service_variables,
    collision_history_variables,
    collision_probe_data_variables,
    create_parts_reminder_variables,
    delete_parts_reminder_variables,
    get_maintenance_timeline_variables,
    get_service_contracts_variables,
    parts_reminders_variables,
    reset_parts_reminder_variables,
    update_parts_reminder_variables,
    update_past_service_variables,
)


class FakeResponse:
    def __init__(self, data: Mapping[str, object]) -> None:
        self.status = 200
        self._payload = {"data": dict(data)}

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


def response(field: str, value: object = None) -> FakeResponse:
    return FakeResponse({field: value})


def make_client(session: FakeSession, *, read_only: bool) -> NissanClient:
    return NissanClient(
        cast(ClientSession, session),
        tokens=Tokens("access-token", "refresh-token", "id-token"),
        read_only=read_only,
    )


def payloads(session: FakeSession) -> list[Mapping[str, object]]:
    values: list[Mapping[str, object]] = []
    for call in session.calls:
        value = call["json"]
        assert isinstance(value, Mapping)
        values.append(value)
    return values


def garage_account() -> NcarIcarRegisterAccountInput:
    return NcarIcarRegisterAccountInput(
        first_name="Ada",
        last_name="Lovelace",
        email="ada@example.com",
        phone_number="+15555550100",
        address=NcarIcarRegisterAccountAddressInput(
            address_1="1 Main St",
            address_2="Suite 2",
            city="Franklin",
            state="TN",
            postal_code="37064",
            country="US",
        ),
    )


def emergency_contact() -> CreateEmergencyContactInput:
    return CreateEmergencyContactInput(
        first_name="Grace",
        last_name="Hopper",
        primary_phone="+15555550101",
        relationship=EmergencyContactRelationship.FRIEND,
    )


def driver_invite() -> DriverInviteInput:
    return DriverInviteInput(
        driver_first_name="Katherine",
        driver_last_name="Johnson",
        driver_email="katherine@example.com",
        driver_phone_number="+15555550102",
        vin="VIN",
        entitlements=("REMOTE_DOOR",),
        invite_type=InviteNotificationType.EMAIL,
        usage_history=True,
        notifications_to_primary=False,
    )


async def test_garage_client_wires_all_operations() -> None:
    session = FakeSession(
        response("addVehicle"),
        response("deleteVehicle"),
        response("ncarIcarAddVehicle"),
        response("pendingVehicles"),
        response("vehicle"),
        response("vehicle"),
        response("vehicle"),
        response("createAPCAgreement"),
        response("updateAPCAgreement"),
        response("connectedTermsAndConditionsByVIN"),
        response("vehicle"),
        response("updateVehicle"),
        response("updateVehicle"),
        response("updateVehicle"),
        response("uploadOwnershipVerification"),
    )
    client = make_client(session, read_only=False)
    account = garage_account()

    assert await client.async_add_vehicle("VIN", True) is None
    assert await client.async_delete_vehicle("VIN") is None
    assert await client.async_add_ncar_icar_vehicle(True, "GUID", account=account) is None
    assert await client.async_get_pending_vehicles() is None
    assert await client.async_get_ownership_status("VIN") is None
    assert await client.async_get_apc_agreement("VIN") is None
    assert await client.async_get_apc_document_url("VIN") is None
    assert await client.async_create_apc_agreement("VIN", True) is None
    assert await client.async_update_apc_agreement("VIN", False) is None
    assert await client.async_get_connected_terms_and_conditions_by_vin("VIN") is None
    assert await client.async_get_onboarding_features("VIN") is None
    assert (
        await client.async_update_vehicle(
            "VIN",
            license_plate="ARIYA",
            hologram=VehicleHologram.E,
        )
        is None
    )
    assert await client.async_update_vehicle_manual_mileage("VIN", manual_mileage=1234) is None
    assert await client.async_update_vehicle_nickname("VIN", "Blue") is None
    assert (
        await client.async_upload_ownership_verification(
            "VIN",
            "title.pdf",
            "BASE64",
            True,
        )
        is None
    )

    requests = payloads(session)
    assert [value["operationName"] for value in requests] == [
        "AddVehicle",
        "DeleteVehicle",
        "NcarIcarAddVehicle",
        "PendingVehicles",
        "OwnershipStatus",
        "APCAgreement",
        "APCDocumentURL",
        "CreateAPCAgreement",
        "UpdateAPCAgreement",
        "ConnectedTermsAndConditionsByVIN",
        "OnboardingFeatures",
        "UpdateVehicle",
        "UpdateVehicleManualMileage",
        "UpdateVehicleNickname",
        "UploadOwnershipVerification",
    ]
    assert [value["variables"] for value in requests] == [
        add_vehicle_variables("VIN", True),
        delete_vehicle_variables("VIN"),
        ncar_icar_add_vehicle_variables(True, "GUID", account=account),
        pending_vehicles_variables(),
        ownership_status_variables("VIN"),
        apc_agreement_variables("VIN"),
        apc_document_url_variables("VIN"),
        create_apc_agreement_variables("VIN", True),
        update_apc_agreement_variables("VIN", False),
        connected_terms_and_conditions_by_vin_variables("VIN"),
        onboarding_features_variables("VIN"),
        update_vehicle_variables(
            "VIN",
            license_plate="ARIYA",
            hologram=VehicleHologram.E,
        ),
        update_vehicle_manual_mileage_variables("VIN", manual_mileage=1234),
        update_vehicle_nickname_variables("VIN", "Blue"),
        upload_ownership_verification_variables(
            "VIN",
            "title.pdf",
            "BASE64",
            True,
        ),
    ]


async def test_driver_and_emergency_client_wires_all_operations() -> None:
    session = FakeSession(
        response("vehicle"),
        response("createEmergencyContact"),
        response("updateEmergencyContact"),
        response("deleteEmergencyContact"),
        response("driverInvites"),
        response("inviteDriver"),
        response("driverInviteAction"),
        response("deleteDriver"),
        response("updateDriver"),
        response("ownerInviteAction"),
        response("createRSALink"),
    )
    client = make_client(session, read_only=False)
    contact = emergency_contact()
    contact_update = UpdateEmergencyContactInput(
        "CONTACT",
        first_name="Rear Admiral Grace",
    )
    invite = driver_invite()
    invite_action = DriverInviteActionInput(
        "INVITE",
        DriverInviteAction.ACCEPT,
        terms_and_conditions=True,
    )
    driver_update = UpdateDriverInput(
        "INVITE",
        ("REMOTE_DOOR", "REMOTE_CLIMATE"),
        True,
        False,
    )
    owner_action = OwnerInviteActionInput(
        "INVITE",
        OwnerInviteAction.RESEND,
        InviteNotificationType.EMAIL,
    )

    assert await client.async_get_emergency_contacts("VIN") is None
    assert await client.async_create_emergency_contact("VIN", contact) is None
    assert await client.async_update_emergency_contact("VIN", contact_update) is None
    assert await client.async_delete_emergency_contact("VIN", "CONTACT") is None
    assert await client.async_get_driver_invites("VIN") is None
    assert await client.async_invite_driver(invite) is None
    assert await client.async_driver_invite_action(invite_action) is None
    assert await client.async_delete_driver("INVITE") is None
    assert await client.async_update_driver(driver_update) is None
    assert await client.async_owner_invite_action(owner_action) is None
    assert await client.async_create_rsa_link("VIN") is None

    requests = payloads(session)
    assert [value["operationName"] for value in requests] == [
        "EmergencyContacts",
        "CreateEmergencyContact",
        "UpdateEmergencyContact",
        "DeleteEmergencyContact",
        "DriverInvites",
        "InviteDriver",
        "DriverInviteAction",
        "DeleteDriver",
        "UpdateDriver",
        "OwnerInviteAction",
        "CreateRSALink",
    ]
    assert [value["variables"] for value in requests] == [
        emergency_contacts_variables("VIN"),
        create_emergency_contact_variables("VIN", contact),
        update_emergency_contact_variables("VIN", contact_update),
        delete_emergency_contact_variables("VIN", "CONTACT"),
        driver_invites_variables("VIN"),
        invite_driver_variables(invite),
        driver_invite_action_variables(invite_action),
        delete_driver_variables("INVITE"),
        update_driver_variables(driver_update),
        owner_invite_action_variables(owner_action),
        create_rsa_link_variables("VIN"),
    ]


async def test_maintenance_client_wires_all_operations() -> None:
    session = FakeSession(
        response("vehicle"),
        response("vehicle"),
        response("addPastService"),
        response("updatePastService"),
        response("vehicle"),
        response("createPartsReminder"),
        response("updatePartsReminder"),
        response("resetPartsReminder"),
        response("deletePartsReminder"),
        response("vehicle"),
        response("vehicle"),
    )
    client = make_client(session, read_only=False)
    past_service = PastServiceInput("VIN", 42, date(2026, 7, 1), 1200)
    updated_service = UpdatePastServiceInput(
        "VIN",
        42,
        date(2026, 7, 2),
        1201,
        7,
    )
    created_reminder = CreatePartsReminderInput(("CABIN_FILTER",))
    updated_reminder = UpdatePartsReminderInput("REMINDER", ("CABIN_FILTER",))
    reset_reminder = ResetPartsReminderInput("REMINDER", ("CABIN_FILTER",))

    assert await client.async_get_maintenance_timeline("VIN", DistanceUnit.MILE) is None
    assert await client.async_get_service_contracts("VIN", 1200) is None
    assert await client.async_add_past_service(past_service) is None
    assert await client.async_update_past_service(updated_service) is None
    assert await client.async_get_parts_reminders("VIN", unit=DistanceUnit.MILE) is None
    assert await client.async_create_parts_reminder("VIN", created_reminder) is None
    assert await client.async_update_parts_reminder("VIN", updated_reminder) is None
    assert await client.async_reset_parts_reminder("VIN", reset_reminder) is None
    assert await client.async_delete_parts_reminder("VIN", "REMINDER") is None
    assert await client.async_get_collision_history("VIN") is None
    assert await client.async_get_collision_probe_data("VIN") is None

    requests = payloads(session)
    assert [value["operationName"] for value in requests] == [
        "GetMaintenanceTimeline",
        "GetServiceContracts",
        "AddPastService",
        "UpdatePastService",
        "PartsReminders",
        "CreatePartsReminder",
        "UpdatePartsReminder",
        "ResetPartsReminder",
        "DeletePartsReminder",
        "CollisionHistory",
        "CollisionProbeData",
    ]
    assert [value["variables"] for value in requests] == [
        get_maintenance_timeline_variables("VIN", DistanceUnit.MILE),
        get_service_contracts_variables("VIN", 1200),
        add_past_service_variables(past_service),
        update_past_service_variables(updated_service),
        parts_reminders_variables("VIN", unit=DistanceUnit.MILE),
        create_parts_reminder_variables("VIN", created_reminder),
        update_parts_reminder_variables("VIN", updated_reminder),
        reset_parts_reminder_variables("VIN", reset_reminder),
        delete_parts_reminder_variables("VIN", "REMINDER"),
        collision_history_variables("VIN"),
        collision_probe_data_variables("VIN"),
    ]


async def assert_read_only(awaitable: Awaitable[object]) -> None:
    with pytest.raises(ReadOnlyError):
        await awaitable


async def test_all_new_mutations_respect_read_only_before_io() -> None:
    session = FakeSession()
    client = make_client(session, read_only=True)
    account = garage_account()
    contact = emergency_contact()
    invite = driver_invite()
    past_service = PastServiceInput("VIN", 42, date(2026, 7, 1), 1200)

    await assert_read_only(client.async_add_vehicle("VIN", True))
    await assert_read_only(client.async_delete_vehicle("VIN"))
    await assert_read_only(client.async_add_ncar_icar_vehicle(True, "GUID", account=account))
    await assert_read_only(client.async_create_apc_agreement("VIN", True))
    await assert_read_only(client.async_update_apc_agreement("VIN", False))
    await assert_read_only(client.async_get_connected_terms_and_conditions_by_vin("VIN"))
    await assert_read_only(client.async_update_vehicle("VIN", hologram=VehicleHologram.E))
    await assert_read_only(client.async_update_vehicle_manual_mileage("VIN", manual_mileage=1200))
    await assert_read_only(client.async_update_vehicle_nickname("VIN", "Blue"))
    await assert_read_only(
        client.async_upload_ownership_verification("VIN", "title.pdf", "BASE64", True)
    )
    await assert_read_only(client.async_create_emergency_contact("VIN", contact))
    await assert_read_only(
        client.async_update_emergency_contact(
            "VIN",
            UpdateEmergencyContactInput("CONTACT", first_name="Grace"),
        )
    )
    await assert_read_only(client.async_delete_emergency_contact("VIN", "CONTACT"))
    await assert_read_only(client.async_invite_driver(invite))
    await assert_read_only(
        client.async_driver_invite_action(
            DriverInviteActionInput("INVITE", DriverInviteAction.ACCEPT)
        )
    )
    await assert_read_only(client.async_delete_driver("INVITE"))
    await assert_read_only(
        client.async_update_driver(UpdateDriverInput("INVITE", (), False, False))
    )
    await assert_read_only(
        client.async_owner_invite_action(
            OwnerInviteActionInput(
                "INVITE",
                OwnerInviteAction.CANCEL,
                InviteNotificationType.EMAIL,
            )
        )
    )
    await assert_read_only(client.async_create_rsa_link("VIN"))
    await assert_read_only(client.async_add_past_service(past_service))
    await assert_read_only(
        client.async_update_past_service(
            UpdatePastServiceInput("VIN", 42, date(2026, 7, 1), 1200, 7)
        )
    )
    await assert_read_only(
        client.async_create_parts_reminder(
            "VIN",
            CreatePartsReminderInput(("CABIN_FILTER",)),
        )
    )
    await assert_read_only(
        client.async_update_parts_reminder(
            "VIN",
            UpdatePartsReminderInput("REMINDER", ("CABIN_FILTER",)),
        )
    )
    await assert_read_only(
        client.async_reset_parts_reminder(
            "VIN",
            ResetPartsReminderInput("REMINDER", ("CABIN_FILTER",)),
        )
    )
    await assert_read_only(client.async_delete_parts_reminder("VIN", "REMINDER"))

    assert session.calls == []
