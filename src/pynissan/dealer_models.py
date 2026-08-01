from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class ServiceContactMethodType(StrEnum):
    """Known service appointment customer contact methods."""

    PHONE = "phone"
    EMAIL = "email"
    MAIL = "mail"
    PAGER = "pager"
    URL = "url"
    SMS = "sms"
    OTHER = "other"
    UNKNOWN_VALUE = "UNKNOWN__"


class MaintenanceVisitAlignment(StrEnum):
    """Known mileage-schedule visit alignment modes."""

    DISTANCE_BASED = "DistanceBased"
    TIME_BASED = "TimeBased"
    DISTANCE_AND_TIME_BASED = "DistanceAndTimeBased"
    UNKNOWN_VALUE = "UNKNOWN__"


@dataclass(frozen=True, slots=True)
class DealerSummary:
    """Compact nullable dealer fields."""

    dealer_id: str | None
    name: str | None
    address_line_1: str | None


@dataclass(frozen=True, slots=True)
class DealerSchedule:
    """One dealer service schedule entry."""

    day_of_week: str
    end_time: str | None
    opened: bool
    start_time: str | None


@dataclass(frozen=True, slots=True)
class DealerServiceSchedule:
    """Named dealer service and its nullable schedules."""

    code: str | None
    name: str | None
    schedules: tuple[DealerSchedule | None, ...] | None


@dataclass(frozen=True, slots=True)
class Dealer:
    """Dealer search result with generated nullable fields."""

    dealer_id: str | None
    name: str | None
    preferred: bool | None
    address_line_1: str | None
    address_line_2: str | None
    latitude: float | None
    longitude: float | None
    postal_code: str | None
    country: str | None
    state_code: str | None
    native_service_booking: bool
    online_scheduling_mobile_url: str | None
    city_name: str | None
    phone_number: str | None
    service_phone: str | None
    website: str | None
    languages_spoken: tuple[str, ...] | None
    email_address: str | None
    service_hours: str | None
    service_schedules: tuple[DealerServiceSchedule | None, ...] | None


@dataclass(frozen=True, slots=True)
class DealerCoupon:
    """Nullable dealer coupon text fields."""

    coupon_id: str | None
    title: str | None
    disclaimer: str | None


@dataclass(frozen=True, slots=True)
class DealerCouponImage:
    """Nullable dealer coupon image fields."""

    coupon_id: str | None
    image_url: str | None


@dataclass(frozen=True, slots=True)
class DealerDealsAndImages:
    """Nullable coupon and coupon-image lists returned for a dealer."""

    coupons: tuple[DealerCoupon | None, ...] | None
    images: tuple[DealerCouponImage | None, ...] | None


@dataclass(frozen=True, slots=True)
class ServiceAdvisor:
    """Nullable service advisor details."""

    advisor_id: str | None
    name: str | None
    job_title: str | None
    email: str | None
    image_url: str | None


@dataclass(frozen=True, slots=True)
class ServiceAppointmentTimeSlot:
    """Appointment day, opening status, and available times."""

    is_open: bool | None
    date: datetime
    times: tuple[datetime | None, ...]


@dataclass(frozen=True, slots=True)
class ServiceDealership:
    """Required dealership object with nullable selected fields."""

    name: str | None
    address_line_1: str | None
    address_line_2: str | None
    city_name: str | None
    state_code: str | None
    phone_number: str | None


@dataclass(frozen=True, slots=True)
class ServiceAddress:
    """Nullable service pick-up or drop-off address fields."""

    address_1: str | None
    address_2: str | None
    city: str | None
    state: str | None
    postal_code: str | None
    country: str | None
    neighbourhood: str | None
    district: str | None
    street_number: str | None


@dataclass(frozen=True, slots=True)
class ServiceTransportationOption:
    """Required transportation option fields."""

    code: str
    name: str
    is_valet: bool
    is_loaner_available: bool


@dataclass(frozen=True, slots=True)
class ServiceContactMethod:
    """Required customer contact method and value."""

    type: ServiceContactMethodType
    value: str


@dataclass(frozen=True, slots=True)
class AppointmentServiceOperation:
    """Nullable operation details attached to an existing appointment."""

    operation_code_description: str | None
    operation_code_id: str | None
    customer_comments: str | None
    category_name: str | None
    description: str | None


