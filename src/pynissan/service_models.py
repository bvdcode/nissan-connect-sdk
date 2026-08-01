from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum

from .models import DistanceUnit


class RecallType(StrEnum):
    """Recall categories returned by Nissan's vehicle service API."""

    RECALL = "RECALL"
    SERVICE = "SERVICE"
    UNKNOWN_VALUE = "UNKNOWN__"


class WarrantyInfoColorStatus(StrEnum):
    """Color status attached to a vehicle warranty summary."""

    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"
    UNKNOWN_VALUE = "UNKNOWN__"


class WarrantyInfoWarrantyStatus(StrEnum):
    """Lifecycle status attached to a vehicle warranty summary."""

    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    UNKNOWN_VALUE = "UNKNOWN__"


@dataclass(frozen=True, slots=True)
class PreferredDealerAddress:
    """Nullable postal address fields returned for a preferred dealer."""

    address1: str | None
    address2: str | None
    city: str | None
    state: str | None
    postal_code: str | None
    country: str | None


@dataclass(frozen=True, slots=True)
class PreferredDealerLocation:
    """Nullable coordinates returned for a preferred dealer."""

    latitude: float | None
    longitude: float | None


@dataclass(frozen=True, slots=True)
class VehiclePreferredDealer:
    """The preferred dealer currently associated with a vehicle."""

    id: str | None
    hash_id: str | None
    name: str | None
    address: PreferredDealerAddress | None
    hours: str | None
    phone: str | None
    service_phone: str | None
    native_service_booking: bool | None
    scheduling_url_mobile: str | None
    location: PreferredDealerLocation | None
    languages_spoken: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class VehicleRecall:
    """One recall or service campaign associated with a vehicle."""

    effective_date: datetime
    nhtsa_id: str | None
    primary_description: str
    remedy_description: str
    risk_description: str
    title: str
    type: RecallType
    recall_code: str | None


@dataclass(frozen=True, slots=True)
class VehicleRoadsideAssistance:
    """Nullable roadside-assistance and towing coverage limits."""

    roadside_months: int | None
    roadside_miles: int | None
    towing_months: int | None
    towing_miles: int | None


@dataclass(frozen=True, slots=True)
class ServiceHistoryMileage:
    """Non-null mileage and unit recorded for a service-history entry."""

    unit: DistanceUnit
    value: int


@dataclass(frozen=True, slots=True)
class VehicleServiceOperation:
    """Nullable operation metadata attached to a service-history entry."""

    service_category_id: str | None
    service_category_name: str | None
    op_code_id: str | None
    op_code_description: str | None


@dataclass(frozen=True, slots=True)
class VehicleServiceHistoryEntry:
    """One completed vehicle service event returned by Nissan."""

    mileage: ServiceHistoryMileage
    service_date: datetime
    dealer_name: str
    dealer_code: str
    services: tuple[str, ...]
    comment: str | None
    maintenance_id: int | None
    service_operation: VehicleServiceOperation | None


@dataclass(frozen=True, slots=True)
class VehicleWarrantyInfo:
    """Current vehicle warranty status and overall coverage limits."""

    color_status: WarrantyInfoColorStatus
    warranty_status: WarrantyInfoWarrantyStatus
    total_mileage: int
    total_months: str


@dataclass(frozen=True, slots=True)
class VehicleWarrantyPeriod:
    """Mileage and calendar boundary for a vehicle warranty period."""

    mileage: int
    date: date


@dataclass(frozen=True, slots=True)
class VehicleWarranty:
    """Warranty summary and its non-null start, end, and current periods."""

    warranty_info: VehicleWarrantyInfo
    start_period: VehicleWarrantyPeriod
    end_period: VehicleWarrantyPeriod
    current_period: VehicleWarrantyPeriod
