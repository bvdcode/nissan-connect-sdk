from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from .common_inputs import AddressInput, CoordinateInput, address_input, coordinate_input
from .graphql_input import UNSET, UnsetType, optional_input_fields, serialize_datetime
from .models import DistanceUnit, SpeedUnit, WeekDay


class BoundaryAlertType(StrEnum):
    """Direction that triggers a vehicle boundary alert."""

    ON_ENTRY = "ON_ENTRY"
    ON_EXIT = "ON_EXIT"


@dataclass(frozen=True, slots=True)
class AlertRadiusInput:
    """Boundary radius with its required distance unit."""

    value: float
    unit: DistanceUnit


@dataclass(frozen=True, slots=True)
class ValetRadiusInput:
    """Valet radius whose non-null distance unit may be omitted."""

    value: float
    unit: DistanceUnit | UnsetType = UNSET


@dataclass(frozen=True, slots=True)
class BoundaryAlertInput:
    """Complete settings required to create a boundary alert."""

    name: str
    coordinate: CoordinateInput
    radius: AlertRadiusInput
    in_vehicle_warning: bool
    alert_type: BoundaryAlertType
    address: AddressInput = field(default_factory=AddressInput)


@dataclass(frozen=True, slots=True)
class BoundaryAlertUpdate:
    """Partial boundary alert update; omitted fields remain unchanged."""

    name: str | UnsetType | None = UNSET
    coordinate: CoordinateInput | UnsetType | None = UNSET
    address: AddressInput | UnsetType | None = UNSET
    radius: AlertRadiusInput | UnsetType | None = UNSET
    in_vehicle_warning: bool | UnsetType | None = UNSET
    alert_type: BoundaryAlertType | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class AlertScheduleInput:
    """Recurring schedule required by a curfew alert."""

    start_date_time: datetime
    duration: str
    week_days: tuple[WeekDay, ...]


@dataclass(frozen=True, slots=True)
class CurfewAlertInput:
    """Complete settings required to create or replace a curfew alert."""

    name: str
    in_vehicle_warning: bool
    schedule: AlertScheduleInput


@dataclass(frozen=True, slots=True)
class AlertSpeedInput:
    """Unit-aware speed threshold used by current MyNISSAN clients."""

    unit: SpeedUnit
    value: int


@dataclass(frozen=True, slots=True)
class SpeedAlertInput:
    """Speed alert settings, including the optional legacy MPH field."""

    in_vehicle_warning: bool
    speed: AlertSpeedInput | UnsetType | None = UNSET
    speed_in_mph: int | UnsetType | None = UNSET


def boundary_alert_input(value: BoundaryAlertInput) -> dict[str, object]:
    return {
        "name": value.name,
        "coordinate": coordinate_input(value.coordinate),
        "address": address_input(value.address),
        "radius": radius_input(value.radius),
        "inVehicleWarning": value.in_vehicle_warning,
        "alertType": value.alert_type.value,
    }


def boundary_alert_update_input(
    service_request_id: str,
    value: BoundaryAlertUpdate,
) -> dict[str, object]:
    return optional_input_fields(
        serviceRequestId=service_request_id,
        name=value.name,
        coordinate=_optional_serialized(value.coordinate, coordinate_input),
        address=_optional_serialized(value.address, address_input),
        radius=_optional_serialized(value.radius, radius_input),
        inVehicleWarning=value.in_vehicle_warning,
        alertType=_optional_enum(value.alert_type),
    )


def curfew_alert_input(value: CurfewAlertInput) -> dict[str, object]:
    return {
        "name": value.name,
        "inVehicleWarning": value.in_vehicle_warning,
        "schedule": {
            "startDateTime": serialize_datetime(value.schedule.start_date_time),
            "duration": value.schedule.duration,
            "weekDays": [day.value for day in value.schedule.week_days],
        },
    }


def speed_alert_input(value: SpeedAlertInput) -> dict[str, object]:
    return optional_input_fields(
        speedInMPH=value.speed_in_mph,
        inVehicleWarning=value.in_vehicle_warning,
        speed=_optional_serialized(value.speed, alert_speed_input),
    )


def radius_input(value: AlertRadiusInput) -> dict[str, object]:
    return {"value": value.value, "unit": value.unit.value}


def valet_radius_input(value: ValetRadiusInput) -> dict[str, object]:
    return optional_input_fields(
        value=value.value,
        unit=_optional_enum(value.unit),
    )


def optional_coordinate_input(
    value: CoordinateInput | UnsetType | None,
) -> object:
    return _optional_serialized(value, coordinate_input)


def optional_valet_radius_input(
    value: ValetRadiusInput | UnsetType | None,
) -> object:
    return _optional_serialized(value, valet_radius_input)


def alert_speed_input(value: AlertSpeedInput) -> dict[str, object]:
    return {"type": value.unit.value, "value": value.value}


def _optional_serialized[InputT](
    value: InputT | UnsetType | None,
    serializer: Callable[[InputT], object],
) -> object:
    if isinstance(value, UnsetType) or value is None:
        return value
    return serializer(value)


def _optional_enum(value: StrEnum | UnsetType | None) -> str | UnsetType | None:
    if isinstance(value, StrEnum):
        return value.value
    return value
