from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from enum import StrEnum

from .exceptions import ResponseError
from .models import DistanceUnit, TemperatureUnit
from .navigation_inputs import (
    NotificationIntervalUnit,
    RecalculatedWaypointType,
    RouteStatus,
)
from .navigation_models import (
    EVWaypoint,
    EVWaypointErrorDetails,
    EVWaypointLimitReachedError,
    EVWaypointMinimumRequirementNotMetError,
    EVWaypointResult,
    EVWaypointRoute,
    EVWaypointRouteType,
    EVWaypointStatus,
    EVWaypointUnableToCompleteRouteError,
    Journey,
    JourneyWaypoint,
    MissingBatteryDetailsErrorDetails,
    NavigationAddress,
    NavigationCoordinate,
    NavigationDistance,
    NavigationNotificationInterval,
    NavigationRouteWaypoint,
    NavigationTemperature,
    NoChargingStationWithinRangeErrorDetails,
    PlannedRoute,
    PointOfInterestDestination,
    PointOfInterestDestinationFolder,
    RouteHistoryEntry,
    SavedTJunctionLocation,
    TJunctionLocations,
    UnableToCompleteSubStepErrorDetails,
    UnsavedTJunctionLocation,
    VehicleJourneys,
    VehiclePlannedRoutes,
    VehiclePointOfInterestDestinations,
    VehicleRoutesHistory,
)


def parse_vehicle_journeys(data: Mapping[str, object]) -> VehicleJourneys | None:
    """Parse a vehicle's nullable journey collection."""

    vehicle = _optional_object(data.get("vehicle"), "vehicle")
    if vehicle is None:
        return None
    if "journeys" not in vehicle:
        return None
    raw_journeys = _nullable_list(vehicle.get("journeys"), "vehicle.journeys")
    if raw_journeys is None:
        return VehicleJourneys(None)
    journeys: list[Journey | None] = []
    for index, raw_journey in enumerate(raw_journeys):
        if raw_journey is None:
            journeys.append(None)
            continue
        journey = _object(raw_journey, f"vehicle.journeys[{index}]")
        raw_waypoints = _nullable_list(
            journey.get("waypoints"),
            f"vehicle.journeys[{index}].waypoints",
        )
        if raw_waypoints is None:
            journeys.append(Journey(None))
            continue
        waypoints: list[JourneyWaypoint | None] = []
        for waypoint_index, raw_waypoint in enumerate(raw_waypoints):
            if raw_waypoint is None:
                waypoints.append(None)
                continue
            path = f"vehicle.journeys[{index}].waypoints[{waypoint_index}]"
            waypoint = _object(raw_waypoint, path)
            waypoints.append(
                JourneyWaypoint(
                    id=_nullable_string(waypoint.get("id"), f"{path}.id"),
                    name=_nullable_string(waypoint.get("name"), f"{path}.name"),
                    address=_parse_optional_address(waypoint.get("address"), f"{path}.address"),
                    coordinate=_parse_optional_coordinate(
                        waypoint.get("coordinate"),
                        f"{path}.coordinate",
                    ),
                    phone_number=_nullable_string(
                        waypoint.get("phoneNumber"),
                        f"{path}.phoneNumber",
                    ),
                )
            )
        journeys.append(Journey(tuple(waypoints)))
    return VehicleJourneys(tuple(journeys))


