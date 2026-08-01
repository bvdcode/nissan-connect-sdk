from __future__ import annotations

from collections.abc import Mapping

from ._parsing_values import (
    _list,
    _object,
    _optional_bool,
    _optional_datetime,
    _optional_float,
    _optional_int,
    _optional_list,
    _optional_object,
    _optional_str,
    _required_bool,
    _required_datetime,
    _required_str,
)
from .models import (
    AlertAddress,
    AlertDistance,
    AlertLocation,
    BoundaryAlert,
    CurfewAlert,
    CurfewSchedule,
    RemoteServiceHistory,
    RemoteServiceHistoryEntry,
    SpeedAlert,
    SpeedThreshold,
    ValetAlert,
)


def _parse_boundary_alerts(value: object) -> tuple[BoundaryAlert | None, ...] | None:
    values = _optional_list(value, "vehicle.boundaryAlerts")
    if values is None:
        return None
    alerts: list[BoundaryAlert | None] = []
    for index, raw_item in enumerate(values):
        if raw_item is None:
            alerts.append(None)
            continue
        path = f"vehicle.boundaryAlerts[{index}]"
        item = _object(raw_item, path)
        address_value = _optional_object(item.get("address"), f"{path}.address")
        location_value = _optional_object(item.get("location"), f"{path}.location")
        radius_value = _optional_object(item.get("radius"), f"{path}.radius")
        alerts.append(
            BoundaryAlert(
                service_request_id=_required_str(
                    item.get("serviceRequestId"), f"{path}.serviceRequestId"
                ),
                alert_type=_optional_str(item.get("alertType")),
                name=_required_str(item.get("name"), f"{path}.name"),
                enabled=_required_bool(item.get("enabled"), f"{path}.enabled"),
                in_vehicle_warning=_required_bool(
                    item.get("inVehicleWarning"), f"{path}.inVehicleWarning"
                ),
                address=(
                    _parse_alert_address(address_value) if address_value is not None else None
                ),
                location=(
                    _parse_alert_location(location_value) if location_value is not None else None
                ),
                radius=_parse_alert_distance(radius_value) if radius_value is not None else None,
            )
        )
    return tuple(alerts)


def _parse_curfew_alerts(value: object) -> tuple[CurfewAlert | None, ...] | None:
    values = _optional_list(value, "vehicle.curfewAlerts")
    if values is None:
        return None
    alerts: list[CurfewAlert | None] = []
    for index, raw_item in enumerate(values):
        if raw_item is None:
            alerts.append(None)
            continue
        path = f"vehicle.curfewAlerts[{index}]"
        item = _object(raw_item, path)
        schedule_value = _optional_object(item.get("schedule"), f"{path}.schedule")
        alerts.append(
            CurfewAlert(
                service_request_id=_required_str(
                    item.get("serviceRequestId"), f"{path}.serviceRequestId"
                ),
                name=_required_str(item.get("name"), f"{path}.name"),
                enabled=_required_bool(item.get("enabled"), f"{path}.enabled"),
                in_vehicle_warning=_required_bool(
                    item.get("inVehicleWarning"), f"{path}.inVehicleWarning"
                ),
                schedule=(
                    _parse_curfew_schedule(schedule_value, f"{path}.schedule")
                    if schedule_value is not None
                    else None
                ),
            )
        )
    return tuple(alerts)


def _parse_speed_alerts(value: object) -> tuple[SpeedAlert | None, ...] | None:
    values = _optional_list(value, "vehicle.speedAlerts")
    if values is None:
        return None
    alerts: list[SpeedAlert | None] = []
    for index, raw_item in enumerate(values):
        if raw_item is None:
            alerts.append(None)
            continue
        path = f"vehicle.speedAlerts[{index}]"
        item = _object(raw_item, path)
        threshold_value = _optional_object(
            item.get("speedThreshold"),
            f"{path}.speedThreshold",
        )
        alerts.append(
            SpeedAlert(
                service_request_id=_required_str(
                    item.get("serviceRequestId"), f"{path}.serviceRequestId"
                ),
                name=_required_str(item.get("name"), f"{path}.name"),
                enabled=_required_bool(item.get("enabled"), f"{path}.enabled"),
                in_vehicle_warning=_required_bool(
                    item.get("inVehicleWarning"), f"{path}.inVehicleWarning"
                ),
                threshold=(
                    SpeedThreshold(
                        unit=_optional_str(threshold_value.get("type")),
                        value=_optional_float(threshold_value.get("value")),
                    )
                    if threshold_value is not None
                    else None
                ),
            )
        )
    return tuple(alerts)


