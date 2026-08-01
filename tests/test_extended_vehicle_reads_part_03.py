from __future__ import annotations

from pynissan.extended_vehicle_models import (
    EmpEvseStatus,
    EmpLocationStatus,
)
from pynissan.extended_vehicle_parsing import (
    parse_driving_history,
    parse_e_vehicle_eligibility,
    parse_ev_charge_stations,
    parse_last_known_camera_usage_counter,
    parse_location_details,
    parse_parking_chargeable,
    parse_shareable_capabilities,
    parse_tariff_pricing,
)


def test_location_details_preserves_emp_status_and_nested_nullable_lists() -> None:
    details = parse_location_details(
        {
            "locationDetails": {
                "__typename": "LocationDetailsResponse",
                "statusCode": "1000",
                "statusMessage": None,
                "timestamp": "raw-location-timestamp",
                "data": [
                    None,
                    {
                        "__typename": "LocationData",
                        "locationId": "location-1",
                        "locationType": "FUTURE_LOCATION_TYPE",
                        "locationName": "Charging Plaza",
                        "locationLogo": None,
                        "locationOperatorName": "Operator",
                        "locationSubOperatorName": None,
                        "locationAddress": "1 Main St",
                        "locationCity": "San Diego",
                        "locationState": "CA",
                        "locationCountry": "US",
                        "locationPostalCode": "92101",
                        "locationTwentyfourseven": True,
                        "locationOpeningTimings": [
                            None,
                            {
                                "__typename": "OpeningTiming",
                                "weekday": 5,
                                "periodBegin": "08:00",
                                "periodEnd": None,
                            },
                        ],
                        "locationInNetwork": False,
                        "phone": None,
                        "locationCoordinates": {
                            "__typename": "Coordinates",
                            "latitude": "32.7157",
                            "longitude": "-117.1611",
                        },
                        "evses": [
                            None,
                            {
                                "__typename": "Evse",
                                "evseId": "EVSE-1",
                                "evseLocationId": None,
                                "evseStatus": "FUTURE_EVSE_STATUS",
                                "evseCapability": ["PLUG_AND_CHARGE_CAPABLE"],
                                "evsePhysicalReference": "A-1",
                                "connector": [
                                    None,
                                    {
                                        "__typename": "Connector",
                                        "connectorId": "connector-1",
                                        "connectorType": "CCS",
                                        "connectorPowerRating": "150 kW",
                                        "connectorDescription": None,
                                    },
                                ],
                            },
                        ],
                    },
                ],
            }
        }
    )

    assert details is not None
    assert details.status_code == "1000"
    assert details.status_message is None
    assert details.timestamp == "raw-location-timestamp"
    assert details.data is not None
    assert isinstance(details.data, tuple)
    assert details.data[0] is None
    location = details.data[1]
    assert location is not None
    assert location.location_type is EmpLocationStatus.UNKNOWN_VALUE
    assert location.location_twenty_four_seven is True
    assert location.opening_timings is not None
    assert location.opening_timings[0] is None
    assert location.coordinates is not None
    assert location.coordinates.latitude == "32.7157"
    assert location.evses is not None
    assert location.evses[0] is None
    evse = location.evses[1]
    assert evse is not None
    assert evse.evse_status is EmpEvseStatus.UNKNOWN_VALUE
    assert evse.evse_capability == ("PLUG_AND_CHARGE_CAPABLE",)
    assert evse.connectors is not None
    assert evse.connectors[0] is None
    connector = evse.connectors[1]
    assert connector is not None
    assert connector.connector_power_rating == "150 kW"


