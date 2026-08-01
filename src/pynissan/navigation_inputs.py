from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from .common_inputs import AddressInput, CoordinateInput, address_input, coordinate_input
from .graphql_input import (
    UNSET,
    UnsetType,
    optional_input_fields,
    serialize_datetime,
    serialize_enum,
)
from .models import DistanceUnit, TemperatureUnit


class NavigationDataSource(StrEnum):
    """Optional telematics routing backend selected by current MyNISSAN clients."""

    KMR = "KMR"


class PointOfInterestFolder(StrEnum):
    """Destination folder accepted by point-of-interest mutations."""

    FAVORITES = "FAVORITES"
    RECENTS = "RECENTS"
    UNKNOWN_VALUE = "UNKNOWN__"


class PointOfInterestFolderFilter(StrEnum):
    """Destination folder filter accepted by point-of-interest reads."""

    FAVORITES = "FAVORITES"
    RECENTS = "RECENTS"
    BOTH = "BOTH"
    UNKNOWN_VALUE = "UNKNOWN__"


class RouteCalculationCondition(StrEnum):
    """Route calculation strategy accepted when sending a destination."""

    FASTEST_ROUTE = "FASTEST_ROUTE"
    SHORTEST_ROUTE = "SHORTEST_ROUTE"
    ECO_ROUTE = "ECO_ROUTE"
    GENERAL_ROUTE = "GENERAL_ROUTE"
    UNKNOWN_VALUE = "UNKNOWN__"


class RecalculatedWaypointType(StrEnum):
    """How Nissan should treat a recalculated route waypoint."""

    WAYPOINT = "WAYPOINT"
    EPOI_NOT_RECALCULATED = "EPOI_NOT_RECALCULATED"
    UNKNOWN_VALUE = "UNKNOWN__"


class ChargingConnectorType(StrEnum):
    """Charging connector category attached to a route waypoint."""

    NORMAL = "NORMAL"
    QUICK = "QUICK"
    UNKNOWN_VALUE = "UNKNOWN__"


class PlugConnectorType(StrEnum):
    """Charging plugs accepted by electric route planning."""

    CCS = "CCS"
    J1772 = "J1772"
    NACS = "NACS"
    UNKNOWN_VALUE = "UNKNOWN__"


class RouteChargingTimeUnit(StrEnum):
    """Charging time unit accepted by planned-route inputs."""

    MINUTE = "MIN"
    UNKNOWN_VALUE = "UNKNOWN__"


class NotificationIntervalUnit(StrEnum):
    """Notification interval unit accepted by planned-route inputs."""

    MINUTE = "MIN"
    UNKNOWN_VALUE = "UNKNOWN__"


class RouteStatus(StrEnum):
    """Route status accepted by the route-history filter."""

    RESERVED = "RESERVED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    DEPARTURED = "DEPARTURED"
    UNKNOWN_VALUE = "UNKNOWN__"


@dataclass(frozen=True, slots=True)
class DestinationInput:
    """Destination sent as a journey waypoint or point of interest."""

    name: str
    coordinate: CoordinateInput
    address: AddressInput = field(default_factory=AddressInput)
    phone_number: str | UnsetType | None = UNSET
    recalculated_waypoint_type: RecalculatedWaypointType | UnsetType | None = UNSET
    charging_output: int | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class RouteChargingTimeInput:
    """Charging duration attached to a planned-route waypoint."""

    value: int
    unit: RouteChargingTimeUnit = RouteChargingTimeUnit.MINUTE


@dataclass(frozen=True, slots=True)
class RouteWaypointInput:
    """One waypoint stored in a planned route."""

    name: str
    coordinate: CoordinateInput
    address: AddressInput = field(default_factory=AddressInput)
    phone_number: str | UnsetType | None = UNSET
    recalculated_waypoint_type: RecalculatedWaypointType | UnsetType | None = UNSET
    charging_output: int | UnsetType | None = UNSET
    charging_time: RouteChargingTimeInput | UnsetType | None = UNSET
    charger_type: ChargingConnectorType | UnsetType | None = UNSET
    state_of_charge_difference: int | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class RouteDistanceInput:
    """Integer route distance whose non-null unit may be omitted."""

    value: int
    unit: DistanceUnit | UnsetType = UNSET


