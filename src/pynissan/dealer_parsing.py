from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime

from .account_parsing import (
    _enum,
    _required_field,
    _required_int,
    _required_nullable_bool,
    _required_nullable_int,
    _required_nullable_string,
    _required_optional_typed_object,
    _required_string,
    _root,
    _typed_object,
    _typename,
)
from .dealer_models import (
    AppointmentServiceOperation,
    CancelServiceAppointmentResult,
    CreatedServiceAppointment,
    Dealer,
    DealerCoupon,
    DealerCouponImage,
    DealerDealsAndImages,
    DealerSchedule,
    DealerServiceOperation,
    DealerServiceSchedule,
    DealerSummary,
    MaintenanceInterval,
    MaintenanceServiceOccurrence,
    MaintenanceVisit,
    MaintenanceVisitAlignment,
    MaintenanceVisits,
    PreferredDealerUpdated,
    PreferredDealerUpdateError,
    PreferredDealerUpdateResult,
    ServiceAddress,
    ServiceAdvisor,
    ServiceAppointment,
    ServiceAppointmentCreateResult,
    ServiceAppointmentTimeSlot,
    ServiceAppointmentUpdateError,
    ServiceAppointmentUpdateResult,
    ServiceCategory,
    ServiceCategoryOperation,
    ServiceContactMethod,
    ServiceContactMethodType,
    ServiceDealership,
    ServiceDiscount,
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


def _parse_dealer_summary(value: Mapping[str, object], path: str) -> DealerSummary:
    return DealerSummary(
        dealer_id=_required_nullable_string(value, "dealerId", f"{path}.dealerId"),
        name=_required_nullable_string(value, "dealerName", f"{path}.dealerName"),
        address_line_1=_required_nullable_string(
            value,
            "dealerAddressLine1",
            f"{path}.dealerAddressLine1",
        ),
    )


def _parse_dealer(value: Mapping[str, object], path: str) -> Dealer:
    return Dealer(
        dealer_id=_required_nullable_string(value, "dealerId", f"{path}.dealerId"),
        name=_required_nullable_string(value, "dealerName", f"{path}.dealerName"),
        preferred=_optional_selected_nullable_bool(value, "isDealerPreferred", path),
        address_line_1=_required_nullable_string(
            value,
            "dealerAddressLine1",
            f"{path}.dealerAddressLine1",
        ),
        address_line_2=_optional_selected_nullable_string(value, "dealerAddressLine2", path),
        latitude=_required_nullable_float(value, "dealerLatitude", f"{path}.dealerLatitude"),
        longitude=_required_nullable_float(value, "dealerLongitude", f"{path}.dealerLongitude"),
        postal_code=_optional_selected_nullable_string(value, "dealerZip", path),
        country=_optional_selected_nullable_string(value, "dealerCountry", path),
        state_code=_optional_selected_nullable_string(value, "dealerStateCode", path),
        native_service_booking=_required_bool(
            value,
            "nativeServiceBooking",
            f"{path}.nativeServiceBooking",
        ),
        online_scheduling_mobile_url=_optional_selected_nullable_string(
            value,
            "dealerOnlineSchedulingMobileUrl",
            path,
        ),
        city_name=_optional_selected_nullable_string(value, "dealerCityName", path),
        phone_number=_optional_selected_nullable_string(value, "dealerPhoneNumber", path),
        service_phone=_optional_selected_nullable_string(value, "dealerServicePhone", path),
        website=_optional_selected_nullable_string(value, "dealerWebsite", path),
        languages_spoken=(
            None
            if "languagesSpoken" not in value
            else _required_string_list(value, "languagesSpoken", path)
        ),
        email_address=_optional_selected_nullable_string(value, "dealerEmailAddress", path),
        service_hours=_optional_selected_nullable_string(value, "dealerServiceHours", path),
        service_schedules=_optional_selected_nullable_list(
            value,
            "dealerServicesSchedules",
            path,
            _parse_dealer_service_schedule,
        ),
    )


def _parse_dealer_service_schedule(
    value: Mapping[str, object],
    path: str,
) -> DealerServiceSchedule:
    return DealerServiceSchedule(
        code=_optional_selected_nullable_string(value, "code", path),
        name=_required_nullable_string(value, "name", f"{path}.name"),
        schedules=_nullable_list(value, "schedules", f"{path}.schedules", _parse_dealer_schedule),
    )


def _parse_dealer_schedule(value: Mapping[str, object], path: str) -> DealerSchedule:
    return DealerSchedule(
        day_of_week=_required_string(value, "dayOfWeek", f"{path}.dayOfWeek"),
        end_time=_required_nullable_string(value, "endTime", f"{path}.endTime"),
        opened=_required_bool(value, "opened", f"{path}.opened"),
        start_time=_required_nullable_string(value, "startTime", f"{path}.startTime"),
    )


def _parse_coupon(value: Mapping[str, object], path: str) -> DealerCoupon:
    return DealerCoupon(
        coupon_id=_required_nullable_string(value, "couponId", f"{path}.couponId"),
        title=_required_nullable_string(value, "couponTitle", f"{path}.couponTitle"),
        disclaimer=_required_nullable_string(
            value,
            "standardDisclaimer",
            f"{path}.standardDisclaimer",
        ),
    )


def _parse_coupon_image(value: Mapping[str, object], path: str) -> DealerCouponImage:
    return DealerCouponImage(
        coupon_id=_required_nullable_string(value, "couponId", f"{path}.couponId"),
        image_url=_required_nullable_string(value, "couponImageUrl", f"{path}.couponImageUrl"),
    )


def _parse_maintenance_visit(value: Mapping[str, object], path: str) -> MaintenanceVisit:
    alignment = _required_field(value, "Alignment", f"{path}.Alignment")
    interval_path = f"{path}.Interval"
    interval = _required_optional_typed_object(value, "Interval", interval_path)
    return MaintenanceVisit(
        alignment=(
            None
            if alignment is None
            else _enum(alignment, MaintenanceVisitAlignment, f"{path}.Alignment")
        ),
        interval=(
            None
            if interval is None
            else MaintenanceInterval(
                month=_required_nullable_int(interval, "Month", f"{interval_path}.Month"),
                year=_required_nullable_int(interval, "Year", f"{interval_path}.Year"),
                next=_required_nullable_bool(interval, "Next", f"{interval_path}.Next"),
                distance_miles=_required_nullable_int(
                    interval,
                    "DistanceMiles",
                    f"{interval_path}.DistanceMiles",
                ),
                distance_km=_required_nullable_int(
                    interval,
                    "DistanceKMs",
                    f"{interval_path}.DistanceKMs",
                ),
            )
        ),
        service_occurrences=_nullable_list(
            value,
            "ServiceOccurrences",
            f"{path}.ServiceOccurrences",
            _parse_maintenance_occurrence,
        ),
    )


def _parse_maintenance_occurrence(
    value: Mapping[str, object],
    path: str,
) -> MaintenanceServiceOccurrence:
    component_path = f"{path}.ServiceComponent"
    component = _required_optional_typed_object(value, "ServiceComponent", component_path)
    component_name = None
    category_name = None
    if component is not None:
        component_name = _required_nullable_string(
            component,
            "ServiceComponentName",
            f"{component_path}.ServiceComponentName",
        )
        category_path = f"{component_path}.ServiceCategory"
        category = _required_optional_typed_object(component, "ServiceCategory", category_path)
        if category is not None:
            category_name = _required_string(
                category,
                "ServiceCategoryName",
                f"{category_path}.ServiceCategoryName",
            )
    service_type_path = f"{path}.ServiceType"
    service_type = _required_optional_typed_object(value, "ServiceType", service_type_path)
    if service_type is None:
        raise ResponseError(f"{service_type_path} is null")
    group_path = f"{service_type_path}.ServiceTypeGroup"
    group = _required_optional_typed_object(service_type, "ServiceTypeGroup", group_path)
    if group is None:
        raise ResponseError(f"{group_path} is null")
    return MaintenanceServiceOccurrence(
        component_name,
        category_name,
        _required_string(
            service_type,
            "ServiceTypeName",
            f"{service_type_path}.ServiceTypeName",
        ),
        _required_string(group, "ServiceTypeGroupName", f"{group_path}.ServiceTypeGroupName"),
    )


def _parse_service_advisor(value: Mapping[str, object], path: str) -> ServiceAdvisor:
    return ServiceAdvisor(
        advisor_id=_required_nullable_string(value, "advisorId", f"{path}.advisorId"),
        name=_required_nullable_string(value, "name", f"{path}.name"),
        job_title=_required_nullable_string(value, "jobTitle", f"{path}.jobTitle"),
        email=_required_nullable_string(value, "email", f"{path}.email"),
        image_url=_required_nullable_string(value, "imageUrl", f"{path}.imageUrl"),
    )


def _parse_time_slot(value: Mapping[str, object], path: str) -> ServiceAppointmentTimeSlot:
    times = _required_field(value, "timeslots", f"{path}.timeslots")
    if not isinstance(times, list):
        raise ResponseError(f"{path}.timeslots is not a list")
    parsed_times: list[datetime | None] = []
    for index, item in enumerate(times):
        if item is None:
            parsed_times.append(None)
            continue
        item_path = f"{path}.timeslots[{index}]"
        timeslot = _typed_object(item, item_path)
        parsed_times.append(_required_datetime(timeslot, "time", f"{item_path}.time"))
    return ServiceAppointmentTimeSlot(
        is_open=_required_nullable_bool(value, "isOpen", f"{path}.isOpen"),
        date=_required_datetime(value, "date", f"{path}.date"),
        times=tuple(parsed_times),
    )


def _parse_service_appointment(value: Mapping[str, object], path: str) -> ServiceAppointment:
    dealership_path = f"{path}.dealership"
    dealership = _required_optional_typed_object(value, "dealership", dealership_path)
    if dealership is None:
        raise ResponseError(f"{dealership_path} is null")
    customer_path = f"{path}.customer"
    customer = _required_optional_typed_object(value, "customer", customer_path)
    if customer is None:
        raise ResponseError(f"{customer_path} is null")
    pick_up_path = f"{path}.pickUpAddress"
    pick_up = _required_optional_typed_object(value, "pickUpAddress", pick_up_path)
    drop_off_path = f"{path}.dropOffAddress"
    drop_off = _required_optional_typed_object(value, "dropOffAddress", drop_off_path)
    transport_path = f"{path}.transport"
    transport = _required_optional_typed_object(value, "transport", transport_path)
    advisor_path = f"{path}.advisor"
    advisor = _required_optional_typed_object(value, "advisor", advisor_path)
    operations = _nullable_list(
        value,
        "serviceOperations",
        f"{path}.serviceOperations",
        _parse_appointment_operation,
    )
    if operations is None:
        raise ResponseError(f"{path}.serviceOperations is null")
    return ServiceAppointment(
        appointment_id=_required_nullable_string(value, "appointmentId", f"{path}.appointmentId"),
        appointment_date=_required_datetime(value, "appointmentDate", f"{path}.appointmentDate"),
        dealer_id=_required_string(value, "dealerId", f"{path}.dealerId"),
        editable=_required_nullable_bool(value, "isEditable", f"{path}.isEditable"),
        dealership=_parse_dealership(dealership, dealership_path),
        pick_up_address=_parse_service_address(pick_up, pick_up_path, pick_up=True),
        drop_off_address=_parse_service_address(drop_off, drop_off_path, pick_up=False),
        transport=(
            None if transport is None else _parse_transportation_option(transport, transport_path)
        ),
        contact_methods=_nullable_list(
            customer,
            "contactMethod",
            f"{customer_path}.contactMethod",
            _parse_contact_method,
        ),
        service_operations=operations,
        advisor=None if advisor is None else _parse_service_advisor(advisor, advisor_path),
        additional_comments=_required_nullable_string(
            value,
            "additionalComments",
            f"{path}.additionalComments",
        ),
    )


def _parse_dealership(value: Mapping[str, object], path: str) -> ServiceDealership:
    return ServiceDealership(
        name=_required_nullable_string(value, "dealerName", f"{path}.dealerName"),
        address_line_1=_required_nullable_string(
            value,
            "dealerAddressLine1",
            f"{path}.dealerAddressLine1",
        ),
        address_line_2=_required_nullable_string(
            value,
            "dealerAddressLine2",
            f"{path}.dealerAddressLine2",
        ),
        city_name=_required_nullable_string(value, "dealerCityName", f"{path}.dealerCityName"),
        state_code=_required_nullable_string(value, "dealerStateCode", f"{path}.dealerStateCode"),
        phone_number=_required_nullable_string(
            value,
            "dealerPhoneNumber",
            f"{path}.dealerPhoneNumber",
        ),
    )


def _parse_service_address(
    value: Mapping[str, object] | None,
    path: str,
    *,
    pick_up: bool,
) -> ServiceAddress | None:
    if value is None:
        return None
    return ServiceAddress(
        address_1=_required_nullable_string(value, "address1", f"{path}.address1"),
        address_2=_required_nullable_string(value, "address2", f"{path}.address2"),
        city=_required_nullable_string(value, "city", f"{path}.city"),
        state=_required_nullable_string(value, "state", f"{path}.state"),
        postal_code=_required_nullable_string(value, "postalCode", f"{path}.postalCode"),
        country=_required_nullable_string(value, "country", f"{path}.country"),
        neighbourhood=(
            _optional_selected_nullable_string(value, "neighbourhood", path) if pick_up else None
        ),
        district=_optional_selected_nullable_string(value, "district", path),
        street_number=_optional_selected_nullable_string(value, "streetNumber", path),
    )


def _parse_transportation_option(
    value: Mapping[str, object],
    path: str,
) -> ServiceTransportationOption:
    return ServiceTransportationOption(
        code=_required_string(value, "code", f"{path}.code"),
        name=_required_string(value, "name", f"{path}.name"),
        is_valet=_required_bool(value, "isValet", f"{path}.isValet"),
        is_loaner_available=_required_bool(
            value,
            "isLoanerAvailable",
            f"{path}.isLoanerAvailable",
        ),
    )


def _parse_contact_method(value: Mapping[str, object], path: str) -> ServiceContactMethod:
    return ServiceContactMethod(
        type=_enum(
            _required_field(value, "type", f"{path}.type"),
            ServiceContactMethodType,
            f"{path}.type",
        ),
        value=_required_string(value, "value", f"{path}.value"),
    )


def _parse_appointment_operation(
    value: Mapping[str, object],
    path: str,
) -> AppointmentServiceOperation:
    return AppointmentServiceOperation(
        operation_code_description=_required_nullable_string(
            value,
            "opCodeDescription",
            f"{path}.opCodeDescription",
        ),
        operation_code_id=_required_nullable_string(value, "opCodeID", f"{path}.opCodeID"),
        customer_comments=_required_nullable_string(
            value,
            "customerComments",
            f"{path}.customerComments",
        ),
        category_name=_required_nullable_string(
            value,
            "serviceCategoryName",
            f"{path}.serviceCategoryName",
        ),
        description=_required_nullable_string(
            value,
            "serviceOperationsDescription",
            f"{path}.serviceOperationsDescription",
        ),
    )


def _parse_service_category(value: Mapping[str, object], path: str) -> ServiceCategory:
    operations = _nullable_list(
        value,
        "serviceOperations",
        f"{path}.serviceOperations",
        _parse_category_operation,
    )
    if operations is None:
        raise ResponseError(f"{path}.serviceOperations is null")
    return ServiceCategory(
        category_id=_required_int(value, "serviceCategoryId", f"{path}.serviceCategoryId"),
        name=_required_string(value, "serviceCategoryName", f"{path}.serviceCategoryName"),
        description=_required_string(
            value,
            "serviceCategoryDescription",
            f"{path}.serviceCategoryDescription",
        ),
        operations=operations,
    )


def _parse_category_operation(
    value: Mapping[str, object],
    path: str,
) -> ServiceCategoryOperation:
    return ServiceCategoryOperation(
        operation_code_id=_required_int(value, "opCodeID", f"{path}.opCodeID"),
        description=_required_string(value, "opCodeDescription", f"{path}.opCodeDescription"),
    )


def _parse_service_operation(
    value: Mapping[str, object],
    path: str,
) -> DealerServiceOperation:
    return DealerServiceOperation(
        operation_code_id=_required_nullable_string(value, "opCodeID", f"{path}.opCodeID"),
        operation_code_description=_required_nullable_string(
            value,
            "opCodeDescription",
            f"{path}.opCodeDescription",
        ),
        customer_comments=_required_nullable_string(
            value,
            "customerComments",
            f"{path}.customerComments",
        ),
        description=_required_nullable_string(
            value,
            "serviceOperationsDescription",
            f"{path}.serviceOperationsDescription",
        ),
        package=_required_string(value, "package", f"{path}.package"),
        maintenance=_required_nullable_bool(value, "maintenance", f"{path}.maintenance"),
        validation=_required_nullable_bool(value, "validation", f"{path}.validation"),
        price=_required_nullable_float(value, "price", f"{path}.price"),
        labor_hours=_required_nullable_float(value, "laborHours", f"{path}.laborHours"),
        discounts=_nullable_list(value, "discounts", f"{path}.discounts", _parse_discount),
    )


def _parse_discount(value: Mapping[str, object], path: str) -> ServiceDiscount:
    return ServiceDiscount(
        code=_required_nullable_string(value, "code", f"{path}.code"),
        description=_required_nullable_string(value, "description", f"{path}.description"),
        price=_required_nullable_float(value, "price", f"{path}.price"),
    )


def _parse_service_operations_at_interval(
    value: Mapping[str, object],
    path: str,
) -> ServiceOperationsAtInterval:
    return ServiceOperationsAtInterval(
        mileage=_required_nullable_int(value, "intervalMileage", f"{path}.intervalMileage"),
        operations=_nullable_list(
            value,
            "serviceOperations",
            f"{path}.serviceOperations",
            _parse_service_operation,
        ),
    )


def _nullable_list[ItemT](
    container: Mapping[str, object],
    field: str,
    path: str,
    parser: Callable[[Mapping[str, object], str], ItemT],
) -> tuple[ItemT | None, ...] | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    if not isinstance(value, list):
        raise ResponseError(f"{path} is not a list")
    result: list[ItemT | None] = []
    for index, item in enumerate(value):
        if item is None:
            result.append(None)
            continue
        item_path = f"{path}[{index}]"
        result.append(parser(_typed_object(item, item_path), item_path))
    return tuple(result)


def _optional_selected_nullable_list[ItemT](
    container: Mapping[str, object],
    field: str,
    parent_path: str,
    parser: Callable[[Mapping[str, object], str], ItemT],
) -> tuple[ItemT | None, ...] | None:
    if field not in container:
        return None
    return _nullable_list(container, field, f"{parent_path}.{field}", parser)


def _required_string_list(
    container: Mapping[str, object],
    field: str,
    parent_path: str,
) -> tuple[str, ...]:
    path = f"{parent_path}.{field}"
    value = _required_field(container, field, path)
    if not isinstance(value, list):
        raise ResponseError(f"{path} is not a list")
    result: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str):
            raise ResponseError(f"{path}[{index}] is not a string")
        result.append(item)
    return tuple(result)


def _optional_selected_nullable_string(
    container: Mapping[str, object],
    field: str,
    parent_path: str,
) -> str | None:
    if field not in container:
        return None
    return _required_nullable_string(container, field, f"{parent_path}.{field}")


def _optional_selected_nullable_bool(
    container: Mapping[str, object],
    field: str,
    parent_path: str,
) -> bool | None:
    if field not in container:
        return None
    return _required_nullable_bool(container, field, f"{parent_path}.{field}")


def _required_bool(container: Mapping[str, object], field: str, path: str) -> bool:
    value = _required_field(container, field, path)
    if not isinstance(value, bool):
        raise ResponseError(f"{path} is not a boolean")
    return value


def _required_nullable_float(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> float | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    if not isinstance(value, int | float) or isinstance(value, bool):
        raise ResponseError(f"{path} is not a number")
    return float(value)


def _required_datetime(container: Mapping[str, object], field: str, path: str) -> datetime:
    value = _required_string(container, field, path)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ResponseError(f"{path} is not an ISO date-time") from None
