from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class DistanceUnit(StrEnum):
    """Distance units accepted by the Nissan GraphQL API."""

    MILE = "MILE"
    KILOMETER = "KILOMETER"
    UNKNOWN_VALUE = "UNKNOWN__"


class SpeedUnit(StrEnum):
    """Speed units accepted by the Nissan GraphQL API."""

    KPH = "KPH"
    MPH = "MPH"
    UNKNOWN_VALUE = "UNKNOWN__"


class TemperatureUnit(StrEnum):
    """Temperature units accepted by the Nissan GraphQL API."""

    CELSIUS = "CELSIUS"
    FAHRENHEIT = "FAHRENHEIT"
    UNKNOWN_VALUE = "UNKNOWN__"


class PurchaseType(StrEnum):
    """Known purchase types reported for a vehicle subscription."""

    PURCHASE = "PURCHASE"
    TRIAL = "TRIAL"
    SUBSCRIPTION = "SUBSCRIPTION"


class ProductType(StrEnum):
    """Known product types reported for a vehicle subscription."""

    TELEMATICS = "TELEMATICS"
    FEATURE_ON_DEMAND = "FEATURE_ON_DEMAND"


class DataPrivacyMode(StrEnum):
    """Vehicle data-sharing mode reported by Nissan."""

    ON = "ON"
    OFF = "OFF"
    UNKNOWN_VALUE = "UNKNOWN__"


class ChargeHistoryAggregator(StrEnum):
    """Time buckets accepted by the vehicle charge history query."""

    DAILY = "DAILY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class WeekDay(StrEnum):
    """Weekday values accepted by Nissan schedule inputs."""

    MONDAY = "MO"
    TUESDAY = "TU"
    WEDNESDAY = "WE"
    THURSDAY = "TH"
    FRIDAY = "FR"
    SATURDAY = "SA"
    SUNDAY = "SU"
    UNKNOWN_VALUE = "UNKNOWN__"


class SeatClimateOption(StrEnum):
    """Available heating and cooling modes for a seat."""

    COOL = "COOL"
    HEAT = "HEAT"
    OFF = "OFF"
    UNKNOWN_VALUE = "UNKNOWN__"


class V2LState(StrEnum):
    """Power-output state reported by a vehicle with V2L support."""

    NO_DISPLAY = "NO_DISPLAY"
    ALL_OFF = "ALL_OFF"
    ALL_ON = "ALL_ON"
    INSIDE_ON = "INSIDE_ON"
    OUTSIDE_ON = "OUTSIDE_ON"
    DISABLED = "DISABLED"
    UNKNOWN_VALUE = "UNKNOWN__"


class CameraPosition(StrEnum):
    """Camera positions returned for remotely captured vehicle photos."""

    OUTSIDE_REAR_CAMERA = "OUTSIDE_REAR_CAMERA"
    OUTSIDE_FRONT_CAMERA = "OUTSIDE_FRONT_CAMERA"
    INSIDE_CAMERA = "INSIDE_CAMERA"
    UNKNOWN_VALUE = "UNKNOWN__"


class CameraService(StrEnum):
    """Services that produced a remotely available vehicle photo."""

    DVR_REMOTE_PHOTO = "DVR_REMOTE_PHOTO"
    DVR_CRASH_PHOTO = "DVR_CRASH_PHOTO"
    UNKNOWN_VALUE = "UNKNOWN__"


