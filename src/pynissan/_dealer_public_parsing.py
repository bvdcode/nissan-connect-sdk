from __future__ import annotations

from collections.abc import Mapping

from ._dealer_appointment_parsing import (
    _parse_service_address,
    _parse_service_advisor,
    _parse_service_appointment,
    _parse_service_category,
    _parse_service_operation,
    _parse_service_operations_at_interval,
    _parse_time_slot,
    _parse_transportation_option,
)
from ._dealer_detail_parsing import (
    _parse_coupon,
    _parse_coupon_image,
    _parse_dealer,
    _parse_dealer_summary,
    _parse_maintenance_visit,
)
from ._dealer_value_parsing import _nullable_list, _required_datetime
from .account_parsing import (
    _required_field,
    _required_nullable_bool,
    _required_nullable_string,
    _required_optional_typed_object,
    _required_string,
    _root,
    _typed_object,
    _typename,
)
from .dealer_models import (
    CancelServiceAppointmentResult,
    CreatedServiceAppointment,
    Dealer,
    DealerDealsAndImages,
    DealerServiceOperation,
    DealerSummary,
    MaintenanceVisits,
    PreferredDealerUpdated,
    PreferredDealerUpdateError,
    PreferredDealerUpdateResult,
    ServiceAdvisor,
    ServiceAppointment,
    ServiceAppointmentCreateResult,
    ServiceAppointmentTimeSlot,
    ServiceAppointmentUpdateError,
    ServiceAppointmentUpdateResult,
    ServiceCategory,
    ServiceOperationsAtInterval,
    ServiceTransportationOption,
    UnselectedDealerResult,
    UpdatedServiceAppointment,
)
from .exceptions import ResponseError


def parse_all_dealers(
    data: Mapping[str, object],
) -> tuple[DealerSummary | None, ...] | None:
    """Parse the nullable compact dealer list."""

    return _nullable_list(data, "dealers", "dealers", _parse_dealer_summary)


def parse_dealers(data: Mapping[str, object]) -> tuple[Dealer | None, ...] | None:
    """Parse nullable full dealer search results."""

    return _nullable_list(data, "dealers", "dealers", _parse_dealer)


def parse_dealer(data: Mapping[str, object]) -> Dealer | None:
    """Parse one nullable full dealer result."""

    root = _root(data, "dealer")
    return None if root is None else _parse_dealer(root, "dealer")


def parse_dealer_deals_and_images(data: Mapping[str, object]) -> DealerDealsAndImages:
    """Parse the two nullable dealer coupon collections."""

    deals = _root(data, "dealsByDealerId")
    images = _root(data, "dealsImagesByDealerId")
    coupons = None
    if deals is not None:
        coupons = _nullable_list(deals, "coupon", "dealsByDealerId.coupon", _parse_coupon)
    coupon_images = None
    if images is not None:
        coupon_images = _nullable_list(
            images,
            "coupons",
            "dealsImagesByDealerId.coupons",
            _parse_coupon_image,
        )
    return DealerDealsAndImages(coupons, coupon_images)


def parse_maintenance_visits(data: Mapping[str, object]) -> MaintenanceVisits | None:
    """Parse generated maintenance schedule visits."""

    viewer = _root(data, "viewer")
    if viewer is None:
        return None
    schedule_path = "viewer.Schedule"
    schedule = _required_optional_typed_object(viewer, "Schedule", schedule_path)
    if schedule is None:
        raise ResponseError(f"{schedule_path} is null")
    return MaintenanceVisits(
        _nullable_list(schedule, "Visits", f"{schedule_path}.Visits", _parse_maintenance_visit)
    )


def parse_service_advisors(
    data: Mapping[str, object],
) -> tuple[ServiceAdvisor | None, ...] | None:
    """Parse nullable service advisor results."""

    return _nullable_list(data, "serviceAdvisors", "serviceAdvisors", _parse_service_advisor)


def parse_service_appointment_time_slots(
    data: Mapping[str, object],
) -> tuple[ServiceAppointmentTimeSlot | None, ...]:
    """Parse the required service appointment time-slot list."""

    value = _required_field(
        data,
        "serviceAppointmentTimeSlots",
        "serviceAppointmentTimeSlots",
    )
    if not isinstance(value, list):
        raise ResponseError("serviceAppointmentTimeSlots is not a list")
    result: list[ServiceAppointmentTimeSlot | None] = []
    for index, item in enumerate(value):
        if item is None:
            result.append(None)
            continue
        path = f"serviceAppointmentTimeSlots[{index}]"
        result.append(_parse_time_slot(_typed_object(item, path), path))
    return tuple(result)


def parse_service_appointments(
    data: Mapping[str, object],
) -> tuple[ServiceAppointment | None, ...] | None:
    """Parse nullable existing service appointments."""

    return _nullable_list(
        data,
        "serviceAppointments",
        "serviceAppointments",
        _parse_service_appointment,
    )


