from __future__ import annotations

from collections.abc import Mapping

from ._second_delivery_detail_parsing import (
    _parse_address,
    _parse_appointment_reference,
    _parse_booked_appointment,
    _parse_call_to_action,
    _parse_eligibility_result,
    _parse_time_slots,
    _second_delivery,
    _second_delivery_field,
)
from ._second_delivery_value_parsing import _parse_operation_result
from .account_parsing import (
    _required_nullable_bool,
    _required_nullable_string,
    _required_optional_typed_object,
    _required_string,
    _typename,
)
from .second_delivery_models import (
    InvalidSecondDeliveryAddress,
    SecondDeliveryAddressValidationResult,
    SecondDeliveryAppointmentForbidden,
    SecondDeliveryAppointmentNotFound,
    SecondDeliveryAppointmentResult,
    SecondDeliveryEligibility,
    SecondDeliveryOperationResult,
    SecondDeliveryTimeSlotsResult,
    UnselectedSecondDeliveryResult,
    ValidSecondDeliveryAddress,
)


def parse_second_delivery_appointment(
    data: Mapping[str, object],
) -> SecondDeliveryAppointmentResult | None:
    """Parse every selected existing second-delivery appointment branch."""

    root = _second_delivery_field(data, "appointment")
    if root is None:
        return None
    typename = _typename(root, "vehicle.secondDelivery.appointment")
    if typename == "SecondDeliveryExistingBookedAppointment":
        return _parse_booked_appointment(root, "vehicle.secondDelivery.appointment")
    if typename == "SecondDeliveryBookedAppointmentNotExistError":
        return SecondDeliveryAppointmentNotFound(
            _required_string(
                root,
                "message",
                "vehicle.secondDelivery.appointment.message",
            )
        )
    if typename == "SecondDeliveryForbiddenError":
        path = "vehicle.secondDelivery.appointment"
        appointment_path = f"{path}.appointment"
        appointment = _required_optional_typed_object(root, "appointment", appointment_path)
        return SecondDeliveryAppointmentForbidden(
            message=_required_string(root, "message", f"{path}.message"),
            redacted_email=_required_nullable_string(
                root,
                "redactedEmail",
                f"{path}.redactedEmail",
            ),
            redacted_phone_number=_required_nullable_string(
                root,
                "redactedPhoneNumber",
                f"{path}.redactedPhoneNumber",
            ),
            appointment=_parse_appointment_reference(appointment, appointment_path),
        )
    return UnselectedSecondDeliveryResult(typename)


def parse_second_delivery_home_time_slots(
    data: Mapping[str, object],
) -> SecondDeliveryTimeSlotsResult | None:
    """Parse at-home second-delivery time slots."""

    return _parse_time_slots(data, "atHome")


def parse_second_delivery_hub_time_slots(
    data: Mapping[str, object],
) -> SecondDeliveryTimeSlotsResult | None:
    """Parse at-hub second-delivery time slots."""

    return _parse_time_slots(data, "atHub")


def parse_second_delivery_virtual_time_slots(
    data: Mapping[str, object],
) -> SecondDeliveryTimeSlotsResult | None:
    """Parse virtual second-delivery time slots."""

    return _parse_time_slots(data, "atVirtual")


def parse_second_delivery_eligibility(
    data: Mapping[str, object],
) -> SecondDeliveryEligibility | None:
    """Parse second-delivery eligibility and CTA state."""

    second_delivery = _second_delivery(data)
    if second_delivery is None:
        return None
    eligibility_path = "vehicle.secondDelivery.eligibility"
    eligibility = _required_optional_typed_object(
        second_delivery,
        "eligibility",
        eligibility_path,
    )
    cta_path = "vehicle.secondDelivery.cta"
    cta = _required_optional_typed_object(second_delivery, "cta", cta_path)
    return SecondDeliveryEligibility(
        result=_parse_eligibility_result(eligibility, eligibility_path),
        call_to_action=_parse_call_to_action(cta, cta_path),
    )


def parse_second_delivery_address_validation(
    data: Mapping[str, object],
) -> SecondDeliveryAddressValidationResult | None:
    """Parse every selected second-delivery address-validation branch."""

    path = "vehicle.secondDelivery.validateAddress"
    root = _second_delivery_field(data, "validateAddress")
    if root is None:
        return None
    typename = _typename(root, path)
    if typename == "ValidSecondDeliveryAddress":
        return ValidSecondDeliveryAddress(_required_nullable_bool(root, "valid", f"{path}.valid"))
    if typename == "InvalidSecondDeliveryAddress":
        address_path = f"{path}.dealerAddress"
        address = _required_optional_typed_object(root, "dealerAddress", address_path)
        return InvalidSecondDeliveryAddress(
            valid=_required_nullable_bool(root, "valid", f"{path}.valid"),
            dealer_address=_parse_address(address, address_path),
        )
    return UnselectedSecondDeliveryResult(typename)


def parse_cancel_second_delivery_appointment(
    data: Mapping[str, object],
) -> SecondDeliveryOperationResult | None:
    """Parse every selected second-delivery cancellation branch."""

    return _parse_operation_result(
        data,
        "cancelSecondDeliveryAppointment",
        "CancelSecondDeliveryAppointmentSuccessResponse",
        {"CancelSecondDeliveryAppointmentUnknownErrorResponse"},
    )


def parse_create_second_delivery_appointment(
    data: Mapping[str, object],
) -> SecondDeliveryOperationResult | None:
    """Parse every selected second-delivery creation branch."""

    return _parse_operation_result(
        data,
        "createSecondDeliveryAppointment",
        "CreateSecondDeliveryAppointmentSuccessResponse",
        {
            "CreateSecondDeliveryInvalidTimeSlotErrorResponse",
            "CreateSecondDeliveryAppointmentUnknownErrorResponse",
        },
    )


def parse_second_delivery_send_auth_code(
    data: Mapping[str, object],
) -> SecondDeliveryOperationResult | None:
    """Parse every selected authentication-code delivery branch."""

    return _parse_operation_result(
        data,
        "secondDeliverySendAuthCode",
        "SecondDeliverySendAuthCodeSuccessResponse",
        {"SecondDeliverySendAuthCodeErrorInvalidAccessTokenResponse"},
    )


def parse_second_delivery_verify_auth_code(
    data: Mapping[str, object],
) -> SecondDeliveryOperationResult | None:
    """Parse every selected authentication-code verification branch."""

    return _parse_operation_result(
        data,
        "secondDeliveryVerifyAuthCode",
        "SecondDeliveryVerifyAuthCodeSuccessResponse",
        {"SecondDeliveryVerifyAuthCodeErrorInvalidAuthResponse"},
    )


def parse_update_second_delivery_appointment(
    data: Mapping[str, object],
) -> SecondDeliveryOperationResult | None:
    """Parse every selected second-delivery update branch."""

    return _parse_operation_result(
        data,
        "updateSecondDeliveryAppointment",
        "UpdateSecondDeliveryAppointmentSuccessResponse",
        {
            "UpdateSecondDeliveryUpdateAppointmentTooSoonErrorResponse",
            "UpdateSecondDeliveryAppointmentUnknownErrorResponse",
        },
    )
