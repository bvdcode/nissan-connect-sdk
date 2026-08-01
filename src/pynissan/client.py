"""Public connected-vehicle client."""

from ._account_client import _AccountClientMixin
from ._alert_client import _AlertClientMixin
from ._climate_charge_client import _ClimateChargeClientMixin
from ._content_client import _ContentClientMixin
from ._dealer_client import _DealerClientMixin
from ._driver_client import _DriverClientMixin
from ._finance_client import _FinanceClientMixin
from ._garage_client import _GarageClientMixin
from ._incident_client import _IncidentClientMixin
from ._message_client import _MessageClientMixin
from ._navigation_command_client import _NavigationCommandClientMixin
from ._navigation_read_client import _NavigationReadClientMixin
from ._ota_notification_client import _OtaNotificationClientMixin
from ._polling_client import _PollingClientMixin
from ._second_delivery_client import _SecondDeliveryClientMixin
from ._vehicle_command_client import _VehicleCommandClientMixin
from ._vehicle_data_client import _VehicleDataClientMixin
from ._vehicle_detail_client import _VehicleDetailClientMixin


class NissanClient(
    _AccountClientMixin,
    _ContentClientMixin,
    _FinanceClientMixin,
    _DealerClientMixin,
    _SecondDeliveryClientMixin,
    _IncidentClientMixin,
    _GarageClientMixin,
    _DriverClientMixin,
    _VehicleDetailClientMixin,
    _NavigationReadClientMixin,
    _MessageClientMixin,
    _AlertClientMixin,
    _VehicleDataClientMixin,
    _PollingClientMixin,
    _ClimateChargeClientMixin,
    _VehicleCommandClientMixin,
    _NavigationCommandClientMixin,
    _OtaNotificationClientMixin,
):
    """Async client for MyNISSAN connected vehicles."""
