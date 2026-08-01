from __future__ import annotations

import hashlib
import re
from collections.abc import Callable, Mapping
from dataclasses import FrozenInstanceError

import pytest

from pynissan import operations
from pynissan.exceptions import ResponseError
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
    APCAgreementMutationResult,
    APCDocument,
    DeleteVehicleError,
    DeleteVehicleSuccess,
    InvalidVINError,
    NonConnectedVehicleResponse,
    OnboardingFeature,
    OnboardingFeatureImageType,
    OwnershipStatus,
    PendingVehicle,
    RegisterCorporateVehicleEmailSentToPrimaryOwnerError,
    RegisterCorporateVehiclePrimaryOwnerConsentIsPendingError,
    RegisterGeneralError,
    RequireOwnershipVerification,
    TermsAndConditionsResponse,
    UnselectedGarageResult,
    UpdateVehicleGeneralError,
    UpdateVehicleHologramInvalidLengthError,
    UpdateVehicleInvalidLicensePlateError,
    UpdateVehicleInvalidMileageError,
    UpdateVehicleManualMileageSuccess,
    UpdateVehicleNicknameMalformedError,
    UpdateVehicleNicknameSuccess,
    UpdateVehicleSuccess,
    UploadOwnershipVerificationSuccess,
    ValidVINResponse,
    VehicleHologram,
    VINAlreadyExistsInAnotherGarageError,
    VINNotFoundError,
)
from pynissan.garage_parsing import (
    parse_add_vehicle,
    parse_apc_agreement,
    parse_apc_document_url,
    parse_connected_terms_and_conditions_by_vin,
    parse_create_apc_agreement,
    parse_delete_vehicle,
    parse_ncar_icar_add_vehicle,
    parse_onboarding_features,
    parse_ownership_status,
    parse_pending_vehicles,
    parse_update_apc_agreement,
    parse_update_vehicle,
    parse_update_vehicle_manual_mileage,
    parse_update_vehicle_nickname,
    parse_upload_ownership_verification,
)

Parser = Callable[[Mapping[str, object]], object | None]

