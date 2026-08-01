from __future__ import annotations

from datetime import datetime

from . import operations
from ._client_base import _NissanClientBase
from ._client_helpers import (
    _climate_parameters_input,
    _date_time_input,
    _optional_variables,
    _start_climate_input,
    _success,
)
from .charge_plan_inputs import (
    cancel_charge_plan_variables,
    enroll_charge_plan_variables,
)
from .charge_plan_models import (
    ChargePlanCancellationResult,
    ChargePlanEnrollmentResult,
)
from .charge_plan_parsing import (
    parse_cancel_charge_plan,
    parse_enroll_charge_plan,
)
from .graphql_input import UNSET, UnsetType, serialize_enum
from .models import (
    ClimateDefaults,
    ClimateSettings,
    ServiceRequest,
    ServiceRequestKind,
    TemperatureUnit,
    VehicleClimateSchedules,
)
from .parsing import (
    parse_climate_defaults,
    parse_climate_schedules,
)
from .pnc_inputs import (
    retry_certificate_install_variables,
    start_charge_session_variables,
    stop_charge_session_variables,
    update_pnc_service_status_variables,
)
from .pnc_models import (
    PlugAndChargeCertificateRetryResult,
    PlugAndChargeServiceStatus,
    PlugAndChargeStatusInput,
    PublicChargeSessionStartResult,
    PublicChargeSessionStopResult,
)
from .pnc_parsing import (
    parse_retry_certificate_install,
    parse_start_charge_session,
    parse_stop_charge_session,
    parse_update_pnc_service_status,
)
from .v1g_inputs import (
    V1GNotificationPreferenceInput,
    v1g_cancel_monitored_charging_plan_variables,
    v1g_enroll_monitored_charging_plan_variables,
    v1g_update_notification_preferences_variables,
)
from .v1g_models import (
    V1GMonitoredChargingPlanCancellationResult,
    V1GMonitoredChargingPlanEnrollmentResult,
    V1GNotificationPreferencesUpdateResult,
)
from .v1g_parsing import (
    parse_v1g_cancel_monitored_charging_plan,
    parse_v1g_enroll_monitored_charging_plan,
    parse_v1g_update_notification_preferences,
)


