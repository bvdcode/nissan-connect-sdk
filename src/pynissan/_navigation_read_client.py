from __future__ import annotations

from datetime import datetime

from . import operations
from ._client_base import _NissanClientBase
from ._client_helpers import _navigation_headers
from .graphql_input import UNSET, UnsetType, optional_input_fields
from .models import (
    DistanceUnit,
    TemperatureUnit,
    VehicleLocation,
    VehiclePhotos,
)
from .navigation_inputs import (
    NavigationDataSource,
    PlugConnectorType,
    PointOfInterestFolderFilter,
    RouteStatus,
    RouteWaypointInput,
    nullable_plug_connector_types_input,
    nullable_route_waypoints_input,
    optional_battery_level_string,
    optional_destination_time,
    optional_navigation_enum,
)
from .navigation_models import (
    EVWaypointResult,
    TJunctionLocations,
    VehicleJourneys,
    VehiclePlannedRoutes,
    VehiclePointOfInterestDestinations,
    VehicleRoutesHistory,
)
from .navigation_parsing import (
    parse_t_junction_locations,
    parse_vehicle_ev_waypoints,
    parse_vehicle_journeys,
    parse_vehicle_planned_routes,
    parse_vehicle_point_of_interest_destinations,
    parse_vehicle_routes_history,
)
from .parsing import (
    parse_photos_around_vehicle,
    parse_vehicle_location,
)


class _NavigationReadClientMixin(_NissanClientBase):
    async def async_get_vehicle_location(self, vin: str) -> VehicleLocation:
        """Return the last cached location without requesting a new fix."""

        data = await self._transport.async_graphql(
            "VehicleLocation",
            operations.VEHICLE_LOCATION,
            {"vin": vin},
        )
        return parse_vehicle_location(data, vin)

    async def async_get_photos_around_vehicle(self, vin: str) -> VehiclePhotos | None:
        """Return cached vehicle photos and their temporary links when available."""

        data = await self._transport.async_graphql(
            "PhotosAroundVehicle",
            operations.PHOTOS_AROUND_VEHICLE,
            {"vin": vin},
        )
        return parse_photos_around_vehicle(data)

    async def async_get_vehicle_journeys(self, vin: str) -> VehicleJourneys | None:
        """Return journeys cached for a connected vehicle."""

        data = await self._transport.async_graphql(
            "VehicleJourneys",
            operations.VEHICLE_JOURNEYS,
            {"vin": vin},
        )
        return parse_vehicle_journeys(data)

    async def async_get_vehicle_planned_routes(
        self,
        vin: str,
        *,
        distance_unit: DistanceUnit | UnsetType | None = UNSET,
        temperature_unit: TemperatureUnit | UnsetType | None = UNSET,
        data_source: NavigationDataSource | None = None,
    ) -> VehiclePlannedRoutes | None:
        """Return saved planned routes for an electric vehicle."""

        data = await self._transport.async_graphql(
            "VehiclePlannedRoutes",
            operations.VEHICLE_PLANNED_ROUTES,
            optional_input_fields(
                vin=vin,
                distanceUnit=optional_navigation_enum(distance_unit),
                temperatureUnit=optional_navigation_enum(temperature_unit),
            ),
            extra_headers=_navigation_headers(data_source),
        )
        return parse_vehicle_planned_routes(data)

    async def async_get_vehicle_point_of_interest_destinations(
        self,
        vin: str,
        *,
        folder: PointOfInterestFolderFilter | UnsetType | None = (PointOfInterestFolderFilter.BOTH),
    ) -> VehiclePointOfInterestDestinations | None:
        """Return favorite and recent destinations stored for a vehicle."""

        data = await self._transport.async_graphql(
            "VehiclePOIDestinations",
            operations.VEHICLE_POINT_OF_INTEREST_DESTINATIONS,
            optional_input_fields(
                vin=vin,
                folderName=optional_navigation_enum(folder),
            ),
        )
        return parse_vehicle_point_of_interest_destinations(data)

    async def async_get_vehicle_routes_history(
        self,
        vin: str,
        *,
        distance_unit: DistanceUnit | UnsetType | None = UNSET,
        temperature_unit: TemperatureUnit | UnsetType | None = UNSET,
        status: RouteStatus | UnsetType | None = UNSET,
    ) -> VehicleRoutesHistory | None:
        """Return route history for a compatible electric AVK2 vehicle."""

        data = await self._transport.async_graphql(
            "RoutesHistory",
            operations.ROUTES_HISTORY,
            optional_input_fields(
                vin=vin,
                distanceUnit=optional_navigation_enum(distance_unit),
                temperatureUnit=optional_navigation_enum(temperature_unit),
                status=optional_navigation_enum(status),
            ),
        )
        return parse_vehicle_routes_history(data)

    async def async_get_t_junction_locations(self, vin: str) -> TJunctionLocations | None:
        """Return saved and unsaved T-junction camera locations."""

        data = await self._transport.async_graphql(
            "TJunctionLocations",
            operations.T_JUNCTION_LOCATIONS,
            {"vin": vin},
        )
        return parse_t_junction_locations(data)

    async def async_get_vehicle_ev_waypoints(
        self,
        vin: str,
        routes: tuple[RouteWaypointInput | None, ...],
        plug_connector_types: tuple[PlugConnectorType | None, ...],
        *,
        depart_at: datetime | UnsetType | None = UNSET,
        arrived_by: datetime | UnsetType | None = UNSET,
        state_of_charge_at_destination: int | UnsetType | None = UNSET,
        distance_unit: DistanceUnit | UnsetType | None = UNSET,
        estimated_battery_level_at_departure: int | UnsetType | None = UNSET,
        minimum_power: float | UnsetType | None = UNSET,
        state_of_charge_at_stop: int | UnsetType | None = UNSET,
        use_hvac: bool | UnsetType | None = UNSET,
        avoid_highway: bool | UnsetType | None = UNSET,
        avoid_tolls: bool | UnsetType | None = UNSET,
        avoid_ferries: bool | UnsetType | None = UNSET,
        data_source: NavigationDataSource | None = None,
    ) -> EVWaypointResult | None:
        """Calculate electric route waypoints or return a typed route error."""

        effective_state_of_charge_at_stop = state_of_charge_at_stop
        if data_source is NavigationDataSource.KMR and isinstance(
            effective_state_of_charge_at_stop,
            UnsetType,
        ):
            effective_state_of_charge_at_stop = 20
        data = await self._transport.async_graphql(
            "VehicleEVWaypoints",
            operations.VEHICLE_EV_WAYPOINTS,
            optional_input_fields(
                vin=vin,
                departAt=optional_destination_time(depart_at),
                arrivedBy=optional_destination_time(arrived_by),
                socAtDestination=state_of_charge_at_destination,
                routes=nullable_route_waypoints_input(routes),
                distanceUnit=optional_navigation_enum(distance_unit),
                plugConnectorTypes=nullable_plug_connector_types_input(plug_connector_types),
                estimatedBatteryLevelAtDeparture=optional_battery_level_string(
                    estimated_battery_level_at_departure
                ),
                minPower=minimum_power,
                socAtStop=effective_state_of_charge_at_stop,
                useHvac=use_hvac,
                avoidHighway=avoid_highway,
                avoidTolls=avoid_tolls,
                avoidFerries=avoid_ferries,
            ),
            extra_headers=_navigation_headers(data_source),
        )
        return parse_vehicle_ev_waypoints(data)