@dataclass(frozen=True, slots=True)
class RouteTemperatureInput:
    """Route temperature whose unit may be omitted or explicitly null."""

    value: float
    unit: TemperatureUnit | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class RouteNotificationIntervalInput:
    """Notification interval stored with a planned route."""

    value: int
    unit: NotificationIntervalUnit = NotificationIntervalUnit.MINUTE


@dataclass(frozen=True, slots=True)
class PlannedRouteInput:
    """Complete route settings required by Nissan's save-route mutation."""

    name: str
    routes: tuple[RouteWaypointInput | None, ...]
    estimated_time_of_departure: datetime
    estimated_time_of_arrival: datetime
    distance: RouteDistanceInput
    temperature: RouteTemperatureInput | UnsetType | None = UNSET
    should_recalculate_route: bool | UnsetType | None = UNSET
    should_enable_notification: bool | UnsetType | None = UNSET
    notification_interval: RouteNotificationIntervalInput | UnsetType | None = UNSET
    avoid_highway: bool | UnsetType | None = UNSET
    avoid_tolls: bool | UnsetType | None = UNSET
    avoid_ferries: bool | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class PlannedRouteUpdate:
    """Partial planned-route update; omitted fields remain unchanged."""

    id: str
    name: str | UnsetType | None = UNSET
    routes: tuple[RouteWaypointInput | None, ...] | UnsetType | None = UNSET
    estimated_time_of_departure: datetime | UnsetType | None = UNSET
    estimated_time_of_arrival: datetime | UnsetType | None = UNSET
    distance: RouteDistanceInput | UnsetType | None = UNSET
    temperature: RouteTemperatureInput | UnsetType | None = UNSET
    notification_interval: RouteNotificationIntervalInput | UnsetType | None = UNSET
    should_enable_notification: bool | UnsetType | None = UNSET
    should_recalculate_route: bool | UnsetType | None = UNSET
    avoid_highway: bool | UnsetType | None = UNSET
    avoid_tolls: bool | UnsetType | None = UNSET
    avoid_ferries: bool | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class TJunctionLocationInput:
    """Unsaved T-Junction location selected for saving."""

    id: str
    name: str


def destination_input(value: DestinationInput) -> dict[str, object]:
    return optional_input_fields(
        name=value.name,
        phoneNumber=value.phone_number,
        coordinate=coordinate_input(value.coordinate),
        address=address_input(value.address),
        recalculatedWaypointType=optional_navigation_enum(value.recalculated_waypoint_type),
        chargingOutput=value.charging_output,
    )


def route_waypoint_input(value: RouteWaypointInput) -> dict[str, object]:
    return optional_input_fields(
        name=value.name,
        coordinate=coordinate_input(value.coordinate),
        address=address_input(value.address),
        phoneNumber=value.phone_number,
        recalculatedWaypointType=optional_navigation_enum(value.recalculated_waypoint_type),
        chargingOutput=value.charging_output,
        chargingTime=_optional_serialized(value.charging_time, route_charging_time_input),
        chargerType=optional_navigation_enum(value.charger_type),
        socDiff=value.state_of_charge_difference,
    )


def route_distance_input(value: RouteDistanceInput) -> dict[str, object]:
    return optional_input_fields(
        value=value.value,
        unit=optional_navigation_enum(value.unit),
    )


def route_temperature_input(value: RouteTemperatureInput) -> dict[str, object]:
    return optional_input_fields(
        value=value.value,
        unit=optional_navigation_enum(value.unit),
    )


def route_notification_interval_input(
    value: RouteNotificationIntervalInput,
) -> dict[str, object]:
    return {"value": value.value, "unit": navigation_enum_input(value.unit)}


def route_charging_time_input(value: RouteChargingTimeInput) -> dict[str, object]:
    return {"unit": navigation_enum_input(value.unit), "value": value.value}