class ServiceRequestStatus(StrEnum):
    """Statuses returned while Nissan processes a remote request."""

    SUCCESS = "SUCCESS"
    INITIATED = "INITIATED"
    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    FAILED = "FAILED"
    SENT = "SENT"
    CANCELLATION_SUCCESS = "CANCELLATION_SUCCESS"
    CANCELLATION_INITIATED = "CANCELLATION_INITIATED"
    CANCELLATION_SENT = "CANCELLATION_SENT"
    CANCELLATION_FAILED = "CANCELLATION_FAILED"
    CANCEL_UPDATE_FAILED = "CANCEL_UPDATE_FAILED"
    CANCEL_UPDATE_INITIATED = "CANCEL_UPDATE_INITIATED"
    CANCEL_UPDATE_SUCCESS = "CANCEL_UPDATE_SUCCESS"
    CANCEL_UPDATE_SENT = "CANCEL_UPDATE_SENT"
    UPDATE_SENT = "UPDATE_SENT"
    UPDATE_INITIATED = "UPDATE_INITIATED"
    UPDATE_SUCCESS = "UPDATE_SUCCESS"
    UPDATE_FAILED = "UPDATE_FAILED"
    SUCCESS_EXECUTION_CONFIRMED = "SUCCESS_EXECUTION_CONFIRMED"
    UNKNOWN = "UNKNOWN"
    UNKNOWN_VALUE = "UNKNOWN__"


_IN_PROGRESS_SERVICE_REQUEST_STATUSES: frozenset[ServiceRequestStatus] = frozenset(
    {
        ServiceRequestStatus.INITIATED,
        ServiceRequestStatus.PENDING,
        ServiceRequestStatus.SCHEDULED,
        ServiceRequestStatus.SENT,
        ServiceRequestStatus.CANCELLATION_INITIATED,
        ServiceRequestStatus.CANCELLATION_SENT,
        ServiceRequestStatus.CANCEL_UPDATE_INITIATED,
        ServiceRequestStatus.CANCEL_UPDATE_SENT,
        ServiceRequestStatus.UPDATE_INITIATED,
        ServiceRequestStatus.UPDATE_SENT,
    }
)

_SUCCESSFUL_SERVICE_REQUEST_STATUSES: frozenset[ServiceRequestStatus] = frozenset(
    {
        ServiceRequestStatus.SUCCESS,
        ServiceRequestStatus.SUCCESS_EXECUTION_CONFIRMED,
        ServiceRequestStatus.CANCELLATION_SUCCESS,
        ServiceRequestStatus.CANCEL_UPDATE_SUCCESS,
        ServiceRequestStatus.UPDATE_SUCCESS,
    }
)


class ServiceRequestKind(StrEnum):
    """The status endpoint associated with a submitted remote request."""

    CHARGE = "charge"
    CHARGE_CONFIGURATION = "charge_configuration"
    CLIMATE = "climate"
    DATA_WIPE = "data_wipe"
    DOOR = "door"
    ENGINE = "engine"
    HORN_LIGHT = "horn_light"
    LOCATION = "location"
    OTA = "ota"
    PHOTO = "photo"
    ROUTE = "route"
    T_JUNCTION = "t_junction"
    V2L = "v2l"
    VEHICLE_STATUS = "vehicle_status"


class VehicleAlertKind(StrEnum):
    """Vehicle-alert category used to select a request-status query."""

    BOUNDARY = "boundary"
    CURFEW = "curfew"
    SPEED = "speed"
    VALET = "valet"


@dataclass(frozen=True, slots=True)
class Tokens:
    """OAuth tokens issued by the MyNISSAN identity service."""

    access_token: str
    refresh_token: str
    id_token: str | None = None


@dataclass(frozen=True, slots=True)
class SeatClimateSettings:
    """Optional climate mode for each supported seat position."""

    front_driver: SeatClimateOption | None = None
    front_passenger: SeatClimateOption | None = None
    rear_left: SeatClimateOption | None = None
    rear_right: SeatClimateOption | None = None
    rear_center: SeatClimateOption | None = None
    third_left: SeatClimateOption | None = None
    third_right: SeatClimateOption | None = None


@dataclass(frozen=True, slots=True)
class ClimateParameters:
    """Optional cabin accessories applied with a climate command."""

    seats: SeatClimateSettings | None = None
    steering_wheel_heater: bool | None = None
    defrost_and_deicer: bool | None = None


