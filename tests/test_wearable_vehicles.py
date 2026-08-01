from __future__ import annotations

import hashlib
import re
from collections.abc import Callable, Mapping

import pytest

from pynissan import operations
from pynissan.exceptions import ResponseError
from pynissan.models import ServiceCapability
from pynissan.wearable_models import (
    VehicleCapabilitySummary,
    VehicleWithCapabilities,
)
from pynissan.wearable_parsing import parse_vehicles_with_capabilities

EXPECTED_DOCUMENT = (
    "query WearableVehicles { vehicles { "
    "__typename vin nickname image year model driverType capabilities { "
    "__typename telematicsProgram status serviceCapability { "
    "__typename type enabled subscribed "
    "} } } }"
)
EXPECTED_OPERATION_ID = "ba7b89a00f05ce82ede35558ebf0464d3f22cd2c9b0b5559a4a2f587a9b843db"


def _vehicle_payload() -> dict[str, object]:
    return {
        "__typename": "BaseElectric2Vehicle",
        "vin": "JN1DF0CD0RM000001",
        "nickname": "Ariya",
        "image": "https://example.invalid/ariya.png",
        "year": "2024",
        "model": "ARIYA",
        "driverType": "PRIMARY",
        "capabilities": {
            "__typename": "VehicleCapability",
            "telematicsProgram": "NNA_EV",
            "status": "ENROLLED",
            "serviceCapability": [
                {
                    "__typename": "ServiceCapability",
                    "type": "REMOTE_CLIMATE_CONTROL",
                    "enabled": True,
                    "subscribed": None,
                },
                None,
            ],
        },
    }


def test_wearable_vehicles_operation_matches_service_document_and_id() -> None:
    assert operations.WEARABLE_VEHICLES == EXPECTED_DOCUMENT
    assert operations.WEARABLE_VEHICLES_OPERATION_ID == EXPECTED_OPERATION_ID
    assert (
        hashlib.sha256(operations.WEARABLE_VEHICLES.encode()).hexdigest() == EXPECTED_OPERATION_ID
    )

    tokens = re.findall(
        r"\.\.\.|[_A-Za-z][_0-9A-Za-z]*|[$!():{}\[\]]",
        operations.WEARABLE_VEHICLES,
    )
    assert hashlib.sha256(" ".join(tokens).encode()).hexdigest() == EXPECTED_OPERATION_ID


def test_parse_wearable_vehicles_preserves_exact_response_shape() -> None:
    result = parse_vehicles_with_capabilities({"vehicles": [_vehicle_payload()]})

    assert result == (
        VehicleWithCapabilities(
            vin="JN1DF0CD0RM000001",
            nickname="Ariya",
            image_url="https://example.invalid/ariya.png",
            year="2024",
            model="ARIYA",
            driver_type="PRIMARY",
            capabilities=VehicleCapabilitySummary(
                telematics_program="NNA_EV",
                enrollment_status="ENROLLED",
                services=(
                    ServiceCapability(
                        type="REMOTE_CLIMATE_CONTROL",
                        enabled=True,
                        subscribed=None,
                    ),
                    None,
                ),
            ),
        ),
    )


def test_parse_wearable_vehicles_preserves_future_enum_values() -> None:
    vehicle = _vehicle_payload()
    vehicle["driverType"] = "FUTURE_DRIVER"
    capabilities = vehicle["capabilities"]
    assert isinstance(capabilities, dict)
    capabilities["telematicsProgram"] = "FUTURE_PROGRAM"
    capabilities["status"] = "FUTURE_STATUS"
    services = capabilities["serviceCapability"]
    assert isinstance(services, list)
    service = services[0]
    assert isinstance(service, dict)
    service["type"] = "FUTURE_SERVICE"

    result = parse_vehicles_with_capabilities({"vehicles": [vehicle]})

    assert result is not None
    parsed_vehicle = result[0]
    assert parsed_vehicle is not None
    assert parsed_vehicle.driver_type == "FUTURE_DRIVER"
    assert parsed_vehicle.capabilities is not None
    assert parsed_vehicle.capabilities.telematics_program == "FUTURE_PROGRAM"
    assert parsed_vehicle.capabilities.enrollment_status == "FUTURE_STATUS"
    assert parsed_vehicle.capabilities.services is not None
    parsed_service = parsed_vehicle.capabilities.services[0]
    assert parsed_service is not None
    assert parsed_service.type == "FUTURE_SERVICE"


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ({"vehicles": None}, None),
        ({"vehicles": []}, ()),
        ({"vehicles": [None]}, (None,)),
    ],
)
def test_parse_wearable_vehicles_preserves_nullable_root_list_and_items(
    payload: Mapping[str, object],
    expected: tuple[VehicleWithCapabilities | None, ...] | None,
) -> None:
    assert parse_vehicles_with_capabilities(payload) == expected