def test_tariff_pricing_preserves_raw_status_and_every_nullable_tier_list() -> None:
    pricing = parse_tariff_pricing(
        {
            "tariffPricing": {
                "__typename": "TariffPricingResponse",
                "statusCode": "1000",
                "statusMessage": None,
                "timestamp": "raw-tariff-timestamp",
                "data": {
                    "__typename": "TariffPricingData",
                    "locationId": "location-1",
                    "maxChargeLimit": "80",
                    "tariffDetails": [
                        None,
                        {
                            "__typename": "TariffDetail",
                            "connectorType": "CCS",
                            "connectorPower": "150 kW",
                            "sessionFee": "1.00",
                            "tariffAltText": {
                                "__typename": "TariffAltText",
                                "en": "English",
                                "fr": None,
                            },
                            "idleFees": {
                                "__typename": "IdleFees",
                                "gracePeriod": "10",
                                "idleFeesTier": [
                                    None,
                                    {
                                        "__typename": "IdleFeeTier",
                                        "congestionLevel": "HIGH",
                                        "timeStart": "08:00",
                                        "timeEnd": "18:00",
                                        "durationStart": "0",
                                        "durationEnd": "60",
                                        "durationUnit": "MINUTE",
                                        "price": "0.50",
                                        "unit": "USD_PER_MINUTE",
                                    },
                                ],
                            },
                            "congestionFees": {
                                "__typename": "CongestionFees",
                                "gracePeriod": None,
                                "congestionTier": [
                                    None,
                                    {
                                        "__typename": "CongestionTier",
                                        "congestionLevel": "MEDIUM",
                                        "vehicleSOCLimit": "90",
                                        "price": "2.00",
                                        "unit": "USD",
                                    },
                                ],
                            },
                            "energyFees": {
                                "__typename": "EnergyFees",
                                "energyFeeTier": [
                                    None,
                                    {
                                        "__typename": "EnergyFeeTier",
                                        "applicableDay": [1, 2, 3],
                                        "timeStart": "00:00",
                                        "timeEnd": "23:59",
                                        "durationStart": None,
                                        "durationEnd": None,
                                        "durationUnit": None,
                                        "minRange": "0",
                                        "maxRange": "100",
                                        "rangeUnit": "KWH",
                                        "price": "0.40",
                                        "unit": "USD_PER_KWH",
                                    },
                                ],
                            },
                        },
                    ],
                },
            }
        }
    )

    assert pricing is not None
    assert pricing.status_code == "1000"
    assert pricing.status_message is None
    assert pricing.timestamp == "raw-tariff-timestamp"
    assert pricing.data is not None
    assert pricing.data.tariff_details is not None
    assert pricing.data.tariff_details[0] is None
    detail = pricing.data.tariff_details[1]
    assert detail is not None
    assert detail.alternative_text is not None
    assert detail.alternative_text.fr is None
    assert detail.idle_fees is not None
    assert detail.idle_fees.tiers is not None
    assert detail.idle_fees.tiers[0] is None
    assert detail.congestion_fees is not None
    assert detail.congestion_fees.tiers is not None
    assert detail.congestion_fees.tiers[0] is None
    assert detail.energy_fees is not None
    assert detail.energy_fees.tiers is not None
    assert detail.energy_fees.tiers[0] is None
    energy_tier = detail.energy_fees.tiers[1]
    assert energy_tier is not None
    assert energy_tier.applicable_day == (1, 2, 3)


def test_nullable_roots_fragments_lists_and_items_are_preserved() -> None:
    assert parse_driving_history({"vehicle": None}) is None
    assert parse_driving_history({"vehicle": {"__typename": "Vehicle"}}) is None
    assert (
        parse_ev_charge_stations(
            {
                "vehicle": {
                    "__typename": "ElectricVehicle",
                    "evChargeStations": None,
                }
            }
        )
        is None
    )
    assert (
        parse_ev_charge_stations(
            {
                "vehicle": {
                    "__typename": "ElectricVehicle",
                    "evChargeStations": [],
                }
            }
        )
        == ()
    )
    assert parse_e_vehicle_eligibility({"eVehicleEligibility": None}) is None
    assert parse_last_known_camera_usage_counter({"vehicle": None}) is None
    assert parse_location_details({"locationDetails": None}) is None
    assert parse_parking_chargeable({"parkingChargeable": None}) is None
    assert parse_shareable_capabilities({"vehicle": None}) is None
    assert parse_tariff_pricing({"tariffPricing": None}) is None

    location_details = parse_location_details(
        {
            "locationDetails": {
                "__typename": "LocationDetailsResponse",
                "statusCode": None,
                "statusMessage": None,
                "timestamp": None,
                "data": None,
            }
        }
    )
    assert location_details is not None
    assert location_details.data is None
