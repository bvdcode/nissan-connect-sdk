from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .models import DistanceUnit, TemperatureUnit
from .navigation_inputs import (
    NotificationIntervalUnit,
    RecalculatedWaypointType,
    RouteStatus,
)


@dataclass(frozen=True, slots=True)
class NavigationAddress:
    """Nullable address fields returned for a navigation destination."""

    address1: str | None
    address2: str | None
    city: str | None
    state: str | None
    postal_code: str | None
    country: str | None


@dataclass(frozen=True, slots=True)
class NavigationCoordinate:
    """Nullable coordinates returned for a navigation destination."""

    latitude: float | None
    longitude: float | None


@dataclass(frozen=True, slots=True)
class NavigationDistance:
    """A non-null distance value and unit within an optional response object."""

    value: int
    unit: DistanceUnit


@dataclass(frozen=True, slots=True)
class NavigationTemperature:
    """A non-null temperature value and unit within an optional response object."""

    value: float
    unit: TemperatureUnit


@dataclass(frozen=True, slots=True)
class NavigationNotificationInterval:
    """Nullable route-notification interval fields."""

    value: int | None
    unit: NotificationIntervalUnit | None


@dataclass(frozen=True, slots=True)
class JourneyWaypoint:
    """One nullable-field waypoint returned in the vehicle journey list."""

    id: str | None
    name: str | None
    address: NavigationAddress | None
    coordinate: NavigationCoordinate | None
    phone_number: str | None


@dataclass(frozen=True, slots=True)
class Journey:
    """One journey and its nullable waypoint list."""

    waypoints: tuple[JourneyWaypoint | None, ...] | None


@dataclass(frozen=True, slots=True)
class VehicleJourneys:
    """The nullable journey collection exposed by a connected vehicle."""

    journeys: tuple[Journey | None, ...] | None


@dataclass(frozen=True, slots=True)
class NavigationRouteWaypoint:
    """One waypoint returned in a planned route or route-history entry."""

    name: str | None
    phone_number: str | None
    address: NavigationAddress | None
    location: NavigationCoordinate | None
    recalculated_waypoint_type: RecalculatedWaypointType | None
    charging_output: int | None


@dataclass(frozen=True, slots=True)
class PlannedRoute:
    """One saved vehicle route with upstream nullability preserved."""

    id: str | None
    name: str | None
    estimated_time_of_departure: datetime | None
    estimated_time_of_arrival: datetime | None
    distance: NavigationDistance | None
    temperature: NavigationTemperature | None
    routes: tuple[NavigationRouteWaypoint | None, ...] | None
    avoid_highway: bool | None
    avoid_tolls: bool | None
    avoid_ferries: bool | None
    should_recalculate_route: bool | None
    should_enable_notification: bool | None
    notification_interval: NavigationNotificationInterval | None
    arrival_flag: bool | None
    departure_flag: bool | None


@dataclass(frozen=True, slots=True)
class VehiclePlannedRoutes:
    """The nullable saved-route collection exposed by an electric vehicle."""

    planned_routes: tuple[PlannedRoute | None, ...] | None


@dataclass(frozen=True, slots=True)
class RouteHistoryEntry:
    """One route-history entry returned for an electric AVK2 vehicle."""

    id: str | None
    name: str | None
    estimated_time_of_departure: datetime | None
    estimated_time_of_arrival: datetime | None
    status: RouteStatus | None
    distance: NavigationDistance | None
    temperature: NavigationTemperature | None
    routes: tuple[NavigationRouteWaypoint | None, ...] | None
    arrival_flag: bool | None
    departure_flag: bool | None


@dataclass(frozen=True, slots=True)
class VehicleRoutesHistory:
    """The nullable route-history collection exposed by an electric AVK2 vehicle."""

    route_history: tuple[RouteHistoryEntry | None, ...] | None


@dataclass(frozen=True, slots=True)
class PointOfInterestDestination:
    """One nullable-field point-of-interest destination."""

    id: str | None
    phone_number: str | None
    name: str | None
    address: NavigationAddress | None
    coordinate: NavigationCoordinate | None


@dataclass(frozen=True, slots=True)
class PointOfInterestDestinationFolder:
    """One point-of-interest folder and its nullable destination list."""

    folder_name: str | None
    destinations: tuple[PointOfInterestDestination | None, ...] | None


