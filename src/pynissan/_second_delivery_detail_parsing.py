from __future__ import annotations

from collections.abc import Mapping

from ._second_delivery_value_parsing import (
    _required_datetime,
    _required_nullable_datetime,
    _required_nullable_float,
)
from .account_parsing import (
    _enum,
    _required_field,
    _required_nullable_bool,
    _required_nullable_int,
    _required_nullable_string,
    _required_optional_typed_object,
    _root,
    _typed_object,
    _typename,
)
from .exceptions import ResponseError
from .second_delivery_inputs import SecondDeliveryAppointmentMode
from .second_delivery_models import (
    SecondDeliveryAddress,
    SecondDeliveryAddressNotServiced,
    SecondDeliveryAppointmentBooked,
    SecondDeliveryAppointmentCompleted,
    SecondDeliveryAppointmentReference,
    SecondDeliveryAppointmentStatus,
    SecondDeliveryBookedAppointment,
    SecondDeliveryCallToAction,
    SecondDeliveryContact,
    SecondDeliveryCoordinates,
    SecondDeliveryDealer,
    SecondDeliveryEligibilityError,
    SecondDeliveryEligibilityResult,
    SecondDeliveryEligible,
    SecondDeliveryHub,
    SecondDeliveryLeadCar,
    SecondDeliveryMarketingMessage,
    SecondDeliveryMarketingVersion,
    SecondDeliverySlotsByDate,
    SecondDeliveryTimeSlot,
    SecondDeliveryTimeSlots,
    SecondDeliveryTimeSlotsResult,
    UnselectedSecondDeliveryResult,
)


def _second_delivery(data: Mapping[str, object]) -> Mapping[str, object] | None:
    vehicle = _root(data, "vehicle")
    if vehicle is None:
        return None
    return _required_optional_typed_object(
        vehicle,
        "secondDelivery",
        "vehicle.secondDelivery",
    )


def _second_delivery_field(
    data: Mapping[str, object],
    field: str,
) -> Mapping[str, object] | None:
    second_delivery = _second_delivery(data)
    if second_delivery is None:
        return None
    return _required_optional_typed_object(
        second_delivery,
        field,
        f"vehicle.secondDelivery.{field}",
    )


def _parse_booked_appointment(
    value: Mapping[str, object],
    path: str,
) -> SecondDeliveryBookedAppointment:
    address_path = f"{path}.address"
    address = _required_optional_typed_object(value, "address", address_path)
    contact_path = f"{path}.contact"
    contact = _required_optional_typed_object(value, "contact", contact_path)
    hub_path = f"{path}.hub"
    hub = _required_optional_typed_object(value, "hub", hub_path)
    mode = _required_field(value, "mode", f"{path}.mode")
    return SecondDeliveryBookedAppointment(
        id=_required_nullable_int(value, "id", f"{path}.id"),
        activity_id=_required_nullable_int(value, "activityId", f"{path}.activityId"),
        begins_at=_required_nullable_datetime(value, "beginsAt", f"{path}.beginsAt"),
        address=_parse_address(address, address_path),
        contact=(
            None
            if contact is None
            else SecondDeliveryContact(
                first_name=_required_nullable_string(
                    contact,
                    "firstName",
                    f"{contact_path}.firstName",
                ),
                last_name=_required_nullable_string(
                    contact,
                    "lastName",
                    f"{contact_path}.lastName",
                ),
                phone_number=_required_nullable_string(
                    contact,
                    "phoneNumber",
                    f"{contact_path}.phoneNumber",
                ),
                email=_required_nullable_string(contact, "email", f"{contact_path}.email"),
            )
        ),
        redelivery_notes=_required_nullable_string(
            value,
            "redeliveryNotes",
            f"{path}.redeliveryNotes",
        ),
        feature_notes=_required_nullable_string(value, "featureNotes", f"{path}.featureNotes"),
        hub=_parse_hub(hub, hub_path, include_dealer=True),
        mode=(None if mode is None else _enum(mode, SecondDeliveryAppointmentMode, f"{path}.mode")),
    )


def _parse_appointment_reference(
    value: Mapping[str, object] | None,
    path: str,
) -> SecondDeliveryAppointmentReference | None:
    if value is None:
        return None
    status = _required_field(value, "status", f"{path}.status")
    return SecondDeliveryAppointmentReference(
        id=_required_nullable_int(value, "id", f"{path}.id"),
        access_token=_required_nullable_string(value, "accessToken", f"{path}.accessToken"),
        status=(
            None
            if status is None
            else _enum(status, SecondDeliveryAppointmentStatus, f"{path}.status")
        ),
    )