class _ClimateChargeClientMixin(_NissanClientBase):
    async def async_get_climate_schedules(
        self,
        vin: str,
        *,
        temperature_unit: TemperatureUnit = TemperatureUnit.FAHRENHEIT,
    ) -> VehicleClimateSchedules:
        """Return recurring and one-time climate schedules and their accessories."""

        data = await self._transport.async_graphql(
            "VehicleClimateSchedules",
            operations.VEHICLE_CLIMATE_SCHEDULES,
            {"vin": vin, "temperatureUnit": serialize_enum(temperature_unit)},
        )
        return parse_climate_schedules(data)

    async def async_get_climate_defaults(
        self,
        vin: str,
        *,
        temperature_unit: TemperatureUnit = TemperatureUnit.FAHRENHEIT,
    ) -> ClimateDefaults | None:
        """Return saved climate defaults when supported by the vehicle."""

        data = await self._transport.async_graphql(
            "VehicleClimateDefaults",
            operations.VEHICLE_CLIMATE_DEFAULTS,
            {"vin": vin, "temperatureUnit": serialize_enum(temperature_unit)},
        )
        return parse_climate_defaults(data)

    async def async_start_climate(
        self,
        vin: str,
        climate: ClimateSettings,
        *,
        set_as_default: bool | None = None,
    ) -> ServiceRequest:
        """Start cabin climate control."""

        variables = _optional_variables(
            vin=vin,
            climate=_start_climate_input(climate),
            parameters=_climate_parameters_input(climate.parameters),
            setAsDefault=set_as_default,
        )
        return await self._async_service_request(
            "StartClimate",
            operations.START_CLIMATE,
            "startClimate",
            variables,
            ServiceRequestKind.CLIMATE,
        )

    async def async_adjust_climate(
        self,
        vin: str,
        climate: ClimateSettings,
        *,
        set_as_default: bool | None = None,
    ) -> ServiceRequest:
        """Adjust climate settings while remote climate is active."""

        variables = _optional_variables(
            vin=vin,
            climate=_start_climate_input(climate),
            parameters=_climate_parameters_input(climate.parameters),
            setAsDefault=set_as_default,
        )
        return await self._async_service_request(
            "AdjustClimate",
            operations.ADJUST_CLIMATE,
            "adjustClimate",
            variables,
            ServiceRequestKind.CLIMATE,
        )

    async def async_stop_climate(self, vin: str) -> ServiceRequest:
        """Stop remote cabin climate control."""

        return await self._async_simple_service_request(
            "StopClimate",
            operations.STOP_CLIMATE,
            "stopClimate",
            vin,
            ServiceRequestKind.CLIMATE,
        )

    async def async_set_climate_defaults(
        self,
        vin: str,
        climate: ClimateSettings,
    ) -> bool:
        """Save the vehicle's default climate temperature and accessories."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "SetClimateDefaults",
            operations.SET_CLIMATE_DEFAULTS,
            _optional_variables(
                vin=vin,
                climate=_start_climate_input(climate),
                parameters=_climate_parameters_input(climate.parameters),
            ),
        )
        return _success(data, "setClimateDefaults")

    async def async_set_delayed_climate(
        self,
        vin: str,
        start_date_time: datetime,
        climate: ClimateSettings,
    ) -> ServiceRequest:
        """Schedule a one-time delayed climate start."""

        return await self._async_service_request(
            "SetDelayedClimate",
            operations.SET_DELAYED_CLIMATE,
            "setDelayedClimate",
            _optional_variables(
                vin=vin,
                startDateTime=_date_time_input(start_date_time),
                climate=_start_climate_input(climate),
                climateAccessories=_climate_parameters_input(climate.parameters),
            ),
            ServiceRequestKind.CLIMATE,
        )

    async def async_cancel_delayed_climate(self, vin: str) -> ServiceRequest:
        """Cancel the one-time delayed climate request."""

        return await self._async_simple_service_request(
            "CancelDelayedClimate",
            operations.CANCEL_DELAYED_CLIMATE,
            "cancelDelayedClimate",
            vin,
            ServiceRequestKind.CLIMATE,
        )

    async def async_start_charge(self, vin: str) -> ServiceRequest:
        """Start charging an attached electric vehicle."""

        return await self._async_simple_service_request(
            "StartCharge",
            operations.START_CHARGE,
            "startCharge",
            vin,
            ServiceRequestKind.CHARGE,
        )

    async def async_stop_charge(self, vin: str) -> ServiceRequest:
        """Stop charging an attached electric vehicle."""

        return await self._async_simple_service_request(
            "StopCharge",
            operations.STOP_CHARGE,
            "stopCharge",
            vin,
            ServiceRequestKind.CHARGE,
        )

    async def async_start_public_charge_session(
        self,
        vin: str,
        evse_id: str,
        *,
        location_id: str | UnsetType | None = UNSET,
    ) -> PublicChargeSessionStartResult | None:
        """Start a Nissan Energy public charging session at one EVSE."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "StartChargeSession",
            operations.START_CHARGE_SESSION,
            start_charge_session_variables(
                vin,
                evse_id,
                location_id=location_id,
            ),
        )
        return parse_start_charge_session(data)

    async def async_enroll_charge_plan(
        self,
        vin: str,
        product_sku: str,
        model: str,
        year: str,
    ) -> ChargePlanEnrollmentResult | None:
        """Enroll the vehicle in an EMP charging product."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "EnrollChargePlan",
            operations.ENROLL_CHARGE_PLAN,
            enroll_charge_plan_variables(vin, product_sku, model, year),
        )
        return parse_enroll_charge_plan(data)

    async def async_cancel_charge_plan(
        self,
        vin: str,
    ) -> ChargePlanCancellationResult | None:
        """Cancel the vehicle's EMP charging-product enrollment."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CancelChargePlan",
            operations.CANCEL_CHARGE_PLAN,
            cancel_charge_plan_variables(vin),
        )
        return parse_cancel_charge_plan(data)

    async def async_stop_public_charge_session(
        self,
        vin: str,
    ) -> PublicChargeSessionStopResult | None:
        """Stop the active Nissan Energy public charging session."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "StopChargeSession",
            operations.STOP_CHARGE_SESSION,
            stop_charge_session_variables(vin),
        )
        return parse_stop_charge_session(data)

    async def async_update_pnc_service_status(
        self,
        vin: str,
        status: PlugAndChargeStatusInput,
    ) -> PlugAndChargeServiceStatus | None:
        """Enable or disable Nissan Energy Plug & Charge enrollment."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdatePnCServiceStatus",
            operations.UPDATE_PNC_SERVICE_STATUS,
            update_pnc_service_status_variables(vin, status),
        )
        return parse_update_pnc_service_status(data)

    async def async_retry_pnc_certificate_install(
        self,
        vin: str,
    ) -> PlugAndChargeCertificateRetryResult | None:
        """Retry installation of the vehicle's Plug & Charge certificate."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "RetryCertInstall",
            operations.RETRY_CERT_INSTALL,
            retry_certificate_install_variables(vin),
        )
        return parse_retry_certificate_install(data)

    async def async_enroll_v1g_monitored_charging_plan(
        self,
        vin: str,
        model: str,
        year: str,
        *,
        plan: str | UnsetType | None = UNSET,
    ) -> V1GMonitoredChargingPlanEnrollmentResult | None:
        """Enroll in V1G Charging Insights with an explicit caller-selected plan."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "V1GEnrollMonitoredChargingPlan",
            operations.V1G_ENROLL_MONITORED_CHARGING_PLAN,
            v1g_enroll_monitored_charging_plan_variables(
                vin,
                model,
                year,
                plan=plan,
            ),
        )
        return parse_v1g_enroll_monitored_charging_plan(data)

    async def async_cancel_v1g_monitored_charging_plan(
        self,
        vin: str,
    ) -> V1GMonitoredChargingPlanCancellationResult | None:
        """Permanently cancel V1G Charging Insights enrollment for a vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "V1GCancelMonitoredChargingPlan",
            operations.V1G_CANCEL_MONITORED_CHARGING_PLAN,
            v1g_cancel_monitored_charging_plan_variables(vin),
        )
        return parse_v1g_cancel_monitored_charging_plan(data)

    async def async_update_v1g_notification_preferences(
        self,
        vin: str,
        *,
        preferences: (tuple[V1GNotificationPreferenceInput | None, ...] | UnsetType | None) = UNSET,
    ) -> V1GNotificationPreferencesUpdateResult | None:
        """Patch V1G Charging Insights notification channels."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "V1GUpdateNotificationPreferences",
            operations.V1G_UPDATE_NOTIFICATION_PREFERENCES,
            v1g_update_notification_preferences_variables(
                vin,
                preferences=preferences,
            ),
        )
        return parse_v1g_update_notification_preferences(data)

    async def async_set_charge_limit(self, vin: str, percent: int) -> ServiceRequest:
        """Set the electric vehicle charging limit."""

        return await self._async_service_request(
            "SetChargeLimit",
            operations.SET_CHARGE_LIMIT,
            "setChargeLimit",
            {"vin": vin, "percent": percent},
            ServiceRequestKind.CHARGE_CONFIGURATION,
        )

    async def async_set_charge_notification_threshold(
        self,
        vin: str,
        percent: int,
    ) -> ServiceRequest:
        """Set the battery percentage that triggers a charge notification."""

        return await self._async_service_request(
            "SetNotificationLimit",
            operations.SET_NOTIFICATION_LIMIT,
            "setChargeNotificationThreshold",
            {"vin": vin, "percent": percent},
            ServiceRequestKind.CHARGE_CONFIGURATION,
        )

    async def async_set_v2l_minimum_battery_charge_level(
        self,
        vin: str,
        percent: int,
    ) -> ServiceRequest:
        """Set the minimum battery percentage reserved while using V2L."""

        return await self._async_service_request(
            "SetV2L",
            operations.SET_V2L,
            "setV2L",
            {"vin": vin, "input": {"minimumBatteryChargeLevel": percent}},
            ServiceRequestKind.V2L,
        )
