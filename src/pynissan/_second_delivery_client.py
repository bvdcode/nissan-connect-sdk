from __future__ import annotations

from datetime import datetime

from . import operations
from ._client_base import _NissanClientBase
from .common_inputs import AddressInput, address_input
from .second_delivery_inputs import (
    SecondDeliveryAppointmentInput,
    second_delivery_appointment_variables,
    second_delivery_home_slots_variables,
    second_delivery_location_slots_variables,
    second_delivery_send_auth_code_variables,
    second_delivery_verify_auth_code_variables,
    update_second_delivery_appointment_variables,
)
from .second_delivery_models import (
    SecondDeliveryAddressValidationResult,
    SecondDeliveryAppointmentResult,
    SecondDeliveryEligibility,
    SecondDeliveryOperationResult,
    SecondDeliveryTimeSlotsResult,
)
from .second_delivery_parsing import (
    parse_cancel_second_delivery_appointment,
    parse_create_second_delivery_appointment,
    parse_second_delivery_address_validation,
    parse_second_delivery_appointment,
    parse_second_delivery_eligibility,
    parse_second_delivery_home_time_slots,
    parse_second_delivery_hub_time_slots,
    parse_second_delivery_send_auth_code,
    parse_second_delivery_verify_auth_code,
    parse_second_delivery_virtual_time_slots,
    parse_update_second_delivery_appointment,
)


class _SecondDeliveryClientMixin(_NissanClientBase):
    async def async_get_second_delivery_appointment(
        self,
        vin: str,
    ) -> SecondDeliveryAppointmentResult | None:
        """Return the existing second-delivery appointment state."""

        data = await self._transport.async_graphql(
            "SecondDeliveryAppointment",
            operations.SECOND_DELIVERY_APPOINTMENT,
            {"vin": vin},
        )
        return parse_second_delivery_appointment(data)

    async def async_get_second_delivery_home_time_slots(
        self,
        vin: str,
        address: AddressInput,
        hub_id: str,
        start: datetime,
        end: datetime,
    ) -> SecondDeliveryTimeSlotsResult | None:
        """Return at-home second-delivery appointment time slots."""

        data = await self._transport.async_graphql(
            "SecondDeliveryAppointmentsAtHome",
            operations.SECOND_DELIVERY_APPOINTMENTS_AT_HOME,
            second_delivery_home_slots_variables(vin, address, hub_id, start, end),
        )
        return parse_second_delivery_home_time_slots(data)

    async def async_get_second_delivery_hub_time_slots(
        self,
        hub_id: str,
        postal_code: str,
        start: datetime,
        end: datetime,
        vin: str,
    ) -> SecondDeliveryTimeSlotsResult | None:
        """Return in-hub second-delivery appointment time slots."""

        data = await self._transport.async_graphql(
            "SecondDeliveryAppointmentsAtHub",
            operations.SECOND_DELIVERY_APPOINTMENTS_AT_HUB,
            second_delivery_location_slots_variables(
                hub_id,
                postal_code,
                start,
                end,
                vin,
            ),
        )
        return parse_second_delivery_hub_time_slots(data)

    async def async_get_second_delivery_virtual_time_slots(
        self,
        hub_id: str,
        postal_code: str,
        start: datetime,
        end: datetime,
        vin: str,
    ) -> SecondDeliveryTimeSlotsResult | None:
        """Return virtual second-delivery appointment time slots."""

        data = await self._transport.async_graphql(
            "SecondDeliveryAppointmentsAtVirtual",
            operations.SECOND_DELIVERY_APPOINTMENTS_AT_VIRTUAL,
            second_delivery_location_slots_variables(
                hub_id,
                postal_code,
                start,
                end,
                vin,
            ),
        )
        return parse_second_delivery_virtual_time_slots(data)

    async def async_get_second_delivery_eligibility(
        self,
        vin: str,
    ) -> SecondDeliveryEligibility | None:
        """Return second-delivery eligibility and CTA state."""

        data = await self._transport.async_graphql(
            "SecondDeliveryEligibility",
            operations.SECOND_DELIVERY_ELIGIBILITY,
            {"vin": vin},
        )
        return parse_second_delivery_eligibility(data)

    async def async_validate_second_delivery_address(
        self,
        vin: str,
        address: AddressInput,
    ) -> SecondDeliveryAddressValidationResult | None:
        """Validate an address for at-home second delivery."""

        data = await self._transport.async_graphql(
            "ValidateSecondDeliveryAddress",
            operations.VALIDATE_SECOND_DELIVERY_ADDRESS,
            {"vin": vin, "address": address_input(address)},
        )
        return parse_second_delivery_address_validation(data)

    async def async_cancel_second_delivery_appointment(
        self,
        activity_id: int,
    ) -> SecondDeliveryOperationResult | None:
        """Cancel a second-delivery appointment."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CancelSecondDeliveryAppointment",
            operations.CANCEL_SECOND_DELIVERY_APPOINTMENT,
            {"activityId": activity_id},
        )
        return parse_cancel_second_delivery_appointment(data)

    async def async_create_second_delivery_appointment(
        self,
        appointment: SecondDeliveryAppointmentInput,
    ) -> SecondDeliveryOperationResult | None:
        """Create a second-delivery appointment."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CreateSecondDeliveryAppointment",
            operations.CREATE_SECOND_DELIVERY_APPOINTMENT,
            second_delivery_appointment_variables(appointment),
        )
        return parse_create_second_delivery_appointment(data)

    async def async_second_delivery_send_auth_code(
        self,
        appointment_id: int,
        access_token: str,
        *,
        send_via_email: bool,
        send_via_sms: bool,
    ) -> SecondDeliveryOperationResult | None:
        """Send a second-delivery appointment authentication code."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "SecondDeliverySendAuthCode",
            operations.SECOND_DELIVERY_SEND_AUTH_CODE,
            second_delivery_send_auth_code_variables(
                appointment_id,
                access_token,
                send_via_email,
                send_via_sms,
            ),
        )
        return parse_second_delivery_send_auth_code(data)

    async def async_second_delivery_verify_auth_code(
        self,
        appointment_id: int,
        access_token: str,
        auth_code: str,
    ) -> SecondDeliveryOperationResult | None:
        """Verify a second-delivery appointment authentication code."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "SecondDeliveryVerifyAuthCode",
            operations.SECOND_DELIVERY_VERIFY_AUTH_CODE,
            second_delivery_verify_auth_code_variables(
                appointment_id,
                access_token,
                auth_code,
            ),
        )
        return parse_second_delivery_verify_auth_code(data)

    async def async_update_second_delivery_appointment(
        self,
        activity_id: int,
        appointment: SecondDeliveryAppointmentInput,
    ) -> SecondDeliveryOperationResult | None:
        """Replace a second-delivery appointment's selected details."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateSecondDeliveryAppointment",
            operations.UPDATE_SECOND_DELIVERY_APPOINTMENT,
            update_second_delivery_appointment_variables(activity_id, appointment),
        )
        return parse_update_second_delivery_appointment(data)
