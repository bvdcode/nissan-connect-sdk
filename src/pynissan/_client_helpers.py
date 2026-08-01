from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from enum import StrEnum

from .exceptions import ResponseError
from .graphql_input import serialize_enum
from .models import (
    ChargeScheduleInput,
    ClimateParameters,
    ClimateScheduleInput,
    ClimateSettings,
    ServiceRequestKind,
    ServiceRequestResult,
    ServiceRequestStatus,
)
from .navigation_inputs import (
    NavigationDataSource,
)


def _start_climate_input(climate: ClimateSettings) -> dict[str, object]:
    return {
        "unit": serialize_enum(climate.unit),
        "temperatureValue": climate.temperature,
    }


def _temperature_input(climate: ClimateSettings) -> dict[str, object]:
    return {"value": climate.temperature, "unit": serialize_enum(climate.unit)}


def _climate_parameters_input(parameters: ClimateParameters | None) -> dict[str, object] | None:
    if parameters is None:
        return None
    seats = parameters.seats
    seats_input = None
    if seats is not None:
        seats_input = _optional_variables(
            frontDriverState=_enum_value(seats.front_driver),
            frontPassengerState=_enum_value(seats.front_passenger),
            rearLeftPassengerState=_enum_value(seats.rear_left),
            rearRightPassengerState=_enum_value(seats.rear_right),
            rearCenterPassengerState=_enum_value(seats.rear_center),
            thirdLeftState=_enum_value(seats.third_left),
            thirdRightState=_enum_value(seats.third_right),
        )
    return _optional_variables(
        seatsClimate=seats_input,
        steeringWheelHeaterState=_on_off(parameters.steering_wheel_heater),
        defrostAndDeicerState=_on_off(parameters.defrost_and_deicer),
    )


def _charge_schedule_input(schedule: ChargeScheduleInput) -> dict[str, object]:
    return {
        "startDateTime": _date_time_input(schedule.start_date_time),
        "duration": schedule.duration,
        "weekDays": [serialize_enum(day) for day in schedule.week_days],
    }


def _climate_schedule_input(schedule: ClimateScheduleInput) -> dict[str, object]:
    return {
        "startDateTime": _date_time_input(schedule.start_date_time),
        "weekDays": [serialize_enum(day) for day in schedule.week_days],
        "temperature": _temperature_input(schedule.climate),
    }


def _date_time_input(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Nissan date-time inputs must include a UTC offset")
    return value.isoformat()


def _enum_value(value: StrEnum | None) -> str | None:
    return serialize_enum(value) if value is not None else None


def _on_off(value: bool | None) -> str | None:
    if value is None:
        return None
    return "ON" if value else "OFF"


def _optional_variables(**values: object) -> dict[str, object]:
    return {key: value for key, value in values.items() if value is not None}


def _validate_positive_integer(value: int, name: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def _response_object(data: Mapping[str, object], root_field: str) -> Mapping[str, object]:
    result = data.get(root_field)
    if not isinstance(result, Mapping):
        raise ResponseError(f"{root_field} is missing from the Nissan response")
    return result


def _success(data: Mapping[str, object], root_field: str) -> bool:
    result = _response_object(data, root_field)
    success = result.get("success")
    if isinstance(success, bool):
        return success
    message = result.get("message")
    if isinstance(message, str) and message:
        raise ResponseError(message)
    raise ResponseError(f"{root_field} did not return a success value")


def _nullable_success(data: Mapping[str, object], root_field: str) -> bool:
    raw_result = data.get(root_field)
    if raw_result is None:
        return False
    if not isinstance(raw_result, Mapping):
        raise ResponseError(f"{root_field} is not an object")
    result = raw_result
    success = result.get("success")
    if isinstance(success, bool):
        return success
    message = result.get("message")
    if isinstance(message, str) and message:
        raise ResponseError(message)
    return False


def _navigation_headers(
    data_source: NavigationDataSource | None,
) -> Mapping[str, str] | None:
    if data_source is None:
        return None
    return {"x-tsp-datasource": serialize_enum(data_source)}


def _is_terminal_service_request(
    kind: ServiceRequestKind,
    result: ServiceRequestResult,
) -> bool:
    if kind in {ServiceRequestKind.ROUTE, ServiceRequestKind.T_JUNCTION}:
        return result.status in {
            ServiceRequestStatus.SUCCESS,
            ServiceRequestStatus.FAILED,
        }
    return result.is_terminal
