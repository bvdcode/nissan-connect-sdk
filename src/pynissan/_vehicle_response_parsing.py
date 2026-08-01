from __future__ import annotations

from collections.abc import Mapping

from ._parsing_values import (
    _nested_optional_str,
    _object,
    _optional_bool,
    _optional_datetime,
    _optional_float,
    _optional_int,
    _optional_object,
    _optional_on_off,
    _optional_seat_option,
    _optional_str,
    _required_datetime,
    _required_distance_unit,
    _required_float,
    _required_int,
    _required_str,
)
from .exceptions import ResponseError
from .models import (
    BatteryStatus,
    ClimateParameters,
    ClimateStatus,
    DistanceReading,
    DoorsStatus,
    DoorState,
    EngineOilDrainRange,
    MaintenanceIndicator,
    Mileage,
    SeatClimateSettings,
    ServiceRequest,
    ServiceRequestKind,
    ServiceRequestResult,
    ServiceRequestStatus,
    TemperatureReading,
    TirePressure,
    VehicleLocation,
)


def parse_service_request(
    data: Mapping[str, object],
    root_field: str,
    kind: ServiceRequestKind,
) -> ServiceRequest:
    """Parse an accepted asynchronous remote request and its immediate metadata."""

    result = _object(data.get(root_field), root_field)
    request_id = _optional_str(result.get("serviceRequestId"))
    if not request_id:
        message = _optional_str(result.get("message"))
        if message:
            raise ResponseError(message)
        raise ResponseError(f"{root_field} did not return a service request id")

    additional_data = _optional_object(
        result.get("additionalData"),
        f"{root_field}.additionalData",
    )
    climate_defaults_success: bool | None = None
    climate_defaults_error_message: str | None = None
    if additional_data is not None:
        climate_defaults_success = _optional_bool(additional_data.get("success"))
        climate_defaults_error_message = _optional_str(additional_data.get("message"))

    return ServiceRequest(
        id=request_id,
        kind=kind,
        climate_defaults_success=climate_defaults_success,
        climate_defaults_error_message=climate_defaults_error_message,
    )


def parse_service_request_result(
    data: Mapping[str, object],
    root_field: str,
    vin: str,
) -> ServiceRequestResult:
    """Parse a remote service-request status operation."""

    result = _object(data.get(root_field), root_field)
    raw_status = result.get("status")
    status: ServiceRequestStatus | None = None
    if raw_status is not None:
        status_value = _required_str(raw_status, f"{root_field}.status")
        try:
            status = ServiceRequestStatus(status_value)
        except ValueError:
            status = ServiceRequestStatus.UNKNOWN_VALUE
    location_value = _optional_object(result.get("location"), f"{root_field}.location")
    return ServiceRequestResult(
        status=status,
        status_details=_optional_str(result.get("statusDetails")),
        location=_parse_location(location_value, vin) if location_value is not None else None,
        activation_date_time=_optional_datetime(result.get("activationDateTime")),
        status_change_date_time=_optional_datetime(result.get("statusChangeDateTime")),
    )


def _parse_battery(value: Mapping[str, object]) -> BatteryStatus:
    remaining = _optional_object(value.get("remainingMileage"), "batteryStatus.remainingMileage")
    return BatteryStatus(
        level=_optional_int(value.get("level")),
        is_plugged_in=_optional_bool(value.get("isPluggedIn")),
        is_charging=_optional_bool(value.get("isCharging")),
        remaining_charge_time=_optional_int(value.get("remainingChargeTime")),
        remaining_mileage=_parse_distance(remaining) if remaining is not None else None,
    )


def _parse_climate_status(value: Mapping[str, object]) -> ClimateStatus:
    temperature = _optional_object(value.get("temperature"), "climateStatus.temperature")
    return ClimateStatus(
        state=_optional_str(value.get("state")),
        temperature=_parse_temperature(temperature) if temperature is not None else None,
    )


def _parse_engine_oil_drain_range(
    value: Mapping[str, object],
) -> EngineOilDrainRange:
    return EngineOilDrainRange(
        range=_required_int(value.get("range"), "engineOilDrainRange.range"),
        unit=_required_distance_unit(
            value.get("unit"),
            "engineOilDrainRange.unit",
        ),
        last_updated_at=_required_datetime(
            value.get("lastUpdatedAt"),
            "engineOilDrainRange.lastUpdatedAt",
        ),
    )


