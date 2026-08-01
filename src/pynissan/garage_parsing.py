from __future__ import annotations

from collections.abc import Mapping

from .exceptions import ResponseError
from .garage_models import (
    AddVehicleResult,
    AddVehicleSuccess,
    AgreementStatus,
    APCAgreement,
    APCAgreementMutationResult,
    APCDocument,
    ConnectedTermsAndConditionsResult,
    DeleteVehicleError,
    DeleteVehicleResult,
    DeleteVehicleSuccess,
    InvalidVINError,
    NcarIcarAddVehicleResult,
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
    UpdateVehicleManualMileageResult,
    UpdateVehicleManualMileageSuccess,
    UpdateVehicleNicknameMalformedError,
    UpdateVehicleNicknameResult,
    UpdateVehicleNicknameSuccess,
    UpdateVehicleResult,
    UpdateVehicleSuccess,
    UploadOwnershipVerificationResult,
    UploadOwnershipVerificationSuccess,
    ValidVINResponse,
    VehicleHologram,
    VINAlreadyExistsInAnotherGarageError,
    VINNotFoundError,
)

type RegistrationCommonResult = (
    AddVehicleSuccess | RegisterGeneralError | RequireOwnershipVerification
)
type CommonVehicleUpdateError = InvalidVINError | VINNotFoundError | UpdateVehicleGeneralError


def parse_add_vehicle(data: Mapping[str, object]) -> AddVehicleResult | None:
    """Parse every generated AddVehicle union branch."""

    root_field = "addVehicle"
    root = _root(data, root_field)
    if root is None:
        return None
    typename = _typename(root, root_field)

    common_result = _parse_registration_common_result(root, root_field, typename)
    if common_result is not None:
        return common_result
    if typename == "RegisterCorporateVehicleEmailSentToPrimaryOwnerError":
        return RegisterCorporateVehicleEmailSentToPrimaryOwnerError(_message(root, root_field))
    if typename == "RegisterCorporateVehiclePrimaryOwnerConsentIsPendingError":
        return RegisterCorporateVehiclePrimaryOwnerConsentIsPendingError(_message(root, root_field))
    if typename == "VINAlreadyExistsInAnotherGarageError":
        return VINAlreadyExistsInAnotherGarageError(_message(root, root_field))
    return UnselectedGarageResult(typename)


def parse_delete_vehicle(data: Mapping[str, object]) -> DeleteVehicleResult | None:
    """Parse the generated DeleteVehicle union branches."""

    root_field = "deleteVehicle"
    root = _root(data, root_field)
    if root is None:
        return None
    typename = _typename(root, root_field)
    if typename == "DeleteVehicleSuccessResponse":
        return DeleteVehicleSuccess(_string(root.get("vin"), f"{root_field}.vin"))
    if typename == "DeleteVehicleError":
        return DeleteVehicleError(_message(root, root_field))
    return UnselectedGarageResult(typename)


def parse_ncar_icar_add_vehicle(
    data: Mapping[str, object],
) -> NcarIcarAddVehicleResult | None:
    """Parse every generated NCAR/ICAR registration union branch."""

    root_field = "ncarIcarAddVehicle"
    root = _root(data, root_field)
    if root is None:
        return None
    typename = _typename(root, root_field)
    result = _parse_registration_common_result(root, root_field, typename)
    if result is not None:
        return result
    return UnselectedGarageResult(typename)


def parse_pending_vehicles(
    data: Mapping[str, object],
) -> tuple[PendingVehicle | None, ...] | None:
    """Parse nullable pending vehicles and nullable list entries."""

    root_field = "pendingVehicles"
    if root_field not in data:
        raise ResponseError(f"{root_field} is missing")
    values = _nullable_list(data.get(root_field), root_field)
    if values is None:
        return None

    vehicles: list[PendingVehicle | None] = []
    for index, value in enumerate(values):
        if value is None:
            vehicles.append(None)
            continue
        path = f"{root_field}[{index}]"
        vehicle = _typed_object(value, path)
        vehicles.append(
            PendingVehicle(
                vin=_string(vehicle.get("vin"), f"{path}.vin"),
                case_status=_nullable_string(
                    vehicle.get("caseStatus"),
                    f"{path}.caseStatus",
                ),
                model=_nullable_string(vehicle.get("model"), f"{path}.model"),
                case_id=_nullable_string(vehicle.get("caseId"), f"{path}.caseId"),
                case_number=_nullable_string(
                    vehicle.get("caseNumber"),
                    f"{path}.caseNumber",
                ),
                year=_nullable_string(vehicle.get("year"), f"{path}.year"),
            )
        )
    return tuple(vehicles)


