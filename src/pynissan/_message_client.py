from __future__ import annotations

from . import operations
from ._client_base import _NissanClientBase
from .device_notification_inputs import (
    in_vehicle_message_variables,
    in_vehicle_messages_variables,
)
from .device_notification_models import (
    InVehicleMessage,
    InVehicleMessageSummary,
)
from .device_notification_parsing import (
    parse_in_vehicle_message,
    parse_in_vehicle_messages,
)
from .graphql_input import UnsetType
from .notification_models import (
    NissanEnergyNotificationPreferences,
    NotificationPreference,
)
from .notification_parsing import (
    parse_nissan_energy_notification_preferences,
    parse_notification_preferences,
)
from .ota_models import OtaUpdate, OtaUpdateProgress
from .ota_parsing import parse_ota_update, parse_ota_update_progress


class _MessageClientMixin(_NissanClientBase):
    async def async_get_ota_update(self, vin: str) -> OtaUpdate | None:
        """Return the OTA campaign currently offered to a compatible vehicle."""

        data = await self._transport.async_graphql(
            "OtaUpdate",
            operations.OTA_UPDATE,
            {"vin": vin},
        )
        return parse_ota_update(data)

    async def async_get_ota_update_progress(
        self,
        vin: str,
        campaign_operation_id: str,
    ) -> OtaUpdateProgress | None:
        """Return download or activation progress for one OTA campaign."""

        data = await self._transport.async_graphql(
            "OtaUpdateProgress",
            operations.OTA_UPDATE_PROGRESS,
            {
                "campaignOperationId": campaign_operation_id,
                "vin": vin,
            },
        )
        return parse_ota_update_progress(data)

    async def async_get_notification_preferences(
        self,
        vin: str,
    ) -> tuple[NotificationPreference | None, ...] | None:
        """Return vehicle notification opt-ins grouped by category."""

        data = await self._transport.async_graphql(
            "NotificationPreferences",
            operations.NOTIFICATION_PREFERENCES,
            {"vin": vin},
        )
        return parse_notification_preferences(data)

    async def async_get_nissan_energy_notification_preferences(
        self,
        vin: str,
    ) -> NissanEnergyNotificationPreferences | None:
        """Return Nissan Energy Charge Network delivery preferences."""

        data = await self._transport.async_graphql(
            "NissanEnergyNotificationPreferences",
            operations.NISSAN_ENERGY_NOTIFICATION_PREFERENCES,
            {"vin": vin},
        )
        return parse_nissan_energy_notification_preferences(data)

    async def async_get_in_vehicle_messages(
        self,
        vin: str,
    ) -> tuple[InVehicleMessageSummary | None, ...] | None:
        """Return the vehicle's nullable in-vehicle message summaries."""

        data = await self._transport.async_graphql(
            "InVehicleMessages",
            operations.IN_VEHICLE_MESSAGES,
            in_vehicle_messages_variables(vin),
        )
        return parse_in_vehicle_messages(data)

    async def async_get_in_vehicle_message(
        self,
        vin: str,
        campaign_id: str,
        *,
        push: bool | UnsetType | None = False,
    ) -> InVehicleMessage | None:
        """Fetch one message, allowing Nissan to record the detail as viewed."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "InVehicleMessage",
            operations.IN_VEHICLE_MESSAGE,
            in_vehicle_message_variables(vin, campaign_id, push=push),
        )
        return parse_in_vehicle_message(data)
