from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

from .driver_models import (
    DriverInviteAction,
    EmergencyContactRelationship,
    InviteNotificationType,
    OwnerInviteAction,
)
from .graphql_input import UNSET, UnsetType, optional_input_fields, serialize_enum


@dataclass(frozen=True, slots=True)
class CreateEmergencyContactInput:
    """Required and optional fields for a new emergency contact."""

    first_name: str
    last_name: str
    primary_phone: str
    relationship: EmergencyContactRelationship
    secondary_phone: str | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class UpdateEmergencyContactInput:
    """Emergency-contact patch with Apollo omission semantics."""

    emergency_contact_id: str
    first_name: str | UnsetType | None = UNSET
    last_name: str | UnsetType | None = UNSET
    primary_phone: str | UnsetType | None = UNSET
    secondary_phone: str | UnsetType | None = UNSET
    relationship: EmergencyContactRelationship | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class DriverInviteInput:
    """Required identity, permissions, and delivery channel for a driver invite."""

    driver_first_name: str
    driver_last_name: str
    driver_email: str
    driver_phone_number: str
    vin: str
    entitlements: tuple[str, ...]
    invite_type: InviteNotificationType
    usage_history: bool
    notifications_to_primary: bool


@dataclass(frozen=True, slots=True)
class DriverInviteActionInput:
    """Prospective-driver action with optional terms acceptance."""

    invite_id: str
    action: DriverInviteAction
    terms_and_conditions: bool | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class UpdateDriverInput:
    """Required replacement permissions for an invited driver."""

    invite_id: str
    entitlements: tuple[str, ...]
    usage_history: bool
    notifications_to_primary: bool


@dataclass(frozen=True, slots=True)
class OwnerInviteActionInput:
    """Owner action and notification channel for a driver invitation."""

    invite_id: str
    action: OwnerInviteAction
    notification_type: InviteNotificationType


def emergency_contacts_variables(vin: str) -> dict[str, object]:
    """Serialize the required VIN for the EmergencyContacts query."""

    return {"vin": vin}


def create_emergency_contact_variables(
    vin: str,
    contact: CreateEmergencyContactInput,
) -> dict[str, object]:
    """Serialize a complete emergency-contact creation request."""

    return {"vin": vin, "contact": create_emergency_contact_input(contact)}


def update_emergency_contact_variables(
    vin: str,
    contact: UpdateEmergencyContactInput,
) -> dict[str, object]:
    """Serialize an emergency-contact patch without inventing omitted fields."""

    return {"vin": vin, "contact": update_emergency_contact_input(contact)}


def delete_emergency_contact_variables(
    vin: str,
    emergency_contact_id: str,
) -> dict[str, object]:
    """Serialize the required emergency-contact deletion identifiers."""

    return {"vin": vin, "emergencyContactId": emergency_contact_id}


def driver_invites_variables(vin: str) -> dict[str, object]:
    """Serialize the required VIN for the DriverInvites query."""

    return {"vin": vin}


def invite_driver_variables(
    config: DriverInviteInput | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize InviteDriver's nullable Apollo-optional config variable."""

    return optional_input_fields(config=_optional_input(config, driver_invite_input))


def driver_invite_action_variables(
    config: DriverInviteActionInput | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize DriverInviteAction's nullable Apollo-optional config variable."""

    return optional_input_fields(config=_optional_input(config, driver_invite_action_input))


def delete_driver_variables(invite_id: str) -> dict[str, object]:
    """Serialize the required invitation ID for DeleteDriver."""

    return {"inviteId": invite_id}


def update_driver_variables(config: UpdateDriverInput) -> dict[str, object]:
    """Serialize the required UpdateDriver config variable."""

    return {"config": update_driver_input(config)}


def owner_invite_action_variables(
    config: OwnerInviteActionInput | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize OwnerInviteAction's nullable Apollo-optional config variable."""

    return optional_input_fields(config=_optional_input(config, owner_invite_action_input))


def create_rsa_link_variables(vin: str) -> dict[str, object]:
    """Serialize the required VIN for CreateRSALink."""

    return {"vin": vin}


def create_emergency_contact_input(
    value: CreateEmergencyContactInput,
) -> dict[str, object]:
    """Serialize a CreateEmergencyContact input object."""

    return optional_input_fields(
        firstName=value.first_name,
        lastName=value.last_name,
        primaryPhone=value.primary_phone,
        secondaryPhone=value.secondary_phone,
        relationship=serialize_enum(value.relationship),
    )


def update_emergency_contact_input(
    value: UpdateEmergencyContactInput,
) -> dict[str, object]:
    """Serialize an UpdateEmergencyContact input object."""

    return optional_input_fields(
        emergencyContactId=value.emergency_contact_id,
        firstName=value.first_name,
        lastName=value.last_name,
        primaryPhone=value.primary_phone,
        secondaryPhone=value.secondary_phone,
        relationship=_optional_enum(value.relationship),
    )


def driver_invite_input(value: DriverInviteInput) -> dict[str, object]:
    """Serialize a DriverInviteInput object."""

    return {
        "driverFirstName": value.driver_first_name,
        "driverLastName": value.driver_last_name,
        "driverEmail": value.driver_email,
        "driverPhoneNumber": value.driver_phone_number,
        "vin": value.vin,
        "entitlements": list(value.entitlements),
        "inviteType": serialize_enum(value.invite_type),
        "usageHistory": value.usage_history,
        "notificationsToPrimary": value.notifications_to_primary,
    }


def driver_invite_action_input(value: DriverInviteActionInput) -> dict[str, object]:
    """Serialize a DriverInviteActionInput object."""

    return optional_input_fields(
        inviteId=value.invite_id,
        action=serialize_enum(value.action),
        termsAndConditions=value.terms_and_conditions,
    )


def update_driver_input(value: UpdateDriverInput) -> dict[str, object]:
    """Serialize an UpdateDriverInput object."""

    return {
        "inviteId": value.invite_id,
        "entitlements": list(value.entitlements),
        "usageHistory": value.usage_history,
        "notificationsToPrimary": value.notifications_to_primary,
    }


def owner_invite_action_input(value: OwnerInviteActionInput) -> dict[str, object]:
    """Serialize an OwnerInviteActionInput object."""

    return {
        "inviteId": value.invite_id,
        "action": serialize_enum(value.action),
        "notificationType": serialize_enum(value.notification_type),
    }


def _optional_enum(value: StrEnum | UnsetType | None) -> object:
    if isinstance(value, UnsetType) or value is None:
        return value
    return serialize_enum(value)


def _optional_input[InputT](
    value: InputT | UnsetType | None,
    serializer: Callable[[InputT], dict[str, object]],
) -> object:
    if isinstance(value, UnsetType) or value is None:
        return value
    return serializer(value)