def parse_ownership_status(data: Mapping[str, object]) -> OwnershipStatus | None:
    """Parse the nullable AVK2 ownership status without a UI default."""

    vehicle = _vehicle(data)
    if vehicle is None or "ownershipStatus" not in vehicle:
        return None
    path = "vehicle.ownershipStatus"
    status = _optional_typed_object(vehicle.get("ownershipStatus"), path)
    if status is None:
        return None
    return OwnershipStatus(
        is_signed_in=_nullable_bool(status.get("isSignedIn"), f"{path}.isSignedIn")
    )


def parse_apc_agreement(data: Mapping[str, object]) -> APCAgreement | None:
    """Parse the nullable APC agreement state."""

    vehicle = _vehicle(data)
    if vehicle is None or "apcAgreement" not in vehicle:
        return None
    path = "vehicle.apcAgreement"
    agreement = _optional_typed_object(vehicle.get("apcAgreement"), path)
    if agreement is None:
        return None
    return APCAgreement(opt_in=_nullable_agreement_status(agreement.get("optIn"), f"{path}.optIn"))


def parse_apc_document_url(data: Mapping[str, object]) -> APCDocument | None:
    """Parse the raw nullable APC document URL, including an empty string."""

    vehicle = _vehicle(data)
    if vehicle is None or "apcAgreement" not in vehicle:
        return None
    path = "vehicle.apcAgreement"
    agreement = _optional_typed_object(vehicle.get("apcAgreement"), path)
    if agreement is None:
        return None
    return APCDocument(
        document_url=_nullable_string(
            agreement.get("documentURL"),
            f"{path}.documentURL",
        )
    )


def parse_create_apc_agreement(
    data: Mapping[str, object],
) -> APCAgreementMutationResult | None:
    """Parse APC agreement creation without coercing a null success flag."""

    return _parse_apc_agreement_mutation(data, "createAPCAgreement")


def parse_update_apc_agreement(
    data: Mapping[str, object],
) -> APCAgreementMutationResult | None:
    """Parse APC agreement update without coercing a null success flag."""

    return _parse_apc_agreement_mutation(data, "updateAPCAgreement")


def parse_connected_terms_and_conditions_by_vin(
    data: Mapping[str, object],
) -> ConnectedTermsAndConditionsResult | None:
    """Parse every generated connected-terms union branch."""

    root_field = "connectedTermsAndConditionsByVIN"
    root = _root(data, root_field)
    if root is None:
        return None
    typename = _typename(root, root_field)
    if typename == "TermsAndConditionsResponse":
        return TermsAndConditionsResponse(
            title=_nullable_string(root.get("title"), f"{root_field}.title"),
            body=_nullable_string(root.get("body"), f"{root_field}.body"),
            url=_nullable_string(root.get("url"), f"{root_field}.url"),
        )
    if typename == "InvalidVINError":
        return InvalidVINError(_message(root, root_field))
    if typename == "NonConnectedVehicleResponse":
        return NonConnectedVehicleResponse(_message(root, root_field))
    if typename == "ValidVINResponse":
        return ValidVINResponse(_message(root, root_field))
    return UnselectedGarageResult(typename)


