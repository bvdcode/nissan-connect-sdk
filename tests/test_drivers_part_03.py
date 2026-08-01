from __future__ import annotations

import pytest
from test_drivers import DriverParser

from pynissan.driver_parsing import (
    parse_create_rsa_link,
    parse_driver_invite_action,
    parse_driver_invites,
    parse_emergency_contacts,
    parse_invite_driver,
    parse_update_driver,
    parse_update_emergency_contact,
)
from pynissan.exceptions import ResponseError


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