def _parse_doors(value: Mapping[str, object]) -> DoorsStatus:
    return DoorsStatus(
        last_updated_at=_optional_datetime(value.get("lastUpdatedAt")),
        front_left=_parse_door(value.get("doorFrontLeft"), "doorsStatus.doorFrontLeft"),
        front_right=_parse_door(value.get("doorFrontRight"), "doorsStatus.doorFrontRight"),
        rear_left=_parse_door(value.get("doorRearLeft"), "doorsStatus.doorRearLeft"),
        rear_right=_parse_door(value.get("doorRearRight"), "doorsStatus.doorRearRight"),
        engine_hood_ajar=_nested_optional_str(value.get("engineHood"), "ajar"),
        hatch_ajar=_nested_optional_str(value.get("hatch"), "ajar"),
        sunroof_ajar=_nested_optional_str(value.get("sunroof"), "ajar"),
        trunk_lock=_nested_optional_str(value.get("trunk"), "lock"),
        overall_lock=_nested_optional_str(value.get("overallLock"), "lock"),
    )


def _parse_door(value: object, path: str) -> DoorState | None:
    item = _optional_object(value, path)
    if item is None:
        return None
    return DoorState(
        ajar=_optional_str(item.get("ajar")),
        window=_optional_str(item.get("window")),
        lock=_optional_str(item.get("lock")),
    )


def _parse_distance(value: Mapping[str, object]) -> DistanceReading:
    return DistanceReading(
        value=_optional_int(value.get("value")),
        unit=_optional_str(value.get("unit")),
        last_updated_at=_optional_datetime(value.get("lastUpdatedAt")),
    )


def _parse_mileage(value: Mapping[str, object]) -> Mileage:
    return Mileage(
        total=_optional_int(value.get("total")),
        unit=_optional_str(value.get("unit")),
        recorded_at=_optional_datetime(value.get("recordedTime")),
    )


def _parse_tires(value: Mapping[str, object]) -> TirePressure:
    return TirePressure(
        last_updated_at=_optional_datetime(value.get("lastUpdatedAt")),
        front_left=_optional_int(value.get("flPressure")),
        front_right=_optional_int(value.get("frPressure")),
        rear_left=_optional_int(value.get("rlPressure")),
        rear_right=_optional_int(value.get("rrPressure")),
        front_left_status=_optional_int(value.get("flStatus")),
        front_right_status=_optional_int(value.get("frStatus")),
        rear_left_status=_optional_int(value.get("rlStatus")),
        rear_right_status=_optional_int(value.get("rrStatus")),
    )


def _parse_maintenance_indicator(value: Mapping[str, object]) -> MaintenanceIndicator:
    return MaintenanceIndicator(
        active=_optional_bool(value.get("active")),
        detailed_message=_optional_str(value.get("detailedMessage")),
        type=_optional_str(value.get("type")),
    )


def _parse_temperature(value: Mapping[str, object]) -> TemperatureReading:
    return TemperatureReading(
        value=_required_float(value.get("value"), "temperature.value"),
        unit=_required_str(value.get("unit"), "temperature.unit"),
    )


def _parse_location(value: Mapping[str, object], vin: str) -> VehicleLocation:
    return VehicleLocation(
        vin=vin,
        latitude=_optional_float(value.get("latitude")),
        longitude=_optional_float(value.get("longitude")),
        last_updated_at=_optional_datetime(value.get("lastUpdatedAt")),
    )


def _parse_climate_parameters(value: Mapping[str, object]) -> ClimateParameters:
    seats_value = _optional_object(value.get("seatsClimate"), "parameters.seatsClimate")
    seats = None
    if seats_value is not None:
        seats = SeatClimateSettings(
            front_driver=_optional_seat_option(seats_value.get("frontDriverState")),
            front_passenger=_optional_seat_option(seats_value.get("frontPassengerState")),
            rear_left=_optional_seat_option(seats_value.get("rearLeftPassengerState")),
            rear_right=_optional_seat_option(seats_value.get("rearRightPassengerState")),
            rear_center=_optional_seat_option(seats_value.get("rearCenterPassengerState")),
            third_left=_optional_seat_option(seats_value.get("thirdLeftState")),
            third_right=_optional_seat_option(seats_value.get("thirdRightState")),
        )
    return ClimateParameters(
        seats=seats,
        steering_wheel_heater=_optional_on_off(value.get("steeringWheelHeaterState")),
        defrost_and_deicer=_optional_on_off(value.get("defrostAndDeicerState")),
    )
