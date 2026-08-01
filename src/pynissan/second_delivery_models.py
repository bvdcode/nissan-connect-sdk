from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .second_delivery_inputs import SecondDeliveryAppointmentMode


class SecondDeliveryAppointmentStatus(StrEnum):
    """Known second-delivery appointment states."""

    BOOKED = "BOOKED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    UNKNOWN_VALUE = "UNKNOWN__"


class SecondDeliveryMarketingVersion(StrEnum):
    """Known second-delivery marketing CTA variants."""

    REMIND_ME_LATER = "REMIND_ME_LATER"
    NO_THANKS = "NO_THANKS"
    UNKNOWN_VALUE = "UNKNOWN__"


@dataclass(frozen=True, slots=True)
class SecondDeliveryCoordinates:
    """Nullable second-delivery address coordinates."""

    latitude: float | None
    longitude: float | None


@dataclass(frozen=True, slots=True)
class SecondDeliveryAddress:
    """Nullable address fields selected by second-delivery operations."""

    address_1: str | None
    address_2: str | None
    city: str | None
    state: str | None
    postal_code: str | None
    country: str | None
    id: int | None = None
    coordinates: SecondDeliveryCoordinates | None = None


@dataclass(frozen=True, slots=True)
class SecondDeliveryDealer:
    """Nullable second-delivery dealer details."""

    code: str | None
    address: SecondDeliveryAddress | None


@dataclass(frozen=True, slots=True)
class SecondDeliveryHub:
    """Nullable second-delivery hub details."""

    id: int | None
    timezone: str | None
    dealer: SecondDeliveryDealer | None = None


@dataclass(frozen=True, slots=True)
class SecondDeliveryContact:
    """Nullable booked-appointment contact fields."""

    first_name: str | None
    last_name: str | None
    phone_number: str | None
    email: str | None


@dataclass(frozen=True, slots=True)
class SecondDeliveryAppointmentReference:
    """Nullable appointment identity returned by restricted flows."""

    id: int | None
    access_token: str | None
    status: SecondDeliveryAppointmentStatus | None


@dataclass(frozen=True, slots=True)
class SecondDeliveryBookedAppointment:
    """Existing booked second-delivery appointment."""

    id: int | None
    activity_id: int | None
    begins_at: datetime | None
    address: SecondDeliveryAddress | None
    contact: SecondDeliveryContact | None
    redelivery_notes: str | None
    feature_notes: str | None
    hub: SecondDeliveryHub | None
    mode: SecondDeliveryAppointmentMode | None


@dataclass(frozen=True, slots=True)
class SecondDeliveryAppointmentNotFound:
    """No booked second-delivery appointment exists."""

    message: str


@dataclass(frozen=True, slots=True)
class SecondDeliveryAppointmentForbidden:
    """Appointment requires an additional authorization flow."""

    message: str
    redacted_email: str | None
    redacted_phone_number: str | None
    appointment: SecondDeliveryAppointmentReference | None


@dataclass(frozen=True, slots=True)
class UnselectedSecondDeliveryResult:
    """Future second-delivery union branch selected only by type name."""

    typename: str


type SecondDeliveryAppointmentResult = (
    SecondDeliveryBookedAppointment
    | SecondDeliveryAppointmentNotFound
    | SecondDeliveryAppointmentForbidden
    | UnselectedSecondDeliveryResult
)


@dataclass(frozen=True, slots=True)
class SecondDeliveryTimeSlot:
    """Nullable second-delivery time-slot fields."""

    time: datetime | None
    id: int | None


@dataclass(frozen=True, slots=True)
class SecondDeliverySlotsByDate:
    """Required date and nullable slots for that date."""

    date: datetime
    time_slots: tuple[SecondDeliveryTimeSlot | None, ...] | None


@dataclass(frozen=True, slots=True)
class SecondDeliveryTimeSlots:
    """Successful second-delivery time-slot search."""

    hub: SecondDeliveryHub | None
    slots_by_date: tuple[SecondDeliverySlotsByDate | None, ...]