@dataclass(frozen=True, slots=True)
class VehiclePointOfInterestDestinations:
    """The nullable point-of-interest folders exposed by a connected vehicle."""

    folders: tuple[PointOfInterestDestinationFolder | None, ...] | None


@dataclass(frozen=True, slots=True)
class UnsavedTJunctionLocation:
    """One unsaved T-Junction location returned by an EVO vehicle."""

    id: str
    latitude: float
    longitude: float
    direction: float
    launch_date: datetime
    address: NavigationAddress | None


@dataclass(frozen=True, slots=True)
class SavedTJunctionLocation:
    """One saved T-Junction location returned by an EVO vehicle."""

    id: str
    latitude: float
    longitude: float
    direction: float
    location_name: str
    address: NavigationAddress | None


@dataclass(frozen=True, slots=True)
class TJunctionLocations:
    """The non-null saved and unsaved T-Junction location collections."""

    unsaved_t_junction_locations: tuple[UnsavedTJunctionLocation, ...]
    saved_t_junction_locations: tuple[SavedTJunctionLocation, ...]


class EVWaypointStatus(StrEnum):
    """Availability status returned for an EV route waypoint."""

    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"
    UNKNOWN_VALUE = "UNKNOWN__"


class EVWaypointRouteType(StrEnum):
    """Role of a waypoint in an EV route calculation."""

    ORIGIN = "ORIGIN"
    STOP = "STOP"
    CHARGING_STATION = "CHARGING_STATION"
    DESTINATION = "DESTINATION"
    UNKNOWN_VALUE = "UNKNOWN__"


@dataclass(frozen=True, slots=True)
class EVWaypointRoute:
    """One nullable-field waypoint in a calculated EV route."""

    name: str | None
    arrival_time: datetime | None
    charging_time_in_seconds: int | None
    level: int | None
    type: EVWaypointRouteType | None
    address: NavigationAddress | None
    location: NavigationCoordinate | None
    status: EVWaypointStatus | None
    charging_output: int | None


@dataclass(frozen=True, slots=True)
class EVWaypoint:
    """A successful EV route calculation."""

    departure_time: datetime | None
    arrival_time: datetime | None
    total_charging_time_in_seconds: int | None
    total_travel_time_in_seconds: int | None
    total_distance: NavigationDistance | None
    routes: tuple[EVWaypointRoute | None, ...] | None


@dataclass(frozen=True, slots=True)
class MissingBatteryDetailsErrorDetails:
    """Battery fields missing from an EV route request."""

    battery_capacity: str | None
    starting_battery_level: str | None


@dataclass(frozen=True, slots=True)
class NoChargingStationWithinRangeErrorDetails:
    """Charging-station search values that prevented EV route completion."""

    center: str | None
    radius: str | None
    charging_connectors: str | None
    min_power: str | None


@dataclass(frozen=True, slots=True)
class UnableToCompleteSubStepErrorDetails:
    """Route sub-step values that prevented EV route completion."""

    start: str | None
    end: str | None
    distance: str | None
    speed: str | None
    slope: str | None
    starting_battery: str | None
    battery_capacity: str | None
    battery_consumption: str | None
    soc_after_charging_near_start: str | None
    minimum_battery: str | None
    charging_station_max_power: str | None


type EVWaypointErrorDetails = (
    MissingBatteryDetailsErrorDetails
    | NoChargingStationWithinRangeErrorDetails
    | UnableToCompleteSubStepErrorDetails
)


@dataclass(frozen=True, slots=True)
class EVWaypointMinimumRequirementNotMetError:
    """A failed EV route calculation whose minimum requirements were not met."""

    message: str


@dataclass(frozen=True, slots=True)
class EVWaypointLimitReachedError:
    """A failed EV route calculation that exceeded a service limit."""

    message: str


@dataclass(frozen=True, slots=True)
class EVWaypointUnableToCompleteRouteError:
    """A failed EV route calculation with an optional typed detail branch."""

    reason: str
    message: str
    details: EVWaypointErrorDetails | None


type EVWaypointResult = (
    EVWaypoint
    | EVWaypointMinimumRequirementNotMetError
    | EVWaypointLimitReachedError
    | EVWaypointUnableToCompleteRouteError
)
