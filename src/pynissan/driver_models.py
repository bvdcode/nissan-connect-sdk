from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class EmergencyContactRelationship(StrEnum):
    """Known emergency-contact relationships accepted and returned by Nissan."""

    ASSISTANT = "ASSISTANT"
    BROTHER = "BROTHER"
    BUSINESS_CONTACT = "BUSINESS_CONTACT"
    CHAUFFEUR = "CHAUFFEUR"
    CO_WORKER = "CO_WORKER"
    DAUGHTER = "DAUGHTER"
    DOCTOR = "DOCTOR"
    EMPLOYEE = "EMPLOYEE"
    FATHER = "FATHER"
    FIANCE = "FIANCE"
    FIANCEE = "FIANCEE"
    FRIEND = "FRIEND"
    GRANDFATHER = "GRANDFATHER"
    GRANDMOTHER = "GRANDMOTHER"
    MOTHER = "MOTHER"
    OTHER = "OTHER"
    PARENTS = "PARENTS"
    PARTNER = "PARTNER"
    RELATIVE = "RELATIVE"
    SIGNIFICANT_OTHER = "SIGNIFICANT_OTHER"
    SISTER = "SISTER"
    SON = "SON"
    SPOUSE = "SPOUSE"
    UNKNOWN_VALUE = "UNKNOWN__"


class InviteNotificationType(StrEnum):
    """Known notification channels for driver invitations."""

    SMS = "SMS"
    EMAIL = "EMAIL"
    UNKNOWN_VALUE = "UNKNOWN__"


class InviteStatus(StrEnum):
    """Known driver-invitation states returned by Nissan."""

    ACCEPTED = "ACCEPTED"
    PENDING = "PENDING"
    DECLINE = "DECLINE"
    REMOVED = "REMOVED"
    CANCEL = "CANCEL"
    EXPIRED = "EXPIRED"
    INVALIDATE = "INVALIDATE"
    NONE = "NONE"
    UNKNOWN_VALUE = "UNKNOWN__"


class DriverInviteAction(StrEnum):
    """Known actions a prospective driver can take on an invitation."""

    DECLINE = "DECLINE"
    ACCEPT = "ACCEPT"
    INVALIDATE = "INVALIDATE"
    UNKNOWN_VALUE = "UNKNOWN__"


class OwnerInviteAction(StrEnum):
    """Known actions an owner can take on a driver invitation."""

    RESEND = "RESEND"
    CANCEL = "CANCEL"
    UNKNOWN_VALUE = "UNKNOWN__"


@dataclass(frozen=True, slots=True)
class EmergencyContact:
    """One nullable-field emergency contact returned for a vehicle."""

    typename: str
    id: str | None
    first_name: str | None
    last_name: str | None
    primary_phone: str | None
    secondary_phone: str | None
    relationship: EmergencyContactRelationship | None


@dataclass(frozen=True, slots=True)
class EmergencyContactsResult:
    """Vehicle type and emergency contacts selected by the vehicle fragment."""

    typename: str
    emergency_contacts: tuple[EmergencyContact | None, ...] | None


@dataclass(frozen=True, slots=True)
class CreateEmergencyContactResult:
    """Nullable response status returned after creating an emergency contact."""

    typename: str
    success: bool | None


@dataclass(frozen=True, slots=True)
class UpdateEmergencyContactResult:
    """Nullable response status returned after updating an emergency contact."""

    typename: str
    success: bool | None


@dataclass(frozen=True, slots=True)
class DeleteEmergencyContactResult:
    """Nullable response status returned after deleting an emergency contact."""

    typename: str
    success: bool | None


@dataclass(frozen=True, slots=True)
class DriverOperationError:
    """A known driver-operation error branch and its server message."""

    typename: str
    error_message: str


@dataclass(frozen=True, slots=True)
class DriverInvite:
    """One current driver invitation returned by Nissan."""

    typename: str
    invite_id: str
    driver_first_name: str
    driver_last_name: str
    driver_email: str
    driver_phone_number: str
    invite_date_time: datetime
    invite_expiry_date_time: datetime
    invite_type: InviteNotificationType
    notifications_to_primary: bool
    usage_history: bool
    status: InviteStatus
    cdiid: str | None


@dataclass(frozen=True, slots=True)
class DriverInvitesResult:
    """Future-safe union result for the DriverInvites query."""

    typename: str
    invites: tuple[DriverInvite, ...] | None
    error: DriverOperationError | None


@dataclass(frozen=True, slots=True)
class InviteDriverSuccess:
    """Driver invitation returned by a successful InviteDriver mutation."""

    vin: str
    invite_id: str
    driver_first_name: str
    driver_last_name: str
    driver_email: str
    driver_phone_number: str
    entitlements: tuple[str, ...]
    invite_type: InviteNotificationType
    usage_history: bool
    notifications_to_primary: bool
    invite_date_time: datetime
    status: InviteStatus


@dataclass(frozen=True, slots=True)
class InviteDriverResult:
    """Future-safe success or validation-error result for InviteDriver."""

    typename: str
    invitation: InviteDriverSuccess | None
    error: DriverOperationError | None


@dataclass(frozen=True, slots=True)
class DriverInviteActionResult:
    """Future-safe result for a prospective driver's invitation action."""

    typename: str
    success: bool | None
    error: DriverOperationError | None


@dataclass(frozen=True, slots=True)
class DeleteDriverResult:
    """Future-safe result for deleting a driver invitation."""

    typename: str
    success: bool | None


@dataclass(frozen=True, slots=True)
class UpdateDriverSuccess:
    """Driver permissions returned by a successful UpdateDriver mutation."""

    entitlements: tuple[str, ...]
    usage_history: bool
    notifications_to_primary: bool
    success: bool


@dataclass(frozen=True, slots=True)
class UpdateDriverResult:
    """Future-safe result for updating a driver's permissions."""

    typename: str
    driver: UpdateDriverSuccess | None


@dataclass(frozen=True, slots=True)
class OwnerInviteActionResult:
    """Future-safe result for an owner's invitation action."""

    typename: str
    success: bool | None


@dataclass(frozen=True, slots=True)
class CreateRSALinkResult:
    """Nullable roadside-assistance link returned for a vehicle."""

    typename: str
    link: str | None
