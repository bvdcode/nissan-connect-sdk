"""Remote lock and horn/light commands require current service availability."""

from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import cast

import pytest
from test_client import FakeResponse, FakeSession, make_client

from pynissan import (
    GraphQLError,
    NissanClient,
    ReadOnlyError,
    ResponseError,
    ServiceRequest,
    ServiceRequestKind,
    UnsupportedCommandError,
)


@dataclass(frozen=True)
class CommandCase:
    call: Callable[[NissanClient, str], Awaitable[ServiceRequest]]
    operation: str
    root: str
    service: str
    kind: ServiceRequestKind


COMMANDS = (
    CommandCase(
        lambda c, v: c.async_lock_doors(v),
        "DoorLock",
        "doorLock",
        "REMOTE_DOOR_LOCK",
        ServiceRequestKind.DOOR,
    ),
    CommandCase(
        lambda c, v: c.async_unlock_doors(v),
        "DoorUnlock",
        "doorUnlock",
        "REMOTE_DOOR_UNLOCK",
        ServiceRequestKind.DOOR,
    ),
    CommandCase(
        lambda c, v: c.async_flash_lights(v),
        "FlashLights",
        "flashLights",
        "REMOTE_HORN_LIGHTS",
        ServiceRequestKind.HORN_LIGHT,
    ),
    CommandCase(
        lambda c, v: c.async_flash_lights_and_horn(v),
        "FlashLightsHorn",
        "flashLightsHorn",
        "REMOTE_HORN_LIGHTS",
        ServiceRequestKind.HORN_LIGHT,
    ),
)


def capabilities_response(
    service: str, *, enabled: bool = True, subscribed: bool | None = True
) -> FakeResponse:
    return FakeResponse(
        200,
        {
            "data": {
                "vehicle": {
                    "capabilities": {
                        "serviceCapability": [
                            {"type": service, "enabled": enabled, "subscribed": subscribed}
                        ]
                    }
                }
            }
        },
    )


def command_response(case: CommandCase) -> FakeResponse:
    return FakeResponse(200, {"data": {case.root: {"serviceRequestId": "request-1"}}})


def request_payload(session: FakeSession, index: int) -> Mapping[str, object]:
    return cast(Mapping[str, object], session.calls[index]["json"])


@pytest.mark.parametrize("case", COMMANDS)
@pytest.mark.asyncio
async def test_supported_command_and_polling(case: CommandCase) -> None:
    check_root = {
        ServiceRequestKind.DOOR: "checkDoorServiceRequest",
        ServiceRequestKind.HORN_LIGHT: "checkHornLightServiceRequest",
    }[case.kind]
    session = FakeSession(
        capabilities_response(case.service),
        command_response(case),
        FakeResponse(200, {"data": {check_root: {"status": "SUCCESS"}}}),
    )
    client = make_client(session, read_only=False)
    request = await case.call(client, "VIN")
    assert request.id == "request-1"
    assert request.kind is case.kind
    result = await client.async_wait_for_service_request("VIN", request)
    assert result.is_success
    assert len(session.calls) == 3
    assert request_payload(session, 0)["operationName"] == "VehicleCapabilities"
    assert request_payload(session, 0)["variables"] == {"vin": "VIN", "unit": "FAHRENHEIT"}
    assert request_payload(session, 1)["operationName"] == case.operation
    assert request_payload(session, 1)["variables"] == {"vin": "VIN"}


@pytest.mark.parametrize("case", COMMANDS[:2])
@pytest.mark.asyncio
async def test_combined_lock_service(case: CommandCase) -> None:
    session = FakeSession(capabilities_response("REMOTE_DOOR_LOCK_UNLOCK"), command_response(case))
    request = await case.call(make_client(session, read_only=False), "VIN")
    assert request.kind is ServiceRequestKind.DOOR


@pytest.mark.parametrize("case", COMMANDS)
@pytest.mark.asyncio
async def test_read_only_blocks_before_any_network(case: CommandCase) -> None:
    session = FakeSession()
    with pytest.raises(ReadOnlyError):
        await case.call(make_client(session, tokens=None), "VIN")
    assert session.calls == []


