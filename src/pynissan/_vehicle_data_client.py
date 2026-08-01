from __future__ import annotations

from . import operations
from ._client_base import _NissanClientBase
from .graphql_input import UNSET, UnsetType
from .maintenance_inputs import (
    CreatePartsReminderInput,
    PastServiceInput,
    ResetPartsReminderInput,
    UpdatePartsReminderInput,
    UpdatePastServiceInput,
    add_past_service_variables,
    collision_history_variables,
    collision_probe_data_variables,
    create_parts_reminder_variables,
    delete_parts_reminder_variables,
    get_maintenance_timeline_variables,
    get_service_contracts_variables,
    parts_reminders_variables,
    reset_parts_reminder_variables,
    update_parts_reminder_variables,
    update_past_service_variables,
)
from .maintenance_models import (
    CollisionHistoryEntry,
    CollisionProbeReading,
    MaintenanceTimeline,
    PartsReminderMutationResult,
    PastServiceResult,
    ServiceContract,
    VehiclePartsReminders,
)
from .maintenance_parsing import (
    parse_add_past_service,
    parse_collision_history,
    parse_collision_probe_data,
    parse_create_parts_reminder,
    parse_delete_parts_reminder,
    parse_maintenance_timeline,
    parse_parts_reminders,
    parse_reset_parts_reminder,
    parse_service_contracts,
    parse_update_parts_reminder,
    parse_update_past_service,
)
from .models import (
    DataPrivacyMode,
    DistanceUnit,
    RemoteServiceHistory,
    VehiclePreferences,
    VehicleSubscriptions,
    VehicleWifiConsumption,
)
from .parsing import (
    parse_remote_service_history,
    parse_vehicle_data_privacy_mode,
    parse_vehicle_preferences,
    parse_vehicle_subscriptions,
    parse_vehicle_wifi_consumption,
)


