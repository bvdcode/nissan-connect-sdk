from __future__ import annotations

import asyncio
import math

from ._energy_client import _EnergyClientMixin
from .energy_account_models import (
    ACCOUNT_STATUS_POLL_INTERVAL_SECONDS,
    ACCOUNT_STATUS_POLL_TIMEOUT_SECONDS,
    EnergyAccountPollingOutcome,
    EnergyAccountStatusResult,
    account_status_polling_outcome,
)
from .pnc_models import (
    PlugAndChargeServiceState,
    PlugAndChargeServiceStatus,
    PublicChargeSessionState,
    PublicChargeSessionStatus,
)


class _PollingClientMixin(_EnergyClientMixin):
    async def async_wait_for_pnc_service_status(
        self,
        vin: str,
        desired_state: PlugAndChargeServiceState,
        *,
        poll_interval_seconds: float = 3.0,
        timeout_seconds: float = 210.0,
    ) -> PlugAndChargeServiceStatus | None:
        """Poll enrollment while it remains in the desired transition state."""

        match desired_state:
            case PlugAndChargeServiceState.ENABLED:
                transitional_state = PlugAndChargeServiceState.ENABLING
            case PlugAndChargeServiceState.DISABLED:
                transitional_state = PlugAndChargeServiceState.DISABLING
            case _:
                raise ValueError("desired_state must be ENABLED or DISABLED")
        if not math.isfinite(poll_interval_seconds) or poll_interval_seconds <= 0:
            raise ValueError("poll_interval_seconds must be a positive finite number")
        if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be a positive finite number")

        async with asyncio.timeout(timeout_seconds):
            while True:
                result = await self.async_get_pnc_service_status(vin)
                state = (
                    result.data.state if result is not None and result.data is not None else None
                )
                if state is not None and state is not transitional_state:
                    return result
                await asyncio.sleep(poll_interval_seconds)

    async def async_wait_for_energy_account_status(
        self,
        vin: str,
        *,
        poll_interval_seconds: float = ACCOUNT_STATUS_POLL_INTERVAL_SECONDS,
        timeout_seconds: float = ACCOUNT_STATUS_POLL_TIMEOUT_SECONDS,
    ) -> EnergyAccountStatusResult | None:
        """Poll Nissan Energy account status until it leaves enrollment transition."""

        if not math.isfinite(poll_interval_seconds) or poll_interval_seconds <= 0:
            raise ValueError("poll_interval_seconds must be a positive finite number")
        if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be a positive finite number")

        async with asyncio.timeout(timeout_seconds):
            while True:
                result = await self.async_get_energy_account_status(vin)
                if account_status_polling_outcome(result) is EnergyAccountPollingOutcome.COMPLETE:
                    return result
                await asyncio.sleep(poll_interval_seconds)

    async def async_wait_for_public_charge_session_status(
        self,
        vin: str,
        *,
        poll_interval_seconds: float = 3.0,
        timeout_seconds: float = 210.0,
    ) -> PublicChargeSessionStatus | None:
        """Poll a public session until it leaves pending or reservation state."""

        if not math.isfinite(poll_interval_seconds) or poll_interval_seconds <= 0:
            raise ValueError("poll_interval_seconds must be a positive finite number")
        if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be a positive finite number")

        terminal_states = {
            PublicChargeSessionState.ACTIVE,
            PublicChargeSessionState.COMPLETED,
            PublicChargeSessionState.FAILED,
        }
        async with asyncio.timeout(timeout_seconds):
            while True:
                result = await self.async_get_public_charge_session_status(vin)
                if result is None or result.data is None:
                    return None
                state = result.data.status
                if state is None or state in terminal_states:
                    return result
                await asyncio.sleep(poll_interval_seconds)
