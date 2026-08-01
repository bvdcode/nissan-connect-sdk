from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ._core_models import CameraPosition, CameraService, ProductType, PurchaseType


@dataclass(frozen=True, slots=True)
class Vehicle:
    """Static data for a vehicle attached to the account."""

    vin: str
    year: str | None
    model: str | None
    color: str | None
    nickname: str | None
    image_url: str | None
    driver_type: str | None
    plate: str | None


@dataclass(frozen=True, slots=True)
class VehiclePhoto:
    """One remotely captured vehicle photo and its upstream metadata."""

    id: str | None
    filename: str | None
    link: str | None
    timestamp: datetime | None
    camera_position: CameraPosition | None
    camera_service: CameraService | None


@dataclass(frozen=True, slots=True)
class VehiclePhotos:
    """Photos currently available around one vehicle."""

    vin: str
    year: str
    model: str
    photos: tuple[VehiclePhoto | None, ...] | None


@dataclass(frozen=True, slots=True)
class RemoteServiceHistoryEntry:
    """One raw remote-service status transition returned by Nissan."""

    service_request_id: str | None
    status: str | None
    service_type: str | None
    status_change_date_time: datetime | None


@dataclass(frozen=True, slots=True)
class RemoteServiceHistory:
    """One nullable page of vehicle remote-service history."""

    page_number: int | None
    items_per_page: int | None
    total_items: int | None
    total_pages: int | None
    history: tuple[RemoteServiceHistoryEntry | None, ...] | None


@dataclass(frozen=True, slots=True)
class ReminderNotificationsAfterLeavingVehicle:
    """Reminder flags returned for supported AVK2 vehicles."""

    lock: bool | None
    door: bool | None
    trunk: bool | None
    sunroof: bool | None
    window: bool | None


@dataclass(frozen=True, slots=True)
class VehiclePreferences:
    """MIL/DTC maintenance-data sharing preferences for a vehicle."""

    enabled: bool | None
    text: bool | None
    phone: bool | None
    email: bool | None


@dataclass(frozen=True, slots=True)
class VehicleSubscriptionProduct:
    """Product metadata attached to a vehicle subscription."""

    product_id: str
    marketing_name: str
    description: str
    services: tuple[str | None, ...]


@dataclass(frozen=True, slots=True)
class VehicleSubscriptionPendingOrder:
    """Pending package activation attached to a vehicle subscription."""

    pending_order_id: str
    package_name: str
    activation_date: datetime | None


@dataclass(frozen=True, slots=True)
class VehicleSubscription:
    """One subscription returned by Nissan without app-level defaults or filtering."""

    subscription_id: str
    subscription_service_type: str
    purchase_type: PurchaseType | str | None
    product_type: ProductType | str | None
    next_billing_date: datetime | None
    goodwill_end_date: datetime | None
    goodwill_start_date: datetime | None
    grace_end_date: datetime | None
    subscription_start_date: datetime
    subscription_end_date: datetime | None
    is_active: bool | None
    np_subscription_price: str | None
    product: VehicleSubscriptionProduct
    pending_order: VehicleSubscriptionPendingOrder | None


@dataclass(frozen=True, slots=True)
class VehicleSubscriptions:
    """The nullable capability branch containing a vehicle's subscriptions."""

    vin: str
    subscriptions: tuple[VehicleSubscription | None, ...] | None


@dataclass(frozen=True, slots=True)
class VehicleWifiConsumption:
    """Current in-vehicle Wi-Fi usage and data cap in gigabytes."""

    usage_percent: float
    usage_amount_gb: float
    data_cap_amount_gb: float
    updated_at: datetime
