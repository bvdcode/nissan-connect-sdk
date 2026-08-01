from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime

from ._dealer_value_parsing import (
    _nullable_list,
    _optional_selected_nullable_string,
    _required_bool,
    _required_datetime,
    _required_nullable_float,
)
from .account_parsing import (
    _enum,
    _required_field,
    _required_int,
    _required_nullable_bool,
    _required_nullable_int,
    _required_nullable_string,
    _required_optional_typed_object,
    _required_string,
    _typed_object,
)
from .dealer_models import (
    AppointmentServiceOperation,
    DealerServiceOperation,
    ServiceAddress,
    ServiceAdvisor,
    ServiceAppointment,
    ServiceAppointmentTimeSlot,
    ServiceCategory,
    ServiceCategoryOperation,
    ServiceContactMethod,
    ServiceContactMethodType,
    ServiceDealership,
    ServiceDiscount,
    ServiceOperationsAtInterval,
    ServiceTransportationOption,
)
from .exceptions import ResponseError


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