@dataclass(frozen=True, slots=True)
class ClimateSettings:
    """Target cabin temperature used by climate and engine commands."""

    temperature: float
    unit: TemperatureUnit
    parameters: ClimateParameters | None = None


@dataclass(frozen=True, slots=True)
class ChargeScheduleInput:
    """Fields used to create or replace a recurring charge schedule."""

    start_date_time: datetime
    duration: str
    week_days: tuple[WeekDay, ...]


@dataclass(frozen=True, slots=True)
class ClimateScheduleInput:
    """Fields used to create or replace a recurring climate schedule."""

    start_date_time: datetime
    week_days: tuple[WeekDay, ...]
    climate: ClimateSettings


@dataclass(frozen=True, slots=True)
class ServiceRequest:
    """An asynchronous remote request accepted by Nissan."""

    id: str
    kind: ServiceRequestKind
    climate_defaults_success: bool | None = None
    climate_defaults_error_message: str | None = None


@dataclass(frozen=True, slots=True)
class VehicleAlertRequest:
    """An asynchronous vehicle-alert change accepted by Nissan."""

    id: str
    kind: VehicleAlertKind


@dataclass(frozen=True, slots=True)
class ServiceRequestResult:
    """The latest upstream state of an asynchronous remote request."""

    status: ServiceRequestStatus | None
    status_details: str | None = None
    location: VehicleLocation | None = None
    activation_date_time: datetime | None = None
    status_change_date_time: datetime | None = None

    @property
    def is_terminal(self) -> bool:
        """Return whether Nissan has finished processing the request."""

        return self.status is not None and self.status not in _IN_PROGRESS_SERVICE_REQUEST_STATUSES

    @property
    def is_success(self) -> bool:
        """Return whether the request finished with a successful status."""

        return self.status is not None and self.status in _SUCCESSFUL_SERVICE_REQUEST_STATUSES


@dataclass(frozen=True, slots=True)
class Vehicle:
    """Static data for a vehicle attached to the account."""

    vin: str
    year: str | None
    model: str | None
    color: str | None
    nickname: str | None
    image_url: str | None
    driver_type: str | None
    plate: str | None


@dataclass(frozen=True, slots=True)
class VehiclePhoto:
    """One remotely captured vehicle photo and its upstream metadata."""

    id: str | None
    filename: str | None
    link: str | None
    timestamp: datetime | None
    camera_position: CameraPosition | None
    camera_service: CameraService | None


@dataclass(frozen=True, slots=True)
class VehiclePhotos:
    """Photos currently available around one vehicle."""

    vin: str
    year: str
    model: str
    photos: tuple[VehiclePhoto | None, ...] | None


@dataclass(frozen=True, slots=True)
class RemoteServiceHistoryEntry:
    """One raw remote-service status transition returned by Nissan."""

    service_request_id: str | None
    status: str | None
    service_type: str | None
    status_change_date_time: datetime | None


@dataclass(frozen=True, slots=True)
class RemoteServiceHistory:
    """One nullable page of vehicle remote-service history."""

    page_number: int | None
    items_per_page: int | None
    total_items: int | None
    total_pages: int | None
    history: tuple[RemoteServiceHistoryEntry | None, ...] | None


@dataclass(frozen=True, slots=True)
class ReminderNotificationsAfterLeavingVehicle:
    """Reminder flags returned for supported AVK2 vehicles."""

    lock: bool | None
    door: bool | None
    trunk: bool | None
    sunroof: bool | None
    window: bool | None


@dataclass(frozen=True, slots=True)
class VehiclePreferences:
    """MIL/DTC maintenance-data sharing preferences for a vehicle."""

    enabled: bool | None
    text: bool | None
    phone: bool | None
    email: bool | None


@dataclass(frozen=True, slots=True)
class VehicleSubscriptionProduct:
    """Product metadata attached to a vehicle subscription."""

    product_id: str
    marketing_name: str
    description: str
    services: tuple[str | None, ...]