EXPECTED_OPERATIONS = {
    "AddVehicle": (
        operations.ADD_VEHICLE,
        operations.ADD_VEHICLE_OPERATION_ID,
        "0b5b92ab96ca9516d63423c56fa08bc01bcdcf15fb644e2907a3aae7253262c0",
    ),
    "DeleteVehicle": (
        operations.DELETE_VEHICLE,
        operations.DELETE_VEHICLE_OPERATION_ID,
        "d7b9f78e719fd1d5809ad60ddf083c1bebb87b5825fc7f6f7a75fee25b7b066e",
    ),
    "NcarIcarAddVehicle": (
        operations.NCAR_ICAR_ADD_VEHICLE,
        operations.NCAR_ICAR_ADD_VEHICLE_OPERATION_ID,
        "2f1580533da2b2669ebd416ef4f63d3e66dba01761849c352d03ed8b9bb6ba8a",
    ),
    "PendingVehicles": (
        operations.PENDING_VEHICLES,
        operations.PENDING_VEHICLES_OPERATION_ID,
        "e41202c3f1905f5ee4e93b9760b88c9e0e574d60ff553af4fb4bd918e2e58f25",
    ),
    "OwnershipStatus": (
        operations.OWNERSHIP_STATUS,
        operations.OWNERSHIP_STATUS_OPERATION_ID,
        "6cff2455b8b5d0d9b9589de1dcc16adaf591b4c38137ffb4dbb88669c2f6ab65",
    ),
    "APCAgreement": (
        operations.APC_AGREEMENT,
        operations.APC_AGREEMENT_OPERATION_ID,
        "e18952fd53569fd51e8891599c90b06157805dcafe21853939fb814a7c628a61",
    ),
    "APCDocumentURL": (
        operations.APC_DOCUMENT_URL,
        operations.APC_DOCUMENT_URL_OPERATION_ID,
        "250c59bfc322084506f261759f5ab9bc53244f76f5bcae8e5adf7c09e245ca5c",
    ),
    "CreateAPCAgreement": (
        operations.CREATE_APC_AGREEMENT,
        operations.CREATE_APC_AGREEMENT_OPERATION_ID,
        "8e54166633dcbcddb8671492d93c7ec82a97a95d78d122ccd8e5512c87076d0e",
    ),
    "UpdateAPCAgreement": (
        operations.UPDATE_APC_AGREEMENT,
        operations.UPDATE_APC_AGREEMENT_OPERATION_ID,
        "abb4343cde0806b62e956b6184f7cba008987d8b9305975c3ec60243e59237e3",
    ),
    "ConnectedTermsAndConditionsByVIN": (
        operations.CONNECTED_TERMS_AND_CONDITIONS_BY_VIN,
        operations.CONNECTED_TERMS_AND_CONDITIONS_BY_VIN_OPERATION_ID,
        "085f39d8b511343fc60438624974a97c89c7d24d94ed1468b98e1824e96a0c06",
    ),
    "OnboardingFeatures": (
        operations.ONBOARDING_FEATURES,
        operations.ONBOARDING_FEATURES_OPERATION_ID,
        "70dff9f83252dce0973a7b2461f3581b3a80944e850bcdd63e81447fbd9e702b",
    ),
    "UpdateVehicle": (
        operations.UPDATE_VEHICLE,
        operations.UPDATE_VEHICLE_OPERATION_ID,
        "1bb299061736d5b8e14d1814bb5c967af7748c41de29443b84a73719ac272ce8",
    ),
    "UpdateVehicleManualMileage": (
        operations.UPDATE_VEHICLE_MANUAL_MILEAGE,
        operations.UPDATE_VEHICLE_MANUAL_MILEAGE_OPERATION_ID,
        "177a7dbf7956abdd7d1382d8aec8c73ddaf043d21ea9de05d481a846cb2058fe",
    ),
    "UpdateVehicleNickname": (
        operations.UPDATE_VEHICLE_NICKNAME,
        operations.UPDATE_VEHICLE_NICKNAME_OPERATION_ID,
        "62444ee58449f5f4ccc5a6881e9069b89e7e717293ffa8de2f66b8981562bb81",
    ),
    "UploadOwnershipVerification": (
        operations.UPLOAD_OWNERSHIP_VERIFICATION,
        operations.UPLOAD_OWNERSHIP_VERIFICATION_OPERATION_ID,
        "9b24a6900530b63e6117409728b3114e8b0c8875ec21d023a7200f6b739d91ba",
    ),
}


def _union_payload(
    root_field: str,
    typename: str,
    fields: Mapping[str, object],
) -> dict[str, object]:
    return {root_field: {"__typename": typename, **fields}}


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


@pytest.mark.parametrize(
    ("parser", "root_field"),
    [
        (parse_create_apc_agreement, "createAPCAgreement"),
        (parse_update_apc_agreement, "updateAPCAgreement"),
    ],
)
@pytest.mark.parametrize("success", [True, False, None])
def test_parse_apc_mutations_preserve_service_success_semantics(
    parser: Parser,
    root_field: str,
    success: bool | None,
) -> None:
    assert parser(
        {
            root_field: {
                "__typename": "ResponseStatus",
                "success": success,
            }
        }
    ) == APCAgreementMutationResult(success)


@pytest.mark.parametrize(
    ("typename", "fields", "expected"),
    [
        (
            "TermsAndConditionsResponse",
            {"title": None, "body": "Terms", "url": None},
            TermsAndConditionsResponse(None, "Terms", None),
        ),
        ("InvalidVINError", {"message": "invalid"}, InvalidVINError("invalid")),
        (
            "NonConnectedVehicleResponse",
            {"message": "not connected"},
            NonConnectedVehicleResponse("not connected"),
        ),
        ("ValidVINResponse", {"message": "valid"}, ValidVINResponse("valid")),
    ],
)
def test_parse_connected_terms_maps_every_service_outcome(
    typename: str,
    fields: dict[str, object],
    expected: object,
) -> None:
    assert (
        parse_connected_terms_and_conditions_by_vin(
            _union_payload("connectedTermsAndConditionsByVIN", typename, fields)
        )
        == expected
    )