def _parse_valet_alert(value: Mapping[str, object]) -> ValetAlert:
    radius_value = _optional_object(value.get("radius"), "vehicle.valetAlert.radius")
    return ValetAlert(
        service_request_id=_optional_str(value.get("serviceRequestId")),
        radius=_parse_alert_distance(radius_value) if radius_value is not None else None,
    )


def _parse_alert_address(value: Mapping[str, object]) -> AlertAddress:
    return AlertAddress(
        address1=_optional_str(value.get("address1")),
        address2=_optional_str(value.get("address2")),
        city=_optional_str(value.get("city")),
        state=_optional_str(value.get("state")),
        country=_optional_str(value.get("country")),
        postal_code=_optional_str(value.get("postalCode")),
    )


def _parse_alert_location(value: Mapping[str, object]) -> AlertLocation:
    return AlertLocation(
        latitude=_optional_float(value.get("latitude")),
        longitude=_optional_float(value.get("longitude")),
    )


def _parse_alert_distance(value: Mapping[str, object]) -> AlertDistance:
    return AlertDistance(
        value=_optional_float(value.get("value")),
        unit=_optional_str(value.get("unit")),
    )


def _parse_curfew_schedule(value: Mapping[str, object], path: str) -> CurfewSchedule:
    raw_week_days = _list(value.get("weekDays"), f"{path}.weekDays")
    week_days = tuple(
        None if raw_value is None else _required_str(raw_value, f"{path}.weekDays[{index}]")
        for index, raw_value in enumerate(raw_week_days)
    )
    return CurfewSchedule(
        all_day=_optional_bool(value.get("allDay")),
        start_date_time=_required_datetime(
            value.get("startDateTime"),
            f"{path}.startDateTime",
        ),
        duration=_optional_str(value.get("duration")),
        week_days=week_days,
    )


def parse_remote_service_history(
    data: Mapping[str, object],
) -> RemoteServiceHistory | None:
    """Parse a page of raw remote-service history."""

    vehicle = _optional_object(data.get("vehicle"), "vehicle")
    if vehicle is None:
        return None
    page = _optional_object(
        vehicle.get("remoteServiceHistory"),
        "vehicle.remoteServiceHistory",
    )
    if page is None:
        return None

    values = _optional_list(page.get("history"), "vehicle.remoteServiceHistory.history")
    history: tuple[RemoteServiceHistoryEntry | None, ...] | None = None
    if values is not None:
        parsed_history: list[RemoteServiceHistoryEntry | None] = []
        for index, value in enumerate(values):
            if value is None:
                parsed_history.append(None)
                continue
            item = _object(value, f"vehicle.remoteServiceHistory.history[{index}]")
            parsed_history.append(
                RemoteServiceHistoryEntry(
                    service_request_id=_optional_str(item.get("serviceRequestId")),
                    status=_optional_str(item.get("status")),
                    service_type=_optional_str(item.get("serviceType")),
                    status_change_date_time=_optional_datetime(item.get("statusChangeDateTime")),
                )
            )
        history = tuple(parsed_history)

    return RemoteServiceHistory(
        page_number=_optional_int(page.get("pageNumber")),
        items_per_page=_optional_int(page.get("itemsPerPage")),
        total_items=_optional_int(page.get("totalItems")),
        total_pages=_optional_int(page.get("totalPages")),
        history=history,
    )
