from __future__ import annotations

import hashlib
from collections.abc import Awaitable, Mapping
from datetime import UTC, datetime
from typing import cast

import pytest
from aiohttp import ClientSession

from pynissan import (
    CollisionCenter,
    CollisionCenterAddress,
    CollisionCenterAddressInput,
    CollisionCenterDistance,
    CollisionCenterPhone,
    CollisionCenterProperties,
    CollisionCenterSearchInput,
    CollisionReportCreated,
    CollisionReportMetadataInput,
    CollisionReportPhotoDeleteError,
    CollisionReportPhotoInput,
    CollisionReportUserInput,
    CollisionReportVehicleInput,
    CoordinateInput,
    CreateCollisionReportInput,
    DistanceUnit,
    InsuranceContact,
    InsuranceStatus,
    NissanClient,
    PhotoSection,
    ReadOnlyError,
    Tokens,
    UnselectedCollisionReportResult,
    VehicleInsurance,
    VehicleInsuranceInput,
    VehicleInsuranceMutationSuccess,
    VehicleInsurer,
    operations,
)
from pynissan.collision_report_inputs import (
    collision_center_variables,
    collision_report_photo_variables,
    create_collision_report_variables,
    delete_collision_report_photo_variables,
)
from pynissan.collision_report_parsing import (
    parse_collision_centers,
    parse_create_collision_report,
    parse_delete_collision_report_photo,
)
from pynissan.insurance_inputs import vehicle_insurance_variables
from pynissan.insurance_parsing import (
    parse_add_vehicle_insurance,
    parse_insurers,
    parse_vehicle_insurance,
)

EXPECTED_OPERATIONS = {
    "ADD_VEHICLE_INSURANCE": ("c8a675f1bbfc0b0dd24aa9df7b1f7226baf678b0ef4bd9b41dae463104220ed8"),
    "GET_VEHICLE_INSURANCE": ("98d754f8f84559168c53b6c10eed74518518f7fcbcbcc724c19a9540059ae045"),
    "INSURERS": "2da75bceb5084402739f948c14cc97a94ef50b9ed3541de666efc7f34f83f83f",
    "UPDATE_VEHICLE_INSURANCE": (
        "22e782bf419449844d927d69e0ebd38f7dfe52215ed063e0cb235146d08341a9"
    ),
    "COLLISION_CENTERS": ("b25799de489658f0d5a885c3d2ba31797db31166c9b37082f06e1daa39b9b27c"),
    "CREATE_COLLISION_REPORT": ("3f4166b52642a9c8045bb9de06031ebe984e25c3f66f0bd38ebdf552f1ea6bfa"),
    "CREATE_COLLISION_REPORT_PDF": (
        "19ca3ecdbedb59fb22a511c38b2515e6a2f3d342fd2a05905a72d74dfa75aee8"
    ),
    "DELETE_PHOTO_FOR_COLLISION_REPORT": (
        "c00cb1ae4ed0e9c46ddb6a9513265c5dc8c2f982ee4a74f7d97ac9e309fa107c"
    ),
    "UPLOAD_PHOTO_FOR_COLLISION_REPORT": (
        "3a98f3817495f4fc58c78d4a3127f53582c255f1aeb17b92998ffceb9537057e"
    ),
}


class FakeResponse:
    def __init__(self, data: Mapping[str, object]) -> None:
        self.status = 200
        self._payload = {"data": data}

    async def __aenter__(self) -> FakeResponse:
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def json(self, *, content_type: object = None) -> object:
        return self._payload


class FakeSession:
    def __init__(self, *responses: FakeResponse) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, object]] = []

    def post(self, url: str, **kwargs: object) -> FakeResponse:
        self.calls.append({"url": url, **kwargs})
        if not self.responses:
            raise AssertionError("Unexpected HTTP request")
        return self.responses.pop(0)


def make_client(session: FakeSession, *, read_only: bool) -> NissanClient:
    return NissanClient(
        cast(ClientSession, session),
        tokens=Tokens("access-token", "refresh-token", "id-token"),
        read_only=read_only,
    )


def insurance_input() -> VehicleInsuranceInput:
    return VehicleInsuranceInput(
        "VIN",
        "insurer-id",
        "policy-number",
        "2027-08-01",
        custom_insurance_name=None,
    )


def collision_report_input() -> CreateCollisionReportInput:
    return CreateCollisionReportInput(
        vin="VIN",
        vehicle=CollisionReportVehicleInput(
            "Nissan",
            "Ariya",
            "2025",
            license_plate=None,
        ),
        user=CollisionReportUserInput(first_name="Owner", email=None),
        insurance_company_name="Example Insurance",
        collision_metadata=CollisionReportMetadataInput(
            report_date_time=datetime(2026, 7, 31, 16, 0, tzinfo=UTC),
            odometer=1234.5,
            unit=DistanceUnit.MILE,
        ),
    )


