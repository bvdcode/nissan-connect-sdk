from collections.abc import Awaitable, Callable
from typing import Protocol

from .models import Tokens
from .request_proof import RequestProof

type TokenListener = Callable[[Tokens], Awaitable[None] | None]


class RequestProofProvider(Protocol):
    """Return request proof, refreshing it when explicitly requested."""

    def __call__(self, force_refresh: bool, /) -> Awaitable[RequestProof]: ...
