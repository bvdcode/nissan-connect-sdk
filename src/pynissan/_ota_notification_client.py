from __future__ import annotations

from datetime import datetime

from . import operations
from ._client_base import _NissanClientBase
from .device_notification_inputs import (
    MobileInfoInput,
    register_device_for_push_notifications_variables,
    register_push_notifications_variables,
    unregister_device_for_push_notifications_variables,
    unregister_push_notifications_variables,
)
from .device_notification_models import (
    DeviceOS,
    PushNotificationResult,
)
from .device_notification_parsing import (
    parse_register_device_for_push_notifications,
    parse_register_push_notifications,
    parse_unregister_device_for_push_notifications,
    parse_unregister_push_notifications,
)
from .graphql_input import UNSET, UnsetType, optional_input_fields
from .models import (
    ServiceRequest,
    ServiceRequestKind,
)
from .notification_inputs import (
    NotificationPreferenceInput,
    notification_preferences_input,
    update_nissan_energy_notification_preferences_variables,
)
from .notification_models import (
    NissanEnergyNotificationPreferencesUpdate,
    NotificationPreference,
)
from .notification_parsing import (
    parse_notification_preferences,
    parse_update_nissan_energy_notification_preferences,
)
from .ota_inputs import (
    data_wipe_type_input,
    download_ota_update_input,
    ota_activation_schedule_input,
)
from .ota_models import DataWipeType


