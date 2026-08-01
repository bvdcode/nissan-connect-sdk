from __future__ import annotations

import asyncio
import math
from collections.abc import Mapping

from aiohttp import ClientSession

from . import operations
from ._client_helpers import _is_terminal_service_request, _nullable_success, _success
from ._profile import profile_for
from ._transport import _NissanTransport
from .callbacks import RequestProofProvider, TokenListener
from .countries import Country
from .exceptions import ReadOnlyError, ResponseError
from .models import (
    ServiceRequest,
    ServiceRequestKind,
    ServiceRequestResult,
    Tokens,
    VehicleAlertKind,
    VehicleAlertRequest,
)
from .parsing import (
    parse_service_request,
    parse_service_request_result,
    parse_vehicle_alert_request,
)
from .request_proof import RequestProof


class _NissanClientBase:
    def __init__(
        self,
        session: ClientSession,
        *,
        country: Country = Country.US,
        tokens: Tokens | None = None,
        token_listener: TokenListener | None = None,
        read_only: bool = True,
        oauth_device_id: str | None = None,
        request_proof: RequestProof | None = None,
        request_proof_provider: RequestProofProvider | None = None,
    ) -> None:
        self._transport = _NissanTransport(
            session,
            profile=profile_for(country),
            tokens=tokens,
            token_listener=token_listener,
            oauth_device_id=oauth_device_id,
            request_proof=request_proof,
            request_proof_provider=request_proof_provider,
        )
        self._country = country
        self._read_only = read_only

    @property
    def country(self) -> Country:
        """Return the country selected for this client."""

        return self._country

    @property
    def read_only(self) -> bool:
        """Return whether state-changing operations are blocked."""

        return self._read_only

    @property
    def tokens(self) -> Tokens | None:
        """Return the currently active OAuth tokens."""

        return self._transport.tokens

    @property
    def oauth_device_id(self) -> str:
        """Return the identifier used for a mobile OAuth authorization scope."""

        return self._transport.oauth_device_id

    async def async_authenticate(self, email: str, password: str) -> Tokens:
        """Authenticate with MyNISSAN credentials."""

        return await self._transport.async_authenticate(email, password)

    async def async_refresh_tokens(self) -> Tokens:
        """Refresh and publish the active OAuth token set."""

        return await self._transport.async_refresh_tokens()

    async def async_check_service_request(
        self,
        vin: str,
        request: ServiceRequest,
    ) -> ServiceRequestResult:
        """Check an asynchronous request using its matching Nissan operation."""

        checks = {
            ServiceRequestKind.CHARGE: (
                "CheckChargeServiceRequest",
                operations.CHECK_CHARGE_REQUEST,
                "checkChargeServiceRequest",
            ),
            ServiceRequestKind.CHARGE_CONFIGURATION: (
                "CheckChargeConfigServiceRequest",
                operations.CHECK_CHARGE_CONFIGURATION_REQUEST,
                "checkChargeConfigServiceRequest",
            ),
            ServiceRequestKind.CLIMATE: (
                "CheckRemoteClimateRequest",
                operations.CHECK_CLIMATE_REQUEST,
                "checkRemoteClimateRequest",
            ),
            ServiceRequestKind.DOOR: (
                "CheckDoorServiceRequest",
                operations.CHECK_DOOR_REQUEST,
                "checkDoorServiceRequest",
            ),
            ServiceRequestKind.ENGINE: (
                "CheckEngineServiceRequest",
                operations.CHECK_ENGINE_REQUEST,
                "checkEngineServiceRequest",
            ),
            ServiceRequestKind.HORN_LIGHT: (
                "CheckHornLightServiceRequest",
                operations.CHECK_HORN_LIGHT_REQUEST,
                "checkHornLightServiceRequest",
            ),
            ServiceRequestKind.LOCATION: (
                "CheckLocationServiceRequest",
                operations.CHECK_LOCATION_REQUEST,
                "checkLocationServiceRequest",
            ),
            ServiceRequestKind.OTA: (
                "CheckOtaUpdateServiceRequest",
                operations.CHECK_OTA_UPDATE_REQUEST,
                "checkOtaUpdateServiceRequest",
            ),
            ServiceRequestKind.PHOTO: (
                "CheckTakePhotosAroundVehicleServiceRequest",
                operations.CHECK_PHOTO_REQUEST,
                "checkTakePhotosAroundVehicleServiceRequest",
            ),
            ServiceRequestKind.ROUTE: (
                "CheckRouteServiceRequest",
                operations.CHECK_ROUTE_REQUEST,
                "checkRouteServiceRequest",
            ),
            ServiceRequestKind.T_JUNCTION: (
                "CheckTJunctionServiceRequest",
                operations.CHECK_T_JUNCTION_REQUEST,
                "checkTJunctionServiceRequest",
            ),
            ServiceRequestKind.V2L: (
                "CheckV2LServiceRequest",
                operations.CHECK_V2L_REQUEST,
                "checkV2LServiceRequest",
            ),
            ServiceRequestKind.VEHICLE_STATUS: (
                "CheckRefreshVehicleStatusRequest",
                operations.CHECK_REFRESH_VEHICLE_STATUS_REQUEST,
                "checkRefreshVehicleStatusRequest",
            ),
        }
        check = checks.get(request.kind)
        if check is None:
            raise ResponseError(
                f"Nissan does not expose a status operation for {request.kind.value} requests"
            )
        operation_name, document, root_field = check
        data = await self._transport.async_graphql(
            operation_name,
            document,
            {"vin": vin, "serviceRequestId": request.id},
        )
        return parse_service_request_result(data, root_field, vin)

    async def async_wait_for_service_request(
        self,
        vin: str,
        request: ServiceRequest,
        *,
        poll_interval_seconds: float = 3.0,
        timeout_seconds: float = 210.0,
    ) -> ServiceRequestResult:
        """Poll a remote request until Nissan returns a terminal status."""

        if not math.isfinite(poll_interval_seconds) or poll_interval_seconds <= 0:
            raise ValueError("poll_interval_seconds must be a positive finite number")
        if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be a positive finite number")

        async with asyncio.timeout(timeout_seconds):
            while True:
                result = await self.async_check_service_request(vin, request)
                if _is_terminal_service_request(request.kind, result):
                    return result
                await asyncio.sleep(poll_interval_seconds)

    async def _async_simple_service_request(
        self,
        operation_name: str,
        document: str,
        root_field: str,
        vin: str,
        kind: ServiceRequestKind,
    ) -> ServiceRequest:
        return await self._async_service_request(
            operation_name,
            document,
            root_field,
            {"vin": vin},
            kind,
        )

    async def _async_service_request(
        self,
        operation_name: str,
        document: str,
        root_field: str,
        variables: Mapping[str, object],
        kind: ServiceRequestKind,
        *,
        extra_headers: Mapping[str, str] | None = None,
    ) -> ServiceRequest:
        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            operation_name,
            document,
            variables,
            extra_headers=extra_headers,
        )
        return parse_service_request(data, root_field, kind)

    async def _async_vehicle_alert_request(
        self,
        operation_name: str,
        document: str,
        root_field: str,
        variables: Mapping[str, object],
        kind: VehicleAlertKind,
    ) -> VehicleAlertRequest:
        self._ensure_write_allowed()
        data = await self._transport.async_graphql(operation_name, document, variables)
        return parse_vehicle_alert_request(data, root_field, kind)

    async def _async_success_operation(
        self,
        operation_name: str,
        document: str,
        root_field: str,
        variables: Mapping[str, object],
    ) -> bool:
        self._ensure_write_allowed()
        data = await self._transport.async_graphql(operation_name, document, variables)
        return _success(data, root_field)

    async def _async_nullable_success_operation(
        self,
        operation_name: str,
        document: str,
        root_field: str,
        variables: Mapping[str, object],
        *,
        extra_headers: Mapping[str, str] | None = None,
    ) -> bool:
        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            operation_name,
            document,
            variables,
            extra_headers=extra_headers,
        )
        return _nullable_success(data, root_field)

    def _ensure_write_allowed(self) -> None:
        if self._read_only:
            raise ReadOnlyError(
                "State-changing operations are disabled; construct the client with read_only=False"
            )
