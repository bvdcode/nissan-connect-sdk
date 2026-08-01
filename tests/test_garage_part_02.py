from __future__ import annotations

import pytest
from test_garage import (
    Parser,
    _union_payload,
)

from pynissan.exceptions import ResponseError
from pynissan.garage_models import (
    APCAgreementMutationResult,
    InvalidVINError,
    NonConnectedVehicleResponse,
    OnboardingFeature,
    OnboardingFeatureImageType,
    RegisterGeneralError,
    TermsAndConditionsResponse,
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