@pytest.mark.parametrize(
    ("raw_image_type", "expected"),
    [
        ("INFO", OnboardingFeatureImageType.INFO),
        ("TELEMATICS", OnboardingFeatureImageType.TELEMATICS),
        ("NECN", OnboardingFeatureImageType.NECN),
        ("V1G", OnboardingFeatureImageType.V1G),
        ("FUTURE_IMAGE", OnboardingFeatureImageType.UNKNOWN_VALUE),
        (None, None),
    ],
)
def test_parse_onboarding_features_preserves_lists_and_future_enums(
    raw_image_type: object,
    expected: OnboardingFeatureImageType | None,
) -> None:
    assert parse_onboarding_features(
        {
            "vehicle": {
                "__typename": "AVK2Vehicle",
                "onboardingFeatures": [
                    None,
                    {
                        "__typename": "OnboardingFeature",
                        "position": 2,
                        "title": None,
                        "body": "Body",
                        "imageType": raw_image_type,
                    },
                ],
            }
        }
    ) == (None, OnboardingFeature(2, None, "Body", expected))


def test_onboarding_features_distinguishes_null_and_empty_lists() -> None:
    assert (
        parse_onboarding_features(
            {
                "vehicle": {
                    "__typename": "AVK2Vehicle",
                    "onboardingFeatures": None,
                }
            }
        )
        is None
    )
    assert (
        parse_onboarding_features(
            {
                "vehicle": {
                    "__typename": "AVK2Vehicle",
                    "onboardingFeatures": [],
                }
            }
        )
        == ()
    )


@pytest.mark.parametrize(
    ("raw_hologram", "expected"),
    [
        ("SINGLE_ZERO", VehicleHologram.SINGLE_ZERO),
        ("DOUBLE_ZERO", VehicleHologram.DOUBLE_ZERO),
        ("ONE", VehicleHologram.ONE),
        ("TWO", VehicleHologram.TWO),
        ("E", VehicleHologram.E),
        ("FUTURE_HOLOGRAM", VehicleHologram.UNKNOWN_VALUE),
        (None, None),
    ],
)
def test_parse_update_vehicle_success_preserves_nullable_fields_and_future_enum(
    raw_hologram: object,
    expected: VehicleHologram | None,
) -> None:
    assert parse_update_vehicle(
        _union_payload(
            "updateVehicle",
            "UpdateVehicleSuccessResponse",
            {"licensePlate": None, "hologram": raw_hologram},
        )
    ) == UpdateVehicleSuccess(None, expected)


@pytest.mark.parametrize(
    ("typename", "expected"),
    [
        (
            "UpdateVehicleInvalidLicensePlateError",
            UpdateVehicleInvalidLicensePlateError("error"),
        ),
        (
            "UpdateVehicleHologramInvalidLengthError",
            UpdateVehicleHologramInvalidLengthError("error"),
        ),
        ("InvalidVINError", InvalidVINError("error")),
        ("VINNotFoundError", VINNotFoundError("error")),
        ("UpdateVehicleGeneralError", UpdateVehicleGeneralError("error")),
    ],
)
def test_parse_update_vehicle_maps_every_error_outcome(
    typename: str,
    expected: object,
) -> None:
    assert (
        parse_update_vehicle(_union_payload("updateVehicle", typename, {"message": "error"}))
        == expected
    )


def test_parse_manual_mileage_success_preserves_string_scalar_and_null() -> None:
    assert parse_update_vehicle_manual_mileage(
        _union_payload(
            "updateVehicle",
            "UpdateVehicleSuccessResponse",
            {"manualMileage": "12345"},
        )
    ) == UpdateVehicleManualMileageSuccess("12345")
    assert parse_update_vehicle_manual_mileage(
        _union_payload(
            "updateVehicle",
            "UpdateVehicleSuccessResponse",
            {"manualMileage": None},
        )
    ) == UpdateVehicleManualMileageSuccess(None)


@pytest.mark.parametrize(
    ("typename", "expected"),
    [
        (
            "UpdateVehicleInvalidMileageError",
            UpdateVehicleInvalidMileageError("error"),
        ),
        ("InvalidVINError", InvalidVINError("error")),
        ("VINNotFoundError", VINNotFoundError("error")),
        ("UpdateVehicleGeneralError", UpdateVehicleGeneralError("error")),
    ],
)
def test_parse_manual_mileage_maps_every_error_outcome(
    typename: str,
    expected: object,
) -> None:
    assert (
        parse_update_vehicle_manual_mileage(
            _union_payload("updateVehicle", typename, {"message": "error"})
        )
        == expected
    )


