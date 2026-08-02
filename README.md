# pynissan

[![CI](https://github.com/bvdcode/nissan-connect-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/bvdcode/nissan-connect-sdk/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/pynissan.svg)](https://pypi.org/project/pynissan/)
[![Python](https://img.shields.io/pypi/pyversions/pynissan.svg)](https://pypi.org/project/pynissan/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

`pynissan` is an async Python client for MyNISSAN connected vehicles. It provides a typed
API for vehicle telemetry, charging, climate, remote commands, account data, and
connected-service features.

The client supports MyNISSAN accounts in the United States and Canada, plus MiNissan
accounts in Mexico. Vehicle and subscription capabilities determine which telemetry and
remote controls are available.

## Highlights

- Fully async I/O built on `aiohttp`.
- Typed, immutable response models and a `py.typed` marker.
- Cached vehicle, battery, charging, climate, door, location, tire, and mileage data.
- Charging, climate, lock, light, horn, engine, location, and status-refresh commands.
- Climate and charge schedules, vehicle capabilities, alerts, maintenance, and history.
- Automatic access-token refresh with a callback for persisting replacement tokens.
- Typed command requests with status polling and terminal results.
- Read-only mode enabled by default for safe discovery and monitoring.

## Installation

```bash
python -m pip install pynissan
```

Python 3.12 or newer is required.

Supported account markets are `Country.US`, `Country.CA`, and `Country.MX`.

## Quick start

The caller owns the `aiohttp.ClientSession` and decides how credentials and reusable tokens
are stored.

```python
from aiohttp import ClientSession

from pynissan import Country, NissanClient, Tokens


async def save_tokens(tokens: Tokens) -> None:
    """Persist replacement tokens in the application's secure storage."""


async def read_vehicle(email: str, password: str) -> None:
    async with ClientSession() as session:
        client = NissanClient(
            session,
            country=Country.US,
            token_listener=save_tokens,
        )
        await client.async_authenticate(email, password)

        vehicles = await client.async_get_vehicles()
        if not vehicles:
            return

        status = await client.async_get_vehicle_status(vehicles[0].vin)
        if status.battery is not None:
            print(status.battery.level)
            print(status.battery.is_charging)
```

Supply previously saved tokens to avoid signing in again:

```python
client = NissanClient(
    session,
    country=Country.US,
    tokens=saved_tokens,
    token_listener=save_tokens,
)
```

The client refreshes expired tokens before a request and publishes the replacement token set
through `token_listener`.

The [authentication guide](docs/authentication.md) covers token reuse and request verification
for applications that need those flows.

## Read-only safety

`NissanClient` starts in read-only mode. Queries work normally, while methods that change
vehicle or account state raise `ReadOnlyError` before any network request is sent.

```python
from pynissan import Country, NissanClient

client = NissanClient(
    session,
    country=Country.US,
    tokens=saved_tokens,
    read_only=False,
)
```

Enable write access only for an explicit user action. Remote commands return a typed request
that can be polled until Nissan reports a terminal status.

```python
from pynissan import ClimateSettings, TemperatureUnit

request = await client.async_start_climate(
    vin,
    ClimateSettings(72, TemperatureUnit.FAHRENHEIT),
)
result = await client.async_wait_for_service_request(vin, request)
```

## Charging state

Battery status distinguishes the cable and charging states and includes the server-provided
remaining charge time.

```python
battery = await client.async_get_vehicle_battery_status(vin)
if battery is not None:
    print(battery.level)
    print(battery.is_plugged_in)
    print(battery.is_charging)
    print(battery.remaining_charge_time)
```

## Errors

All package exceptions inherit from `NissanError`:

- `AuthenticationError` for sign-in and token-refresh failures;
- `NetworkError` for connection and timeout failures;
- `ApiError` for rejected HTTP requests;
- `GraphQLError` for rejected GraphQL operations;
- `ResponseError` for malformed responses;
- `ReadOnlyError` for blocked state-changing operations.

## Development

```bash
python -m pip install -e ".[test]"
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m pytest
python -m build
```

See the [API guide](docs/api.md) and [authentication guide](docs/authentication.md) for usage
details. Development and release procedures are documented in
[CONTRIBUTING.md](CONTRIBUTING.md) and [docs/releasing.md](docs/releasing.md). Security issues
should follow [SECURITY.md](SECURITY.md).

## Project status

`pynissan` is maintained by the community and is not affiliated with, endorsed by, or
supported by Nissan Motor Co., Ltd.
