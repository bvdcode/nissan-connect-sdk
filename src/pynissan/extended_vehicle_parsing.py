from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from enum import StrEnum

from .exceptions import ResponseError
from .extended_vehicle_models import (
    DrivingHistory,
    DrivingHistoryAverageSpeed,
    DrivingHistoryCo2Saved,
    DrivingHistoryCoordinate,
    DrivingHistoryDistance,
    DrivingHistoryTrip,
    DrivingHistoryTripSummary,
    EmpConnector,
    EmpEvse,
    EmpEvseStatus,
    EmpLocation,
    EmpLocationCoordinates,
    EmpLocationOpeningTiming,
    EmpLocationStatus,
    EVChargeStation,
    EVChargeStationAddress,
    EVChargeStationConnector,
    EVChargeStationCoordinate,
    EVehicleEligibility,
    EVehicleEligibilityData,
    LastKnownCameraUsageCounter,
    LocationDetails,
    ParkingChargeable,
    ParkingChargeableData,
    ShareableCapabilities,
    ShareableCapability,
    ShareableCapabilityGroup,
    TariffCongestionFees,
    TariffCongestionFeeTier,
    TariffDetail,
    TariffEnergyFees,
    TariffEnergyFeeTier,
    TariffIdleFees,
    TariffIdleFeeTier,
    TariffLocalizedText,
    TariffPricing,
    TariffPricingData,
    WeightUnit,
)
from .models import DistanceUnit, SpeedUnit
from .navigation_inputs import PlugConnectorType


def parse_driving_history(data: Mapping[str, object]) -> DrivingHistory | None:
    """Parse an electric vehicle's driving history with strict list nullability."""

    vehicle = _vehicle(data)
    if vehicle is None or "drivingHistory" not in vehicle:
        return None
    path = "vehicle.drivingHistory"
    history = _optional_typed_object(vehicle.get("drivingHistory"), path)
    if history is None:
        return None

    summary_values = _list(history.get("tripSummaries"), f"{path}.tripSummaries")
    summaries: list[DrivingHistoryTripSummary] = []
    for index, value in enumerate(summary_values):
        summaries.append(_parse_driving_history_summary(value, f"{path}.tripSummaries[{index}]"))

    trip_values = _list(history.get("trips"), f"{path}.trips")
    trips: list[DrivingHistoryTrip] = []
    for index, value in enumerate(trip_values):
        trips.append(_parse_driving_history_trip(value, f"{path}.trips[{index}]"))

    return DrivingHistory(tuple(summaries), tuple(trips))


def parse_ev_charge_stations(
    data: Mapping[str, object],
) -> tuple[EVChargeStation | None, ...] | None:
    """Parse nearby charging stations while preserving nullable list items."""

    vehicle = _vehicle(data)
    if vehicle is None or "evChargeStations" not in vehicle:
        return None
    path = "vehicle.evChargeStations"
    values = _nullable_list(vehicle.get("evChargeStations"), path)
    if values is None:
        return None

    stations: list[EVChargeStation | None] = []
    for index, value in enumerate(values):
        if value is None:
            stations.append(None)
            continue
        stations.append(_parse_ev_charge_station(value, f"{path}[{index}]"))
    return tuple(stations)


def parse_e_vehicle_eligibility(
    data: Mapping[str, object],
) -> EVehicleEligibility | None:
    """Parse the raw eVehicle eligibility status wrapper."""

    root_field = "eVehicleEligibility"
    if root_field not in data:
        raise ResponseError(f"{root_field} is missing")
    result = _optional_typed_object(data.get(root_field), root_field)
    if result is None:
        return None
    eligibility_data = _optional_typed_object(
        result.get("data"),
        f"{root_field}.data",
    )
    return EVehicleEligibility(
        status_code=_nullable_string(result.get("statusCode"), f"{root_field}.statusCode"),
        status_message=_nullable_string(
            result.get("statusMessage"),
            f"{root_field}.statusMessage",
        ),
        timestamp=_nullable_string(result.get("timestamp"), f"{root_field}.timestamp"),
        data=(
            EVehicleEligibilityData(
                vin=_nullable_string(
                    eligibility_data.get("vin"),
                    f"{root_field}.data.vin",
                ),
                v1g_eligible=_nullable_bool(
                    eligibility_data.get("v1GEligible"),
                    f"{root_field}.data.v1GEligible",
                ),
            )
            if eligibility_data is not None
            else None
        ),
    )


