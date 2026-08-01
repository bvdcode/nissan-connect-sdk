from __future__ import annotations

from collections.abc import Callable, Mapping

from pynissan import operations

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