@dataclass(frozen=True, slots=True)
class VehicleSubscriptionPendingOrder:
    """Pending package activation attached to a vehicle subscription."""

    pending_order_id: str
    package_name: str
    activation_date: datetime | None


@dataclass(frozen=True, slots=True)
class VehicleSubscription:
    """One subscription returned by Nissan without app-level defaults or filtering."""

    subscription_id: str
    subscription_service_type: str
    purchase_type: PurchaseType | str | None
    product_type: ProductType | str | None
    next_billing_date: datetime | None
    goodwill_end_date: datetime | None
    goodwill_start_date: datetime | None
    grace_end_date: datetime | None
    subscription_start_date: datetime
    subscription_end_date: datetime | None
    is_active: bool | None
    np_subscription_price: str | None
    product: VehicleSubscriptionProduct
    pending_order: VehicleSubscriptionPendingOrder | None


@dataclass(frozen=True, slots=True)
class VehicleSubscriptions:
    """The nullable capability branch containing a vehicle's subscriptions."""

    vin: str
    subscriptions: tuple[VehicleSubscription | None, ...] | None


@dataclass(frozen=True, slots=True)
class VehicleWifiConsumption:
    """Current in-vehicle Wi-Fi usage and data cap in gigabytes."""

    usage_percent: float
    usage_amount_gb: float
    data_cap_amount_gb: float
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class AlertAddress:
    """Nullable address fields attached to a configured boundary alert."""

    address1: str | None
    address2: str | None
    city: str | None
    state: str | None
    country: str | None
    postal_code: str | None


@dataclass(frozen=True, slots=True)
class AlertLocation:
    """Coordinates attached to an alert configuration or breach event."""

    latitude: float | None
    longitude: float | None


@dataclass(frozen=True, slots=True)
class AlertDistance:
    """A nullable distance value and its raw upstream unit."""

    value: float | None
    unit: str | None


@dataclass(frozen=True, slots=True)
class BoundaryAlert:
    """A configured entry or exit boundary alert."""

    service_request_id: str
    alert_type: str | None
    name: str
    enabled: bool
    in_vehicle_warning: bool
    address: AlertAddress | None
    location: AlertLocation | None
    radius: AlertDistance | None


@dataclass(frozen=True, slots=True)
class CurfewSchedule:
    """Schedule attached to a configured curfew alert."""

    all_day: bool | None
    start_date_time: datetime
    duration: str | None
    week_days: tuple[str | None, ...]


@dataclass(frozen=True, slots=True)
class CurfewAlert:
    """A configured vehicle curfew alert."""

    service_request_id: str
    name: str
    enabled: bool
    in_vehicle_warning: bool
    schedule: CurfewSchedule | None


@dataclass(frozen=True, slots=True)
class SpeedThreshold:
    """Speed threshold with its raw upstream unit."""

    unit: str | None
    value: float | None


@dataclass(frozen=True, slots=True)
class SpeedAlert:
    """A configured vehicle speed alert."""

    service_request_id: str
    name: str
    enabled: bool
    in_vehicle_warning: bool
    threshold: SpeedThreshold | None


@dataclass(frozen=True, slots=True)
class ValetAlert:
    """The currently configured valet boundary alert."""

    service_request_id: str | None
    radius: AlertDistance | None


@dataclass(frozen=True, slots=True)
class VehicleAlerts:
    """Nullable alert configurations returned for one connected vehicle."""

    boundary_alerts: tuple[BoundaryAlert | None, ...] | None
    curfew_alerts: tuple[CurfewAlert | None, ...] | None
    speed_alerts: tuple[SpeedAlert | None, ...] | None
    valet_alert: ValetAlert | None


@dataclass(frozen=True, slots=True)
class BreachAlert:
    """One raw vehicle-alert breach event."""

    service_type: str | None
    breach_date_time: datetime | None
    name: str | None
    location: AlertLocation | None


