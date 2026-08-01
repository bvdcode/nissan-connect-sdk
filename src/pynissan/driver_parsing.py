from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from enum import StrEnum

from .driver_models import (
    CreateEmergencyContactResult,
    CreateRSALinkResult,
    DeleteDriverResult,
    DeleteEmergencyContactResult,
    DriverInvite,
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
    OwnerInviteActionResult,
    UpdateDriverResult,
    UpdateDriverSuccess,
    UpdateEmergencyContactResult,
)
from .exceptions import ResponseError

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


def parse_emergency_contacts(
    data: Mapping[str, object],
) -> EmergencyContactsResult | None:
    """Parse a nullable vehicle and its nullable emergency-contact collection."""

    root_field = "vehicle"
    vehicle = _root(data, root_field)
    if vehicle is None:
        return None

    typename = _typename(vehicle, root_field)
    if "emergencyContacts" not in vehicle:
        if typename in _BASE_CONNECTED_VEHICLE_TYPES:
            raise ResponseError(f"{root_field}.emergencyContacts is missing")
        return EmergencyContactsResult(typename, None)

    contacts_path = f"{root_field}.emergencyContacts"
    raw_contacts = _nullable_list(
        _required_value(vehicle, "emergencyContacts", contacts_path),
        contacts_path,
    )
    contacts: tuple[EmergencyContact | None, ...] | None = None
    if raw_contacts is not None:
        parsed_contacts: list[EmergencyContact | None] = []
        for index, raw_contact in enumerate(raw_contacts):
            if raw_contact is None:
                parsed_contacts.append(None)
                continue
            parsed_contacts.append(
                _parse_emergency_contact(raw_contact, f"{contacts_path}[{index}]")
            )
        contacts = tuple(parsed_contacts)
    return EmergencyContactsResult(typename, contacts)


def parse_create_emergency_contact(
    data: Mapping[str, object],
) -> CreateEmergencyContactResult | None:
    """Parse the nullable union returned by CreateEmergencyContact."""

    root_field = "createEmergencyContact"
    result = _root(data, root_field)
    if result is None:
        return None
    typename = _typename(result, root_field)
    success = None
    if typename == "ResponseStatus":
        success = _required_nullable_bool(result, "success", f"{root_field}.success")
    return CreateEmergencyContactResult(typename, success)


def parse_update_emergency_contact(
    data: Mapping[str, object],
) -> UpdateEmergencyContactResult | None:
    """Parse UpdateEmergencyContact's nullable direct response."""

    root_field = "updateEmergencyContact"
    result = _root(data, root_field)
    if result is None:
        return None
    return UpdateEmergencyContactResult(
        _typename(result, root_field),
        _required_nullable_bool(result, "success", f"{root_field}.success"),
    )


def parse_delete_emergency_contact(
    data: Mapping[str, object],
) -> DeleteEmergencyContactResult | None:
    """Parse DeleteEmergencyContact's nullable direct response."""

    root_field = "deleteEmergencyContact"
    result = _root(data, root_field)
    if result is None:
        return None
    return DeleteEmergencyContactResult(
        _typename(result, root_field),
        _required_nullable_bool(result, "success", f"{root_field}.success"),
    )


def parse_driver_invites(data: Mapping[str, object]) -> DriverInvitesResult | None:
    """Parse every known DriverInvites union branch and preserve future types."""

    root_field = "driverInvites"
    result = _root(data, root_field)
    if result is None:
        return None
    typename = _typename(result, root_field)
    if typename == "DriverInvitesSuccessResponse":
        invites_path = f"{root_field}.invites"
        raw_invites = _required_list(result, "invites", invites_path)
        invites = tuple(
            _parse_driver_invite(value, f"{invites_path}[{index}]")
            for index, value in enumerate(raw_invites)
        )
        return DriverInvitesResult(typename, invites, None)
    if typename in _DRIVER_INVITES_ERROR_TYPES:
        return DriverInvitesResult(typename, None, _parse_error(result, root_field, typename))
    return DriverInvitesResult(typename, None, None)


def parse_invite_driver(data: Mapping[str, object]) -> InviteDriverResult | None:
    """Parse every known InviteDriver union branch and preserve future types."""

    root_field = "inviteDriver"
    result = _root(data, root_field)
    if result is None:
        return None
    typename = _typename(result, root_field)
    if typename == "InviteDriverSuccessResponse":
        return InviteDriverResult(
            typename,
            _parse_invite_driver_success(result, root_field),
            None,
        )
    if typename in _INVITE_DRIVER_ERROR_TYPES:
        return InviteDriverResult(typename, None, _parse_error(result, root_field, typename))
    return InviteDriverResult(typename, None, None)


def parse_driver_invite_action(
    data: Mapping[str, object],
) -> DriverInviteActionResult | None:
    """Parse every known DriverInviteAction union branch and preserve future types."""

    root_field = "driverInviteAction"
    result = _root(data, root_field)
    if result is None:
        return None
    typename = _typename(result, root_field)
    if typename == "DriverInviteActionSuccessResponse":
        return DriverInviteActionResult(
            typename,
            _required_bool(result, "success", f"{root_field}.success"),
            None,
        )
    if typename in _DRIVER_INVITE_ACTION_ERROR_TYPES:
        return DriverInviteActionResult(
            typename,
            None,
            _parse_error(result, root_field, typename),
        )
    return DriverInviteActionResult(typename, None, None)


