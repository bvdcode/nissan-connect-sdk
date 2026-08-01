from __future__ import annotations

from . import operations
from ._client_base import _NissanClientBase
from .garage_inputs import (
    NcarIcarRegisterAccountInput,
    add_vehicle_variables,
    apc_agreement_variables,
    apc_document_url_variables,
    connected_terms_and_conditions_by_vin_variables,
    create_apc_agreement_variables,
    delete_vehicle_variables,
    ncar_icar_add_vehicle_variables,
    onboarding_features_variables,
    ownership_status_variables,
    pending_vehicles_variables,
    update_apc_agreement_variables,
    update_vehicle_manual_mileage_variables,
    update_vehicle_nickname_variables,
    update_vehicle_variables,
    upload_ownership_verification_variables,
)
from .garage_models import (
    AddVehicleResult,
    APCAgreement,
    APCAgreementMutationResult,
    APCDocument,
    ConnectedTermsAndConditionsResult,
    DeleteVehicleResult,
    NcarIcarAddVehicleResult,
    OnboardingFeature,
    OwnershipStatus,
    PendingVehicle,
    UpdateVehicleManualMileageResult,
    UpdateVehicleNicknameResult,
    UpdateVehicleResult,
    UploadOwnershipVerificationResult,
    VehicleHologram,
)
from .garage_parsing import (
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
from .graphql_input import UNSET, UnsetType
from .models import (
    Vehicle,
)
from .parsing import (
    parse_vehicles,
)
from .wearable_models import VehicleWithCapabilities
from .wearable_parsing import parse_vehicles_with_capabilities


class _GarageClientMixin(_NissanClientBase):
    async def async_get_vehicles(self) -> tuple[Vehicle, ...]:
        """Return vehicles attached to the account."""

        data = await self._transport.async_graphql(
            "VehiclesStaticData",
            operations.VEHICLES_STATIC_DATA,
            {},
        )
        return parse_vehicles(data)

    async def async_get_vehicles_with_capabilities(
        self,
    ) -> tuple[VehicleWithCapabilities | None, ...] | None:
        """Return the wearable client's batch vehicle and capability summary."""

        data = await self._transport.async_graphql(
            "WearableVehicles",
            operations.WEARABLE_VEHICLES,
            {},
        )
        return parse_vehicles_with_capabilities(data)

    async def async_add_vehicle(
        self,
        vin: str,
        terms_and_conditions_accepted: bool,
    ) -> AddVehicleResult | None:
        """Register a vehicle in the signed-in account's garage."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "AddVehicle",
            operations.ADD_VEHICLE,
            add_vehicle_variables(vin, terms_and_conditions_accepted),
        )
        return parse_add_vehicle(data)

    async def async_delete_vehicle(self, vin: str) -> DeleteVehicleResult | None:
        """Remove a vehicle from the signed-in account's garage."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "DeleteVehicle",
            operations.DELETE_VEHICLE,
            delete_vehicle_variables(vin),
        )
        return parse_delete_vehicle(data)

    async def async_add_ncar_icar_vehicle(
        self,
        terms_and_conditions_accepted: bool,
        guid: str,
        *,
        account: NcarIcarRegisterAccountInput | UnsetType | None = UNSET,
    ) -> NcarIcarAddVehicleResult | None:
        """Register a vehicle through the NCAR/ICAR garage flow."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "NcarIcarAddVehicle",
            operations.NCAR_ICAR_ADD_VEHICLE,
            ncar_icar_add_vehicle_variables(
                terms_and_conditions_accepted,
                guid,
                account=account,
            ),
        )
        return parse_ncar_icar_add_vehicle(data)

    async def async_get_pending_vehicles(
        self,
    ) -> tuple[PendingVehicle | None, ...] | None:
        """Return garage registrations awaiting ownership verification."""

        data = await self._transport.async_graphql(
            "PendingVehicles",
            operations.PENDING_VEHICLES,
            pending_vehicles_variables(),
        )
        return parse_pending_vehicles(data)

    async def async_get_ownership_status(self, vin: str) -> OwnershipStatus | None:
        """Return the vehicle's account ownership sign-in state."""

        data = await self._transport.async_graphql(
            "OwnershipStatus",
            operations.OWNERSHIP_STATUS,
            ownership_status_variables(vin),
        )
        return parse_ownership_status(data)

    async def async_get_apc_agreement(self, vin: str) -> APCAgreement | None:
        """Return the vehicle's APC agreement state."""

        data = await self._transport.async_graphql(
            "APCAgreement",
            operations.APC_AGREEMENT,
            apc_agreement_variables(vin),
        )
        return parse_apc_agreement(data)

    async def async_get_apc_document_url(self, vin: str) -> APCDocument | None:
        """Return the vehicle's APC agreement document URL."""

        data = await self._transport.async_graphql(
            "APCDocumentURL",
            operations.APC_DOCUMENT_URL,
            apc_document_url_variables(vin),
        )
        return parse_apc_document_url(data)

    async def async_create_apc_agreement(
        self,
        vin: str,
        opt_in: bool,
    ) -> APCAgreementMutationResult | None:
        """Create the vehicle's APC agreement selection."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CreateAPCAgreement",
            operations.CREATE_APC_AGREEMENT,
            create_apc_agreement_variables(vin, opt_in),
        )
        return parse_create_apc_agreement(data)

    async def async_update_apc_agreement(
        self,
        vin: str,
        opt_in: bool,
    ) -> APCAgreementMutationResult | None:
        """Update the vehicle's APC agreement selection."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateAPCAgreement",
            operations.UPDATE_APC_AGREEMENT,
            update_apc_agreement_variables(vin, opt_in),
        )
        return parse_update_apc_agreement(data)

    async def async_get_connected_terms_and_conditions_by_vin(
        self,
        vin: str,
    ) -> ConnectedTermsAndConditionsResult | None:
        """Request connected-services terms for a VIN through Nissan's mutation."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "ConnectedTermsAndConditionsByVIN",
            operations.CONNECTED_TERMS_AND_CONDITIONS_BY_VIN,
            connected_terms_and_conditions_by_vin_variables(vin),
        )
        return parse_connected_terms_and_conditions_by_vin(data)

    async def async_get_onboarding_features(
        self,
        vin: str,
    ) -> tuple[OnboardingFeature | None, ...] | None:
        """Return feature cards used while onboarding a vehicle."""

        data = await self._transport.async_graphql(
            "OnboardingFeatures",
            operations.ONBOARDING_FEATURES,
            onboarding_features_variables(vin),
        )
        return parse_onboarding_features(data)

    async def async_update_vehicle(
        self,
        vin: str,
        *,
        license_plate: str | UnsetType | None = UNSET,
        hologram: VehicleHologram | UnsetType | None = UNSET,
    ) -> UpdateVehicleResult | None:
        """Update optional license-plate and hologram garage metadata."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateVehicle",
            operations.UPDATE_VEHICLE,
            update_vehicle_variables(
                vin,
                license_plate=license_plate,
                hologram=hologram,
            ),
        )
        return parse_update_vehicle(data)

    async def async_update_vehicle_manual_mileage(
        self,
        vin: str,
        *,
        manual_mileage: int | UnsetType | None = UNSET,
    ) -> UpdateVehicleManualMileageResult | None:
        """Update or clear the vehicle's manually recorded mileage."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateVehicleManualMileage",
            operations.UPDATE_VEHICLE_MANUAL_MILEAGE,
            update_vehicle_manual_mileage_variables(
                vin,
                manual_mileage=manual_mileage,
            ),
        )
        return parse_update_vehicle_manual_mileage(data)

    async def async_update_vehicle_nickname(
        self,
        vin: str,
        nickname: str,
    ) -> UpdateVehicleNicknameResult | None:
        """Update the vehicle nickname shown in the account garage."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateVehicleNickname",
            operations.UPDATE_VEHICLE_NICKNAME,
            update_vehicle_nickname_variables(vin, nickname),
        )
        return parse_update_vehicle_nickname(data)

    async def async_upload_ownership_verification(
        self,
        vin: str,
        filename: str,
        attachment: str,
        opt_in_sms: bool,
    ) -> UploadOwnershipVerificationResult | None:
        """Upload an ownership-verification attachment for a pending vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UploadOwnershipVerification",
            operations.UPLOAD_OWNERSHIP_VERIFICATION,
            upload_ownership_verification_variables(
                vin,
                filename,
                attachment,
                opt_in_sms,
            ),
        )
        return parse_upload_ownership_verification(data)
