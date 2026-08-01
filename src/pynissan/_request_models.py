from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ._core_models import (
    _SUCCESSFUL_SERVICE_REQUEST_STATUSES,
    _TERMINAL_SERVICE_REQUEST_STATUSES,
    SeatClimateOption,
    ServiceRequestKind,
    ServiceRequestStatus,
    TemperatureUnit,
    VehicleAlertKind,
    WeekDay,
)
from ._vehicle_status_models import VehicleLocation


@dataclass(frozen=True, slots=True)
class Tokens:
    """OAuth tokens issued by the MyNISSAN identity service."""

    access_token: str
    refresh_token: str
    id_token: str | None = None


@dataclass(frozen=True, slots=True)
class SeatClimateSettings:
    """Optional climate mode for each supported seat position."""

    front_driver: SeatClimateOption | None = None
    front_passenger: SeatClimateOption | None = None
    rear_left: SeatClimateOption | None = None
    rear_right: SeatClimateOption | None = None
    rear_center: SeatClimateOption | None = None
    third_left: SeatClimateOption | None = None
    third_right: SeatClimateOption | None = None


@dataclass(frozen=True, slots=True)
class ClimateParameters:
    """Optional cabin accessories applied with a climate command."""

    seats: SeatClimateSettings | None = None
    steering_wheel_heater: bool | None = None
    defrost_and_deicer: bool | None = None


@dataclass(frozen=True, slots=True)
class ClimateSettings:
    """Target cabin temperature used by climate and engine commands."""

    temperature: float
    unit: TemperatureUnit
    parameters: ClimateParameters | None = None


@dataclass(frozen=True, slots=True)
class ChargeScheduleInput:
    """Fields used to create or replace a recurring charge schedule."""

    start_date_time: datetime
    duration: str
    week_days: tuple[WeekDay, ...]


@dataclass(frozen=True, slots=True)
class ClimateScheduleInput:
    """Fields used to create or replace a recurring climate schedule."""

    start_date_time: datetime
    week_days: tuple[WeekDay, ...]
    climate: ClimateSettings


@dataclass(frozen=True, slots=True)
class ServiceRequest:
    """An asynchronous remote request accepted by Nissan."""

    id: str
    kind: ServiceRequestKind
    climate_defaults_success: bool | None = None
    climate_defaults_error_message: str | None = None


@dataclass(frozen=True, slots=True)
class VehicleAlertRequest:
    """An asynchronous vehicle-alert change accepted by Nissan."""

    id: str
    kind: VehicleAlertKind


@dataclass(frozen=True, slots=True)
class ServiceRequestResult:
    """The latest upstream state of an asynchronous remote request."""

    status: ServiceRequestStatus | None
    status_details: str | None = None
    location: VehicleLocation | None = None
    activation_date_time: datetime | None = None
    status_change_date_time: datetime | None = None

    @property
    def is_terminal(self) -> bool:
        """Return whether Nissan has finished processing the request."""

        return self.status in _TERMINAL_SERVICE_REQUEST_STATUSES

    @property
    def is_success(self) -> bool:
        """Return whether the request finished with a successful status."""

        return self.status is not None and self.status in _SUCCESSFUL_SERVICE_REQUEST_STATUSES
