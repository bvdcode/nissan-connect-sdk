from __future__ import annotations

import hashlib
import re
from collections.abc import Callable, Mapping
from datetime import UTC, datetime

import pytest

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
    CreateEmergencyContactResult,
    CreateRSALinkResult,
    DeleteDriverResult,
    DeleteEmergencyContactResult,
    DriverInvite,
    DriverInviteAction,
    DriverInviteActionResult,
    DriverInvitesResult,
    DriverOperationError,
    EmergencyContact,
    EmergencyContactRelationship,
    EmergencyContactsResult,
    InviteDriverResult,
    InviteDriverSuccess,
    InviteNotificationType,
    InviteStatus,
    OwnerInviteAction,
    OwnerInviteActionResult,
    UpdateDriverResult,
    UpdateDriverSuccess,
    UpdateEmergencyContactResult,
)
from pynissan.driver_parsing import (
    parse_create_emergency_contact,
    parse_create_rsa_link,
    parse_delete_driver,
    parse_delete_emergency_contact,
    parse_driver_invite_action,
    parse_driver_invites,
    parse_emergency_contacts,
    parse_invite_driver,
    parse_owner_invite_action,
    parse_update_driver,
    parse_update_emergency_contact,
)
from pynissan.exceptions import ResponseError
from pynissan.graphql_input import UNSET
from pynissan.operations import (
    CREATE_EMERGENCY_CONTACT,
    CREATE_EMERGENCY_CONTACT_OPERATION_ID,
    CREATE_RSA_LINK,
    CREATE_RSA_LINK_OPERATION_ID,
    DELETE_DRIVER,
    DELETE_DRIVER_OPERATION_ID,
    DELETE_EMERGENCY_CONTACT,
    DELETE_EMERGENCY_CONTACT_OPERATION_ID,
    DRIVER_INVITE_ACTION,
    DRIVER_INVITE_ACTION_OPERATION_ID,
    DRIVER_INVITES,
    DRIVER_INVITES_OPERATION_ID,
    EMERGENCY_CONTACTS,
    EMERGENCY_CONTACTS_OPERATION_ID,
    INVITE_DRIVER,
    INVITE_DRIVER_OPERATION_ID,
    OWNER_INVITE_ACTION,
    OWNER_INVITE_ACTION_OPERATION_ID,
    UPDATE_DRIVER,
    UPDATE_DRIVER_OPERATION_ID,
    UPDATE_EMERGENCY_CONTACT,
    UPDATE_EMERGENCY_CONTACT_OPERATION_ID,
)

type DriverParser = Callable[[Mapping[str, object]], object]

OPERATION_CONTRACTS = (
    (
        EMERGENCY_CONTACTS,
        EMERGENCY_CONTACTS_OPERATION_ID,
        "4a25bb6332b775a8d3c7a537b9c18240bd124b5f82d13ed6f57db183a27540c6",
    ),
    (
        CREATE_EMERGENCY_CONTACT,
        CREATE_EMERGENCY_CONTACT_OPERATION_ID,
        "6ec9650b727fad0009a31a84c7c856c1d4237859a425415e4af7af32c62720d6",
    ),
    (
        UPDATE_EMERGENCY_CONTACT,
        UPDATE_EMERGENCY_CONTACT_OPERATION_ID,
        "82e01b08a8d4d1234bfb291bc0c4088879005a0a78be17b0ffc07ec0cad38265",
    ),
    (
        DELETE_EMERGENCY_CONTACT,
        DELETE_EMERGENCY_CONTACT_OPERATION_ID,
        "49f5110a425f067c57ae4e77ee9cfef549643bcda9d3197ad78019dce5fc6e82",
    ),
    (
        DRIVER_INVITES,
        DRIVER_INVITES_OPERATION_ID,
        "1bf5c7a74ce2b01e3a7ca16609291cc461da80e5aafe41880c167403b1d4356c",
    ),
    (
        INVITE_DRIVER,
        INVITE_DRIVER_OPERATION_ID,
        "a011493c8f4daac8023e76727754e418c20fe10da9ff5ed01ce3b7e3e46bb53f",
    ),
    (
        DRIVER_INVITE_ACTION,
        DRIVER_INVITE_ACTION_OPERATION_ID,
        "336f69dee9d863de166355ec7cedebf4a8c610f7da5641742998408d4f33aced",
    ),
    (
        DELETE_DRIVER,
        DELETE_DRIVER_OPERATION_ID,
        "eb15f5cf270689f8b2433876f16809168d24d204cabef33a4a008d7cfe85eef8",
    ),
    (
        UPDATE_DRIVER,
        UPDATE_DRIVER_OPERATION_ID,
        "a1c9e0cca6955aece39702953a1dc2bb3b5aa709c2cdc5269eac69f4d4cef5dd",
    ),
    (
        OWNER_INVITE_ACTION,
        OWNER_INVITE_ACTION_OPERATION_ID,
        "c38c7b81b5834b725ec36d734680ea3a8e234fd432c8426eb21291febb6c9b67",
    ),
    (
        CREATE_RSA_LINK,
        CREATE_RSA_LINK_OPERATION_ID,
        "83b33ea891ea26d4d7c3bee4116075d372f5961237353a29b9710b7b3e4dc81f",
    ),
)


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