def parse_vehicle_planned_routes(
    data: Mapping[str, object],
) -> VehiclePlannedRoutes | None:
    """Parse a vehicle's nullable saved planned routes."""

    vehicle = _optional_object(data.get("vehicle"), "vehicle")
    if vehicle is None:
        return None
    if "plannedRoutes" not in vehicle:
        return None
    raw_routes = _nullable_list(vehicle.get("plannedRoutes"), "vehicle.plannedRoutes")
    if raw_routes is None:
        return VehiclePlannedRoutes(None)
    routes: list[PlannedRoute | None] = []
    for index, raw_route in enumerate(raw_routes):
        if raw_route is None:
            routes.append(None)
            continue
        path = f"vehicle.plannedRoutes[{index}]"
        route = _object(raw_route, path)
        routes.append(
            PlannedRoute(
                id=_nullable_string(route.get("id"), f"{path}.id"),
                name=_nullable_string(route.get("name"), f"{path}.name"),
                estimated_time_of_departure=_nullable_datetime(
                    route.get("estimatedTimeOfDeparture"),
                    f"{path}.estimatedTimeOfDeparture",
                ),
                estimated_time_of_arrival=_nullable_datetime(
                    route.get("estimatedTimeOfArrival"),
                    f"{path}.estimatedTimeOfArrival",
                ),
                distance=_parse_optional_distance(route.get("distance"), f"{path}.distance"),
                temperature=_parse_optional_temperature(
                    route.get("temperature"),
                    f"{path}.temperature",
                ),
                routes=_parse_navigation_route_waypoints(
                    route.get("routes"),
                    f"{path}.routes",
                ),
                avoid_highway=_nullable_bool(route.get("avoidHighway"), f"{path}.avoidHighway"),
                avoid_tolls=_nullable_bool(route.get("avoidTolls"), f"{path}.avoidTolls"),
                avoid_ferries=_nullable_bool(route.get("avoidFerries"), f"{path}.avoidFerries"),
                should_recalculate_route=_nullable_bool(
                    route.get("shouldRecalculateRoute"),
                    f"{path}.shouldRecalculateRoute",
                ),
                should_enable_notification=_nullable_bool(
                    route.get("shouldEnableNotification"),
                    f"{path}.shouldEnableNotification",
                ),
                notification_interval=_parse_optional_notification_interval(
                    route.get("notificationInterval"),
                    f"{path}.notificationInterval",
                ),
                arrival_flag=_nullable_bool(route.get("arrivalFlag"), f"{path}.arrivalFlag"),
                departure_flag=_nullable_bool(
                    route.get("departureFlag"),
                    f"{path}.departureFlag",
                ),
            )
        )
    return VehiclePlannedRoutes(tuple(routes))


def parse_vehicle_routes_history(
    data: Mapping[str, object],
) -> VehicleRoutesHistory | None:
    """Parse a vehicle's nullable route-history collection."""

    vehicle = _optional_object(data.get("vehicle"), "vehicle")
    if vehicle is None:
        return None
    if "routeHistory" not in vehicle:
        return None
    raw_entries = _nullable_list(vehicle.get("routeHistory"), "vehicle.routeHistory")
    if raw_entries is None:
        return VehicleRoutesHistory(None)
    entries: list[RouteHistoryEntry | None] = []
    for index, raw_entry in enumerate(raw_entries):
        if raw_entry is None:
            entries.append(None)
            continue
        path = f"vehicle.routeHistory[{index}]"
        entry = _object(raw_entry, path)
        entries.append(
            RouteHistoryEntry(
                id=_nullable_string(entry.get("id"), f"{path}.id"),
                name=_nullable_string(entry.get("name"), f"{path}.name"),
                estimated_time_of_departure=_nullable_datetime(
                    entry.get("estimatedTimeOfDeparture"),
                    f"{path}.estimatedTimeOfDeparture",
                ),
                estimated_time_of_arrival=_nullable_datetime(
                    entry.get("estimatedTimeOfArrival"),
                    f"{path}.estimatedTimeOfArrival",
                ),
                status=_nullable_enum(entry.get("status"), RouteStatus, f"{path}.status"),
                distance=_parse_optional_distance(entry.get("distance"), f"{path}.distance"),
                temperature=_parse_optional_temperature(
                    entry.get("temperature"),
                    f"{path}.temperature",
                ),
                routes=_parse_navigation_route_waypoints(
                    entry.get("routes"),
                    f"{path}.routes",
                ),
                arrival_flag=_nullable_bool(entry.get("arrivalFlag"), f"{path}.arrivalFlag"),
                departure_flag=_nullable_bool(
                    entry.get("departureFlag"),
                    f"{path}.departureFlag",
                ),
            )
        )
    return VehicleRoutesHistory(tuple(entries))