def parse_last_known_camera_usage_counter(
    data: Mapping[str, object],
) -> LastKnownCameraUsageCounter | None:
    """Parse the last known camera usage counter for an AVK2 vehicle."""

    vehicle = _vehicle(data)
    if vehicle is None or "lastKnownCameraUsageCounter" not in vehicle:
        return None
    path = "vehicle.lastKnownCameraUsageCounter"
    result = _optional_typed_object(vehicle.get("lastKnownCameraUsageCounter"), path)
    if result is None:
        return None
    return LastKnownCameraUsageCounter(
        counter=_nullable_string(result.get("counter"), f"{path}.counter"),
        last_update_time=_nullable_datetime(
            result.get("lastUpdateTime"),
            f"{path}.lastUpdateTime",
        ),
    )


def parse_location_details(data: Mapping[str, object]) -> LocationDetails | None:
    """Parse the raw EMP status wrapper and charging-location collection."""

    root_field = "locationDetails"
    if root_field not in data:
        raise ResponseError(f"{root_field} is missing")
    result = _optional_typed_object(data.get(root_field), root_field)
    if result is None:
        return None

    raw_locations = _nullable_list(result.get("data"), f"{root_field}.data")
    locations: tuple[EmpLocation | None, ...] | None = None
    if raw_locations is not None:
        parsed_locations: list[EmpLocation | None] = []
        for index, value in enumerate(raw_locations):
            if value is None:
                parsed_locations.append(None)
                continue
            parsed_locations.append(_parse_emp_location(value, f"{root_field}.data[{index}]"))
        locations = tuple(parsed_locations)

    return LocationDetails(
        status_code=_nullable_string(result.get("statusCode"), f"{root_field}.statusCode"),
        status_message=_nullable_string(
            result.get("statusMessage"),
            f"{root_field}.statusMessage",
        ),
        timestamp=_nullable_string(result.get("timestamp"), f"{root_field}.timestamp"),
        data=locations,
    )


def parse_parking_chargeable(data: Mapping[str, object]) -> ParkingChargeable | None:
    """Parse the raw EMP parking-chargeability status wrapper."""

    root_field = "parkingChargeable"
    if root_field not in data:
        raise ResponseError(f"{root_field} is missing")
    result = _optional_typed_object(data.get(root_field), root_field)
    if result is None:
        return None
    raw_data = _optional_typed_object(result.get("data"), f"{root_field}.data")
    return ParkingChargeable(
        status_code=_nullable_string(result.get("statusCode"), f"{root_field}.statusCode"),
        status_message=_nullable_string(
            result.get("statusMessage"),
            f"{root_field}.statusMessage",
        ),
        timestamp=_nullable_string(result.get("timestamp"), f"{root_field}.timestamp"),
        data=(
            ParkingChargeableData(
                evse_id=_nullable_string(raw_data.get("evseId"), f"{root_field}.data.evseId"),
                is_parking_chargeable=_nullable_bool(
                    raw_data.get("isParkingChargeable"),
                    f"{root_field}.data.isParkingChargeable",
                ),
                is_congestion_chargeable=_nullable_bool(
                    raw_data.get("isCongestionChargeable"),
                    f"{root_field}.data.isCongestionChargeable",
                ),
            )
            if raw_data is not None
            else None
        ),
    )


def parse_shareable_capabilities(
    data: Mapping[str, object],
) -> ShareableCapabilities | None:
    """Parse shareable capability groups while retaining nullable list items."""

    vehicle = _vehicle(data)
    if vehicle is None or "shareableCapabilities" not in vehicle:
        return None
    path = "vehicle.shareableCapabilities"
    result = _optional_typed_object(vehicle.get("shareableCapabilities"), path)
    if result is None:
        return None

    raw_groups = _list(result.get("group"), f"{path}.group")
    groups: list[ShareableCapabilityGroup | None] = []
    for index, value in enumerate(raw_groups):
        if value is None:
            groups.append(None)
            continue
        groups.append(_parse_shareable_capability_group(value, f"{path}.group[{index}]"))
    return ShareableCapabilities(tuple(groups))


