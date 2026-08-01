from __future__ import annotations

from . import operations
from ._client_base import _NissanClientBase
from .graphql_input import UNSET, UnsetType, serialize_enum
from .models import (
    BatteryStatus,
    BoundaryAlert,
    ClimateStatus,
    CurfewAlert,
    DistanceUnit,
    DoorsStatus,
    SpeedAlert,
    SpeedUnit,
    TemperatureUnit,
    ValetAlert,
    VehicleStatus,
)
from .parsing import (
    parse_vehicle_status,
)
from .vehicle_detail_inputs import (
    vehicle_battery_status_variables,
    vehicle_boundary_alerts_variables,
    vehicle_climate_status_variables,
    vehicle_curfew_alerts_variables,
    vehicle_doors_status_variables,
    vehicle_model_year_variables,
    vehicle_nickname_variables,
    vehicle_speed_alerts_variables,
    vehicle_status_and_recalls_variables,
    vehicle_status_variables,
    vehicle_valet_alerts_variables,
)
from .vehicle_detail_models import (
    VehicleModelYear,
    VehicleNickname,
    VehicleStatusAndRecalls,
)
from .vehicle_detail_parsing import (
    parse_vehicle_battery_status,
    parse_vehicle_boundary_alerts,
    parse_vehicle_climate_status,
    parse_vehicle_core_status,
    parse_vehicle_curfew_alerts,
    parse_vehicle_doors_status,
    parse_vehicle_model_year,
    parse_vehicle_nickname,
    parse_vehicle_speed_alerts,
    parse_vehicle_status_and_recalls,
    parse_vehicle_valet_alert,
)


class _VehicleDetailClientMixin(_NissanClientBase):
    async def async_get_vehicle_status(
        self,
        vin: str,
        *,
        distance_unit: DistanceUnit = DistanceUnit.MILE,
        temperature_unit: TemperatureUnit = TemperatureUnit.FAHRENHEIT,
    ) -> VehicleStatus:
        """Return cached dynamic status without waking the vehicle."""

        data = await self._transport.async_graphql(
            "VehicleDynamicData",
            operations.VEHICLE_DYNAMIC_DATA,
            {
                "vin": vin,
                "unit": serialize_enum(distance_unit),
                "temperatureUnit": serialize_enum(temperature_unit),
            },
        )
        return parse_vehicle_status(data, vin)

    async def async_get_vehicle_battery_status(
        self,
        vin: str,
        *,
        unit: DistanceUnit | UnsetType | None = UNSET,
    ) -> BatteryStatus | None:
        """Return the upstream service's standalone cached battery-status response."""

        data = await self._transport.async_graphql(
            "VehicleBatteryStatus",
            operations.VEHICLE_BATTERY_STATUS,
            vehicle_battery_status_variables(vin, unit=unit),
        )
        return parse_vehicle_battery_status(data, vin)

    async def async_get_vehicle_boundary_alerts(
        self,
        vin: str,
        *,
        distance_unit: DistanceUnit | UnsetType | None = UNSET,
    ) -> tuple[BoundaryAlert | None, ...] | None:
        """Return the upstream service's standalone boundary-alert collection."""

        data = await self._transport.async_graphql(
            "VehicleBoundaryAlerts",
            operations.VEHICLE_BOUNDARY_ALERTS,
            vehicle_boundary_alerts_variables(
                vin,
                distance_unit=distance_unit,
            ),
        )
        return parse_vehicle_boundary_alerts(data)

    async def async_get_vehicle_climate_status(
        self,
        vin: str,
        temperature_unit: TemperatureUnit,
    ) -> ClimateStatus | None:
        """Return the upstream service's standalone cached climate-status response."""

        data = await self._transport.async_graphql(
            "VehicleClimateStatus",
            operations.VEHICLE_CLIMATE_STATUS,
            vehicle_climate_status_variables(vin, temperature_unit),
        )
        return parse_vehicle_climate_status(data, vin)

    async def async_get_vehicle_curfew_alerts(
        self,
        vin: str,
    ) -> tuple[CurfewAlert | None, ...] | None:
        """Return the upstream service's standalone curfew-alert collection."""

        data = await self._transport.async_graphql(
            "VehicleCurfewAlerts",
            operations.VEHICLE_CURFEW_ALERTS,
            vehicle_curfew_alerts_variables(vin),
        )
        return parse_vehicle_curfew_alerts(data)

    async def async_get_vehicle_doors_status(
        self,
        vin: str,
    ) -> DoorsStatus | None:
        """Return the upstream service's standalone cached doors-status response."""

        data = await self._transport.async_graphql(
            "VehicleDoorsStatus",
            operations.VEHICLE_DOORS_STATUS,
            vehicle_doors_status_variables(vin),
        )
        return parse_vehicle_doors_status(data, vin)

    async def async_get_vehicle_model_year(
        self,
        vin: str,
    ) -> VehicleModelYear | None:
        """Return the standalone required model and year fields for a vehicle."""

        data = await self._transport.async_graphql(
            "VehicleModelYear",
            operations.VEHICLE_MODEL_YEAR,
            vehicle_model_year_variables(vin),
        )
        return parse_vehicle_model_year(data)

    async def async_get_vehicle_nickname(
        self,
        vin: str,
    ) -> VehicleNickname | None:
        """Return the standalone nullable nickname response for a vehicle."""

        data = await self._transport.async_graphql(
            "VehicleNickname",
            operations.VEHICLE_NICKNAME,
            vehicle_nickname_variables(vin),
        )
        return parse_vehicle_nickname(data)

    async def async_get_vehicle_speed_alerts(
        self,
        vin: str,
        *,
        speed_unit: SpeedUnit | UnsetType | None = UNSET,
    ) -> tuple[SpeedAlert | None, ...] | None:
        """Return the upstream service's standalone speed-alert collection."""

        data = await self._transport.async_graphql(
            "VehicleSpeedAlerts",
            operations.VEHICLE_SPEED_ALERTS,
            vehicle_speed_alerts_variables(vin, speed_unit=speed_unit),
        )
        return parse_vehicle_speed_alerts(data)

    async def async_get_vehicle_core_status(
        self,
        vin: str,
        *,
        unit: DistanceUnit | UnsetType | None = UNSET,
    ) -> VehicleStatus | None:
        """Return the narrower non-EV VehicleStatus operation from the upstream service."""

        data = await self._transport.async_graphql(
            "VehicleStatus",
            operations.VEHICLE_STATUS,
            vehicle_status_variables(vin, unit=unit),
        )
        return parse_vehicle_core_status(data, vin)

    async def async_get_vehicle_status_and_recalls(
        self,
        vin: str,
        *,
        unit: DistanceUnit | UnsetType | None = UNSET,
    ) -> VehicleStatusAndRecalls | None:
        """Return the upstream service's combined cached core status and recalls response."""

        data = await self._transport.async_graphql(
            "VehicleStatusAndRecalls",
            operations.VEHICLE_STATUS_AND_RECALLS,
            vehicle_status_and_recalls_variables(vin, unit=unit),
        )
        return parse_vehicle_status_and_recalls(data, vin)

    async def async_get_vehicle_valet_alert(
        self,
        vin: str,
        *,
        distance_unit: DistanceUnit | UnsetType | None = UNSET,
    ) -> ValetAlert | None:
        """Return the upstream service's standalone valet-alert response."""

        data = await self._transport.async_graphql(
            "VehicleValetAlerts",
            operations.VEHICLE_VALET_ALERTS,
            vehicle_valet_alerts_variables(vin, distance_unit=distance_unit),
        )
        return parse_vehicle_valet_alert(data)