def parse_onboarding_features(
    data: Mapping[str, object],
) -> tuple[OnboardingFeature | None, ...] | None:
    """Parse nullable onboarding features and nullable list entries."""

    vehicle = _vehicle(data)
    if vehicle is None or "onboardingFeatures" not in vehicle:
        return None
    path = "vehicle.onboardingFeatures"
    values = _nullable_list(vehicle.get("onboardingFeatures"), path)
    if values is None:
        return None

    features: list[OnboardingFeature | None] = []
    for index, value in enumerate(values):
        if value is None:
            features.append(None)
            continue
        feature_path = f"{path}[{index}]"
        feature = _typed_object(value, feature_path)
        features.append(
            OnboardingFeature(
                position=_nullable_int(
                    feature.get("position"),
                    f"{feature_path}.position",
                ),
                title=_nullable_string(
                    feature.get("title"),
                    f"{feature_path}.title",
                ),
                body=_nullable_string(feature.get("body"), f"{feature_path}.body"),
                image_type=_nullable_onboarding_feature_image_type(
                    feature.get("imageType"),
                    f"{feature_path}.imageType",
                ),
            )
        )
    return tuple(features)


def parse_update_vehicle(data: Mapping[str, object]) -> UpdateVehicleResult | None:
    """Parse every generated license-plate and hologram update branch."""

    root_field = "updateVehicle"
    root = _root(data, root_field)
    if root is None:
        return None
    typename = _typename(root, root_field)
    if typename == "UpdateVehicleSuccessResponse":
        return UpdateVehicleSuccess(
            license_plate=_nullable_string(
                root.get("licensePlate"),
                f"{root_field}.licensePlate",
            ),
            hologram=_nullable_vehicle_hologram(
                root.get("hologram"),
                f"{root_field}.hologram",
            ),
        )
    if typename == "UpdateVehicleInvalidLicensePlateError":
        return UpdateVehicleInvalidLicensePlateError(_message(root, root_field))
    if typename == "UpdateVehicleHologramInvalidLengthError":
        return UpdateVehicleHologramInvalidLengthError(_message(root, root_field))
    common_error = _parse_common_vehicle_update_error(root, root_field, typename)
    if common_error is not None:
        return common_error
    return UnselectedGarageResult(typename)


def parse_update_vehicle_manual_mileage(
    data: Mapping[str, object],
) -> UpdateVehicleManualMileageResult | None:
    """Parse every generated manual-mileage update branch."""

    root_field = "updateVehicle"
    root = _root(data, root_field)
    if root is None:
        return None
    typename = _typename(root, root_field)
    if typename == "UpdateVehicleSuccessResponse":
        return UpdateVehicleManualMileageSuccess(
            manual_mileage=_nullable_string(
                root.get("manualMileage"),
                f"{root_field}.manualMileage",
            )
        )
    if typename == "UpdateVehicleInvalidMileageError":
        return UpdateVehicleInvalidMileageError(_message(root, root_field))
    common_error = _parse_common_vehicle_update_error(root, root_field, typename)
    if common_error is not None:
        return common_error
    return UnselectedGarageResult(typename)


def parse_update_vehicle_nickname(
    data: Mapping[str, object],
) -> UpdateVehicleNicknameResult | None:
    """Parse every generated nickname update branch."""

    root_field = "updateVehicle"
    root = _root(data, root_field)
    if root is None:
        return None
    typename = _typename(root, root_field)
    if typename == "UpdateVehicleSuccessResponse":
        return UpdateVehicleNicknameSuccess(
            nickname=_string(root.get("nickname"), f"{root_field}.nickname")
        )
    if typename == "UpdateVehicleNicknameMalformedError":
        return UpdateVehicleNicknameMalformedError(_message(root, root_field))
    common_error = _parse_common_vehicle_update_error(root, root_field, typename)
    if common_error is not None:
        return common_error
    return UnselectedGarageResult(typename)


def parse_upload_ownership_verification(
    data: Mapping[str, object],
) -> UploadOwnershipVerificationResult | None:
    """Parse every generated ownership-verification upload branch."""

    root_field = "uploadOwnershipVerification"
    root = _root(data, root_field)
    if root is None:
        return None
    typename = _typename(root, root_field)
    if typename == "UploadOwnershipVerificationSuccess":
        return UploadOwnershipVerificationSuccess(
            case_number=_string(
                root.get("caseNumber"),
                f"{root_field}.caseNumber",
            )
        )
    if typename == "RegisterGeneralError":
        return RegisterGeneralError(_message(root, root_field))
    return UnselectedGarageResult(typename)