def parse_tariff_pricing(data: Mapping[str, object]) -> TariffPricing | None:
    """Parse the raw EMP tariff-pricing status wrapper."""

    root_field = "tariffPricing"
    if root_field not in data:
        raise ResponseError(f"{root_field} is missing")
    result = _optional_typed_object(data.get(root_field), root_field)
    if result is None:
        return None
    raw_data = _optional_typed_object(result.get("data"), f"{root_field}.data")
    return TariffPricing(
        status_code=_nullable_string(result.get("statusCode"), f"{root_field}.statusCode"),
        status_message=_nullable_string(
            result.get("statusMessage"),
            f"{root_field}.statusMessage",
        ),
        timestamp=_nullable_string(result.get("timestamp"), f"{root_field}.timestamp"),
        data=(
            _parse_tariff_pricing_data(raw_data, f"{root_field}.data")
            if raw_data is not None
            else None
        ),
    )


def _parse_driving_history_summary(
    value: object,
    path: str,
) -> DrivingHistoryTripSummary:
    summary = _typed_object(value, path)
    return DrivingHistoryTripSummary(
        user_id=_nullable_string(summary.get("userId"), f"{path}.userId"),
        day=_nullable_int(summary.get("day"), f"{path}.day"),
        month=_nullable_int(summary.get("month"), f"{path}.month"),
        year=_nullable_int(summary.get("year"), f"{path}.year"),
        number_of_trips=_nullable_int(
            summary.get("numberOfTrips"),
            f"{path}.numberOfTrips",
        ),
        distance_traveled=_parse_optional_driving_distance(
            summary.get("distanceTraveled"),
            f"{path}.distanceTraveled",
        ),
        duration=_nullable_string(summary.get("duration"), f"{path}.duration"),
        average_speed=_parse_optional_average_speed(
            summary.get("averageSpeed"),
            f"{path}.averageSpeed",
        ),
        energy_consumed=_nullable_float(
            summary.get("energyConsumed"),
            f"{path}.energyConsumed",
        ),
        co2_saved=_parse_optional_co2_saved(
            summary.get("co2Saved"),
            f"{path}.co2Saved",
        ),
    )


def _parse_driving_history_trip(value: object, path: str) -> DrivingHistoryTrip:
    trip = _typed_object(value, path)
    return DrivingHistoryTrip(
        distance=_parse_optional_driving_distance(
            trip.get("distance"),
            f"{path}.distance",
        ),
        start_date=_nullable_datetime(trip.get("startDate"), f"{path}.startDate"),
        end_date=_nullable_datetime(trip.get("endDate"), f"{path}.endDate"),
        duration=_nullable_int(trip.get("duration"), f"{path}.duration"),
        start_location=_parse_optional_driving_coordinate(
            trip.get("startLocation"),
            f"{path}.startLocation",
        ),
        end_location=_parse_optional_driving_coordinate(
            trip.get("endLocation"),
            f"{path}.endLocation",
        ),
        average_speed=_parse_optional_average_speed(
            trip.get("averageSpeed"),
            f"{path}.averageSpeed",
        ),
        energy_consumed=_nullable_float(
            trip.get("energyConsumed"),
            f"{path}.energyConsumed",
        ),
        energy_saved=_nullable_float(trip.get("energySaved"), f"{path}.energySaved"),
        co2_saved=_parse_optional_co2_saved(trip.get("co2Saved"), f"{path}.co2Saved"),
        user_id=_nullable_string(trip.get("userId"), f"{path}.userId"),
    )


def _parse_optional_driving_distance(
    value: object,
    path: str,
) -> DrivingHistoryDistance | None:
    distance = _optional_typed_object(value, path)
    if distance is None:
        return None
    return DrivingHistoryDistance(
        unit=_enum(distance.get("unit"), DistanceUnit, f"{path}.unit"),
        value=_float(distance.get("value"), f"{path}.value"),
    )


