from __future__ import annotations

from collections.abc import Mapping

from ._parsing_values import (
    _list,
    _object,
    _optional_datetime,
    _optional_float,
    _optional_int,
    _optional_list,
    _optional_object,
    _optional_str,
    _optional_v2l_state,
    _parse_week_days,
    _required_datetime,
    _required_str,
)
from ._vehicle_response_parsing import _parse_climate_parameters, _parse_temperature
from .models import (
    ChargeConfig,
    ChargeHistorySummary,
    ChargeSchedule,
    ChargeSession,
    ClimateDefaults,
    ClimateSchedule,
    DelayedClimateSchedule,
    V2LStatus,
    VehicleChargeHistory,
    VehicleClimateSchedules,
)


def parse_charge_schedules(data: Mapping[str, object]) -> tuple[ChargeSchedule, ...]:
    """Parse charge schedules."""

    vehicle = _object(data.get("vehicle"), "vehicle")
    values = _optional_list(vehicle.get("chargeSchedules"), "vehicle.chargeSchedules") or []
    schedules: list[ChargeSchedule] = []
    for index, value in enumerate(values):
        item = _object(value, f"vehicle.chargeSchedules[{index}]")
        schedules.append(
            ChargeSchedule(
                id=_required_str(item.get("id"), "chargeSchedule.id"),
                state=_optional_str(item.get("state")),
                start_date_time=_required_datetime(
                    item.get("startDateTime"), "chargeSchedule.startDateTime"
                ),
                duration=_required_str(item.get("duration"), "chargeSchedule.duration"),
                week_days=_parse_week_days(item.get("weekDays"), "chargeSchedule.weekDays"),
            )
        )
    return tuple(schedules)


def parse_charge_config(data: Mapping[str, object]) -> ChargeConfig | None:
    """Parse configured charging limits, if supported by the vehicle."""

    vehicle = _object(data.get("vehicle"), "vehicle")
    config = _optional_object(vehicle.get("chargeConfig"), "vehicle.chargeConfig")
    if config is None:
        return None

    limits = _optional_object(config.get("limits"), "vehicle.chargeConfig.limits")
    if limits is None:
        return ChargeConfig(None, None)

    charge = _optional_object(limits.get("charge"), "vehicle.chargeConfig.limits.charge")
    notification = _optional_object(
        limits.get("notification"),
        "vehicle.chargeConfig.limits.notification",
    )
    return ChargeConfig(
        charge_limit_percent=(_optional_int(charge.get("percent")) if charge is not None else None),
        notification_threshold_percent=(
            _optional_int(notification.get("percent")) if notification is not None else None
        ),
    )


def parse_v2l_status(data: Mapping[str, object]) -> V2LStatus | None:
    """Parse V2L state and battery reserve percentages."""

    vehicle = _optional_object(data.get("vehicle"), "vehicle")
    if vehicle is None:
        return None
    status = _optional_object(vehicle.get("v2lStatus"), "vehicle.v2lStatus")
    if status is None:
        return None
    return V2LStatus(
        state=_optional_v2l_state(status.get("state")),
        charge_limit_percent=_optional_float(status.get("chargeLimitationLevel")),
        minimum_charge_limit_percent=_optional_float(status.get("chargeMinimumLimitationLevel")),
    )


def parse_vehicle_charge_history(
    data: Mapping[str, object],
) -> VehicleChargeHistory | None:
    """Parse charging sessions and aggregate summaries, if supported."""

    vehicle = _object(data.get("vehicle"), "vehicle")
    history = _optional_object(vehicle.get("chargeHistory"), "vehicle.chargeHistory")
    if history is None:
        return None

    charge_values = _list(history.get("charges"), "vehicle.chargeHistory.charges")
    charges: list[ChargeSession] = []
    for index, value in enumerate(charge_values):
        item = _object(value, f"vehicle.chargeHistory.charges[{index}]")
        charges.append(
            ChargeSession(
                start=_optional_datetime(item.get("start")),
                end=_optional_datetime(item.get("end")),
                duration=_optional_str(item.get("duration")),
                recovered_energy_kwh=_optional_float(item.get("recoveredEnergy")),
            )
        )

    summary_values = _list(
        history.get("chargeSummaries"),
        "vehicle.chargeHistory.chargeSummaries",
    )
    summaries: list[ChargeHistorySummary] = []
    for index, value in enumerate(summary_values):
        item = _object(value, f"vehicle.chargeHistory.chargeSummaries[{index}]")
        summaries.append(
            ChargeHistorySummary(
                day=_optional_int(item.get("day")),
                month=_optional_int(item.get("month")),
                year=_optional_int(item.get("year")),
                number_of_charge_sessions=_optional_int(item.get("numberOfChargeSessions")),
                total_energy_recovered_kwh=_optional_float(item.get("totalEnergyRecovered")),
                total_duration_minutes=_optional_int(item.get("totalDuration")),
                number_of_errors=_optional_int(item.get("numberOfErrors")),
                user_id=_optional_str(item.get("userId")),
                role_type=_optional_str(item.get("roleType")),
            )
        )

    return VehicleChargeHistory(tuple(charges), tuple(summaries))


def parse_climate_schedules(data: Mapping[str, object]) -> VehicleClimateSchedules:
    """Parse recurring and one-time climate schedules and their accessories."""

    vehicle = _object(data.get("vehicle"), "vehicle")
    values = _optional_list(vehicle.get("climateSchedules"), "vehicle.climateSchedules") or []
    schedules: list[ClimateSchedule] = []
    for index, value in enumerate(values):
        item = _object(value, f"vehicle.climateSchedules[{index}]")
        temperature = _object(item.get("temperature"), "climateSchedule.temperature")
        schedules.append(
            ClimateSchedule(
                id=_required_str(item.get("id"), "climateSchedule.id"),
                state=_optional_str(item.get("state")),
                start_date_time=_required_datetime(
                    item.get("startDateTime"), "climateSchedule.startDateTime"
                ),
                week_days=_parse_week_days(item.get("weekDays"), "climateSchedule.weekDays"),
                temperature=_parse_temperature(temperature),
            )
        )

    accessories = _optional_object(
        vehicle.get("climateSchedulesAccessories"),
        "vehicle.climateSchedulesAccessories",
    )
    delayed = _optional_object(
        vehicle.get("delayedClimateSchedule"),
        "vehicle.delayedClimateSchedule",
    )
    return VehicleClimateSchedules(
        schedules=tuple(schedules),
        accessories=(_parse_climate_parameters(accessories) if accessories is not None else None),
        delayed_schedule=(
            DelayedClimateSchedule(start_date_time=_optional_datetime(delayed.get("startDateTime")))
            if delayed is not None
            else None
        ),
    )


def parse_climate_defaults(data: Mapping[str, object]) -> ClimateDefaults | None:
    """Parse saved climate defaults, if supported by the vehicle."""

    vehicle = _object(data.get("vehicle"), "vehicle")
    defaults = _optional_object(vehicle.get("climateDefaults"), "vehicle.climateDefaults")
    if defaults is None:
        return None
    climate = _optional_object(defaults.get("climate"), "vehicle.climateDefaults.climate")
    parameters = _optional_object(defaults.get("parameters"), "vehicle.climateDefaults.parameters")
    return ClimateDefaults(
        climate=_parse_temperature(climate) if climate is not None else None,
        parameters=_parse_climate_parameters(parameters) if parameters is not None else None,
    )