def parse_service_categories(
    data: Mapping[str, object],
) -> tuple[ServiceCategory | None, ...] | None:
    """Parse nullable service categories."""

    return _nullable_list(data, "serviceCategories", "serviceCategories", _parse_service_category)


def parse_service_operations(
    data: Mapping[str, object],
) -> tuple[DealerServiceOperation | None, ...] | None:
    """Parse nullable service operations."""

    return _nullable_list(data, "serviceOperations", "serviceOperations", _parse_service_operation)


def parse_service_operations_by_mileage(
    data: Mapping[str, object],
) -> tuple[ServiceOperationsAtInterval | None, ...] | None:
    """Parse service operations grouped by closest mileage intervals."""

    root = _root(data, "serviceOperationsByMileage")
    if root is None:
        return None
    return _nullable_list(
        root,
        "servicesAtClosestIntervals",
        "serviceOperationsByMileage.servicesAtClosestIntervals",
        _parse_service_operations_at_interval,
    )


def parse_transportation_options(
    data: Mapping[str, object],
) -> tuple[ServiceTransportationOption | None, ...] | None:
    """Parse nullable appointment transportation options."""

    return _nullable_list(
        data,
        "transportationOptions",
        "transportationOptions",
        _parse_transportation_option,
    )


def parse_cancel_service_appointment(
    data: Mapping[str, object],
) -> CancelServiceAppointmentResult | None:
    """Parse nullable service appointment cancellation status."""

    field = "cancelServiceAppointment"
    root = _root(data, field)
    if root is None:
        return None
    return CancelServiceAppointmentResult(
        _required_nullable_bool(root, "success", f"{field}.success")
    )


def parse_create_service_appointment(
    data: Mapping[str, object],
) -> ServiceAppointmentCreateResult | None:
    """Parse the selected service appointment creation branch."""

    field = "createServiceAppointment"
    root = _root(data, field)
    if root is None:
        return None
    typename = _typename(root, field)
    if typename == "ServiceAppointment":
        return CreatedServiceAppointment(
            _required_nullable_string(root, "appointmentId", f"{field}.appointmentId")
        )
    return UnselectedDealerResult(typename)


def parse_update_service_appointment(
    data: Mapping[str, object],
) -> ServiceAppointmentUpdateResult | None:
    """Parse every selected service appointment update union branch."""

    field = "updateServiceAppointment"
    root = _root(data, field)
    if root is None:
        return None
    typename = _typename(root, field)
    if typename == "ServiceAppointmentError":
        return ServiceAppointmentUpdateError(
            message=_required_string(root, "message", f"{field}.message"),
            error=_required_nullable_string(root, "error", f"{field}.error"),
        )
    if typename != "ServiceAppointment":
        return UnselectedDealerResult(typename)
    pick_up_path = f"{field}.pickUpAddress"
    pick_up = _required_optional_typed_object(root, "pickUpAddress", pick_up_path)
    transport_path = f"{field}.transport"
    transport = _required_optional_typed_object(root, "transport", transport_path)
    vehicle_path = f"{field}.vehicle"
    vehicle = _required_optional_typed_object(root, "vehicle", vehicle_path)
    if vehicle is None:
        raise ResponseError(f"{vehicle_path} is null")
    return UpdatedServiceAppointment(
        dealer_id=_required_string(root, "dealerId", f"{field}.dealerId"),
        appointment_id=_required_nullable_string(
            root,
            "appointmentId",
            f"{field}.appointmentId",
        ),
        appointment_date=_required_datetime(
            root,
            "appointmentDate",
            f"{field}.appointmentDate",
        ),
        additional_comments=_required_nullable_string(
            root,
            "additionalComments",
            f"{field}.additionalComments",
        ),
        pick_up_address=_parse_service_address(pick_up, pick_up_path, pick_up=True),
        transport_name=(
            None
            if transport is None
            else _required_string(transport, "name", f"{transport_path}.name")
        ),
        type=_required_string(root, "type", f"{field}.type"),
        vin=_required_string(vehicle, "vin", f"{vehicle_path}.vin"),
    )


def parse_update_vehicle_preferred_dealer(
    data: Mapping[str, object],
) -> PreferredDealerUpdateResult | None:
    """Parse every generated preferred-dealer update union branch."""

    field = "updateVehicle"
    root = _root(data, field)
    if root is None:
        return None
    typename = _typename(root, field)
    if typename == "UpdateVehicleSuccessResponse":
        return PreferredDealerUpdated(
            _required_nullable_string(root, "preferredDealer", f"{field}.preferredDealer")
        )
    if typename in {
        "RequiresAtLeastOneArgumentError",
        "InvalidVINError",
        "VINNotFoundError",
        "UpdateVehicleGeneralError",
    }:
        return PreferredDealerUpdateError(
            typename,
            _required_string(root, "message", f"{field}.message"),
        )
    return UnselectedDealerResult(typename)