def _parse_optional_average_speed(
    value: object,
    path: str,
) -> DrivingHistoryAverageSpeed | None:
    speed = _optional_typed_object(value, path)
    if speed is None:
        return None
    return DrivingHistoryAverageSpeed(
        type=_nullable_enum(speed.get("type"), SpeedUnit, f"{path}.type"),
        value=_nullable_float(speed.get("value"), f"{path}.value"),
    )


def _parse_optional_co2_saved(
    value: object,
    path: str,
) -> DrivingHistoryCo2Saved | None:
    saved = _optional_typed_object(value, path)
    if saved is None:
        return None
    return DrivingHistoryCo2Saved(
        unit=_nullable_enum(saved.get("unit"), WeightUnit, f"{path}.unit"),
        value=_nullable_float(saved.get("value"), f"{path}.value"),
    )


def _parse_optional_driving_coordinate(
    value: object,
    path: str,
) -> DrivingHistoryCoordinate | None:
    coordinate = _optional_typed_object(value, path)
    if coordinate is None:
        return None
    return DrivingHistoryCoordinate(
        latitude=_nullable_float(coordinate.get("latitude"), f"{path}.latitude"),
        longitude=_nullable_float(coordinate.get("longitude"), f"{path}.longitude"),
    )


def _parse_ev_charge_station(value: object, path: str) -> EVChargeStation:
    station = _typed_object(value, path)
    raw_connectors = _nullable_list(station.get("connectors"), f"{path}.connectors")
    connectors: tuple[EVChargeStationConnector | None, ...] | None = None
    if raw_connectors is not None:
        parsed_connectors: list[EVChargeStationConnector | None] = []
        for index, raw_connector in enumerate(raw_connectors):
            if raw_connector is None:
                parsed_connectors.append(None)
                continue
            parsed_connectors.append(
                _parse_ev_charge_station_connector(
                    raw_connector,
                    f"{path}.connectors[{index}]",
                )
            )
        connectors = tuple(parsed_connectors)

    return EVChargeStation(
        id=_nullable_string(station.get("id"), f"{path}.id"),
        name=_nullable_string(station.get("name"), f"{path}.name"),
        phone_number=_nullable_string(
            station.get("phoneNumber"),
            f"{path}.phoneNumber",
        ),
        address=_parse_optional_station_address(station.get("address"), f"{path}.address"),
        location=_parse_optional_station_coordinate(
            station.get("location"),
            f"{path}.location",
        ),
        connectors=connectors,
    )


def _parse_optional_station_address(
    value: object,
    path: str,
) -> EVChargeStationAddress | None:
    address = _optional_typed_object(value, path)
    if address is None:
        return None
    return EVChargeStationAddress(
        address1=_nullable_string(address.get("address1"), f"{path}.address1"),
        address2=_nullable_string(address.get("address2"), f"{path}.address2"),
        city=_nullable_string(address.get("city"), f"{path}.city"),
        country=_nullable_string(address.get("country"), f"{path}.country"),
        postal_code=_nullable_string(address.get("postalCode"), f"{path}.postalCode"),
        state=_nullable_string(address.get("state"), f"{path}.state"),
    )


def _parse_optional_station_coordinate(
    value: object,
    path: str,
) -> EVChargeStationCoordinate | None:
    coordinate = _optional_typed_object(value, path)
    if coordinate is None:
        return None
    return EVChargeStationCoordinate(
        latitude=_nullable_float(coordinate.get("latitude"), f"{path}.latitude"),
        longitude=_nullable_float(coordinate.get("longitude"), f"{path}.longitude"),
    )


def _parse_ev_charge_station_connector(
    value: object,
    path: str,
) -> EVChargeStationConnector:
    connector = _typed_object(value, path)
    return EVChargeStationConnector(
        plug_connector_type=_nullable_enum(
            connector.get("plugConnectorType"),
            PlugConnectorType,
            f"{path}.plugConnectorType",
        ),
        rated_power_kw=_nullable_float(
            connector.get("ratedPowerKW"),
            f"{path}.ratedPowerKW",
        ),
        voltage_v=_nullable_int(connector.get("voltageV"), f"{path}.voltageV"),
        current_a=_nullable_int(connector.get("currentA"), f"{path}.currentA"),
        current_type=_nullable_string(
            connector.get("currentType"),
            f"{path}.currentType",
        ),
    )


