from __future__ import annotations

from datetime import datetime

from . import operations
from ._client_base import _NissanClientBase
from .dealer_inputs import (
    MaintenanceMileageInput,
    ServiceAppointmentInput,
    ServiceCode,
    ServiceLocationType,
    all_dealers_variables,
    cancel_service_appointment_variables,
    dealers_by_search_variables,
    maintenance_visits_variables,
    service_advisors_variables,
    service_appointment_variables,
    service_appointments_variables,
    service_time_slots_variables,
    update_service_appointment_variables,
)
from .dealer_models import (
    CancelServiceAppointmentResult,
    Dealer,
    DealerDealsAndImages,
    DealerServiceOperation,
    DealerSummary,
    MaintenanceVisits,
    PreferredDealerUpdateResult,
    ServiceAdvisor,
    ServiceAppointment,
    ServiceAppointmentCreateResult,
    ServiceAppointmentTimeSlot,
    ServiceAppointmentUpdateResult,
    ServiceCategory,
    ServiceOperationsAtInterval,
    ServiceTransportationOption,
)
from .dealer_parsing import (
    parse_all_dealers,
    parse_cancel_service_appointment,
    parse_create_service_appointment,
    parse_dealer,
    parse_dealer_deals_and_images,
    parse_dealers,
    parse_maintenance_visits,
    parse_service_advisors,
    parse_service_appointment_time_slots,
    parse_service_appointments,
    parse_service_categories,
    parse_service_operations,
    parse_service_operations_by_mileage,
    parse_transportation_options,
    parse_update_service_appointment,
    parse_update_vehicle_preferred_dealer,
)
from .graphql_input import UNSET, UnsetType


