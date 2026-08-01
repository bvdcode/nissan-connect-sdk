from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .common_inputs import AddressInput, address_input
from .graphql_input import (
    UNSET,
    UnsetType,
    optional_input_fields,
    serialize_datetime,
    serialize_enum,
)
from .models import DistanceUnit


class ServiceCode(StrEnum):
    """Known dealer service filters."""

    SERVICE = "SERVICE"
    NISSAN_SALES = "NISSAN_SALES"
    BODY_AND_PAINT = "BODY_AND_PAINT"
    CUSTOMER_SERVICE = "CUSTOMER_SERVICE"
    ONLINE_SUPPORT = "ONLINE_SUPPORT"
    CLOSED_SALES = "CLOSED_SALES"
    CLOSED_DISTRIBUTOR = "CLOSED_DISTRIBUTOR"
    FLEET = "FLEET"
    SERVICE_LEAF = "SERVICE_LEAF"
    VALUE_ADVANTAGE = "VALUE_ADVANTAGE"
    NITROGEN = "NITROGEN"
    SALES = "SALES"
    SHOWROOM = "SHOWROOM"
    TEST_DRIVE = "TEST_DRIVE"
    GENERAL = "GENERAL"
    UNKNOWN_VALUE = "UNKNOWN__"


class ServiceLocationType(StrEnum):
    """Known service transportation address roles."""

    PICK_UP = "pick_up"
    DROP_OFF = "drop_off"
    UNKNOWN_VALUE = "UNKNOWN__"


@dataclass(frozen=True, slots=True)
class MaintenanceMileageInput:
    """Optional metric and imperial maintenance mileage values."""

    monthly_km: int | UnsetType | None = UNSET
    total_km: int | UnsetType | None = UNSET
    monthly_mile: int | UnsetType | None = UNSET
    total_mile: int | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class ServiceCustomerInput:
    """Required customer phone and email for a service appointment."""

    phone: str
    email: str


@dataclass(frozen=True, slots=True)
class ServiceDiscountInput:
    """Optional nullable discount fields copied into an appointment operation."""

    code: str | UnsetType | None = UNSET
    description: str | UnsetType | None = UNSET
    price: float | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class ServiceOperationInput:
    """Optional nullable fields for one requested service operation."""

    operation_code_id: str | UnsetType | None = UNSET
    operation_code_description: str | UnsetType | None = UNSET
    customer_comments: str | UnsetType | None = UNSET
    description: str | UnsetType | None = UNSET
    package: str | UnsetType | None = UNSET
    maintenance: bool | UnsetType | None = UNSET
    validation: bool | UnsetType | None = UNSET
    price: float | UnsetType | None = UNSET
    labor_hours: float | UnsetType | None = UNSET
    discounts: tuple[ServiceDiscountInput | None, ...] | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class ServiceAdvisorInput:
    """Optional nullable advisor fields copied into an appointment."""

    advisor_id: str | UnsetType | None = UNSET
    name: str | UnsetType | None = UNSET
    job_title: str | UnsetType | None = UNSET
    email: str | UnsetType | None = UNSET
    image_url: str | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class TransportationPreferencesInput:
    """Optional nullable appointment transportation preferences."""

    valet_required: bool | UnsetType | None = UNSET
    loaner_required: bool | UnsetType | None = UNSET
    pick_up_required: bool | UnsetType | None = UNSET
    drop_off_required: bool | UnsetType | None = UNSET
    reminders: str | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class TransportationOptionInput:
    """Required transportation identity and optional preference details."""

    code: str
    name: str
    is_valet: bool | UnsetType | None = UNSET
    is_loaner_available: bool | UnsetType | None = UNSET
    comments: str | UnsetType | None = UNSET
    preferences: TransportationPreferencesInput | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class ServiceOdometerInput:
    """Required appointment odometer value and unit."""

    unit: DistanceUnit
    value: int


@dataclass(frozen=True, slots=True)
class ServiceAppointmentInput:
    """Complete service appointment input from the mobile schema."""

    vin: str
    dealer_id: str
    appointment_date: datetime
    contact_methods: ServiceCustomerInput
    service_operations: tuple[ServiceOperationInput | None, ...]
    odometer: ServiceOdometerInput
    drop_off_address: AddressInput | UnsetType | None = UNSET
    pick_up_address: AddressInput | UnsetType | None = UNSET
    transport: TransportationOptionInput | UnsetType | None = UNSET
    advisor: ServiceAdvisorInput | UnsetType | None = UNSET
    additional_comments: str | UnsetType | None = UNSET


