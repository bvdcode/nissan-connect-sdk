from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import FrozenInstanceError

import pytest
from test_garage import (
    Parser,
    _union_payload,
)

from pynissan.exceptions import ResponseError
from pynissan.garage_models import (
    PendingVehicle,
    UnselectedGarageResult,
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
