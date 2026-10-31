"""Vehicle telemetry and normalized status values."""

from dataclasses import replace

import pytest

from pynissan import DoorState
from pynissan.parsing import parse_vehicle_status, parse_vehicles


def vehicle_payload() -> dict[str, object]:
    return {
        "__typename": "ElectricAVK2Vehicle",
        "mileage": {"total": 12345, "unit": "KILOMETER", "recordedTime": None},
        "tirePressure": {
            "flPressure": 35,
            "frPressure": 36,
            "rlPressure": 37,
            "rrPressure": 38,
        },
        "doorsStatus": {
            "doorFrontLeft": {"ajar": "OPEN", "lock": "UNLOCKED"},
            "doorFrontRight": {"ajar": "CLOSED", "lock": "LOCKED"},
            "doorRearLeft": {"ajar": "CLOSED", "lock": "UNLOCKED"},
            "doorRearRight": {"ajar": "OPEN", "lock": "LOCKED"},
            "engineHood": {"ajar": "OPEN"},
            "hatch": {"ajar": "CLOSED"},
            "trunk": {"lock": "LOCKED"},
            "overallLock": {"lock": "UNLOCKED"},
        },
        "mils": [
            {"active": True, "detailedMessage": "Check tire pressure", "type": "TIRE"},
            {"active": False, "detailedMessage": "Inactive", "type": "OTHER"},
            {"active": None, "detailedMessage": "Unknown", "type": "UNKNOWN"},
            {"active": True, "detailedMessage": None, "type": "SERVICE"},
        ],
    }


def test_vehicle_telemetry() -> None:
    status = parse_vehicle_status({"vehicle": vehicle_payload()}, "VIN")
    assert status.mileage is not None
    assert status.mileage.total == 12345
    assert status.mileage.unit == "KILOMETER"
    tires = status.tire_pressure
    assert tires is not None
    assert tires.unit == "psi"
    assert (tires.front_left, tires.front_right, tires.rear_left, tires.rear_right) == (
        35,
        36,
        37,
        38,
    )
    doors = status.doors
    assert doors is not None
    for door, opened, locked in (
        (doors.front_left, True, False),
        (doors.front_right, False, True),
        (doors.rear_left, False, False),
        (doors.rear_right, True, True),
    ):
        assert door is not None
        assert door.is_open is opened
        assert door.is_locked is locked
    assert doors.is_locked is False
    assert doors.is_trunk_locked is True
    assert doors.is_trunk_open is False
    assert doors.is_hood_open is True
    assert status.warning_count == 2
    assert status.warning_messages == ("Check tire pressure",)
    assert tuple(item.type for item in status.active_warnings) == ("TIRE", "SERVICE")
    assert len(status.maintenance_indicators) == 4


@pytest.mark.parametrize("value", [None, "UNKNOWN__", "NEW_STATE"])
def test_unknown_states_stay_unknown(value: str | None) -> None:
    door = DoorState(value, None, value)
    assert door.is_open is None
    assert door.is_locked is None
    assert door.ajar == value and door.lock == value
    status = parse_vehicle_status({"vehicle": vehicle_payload()}, "VIN")
    assert status.doors is not None
    doors = replace(
        status.doors, overall_lock=value, trunk_lock=value, hatch_ajar=value, engine_hood_ajar=value
    )
    assert doors.is_locked is None
    assert doors.is_trunk_locked is None
    assert doors.is_trunk_open is None
    assert doors.is_hood_open is None


def test_partial_data_remains_nullable() -> None:
    status = parse_vehicle_status({"vehicle": {"tirePressure": {"flPressure": 35}}}, "VIN")
    assert status.mileage is None
    assert status.doors is None
    assert status.tire_pressure is not None
    assert status.tire_pressure.front_left == 35
    assert status.tire_pressure.front_right is None
    assert status.tire_pressure.rear_left is None
    assert status.tire_pressure.rear_right is None
    assert status.warning_count == 0
    assert status.active_warnings == ()
    assert status.warning_messages == ()


def test_warning_messages_are_preserved() -> None:
    message = "Detailed warning " * 50
    payload = vehicle_payload()
    payload["mils"] = [{"active": True, "detailedMessage": message, "type": "SERVICE"}]
    status = parse_vehicle_status({"vehicle": payload}, "VIN")
    assert status.warning_count == 1
    assert status.warning_messages == (message,)


@pytest.mark.parametrize("image", [None, "https://example.test/vehicle.png"])
def test_vehicle_image(image: str | None) -> None:
    vehicles = parse_vehicles({"vehicles": [{"vin": "VIN", "image": image}]})
    assert vehicles[0].image_url == image