def test_parse_emergency_contact_mutation_results_preserves_nullable_success() -> None:
    assert parse_create_emergency_contact(
        {"createEmergencyContact": {"__typename": "ResponseStatus", "success": None}}
    ) == CreateEmergencyContactResult("ResponseStatus", None)
    assert parse_create_emergency_contact(
        {"createEmergencyContact": {"__typename": "FutureCreateResult"}}
    ) == CreateEmergencyContactResult("FutureCreateResult", None)
    assert parse_update_emergency_contact(
        {"updateEmergencyContact": {"__typename": "ResponseStatus", "success": True}}
    ) == UpdateEmergencyContactResult("ResponseStatus", True)
    assert parse_delete_emergency_contact(
        {"deleteEmergencyContact": {"__typename": "ResponseStatus", "success": False}}
    ) == DeleteEmergencyContactResult("ResponseStatus", False)


def test_parse_driver_invites_success_is_exact_and_future_safe() -> None:
    result = parse_driver_invites(
        {
            "driverInvites": {
                "__typename": "DriverInvitesSuccessResponse",
                "invites": [
                    {
                        "__typename": "Invitation",
                        "inviteId": "INVITE",
                        "driverFirstName": "Ada",
                        "driverLastName": "Lovelace",
                        "driverEmail": "ada@example.invalid",
                        "driverPhoneNumber": "+15550000000",
                        "inviteDateTime": "2026-07-31T12:00:00Z",
                        "inviteExpiryDateTime": "2026-08-07T12:00:00+00:00",
                        "inviteType": "FUTURE_CHANNEL",
                        "notificationsToPrimary": True,
                        "usageHistory": False,
                        "status": "FUTURE_STATUS",
                        "cdiid": None,
                    }
                ],
            }
        }
    )

    assert result == DriverInvitesResult(
        "DriverInvitesSuccessResponse",
        (
            DriverInvite(
                "Invitation",
                "INVITE",
                "Ada",
                "Lovelace",
                "ada@example.invalid",
                "+15550000000",
                datetime(2026, 7, 31, 12, tzinfo=UTC),
                datetime(2026, 8, 7, 12, tzinfo=UTC),
                InviteNotificationType.UNKNOWN_VALUE,
                True,
                False,
                InviteStatus.UNKNOWN_VALUE,
                None,
            ),
        ),
        None,
    )
    assert parse_driver_invites(
        {"driverInvites": {"__typename": "FutureDriverInvitesResult"}}
    ) == DriverInvitesResult("FutureDriverInvitesResult", None, None)


@pytest.mark.parametrize(
    "typename",
    ("GeneralErrors", "DatabaseError", "BrandError", "TokenError", "VinValidationError"),
)
def test_parse_driver_invites_preserves_every_known_error(typename: str) -> None:
    assert parse_driver_invites(
        {"driverInvites": {"__typename": typename, "errorMessage": "denied"}}
    ) == DriverInvitesResult(
        typename,
        None,
        DriverOperationError(typename, "denied"),
    )


