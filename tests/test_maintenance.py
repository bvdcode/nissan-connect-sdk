from __future__ import annotations

from collections.abc import Mapping

EXPECTED_OPERATION_IDS = {
    "GET_MAINTENANCE_TIMELINE": (
        "6bad114fbfd471b87bd47b5648b5f0637a93d0c23bd2eb6d274a39550dcf32d8"
    ),
    "GET_SERVICE_CONTRACTS": ("e962736c9aae011b2a36e6e58389149f31918e7857ce18600764875de90119ed"),
    "ADD_PAST_SERVICE": ("cafadb5455f97421a20e39cd512e4f6d330571bec51ead159d4475b4dcd232f4"),
    "UPDATE_PAST_SERVICE": ("fa9c97a384127dffe11abb854538bfa76f8d21420c043c4414a2fef348586b7b"),
    "PARTS_REMINDERS": ("4b5fb536d6007cd8c5f17a64a93dc6511ae69954c522f211ca4d42a69b0aeb7b"),
    "CREATE_PARTS_REMINDER": ("488ccc2a7e7a0af3112ab1a91ce224e2c83f7dbcdcf824df99049fdf0ab607f4"),
    "UPDATE_PARTS_REMINDER": ("08531ffe6e151b3bf7c8b6f33d04ca3408232f0c83bc743948e9dda9b2efd5ce"),
    "RESET_PARTS_REMINDER": ("2e015a323d69646298637c701cc5fb6842dfdb9e295ac18a6b93b68d9b582ea5"),
    "DELETE_PARTS_REMINDER": ("237b3f40451ba30e043a8b0b1dccd679bfd389924c16e1026c15ebdf10542b77"),
    "COLLISION_HISTORY": ("ca2779551c7312455dbe80dce6dac3199494f71a1010f53bc211616ce8776622"),
    "COLLISION_PROBE_DATA": ("f151d6ce54b3bc683412838ff8ce6460e06874e61a671da481d7d6238723c547"),
}


def vehicle_data(
    *,
    typename: str = "ElectricAVK2Vehicle",
    **fields: object,
) -> dict[str, object]:
    return {"vehicle": {"__typename": typename, **fields}}


def service_contract(**overrides: object) -> dict[str, object]:
    result: dict[str, object] = {
        "__typename": "WarrantyServiceContract",
        "status": "ACTIVE",
        "coverage": "FULL",
        "coverageDescription": "Scheduled maintenance",
        "coverageName": "Maintenance Care",
        "planEffectiveDate": "2025-01-02",
        "planEffectiveMiles": 10,
        "planExpirationDate": "2028-01-02",
        "planExpirationOdometer": 36010,
        "planCancelledDate": None,
        "planCancelledOdometer": None,
        "agreement": "AG-1",
        "deductibleAmount": 25,
        "expiringSoon": False,
    }
    result.update(overrides)
    return result


def configuration_thresholds(**overrides: object) -> dict[str, object]:
    result: dict[str, object] = {
        "__typename": "PartsReminderConfigurationThresholds",
        "min": 1,
        "max": 24,
        "interval": 1,
        "distanceUnit": "MILE",
    }
    result.update(overrides)
    return result


def part(**overrides: object) -> dict[str, object]:
    result: dict[str, object] = {
        "__typename": "Part",
        "id": "engine-air-filter",
        "name": "Engine air filter",
        "reminderConfiguration": {
            "__typename": "PartReminderConfiguration",
            "months": configuration_thresholds(),
            "distance": configuration_thresholds(
                min=500,
                max=30000,
                interval=500,
                distanceUnit="MILE",
            ),
        },
    }
    result.update(overrides)
    return result


def reminder_distance(value: int = 12000) -> dict[str, object]:
    return {"__typename": "Distance", "unit": "MILE", "value": value}


def parts_reminder(**overrides: object) -> dict[str, object]:
    result: dict[str, object] = {
        "__typename": "PartsReminder",
        "id": "reminder-1",
        "overdue": True,
        "date": "2026-07-30T10:20:30Z",
        "monthsInterval": 6,
        "distanceInterval": reminder_distance(5000),
        "nextReminderDistance": reminder_distance(17000),
        "nextReminderDate": "2027-01-30T10:20:30-08:00",
        "status": "OVERDUE",
        "parts": [part()],
        "mileage": reminder_distance(),
    }
    result.update(overrides)
    return result


def collision_probe_reading(**overrides: object) -> dict[str, object]:
    result: dict[str, object] = {
        "__typename": "CollisionProbeReading",
        "collisionTime": "2026-07-29T01:02:03Z",
        "latitude": 32.7157,
        "longitude": -117.1611,
        "milCount": 2,
        "milData": "P0001,P0002",
        "odometer": 12345.5,
        "speed": 21.25,
        "unit": "MILE",
    }
    result.update(overrides)
    return result


def without_field(value: Mapping[str, object], field: str) -> dict[str, object]:
    result = dict(value)
    del result[field]
    return result