@dataclass(frozen=True, slots=True)
class BreachAlerts:
    """One nullable page of vehicle-alert breach events."""

    items_per_page: int | None
    page_number: int | None
    total_items: int | None
    total_pages: int | None
    alerts: tuple[BreachAlert | None, ...] | None


@dataclass(frozen=True, slots=True)
class DistanceReading:
    """A distance value returned by the connected vehicle service."""

    value: int | None
    unit: str | None
    last_updated_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class Mileage:
    """The vehicle odometer reading."""

    total: int | None
    unit: str | None
    recorded_at: datetime | None


@dataclass(frozen=True, slots=True)
class DoorState:
    """Reported state of a door and its window and lock."""

    ajar: str | None
    window: str | None
    lock: str | None


@dataclass(frozen=True, slots=True)
class DoorsStatus:
    """Reported state of the vehicle openings and locks."""

    last_updated_at: datetime | None
    front_left: DoorState | None
    front_right: DoorState | None
    rear_left: DoorState | None
    rear_right: DoorState | None
    engine_hood_ajar: str | None
    hatch_ajar: str | None
    sunroof_ajar: str | None
    trunk_lock: str | None
    overall_lock: str | None


@dataclass(frozen=True, slots=True)
class BatteryStatus:
    """Reported electric vehicle battery status."""

    level: int | None
    is_plugged_in: bool | None
    is_charging: bool | None
    remaining_charge_time: int | None
    remaining_mileage: DistanceReading | None


@dataclass(frozen=True, slots=True)
class TirePressure:
    """Raw tire pressure and status values returned by the API."""

    last_updated_at: datetime | None
    front_left: int | None
    front_right: int | None
    rear_left: int | None
    rear_right: int | None
    front_left_status: int | None
    front_right_status: int | None
    rear_left_status: int | None
    rear_right_status: int | None


@dataclass(frozen=True, slots=True)
class MaintenanceIndicator:
    """A vehicle malfunction or maintenance indicator."""

    active: bool | None
    detailed_message: str | None
    type: str | None


@dataclass(frozen=True, slots=True)
class TemperatureReading:
    """A temperature value returned by the API."""

    value: float
    unit: str


@dataclass(frozen=True, slots=True)
class ClimateStatus:
    """Reported climate control state."""

    state: str | None
    temperature: TemperatureReading | None


@dataclass(frozen=True, slots=True)
class EngineOilDrainRange:
    """Remaining engine-oil service range reported by a combustion vehicle."""

    range: int
    unit: DistanceUnit
    last_updated_at: datetime


@dataclass(frozen=True, slots=True)
class VehicleStatus:
    """Cached dynamic data for one vehicle."""

    vin: str
    vehicle_type: str | None
    battery: BatteryStatus | None
    climate: ClimateStatus | None
    doors: DoorsStatus | None
    fuel_range: DistanceReading | None
    mileage: Mileage | None
    tire_pressure: TirePressure | None
    maintenance_indicators: tuple[MaintenanceIndicator, ...]
    engine_oil_drain_range: EngineOilDrainRange | None = None


@dataclass(frozen=True, slots=True)
class VehicleLocation:
    """The last reported location of a vehicle."""

    vin: str
    latitude: float | None
    longitude: float | None
    last_updated_at: datetime | None


@dataclass(frozen=True, slots=True)
class ServiceCapability:
    """A connected service advertised for a vehicle."""

    type: str
    enabled: bool
    subscribed: bool | None


@dataclass(frozen=True, slots=True)
class AccessoryCapability:
    """Whether a vehicle accessory is available."""

    enabled: bool | None


@dataclass(frozen=True, slots=True)
class SeatHeaterAccessories:
    """Heating or heating-and-cooling support by seat position."""

    assistant_seat: str | None
    driver_seat: str | None
    second_centre_seat: str | None
    second_left_seat: str | None
    second_right_seat: str | None
    third_left_seat: str | None
    third_right_seat: str | None