@pytest.mark.parametrize("case", COMMANDS)
@pytest.mark.parametrize(("enabled", "subscribed"), [(False, True), (True, False), (True, None)])
@pytest.mark.asyncio
async def test_unsupported_command_is_not_sent(
    case: CommandCase, enabled: bool, subscribed: bool | None
) -> None:
    session = FakeSession(
        capabilities_response(case.service, enabled=enabled, subscribed=subscribed)
    )
    with pytest.raises(UnsupportedCommandError) as error:
        await case.call(make_client(session, read_only=False), "VIN")
    assert error.value.command == case.operation
    assert len(session.calls) == 1
    assert request_payload(session, 0)["operationName"] == "VehicleCapabilities"


@pytest.mark.parametrize("case", COMMANDS)
@pytest.mark.asyncio
async def test_missing_capabilities_do_not_allow_commands(case: CommandCase) -> None:
    session = FakeSession(FakeResponse(200, {"data": {"vehicle": {"capabilities": None}}}))
    with pytest.raises(UnsupportedCommandError):
        await case.call(make_client(session, read_only=False), "VIN")
    assert len(session.calls) == 1


@pytest.mark.parametrize(
    ("case", "other_service"),
    [
        (COMMANDS[0], "REMOTE_DOOR_UNLOCK"),
        (COMMANDS[1], "REMOTE_DOOR_LOCK"),
    ],
)
@pytest.mark.asyncio
async def test_directional_service_does_not_grant_opposite_action(
    case: CommandCase, other_service: str
) -> None:
    session = FakeSession(capabilities_response(other_service))
    with pytest.raises(UnsupportedCommandError):
        await case.call(make_client(session, read_only=False), "VIN")
    assert len(session.calls) == 1


@pytest.mark.asyncio
async def test_subscription_is_checked_again_for_each_command() -> None:
    case = COMMANDS[0]
    session = FakeSession(
        capabilities_response(case.service),
        command_response(case),
        capabilities_response(case.service, subscribed=False),
    )
    client = make_client(session, read_only=False)
    await case.call(client, "VIN")
    with pytest.raises(UnsupportedCommandError):
        await case.call(client, "VIN")
    assert len(session.calls) == 3
    assert request_payload(session, 2)["operationName"] == "VehicleCapabilities"


@pytest.mark.asyncio
async def test_capabilities_are_specific_to_the_requested_vehicle() -> None:
    case = COMMANDS[0]
    session = FakeSession(
        capabilities_response(case.service),
        command_response(case),
        capabilities_response(case.service, enabled=False),
    )
    client = make_client(session, read_only=False)
    await case.call(client, "VIN1")
    with pytest.raises(UnsupportedCommandError):
        await case.call(client, "VIN2")
    assert request_payload(session, 0)["variables"] == {"vin": "VIN1", "unit": "FAHRENHEIT"}
    assert request_payload(session, 2)["variables"] == {"vin": "VIN2", "unit": "FAHRENHEIT"}


@pytest.mark.parametrize("case", COMMANDS)
@pytest.mark.asyncio
async def test_capability_error_prevents_command(case: CommandCase) -> None:
    session = FakeSession(FakeResponse(200, {"errors": [{"message": "Unavailable"}]}))
    with pytest.raises(GraphQLError):
        await case.call(make_client(session, read_only=False), "VIN")
    assert len(session.calls) == 1


@pytest.mark.asyncio
async def test_malformed_capabilities_prevent_command() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "capabilities": {
                            "serviceCapability": [
                                {"type": "REMOTE_DOOR_LOCK", "enabled": "yes", "subscribed": True}
                            ]
                        }
                    }
                }
            },
        )
    )
    with pytest.raises(ResponseError):
        await COMMANDS[0].call(make_client(session, read_only=False), "VIN")
    assert len(session.calls) == 1
