from __future__ import annotations

from collections.abc import Mapping

from ._extended_vehicle_driving_parsing import (
    _parse_driving_history_summary,
    _parse_driving_history_trip,
)
from ._extended_vehicle_location_parsing import _parse_emp_location, _parse_ev_charge_station
from ._extended_vehicle_tariff_parsing import (
    _parse_shareable_capability_group,
    _parse_tariff_pricing_data,
)
from ._extended_vehicle_value_parsing import (
    _list,
    _nullable_bool,
    _nullable_datetime,
    _nullable_list,
    _nullable_string,
    _optional_typed_object,
    _vehicle,
)
from .exceptions import ResponseError
from .extended_vehicle_models import (
    DrivingHistory,
    DrivingHistoryTrip,
    DrivingHistoryTripSummary,
    EmpLocation,
    EVChargeStation,
    EVehicleEligibility,
    EVehicleEligibilityData,
    LastKnownCameraUsageCounter,
    LocationDetails,
    ParkingChargeable,
    ParkingChargeableData,
    ShareableCapabilities,
    ShareableCapabilityGroup,
    TariffPricing,
)


def parse_driving_history(data: Mapping[str, object]) -> DrivingHistory | None:
    """Parse an electric vehicle's driving history with strict list nullability."""

    vehicle = _vehicle(data)
    if vehicle is None or "drivingHistory" not in vehicle:
        return None
    path = "vehicle.drivingHistory"
    history = _optional_typed_object(vehicle.get("drivingHistory"), path)
    if history is None:
        return None

    summary_values = _list(history.get("tripSummaries"), f"{path}.tripSummaries")
    summaries: list[DrivingHistoryTripSummary] = []
    for index, value in enumerate(summary_values):
        summaries.append(_parse_driving_history_summary(value, f"{path}.tripSummaries[{index}]"))

    trip_values = _list(history.get("trips"), f"{path}.trips")
    trips: list[DrivingHistoryTrip] = []
    for index, value in enumerate(trip_values):
        trips.append(_parse_driving_history_trip(value, f"{path}.trips[{index}]"))

    return DrivingHistory(tuple(summaries), tuple(trips))


def parse_ev_charge_stations(
    data: Mapping[str, object],
) -> tuple[EVChargeStation | None, ...] | None:
    """Parse nearby charging stations while preserving nullable list items."""

    vehicle = _vehicle(data)
    if vehicle is None or "evChargeStations" not in vehicle:
        return None
    path = "vehicle.evChargeStations"
    values = _nullable_list(vehicle.get("evChargeStations"), path)
    if values is None:
        return None

    stations: list[EVChargeStation | None] = []
    for index, value in enumerate(values):
        if value is None:
            stations.append(None)
            continue
        stations.append(_parse_ev_charge_station(value, f"{path}[{index}]"))
    return tuple(stations)


def parse_e_vehicle_eligibility(
    data: Mapping[str, object],
) -> EVehicleEligibility | None:
    """Parse the raw eVehicle eligibility status wrapper."""

    root_field = "eVehicleEligibility"
    if root_field not in data:
        raise ResponseError(f"{root_field} is missing")
    result = _optional_typed_object(data.get(root_field), root_field)
    if result is None:
        return None
    eligibility_data = _optional_typed_object(
        result.get("data"),
        f"{root_field}.data",
    )
    return EVehicleEligibility(
        status_code=_nullable_string(result.get("statusCode"), f"{root_field}.statusCode"),
        status_message=_nullable_string(
            result.get("statusMessage"),
            f"{root_field}.statusMessage",
        ),
        timestamp=_nullable_string(result.get("timestamp"), f"{root_field}.timestamp"),
        data=(
            EVehicleEligibilityData(
                vin=_nullable_string(
                    eligibility_data.get("vin"),
                    f"{root_field}.data.vin",
                ),
                v1g_eligible=_nullable_bool(
                    eligibility_data.get("v1GEligible"),
                    f"{root_field}.data.v1GEligible",
                ),
            )
            if eligibility_data is not None
            else None
        ),
    )


def parse_last_known_camera_usage_counter(
    data: Mapping[str, object],
) -> LastKnownCameraUsageCounter | None:
    """Parse the last known camera usage counter for an AVK2 vehicle."""

    vehicle = _vehicle(data)
    if vehicle is None or "lastKnownCameraUsageCounter" not in vehicle:
        return None
    path = "vehicle.lastKnownCameraUsageCounter"
    result = _optional_typed_object(vehicle.get("lastKnownCameraUsageCounter"), path)
    if result is None:
        return None
    return LastKnownCameraUsageCounter(
        counter=_nullable_string(result.get("counter"), f"{path}.counter"),
        last_update_time=_nullable_datetime(
            result.get("lastUpdateTime"),
            f"{path}.lastUpdateTime",
        ),
    )