@dataclass(frozen=True, slots=True)
class SeatHeaterCapability:
    """Seat climate accessory support advertised by the vehicle."""

    enabled: bool | None
    accessories: SeatHeaterAccessories | None


@dataclass(frozen=True, slots=True)
class SunRoofCapability:
    """Sun roof type and availability advertised by the vehicle."""

    type: str | None
    enabled: bool | None


@dataclass(frozen=True, slots=True)
class WayPointCapability:
    """Waypoint support and the maximum number accepted by the vehicle."""

    enabled: bool | None
    max_number: int | None


@dataclass(frozen=True, slots=True)
class HvacTemperatureCapabilities:
    """Supported HVAC temperature range in the requested unit."""

    unit: str
    default: float
    minimum: float
    maximum: float
    resolution: float


@dataclass(frozen=True, slots=True)
class VehicleAccessoriesDetails:
    """Accessory capabilities advertised for a vehicle."""

    seat_heater: SeatHeaterCapability | None
    steering_heat: AccessoryCapability | None
    sun_roof: SunRoofCapability | None
    window_status: AccessoryCapability | None
    way_point: WayPointCapability | None
    hvac_temperatures: HvacTemperatureCapabilities | None


@dataclass(frozen=True, slots=True)
class VehicleCapabilities:
    """Connected service capabilities for a vehicle."""

    vin: str
    telematics_program: str | None
    enrollment_status: str | None
    services: tuple[ServiceCapability, ...]
    accessories_details: VehicleAccessoriesDetails | None = None


@dataclass(frozen=True, slots=True)
class ChargeSchedule:
    """A recurring vehicle charging schedule."""

    id: str
    state: str | None
    start_date_time: datetime
    duration: str
    week_days: tuple[WeekDay, ...]


@dataclass(frozen=True, slots=True)
class ChargeConfig:
    """Configured charging and notification limits, expressed as percentages."""

    charge_limit_percent: int | None
    notification_threshold_percent: int | None


@dataclass(frozen=True, slots=True)
class V2LStatus:
    """V2L state and battery reserve levels, expressed as percentages."""

    state: V2LState | None
    charge_limit_percent: float | None
    minimum_charge_limit_percent: float | None


@dataclass(frozen=True, slots=True)
class ChargeSession:
    """One charging session; recovered energy is expressed in kilowatt-hours."""

    start: datetime | None
    end: datetime | None
    duration: str | None
    recovered_energy_kwh: float | None


@dataclass(frozen=True, slots=True)
class ChargeHistorySummary:
    """Aggregated charge history; energy is in kWh and duration is in minutes."""

    day: int | None
    month: int | None
    year: int | None
    number_of_charge_sessions: int | None
    total_energy_recovered_kwh: float | None
    total_duration_minutes: int | None
    number_of_errors: int | None
    user_id: str | None
    role_type: str | None


@dataclass(frozen=True, slots=True)
class VehicleChargeHistory:
    """Charging sessions and summaries for one requested time aggregation."""

    charges: tuple[ChargeSession, ...]
    charge_summaries: tuple[ChargeHistorySummary, ...]


@dataclass(frozen=True, slots=True)
class ClimateSchedule:
    """A recurring cabin climate schedule."""

    id: str
    state: str | None
    start_date_time: datetime
    week_days: tuple[WeekDay, ...]
    temperature: TemperatureReading


@dataclass(frozen=True, slots=True)
class DelayedClimateSchedule:
    """The one-time delayed climate start configured for an Ariya."""

    start_date_time: datetime | None


@dataclass(frozen=True, slots=True)
class VehicleClimateSchedules:
    """Recurring schedules and vehicle-level climate schedule settings."""

    schedules: tuple[ClimateSchedule, ...]
    accessories: ClimateParameters | None
    delayed_schedule: DelayedClimateSchedule | None


@dataclass(frozen=True, slots=True)
class ClimateDefaults:
    """The vehicle's saved default climate configuration."""

    climate: TemperatureReading | None
    parameters: ClimateParameters | None
