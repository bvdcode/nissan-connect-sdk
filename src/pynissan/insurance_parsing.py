from __future__ import annotations

from collections.abc import Mapping

from .account_parsing import (
    _required_enum,
    _required_field,
    _required_nullable_string,
    _required_optional_typed_object,
    _required_string,
    _root,
    _typed_object,
    _typename,
)
from .exceptions import ResponseError
from .insurance_models import (
    InsuranceContact,
    InsuranceStatus,
    UnselectedInsuranceResult,
    VehicleInsurance,
    VehicleInsuranceMutationError,
    VehicleInsuranceMutationResult,
    VehicleInsuranceMutationSuccess,
    VehicleInsurer,
)


def parse_add_vehicle_insurance(
    data: Mapping[str, object],
) -> VehicleInsuranceMutationResult | None:
    """Parse every generated add-insurance union branch."""

    return _parse_insurance_mutation(
        data,
        "addVehicleInsurance",
        "AddVehicleInsuranceSuccess",
        "AddVehicleInsuranceGeneralError",
    )


def parse_update_vehicle_insurance(
    data: Mapping[str, object],
) -> VehicleInsuranceMutationResult | None:
    """Parse every generated update-insurance union branch."""

    return _parse_insurance_mutation(
        data,
        "updateVehicleInsurance",
        "UpdateVehicleInsuranceSuccess",
        "UpdateVehicleInsuranceGeneralError",
    )


def parse_vehicle_insurance(data: Mapping[str, object]) -> VehicleInsurance | None:
    """Parse the nullable insurance policy attached to a nullable vehicle."""

    vehicle = _root(data, "vehicle")
    if vehicle is None:
        return None
    _typename(vehicle, "vehicle")
    insurance = _required_optional_typed_object(
        vehicle,
        "insurance",
        "vehicle.insurance",
    )
    if insurance is None:
        return None
    return _parse_vehicle_insurance(insurance, "vehicle.insurance")


def parse_insurers(
    data: Mapping[str, object],
) -> tuple[VehicleInsurer | None, ...] | None:
    """Parse the nullable insurer catalog and nullable list entries."""

    field = "insurers"
    value = _required_field(data, field, field)
    if value is None:
        return None
    if not isinstance(value, list):
        raise ResponseError(f"{field} is not a list")
    insurers: list[VehicleInsurer | None] = []
    for index, item in enumerate(value):
        if item is None:
            insurers.append(None)
            continue
        path = f"{field}[{index}]"
        insurers.append(_parse_insurer(_typed_object(item, path), path))
    return tuple(insurers)


def _parse_insurance_mutation(
    data: Mapping[str, object],
    field: str,
    success_typename: str,
    error_typename: str,
) -> VehicleInsuranceMutationResult | None:
    root = _root(data, field)
    if root is None:
        return None
    typename = _typename(root, field)
    if typename == success_typename:
        return VehicleInsuranceMutationSuccess(_required_bool(root, "success", f"{field}.success"))
    if typename == error_typename:
        return VehicleInsuranceMutationError(_required_string(root, "message", f"{field}.message"))
    return UnselectedInsuranceResult(typename)


def _parse_vehicle_insurance(
    value: Mapping[str, object],
    path: str,
) -> VehicleInsurance:
    _typename(value, path)
    insurer = _typed_object(
        _required_field(value, "insurer", f"{path}.insurer"),
        f"{path}.insurer",
    )
    return VehicleInsurance(
        id=_required_string(value, "id", f"{path}.id"),
        policy_number=_required_string(
            value,
            "policyNumber",
            f"{path}.policyNumber",
        ),
        expiration_date=_required_string(
            value,
            "expirationDate",
            f"{path}.expirationDate",
        ),
        status=_required_enum(value, "status", InsuranceStatus, f"{path}.status"),
        insurer=_parse_insurer(insurer, f"{path}.insurer"),
    )


def _parse_insurer(value: Mapping[str, object], path: str) -> VehicleInsurer:
    _typename(value, path)
    contacts_value = _required_field(value, "contacts", f"{path}.contacts")
    if not isinstance(contacts_value, list):
        raise ResponseError(f"{path}.contacts is not a list")
    contacts: list[InsuranceContact | None] = []
    for index, item in enumerate(contacts_value):
        if item is None:
            contacts.append(None)
            continue
        item_path = f"{path}.contacts[{index}]"
        contact = _typed_object(item, item_path)
        _typename(contact, item_path)
        contacts.append(
            InsuranceContact(
                _required_nullable_string(contact, "location", f"{item_path}.location"),
                _required_nullable_string(
                    contact,
                    "phoneNumber",
                    f"{item_path}.phoneNumber",
                ),
            )
        )
    return VehicleInsurer(
        id=_required_string(value, "id", f"{path}.id"),
        name=_required_string(value, "name", f"{path}.name"),
        contacts=tuple(contacts),
    )


def _required_bool(container: Mapping[str, object], field: str, path: str) -> bool:
    value = _required_field(container, field, path)
    if not isinstance(value, bool):
        raise ResponseError(f"{path} is not a boolean")
    return value
