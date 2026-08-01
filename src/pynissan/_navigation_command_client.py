from __future__ import annotations

from datetime import datetime

from . import operations
from ._client_base import _NissanClientBase
from ._client_helpers import _navigation_headers
from .graphql_input import UNSET, UnsetType, optional_input_fields
from .models import (
    ServiceRequest,
    ServiceRequestKind,
)
from .navigation_inputs import (
    DestinationInput,
    NavigationDataSource,
    PlannedRouteInput,
    PlannedRouteUpdate,
    PointOfInterestFolder,
    RouteCalculationCondition,
    TJunctionLocationInput,
    delete_saved_t_junction_locations_input,
    delete_unsaved_t_junction_locations_input,
    destination_input,
    navigation_enum_input,
    optional_destination_time,
    optional_navigation_enum,
    planned_route_input,
    planned_route_update_input,
    save_t_junction_locations_input,
    update_saved_t_junction_location_input,
)


class _NavigationCommandClientMixin(_NissanClientBase):
    async def async_send_journey(
        self,
        vin: str,
        waypoints: tuple[DestinationInput, ...],
        *,
        avoid_highway: bool | UnsetType | None = UNSET,
        avoid_tolls: bool | UnsetType | None = UNSET,
        avoid_ferries: bool | UnsetType | None = UNSET,
        estimated_time_of_arrival: datetime | UnsetType | None = UNSET,
        estimated_time_of_departure: datetime | UnsetType | None = UNSET,
        arrival_flag: bool | UnsetType | None = UNSET,
        departure_flag: bool | UnsetType | None = UNSET,
        data_source: NavigationDataSource | None = None,
    ) -> bool:
        """Send an ad-hoc journey and its waypoints to the vehicle."""

        return await self._async_nullable_success_operation(
            "SendJourney",
            operations.SEND_JOURNEY,
            "sendJourney",
            optional_input_fields(
                vin=vin,
                waypoints=[destination_input(waypoint) for waypoint in waypoints],
                avoidHighway=avoid_highway,
                avoidTolls=avoid_tolls,
                avoidFerries=avoid_ferries,
                estimatedTimeOfArrival=optional_destination_time(estimated_time_of_arrival),
                estimatedTimeOfDeparture=optional_destination_time(estimated_time_of_departure),
                arrivalFlag=arrival_flag,
                departureFlag=departure_flag,
            ),
            extra_headers=_navigation_headers(data_source),
        )

    async def async_send_planned_route(
        self,
        vin: str,
        route_id: str,
        *,
        estimated_time_of_arrival: datetime | UnsetType | None = UNSET,
        estimated_time_of_departure: datetime | UnsetType | None = UNSET,
        arrival_flag: bool | UnsetType | None = UNSET,
        departure_flag: bool | UnsetType | None = UNSET,
        data_source: NavigationDataSource | None = None,
    ) -> bool:
        """Send a previously saved route to the vehicle."""

        return await self._async_nullable_success_operation(
            "SendPlannedRoute",
            operations.SEND_PLANNED_ROUTE,
            "sendPlannedRoute",
            optional_input_fields(
                vin=vin,
                routeId=route_id,
                estimatedTimeOfArrival=optional_destination_time(estimated_time_of_arrival),
                estimatedTimeOfDeparture=optional_destination_time(estimated_time_of_departure),
                arrivalFlag=arrival_flag,
                departureFlag=departure_flag,
            ),
            extra_headers=_navigation_headers(data_source),
        )

    async def async_send_point_of_interest(
        self,
        vin: str,
        folder: PointOfInterestFolder,
        destination: DestinationInput,
        *,
        calculation_condition: RouteCalculationCondition | UnsetType | None = UNSET,
        avoid_highway: bool | UnsetType | None = UNSET,
        avoid_tolls: bool | UnsetType | None = UNSET,
        avoid_ferries: bool | UnsetType | None = UNSET,
    ) -> bool:
        """Send a favorite or recent point of interest to the vehicle."""

        return await self._async_nullable_success_operation(
            "SendPointOfInterest",
            operations.SEND_POINT_OF_INTEREST,
            "sendPointOfInterest",
            optional_input_fields(
                vin=vin,
                folderName=navigation_enum_input(folder),
                destinationInput=destination_input(destination),
                calculationCondition=optional_navigation_enum(calculation_condition),
                avoidHighway=avoid_highway,
                avoidTolls=avoid_tolls,
                avoidFerries=avoid_ferries,
            ),
        )

    async def async_save_route(
        self,
        vin: str,
        route: PlannedRouteInput,
        *,
        arrival_flag: bool | UnsetType | None = UNSET,
        departure_flag: bool | UnsetType | None = UNSET,
        data_source: NavigationDataSource | None = None,
    ) -> ServiceRequest:
        """Save a planned route in the vehicle account."""

        return await self._async_service_request(
            "SaveRoute",
            operations.SAVE_ROUTE,
            "saveRoute",
            optional_input_fields(
                vin=vin,
                plannedRoute=planned_route_input(route),
                arrivalFlag=arrival_flag,
                departureFlag=departure_flag,
            ),
            ServiceRequestKind.ROUTE,
            extra_headers=_navigation_headers(data_source),
        )

    async def async_update_route(
        self,
        vin: str,
        route: PlannedRouteUpdate,
        *,
        arrival_flag: bool | UnsetType | None = UNSET,
        departure_flag: bool | UnsetType | None = UNSET,
    ) -> ServiceRequest:
        """Patch a saved planned route."""

        return await self._async_service_request(
            "UpdateRoute",
            operations.UPDATE_ROUTE,
            "updateRoute",
            optional_input_fields(
                vin=vin,
                plannedRoute=planned_route_update_input(route),
                arrivalFlag=arrival_flag,
                departureFlag=departure_flag,
            ),
            ServiceRequestKind.ROUTE,
        )

    async def async_delete_route(self, vin: str, route_id: str) -> bool:
        """Delete a saved planned route."""

        return await self._async_nullable_success_operation(
            "DeleteRoute",
            operations.DELETE_ROUTE,
            "deleteRoute",
            {"vin": vin, "routeId": route_id},
        )

    async def async_delete_favorite_point_of_interest(
        self,
        vin: str,
        destination_id: str,
    ) -> bool:
        """Delete a destination from the vehicle's favorites."""

        return await self._async_nullable_success_operation(
            "DeleteFavoritePointOfInterest",
            operations.DELETE_FAVORITE_POINT_OF_INTEREST,
            "deleteFavoritePointOfInterest",
            {"vin": vin, "destinationId": destination_id},
        )

    async def async_save_t_junction_locations(
        self,
        vin: str,
        last_updated_at: str,
        locations: tuple[TJunctionLocationInput, ...],
    ) -> ServiceRequest:
        """Save selected T-junction camera locations."""

        return await self._async_service_request(
            "SaveTJunctionLocations",
            operations.SAVE_T_JUNCTION_LOCATIONS,
            "saveTJunctionLocations",
            {
                "input": save_t_junction_locations_input(
                    vin,
                    last_updated_at,
                    locations,
                )
            },
            ServiceRequestKind.T_JUNCTION,
        )

    async def async_update_saved_t_junction_location(
        self,
        vin: str,
        location_id: str,
        location_name: str,
    ) -> ServiceRequest:
        """Rename a saved T-junction camera location."""

        return await self._async_service_request(
            "UpdateSavedTJunctionLocation",
            operations.UPDATE_SAVED_T_JUNCTION_LOCATION,
            "updateSavedTJunctionLocation",
            {
                "input": update_saved_t_junction_location_input(
                    vin,
                    location_id,
                    location_name,
                )
            },
            ServiceRequestKind.T_JUNCTION,
        )

    async def async_delete_saved_t_junction_locations(
        self,
        vin: str,
        location_ids: tuple[str, ...],
        *,
        last_updated_at: str,
    ) -> ServiceRequest:
        """Delete saved T-junction camera locations."""

        return await self._async_service_request(
            "DeleteSavedTJunctionLocations",
            operations.DELETE_SAVED_T_JUNCTION_LOCATIONS,
            "deleteSavedTJunctionLocations",
            {
                "input": delete_saved_t_junction_locations_input(
                    vin,
                    location_ids,
                    last_updated_at,
                )
            },
            ServiceRequestKind.T_JUNCTION,
        )

    async def async_delete_unsaved_t_junction_locations(
        self,
        vin: str,
        location_ids: tuple[str, ...],
    ) -> ServiceRequest:
        """Discard unsaved T-junction camera locations."""

        return await self._async_service_request(
            "DeleteUnsavedTJunctionLocations",
            operations.DELETE_UNSAVED_T_JUNCTION_LOCATIONS,
            "deleteUnsavedTJunctionLocations",
            {
                "input": delete_unsaved_t_junction_locations_input(
                    vin,
                    location_ids,
                )
            },
            ServiceRequestKind.T_JUNCTION,
        )