def parse_vehicle_point_of_interest_destinations(
    data: Mapping[str, object],
) -> VehiclePointOfInterestDestinations | None:
    """Parse a vehicle's nullable point-of-interest folders."""

    vehicle = _optional_object(data.get("vehicle"), "vehicle")
    if vehicle is None:
        return None
    if "pointOfInterestDestination" not in vehicle:
        return None
    container = _optional_object(
        vehicle.get("pointOfInterestDestination"),
        "vehicle.pointOfInterestDestination",
    )
    if container is None:
        return None
    raw_folders = _nullable_list(
        container.get("folders"),
        "vehicle.pointOfInterestDestination.folders",
    )
    if raw_folders is None:
        return VehiclePointOfInterestDestinations(None)
    folders: list[PointOfInterestDestinationFolder | None] = []
    for index, raw_folder in enumerate(raw_folders):
        if raw_folder is None:
            folders.append(None)
            continue
        path = f"vehicle.pointOfInterestDestination.folders[{index}]"
        folder = _object(raw_folder, path)
        raw_destinations = _nullable_list(folder.get("destinations"), f"{path}.destinations")
        destinations: tuple[PointOfInterestDestination | None, ...] | None = None
        if raw_destinations is not None:
            parsed_destinations: list[PointOfInterestDestination | None] = []
            for destination_index, raw_destination in enumerate(raw_destinations):
                if raw_destination is None:
                    parsed_destinations.append(None)
                    continue
                destination_path = f"{path}.destinations[{destination_index}]"
                destination = _object(raw_destination, destination_path)
                parsed_destinations.append(
                    PointOfInterestDestination(
                        id=_nullable_string(
                            destination.get("id"),
                            f"{destination_path}.id",
                        ),
                        phone_number=_nullable_string(
                            destination.get("phoneNumber"),
                            f"{destination_path}.phoneNumber",
                        ),
                        name=_nullable_string(
                            destination.get("name"),
                            f"{destination_path}.name",
                        ),
                        address=_parse_optional_address(
                            destination.get("address"),
                            f"{destination_path}.address",
                        ),
                        coordinate=_parse_optional_coordinate(
                            destination.get("coordinate"),
                            f"{destination_path}.coordinate",
                        ),
                    )
                )
            destinations = tuple(parsed_destinations)
        folders.append(
            PointOfInterestDestinationFolder(
                folder_name=_nullable_string(folder.get("folderName"), f"{path}.folderName"),
                destinations=destinations,
            )
        )
    return VehiclePointOfInterestDestinations(tuple(folders))


def parse_t_junction_locations(data: Mapping[str, object]) -> TJunctionLocations | None:
    """Parse saved and unsaved T-junction camera locations."""

    vehicle = _optional_object(data.get("vehicle"), "vehicle")
    if vehicle is None:
        return None
    if "unsavedTJunctionLocations" not in vehicle and "savedTJunctionLocations" not in vehicle:
        return None
    raw_unsaved = _list(
        vehicle.get("unsavedTJunctionLocations"),
        "vehicle.unsavedTJunctionLocations",
    )
    raw_saved = _list(
        vehicle.get("savedTJunctionLocations"),
        "vehicle.savedTJunctionLocations",
    )
    unsaved: list[UnsavedTJunctionLocation] = []
    for index, raw_location in enumerate(raw_unsaved):
        path = f"vehicle.unsavedTJunctionLocations[{index}]"
        location = _object(raw_location, path)
        unsaved.append(
            UnsavedTJunctionLocation(
                id=_string(location.get("id"), f"{path}.id"),
                latitude=_float(location.get("latitude"), f"{path}.latitude"),
                longitude=_float(location.get("longitude"), f"{path}.longitude"),
                direction=_float(location.get("direction"), f"{path}.direction"),
                launch_date=_datetime(location.get("launchDate"), f"{path}.launchDate"),
                address=_parse_optional_address(location.get("address"), f"{path}.address"),
            )
        )
    saved: list[SavedTJunctionLocation] = []
    for index, raw_location in enumerate(raw_saved):
        path = f"vehicle.savedTJunctionLocations[{index}]"
        location = _object(raw_location, path)
        saved.append(
            SavedTJunctionLocation(
                id=_string(location.get("id"), f"{path}.id"),
                latitude=_float(location.get("latitude"), f"{path}.latitude"),
                longitude=_float(location.get("longitude"), f"{path}.longitude"),
                direction=_float(location.get("direction"), f"{path}.direction"),
                location_name=_string(
                    location.get("locationName"),
                    f"{path}.locationName",
                ),
                address=_parse_optional_address(location.get("address"), f"{path}.address"),
            )
        )
    return TJunctionLocations(tuple(unsaved), tuple(saved))


