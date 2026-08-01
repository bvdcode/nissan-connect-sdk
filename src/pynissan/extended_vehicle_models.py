from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .models import DistanceUnit, SpeedUnit
from .navigation_inputs import PlugConnectorType


class DrivingHistoryAggregator(StrEnum):
    """Time bucket accepted by the driving-history query."""

    DAILY = "DAILY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"
    UNKNOWN_VALUE = "UNKNOWN__"


class WeightUnit(StrEnum):
    """Weight units accepted and returned by driving history."""

    POUND = "POUND"
    KILOGRAM = "KILOGRAM"
    GRAM = "GRAM"
    UNKNOWN_VALUE = "UNKNOWN__"


class EmpLocationStatus(StrEnum):
    """Known location categories returned by Nissan's charging network API."""

    ON_STREET = "ON_STREET"
    PARKING_GARAGE = "PARKING_GARAGE"
    UNDERGROUND_GARAGE = "UNDERGROUND_GARAGE"
    PARKING_LOT = "PARKING_LOT"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"
    ALONG_MOTORWAY = "ALONG_MOTORWAY"
    ON_DRIVEWAY = "ON_DRIVEWAY"
    UNKNOWN_VALUE = "UNKNOWN__"


class EmpEvseStatus(StrEnum):
    """Known EVSE states returned by Nissan's charging network API."""

    AVAILABLE = "AVAILABLE"
    BLOCKED = "BLOCKED"
    CHARGING = "CHARGING"
    INOPERATIVE = "INOPERATIVE"
    OUT_OF_ORDER = "OUTOFORDER"
    PLANNED = "PLANNED"
    REMOVED = "REMOVED"
    RESERVED = "RESERVED"
    UNKNOWN = "UNKNOWN"
    UNKNOWN_VALUE = "UNKNOWN__"


@dataclass(frozen=True, slots=True)
class DrivingHistoryDistance:
    """Non-null distance fields nested in a driving-history response."""

    unit: DistanceUnit
    value: float


@dataclass(frozen=True, slots=True)
class DrivingHistoryAverageSpeed:
    """Nullable average-speed fields nested in driving history."""

    type: SpeedUnit | None
    value: float | None


@dataclass(frozen=True, slots=True)
class DrivingHistoryCo2Saved:
    """Nullable CO2 saving fields nested in driving history."""

    unit: WeightUnit | None
    value: float | None


@dataclass(frozen=True, slots=True)
class DrivingHistoryCoordinate:
    """Nullable start or end coordinates for a recorded trip."""

    latitude: float | None
    longitude: float | None


@dataclass(frozen=True, slots=True)
class DrivingHistoryTripSummary:
    """One nullable-field aggregate returned for a driving-history bucket."""

    user_id: str | None
    day: int | None
    month: int | None
    year: int | None
    number_of_trips: int | None
    distance_traveled: DrivingHistoryDistance | None
    duration: str | None
    average_speed: DrivingHistoryAverageSpeed | None
    energy_consumed: float | None
    co2_saved: DrivingHistoryCo2Saved | None


@dataclass(frozen=True, slots=True)
class DrivingHistoryTrip:
    """One individual trip returned by driving history."""

    distance: DrivingHistoryDistance | None
    start_date: datetime | None
    end_date: datetime | None
    duration: int | None
    start_location: DrivingHistoryCoordinate | None
    end_location: DrivingHistoryCoordinate | None
    average_speed: DrivingHistoryAverageSpeed | None
    energy_consumed: float | None
    energy_saved: float | None
    co2_saved: DrivingHistoryCo2Saved | None
    user_id: str | None


@dataclass(frozen=True, slots=True)
class DrivingHistory:
    """Non-null driving-history collections returned for an electric vehicle."""

    trip_summaries: tuple[DrivingHistoryTripSummary, ...]
    trips: tuple[DrivingHistoryTrip, ...]


@dataclass(frozen=True, slots=True)
class EVChargeStationAddress:
    """Nullable address fields for a nearby charging station."""

    address1: str | None
    address2: str | None
    city: str | None
    country: str | None
    postal_code: str | None
    state: str | None


@dataclass(frozen=True, slots=True)
class EVChargeStationCoordinate:
    """Nullable coordinates for a nearby charging station."""

    latitude: float | None
    longitude: float | None


@dataclass(frozen=True, slots=True)
class EVChargeStationConnector:
    """Nullable connector details advertised by a charging station."""

    plug_connector_type: PlugConnectorType | None
    rated_power_kw: float | None
    voltage_v: int | None
    current_a: int | None
    current_type: str | None


@dataclass(frozen=True, slots=True)
class EVChargeStation:
    """One nullable-field charging station returned near a coordinate."""

    id: str | None
    name: str | None
    phone_number: str | None
    address: EVChargeStationAddress | None
    location: EVChargeStationCoordinate | None
    connectors: tuple[EVChargeStationConnector | None, ...] | None


@dataclass(frozen=True, slots=True)
class EVehicleEligibilityData:
    """Nullable V1G eligibility values returned for a VIN."""

    vin: str | None
    v1g_eligible: bool | None


@dataclass(frozen=True, slots=True)
class EVehicleEligibility:
    """Raw status wrapper returned by the eVehicle eligibility endpoint."""

    status_code: str | None
    status_message: str | None
    timestamp: str | None
    data: EVehicleEligibilityData | None


@dataclass(frozen=True, slots=True)
class LastKnownCameraUsageCounter:
    """The last camera counter and update time known to Nissan."""

    counter: str | None
    last_update_time: datetime | None