class _VehicleDataClientMixin(_NissanClientBase):
    async def async_get_vehicle_data_privacy_mode(
        self,
        vin: str,
    ) -> DataPrivacyMode | None:
        """Return the vehicle's current data privacy mode."""

        data = await self._transport.async_graphql(
            "VehicleDataPrivacyMode",
            operations.VEHICLE_DATA_PRIVACY_MODE,
            {"vin": vin},
        )
        return parse_vehicle_data_privacy_mode(data)

    async def async_get_vehicle_wifi_consumption(
        self,
        vin: str,
    ) -> VehicleWifiConsumption | None:
        """Return current in-vehicle Wi-Fi consumption when available."""

        data = await self._transport.async_graphql(
            "VehicleWifiConsumption",
            operations.VEHICLE_WIFI_CONSUMPTION,
            {"vin": vin},
        )
        return parse_vehicle_wifi_consumption(data)

    async def async_get_vehicle_preferences(
        self,
        vin: str,
    ) -> VehiclePreferences | None:
        """Return MIL/DTC maintenance-data sharing preferences when available."""

        data = await self._transport.async_graphql(
            "VehiclePreferences",
            operations.VEHICLE_PREFERENCES,
            {"vin": vin},
        )
        return parse_vehicle_preferences(data)

    async def async_get_vehicle_subscriptions(
        self,
        vin: str,
    ) -> VehicleSubscriptions | None:
        """Return the vehicle subscription capability without app-level filtering."""

        data = await self._transport.async_graphql(
            "VehicleSubscriptions",
            operations.VEHICLE_SUBSCRIPTIONS,
            {"vin": vin},
        )
        return parse_vehicle_subscriptions(data, vin)

    async def async_update_vehicle_preferences(
        self,
        vin: str,
        preferences: VehiclePreferences,
    ) -> bool:
        """Replace all MIL/DTC maintenance-data sharing preferences."""

        return await self._async_success_operation(
            "UpdateVehiclePreferences",
            operations.UPDATE_VEHICLE_PREFERENCES,
            "updateVehiclePreferences",
            {
                "vin": vin,
                "communication": {
                    "milDataSharing": {
                        "enabled": preferences.enabled,
                        "text": preferences.text,
                        "phone": preferences.phone,
                        "email": preferences.email,
                    }
                },
            },
        )

    async def async_get_remote_service_history(
        self,
        vin: str,
        *,
        page_number: int,
        items_per_page: int,
    ) -> RemoteServiceHistory | None:
        """Return one page of raw remote-service request history."""

        data = await self._transport.async_graphql(
            "RemoteServiceHistory",
            operations.REMOTE_SERVICE_HISTORY,
            {
                "vin": vin,
                "pageNumber": page_number,
                "itemsPerPage": items_per_page,
            },
        )
        return parse_remote_service_history(data)

    async def async_get_maintenance_timeline(
        self,
        vin: str,
        mileage_unit: DistanceUnit = DistanceUnit.MILE,
    ) -> MaintenanceTimeline | None:
        """Return the vehicle's current and projected maintenance milestones."""

        data = await self._transport.async_graphql(
            "GetMaintenanceTimeline",
            operations.GET_MAINTENANCE_TIMELINE,
            get_maintenance_timeline_variables(vin, mileage_unit),
        )
        return parse_maintenance_timeline(data)

    async def async_get_service_contracts(
        self,
        vin: str,
        mileage: int,
    ) -> tuple[ServiceContract | None, ...] | None:
        """Return warranty service contracts evaluated at the supplied mileage."""

        data = await self._transport.async_graphql(
            "GetServiceContracts",
            operations.GET_SERVICE_CONTRACTS,
            get_service_contracts_variables(vin, mileage),
        )
        return parse_service_contracts(data)

    async def async_add_past_service(
        self,
        service: PastServiceInput | UnsetType | None = UNSET,
    ) -> PastServiceResult | None:
        """Add a completed maintenance record to the account."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "AddPastService",
            operations.ADD_PAST_SERVICE,
            add_past_service_variables(service),
        )
        return parse_add_past_service(data)

    async def async_update_past_service(
        self,
        service: UpdatePastServiceInput,
    ) -> PastServiceResult | None:
        """Replace a completed maintenance record."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdatePastService",
            operations.UPDATE_PAST_SERVICE,
            update_past_service_variables(service),
        )
        return parse_update_past_service(data)

    async def async_get_parts_reminders(
        self,
        vin: str,
        *,
        unit: DistanceUnit | UnsetType | None = UNSET,
    ) -> VehiclePartsReminders | None:
        """Return the vehicle's service-part catalog and configured reminders."""

        data = await self._transport.async_graphql(
            "PartsReminders",
            operations.PARTS_REMINDERS,
            parts_reminders_variables(vin, unit=unit),
        )
        return parse_parts_reminders(data)

    async def async_create_parts_reminder(
        self,
        vin: str,
        reminder: CreatePartsReminderInput,
    ) -> PartsReminderMutationResult | None:
        """Create a service-parts reminder for a vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CreatePartsReminder",
            operations.CREATE_PARTS_REMINDER,
            create_parts_reminder_variables(vin, reminder),
        )
        return parse_create_parts_reminder(data)

    async def async_update_parts_reminder(
        self,
        vin: str,
        reminder: UpdatePartsReminderInput,
    ) -> PartsReminderMutationResult | None:
        """Replace a service-parts reminder for a vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdatePartsReminder",
            operations.UPDATE_PARTS_REMINDER,
            update_parts_reminder_variables(vin, reminder),
        )
        return parse_update_parts_reminder(data)

    async def async_reset_parts_reminder(
        self,
        vin: str,
        reminder: ResetPartsReminderInput,
    ) -> PartsReminderMutationResult | None:
        """Reset a service-parts reminder schedule."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "ResetPartsReminder",
            operations.RESET_PARTS_REMINDER,
            reset_parts_reminder_variables(vin, reminder),
        )
        return parse_reset_parts_reminder(data)

    async def async_delete_parts_reminder(
        self,
        vin: str,
        reminder_id: str,
    ) -> PartsReminderMutationResult | None:
        """Delete a service-parts reminder from a vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "DeletePartsReminder",
            operations.DELETE_PARTS_REMINDER,
            delete_parts_reminder_variables(vin, reminder_id),
        )
        return parse_delete_parts_reminder(data)

    async def async_get_collision_history(
        self,
        vin: str,
    ) -> tuple[CollisionHistoryEntry | None, ...] | None:
        """Return collision reports attached to the vehicle account."""

        data = await self._transport.async_graphql(
            "CollisionHistory",
            operations.COLLISION_HISTORY,
            collision_history_variables(vin),
        )
        return parse_collision_history(data)

    async def async_get_collision_probe_data(
        self,
        vin: str,
    ) -> tuple[CollisionProbeReading | None, ...] | None:
        """Return vehicle telemetry captured for a collision report."""

        data = await self._transport.async_graphql(
            "CollisionProbeData",
            operations.COLLISION_PROBE_DATA,
            collision_probe_data_variables(vin),
        )
        return parse_collision_probe_data(data)
