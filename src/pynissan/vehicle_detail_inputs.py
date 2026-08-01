from __future__ import annotations

from enum import StrEnum

from .graphql_input import UNSET, UnsetType, optional_input_fields, serialize_enum
from .models import DistanceUnit, SpeedUnit, TemperatureUnit


def vehicle_battery_status_variables(
    vin: str,
    *,
    unit: DistanceUnit | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize the exact VehicleBatteryStatus variables."""

    return optional_input_fields(vin=vin, unit=_optional_enum(unit))


def vehicle_boundary_alerts_variables(
    vin: str,
    *,
    distance_unit: DistanceUnit | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize the exact VehicleBoundaryAlerts variables."""

    return optional_input_fields(
        vin=vin,
        distanceUnit=_optional_enum(distance_unit),
    )


def vehicle_climate_status_variables(
    vin: str,
    temperature_unit: TemperatureUnit,
) -> dict[str, object]:
    """Serialize the required VehicleClimateStatus variables."""

    return {
        "vin": vin,
        "temperatureUnit": serialize_enum(temperature_unit),
    }


def vehicle_curfew_alerts_variables(vin: str) -> dict[str, object]:
    """Serialize the required VehicleCurfewAlerts VIN."""

    return {"vin": vin}


def vehicle_doors_status_variables(vin: str) -> dict[str, object]:
    """Serialize the required VehicleDoorsStatus VIN."""

    return {"vin": vin}


def vehicle_model_year_variables(vin: str) -> dict[str, object]:
    """Serialize the required VehicleModelYear VIN."""

    return {"vin": vin}


def vehicle_nickname_variables(vin: str) -> dict[str, object]:
    """Serialize the required VehicleNickname VIN."""

    return {"vin": vin}


def vehicle_speed_alerts_variables(
    vin: str,
    *,
    speed_unit: SpeedUnit | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize the exact VehicleSpeedAlerts variables."""

    return optional_input_fields(vin=vin, speedUnit=_optional_enum(speed_unit))


def vehicle_status_variables(
    vin: str,
    *,
    unit: DistanceUnit | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize the exact VehicleStatus variables."""

    return optional_input_fields(vin=vin, unit=_optional_enum(unit))


def vehicle_status_and_recalls_variables(
    vin: str,
    *,
    unit: DistanceUnit | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize the exact VehicleStatusAndRecalls variables."""

    return optional_input_fields(vin=vin, unit=_optional_enum(unit))


def vehicle_valet_alerts_variables(
    vin: str,
    *,
    distance_unit: DistanceUnit | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize the exact VehicleValetAlerts variables."""

    return optional_input_fields(
        vin=vin,
        distanceUnit=_optional_enum(distance_unit),
    )


def _optional_enum(value: StrEnum | UnsetType | None) -> object:
    if isinstance(value, UnsetType) or value is None:
        return value
    return serialize_enum(value)
