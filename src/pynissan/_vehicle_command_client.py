from __future__ import annotations

from . import operations
from ._client_base import _NissanClientBase
from ._client_helpers import (
    _charge_schedule_input,
    _climate_parameters_input,
    _climate_schedule_input,
    _optional_variables,
    _temperature_input,
)
from .models import (
    ChargeScheduleInput,
    ClimateScheduleInput,
    ClimateSettings,
    ServiceRequest,
    ServiceRequestKind,
)


class _VehicleCommandClientMixin(_NissanClientBase):
    async def async_lock_doors(self, vin: str) -> ServiceRequest:
        """Lock the vehicle doors."""

        return await self._async_simple_service_request(
            "DoorLock",
            operations.DOOR_LOCK,
            "doorLock",
            vin,
            ServiceRequestKind.DOOR,
        )

    async def async_unlock_doors(self, vin: str) -> ServiceRequest:
        """Unlock the vehicle doors."""

        return await self._async_simple_service_request(
            "DoorUnlock",
            operations.DOOR_UNLOCK,
            "doorUnlock",
            vin,
            ServiceRequestKind.DOOR,
        )

    async def async_flash_lights(self, vin: str) -> ServiceRequest:
        """Flash the vehicle lights."""

        return await self._async_simple_service_request(
            "FlashLights",
            operations.FLASH_LIGHTS,
            "flashLights",
            vin,
            ServiceRequestKind.HORN_LIGHT,
        )

    async def async_flash_lights_and_horn(self, vin: str) -> ServiceRequest:
        """Flash the lights and sound the horn."""

        return await self._async_simple_service_request(
            "FlashLightsHorn",
            operations.FLASH_LIGHTS_HORN,
            "flashLightsHorn",
            vin,
            ServiceRequestKind.HORN_LIGHT,
        )

    async def async_locate_vehicle(self, vin: str) -> ServiceRequest:
        """Request a fresh vehicle location."""

        return await self._async_simple_service_request(
            "LocateVehicle",
            operations.LOCATE_VEHICLE,
            "locateVehicle",
            vin,
            ServiceRequestKind.LOCATION,
        )

    async def async_start_engine(
        self,
        vin: str,
        *,
        climate: ClimateSettings | None = None,
        set_as_default: bool | None = None,
    ) -> ServiceRequest:
        """Start the engine, optionally with a climate configuration."""

        engine_climate = None
        if climate is not None:
            engine_climate = _optional_variables(
                temperature=_temperature_input(climate),
                parameters=_climate_parameters_input(climate.parameters),
            )
        return await self._async_service_request(
            "EngineStart",
            operations.ENGINE_START,
            "engineStart",
            _optional_variables(
                vin=vin,
                climate=engine_climate,
                setAsDefault=set_as_default,
            ),
            ServiceRequestKind.ENGINE,
        )

    async def async_stop_engine(self, vin: str) -> ServiceRequest:
        """Stop a remotely started engine."""

        return await self._async_simple_service_request(
            "EngineStop",
            operations.ENGINE_STOP,
            "engineStop",
            vin,
            ServiceRequestKind.ENGINE,
        )

    async def async_refresh_vehicle_status(self, vin: str) -> ServiceRequest:
        """Ask the vehicle to publish fresh dynamic status."""

        return await self._async_simple_service_request(
            "RefreshVehicleStatus",
            operations.REFRESH_VEHICLE_STATUS,
            "refreshVehicleStatus",
            vin,
            ServiceRequestKind.VEHICLE_STATUS,
        )

    async def async_refresh_battery_status(self, vin: str) -> bool:
        """Ask the electric vehicle to refresh its battery status."""

        return await self._async_success_operation(
            "RefreshBatteryStatus",
            operations.REFRESH_BATTERY_STATUS,
            "refreshBatteryStatus",
            {"vin": vin},
        )

    async def async_refresh_climate_status(self, vin: str) -> bool:
        """Ask the vehicle to refresh its climate status."""

        return await self._async_success_operation(
            "RefreshClimateStatus",
            operations.REFRESH_CLIMATE_STATUS,
            "refreshClimateStatus",
            {"vin": vin},
        )

    async def async_wake_up_vehicle(self, vin: str) -> bool:
        """Wake the vehicle telematics unit."""

        return await self._async_success_operation(
            "WakeUpVehicle",
            operations.WAKE_UP_VEHICLE,
            "wakeUp",
            {"vin": vin},
        )

    async def async_take_photos_around_vehicle(self, vin: str) -> ServiceRequest:
        """Request exterior camera photos on supported vehicles."""

        return await self._async_simple_service_request(
            "TakePhotosAroundVehicle",
            operations.TAKE_PHOTOS_AROUND_VEHICLE,
            "takePhotosAroundVehicle",
            vin,
            ServiceRequestKind.PHOTO,
        )

    async def async_create_charge_schedule(
        self,
        vin: str,
        schedule: ChargeScheduleInput,
    ) -> ServiceRequest:
        """Create a recurring charge schedule."""

        return await self._async_service_request(
            "CreateChargeSchedule",
            operations.CREATE_CHARGE_SCHEDULE,
            "createChargeSchedule",
            {"vin": vin, "schedule": _charge_schedule_input(schedule)},
            ServiceRequestKind.CHARGE_CONFIGURATION,
        )

    async def async_update_charge_schedule(
        self,
        vin: str,
        schedule_id: str,
        schedule: ChargeScheduleInput,
    ) -> ServiceRequest:
        """Replace a recurring charge schedule."""

        schedule_input = {"id": schedule_id, **_charge_schedule_input(schedule)}
        return await self._async_service_request(
            "UpdateChargeSchedule",
            operations.UPDATE_CHARGE_SCHEDULE,
            "updateChargeSchedule",
            {"vin": vin, "schedule": schedule_input},
            ServiceRequestKind.CHARGE_CONFIGURATION,
        )

    async def async_delete_charge_schedule(self, vin: str, schedule_id: str) -> ServiceRequest:
        """Delete a recurring charge schedule."""

        return await self._async_service_request(
            "DeleteChargeSchedule",
            operations.DELETE_CHARGE_SCHEDULE,
            "deleteChargeSchedule",
            {"vin": vin, "id": schedule_id},
            ServiceRequestKind.CHARGE_CONFIGURATION,
        )

    async def async_toggle_charge_schedule(
        self,
        vin: str,
        schedule_id: str,
        *,
        enabled: bool,
    ) -> ServiceRequest:
        """Enable or disable a recurring charge schedule."""

        return await self._async_service_request(
            "ToggleChargeSchedule",
            operations.TOGGLE_CHARGE_SCHEDULE,
            "toggleChargeSchedule",
            {"vin": vin, "schedule": {"id": schedule_id, "enable": enabled}},
            ServiceRequestKind.CHARGE_CONFIGURATION,
        )

    async def async_create_climate_schedule(
        self,
        vin: str,
        schedule: ClimateScheduleInput,
    ) -> ServiceRequest:
        """Create a recurring climate schedule."""

        return await self._async_service_request(
            "CreateClimateSchedule",
            operations.CREATE_CLIMATE_SCHEDULE,
            "createClimateSchedule",
            _optional_variables(
                vin=vin,
                schedule=_climate_schedule_input(schedule),
                climateAccessories=_climate_parameters_input(schedule.climate.parameters),
            ),
            ServiceRequestKind.CLIMATE,
        )

    async def async_update_climate_schedule(
        self,
        vin: str,
        schedule_id: str,
        schedule: ClimateScheduleInput,
    ) -> ServiceRequest:
        """Replace a recurring climate schedule."""

        schedule_input = {"id": schedule_id, **_climate_schedule_input(schedule)}
        return await self._async_service_request(
            "UpdateClimateSchedule",
            operations.UPDATE_CLIMATE_SCHEDULE,
            "updateClimateSchedule",
            _optional_variables(
                vin=vin,
                schedule=schedule_input,
                climateAccessories=_climate_parameters_input(schedule.climate.parameters),
            ),
            ServiceRequestKind.CLIMATE,
        )

    async def async_delete_climate_schedule(self, vin: str, schedule_id: str) -> ServiceRequest:
        """Delete a recurring climate schedule."""

        return await self._async_service_request(
            "DeleteClimateSchedule",
            operations.DELETE_CLIMATE_SCHEDULE,
            "deleteClimateSchedule",
            {"vin": vin, "id": schedule_id},
            ServiceRequestKind.CLIMATE,
        )

    async def async_toggle_climate_schedule(
        self,
        vin: str,
        schedule_id: str,
        *,
        enabled: bool,
    ) -> ServiceRequest:
        """Enable or disable a recurring climate schedule."""

        return await self._async_service_request(
            "ToggleClimateSchedule",
            operations.TOGGLE_CLIMATE_SCHEDULE,
            "toggleClimateSchedule",
            {"vin": vin, "schedule": {"id": schedule_id, "enable": enabled}},
            ServiceRequestKind.CLIMATE,
        )