def _parse_emp_location(value: object, path: str) -> EmpLocation:
    location = _typed_object(value, path)
    return EmpLocation(
        location_id=_nullable_string(location.get("locationId"), f"{path}.locationId"),
        location_type=_nullable_enum(
            location.get("locationType"),
            EmpLocationStatus,
            f"{path}.locationType",
        ),
        location_name=_nullable_string(
            location.get("locationName"),
            f"{path}.locationName",
        ),
        location_logo=_nullable_string(
            location.get("locationLogo"),
            f"{path}.locationLogo",
        ),
        location_operator_name=_nullable_string(
            location.get("locationOperatorName"),
            f"{path}.locationOperatorName",
        ),
        location_sub_operator_name=_nullable_string(
            location.get("locationSubOperatorName"),
            f"{path}.locationSubOperatorName",
        ),
        location_address=_nullable_string(
            location.get("locationAddress"),
            f"{path}.locationAddress",
        ),
        location_city=_nullable_string(
            location.get("locationCity"),
            f"{path}.locationCity",
        ),
        location_state=_nullable_string(
            location.get("locationState"),
            f"{path}.locationState",
        ),
        location_country=_nullable_string(
            location.get("locationCountry"),
            f"{path}.locationCountry",
        ),
        location_postal_code=_nullable_string(
            location.get("locationPostalCode"),
            f"{path}.locationPostalCode",
        ),
        location_twenty_four_seven=_nullable_bool(
            location.get("locationTwentyfourseven"),
            f"{path}.locationTwentyfourseven",
        ),
        opening_timings=_parse_emp_opening_timings(
            location.get("locationOpeningTimings"),
            f"{path}.locationOpeningTimings",
        ),
        location_in_network=_nullable_bool(
            location.get("locationInNetwork"),
            f"{path}.locationInNetwork",
        ),
        phone=_nullable_string(location.get("phone"), f"{path}.phone"),
        coordinates=_parse_optional_emp_coordinates(
            location.get("locationCoordinates"),
            f"{path}.locationCoordinates",
        ),
        evses=_parse_emp_evses(location.get("evses"), f"{path}.evses"),
    )


def _parse_emp_opening_timings(
    value: object,
    path: str,
) -> tuple[EmpLocationOpeningTiming | None, ...] | None:
    raw_timings = _nullable_list(value, path)
    if raw_timings is None:
        return None
    timings: list[EmpLocationOpeningTiming | None] = []
    for index, raw_timing in enumerate(raw_timings):
        if raw_timing is None:
            timings.append(None)
            continue
        item_path = f"{path}[{index}]"
        timing = _typed_object(raw_timing, item_path)
        timings.append(
            EmpLocationOpeningTiming(
                weekday=_nullable_int(timing.get("weekday"), f"{item_path}.weekday"),
                period_begin=_nullable_string(
                    timing.get("periodBegin"),
                    f"{item_path}.periodBegin",
                ),
                period_end=_nullable_string(
                    timing.get("periodEnd"),
                    f"{item_path}.periodEnd",
                ),
            )
        )
    return tuple(timings)


def _parse_optional_emp_coordinates(
    value: object,
    path: str,
) -> EmpLocationCoordinates | None:
    coordinates = _optional_typed_object(value, path)
    if coordinates is None:
        return None
    return EmpLocationCoordinates(
        latitude=_nullable_string(coordinates.get("latitude"), f"{path}.latitude"),
        longitude=_nullable_string(coordinates.get("longitude"), f"{path}.longitude"),
    )


def _parse_emp_evses(
    value: object,
    path: str,
) -> tuple[EmpEvse | None, ...] | None:
    raw_evses = _nullable_list(value, path)
    if raw_evses is None:
        return None
    evses: list[EmpEvse | None] = []
    for index, raw_evse in enumerate(raw_evses):
        if raw_evse is None:
            evses.append(None)
            continue
        evses.append(_parse_emp_evse(raw_evse, f"{path}[{index}]"))
    return tuple(evses)


