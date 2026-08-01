from __future__ import annotations

import asyncio
import math
from typing import assert_never

from . import operations
from ._client_base import _NissanClientBase
from ._client_helpers import _enum_value, _optional_variables, _validate_positive_integer
from .alert_inputs import (
    BoundaryAlertInput,
    BoundaryAlertUpdate,
    CurfewAlertInput,
    SpeedAlertInput,
    ValetRadiusInput,
    boundary_alert_input,
    boundary_alert_update_input,
    curfew_alert_input,
    optional_coordinate_input,
    optional_valet_radius_input,
    speed_alert_input,
)
from .common_inputs import CoordinateInput
from .graphql_input import UNSET, UnsetType, optional_input_fields
from .models import (
    BreachAlerts,
    DistanceUnit,
    ReminderNotificationsAfterLeavingVehicle,
    ServiceRequestStatus,
    SpeedUnit,
    VehicleAlertKind,
    VehicleAlertRequest,
    VehicleAlerts,
)
from .parsing import (
    parse_alert_request_status,
    parse_breach_alerts,
    parse_reminder_notifications_after_leaving_vehicle,
    parse_toggle_reminder_notifications_after_leaving_vehicle,
    parse_vehicle_alerts,
)


class _AlertClientMixin(_NissanClientBase):
    async def async_get_vehicle_alerts(
        self,
        vin: str,
        *,
        speed_unit: SpeedUnit | None = None,
        distance_unit: DistanceUnit | None = None,
    ) -> VehicleAlerts | None:
        """Return all configured vehicle alerts in one cached read."""

        data = await self._transport.async_graphql(
            "VehicleAlerts",
            operations.VEHICLE_ALERTS,
            _optional_variables(
                vin=vin,
                speedUnit=_enum_value(speed_unit),
                distanceUnit=_enum_value(distance_unit),
            ),
        )
        return parse_vehicle_alerts(data)

    async def async_get_breach_alerts(
        self,
        vin: str,
        *,
        page_number: int = 1,
        items_per_page: int = 20,
    ) -> BreachAlerts | None:
        """Return one page of raw vehicle-alert breach events."""

        _validate_positive_integer(page_number, "page_number")
        _validate_positive_integer(items_per_page, "items_per_page")
        data = await self._transport.async_graphql(
            "BreachAlerts",
            operations.BREACH_ALERTS,
            {
                "vin": vin,
                "pageNumber": page_number,
                "itemsPerPage": items_per_page,
            },
        )
        return parse_breach_alerts(data)

    async def async_get_alert_request_status(
        self,
        vin: str,
        service_request_id: str,
        alert_kind: VehicleAlertKind,
    ) -> str | None:
        """Return the raw status of a vehicle-alert configuration request."""

        match alert_kind:
            case VehicleAlertKind.BOUNDARY:
                operation_name = "VehicleBoundaryAlert"
                document = operations.VEHICLE_BOUNDARY_ALERT
                root_field = "boundaryAlert"
                status_required = True
            case VehicleAlertKind.CURFEW:
                operation_name = "VehicleCurfewAlert"
                document = operations.VEHICLE_CURFEW_ALERT
                root_field = "curfewAlert"
                status_required = True
            case VehicleAlertKind.SPEED:
                operation_name = "VehicleSpeedAlert"
                document = operations.VEHICLE_SPEED_ALERT
                root_field = "speedAlert"
                status_required = True
            case VehicleAlertKind.VALET:
                operation_name = "VehicleValetAlert"
                document = operations.VEHICLE_VALET_ALERT
                root_field = "valetAlert"
                status_required = False
            case _:
                assert_never(alert_kind)

        data = await self._transport.async_graphql(
            operation_name,
            document,
            {"vin": vin, "serviceRequestId": service_request_id},
        )
        return parse_alert_request_status(
            data,
            root_field,
            status_required=status_required,
        )

    async def async_wait_for_alert_request(
        self,
        vin: str,
        request: VehicleAlertRequest,
        *,
        poll_interval_seconds: float = 1.0,
        timeout_seconds: float = 210.0,
    ) -> str:
        """Poll a vehicle-alert change until Nissan reports success or failure."""

        if not math.isfinite(poll_interval_seconds) or poll_interval_seconds <= 0:
            raise ValueError("poll_interval_seconds must be a positive finite number")
        if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be a positive finite number")

        async with asyncio.timeout(timeout_seconds):
            while True:
                status = await self.async_get_alert_request_status(
                    vin,
                    request.id,
                    request.kind,
                )
                if status in {
                    ServiceRequestStatus.SUCCESS.value,
                    ServiceRequestStatus.FAILED.value,
                }:
                    return status
                await asyncio.sleep(poll_interval_seconds)

    async def async_create_boundary_alert(
        self,
        vin: str,
        alert: BoundaryAlertInput,
    ) -> VehicleAlertRequest:
        """Create a vehicle entry or exit boundary alert."""

        return await self._async_vehicle_alert_request(
            "CreateBoundaryAlert",
            operations.CREATE_BOUNDARY_ALERT,
            "createBoundaryAlert",
            {"vin": vin, "alert": boundary_alert_input(alert)},
            VehicleAlertKind.BOUNDARY,
        )

    async def async_update_boundary_alert(
        self,
        vin: str,
        service_request_id: str,
        update: BoundaryAlertUpdate,
    ) -> VehicleAlertRequest:
        """Patch an existing boundary alert."""

        return await self._async_vehicle_alert_request(
            "SetBoundaryAlert",
            operations.UPDATE_BOUNDARY_ALERT,
            "setBoundaryAlert",
            {
                "vin": vin,
                "alert": boundary_alert_update_input(service_request_id, update),
            },
            VehicleAlertKind.BOUNDARY,
        )

    async def async_delete_boundary_alert(
        self,
        vin: str,
        service_request_id: str,
    ) -> VehicleAlertRequest:
        """Delete an existing boundary alert."""

        return await self._async_vehicle_alert_request(
            "CancelBoundaryAlert",
            operations.DELETE_BOUNDARY_ALERT,
            "cancelBoundaryAlert",
            {"vin": vin, "serviceRequestId": service_request_id},
            VehicleAlertKind.BOUNDARY,
        )

    async def async_toggle_boundary_alert(
        self,
        vin: str,
        service_request_id: str,
        *,
        enabled: bool,
    ) -> VehicleAlertRequest:
        """Enable or disable an existing boundary alert."""

        return await self._async_vehicle_alert_request(
            "ToggleBoundaryAlert",
            operations.TOGGLE_BOUNDARY_ALERT,
            "toggleBoundaryAlert",
            {
                "vin": vin,
                "alert": {
                    "serviceRequestId": service_request_id,
                    "enable": enabled,
                },
            },
            VehicleAlertKind.BOUNDARY,
        )

    async def async_create_curfew_alert(
        self,
        vin: str,
        alert: CurfewAlertInput,
    ) -> VehicleAlertRequest:
        """Create a recurring vehicle curfew alert."""

        return await self._async_vehicle_alert_request(
            "CreateCurfewAlert",
            operations.CREATE_CURFEW_ALERT,
            "createCurfewAlert",
            {"vin": vin, "alert": curfew_alert_input(alert)},
            VehicleAlertKind.CURFEW,
        )

    async def async_update_curfew_alert(
        self,
        vin: str,
        service_request_id: str,
        alert: CurfewAlertInput,
    ) -> VehicleAlertRequest:
        """Replace an existing curfew alert."""

        return await self._async_vehicle_alert_request(
            "SetCurfewAlert",
            operations.UPDATE_CURFEW_ALERT,
            "setCurfewAlert",
            {
                "vin": vin,
                "serviceRequestId": service_request_id,
                "alert": curfew_alert_input(alert),
            },
            VehicleAlertKind.CURFEW,
        )

    async def async_delete_curfew_alert(
        self,
        vin: str,
        service_request_id: str,
    ) -> VehicleAlertRequest:
        """Delete an existing curfew alert."""

        return await self._async_vehicle_alert_request(
            "CancelCurfewAlert",
            operations.DELETE_CURFEW_ALERT,
            "cancelCurfewAlert",
            {"vin": vin, "serviceRequestId": service_request_id},
            VehicleAlertKind.CURFEW,
        )

    async def async_toggle_curfew_alert(
        self,
        vin: str,
        service_request_id: str,
        *,
        enabled: bool,
    ) -> VehicleAlertRequest:
        """Enable or disable an existing curfew alert."""

        return await self._async_vehicle_alert_request(
            "ToggleCurfewAlert",
            operations.TOGGLE_CURFEW_ALERT,
            "toggleCurfewAlert",
            {
                "vin": vin,
                "alert": {
                    "serviceRequestId": service_request_id,
                    "enable": enabled,
                },
            },
            VehicleAlertKind.CURFEW,
        )

    async def async_create_speed_alert(
        self,
        vin: str,
        alert: SpeedAlertInput,
    ) -> VehicleAlertRequest:
        """Create a vehicle speed alert."""

        return await self._async_vehicle_alert_request(
            "CreateSpeedAlert",
            operations.CREATE_SPEED_ALERT,
            "createSpeedAlert",
            {"vin": vin, "alert": speed_alert_input(alert)},
            VehicleAlertKind.SPEED,
        )

    async def async_update_speed_alert(
        self,
        vin: str,
        service_request_id: str,
        alert: SpeedAlertInput,
    ) -> VehicleAlertRequest:
        """Replace an existing speed alert."""

        speed_update = {
            "serviceRequestId": service_request_id,
            **speed_alert_input(alert),
        }
        return await self._async_vehicle_alert_request(
            "SetSpeedAlert",
            operations.UPDATE_SPEED_ALERT,
            "setSpeedAlert",
            {"vin": vin, "alert": speed_update},
            VehicleAlertKind.SPEED,
        )

    async def async_delete_speed_alert(
        self,
        vin: str,
        service_request_id: str,
    ) -> VehicleAlertRequest:
        """Delete an existing speed alert."""

        return await self._async_vehicle_alert_request(
            "CancelSpeedAlert",
            operations.DELETE_SPEED_ALERT,
            "cancelSpeedAlert",
            {"vin": vin, "serviceRequestId": service_request_id},
            VehicleAlertKind.SPEED,
        )

    async def async_toggle_speed_alert(
        self,
        vin: str,
        service_request_id: str,
        *,
        enabled: bool,
    ) -> VehicleAlertRequest:
        """Enable or disable an existing speed alert."""

        return await self._async_vehicle_alert_request(
            "ToggleSpeedAlert",
            operations.TOGGLE_SPEED_ALERT,
            "toggleSpeedAlert",
            {
                "vin": vin,
                "alert": {
                    "serviceRequestId": service_request_id,
                    "enable": enabled,
                },
            },
            VehicleAlertKind.SPEED,
        )

    async def async_activate_valet_alert(
        self,
        vin: str,
        *,
        radius: ValetRadiusInput | UnsetType | None = UNSET,
        location: CoordinateInput | UnsetType | None = UNSET,
    ) -> VehicleAlertRequest:
        """Activate a valet boundary alert around an optional location."""

        variables = optional_input_fields(
            vin=vin,
            radiusWithUnit=optional_valet_radius_input(radius),
            location=optional_coordinate_input(location),
        )
        return await self._async_vehicle_alert_request(
            "ActivateValetAlert",
            operations.ACTIVATE_VALET_ALERT,
            "activateValetAlert",
            variables,
            VehicleAlertKind.VALET,
        )

    async def async_deactivate_valet_alert(
        self,
        vin: str,
        service_request_id: str,
    ) -> VehicleAlertRequest:
        """Deactivate the current valet alert."""

        return await self._async_vehicle_alert_request(
            "DeactivateValetAlert",
            operations.DEACTIVATE_VALET_ALERT,
            "deactivateValetAlert",
            {"vin": vin, "serviceRequestId": service_request_id},
            VehicleAlertKind.VALET,
        )

    async def async_get_reminder_notifications_after_leaving_vehicle(
        self,
        vin: str,
    ) -> ReminderNotificationsAfterLeavingVehicle | None:
        """Return after-leaving reminder flags when supported by the vehicle."""

        data = await self._transport.async_graphql(
            "ReminderNotificationsAfterLeavingVehicle",
            operations.REMINDER_NOTIFICATIONS_AFTER_LEAVING_VEHICLE,
            {"vin": vin},
        )
        return parse_reminder_notifications_after_leaving_vehicle(data)

    async def async_toggle_reminder_notifications_after_leaving_vehicle(
        self,
        vin: str,
        *,
        enable_lock: bool | None = None,
        enable_door: bool | None = None,
        enable_trunk: bool | None = None,
        enable_sunroof: bool | None = None,
        enable_window: bool | None = None,
    ) -> bool | None:
        """Patch one or more after-leaving reminder flags."""

        reminder_notifications = _optional_variables(
            enableLock=enable_lock,
            enableDoor=enable_door,
            enableTrunk=enable_trunk,
            enableSunroof=enable_sunroof,
            enableWindow=enable_window,
        )
        if not reminder_notifications:
            raise ValueError("At least one reminder notification setting is required")
        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "ToggleReminderNotificationsAfterLeavingVehicle",
            operations.TOGGLE_REMINDER_NOTIFICATIONS_AFTER_LEAVING_VEHICLE,
            {
                "vin": vin,
                "reminderNotifications": reminder_notifications,
            },
        )
        return parse_toggle_reminder_notifications_after_leaving_vehicle(data)