def test_parse_wearable_vehicle_preserves_nullable_vehicle_fields() -> None:
    vehicle = _vehicle_payload()
    vehicle["nickname"] = None
    vehicle["driverType"] = None
    vehicle["capabilities"] = None

    result = parse_vehicles_with_capabilities({"vehicles": [vehicle]})

    assert result is not None
    parsed_vehicle = result[0]
    assert parsed_vehicle is not None
    assert parsed_vehicle.nickname is None
    assert parsed_vehicle.driver_type is None
    assert parsed_vehicle.capabilities is None


@pytest.mark.parametrize("service_capability", [None, []])
def test_parse_wearable_vehicle_preserves_nullable_and_empty_service_lists(
    service_capability: object,
) -> None:
    vehicle = _vehicle_payload()
    capabilities = vehicle["capabilities"]
    assert isinstance(capabilities, dict)
    capabilities["serviceCapability"] = service_capability

    result = parse_vehicles_with_capabilities({"vehicles": [vehicle]})

    assert result is not None
    parsed_vehicle = result[0]
    assert parsed_vehicle is not None
    assert parsed_vehicle.capabilities is not None
    if service_capability is None:
        assert parsed_vehicle.capabilities.services is None
    else:
        assert parsed_vehicle.capabilities.services == ()


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("vin", None, "vehicles[0].vin is not a string"),
        ("image", None, "vehicles[0].image is not a string"),
        ("year", None, "vehicles[0].year is not a string"),
        ("model", None, "vehicles[0].model is not a string"),
        ("vin", 1, "vehicles[0].vin is not a string"),
        ("image", False, "vehicles[0].image is not a string"),
    ],
)
def test_parse_wearable_vehicle_rejects_missing_or_malformed_required_scalars(
    field: str,
    value: object,
    message: str,
) -> None:
    vehicle = _vehicle_payload()
    vehicle[field] = value

    with pytest.raises(ResponseError, match=re.escape(message)):
        parse_vehicles_with_capabilities({"vehicles": [vehicle]})


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda vehicle: vehicle["capabilities"].__setitem__(
                "telematicsProgram",
                None,
            ),
            "vehicles[0].capabilities.telematicsProgram is not a string",
        ),
        (
            lambda vehicle: vehicle["capabilities"].__setitem__("status", None),
            "vehicles[0].capabilities.status is not a string",
        ),
        (
            lambda vehicle: vehicle["capabilities"]["serviceCapability"][0].__setitem__(
                "type",
                None,
            ),
            "vehicles[0].capabilities.serviceCapability[0].type is not a string",
        ),
        (
            lambda vehicle: vehicle["capabilities"]["serviceCapability"][0].__setitem__(
                "enabled",
                None,
            ),
            "vehicles[0].capabilities.serviceCapability[0].enabled is not a boolean",
        ),
    ],
)
def test_parse_wearable_vehicle_rejects_malformed_capability_scalars(
    mutate: Callable[[dict[str, object]], None],
    message: str,
) -> None:
    vehicle = _vehicle_payload()
    mutate(vehicle)

    with pytest.raises(ResponseError, match=re.escape(message)):
        parse_vehicles_with_capabilities({"vehicles": [vehicle]})


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({}, "vehicles is missing"),
        ({"vehicles": {}}, "vehicles is not a list"),
        ({"vehicles": ["vehicle"]}, "vehicles[0] is not an object"),
    ],
)
def test_parse_wearable_vehicles_rejects_malformed_root(
    payload: Mapping[str, object],
    message: str,
) -> None:
    with pytest.raises(ResponseError, match=re.escape(message)):
        parse_vehicles_with_capabilities(payload)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda vehicle: vehicle.__setitem__("__typename", None),
            "vehicles[0].__typename is not a string",
        ),
        (
            lambda vehicle: vehicle.__setitem__("capabilities", "capabilities"),
            "vehicles[0].capabilities is not an object",
        ),
        (
            lambda vehicle: vehicle["capabilities"].__setitem__(
                "__typename",
                None,
            ),
            "vehicles[0].capabilities.__typename is not a string",
        ),
        (
            lambda vehicle: vehicle["capabilities"].__setitem__(
                "serviceCapability",
                {},
            ),
            "vehicles[0].capabilities.serviceCapability is not a list",
        ),
        (
            lambda vehicle: vehicle["capabilities"]["serviceCapability"].__setitem__(
                0,
                "service",
            ),
            "vehicles[0].capabilities.serviceCapability[0] is not an object",
        ),
        (
            lambda vehicle: vehicle["capabilities"]["serviceCapability"][0].__setitem__(
                "__typename",
                None,
            ),
            "vehicles[0].capabilities.serviceCapability[0].__typename is not a string",
        ),
        (
            lambda vehicle: vehicle["capabilities"]["serviceCapability"][0].__setitem__(
                "subscribed",
                "yes",
            ),
            "vehicles[0].capabilities.serviceCapability[0].subscribed is not a boolean",
        ),
    ],
)
def test_parse_wearable_vehicle_rejects_malformed_nested_shapes(
    mutate: Callable[[dict[str, object]], None],
    message: str,
) -> None:
    vehicle = _vehicle_payload()
    mutate(vehicle)

    with pytest.raises(ResponseError, match=re.escape(message)):
        parse_vehicles_with_capabilities({"vehicles": [vehicle]})
