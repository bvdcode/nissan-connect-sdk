"""Charging estimates derived from reported battery status."""

from datetime import UTC, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from pynissan import BatteryStatus
from pynissan.parsing import parse_vehicle_status


@pytest.mark.parametrize(
    ("charging", "minutes", "duration"),
    [
        (True, 125, timedelta(hours=2, minutes=5)),
        (True, 0, timedelta(0)),
        (True, None, None),
        (True, -1, None),
        (False, 125, None),
        (None, 125, None),
    ],
)
def test_remaining_charge_duration(
    charging: bool | None, minutes: int | None, duration: timedelta | None
) -> None:
    battery = BatteryStatus(50, True, charging, minutes, None)
    assert battery.remaining_charge_duration == duration
    assert battery.remaining_charge_time == minutes
    observed_at = datetime(2026, 10, 30, 23, 30, tzinfo=UTC)
    estimate = battery.estimate_charge_completion(observed_at)
    if duration is None:
        assert estimate is None
    else:
        assert estimate == observed_at + duration


def test_estimate_uses_explicit_observation_time() -> None:
    battery = BatteryStatus(50, True, True, 125, None)
    observed_at = datetime(2026, 10, 30, 23, 30, tzinfo=timezone(timedelta(hours=-7)))
    expected = datetime(2026, 10, 31, 1, 35, tzinfo=observed_at.tzinfo)
    assert battery.estimate_charge_completion(observed_at) == expected
    assert battery.estimate_charge_completion(observed_at) == expected


def test_estimate_requires_timezone() -> None:
    battery = BatteryStatus(50, True, True, 125, None)
    with pytest.raises(ValueError, match="timezone-aware"):
        battery.estimate_charge_completion(datetime(2026, 10, 30, 12))


@pytest.mark.parametrize(
    ("month", "day", "expected_utc"),
    [
        (3, 8, datetime(2026, 3, 8, 10, 30, tzinfo=UTC)),
        (11, 1, datetime(2026, 11, 1, 9, 30, tzinfo=UTC)),
    ],
)
def test_estimate_uses_elapsed_time_across_dst(
    month: int, day: int, expected_utc: datetime
) -> None:
    battery = BatteryStatus(50, True, True, 60, None)
    observed_at = datetime(2026, month, day, 1, 30, tzinfo=ZoneInfo("America/Los_Angeles"))
    completion = battery.estimate_charge_completion(observed_at)
    assert completion is not None
    assert completion.astimezone(UTC) == expected_utc


def test_parsed_battery_exposes_estimate() -> None:
    status = parse_vehicle_status(
        {
            "vehicle": {
                "batteryStatus": {
                    "level": 50,
                    "isPluggedIn": True,
                    "isCharging": True,
                    "remainingChargeTime": 30,
                }
            }
        },
        "VIN",
    )
    assert status.battery is not None
    observed_at = datetime(2026, 10, 30, 12, tzinfo=UTC)
    assert status.battery.estimate_charge_completion(observed_at) == datetime(
        2026, 10, 30, 12, 30, tzinfo=UTC
    )
