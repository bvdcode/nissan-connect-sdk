from __future__ import annotations

from collections.abc import Mapping

from ._driver_detail_parsing import (
    _parse_driver_invite,
    _parse_emergency_contact,
    _parse_error,
    _parse_invite_driver_success,
)
from ._driver_value_parsing import (
    _nullable_list,
    _required_bool,
    _required_list,
    _required_nullable_bool,
    _required_nullable_string,
    _required_string_tuple,
    _required_value,
    _root,
    _typename,
)
from .driver_models import (
    CreateEmergencyContactResult,
    CreateRSALinkResult,
    DeleteDriverResult,
    DeleteEmergencyContactResult,
    DriverInviteActionResult,
    DriverInvitesResult,
    EmergencyContact,
    EmergencyContactsResult,
    InviteDriverResult,
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