def all_dealers_variables(
    vin: str | UnsetType | None = UNSET,
    page_size: int | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize optional compact dealer-list filters."""

    return optional_input_fields(vin=vin, pageSize=page_size)


def dealers_by_search_variables(
    *,
    vin: str | UnsetType | None = UNSET,
    service_code: ServiceCode | UnsetType | None = UNSET,
    radius: int | UnsetType | None = UNSET,
    latitude: float | UnsetType | None = UNSET,
    longitude: float | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize independently optional dealer search filters."""

    serialized_service_code: object = service_code
    if isinstance(service_code, ServiceCode):
        serialized_service_code = serialize_enum(service_code)
    return optional_input_fields(
        vin=vin,
        serviceCode=serialized_service_code,
        radius=radius,
        latitude=latitude,
        longitude=longitude,
    )


def maintenance_visits_variables(
    vin: str,
    mileage: MaintenanceMileageInput,
    severity_id: str,
    past_visits: int,
    future_visits: int,
) -> dict[str, object]:
    """Serialize maintenance-visit generation variables."""

    return {
        "vin": vin,
        "mileage": optional_input_fields(
            monthlyKM=mileage.monthly_km,
            totalKM=mileage.total_km,
            monthlyMile=mileage.monthly_mile,
            totalMile=mileage.total_mile,
        ),
        "severityId": severity_id,
        "pastVisits": past_visits,
        "futureVisits": future_visits,
    }


def service_advisors_variables(
    dealer_id: str,
    service_operation_ids: tuple[str, ...],
    vin: str | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize advisor and transportation-option lookup variables."""

    return optional_input_fields(
        dealerId=dealer_id,
        serviceOperationIds=list(service_operation_ids),
        vin=vin,
    )


def service_time_slots_variables(
    dealer_id: str,
    service_operation_ids: tuple[str, ...],
    start_date: datetime,
    *,
    advisor_id: str | UnsetType | None = UNSET,
    transportation_code: str | UnsetType | None = UNSET,
    location_type: ServiceLocationType | UnsetType | None = UNSET,
    vin: str | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize service appointment time-slot filters."""

    serialized_location_type: object = location_type
    if isinstance(location_type, ServiceLocationType):
        serialized_location_type = serialize_enum(location_type)
    return optional_input_fields(
        dealerId=dealer_id,
        serviceOperationIds=list(service_operation_ids),
        startDate=serialize_datetime(start_date),
        advisorId=advisor_id,
        transportationCode=transportation_code,
        locationType=serialized_location_type,
        vin=vin,
    )


def service_appointments_variables(
    vin: str,
    start_date: datetime | UnsetType | None = UNSET,
    end_date: datetime | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize a vehicle and optional appointment date-time range."""

    serialized_start: object = (
        serialize_datetime(start_date) if isinstance(start_date, datetime) else start_date
    )
    serialized_end: object = (
        serialize_datetime(end_date) if isinstance(end_date, datetime) else end_date
    )
    return optional_input_fields(vin=vin, startDate=serialized_start, endDate=serialized_end)


def service_appointment_variables(config: ServiceAppointmentInput) -> dict[str, object]:
    """Serialize a complete appointment input."""

    drop_off: object = config.drop_off_address
    if isinstance(config.drop_off_address, AddressInput):
        drop_off = address_input(config.drop_off_address)
    pick_up: object = config.pick_up_address
    if isinstance(config.pick_up_address, AddressInput):
        pick_up = address_input(config.pick_up_address)
    transport: object = config.transport
    if isinstance(config.transport, TransportationOptionInput):
        transport = _transportation_option_input(config.transport)
    advisor: object = config.advisor
    if isinstance(config.advisor, ServiceAdvisorInput):
        advisor = _service_advisor_input(config.advisor)
    return {
        "appointment": optional_input_fields(
            vin=config.vin,
            dealerId=config.dealer_id,
            appointmentDate=serialize_datetime(config.appointment_date),
            contactMethods={
                "phone": config.contact_methods.phone,
                "email": config.contact_methods.email,
            },
            dropOffAddress=drop_off,
            pickUpAddress=pick_up,
            transport=transport,
            serviceOperations=[
                None if operation is None else _service_operation_input(operation)
                for operation in config.service_operations
            ],
            advisor=advisor,
            odometer={
                "unit": serialize_enum(config.odometer.unit),
                "value": config.odometer.value,
            },
            additionalComments=config.additional_comments,
        )
    }


def update_service_appointment_variables(
    appointment_id: str,
    config: ServiceAppointmentInput,
) -> dict[str, object]:
    """Serialize an appointment ID and replacement appointment fields."""

    return {"appointmentId": appointment_id, **service_appointment_variables(config)}


def cancel_service_appointment_variables(
    appointment_id: str,
    dealer_id: str,
    vin: str | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize service appointment cancellation variables."""

    return optional_input_fields(appointmentId=appointment_id, dealerId=dealer_id, vin=vin)


def _service_operation_input(config: ServiceOperationInput) -> dict[str, object]:
    discounts: object = config.discounts
    if isinstance(config.discounts, tuple):
        discounts = [
            None
            if discount is None
            else optional_input_fields(
                code=discount.code,
                description=discount.description,
                price=discount.price,
            )
            for discount in config.discounts
        ]
    return optional_input_fields(
        opCodeID=config.operation_code_id,
        opCodeDescription=config.operation_code_description,
        customerComments=config.customer_comments,
        serviceOperationsDescription=config.description,
        package=config.package,
        maintenance=config.maintenance,
        validation=config.validation,
        price=config.price,
        laborHours=config.labor_hours,
        discounts=discounts,
    )


def _service_advisor_input(config: ServiceAdvisorInput) -> dict[str, object]:
    return optional_input_fields(
        advisorId=config.advisor_id,
        name=config.name,
        jobTitle=config.job_title,
        email=config.email,
        imageUrl=config.image_url,
    )


def _transportation_option_input(config: TransportationOptionInput) -> dict[str, object]:
    preferences: object = config.preferences
    if isinstance(config.preferences, TransportationPreferencesInput):
        preferences = optional_input_fields(
            isValetRequired=config.preferences.valet_required,
            isLoanerRequired=config.preferences.loaner_required,
            isPickUpRequired=config.preferences.pick_up_required,
            isDropOffRequired=config.preferences.drop_off_required,
            reminders=config.preferences.reminders,
        )
    return optional_input_fields(
        code=config.code,
        name=config.name,
        isValet=config.is_valet,
        isLoanerAvailable=config.is_loaner_available,
        comments=config.comments,
        preferences=preferences,
    )
