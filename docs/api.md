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

## Vehicle telemetry

`async_get_vehicle_status(vin)` returns the combined cached `VehicleStatus`. Each optional
section can be `None` when the vehicle does not report it.

| Data | Model fields |
| --- | --- |
| Remaining charging time | `status.battery.remaining_charge_time` in minutes; `remaining_charge_duration` as a `timedelta` during charging |
| Estimated charging completion | `status.battery.estimate_charge_completion(observed_at)` |
| Odometer | `status.mileage.total`, with `status.mileage.unit` and `status.mileage.recorded_at` |
| Four tire pressures | `status.tire_pressure.front_left`, `front_right`, `rear_left`, `rear_right`; `unit` is `"psi"` |
| Tire condition | `status.tire_pressure.front_left_status`, `front_right_status`, `rear_left_status`, `rear_right_status` |
| Each door and window | `status.doors.front_left`, `front_right`, `rear_left`, `rear_right`: raw `ajar`, `window`, `lock`; nullable `is_open` and `is_locked` properties |
| Overall locks, trunk, hood | `status.doors.is_locked`, `is_trunk_locked`, `is_trunk_open`, `is_hood_open` |
| Active warning count | `status.warning_count` |
| Active warnings and messages | `status.active_warnings`, `status.warning_messages` |
| All maintenance indicators | `status.maintenance_indicators`, including inactive and unknown indicators |
| Vehicle image | `vehicle.image_url` from `async_get_vehicles()` |

Odometer values retain the reported unit without conversion. Tire pressures are in psi;
individual values and their reported condition can be absent. A missing or unrecognized
door/lock state produces `None` from the convenience properties, not a closed or locked
state. The raw values remain available. The overall lock property uses the reported overall
state rather than inferring it from individual doors.

`active_warnings` includes only maintenance indicators with `active=True`.
`warning_count` counts those indicators, including ones without a message;
`warning_messages` includes their available messages without truncation. An empty warning
tuple does not distinguish a response with no indicators from one without indicator data.

`image_url` is the vehicle artwork supplied with its account record, not a camera image.
The URL is optional; the package does not download the image.

### Charging estimates

```python
from datetime import UTC, datetime

battery = await client.async_get_vehicle_battery_status(vin)
observed_at = datetime.now(UTC)
if battery is not None:
    remaining = battery.remaining_charge_duration
    completion = battery.estimate_charge_completion(observed_at)
```

Supply a timezone-aware observation timestamp. The estimate adds the reported remaining
minutes as elapsed time and returns the result in the observation's timezone, including
daylight-saving transitions. A naive timestamp raises `ValueError`.

Both helpers return `None` unless charging is explicitly active and the remaining time is
present and nonnegative. The raw `remaining_charge_time` remains available regardless of
charging state. Completion is a local estimate, not a server-reported finish timestamp;
cached telemetry may be stale. Use the telemetry's observation time when it is known rather
than repeatedly advancing an older estimate with the current time.

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
`ServiceCapability.is_available` requires both `enabled=True` and `subscribed=True`.
`VehicleCapabilities` exposes `can_lock_doors`, `can_unlock_doors`, `can_flash_lights`, and
`can_flash_lights_and_horn` for deciding which controls to offer. Lock and unlock support
can be advertised together or separately. Both light commands use the horn/light service;
there is no separate horn-only command.

The four lock and light/horn methods fetch the vehicle's current capabilities before each
command. A disabled, missing, or unconfirmed subscription raises `UnsupportedCommandError`
without sending the mutation. Capability-query errors propagate without sending it either.
Read-only mode rejects the action before even querying capabilities. A successful preflight
does not guarantee execution: the server and vehicle can still reject a command.

Operations that require request verification use the request proof configured on the client.
Most commands return a `ServiceRequest`; pass it to `async_wait_for_service_request()` to wait
for a terminal result.

```python
capabilities = await client.async_get_vehicle_capabilities(vin)
if capabilities.can_lock_doors:
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
`ReadOnlyError`, and `UnsupportedCommandError`.
