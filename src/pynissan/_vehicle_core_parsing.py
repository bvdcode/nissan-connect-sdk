from __future__ import annotations

from collections.abc import Mapping

from ._parsing_values import (
    _list,
    _object,
    _optional_bool,
    _optional_camera_position,
    _optional_camera_service,
    _optional_datetime,
    _optional_int,
    _optional_list,
    _optional_object,
    _optional_str,
    _required_str,
)
from ._vehicle_alert_parsing import (
    _parse_alert_location,
    _parse_boundary_alerts,
    _parse_curfew_alerts,
    _parse_speed_alerts,
    _parse_valet_alert,
)
from ._vehicle_response_parsing import (
    _parse_battery,
    _parse_climate_status,
    _parse_distance,
    _parse_doors,
    _parse_engine_oil_drain_range,
    _parse_location,
    _parse_maintenance_indicator,
    _parse_mileage,
    _parse_tires,
)
from .exceptions import ResponseError
from .models import (
    BreachAlert,
    BreachAlerts,
    DataPrivacyMode,
    ReminderNotificationsAfterLeavingVehicle,
    Vehicle,
    VehicleAlertKind,
    VehicleAlertRequest,
    VehicleAlerts,
    VehicleLocation,
    VehiclePhoto,
    VehiclePhotos,
    VehicleStatus,
)


def parse_vehicles(data: Mapping[str, object]) -> tuple[Vehicle, ...]:
    """Parse the account vehicle list."""

    values = _list(data.get("vehicles"), "vehicles")
    vehicles: list[Vehicle] = []
    for index, value in enumerate(values):
        item = _object(value, f"vehicles[{index}]")
        vehicles.append(
            Vehicle(
                vin=_required_str(item.get("vin"), f"vehicles[{index}].vin"),
                year=_optional_str(item.get("year")),
                model=_optional_str(item.get("model")),
                color=_optional_str(item.get("color")),
                nickname=_optional_str(item.get("nickname")),
                image_url=_optional_str(item.get("image")),
                driver_type=_optional_str(item.get("driverType")),
                plate=_optional_str(item.get("plate")),
            )
        )
    return tuple(vehicles)


def parse_vehicle_status(data: Mapping[str, object], vin: str) -> VehicleStatus:
    """Parse dynamic status for one vehicle."""

    vehicle = _object(data.get("vehicle"), "vehicle")
    battery_value = _optional_object(vehicle.get("batteryStatus"), "vehicle.batteryStatus")
    climate_value = _optional_object(vehicle.get("climateStatus"), "vehicle.climateStatus")
    doors_value = _optional_object(vehicle.get("doorsStatus"), "vehicle.doorsStatus")
    fuel_value = _optional_object(vehicle.get("fuelAutonomy"), "vehicle.fuelAutonomy")
    mileage_value = _optional_object(vehicle.get("mileage"), "vehicle.mileage")
    tires_value = _optional_object(vehicle.get("tirePressure"), "vehicle.tirePressure")
    engine_oil_value = _optional_object(
        vehicle.get("engineOilDrainRange"),
        "vehicle.engineOilDrainRange",
    )

    mils = _optional_list(vehicle.get("mils"), "vehicle.mils") or []
    indicators = tuple(
        _parse_maintenance_indicator(_object(value, f"vehicle.mils[{index}]"))
        for index, value in enumerate(mils)
    )

    return VehicleStatus(
        vin=vin,
        vehicle_type=_optional_str(vehicle.get("__typename")),
        battery=_parse_battery(battery_value) if battery_value is not None else None,
        climate=_parse_climate_status(climate_value) if climate_value is not None else None,
        doors=_parse_doors(doors_value) if doors_value is not None else None,
        fuel_range=_parse_distance(fuel_value) if fuel_value is not None else None,
        mileage=_parse_mileage(mileage_value) if mileage_value is not None else None,
        tire_pressure=_parse_tires(tires_value) if tires_value is not None else None,
        maintenance_indicators=indicators,
        engine_oil_drain_range=(
            _parse_engine_oil_drain_range(engine_oil_value)
            if engine_oil_value is not None
            else None
        ),
    )


def parse_vehicle_location(data: Mapping[str, object], vin: str) -> VehicleLocation:
    """Parse the cached vehicle location query."""

    vehicle = _object(data.get("vehicle"), "vehicle")
    location = _optional_object(vehicle.get("location"), "vehicle.location")
    if location is None:
        return VehicleLocation(vin=vin, latitude=None, longitude=None, last_updated_at=None)
    return _parse_location(location, vin)


def parse_photos_around_vehicle(data: Mapping[str, object]) -> VehiclePhotos | None:
    """Parse photos currently available around a vehicle."""

    vehicle = _optional_object(data.get("vehicle"), "vehicle")
    if vehicle is None:
        return None

    values = _optional_list(
        vehicle.get("photosAroundVehicle"),
        "vehicle.photosAroundVehicle",
    )
    photos: tuple[VehiclePhoto | None, ...] | None = None
    if values is not None:
        parsed_photos: list[VehiclePhoto | None] = []
        for index, value in enumerate(values):
            if value is None:
                parsed_photos.append(None)
                continue
            item = _object(value, f"vehicle.photosAroundVehicle[{index}]")
            parsed_photos.append(
                VehiclePhoto(
                    id=_optional_str(item.get("id")),
                    filename=_optional_str(item.get("filename")),
                    link=_optional_str(item.get("link")),
                    timestamp=_optional_datetime(item.get("timeStamp")),
                    camera_position=_optional_camera_position(item.get("cameraPosition")),
                    camera_service=_optional_camera_service(item.get("cameraService")),
                )
            )
        photos = tuple(parsed_photos)

    return VehiclePhotos(
        vin=_required_str(vehicle.get("vin"), "vehicle.vin"),
        year=_required_str(vehicle.get("year"), "vehicle.year"),
        model=_required_str(vehicle.get("model"), "vehicle.model"),
        photos=photos,
    )