@dataclass(frozen=True, slots=True)
class ServiceAppointment:
    """Existing service appointment and selected related data."""

    appointment_id: str | None
    appointment_date: datetime
    dealer_id: str
    editable: bool | None
    dealership: ServiceDealership
    pick_up_address: ServiceAddress | None
    drop_off_address: ServiceAddress | None
    transport: ServiceTransportationOption | None
    contact_methods: tuple[ServiceContactMethod | None, ...] | None
    service_operations: tuple[AppointmentServiceOperation | None, ...]
    advisor: ServiceAdvisor | None
    additional_comments: str | None


@dataclass(frozen=True, slots=True)
class ServiceCategoryOperation:
    """Required service-category operation identity."""

    operation_code_id: int
    description: str


@dataclass(frozen=True, slots=True)
class ServiceCategory:
    """Required service category and operations."""

    category_id: int
    name: str
    description: str
    operations: tuple[ServiceCategoryOperation | None, ...]


@dataclass(frozen=True, slots=True)
class ServiceDiscount:
    """Nullable service operation discount fields."""

    code: str | None
    description: str | None
    price: float | None


@dataclass(frozen=True, slots=True)
class DealerServiceOperation:
    """Dealer service operation with generated nullable fields."""

    operation_code_id: str | None
    operation_code_description: str | None
    customer_comments: str | None
    description: str | None
    package: str
    maintenance: bool | None
    validation: bool | None
    price: float | None
    labor_hours: float | None
    discounts: tuple[ServiceDiscount | None, ...] | None


@dataclass(frozen=True, slots=True)
class ServiceOperationsAtInterval:
    """Nullable mileage interval and its nullable service operations."""

    mileage: int | None
    operations: tuple[DealerServiceOperation | None, ...] | None


@dataclass(frozen=True, slots=True)
class MaintenanceInterval:
    """Nullable interval values for one generated maintenance visit."""

    month: int | None
    year: int | None
    next: bool | None
    distance_miles: int | None
    distance_km: int | None


@dataclass(frozen=True, slots=True)
class MaintenanceServiceOccurrence:
    """Nullable maintenance component and required service-type details."""

    component_name: str | None
    category_name: str | None
    type_name: str
    type_group_name: str


@dataclass(frozen=True, slots=True)
class MaintenanceVisit:
    """One generated maintenance visit."""

    alignment: MaintenanceVisitAlignment | None
    interval: MaintenanceInterval | None
    service_occurrences: tuple[MaintenanceServiceOccurrence | None, ...] | None


@dataclass(frozen=True, slots=True)
class MaintenanceVisits:
    """Nullable generated maintenance visits."""

    visits: tuple[MaintenanceVisit | None, ...] | None


@dataclass(frozen=True, slots=True)
class CancelServiceAppointmentResult:
    """Nullable service appointment cancellation status."""

    success: bool | None


@dataclass(frozen=True, slots=True)
class CreatedServiceAppointment:
    """Created service appointment identifier."""

    appointment_id: str | None


@dataclass(frozen=True, slots=True)
class UpdatedServiceAppointment:
    """Selected fields returned after updating an appointment."""

    dealer_id: str
    appointment_id: str | None
    appointment_date: datetime
    additional_comments: str | None
    pick_up_address: ServiceAddress | None
    transport_name: str | None
    type: str
    vin: str


@dataclass(frozen=True, slots=True)
class ServiceAppointmentUpdateError:
    """Service appointment update error fields."""

    message: str
    error: str | None


@dataclass(frozen=True, slots=True)
class UnselectedDealerResult:
    """Future dealer or appointment union branch selected only by type name."""

    typename: str


type ServiceAppointmentCreateResult = CreatedServiceAppointment | UnselectedDealerResult
type ServiceAppointmentUpdateResult = (
    UpdatedServiceAppointment | ServiceAppointmentUpdateError | UnselectedDealerResult
)


@dataclass(frozen=True, slots=True)
class PreferredDealerUpdated:
    """Nullable preferred dealer returned by a vehicle update."""

    preferred_dealer: str | None


@dataclass(frozen=True, slots=True)
class PreferredDealerUpdateError:
    """Known preferred-dealer update error and required message."""

    typename: str
    message: str


type PreferredDealerUpdateResult = (
    PreferredDealerUpdated | PreferredDealerUpdateError | UnselectedDealerResult
)
