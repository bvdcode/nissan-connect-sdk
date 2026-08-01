from __future__ import annotations

from ._extended_vehicle_value_parsing import (
    _enum,
    _float,
    _nullable_datetime,
    _nullable_enum,
    _nullable_float,
    _nullable_int,
    _nullable_string,
    _optional_typed_object,
    _typed_object,
)
from .extended_vehicle_models import (
    DrivingHistoryAverageSpeed,
    DrivingHistoryCo2Saved,
    DrivingHistoryCoordinate,
    DrivingHistoryDistance,
    DrivingHistoryTrip,
    DrivingHistoryTripSummary,
    WeightUnit,
)
from .models import DistanceUnit, SpeedUnit


def _parse_driving_history_summary(
    value: object,
    path: str,
) -> DrivingHistoryTripSummary:
    summary = _typed_object(value, path)
    return DrivingHistoryTripSummary(
        user_id=_nullable_string(summary.get("userId"), f"{path}.userId"),
        day=_nullable_int(summary.get("day"), f"{path}.day"),
        month=_nullable_int(summary.get("month"), f"{path}.month"),
        year=_nullable_int(summary.get("year"), f"{path}.year"),
        number_of_trips=_nullable_int(
            summary.get("numberOfTrips"),
            f"{path}.numberOfTrips",
        ),
        distance_traveled=_parse_optional_driving_distance(
            summary.get("distanceTraveled"),
            f"{path}.distanceTraveled",
        ),
        duration=_nullable_string(summary.get("duration"), f"{path}.duration"),
        average_speed=_parse_optional_average_speed(
            summary.get("averageSpeed"),
            f"{path}.averageSpeed",
        ),
        energy_consumed=_nullable_float(
            summary.get("energyConsumed"),
            f"{path}.energyConsumed",
        ),
        co2_saved=_parse_optional_co2_saved(
            summary.get("co2Saved"),
            f"{path}.co2Saved",
        ),
    )


def _parse_driving_history_trip(value: object, path: str) -> DrivingHistoryTrip:
    trip = _typed_object(value, path)
    return DrivingHistoryTrip(
        distance=_parse_optional_driving_distance(
            trip.get("distance"),
            f"{path}.distance",
        ),
        start_date=_nullable_datetime(trip.get("startDate"), f"{path}.startDate"),
        end_date=_nullable_datetime(trip.get("endDate"), f"{path}.endDate"),
        duration=_nullable_int(trip.get("duration"), f"{path}.duration"),
        start_location=_parse_optional_driving_coordinate(
            trip.get("startLocation"),
            f"{path}.startLocation",
        ),
        end_location=_parse_optional_driving_coordinate(
            trip.get("endLocation"),
            f"{path}.endLocation",
        ),
        average_speed=_parse_optional_average_speed(
            trip.get("averageSpeed"),
            f"{path}.averageSpeed",
        ),
        energy_consumed=_nullable_float(
            trip.get("energyConsumed"),
            f"{path}.energyConsumed",
        ),
        energy_saved=_nullable_float(trip.get("energySaved"), f"{path}.energySaved"),
        co2_saved=_parse_optional_co2_saved(trip.get("co2Saved"), f"{path}.co2Saved"),
        user_id=_nullable_string(trip.get("userId"), f"{path}.userId"),
    )


def _parse_optional_driving_distance(
    value: object,
    path: str,
) -> DrivingHistoryDistance | None:
    distance = _optional_typed_object(value, path)
    if distance is None:
        return None
    return DrivingHistoryDistance(
        unit=_enum(distance.get("unit"), DistanceUnit, f"{path}.unit"),
        value=_float(distance.get("value"), f"{path}.value"),
    )


def _parse_optional_average_speed(
    value: object,
    path: str,
) -> DrivingHistoryAverageSpeed | None:
    speed = _optional_typed_object(value, path)
    if speed is None:
        return None
    return DrivingHistoryAverageSpeed(
        type=_nullable_enum(speed.get("type"), SpeedUnit, f"{path}.type"),
        value=_nullable_float(speed.get("value"), f"{path}.value"),
    )


def _parse_optional_co2_saved(
    value: object,
    path: str,
) -> DrivingHistoryCo2Saved | None:
    saved = _optional_typed_object(value, path)
    if saved is None:
        return None
    return DrivingHistoryCo2Saved(
        unit=_nullable_enum(saved.get("unit"), WeightUnit, f"{path}.unit"),
        value=_nullable_float(saved.get("value"), f"{path}.value"),
    )


def _parse_optional_driving_coordinate(
    value: object,
    path: str,
) -> DrivingHistoryCoordinate | None:
    coordinate = _optional_typed_object(value, path)
    if coordinate is None:
        return None
    return DrivingHistoryCoordinate(
        latitude=_nullable_float(coordinate.get("latitude"), f"{path}.latitude"),
        longitude=_nullable_float(coordinate.get("longitude"), f"{path}.longitude"),
    )