def parse_vehicle_alerts(data: Mapping[str, object]) -> VehicleAlerts | None:
    """Parse all configured alerts for one connected vehicle."""

    vehicle = _optional_object(data.get("vehicle"), "vehicle")
    if vehicle is None:
        return None
    alert_fields = ("boundaryAlerts", "curfewAlerts", "speedAlerts", "valetAlert")
    if not any(field in vehicle for field in alert_fields):
        return None

    valet_value = _optional_object(vehicle.get("valetAlert"), "vehicle.valetAlert")
    return VehicleAlerts(
        boundary_alerts=_parse_boundary_alerts(vehicle.get("boundaryAlerts")),
        curfew_alerts=_parse_curfew_alerts(vehicle.get("curfewAlerts")),
        speed_alerts=_parse_speed_alerts(vehicle.get("speedAlerts")),
        valet_alert=_parse_valet_alert(valet_value) if valet_value is not None else None,
    )


def parse_breach_alerts(data: Mapping[str, object]) -> BreachAlerts | None:
    """Parse one page of raw vehicle-alert breach events."""

    vehicle = _optional_object(data.get("vehicle"), "vehicle")
    if vehicle is None:
        return None
    page = _optional_object(vehicle.get("breachAlerts"), "vehicle.breachAlerts")
    if page is None:
        return None

    values = _optional_list(page.get("alerts"), "vehicle.breachAlerts.alerts")
    alerts: tuple[BreachAlert | None, ...] | None = None
    if values is not None:
        parsed_alerts: list[BreachAlert | None] = []
        for index, value in enumerate(values):
            if value is None:
                parsed_alerts.append(None)
                continue
            path = f"vehicle.breachAlerts.alerts[{index}]"
            item = _object(value, path)
            location_value = _optional_object(item.get("location"), f"{path}.location")
            parsed_alerts.append(
                BreachAlert(
                    service_type=_optional_str(item.get("serviceType")),
                    breach_date_time=_optional_datetime(item.get("breachDateTime")),
                    name=_optional_str(item.get("name")),
                    location=(
                        _parse_alert_location(location_value)
                        if location_value is not None
                        else None
                    ),
                )
            )
        alerts = tuple(parsed_alerts)

    return BreachAlerts(
        items_per_page=_optional_int(page.get("itemsPerPage")),
        page_number=_optional_int(page.get("pageNumber")),
        total_items=_optional_int(page.get("totalItems")),
        total_pages=_optional_int(page.get("totalPages")),
        alerts=alerts,
    )


def parse_alert_request_status(
    data: Mapping[str, object],
    root_field: str,
    *,
    status_required: bool,
) -> str | None:
    """Parse the raw status returned by one vehicle-alert detail query."""

    vehicle = _optional_object(data.get("vehicle"), "vehicle")
    if vehicle is None:
        return None
    alert = _optional_object(vehicle.get(root_field), f"vehicle.{root_field}")
    if alert is None:
        return None
    if status_required:
        return _required_str(alert.get("status"), f"vehicle.{root_field}.status")
    return _optional_str(alert.get("status"))


def parse_vehicle_alert_request(
    data: Mapping[str, object],
    root_field: str,
    kind: VehicleAlertKind,
) -> VehicleAlertRequest:
    """Parse an accepted asynchronous vehicle-alert change."""

    result = _object(data.get(root_field), root_field)
    request_id = _optional_str(result.get("serviceRequestId"))
    if not request_id:
        message = _optional_str(result.get("message"))
        if message:
            raise ResponseError(message)
        raise ResponseError(f"{root_field} did not return a service request id")
    return VehicleAlertRequest(request_id, kind)


def parse_reminder_notifications_after_leaving_vehicle(
    data: Mapping[str, object],
) -> ReminderNotificationsAfterLeavingVehicle | None:
    """Parse nullable after-leaving reminder flags for an AVK2 vehicle."""

    vehicle = _optional_object(data.get("vehicle"), "vehicle")
    if vehicle is None:
        return None
    reminders = _optional_object(
        vehicle.get("reminderNotificationsAfterLeavingVehicle"),
        "vehicle.reminderNotificationsAfterLeavingVehicle",
    )
    if reminders is None:
        return None
    return ReminderNotificationsAfterLeavingVehicle(
        lock=_optional_bool(reminders.get("lock")),
        door=_optional_bool(reminders.get("door")),
        trunk=_optional_bool(reminders.get("trunk")),
        sunroof=_optional_bool(reminders.get("sunroof")),
        window=_optional_bool(reminders.get("window")),
    )


def parse_toggle_reminder_notifications_after_leaving_vehicle(
    data: Mapping[str, object],
) -> bool | None:
    """Parse the nullable success value returned by the reminder mutation."""

    result = _optional_object(
        data.get("toggleReminderNotificationsAfterLeavingVehicle"),
        "toggleReminderNotificationsAfterLeavingVehicle",
    )
    return _optional_bool(result.get("success")) if result is not None else None


def parse_vehicle_data_privacy_mode(
    data: Mapping[str, object],
) -> DataPrivacyMode | None:
    """Parse a vehicle's required privacy mode when the vehicle exists."""

    vehicle = _optional_object(data.get("vehicle"), "vehicle")
    if vehicle is None:
        return None
    raw_mode = _required_str(
        vehicle.get("dataPrivacyMode"),
        "vehicle.dataPrivacyMode",
    )
    try:
        return DataPrivacyMode(raw_mode)
    except ValueError:
        return DataPrivacyMode.UNKNOWN_VALUE
