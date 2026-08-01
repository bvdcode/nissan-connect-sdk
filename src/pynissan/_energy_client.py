from __future__ import annotations

from . import operations
from ._client_base import _NissanClientBase
from .charge_plan_inputs import (
    charge_product_variables,
    pricing_details_variables,
)
from .charge_plan_models import (
    ChargePlanPricingDetails,
    ChargeProductResult,
)
from .charge_plan_parsing import (
    parse_charge_product,
    parse_pricing_details,
)
from .common_inputs import CoordinateInput
from .energy_account_models import (
    EnergyAccountStatusResult,
)
from .energy_account_parsing import parse_account_status
from .extended_vehicle_inputs import (
    EmpConnectorLevelInput,
    EmpEvseStatusInput,
    driving_history_variables,
    e_vehicle_eligibility_variables,
    ev_charge_stations_variables,
    last_known_camera_usage_counter_variables,
    location_details_variables,
    parking_chargeable_variables,
    shareable_capabilities_variables,
    tariff_pricing_variables,
)
from .extended_vehicle_models import (
    DrivingHistory,
    DrivingHistoryAggregator,
    EVChargeStation,
    EVehicleEligibility,
    LastKnownCameraUsageCounter,
    LocationDetails,
    ParkingChargeable,
    ShareableCapabilities,
    TariffPricing,
    WeightUnit,
)
from .extended_vehicle_parsing import (
    parse_driving_history,
    parse_e_vehicle_eligibility,
    parse_ev_charge_stations,
    parse_last_known_camera_usage_counter,
    parse_location_details,
    parse_parking_chargeable,
    parse_shareable_capabilities,
    parse_tariff_pricing,
)
from .graphql_input import UNSET, UnsetType, serialize_enum
from .models import (
    ChargeConfig,
    ChargeHistoryAggregator,
    ChargeSchedule,
    DistanceUnit,
    SpeedUnit,
    TemperatureUnit,
    V2LStatus,
    VehicleCapabilities,
    VehicleChargeHistory,
)
from .navigation_inputs import (
    PlugConnectorType,
)
from .parsing import (
    parse_charge_config,
    parse_charge_schedules,
    parse_v2l_status,
    parse_vehicle_capabilities,
    parse_vehicle_charge_history,
)
from .pnc_models import (
    PlugAndChargeServiceStatus,
    PublicChargeSessionStatus,
)
from .pnc_parsing import (
    parse_charge_session_status,
    parse_pnc_service_status,
)
from .service_inputs import (
    vehicle_preferred_dealer_variables,
    vehicle_recalls_variables,
    vehicle_roadside_assistance_variables,
    vehicle_service_history_variables,
    warranty_info_variables,
)
from .service_models import (
    VehiclePreferredDealer,
    VehicleRecall,
    VehicleRoadsideAssistance,
    VehicleServiceHistoryEntry,
    VehicleWarranty,
)
from .service_parsing import (
    parse_vehicle_preferred_dealer,
    parse_vehicle_recalls,
    parse_vehicle_roadside_assistance,
    parse_vehicle_service_history,
    parse_warranty_info,
)
from .v1g_inputs import (
    v1g_monitored_charging_account_status_variables,
    v1g_tokenized_url_variables,
)
from .v1g_models import (
    V1GMonitoredChargingAccountStatusResult,
    V1GTokenizedUrlResult,
)
from .v1g_parsing import (
    parse_v1g_monitored_charging_account_status,
    parse_v1g_tokenized_url,
)


