from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class NotificationCategory(StrEnum):
    """Known vehicle-notification categories exposed by Nissan."""

    DOOR_LOCK = "DOOR_LOCK"
    DOOR_UNLOCK = "DOOR_UNLOCK"
    ENGINE = "ENGINE"
    HORN_LIGHTS = "HORN_LIGHTS"
    LOCATION = "LOCATION"
    BOUNDARY_ALERTS = "BOUNDARY_ALERTS"
    CURFEW_ALERTS = "CURFEW_ALERTS"
    SPEED_ALERTS = "SPEED_ALERTS"
    STOLEN_VEHICLE = "STOLEN_VEHICLE"
    THEFT_ALARM = "THEFT_ALARM"
    MIL = "MIL"
    LAST_MILE_NAVIGATION = "LAST_MILE_NAVIGATION"
    VEHICLE_HEALTH_REPORT = "VEHICLE_HEALTH_REPORT"
    T_JUNCTION = "T_JUNCTION"
    EV_ROUTE_PLAN = "EV_ROUTE_PLAN"
    REMOTE_HVAC = "REMOTE_HVAC"
    VEHICLE_CHARGE = "VEHICLE_CHARGE"
    PLUGIN_REMINDER = "PLUGIN_REMINDER"
    ECALL_AUTOMATIC = "ECALL_AUTOMATIC"
    IRP_PRECONDITION_REMINDER = "IRP_PRECONDITION_REMINDER"
    MECHANICAL_ALERT = "MECHANICAL_ALERT"
    FIRMWARE_OVER_THE_AIR = "FIRMWARE_OVER_THE_AIR"
    BATTERY_HEATING = "BATTERY_HEATING"
    PREDICTIVE_MAINTENANCE_REMINDER = "PREDICTIVE_MAINTENANCE_REMINDER"
    PROACTIVE_MAINTENANCE_REMINDER = "PROACTIVE_MAINTENANCE_REMINDER"
    LEAVING_VEHICLE_REMINDER = "LEAVING_VEHICLE_REMINDER"
    INAPP_MESSAGING = "INAPP_MESSAGING"
    SMART_CHARGE = "SMART_CHARGE"
    POWER_STEERING_WARNING_ALERT = "POWER_STEERING_WARNING_ALERT"
    ELECTRIC_SHIFT_CONTROL_ALERT = "ELECTRIC_SHIFT_CONTROL_ALERT"
    AIRBAG_ALERT = "AIRBAG_ALERT"
    TWELVE_VOLT_BATTERY_WARNING_ALERT = "TWELVE_VOLT_BATTERY_WARNING_ALERT"
    OIL_PRESSURE_ALERT = "OIL_PRESSURE_ALERT"
    TIRE_PRESSURE_ALERT = "TIRE_PRESSURE_ALERT"
    BRAKES_ALERT = "BRAKES_ALERT"
    POWER_LIMITATION_ALERT = "POWER_LIMITATION_ALERT"
    CHECK_ENGINE_ALERT = "CHECK_ENGINE_ALERT"
    ABS_ALERT = "ABS_ALERT"
    OTA = "OTA"
    FOD = "FOD"
    VEHICLE_DYNAMIC_CONTROL_ALERT = "VEHICLE_DYNAMIC_CONTROL_ALERT"
    E_PARKING_BRAKE_ALERT = "E_PARKING_BRAKE_ALERT"
    AWD_ALERT = "AWD_ALERT"
    ENGINE_COOLANT_ALERT = "ENGINE_COOLANT_ALERT"
    I_KEY_ALERT = "I_KEY_ALERT"
    LOW_BEAM_ALERT = "LOW_BEAM_ALERT"
    UNKNOWN_VALUE = "UNKNOWN__"


class NotificationDestination(StrEnum):
    """Known delivery channels for vehicle notifications."""

    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"
    UNKNOWN_VALUE = "UNKNOWN__"


@dataclass(frozen=True, slots=True)
class NotificationTypePreference:
    """Opt-in state for one notification delivery channel."""

    destination: NotificationDestination
    opt_in: bool


@dataclass(frozen=True, slots=True)
class NotificationPreference:
    """Delivery preferences for one vehicle-notification category."""

    notification_category: NotificationCategory
    notification_type: tuple[NotificationTypePreference | None, ...]


@dataclass(frozen=True, slots=True)
class NissanEnergyNotificationPreferences:
    """Delivery flags for Nissan Energy Charge Network notifications."""

    email_status: bool | None
    push_status: bool | None
    sms_status: bool | None


@dataclass(frozen=True, slots=True)
class NissanEnergyNotificationPreferencesUpdate:
    """Status and resulting preferences returned by the Nissan Energy mutation."""

    status_code: str | None
    status_message: str | None
    timestamp: str | None
    preferences: NissanEnergyNotificationPreferences | None