def _parse_emp_evse(value: object, path: str) -> EmpEvse:
    evse = _typed_object(value, path)
    capabilities = _parse_nullable_string_items(
        evse.get("evseCapability"),
        f"{path}.evseCapability",
    )
    raw_connectors = _nullable_list(evse.get("connector"), f"{path}.connector")
    connectors: tuple[EmpConnector | None, ...] | None = None
    if raw_connectors is not None:
        parsed_connectors: list[EmpConnector | None] = []
        for index, raw_connector in enumerate(raw_connectors):
            if raw_connector is None:
                parsed_connectors.append(None)
                continue
            parsed_connectors.append(
                _parse_emp_connector(raw_connector, f"{path}.connector[{index}]")
            )
        connectors = tuple(parsed_connectors)

    return EmpEvse(
        evse_id=_nullable_string(evse.get("evseId"), f"{path}.evseId"),
        evse_location_id=_nullable_string(
            evse.get("evseLocationId"),
            f"{path}.evseLocationId",
        ),
        evse_status=_nullable_enum(
            evse.get("evseStatus"),
            EmpEvseStatus,
            f"{path}.evseStatus",
        ),
        evse_capability=capabilities,
        evse_physical_reference=_nullable_string(
            evse.get("evsePhysicalReference"),
            f"{path}.evsePhysicalReference",
        ),
        connectors=connectors,
    )


def _parse_emp_connector(value: object, path: str) -> EmpConnector:
    connector = _typed_object(value, path)
    return EmpConnector(
        connector_id=_nullable_string(connector.get("connectorId"), f"{path}.connectorId"),
        connector_type=_nullable_string(
            connector.get("connectorType"),
            f"{path}.connectorType",
        ),
        connector_power_rating=_nullable_string(
            connector.get("connectorPowerRating"),
            f"{path}.connectorPowerRating",
        ),
        connector_description=_nullable_string(
            connector.get("connectorDescription"),
            f"{path}.connectorDescription",
        ),
    )


def _parse_shareable_capability_group(
    value: object,
    path: str,
) -> ShareableCapabilityGroup:
    group = _typed_object(value, path)
    raw_capabilities = _list(group.get("capabilities"), f"{path}.capabilities")
    capabilities: list[ShareableCapability | None] = []
    for index, raw_capability in enumerate(raw_capabilities):
        if raw_capability is None:
            capabilities.append(None)
            continue
        item_path = f"{path}.capabilities[{index}]"
        capability = _typed_object(raw_capability, item_path)
        capabilities.append(
            ShareableCapability(
                id=_string(capability.get("id"), f"{item_path}.id"),
                name=_nullable_string(capability.get("name"), f"{item_path}.name"),
                shareable=_nullable_bool(
                    capability.get("shareable"),
                    f"{item_path}.shareable",
                ),
            )
        )
    return ShareableCapabilityGroup(
        id=_string(group.get("id"), f"{path}.id"),
        name=_nullable_string(group.get("name"), f"{path}.name"),
        shared=_nullable_bool(group.get("shared"), f"{path}.shared"),
        capabilities=tuple(capabilities),
    )


def _parse_tariff_pricing_data(
    value: Mapping[str, object],
    path: str,
) -> TariffPricingData:
    raw_details = _nullable_list(value.get("tariffDetails"), f"{path}.tariffDetails")
    details: tuple[TariffDetail | None, ...] | None = None
    if raw_details is not None:
        parsed_details: list[TariffDetail | None] = []
        for index, raw_detail in enumerate(raw_details):
            if raw_detail is None:
                parsed_details.append(None)
                continue
            parsed_details.append(
                _parse_tariff_detail(raw_detail, f"{path}.tariffDetails[{index}]")
            )
        details = tuple(parsed_details)
    return TariffPricingData(
        location_id=_nullable_string(value.get("locationId"), f"{path}.locationId"),
        max_charge_limit=_nullable_string(
            value.get("maxChargeLimit"),
            f"{path}.maxChargeLimit",
        ),
        tariff_details=details,
    )