class _DealerClientMixin(_NissanClientBase):
    async def async_get_all_dealers(
        self,
        *,
        vin: str | UnsetType | None = UNSET,
        page_size: int | UnsetType | None = UNSET,
    ) -> tuple[DealerSummary | None, ...] | None:
        """Return the compact dealer list with optional vehicle and page filters."""

        data = await self._transport.async_graphql(
            "AllDealers",
            operations.ALL_DEALERS,
            all_dealers_variables(vin, page_size),
        )
        return parse_all_dealers(data)

    async def async_get_dealers(
        self,
        postal_code: str,
    ) -> tuple[Dealer | None, ...] | None:
        """Return dealers matching a postal code."""

        data = await self._transport.async_graphql(
            "Dealers",
            operations.DEALERS,
            {"zip": postal_code},
        )
        return parse_dealers(data)

    async def async_search_dealers(
        self,
        *,
        vin: str | UnsetType | None = UNSET,
        service_code: ServiceCode | UnsetType | None = UNSET,
        radius: int | UnsetType | None = UNSET,
        latitude: float | UnsetType | None = UNSET,
        longitude: float | UnsetType | None = UNSET,
    ) -> tuple[Dealer | None, ...] | None:
        """Search dealers with independently optional vehicle and location filters."""

        data = await self._transport.async_graphql(
            "DealersBySearch",
            operations.DEALERS_BY_SEARCH,
            dealers_by_search_variables(
                vin=vin,
                service_code=service_code,
                radius=radius,
                latitude=latitude,
                longitude=longitude,
            ),
        )
        return parse_dealers(data)

    async def async_get_dealer_deals_and_images(
        self,
        dealer_id: str,
    ) -> DealerDealsAndImages:
        """Return coupons and coupon images for a dealer."""

        data = await self._transport.async_graphql(
            "DealsAndImagesByDealerId",
            operations.DEALS_AND_IMAGES_BY_DEALER_ID,
            {"dealerId": dealer_id},
        )
        return parse_dealer_deals_and_images(data)

    async def async_get_dealer(self, dealer_id: str) -> Dealer | None:
        """Return one dealer by identifier."""

        data = await self._transport.async_graphql(
            "GetDealerById",
            operations.GET_DEALER_BY_ID,
            {"dealerId": dealer_id},
        )
        return parse_dealer(data)

    async def async_generate_all_maintenance_visits(
        self,
        vin: str,
        mileage: MaintenanceMileageInput,
        severity_id: str,
        past_visits: int,
        future_visits: int,
    ) -> MaintenanceVisits | None:
        """Generate the requested past and future maintenance visits."""

        data = await self._transport.async_graphql(
            "GenerateAllVisits",
            operations.GENERATE_ALL_VISITS,
            maintenance_visits_variables(
                vin,
                mileage,
                severity_id,
                past_visits,
                future_visits,
            ),
        )
        return parse_maintenance_visits(data)

    async def async_generate_next_maintenance_visit(
        self,
        vin: str,
        mileage: MaintenanceMileageInput,
        severity_id: str,
        past_visits: int,
        future_visits: int,
    ) -> MaintenanceVisits | None:
        """Generate the next maintenance visit with a severity identifier."""

        data = await self._transport.async_graphql(
            "GenerateNextVisit",
            operations.GENERATE_NEXT_VISIT,
            maintenance_visits_variables(
                vin,
                mileage,
                severity_id,
                past_visits,
                future_visits,
            ),
        )
        return parse_maintenance_visits(data)

    async def async_generate_next_maintenance_visit_no_severity(
        self,
        vin: str,
        mileage: MaintenanceMileageInput,
        severity_id: str,
        past_visits: int,
        future_visits: int,
    ) -> MaintenanceVisits | None:
        """Call Nissan's separately named no-severity maintenance operation."""

        data = await self._transport.async_graphql(
            "GenerateNextVisitNoSeverity",
            operations.GENERATE_NEXT_VISIT_NO_SEVERITY,
            maintenance_visits_variables(
                vin,
                mileage,
                severity_id,
                past_visits,
                future_visits,
            ),
        )
        return parse_maintenance_visits(data)

    async def async_get_service_advisors(
        self,
        dealer_id: str,
        service_operation_ids: tuple[str, ...],
        *,
        vin: str | UnsetType | None = UNSET,
    ) -> tuple[ServiceAdvisor | None, ...] | None:
        """Return service advisors for selected dealer operations."""

        data = await self._transport.async_graphql(
            "ServiceAdvisors",
            operations.SERVICE_ADVISORS,
            service_advisors_variables(dealer_id, service_operation_ids, vin),
        )
        return parse_service_advisors(data)

    async def async_get_service_appointment_time_slots(
        self,
        dealer_id: str,
        service_operation_ids: tuple[str, ...],
        start_date: datetime,
        *,
        advisor_id: str | UnsetType | None = UNSET,
        transportation_code: str | UnsetType | None = UNSET,
        location_type: ServiceLocationType | UnsetType | None = UNSET,
        vin: str | UnsetType | None = UNSET,
    ) -> tuple[ServiceAppointmentTimeSlot | None, ...]:
        """Return available service appointment time slots."""

        data = await self._transport.async_graphql(
            "ServiceAppointmentTimeSlots",
            operations.SERVICE_APPOINTMENT_TIME_SLOTS,
            service_time_slots_variables(
                dealer_id,
                service_operation_ids,
                start_date,
                advisor_id=advisor_id,
                transportation_code=transportation_code,
                location_type=location_type,
                vin=vin,
            ),
        )
        return parse_service_appointment_time_slots(data)

    async def async_get_service_appointments(
        self,
        vin: str,
        *,
        start_date: datetime | UnsetType | None = UNSET,
        end_date: datetime | UnsetType | None = UNSET,
    ) -> tuple[ServiceAppointment | None, ...] | None:
        """Return service appointments for a vehicle and optional date-time range."""

        data = await self._transport.async_graphql(
            "ServiceAppointments",
            operations.SERVICE_APPOINTMENTS,
            service_appointments_variables(vin, start_date, end_date),
        )
        return parse_service_appointments(data)

    async def async_get_service_categories(
        self,
    ) -> tuple[ServiceCategory | None, ...] | None:
        """Return service categories and their operations."""

        data = await self._transport.async_graphql(
            "ServiceCategories",
            operations.SERVICE_CATEGORIES,
            {},
        )
        return parse_service_categories(data)

    async def async_get_service_operations(
        self,
        vin: str,
        dealer_id: str,
    ) -> tuple[DealerServiceOperation | None, ...] | None:
        """Return the service operations available for a vehicle and dealer."""

        data = await self._transport.async_graphql(
            "ServiceOperations",
            operations.SERVICE_OPERATIONS,
            {"vin": vin, "dealerId": dealer_id},
        )
        return parse_service_operations(data)

    async def async_get_service_operations_by_mileage(
        self,
        vin: str,
        dealer_id: str,
        mileage: int,
    ) -> tuple[ServiceOperationsAtInterval | None, ...] | None:
        """Return service operations grouped around the supplied mileage."""

        data = await self._transport.async_graphql(
            "ServiceOperationsByMileage",
            operations.SERVICE_OPERATIONS_BY_MILEAGE,
            {"vin": vin, "dealerId": dealer_id, "mileage": mileage},
        )
        return parse_service_operations_by_mileage(data)

    async def async_get_transportation_options(
        self,
        dealer_id: str,
        service_operation_ids: tuple[str, ...],
        *,
        vin: str | UnsetType | None = UNSET,
    ) -> tuple[ServiceTransportationOption | None, ...] | None:
        """Return transportation options for selected dealer operations."""

        data = await self._transport.async_graphql(
            "TransportationOptions",
            operations.TRANSPORTATION_OPTIONS,
            service_advisors_variables(dealer_id, service_operation_ids, vin),
        )
        return parse_transportation_options(data)

    async def async_cancel_service_appointment(
        self,
        appointment_id: str,
        dealer_id: str,
        *,
        vin: str | UnsetType | None = UNSET,
    ) -> CancelServiceAppointmentResult | None:
        """Cancel a service appointment."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CancelServiceAppointment",
            operations.CANCEL_SERVICE_APPOINTMENT,
            cancel_service_appointment_variables(appointment_id, dealer_id, vin),
        )
        return parse_cancel_service_appointment(data)

    async def async_create_service_appointment(
        self,
        appointment: ServiceAppointmentInput,
    ) -> ServiceAppointmentCreateResult | None:
        """Create a service appointment."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CreateServiceAppointment",
            operations.CREATE_SERVICE_APPOINTMENT,
            service_appointment_variables(appointment),
        )
        return parse_create_service_appointment(data)

    async def async_update_service_appointment(
        self,
        appointment_id: str,
        appointment: ServiceAppointmentInput,
    ) -> ServiceAppointmentUpdateResult | None:
        """Replace a service appointment's selected details."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateServiceAppointment",
            operations.UPDATE_SERVICE_APPOINTMENT,
            update_service_appointment_variables(appointment_id, appointment),
        )
        return parse_update_service_appointment(data)

    async def async_update_vehicle_preferred_dealer(
        self,
        vin: str,
        preferred_dealer_id: str,
    ) -> PreferredDealerUpdateResult | None:
        """Set the preferred dealer for a vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateVehiclePreferredDealer",
            operations.UPDATE_VEHICLE_PREFERRED_DEALER,
            {"vin": vin, "preferredDealerId": preferred_dealer_id},
        )
        return parse_update_vehicle_preferred_dealer(data)
