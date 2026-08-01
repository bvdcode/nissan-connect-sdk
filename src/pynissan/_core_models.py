from __future__ import annotations

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


_SUCCESSFUL_SERVICE_REQUEST_STATUSES: frozenset[ServiceRequestStatus] = frozenset(
    {
        ServiceRequestStatus.SUCCESS,
        ServiceRequestStatus.SUCCESS_EXECUTION_CONFIRMED,
        ServiceRequestStatus.CANCELLATION_SUCCESS,
        ServiceRequestStatus.CANCEL_UPDATE_SUCCESS,
        ServiceRequestStatus.UPDATE_SUCCESS,
    }
)

_TERMINAL_SERVICE_REQUEST_STATUSES: frozenset[ServiceRequestStatus] = frozenset(
    {
        *_SUCCESSFUL_SERVICE_REQUEST_STATUSES,
        ServiceRequestStatus.FAILED,
        ServiceRequestStatus.CANCELLATION_FAILED,
        ServiceRequestStatus.CANCEL_UPDATE_FAILED,
        ServiceRequestStatus.UPDATE_FAILED,
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