def planned_route_input(value: PlannedRouteInput) -> dict[str, object]:
    return optional_input_fields(
        name=value.name,
        routes=[route_waypoint_input(item) if item is not None else None for item in value.routes],
        estimatedTimeOfDeparture=serialize_datetime(value.estimated_time_of_departure),
        estimatedTimeOfArrival=serialize_datetime(value.estimated_time_of_arrival),
        distance=route_distance_input(value.distance),
        temperature=_optional_serialized(value.temperature, route_temperature_input),
        shouldRecalculateRoute=value.should_recalculate_route,
        shouldEnableNotification=value.should_enable_notification,
        notificationInterval=_optional_serialized(
            value.notification_interval,
            route_notification_interval_input,
        ),
        avoidHighway=value.avoid_highway,
        avoidTolls=value.avoid_tolls,
        avoidFerries=value.avoid_ferries,
    )


def planned_route_update_input(value: PlannedRouteUpdate) -> dict[str, object]:
    return optional_input_fields(
        id=value.id,
        name=value.name,
        routes=_optional_routes(value.routes),
        estimatedTimeOfDeparture=_optional_datetime(value.estimated_time_of_departure),
        estimatedTimeOfArrival=_optional_datetime(value.estimated_time_of_arrival),
        distance=_optional_serialized(value.distance, route_distance_input),
        temperature=_optional_serialized(value.temperature, route_temperature_input),
        notificationInterval=_optional_serialized(
            value.notification_interval,
            route_notification_interval_input,
        ),
        shouldEnableNotification=value.should_enable_notification,
        shouldRecalculateRoute=value.should_recalculate_route,
        avoidHighway=value.avoid_highway,
        avoidTolls=value.avoid_tolls,
        avoidFerries=value.avoid_ferries,
    )


def t_junction_location_input(value: TJunctionLocationInput) -> dict[str, object]:
    return {"id": value.id, "name": value.name}


def save_t_junction_locations_input(
    vin: str,
    last_updated_at: str,
    locations: tuple[TJunctionLocationInput, ...],
) -> dict[str, object]:
    return {
        "vin": vin,
        "lastUpdatedAt": last_updated_at,
        "locationIds": [t_junction_location_input(location) for location in locations],
    }


def update_saved_t_junction_location_input(
    vin: str,
    location_id: str,
    location_name: str,
) -> dict[str, object]:
    return {"vin": vin, "id": location_id, "locationName": location_name}


def delete_saved_t_junction_locations_input(
    vin: str,
    location_ids: tuple[str, ...],
    last_updated_at: str,
) -> dict[str, object]:
    return {
        "vin": vin,
        "locationIds": list(location_ids),
        "lastUpdatedAt": last_updated_at,
    }


def delete_unsaved_t_junction_locations_input(
    vin: str,
    location_ids: tuple[str, ...],
) -> dict[str, object]:
    return {"vin": vin, "locationIds": list(location_ids)}


def optional_destination_time(value: datetime | UnsetType | None) -> object:
    return _optional_datetime(value)


def optional_navigation_enum(value: StrEnum | UnsetType | None) -> object:
    if isinstance(value, StrEnum):
        return navigation_enum_input(value)
    return value


def navigation_enum_input(value: StrEnum) -> str:
    return serialize_enum(value)


def nullable_route_waypoints_input(
    values: tuple[RouteWaypointInput | None, ...],
) -> list[object]:
    return [route_waypoint_input(value) if value is not None else None for value in values]


def nullable_plug_connector_types_input(
    values: tuple[PlugConnectorType | None, ...],
) -> list[str | None]:
    return [navigation_enum_input(value) if value is not None else None for value in values]


def optional_battery_level_string(value: int | UnsetType | None) -> object:
    if isinstance(value, UnsetType) or value is None:
        return value
    return str(value)


def _optional_routes(
    value: tuple[RouteWaypointInput | None, ...] | UnsetType | None,
) -> object:
    if isinstance(value, UnsetType) or value is None:
        return value
    return [route_waypoint_input(item) if item is not None else None for item in value]


def _optional_datetime(value: datetime | UnsetType | None) -> object:
    if isinstance(value, UnsetType) or value is None:
        return value
    return serialize_datetime(value)


def _optional_serialized[InputT](
    value: InputT | UnsetType | None,
    serializer: Callable[[InputT], object],
) -> object:
    if isinstance(value, UnsetType) or value is None:
        return value
    return serializer(value)
