"""Availability of remote commands by vehicle and service subscription."""

import pytest

from pynissan import ServiceCapability, VehicleCapabilities
from pynissan.parsing import parse_vehicle_capabilities


@pytest.mark.parametrize(
    ("enabled", "subscribed", "expected"),
    [
        (True, True, True),
        (False, True, False),
        (True, False, False),
        (True, None, False),
        (False, None, False),
    ],
)
def test_available_service(enabled: bool, subscribed: bool | None, expected: bool) -> None:
    service = ServiceCapability("REMOTE_DOOR_LOCK_UNLOCK", enabled, subscribed)
    capabilities = VehicleCapabilities("VIN", None, None, (service,))
    assert service.is_available is expected
    assert capabilities.supports_service(service.type) is expected
    assert capabilities.can_lock_doors is expected
    assert capabilities.can_unlock_doors is expected
    assert capabilities.can_flash_lights is False


@pytest.mark.parametrize(
    ("services", "lock", "unlock", "lights"),
    [
        ((), False, False, False),
        (("REMOTE_DOOR_LOCK_UNLOCK",), True, True, False),
        (("REMOTE_DOOR_LOCK",), True, False, False),
        (("REMOTE_DOOR_UNLOCK",), False, True, False),
        (("REMOTE_DOOR_LOCK", "REMOTE_DOOR_UNLOCK"), True, True, False),
        (("REMOTE_HORN_LIGHTS",), False, False, True),
        (("UNKNOWN__",), False, False, False),
    ],
)
def test_directional_command_support(
    services: tuple[str, ...], lock: bool, unlock: bool, lights: bool
) -> None:
    capabilities = VehicleCapabilities(
        "VIN", None, None, tuple(ServiceCapability(service, True, True) for service in services)
    )
    assert capabilities.can_lock_doors is lock
    assert capabilities.can_unlock_doors is unlock
    assert capabilities.can_flash_lights is lights
    assert capabilities.can_flash_lights_and_horn is lights
    assert capabilities.supports_service("UNKNOWN_SERVICE") is False


@pytest.mark.parametrize("subscribed", [False, None])
def test_unsubscribed_lights(subscribed: bool | None) -> None:
    capabilities = VehicleCapabilities(
        "VIN", None, None, (ServiceCapability("REMOTE_HORN_LIGHTS", True, subscribed),)
    )
    assert capabilities.can_flash_lights is False
    assert capabilities.can_flash_lights_and_horn is False


def test_parsed_capabilities_expose_support() -> None:
    capabilities = parse_vehicle_capabilities(
        {
            "vehicle": {
                "capabilities": {
                    "serviceCapability": [
                        {"type": "REMOTE_DOOR_UNLOCK", "enabled": True, "subscribed": True},
                        {"type": "REMOTE_DOOR_LOCK", "enabled": True, "subscribed": False},
                    ]
                }
            }
        },
        "VIN",
    )
    assert capabilities.can_lock_doors is False
    assert capabilities.can_unlock_doors is True
    assert capabilities.can_flash_lights is False
    assert (
        parse_vehicle_capabilities({"vehicle": {"capabilities": None}}, "VIN").can_lock_doors
        is False
    )
