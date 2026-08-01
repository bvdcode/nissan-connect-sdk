from __future__ import annotations

import hashlib
import re

import pytest
from test_garage import (
    EXPECTED_OPERATIONS,
    _union_payload,
)

from pynissan.garage_inputs import (
    NcarIcarRegisterAccountAddressInput,
    NcarIcarRegisterAccountInput,
    add_vehicle_variables,
    apc_agreement_variables,
    apc_document_url_variables,
    connected_terms_and_conditions_by_vin_variables,
    create_apc_agreement_variables,
    delete_vehicle_variables,
    ncar_icar_add_vehicle_variables,
    ncar_icar_register_account_address_input,
    ncar_icar_register_account_input,
    onboarding_features_variables,
    ownership_status_variables,
    pending_vehicles_variables,
    update_apc_agreement_variables,
    update_vehicle_manual_mileage_variables,
    update_vehicle_nickname_variables,
    update_vehicle_variables,
    upload_ownership_verification_variables,
)
from pynissan.garage_models import (
    AddVehicleSuccess,
    AgreementStatus,
    APCAgreement,
    APCDocument,
    DeleteVehicleError,
    DeleteVehicleSuccess,
    OwnershipStatus,
    PendingVehicle,
    RegisterCorporateVehicleEmailSentToPrimaryOwnerError,
    RegisterCorporateVehiclePrimaryOwnerConsentIsPendingError,
    RegisterGeneralError,
    RequireOwnershipVerification,
    VehicleHologram,
    VINAlreadyExistsInAnotherGarageError,
)
from pynissan.garage_parsing import (
    parse_add_vehicle,
    parse_apc_agreement,
    parse_apc_document_url,
    parse_delete_vehicle,
    parse_ncar_icar_add_vehicle,
    parse_ownership_status,
    parse_pending_vehicles,
)


@pytest.mark.parametrize(
    ("operation_name", "document", "operation_id", "token_hash"),
    [(operation_name, *values) for operation_name, values in EXPECTED_OPERATIONS.items()],
)
def test_garage_operations_match_service_documents_and_ids(
    operation_name: str,
    document: str,
    operation_id: str,
    token_hash: str,
) -> None:
    assert document.startswith((f"query {operation_name}", f"mutation {operation_name}"))
    assert hashlib.sha256(document.encode()).hexdigest() == operation_id
    tokens = " ".join(re.findall(r"\.\.\.|[_A-Za-z][_0-9A-Za-z]*|[$!():{}\[\]]", document))
    assert hashlib.sha256(tokens.encode()).hexdigest() == token_hash


def test_required_garage_variables_match_generated_operations() -> None:
    assert add_vehicle_variables("VIN", True) == {
        "vin": "VIN",
        "termsAndConditionsAccepted": True,
    }
    assert delete_vehicle_variables("VIN") == {"vin": "VIN"}
    assert pending_vehicles_variables() == {}
    assert ownership_status_variables("VIN") == {"vin": "VIN"}
    assert apc_agreement_variables("VIN") == {"vin": "VIN"}
    assert apc_document_url_variables("VIN") == {"vin": "VIN"}
    assert create_apc_agreement_variables("VIN", True) == {
        "optIn": True,
        "vin": "VIN",
    }
    assert update_apc_agreement_variables("VIN", False) == {
        "optIn": False,
        "vin": "VIN",
    }
    assert connected_terms_and_conditions_by_vin_variables("VIN") == {"vin": "VIN"}
    assert onboarding_features_variables("VIN") == {"vin": "VIN"}
    assert update_vehicle_nickname_variables("VIN", "Ariya") == {
        "vin": "VIN",
        "nickname": "Ariya",
    }
    assert upload_ownership_verification_variables(
        "VIN",
        "title.pdf",
        "BASE64",
        True,
    ) == {
        "vin": "VIN",
        "filename": "title.pdf",
        "attachment": "BASE64",
        "optInSMS": True,
    }


