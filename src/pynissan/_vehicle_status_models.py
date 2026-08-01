from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ._core_models import DistanceUnit


@dataclass(frozen=True, slots=True)
class DistanceReading:
    """A distance value returned by the connected vehicle service."""

    value: int | None
    unit: str | None
    last_updated_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class Mileage:
    """The vehicle odometer reading."""

    total: int | None
    unit: str | None
    recorded_at: datetime | None


@dataclass(frozen=True, slots=True)
class DoorState:
    """Reported state of a door and its window and lock."""

    ajar: str | None
    window: str | None
    lock: str | None


@dataclass(frozen=True, slots=True)
class DoorsStatus:
    """Reported state of the vehicle openings and locks."""

    last_updated_at: datetime | None
    front_left: DoorState | None
    front_right: DoorState | None
    rear_left: DoorState | None
    rear_right: DoorState | None
    engine_hood_ajar: str | None
    hatch_ajar: str | None
    sunroof_ajar: str | None
    trunk_lock: str | None
    overall_lock: str | None


@dataclass(frozen=True, slots=True)
class BatteryStatus:
    """Reported electric vehicle battery status."""

    level: int | None
    is_plugged_in: bool | None
    is_charging: bool | None
    remaining_charge_time: int | None
    remaining_mileage: DistanceReading | None


@dataclass(frozen=True, slots=True)
class TirePressure:
    """Raw tire pressure and status values returned by the API."""

    last_updated_at: datetime | None
    front_left: int | None
    front_right: int | None
    rear_left: int | None
    rear_right: int | None
    front_left_status: int | None
    front_right_status: int | None
    rear_left_status: int | None
    rear_right_status: int | None


@dataclass(frozen=True, slots=True)
class MaintenanceIndicator:
    """A vehicle malfunction or maintenance indicator."""

    active: bool | None
    detailed_message: str | None
    type: str | None


@dataclass(frozen=True, slots=True)
class TemperatureReading:
    """A temperature value returned by the API."""

    value: float
    unit: str


@dataclass(frozen=True, slots=True)
class ClimateStatus:
    """Reported climate control state."""

    state: str | None
    temperature: TemperatureReading | None


@dataclass(frozen=True, slots=True)
class EngineOilDrainRange:
    """Remaining engine-oil service range reported by a combustion vehicle."""

    range: int
    unit: DistanceUnit
    last_updated_at: datetime


@dataclass(frozen=True, slots=True)
class VehicleStatus:
    """Cached dynamic data for one vehicle."""

    vin: str
    vehicle_type: str | None
    battery: BatteryStatus | None
    climate: ClimateStatus | None
    doors: DoorsStatus | None
    fuel_range: DistanceReading | None
    mileage: Mileage | None
    tire_pressure: TirePressure | None
    maintenance_indicators: tuple[MaintenanceIndicator, ...]
    engine_oil_drain_range: EngineOilDrainRange | None = None


@dataclass(frozen=True, slots=True)
class VehicleLocation:
    """The last reported location of a vehicle."""

    vin: str
    latitude: float | None
    longitude: float | None
    last_updated_at: datetime | None