def test_parse_nickname_success_matches_service_success_outcome() -> None:
    assert parse_update_vehicle_nickname(
        _union_payload(
            "updateVehicle",
            "UpdateVehicleSuccessResponse",
            {"nickname": "Ariya"},
        )
    ) == UpdateVehicleNicknameSuccess("Ariya")


@pytest.mark.parametrize(
    ("typename", "expected"),
    [
        (
            "UpdateVehicleNicknameMalformedError",
            UpdateVehicleNicknameMalformedError("error"),
        ),
        ("InvalidVINError", InvalidVINError("error")),
        ("VINNotFoundError", VINNotFoundError("error")),
        ("UpdateVehicleGeneralError", UpdateVehicleGeneralError("error")),
    ],
)
def test_parse_nickname_maps_every_error_outcome(
    typename: str,
    expected: object,
) -> None:
    assert (
        parse_update_vehicle_nickname(
            _union_payload("updateVehicle", typename, {"message": "error"})
        )
        == expected
    )


@pytest.mark.parametrize(
    ("typename", "fields", "expected"),
    [
        (
            "UploadOwnershipVerificationSuccess",
            {"caseNumber": "CASE-1"},
            UploadOwnershipVerificationSuccess("CASE-1"),
        ),
        ("RegisterGeneralError", {"message": "failed"}, RegisterGeneralError("failed")),
    ],
)
def test_parse_ownership_verification_maps_every_service_outcome(
    typename: str,
    fields: dict[str, object],
    expected: object,
) -> None:
    assert (
        parse_upload_ownership_verification(
            _union_payload("uploadOwnershipVerification", typename, fields)
        )
        == expected
    )


@pytest.mark.parametrize(
    ("parser", "root_field"),
    [
        (parse_add_vehicle, "addVehicle"),
        (parse_delete_vehicle, "deleteVehicle"),
        (parse_ncar_icar_add_vehicle, "ncarIcarAddVehicle"),
        (parse_pending_vehicles, "pendingVehicles"),
        (parse_ownership_status, "vehicle"),
        (parse_apc_agreement, "vehicle"),
        (parse_apc_document_url, "vehicle"),
        (parse_create_apc_agreement, "createAPCAgreement"),
        (parse_update_apc_agreement, "updateAPCAgreement"),
        (parse_connected_terms_and_conditions_by_vin, "connectedTermsAndConditionsByVIN"),
        (parse_onboarding_features, "vehicle"),
        (parse_update_vehicle, "updateVehicle"),
        (parse_update_vehicle_manual_mileage, "updateVehicle"),
        (parse_update_vehicle_nickname, "updateVehicle"),
        (parse_upload_ownership_verification, "uploadOwnershipVerification"),
    ],
)
def test_garage_parsers_preserve_nullable_roots_and_reject_missing_roots(
    parser: Parser,
    root_field: str,
) -> None:
    assert parser({root_field: None}) is None
    with pytest.raises(ResponseError, match=rf"^{root_field} is missing$"):
        parser({})


@pytest.mark.parametrize(
    ("parser", "root_field", "typename"),
    [
        (parse_add_vehicle, "addVehicle", "VINAlreadyExistsInYourGarageError"),
        (parse_delete_vehicle, "deleteVehicle", "FutureResult"),
        (parse_ncar_icar_add_vehicle, "ncarIcarAddVehicle", "InvalidVINError"),
        (
            parse_connected_terms_and_conditions_by_vin,
            "connectedTermsAndConditionsByVIN",
            "FutureResult",
        ),
        (parse_update_vehicle, "updateVehicle", "RequiresAtLeastOneArgumentError"),
        (
            parse_update_vehicle_manual_mileage,
            "updateVehicle",
            "UpdateVehicleInvalidNicknameError",
        ),
        (
            parse_update_vehicle_nickname,
            "updateVehicle",
            "UpdateVehicleNicknameExcessCharactersError",
        ),
        (
            parse_upload_ownership_verification,
            "uploadOwnershipVerification",
            "FutureResult",
        ),
    ],
)
def test_union_parsers_preserve_unselected_typenames(
    parser: Parser,
    root_field: str,
    typename: str,
) -> None:
    assert parser(_union_payload(root_field, typename, {})) == UnselectedGarageResult(typename)