def test_insurance_and_collision_operations_match_service_documents() -> None:
    for constant, expected_id in EXPECTED_OPERATIONS.items():
        document = getattr(operations, constant)
        operation_id = getattr(operations, f"{constant}_OPERATION_ID")
        assert operation_id == expected_id
        assert hashlib.sha256(document.encode()).hexdigest() == expected_id


def test_insurance_and_collision_inputs_preserve_omitted_and_null_fields() -> None:
    assert vehicle_insurance_variables(insurance_input()) == {
        "input": {
            "vin": "VIN",
            "insurerId": "insurer-id",
            "policyNumber": "policy-number",
            "expiryDate": "2027-08-01",
            "customInsuranceName": None,
        }
    }
    search = CollisionCenterSearchInput(
        "VIN",
        coordinates=CoordinateInput(35.9, -86.9),
        address=CollisionCenterAddressInput(country="US", postal_code=None),
    )
    assert collision_center_variables(search) == {
        "input": {
            "vin": "VIN",
            "coordinates": {"latitude": 35.9, "longitude": -86.9},
            "address": {"country": "US", "postalCode": None},
        }
    }
    assert create_collision_report_variables(collision_report_input()) == {
        "input": {
            "vin": "VIN",
            "user": {"firstName": "Owner", "email": None},
            "insuranceCompanyName": "Example Insurance",
            "vehicle": {
                "make": "Nissan",
                "model": "Ariya",
                "modelYear": "2025",
                "licensePlate": None,
            },
            "collisionMetadata": {
                "reportDateTime": "2026-07-31T16:00:00+00:00",
                "odometer": 1234.5,
                "unit": "MILE",
            },
        }
    }
    photo = CollisionReportPhotoInput("base64-image", filename=None)
    assert collision_report_photo_variables("VIN", "claim", photo, PhotoSection.THREE) == {
        "input": {
            "vin": "VIN",
            "collisionId": "claim",
            "photo": {"filename": None, "attachment": "base64-image"},
            "photoSection": "THREE",
        }
    }
    with pytest.raises(ValueError, match="UNKNOWN_VALUE cannot be sent"):
        delete_collision_report_photo_variables(
            "VIN",
            "claim",
            PhotoSection.UNKNOWN_VALUE,
        )


def test_parse_insurance_catalog_policy_and_mutation() -> None:
    contact = InsuranceContact("Claims", "+15555550100")
    insurer = VehicleInsurer("insurer-id", "Example Insurance", (contact, None))
    insurer_data = {
        "__typename": "Insurer",
        "id": "insurer-id",
        "name": "Example Insurance",
        "contacts": [
            {
                "__typename": "Contact",
                "location": "Claims",
                "phoneNumber": "+15555550100",
            },
            None,
        ],
    }
    assert parse_insurers({"insurers": [insurer_data, None]}) == (insurer, None)
    assert parse_vehicle_insurance(
        {
            "vehicle": {
                "__typename": "Vehicle",
                "insurance": {
                    "__typename": "Insurance",
                    "id": "insurance-id",
                    "policyNumber": "policy-number",
                    "expirationDate": "2027-08-01",
                    "status": "active",
                    "insurer": insurer_data,
                },
            }
        }
    ) == VehicleInsurance(
        "insurance-id",
        "policy-number",
        "2027-08-01",
        InsuranceStatus.ACTIVE,
        insurer,
    )
    assert parse_add_vehicle_insurance(
        {
            "addVehicleInsurance": {
                "__typename": "AddVehicleInsuranceSuccess",
                "success": True,
            }
        }
    ) == VehicleInsuranceMutationSuccess(True)


