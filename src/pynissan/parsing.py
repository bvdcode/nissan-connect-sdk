from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime

from .exceptions import ResponseError
from .models import (
    AccessoryCapability,
    AlertAddress,
    AlertDistance,
    AlertLocation,
    BatteryStatus,
    BoundaryAlert,
    BreachAlert,
    BreachAlerts,
    CameraPosition,
    CameraService,
    ChargeConfig,
    ChargeHistorySummary,
    ChargeSchedule,
    ChargeSession,
    ClimateDefaults,
    ClimateParameters,
    ClimateSchedule,
    ClimateStatus,
    CurfewAlert,
    CurfewSchedule,
    DataPrivacyMode,
    DelayedClimateSchedule,
    DistanceReading,
    DistanceUnit,
    DoorsStatus,
    DoorState,
    EngineOilDrainRange,
    HvacTemperatureCapabilities,
    MaintenanceIndicator,
    Mileage,
    ProductType,
    PurchaseType,
    ReminderNotificationsAfterLeavingVehicle,
    RemoteServiceHistory,
    RemoteServiceHistoryEntry,
    SeatClimateOption,
    SeatClimateSettings,
    SeatHeaterAccessories,
    SeatHeaterCapability,
    ServiceCapability,
    ServiceRequest,
    ServiceRequestKind,
    ServiceRequestResult,
    ServiceRequestStatus,
    SpeedAlert,
    SpeedThreshold,
    SunRoofCapability,
    TemperatureReading,
    TirePressure,
    V2LState,
    V2LStatus,
    ValetAlert,
    Vehicle,
    VehicleAccessoriesDetails,
    VehicleAlertKind,
    VehicleAlertRequest,
    VehicleAlerts,
    VehicleCapabilities,
    VehicleChargeHistory,
    VehicleClimateSchedules,
    VehicleLocation,
    VehiclePhoto,
    VehiclePhotos,
    VehiclePreferences,
    VehicleStatus,
    VehicleSubscription,
    VehicleSubscriptionPendingOrder,
    VehicleSubscriptionProduct,
    VehicleSubscriptions,
    VehicleWifiConsumption,
    WayPointCapability,
    WeekDay,
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


def parse_vehicle_wifi_consumption(
    data: Mapping[str, object],
) -> VehicleWifiConsumption | None:
    """Parse nullable vehicle Wi-Fi consumption with required inner fields."""

    vehicle = _optional_object(data.get("vehicle"), "vehicle")
    if vehicle is None:
        return None
    capabilities = _optional_object(
        vehicle.get("capabilities"),
        "vehicle.capabilities",
    )
    if capabilities is None:
        return None
    consumption = _optional_object(
        capabilities.get("wifiConsumption"),
        "vehicle.capabilities.wifiConsumption",
    )
    if consumption is None:
        return None
    return VehicleWifiConsumption(
        usage_percent=_required_float(
            consumption.get("usagePercent"),
            "vehicle.capabilities.wifiConsumption.usagePercent",
        ),
        usage_amount_gb=_required_float(
            consumption.get("usageAmount"),
            "vehicle.capabilities.wifiConsumption.usageAmount",
        ),
        data_cap_amount_gb=_required_float(
            consumption.get("dataCapAmount"),
            "vehicle.capabilities.wifiConsumption.dataCapAmount",
        ),
        updated_at=_required_datetime(
            consumption.get("updatedAt"),
            "vehicle.capabilities.wifiConsumption.updatedAt",
        ),
    )


def parse_vehicle_preferences(
    data: Mapping[str, object],
) -> VehiclePreferences | None:
    """Parse nullable MIL/DTC maintenance-data sharing preferences."""

    vehicle = _optional_object(data.get("vehicle"), "vehicle")
    if vehicle is None:
        return None
    preferences = _optional_object(
        vehicle.get("preferences"),
        "vehicle.preferences",
    )
    if preferences is None:
        return None
    communication = _optional_object(
        preferences.get("communication"),
        "vehicle.preferences.communication",
    )
    if communication is None:
        return None
    mil_data_sharing = _optional_object(
        communication.get("milDataSharing"),
        "vehicle.preferences.communication.milDataSharing",
    )
    if mil_data_sharing is None:
        return None
    return VehiclePreferences(
        enabled=_optional_bool(mil_data_sharing.get("enabled")),
        text=_optional_bool(mil_data_sharing.get("text")),
        phone=_optional_bool(mil_data_sharing.get("phone")),
        email=_optional_bool(mil_data_sharing.get("email")),
    )


def parse_vehicle_subscriptions(
    data: Mapping[str, object],
    vin: str,
) -> VehicleSubscriptions | None:
    """Parse the vehicle subscription capability without app-level coercion."""

    vehicle = _optional_object(data.get("vehicle"), "vehicle")
    if vehicle is None:
        return None
    _required_graphql_string(vehicle.get("__typename"), "vehicle.__typename")

    capabilities = _optional_object(
        vehicle.get("capabilities"),
        "vehicle.capabilities",
    )
    if capabilities is None:
        return VehicleSubscriptions(vin=vin, subscriptions=None)
    _required_graphql_string(
        capabilities.get("__typename"),
        "vehicle.capabilities.__typename",
    )

    values = _list(
        capabilities.get("subscriptions"),
        "vehicle.capabilities.subscriptions",
    )
    subscriptions: list[VehicleSubscription | None] = []
    for index, raw_subscription in enumerate(values):
        if raw_subscription is None:
            subscriptions.append(None)
            continue
        path = f"vehicle.capabilities.subscriptions[{index}]"
        subscriptions.append(_parse_vehicle_subscription(_object(raw_subscription, path), path))

    return VehicleSubscriptions(vin=vin, subscriptions=tuple(subscriptions))


def _parse_vehicle_subscription(
    value: Mapping[str, object],
    path: str,
) -> VehicleSubscription:
    _required_graphql_string(value.get("__typename"), f"{path}.__typename")
    product_path = f"{path}.product"
    product = _parse_vehicle_subscription_product(
        _object(value.get("product"), product_path),
        product_path,
    )
    pending_order_path = f"{path}.pendingOrder"
    pending_order_value = _optional_object(value.get("pendingOrder"), pending_order_path)
    pending_order = (
        _parse_vehicle_subscription_pending_order(pending_order_value, pending_order_path)
        if pending_order_value is not None
        else None
    )
    return VehicleSubscription(
        subscription_id=_required_graphql_string(
            value.get("subscriptionId"),
            f"{path}.subscriptionId",
        ),
        subscription_service_type=_required_graphql_string(
            value.get("subscriptionServiceType"),
            f"{path}.subscriptionServiceType",
        ),
        purchase_type=_nullable_purchase_type(
            value.get("purchaseType"),
            f"{path}.purchaseType",
        ),
        product_type=_nullable_product_type(
            value.get("productType"),
            f"{path}.productType",
        ),
        next_billing_date=_nullable_aware_datetime(
            value.get("nextBillingDate"),
            f"{path}.nextBillingDate",
        ),
        goodwill_end_date=_nullable_aware_datetime(
            value.get("goodwillEndDate"),
            f"{path}.goodwillEndDate",
        ),
        goodwill_start_date=_nullable_aware_datetime(
            value.get("goodwillStartDate"),
            f"{path}.goodwillStartDate",
        ),
        grace_end_date=_nullable_aware_datetime(
            value.get("graceEndDate"),
            f"{path}.graceEndDate",
        ),
        subscription_start_date=_required_aware_datetime(
            value.get("subscriptionStartDate"),
            f"{path}.subscriptionStartDate",
        ),
        subscription_end_date=_nullable_aware_datetime(
            value.get("subscriptionEndDate"),
            f"{path}.subscriptionEndDate",
        ),
        is_active=_nullable_graphql_bool(value.get("isActive"), f"{path}.isActive"),
        np_subscription_price=_nullable_graphql_string(
            value.get("npSubscriptionPrice"),
            f"{path}.npSubscriptionPrice",
        ),
        product=product,
        pending_order=pending_order,
    )


def _parse_vehicle_subscription_product(
    value: Mapping[str, object],
    path: str,
) -> VehicleSubscriptionProduct:
    _required_graphql_string(value.get("__typename"), f"{path}.__typename")
    raw_services = _list(value.get("services"), f"{path}.services")
    services = tuple(
        None
        if raw_service is None
        else _required_graphql_string(raw_service, f"{path}.services[{index}]")
        for index, raw_service in enumerate(raw_services)
    )
    return VehicleSubscriptionProduct(
        product_id=_required_graphql_string(value.get("productId"), f"{path}.productId"),
        marketing_name=_required_graphql_string(
            value.get("marketingName"),
            f"{path}.marketingName",
        ),
        description=_required_graphql_string(
            value.get("description"),
            f"{path}.description",
        ),
        services=services,
    )


def _parse_vehicle_subscription_pending_order(
    value: Mapping[str, object],
    path: str,
) -> VehicleSubscriptionPendingOrder:
    _required_graphql_string(value.get("__typename"), f"{path}.__typename")
    return VehicleSubscriptionPendingOrder(
        pending_order_id=_required_graphql_string(
            value.get("pendingOrderId"),
            f"{path}.pendingOrderId",
        ),
        package_name=_required_graphql_string(
            value.get("packageName"),
            f"{path}.packageName",
        ),
        activation_date=_nullable_aware_datetime(
            value.get("activationDate"),
            f"{path}.activationDate",
        ),
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


def parse_vehicle_capabilities(data: Mapping[str, object], vin: str) -> VehicleCapabilities:
    """Parse connected services advertised for one vehicle."""

    vehicle = _object(data.get("vehicle"), "vehicle")
    capabilities = _optional_object(vehicle.get("capabilities"), "vehicle.capabilities")
    if capabilities is None:
        return VehicleCapabilities(vin, None, None, ())
    service_values = (
        _optional_list(
            capabilities.get("serviceCapability"),
            "vehicle.capabilities.serviceCapability",
        )
        or []
    )
    services: list[ServiceCapability] = []
    for index, value in enumerate(service_values):
        item = _object(value, f"vehicle.capabilities.serviceCapability[{index}]")
        services.append(
            ServiceCapability(
                type=_required_str(item.get("type"), "serviceCapability.type"),
                enabled=_required_bool(item.get("enabled"), "serviceCapability.enabled"),
                subscribed=_optional_bool(item.get("subscribed")),
            )
        )
    return VehicleCapabilities(
        vin=vin,
        telematics_program=_optional_str(capabilities.get("telematicsProgram")),
        enrollment_status=_optional_str(capabilities.get("status")),
        services=tuple(services),
        accessories_details=_parse_vehicle_accessories_details(
            capabilities.get("accessoriesDetails")
        ),
    )


def _parse_vehicle_accessories_details(value: object) -> VehicleAccessoriesDetails | None:
    details = _optional_object(value, "vehicle.capabilities.accessoriesDetails")
    if details is None:
        return None

    seat_heater = _optional_object(
        details.get("seatHeater"),
        "vehicle.capabilities.accessoriesDetails.seatHeater",
    )
    steering_heat = _optional_object(
        details.get("steeringHeat"),
        "vehicle.capabilities.accessoriesDetails.steeringHeat",
    )
    sun_roof = _optional_object(
        details.get("sunRoof"),
        "vehicle.capabilities.accessoriesDetails.sunRoof",
    )
    window_status = _optional_object(
        details.get("windowStatus"),
        "vehicle.capabilities.accessoriesDetails.windowStatus",
    )
    way_point = _optional_object(
        details.get("wayPoint"),
        "vehicle.capabilities.accessoriesDetails.wayPoint",
    )
    hvac_temperatures = _optional_object(
        details.get("hvacTemperatures"),
        "vehicle.capabilities.accessoriesDetails.hvacTemperatures",
    )

    return VehicleAccessoriesDetails(
        seat_heater=(
            _parse_seat_heater_capability(seat_heater) if seat_heater is not None else None
        ),
        steering_heat=(
            AccessoryCapability(enabled=_optional_bool(steering_heat.get("enabled")))
            if steering_heat is not None
            else None
        ),
        sun_roof=(
            SunRoofCapability(
                type=_optional_str(sun_roof.get("type")),
                enabled=_optional_bool(sun_roof.get("enabled")),
            )
            if sun_roof is not None
            else None
        ),
        window_status=(
            AccessoryCapability(enabled=_optional_bool(window_status.get("enabled")))
            if window_status is not None
            else None
        ),
        way_point=(
            WayPointCapability(
                enabled=_optional_bool(way_point.get("enabled")),
                max_number=_optional_int(way_point.get("maxNumber")),
            )
            if way_point is not None
            else None
        ),
        hvac_temperatures=(
            HvacTemperatureCapabilities(
                unit=_required_str(hvac_temperatures.get("unit"), "hvacTemperatures.unit"),
                default=_required_float(
                    hvac_temperatures.get("default"), "hvacTemperatures.default"
                ),
                minimum=_required_float(hvac_temperatures.get("min"), "hvacTemperatures.min"),
                maximum=_required_float(hvac_temperatures.get("max"), "hvacTemperatures.max"),
                resolution=_required_float(
                    hvac_temperatures.get("resolution"), "hvacTemperatures.resolution"
                ),
            )
            if hvac_temperatures is not None
            else None
        ),
    )


def _parse_seat_heater_capability(value: Mapping[str, object]) -> SeatHeaterCapability:
    accessories = _optional_object(
        value.get("accessories"),
        "vehicle.capabilities.accessoriesDetails.seatHeater.accessories",
    )
    parsed_accessories = None
    if accessories is not None:
        parsed_accessories = SeatHeaterAccessories(
            assistant_seat=_optional_str(accessories.get("assistantSeat")),
            driver_seat=_optional_str(accessories.get("driverSeat")),
            second_centre_seat=_optional_str(accessories.get("secondCentreSeat")),
            second_left_seat=_optional_str(accessories.get("secondLeftSeat")),
            second_right_seat=_optional_str(accessories.get("secondRightSeat")),
            third_left_seat=_optional_str(accessories.get("thirdLeftSeat")),
            third_right_seat=_optional_str(accessories.get("thirdRightSeat")),
        )
    return SeatHeaterCapability(
        enabled=_optional_bool(value.get("enabled")),
        accessories=parsed_accessories,
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


def _parse_week_days(value: object, path: str) -> tuple[WeekDay, ...]:
    values = _list(value, path)
    days: list[WeekDay] = []
    for item in values:
        raw = _required_str(item, path)
        try:
            days.append(WeekDay(raw))
        except ValueError:
            days.append(WeekDay.UNKNOWN_VALUE)
    return tuple(days)


def _optional_seat_option(value: object) -> SeatClimateOption | None:
    raw = _optional_str(value)
    if raw is None:
        return None
    try:
        return SeatClimateOption(raw)
    except ValueError:
        return SeatClimateOption.UNKNOWN_VALUE


def _optional_camera_position(value: object) -> CameraPosition | None:
    raw = _optional_str(value)
    if raw is None:
        return None
    try:
        return CameraPosition(raw)
    except ValueError:
        return CameraPosition.UNKNOWN_VALUE


def _optional_camera_service(value: object) -> CameraService | None:
    raw = _optional_str(value)
    if raw is None:
        return None
    try:
        return CameraService(raw)
    except ValueError:
        return CameraService.UNKNOWN_VALUE


def _optional_v2l_state(value: object) -> V2LState | None:
    raw = _optional_str(value)
    if raw is None:
        return None
    try:
        return V2LState(raw)
    except ValueError:
        return V2LState.UNKNOWN_VALUE


def _optional_on_off(value: object) -> bool | None:
    raw = _optional_str(value)
    if raw == "ON":
        return True
    if raw == "OFF":
        return False
    return None


def _nested_optional_str(value: object, key: str) -> str | None:
    item = _optional_object(value, key)
    return _optional_str(item.get(key)) if item is not None else None


def _object(value: object, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ResponseError(f"{path} is not an object")
    return value


def _optional_object(value: object, path: str) -> Mapping[str, object] | None:
    if value is None:
        return None
    return _object(value, path)


def _list(value: object, path: str) -> list[object]:
    if not isinstance(value, list):
        raise ResponseError(f"{path} is not a list")
    return value


def _optional_list(value: object, path: str) -> list[object] | None:
    if value is None:
        return None
    return _list(value, path)


def _required_str(value: object, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise ResponseError(f"{path} is not a non-empty string")
    return value


def _required_graphql_string(value: object, path: str) -> str:
    if not isinstance(value, str):
        raise ResponseError(f"{path} is not a string")
    return value


def _nullable_graphql_string(value: object, path: str) -> str | None:
    if value is None:
        return None
    return _required_graphql_string(value, path)


def _optional_str(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _required_bool(value: object, path: str) -> bool:
    if not isinstance(value, bool):
        raise ResponseError(f"{path} is not a boolean")
    return value


def _required_int(value: object, path: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ResponseError(f"{path} is not an integer")
    return value


def _optional_bool(value: object) -> bool | None:
    return value if isinstance(value, bool) else None


def _nullable_graphql_bool(value: object, path: str) -> bool | None:
    if value is None:
        return None
    return _required_bool(value, path)


def _optional_int(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _required_float(value: object, path: str) -> float:
    result = _optional_float(value)
    if result is None:
        raise ResponseError(f"{path} is not numeric")
    return result


def _required_distance_unit(value: object, path: str) -> DistanceUnit:
    raw = _required_str(value, path)
    try:
        return DistanceUnit(raw)
    except ValueError:
        return DistanceUnit.UNKNOWN_VALUE


def _optional_float(value: object) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


def _required_datetime(value: object, path: str) -> datetime:
    parsed = _optional_datetime(value)
    if parsed is None:
        raise ResponseError(f"{path} is not an ISO-8601 date-time")
    return parsed


def _required_aware_datetime(value: object, path: str) -> datetime:
    if not isinstance(value, str):
        raise ResponseError(f"{path} is not an ISO-8601 date-time with an offset")
    normalized = f"{value[:-1]}+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as error:
        raise ResponseError(f"{path} is not an ISO-8601 date-time with an offset") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ResponseError(f"{path} is not an ISO-8601 date-time with an offset")
    return parsed


def _nullable_aware_datetime(value: object, path: str) -> datetime | None:
    if value is None:
        return None
    return _required_aware_datetime(value, path)


def _optional_datetime(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _nullable_purchase_type(value: object, path: str) -> PurchaseType | str | None:
    if value is None:
        return None
    raw_value = _required_str(value, path)
    try:
        return PurchaseType(raw_value)
    except ValueError:
        return raw_value


def _nullable_product_type(value: object, path: str) -> ProductType | str | None:
    if value is None:
        return None
    raw_value = _required_str(value, path)
    try:
        return ProductType(raw_value)
    except ValueError:
        return raw_value
