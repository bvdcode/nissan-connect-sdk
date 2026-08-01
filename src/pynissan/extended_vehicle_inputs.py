from __future__ import annotations

from enum import StrEnum

from .common_inputs import CoordinateInput, coordinate_input
from .extended_vehicle_models import DrivingHistoryAggregator, WeightUnit
from .graphql_input import UNSET, UnsetType, optional_input_fields, serialize_enum
from .models import DistanceUnit, SpeedUnit
from .navigation_inputs import PlugConnectorType


class EmpEvseStatusInput(StrEnum):
    """EVSE availability filter accepted by LocationDetails."""

    AVAILABLE = "AVAILABLE"
    ALL = "ALL"
    UNKNOWN_VALUE = "UNKNOWN__"


class EmpConnectorLevelInput(StrEnum):
    """Connector level filter accepted by LocationDetails."""

    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    UNKNOWN_VALUE = "UNKNOWN__"


def driving_history_variables(
    vin: str,
    aggregator: DrivingHistoryAggregator,
    *,
    distance_unit: DistanceUnit | UnsetType | None = UNSET,
    weight_unit: WeightUnit | UnsetType | None = UNSET,
    speed_unit: SpeedUnit | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize DrivingHistory variables with Apollo omission semantics."""

    return optional_input_fields(
        vin=vin,
        aggregator=serialize_enum(aggregator),
        distanceUnit=_optional_enum(distance_unit),
        weightUnit=_optional_enum(weight_unit),
        speedUnit=_optional_enum(speed_unit),
    )


def ev_charge_stations_variables(
    vin: str,
    coordinate: CoordinateInput,
    *,
    plug_connector_types: (tuple[PlugConnectorType | None, ...] | UnsetType | None) = UNSET,
    enable_within_range_restriction: bool | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize EVChargeStations variables while retaining explicit nulls."""

    return optional_input_fields(
        vin=vin,
        coordinate=coordinate_input(coordinate),
        plugConnectorTypes=_optional_nullable_enum_list(plug_connector_types),
        enableWithinRangeRestriction=enable_within_range_restriction,
    )


def e_vehicle_eligibility_variables(vin: str) -> dict[str, object]:
    """Serialize eVehicleEligibility variables."""

    return {"vin": vin}


def last_known_camera_usage_counter_variables(vin: str) -> dict[str, object]:
    """Serialize LastKnownCameraUsageCounter variables."""

    return {"vin": vin}


def location_details_variables(
    vin: str,
    latitude: str,
    longitude: str,
    in_network_only: bool,
    range_value: int,
    *,
    operator_names: tuple[str | None, ...] | UnsetType | None = UNSET,
    evse: EmpEvseStatusInput | UnsetType | None = UNSET,
    plug_types: tuple[str | None, ...] | UnsetType | None = UNSET,
    charge_level: EmpConnectorLevelInput | UnsetType | None = UNSET,
    pnc_stations_only: bool | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize LocationDetails variables with nullable filters preserved."""

    return optional_input_fields(
        vin=vin,
        latitude=latitude,
        longitude=longitude,
        inNetworkOnly=in_network_only,
        range=range_value,
        operatorName=_optional_nullable_string_list(operator_names),
        evse=_optional_enum(evse),
        plugType=_optional_nullable_string_list(plug_types),
        chargeLevel=_optional_enum(charge_level),
        pncStationsOnly=pnc_stations_only,
    )


def parking_chargeable_variables(evse_id: str) -> dict[str, object]:
    """Serialize ParkingChargeable variables."""

    return {"evseId": evse_id}


def shareable_capabilities_variables(
    vin: str,
    *,
    driver_id: str | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize ShareableCapabilities variables while preserving null versus omission."""

    return optional_input_fields(vin=vin, driverId=driver_id)


def tariff_pricing_variables(vin: str, location_id: str) -> dict[str, object]:
    """Serialize TariffPricing variables."""

    return {"vin": vin, "locationId": location_id}


def _optional_enum(value: StrEnum | UnsetType | None) -> object:
    if isinstance(value, StrEnum):
        return serialize_enum(value)
    return value


def _optional_nullable_enum_list[EnumT: StrEnum](
    value: tuple[EnumT | None, ...] | UnsetType | None,
) -> object:
    if isinstance(value, UnsetType) or value is None:
        return value
    return [serialize_enum(item) if item is not None else None for item in value]


def _optional_nullable_string_list(
    value: tuple[str | None, ...] | UnsetType | None,
) -> object:
    if isinstance(value, UnsetType) or value is None:
        return value
    return list(value)