@dataclass(frozen=True, slots=True)
class SecondDeliveryAddressNotServiced:
    """The supplied address is outside the second-delivery service area."""

    message: str | None


type SecondDeliveryTimeSlotsResult = (
    SecondDeliveryTimeSlots | SecondDeliveryAddressNotServiced | UnselectedSecondDeliveryResult
)


@dataclass(frozen=True, slots=True)
class SecondDeliveryLeadCar:
    """Nullable lead-vehicle fields used by second-delivery eligibility."""

    trim: str | None
    deleted: bool | None
    interior_color: str | None
    retail_sales_date: str | None
    plate: str | None
    brand: str | None
    year: str | None
    model: str | None
    mileage: int | None
    lead_id: int | None
    exterior_color: str | None
    name: str | None
    vin: str | None
    id: int | None


@dataclass(frozen=True, slots=True)
class SecondDeliveryEligible:
    """Eligible retail-delivery record details."""

    hub: SecondDeliveryHub | None
    lead_car: SecondDeliveryLeadCar | None
    redelivery_lead_id: int | None
    days_since_retail_sales_date: int | None


@dataclass(frozen=True, slots=True)
class SecondDeliveryAppointmentBooked:
    """Eligibility indicates an appointment is already booked."""

    appointment: SecondDeliveryAppointmentReference | None


@dataclass(frozen=True, slots=True)
class SecondDeliveryAppointmentCompleted:
    """Eligibility indicates the appointment was completed."""

    appointment: SecondDeliveryAppointmentReference | None


@dataclass(frozen=True, slots=True)
class SecondDeliveryEligibilityError:
    """Known eligibility error branch with nullable message."""

    typename: str
    message: str | None


type SecondDeliveryEligibilityResult = (
    SecondDeliveryEligible
    | SecondDeliveryAppointmentBooked
    | SecondDeliveryAppointmentCompleted
    | SecondDeliveryEligibilityError
    | UnselectedSecondDeliveryResult
)


@dataclass(frozen=True, slots=True)
class SecondDeliveryMarketingMessage:
    """Nullable marketing message CTA configuration."""

    version: SecondDeliveryMarketingVersion | None
    display_threshold_days: int | None
    remind_later_threshold_days: int | None


@dataclass(frozen=True, slots=True)
class SecondDeliveryCallToAction:
    """Nullable second-delivery CTA state."""

    marketing_message: SecondDeliveryMarketingMessage | None
    discover_prioritized: bool | None
    days_since_purchased: int | None


@dataclass(frozen=True, slots=True)
class SecondDeliveryEligibility:
    """Eligibility union and independent CTA state."""

    result: SecondDeliveryEligibilityResult | None
    call_to_action: SecondDeliveryCallToAction | None


@dataclass(frozen=True, slots=True)
class ValidSecondDeliveryAddress:
    """Nullable positive address-validation flag."""

    valid: bool | None


@dataclass(frozen=True, slots=True)
class InvalidSecondDeliveryAddress:
    """Nullable negative flag and the dealer address to use instead."""

    valid: bool | None
    dealer_address: SecondDeliveryAddress | None


type SecondDeliveryAddressValidationResult = (
    ValidSecondDeliveryAddress | InvalidSecondDeliveryAddress | UnselectedSecondDeliveryResult
)


@dataclass(frozen=True, slots=True)
class SecondDeliveryOperationSuccess:
    """Required success flag returned by a second-delivery mutation."""

    success: bool


@dataclass(frozen=True, slots=True)
class SecondDeliveryOperationError:
    """Known second-delivery mutation error with nullable message."""

    typename: str
    message: str | None


type SecondDeliveryOperationResult = (
    SecondDeliveryOperationSuccess | SecondDeliveryOperationError | UnselectedSecondDeliveryResult
)
