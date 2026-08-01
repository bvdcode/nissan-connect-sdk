from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ._core_models import V2LState, WeekDay
from ._request_models import ClimateParameters
from ._vehicle_status_models import TemperatureReading


@dataclass(frozen=True, slots=True)
class ChargeSchedule:
    """A recurring vehicle charging schedule."""

    id: str
    state: str | None
    start_date_time: datetime
    duration: str
    week_days: tuple[WeekDay, ...]


@dataclass(frozen=True, slots=True)
class ChargeConfig:
    """Configured charging and notification limits, expressed as percentages."""

    charge_limit_percent: int | None
    notification_threshold_percent: int | None


@dataclass(frozen=True, slots=True)
class V2LStatus:
    """V2L state and battery reserve levels, expressed as percentages."""

    state: V2LState | None
    charge_limit_percent: float | None
    minimum_charge_limit_percent: float | None


@dataclass(frozen=True, slots=True)
class ChargeSession:
    """One charging session; recovered energy is expressed in kilowatt-hours."""

    start: datetime | None
    end: datetime | None
    duration: str | None
    recovered_energy_kwh: float | None


@dataclass(frozen=True, slots=True)
class ChargeHistorySummary:
    """Aggregated charge history; energy is in kWh and duration is in minutes."""

    day: int | None
    month: int | None
    year: int | None
    number_of_charge_sessions: int | None
    total_energy_recovered_kwh: float | None
    total_duration_minutes: int | None
    number_of_errors: int | None
    user_id: str | None
    role_type: str | None


@dataclass(frozen=True, slots=True)
class VehicleChargeHistory:
    """Charging sessions and summaries for one requested time aggregation."""

    charges: tuple[ChargeSession, ...]
    charge_summaries: tuple[ChargeHistorySummary, ...]


@dataclass(frozen=True, slots=True)
class ClimateSchedule:
    """A recurring cabin climate schedule."""

    id: str
    state: str | None
    start_date_time: datetime
    week_days: tuple[WeekDay, ...]
    temperature: TemperatureReading


@dataclass(frozen=True, slots=True)
class DelayedClimateSchedule:
    """The one-time delayed climate start configured for an Ariya."""

    start_date_time: datetime | None


@dataclass(frozen=True, slots=True)
class VehicleClimateSchedules:
    """Recurring schedules and vehicle-level climate schedule settings."""

    schedules: tuple[ClimateSchedule, ...]
    accessories: ClimateParameters | None
    delayed_schedule: DelayedClimateSchedule | None


@dataclass(frozen=True, slots=True)
class ClimateDefaults:
    """The vehicle's saved default climate configuration."""

    climate: TemperatureReading | None
    parameters: ClimateParameters | None
