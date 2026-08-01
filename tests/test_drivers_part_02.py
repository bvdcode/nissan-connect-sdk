from __future__ import annotations

from datetime import UTC, datetime

import pytest
from test_drivers import DriverParser

from pynissan.driver_models import (
    CreateEmergencyContactResult,
    CreateRSALinkResult,
    DeleteDriverResult,
    DeleteEmergencyContactResult,
    DriverInvite,
    DriverInviteActionResult,
    DriverInvitesResult,
    DriverOperationError,
    InviteDriverResult,
    InviteDriverSuccess,
    InviteNotificationType,
    InviteStatus,
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