def parse_vehicle_ev_waypoints(data: Mapping[str, object]) -> EVWaypointResult | None:
    """Parse a successful EV route calculation or its typed error branch."""

    vehicle = _optional_object(data.get("vehicle"), "vehicle")
    if vehicle is None:
        return None
    result = _optional_object(vehicle.get("evWaypoints"), "vehicle.evWaypoints")
    if result is None:
        return None
    typename = _string(result.get("__typename"), "vehicle.evWaypoints.__typename")
    if typename == "EVWaypoint":
        return _parse_ev_waypoint(result)
    if typename == "MinimumRequirementNotMetError":
        return EVWaypointMinimumRequirementNotMetError(
            _string(result.get("message"), "vehicle.evWaypoints.message")
        )
    if typename == "LimitReachedError":
        return EVWaypointLimitReachedError(
            _string(result.get("message"), "vehicle.evWaypoints.message")
        )
    if typename == "UnableToCompleteRouteError":
        return EVWaypointUnableToCompleteRouteError(
            reason=_string(result.get("reason"), "vehicle.evWaypoints.reason"),
            message=_string(result.get("message"), "vehicle.evWaypoints.message"),
            details=_parse_ev_waypoint_error_details(result.get("details")),
        )
    raise ResponseError(f"Unsupported vehicle.evWaypoints type: {typename}")


def _parse_ev_waypoint(value: Mapping[str, object]) -> EVWaypoint:
    raw_routes = _nullable_list(value.get("routes"), "vehicle.evWaypoints.routes")
    routes: tuple[EVWaypointRoute | None, ...] | None = None
    if raw_routes is not None:
        parsed_routes: list[EVWaypointRoute | None] = []
        for index, raw_route in enumerate(raw_routes):
            if raw_route is None:
                parsed_routes.append(None)
                continue
            path = f"vehicle.evWaypoints.routes[{index}]"
            route = _object(raw_route, path)
            parsed_routes.append(
                EVWaypointRoute(
                    name=_nullable_string(route.get("name"), f"{path}.name"),
                    arrival_time=_nullable_datetime(
                        route.get("arrivalTime"),
                        f"{path}.arrivalTime",
                    ),
                    charging_time_in_seconds=_nullable_int(
                        route.get("chargingTimeInSeconds"),
                        f"{path}.chargingTimeInSeconds",
                    ),
                    level=_nullable_int(route.get("level"), f"{path}.level"),
                    type=_nullable_enum(route.get("type"), EVWaypointRouteType, f"{path}.type"),
                    address=_parse_optional_address(route.get("address"), f"{path}.address"),
                    location=_parse_optional_coordinate(
                        route.get("location"),
                        f"{path}.location",
                    ),
                    status=_nullable_enum(
                        route.get("status"),
                        EVWaypointStatus,
                        f"{path}.status",
                    ),
                    charging_output=_nullable_int(
                        route.get("chargingOutput"),
                        f"{path}.chargingOutput",
                    ),
                )
            )
        routes = tuple(parsed_routes)
    return EVWaypoint(
        departure_time=_nullable_datetime(
            value.get("departureTime"),
            "vehicle.evWaypoints.departureTime",
        ),
        arrival_time=_nullable_datetime(
            value.get("arrivalTime"),
            "vehicle.evWaypoints.arrivalTime",
        ),
        total_charging_time_in_seconds=_nullable_int(
            value.get("totalChargingTimeInSeconds"),
            "vehicle.evWaypoints.totalChargingTimeInSeconds",
        ),
        total_travel_time_in_seconds=_nullable_int(
            value.get("totalTravelTimeInSeconds"),
            "vehicle.evWaypoints.totalTravelTimeInSeconds",
        ),
        total_distance=_parse_optional_distance(
            value.get("totalDistance"),
            "vehicle.evWaypoints.totalDistance",
        ),
        routes=routes,
    )


