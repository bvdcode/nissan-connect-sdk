from __future__ import annotations

from . import operations
from ._client_base import _NissanClientBase
from .collision_report_inputs import (
    CollisionCenterSearchInput,
    CollisionReportPhotoInput,
    CreateCollisionReportInput,
    collision_center_variables,
    collision_report_pdf_variables,
    collision_report_photo_variables,
    create_collision_report_variables,
    delete_collision_report_photo_variables,
)
from .collision_report_models import (
    CollisionCenter,
    CreateCollisionReportPdfResult,
    CreateCollisionReportResult,
    DeleteCollisionReportPhotoResult,
    PhotoSection,
    UploadCollisionReportPhotoResult,
)
from .collision_report_parsing import (
    parse_collision_centers,
    parse_create_collision_report,
    parse_create_collision_report_pdf,
    parse_delete_collision_report_photo,
    parse_upload_collision_report_photo,
)
from .insurance_inputs import VehicleInsuranceInput, vehicle_insurance_variables
from .insurance_models import (
    VehicleInsurance,
    VehicleInsuranceMutationResult,
    VehicleInsurer,
)
from .insurance_parsing import (
    parse_add_vehicle_insurance,
    parse_insurers,
    parse_update_vehicle_insurance,
    parse_vehicle_insurance,
)


class _IncidentClientMixin(_NissanClientBase):
    async def async_get_insurers(
        self,
    ) -> tuple[VehicleInsurer | None, ...] | None:
        """Return the insurer catalog available to the signed-in account."""

        data = await self._transport.async_graphql(
            "Insurers",
            operations.INSURERS,
            {},
        )
        return parse_insurers(data)

    async def async_get_vehicle_insurance(
        self,
        vin: str,
    ) -> VehicleInsurance | None:
        """Return the insurance policy attached to a vehicle."""

        data = await self._transport.async_graphql(
            "GetVehicleInsurance",
            operations.GET_VEHICLE_INSURANCE,
            {"vin": vin},
        )
        return parse_vehicle_insurance(data)

    async def async_add_vehicle_insurance(
        self,
        config: VehicleInsuranceInput,
    ) -> VehicleInsuranceMutationResult | None:
        """Add insurance details to a vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "AddVehicleInsurance",
            operations.ADD_VEHICLE_INSURANCE,
            vehicle_insurance_variables(config),
        )
        return parse_add_vehicle_insurance(data)

    async def async_update_vehicle_insurance(
        self,
        config: VehicleInsuranceInput,
    ) -> VehicleInsuranceMutationResult | None:
        """Replace insurance details for a vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateVehicleInsurance",
            operations.UPDATE_VEHICLE_INSURANCE,
            vehicle_insurance_variables(config),
        )
        return parse_update_vehicle_insurance(data)

    async def async_get_collision_centers(
        self,
        config: CollisionCenterSearchInput,
    ) -> tuple[CollisionCenter | None, ...] | None:
        """Return collision centers matching vehicle and location filters."""

        data = await self._transport.async_graphql(
            "CollisionCenters",
            operations.COLLISION_CENTERS,
            collision_center_variables(config),
        )
        return parse_collision_centers(data)

    async def async_create_collision_report(
        self,
        config: CreateCollisionReportInput,
    ) -> CreateCollisionReportResult | None:
        """Create a collision report for a vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CreateCollisionReport",
            operations.CREATE_COLLISION_REPORT,
            create_collision_report_variables(config),
        )
        return parse_create_collision_report(data)

    async def async_create_collision_report_pdf(
        self,
        collision_id: str,
    ) -> CreateCollisionReportPdfResult | None:
        """Generate a PDF URL for a collision report."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CreateCollisionReportPDF",
            operations.CREATE_COLLISION_REPORT_PDF,
            collision_report_pdf_variables(collision_id),
        )
        return parse_create_collision_report_pdf(data)

    async def async_delete_photo_for_collision_report(
        self,
        vin: str,
        collision_id: str,
        photo_section: PhotoSection,
    ) -> DeleteCollisionReportPhotoResult | None:
        """Delete one photo slot from a collision report."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "DeletePhotoForCollisionReport",
            operations.DELETE_PHOTO_FOR_COLLISION_REPORT,
            delete_collision_report_photo_variables(
                vin,
                collision_id,
                photo_section,
            ),
        )
        return parse_delete_collision_report_photo(data)

    async def async_upload_photo_for_collision_report(
        self,
        vin: str,
        collision_id: str,
        photo: CollisionReportPhotoInput,
        photo_section: PhotoSection,
    ) -> UploadCollisionReportPhotoResult | None:
        """Upload a Base64 attachment to one collision-report photo slot."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UploadPhotoForCollisionReport",
            operations.UPLOAD_PHOTO_FOR_COLLISION_REPORT,
            collision_report_photo_variables(
                vin,
                collision_id,
                photo,
                photo_section,
            ),
        )
        return parse_upload_collision_report_photo(data)