def test_parse_collision_centers_and_mutation_unions() -> None:
    assert parse_collision_centers(
        {
            "collisionCenters": [
                {
                    "__typename": "CollisionCenter",
                    "id": "center-id",
                    "name": "Nissan Collision",
                    "address": {
                        "__typename": "Address",
                        "address1": "1 Main St",
                        "address2": None,
                        "city": "Franklin",
                        "state": "TN",
                        "postalCode": "37064",
                        "country": "US",
                    },
                    "distance": {
                        "__typename": "Distance",
                        "value": 8,
                        "unit": "MILE",
                        "driveTime": None,
                    },
                    "phones": [
                        {
                            "__typename": "Phone",
                            "isPrimary": True,
                            "number": "+15555550101",
                        },
                        None,
                    ],
                    "emails": ["claims@example.test", None],
                    "website": None,
                    "properties": {
                        "__typename": "Properties",
                        "nissanCertified": True,
                        "evCertified": None,
                        "p1669718Status": None,
                        "relevanceScore": 0.9,
                        "smartFilterQualified": None,
                        "participantProfileStatus": None,
                        "nissanGTR": False,
                        "typeFacility": None,
                    },
                },
                None,
            ]
        }
    ) == (
        CollisionCenter(
            "center-id",
            "Nissan Collision",
            CollisionCenterAddress("1 Main St", None, "Franklin", "TN", "37064", "US"),
            CollisionCenterDistance(8.0, DistanceUnit.MILE, None),
            (CollisionCenterPhone(True, "+15555550101"), None),
            ("claims@example.test", None),
            None,
            CollisionCenterProperties(True, None, None, 0.9, None, None, False, None),
        ),
        None,
    )
    assert parse_create_collision_report(
        {
            "createCollisionReport": {
                "__typename": "CreateCollisionReportSuccess",
                "collisionId": "claim",
            }
        }
    ) == CollisionReportCreated("claim")
    assert parse_delete_collision_report_photo(
        {
            "deletePhotoForCollisionReport": {
                "__typename": "DeletePhotoForCollisionReportError",
                "message": None,
            }
        }
    ) == CollisionReportPhotoDeleteError(None)
    assert parse_create_collision_report(
        {"createCollisionReport": {"__typename": "FutureCollisionResult"}}
    ) == UnselectedCollisionReportResult("FutureCollisionResult")


async def test_client_wires_all_insurance_and_collision_report_operations() -> None:
    session = FakeSession(
        FakeResponse({"insurers": None}),
        FakeResponse({"vehicle": None}),
        FakeResponse({"addVehicleInsurance": None}),
        FakeResponse({"updateVehicleInsurance": None}),
        FakeResponse({"collisionCenters": None}),
        FakeResponse({"createCollisionReport": None}),
        FakeResponse({"createCollisionReportPDF": None}),
        FakeResponse({"deletePhotoForCollisionReport": None}),
        FakeResponse({"uploadPhotoForCollisionReport": None}),
    )
    sdk = make_client(session, read_only=False)
    insurance = insurance_input()
    search = CollisionCenterSearchInput("VIN", claim_id="claim")
    report = collision_report_input()
    photo = CollisionReportPhotoInput("base64-image")

    assert await sdk.async_get_insurers() is None
    assert await sdk.async_get_vehicle_insurance("VIN") is None
    assert await sdk.async_add_vehicle_insurance(insurance) is None
    assert await sdk.async_update_vehicle_insurance(insurance) is None
    assert await sdk.async_get_collision_centers(search) is None
    assert await sdk.async_create_collision_report(report) is None
    assert await sdk.async_create_collision_report_pdf("claim") is None
    assert (
        await sdk.async_delete_photo_for_collision_report("VIN", "claim", PhotoSection.ONE) is None
    )
    assert (
        await sdk.async_upload_photo_for_collision_report(
            "VIN",
            "claim",
            photo,
            PhotoSection.ONE,
        )
        is None
    )

    payloads: list[Mapping[str, object]] = []
    for call in session.calls:
        payload = call["json"]
        assert isinstance(payload, Mapping)
        payloads.append(payload)
    assert [payload["operationName"] for payload in payloads] == [
        "Insurers",
        "GetVehicleInsurance",
        "AddVehicleInsurance",
        "UpdateVehicleInsurance",
        "CollisionCenters",
        "CreateCollisionReport",
        "CreateCollisionReportPDF",
        "DeletePhotoForCollisionReport",
        "UploadPhotoForCollisionReport",
    ]


async def test_read_only_mode_blocks_all_insurance_and_collision_mutations() -> None:
    session = FakeSession()
    sdk = make_client(session, read_only=True)
    photo = CollisionReportPhotoInput("base64-image")
    calls: tuple[Awaitable[object], ...] = (
        sdk.async_add_vehicle_insurance(insurance_input()),
        sdk.async_update_vehicle_insurance(insurance_input()),
        sdk.async_create_collision_report(collision_report_input()),
        sdk.async_create_collision_report_pdf("claim"),
        sdk.async_delete_photo_for_collision_report("VIN", "claim", PhotoSection.ONE),
        sdk.async_upload_photo_for_collision_report(
            "VIN",
            "claim",
            photo,
            PhotoSection.ONE,
        ),
    )

    for call in calls:
        with pytest.raises(ReadOnlyError):
            await call

    assert session.calls == []