def _parse_ev_waypoint_error_details(value: object) -> EVWaypointErrorDetails | None:
    details = _optional_object(value, "vehicle.evWaypoints.details")
    if details is None:
        return None
    typename = _string(details.get("__typename"), "vehicle.evWaypoints.details.__typename")
    if typename == "MissingBatteryDetailsErrorDetails":
        return MissingBatteryDetailsErrorDetails(
            battery_capacity=_nullable_string(
                details.get("batteryCapacity"),
                "vehicle.evWaypoints.details.batteryCapacity",
            ),
            starting_battery_level=_nullable_string(
                details.get("startingBatteryLevel"),
                "vehicle.evWaypoints.details.startingBatteryLevel",
            ),
        )
    if typename == "NoChargingStationWithinRangeErrorDetails":
        return NoChargingStationWithinRangeErrorDetails(
            center=_nullable_string(details.get("center"), "vehicle.evWaypoints.details.center"),
            radius=_nullable_string(details.get("radius"), "vehicle.evWaypoints.details.radius"),
            charging_connectors=_nullable_string(
                details.get("chargingConnectors"),
                "vehicle.evWaypoints.details.chargingConnectors",
            ),
            min_power=_nullable_string(
                details.get("minPower"),
                "vehicle.evWaypoints.details.minPower",
            ),
        )
    if typename == "UnableToCompleteSubStepErrorDetails":
        return UnableToCompleteSubStepErrorDetails(
            start=_nullable_string(details.get("start"), "vehicle.evWaypoints.details.start"),
            end=_nullable_string(details.get("end"), "vehicle.evWaypoints.details.end"),
            distance=_nullable_string(
                details.get("distance"),
                "vehicle.evWaypoints.details.distance",
            ),
            speed=_nullable_string(details.get("speed"), "vehicle.evWaypoints.details.speed"),
            slope=_nullable_string(details.get("slope"), "vehicle.evWaypoints.details.slope"),
            starting_battery=_nullable_string(
                details.get("startingBattery"),
                "vehicle.evWaypoints.details.startingBattery",
            ),
            battery_capacity=_nullable_string(
                details.get("batteryCapacity"),
                "vehicle.evWaypoints.details.batteryCapacity",
            ),
            battery_consumption=_nullable_string(
                details.get("batteryConsumption"),
                "vehicle.evWaypoints.details.batteryConsumption",
            ),
            soc_after_charging_near_start=_nullable_string(
                details.get("socAfterChargingNearStart"),
                "vehicle.evWaypoints.details.socAfterChargingNearStart",
            ),
            minimum_battery=_nullable_string(
                details.get("minimumBattery"),
                "vehicle.evWaypoints.details.minimumBattery",
            ),
            charging_station_max_power=_nullable_string(
                details.get("chargingStationMaxPower"),
                "vehicle.evWaypoints.details.chargingStationMaxPower",
            ),
        )
    raise ResponseError(f"Unsupported vehicle.evWaypoints.details type: {typename}")


def _parse_navigation_route_waypoints(
    value: object,
    path: str,
) -> tuple[NavigationRouteWaypoint | None, ...] | None:
    raw_routes = _nullable_list(value, path)
    if raw_routes is None:
        return None
    routes: list[NavigationRouteWaypoint | None] = []
    for index, raw_route in enumerate(raw_routes):
        if raw_route is None:
            routes.append(None)
            continue
        item_path = f"{path}[{index}]"
        route = _object(raw_route, item_path)
        routes.append(
            NavigationRouteWaypoint(
                name=_nullable_string(route.get("name"), f"{item_path}.name"),
                phone_number=_nullable_string(
                    route.get("phoneNumber"),
                    f"{item_path}.phoneNumber",
                ),
                address=_parse_optional_address(
                    route.get("address"),
                    f"{item_path}.address",
                ),
                location=_parse_optional_coordinate(
                    route.get("location"),
                    f"{item_path}.location",
                ),
                recalculated_waypoint_type=_nullable_enum(
                    route.get("recalculatedWaypointType"),
                    RecalculatedWaypointType,
                    f"{item_path}.recalculatedWaypointType",
                ),
                charging_output=_nullable_int(
                    route.get("chargingOutput"),
                    f"{item_path}.chargingOutput",
                ),
            )
        )
    return tuple(routes)


