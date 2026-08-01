from __future__ import annotations

from collections.abc import Mapping

from ._navigation_value_parsing import (
    _datetime,
    _float,
    _list,
    _nullable_bool,
    _nullable_datetime,
    _nullable_enum,
    _nullable_list,
    _nullable_string,
    _object,
    _optional_object,
    _string,
)
from ._navigation_waypoint_parsing import (
    _parse_ev_waypoint,
    _parse_ev_waypoint_error_details,
    _parse_navigation_route_waypoints,
    _parse_optional_address,
    _parse_optional_coordinate,
    _parse_optional_distance,
    _parse_optional_notification_interval,
    _parse_optional_temperature,
)
from .exceptions import ResponseError
from .navigation_inputs import (
    RouteStatus,
)
from .navigation_models import (
    EVWaypointLimitReachedError,
    EVWaypointMinimumRequirementNotMetError,
    EVWaypointResult,
    EVWaypointUnableToCompleteRouteError,
    Journey,
    JourneyWaypoint,
    PlannedRoute,
    PointOfInterestDestination,
    PointOfInterestDestinationFolder,
    RouteHistoryEntry,
    SavedTJunctionLocation,
    TJunctionLocations,
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