def _parse_tariff_detail(value: object, path: str) -> TariffDetail:
    detail = _typed_object(value, path)
    return TariffDetail(
        connector_type=_nullable_string(
            detail.get("connectorType"),
            f"{path}.connectorType",
        ),
        connector_power=_nullable_string(
            detail.get("connectorPower"),
            f"{path}.connectorPower",
        ),
        session_fee=_nullable_string(detail.get("sessionFee"), f"{path}.sessionFee"),
        alternative_text=_parse_optional_tariff_text(
            detail.get("tariffAltText"),
            f"{path}.tariffAltText",
        ),
        idle_fees=_parse_optional_idle_fees(detail.get("idleFees"), f"{path}.idleFees"),
        congestion_fees=_parse_optional_congestion_fees(
            detail.get("congestionFees"),
            f"{path}.congestionFees",
        ),
        energy_fees=_parse_optional_energy_fees(
            detail.get("energyFees"),
            f"{path}.energyFees",
        ),
    )


def _parse_optional_tariff_text(
    value: object,
    path: str,
) -> TariffLocalizedText | None:
    text = _optional_typed_object(value, path)
    if text is None:
        return None
    return TariffLocalizedText(
        en=_nullable_string(text.get("en"), f"{path}.en"),
        fr=_nullable_string(text.get("fr"), f"{path}.fr"),
    )


def _parse_optional_idle_fees(value: object, path: str) -> TariffIdleFees | None:
    fees = _optional_typed_object(value, path)
    if fees is None:
        return None
    raw_tiers = _nullable_list(fees.get("idleFeesTier"), f"{path}.idleFeesTier")
    tiers: tuple[TariffIdleFeeTier | None, ...] | None = None
    if raw_tiers is not None:
        parsed_tiers: list[TariffIdleFeeTier | None] = []
        for index, raw_tier in enumerate(raw_tiers):
            if raw_tier is None:
                parsed_tiers.append(None)
                continue
            parsed_tiers.append(_parse_idle_fee_tier(raw_tier, f"{path}.idleFeesTier[{index}]"))
        tiers = tuple(parsed_tiers)
    return TariffIdleFees(
        grace_period=_nullable_string(fees.get("gracePeriod"), f"{path}.gracePeriod"),
        tiers=tiers,
    )


def _parse_idle_fee_tier(value: object, path: str) -> TariffIdleFeeTier:
    tier = _typed_object(value, path)
    return TariffIdleFeeTier(
        congestion_level=_nullable_string(
            tier.get("congestionLevel"),
            f"{path}.congestionLevel",
        ),
        time_start=_nullable_string(tier.get("timeStart"), f"{path}.timeStart"),
        time_end=_nullable_string(tier.get("timeEnd"), f"{path}.timeEnd"),
        duration_start=_nullable_string(
            tier.get("durationStart"),
            f"{path}.durationStart",
        ),
        duration_end=_nullable_string(tier.get("durationEnd"), f"{path}.durationEnd"),
        duration_unit=_nullable_string(tier.get("durationUnit"), f"{path}.durationUnit"),
        price=_nullable_string(tier.get("price"), f"{path}.price"),
        unit=_nullable_string(tier.get("unit"), f"{path}.unit"),
    )


def _parse_optional_congestion_fees(
    value: object,
    path: str,
) -> TariffCongestionFees | None:
    fees = _optional_typed_object(value, path)
    if fees is None:
        return None
    raw_tiers = _nullable_list(fees.get("congestionTier"), f"{path}.congestionTier")
    tiers: tuple[TariffCongestionFeeTier | None, ...] | None = None
    if raw_tiers is not None:
        parsed_tiers: list[TariffCongestionFeeTier | None] = []
        for index, raw_tier in enumerate(raw_tiers):
            if raw_tier is None:
                parsed_tiers.append(None)
                continue
            parsed_tiers.append(
                _parse_congestion_fee_tier(raw_tier, f"{path}.congestionTier[{index}]")
            )
        tiers = tuple(parsed_tiers)
    return TariffCongestionFees(
        grace_period=_nullable_string(fees.get("gracePeriod"), f"{path}.gracePeriod"),
        tiers=tiers,
    )


def _parse_congestion_fee_tier(
    value: object,
    path: str,
) -> TariffCongestionFeeTier:
    tier = _typed_object(value, path)
    return TariffCongestionFeeTier(
        congestion_level=_nullable_string(
            tier.get("congestionLevel"),
            f"{path}.congestionLevel",
        ),
        vehicle_soc_limit=_nullable_string(
            tier.get("vehicleSOCLimit"),
            f"{path}.vehicleSOCLimit",
        ),
        price=_nullable_string(tier.get("price"), f"{path}.price"),
        unit=_nullable_string(tier.get("unit"), f"{path}.unit"),
    )


