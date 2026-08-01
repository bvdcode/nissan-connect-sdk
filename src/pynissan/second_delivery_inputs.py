from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .common_inputs import AddressInput, address_input
from .graphql_input import (
    UNSET,
    UnsetType,
    optional_input_fields,
    serialize_datetime,
    serialize_enum,
)


class SecondDeliveryAppointmentMode(StrEnum):
    """Known second-delivery appointment modes."""

    AT_HOME = "AT_HOME"
    AT_DEALER = "AT_DEALER"
    VIRTUAL = "VIRTUAL"
    UNKNOWN_VALUE = "UNKNOWN__"


@dataclass(frozen=True, slots=True)
class SecondDeliveryContactInput:
    """Required second-delivery customer contact fields."""

    first_name: str
    last_name: str
    phone_number: str
    email: str


@dataclass(frozen=True, slots=True)
class SecondDeliveryAppointmentInput:
    """Fields used to create or replace a second-delivery appointment."""

    vin: str
    address: AddressInput
    contact: SecondDeliveryContactInput
    time_slot_id: int
    redelivery_notes: str | UnsetType | None = UNSET
    feature_notes: str | UnsetType | None = UNSET
    mode: SecondDeliveryAppointmentMode | UnsetType | None = UNSET


def second_delivery_appointment_variables(
    config: SecondDeliveryAppointmentInput,
) -> dict[str, object]:
    """Serialize second-delivery appointment creation variables."""

    mode: object = config.mode
    if isinstance(config.mode, SecondDeliveryAppointmentMode):
        mode = serialize_enum(config.mode)
    return optional_input_fields(
        vin=config.vin,
        address=address_input(config.address),
        contactInformation=_contact_input(config.contact),
        timeSlotId=config.time_slot_id,
        redeliveryNotes=config.redelivery_notes,
        featureNotes=config.feature_notes,
        mode=mode,
    )


def update_second_delivery_appointment_variables(
    activity_id: int,
    config: SecondDeliveryAppointmentInput,
) -> dict[str, object]:
    """Serialize second-delivery appointment replacement variables."""

    return optional_input_fields(
        vin=config.vin,
        activityId=activity_id,
        address=address_input(config.address),
        contactInformation=_contact_input(config.contact),
        timeSlotId=config.time_slot_id,
        redeliveryNotes=config.redelivery_notes,
        featureNotes=config.feature_notes,
    )


def second_delivery_home_slots_variables(
    vin: str,
    address: AddressInput,
    hub_id: str,
    start: datetime,
    end: datetime,
) -> dict[str, object]:
    """Serialize second-delivery at-home time-slot variables."""

    return {
        "vin": vin,
        "address": address_input(address),
        "hubId": hub_id,
        "start": serialize_datetime(start),
        "end": serialize_datetime(end),
    }


def second_delivery_location_slots_variables(
    hub_id: str,
    postal_code: str,
    start: datetime,
    end: datetime,
    vin: str,
) -> dict[str, object]:
    """Serialize at-hub or virtual second-delivery time-slot variables."""

    return {
        "hubId": hub_id,
        "zipCode": postal_code,
        "start": serialize_datetime(start),
        "end": serialize_datetime(end),
        "vin": vin,
    }


def second_delivery_send_auth_code_variables(
    appointment_id: int,
    access_token: str,
    send_via_email: bool,
    send_via_sms: bool,
) -> dict[str, object]:
    """Serialize second-delivery authentication-code delivery variables."""

    return {
        "appointmentId": appointment_id,
        "accessToken": access_token,
        "sendViaEmail": send_via_email,
        "sendViaSMS": send_via_sms,
    }


def second_delivery_verify_auth_code_variables(
    appointment_id: int,
    access_token: str,
    auth_code: str,
) -> dict[str, object]:
    """Serialize second-delivery authentication-code verification variables."""

    return {
        "appointmentId": appointment_id,
        "accessToken": access_token,
        "authCode": auth_code,
    }


def _contact_input(value: SecondDeliveryContactInput) -> dict[str, object]:
    return {
        "firstName": value.first_name,
        "lastName": value.last_name,
        "phoneNumber": value.phone_number,
        "email": value.email,
    }
