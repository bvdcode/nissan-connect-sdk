from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .collision_report_models import PhotoSection
from .common_inputs import CoordinateInput, coordinate_input
from .graphql_input import (
    UNSET,
    UnsetType,
    optional_input_fields,
    serialize_datetime,
    serialize_enum,
)
from .models import DistanceUnit


@dataclass(frozen=True, slots=True)
class CollisionCenterAddressInput:
    """Optional country and postal code for collision-center discovery."""

    country: str | UnsetType | None = UNSET
    postal_code: str | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class CollisionCenterSearchInput:
    """Vehicle and optional location or claim filters for collision centers."""

    vin: str
    coordinates: CoordinateInput | UnsetType | None = UNSET
    address: CollisionCenterAddressInput | UnsetType | None = UNSET
    claim_id: str | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class CollisionReportVehicleInput:
    """Required vehicle identity and optional registration details."""

    make: str
    model: str
    model_year: str
    license_plate: str | UnsetType | None = UNSET
    color: str | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class CollisionReportUserInput:
    """Optional driver contact fields included in a collision report."""

    first_name: str | UnsetType | None = UNSET
    last_name: str | UnsetType | None = UNSET
    email: str | UnsetType | None = UNSET
    phone_number: str | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class CollisionReportCollisionCenterInput:
    """Optional collision-center details included in a report."""

    name: str | UnsetType | None = UNSET
    address: str | UnsetType | None = UNSET
    phone_number: str | UnsetType | None = UNSET
    email: str | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class CollisionReportTowingCompanyInput:
    """Optional towing-company details included in a report."""

    name: str | UnsetType | None = UNSET
    email: str | UnsetType | None = UNSET
    phone_number: str | UnsetType | None = UNSET
    address: str | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class CollisionReportMetadataInput:
    """Optional collision telemetry and report time fields."""

    report_date_time: datetime | UnsetType | None = UNSET
    collision_date_time: datetime | UnsetType | None = UNSET
    odometer: float | UnsetType | None = UNSET
    speed: float | UnsetType | None = UNSET
    unit: DistanceUnit | UnsetType | None = UNSET
    mil_count: int | UnsetType | None = UNSET
    mil_data: str | UnsetType | None = UNSET
    latitude: float | UnsetType | None = UNSET
    longitude: float | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class CreateCollisionReportInput:
    """Complete input for creating a collision report."""

    vin: str
    vehicle: CollisionReportVehicleInput
    user: CollisionReportUserInput | UnsetType | None = UNSET
    insurance_company_name: str | UnsetType | None = UNSET
    collision_center: CollisionReportCollisionCenterInput | UnsetType | None = UNSET
    towing_company: CollisionReportTowingCompanyInput | UnsetType | None = UNSET
    collision_metadata: CollisionReportMetadataInput | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class CollisionReportPhotoInput:
    """Base64 attachment and optional filename for a report photo."""

    attachment: str
    filename: str | UnsetType | None = UNSET


def collision_center_variables(config: CollisionCenterSearchInput) -> dict[str, object]:
    """Serialize collision-center discovery variables."""

    coordinates: object = (
        coordinate_input(config.coordinates)
        if isinstance(config.coordinates, CoordinateInput)
        else config.coordinates
    )
    address: object = (
        collision_center_address_input(config.address)
        if isinstance(config.address, CollisionCenterAddressInput)
        else config.address
    )
    return {
        "input": optional_input_fields(
            vin=config.vin,
            coordinates=coordinates,
            address=address,
            claimId=config.claim_id,
        )
    }


def create_collision_report_variables(
    config: CreateCollisionReportInput,
) -> dict[str, object]:
    """Serialize collision-report creation variables."""

    user: object = (
        collision_report_user_input(config.user)
        if isinstance(config.user, CollisionReportUserInput)
        else config.user
    )
    collision_center: object = (
        collision_report_collision_center_input(config.collision_center)
        if isinstance(config.collision_center, CollisionReportCollisionCenterInput)
        else config.collision_center
    )
    towing_company: object = (
        collision_report_towing_company_input(config.towing_company)
        if isinstance(config.towing_company, CollisionReportTowingCompanyInput)
        else config.towing_company
    )
    collision_metadata: object = (
        collision_report_metadata_input(config.collision_metadata)
        if isinstance(config.collision_metadata, CollisionReportMetadataInput)
        else config.collision_metadata
    )
    return {
        "input": optional_input_fields(
            vin=config.vin,
            user=user,
            insuranceCompanyName=config.insurance_company_name,
            vehicle=collision_report_vehicle_input(config.vehicle),
            collisionCenter=collision_center,
            towingCompany=towing_company,
            collisionMetadata=collision_metadata,
        )
    }


def collision_report_photo_variables(
    vin: str,
    collision_id: str,
    photo: CollisionReportPhotoInput,
    photo_section: PhotoSection,
) -> dict[str, object]:
    """Serialize collision-report photo upload variables."""

    return {
        "input": {
            "vin": vin,
            "collisionId": collision_id,
            "photo": optional_input_fields(
                filename=photo.filename,
                attachment=photo.attachment,
            ),
            "photoSection": serialize_enum(photo_section),
        }
    }


def collision_report_pdf_variables(collision_id: str) -> dict[str, object]:
    """Serialize collision-report PDF generation variables."""

    return {"input": {"collisionId": collision_id}}


def delete_collision_report_photo_variables(
    vin: str,
    collision_id: str,
    photo_section: PhotoSection,
) -> dict[str, object]:
    """Serialize collision-report photo deletion variables."""

    return {
        "input": {
            "vin": vin,
            "collisionId": collision_id,
            "photoSection": serialize_enum(photo_section),
        }
    }


def collision_center_address_input(value: CollisionCenterAddressInput) -> dict[str, object]:
    return optional_input_fields(country=value.country, postalCode=value.postal_code)


def collision_report_vehicle_input(
    value: CollisionReportVehicleInput,
) -> dict[str, object]:
    return optional_input_fields(
        make=value.make,
        model=value.model,
        modelYear=value.model_year,
        licensePlate=value.license_plate,
        color=value.color,
    )


def collision_report_user_input(value: CollisionReportUserInput) -> dict[str, object]:
    return optional_input_fields(
        firstName=value.first_name,
        lastName=value.last_name,
        email=value.email,
        phoneNumber=value.phone_number,
    )


def collision_report_collision_center_input(
    value: CollisionReportCollisionCenterInput,
) -> dict[str, object]:
    return optional_input_fields(
        name=value.name,
        address=value.address,
        phoneNumber=value.phone_number,
        email=value.email,
    )


def collision_report_towing_company_input(
    value: CollisionReportTowingCompanyInput,
) -> dict[str, object]:
    return optional_input_fields(
        name=value.name,
        email=value.email,
        phoneNumber=value.phone_number,
        address=value.address,
    )


def collision_report_metadata_input(
    value: CollisionReportMetadataInput,
) -> dict[str, object]:
    report_date_time: object = _optional_datetime(value.report_date_time)
    collision_date_time: object = _optional_datetime(value.collision_date_time)
    unit: object = (
        serialize_enum(value.unit) if isinstance(value.unit, DistanceUnit) else value.unit
    )
    return optional_input_fields(
        reportDateTime=report_date_time,
        collisionDateTime=collision_date_time,
        odometer=value.odometer,
        speed=value.speed,
        unit=unit,
        milCount=value.mil_count,
        milData=value.mil_data,
        latitude=value.latitude,
        longitude=value.longitude,
    )


def _optional_datetime(value: datetime | UnsetType | None) -> object:
    return serialize_datetime(value) if isinstance(value, datetime) else value