@pytest.mark.parametrize(
    ("parser", "payload", "message"),
    [
        (parse_add_vehicle, {"addVehicle": {}}, "addVehicle.__typename is not a string"),
        (
            parse_delete_vehicle,
            _union_payload("deleteVehicle", "DeleteVehicleError", {"message": 500}),
            "deleteVehicle.message is not a string",
        ),
        (
            parse_ncar_icar_add_vehicle,
            _union_payload("ncarIcarAddVehicle", "AddVehicleSuccessResponse", {"vin": None}),
            "ncarIcarAddVehicle.vin is not a string",
        ),
        (
            parse_pending_vehicles,
            {"pendingVehicles": "not-a-list"},
            "pendingVehicles is not a list",
        ),
        (
            parse_pending_vehicles,
            {"pendingVehicles": [{"__typename": "PendingVehicle", "vin": 7}]},
            "pendingVehicles[0].vin is not a string",
        ),
        (
            parse_ownership_status,
            {
                "vehicle": {
                    "__typename": "AVK2Vehicle",
                    "ownershipStatus": {
                        "__typename": "OwnershipStatus",
                        "isSignedIn": "yes",
                    },
                }
            },
            "vehicle.ownershipStatus.isSignedIn is not a boolean",
        ),
        (
            parse_apc_agreement,
            {
                "vehicle": {
                    "__typename": "AVK2Vehicle",
                    "apcAgreement": {"__typename": "APCAgreement", "optIn": True},
                }
            },
            "vehicle.apcAgreement.optIn is not a string",
        ),
        (
            parse_apc_document_url,
            {
                "vehicle": {
                    "__typename": "AVK2Vehicle",
                    "apcAgreement": {
                        "__typename": "APCAgreement",
                        "documentURL": 3,
                    },
                }
            },
            "vehicle.apcAgreement.documentURL is not a string",
        ),
        (
            parse_create_apc_agreement,
            {"createAPCAgreement": {"__typename": "ResponseStatus", "success": "yes"}},
            "createAPCAgreement.success is not a boolean",
        ),
        (
            parse_update_apc_agreement,
            {"updateAPCAgreement": {"__typename": "ResponseStatus", "success": 1}},
            "updateAPCAgreement.success is not a boolean",
        ),
        (
            parse_connected_terms_and_conditions_by_vin,
            _union_payload(
                "connectedTermsAndConditionsByVIN",
                "TermsAndConditionsResponse",
                {"title": 1},
            ),
            "connectedTermsAndConditionsByVIN.title is not a string",
        ),
        (
            parse_onboarding_features,
            {
                "vehicle": {
                    "__typename": "AVK2Vehicle",
                    "onboardingFeatures": [{"__typename": "OnboardingFeature", "position": True}],
                }
            },
            "vehicle.onboardingFeatures[0].position is not an integer",
        ),
        (
            parse_update_vehicle,
            _union_payload(
                "updateVehicle",
                "UpdateVehicleSuccessResponse",
                {"licensePlate": 1},
            ),
            "updateVehicle.licensePlate is not a string",
        ),
        (
            parse_update_vehicle_manual_mileage,
            _union_payload(
                "updateVehicle",
                "UpdateVehicleSuccessResponse",
                {"manualMileage": 12345},
            ),
            "updateVehicle.manualMileage is not a string",
        ),
        (
            parse_update_vehicle_nickname,
            _union_payload(
                "updateVehicle",
                "UpdateVehicleSuccessResponse",
                {"nickname": None},
            ),
            "updateVehicle.nickname is not a string",
        ),
        (
            parse_upload_ownership_verification,
            _union_payload(
                "uploadOwnershipVerification",
                "UploadOwnershipVerificationSuccess",
                {"caseNumber": 1},
            ),
            "uploadOwnershipVerification.caseNumber is not a string",
        ),
    ],
)
def test_garage_parsers_reject_malformed_responses(
    parser: Parser,
    payload: Mapping[str, object],
    message: str,
) -> None:
    with pytest.raises(ResponseError, match=re.escape(message)):
        parser(payload)


def test_garage_models_are_frozen() -> None:
    vehicle = PendingVehicle("VIN", None, None, None, None, None)

    with pytest.raises(FrozenInstanceError):
        vehicle.vin = "OTHER"  # type: ignore[misc]
