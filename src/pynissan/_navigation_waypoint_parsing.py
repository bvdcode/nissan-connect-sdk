from __future__ import annotations

from collections.abc import Mapping

from ._navigation_value_parsing import (
    _enum,
    _float,
    _int,
    _nullable_datetime,
    _nullable_enum,
    _nullable_float,
    _nullable_int,
    _nullable_list,
    _nullable_string,
    _object,
    _optional_object,
    _string,
)
from .exceptions import ResponseError
from .models import DistanceUnit, TemperatureUnit
from .navigation_inputs import (
    NotificationIntervalUnit,
    RecalculatedWaypointType,
)
from .navigation_models import (
    EVWaypoint,
    EVWaypointErrorDetails,
    EVWaypointRoute,
    EVWaypointRouteType,
    EVWaypointStatus,
    MissingBatteryDetailsErrorDetails,
    NavigationAddress,
    NavigationCoordinate,
    NavigationDistance,
    NavigationNotificationInterval,
    NavigationRouteWaypoint,
    NavigationTemperature,
    NoChargingStationWithinRangeErrorDetails,
    UnableToCompleteSubStepErrorDetails,
)


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
