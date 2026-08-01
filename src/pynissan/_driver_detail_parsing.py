from __future__ import annotations

from collections.abc import Mapping

from ._driver_value_parsing import (
    _required_bool,
    _required_datetime,
    _required_enum,
    _required_nullable_enum,
    _required_nullable_string,
    _required_string,
    _required_string_tuple,
    _typed_object,
    _typename,
)
from .driver_models import (
    DriverInvite,
    DriverOperationError,
    EmergencyContact,
    EmergencyContactRelationship,
    InviteDriverSuccess,
    InviteNotificationType,
    InviteStatus,
)

_BASE_CONNECTED_VEHICLE_TYPES = frozenset(
    {
        "AVK2Vehicle",
        "AVKVehicle",
        "ConnectedVehicle",
        "ElectricAVK2Vehicle",
        "ElectricEVOVehicle",
        "ElectricVehicle",
        "EVOVehicle",
    }
)
_DRIVER_INVITES_ERROR_TYPES = frozenset(
    {
        "GeneralErrors",
        "DatabaseError",
        "BrandError",
        "TokenError",
        "VinValidationError",
    }
)
_INVITE_DRIVER_ERROR_TYPES = frozenset(
    {
        "FirstNameValidationError",
        "LastNameValidationError",
        "EmailValidationError",
        "PhoneValidationError",
        "ExistingInviteError",
        "MaxInvitesReachedError",
    }
)
_DRIVER_INVITE_ACTION_ERROR_TYPES = frozenset(
    {
        "GeneralErrors",
        "DatabaseError",
        "InvalidInviteIdError",
        "TokenError",
        "BrandError",
        "TermsAndConditionsError",
        "CountryError",
    }
)


def _parse_emergency_contact(value: object, path: str) -> EmergencyContact:
    contact = _typed_object(value, path)
    return EmergencyContact(
        typename=_typename(contact, path),
        id=_required_nullable_string(contact, "id", f"{path}.id"),
        first_name=_required_nullable_string(contact, "firstName", f"{path}.firstName"),
        last_name=_required_nullable_string(contact, "lastName", f"{path}.lastName"),
        primary_phone=_required_nullable_string(
            contact,
            "primaryPhone",
            f"{path}.primaryPhone",
        ),
        secondary_phone=_required_nullable_string(
            contact,
            "secondaryPhone",
            f"{path}.secondaryPhone",
        ),
        relationship=_required_nullable_enum(
            contact,
            "relationship",
            EmergencyContactRelationship,
            f"{path}.relationship",
        ),
    )


def _parse_driver_invite(value: object, path: str) -> DriverInvite:
    invite = _typed_object(value, path)
    return DriverInvite(
        typename=_typename(invite, path),
        invite_id=_required_string(invite, "inviteId", f"{path}.inviteId"),
        driver_first_name=_required_string(
            invite,
            "driverFirstName",
            f"{path}.driverFirstName",
        ),
        driver_last_name=_required_string(
            invite,
            "driverLastName",
            f"{path}.driverLastName",
        ),
        driver_email=_required_string(invite, "driverEmail", f"{path}.driverEmail"),
        driver_phone_number=_required_string(
            invite,
            "driverPhoneNumber",
            f"{path}.driverPhoneNumber",
        ),
        invite_date_time=_required_datetime(
            invite,
            "inviteDateTime",
            f"{path}.inviteDateTime",
        ),
        invite_expiry_date_time=_required_datetime(
            invite,
            "inviteExpiryDateTime",
            f"{path}.inviteExpiryDateTime",
        ),
        invite_type=_required_enum(
            invite,
            "inviteType",
            InviteNotificationType,
            f"{path}.inviteType",
        ),
        notifications_to_primary=_required_bool(
            invite,
            "notificationsToPrimary",
            f"{path}.notificationsToPrimary",
        ),
        usage_history=_required_bool(
            invite,
            "usageHistory",
            f"{path}.usageHistory",
        ),
        status=_required_enum(invite, "status", InviteStatus, f"{path}.status"),
        cdiid=_required_nullable_string(invite, "cdiid", f"{path}.cdiid"),
    )


def _parse_invite_driver_success(
    result: Mapping[str, object],
    path: str,
) -> InviteDriverSuccess:
    return InviteDriverSuccess(
        vin=_required_string(result, "vin", f"{path}.vin"),
        invite_id=_required_string(result, "inviteId", f"{path}.inviteId"),
        driver_first_name=_required_string(
            result,
            "driverFirstName",
            f"{path}.driverFirstName",
        ),
        driver_last_name=_required_string(
            result,
            "driverLastName",
            f"{path}.driverLastName",
        ),
        driver_email=_required_string(result, "driverEmail", f"{path}.driverEmail"),
        driver_phone_number=_required_string(
            result,
            "driverPhoneNumber",
            f"{path}.driverPhoneNumber",
        ),
        entitlements=_required_string_tuple(
            result,
            "entitlements",
            f"{path}.entitlements",
        ),
        invite_type=_required_enum(
            result,
            "inviteType",
            InviteNotificationType,
            f"{path}.inviteType",
        ),
        usage_history=_required_bool(result, "usageHistory", f"{path}.usageHistory"),
        notifications_to_primary=_required_bool(
            result,
            "notificationsToPrimary",
            f"{path}.notificationsToPrimary",
        ),
        invite_date_time=_required_datetime(
            result,
            "inviteDateTime",
            f"{path}.inviteDateTime",
        ),
        status=_required_enum(result, "status", InviteStatus, f"{path}.status"),
    )


def _parse_error(
    result: Mapping[str, object],
    path: str,
    typename: str,
) -> DriverOperationError:
    return DriverOperationError(
        typename,
        _required_string(result, "errorMessage", f"{path}.errorMessage"),
    )