def test_parse_invite_driver_success_is_exact() -> None:
    result = parse_invite_driver(
        {
            "inviteDriver": {
                "__typename": "InviteDriverSuccessResponse",
                "vin": "VIN",
                "inviteId": "INVITE",
                "driverFirstName": "Ada",
                "driverLastName": "Lovelace",
                "driverEmail": "ada@example.invalid",
                "driverPhoneNumber": "+15550000000",
                "entitlements": ["CLIMATE", "LOCK"],
                "inviteType": "EMAIL",
                "usageHistory": True,
                "notificationsToPrimary": False,
                "inviteDateTime": "2026-07-31T12:00:00-07:00",
                "status": "PENDING",
            }
        }
    )

    assert result == InviteDriverResult(
        "InviteDriverSuccessResponse",
        InviteDriverSuccess(
            "VIN",
            "INVITE",
            "Ada",
            "Lovelace",
            "ada@example.invalid",
            "+15550000000",
            ("CLIMATE", "LOCK"),
            InviteNotificationType.EMAIL,
            True,
            False,
            datetime.fromisoformat("2026-07-31T12:00:00-07:00"),
            InviteStatus.PENDING,
        ),
        None,
    )


@pytest.mark.parametrize(
    "typename",
    (
        "FirstNameValidationError",
        "LastNameValidationError",
        "EmailValidationError",
        "PhoneValidationError",
        "ExistingInviteError",
        "MaxInvitesReachedError",
    ),
)
def test_parse_invite_driver_preserves_every_known_error(typename: str) -> None:
    assert parse_invite_driver(
        {"inviteDriver": {"__typename": typename, "errorMessage": "invalid"}}
    ) == InviteDriverResult(
        typename,
        None,
        DriverOperationError(typename, "invalid"),
    )


@pytest.mark.parametrize(
    "typename",
    (
        "GeneralErrors",
        "DatabaseError",
        "InvalidInviteIdError",
        "TokenError",
        "BrandError",
        "TermsAndConditionsError",
        "CountryError",
    ),
)
def test_parse_driver_invite_action_preserves_every_known_error(typename: str) -> None:
    assert parse_driver_invite_action(
        {"driverInviteAction": {"__typename": typename, "errorMessage": "invalid"}}
    ) == DriverInviteActionResult(
        typename,
        None,
        DriverOperationError(typename, "invalid"),
    )


def test_parse_remaining_driver_results_preserves_success_and_future_branches() -> None:
    assert parse_driver_invite_action(
        {
            "driverInviteAction": {
                "__typename": "DriverInviteActionSuccessResponse",
                "success": True,
            }
        }
    ) == DriverInviteActionResult("DriverInviteActionSuccessResponse", True, None)
    assert parse_delete_driver(
        {"deleteDriver": {"__typename": "DeleteDriverSuccessResponse", "success": False}}
    ) == DeleteDriverResult("DeleteDriverSuccessResponse", False)
    assert parse_update_driver(
        {
            "updateDriver": {
                "__typename": "UpdateDriverSuccessResponse",
                "entitlements": ["CLIMATE"],
                "usageHistory": False,
                "notificationsToPrimary": True,
                "success": True,
            }
        }
    ) == UpdateDriverResult(
        "UpdateDriverSuccessResponse",
        UpdateDriverSuccess(("CLIMATE",), False, True, True),
    )
    assert parse_owner_invite_action(
        {
            "ownerInviteAction": {
                "__typename": "OwnerInviteActionSuccessResponse",
                "success": True,
            }
        }
    ) == OwnerInviteActionResult("OwnerInviteActionSuccessResponse", True)
    assert parse_delete_driver(
        {"deleteDriver": {"__typename": "FutureDeleteDriverResponse"}}
    ) == DeleteDriverResult("FutureDeleteDriverResponse", None)
    assert parse_update_driver(
        {"updateDriver": {"__typename": "FutureUpdateDriverResponse"}}
    ) == UpdateDriverResult("FutureUpdateDriverResponse", None)
    assert parse_owner_invite_action(
        {"ownerInviteAction": {"__typename": "FutureOwnerActionResponse"}}
    ) == OwnerInviteActionResult("FutureOwnerActionResponse", None)