def _parse_time_slots(
    data: Mapping[str, object],
    mode_field: str,
) -> SecondDeliveryTimeSlotsResult | None:
    second_delivery = _second_delivery(data)
    if second_delivery is None:
        return None
    appointments_path = "vehicle.secondDelivery.appointments"
    appointments = _required_optional_typed_object(
        second_delivery,
        "appointments",
        appointments_path,
    )
    if appointments is None:
        return None
    path = f"{appointments_path}.{mode_field}"
    root = _required_optional_typed_object(appointments, mode_field, path)
    if root is None:
        return None
    typename = _typename(root, path)
    if typename == "SecondDeliveryAppointmentTimeSlotsErrorAddressNotServicedResponse":
        return SecondDeliveryAddressNotServiced(
            _required_nullable_string(root, "message", f"{path}.message")
        )
    if typename != "SecondDeliveryAppointmentTimeSlotsSuccessResponse":
        return UnselectedSecondDeliveryResult(typename)
    hub_path = f"{path}.hub"
    hub = _required_optional_typed_object(root, "hub", hub_path)
    slots_value = _required_field(root, "slotsByDate", f"{path}.slotsByDate")
    if not isinstance(slots_value, list):
        raise ResponseError(f"{path}.slotsByDate is not a list")
    slots: list[SecondDeliverySlotsByDate | None] = []
    for index, item in enumerate(slots_value):
        if item is None:
            slots.append(None)
            continue
        item_path = f"{path}.slotsByDate[{index}]"
        slots.append(_parse_slots_by_date(_typed_object(item, item_path), item_path))
    return SecondDeliveryTimeSlots(_parse_hub(hub, hub_path, include_dealer=False), tuple(slots))


def _parse_slots_by_date(
    value: Mapping[str, object],
    path: str,
) -> SecondDeliverySlotsByDate:
    time_slots_value = _required_field(value, "timeslots", f"{path}.timeslots")
    time_slots = None
    if time_slots_value is not None:
        if not isinstance(time_slots_value, list):
            raise ResponseError(f"{path}.timeslots is not a list")
        parsed: list[SecondDeliveryTimeSlot | None] = []
        for index, item in enumerate(time_slots_value):
            if item is None:
                parsed.append(None)
                continue
            item_path = f"{path}.timeslots[{index}]"
            time_slot = _typed_object(item, item_path)
            parsed.append(
                SecondDeliveryTimeSlot(
                    time=_required_nullable_datetime(time_slot, "time", f"{item_path}.time"),
                    id=_required_nullable_int(time_slot, "id", f"{item_path}.id"),
                )
            )
        time_slots = tuple(parsed)
    return SecondDeliverySlotsByDate(
        date=_required_datetime(value, "date", f"{path}.date"),
        time_slots=time_slots,
    )


def _parse_eligibility_result(
    value: Mapping[str, object] | None,
    path: str,
) -> SecondDeliveryEligibilityResult | None:
    if value is None:
        return None
    typename = _typename(value, path)
    if typename == "SecondDeliveryEligibilityResponseRDRRecordFound":
        hub_path = f"{path}.hub"
        hub = _required_optional_typed_object(value, "hub", hub_path)
        lead_car_path = f"{path}.leadCar"
        lead_car = _required_optional_typed_object(value, "leadCar", lead_car_path)
        return SecondDeliveryEligible(
            hub=_parse_hub(hub, hub_path, include_dealer=True),
            lead_car=_parse_lead_car(lead_car, lead_car_path),
            redelivery_lead_id=_required_nullable_int(
                value,
                "redeliveryLeadId",
                f"{path}.redeliveryLeadId",
            ),
            days_since_retail_sales_date=_required_nullable_int(
                value,
                "daysSinceRetailSalesDate",
                f"{path}.daysSinceRetailSalesDate",
            ),
        )
    if typename in {
        "SecondDeliveryEligibilityResponseAppointmentBooked",
        "SecondDeliveryEligibilityResponseAppointmentCompleted",
    }:
        appointment_path = f"{path}.appointment"
        appointment = _required_optional_typed_object(value, "appointment", appointment_path)
        reference = _parse_appointment_reference(appointment, appointment_path)
        if typename == "SecondDeliveryEligibilityResponseAppointmentBooked":
            return SecondDeliveryAppointmentBooked(reference)
        return SecondDeliveryAppointmentCompleted(reference)
    if typename in {
        "SecondDeliveryEligibilityResponseNonParticipatingDealer",
        "SecondDeliveryEligibilityResponseVinNotFound",
    }:
        return SecondDeliveryEligibilityError(
            typename,
            _required_nullable_string(value, "message", f"{path}.message"),
        )
    return UnselectedSecondDeliveryResult(typename)