def _parse_optional_energy_fees(value: object, path: str) -> TariffEnergyFees | None:
    fees = _optional_typed_object(value, path)
    if fees is None:
        return None
    raw_tiers = _nullable_list(fees.get("energyFeeTier"), f"{path}.energyFeeTier")
    tiers: tuple[TariffEnergyFeeTier | None, ...] | None = None
    if raw_tiers is not None:
        parsed_tiers: list[TariffEnergyFeeTier | None] = []
        for index, raw_tier in enumerate(raw_tiers):
            if raw_tier is None:
                parsed_tiers.append(None)
                continue
            parsed_tiers.append(_parse_energy_fee_tier(raw_tier, f"{path}.energyFeeTier[{index}]"))
        tiers = tuple(parsed_tiers)
    return TariffEnergyFees(tiers=tiers)


def _parse_energy_fee_tier(value: object, path: str) -> TariffEnergyFeeTier:
    tier = _typed_object(value, path)
    applicable_day = _parse_nullable_int_items(
        tier.get("applicableDay"),
        f"{path}.applicableDay",
    )
    return TariffEnergyFeeTier(
        applicable_day=applicable_day,
        time_start=_nullable_string(tier.get("timeStart"), f"{path}.timeStart"),
        time_end=_nullable_string(tier.get("timeEnd"), f"{path}.timeEnd"),
        duration_start=_nullable_string(
            tier.get("durationStart"),
            f"{path}.durationStart",
        ),
        duration_end=_nullable_string(tier.get("durationEnd"), f"{path}.durationEnd"),
        duration_unit=_nullable_string(tier.get("durationUnit"), f"{path}.durationUnit"),
        min_range=_nullable_string(tier.get("minRange"), f"{path}.minRange"),
        max_range=_nullable_string(tier.get("maxRange"), f"{path}.maxRange"),
        range_unit=_nullable_string(tier.get("rangeUnit"), f"{path}.rangeUnit"),
        price=_nullable_string(tier.get("price"), f"{path}.price"),
        unit=_nullable_string(tier.get("unit"), f"{path}.unit"),
    )


def _parse_nullable_string_items(
    value: object,
    path: str,
) -> tuple[str | None, ...] | None:
    values = _nullable_list(value, path)
    if values is None:
        return None
    return tuple(_nullable_string(item, f"{path}[{index}]") for index, item in enumerate(values))


def _parse_nullable_int_items(
    value: object,
    path: str,
) -> tuple[int | None, ...] | None:
    values = _nullable_list(value, path)
    if values is None:
        return None
    return tuple(_nullable_int(item, f"{path}[{index}]") for index, item in enumerate(values))


def _vehicle(data: Mapping[str, object]) -> Mapping[str, object] | None:
    if "vehicle" not in data:
        raise ResponseError("vehicle is missing")
    return _optional_typed_object(data.get("vehicle"), "vehicle")


def _object(value: object, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ResponseError(f"{path} is not an object")
    return value


def _typed_object(value: object, path: str) -> Mapping[str, object]:
    result = _object(value, path)
    _string(result.get("__typename"), f"{path}.__typename")
    return result


def _optional_typed_object(
    value: object,
    path: str,
) -> Mapping[str, object] | None:
    if value is None:
        return None
    return _typed_object(value, path)


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


def _enum[EnumT: StrEnum](
    value: object,
    enum_type: type[EnumT],
    path: str,
) -> EnumT:
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


def _nullable_datetime(value: object, path: str) -> datetime | None:
    if value is None:
        return None
    raw_value = _string(value, path)
    normalized = f"{raw_value[:-1]}+00:00" if raw_value.endswith("Z") else raw_value
    try:
        result = datetime.fromisoformat(normalized)
    except ValueError as error:
        raise ResponseError(f"{path} is not an ISO-8601 date-time") from error
    if result.tzinfo is None or result.utcoffset() is None:
        raise ResponseError(f"{path} is not an ISO-8601 date-time with an offset")
    return result