def test_parse_create_rsa_link_preserves_nullable_link() -> None:
    assert parse_create_rsa_link(
        {"createRSALink": {"__typename": "RSALink", "link": None}}
    ) == CreateRSALinkResult("RSALink", None)
    assert parse_create_rsa_link(
        {"createRSALink": {"__typename": "RSALink", "link": "https://example.invalid/rsa"}}
    ) == CreateRSALinkResult("RSALink", "https://example.invalid/rsa")


@pytest.mark.parametrize(
    ("parser", "root_field"),
    (
        (parse_emergency_contacts, "vehicle"),
        (parse_create_emergency_contact, "createEmergencyContact"),
        (parse_update_emergency_contact, "updateEmergencyContact"),
        (parse_delete_emergency_contact, "deleteEmergencyContact"),
        (parse_driver_invites, "driverInvites"),
        (parse_invite_driver, "inviteDriver"),
        (parse_driver_invite_action, "driverInviteAction"),
        (parse_delete_driver, "deleteDriver"),
        (parse_update_driver, "updateDriver"),
        (parse_owner_invite_action, "ownerInviteAction"),
        (parse_create_rsa_link, "createRSALink"),
    ),
)
def test_driver_parsers_accept_nullable_roots(
    parser: DriverParser,
    root_field: str,
) -> None:
    assert parser({root_field: None}) is None


@pytest.mark.parametrize(
    ("parser", "payload", "message"),
    (
        (parse_driver_invites, {}, "driverInvites is missing"),
        (parse_driver_invites, {"driverInvites": []}, "driverInvites is not an object"),
        (
            parse_driver_invites,
            {"driverInvites": {"invites": []}},
            "driverInvites.__typename is missing",
        ),
        (
            parse_emergency_contacts,
            {"vehicle": {"__typename": "ConnectedVehicle"}},
            "vehicle.emergencyContacts is missing",
        ),
        (
            parse_emergency_contacts,
            {"vehicle": {"__typename": "ConnectedVehicle", "emergencyContacts": {}}},
            "vehicle.emergencyContacts is not a list",
        ),
        (
            parse_driver_invites,
            {
                "driverInvites": {
                    "__typename": "DriverInvitesSuccessResponse",
                    "invites": [None],
                }
            },
            "driverInvites.invites\\[0\\] is not an object",
        ),
        (
            parse_driver_invites,
            {"driverInvites": {"__typename": "GeneralErrors"}},
            "driverInvites.errorMessage is missing",
        ),
        (
            parse_invite_driver,
            {
                "inviteDriver": {
                    "__typename": "InviteDriverSuccessResponse",
                    "vin": "VIN",
                    "inviteId": "INVITE",
                    "driverFirstName": "Ada",
                    "driverLastName": "Lovelace",
                    "driverEmail": "ada@example.invalid",
                    "driverPhoneNumber": "+15550000000",
                    "entitlements": [],
                    "inviteType": "EMAIL",
                    "usageHistory": True,
                    "notificationsToPrimary": False,
                    "inviteDateTime": "2026-07-31T12:00:00",
                    "status": "PENDING",
                }
            },
            "inviteDriver.inviteDateTime is not an ISO-8601 date-time with an offset",
        ),
        (
            parse_driver_invite_action,
            {
                "driverInviteAction": {
                    "__typename": "DriverInviteActionSuccessResponse",
                    "success": None,
                }
            },
            "driverInviteAction.success is not a boolean",
        ),
        (
            parse_update_driver,
            {
                "updateDriver": {
                    "__typename": "UpdateDriverSuccessResponse",
                    "entitlements": [None],
                    "usageHistory": False,
                    "notificationsToPrimary": True,
                    "success": True,
                }
            },
            "updateDriver.entitlements\\[0\\] is not a string",
        ),
        (
            parse_update_emergency_contact,
            {"updateEmergencyContact": {"__typename": "ResponseStatus"}},
            "updateEmergencyContact.success is missing",
        ),
        (
            parse_create_rsa_link,
            {"createRSALink": {"__typename": "RSALink"}},
            "createRSALink.link is missing",
        ),
    ),
)
def test_driver_parsers_reject_malformed_or_missing_fields(
    parser: DriverParser,
    payload: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(ResponseError, match=message):
        parser(payload)
