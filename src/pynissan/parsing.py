"""Core vehicle response parsers."""

from ._vehicle_alert_parsing import (
    parse_remote_service_history,
)
from ._vehicle_capability_parsing import (
    parse_vehicle_capabilities,
)
from ._vehicle_core_parsing import (
    parse_alert_request_status,
    parse_breach_alerts,
    parse_photos_around_vehicle,
    parse_reminder_notifications_after_leaving_vehicle,
    parse_toggle_reminder_notifications_after_leaving_vehicle,
    parse_vehicle_alert_request,
    parse_vehicle_alerts,
    parse_vehicle_data_privacy_mode,
    parse_vehicle_location,
    parse_vehicle_status,
    parse_vehicles,
)
from ._vehicle_energy_parsing import (
    parse_charge_config,
    parse_charge_schedules,
    parse_climate_defaults,
    parse_climate_schedules,
    parse_v2l_status,
    parse_vehicle_charge_history,
)
from ._vehicle_response_parsing import (
    parse_service_request,
    parse_service_request_result,
)
from ._vehicle_subscription_parsing import (
    parse_vehicle_preferences,
    parse_vehicle_subscriptions,
    parse_vehicle_wifi_consumption,
)

__all__ = (
    "parse_alert_request_status",
    "parse_breach_alerts",
    "parse_charge_config",
    "parse_charge_schedules",
    "parse_climate_defaults",
    "parse_climate_schedules",
    "parse_photos_around_vehicle",
    "parse_reminder_notifications_after_leaving_vehicle",
    "parse_remote_service_history",
    "parse_service_request",
    "parse_service_request_result",
    "parse_toggle_reminder_notifications_after_leaving_vehicle",
    "parse_v2l_status",
    "parse_vehicle_alert_request",
    "parse_vehicle_alerts",
    "parse_vehicle_capabilities",
    "parse_vehicle_charge_history",
    "parse_vehicle_data_privacy_mode",
    "parse_vehicle_location",
    "parse_vehicle_preferences",
    "parse_vehicle_status",
    "parse_vehicle_subscriptions",
    "parse_vehicle_wifi_consumption",
    "parse_vehicles",
)