def _parse_call_to_action(
    value: Mapping[str, object] | None,
    path: str,
) -> SecondDeliveryCallToAction | None:
    if value is None:
        return None
    marketing_path = f"{path}.marketingMessage"
    marketing = _required_optional_typed_object(value, "marketingMessage", marketing_path)
    discover_path = f"{path}.discover"
    discover = _required_optional_typed_object(value, "discover", discover_path)
    marketing_result = None
    if marketing is not None:
        version = _required_field(
            marketing, "versionToDisplay", f"{marketing_path}.versionToDisplay"
        )
        marketing_result = SecondDeliveryMarketingMessage(
            version=(
                None
                if version is None
                else _enum(
                    version,
                    SecondDeliveryMarketingVersion,
                    f"{marketing_path}.versionToDisplay",
                )
            ),
            display_threshold_days=_required_nullable_int(
                marketing,
                "displayMarketingMessageThresholdInDays",
                f"{marketing_path}.displayMarketingMessageThresholdInDays",
            ),
            remind_later_threshold_days=_required_nullable_int(
                marketing,
                "remindMeLaterThresholdInDays",
                f"{marketing_path}.remindMeLaterThresholdInDays",
            ),
        )
    return SecondDeliveryCallToAction(
        marketing_message=marketing_result,
        discover_prioritized=(
            None
            if discover is None
            else _required_nullable_bool(
                discover,
                "prioritized",
                f"{discover_path}.prioritized",
            )
        ),
        days_since_purchased=_required_nullable_int(
            value,
            "daysSincePurchased",
            f"{path}.daysSincePurchased",
        ),
    )


def _parse_lead_car(
    value: Mapping[str, object] | None,
    path: str,
) -> SecondDeliveryLeadCar | None:
    if value is None:
        return None
    return SecondDeliveryLeadCar(
        trim=_required_nullable_string(value, "trim", f"{path}.trim"),
        deleted=_required_nullable_bool(value, "deleted", f"{path}.deleted"),
        interior_color=_required_nullable_string(
            value,
            "interiorColor",
            f"{path}.interiorColor",
        ),
        retail_sales_date=_required_nullable_string(
            value,
            "retailSalesDate",
            f"{path}.retailSalesDate",
        ),
        plate=_required_nullable_string(value, "plate", f"{path}.plate"),
        brand=_required_nullable_string(value, "brand", f"{path}.brand"),
        year=_required_nullable_string(value, "year", f"{path}.year"),
        model=_required_nullable_string(value, "model", f"{path}.model"),
        mileage=_required_nullable_int(value, "mileage", f"{path}.mileage"),
        lead_id=_required_nullable_int(value, "leadId", f"{path}.leadId"),
        exterior_color=_required_nullable_string(
            value,
            "exteriorColor",
            f"{path}.exteriorColor",
        ),
        name=_required_nullable_string(value, "name", f"{path}.name"),
        vin=_required_nullable_string(value, "vin", f"{path}.vin"),
        id=_required_nullable_int(value, "id", f"{path}.id"),
    )


def _parse_hub(
    value: Mapping[str, object] | None,
    path: str,
    *,
    include_dealer: bool,
) -> SecondDeliveryHub | None:
    if value is None:
        return None
    dealer = None
    if include_dealer:
        dealer_path = f"{path}.dealer"
        dealer_value = _required_optional_typed_object(value, "dealer", dealer_path)
        if dealer_value is not None:
            address_path = f"{dealer_path}.address"
            address = _required_optional_typed_object(dealer_value, "address", address_path)
            dealer = SecondDeliveryDealer(
                code=_required_nullable_string(dealer_value, "code", f"{dealer_path}.code"),
                address=_parse_address(address, address_path),
            )
    return SecondDeliveryHub(
        id=_required_nullable_int(value, "id", f"{path}.id"),
        timezone=_required_nullable_string(value, "timezone", f"{path}.timezone"),
        dealer=dealer,
    )


def _parse_address(
    value: Mapping[str, object] | None,
    path: str,
) -> SecondDeliveryAddress | None:
    if value is None:
        return None
    coordinates = None
    if "coordinates" in value:
        coordinate_path = f"{path}.coordinates"
        coordinate_value = _required_optional_typed_object(value, "coordinates", coordinate_path)
        if coordinate_value is not None:
            coordinates = SecondDeliveryCoordinates(
                latitude=_required_nullable_float(
                    coordinate_value,
                    "latitude",
                    f"{coordinate_path}.latitude",
                ),
                longitude=_required_nullable_float(
                    coordinate_value,
                    "longitude",
                    f"{coordinate_path}.longitude",
                ),
            )
    return SecondDeliveryAddress(
        address_1=_required_nullable_string(value, "address1", f"{path}.address1"),
        address_2=_required_nullable_string(value, "address2", f"{path}.address2"),
        city=_required_nullable_string(value, "city", f"{path}.city"),
        state=_required_nullable_string(value, "state", f"{path}.state"),
        postal_code=_required_nullable_string(value, "postalCode", f"{path}.postalCode"),
        country=(
            None
            if "country" not in value
            else _required_nullable_string(value, "country", f"{path}.country")
        ),
        id=(None if "id" not in value else _required_nullable_int(value, "id", f"{path}.id")),
        coordinates=coordinates,
    )