def parse_delete_driver(data: Mapping[str, object]) -> DeleteDriverResult | None:
    """Parse DeleteDriver's known success branch and preserve future types."""

    root_field = "deleteDriver"
    result = _root(data, root_field)
    if result is None:
        return None
    typename = _typename(result, root_field)
    success = None
    if typename == "DeleteDriverSuccessResponse":
        success = _required_bool(result, "success", f"{root_field}.success")
    return DeleteDriverResult(typename, success)


def parse_update_driver(data: Mapping[str, object]) -> UpdateDriverResult | None:
    """Parse UpdateDriver's known success branch and preserve future types."""

    root_field = "updateDriver"
    result = _root(data, root_field)
    if result is None:
        return None
    typename = _typename(result, root_field)
    driver = None
    if typename == "UpdateDriverSuccessResponse":
        driver = UpdateDriverSuccess(
            entitlements=_required_string_tuple(
                result,
                "entitlements",
                f"{root_field}.entitlements",
            ),
            usage_history=_required_bool(
                result,
                "usageHistory",
                f"{root_field}.usageHistory",
            ),
            notifications_to_primary=_required_bool(
                result,
                "notificationsToPrimary",
                f"{root_field}.notificationsToPrimary",
            ),
            success=_required_bool(result, "success", f"{root_field}.success"),
        )
    return UpdateDriverResult(typename, driver)


def parse_owner_invite_action(
    data: Mapping[str, object],
) -> OwnerInviteActionResult | None:
    """Parse OwnerInviteAction's known success branch and preserve future types."""

    root_field = "ownerInviteAction"
    result = _root(data, root_field)
    if result is None:
        return None
    typename = _typename(result, root_field)
    success = None
    if typename == "OwnerInviteActionSuccessResponse":
        success = _required_bool(result, "success", f"{root_field}.success")
    return OwnerInviteActionResult(typename, success)


def parse_create_rsa_link(data: Mapping[str, object]) -> CreateRSALinkResult | None:
    """Parse CreateRSALink's nullable direct response and link."""

    root_field = "createRSALink"
    result = _root(data, root_field)
    if result is None:
        return None
    return CreateRSALinkResult(
        _typename(result, root_field),
        _required_nullable_string(result, "link", f"{root_field}.link"),
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


def _root(
    data: Mapping[str, object],
    root_field: str,
) -> Mapping[str, object] | None:
    value = _required_value(data, root_field, root_field)
    if value is None:
        return None
    return _typed_object(value, root_field)


def _typed_object(value: object, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ResponseError(f"{path} is not an object")
    _typename(value, path)
    return value


def _typename(container: Mapping[str, object], path: str) -> str:
    return _required_string(container, "__typename", f"{path}.__typename")


def _required_value(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> object:
    if field not in container:
        raise ResponseError(f"{path} is missing")
    return container[field]


def _required_string(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> str:
    return _string(_required_value(container, field, path), path)


def _required_nullable_string(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> str | None:
    value = _required_value(container, field, path)
    if value is None:
        return None
    return _string(value, path)


def _required_bool(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> bool:
    value = _required_value(container, field, path)
    if not isinstance(value, bool):
        raise ResponseError(f"{path} is not a boolean")
    return value


def _required_nullable_bool(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> bool | None:
    value = _required_value(container, field, path)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ResponseError(f"{path} is not a boolean")
    return value


def _required_list(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> list[object]:
    value = _required_value(container, field, path)
    if not isinstance(value, list):
        raise ResponseError(f"{path} is not a list")
    return value


def _nullable_list(value: object, path: str) -> list[object] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        raise ResponseError(f"{path} is not a list")
    return value


def _required_string_tuple(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> tuple[str, ...]:
    values = _required_list(container, field, path)
    return tuple(_string(value, f"{path}[{index}]") for index, value in enumerate(values))


def _string(value: object, path: str) -> str:
    if not isinstance(value, str):
        raise ResponseError(f"{path} is not a string")
    return value


def _required_datetime(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> datetime:
    raw_value = _required_string(container, field, path)
    normalized = f"{raw_value[:-1]}+00:00" if raw_value.endswith("Z") else raw_value
    try:
        result = datetime.fromisoformat(normalized)
    except ValueError as error:
        raise ResponseError(f"{path} is not an ISO-8601 date-time") from error
    if result.tzinfo is None or result.utcoffset() is None:
        raise ResponseError(f"{path} is not an ISO-8601 date-time with an offset")
    return result


def _required_enum[EnumT: StrEnum](
    container: Mapping[str, object],
    field: str,
    enum_type: type[EnumT],
    path: str,
) -> EnumT:
    return _enum(_required_value(container, field, path), enum_type, path)


def _required_nullable_enum[EnumT: StrEnum](
    container: Mapping[str, object],
    field: str,
    enum_type: type[EnumT],
    path: str,
) -> EnumT | None:
    value = _required_value(container, field, path)
    if value is None:
        return None
    return _enum(value, enum_type, path)


def _enum[EnumT: StrEnum](value: object, enum_type: type[EnumT], path: str) -> EnumT:
    raw_value = _string(value, path)
    try:
        return enum_type(raw_value)
    except ValueError:
        return enum_type("UNKNOWN__")