class _EnergyClientMixin(_NissanClientBase):
    async def async_get_vehicle_capabilities(
        self,
        vin: str,
        temperature_unit: TemperatureUnit = TemperatureUnit.FAHRENHEIT,
    ) -> VehicleCapabilities:
        """Return the connected services advertised for a vehicle."""

        data = await self._transport.async_graphql(
            "VehicleCapabilities",
            operations.VEHICLE_CAPABILITIES,
            {"vin": vin, "unit": serialize_enum(temperature_unit)},
        )
        return parse_vehicle_capabilities(data, vin)

    async def async_get_charge_schedules(self, vin: str) -> tuple[ChargeSchedule, ...]:
        """Return the vehicle's recurring charge schedules."""

        data = await self._transport.async_graphql(
            "VehicleChargeSchedules",
            operations.VEHICLE_CHARGE_SCHEDULES,
            {"vin": vin},
        )
        return parse_charge_schedules(data)

    async def async_get_charge_config(self, vin: str) -> ChargeConfig | None:
        """Return configured charging limits when supported by the vehicle."""

        data = await self._transport.async_graphql(
            "ChargeConfig",
            operations.CHARGE_CONFIG,
            {"vin": vin},
        )
        return parse_charge_config(data)

    async def async_get_v2l_status(self, vin: str) -> V2LStatus | None:
        """Return V2L state and battery reserve levels when supported."""

        data = await self._transport.async_graphql(
            "V2lStatus",
            operations.V2L_STATUS,
            {"vin": vin},
        )
        return parse_v2l_status(data)

    async def async_get_charge_history(
        self,
        vin: str,
        aggregator: ChargeHistoryAggregator,
    ) -> VehicleChargeHistory | None:
        """Return charging sessions and summaries for a requested aggregation."""

        data = await self._transport.async_graphql(
            "VehicleChargeHistory",
            operations.VEHICLE_CHARGE_HISTORY,
            {"vin": vin, "aggregator": serialize_enum(aggregator)},
        )
        return parse_vehicle_charge_history(data)

    async def async_get_energy_account_status(
        self,
        vin: str,
    ) -> EnergyAccountStatusResult | None:
        """Return Nissan Energy account, PnC, toggle, and NACS status."""

        data = await self._transport.async_graphql(
            "AccountStatus",
            operations.ACCOUNT_STATUS,
            {"vin": vin},
        )
        return parse_account_status(data)

    async def async_get_charge_product(
        self,
        vin: str,
    ) -> ChargeProductResult | None:
        """Return the EMP charge-plan product offered for the vehicle."""

        data = await self._transport.async_graphql(
            "ChargeProduct",
            operations.CHARGE_PRODUCT,
            charge_product_variables(vin),
        )
        return parse_charge_product(data)

    async def async_get_charge_plan_pricing_details(
        self,
        vin: str,
        location_id: str,
    ) -> ChargePlanPricingDetails | None:
        """Return EMP parking and connector tariffs for a charging location."""

        data = await self._transport.async_graphql(
            "PricingDetails",
            operations.PRICING_DETAILS,
            pricing_details_variables(vin, location_id),
        )
        return parse_pricing_details(data)

    async def async_get_driving_history(
        self,
        vin: str,
        aggregator: DrivingHistoryAggregator,
        *,
        distance_unit: DistanceUnit | UnsetType | None = UNSET,
        weight_unit: WeightUnit | UnsetType | None = UNSET,
        speed_unit: SpeedUnit | UnsetType | None = UNSET,
    ) -> DrivingHistory | None:
        """Return trip summaries and individual trips for an electric vehicle."""

        data = await self._transport.async_graphql(
            "DrivingHistory",
            operations.DRIVING_HISTORY,
            driving_history_variables(
                vin,
                aggregator,
                distance_unit=distance_unit,
                weight_unit=weight_unit,
                speed_unit=speed_unit,
            ),
        )
        return parse_driving_history(data)

    async def async_get_ev_charge_stations(
        self,
        vin: str,
        coordinate: CoordinateInput,
        *,
        plug_connector_types: (tuple[PlugConnectorType | None, ...] | UnsetType | None) = UNSET,
        enable_within_range_restriction: bool | UnsetType | None = UNSET,
    ) -> tuple[EVChargeStation | None, ...] | None:
        """Return charging stations near a coordinate for the vehicle."""

        data = await self._transport.async_graphql(
            "EVChargeStations",
            operations.EV_CHARGE_STATIONS,
            ev_charge_stations_variables(
                vin,
                coordinate,
                plug_connector_types=plug_connector_types,
                enable_within_range_restriction=enable_within_range_restriction,
            ),
        )
        return parse_ev_charge_stations(data)

    async def async_get_e_vehicle_eligibility(
        self,
        vin: str,
    ) -> EVehicleEligibility | None:
        """Return the Nissan Energy eligibility response for the vehicle."""

        data = await self._transport.async_graphql(
            "eVehicleEligibility",
            operations.E_VEHICLE_ELIGIBILITY,
            e_vehicle_eligibility_variables(vin),
        )
        return parse_e_vehicle_eligibility(data)

    async def async_get_last_known_camera_usage_counter(
        self,
        vin: str,
    ) -> LastKnownCameraUsageCounter | None:
        """Return the last known camera usage counter and update time."""

        data = await self._transport.async_graphql(
            "LastKnownCameraUsageCounter",
            operations.LAST_KNOWN_CAMERA_USAGE_COUNTER,
            last_known_camera_usage_counter_variables(vin),
        )
        return parse_last_known_camera_usage_counter(data)

    async def async_get_location_details(
        self,
        vin: str,
        latitude: str,
        longitude: str,
        in_network_only: bool,
        range_value: int,
        *,
        operator_names: tuple[str | None, ...] | UnsetType | None = UNSET,
        evse: EmpEvseStatusInput | UnsetType | None = UNSET,
        plug_types: tuple[str | None, ...] | UnsetType | None = UNSET,
        charge_level: EmpConnectorLevelInput | UnsetType | None = UNSET,
        pnc_stations_only: bool | UnsetType | None = UNSET,
    ) -> LocationDetails | None:
        """Return Nissan Energy charging-location details for a search area."""

        data = await self._transport.async_graphql(
            "LocationDetails",
            operations.LOCATION_DETAILS,
            location_details_variables(
                vin,
                latitude,
                longitude,
                in_network_only,
                range_value,
                operator_names=operator_names,
                evse=evse,
                plug_types=plug_types,
                charge_level=charge_level,
                pnc_stations_only=pnc_stations_only,
            ),
        )
        return parse_location_details(data)

    async def async_get_parking_chargeable(
        self,
        evse_id: str,
    ) -> ParkingChargeable | None:
        """Return whether parking fees can be charged for an EVSE."""

        data = await self._transport.async_graphql(
            "ParkingChargeable",
            operations.PARKING_CHARGEABLE,
            parking_chargeable_variables(evse_id),
        )
        return parse_parking_chargeable(data)

    async def async_get_shareable_capabilities(
        self,
        vin: str,
        *,
        driver_id: str | UnsetType | None = UNSET,
    ) -> ShareableCapabilities | None:
        """Return capabilities that can be shared with another driver."""

        data = await self._transport.async_graphql(
            "ShareableCapabilities",
            operations.SHAREABLE_CAPABILITIES,
            shareable_capabilities_variables(vin, driver_id=driver_id),
        )
        return parse_shareable_capabilities(data)

    async def async_get_tariff_pricing(
        self,
        vin: str,
        location_id: str,
    ) -> TariffPricing | None:
        """Return Nissan Energy tariff pricing for one charging location."""

        data = await self._transport.async_graphql(
            "TariffPricing",
            operations.TARIFF_PRICING,
            tariff_pricing_variables(vin, location_id),
        )
        return parse_tariff_pricing(data)

    async def async_get_pnc_service_status(
        self,
        vin: str,
    ) -> PlugAndChargeServiceStatus | None:
        """Return the vehicle's Nissan Energy Plug & Charge enrollment state."""

        data = await self._transport.async_graphql(
            "PNCServiceStatus",
            operations.PNC_SERVICE_STATUS,
            {"vin": vin},
        )
        return parse_pnc_service_status(data)

    async def async_get_v1g_monitored_charging_account_status(
        self,
        vin: str,
    ) -> V1GMonitoredChargingAccountStatusResult | None:
        """Return raw V1G Charging Insights enrollment and notification state."""

        data = await self._transport.async_graphql(
            "V1GMonitoredChargingAccountStatus",
            operations.V1G_MONITORED_CHARGING_ACCOUNT_STATUS,
            v1g_monitored_charging_account_status_variables(vin),
        )
        return parse_v1g_monitored_charging_account_status(data)

    async def async_get_v1g_tokenized_url(
        self,
        vin: str,
    ) -> V1GTokenizedUrlResult | None:
        """Return the sensitive, potentially ephemeral V1G web-view URL."""

        data = await self._transport.async_graphql(
            "V1GTokenizedUrl",
            operations.V1G_TOKENIZED_URL,
            v1g_tokenized_url_variables(vin),
        )
        return parse_v1g_tokenized_url(data)

    async def async_get_public_charge_session_status(
        self,
        vin: str,
    ) -> PublicChargeSessionStatus | None:
        """Return the current Nissan Energy public charging-session state."""

        data = await self._transport.async_graphql(
            "ChargeSessionStatus",
            operations.CHARGE_SESSION_STATUS,
            {"vin": vin},
        )
        return parse_charge_session_status(data)

    async def async_get_vehicle_preferred_dealer(
        self,
        vin: str,
    ) -> VehiclePreferredDealer | None:
        """Return the preferred dealer currently associated with the vehicle."""

        data = await self._transport.async_graphql(
            "VehiclePreferredDealer",
            operations.VEHICLE_PREFERRED_DEALER,
            vehicle_preferred_dealer_variables(vin),
        )
        return parse_vehicle_preferred_dealer(data)

    async def async_get_vehicle_recalls(
        self,
        vin: str,
    ) -> tuple[VehicleRecall, ...] | None:
        """Return the vehicle's non-null recall and service-campaign list."""

        data = await self._transport.async_graphql(
            "VehicleRecalls",
            operations.VEHICLE_RECALLS,
            vehicle_recalls_variables(vin),
        )
        return parse_vehicle_recalls(data)

    async def async_get_vehicle_roadside_assistance(
        self,
        vin: str,
    ) -> VehicleRoadsideAssistance | None:
        """Return roadside and towing coverage limits reported by Nissan."""

        data = await self._transport.async_graphql(
            "VehicleRoadsideAssistance",
            operations.VEHICLE_ROADSIDE_ASSISTANCE,
            vehicle_roadside_assistance_variables(vin),
        )
        return parse_vehicle_roadside_assistance(data)

    async def async_get_vehicle_service_history(
        self,
        vin: str,
        *,
        unit: DistanceUnit | UnsetType | None = UNSET,
    ) -> tuple[VehicleServiceHistoryEntry, ...] | None:
        """Return completed service records in the requested distance unit."""

        data = await self._transport.async_graphql(
            "VehicleServiceHistory",
            operations.VEHICLE_SERVICE_HISTORY,
            vehicle_service_history_variables(vin, unit=unit),
        )
        return parse_vehicle_service_history(data)

    async def async_get_warranty_info(
        self,
        vin: str,
        *,
        mileage: int | UnsetType | None = UNSET,
    ) -> VehicleWarranty | None:
        """Return the vehicle warranty at an optional caller-supplied mileage."""

        data = await self._transport.async_graphql(
            "WarrantyInfo",
            operations.WARRANTY_INFO,
            warranty_info_variables(vin, mileage=mileage),
        )
        return parse_warranty_info(data)