def test_ncar_icar_account_input_matches_all_non_null_generated_fields() -> None:
    address = NcarIcarRegisterAccountAddressInput(
        address_1="1 Main St",
        address_2="Unit 2",
        city="Franklin",
        state="TN",
        postal_code="37064",
        country="US",
    )
    account = NcarIcarRegisterAccountInput(
        first_name="Ada",
        last_name="Lovelace",
        email="ada@example.test",
        phone_number="+15555550100",
        address=address,
    )
    expected_address = {
        "address1": "1 Main St",
        "address2": "Unit 2",
        "city": "Franklin",
        "state": "TN",
        "postalCode": "37064",
        "country": "US",
    }
    expected_account = {
        "firstName": "Ada",
        "lastName": "Lovelace",
        "email": "ada@example.test",
        "phoneNumber": "+15555550100",
        "address": expected_address,
    }

    assert ncar_icar_register_account_address_input(address) == expected_address
    assert ncar_icar_register_account_input(account) == expected_account
    assert ncar_icar_add_vehicle_variables(True, "GUID", account=account) == {
        "termsAndConditionsAccepted": True,
        "guid": "GUID",
        "account": expected_account,
    }


def test_ncar_icar_nullable_account_preserves_omission_and_explicit_null() -> None:
    assert ncar_icar_add_vehicle_variables(False, "GUID") == {
        "termsAndConditionsAccepted": False,
        "guid": "GUID",
    }
    assert ncar_icar_add_vehicle_variables(False, "GUID", account=None) == {
        "termsAndConditionsAccepted": False,
        "guid": "GUID",
        "account": None,
    }


@pytest.mark.parametrize("hologram", list(VehicleHologram)[:-1])
def test_update_vehicle_serializes_every_known_hologram(hologram: VehicleHologram) -> None:
    assert update_vehicle_variables(
        "VIN",
        license_plate="ABC123",
        hologram=hologram,
    ) == {
        "vin": "VIN",
        "licensePlate": "ABC123",
        "hologram": hologram.value,
    }


def test_update_vehicle_preserves_optional_input_states() -> None:
    assert update_vehicle_variables("VIN") == {"vin": "VIN"}
    assert update_vehicle_variables("VIN", license_plate=None, hologram=None) == {
        "vin": "VIN",
        "licensePlate": None,
        "hologram": None,
    }
    with pytest.raises(ValueError, match="UNKNOWN_VALUE cannot be sent"):
        update_vehicle_variables("VIN", hologram=VehicleHologram.UNKNOWN_VALUE)


def test_manual_mileage_preserves_optional_input_states() -> None:
    assert update_vehicle_manual_mileage_variables("VIN") == {"vin": "VIN"}
    assert update_vehicle_manual_mileage_variables("VIN", manual_mileage=None) == {
        "vin": "VIN",
        "manualMileage": None,
    }
    assert update_vehicle_manual_mileage_variables("VIN", manual_mileage=12345) == {
        "vin": "VIN",
        "manualMileage": 12345,
    }


@pytest.mark.parametrize(
    ("typename", "fields", "expected"),
    [
        ("AddVehicleSuccessResponse", {"vin": "VIN"}, AddVehicleSuccess("VIN")),
        ("RegisterGeneralError", {"message": "general"}, RegisterGeneralError("general")),
        (
            "RequireOwnershipVerification",
            {"message": "verify"},
            RequireOwnershipVerification("verify"),
        ),
        (
            "RegisterCorporateVehicleEmailSentToPrimaryOwnerError",
            {"message": "email sent"},
            RegisterCorporateVehicleEmailSentToPrimaryOwnerError("email sent"),
        ),
        (
            "RegisterCorporateVehiclePrimaryOwnerConsentIsPendingError",
            {"message": "pending"},
            RegisterCorporateVehiclePrimaryOwnerConsentIsPendingError("pending"),
        ),
        (
            "VINAlreadyExistsInAnotherGarageError",
            {"message": "duplicate"},
            VINAlreadyExistsInAnotherGarageError("duplicate"),
        ),
    ],
)
def test_parse_add_vehicle_maps_every_service_outcome(
    typename: str,
    fields: dict[str, object],
    expected: object,
) -> None:
    assert parse_add_vehicle(_union_payload("addVehicle", typename, fields)) == expected


