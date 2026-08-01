from __future__ import annotations

from .graphql_input import UNSET, UnsetType, optional_input_fields, serialize_enum
from .models import DistanceUnit


def vehicle_preferred_dealer_variables(vin: str) -> dict[str, object]:
    """Serialize variables for the preferred-dealer query."""

    return {"vin": vin}


def vehicle_recalls_variables(vin: str) -> dict[str, object]:
    """Serialize variables for the standalone vehicle-recalls query."""

    return {"vin": vin}


def vehicle_roadside_assistance_variables(vin: str) -> dict[str, object]:
    """Serialize variables for the roadside-assistance query."""

    return {"vin": vin}


def vehicle_service_history_variables(
    vin: str,
    *,
    unit: DistanceUnit | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize service-history variables while preserving Apollo optionality."""

    return optional_input_fields(vin=vin, unit=_optional_distance_unit(unit))


def warranty_info_variables(
    vin: str,
    *,
    mileage: int | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize warranty variables while preserving omitted and null mileage."""

    return optional_input_fields(vin=vin, mileage=mileage)


def _optional_distance_unit(value: DistanceUnit | UnsetType | None) -> object:
    if isinstance(value, DistanceUnit):
        return serialize_enum(value)
    return value
