# API guide

The package exports `NissanClient`, `Country`, `Tokens`, `RequestProof`,
`RequestProofProvider`, domain models, input models, enums, and exceptions from the
`pynissan` namespace. Public objects include precise type hints and runtime docstrings.

## Client lifecycle

The caller owns the `aiohttp.ClientSession` and closes it after all client work is complete.
One client represents one account and one country.
Supported account markets are the United States (`Country.US`), Canada (`Country.CA`), and
Mexico (`Country.MX`).

```python
from aiohttp import ClientSession

from pynissan import Country, NissanClient


async with ClientSession() as session:
    client = NissanClient(session, country=Country.US)
    await client.async_authenticate(email, password)
    vehicles = await client.async_get_vehicles()
```

## Common reads

| Method | Result |
| --- | --- |
| `async_get_vehicles()` | Vehicles associated with the account |
| `async_get_vehicle_status()` | Combined cached status and telemetry |
| `async_get_vehicle_battery_status()` | Battery level, cable state, charge state, range, and remaining time |
| `async_get_vehicle_climate_status()` | Cached cabin climate state |
| `async_get_vehicle_doors_status()` | Door and lock state |
| `async_get_vehicle_location()` | Last reported vehicle location |
| `async_get_vehicle_capabilities()` | Features reported for a vehicle |
| `async_get_charge_schedules()` | Recurring charging schedules |
| `async_get_climate_schedules()` | Recurring climate schedules |
| `async_get_vehicle_service_history()` | Service history entries |

Nullable service fields remain nullable in the returned models. Enum types with an
`UNKNOWN_VALUE` member preserve future upstream values without mapping them to a known state.

## Remote commands

State-changing methods require `read_only=False` when constructing the client.

| Method | Command |
| --- | --- |
| `async_start_climate()` / `async_stop_climate()` | Cabin climate |
| `async_start_charge()` / `async_stop_charge()` | Charging |
| `async_lock_doors()` / `async_unlock_doors()` | Door locks |
| `async_flash_lights()` | Exterior lights |
| `async_flash_lights_and_horn()` | Exterior lights and horn |
| `async_start_engine()` / `async_stop_engine()` | Remote engine start |
| `async_locate_vehicle()` | Vehicle location refresh |
| `async_refresh_vehicle_status()` | Vehicle status refresh |

Vehicle capabilities and account subscriptions determine whether a command is available.
Operations that require request verification use the request proof configured on the client.
Most commands return a `ServiceRequest`; pass it to `async_wait_for_service_request()` to wait
for a terminal result.

```python
request = await client.async_lock_doors(vin)
result = await client.async_wait_for_service_request(vin, request)
```

All polling helpers raise `TimeoutError` when their configured deadline expires. Nullable
results retain the response semantics of the corresponding operation.

## Read-only policy

Read-only mode is enabled by default. A blocked mutation raises `ReadOnlyError` before sending
a network request. Applications should create write-enabled clients only for explicit user
actions.

## Errors

Catch `NissanError` for package-level handling, or use its specific subclasses:
`AuthenticationError`, `NetworkError`, `ApiError`, `GraphQLError`, `ResponseError`, and
`ReadOnlyError`.
