from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class AlertAddress:
    """Nullable address fields attached to a configured boundary alert."""

    address1: str | None
    address2: str | None
    city: str | None
    state: str | None
    country: str | None
    postal_code: str | None


@dataclass(frozen=True, slots=True)
class AlertLocation:
    """Coordinates attached to an alert configuration or breach event."""

    latitude: float | None
    longitude: float | None


@dataclass(frozen=True, slots=True)
class AlertDistance:
    """A nullable distance value and its raw upstream unit."""

    value: float | None
    unit: str | None


@dataclass(frozen=True, slots=True)
class BoundaryAlert:
    """A configured entry or exit boundary alert."""

    service_request_id: str
    alert_type: str | None
    name: str
    enabled: bool
    in_vehicle_warning: bool
    address: AlertAddress | None
    location: AlertLocation | None
    radius: AlertDistance | None


@dataclass(frozen=True, slots=True)
class CurfewSchedule:
    """Schedule attached to a configured curfew alert."""

    all_day: bool | None
    start_date_time: datetime
    duration: str | None
    week_days: tuple[str | None, ...]


@dataclass(frozen=True, slots=True)
class CurfewAlert:
    """A configured vehicle curfew alert."""

    service_request_id: str
    name: str
    enabled: bool
    in_vehicle_warning: bool
    schedule: CurfewSchedule | None


@dataclass(frozen=True, slots=True)
class SpeedThreshold:
    """Speed threshold with its raw upstream unit."""

    unit: str | None
    value: float | None


@dataclass(frozen=True, slots=True)
class SpeedAlert:
    """A configured vehicle speed alert."""

    service_request_id: str
    name: str
    enabled: bool
    in_vehicle_warning: bool
    threshold: SpeedThreshold | None


@dataclass(frozen=True, slots=True)
class ValetAlert:
    """The currently configured valet boundary alert."""

    service_request_id: str | None
    radius: AlertDistance | None


@dataclass(frozen=True, slots=True)
class VehicleAlerts:
    """Nullable alert configurations returned for one connected vehicle."""

    boundary_alerts: tuple[BoundaryAlert | None, ...] | None
    curfew_alerts: tuple[CurfewAlert | None, ...] | None
    speed_alerts: tuple[SpeedAlert | None, ...] | None
    valet_alert: ValetAlert | None


@dataclass(frozen=True, slots=True)
class BreachAlert:
    """One raw vehicle-alert breach event."""

    service_type: str | None
    breach_date_time: datetime | None
    name: str | None
    location: AlertLocation | None


@dataclass(frozen=True, slots=True)
class BreachAlerts:
    """One nullable page of vehicle-alert breach events."""

    items_per_page: int | None
    page_number: int | None
    total_items: int | None
    total_pages: int | None
    alerts: tuple[BreachAlert | None, ...] | None
