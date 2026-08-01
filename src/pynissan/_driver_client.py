from __future__ import annotations

from . import operations
from ._client_base import _NissanClientBase
from .driver_inputs import (
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
from .driver_models import (
    CreateEmergencyContactResult,
    CreateRSALinkResult,
    DeleteDriverResult,
    DeleteEmergencyContactResult,
    DriverInviteActionResult,
    DriverInvitesResult,
    EmergencyContactsResult,
    InviteDriverResult,
    OwnerInviteActionResult,
    UpdateDriverResult,
    UpdateEmergencyContactResult,
)
from .driver_parsing import (
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
from .graphql_input import UNSET, UnsetType


class _DriverClientMixin(_NissanClientBase):
    async def async_get_emergency_contacts(
        self,
        vin: str,
    ) -> EmergencyContactsResult | None:
        """Return emergency contacts configured for a vehicle."""

        data = await self._transport.async_graphql(
            "EmergencyContacts",
            operations.EMERGENCY_CONTACTS,
            emergency_contacts_variables(vin),
        )
        return parse_emergency_contacts(data)

    async def async_create_emergency_contact(
        self,
        vin: str,
        contact: CreateEmergencyContactInput,
    ) -> CreateEmergencyContactResult | None:
        """Create an emergency contact for a vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CreateEmergencyContact",
            operations.CREATE_EMERGENCY_CONTACT,
            create_emergency_contact_variables(vin, contact),
        )
        return parse_create_emergency_contact(data)

    async def async_update_emergency_contact(
        self,
        vin: str,
        contact: UpdateEmergencyContactInput,
    ) -> UpdateEmergencyContactResult | None:
        """Update an emergency contact configured for a vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateEmergencyContact",
            operations.UPDATE_EMERGENCY_CONTACT,
            update_emergency_contact_variables(vin, contact),
        )
        return parse_update_emergency_contact(data)

    async def async_delete_emergency_contact(
        self,
        vin: str,
        emergency_contact_id: str,
    ) -> DeleteEmergencyContactResult | None:
        """Delete an emergency contact configured for a vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "DeleteEmergencyContact",
            operations.DELETE_EMERGENCY_CONTACT,
            delete_emergency_contact_variables(vin, emergency_contact_id),
        )
        return parse_delete_emergency_contact(data)

    async def async_get_driver_invites(self, vin: str) -> DriverInvitesResult | None:
        """Return shared-driver invitations for a vehicle."""

        data = await self._transport.async_graphql(
            "DriverInvites",
            operations.DRIVER_INVITES,
            driver_invites_variables(vin),
        )
        return parse_driver_invites(data)

    async def async_invite_driver(
        self,
        config: DriverInviteInput | UnsetType | None = UNSET,
    ) -> InviteDriverResult | None:
        """Invite another account to drive a vehicle with selected permissions."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "InviteDriver",
            operations.INVITE_DRIVER,
            invite_driver_variables(config),
        )
        return parse_invite_driver(data)

    async def async_driver_invite_action(
        self,
        config: DriverInviteActionInput | UnsetType | None = UNSET,
    ) -> DriverInviteActionResult | None:
        """Accept, decline, or invalidate a received driver invitation."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "DriverInviteAction",
            operations.DRIVER_INVITE_ACTION,
            driver_invite_action_variables(config),
        )
        return parse_driver_invite_action(data)

    async def async_delete_driver(self, invite_id: str) -> DeleteDriverResult | None:
        """Remove a shared driver or invitation from the account."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "DeleteDriver",
            operations.DELETE_DRIVER,
            delete_driver_variables(invite_id),
        )
        return parse_delete_driver(data)

    async def async_update_driver(
        self,
        config: UpdateDriverInput,
    ) -> UpdateDriverResult | None:
        """Replace a shared driver's permissions and notification settings."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateDriver",
            operations.UPDATE_DRIVER,
            update_driver_variables(config),
        )
        return parse_update_driver(data)

    async def async_owner_invite_action(
        self,
        config: OwnerInviteActionInput | UnsetType | None = UNSET,
    ) -> OwnerInviteActionResult | None:
        """Resend or cancel a shared-driver invitation as the vehicle owner."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "OwnerInviteAction",
            operations.OWNER_INVITE_ACTION,
            owner_invite_action_variables(config),
        )
        return parse_owner_invite_action(data)

    async def async_create_rsa_link(self, vin: str) -> CreateRSALinkResult | None:
        """Create the roadside-assistance link associated with a vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CreateRSALink",
            operations.CREATE_RSA_LINK,
            create_rsa_link_variables(vin),
        )
        return parse_create_rsa_link(data)