def _parse_optional_address(value: object, path: str) -> NavigationAddress | None:
    address = _optional_object(value, path)
    if address is None:
        return None
    return NavigationAddress(
        address1=_nullable_string(address.get("address1"), f"{path}.address1"),
        address2=_nullable_string(address.get("address2"), f"{path}.address2"),
        city=_nullable_string(address.get("city"), f"{path}.city"),
        state=_nullable_string(address.get("state"), f"{path}.state"),
        postal_code=_nullable_string(address.get("postalCode"), f"{path}.postalCode"),
        country=_nullable_string(address.get("country"), f"{path}.country"),
    )


def _parse_optional_coordinate(value: object, path: str) -> NavigationCoordinate | None:
    coordinate = _optional_object(value, path)
    if coordinate is None:
        return None
    return NavigationCoordinate(
        latitude=_nullable_float(coordinate.get("latitude"), f"{path}.latitude"),
        longitude=_nullable_float(coordinate.get("longitude"), f"{path}.longitude"),
    )


def _parse_optional_distance(value: object, path: str) -> NavigationDistance | None:
    distance = _optional_object(value, path)
    if distance is None:
        return None
    return NavigationDistance(
        value=_int(distance.get("value"), f"{path}.value"),
        unit=_enum(distance.get("unit"), DistanceUnit, f"{path}.unit"),
    )


def _parse_optional_temperature(value: object, path: str) -> NavigationTemperature | None:
    temperature = _optional_object(value, path)
    if temperature is None:
        return None
    return NavigationTemperature(
        value=_float(temperature.get("value"), f"{path}.value"),
        unit=_enum(temperature.get("unit"), TemperatureUnit, f"{path}.unit"),
    )


def _parse_optional_notification_interval(
    value: object,
    path: str,
) -> NavigationNotificationInterval | None:
    interval = _optional_object(value, path)
    if interval is None:
        return None
    return NavigationNotificationInterval(
        value=_nullable_int(interval.get("value"), f"{path}.value"),
        unit=_nullable_enum(interval.get("unit"), NotificationIntervalUnit, f"{path}.unit"),
    )


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


def _nullable_list(value: object, path: str) -> list[object] | None:
    if value is None:
        return None
    return _list(value, path)


def _string(value: object, path: str) -> str:
    if not isinstance(value, str):
        raise ResponseError(f"{path} is not a string")
    return value


def _nullable_string(value: object, path: str) -> str | None:
    if value is None:
        return None
    return _string(value, path)


def _int(value: object, path: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ResponseError(f"{path} is not an integer")
    return value


def _nullable_int(value: object, path: str) -> int | None:
    if value is None:
        return None
    return _int(value, path)


def _float(value: object, path: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ResponseError(f"{path} is not numeric")
    return float(value)


def _nullable_float(value: object, path: str) -> float | None:
    if value is None:
        return None
    return _float(value, path)


def _nullable_bool(value: object, path: str) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ResponseError(f"{path} is not a boolean")
    return value


def _enum[EnumT: StrEnum](value: object, enum_type: type[EnumT], path: str) -> EnumT:
    raw_value = _string(value, path)
    try:
        return enum_type(raw_value)
    except ValueError:
        unknown_value = getattr(enum_type, "UNKNOWN_VALUE", None)
        if isinstance(unknown_value, enum_type):
            return unknown_value
        raise ResponseError(f"{path} has an unsupported value: {raw_value}") from None


def _nullable_enum[EnumT: StrEnum](
    value: object,
    enum_type: type[EnumT],
    path: str,
) -> EnumT | None:
    if value is None:
        return None
    return _enum(value, enum_type, path)


def _datetime(value: object, path: str) -> datetime:
    raw_value = _string(value, path)
    normalized = f"{raw_value[:-1]}+00:00" if raw_value.endswith("Z") else raw_value
    try:
        result = datetime.fromisoformat(normalized)
    except ValueError as error:
        raise ResponseError(f"{path} is not an ISO-8601 date-time") from error
    if result.tzinfo is None or result.utcoffset() is None:
        raise ResponseError(f"{path} is not an ISO-8601 date-time with an offset")
    return result


def _nullable_datetime(value: object, path: str) -> datetime | None:
    if value is None:
        return None
    return _datetime(value, path)
