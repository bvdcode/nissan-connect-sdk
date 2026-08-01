from __future__ import annotations

import pytest

from pynissan import ResponseError
from pynissan.extended_vehicle_parsing import (
    parse_driving_history,
    parse_e_vehicle_eligibility,
    parse_last_known_camera_usage_counter,
    parse_location_details,
    parse_shareable_capabilities,
    parse_tariff_pricing,
)


def test_non_null_driving_history_and_shareable_lists_are_enforced() -> None:
    with pytest.raises(ResponseError, match=r"tripSummaries is not a list"):
        parse_driving_history(
            {
                "vehicle": {
                    "__typename": "ElectricVehicle",
                    "drivingHistory": {
                        "__typename": "DrivingHistory",
                        "tripSummaries": None,
                        "trips": [],
                    },
                }
            }
        )

    with pytest.raises(ResponseError, match=r"tripSummaries\[0\] is not an object"):
        parse_driving_history(
            {
                "vehicle": {
                    "__typename": "ElectricVehicle",
                    "drivingHistory": {
                        "__typename": "DrivingHistory",
                        "tripSummaries": [None],
                        "trips": [],
                    },
                }
            }
        )

    with pytest.raises(ResponseError, match=r"shareableCapabilities.group is not a list"):
        parse_shareable_capabilities(
            {
                "vehicle": {
                    "__typename": "AVK2Vehicle",
                    "shareableCapabilities": {
                        "__typename": "ShareableCapabilities",
                        "group": None,
                    },
                }
            }
        )

    with pytest.raises(ResponseError, match=r"capabilities is not a list"):
        parse_shareable_capabilities(
            {
                "vehicle": {
                    "__typename": "AVK2Vehicle",
                    "shareableCapabilities": {
                        "__typename": "ShareableCapabilities",
                        "group": [
                            {
                                "__typename": "CapabilityGroup",
                                "id": "group-1",
                                "name": None,
                                "shared": None,
                                "capabilities": None,
                            }
                        ],
                    },
                }
            }
        )


def test_nullable_nested_list_items_are_preserved() -> None:
    location_details = parse_location_details(
        {
            "locationDetails": {
                "__typename": "LocationDetailsResponse",
                "statusCode": None,
                "statusMessage": None,
                "timestamp": None,
                "data": [
                    {
                        "__typename": "LocationData",
                        "evses": [
                            {
                                "__typename": "Evse",
                                "evseCapability": [None, "REMOTE_START"],
                            }
                        ],
                    }
                ],
            }
        }
    )
    assert location_details is not None
    assert location_details.data is not None
    location = location_details.data[0]
    assert location is not None
    assert location.evses is not None
    evse = location.evses[0]
    assert evse is not None
    assert evse.evse_capability == (None, "REMOTE_START")

    tariff_pricing = parse_tariff_pricing(
        {
            "tariffPricing": {
                "__typename": "TariffPricingResponse",
                "statusCode": None,
                "statusMessage": None,
                "timestamp": None,
                "data": {
                    "__typename": "TariffPricingData",
                    "tariffDetails": [
                        {
                            "__typename": "TariffDetail",
                            "energyFees": {
                                "__typename": "EnergyFees",
                                "energyFeeTier": [
                                    {
                                        "__typename": "EnergyFeeTier",
                                        "applicableDay": [1, None],
                                    }
                                ],
                            },
                        }
                    ],
                },
            }
        }
    )
    assert tariff_pricing is not None
    assert tariff_pricing.data is not None
    assert tariff_pricing.data.tariff_details is not None
    detail = tariff_pricing.data.tariff_details[0]
    assert detail is not None
    assert detail.energy_fees is not None
    assert detail.energy_fees.tiers is not None
    tier = detail.energy_fees.tiers[0]
    assert tier is not None
    assert tier.applicable_day == (1, None)


def test_extended_parsers_reject_naive_datetime_and_wrong_nullable_scalar_type() -> None:
    with pytest.raises(ResponseError, match="date-time with an offset"):
        parse_last_known_camera_usage_counter(
            {
                "vehicle": {
                    "__typename": "AVK2Vehicle",
                    "lastKnownCameraUsageCounter": {
                        "__typename": "CameraUsageCounter",
                        "counter": None,
                        "lastUpdateTime": "2026-07-31T19:30:00",
                    },
                }
            }
        )

    with pytest.raises(ResponseError, match=r"statusCode is not a string"):
        parse_e_vehicle_eligibility(
            {
                "eVehicleEligibility": {
                    "__typename": "EVehicleEligibilityResponse",
                    "statusCode": 1000,
                    "statusMessage": None,
                    "timestamp": None,
                    "data": None,
                }
            }
        )
