from __future__ import annotations

import hashlib
import re
from collections.abc import Callable

import pytest
from test_drivers import (
    OPERATION_CONTRACTS,
)

from pynissan.driver_inputs import (
    CreateEmergencyContactInput,
    DriverInviteActionInput,
    DriverInviteInput,
    OwnerInviteActionInput,
    UpdateDriverInput,
    UpdateEmergencyContactInput,
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
from pynissan.driver_models import (
    DriverInviteAction,
    EmergencyContact,
    EmergencyContactRelationship,
    EmergencyContactsResult,
    InviteNotificationType,
    InviteStatus,
    OwnerInviteAction,
)
from pynissan.driver_parsing import (
    parse_emergency_contacts,
)
from pynissan.graphql_input import UNSET


@pytest.mark.parametrize(("document", "operation_id", "token_hash"), OPERATION_CONTRACTS)
def test_driver_operations_match_exact_persisted_contracts(
    document: str,
    operation_id: str,
    token_hash: str,
) -> None:
    tokens = " ".join(re.findall(r"\.\.\.|[_A-Za-z][_0-9A-Za-z]*|[$!():{}\[\]]", document))

    assert hashlib.sha256(document.encode()).hexdigest() == operation_id
    assert hashlib.sha256(tokens.encode()).hexdigest() == token_hash


def test_driver_enums_match_all_service_values() -> None:
    assert tuple(value.value for value in EmergencyContactRelationship) == (
        "ASSISTANT",
        "BROTHER",
        "BUSINESS_CONTACT",
        "CHAUFFEUR",
        "CO_WORKER",
        "DAUGHTER",
        "DOCTOR",
        "EMPLOYEE",
        "FATHER",
        "FIANCE",
        "FIANCEE",
        "FRIEND",
        "GRANDFATHER",
        "GRANDMOTHER",
        "MOTHER",
        "OTHER",
        "PARENTS",
        "PARTNER",
        "RELATIVE",
        "SIGNIFICANT_OTHER",
        "SISTER",
        "SON",
        "SPOUSE",
        "UNKNOWN__",
    )
    assert tuple(value.value for value in InviteNotificationType) == (
        "SMS",
        "EMAIL",
        "UNKNOWN__",
    )
    assert tuple(value.value for value in InviteStatus) == (
        "ACCEPTED",
        "PENDING",
        "DECLINE",
        "REMOVED",
        "CANCEL",
        "EXPIRED",
        "INVALIDATE",
        "NONE",
        "UNKNOWN__",
    )
    assert tuple(value.value for value in DriverInviteAction) == (
        "DECLINE",
        "ACCEPT",
        "INVALIDATE",
        "UNKNOWN__",
    )
    assert tuple(value.value for value in OwnerInviteAction) == (
        "RESEND",
        "CANCEL",
        "UNKNOWN__",
    )


def test_required_driver_variables_use_exact_shapes() -> None:
    assert emergency_contacts_variables("VIN") == {"vin": "VIN"}
    assert driver_invites_variables("VIN") == {"vin": "VIN"}
    assert delete_emergency_contact_variables("VIN", "CONTACT") == {
        "vin": "VIN",
        "emergencyContactId": "CONTACT",
    }
    assert delete_driver_variables("INVITE") == {"inviteId": "INVITE"}
    assert create_rsa_link_variables("VIN") == {"vin": "VIN"}


def test_emergency_contact_inputs_preserve_apollo_optional_states() -> None:
    created = CreateEmergencyContactInput(
        "Ada",
        "Lovelace",
        "+15550000000",
        EmergencyContactRelationship.FRIEND,
    )
    assert create_emergency_contact_variables("VIN", created) == {
        "vin": "VIN",
        "contact": {
            "firstName": "Ada",
            "lastName": "Lovelace",
            "primaryPhone": "+15550000000",
            "relationship": "FRIEND",
        },
    }
    assert create_emergency_contact_variables(
        "VIN",
        CreateEmergencyContactInput(
            "Ada",
            "Lovelace",
            "+15550000000",
            EmergencyContactRelationship.FRIEND,
            secondary_phone=None,
        ),
    )["contact"] == {
        "firstName": "Ada",
        "lastName": "Lovelace",
        "primaryPhone": "+15550000000",
        "secondaryPhone": None,
        "relationship": "FRIEND",
    }

    assert update_emergency_contact_variables(
        "VIN",
        UpdateEmergencyContactInput(
            "CONTACT",
            first_name=UNSET,
            last_name=None,
            primary_phone="+15551111111",
            secondary_phone=None,
            relationship=EmergencyContactRelationship.SPOUSE,
        ),
    ) == {
        "vin": "VIN",
        "contact": {
            "emergencyContactId": "CONTACT",
            "lastName": None,
            "primaryPhone": "+15551111111",
            "secondaryPhone": None,
            "relationship": "SPOUSE",
        },
    }


def test_nullable_driver_configs_preserve_omitted_null_and_value() -> None:
    assert invite_driver_variables() == {}
    assert invite_driver_variables(None) == {"config": None}
    assert driver_invite_action_variables() == {}
    assert driver_invite_action_variables(None) == {"config": None}
    assert owner_invite_action_variables() == {}
    assert owner_invite_action_variables(None) == {"config": None}

    assert invite_driver_variables(
        DriverInviteInput(
            "Ada",
            "Lovelace",
            "ada@example.invalid",
            "+15550000000",
            "VIN",
            (),
            InviteNotificationType.EMAIL,
            False,
            True,
        )
    ) == {
        "config": {
            "driverFirstName": "Ada",
            "driverLastName": "Lovelace",
            "driverEmail": "ada@example.invalid",
            "driverPhoneNumber": "+15550000000",
            "vin": "VIN",
            "entitlements": [],
            "inviteType": "EMAIL",
            "usageHistory": False,
            "notificationsToPrimary": True,
        }
    }
    assert driver_invite_action_variables(
        DriverInviteActionInput("INVITE", DriverInviteAction.ACCEPT)
    ) == {"config": {"inviteId": "INVITE", "action": "ACCEPT"}}
    assert driver_invite_action_variables(
        DriverInviteActionInput(
            "INVITE",
            DriverInviteAction.ACCEPT,
            terms_and_conditions=None,
        )
    ) == {
        "config": {
            "inviteId": "INVITE",
            "action": "ACCEPT",
            "termsAndConditions": None,
        }
    }
    assert owner_invite_action_variables(
        OwnerInviteActionInput(
            "INVITE",
            OwnerInviteAction.RESEND,
            InviteNotificationType.SMS,
        )
    ) == {
        "config": {
            "inviteId": "INVITE",
            "action": "RESEND",
            "notificationType": "SMS",
        }
    }


def test_update_driver_input_has_no_hidden_permission_defaults() -> None:
    assert update_driver_variables(
        UpdateDriverInput("INVITE", ("CLIMATE", "LOCK"), False, True)
    ) == {
        "config": {
            "inviteId": "INVITE",
            "entitlements": ["CLIMATE", "LOCK"],
            "usageHistory": False,
            "notificationsToPrimary": True,
        }
    }


@pytest.mark.parametrize(
    "serialize",
    (
        lambda: create_emergency_contact_variables(
            "VIN",
            CreateEmergencyContactInput(
                "Ada",
                "Lovelace",
                "+15550000000",
                EmergencyContactRelationship.UNKNOWN_VALUE,
            ),
        ),
        lambda: update_emergency_contact_variables(
            "VIN",
            UpdateEmergencyContactInput(
                "CONTACT",
                relationship=EmergencyContactRelationship.UNKNOWN_VALUE,
            ),
        ),
        lambda: invite_driver_variables(
            DriverInviteInput(
                "Ada",
                "Lovelace",
                "ada@example.invalid",
                "+15550000000",
                "VIN",
                (),
                InviteNotificationType.UNKNOWN_VALUE,
                False,
                False,
            )
        ),
        lambda: driver_invite_action_variables(
            DriverInviteActionInput("INVITE", DriverInviteAction.UNKNOWN_VALUE)
        ),
        lambda: owner_invite_action_variables(
            OwnerInviteActionInput(
                "INVITE",
                OwnerInviteAction.UNKNOWN_VALUE,
                InviteNotificationType.EMAIL,
            )
        ),
    ),
)
def test_unknown_input_enums_are_never_serialized(serialize: Callable[[], object]) -> None:
    with pytest.raises(ValueError, match="UNKNOWN_VALUE"):
        serialize()


def test_parse_emergency_contacts_preserves_nullable_fields_items_and_future_enum() -> None:
    result = parse_emergency_contacts(
        {
            "vehicle": {
                "__typename": "ElectricAVK2Vehicle",
                "emergencyContacts": [
                    None,
                    {
                        "__typename": "EmergencyContact",
                        "id": None,
                        "firstName": "Ada",
                        "lastName": None,
                        "primaryPhone": "+15550000000",
                        "secondaryPhone": None,
                        "relationship": "FUTURE_RELATIONSHIP",
                    },
                ],
            }
        }
    )

    assert result == EmergencyContactsResult(
        "ElectricAVK2Vehicle",
        (
            None,
            EmergencyContact(
                "EmergencyContact",
                None,
                "Ada",
                None,
                "+15550000000",
                None,
                EmergencyContactRelationship.UNKNOWN_VALUE,
            ),
        ),
    )
    assert parse_emergency_contacts(
        {"vehicle": {"__typename": "NonConnectedVehicleResponse"}}
    ) == EmergencyContactsResult("NonConnectedVehicleResponse", None)
    assert parse_emergency_contacts(
        {"vehicle": {"__typename": "ConnectedVehicle", "emergencyContacts": None}}
    ) == EmergencyContactsResult("ConnectedVehicle", None)