@pytest.mark.parametrize(
    ("typename", "fields", "expected"),
    [
        ("AddVehicleSuccessResponse", {"vin": "VIN"}, AddVehicleSuccess("VIN")),
        ("RegisterGeneralError", {"message": "general"}, RegisterGeneralError("general")),
        (
            "RequireOwnershipVerification",
            {"message": "verify"},
            RequireOwnershipVerification("verify"),
        ),
    ],
)
def test_parse_ncar_icar_add_vehicle_maps_every_service_outcome(
    typename: str,
    fields: dict[str, object],
    expected: object,
) -> None:
    assert (
        parse_ncar_icar_add_vehicle(_union_payload("ncarIcarAddVehicle", typename, fields))
        == expected
    )


@pytest.mark.parametrize(
    ("typename", "fields", "expected"),
    [
        ("DeleteVehicleSuccessResponse", {"vin": "VIN"}, DeleteVehicleSuccess("VIN")),
        ("DeleteVehicleError", {"message": "failed"}, DeleteVehicleError("failed")),
    ],
)
def test_parse_delete_vehicle_maps_every_service_outcome(
    typename: str,
    fields: dict[str, object],
    expected: object,
) -> None:
    assert parse_delete_vehicle(_union_payload("deleteVehicle", typename, fields)) == expected


def test_parse_pending_vehicles_preserves_nullable_list_items_and_fields() -> None:
    assert parse_pending_vehicles({"pendingVehicles": None}) is None
    assert parse_pending_vehicles({"pendingVehicles": []}) == ()
    assert parse_pending_vehicles(
        {
            "pendingVehicles": [
                None,
                {
                    "__typename": "PendingVehicle",
                    "vin": "VIN",
                    "caseStatus": "OPEN",
                    "model": None,
                    "caseId": "CASE-ID",
                    "caseNumber": None,
                    "year": "2026",
                },
            ]
        }
    ) == (
        None,
        PendingVehicle("VIN", "OPEN", None, "CASE-ID", None, "2026"),
    )


def test_parse_ownership_status_preserves_nullable_state_and_fragment_absence() -> None:
    assert parse_ownership_status({"vehicle": {"__typename": "Vehicle"}}) is None
    assert parse_ownership_status(
        {
            "vehicle": {
                "__typename": "AVK2Vehicle",
                "ownershipStatus": {
                    "__typename": "OwnershipStatus",
                    "isSignedIn": True,
                },
            }
        }
    ) == OwnershipStatus(True)
    assert parse_ownership_status(
        {
            "vehicle": {
                "__typename": "AVK2Vehicle",
                "ownershipStatus": {
                    "__typename": "OwnershipStatus",
                    "isSignedIn": None,
                },
            }
        }
    ) == OwnershipStatus(None)


@pytest.mark.parametrize(
    ("raw_status", "expected"),
    [
        ("ACTIVATED", AgreementStatus.ACTIVATED),
        ("DEACTIVATED", AgreementStatus.DEACTIVATED),
        ("NO_STATUS", AgreementStatus.NO_STATUS),
        ("FUTURE_STATUS", AgreementStatus.UNKNOWN_VALUE),
        (None, None),
    ],
)
def test_parse_apc_agreement_maps_known_and_future_statuses(
    raw_status: object,
    expected: AgreementStatus | None,
) -> None:
    assert parse_apc_agreement(
        {
            "vehicle": {
                "__typename": "AVK2Vehicle",
                "apcAgreement": {
                    "__typename": "APCAgreement",
                    "optIn": raw_status,
                },
            }
        }
    ) == APCAgreement(expected)


def test_parse_apc_document_url_preserves_null_and_blank_values() -> None:
    assert parse_apc_document_url(
        {
            "vehicle": {
                "__typename": "AVK2Vehicle",
                "apcAgreement": {
                    "__typename": "APCAgreement",
                    "documentURL": "",
                },
            }
        }
    ) == APCDocument("")
    assert parse_apc_document_url(
        {
            "vehicle": {
                "__typename": "AVK2Vehicle",
                "apcAgreement": {
                    "__typename": "APCAgreement",
                    "documentURL": None,
                },
            }
        }
    ) == APCDocument(None)
