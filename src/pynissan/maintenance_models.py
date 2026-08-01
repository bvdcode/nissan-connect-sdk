from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum

from .models import DistanceUnit


class WarrantyServiceContractStatus(StrEnum):
    """Lifecycle states returned for a Nissan service contract."""

    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    UNKNOWN_VALUE = "UNKNOWN__"


class PartsReminderStatus(StrEnum):
    """Lifecycle states returned for a vehicle parts reminder."""

    ACTIVE = "ACTIVE"
    OVERDUE = "OVERDUE"
    SYNC_PENDING = "SYNC_PENDING"
    ERROR = "ERROR"
    UNKNOWN_VALUE = "UNKNOWN__"


@dataclass(frozen=True, slots=True)
class MaintenanceTimeline:
    """Current and projected service milestones for a vehicle."""

    last_service_date: date
    last_service_mileage: int
    next_service_date: date
    next_service_mileage: int
    remaining_service_mileage: int
    remaining_service_months: int
    mileage_unit: DistanceUnit
    current_mileage: int


@dataclass(frozen=True, slots=True)
class ServiceContract:
    """Nullable coverage details for one vehicle service contract."""

    status: WarrantyServiceContractStatus | None
    coverage: str | None
    coverage_description: str | None
    coverage_name: str | None
    plan_effective_date: date | None
    plan_effective_miles: int | None
    plan_expiration_date: date | None
    plan_expiration_odometer: int | None
    plan_cancelled_date: date | None
    plan_cancelled_odometer: int | None
    agreement: str | None
    deductible_amount: int | None
    expiring_soon: bool | None


@dataclass(frozen=True, slots=True)
class PastServiceSuccess:
    """Successful add or update of a past service record."""

    success: bool


@dataclass(frozen=True, slots=True)
class PastServiceGeneralError:
    """General registration failure returned for a past service record."""

    message: str


@dataclass(frozen=True, slots=True)
class PastServiceExists:
    """Conflict returned when an equivalent past service already exists."""

    message: str


@dataclass(frozen=True, slots=True)
class UnknownPastServiceResult:
    """Future past-service union member not known by this SDK version."""

    typename: str


type PastServiceResult = (
    PastServiceSuccess | PastServiceGeneralError | PastServiceExists | UnknownPastServiceResult
)


@dataclass(frozen=True, slots=True)
class PartsReminderConfigurationThresholds:
    """Allowed range and step for a configurable reminder interval."""

    min: int
    max: int
    interval: int
    distance_unit: DistanceUnit | None


@dataclass(frozen=True, slots=True)
class PartReminderConfiguration:
    """Optional month and distance thresholds for one service part."""

    months: PartsReminderConfigurationThresholds | None
    distance: PartsReminderConfigurationThresholds | None


@dataclass(frozen=True, slots=True)
class MaintenancePart:
    """A service part that can be attached to a reminder."""

    id: str | None
    name: str
    reminder_configuration: PartReminderConfiguration | None


@dataclass(frozen=True, slots=True)
class ReminderDistance:
    """Integer distance and unit returned for a parts reminder."""

    unit: DistanceUnit
    value: int


@dataclass(frozen=True, slots=True)
class PartsReminder:
    """One parts reminder and its current scheduling state."""

    id: str
    overdue: bool
    date: datetime | None
    months_interval: int | None
    distance_interval: ReminderDistance | None
    next_reminder_distance: ReminderDistance | None
    next_reminder_date: datetime | None
    status: PartsReminderStatus | None
    parts: tuple[MaintenancePart, ...]
    mileage: ReminderDistance | None


@dataclass(frozen=True, slots=True)
class VehiclePartsReminders:
    """Nullable part catalog and reminders available for an AVK2 vehicle."""

    parts: tuple[MaintenancePart | None, ...] | None
    reminders: tuple[PartsReminder | None, ...] | None


@dataclass(frozen=True, slots=True)
class PartsReminderMutationResult:
    """Nullable success flag returned by a parts-reminder mutation."""

    typename: str
    success: bool | None


@dataclass(frozen=True, slots=True)
class CollisionHistoryEntry:
    """One collision report known to the vehicle account."""

    collision_id: str
    report_date_time: datetime | None
    collision_date_time: datetime | None


@dataclass(frozen=True, slots=True)
class CollisionProbeReading:
    """Vehicle telemetry captured at the time of a collision."""

    collision_time: datetime
    latitude: float
    longitude: float
    mil_count: int
    mil_data: str
    odometer: float
    speed: float
    unit: DistanceUnit