@dataclass(frozen=True, slots=True)
class EmpLocationOpeningTiming:
    """Nullable opening period for one weekday at a charging location."""

    weekday: int | None
    period_begin: str | None
    period_end: str | None


@dataclass(frozen=True, slots=True)
class EmpLocationCoordinates:
    """String coordinates returned by the EMP location-details endpoint."""

    latitude: str | None
    longitude: str | None


@dataclass(frozen=True, slots=True)
class EmpConnector:
    """Nullable EMP connector metadata attached to an EVSE."""

    connector_id: str | None
    connector_type: str | None
    connector_power_rating: str | None
    connector_description: str | None


@dataclass(frozen=True, slots=True)
class EmpEvse:
    """One nullable-field EVSE returned for an EMP charging location."""

    evse_id: str | None
    evse_location_id: str | None
    evse_status: EmpEvseStatus | None
    evse_capability: tuple[str | None, ...] | None
    evse_physical_reference: str | None
    connectors: tuple[EmpConnector | None, ...] | None


@dataclass(frozen=True, slots=True)
class EmpLocation:
    """One charging-network location returned by LocationDetails."""

    location_id: str | None
    location_type: EmpLocationStatus | None
    location_name: str | None
    location_logo: str | None
    location_operator_name: str | None
    location_sub_operator_name: str | None
    location_address: str | None
    location_city: str | None
    location_state: str | None
    location_country: str | None
    location_postal_code: str | None
    location_twenty_four_seven: bool | None
    opening_timings: tuple[EmpLocationOpeningTiming | None, ...] | None
    location_in_network: bool | None
    phone: str | None
    coordinates: EmpLocationCoordinates | None
    evses: tuple[EmpEvse | None, ...] | None


@dataclass(frozen=True, slots=True)
class LocationDetails:
    """Raw EMP status wrapper and nullable charging-location collection."""

    status_code: str | None
    status_message: str | None
    timestamp: str | None
    data: tuple[EmpLocation | None, ...] | None


@dataclass(frozen=True, slots=True)
class ParkingChargeableData:
    """Nullable parking and congestion chargeability flags for an EVSE."""

    evse_id: str | None
    is_parking_chargeable: bool | None
    is_congestion_chargeable: bool | None


@dataclass(frozen=True, slots=True)
class ParkingChargeable:
    """Raw EMP status wrapper for EVSE parking chargeability."""

    status_code: str | None
    status_message: str | None
    timestamp: str | None
    data: ParkingChargeableData | None


@dataclass(frozen=True, slots=True)
class ShareableCapability:
    """One capability that may be shared with an additional driver."""

    id: str
    name: str | None
    shareable: bool | None


@dataclass(frozen=True, slots=True)
class ShareableCapabilityGroup:
    """One capability group and its non-null capability collection."""

    id: str
    name: str | None
    shared: bool | None
    capabilities: tuple[ShareableCapability | None, ...]


@dataclass(frozen=True, slots=True)
class ShareableCapabilities:
    """Non-null group collection exposed by an AVK2 vehicle."""

    groups: tuple[ShareableCapabilityGroup | None, ...]


@dataclass(frozen=True, slots=True)
class TariffLocalizedText:
    """Nullable English and French tariff text."""

    en: str | None
    fr: str | None


@dataclass(frozen=True, slots=True)
class TariffIdleFeeTier:
    """One nullable-field idle-fee tier."""

    congestion_level: str | None
    time_start: str | None
    time_end: str | None
    duration_start: str | None
    duration_end: str | None
    duration_unit: str | None
    price: str | None
    unit: str | None


@dataclass(frozen=True, slots=True)
class TariffIdleFees:
    """Idle-fee grace period and nullable tiers."""

    grace_period: str | None
    tiers: tuple[TariffIdleFeeTier | None, ...] | None


@dataclass(frozen=True, slots=True)
class TariffCongestionFeeTier:
    """One nullable-field congestion-fee tier."""

    congestion_level: str | None
    vehicle_soc_limit: str | None
    price: str | None
    unit: str | None


@dataclass(frozen=True, slots=True)
class TariffCongestionFees:
    """Congestion-fee grace period and nullable tiers."""

    grace_period: str | None
    tiers: tuple[TariffCongestionFeeTier | None, ...] | None


@dataclass(frozen=True, slots=True)
class TariffEnergyFeeTier:
    """One nullable-field energy-fee tier."""

    applicable_day: tuple[int | None, ...] | None
    time_start: str | None
    time_end: str | None
    duration_start: str | None
    duration_end: str | None
    duration_unit: str | None
    min_range: str | None
    max_range: str | None
    range_unit: str | None
    price: str | None
    unit: str | None


@dataclass(frozen=True, slots=True)
class TariffEnergyFees:
    """Nullable energy-fee tiers for one charging tariff."""

    tiers: tuple[TariffEnergyFeeTier | None, ...] | None


@dataclass(frozen=True, slots=True)
class TariffDetail:
    """Tariff details for one connector category."""

    connector_type: str | None
    connector_power: str | None
    session_fee: str | None
    alternative_text: TariffLocalizedText | None
    idle_fees: TariffIdleFees | None
    congestion_fees: TariffCongestionFees | None
    energy_fees: TariffEnergyFees | None


@dataclass(frozen=True, slots=True)
class TariffPricingData:
    """Nullable tariff fields returned for a charging location."""

    location_id: str | None
    max_charge_limit: str | None
    tariff_details: tuple[TariffDetail | None, ...] | None


@dataclass(frozen=True, slots=True)
class TariffPricing:
    """Raw EMP status wrapper for location tariff pricing."""

    status_code: str | None
    status_message: str | None
    timestamp: str | None
    data: TariffPricingData | None