def parse_location_details(data: Mapping[str, object]) -> LocationDetails | None:
    """Parse the raw EMP status wrapper and charging-location collection."""

    root_field = "locationDetails"
    if root_field not in data:
        raise ResponseError(f"{root_field} is missing")
    result = _optional_typed_object(data.get(root_field), root_field)
    if result is None:
        return None

    raw_locations = _nullable_list(result.get("data"), f"{root_field}.data")
    locations: tuple[EmpLocation | None, ...] | None = None
    if raw_locations is not None:
        parsed_locations: list[EmpLocation | None] = []
        for index, value in enumerate(raw_locations):
            if value is None:
                parsed_locations.append(None)
                continue
            parsed_locations.append(_parse_emp_location(value, f"{root_field}.data[{index}]"))
        locations = tuple(parsed_locations)

    return LocationDetails(
        status_code=_nullable_string(result.get("statusCode"), f"{root_field}.statusCode"),
        status_message=_nullable_string(
            result.get("statusMessage"),
            f"{root_field}.statusMessage",
        ),
        timestamp=_nullable_string(result.get("timestamp"), f"{root_field}.timestamp"),
        data=locations,
    )


def parse_parking_chargeable(data: Mapping[str, object]) -> ParkingChargeable | None:
    """Parse the raw EMP parking-chargeability status wrapper."""

    root_field = "parkingChargeable"
    if root_field not in data:
        raise ResponseError(f"{root_field} is missing")
    result = _optional_typed_object(data.get(root_field), root_field)
    if result is None:
        return None
    raw_data = _optional_typed_object(result.get("data"), f"{root_field}.data")
    return ParkingChargeable(
        status_code=_nullable_string(result.get("statusCode"), f"{root_field}.statusCode"),
        status_message=_nullable_string(
            result.get("statusMessage"),
            f"{root_field}.statusMessage",
        ),
        timestamp=_nullable_string(result.get("timestamp"), f"{root_field}.timestamp"),
        data=(
            ParkingChargeableData(
                evse_id=_nullable_string(raw_data.get("evseId"), f"{root_field}.data.evseId"),
                is_parking_chargeable=_nullable_bool(
                    raw_data.get("isParkingChargeable"),
                    f"{root_field}.data.isParkingChargeable",
                ),
                is_congestion_chargeable=_nullable_bool(
                    raw_data.get("isCongestionChargeable"),
                    f"{root_field}.data.isCongestionChargeable",
                ),
            )
            if raw_data is not None
            else None
        ),
    )


def parse_shareable_capabilities(
    data: Mapping[str, object],
) -> ShareableCapabilities | None:
    """Parse shareable capability groups while retaining nullable list items."""

    vehicle = _vehicle(data)
    if vehicle is None or "shareableCapabilities" not in vehicle:
        return None
    path = "vehicle.shareableCapabilities"
    result = _optional_typed_object(vehicle.get("shareableCapabilities"), path)
    if result is None:
        return None

    raw_groups = _list(result.get("group"), f"{path}.group")
    groups: list[ShareableCapabilityGroup | None] = []
    for index, value in enumerate(raw_groups):
        if value is None:
            groups.append(None)
            continue
        groups.append(_parse_shareable_capability_group(value, f"{path}.group[{index}]"))
    return ShareableCapabilities(tuple(groups))


def parse_tariff_pricing(data: Mapping[str, object]) -> TariffPricing | None:
    """Parse the raw EMP tariff-pricing status wrapper."""

    root_field = "tariffPricing"
    if root_field not in data:
        raise ResponseError(f"{root_field} is missing")
    result = _optional_typed_object(data.get(root_field), root_field)
    if result is None:
        return None
    raw_data = _optional_typed_object(result.get("data"), f"{root_field}.data")
    return TariffPricing(
        status_code=_nullable_string(result.get("statusCode"), f"{root_field}.statusCode"),
        status_message=_nullable_string(
            result.get("statusMessage"),
            f"{root_field}.statusMessage",
        ),
        timestamp=_nullable_string(result.get("timestamp"), f"{root_field}.timestamp"),
        data=(
            _parse_tariff_pricing_data(raw_data, f"{root_field}.data")
            if raw_data is not None
            else None
        ),
    )
