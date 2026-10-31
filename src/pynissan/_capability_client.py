"""Vehicle capability queries shared by telemetry and remote commands."""

from . import operations
from ._client_base import _NissanClientBase
from .graphql_input import serialize_enum
from .models import TemperatureUnit, VehicleCapabilities
from .parsing import parse_vehicle_capabilities


class _CapabilityClientMixin(_NissanClientBase):
    async def async_get_vehicle_capabilities(
        self,
        vin: str,
        temperature_unit: TemperatureUnit = TemperatureUnit.FAHRENHEIT,
    ) -> VehicleCapabilities:
        """Return the connected services advertised for a vehicle."""

        data = await self._transport.async_graphql(
            "VehicleCapabilities",
            operations.VEHICLE_CAPABILITIES,
            {"vin": vin, "unit": serialize_enum(temperature_unit)},
        )
        return parse_vehicle_capabilities(data, vin)