def _parse_registration_common_result(
    root: Mapping[str, object],
    root_field: str,
    typename: str,
) -> RegistrationCommonResult | None:
    if typename == "AddVehicleSuccessResponse":
        return AddVehicleSuccess(_string(root.get("vin"), f"{root_field}.vin"))
    if typename == "RegisterGeneralError":
        return RegisterGeneralError(_message(root, root_field))
    if typename == "RequireOwnershipVerification":
        return RequireOwnershipVerification(_message(root, root_field))
    return None


def _parse_common_vehicle_update_error(
    root: Mapping[str, object],
    root_field: str,
    typename: str,
) -> CommonVehicleUpdateError | None:
    if typename == "InvalidVINError":
        return InvalidVINError(_message(root, root_field))
    if typename == "VINNotFoundError":
        return VINNotFoundError(_message(root, root_field))
    if typename == "UpdateVehicleGeneralError":
        return UpdateVehicleGeneralError(_message(root, root_field))
    return None


def _parse_apc_agreement_mutation(
    data: Mapping[str, object],
    root_field: str,
) -> APCAgreementMutationResult | None:
    root = _root(data, root_field)
    if root is None:
        return None
    return APCAgreementMutationResult(
        success=_nullable_bool(root.get("success"), f"{root_field}.success")
    )


def _vehicle(data: Mapping[str, object]) -> Mapping[str, object] | None:
    return _root(data, "vehicle")


def _root(
    data: Mapping[str, object],
    root_field: str,
) -> Mapping[str, object] | None:
    if root_field not in data:
        raise ResponseError(f"{root_field} is missing")
    return _optional_typed_object(data.get(root_field), root_field)


def _typed_object(value: object, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ResponseError(f"{path} is not an object")
    _typename(value, path)
    return value


def _optional_typed_object(
    value: object,
    path: str,
) -> Mapping[str, object] | None:
    if value is None:
        return None
    return _typed_object(value, path)


def _typename(value: Mapping[str, object], path: str) -> str:
    return _string(value.get("__typename"), f"{path}.__typename")


def _message(value: Mapping[str, object], path: str) -> str:
    return _string(value.get("message"), f"{path}.message")


def _nullable_list(value: object, path: str) -> list[object] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        raise ResponseError(f"{path} is not a list")
    return value


def _string(value: object, path: str) -> str:
    if not isinstance(value, str):
        raise ResponseError(f"{path} is not a string")
    return value


def _nullable_string(value: object, path: str) -> str | None:
    if value is None:
        return None
    return _string(value, path)


def _nullable_bool(value: object, path: str) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ResponseError(f"{path} is not a boolean")
    return value


def _nullable_int(value: object, path: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise ResponseError(f"{path} is not an integer")
    return value


def _nullable_agreement_status(value: object, path: str) -> AgreementStatus | None:
    raw_value = _nullable_string(value, path)
    if raw_value is None:
        return None
    try:
        return AgreementStatus(raw_value)
    except ValueError:
        return AgreementStatus.UNKNOWN_VALUE


def _nullable_vehicle_hologram(value: object, path: str) -> VehicleHologram | None:
    raw_value = _nullable_string(value, path)
    if raw_value is None:
        return None
    try:
        return VehicleHologram(raw_value)
    except ValueError:
        return VehicleHologram.UNKNOWN_VALUE


def _nullable_onboarding_feature_image_type(
    value: object,
    path: str,
) -> OnboardingFeatureImageType | None:
    raw_value = _nullable_string(value, path)
    if raw_value is None:
        return None
    try:
        return OnboardingFeatureImageType(raw_value)
    except ValueError:
        return OnboardingFeatureImageType.UNKNOWN_VALUE
