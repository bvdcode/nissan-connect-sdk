from __future__ import annotations

from ._extended_vehicle_value_parsing import (
    _nullable_bool,
    _nullable_enum,
    _nullable_float,
    _nullable_int,
    _nullable_list,
    _nullable_string,
    _optional_typed_object,
    _parse_nullable_string_items,
    _typed_object,
)
from .extended_vehicle_models import (
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
)
from .navigation_inputs import PlugConnectorType


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
