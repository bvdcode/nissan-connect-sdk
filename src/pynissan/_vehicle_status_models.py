from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import ClassVar, Literal

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

    @property
    def is_open(self) -> bool | None:
        """Return whether the door is open, or None for an unknown state."""

        return _opening_is_open(self.ajar)

    @property
    def is_locked(self) -> bool | None:
        """Return whether the door is locked, or None for an unknown state."""

        return _lock_is_locked(self.lock)


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

    @property
    def is_locked(self) -> bool | None:
        """Return the reported overall lock state without inferring missing values."""

        return _lock_is_locked(self.overall_lock)

    @property
    def is_trunk_locked(self) -> bool | None:
        """Return the reported trunk lock state, or None when unknown."""

        return _lock_is_locked(self.trunk_lock)

    @property
    def is_trunk_open(self) -> bool | None:
        """Return whether the reported rear hatch is open, or None when unknown."""

        return _opening_is_open(self.hatch_ajar)

    @property
    def is_hood_open(self) -> bool | None:
        """Return whether the engine hood is open, or None when unknown."""

        return _opening_is_open(self.engine_hood_ajar)


@dataclass(frozen=True, slots=True)
class BatteryStatus:
    """Reported battery status, with remaining charge time expressed in minutes."""

    level: int | None
    is_plugged_in: bool | None
    is_charging: bool | None
    remaining_charge_time: int | None
    remaining_mileage: DistanceReading | None

    @property
    def remaining_charge_duration(self) -> timedelta | None:
        """Return a valid remaining duration only when charging is confirmed active."""

        minutes = self.remaining_charge_time
        if self.is_charging is not True or minutes is None or minutes < 0:
            return None
        return timedelta(minutes=minutes)

    def estimate_charge_completion(self, observed_at: datetime) -> datetime | None:
        """Estimate completion from an aware observation time and remaining duration.

        This is a derived estimate, not a timestamp reported by the vehicle.
        The caller supplies the time at which the cached status was obtained.
        """

        if observed_at.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        duration = self.remaining_charge_duration
        if duration is None:
            return None
        return (observed_at.astimezone(UTC) + duration).astimezone(observed_at.tzinfo)


@dataclass(frozen=True, slots=True)
class TirePressure:
    """Reported pressure for each tire in pounds per square inch (psi)."""

    unit: ClassVar[Literal["psi"]] = "psi"

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

    @property
    def active_warnings(self) -> tuple[MaintenanceIndicator, ...]:
        """Return indicators explicitly marked active by the service."""

        return tuple(item for item in self.maintenance_indicators if item.active is True)

    @property
    def warning_count(self) -> int:
        """Return the number of reported active maintenance indicators."""

        return len(self.active_warnings)

    @property
    def warning_messages(self) -> tuple[str, ...]:
        """Return available messages for active warnings without truncation."""

        return tuple(
            item.detailed_message
            for item in self.active_warnings
            if item.detailed_message is not None
        )


@dataclass(frozen=True, slots=True)
class VehicleLocation:
    """The last reported location of a vehicle."""

    vin: str
    latitude: float | None
    longitude: float | None
    last_updated_at: datetime | None


def _opening_is_open(value: str | None) -> bool | None:
    match value:
        case "OPEN":
            return True
        case "CLOSED":
            return False
        case _:
            return None


def _lock_is_locked(value: str | None) -> bool | None:
    match value:
        case "LOCKED":
            return True
        case "UNLOCKED":
            return False
        case _:
            return None