class _OtaNotificationClientMixin(_NissanClientBase):
    async def async_download_ota_update(
        self,
        vin: str,
        ota_update_id: str,
    ) -> ServiceRequest:
        """Ask a compatible vehicle to download an offered OTA campaign."""

        return await self._async_service_request(
            "DownloadOTAUpdate",
            operations.DOWNLOAD_OTA_UPDATE,
            "downloadOTAUpdate",
            {
                "vin": vin,
                "input": download_ota_update_input(ota_update_id),
            },
            ServiceRequestKind.OTA,
        )

    async def async_activate_ota_update(
        self,
        vin: str,
        ota_update_id: str,
    ) -> ServiceRequest:
        """Ask a compatible vehicle to activate a downloaded OTA campaign."""

        return await self._async_service_request(
            "ActivateOTAUpdate",
            operations.ACTIVATE_OTA_UPDATE,
            "activateOTAUpdate",
            {"vin": vin, "otaUpdateId": ota_update_id},
            ServiceRequestKind.OTA,
        )

    async def async_cancel_ota_activation(
        self,
        vin: str,
        ota_update_id: str,
    ) -> ServiceRequest:
        """Cancel an OTA campaign activation in progress."""

        return await self._async_service_request(
            "CancelActivationOTAUpdate",
            operations.CANCEL_ACTIVATION_OTA_UPDATE,
            "cancelActivationOTAUpdate",
            {"vin": vin, "otaUpdateId": ota_update_id},
            ServiceRequestKind.OTA,
        )

    async def async_schedule_ota_activation(
        self,
        vin: str,
        ota_update_id: str,
        scheduled_date: datetime,
    ) -> ServiceRequest:
        """Schedule activation of a downloaded OTA campaign."""

        return await self._async_service_request(
            "ScheduleActivationOTAUpdate",
            operations.SCHEDULE_ACTIVATION_OTA_UPDATE,
            "scheduleActivationOTAUpdate",
            {
                "vin": vin,
                "input": ota_activation_schedule_input(
                    ota_update_id,
                    scheduled_date,
                ),
            },
            ServiceRequestKind.OTA,
        )

    async def async_update_scheduled_ota_activation(
        self,
        vin: str,
        ota_update_id: str,
        scheduled_date: datetime,
    ) -> ServiceRequest:
        """Move an already scheduled OTA campaign activation."""

        return await self._async_service_request(
            "UpdateScheduledActivationOTAUpdate",
            operations.UPDATE_SCHEDULED_ACTIVATION_OTA_UPDATE,
            "updateScheduledActivationOTAUpdate",
            {
                "vin": vin,
                "input": ota_activation_schedule_input(
                    ota_update_id,
                    scheduled_date,
                ),
            },
            ServiceRequestKind.OTA,
        )

    async def async_cancel_scheduled_ota_activation(
        self,
        vin: str,
        ota_update_id: str,
    ) -> ServiceRequest:
        """Cancel a scheduled OTA campaign activation."""

        return await self._async_service_request(
            "CancelScheduledActivationOTAUpdate",
            operations.CANCEL_SCHEDULED_ACTIVATION_OTA_UPDATE,
            "cancelScheduledActivationOTAUpdate",
            {"vin": vin, "otaUpdateId": ota_update_id},
            ServiceRequestKind.OTA,
        )

    async def async_wipe_vehicle_data(
        self,
        vin: str,
        *,
        data_wipe_type: DataWipeType | UnsetType | None = UNSET,
    ) -> ServiceRequest:
        """Submit Nissan's remote vehicle data-wipe operation."""

        serialized_type: object = data_wipe_type
        if isinstance(data_wipe_type, DataWipeType):
            serialized_type = data_wipe_type_input(data_wipe_type)
        return await self._async_service_request(
            "DataWipe",
            operations.DATA_WIPE,
            "dataWipe",
            optional_input_fields(vin=vin, dataWipeType=serialized_type),
            ServiceRequestKind.DATA_WIPE,
        )

    async def async_set_notification_preferences(
        self,
        vin: str,
        preferences: tuple[NotificationPreferenceInput | None, ...],
    ) -> tuple[NotificationPreference | None, ...] | None:
        """Replace vehicle notification opt-ins with the supplied preferences."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "SetNotificationPreferences",
            operations.SET_NOTIFICATION_PREFERENCES,
            {
                "vin": vin,
                "preferences": notification_preferences_input(preferences),
            },
        )
        return parse_notification_preferences(data, "setNotificationPreferences")

    async def async_update_nissan_energy_notification_preferences(
        self,
        vin: str,
        *,
        email_status: bool | UnsetType | None = UNSET,
        push_status: bool | UnsetType | None = UNSET,
        sms_status: bool | UnsetType | None = UNSET,
    ) -> NissanEnergyNotificationPreferencesUpdate | None:
        """Patch Nissan Energy delivery flags, preserving omitted and null values."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateNotificationPreferences",
            operations.UPDATE_NISSAN_ENERGY_NOTIFICATION_PREFERENCES,
            update_nissan_energy_notification_preferences_variables(
                vin,
                email_status=email_status,
                push_status=push_status,
                sms_status=sms_status,
            ),
        )
        return parse_update_nissan_energy_notification_preferences(data)

    async def async_register_push_notifications(
        self,
        device_id: str,
        token: str,
        device_os: DeviceOS,
    ) -> bool | None:
        """Register a legacy push token for the authenticated account."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "RegisterPushNotifications",
            operations.REGISTER_PUSH_NOTIFICATIONS,
            register_push_notifications_variables(device_id, token, device_os),
        )
        return parse_register_push_notifications(data)

    async def async_unregister_push_notifications(
        self,
        device_id: str,
        device_os: DeviceOS,
    ) -> bool | None:
        """Unregister a legacy push token for the authenticated account."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UnregisterPushNotifications",
            operations.UNREGISTER_PUSH_NOTIFICATIONS,
            unregister_push_notifications_variables(device_id, device_os),
        )
        return parse_unregister_push_notifications(data)

    async def async_register_device_for_push_notifications(
        self,
        mobile_info: MobileInfoInput,
    ) -> PushNotificationResult | None:
        """Register a mobile installation through Nissan's current push API."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "RegisterDeviceForPushNotifications",
            operations.REGISTER_DEVICE_FOR_PUSH_NOTIFICATIONS,
            register_device_for_push_notifications_variables(mobile_info),
        )
        return parse_register_device_for_push_notifications(data)

    async def async_unregister_device_for_push_notifications(
        self,
        app_name: str,
        device_id: str,
        device_os: DeviceOS,
    ) -> PushNotificationResult | None:
        """Unregister a mobile installation from Nissan's current push API."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UnregisterDeviceForPushNotifications",
            operations.UNREGISTER_DEVICE_FOR_PUSH_NOTIFICATIONS,
            unregister_device_for_push_notifications_variables(
                app_name,
                device_id,
                device_os,
            ),
        )
        return parse_unregister_device_for_push_notifications(data)
